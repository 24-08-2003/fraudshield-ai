"""
FraudShield AI — Airflow DAG: Full ML Training Pipeline
Orchestrates: data ingestion → validation → preprocessing → training → evaluation → model registration
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule

ML_DIR = "/opt/airflow/ml"

default_args = {
    "owner": "fraudshield",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def check_validation_result(**context):
    """Branch: only proceed to training if validation passed."""
    import json
    import os

    result_path = f"{ML_DIR}/data/raw/validation_report.json"
    if not os.path.exists(result_path):
        return "validation_failed"

    with open(result_path) as f:
        report = json.load(f)

    if report.get("success", False):
        return "run_preprocessing"
    return "validation_failed"


def check_model_quality(**context):
    """Branch: only register if model meets quality bar."""
    import json
    import os

    metrics_path = f"{ML_DIR}/data/processed/metrics.json"
    if not os.path.exists(metrics_path):
        return "quality_gate_failed"

    with open(metrics_path) as f:
        metrics = json.load(f)

    if metrics.get("best_f1", 0) >= 0.85:
        return "register_model"
    return "quality_gate_failed"


with DAG(
    dag_id="fraud_training_pipeline",
    description="End-to-end MLOps training pipeline for FraudShield AI",
    default_args=default_args,
    schedule_interval="0 2 * * 1",  # Weekly on Monday at 2 AM
    catchup=False,
    tags=["fraud-detection", "mlops", "training"],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id="start")

    ingest_data = BashOperator(
        task_id="ingest_data",
        bash_command=f"cd {ML_DIR} && python src/data_ingestion.py",
        doc_md="Generate/fetch raw transaction data",
    )

    validate_data = BashOperator(
        task_id="validate_data",
        bash_command=f"cd {ML_DIR} && python src/validate_data.py",
        doc_md="Run Great Expectations validation suite",
    )

    branch_validation = BranchPythonOperator(
        task_id="branch_validation_check",
        python_callable=check_validation_result,
    )

    validation_failed = BashOperator(
        task_id="validation_failed",
        bash_command='echo "❌ Data validation FAILED. Pipeline halted." && exit 1',
    )

    run_preprocessing = BashOperator(
        task_id="run_preprocessing",
        bash_command=f"cd {ML_DIR} && python src/preprocessing.py",
        doc_md="Feature engineering, SMOTE, train/val/test splits",
    )

    train_model = BashOperator(
        task_id="train_model",
        bash_command=f"cd {ML_DIR} && python src/train.py",
        doc_md="Train XGBoost and LightGBM with MLflow tracking",
    )

    evaluate_model = BashOperator(
        task_id="evaluate_model",
        bash_command=f"cd {ML_DIR} && python src/evaluate.py",
        doc_md="Evaluate models on hold-out test set",
    )

    quality_gate = BranchPythonOperator(
        task_id="quality_gate",
        python_callable=check_model_quality,
    )

    quality_gate_failed = BashOperator(
        task_id="quality_gate_failed",
        bash_command='echo "⚠️  Model quality below threshold. Not registering." && exit 0',
    )

    register_model = BashOperator(
        task_id="register_model",
        bash_command=f"cd {ML_DIR} && python src/register_model.py",
        doc_md="Register best model to MLflow Model Registry",
    )

    run_drift_report = BashOperator(
        task_id="run_drift_report",
        bash_command=f"cd {ML_DIR} && python src/drift_monitoring.py",
        doc_md="Generate Evidently AI drift monitoring report",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_DONE)

    # DAG flow
    (
        start
        >> ingest_data
        >> validate_data
        >> branch_validation
        >> [validation_failed, run_preprocessing]
    )
    (
        run_preprocessing
        >> train_model
        >> evaluate_model
        >> quality_gate
        >> [quality_gate_failed, register_model]
    )
    [register_model, quality_gate_failed, validation_failed] >> run_drift_report >> end
