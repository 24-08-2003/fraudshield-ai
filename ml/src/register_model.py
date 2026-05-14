"""
FraudShield AI — MLflow Model Registry
Registers the best trained model in the MLflow Model Registry.
"""
import json
import logging
import pickle
from pathlib import Path

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "params.yaml"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = PROCESSED_DIR / "models"


def load_params() -> dict:
    with open(PARAMS_PATH) as f:
        return yaml.safe_load(f)


def load_pickle(path: Path):
    with open(path, "rb") as f:
        return pickle.load(f)


def main():
    params = load_params()
    mlflow_params = params["mlflow"]
    eval_params = params["evaluation"]

    mlflow.set_tracking_uri(mlflow_params.get("tracking_uri", "http://localhost:5000"))

    # Load evaluation metrics
    with open(PROCESSED_DIR / "metrics.json") as f:
        metrics = json.load(f)

    best_model_name = metrics["best_model"]
    best_f1 = metrics["best_f1"]
    min_f1 = eval_params.get("min_f1_score", 0.85)

    logger.info(f"🏆 Best model: {best_model_name} (F1={best_f1:.4f})")

    if best_f1 < min_f1:
        logger.warning(
            f"⚠️  Model F1 {best_f1:.4f} below minimum {min_f1}. "
            "Skipping registration."
        )
        return

    # Load run IDs
    with open(PROCESSED_DIR / "run_ids.json") as f:
        run_ids = json.load(f)

    run_id = run_ids[best_model_name]["run_id"]
    model_registry_name = mlflow_params["model_name"]

    # Register model
    logger.info(f"📦 Registering model '{model_registry_name}' from run {run_id}...")

    artifact_path = f"{best_model_name}_model"
    model_uri = f"runs:/{run_id}/{artifact_path}"

    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=model_registry_name,
        tags={
            "model_type": best_model_name,
            "f1_score": str(round(best_f1, 4)),
            "auc_pr": str(round(metrics.get(f"{best_model_name}_auc_pr", 0), 4)),
            "trained_on": "synthetic_fraud_data",
        },
    )

    logger.info(f"   Registered as version {model_version.version}")

    # Transition to Production stage
    client = mlflow.MlflowClient()

    # Archive current production models
    current_prod = client.get_latest_versions(model_registry_name, stages=["Production"])
    for mv in current_prod:
        logger.info(f"   Archiving version {mv.version} (was Production)")
        client.transition_model_version_stage(
            name=model_registry_name,
            version=mv.version,
            stage="Archived",
            archive_existing_versions=False,
        )

    # Promote new version
    client.transition_model_version_stage(
        name=model_registry_name,
        version=model_version.version,
        stage="Production",
    )

    logger.info(f"✅ Model v{model_version.version} promoted to Production.")
    logger.info(f"   Model URI: models:/{model_registry_name}/Production")


if __name__ == "__main__":
    main()
