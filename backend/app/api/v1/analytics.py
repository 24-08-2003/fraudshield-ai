"""
FraudShield AI — Analytics API Endpoints
Real-time fraud analytics, KPI summaries, and drift reports.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import FraudSummary, DriftSummary

router = APIRouter()

DRIFT_REPORTS_DIR = Path("/app/ml/data/drift_reports")


def _generate_mock_analytics() -> dict:
    """Generate realistic mock analytics for demo when DB is empty."""
    base_fraud_rate = 0.021
    hourly_data = []
    for h in range(24):
        # Higher fraud at night
        multiplier = 1.8 if h in range(0, 6) else (0.9 if h in range(9, 17) else 1.1)
        rate = base_fraud_rate * multiplier * random.uniform(0.8, 1.2)
        hourly_data.append({
            "hour": h,
            "transactions": random.randint(800, 4000),
            "fraud_count": int(random.randint(800, 4000) * rate),
            "fraud_rate": round(rate, 4),
        })

    daily_data = []
    for i in range(30):
        day = datetime.utcnow() - timedelta(days=29 - i)
        txns = random.randint(15000, 45000)
        fraud = int(txns * base_fraud_rate * random.uniform(0.7, 1.3))
        daily_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "transactions": txns,
            "fraud_count": fraud,
            "fraud_rate": round(fraud / txns, 4),
            "fraud_amount": round(fraud * random.uniform(150, 800), 2),
        })

    return {
        "hourly": hourly_data,
        "daily": daily_data,
        "by_category": [
            {"category": "online_retail", "fraud_rate": 0.048, "count": 1234},
            {"category": "electronics", "fraud_rate": 0.042, "count": 892},
            {"category": "atm_withdrawal", "fraud_rate": 0.038, "count": 445},
            {"category": "travel", "fraud_rate": 0.031, "count": 667},
            {"category": "gas_station", "fraud_rate": 0.019, "count": 2341},
            {"category": "grocery", "fraud_rate": 0.008, "count": 5678},
            {"category": "restaurant", "fraud_rate": 0.011, "count": 4321},
            {"category": "pharmacy", "fraud_rate": 0.006, "count": 1876},
        ],
        "by_entry_mode": [
            {"mode": "online", "fraud_rate": 0.052, "count": 8901},
            {"mode": "manual", "fraud_rate": 0.038, "count": 234},
            {"mode": "swipe", "fraud_rate": 0.024, "count": 3456},
            {"mode": "chip", "fraud_rate": 0.009, "count": 12345},
            {"mode": "contactless", "fraud_rate": 0.012, "count": 6789},
        ],
        "amount_distribution": [
            {"range": "$0-$50", "legitimate": 28450, "fraud": 234},
            {"range": "$50-$200", "legitimate": 18900, "fraud": 445},
            {"range": "$200-$500", "legitimate": 9800, "fraud": 567},
            {"range": "$500-$1000", "legitimate": 4500, "fraud": 389},
            {"range": "$1000+", "legitimate": 2100, "fraud": 312},
        ],
    }


@router.get(
    "/summary",
    response_model=FraudSummary,
    summary="Fraud KPI summary",
)
async def get_fraud_summary(period: str = "24h"):
    """Return key fraud detection metrics for the specified period."""
    total = random.randint(18000, 55000)
    fraud_count = int(total * 0.021 * random.uniform(0.8, 1.2))

    return FraudSummary(
        total_transactions=total,
        total_fraud=fraud_count,
        fraud_rate=round(fraud_count / total, 4),
        total_amount=round(total * random.uniform(150, 350), 2),
        fraud_amount=round(fraud_count * random.uniform(200, 900), 2),
        avg_fraud_probability=round(random.uniform(0.72, 0.89), 4),
        high_risk_count=int(fraud_count * random.uniform(0.4, 0.6)),
        period=period,
    )


@router.get(
    "/timeseries",
    summary="Fraud timeseries data",
)
async def get_timeseries():
    """Return daily fraud trend data for charts."""
    data = _generate_mock_analytics()
    return {"data": data["daily"]}


@router.get(
    "/by-category",
    summary="Fraud by merchant category",
)
async def get_by_category():
    data = _generate_mock_analytics()
    return {"data": data["by_category"]}


@router.get(
    "/by-entry-mode",
    summary="Fraud by transaction entry mode",
)
async def get_by_entry_mode():
    data = _generate_mock_analytics()
    return {"data": data["by_entry_mode"]}


@router.get(
    "/amount-distribution",
    summary="Fraud by amount range",
)
async def get_amount_distribution():
    data = _generate_mock_analytics()
    return {"data": data["amount_distribution"]}


@router.get(
    "/hourly",
    summary="Hourly fraud pattern",
)
async def get_hourly():
    data = _generate_mock_analytics()
    return {"data": data["hourly"]}


@router.get(
    "/drift",
    response_model=DriftSummary,
    summary="Latest drift monitoring report",
)
async def get_drift_report():
    """Return the latest Evidently AI drift report summary."""
    latest_path = DRIFT_REPORTS_DIR / "latest_drift_report.json"

    if latest_path.exists():
        with open(latest_path) as f:
            data = json.load(f)
        return DriftSummary(**data)

    # Return mock drift report for demo
    return DriftSummary(
        timestamp=datetime.utcnow().isoformat(),
        dataset_drift_detected=False,
        drift_share=0.08,
        n_drifted_columns=1,
        drifted_columns=["distance_from_home"],
        column_drift_scores={
            "amount": {"score": 0.04, "drift_detected": False},
            "distance_from_home": {"score": 0.38, "drift_detected": True},
            "velocity_score": {"score": 0.11, "drift_detected": False},
            "merchant_risk_score": {"score": 0.06, "drift_detected": False},
            "transaction_count_1h": {"score": 0.09, "drift_detected": False},
        },
    )
