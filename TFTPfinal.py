# -*- coding: utf-8 -*-


import socket

#opcode denotaton
RRQ_OPCODE = 1
WRQ_OPCODE = 2
DATA_OPCODE = 3
ACK_OPCODE = 4
ERROR_OPCODE = 5

#able to chnage, made these as basic values
MAX_PACKET_SIZE = 516
MAX_DATA_SIZE = 512

#method to create a packet and fill
def create_packet(opcode, block_number=0, data=b''):
    packet = bytearray()
    packet += b'\x00'
    packet += bytes([opcode])
    packet += block_number.to_bytes(2, byteorder='big')
    packet += data
    return bytes(packet)

#parses though the packet and returns bytearray of data along with opcode and block size for processing
def parse_packet(packet):
    opcode = packet[1]
    block_number = int.from_bytes(packet[2:4], byteorder='big')
    data = packet[4:]
    return opcode, block_number, data

#sendng packets over  socket
def send_tftp_packet(sock, opcode, block_number=0, data=b'', addr=None):
    packet = create_packet(opcode, block_number, data)
    if addr is None:
        sock.send(packet)
    else:
        sock.sendto(packet, addr)
    return packet

#recieving packtes. Calls for an RRQ from either client and requires a reponse of packet and such left
def tftp_download_file(server_addr, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = bytearray()
    try:
        packet = send_tftp_packet(sock, RRQ_OPCODE, data=f'{filename}\x00octet\x00'.encode(), addr=server_addr)
        while True:
            packet, _ = sock.recvfrom(MAX_PACKET_SIZE)
            opcode, block_number, packet_data = parse_packet(packet)
            if opcode == DATA_OPCODE:
                data += packet_data
                if len(packet_data) < MAX_DATA_SIZE:
                    return bytes(data)
            elif opcode == ERROR_OPCODE:
                raise RuntimeError(f'TFTP error: {packet_data.decode()}')
                #require response and cancels without one
                
    except EOFError:
        print("no data provided to input function")
        sock.close()