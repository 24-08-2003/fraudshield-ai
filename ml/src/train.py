"""FraudShield AI — MLflow-Tracked Model Training.

Trains XGBoost and LightGBM classifiers on preprocessed fraud data
and logs all parameters, metrics, and model artefacts to MLflow.
"""
import json
import logging
import pickle
import sys
from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import yaml
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
import xgboost as xgb
import lightgbm as lgb

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "params.yaml"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = PROCESSED_DIR / "models"


def load_params() -> dict[str, Any]:
    """Load pipeline parameters from the YAML config file.

    Returns:
        Nested dictionary of pipeline parameters.
    """
    with open(PARAMS_PATH) as f:
        return yaml.safe_load(f)


def load_pickle(path: Path) -> Any:
    """Deserialize a pickle file from disk.

    Args:
        path: Path to the pickle file.

    Returns:
        Deserialized Python object.
    """
    with open(path, "rb") as f:
        return pickle.load(f)


def save_pickle(obj: Any, path: Path) -> None:
    """Serialize an object to a pickle file, creating parent dirs if needed.

    Args:
        obj: Any Python object to persist.
        path: Destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    """Compute classification metrics at a given decision threshold.

    Args:
        y_true: Ground-truth binary labels.
        y_pred: Hard predictions (unused — kept for API compatibility).
        y_proba: Predicted probabilities for the positive class.
        threshold: Decision threshold to binarise ``y_proba``.

    Returns:
        Dictionary with keys ``f1``, ``precision``, ``recall``,
        ``roc_auc``, and ``auc_pr``.
    """
    y_bin = (y_proba >= threshold).astype(int)
    return {
        "f1": float(f1_score(y_true, y_bin, zero_division=0)),
        "precision": float(precision_score(y_true, y_bin, zero_division=0)),
        "recall": float(recall_score(y_true, y_bin, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "auc_pr": float(average_precision_score(y_true, y_proba)),
    }


def train_xgboost(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    params: dict[str, Any],
) -> tuple[xgb.XGBClassifier, dict[str, float]]:
    """Train an XGBoost classifier with early stopping.

    Args:
        X_train: Training feature matrix.
        y_train: Training labels.
        X_val: Validation feature matrix.
        y_val: Validation labels.
        params: Full params dict; uses the ``xgboost`` sub-key.

    Returns:
        Tuple of (fitted XGBClassifier, validation metrics dict).
    """
    logger.info("🚀 Training XGBoost...")
    xgb_params = params["xgboost"].copy()
    eval_metric = xgb_params.pop("eval_metric", "aucpr")
    early_stopping = xgb_params.pop("early_stopping_rounds", 50)

    model = xgb.XGBClassifier(
        **xgb_params,
        use_label_encoder=False,
        eval_metric=eval_metric,
        verbosity=0,
    )
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        early_stopping_rounds=early_stopping,
        verbose=False,
    )
    y_proba = model.predict_proba(X_val)[:, 1]
    metrics = compute_metrics(y_val, model.predict(X_val), y_proba)
    logger.info(f"   XGBoost Val — F1: {metrics['f1']:.4f} | AUC-PR: {metrics['auc_pr']:.4f}")
    return model, metrics


def train_lightgbm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    params: dict[str, Any],
) -> tuple[lgb.LGBMClassifier, dict[str, float]]:
    """Train a LightGBM classifier with early stopping.

    Args:
        X_train: Training feature matrix.
        y_train: Training labels.
        X_val: Validation feature matrix.
        y_val: Validation labels.
        params: Full params dict; uses the ``lightgbm`` sub-key.

    Returns:
        Tuple of (fitted LGBMClassifier, validation metrics dict).
    """
    logger.info("🚀 Training LightGBM...")
    lgb_params = params["lightgbm"].copy()

    model = lgb.LGBMClassifier(**lgb_params, verbose=-1)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)],
    )
    y_proba = model.predict_proba(X_val)[:, 1]
    metrics = compute_metrics(y_val, model.predict(X_val), y_proba)
    logger.info(f"   LightGBM Val — F1: {metrics['f1']:.4f} | AUC-PR: {metrics['auc_pr']:.4f}")
    return model, metrics


def main() -> None:
    """Run the full training pipeline: load data, train both models, log to MLflow.

    Trains XGBoost and LightGBM on preprocessed splits, logs all
    parameters, validation metrics, and model artefacts to MLflow,
    then persists models locally for the evaluate step.
    """
    params = load_params()
    mlflow_params = params["mlflow"]

    tracking_uri = mlflow_params.get("tracking_uri", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(mlflow_params["experiment_name"])

    logger.info("📥 Loading processed data...")
    X_train = load_pickle(PROCESSED_DIR / "X_train.pkl")
    y_train = load_pickle(PROCESSED_DIR / "y_train.pkl")
    X_val = load_pickle(PROCESSED_DIR / "X_val.pkl")
    y_val = load_pickle(PROCESSED_DIR / "y_val.pkl")

    logger.info(f"   Train shape: {X_train.shape}, Val shape: {X_val.shape}")

    # ── XGBoost Run ───────────────────────────────────────────────────────────
    with mlflow.start_run(run_name="xgboost_training") as xgb_run:
        mlflow.log_params(params["xgboost"])
        xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_val, y_val, params)
        mlflow.log_metrics({f"val_{k}": v for k, v in xgb_metrics.items()})
        mlflow.xgboost.log_model(xgb_model, artifact_path="xgboost_model")
        xgb_run_id = xgb_run.info.run_id
        logger.info(f"   XGBoost run ID: {xgb_run_id}")

    # ── LightGBM Run ──────────────────────────────────────────────────────────
    with mlflow.start_run(run_name="lightgbm_training") as lgb_run:
        mlflow.log_params(params["lightgbm"])
        lgb_model, lgb_metrics = train_lightgbm(X_train, y_train, X_val, y_val, params)
        mlflow.log_metrics({f"val_{k}": v for k, v in lgb_metrics.items()})
        mlflow.sklearn.log_model(lgb_model, artifact_path="lightgbm_model")
        lgb_run_id = lgb_run.info.run_id
        logger.info(f"   LightGBM run ID: {lgb_run_id}")

    # ── Save best model locally ───────────────────────────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    save_pickle(xgb_model, MODELS_DIR / "xgboost_model.pkl")
    save_pickle(lgb_model, MODELS_DIR / "lightgbm_model.pkl")

    # Save run IDs for evaluate step
    run_ids = {
        "xgboost": {"run_id": xgb_run_id, "metrics": xgb_metrics},
        "lightgbm": {"run_id": lgb_run_id, "metrics": lgb_metrics},
    }
    with open(PROCESSED_DIR / "run_ids.json", "w") as f:
        json.dump(run_ids, f, indent=2)

    logger.info("✅ Training complete. Both models saved.")


if __name__ == "__main__":
    main()
