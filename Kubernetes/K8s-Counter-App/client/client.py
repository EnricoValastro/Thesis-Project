import socket
import os
import sys
import time
import random

# Client ID
clients = ['Client1', 'Client2', 'Client3', 'Client4', 'Client5' ]

# Retrive server address and port from k8s env
SRV = os.getenv('SERVER_ADDRESS')
PORT = int(os.getenv('SERVER_PORT'))

# Select Client ID on pseudo-randomic way
def selectRandom():
    return random.choice(clients)       

def start_client():
    
    # Sock init
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SRV, PORT)
    try:
        sock.connect(server_address)
    except Exception as e:
        print("Cannot connect to the server,", e) 

    try:
        message = selectRandom()
        
        print('Sending:  {!r}'.format(message))
        # Send messagge (Client ID)
        sock.sendall(message.encode())

        amount_received = 0
        amount_expected = len(message)

        # Wait for response
        while amount_received < amount_expected:
            data = sock.recv(64)
            amount_received += len(data)
            print('Received: {!r}'.format(data))
    finally:
        print('Closing socket\n')
        sock.close()
    exit(0)

start_client()