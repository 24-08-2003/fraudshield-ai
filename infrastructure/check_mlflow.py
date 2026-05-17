import requests, json, traceback
out = {'status': None, 'text': None, 'error': None}
try:
    resp = requests.post('http://localhost:5000/api/2.0/mlflow/registered-models/search', json={})
    out['status'] = resp.status_code
    out['text'] = resp.text
except Exception as e:
    out['error'] = traceback.format_exc()
with open('mlflow_models.json','w', encoding='utf-8') as f:
    f.write(json.dumps(out))
print('WROTE')
