import socket
import sys
import threading
import os
import time

PORT = int(os.getenv('LISTEN_PORT'))
lock = threading.Lock()

def handle_client_request(connection):
    try:
        data = connection.recv(64)
        data = data.decode()

        time.sleep(1.5)

        if os.path.exists("counter/"+data + '.txt'):
        # Il file esiste, leggi il valore corrente e incrementalo
            with open("counter/"+data + '.txt', 'r') as file:
                current_value = int(file.read())
            
            new_value = current_value + 1
            
            # Scrivi il nuovo valore nel file
            with open("counter/"+data + '.txt', 'w') as file:
                file.write(str(new_value))
        else:
            # Il file non esiste, crea un nuovo file con valore 1
            with open("counter/"+data + '.txt', 'w') as file:
                file.write('1')

        lock.acquire()

        fp = open("counter/clientHistory.txt", "a")
        fp.write(f"{data}\n")

        lock.release()

        response = b'Completed!'
        connection.sendall(response)
    finally:
        connection.close()


def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', PORT)
    print('Starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    sock.listen()

    while True:
        print('\nWaiting for a connection')
        connection, client_address = sock.accept()

        client_thread = threading.Thread(target=handle_client_request, args=(connection,))
        client_thread.start()

start_server()
