"""FraudShield AI — Feature Engineering.

Computes engineered features from raw transaction data.
"""

from pathlib import Path  # noqa: F401

import numpy as np
import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add cyclical sine/cosine encodings for time-based columns.

    Args:
        df: Raw transaction DataFrame containing ``hour_of_day`` and
            ``day_of_week`` columns.

    Returns:
        DataFrame with four new columns: ``hour_sin``, ``hour_cos``,
        ``dow_sin``, ``dow_cos``.
    """
    df = df.copy()
    if "hour_of_day" in df.columns:
        df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
    if "day_of_week" in df.columns:
        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    return df


def add_amount_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add log-transformed and ratio amount features.

    Args:
        df: Transaction DataFrame containing ``amount`` and optionally
            ``amount_mean_1h``.

    Returns:
        DataFrame with new columns ``log_amount`` and
        ``amount_vs_mean_ratio``.
    """
    df = df.copy()
    df["log_amount"] = np.log1p(df["amount"])
    if "amount_mean_1h" in df.columns and df["amount_mean_1h"].gt(0).any():
        df["amount_vs_mean_ratio"] = df["amount"] / (df["amount_mean_1h"] + 1e-6)
    else:
        df["amount_vs_mean_ratio"] = 1.0
    return df


def add_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """Combine risk indicators into a single composite score in [0, 1].

    Args:
        df: Transaction DataFrame containing ``merchant_risk_score``,
            ``velocity_score``, ``distance_from_home``, and
            ``transaction_count_1h``.

    Returns:
        DataFrame with new column ``composite_risk``.
    """
    df = df.copy()
    df["composite_risk"] = (
        0.3 * df.get("merchant_risk_score", 0)
        + 0.3 * df.get("velocity_score", 0)
        + 0.2 * (df.get("distance_from_home", 0) / 5000).clip(0, 1)
        + 0.2 * (df.get("transaction_count_1h", 0) / 15).clip(0, 1)
    )
    return df


def encode_categoricals(
    df: pd.DataFrame, categorical_cols: list[str]
) -> pd.DataFrame:
    """One-hot encode categorical columns, dropping originals.

    Args:
        df: Transaction DataFrame.
        categorical_cols: List of column names to encode.

    Returns:
        DataFrame with original categorical columns replaced by
        one-hot encoded columns.
    """
    df = df.copy()
    cols_present = [c for c in categorical_cols if c in df.columns]
    if cols_present:
        df = pd.get_dummies(df, columns=cols_present, drop_first=False, dtype=float)
    return df


def get_feature_columns(
    df: pd.DataFrame, target_col: str = "is_fraud"
) -> list[str]:
    """Return all feature columns, excluding ID and target columns.

    Args:
        df: Engineered transaction DataFrame.
        target_col: Name of the target/label column to exclude.

    Returns:
        Sorted list of feature column names.
    """
    exclude = {target_col, "transaction_id", "customer_id", "timestamp"}
    return [c for c in df.columns if c not in exclude]


def engineer_features(
    df: pd.DataFrame,
    categorical_cols: list[str],
) -> pd.DataFrame:
    """Run the full feature engineering pipeline in order.

    Applies time features, amount features, risk features, and
    one-hot encoding sequentially.

    Args:
        df: Raw transaction DataFrame.
        categorical_cols: Columns to one-hot encode.

    Returns:
        Fully engineered DataFrame ready for model training.
    """
    df = add_time_features(df)
    df = add_amount_features(df)
    df = add_risk_features(df)
    df = encode_categoricals(df, categorical_cols)
    return df
