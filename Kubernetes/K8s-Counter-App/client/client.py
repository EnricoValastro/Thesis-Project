import socket
import os
import sys
import time
import random

clients = ['Client1', 'Client2', 'Client3', 'Client4', 'Client5' ]

SRV = os.getenv('SERVER_ADDRESS')
PORT = int(os.getenv('SERVER_PORT'))

def selectRandom():
    return random.choice(clients)       

def start_client():
    
    time.sleep(5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SRV, PORT)
    try:
        sock.connect(server_address)
    except Exception as e:
        print("Cannot connect to the server,", e) 

    try:
        message = selectRandom()
        
        print('Sending:  {!r}'.format(message))
        sock.sendall(message.encode())

        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(64)
            amount_received += len(data)
            print('Received: {!r}'.format(data))
    finally:
        print('Closing socket\n')
        sock.close()
    exit(0)

start_client()