"""
FraudShield AI — Health Check Endpoints
"""
import time
from datetime import datetime

from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter()

START_TIME = time.time()


@router.get("/health", summary="Health check")
async def health_check(request: Request):
    uptime_seconds = int(time.time() - START_TIME)
    model_loaded = hasattr(request.app.state, "predictor") and request.app.state.predictor.model is not None

    return {
        "status": "healthy",
        "service": "FraudShield AI API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
        "model_loaded": model_loaded,
    }


@router.get("/health/live", summary="Liveness probe")
async def liveness():
    return {"status": "alive"}


@router.get("/health/ready", summary="Readiness probe")
async def readiness(request: Request):
    checks = {}

    # Check model
    checks["model"] = (
        hasattr(request.app.state, "predictor") and
        request.app.state.predictor is not None
    )

    ready = all(checks.values())
    return {
        "ready": ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
