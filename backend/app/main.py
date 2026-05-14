"""
FraudShield AI — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import predict, ingest, models, analytics, health, ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 FraudShield AI Backend starting up...")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Load ML model
    from app.ml.predictor import FraudPredictor
    app.state.predictor = FraudPredictor()
    await app.state.predictor.load_model()
    logger.info("✅ ML model loaded successfully")
    yield
    logger.info("🛑 Shutting down FraudShield AI Backend...")
    await engine.dispose()


app = FastAPI(
    title="FraudShield AI API",
    description="Production-grade credit card fraud detection API with MLOps lifecycle",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Prometheus Metrics ────────────────────────────────────────────────────────
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
).instrument(app).expose(app, endpoint="/metrics")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, prefix="/api/v1/predict", tags=["Predictions"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["Data Ingestion"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Model Registry"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "FraudShield AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }
