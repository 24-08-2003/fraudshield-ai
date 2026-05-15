import json, traceback
from mlflow.tracking import MlflowClient
out={'models': None, 'error': None}
try:
    client = MlflowClient(tracking_uri='http://localhost:5000')
    models = client.search_registered_models()
    names = []
    for m in models:
        if hasattr(m, 'registered_model') and getattr(m.registered_model, 'name', None):
            names.append(m.registered_model.name)
        elif hasattr(m, 'name'):
            names.append(m.name)
        else:
            names.append(str(m))
    out['models'] = names
except Exception as e:
    out['error'] = traceback.format_exc()
with open('mlflow_models_client.json','w', encoding='utf-8') as f:
    f.write(json.dumps(out))
print('WROTE')
