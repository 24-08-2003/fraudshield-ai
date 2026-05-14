"""
FraudShield AI — Model Registry API Endpoints
"""
import logging
from typing import Optional

import mlflow
from mlflow.tracking import MlflowClient
from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas.schemas import ModelInfo, ModelListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_client() -> MlflowClient:
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    return MlflowClient()


def _mock_models() -> list[ModelInfo]:
    """Return mock model data for demo when MLflow is unavailable."""
    return [
        ModelInfo(
            name="fraudshield_classifier",
            version="3",
            stage="Production",
            description="XGBoost classifier trained on 100k synthetic transactions",
            metrics={
                "f1_score": 0.9124,
                "auc_pr": 0.9341,
                "roc_auc": 0.9812,
                "precision": 0.8967,
                "recall": 0.9289,
            },
            created_at="2024-03-15T10:23:45",
            run_id="abc123def456",
        ),
        ModelInfo(
            name="fraudshield_classifier",
            version="2",
            stage="Staging",
            description="LightGBM challenger model",
            metrics={
                "f1_score": 0.8991,
                "auc_pr": 0.9187,
                "roc_auc": 0.9743,
                "precision": 0.8823,
                "recall": 0.9167,
            },
            created_at="2024-03-10T08:15:30",
            run_id="xyz789ghi012",
        ),
        ModelInfo(
            name="fraudshield_classifier",
            version="1",
            stage="Archived",
            description="Initial XGBoost baseline",
            metrics={
                "f1_score": 0.8534,
                "auc_pr": 0.8721,
                "roc_auc": 0.9456,
                "precision": 0.8312,
                "recall": 0.8764,
            },
            created_at="2024-03-01T14:00:00",
            run_id="prev123model456",
        ),
    ]


@router.get(
    "/",
    response_model=ModelListResponse,
    summary="List all registered models",
)
async def list_models(name: Optional[str] = None):
    """List all versions of registered fraud detection models."""
    try:
        client = _get_client()
        model_name = name or settings.MLFLOW_MODEL_NAME
        versions = client.search_model_versions(f"name='{model_name}'")

        models = []
        for mv in versions:
            # Fetch run metrics
            try:
                run = client.get_run(mv.run_id)
                metrics = {
                    k.replace("test_", ""): round(v, 4)
                    for k, v in run.data.metrics.items()
                    if "test_" in k and isinstance(v, float)
                }
            except Exception:
                metrics = {}

            models.append(ModelInfo(
                name=mv.name,
                version=str(mv.version),
                stage=mv.current_stage,
                description=mv.description,
                metrics=metrics,
                created_at=str(mv.creation_timestamp),
                run_id=mv.run_id,
            ))

        return ModelListResponse(models=models, total=len(models))

    except Exception as e:
        logger.warning(f"MLflow unavailable ({e}). Returning mock data.")
        mock = _mock_models()
        return ModelListResponse(models=mock, total=len(mock))


@router.post(
    "/{model_name}/promote",
    summary="Promote a model version to Production",
)
async def promote_model(model_name: str, version: str):
    """Promote a specific model version to Production stage."""
    try:
        client = _get_client()

        # Archive current production
        current = client.get_latest_versions(model_name, stages=["Production"])
        for mv in current:
            client.transition_model_version_stage(
                name=model_name,
                version=mv.version,
                stage="Archived",
            )

        # Promote new version
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
        )

        return {
            "success": True,
            "message": f"Model {model_name} v{version} promoted to Production",
            "model_name": model_name,
            "version": version,
            "stage": "Production",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MLflow operation failed: {str(e)}",
        )


@router.get(
    "/experiments",
    summary="List MLflow experiments",
)
async def list_experiments():
    """List all MLflow experiments."""
    try:
        client = _get_client()
        experiments = client.search_experiments()
        return {
            "experiments": [
                {
                    "id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage,
                }
                for exp in experiments
            ]
        }
    except Exception as e:
        logger.warning(f"MLflow unavailable: {e}")
        return {
            "experiments": [
                {
                    "id": "1",
                    "name": "fraud_detection",
                    "artifact_location": "mlflow-artifacts:/1",
                    "lifecycle_stage": "active",
                }
            ]
        }
