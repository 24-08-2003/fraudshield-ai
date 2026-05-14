"""FraudShield AI — Data Preprocessing Pipeline.

Loads raw data, engineers features, scales, and produces stratified
train / val / test splits with optional SMOTE oversampling.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from feature_engineering import engineer_features, get_feature_columns

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "params.yaml"
RAW_PATH = ROOT / "data" / "raw" / "transactions.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = PROCESSED_DIR / "models"


def load_params() -> dict[str, Any]:
    """Load pipeline parameters from the YAML config file.

    Returns:
        Nested dictionary of pipeline parameters.
    """
    with open(PARAMS_PATH) as f:
        return yaml.safe_load(f)


def save_pickle(obj: Any, path: Path) -> None:
    """Serialize an object to a pickle file, creating parent dirs if needed.

    Args:
        obj: Any Python object to persist.
        path: Destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    logger.info(f"   Saved → {path}")


def main() -> None:
    """Run the end-to-end preprocessing pipeline.

    Reads raw transactions, applies feature engineering, performs
    stratified train/val/test splitting, optionally scales features
    and applies SMOTE, then persists all artefacts to disk.
    """
    params = load_params()
    data_params = params["data"]
    feat_params = params["features"]
    prep_params = params["preprocessing"]

    logger.info("📥 Loading raw transactions...")
    df = pd.read_csv(RAW_PATH)
    logger.info(f"   Shape: {df.shape}")

    # Feature engineering
    logger.info("⚙️  Engineering features...")
    df = engineer_features(df, categorical_cols=feat_params["categorical_cols"])

    # Split
    target = "is_fraud"
    feature_cols = get_feature_columns(df, target_col=target)
    X = df[feature_cols].values
    y = df[target].values

    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y,
        test_size=data_params["test_size"],
        random_state=data_params["random_state"],
        stratify=y,
    )
    val_ratio = data_params["val_size"] / (1 - data_params["test_size"])
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp,
        test_size=val_ratio,
        random_state=data_params["random_state"],
        stratify=y_temp,
    )

    logger.info(f"   Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    logger.info(f"   Train fraud rate: {y_train.mean():.4f}")

    # Scale
    if prep_params.get("scale_features", True):
        logger.info("📏 Scaling features...")
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)
        X_test = scaler.transform(X_test)
        save_pickle(scaler, PROCESSED_DIR / "scaler.pkl")
    else:
        scaler = None

    # SMOTE oversampling
    if prep_params.get("smote", True):
        logger.info("🔄 Applying SMOTE oversampling...")
        smote = SMOTE(
            sampling_strategy=prep_params.get("smote_ratio", 0.3),
            random_state=data_params["random_state"],
        )
        X_train, y_train = smote.fit_resample(X_train, y_train)
        logger.info(f"   After SMOTE — Train: {X_train.shape}, Fraud rate: {y_train.mean():.4f}")

    # Save splits
    logger.info("💾 Saving processed splits...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    save_pickle(X_train, PROCESSED_DIR / "X_train.pkl")
    save_pickle(X_val, PROCESSED_DIR / "X_val.pkl")
    save_pickle(X_test, PROCESSED_DIR / "X_test.pkl")
    save_pickle(y_train, PROCESSED_DIR / "y_train.pkl")
    save_pickle(y_val, PROCESSED_DIR / "y_val.pkl")
    save_pickle(y_test, PROCESSED_DIR / "y_test.pkl")

    # Save feature names
    feature_info = {
        "feature_names": feature_cols,
        "n_features": len(feature_cols),
        "n_train": int(X_train.shape[0]),
        "n_val": int(X_val.shape[0]),
        "n_test": int(X_test.shape[0]),
    }
    with open(PROCESSED_DIR / "feature_names.json", "w") as f:
        json.dump(feature_info, f, indent=2)

    logger.info("✅ Preprocessing complete.")


if __name__ == "__main__":
    main()
