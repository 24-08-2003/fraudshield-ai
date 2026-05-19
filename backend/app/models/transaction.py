"""SQLAlchemy ORM model for fraud prediction results."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transaction_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    customer_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    # Input features
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    merchant_category: Mapped[str] = mapped_column(String(64), nullable=False)
    card_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entry_mode: Mapped[str] = mapped_column(String(32), nullable=False)
    hour_of_day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_count_1h: Mapped[int] = mapped_column(Integer, default=0)
    transaction_count_24h: Mapped[int] = mapped_column(Integer, default=0)
    amount_mean_1h: Mapped[float] = mapped_column(Float, default=0.0)
    amount_std_1h: Mapped[float] = mapped_column(Float, default=0.0)
    merchant_risk_score: Mapped[float] = mapped_column(Float, default=0.5)
    distance_from_home: Mapped[float] = mapped_column(Float, default=0.0)
    velocity_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Prediction results
    fraud_probability: Mapped[float] = mapped_column(Float, nullable=False)
    is_fraud: Mapped[bool] = mapped_column(Boolean, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    threshold_used: Mapped[float] = mapped_column(Float, nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
