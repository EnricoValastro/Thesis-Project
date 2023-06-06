import socket
import random
import threading

clients = ['Client1', 'Client2', 'Client3', 'Client4', 'Client5' ]
threads = []

def selectRandom():
    return random.choice(clients)

def send_client_request(id):

    print('Client '+id+' sending request to server')

    # Indirizzo IP e porta del server
    server_ip = '127.0.0.1'  # Indirizzo IP del server
    server_port = 3500  # Porta del server

    # Creazione del socket del client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((server_ip, server_port))
        print('Connesso al server.')

        client_socket.sendall(id.encode())

        # Ricezione dei dati dal server
        data = client_socket.recv(1024).decode()
        print('Risposta dal server:'+ data)

    except ConnectionRefusedError:
        print('Connessione rifiutata.')
    except KeyboardInterrupt:
        print('Connessione chiusa.')

    # Chiusura del socket del client
    client_socket.close()

def start_client():
    for i in range(0,3):
        # Avvia un nuovo thread client
        id = selectRandom()
        client_thread = threading.Thread(target=send_client_request, args=(id,))
        client_thread.start()
        threads.append(client_thread)
    
    for thread in threads:
        thread.join()

start_client()