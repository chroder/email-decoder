import sys
import os.path
from optparse import OptionParser
from flanker import mime
from email_decoder.parser import Parser
from email_decoder.output import message_to_json
from email_decoder.output import message_to_msgpack

parser = OptionParser()
(options, args) = parser.parse_args()

if not args[0]:
    print("An argument is required (the name of the file)")
    sys.exit(1)

file_path = args[0]
if not os.path.isfile(file_path):
    print("The file specified does not exist")
    sys.exit(1)

with open(file_path, 'r') as f:
    file_contents = f.read()

mimepart = mime.from_string(file_contents)

parser = Parser()
msg = parser.message_from_mimepart(mimepart)
print message_to_json(msg)