# KubernetesPodOperator on Airflow
The KubernetesPodOperator on Airflow is a very powerful operator. It allows you to build and run any image in a Kubernetes cluster. This is particularly useful if you have enough DAGs inside your Airflow server that you start to run into dependency conflicts.

Things you'll need before you can run the KubernetesPodOperator on Airflow:
1. A Kubernetes cluster. Have the kubeconfig file available on your Airflow server for your DAG to point to.
2. A registry to pull your image from. Here I will simply use the [Docker Registry](https://docs.docker.com/registry/).

## Preparations
This simple demonstration will show how to use secrets and configmaps from a Kubernetes cluster in a KubernetesPodOperator, so the first step should be to create those resources in our cluster.

### Create Kubernetes resouces
To create the configmap, run

```
# kubectl create configmap NAME --from-env-file=/path/to/file
kubectl create configmap airflow-configmap --from-env-file=configmap.txt
```

To create the secret, run 
```
# kubectl create secret generic NAME --from-file=/path/to/file
kubectl create secret generic airflow-secret --from-file=secret.json
```

### Docker Registry
Next step is to set up the Docker Registry. The `docker_registry_command.sh` file contains a docker run command for spinning up a registry container. With the registry container up, build the image inside `python_image/` and give it a tag so that it points to your registry, then push it
```console
cd python_image
docker build -t localhost:5000/python_script .
docker push localhost:5000/python_script
```

To check if the image has been successfully pushed to the registry, go to `http://localhost:5000/v2/_catalog`.

## `kubepod_DAG.py`
With these initial steps completed, the `kubepod` DAG can be run. The DAG contains two tasks. The first communicates with a Kubernetes cluster to perform a simple task from within that cluster, which is to run `script.py` inside `python_image/`. This script will get the values of the secret and the configmap we just created. The second task is a `BashOperator` that gets the output from the XCom passed by the `KubernetesPodOperator`.
