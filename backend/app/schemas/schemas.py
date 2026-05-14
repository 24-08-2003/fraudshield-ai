"""
FraudShield AI — Pydantic Request/Response Schemas
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ── Transaction Schemas ───────────────────────────────────────────────────────

class TransactionRequest(BaseModel):
    transaction_id: Optional[str] = Field(None, description="Unique transaction ID")
    customer_id: Optional[str] = Field(None, description="Customer identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    merchant_category: str = Field(..., description="Merchant category code")
    card_type: str = Field(..., description="Card network type")
    entry_mode: str = Field(..., description="Transaction entry mode")
    hour_of_day: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    transaction_count_1h: int = Field(default=0, ge=0)
    transaction_count_24h: int = Field(default=0, ge=0)
    amount_mean_1h: float = Field(default=0.0, ge=0)
    amount_std_1h: float = Field(default=0.0, ge=0)
    merchant_risk_score: float = Field(default=0.5, ge=0, le=1)
    distance_from_home: float = Field(default=0.0, ge=0)
    velocity_score: float = Field(default=0.0, ge=0, le=1)

    @field_validator("merchant_category")
    @classmethod
    def validate_merchant_category(cls, v: str) -> str:
        valid = {
            "grocery", "restaurant", "gas_station", "online_retail",
            "travel", "entertainment", "pharmacy", "electronics",
            "clothing", "healthcare", "utilities", "atm_withdrawal",
        }
        if v not in valid:
            raise ValueError(f"Invalid merchant_category. Must be one of: {valid}")
        return v

    @field_validator("card_type")
    @classmethod
    def validate_card_type(cls, v: str) -> str:
        valid = {"visa", "mastercard", "amex", "discover"}
        if v not in valid:
            raise ValueError(f"Invalid card_type. Must be one of: {valid}")
        return v


class PredictionResponse(BaseModel):
    transaction_id: Optional[str]
    fraud_probability: float = Field(..., ge=0, le=1)
    is_fraud: bool
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    model_version: str
    threshold_used: float
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchPredictionRequest(BaseModel):
    transactions: list[TransactionRequest] = Field(..., min_length=1, max_length=1000)


class BatchPredictionResponse(BaseModel):
    total: int
    fraud_count: int
    fraud_rate: float
    predictions: list[PredictionResponse]
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ── Analytics Schemas ─────────────────────────────────────────────────────────

class FraudSummary(BaseModel):
    total_transactions: int
    total_fraud: int
    fraud_rate: float
    total_amount: float
    fraud_amount: float
    avg_fraud_probability: float
    high_risk_count: int
    period: str


class DriftSummary(BaseModel):
    timestamp: str
    dataset_drift_detected: bool
    drift_share: float
    n_drifted_columns: int
    drifted_columns: list[str]
    column_drift_scores: dict


# ── Model Registry Schemas ────────────────────────────────────────────────────

class ModelInfo(BaseModel):
    name: str
    version: str
    stage: str
    description: Optional[str]
    metrics: dict
    created_at: Optional[str]
    run_id: Optional[str]


class ModelListResponse(BaseModel):
    models: list[ModelInfo]
    total: int


# ── Ingestion Schemas ─────────────────────────────────────────────────────────

class IngestionResponse(BaseModel):
    success: bool
    message: str
    n_rows: int
    n_fraud_detected: Optional[int] = None
    validation_passed: bool
    processing_time_ms: float
