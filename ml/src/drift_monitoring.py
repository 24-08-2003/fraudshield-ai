"""FraudShield AI — Evidently AI Drift Monitoring.

Detects data drift and target drift between the reference training
distribution and the most recent production data window.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

import pickle
from typing import Any

import numpy as np
import pandas as pd

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    ClassificationPreset,
    TargetDriftPreset,
)
from evidently.metrics import (
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
    ColumnDriftMetric,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "data" / "drift_reports"

NUMERIC_FEATURES = [
    "amount", "hour_of_day", "day_of_week", "transaction_count_1h",
    "transaction_count_24h", "amount_mean_1h", "amount_std_1h",
    "merchant_risk_score", "distance_from_home", "velocity_score",
]
CATEGORICAL_FEATURES = ["merchant_category", "card_type", "entry_mode"]


def load_reference_data() -> pd.DataFrame:
    """Load the first 60 % of the raw CSV as the reference distribution.

    Returns:
        DataFrame representing the stable training-time distribution.
    """
    raw_path = ROOT / "data" / "raw" / "transactions.csv"
    df = pd.read_csv(raw_path)
    n_ref = int(len(df) * 0.6)
    return df.iloc[:n_ref].copy()


def load_current_data() -> pd.DataFrame:
    """Load the last 20 % of the raw CSV to simulate recent production data.

    Returns:
        DataFrame representing the current production distribution.
    """
    raw_path = ROOT / "data" / "raw" / "transactions.csv"
    df = pd.read_csv(raw_path)
    n_ref = int(len(df) * 0.8)
    return df.iloc[n_ref:].copy()


def run_drift_report(
    reference: pd.DataFrame, current: pd.DataFrame
) -> dict[str, Any]:
    """Run an Evidently drift report and return a JSON-serialisable summary.

    Persists both an HTML visualisation and a JSON summary, with the
    latest report also written to ``latest_drift_report.json``.

    Args:
        reference: Reference dataset (training distribution).
        current: Current dataset (recent production window).

    Returns:
        Summary dictionary containing drift flags, drift share, and
        per-column drift scores.
    """
    column_mapping = ColumnMapping(
        target="is_fraud",
        numerical_features=NUMERIC_FEATURES,
        categorical_features=CATEGORICAL_FEATURES,
    )

    report = Report(metrics=[
        DatasetDriftMetric(),
        DatasetMissingValuesMetric(),
        DataDriftPreset(),
    ])

    report.run(
        reference_data=reference,
        current_data=current,
        column_mapping=column_mapping,
    )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    html_path = REPORTS_DIR / f"drift_report_{timestamp}.html"
    json_path = REPORTS_DIR / f"drift_report_{timestamp}.json"
    latest_json = REPORTS_DIR / "latest_drift_report.json"

    report.save_html(str(html_path))

    result_dict = report.as_dict()

    # Extract key metrics for summary
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "n_reference": len(reference),
        "n_current": len(current),
        "dataset_drift_detected": False,
        "drift_share": 0.0,
        "drifted_columns": [],
        "column_drift_scores": {},
    }

    for metric_result in result_dict.get("metrics", []):
        if metric_result["metric"] == "DatasetDriftMetric":
            res = metric_result["result"]
            summary["dataset_drift_detected"] = res.get("dataset_drift", False)
            summary["drift_share"] = res.get("drift_share", 0.0)
            summary["n_drifted_columns"] = res.get("number_of_drifted_columns", 0)

        if metric_result["metric"] == "DataDriftTable":
            for col_result in metric_result.get("result", {}).get("drift_by_columns", {}).values():
                col_name = col_result.get("column_name", "unknown")
                drift_score = col_result.get("drift_score", 0.0)
                drift_detected = col_result.get("drift_detected", False)
                summary["column_drift_scores"][col_name] = {
                    "score": float(drift_score),
                    "drift_detected": drift_detected,
                }
                if drift_detected:
                    summary["drifted_columns"].append(col_name)

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    with open(latest_json, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"   Drift report saved: {html_path}")
    logger.info(f"   Dataset drift: {summary['dataset_drift_detected']}")
    logger.info(f"   Drift share: {summary['drift_share']:.2%}")
    logger.info(f"   Drifted columns: {summary['drifted_columns']}")

    return summary


def main() -> None:
    """Entry point: load reference/current data, run drift report, log results."""
    logger.info("🔍 Running Evidently AI drift monitoring...")
    reference = load_reference_data()
    current = load_current_data()
    summary = run_drift_report(reference, current)

    if summary["dataset_drift_detected"]:
        logger.warning("⚠️  DATA DRIFT DETECTED — Consider retraining the model!")
    else:
        logger.info("✅ No significant data drift detected.")


if __name__ == "__main__":
    main()
