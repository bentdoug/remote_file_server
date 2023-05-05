import struct
import TFTPfinal as comms
import common_variables as env

PACKET_FORMAT = env.PACKET_FORMAT #"ss"  opcode [b'<STR>], filename [b'<STR>]
OPCODES = env.OPCODES # Dictionary of opcodes key: name/function - value: corresponding opcode

class client:
    '''
    This class houses methods necessary for client side functionality of the remote file server program
    '''
    def __init__(self):
        '''
        Initializes a client object, connects to a server, waits for server instructions, then upon
        recieval of the appriopriate command, enters state where user can select actions
        '''
        self.server = comms.establish_server_connection() 
        self.listen_for_server_cmd()
        self.handle_ui()

    def listen_for_server_cmd(self):
        state = None
        while state is not OPCODES["Done"]:
            recvd = self.server.listen()
            if recvd[0] == OPCODES["request_file_hash"]: # Server is requesting information regarding the client's version of specified file
                self.send_acknowledgement(OPCODES["request_file_info"])
                self.send_file_hash(recvd[1])
            if recvd[0] == OPCODES["request_file_contents"]: # Server is requesting the contents of the specified file
                self.send_acknowledgement(OPCODES["request_file_contents"])
                self.send_file_contents(recvd[1])
            if recvd[0] == OPCODES["Done"]:
                state = OPCODES["Done"]

    def add_new_file(self, file):
        self.server.send(OPCODES["add_file"])
        self.send_file_contents(file)

    def send_file_contents(self, file):
        with open(file, 'r') as f:
            file_contents = f.read()
        self.server.send(file_contents)
    
    def send_acknowledgement(self, cmd):
        packet_info = [cmd, None.encode('utf-8')]
        request_cmd = struct.pack(PACKET_FORMAT, *packet_info)
        self.server.send(request_cmd)

    def send_file_hash(self, file):
        with open(file, 'r') as f:
            file_contents = f.read()
        self.server.send(hash(file_contents))