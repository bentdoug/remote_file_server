import struct
import TFTPfinal
import comms.communications as comms
import common_variables as env
import Server_Client_connections as connect
import UI
import sys
import time

PACKET_FORMAT = env.PACKET_FORMAT #"ss"  opcode [b'<STR>], filename [b'<STR>]
OPCODES = env.OPCODES # Dictionary of opcodes key: name/function - value: corresponding opcode
server_address = "0.0.0.0"


class client:
    '''
    This class houses methods necessary for client side functionality of the remote file server program
    '''
    def __init__(self):
        '''
        Initializes a client object, connects to a server, waits for server instructions, then upon
        recieval of the appriopriate command, enters state where user can select actions
        '''
        self.comms = comms.comms(0)
        self.listen_for_server_cmd()
        UI.call_fn(self)

    def listen_for_server_cmd(self):
        '''
        Listens for an OPCODE from the server connection and initiates the appropriate 
        functions upon receiving one
        '''
        state = None
        while state is not OPCODES["Done"]:
            recvd = self.comms.receive_opcode()
            if recvd[0] == OPCODES["request_file_hash"]: # Server is requesting information regarding the client's version of specified file
                #self.send_acknowledgement(OPCODES["request_file_info"])
                self.send_file_hash(recvd[1])
            if recvd[0] == OPCODES["request_file_contents"]: # Server is requesting the contents of the specified file
                self.send_file_contents('bin/client/'+recvd[1])
            if recvd[0] == OPCODES["Done"]:
                state = OPCODES["Done"]

    def push_file(self, file):
        '''
        Facilitates adding a file from the client to the server

        Parameters:
            file (str):
                A string representing the file to be sent's name
        '''
        self.comms.send_opcode(OPCODES["add_file"], file.split('/')[-1])
        self.send_file_contents(file)

    def send_file_contents(self, file):
        '''
        Function to send the contents of a file from the client to the server

        Parameters:
            file (str)
                A string representing the file to be sent's name
        '''
        with open(file, 'r') as f:
            file_contents = f.read()
        self.comms.send_file(file)
        time.sleep(1)
        self.comms.send_opcode(OPCODES["Done"])
    
    def send_acknowledgement(self, cmd):
        packet_info = [cmd, None.encode('utf-8')]
        request_cmd = struct.pack(PACKET_FORMAT, *packet_info)
        self.comms.send_str(request_cmd)

    def send_file_hash(self, file):
        '''
        Sends the hash value of a specified file

        Parameters:
            file (str)
                A string representing the file who's hash is to be sent's name
        '''
        with open('bin/client/'+file, 'r') as f:
            file_contents = f.read()
        self.comms.send_hash(file, hash(file_contents))

    def disconnect(self):
        '''
        Facilitates the disconnection from the socket and subsequent ending of the program
        '''
        self.comms.send_opcode(OPCODES["disconnect"])
        #self.listen_for_server_cmd()
        sys.exit()

def start():
    '''
    Entry point for client initialization. Creates & initializes a client object
    '''
    server_instance = client()