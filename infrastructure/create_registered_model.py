import json, traceback
from mlflow.tracking import MlflowClient
out={'created': None, 'models': None, 'error': None}
try:
    client = MlflowClient(tracking_uri='http://mlflow:5000')
    try:
        client.create_registered_model('fraudshield_classifier')
        out['created'] = True
    except Exception as e:
        out['created'] = False
    models = client.search_registered_models()
    names = []
    for m in models:
        # support both result shapes
        if hasattr(m, 'registered_model') and getattr(m.registered_model, 'name', None):
            names.append(m.registered_model.name)
        elif hasattr(m, 'name'):
            names.append(m.name)
        else:
            names.append(str(m))
    out['models'] = names
except Exception:
    out['error'] = traceback.format_exc()
print(json.dumps(out))
