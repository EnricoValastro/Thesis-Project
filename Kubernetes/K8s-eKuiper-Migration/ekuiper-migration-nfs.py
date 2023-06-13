from kubernetes import client, config
import subprocess
import datetime;
import dateutil.tz

config.load_kube_config()
v1 = client.CoreV1Api()
# Prepara la patch da applicare ai nodi per indurre k8s a spostare PV dal nodo attuale al nodo di 
# destinazione. Questo script utilizza label diversi rispetto agli altri, perchè per il caso nfs 
# è stato effettuato un deployment differente
source = {
        "metadata": {
            "labels": {
                "nd": "1"
            }
        }
}
destination = {
        "metadata": {
            "labels": {
                "nd": "2"
            }
        }
}

date_format = '%Y-%m-%d %H:%M:%S%z'

# Migration start
migration_start = datetime.datetime.now(dateutil.tz.tzlocal())

# Ottiene la lista dei nodi
node_list = v1.list_node()

# Sulla base del label del nodo capisco qual'è la sorgente e quale è la destinazione, switch dei label 
# per indurre k8s a spostare il PV da un nodo all'altro
for n in node_list.items:
    if (('nd', '1') in n.metadata.labels.items()):
        patch_node_lab_res = v1.patch_node(n.metadata.name, destination)
    elif (('nd', '2') in n.metadata.labels.items()):
        patch_node_lab_res = v1.patch_node(n.metadata.name, source)

# Richiedo la lista dei pod (è unico) con label "app=server"
pod_list = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
for pod in pod_list.items:
    if("ekuiper" in pod.metadata.name):
        # Elimino il pod inducendo k8s a richedularlo. Il pod sarà schedulato sul nodo in cui si trova il PV
        # quindi nel nodo destinazione
        delete_pod_response = v1.delete_namespaced_pod(pod.metadata.name, 'default')
        
        # Downtime begin
        downtime_begin = datetime.datetime.now(dateutil.tz.tzlocal())

        # Attendo attivamente che il pod torni up and running
        res = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
        x = True
        while(res.items[0].metadata.name == pod.metadata.name or x):
            if(res.items[0].metadata.name != pod.metadata.name):
                try:
                    res.items[0].status.container_statuses[0].state.running.started_at
                    x = False
                    break
                except:
                    x = True
            res = v1.list_namespaced_pod('default', label_selector="app.kubernetes.io/name=ekuiper")
        # Il pod è up e running sul nodo destinazione

        # Downtime end
        downtime_end = datetime.datetime.now(dateutil.tz.tzlocal())
        
        # Migration end
        migration_end = datetime.datetime.now(dateutil.tz.tzlocal())
        

tot_time = migration_end - migration_start
downtime = downtime_end - downtime_begin

print("Total time: "+str(tot_time))
print("Downtime: "+str(downtime))