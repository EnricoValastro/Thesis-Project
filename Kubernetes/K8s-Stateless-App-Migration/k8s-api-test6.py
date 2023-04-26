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

res = v1.list_node()
for node in res.items:
    if (('migration', 'toThis') in node.metadata.labels.items()):
        res1 = v1.patch_node(node.metadata.name, fromThis)
    elif (('migration', 'fromThis') in node.metadata.labels.items()):
        res2 = v1.patch_node(node.metadata.name, toThis)
