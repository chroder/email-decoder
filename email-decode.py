import logging
import sys
import os.path
import argparse
from flanker import mime
from email_decoder.parser import Parser
from email_decoder.output import message_to_json
from email_decoder.output import message_to_msgpack
from email_decoder.output import message_to_debug_out

opt_parser = argparse.ArgumentParser(description='Reads a raw email file and outputs a structured version in various formats')
opt_parser.add_argument('file', metavar='file', type=str, help='Path to an email file to parse')
opt_parser.add_argument('--format', dest="format", type=str, help='The output format: json, msgpack, debug', default="debug")
args = opt_parser.parse_args()

if not args.file:
    print("An argument is required (the name of the file)")
    sys.exit(1)

file_path = args.file
if not os.path.isfile(file_path):
    print("The file specified does not exist")
    sys.exit(1)

with open(file_path, 'r') as f:
    file_contents = f.read()

mimepart = mime.from_string(file_contents)

parser = Parser()
msg = parser.message_from_mimepart(mimepart)

if args.format == "json":
    print message_to_json(msg)
elif args.format == "msgpack":
    print message_to_msgpack(msg)
else:
    message_to_debug_out(msg)
