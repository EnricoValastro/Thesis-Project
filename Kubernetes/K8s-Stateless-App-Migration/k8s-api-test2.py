from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()
print("K8s python client api test 2 !!")
print("Deleting Pod:")
api_response = v1.delete_namespaced_pod('todo-deployment-64c9c99796-9476m', 'default', pretty='true')
print(api_response)