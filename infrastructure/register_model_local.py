import json, traceback
from sklearn.dummy import DummyClassifier
from sklearn.datasets import load_iris
import mlflow, mlflow.sklearn
from mlflow.tracking import MlflowClient
out={'ok': False, 'error': None}
try:
    X,y = load_iris(return_X_y=True)
    clf = DummyClassifier(strategy='most_frequent')
    clf.fit(X,y)
    mlflow.set_tracking_uri('http://localhost:5000')
    client = MlflowClient(tracking_uri='http://localhost:5000')
    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(clf, 'model')
        run_id = run.info.run_id
        mv = client.create_model_version(name='fraudshield_classifier', source='runs:/' + run_id + '/model', run_id=run_id)
        client.transition_model_version_stage(name='fraudshield_classifier', version=mv.version, stage='Production', archive_existing_versions=True)
    out['ok'] = True
except Exception as e:
    out['error'] = traceback.format_exc()
with open('register_result.json','w', encoding='utf-8') as f:
    f.write(json.dumps(out))
print('WROTE')
