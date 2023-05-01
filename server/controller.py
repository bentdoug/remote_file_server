import struct
import os

PACKET_FORMAT = os.getenv("PACKET_FORMAT") #"ss"  opcode [b'<STR>], filename [b'<STR>]
OPCODES = os.getenv("OPCODES") # Dictionary of opcodes key: name/function - value: corresponding opcode

class server:
    '''
    This class houses methods necessary for server side functionality of the remote file server program
    '''

    def __init__(self):
        '''
        Initializes a server object, loads in the db of files saved to the server, listens for a client connection, and syncronizes
        with client upon connection. After syncronization, server waits for client command input.
        '''
        self.stored_files = load_db() # TODO: Confirm method naming to load in csv information from DB
        self.client = comms.establish_connection() # TODO: Confirm method naming to initialize socket connection - return once connection accepted
        self.sync()
        self.listen_for_cmd()

    def listen_for_cmd(self):
        '''
        Listens for client commands and executes them as necessary. Upon recieving 'disconnect' command, initiates syncronization and
        disconnect.
        '''
        state = None
        while state is not OPCODES["Quit"]:
            recvd = self.client.listen()
            if recvd[0] == OPCODES["request_file_info"]: # Client requesting server's version of specified file
                self.send_acknowledgement(OPCODES["request_file_contents"])
                self.send_file_info(recvd[1])
            if recvd[0] == OPCODES["send_file_info"]: # Client requesting to send server the client's version of specified file
                self.send_acknowledgement(OPCODES["send_file_contents"])
                self.get_file_info(recvd[1])
            if recvd[0] == OPCODES["compare_hashes"]: # Client is requesting to compare the hash of the specified file
                self.send_acknowledgement(OPCODES["compare_hashes"])
                self.compare_hash(recvd[1])
            if recvd[0] == OPCODES["send_file_hash"]: # Client is requesting to send the hash of the specified file to the server
                pass
            if recvd[0] == OPCODES["request_file_hash"]: # Client is requesting the server to send the stored hash of the specified file
                pass
            if recvd[0] == OPCODES["disconnect"]: # Client is requesting to disconnect. Triggers final syncronization followed by disconnection
                self.send_acknowledgement(OPCODES["disconnect"])
                self.sync()
                self.client.disconnect()

    def sync(self):
        '''
        Syncronizes the server db with the client file's state
        '''
        client_hashes = self.client.send_and_recv(self.stored_files.keys()) # Sends the keys (names of already saved files) to the client and awaits response
        to_update = []
        # Create a list of files that are no longer up-to-date
        for file in self.stored_files.keys():
            try:
                if self.stored_files[file] != client_hashes[file]:
                    to_update.append(file)
            except KeyError:
                print("The following file's information was requested from client but not returned to server: {0}".format(file))
        
        # Request to update out-of-date files
        for file in to_update:
            self.get_file_info(file)

    def get_file_info(self, file):
        '''
        Creates request for file contents from the client and sends to the client. Upon recieving the file contents, it is unpacked,
        and saved to the server for later access.

        Parameters:
            file (str):
                A string indicating the name of the file who's information is being requested.
        '''
        packet_info = [OPCODES["request_file_contents"], file.encode('utf-8')]
        request_cmd = struct.pack(PACKET_FORMAT, *packet_info)
        file_contents = self.client.send_and_recv(request_cmd)
        self.save_file(file_contents)

    def save_file(file):
        '''
        Initiate saving the contents of a file recieved from the client

        Parameters:
            file (struct)
                The packet containing the file to be unpacked and saved to the server
        '''
        file_contents = struct.unpack(PACKET_FORMAT, file)
        db.save_to_db(file_contents) # TODO: Send the contents of the unpacked file to get saved to the db

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
        server_hash = db.get_hash(file_name)

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