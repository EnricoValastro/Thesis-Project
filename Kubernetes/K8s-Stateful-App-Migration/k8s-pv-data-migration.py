import subprocess

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, source_path, destination_path):
    # Copia il file dal nodo di origine al nodo di destinazione utilizzando scp
    copy_command = f'scp {source_node}:{source_path} {destination_node}:{destination_path}'
    execute_command(copy_command)

# Configura i dettagli del cluster e i percorsi dei file
source_node = "cb0@192.168.42.157"
destination_node = "cb0@192.168.42.158"
source_path = "/home/cb0/state"
destination_path = "/home/cb0/state"

# Esegui lo spostamento del file
copy_file_between_nodes(source_node, destination_node, source_path, destination_path)
