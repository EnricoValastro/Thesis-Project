from kubernetes import client, config
import subprocess

config.load_kube_config()
v1 = client.CoreV1Api()