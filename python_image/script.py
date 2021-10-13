import ast
import json
import os

configmap = os.environ['configmapkey']
secret = ''

# Read secret from mounted volume
with open('/var/secrets/secret.json','r') as f:
    s = json.load(f)
    secret = s['secret']

output = {
    'configmap': configmap,
    'secret': secret
}

# Write to xcom output file
with open('/airflow/xcom/return.json','w+') as f:
    json.dump(output, f)
