import Server_Client_connections as connect
import common_variables as env
import os

SEPARATOR = env.OPCODES["Seperator"]
BUFFER_SIZE = int(env.OPCODES["Buffer_Size"])
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
versions = ['Client', 'Server']


class comms():
    def __init__(self, version):
        self.version = version
        if version == 0:
            self.socket = connect.establish_server_connection(HOST, PORT)
        if version == 1:
            self.socket = connect.receive_client_connection(HOST, PORT)[0]

    def send_str(self, str):
        self.socket.send(f"{str}".encode())

    def send_opcode(self, opcode, file_name):
        print("{} is sending {}".format(versions[self.version], opcode))
        to_send = f"{opcode}{SEPARATOR}{file_name}"
        print("sending; ", to_send)
        self.socket.send(to_send.encode())

    def receive_opcode(self):
        print('{} is listening for OPCODE'.format(versions[self.version]))
        received = self.socket.recv(BUFFER_SIZE).decode()
        print("got", received)
        opcode, file_name = received.split(SEPARATOR)
        return [opcode, file_name]

    def send_file(self, file_path):
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
        received = self.socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)

        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)

    def recieve_str(self):
        received = self.socket.recv(BUFFER_SIZE).decode()
        return received