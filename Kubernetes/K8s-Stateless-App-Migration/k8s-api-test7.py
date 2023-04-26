from kubernetes import client, config

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

#change node labels
res = v1.list_node()
for node in res.items:
    if (('migration', 'toThis') in node.metadata.labels.items()):
        res1 = v1.patch_node(node.metadata.name, fromThis)
    elif (('migration', 'fromThis') in node.metadata.labels.items()):
        res2 = v1.patch_node(node.metadata.name, toThis)


ret = v1.list_namespaced_pod('default')
for pod in ret.items:
    if("nginx-depl" in pod.metadata.name):
        api_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        if(api_response):
            print("Pod "+pod.metadata.name+" deleted")