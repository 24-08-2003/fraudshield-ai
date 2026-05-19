"""FraudShield AI — FastAPI Application Entry Point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import analytics, health, ingest, models, predict, ws
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # noqa: F401 — registers ORM models with Base.metadata

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# FIX 1: flag pour désactiver le chargement du modèle en CI/tests
#         (le modèle MLflow n'existe pas dans l'environnement CI)
_SKIP_MODEL_LOAD = os.getenv("SKIP_MODEL_LOAD", "false").lower() == "true"
_TESTING = os.getenv("TESTING", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401
    """Startup and shutdown lifecycle."""
    logger.info("🚀 FraudShield AI Backend starting up...")

    # FIX 2: création des tables DB uniquement si non en mode test pur
    #         (en test, les fixtures pytest gèrent le schéma)
    if not _TESTING:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables verified")

    # FIX 3: chargement conditionnel du modèle ML
    if _SKIP_MODEL_LOAD or _TESTING:
        logger.warning(
            "⚠️  Model loading SKIPPED (SKIP_MODEL_LOAD=%s, TESTING=%s). "
            "Prediction endpoints will return 503.",
            _SKIP_MODEL_LOAD,
            _TESTING,
        )
        app.state.predictor = None
    else:
        # Import local pour éviter les imports circulaires et l'overhead en tests
        from app.ml.predictor import FraudPredictor  # noqa: PLC0415

        predictor = FraudPredictor()
        await predictor.load_model()
        app.state.predictor = predictor
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
async def root() -> dict:
    """Return service metadata."""
    return {
        "service": "FraudShield AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }