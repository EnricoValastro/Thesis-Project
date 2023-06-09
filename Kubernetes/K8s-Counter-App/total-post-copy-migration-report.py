from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz
import time
import statistics

# This script perform a post-copy stateful migration.

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

pod_name = ""

fp1 = open("report/downtimeReport.txt", "a")
fp2 = open("report/totalTimeReport.txt", "a")
fp3 = open("report/dataTransferReport.txt", "a")

tot=[]
down=[]
data=[]

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copy file from source node to master node
    copy_step1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path} .'
    execute_command(copy_step1)

    # Copy file from master node to destination node
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete counter {user}{destination_node}:{dpath}'
    execute_command(copy_step2)


for i in range(0,33):

    for j in range(0,33):

        # Migration start
        migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

        node_list = v1.list_node()

        for n in node_list.items:
            if (('type', 'source') in n.metadata.labels.items()):
                source_node = n.status.addresses[0].address
                patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
            elif (('type', 'destination') in n.metadata.labels.items()):
                destination_node = n.status.addresses[0].address
                patch_node_lab_res = v1.patch_node(n.metadata.name, source)

        # Get target pod
        pod_list = v1.list_namespaced_pod('default', label_selector="app=server")

        for pod in pod_list.items:
            if("server-deployment" in pod.metadata.name):
                # App migration start
                delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
                
                # Downtime begin
                downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

                res = v1.list_namespaced_pod('default', label_selector="app=server")
                x = True
                # Wait until pod is up and running
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

        copy_file_between_nodes(source_node, destination_node, path)

        # State migration end
        state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())
        migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        tot_time = migration_end - migration_start
        data_migration_time = state_migration_end - state_migration_start
        downtime = downtime_end - downtime_begin

        tot.append(tot_time)
        down.append(downtime)
        data.append(data_migration_time)

    fp1.write(str(statistics.mean(down))+",\n")
    fp2.write(str(statistics.mean(tot))+",\n")
    fp3.write(str(dstatistics.mean(data))+",\n")

    time.sleep(1.5)