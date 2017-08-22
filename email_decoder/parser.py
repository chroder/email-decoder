import logging
import rfc822
from datetime import datetime
from email_decoder.models.message import Message
from email_decoder.models.addr import Addr
from flanker.mime.message.headers.encodedword import decode
from email_decoder.models.headers import Headers
from email.utils import parsedate_tz
from email.utils import mktime_tz


class Parser:
    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger(__name__)

        self.logger = logger

    def message_from_mimepart(self, mimepart):
        msg = Message()
        msg.raw_headers = headers_from_mimepart(mimepart)
        msg.headers = self.parsed_headers_from_raw_headers(msg.raw_headers)
        msg.subject = mimepart.subject
        msg.date = datetime.utcnow()
        msg.message_date = msg.headers.get_header_value('Date') or None
        msg.from_addr = msg.headers.get_header_value('From') or None
        msg.to_addrs = msg.headers.get_header_values('To') or None
        msg.cc_addrs = msg.headers.get_header_values('CC') or None
        msg.bcc_addrs = msg.headers.get_header_values('BCC') or None
        msg.reply_to_addr = msg.headers.get_header_value('Reply-To') or None
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

        for hname in Headers.ADDR_HEADERS:
            hs = raw_headers.get_headers(hname)
            if hs:
                addresses = parse_address_hval_list([h.value for h in hs])
                for name, email in addresses:
                    addr = Addr(name, email)
                    if addr.is_valid:
                        headers.add_header_value(hname, addr)
                    else:
                        self.logger.warning("Invalid email address in %s header: %s", hname, addr.email,
                                            extra={"tag": "invalid_email_address", "hname": hname, "email_address": addr.email})

        for hname in Headers.DATE_HEADERS:
            hs = raw_headers.get_headers(hname)
            if hs:
                for h in hs:
                    try:
                        date = parse_date_hval(h.value)
                        headers.add_header_value(hname, date, is_single=True)
                        break  # we only want a single date value
                    except ValueError:
                        self.logger.warning("Invalid date in %s header: %s", hname, h.value,
                                            {"tag": "invalid_date_header", "hname": hname, "date_string": h.value})

        for hname, hs in raw_headers.headers.iteritems():
            if hname not in Headers.ADDR_HEADERS and hname not in Headers.DATE_HEADERS:
                for h in hs:
                    headers.add_header_value(hname, h.value)

        # From header is a single value
        from_header = headers.get_header('From')
        if from_header:
            from_header.is_single = True

        return headers


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
    Given a list of strings containing email addresses, parse out the name/email pairs into a list of (name, email)

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
            print elem
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
    return dt
