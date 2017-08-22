import mimetypes
import binascii
import rfc822
import uuid
from datetime import datetime
from email_decoder.models.message import Message
from email_decoder.models.addr import Addr
from email_decoder.models.file import File
from flanker.mime.message.headers.encodedword import decode
from flanker import mime
from ordered_set import OrderedSet
import itertools
from email_decoder.models.headers import Headers
from email.utils import parsedate_tz
from email.utils import mktime_tz
import structlog


class Parser:
    def __init__(self, logger=None, filestore=None):
        if logger is None:
            logger = structlog.get_logger()

        self.logger = logger

        if filestore is None:
            def filestore(f):
                return "<no store>"

        self.filestore = filestore

    def message_from_mimepart(self, mimepart):
        msg = Message()
        msg.raw_headers = headers_from_mimepart(mimepart)
        msg.headers = self.parsed_headers_from_raw_headers(msg.raw_headers)
        msg.subject = mimepart.subject
        msg.date = datetime.utcnow()
        msg.message_id = msg.headers.get_header_value('Message-ID') or None
        msg.from_addr = msg.headers.get_header_value('From') or None
        msg.to_addrs = msg.headers.get_header_values('To') or None
        msg.cc_addrs = msg.headers.get_header_values('CC') or None
        msg.bcc_addrs = msg.headers.get_header_values('BCC') or None
        msg.reply_to_addr = msg.headers.get_header_value('Reply-To') or None

        # Read references
        msg.references = parse_references_hval_list(list(itertools.chain.from_iterable([
            msg.headers.get_header_values('In-Reply-To') or [],
            msg.headers.get_header_values('References') or []
        ])))

        if msg.headers.has_header('Date'):
            msg.message_date = msg.headers.get_header_value('Date') or None
        elif msg.headers.has_header('Received'):
            received_hval = msg.headers.get_header_value('Received')
            try:
                msg.message_date = parse_date_from_received_hval(received_hval)
            except ValueError:
                msg.message_date = None
                self.logger.warning("Failed to parse date", tag="invalid_date_header", hname="Received", date_string=received_hval)

        if msg.headers.has_header('MIME-Version'):
            mime_version = msg.headers.get_header('MIME-Version').value.lower()
            if not mime_version.startswith('1.0'):
                self.logger.warning("Unexpected MIME-Version", tag=unexpected_mime_version, hname="MIME-Version", mime_version=mime_version)

        state = ParserState()
        self._walk_parts(state, mimepart)

        if state.html_parts:
            msg.body_html = ''.join(state.html_parts)
        if state.text_parts:
            msg.body_text = '\n'.join(state.text_parts)
        if state.attachments:
            for f in state.attachments:
                msg.files.append(f)

        return msg

    def parsed_headers_from_raw_headers(self, raw_headers):
        """
        Takes a Headers collection of raw headers (values are raw strings),
        and copies them into a collection where the headers are parsed into more
        meaningful values (e.g. email addresses are split).

        :param email_decoder.models.headers.Headers raw_headers: Collection of raw headers
        :return email_decoder.models.headers.Headers
        """
        headers = Headers()
        done_headers = set()

        for hname in Headers.ADDR_HEADERS:
            done_headers.add(hname.lower())
            hs = raw_headers.get_headers(hname)
            if hs:
                addresses = parse_address_hval_list([h.value for h in hs])
                for name, email in addresses:
                    addr = Addr(email, name)
                    if addr.is_valid:
                        headers.add_header_value(hname, addr)
                    else:
                        self.logger.warning("Invalid email address", tag=invalid_email_address, hname=hname, email_address=addr.email)

        for hname in Headers.DATE_HEADERS:
            done_headers.add(hname.lower())
            hs = raw_headers.get_headers(hname)
            if hs:
                for h in hs:
                    try:
                        date = parse_date_hval(h.value)
                        headers.add_header_value(hname, date, is_single=True)
                        break  # we only want a single date value
                    except ValueError:
                        self.logger.warning("Could not parse date", tag="invalid_date_header", hname=hname, date_string=h.value)

        for hname, hs in raw_headers.headers.iteritems():
            if hname.lower() not in done_headers:
                for h in hs:
                    headers.add_header_value(hname, h.value)

        # From header is a single value
        from_header = headers.get_header('From')
        if from_header:
            from_header.is_single = True

        return headers

    def _walk_parts(self, state, mimepart):
        for part in mimepart.walk(with_self=mimepart.content_type.is_singlepart()):
            try:
                if part.content_type.is_multipart():
                    continue
                self._parse_parts(state, part)
            except (mime.DecodingError, AttributeError, RuntimeError, TypeError, binascii.Error, UnicodeDecodeError) as e:
                self.logger.error('Error parsing message MIME parts', error=e)
                state.mark_error()

    def _parse_parts(self, state, mimepart):
        disposition, _ = mimepart.content_disposition
        content_id = mimepart.headers.get('Content-Id')
        content_type, params = mimepart.content_type

        filename = mimepart.detected_file_name
        if filename == '':
            filename = None

        data = mimepart.body

        is_text = content_type.startswith('text')
        if disposition not in (None, 'inline', 'attachment'):
            self.logger.error('Unknown Content-Disposition',  bad_content_disposition=mimepart.content_disposition)
            state.mark_error()
            return

        if disposition == 'attachment':
            self._save_attachment(state, data, disposition, content_type, filename, content_id)
            return

        if disposition == 'inline' and not (is_text and filename is None and content_id is None):
            # the extra logic above is to catch edge-cases where the mailer
            # sets Content-Disposition: on text body parts. These arent attachments, they're body parts
            self._save_attachment(state, data, disposition, content_type, filename, content_id)
            return

        if is_text:
            if data is None:
                return
            normalized_data = data.encode('utf-8', 'strict')
            normalized_data = normalized_data.replace('\r\n', '\n').replace('\r', '\n')
            if content_type == 'text/html':
                state.html_parts.append(normalized_data)
            elif content_type == 'text/plain':
                state.text_parts.append(normalized_data)
            else:
                self.logger.info('Saving other text MIME part as attachment', content_type=content_type)
                self._save_attachment(state, data, 'attachment', content_type, filename, content_id)
            return

        # Finally, if we get a non-text MIME part without Content-Disposition,
        # treat it as an attachment.
        self._save_attachment(state, data, 'attachment', content_type, filename, content_id)

    def _save_attachment(self, state, data, disposition, content_type, filename, content_id):
        if filename is None:
            mimetypes.init()
            ext = mimetypes.guess_extension(content_type) or ""
            filename = str(uuid.uuid4()) + ext

        f = File()
        f.content_id = content_id
        f.filename = filename
        f.size = len(data)
        f.content_type = content_type
        f.is_inline = disposition == "inline"
        f.data = self.filestore(data)

        state.attachments.append(f)


