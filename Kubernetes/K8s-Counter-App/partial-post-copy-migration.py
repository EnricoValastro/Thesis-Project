from kubernetes import client, config
import subprocess
import datetime;
import time
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
path= "/home/cb0/counter"
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
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete counter {user}{destination_node}:{dpath}'
    execute_command(copy_step2)


def partial_migration(source_node,destination_node,path):
    get_history = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path}/clientHistory.txt .'
    execute_command(get_history)

    with open('clientHistory.txt', 'r') as file:
        clients = file.readlines()
        last_client = clients[-1]
        print(last_client)

    last_client = last_client.strip('\n')
    copy_moste_recent_modified_file1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path}/{last_client}.txt .'
    print(copy_moste_recent_modified_file1)
    execute_command(copy_moste_recent_modified_file1)

    copy_moste_recent_modified_file2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete {last_client}.txt {user}{destination_node}:{dpath}/counter'
    execute_command(copy_moste_recent_modified_file2)

node_list = v1.list_node()

# Migration start
migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Get node list, find source and destination ip, swap labels.
for n in node_list.items:
    if (('type', 'source') in n.metadata.labels.items()):
        source_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('type', 'destination') in n.metadata.labels.items()):
        destination_node = n.status.addresses[0].address
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)


pod_list = v1.list_namespaced_pod('default', label_selector="app=server")
for pod in pod_list.items:
    if("server-deployment" in pod.metadata.name):
        # App migration start
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        
        # Downtime begin
        downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

        res = v1.list_namespaced_pod('default', label_selector="app=server")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                    break
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app=server")

# State migration begin
state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Find and migrate the most recent modified file
partial_migration(source_node,destination_node,path)

downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())

copy_file_between_nodes(source_node, destination_node, path)

# State migration end
state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())
migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

tot_time = migration_end - migration_start
data_migration_time = state_migration_end - state_migration_start
downtime = downtime_end - downtime_begin

print("Total time: "+str(tot_time))
print("State migration: "+str(data_migration_time))
print("Downtime: "+str(downtime))
