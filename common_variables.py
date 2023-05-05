import os

OPCODES = {
    "Quit" : "OP_QUIT",
    "Done" : "OP_DONE",
    "request_file_contents" : "OP_REQUEST_FILE",
    "send_file_contents" : "OP_SEND_FILE",
    "compare_hashes" : "OP_COMP_HASHES",
    "add_file" : "OP_ADD_FILE",
    "request_file_hash" : "OP_REQ_HASH",
    "send_file_hash" : "OP_SEND_HASH",
    "disconnect" : "OP_DISCONNECT",
    "Seperator" : "<SEPERATOR>",
    "Buffer_Size" : "4096"
    }

PACKET_FORMAT = "ss" # opcode (str) file name (str)
