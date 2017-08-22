import json
import msgpack
from datetime import datetime
from email_decoder.models.message import Message
from email_decoder.models.headers import Headers
from email_decoder.models.addr import Addr
from email_decoder.models.file import File
from flanker.mime.message.headers.wrappers import ContentType
from flanker.mime.message.headers.wrappers import WithParams


def object_to_dict(obj):
    if isinstance(obj, Message):
        res = dict()
        res['subject'] = obj.subject
        res['message_id'] = obj.message_id
        res['references'] = obj.references
        res['from_addr'] = object_to_dict(obj.from_addr) if obj.from_addr else None
        res['to_addrs'] = object_to_dict(obj.to_addrs) if obj.to_addrs else None
        res['cc_addrs'] = object_to_dict(obj.cc_addrs) if obj.cc_addrs else None
        res['bcc_addrs'] = object_to_dict(obj.bcc_addrs) if obj.bcc_addrs else None
        res['date'] = obj.date.isoformat(' ') if obj.date else None
        res['message_date'] = obj.message_date.isoformat(' ') if obj.message_date else None
        res['body_html'] = object_to_dict(obj.body_html)
        res['body_text'] = object_to_dict(obj.body_text)
        res['headers'] = object_to_dict(obj.headers)
        res['raw_headers'] = object_to_dict(obj.raw_headers)
        res['files'] = object_to_dict(obj.files)
        return res

    if isinstance(obj, Headers):
        res = dict()
        for (hname, hs) in obj.headers.iteritems():
            if len(hs) and hs[0].is_single:
                res[hname] = object_to_dict(hs[0].value)
            else:
                res[hname] = [object_to_dict(h.value) for h in hs]

        return res

    if isinstance(obj, datetime):
        return obj.isoformat(' ')

    if isinstance(obj, Addr):
        return {"name": obj.name, "email": obj.email}

    if isinstance(obj, File):
        return obj.__dict__

    if isinstance(obj, ContentType):
        return {"content_type": obj.__str__(), "main_type": obj.main, "sub_type": obj.sub, "params": obj.params}

    if isinstance(obj, WithParams):
        return obj.params

    if type(obj) is list:
        return [object_to_dict(x) for x in obj]

    return obj


def message_to_json(message):
    return json.dumps(object_to_dict(message), indent=4)


def message_to_msgpack(message):
    return msgpack.packb(object_to_dict(message))


def addr_to_str(addr):
    if addr.name:
        return "%s <%s>" % (addr.name, addr.email)
    else:
        return addr.email


def message_to_debug_out(message):
    print("%-10s %s" % ("Subject:", message.subject))
    print("%-10s %s" % ("From:", addr_to_str(message.from_addr)))
    if message.to_addrs:
        print("%-10s %s" % ("To:", ', '.join([addr_to_str(a) for a in message.to_addrs])))
    if message.cc_addrs:
        print("%-10s %s" % ("CC:", ', '.join([addr_to_str(a) for a in message.cc_addrs])))

    if message.body_html:
        print('\n')
        print(message.body_html)

    if message.body_html and message.body_text:
        print("\n\n")
        print("-" * 78)
        print("\n\n")

    if message.body_text:
        print('\n')
        print(message.body_text)

    if message.files:
        print('\n')
        print("Attachments:")
        for f in message.files:
            print("  * %s (%s bytes) -- %s" % (f.filename, f.size, f.content_type))
