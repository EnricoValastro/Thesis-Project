from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()


res = v1.list_node()
for node in res.items:
    if (('migration', 'toThis') in node.metadata.labels.items()):
        print(node.metadata.name)