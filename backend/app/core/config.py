"""
FraudShield AI — Application Configuration
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "FraudShield AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-strong-secret"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fraudshield:fraudshield@postgres:5432/fraudshield"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    MLFLOW_MODEL_NAME: str = "fraudshield_classifier"
    MLFLOW_MODEL_STAGE: str = "Production"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://frontend:3000",
        "https://fraudshield.ai",
    ]

    # ML Inference
    FRAUD_THRESHOLD: float = 0.5
    MODEL_CACHE_TTL: int = 3600  # seconds

    # Prometheus
    PROMETHEUS_PORT: int = 9090

    # Feature config
    NUMERIC_FEATURES: list[str] = [
        "amount", "hour_of_day", "day_of_week",
        "transaction_count_1h", "transaction_count_24h",
        "amount_mean_1h", "amount_std_1h",
        "merchant_risk_score", "distance_from_home", "velocity_score",
    ]
    CATEGORICAL_FEATURES: list[str] = [
        "merchant_category", "card_type", "entry_mode",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
