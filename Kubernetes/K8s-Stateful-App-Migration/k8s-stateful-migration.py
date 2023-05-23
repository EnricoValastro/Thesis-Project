from kubernetes import client, config
import subprocess

config.load_kube_config()
v1 = client.CoreV1Api()

source = {
        "metadata": {
            "labels": {
                "type": "source"
            }
        }
}
destination = {
        "metadata": {
            "labels": {
                "type": "destination"
            }
        }
}

user="cb0@"
path= "/home/cb0/state"

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copia il file dal nodo di origine al nodo master
    copy_step1 = f'sudo scp {user}{source_node}:{path}/todo.db .'
    execute_command(copy_step1)

    # Copia il file dal nodo master al nodo di destinazione
    copy_step2 = f'sudo scp todo.db {user}{destination_node}:{path}'
    execute_command(copy_step2)

node_list = v1.list_node()

# Get node list, find source and destination ip, swap labels.
for n in node_list.items:
    if (('type', 'source') in n.metadata.labels.items()):
        source_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('type', 'destination') in n.metadata.labels.items()):
        destination_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)


copy_file_between_nodes(source_node, destination_node, path)

pod_list = v1.list_namespaced_pod('default', label_selector="app=td")
for pod in pod_list.items:
    if("td-deployment" in pod.metadata.name):
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')

