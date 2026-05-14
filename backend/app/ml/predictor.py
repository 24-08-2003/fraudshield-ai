"""
FraudShield AI — ML Predictor
Loads the production model from MLflow and performs inference.
"""
import logging
import pickle
from typing import Optional

import mlflow
import mlflow.sklearn
import mlflow.xgboost
import numpy as np
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)

MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "gas_station", "online_retail",
    "travel", "entertainment", "pharmacy", "electronics",
    "clothing", "healthcare", "utilities", "atm_withdrawal",
]
CARD_TYPES = ["visa", "mastercard", "amex", "discover"]
ENTRY_MODES = ["chip", "swipe", "contactless", "online", "manual"]


class FraudPredictor:
    """Production fraud detection predictor backed by MLflow."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names: list[str] = []
        self.model_version: Optional[str] = None
        self.model_name: Optional[str] = None

    async def load_model(self):
        """Load production model from MLflow registry."""
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        try:
            model_uri = (
                f"models:/{settings.MLFLOW_MODEL_NAME}/{settings.MLFLOW_MODEL_STAGE}"
            )
            logger.info(f"Loading model from: {model_uri}")
            self.model = mlflow.pyfunc.load_model(model_uri)
            self.model_name = settings.MLFLOW_MODEL_NAME
            logger.info("✅ Production model loaded from MLflow")
        except Exception as e:
            logger.warning(f"MLflow model not found ({e}). Using fallback mock predictor.")
            self.model = None

    def _build_feature_vector(self, transaction: dict) -> np.ndarray:
        """Convert a transaction dict into a feature vector."""
        df = pd.DataFrame([transaction])

        # Add engineered features
        df["log_amount"] = np.log1p(df["amount"])
        df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["amount_vs_mean_ratio"] = df["amount"] / (df["amount_mean_1h"] + 1e-6)
        df["composite_risk"] = (
            0.3 * df["merchant_risk_score"] +
            0.3 * df["velocity_score"] +
            0.2 * (df["distance_from_home"] / 5000).clip(0, 1) +
            0.2 * (df["transaction_count_1h"] / 15).clip(0, 1)
        )

        # One-hot encode categoricals
        df = pd.get_dummies(
            df,
            columns=["merchant_category", "card_type", "entry_mode"],
            drop_first=False,
            dtype=float,
        )

        # Drop non-feature columns
        drop_cols = [
            c for c in ["transaction_id", "customer_id", "timestamp", "is_fraud"]
            if c in df.columns
        ]
        df = df.drop(columns=drop_cols, errors="ignore")

        return df.values

    def predict(self, transaction: dict) -> dict:
        """Run fraud prediction for a single transaction."""
        if self.model is None:
            # Fallback: rule-based heuristic for demo
            return self._heuristic_predict(transaction)

        try:
            features = self._build_feature_vector(transaction)
            features_df = pd.DataFrame(features)
            proba = self.model.predict(features_df)
            if hasattr(proba, "__len__") and len(proba.shape) > 1:
                fraud_prob = float(proba[0][1])
            else:
                fraud_prob = float(proba[0])

            is_fraud = fraud_prob >= settings.FRAUD_THRESHOLD
            risk_level = (
                "HIGH" if fraud_prob >= 0.8
                else "MEDIUM" if fraud_prob >= 0.5
                else "LOW"
            )

            return {
                "fraud_probability": round(fraud_prob, 4),
                "is_fraud": bool(is_fraud),
                "risk_level": risk_level,
                "model_version": self.model_version or "production",
                "threshold_used": settings.FRAUD_THRESHOLD,
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._heuristic_predict(transaction)

    def _heuristic_predict(self, transaction: dict) -> dict:
        """Rule-based fallback predictor when ML model is unavailable."""
        risk_score = 0.0
        amount = transaction.get("amount", 0)
        merchant_risk = transaction.get("merchant_risk_score", 0)
        velocity = transaction.get("velocity_score", 0)
        distance = transaction.get("distance_from_home", 0)
        hour = transaction.get("hour_of_day", 12)

        # Risk rules
        if amount > 1000:
            risk_score += 0.25
        if amount < 1:
            risk_score += 0.15
        if merchant_risk > 0.7:
            risk_score += 0.2
        if velocity > 0.7:
            risk_score += 0.2
        if distance > 1000:
            risk_score += 0.15
        if hour in range(0, 6):
            risk_score += 0.1

        risk_score = min(risk_score, 1.0)
        is_fraud = risk_score >= settings.FRAUD_THRESHOLD

        return {
            "fraud_probability": round(risk_score, 4),
            "is_fraud": bool(is_fraud),
            "risk_level": "HIGH" if risk_score >= 0.8 else "MEDIUM" if risk_score >= 0.5 else "LOW",
            "model_version": "heuristic-fallback",
            "threshold_used": settings.FRAUD_THRESHOLD,
        }

    def predict_batch(self, transactions: list[dict]) -> list[dict]:
        """Run fraud prediction for a batch of transactions."""
        return [self.predict(txn) for txn in transactions]
