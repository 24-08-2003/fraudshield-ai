"""Shared pytest fixtures for FraudShield AI ML tests."""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ml/src"))


# ---------------------------------------------------------------------------
# DataFrame factory
# ---------------------------------------------------------------------------

def make_transaction_df(n: int = 200, fraud_ratio: float = 0.05) -> pd.DataFrame:
    """Return a minimal synthetic transaction DataFrame.

    Args:
        n: Number of rows.
        fraud_ratio: Fraction of rows to label as fraud.

    Returns:
        Shuffled DataFrame with all 17 raw transaction columns.
    """
    rng = np.random.default_rng(42)
    n_fraud = max(1, int(n * fraud_ratio))
    n_legit = n - n_fraud
    data = {
        "transaction_id": [f"TXN_{i:06d}" for i in range(n)],
        "customer_id": [f"CUST_{i % 20:04d}" for i in range(n)],
        "timestamp": ["2024-06-01T12:00:00"] * n,
        "amount": np.abs(rng.lognormal(3.5, 1.0, n)),
        "merchant_category": rng.choice(
            ["grocery", "online_retail", "electronics", "gas_station"], n
        ),
        "card_type": rng.choice(["visa", "mastercard", "amex", "discover"], n),
        "entry_mode": rng.choice(["chip", "online", "contactless", "swipe", "manual"], n),
        "hour_of_day": rng.integers(0, 24, n),
        "day_of_week": rng.integers(0, 7, n),
        "transaction_count_1h": rng.integers(0, 10, n),
        "transaction_count_24h": rng.integers(1, 20, n),
        "amount_mean_1h": np.abs(rng.lognormal(3.0, 0.5, n)),
        "amount_std_1h": np.abs(rng.lognormal(2.0, 0.5, n)),
        "merchant_risk_score": rng.uniform(0, 1, n),
        "distance_from_home": np.abs(rng.exponential(50, n)),
        "velocity_score": rng.uniform(0, 1, n),
        "is_fraud": [1] * n_fraud + [0] * n_legit,
    }
    return pd.DataFrame(data).sample(frac=1, random_state=42).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small transaction DataFrame (200 rows, 5 % fraud)."""
    return make_transaction_df(n=200, fraud_ratio=0.05)


@pytest.fixture
def large_df() -> pd.DataFrame:
    """Larger transaction DataFrame for split-ratio tests (1000 rows, 5 % fraud)."""
    return make_transaction_df(n=1000, fraud_ratio=0.05)


@pytest.fixture
def engineered_df(sample_df: pd.DataFrame) -> pd.DataFrame:
    """Transaction DataFrame after the full feature engineering pipeline."""
    from feature_engineering import engineer_features

    cats = ["merchant_category", "card_type", "entry_mode"]
    return engineer_features(sample_df, categorical_cols=cats)


@pytest.fixture
def xy_arrays(engineered_df: pd.DataFrame):
    """Return (X, y) numpy arrays ready for sklearn, as a 2-tuple."""
    from feature_engineering import get_feature_columns

    feature_cols = get_feature_columns(engineered_df)
    X = engineered_df[feature_cols].values
    y = engineered_df["is_fraud"].values
    return X, y
