from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz


def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copia i file dal nfs servr al nodo master
    copy_step1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}192.168.42.157:{path} .'
    execute_command(copy_step1)

    # Copia i file dal nodo master al nodo di destinazione
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete pvc {user}{destination_node}:{dpath}'
    execute_command(copy_step2)

config.load_kube_config()
v1 = client.CoreV1Api()

# Prepara la patch da applicare ai nodi per indurre k8s a spostare PV dal nodo attuale al nodo di 
# destinazione. Questo script utilizza label diversi rispetto agli altri, perchè per il caso nfs 
# è stato effettuato un deployment differente
source = {
        "metadata": {
            "labels": {
                "nd": "1"
            }
        }
}
destination = {
        "metadata": {
            "labels": {
                "nd": "2"
            }
        }
}

date_format = '%Y-%m-%d %H:%M:%S%z'

user="cb0@"
path= "/home/cb0/nfs/pvc"
dpath= "/home/cb0/nfs"

# Migration start
migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Copia dal nfs server al master node il file clientHistory
get_history = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}192.168.42.157:{path}/clientHistory.txt .'
execute_command(get_history)

# Legge dal file chi è l'ultimo cliente
with open('clientHistory.txt', 'r') as file:
    clients = file.readlines()
    last_client = clients[-1]

last_client = last_client.strip('\n')

# Ottiene la lista dei nodi
node_list = v1.list_node()

# Sulla base del label del nodo capisco qual'è la sorgente e quale è la destinazione, switch dei label 
# per indurre k8s a spostare il PV da un nodo all'altro
for n in node_list.items:
    if (('nd', '1') in n.metadata.labels.items()):
        source_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('nd', '2') in n.metadata.labels.items()):
        destination_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)

# State migration begin
state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Copia parziale del file relativo all'ultimo cliente dal nodo sorgente al nodo master
copy_moste_recent_modified_file1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}192.168.42.157:{path}/{last_client}.txt .'
execute_command(copy_moste_recent_modified_file1)

# Copia parziale del file relativo all'ultimo cliente dal nodo master al nodo destinazione
copy_moste_recent_modified_file2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete {last_client}.txt {user}{destination_node}:{dpath}/pvc'
execute_command(copy_moste_recent_modified_file2)

# State migration end
state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

# Richiedo la lista dei pod (è unico) con label "app=server-v2"
pod_list = v1.list_namespaced_pod('default', label_selector="app=server-v2")
for pod in pod_list.items:
    if("server-deployment-with-nfs" in pod.metadata.name):
        # Elimino il pod inducendo k8s a richedularlo. Il pod sarà schedulato sul nodo in cui si trova il PV
        # quindi nel nodo destinazione
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        
        # Downtime begin
        downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

        # Attendo attivamente che il pod torni up and running
        res = v1.list_namespaced_pod('default', label_selector="app=server-v2")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                    break
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app=server-v2")
        # Il pod è up e running sul nodo destinazione
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