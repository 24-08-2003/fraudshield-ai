"""
FraudShield AI — Model Evaluation
Evaluates trained models on hold-out test set, logs to MLflow, and saves metrics/plots.
"""
import json
import logging
import pickle
from pathlib import Path

import mlflow
import numpy as np
import yaml
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "params.yaml"
PROCESSED_DIR = ROOT / "data" / "processed"
PLOTS_DIR = PROCESSED_DIR / "plots"


def load_params() -> dict:
    with open(PARAMS_PATH) as f:
        return yaml.safe_load(f)


def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def evaluate_model(model, X_test, y_test, threshold: float = 0.5) -> dict:
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "auc_pr": float(average_precision_score(y_test, y_proba)),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "specificity": float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
    }
    return metrics, y_proba


def build_roc_curve_data(y_test, y_proba) -> list[dict]:
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    step = max(1, len(fpr) // 200)
    return [
        {"fpr": float(f), "tpr": float(t), "threshold": float(th)}
        for f, t, th in zip(fpr[::step], tpr[::step], thresholds[::step])
    ]


def build_pr_curve_data(y_test, y_proba) -> list[dict]:
    prec, rec, thresholds = precision_recall_curve(y_test, y_proba)
    step = max(1, len(prec) // 200)
    return [
        {"precision": float(p), "recall": float(r)}
        for p, r in zip(prec[::step], rec[::step])
    ]


def build_cm_data(y_test, y_proba, threshold: float) -> list[dict]:
    y_pred = (y_proba >= threshold).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    labels = ["Legitimate", "Fraud"]
    result = []
    for i, actual in enumerate(labels):
        for j, predicted in enumerate(labels):
            result.append({
                "actual": actual,
                "predicted": predicted,
                "count": int(cm[i, j]),
            })
    return result


def main():
    params = load_params()
    eval_params = params["evaluation"]
    threshold = eval_params.get("threshold", 0.5)

    mlflow.set_tracking_uri(params["mlflow"].get("tracking_uri", "http://localhost:5000"))
    mlflow.set_experiment(params["mlflow"]["experiment_name"])

    logger.info("📥 Loading test data and models...")
    X_test = load_pickle(PROCESSED_DIR / "X_test.pkl")
    y_test = load_pickle(PROCESSED_DIR / "y_test.pkl")

    with open(PROCESSED_DIR / "run_ids.json") as f:
        run_ids = json.load(f)

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    all_metrics = {}
    best_model_name = None
    best_f1 = -1.0

    for model_name in ["xgboost", "lightgbm"]:
        model_path = PROCESSED_DIR / "models" / f"{model_name}_model.pkl"
        model = load_pickle(model_path)

        metrics, y_proba = evaluate_model(model, X_test, y_test, threshold)
        all_metrics[model_name] = metrics

        logger.info(
            f"📊 {model_name.upper()} Test — "
            f"F1: {metrics['f1']:.4f} | AUC-PR: {metrics['auc_pr']:.4f} | "
            f"ROC-AUC: {metrics['roc_auc']:.4f}"
        )

        # Log to existing MLflow run
        run_id = run_ids[model_name]["run_id"]
        with mlflow.start_run(run_id=run_id):
            mlflow.log_metrics({f"test_{k}": v for k, v in metrics.items()
                                 if isinstance(v, float)})

        # Save plots
        roc_data = build_roc_curve_data(y_test, y_proba)
        pr_data = build_pr_curve_data(y_test, y_proba)
        cm_data = build_cm_data(y_test, y_proba, threshold)

        with open(PLOTS_DIR / f"{model_name}_roc_curve.json", "w") as f:
            json.dump(roc_data, f)
        with open(PLOTS_DIR / f"{model_name}_pr_curve.json", "w") as f:
            json.dump(pr_data, f)
        with open(PLOTS_DIR / f"{model_name}_confusion_matrix.json", "w") as f:
            json.dump(cm_data, f)

        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_model_name = model_name

    # Save combined metrics (DVC metrics file)
    combined_metrics = {
        "best_model": best_model_name,
        "best_f1": best_f1,
        **{f"{k}_{m}": v for k, mv in all_metrics.items() for m, v in mv.items()},
    }
    with open(PROCESSED_DIR / "metrics.json", "w") as f:
        json.dump(combined_metrics, f, indent=2)

    # Symlink best model plots for DVC
    for plot_type in ["roc_curve", "pr_curve", "confusion_matrix"]:
        src = PLOTS_DIR / f"{best_model_name}_{plot_type}.json"
        dst = PLOTS_DIR / f"{plot_type}.json"
        if dst.exists():
            dst.unlink()
        dst.write_text(src.read_text())

    logger.info(f"✅ Evaluation complete. Best model: {best_model_name} (F1={best_f1:.4f})")

    # Validate minimum performance
    min_f1 = eval_params.get("min_f1_score", 0.85)
    if best_f1 < min_f1:
        logger.warning(f"⚠️  Best F1 {best_f1:.4f} below minimum threshold {min_f1}")


if __name__ == "__main__":
    main()
