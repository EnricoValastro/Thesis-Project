import socket
import threading
import os

def handle_client_request(client_socket):
    # Ricevi la richiesta dal client
    request = client_socket.recv(1024)
    value = request.decode()

    # Verifica se il file esiste
    if os.path.exists("etc/counter/"+value + '.txt'):
        # Il file esiste, leggi il valore corrente e incrementalo
        with open("etc/counter/"+value + '.txt', 'r') as file:
            current_value = int(file.read())
        
        new_value = current_value + 1
        
        # Scrivi il nuovo valore nel file
        with open("etc/counter/"+value + '.txt', 'w') as file:
            file.write(str(new_value))
    else:
        # Il file non esiste, crea un nuovo file con valore 1
        with open("etc/counter/"+value + '.txt', 'w') as file:
            file.write('1')

    # Acquisisce il lock prima di accedere alla risorsa condivisa
    lock.acquire()
    try:
        # Apri il file in modalità append (aggiunta)
        with open("etc/counter/clientHistory.txt", "a") as file:
            file.write(f"{value}\n")
    finally:
        # Rilascia il lock dopo aver finito l'operazione
        lock.release()

    # Invia la conferma al client
    response = 'Operazione completata con successo'
    client_socket.send(response.encode())

    # Chiudi la connessione con il client
    client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 3500))
    server_socket.listen(5)
    print('Server in ascolto...')

    while True:
        client_socket, client_address = server_socket.accept()
        print('Connessione accettata da:', client_address)

        # Avvia un nuovo thread per gestire la connessione del client
        client_thread = threading.Thread(target=handle_client_request, args=(client_socket,))
        client_thread.start()

lock = threading.Lock()
start_server()
