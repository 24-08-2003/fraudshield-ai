"""
FraudShield AI — Data Ingestion API Endpoints
Handles CSV uploads and API-based data ingestion with validation.
"""
import io
import time
import logging

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status

from app.schemas.schemas import IngestionResponse
from app.ml.predictor import FraudPredictor

logger = logging.getLogger(__name__)
router = APIRouter()

REQUIRED_COLUMNS = {
    "amount", "merchant_category", "card_type", "entry_mode",
    "hour_of_day", "day_of_week",
}

VALID_MERCHANT_CATEGORIES = {
    "grocery", "restaurant", "gas_station", "online_retail",
    "travel", "entertainment", "pharmacy", "electronics",
    "clothing", "healthcare", "utilities", "atm_withdrawal",
}


def get_predictor(request: Request) -> FraudPredictor:
    return request.app.state.predictor


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate uploaded dataframe structure and content."""
    issues = []

    # Check required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        issues.append(f"Missing required columns: {missing}")

    if df.empty:
        issues.append("Dataset is empty")

    if "amount" in df.columns:
        if df["amount"].isnull().any():
            issues.append("Null values in 'amount' column")
        if (df["amount"] <= 0).any():
            issues.append("Non-positive values found in 'amount' column")

    if "merchant_category" in df.columns:
        invalid_cats = set(df["merchant_category"].dropna().unique()) - VALID_MERCHANT_CATEGORIES
        if invalid_cats:
            issues.append(f"Invalid merchant categories: {invalid_cats}")

    if "hour_of_day" in df.columns:
        if not df["hour_of_day"].between(0, 23).all():
            issues.append("hour_of_day values must be 0–23")

    return len(issues) == 0, issues


@router.post(
    "/csv",
    response_model=IngestionResponse,
    summary="Ingest CSV transaction data",
    description="Upload a CSV file of transactions for validation and optional fraud scoring.",
)
async def ingest_csv(
    file: UploadFile = File(..., description="CSV file with transaction records"),
    score_fraud: bool = False,
    predictor: FraudPredictor = Depends(get_predictor),
):
    start = time.perf_counter()

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV: {str(e)}",
        )

    # Fill optional columns with defaults
    df["transaction_count_1h"] = df.get("transaction_count_1h", 0)
    df["transaction_count_24h"] = df.get("transaction_count_24h", 0)
    df["amount_mean_1h"] = df.get("amount_mean_1h", 0.0)
    df["amount_std_1h"] = df.get("amount_std_1h", 0.0)
    df["merchant_risk_score"] = df.get("merchant_risk_score", 0.5)
    df["distance_from_home"] = df.get("distance_from_home", 0.0)
    df["velocity_score"] = df.get("velocity_score", 0.0)

    validation_passed, issues = validate_dataframe(df)

    fraud_count = None
    if score_fraud and validation_passed:
        records = df.to_dict(orient="records")
        results = predictor.predict_batch(records)
        fraud_count = sum(1 for r in results if r["is_fraud"])
        logger.info(f"Batch scored {len(records)} transactions: {fraud_count} flagged as fraud")

    elapsed = (time.perf_counter() - start) * 1000

    return IngestionResponse(
        success=validation_passed,
        message="Data ingested successfully" if validation_passed else f"Validation issues: {'; '.join(issues)}",
        n_rows=len(df),
        n_fraud_detected=fraud_count,
        validation_passed=validation_passed,
        processing_time_ms=round(elapsed, 2),
    )


@router.post(
    "/stream",
    response_model=IngestionResponse,
    summary="Ingest streaming transaction data",
    description="Ingest a JSON array of transactions from an upstream API/stream.",
)
async def ingest_stream(
    transactions: list[dict],
    score_fraud: bool = True,
    predictor: FraudPredictor = Depends(get_predictor),
):
    start = time.perf_counter()

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions provided",
        )

    if len(transactions) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10,000 transactions per request",
        )

    df = pd.DataFrame(transactions)
    validation_passed, issues = validate_dataframe(df)

    fraud_count = None
    if score_fraud and validation_passed:
        results = predictor.predict_batch(transactions)
        fraud_count = sum(1 for r in results if r["is_fraud"])

    elapsed = (time.perf_counter() - start) * 1000

    return IngestionResponse(
        success=validation_passed,
        message="Stream ingested successfully" if validation_passed else f"Issues: {'; '.join(issues)}",
        n_rows=len(df),
        n_fraud_detected=fraud_count,
        validation_passed=validation_passed,
        processing_time_ms=round(elapsed, 2),
    )
