from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes import secret
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

default_args = {
    'owner': 'Sean Sy',
    'depends_on_past': False,
    'start_date': datetime(2021,1,1),
    'email': 'seannevintsy@gmail.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

secret_volume = secret.Secret(
    deploy_type='volume',
    # Path where we mount the secret as volume
    deploy_target='/var/secrets',
    # Name of Kubernetes Secret
    secret='airflow-secret',
    # Key in the form of file name
    key='secret.json'
)

with DAG(
    'kubepod', default_args=default_args, schedule_interval=None
) as dag:

    kube_task = KubernetesPodOperator(
        task_id='kube_task',
        # Path to kubeconfig file of the Kubernetes cluster to use
        config_file='/opt/airflow/.kube/config',
        # Kubernetes namespace
        namespace='default',
        # Name of Kubernetes pod
        name='kube_task',
        # Image from some registry
        image='localhost:5000/python_script',
        cmds=['python','script.py'],
        # If True the content of the file /airflow/xcom/return.json in the
        # container will also be pushed to an XCom when the container completes
        do_xcom_push=True,
        # Delete pod after task is done
        is_delete_operator_pod=True,
        in_cluster=False,
        get_logs=True,
        startup_timeout_seconds=300,
        # The secrets to pass to Pod, the Pod will fail to create if the
        # secrets you specify in a Secret object do not exist in Kubernetes.
        secrets=[secret_volume],
        configmaps=['airflow-configmap']
    )

    echo_result = BashOperator(
        task_id='echo_result',
        bash_command='echo "{{ task_instance.xcom_pull(task_ids=\'kube_task\') }}"'
    ) 

    kube_task >> echo_result
