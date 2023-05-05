# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:31:22 2023

@author: matth
"""
import socket

def establish_server_connection(server_address, server_port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    print(f"[+] Connecting to {server_address}:{server_port}")
    client_socket.connect((server_address, server_port))
    print("[+] Connected.")
    return client_socket

def receive_client_connection(server_address, server_port):
    
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    try:
        server_socket.bind((server_address, server_port))
    except:
        print(server_port, "is likely in use")

    # if below code is executed, that means the sender is connected
    
    # Listen for incoming connections
    server_socket.listen(5)
    print(f"[*] Listening as {server_address}:{server_port}")
    # Wait for a client to connect
    client_socket, client_address = server_socket.accept()
    print(f"[+] {client_address} is connected.")
    return client_socket, client_address