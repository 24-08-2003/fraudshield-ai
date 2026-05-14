"""
FraudShield AI — Prediction API Endpoints
"""
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status

from app.schemas.schemas import (
    TransactionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
)
from app.ml.predictor import FraudPredictor

router = APIRouter()


def get_predictor(request: Request) -> FraudPredictor:
    return request.app.state.predictor


@router.post(
    "/",
    response_model=PredictionResponse,
    summary="Predict fraud for a single transaction",
    description="Submit a single transaction for real-time fraud detection.",
)
async def predict_transaction(
    transaction: TransactionRequest,
    predictor: FraudPredictor = Depends(get_predictor),
):
    start = time.perf_counter()
    try:
        result = predictor.predict(transaction.model_dump())
        elapsed = (time.perf_counter() - start) * 1000

        return PredictionResponse(
            transaction_id=transaction.transaction_id,
            fraud_probability=result["fraud_probability"],
            is_fraud=result["is_fraud"],
            risk_level=result["risk_level"],
            model_version=result["model_version"],
            threshold_used=result["threshold_used"],
            processing_time_ms=round(elapsed, 2),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Batch fraud prediction",
    description="Submit up to 1000 transactions for batch fraud detection.",
)
async def predict_batch(
    request: BatchPredictionRequest,
    predictor: FraudPredictor = Depends(get_predictor),
):
    start = time.perf_counter()
    try:
        transactions = [t.model_dump() for t in request.transactions]
        results = predictor.predict_batch(transactions)
        elapsed = (time.perf_counter() - start) * 1000

        fraud_count = sum(1 for r in results if r["is_fraud"])
        fraud_rate = fraud_count / len(results) if results else 0.0

        predictions = [
            PredictionResponse(
                transaction_id=request.transactions[i].transaction_id,
                fraud_probability=r["fraud_probability"],
                is_fraud=r["is_fraud"],
                risk_level=r["risk_level"],
                model_version=r["model_version"],
                threshold_used=r["threshold_used"],
                processing_time_ms=round(elapsed / len(results), 2),
            )
            for i, r in enumerate(results)
        ]

        return BatchPredictionResponse(
            total=len(results),
            fraud_count=fraud_count,
            fraud_rate=round(fraud_rate, 4),
            predictions=predictions,
            processing_time_ms=round(elapsed, 2),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}",
        )
