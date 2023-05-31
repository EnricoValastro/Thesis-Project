from kubernetes import client, config
import subprocess
import statistics
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
path= "/home/cb0/state"
dpath= "/home/cb0"

date_format = '%Y-%m-%d %H:%M:%S%z'

fp1 = open("downtimeReport.txt", "a")
fp2 = open("totalTimeReport.txt", "a")
fp3 = open("dataTransferReport.txt", "a")

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def copy_file_between_nodes(source_node, destination_node, path):
    # Copy dir and file from source node to master node
    copy_step1 = f'sshpass -p "Birex2023" rsync -vrpohlg --delete {user}{source_node}:{path} .'
    execute_command(copy_step1)

    # Copy dir and file from master node to destination node
    copy_step2 = f' sshpass -p "Birex2023" rsync -vrpohlg --delete state {user}{destination_node}:{dpath}'
    execute_command(copy_step2)

for i in range(0,33):
    print("*************** Round: "+str(i)+" ***************")
    avg_time = []
    avg_downtime = []
    avg_data_transfer_time = [] 

    for j in range(0,33):

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
        
        # State migration begin
        state_migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

        copy_file_between_nodes(source_node, destination_node, path)

        # State migration end
        state_migration_end = datetime.datetime.now(dateutil.tz.tzlocal())

        pod_list = v1.list_namespaced_pod('default', label_selector="app=td")
        for pod in pod_list.items:
            if("td-deployment" in pod.metadata.name):
                # App migration start
                delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
                
                # Downtime begin
                downtime_start = datetime.datetime.now(dateutil.tz.tzlocal())

                res = v1.list_namespaced_pod('default', label_selector="app=td")
                x = True
                while(res.items[0].metadata.name == pod.metadata.name or x):
                    if(res.items[0].metadata.name != pod.metadata.name):
                        try:
                            res.items[0].status.container_statuses[0].state.running.started_at
                            x = False
                            break
                        except:
                            x = True
                    res = v1.list_namespaced_pod('default', label_selector="app=td")
                downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())
                migration_end = datetime.datetime.now(dateutil.tz.tzlocal())
        
        tot_time = migration_end - migration_start
        data_migration_time = state_migration_end - state_migration_start
        downtime = downtime_end - downtime_start
        print("Migration time: " +str(tot_time))
        print("Data migration time: " +str(data_migration_time))
        print("Downtime: " +str(downtime))

        avg_time.append(float(str(tot_time).split(":")[2]))
        avg_downtime.append(float(str(downtime).split(":")[2]))
        avg_data_transfer_time.append(float(str(data_migration_time).split(":")[2]))

        time.sleep(1.5)
    
    avg_time_mean = statistics.mean(avg_time)
    avg_downtime_mean = statistics.mean(avg_downtime)
    avg_data_transfer_time_mean = statistics.mean(avg_data_transfer_time)

    fp1.write(str(avg_downtime_mean)+",\n")
    fp2.write(str(avg_time_mean)+",\n")
    fp3.write(str(avg_data_transfer_time_mean)+",\n")

fp1.close()    
fp2.close()
fp3.close()