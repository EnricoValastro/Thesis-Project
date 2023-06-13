# ******************************************************************************************************* #
#                                This script perform a post-copy stateful migration.                      #
# ******************************************************************************************************* #
from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz

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
path= "/home/cb0/kuiper"
dpath= "/home/cb0"

date_format = '%Y-%m-%d %H:%M:%S%z'


def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copia il file dal nodo di origine al nodo master
    copy_step1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path} .'
    execute_command(copy_step1)

    # Copia il file dal nodo master al nodo di destinazione
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete state {user}{destination_node}:{dpath}'
    execute_command(copy_step2)

# Migration start
migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Richiede la lista dei nodi
node_list = v1.list_node()

# Get node list, find source and destination ip, swap labels.
for n in node_list.items:
    if (('type', 'source') in n.metadata.labels.items()):
        source_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('type', 'destination') in n.metadata.labels.items()):
        destination_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)

pod_list = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
for pod in pod_list.items:
    if("ekuiper" in pod.metadata.name):
        # App migration start
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        
        # Downtime begin
        downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

        # State migration begin
        state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

        # Move file between node
        copy_file_between_nodes(source_node, destination_node, path)

        # State migration end
        state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        res = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                    break
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")

downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())
migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

tot_time = migration_end - migration_start
data_migration_time = state_migration_end - state_migration_start
downtime = downtime_end - downtime_begin

print("Total time: "+str(tot_time))
print("State migration: "+str(data_migration_time))
print("Downtime: "+str(downtime))