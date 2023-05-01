# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 20:46:30 2023

@author: matth
"""

import socket

RRQ_OPCODE = 1
WRQ_OPCODE = 2
DATA_OPCODE = 3
ACK_OPCODE = 4
ERROR_OPCODE = 5

MAX_PACKET_SIZE = 516
MAX_DATA_SIZE = 512

def create_packet(opcode, block_number=0, data=b''):
    packet = bytearray()
    packet += b'\x00'
    packet += bytes([opcode])
    packet += block_number.to_bytes(2, byteorder='big')
    packet += data
    return bytes(packet)

def parse_packet(packet):
    opcode = packet[1]
    block_number = int.from_bytes(packet[2:4], byteorder='big')
    data = packet[4:]
    return opcode, block_number, data

def send_tftp_packet(sock, opcode, block_number=0, data=b'', addr=None):
    packet = create_packet(opcode, block_number, data)
    if addr is None:
        sock.send(packet)
    else:
        sock.sendto(packet, addr)
    return packet

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
    except EOFError:
        print("no data provided to input function")
        sock.close()