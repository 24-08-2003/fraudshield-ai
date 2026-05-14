"""FraudShield AI — Synthetic Data Ingestion.

Generates realistic credit card fraud transaction data for demonstration
and training purposes, with configurable fraud ratio and sample size.
"""

import json
import logging
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from faker import Faker

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
PARAMS_PATH = ROOT / "params.yaml"
OUTPUT_PATH = ROOT / "data" / "raw" / "transactions.csv"


MERCHANT_CATEGORIES = [
    "grocery", "restaurant", "gas_station", "online_retail",
    "travel", "entertainment", "pharmacy", "electronics",
    "clothing", "healthcare", "utilities", "atm_withdrawal",
]

CARD_TYPES = ["visa", "mastercard", "amex", "discover"]
ENTRY_MODES = ["chip", "swipe", "contactless", "online", "manual"]

HIGH_RISK_CATEGORIES = {"online_retail", "electronics", "atm_withdrawal", "travel"}
HIGH_RISK_HOURS = set(range(0, 6))  # 12am – 6am


def load_params() -> dict[str, Any]:
    """Load pipeline parameters from the YAML config file.

    Returns:
        Nested dictionary of pipeline parameters.
    """
    with open(PARAMS_PATH) as f:
        return yaml.safe_load(f)


def generate_customer_profiles(n_customers: int) -> pd.DataFrame:
    """Generate synthetic customer profiles with geographic home coordinates.

    Args:
        n_customers: Number of unique customer profiles to create.

    Returns:
        DataFrame with columns ``customer_id``, ``home_lat``,
        ``home_lon``, and ``credit_limit``.
    """
    return pd.DataFrame({
        "customer_id": [f"CUST_{i:06d}" for i in range(n_customers)],
        "home_lat": np.random.uniform(25.0, 48.0, n_customers),
        "home_lon": np.random.uniform(-120.0, -70.0, n_customers),
        "credit_limit": np.random.lognormal(8.5, 0.8, n_customers),
    })


def generate_transactions(
    n_samples: int,
    fraud_ratio: float,
    random_state: int,
) -> pd.DataFrame:
    """Generate a synthetic dataset of credit card transactions.

    Fraud transactions are injected with behavioural patterns that differ
    from legitimate ones (higher velocity, unusual hours, larger amounts).

    Args:
        n_samples: Total number of transactions to generate.
        fraud_ratio: Fraction of transactions that should be fraudulent.
        random_state: Seed for reproducibility.

    Returns:
        Shuffled DataFrame of transactions with 17 feature columns and
        the ``is_fraud`` binary label.
    """
    np.random.seed(random_state)
    random.seed(random_state)

    n_fraud = int(n_samples * fraud_ratio)
    n_legit = n_samples - n_fraud
    n_customers = n_samples // 5

    logger.info(f"Generating {n_samples:,} transactions ({n_fraud:,} fraud, {n_legit:,} legitimate)")

    customers = generate_customer_profiles(n_customers)

    records = []
    base_time = datetime(2024, 1, 1)

    for i in range(n_samples):
        is_fraud = i < n_fraud
        cust = customers.iloc[np.random.randint(0, n_customers)]

        # Time
        offset_seconds = np.random.randint(0, 365 * 24 * 3600)
        ts = base_time + timedelta(seconds=int(offset_seconds))
        hour = ts.hour
        day_of_week = ts.weekday()

        # Merchant
        if is_fraud:
            merchant_category = random.choices(
                list(MERCHANT_CATEGORIES),
                weights=[1, 1, 1, 4, 3, 1, 1, 4, 1, 1, 1, 4],
            )[0]
        else:
            merchant_category = random.choice(MERCHANT_CATEGORIES)

        entry_mode = random.choice(ENTRY_MODES)
        card_type = random.choice(CARD_TYPES)

        # Amount
        if is_fraud:
            amount = np.random.choice([
                np.random.uniform(0.01, 5.0),        # micro fraud
                np.random.uniform(200.0, 5000.0),    # large fraud
                np.random.lognormal(4.5, 1.2),       # random
            ], p=[0.3, 0.4, 0.3])
        else:
            amount = abs(np.random.lognormal(3.5, 1.0))
            amount = min(amount, cust["credit_limit"])

        # Location risk (distance from home)
        if is_fraud:
            distance_from_home = np.random.uniform(100, 5000)
        else:
            distance_from_home = abs(np.random.exponential(50))

        # Velocity features (simulated)
        if is_fraud:
            transaction_count_1h = np.random.randint(3, 15)
            transaction_count_24h = np.random.randint(10, 40)
            amount_mean_1h = amount * np.random.uniform(0.8, 1.2)
            amount_std_1h = amount * np.random.uniform(0.3, 2.0)
            velocity_score = np.random.uniform(0.6, 1.0)
        else:
            transaction_count_1h = np.random.randint(0, 4)
            transaction_count_24h = np.random.randint(1, 12)
            amount_mean_1h = amount * np.random.uniform(0.5, 1.5)
            amount_std_1h = amount * np.random.uniform(0.0, 0.5)
            velocity_score = np.random.uniform(0.0, 0.4)

        # Merchant risk score
        base_risk = 0.7 if merchant_category in HIGH_RISK_CATEGORIES else 0.2
        merchant_risk_score = np.clip(base_risk + np.random.normal(0, 0.15), 0, 1)

        records.append({
            "transaction_id": f"TXN_{i:09d}",
            "customer_id": cust["customer_id"],
            "timestamp": ts.isoformat(),
            "amount": round(amount, 2),
            "merchant_category": merchant_category,
            "card_type": card_type,
            "entry_mode": entry_mode,
            "hour_of_day": hour,
            "day_of_week": day_of_week,
            "transaction_count_1h": transaction_count_1h,
            "transaction_count_24h": transaction_count_24h,
            "amount_mean_1h": round(amount_mean_1h, 2),
            "amount_std_1h": round(amount_std_1h, 2),
            "merchant_risk_score": round(merchant_risk_score, 4),
            "distance_from_home": round(distance_from_home, 2),
            "velocity_score": round(velocity_score, 4),
            "is_fraud": int(is_fraud),
        })

    df = pd.DataFrame(records)
    # Shuffle rows so fraud isn't all at the top
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    return df


def main() -> None:
    """Generate synthetic transactions and persist them to CSV.

    Reads ``n_samples``, ``fraud_ratio``, and ``random_state`` from
    ``params.yaml``, generates the dataset, saves it under
    ``data/raw/transactions.csv``, and writes a JSON metadata file.
    """
    params = load_params()
    data_params = params["data"]

    df = generate_transactions(
        n_samples=data_params["n_samples"],
        fraud_ratio=data_params["fraud_ratio"],
        random_state=data_params["random_state"],
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    fraud_count = df["is_fraud"].sum()
    logger.info(f"✅ Saved {len(df):,} transactions to {OUTPUT_PATH}")
    logger.info(f"   Fraud: {fraud_count:,} ({fraud_count/len(df)*100:.2f}%)")
    logger.info(f"   Legitimate: {len(df)-fraud_count:,}")

    # Write dataset info
    info = {
        "n_samples": len(df),
        "n_fraud": int(fraud_count),
        "n_legitimate": int(len(df) - fraud_count),
        "fraud_ratio": float(fraud_count / len(df)),
        "columns": list(df.columns),
        "generated_at": datetime.utcnow().isoformat(),
    }
    info_path = OUTPUT_PATH.parent / "dataset_info.json"
    with open(info_path, "w") as f:
        json.dump(info, f, indent=2)
    logger.info(f"   Dataset info saved to {info_path}")


if __name__ == "__main__":
    main()
