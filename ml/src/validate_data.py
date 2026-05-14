"""FraudShield AI — Great Expectations Data Validation.

Validates raw transaction data against the ``fraud_data_suite``
expectations before any training step, and writes a JSON report.
"""
import json
import logging
import sys
from pathlib import Path

import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "transactions.csv"
GE_DIR = ROOT / "great_expectations"
OUTPUT_PATH = ROOT / "data" / "raw" / "validation_report.json"


def run_validation() -> bool:
    """Run the Great Expectations checkpoint against the raw transaction CSV.

    Loads ``data/raw/transactions.csv``, runs the ``fraud_data_checkpoint``
    checkpoint, and writes a JSON summary report to
    ``data/raw/validation_report.json``.

    Returns:
        ``True`` if all expectations pass, ``False`` otherwise.
    """
    logger.info("📋 Running Great Expectations validation...")

    df = pd.read_csv(RAW_PATH)
    context = gx.get_context(context_root_dir=str(GE_DIR))

    datasource = context.sources.add_or_update_pandas(name="transactions_source")
    asset = datasource.add_dataframe_asset(name="transactions")
    batch_request = asset.build_batch_request(dataframe=df)

    checkpoint_result = context.run_checkpoint(
        checkpoint_name="fraud_data_checkpoint",
        batch_request=batch_request,
    )

    results = checkpoint_result.run_results
    success = checkpoint_result.success

    # Compile report
    report = {
        "success": success,
        "n_rows": len(df),
        "n_fraud": int(df["is_fraud"].sum()),
        "fraud_rate": float(df["is_fraud"].mean()),
        "validation_results": [],
    }

    for result_key, result_val in results.items():
        for er in result_val.results:
            report["validation_results"].append({
                "expectation_type": er.expectation_config.expectation_type,
                "success": er.success,
                "column": er.expectation_config.kwargs.get("column", "N/A"),
            })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    n_pass = sum(1 for r in report["validation_results"] if r["success"])
    n_fail = len(report["validation_results"]) - n_pass

    logger.info(f"   Expectations: {n_pass} passed, {n_fail} failed")
    logger.info(f"   Overall: {'✅ PASS' if success else '❌ FAIL'}")

    return success


if __name__ == "__main__":
    ok = run_validation()
    sys.exit(0 if ok else 1)
