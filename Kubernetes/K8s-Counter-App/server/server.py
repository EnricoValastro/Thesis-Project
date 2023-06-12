import socket
import sys
import threading
import os
import time

PORT = int(os.getenv('LISTEN_PORT'))
lock = threading.Lock()

def handle_client_request(connection):
    try:
        # Receive data
        data = connection.recv(64)
        data = data.decode()

        # Simulate operation
        time.sleep(1.5)

        # Check for file ClientId.txt
        if os.path.exists("counter/"+data + '.txt'):
        # If file exists, read and increase current value
            with open("counter/"+data + '.txt', 'r') as file:
                current_value = int(file.read())
            
            new_value = current_value + 1
            
            # Write new value on file 
            with open("counter/"+data + '.txt', 'w') as file:
                file.write(str(new_value))
        else:
            # If file dosen't exists, create it and write 1
            with open("counter/"+data + '.txt', 'w') as file:
                file.write('1')

        # Acquire lock to synchronize thread on shared file
        lock.acquire()

        # Update clientHistory that keep track of last client served
        fp = open("counter/clientHistory.txt", "a")
        fp.write(f"{data}\n")

        lock.release()

        response = b'Completed!'
        connection.sendall(response)
    finally:
        connection.close()


def start_server():
    # Open socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', PORT)
    print('Starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    sock.listen()

    while True:
        print('\nWaiting for a connection')
        connection, client_address = sock.accept()

        # Create and run a thread to serve client
        client_thread = threading.Thread(target=handle_client_request, args=(connection,))
        client_thread.start()

start_server()
