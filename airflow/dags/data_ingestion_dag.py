"""
FraudShield AI — Airflow DAG: Daily Data Ingestion
Pulls new transaction data on a daily schedule.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.hooks.base import BaseHook

ML_DIR = "/opt/airflow/ml"

default_args = {
    "owner": "fraudshield",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=3),
}


def generate_incremental_data(**context):
    """Generate incremental data (simulates pulling from upstream API)."""
    import sys
    sys.path.insert(0, f"{ML_DIR}/src")

    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    from pathlib import Path

    np.random.seed(int(datetime.utcnow().timestamp()) % 1000)
    n_samples = np.random.randint(500, 2000)
    fraud_ratio = 0.02

    # Import and use the ingestion module
    from data_ingestion import generate_transactions

    df = generate_transactions(
        n_samples=n_samples,
        fraud_ratio=fraud_ratio,
        random_state=int(datetime.utcnow().timestamp()) % 10000,
    )

    date_str = context["ds"]
    output_path = Path(f"{ML_DIR}/data/raw/incremental_{date_str}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ Ingested {len(df)} transactions for {date_str}")
    return {"n_transactions": len(df), "date": date_str}


def validate_incremental(**context):
    """Quick validation of incremental data."""
    import json
    from pathlib import Path
    import pandas as pd

    date_str = context["ds"]
    data_path = Path(f"{ML_DIR}/data/raw/incremental_{date_str}.csv")

    if not data_path.exists():
        raise FileNotFoundError(f"No incremental data found for {date_str}")

    df = pd.read_csv(data_path)

    issues = []
    if df.isnull().sum().sum() > 0:
        issues.append("Null values detected")
    if not set(["amount", "is_fraud", "transaction_id"]).issubset(df.columns):
        issues.append("Missing required columns")
    if len(df) == 0:
        issues.append("Empty dataset")
    if df["amount"].lt(0).any():
        issues.append("Negative amounts detected")

    result = {
        "date": date_str,
        "n_rows": len(df),
        "issues": issues,
        "passed": len(issues) == 0,
    }

    report_path = Path(f"{ML_DIR}/data/raw/validation_incremental_{date_str}.json")
    with open(report_path, "w") as f:
        json.dump(result, f, indent=2)

    if issues:
        raise ValueError(f"Validation issues: {issues}")

    print(f"✅ Incremental data validated: {len(df)} rows, no issues")


with DAG(
    dag_id="data_ingestion_pipeline",
    description="Daily transaction data ingestion pipeline",
    default_args=default_args,
    schedule_interval="0 6 * * *",  # Daily at 6 AM
    catchup=False,
    tags=["fraud-detection", "data-ingestion"],
    max_active_runs=1,
) as dag:

    start = EmptyOperator(task_id="start")

    ingest = PythonOperator(
        task_id="ingest_incremental_data",
        python_callable=generate_incremental_data,
        doc_md="Pull/generate new transaction data for the day",
    )

    validate = PythonOperator(
        task_id="validate_incremental_data",
        python_callable=validate_incremental,
        doc_md="Quick quality check on incremental data",
    )

    archive_old = BashOperator(
        task_id="archive_old_data",
        bash_command=(
            f"find {ML_DIR}/data/raw -name 'incremental_*.csv' "
            "-mtime +30 -exec gzip {} \\; "
            "|| true"
        ),
        doc_md="Compress incremental files older than 30 days",
    )

    end = EmptyOperator(task_id="end")

    start >> ingest >> validate >> archive_old >> end
