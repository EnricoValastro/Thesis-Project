from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()
ret = v1.list_namespaced_pod('default')
for pod in ret.items:
    if("nginx-depl" in pod.metadata.name):
        api_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        if(api_response):
            print("Pod "+pod.metadata.name+" deleted")