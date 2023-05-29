import subprocess

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, source_path, destination_path, password):
    # Copia il file dal nodo di origine al nodo master
    copy_step1 = f'sshpass -p "Birex2023" scp -r {source_node}:{source_path} .'
    execute_command(copy_step1)

    # Copia il file dal nodo master al nodo di destinazione
    copy_step2 = f'sshpass -p "Birex2023" scp -r prova.txt {destination_node}:{destination_path}'
    execute_command(copy_step2)


# Configura i dettagli del cluster e i percorsi dei file
destination_node = "cb0@192.168.42.157"
source_node = "cb0@192.168.42.158"
source_path = "/home/cb0/prova.txt"
destination_path = "/home/cb0/"
file_name = "prova.txt"
password = "Birex2023"

# Esegui lo spostamento del file
copy_file_between_nodes(source_node, destination_node, source_path, destination_path, password)

