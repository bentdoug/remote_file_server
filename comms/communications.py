import Server_Client_connections as connect
import common_variables as env
import os
import traceback

SEPARATOR = env.OPCODES["Seperator"]
BUFFER_SIZE = int(env.OPCODES["Buffer_Size"])
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on 
versions = ['Client', 'Server']


class comms():
    def __init__(self, version):
        '''
        Initializes the comms object which facilitates all communication related
        functions between client and server
        '''
        self.version = version
        if version == 0:
            self.socket = connect.establish_server_connection(HOST, PORT)
        if version == 1:
            self.socket = connect.receive_client_connection(HOST, PORT)[0]

    def send_str(self, str):
        '''
        Facilitates the sending of a string message through the socket

        Parameters:
            str (str):
                The string to be sent through the socket
        '''
        print("{} is sending {} as string".format(versions[self.version], str))
        self.socket.send(f"{str}".encode())

    def send_hash(self, file_name, hash):
        '''
        Facilitates the sending of a file's hash value through the socket connection

        Parameters:
            file_name (str):
                A string representing the name of the file who's hash is to be sent

            hash (int):
                the hash value of the file who's hash is to be sent
        '''
        to_send = f"\"{file_name}\" : \"{hash}\""
        to_send = "{" + to_send + "}"
        self.send_str(to_send)

    def send_opcode(self, opcode, file_name="None"):
        '''
        Facilitates sending an opcode through the socket connection

        Parameters:
            opcode (str):
                The opcode that should be sent through the socket connection
            file_name (str):
                The file (if applicable) the OPCODE is in reference too
        '''
        to_send = f"{opcode}{SEPARATOR}{file_name}"
        print("{} is sending {}".format(versions[self.version], to_send))
        self.socket.send(to_send.encode())

    def receive_opcode(self):
        '''
        Facilitates receiving an OPCODE through the socket connection

        Returns:
            The recieved opcode and file name that the opcode is in reference too
        '''
        print('{} is listening for OPCODE'.format(versions[self.version]))
        received = self.socket.recv(BUFFER_SIZE).decode()
        print("got", received)
        opcode, file_name = received.split(SEPARATOR)
        return [opcode, file_name]

    def send_file(self, file_path):
        '''
        Facilitates the sending of a specified file through the socket connection

        Parameters:
            file_path (str):
                A string representing the file path to the file to be sent
        '''
        print("{} is sending {}".format(versions[self.version], file_path))
        # get file size
        filesize = os.path.getsize(file_path)

        # Send file name and size
        self.socket.send(f"{file_path}{SEPARATOR}{filesize}".encode())

        with open(file_path, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # use sendall to assure transimission in 
                # busy networks
                self.socket.sendall(bytes_read)

    def recieve_file(self):
        '''
        Facilitates receiving a file through the socket connection

        Returns:
            the file's name and the contents of the file in string format
        '''
        print('{} is attempting to recieve a file'.format(versions[self.version]))
        received = self.socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        str_of_file = ""

        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = self.socket.recv(BUFFER_SIZE)
            print('bytes_read = ', bytes_read)
            if bytes_read == b'OP_DONE<SEPERATOR>None':    
                # nothing left to receive
                break
            # write to the file the bytes we just received
            str_of_file += str(bytes_read)
        print('{} has recieved {}'.format(versions[self.version], filename))
        return filename, str_of_file

    def recieve_str(self):
        '''
        Facilitates receiving a string through the socket connection

        Returns:
            The string recieved through the socket connection
        '''
        received = self.socket.recv(BUFFER_SIZE).decode()
        return received
    
    def disconnect(self):
        '''
        Closes the socket connection
        '''
        self.socket.close()