from kubernetes import client, config
import datetime;
import dateutil.tz

config.load_kube_config()
v1 = client.CoreV1Api()


#get pv list 
pv_list = v1.list_persistent_volume()
print(pv_list)

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

res = v1.list_node()
for node in res.items:
    if (('migration', 'toThis') in node.metadata.labels.items()):
        patch_node_lab_res1 = v1.patch_node(node.metadata.name, fromThis)
    elif (('migration', 'fromThis') in node.metadata.labels.items()):
        patch_node_lab_res2 = v1.patch_node(node.metadata.name, toThis)