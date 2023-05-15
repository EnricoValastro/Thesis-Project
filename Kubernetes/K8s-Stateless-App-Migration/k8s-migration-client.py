from kubernetes import client, config
import datetime;
import dateutil.tz

config.load_kube_config()
v1 = client.CoreV1Api()

fromThis = {
        "metadata": {
            "labels": {
                "migration": "fromThis"
            }
        }
}
toThis = {
        "metadata": {
            "labels": {
                "migration": "toThis"
            }
        }
}
date_format = '%Y-%m-%d %H:%M:%S%z'

#migration procedure starts get timestamp:
migration_start_timestamp = datetime.datetime.now(dateutil.tz.tzlocal())
print(migration_start_timestamp.strftime(date_format))

#change node labels
res = v1.list_node()
for node in res.items:
    if (('migration', 'toThis') in node.metadata.labels.items()):
        patch_node_lab_res1 = v1.patch_node(node.metadata.name, fromThis)
        origin_node = node.metadata.name
    elif (('migration', 'fromThis') in node.metadata.labels.items()):
        patch_node_lab_res2 = v1.patch_node(node.metadata.name, toThis)
        destination_node = node.metadata.name

#get pod list and delete the target one
pod_list = v1.list_namespaced_pod('default', label_selector="app=nginx")
for pod in pod_list.items:
    if("nginx-depl" in pod.metadata.name):
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        deletion_pod_timestamp = datetime.datetime.now(dateutil.tz.tzlocal())
        print(deletion_pod_timestamp.strftime(date_format))
#get new pod list 
        res = v1.list_namespaced_pod('default', label_selector="app=nginx")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app=nginx")
        new_pod_up_running_timestamp = datetime.datetime.now(dateutil.tz.tzlocal())
        print(new_pod_up_running_timestamp.strftime(date_format))

downt = new_pod_up_running_timestamp - deletion_pod_timestamp
tot = new_pod_up_running_timestamp - migration_start_timestamp

print("Duration of the migration process : " + str(tot))
print("Service downtime: " + str(downt))

