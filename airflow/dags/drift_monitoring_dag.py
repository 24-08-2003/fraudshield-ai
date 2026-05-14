"""
FraudShield AI — Airflow DAG: Drift Monitoring
Daily Evidently AI drift report generation with alerting.
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
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_drift_analysis(**context):
    """Execute Evidently drift monitoring."""
    import sys
    sys.path.insert(0, f"{ML_DIR}/src")
    from drift_monitoring import main as run_drift
    run_drift()


def check_drift_threshold(**context):
    """Branch based on whether drift was detected."""
    import json
    from pathlib import Path

    latest_report = Path(f"{ML_DIR}/data/drift_reports/latest_drift_report.json")
    if not latest_report.exists():
        return "no_drift_detected"

    with open(latest_report) as f:
        report = json.load(f)

    drift_share = report.get("drift_share", 0.0)
    n_drifted = report.get("n_drifted_columns", 0)

    # Alert if >20% of features drift OR drift share > 0.3
    if drift_share > 0.3 or n_drifted >= 4:
        return "severe_drift_alert"
    elif report.get("dataset_drift_detected", False):
        return "mild_drift_detected"
    return "no_drift_detected"


def send_drift_alert(**context):
    """Log severe drift alert (in production, send Slack/PagerDuty)."""
    import json
    from pathlib import Path

    report_path = Path(f"{ML_DIR}/data/drift_reports/latest_drift_report.json")
    with open(report_path) as f:
        report = json.load(f)

    alert_msg = (
        f"🚨 SEVERE DATA DRIFT DETECTED\n"
        f"   Drift share: {report['drift_share']:.2%}\n"
        f"   Drifted columns: {report.get('drifted_columns', [])}\n"
        f"   Recommendation: Trigger model retraining immediately\n"
        f"   Report timestamp: {report['timestamp']}"
    )
    print(alert_msg)
    # In production: requests.post(slack_webhook, json={"text": alert_msg})


with DAG(
    dag_id="drift_monitoring_pipeline",
    description="Daily Evidently AI drift monitoring and alerting",
    default_args=default_args,
    schedule_interval="0 8 * * *",  # Daily at 8 AM
    catchup=False,
    tags=["fraud-detection", "monitoring", "drift"],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id="start")

    analyze_drift = PythonOperator(
        task_id="analyze_drift",
        python_callable=run_drift_analysis,
        doc_md="Generate Evidently AI drift report",
    )

    check_threshold = BranchPythonOperator(
        task_id="check_drift_threshold",
        python_callable=check_drift_threshold,
    )

    no_drift_detected = BashOperator(
        task_id="no_drift_detected",
        bash_command='echo "✅ No significant drift detected. Model remains stable."',
    )

    mild_drift_detected = BashOperator(
        task_id="mild_drift_detected",
        bash_command=(
            'echo "⚠️  Mild drift detected. Monitoring closely. '
            'Consider scheduling retraining within 1 week."'
        ),
    )

    severe_drift_alert = PythonOperator(
        task_id="severe_drift_alert",
        python_callable=send_drift_alert,
    )

    trigger_retraining = BashOperator(
        task_id="trigger_retraining",
        bash_command=(
            "airflow dags trigger fraud_training_pipeline "
            "--conf '{\"triggered_by\": \"drift_monitoring\"}' || true"
        ),
    )

    update_metrics_db = BashOperator(
        task_id="update_metrics_db",
        bash_command=f"cd {ML_DIR} && python src/drift_monitoring.py || true",
        trigger_rule=TriggerRule.ALL_DONE,
        doc_md="Ensure latest metrics are saved to database",
    )

    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_DONE)

    start >> analyze_drift >> check_threshold
    check_threshold >> [no_drift_detected, mild_drift_detected, severe_drift_alert]
    severe_drift_alert >> trigger_retraining
    [no_drift_detected, mild_drift_detected, trigger_retraining] >> update_metrics_db >> end
