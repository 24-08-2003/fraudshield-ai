"""
FraudShield AI — WebSocket Real-time Feed
Streams live fraud events to the frontend dashboard.
"""
import asyncio
import json
import logging
import random
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "gas_station", "online_retail",
    "travel", "electronics", "pharmacy", "clothing",
]

CARD_TYPES = ["visa", "mastercard", "amex", "discover"]
RISK_LEVELS = ["LOW", "LOW", "LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH"]
COUNTRIES = ["US", "US", "US", "US", "GB", "CA", "AU", "DE", "FR"]


def generate_live_transaction() -> dict:
    """Generate a realistic simulated live transaction event."""
    is_fraud = random.random() < 0.025  # 2.5% fraud rate
    amount = (
        random.uniform(0.01, 5.0) if (is_fraud and random.random() < 0.2)
        else random.uniform(200, 5000) if (is_fraud and random.random() < 0.6)
        else random.uniform(5, 500)
    )

    fraud_prob = (
        random.uniform(0.65, 0.99) if is_fraud
        else random.uniform(0.01, 0.35)
    )
    risk_level = (
        "HIGH" if fraud_prob >= 0.8
        else "MEDIUM" if fraud_prob >= 0.5
        else "LOW"
    )

    return {
        "transaction_id": f"TXN_{random.randint(100000000, 999999999)}",
        "timestamp": datetime.utcnow().isoformat(),
        "amount": round(amount, 2),
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "card_type": random.choice(CARD_TYPES),
        "country": random.choice(COUNTRIES),
        "fraud_probability": round(fraud_prob, 4),
        "is_fraud": is_fraud,
        "risk_level": risk_level,
        "customer_id": f"CUST_{random.randint(1000, 99999):05d}",
    }


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.active_connections.remove(ws)


manager = ConnectionManager()


@router.websocket("/live-transactions")
async def live_transactions(websocket: WebSocket):
    """Stream live transaction events with fraud predictions."""
    await manager.connect(websocket)
    try:
        while True:
            # Generate 1-3 transactions per second
            n_events = random.randint(1, 3)
            for _ in range(n_events):
                event = generate_live_transaction()
                await websocket.send_json({
                    "type": "transaction",
                    "data": event,
                })
            await asyncio.sleep(random.uniform(0.3, 1.0))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/metrics")
async def live_metrics(websocket: WebSocket):
    """Stream aggregated fraud metrics every 5 seconds."""
    await manager.connect(websocket)
    try:
        while True:
            metrics = {
                "type": "metrics",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "transactions_per_second": round(random.uniform(18, 45), 1),
                    "fraud_rate_1m": round(random.uniform(0.018, 0.028), 4),
                    "avg_latency_ms": round(random.uniform(8, 25), 1),
                    "high_risk_last_minute": random.randint(2, 12),
                    "model_confidence": round(random.uniform(0.88, 0.95), 3),
                },
            }
            await websocket.send_json(metrics)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Metrics WebSocket error: {e}")
        manager.disconnect(websocket)
