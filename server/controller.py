import struct
import common_variables as env
import TFTPfinal
import comms.communications as comms
import Database
import json
import sys

PACKET_FORMAT = env.PACKET_FORMAT #"ss"  opcode [b'<STR>], filename [b'<STR>]
OPCODES = env.OPCODES # Dictionary of opcodes key: name/function - value: corresponding opcode
client_address = "0.0.0.0"

class server:
    '''
    This class houses methods necessary for server side functionality of the remote file server program
    '''

    def __init__(self):
        '''
        Initializes a server object, loads in the db of files saved to the server, listens for a client connection, and syncronizes
        with client upon connection. After syncronization, server waits for client command input.
        '''
        self.db = Database.Database()
        self.files_hashes = self.db.get_db()
        self.comms = comms.comms(1)
        self.sync()
        self.listen_for_cmd()

    def listen_for_cmd(self):
        '''
        Listens for client commands and executes them as necessary. Upon recieving 'disconnect' command, initiates syncronization and
        disconnect.
        '''
        state = None
        while state is not OPCODES["Quit"]:
            recvd = self.comms.receive_opcode()
            if recvd[0] == OPCODES["request_file_contents"]: # Client requesting server's version of specified file
                self.send_file_info(recvd[1])
            if recvd[0] == OPCODES["send_file_contents"]: # Client requesting to send server the client's version of specified file
                self.get_file_info(recvd[1])
            if recvd[0] == OPCODES["compare_hashes"]: # Client is requesting to compare the hash of the specified file
                self.compare_hash(recvd[1])
            if recvd[0] == OPCODES["add_file"]:
                self.get_file_info(recvd[1])
            if recvd[0] == OPCODES["send_file_hash"]: # Client is requesting to send the hash of the specified file to the server
                pass
            if recvd[0] == OPCODES["request_file_hash"]: # Client is requesting the server to send the stored hash of the specified file
                pass
            if recvd[0] == OPCODES["disconnect"]: # Client is requesting to disconnect. Triggers final syncronization followed by disconnection
                #self.sync()
                self.comms.disconnect()
                state = OPCODES["Quit"]

    def sync(self):
        '''
        Syncronizes the server db with the client file's state
        '''
        received_file_hashes = ""
        client_hashes = {}
        if self.files_hashes.keys():
            for file in self.files_hashes.keys():
                self.comms.send_opcode(OPCODES["request_file_hash"], file)
                received_file_hashes += (self.comms.recieve_str())
            print('received hashes {}'.format(received_file_hashes))
            recvd_hashes = json.loads(received_file_hashes)
            client_hashes |= recvd_hashes
            to_update = []
            # Create a list of files that are no longer up-to-date
            for file in self.files_hashes.keys():
                try:
                    print(type(self.files_hashes), type(client_hashes))
                    if self.files_hashes[file] != client_hashes[file]:
                        to_update.append(file)
                except KeyError:
                    print("The following file's information was requested from client but not returned to server: {0}".format(file))
            
            # Request to update out-of-date files
            for file in to_update:
                self.get_file_info(file)
        self.comms.send_opcode(OPCODES["Done"])

    def get_file_info(self, file):
        '''
        Creates request for file contents from the client and sends to the client. Upon recieving the file contents, it is unpacked,
        and saved to the server for later access.

        Parameters:
            file (str):
                A string indicating the name of the file who's information is being requested.
        '''
        self.comms.send_opcode(OPCODES["request_file_contents"], file)
        file_name, file_contents = self.comms.recieve_file()
        self.save_file(file_name, file_contents)

    def save_file(self, file_name, file_contents):
        '''
        Initiate saving the contents of a file recieved from the client and save the hash of the new file

        Parameters:
            file (struct)
                The packet containing the file to be unpacked and saved to the server
        '''
        print("Server is attempting to save the received file.")
        Database.save_file(file_name, file_contents) # TODO: Send the contents of the unpacked file to get saved to the db
        self.files_hashes[file_name] = hash(file_contents)
        print("{} has been succesfully saved".format(file_name))

    def compare_hash(self, file_name):
        '''
        This method compares the server side hash of a file vs the recieved client side hash to establish the existence of any
        diffs

        Parameters:
            file_name (str):
                String indicating the file to compare hashes for

        Returns
            Boolean:
                True/False indicating whether the file hashes are the same (True) or different (False)
        '''
        server_hash = self.files_hashes[file_name]

        packet_info = [OPCODES["request_hash"], file_name.encode('utf-8')]
        request_cmd = struct.pack(PACKET_FORMAT, *packet_info)
        client_hash = self.client.send_and_recv(request_cmd)

        if server_hash == client_hash: # Hashes are the same (file has not changed)
            '''packet_info = [OPCODES["no_update_required"], file_name.encode('utf-8')]
            cmd = struct.pack(PACKET_FORMAT, *packet_info)
            self.client.send(cmd)'''
            return True
        else: # Hashes are different (file has changed)
            return False
        
def start():
    '''
    Entry point for server initialization. Creates & initializes a server object
    '''
    server_instance = server()