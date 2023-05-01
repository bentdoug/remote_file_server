import os

OPCODES = {
    "Quit" : "OP_QUIT",
    "request_file_contents" : "OP_REQUEST_FILE",
    "send_file_contents" : "OP_SEND_FILE",
    "compare_hashes" : "OP_COMP_HASHES",
    "request_file_hash" : "OP_REQ_HASH",
    "send_file_hash" : "OP_SEND_HASH",
    "disconnect" : "OP_DISCONNECT"
    }

PACKET_FORMAT = "ss" # opcode (str) file name (str)

os.environ["PACKET_FORMAT"] = PACKET_FORMAT
os.environ["OPCODES"] = OPCODES