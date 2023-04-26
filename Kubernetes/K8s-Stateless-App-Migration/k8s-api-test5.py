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
res = v1.patch_node('k8-2', fromThis)
res2 = v1.patch_node('k8-3', toThis)