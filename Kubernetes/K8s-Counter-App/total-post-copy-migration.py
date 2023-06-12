from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz

# This script perform a post-copy stateful migration.

config.load_kube_config()
v1 = client.CoreV1Api()

# Prepara la patch da applicare ai nodi per indurre k8s a spostare PV dal nodo attuale al nodo di destinazione 
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
path= "/home/cb0/counter"
dpath= "/home/cb0"

date_format = '%Y-%m-%d %H:%M:%S%z'

pod_name = ""

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copia il file dal nodo di origine al nodo master
    copy_step1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path} .'
    execute_command(copy_step1)

    # Copia il file dal nodo master al nodo di destinazione
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete counter {user}{destination_node}:{dpath}'
    execute_command(copy_step2)

# Migration start
migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Ottiene la lista dei nodi
node_list = v1.list_node()

# Sulla base del label del nodo capisco qual'è la sorgente e quale è la destinazione, switch dei label 
# per indurre k8s a spostare il PV da un nodo all'altro
for n in node_list.items:
    if (('type', 'source') in n.metadata.labels.items()):
        source_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('type', 'destination') in n.metadata.labels.items()):
        destination_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)

# Richiedo la lista dei pod (è unico) con label "app=server"
pod_list = v1.list_namespaced_pod('default', label_selector="app=server")

for pod in pod_list.items:
    if("server-deployment" in pod.metadata.name):
        # Elimino il pod inducendo k8s a richedularlo. Il pod sarà schedulato sul nodo in cui si trova il PV
        # quindi nel nodo destinazione
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        
        # Downtime begin
        downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())
        
        # Attendo attivamente che il pod torni up and running
        res = v1.list_namespaced_pod('default', label_selector="app=server")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                pod_name = res.items[0].metadata.name
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                    break
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app=server")

# State migration begin
state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Sposto i dati dalla sorgente alla destinazione
copy_file_between_nodes(source_node, destination_node, path)

# State migration end
state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

# Downtime end
downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())

# Migration end
migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

tot_time = migration_end - migration_start
data_migration_time = state_migration_end - state_migration_start
downtime = downtime_end - downtime_begin

print("Total time: "+str(tot_time))
print("State migration: "+str(data_migration_time))
print("Downtime: "+str(downtime))
