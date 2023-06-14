# *********************************************************************************************************
#                 This script perform multiple pre-copy stateful migration and collect data.
# *********************************************************************************************************
from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz
import time 
import statistics

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

avg_tot_time = []
avg_downtime = []
avg_data_migration_time = []

fp1 = open("report/pre-copy/tot-time-report.txt", "a")
fp2 = open("report/pre-copy/downtime-report.txt", "a")
fp3 = open("report/pre-copy/data-time-report.txt", "a")

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


for i in range(0,10):
    print("**************** Round: " + str(i)+" ****************" )
    for j in range(0,16):
        print("******* Run: "+str(j)+" *******")
        # Migration start
        migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

        # Richiede la lista dei nodi
        node_list = v1.list_node()

        # Get node list, find source and destination ip, swap labels.
        print("Patching Node Labels")
        for n in node_list.items:
            if (('type', 'source') in n.metadata.labels.items()):
                source_node = n.status.addresses[0].address
                patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
            elif (('type', 'destination') in n.metadata.labels.items()):
                destination_node = n.status.addresses[0].address
                patch_node_lab_res = v1.patch_node(n.metadata.name, source)

        print("Moving state from source to destination") 
        # State migration begin
        state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

        # Move file between node
        copy_file_between_nodes(source_node, destination_node, path)

        # State migration end
        state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        pod_list = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
        for pod in pod_list.items:
            if("ekuiper" in pod.metadata.name):
                print("Killing pod: "+str(pod.metadata.name))
                # App migration start
                delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
                
                # Downtime begin
                downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

                print("Waiting for pod restart...")
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
                print("Pod up and running")
                downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())
                migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        tot_time = migration_end - migration_start
        data_migration_time = state_migration_end - state_migration_start
        downtime = downtime_end - downtime_begin

        avg_tot_time.append(float(str(tot_time).split(":")[2]))
        avg_downtime.append(float(str(downtime).split(":")[2]))
        avg_data_migration_time.append(float(str(data_migration_time).split(":")[2]))

        time.sleep(3)
    
    fp1.write(str(statistics.mean(avg_tot_time))+",\n")
    fp2.write(str(statistics.mean(avg_downtime))+",\n")
    fp3.write(str(statistics.mean(avg_data_migration_time))+",\n")

fp1.close()
fp2.close()
fp3.close()

