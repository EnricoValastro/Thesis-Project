import socket
import random 
from kubernetes import client, config

clients = ['Client1', 'Client2', 'Client3', 'Client4', 'Client5' ]

config.load_kube_config()
v1 = client.CoreV1Api()

service_name = "counter-service"
service = v1.read_namespaced_service(name=service_name, namespace="default")
service_ip = service.spec.cluster_ip
service_port = 3500

def selectRandom():
    return random.choice(clients)

def client():

    # Creazione del socket del client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((service_ip, service_port))
        print('Connesso al server.')

        id = selectRandom()

        print("Client: "+id)

        client_socket.sendall(id.encode())

        # Ricezione dei dati dal server
        data = client_socket.recv(1024).decode()
        print('Risposta dal server:', data)

    except ConnectionRefusedError:
        print('Connessione rifiutata.')
    except KeyboardInterrupt:
        print('Connessione chiusa.')

    # Chiusura del socket del client
    client_socket.close()

# Esecuzione del client
client()
