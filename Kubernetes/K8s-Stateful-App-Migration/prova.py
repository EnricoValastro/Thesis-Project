import subprocess

def execute_command(command, password):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate(input="Birex2023\n")
    return output, error

def copy_file_between_nodes(source_node, destination_node, source_path, destination_path, password):
    # Copia il file dal nodo di origine al nodo master
    copy_step1 = f'echo {password} | sudo -S scp {source_node}:{source_path} .'
    execute_command(copy_step1, password)

    # Copia il file dal nodo master al nodo di destinazione
    copy_step2 = f'echo {password} | sudo -S scp {file_name} {destination_node}:{destination_path}'
    execute_command(copy_step2, password)


# Configura i dettagli del cluster e i percorsi dei file
source_node = "cb0@192.168.42.157"
destination_node = "cb0@192.168.42.158"
source_path = "/home/cb0/state/prova.txt"
destination_path = "/home/cb0/state"
file_name = "prova.txt"
password = "Birex2023"

# Esegui lo spostamento del file
copy_file_between_nodes(source_node, destination_node, source_path, destination_path, password)