class ParserState:
    def __init__(self):
        self.html_parts = []
        self.text_parts = []
        self.attachments = []
        self.is_error = False

    def mark_error(self):
        self.is_error = True


def parse_date_from_received_hval(received_hval):
    dontcare, date_str = received_hval.split(';')
    return parse_date_hval(date_str)


def headers_from_mimepart(mimepart):
    """
    Extracts all headers from a mimepart

    :param flanker.mime.message.part.MimePart mimepart: The mime part to look in
    :return email_decoder.models.headers.Headers
    """
    headers = Headers()

    for name, value in mimepart.headers.iteritems():
        headers.add_header_value(name, value)

    return headers


def parse_address_hval(hval):
    """
    Given a address collection header value, parse out the name/email pairs into a list of (name, email)

    :param  string hval: Email address strings
    :return set[string, string]
    """
    addresses = set()
    for phrase, addrspec in rfc822.AddressList(hval).addresslist:
        addresses.add((decode(phrase), decode(addrspec)))

    return sorted(elem for elem in addresses)


def parse_address_hval_list(addr_hvals):
    """
    Given a list of strings containing email addresses, parse out the name/email pairs into a single list without dupes.

    :param  list[string] addr_hvals: Email address strings
    :return list[email_decoder.models.addr.Addr]
    """
    addresses = set()
    for hval in addr_hvals:
        for elem in parse_address_hval(hval):
            addresses.add(elem)

    return sorted(elem for elem in addresses)


def parse_date_hval(hval):
    """
    Given a header value string representing a date and time, return a Datetime

    :param string hval: The date and time string
    :return datetime
    """
    date_tuple = parsedate_tz(hval)
    if not date_tuple:
        raise ValueError

    timestamp = mktime_tz(date_tuple)
    dt = datetime.utcfromtimestamp(timestamp)
    dt.replace(microsecond=0)
    return dt


def parse_references_hval(hval):
    return hval.split()


def parse_references_hval_list(references_hvals):
    set = OrderedSet()
    for hval in references_hvals:
        set.update(parse_references_hval(hval))
    return set.items