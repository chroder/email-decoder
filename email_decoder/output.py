import json
import msgpack
from datetime import datetime
from email_decoder.models.message import Message
from email_decoder.models.headers import Headers
from email_decoder.models.body import Body
from email_decoder.models.addr import Addr
from flanker.mime.message.headers.wrappers import ContentType
from flanker.mime.message.headers.wrappers import WithParams
from flanker.mime.message.headers.wrappers import MessageId


def object_to_dict(obj, opts=None):
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
        res['body_parts'] = [object_to_dict(p) for p in obj.body_parts]
        res['headers'] = object_to_dict(obj.headers)
        res['raw_headers'] = object_to_dict(obj.raw_headers, {"raw_names": True})
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

    if isinstance(obj, Body):
        return {"type": obj.type, "content": obj.content}

    if isinstance(obj, Addr):
        return {"name": obj.name, "email": obj.email}

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

