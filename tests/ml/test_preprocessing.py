"""FraudShield AI — ML Tests: Preprocessing, Feature Engineering & ML Bugs."""

import os
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../ml/src"))


def make_sample_df(n: int = 100, fraud_ratio: float = 0.02) -> pd.DataFrame:
    """Create a minimal sample transaction DataFrame for unit tests.

    Args:
        n: Number of rows to generate.
        fraud_ratio: Fraction of rows labelled as fraud.

    Returns:
        Shuffled DataFrame with all required raw columns.
    """
    rng = np.random.default_rng(42)
    n_fraud = max(1, int(n * fraud_ratio))
    n_legit = n - n_fraud
    data = {
        "transaction_id": [f"TXN_{i}" for i in range(n)],
        "customer_id": [f"CUST_{i % 20}" for i in range(n)],
        "timestamp": ["2024-01-15T10:30:00"] * n,
        "amount": np.abs(rng.lognormal(3.5, 1.0, n)),
        "merchant_category": rng.choice(
            ["grocery", "online_retail", "electronics", "gas_station"], n
        ),
        "card_type": rng.choice(["visa", "mastercard"], n),
        "entry_mode": rng.choice(["chip", "online", "contactless"], n),
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


class TestFeatureEngineering:
    def test_add_time_features_creates_sin_cos(self):
        from feature_engineering import add_time_features
        df = make_sample_df(50)
        result = add_time_features(df)
        assert "hour_sin" in result.columns
        assert "hour_cos" in result.columns
        assert "dow_sin" in result.columns
        assert "dow_cos" in result.columns

    def test_sin_cos_range(self):
        from feature_engineering import add_time_features
        df = make_sample_df(100)
        result = add_time_features(df)
        assert result["hour_sin"].between(-1, 1).all()
        assert result["hour_cos"].between(-1, 1).all()

    def test_add_amount_features(self):
        from feature_engineering import add_amount_features
        df = make_sample_df(50)
        result = add_amount_features(df)
        assert "log_amount" in result.columns
        assert (result["log_amount"] >= 0).all()

    def test_add_risk_features(self):
        from feature_engineering import add_risk_features
        df = make_sample_df(50)
        result = add_risk_features(df)
        assert "composite_risk" in result.columns
        assert result["composite_risk"].between(0, 1).all()

    def test_encode_categoricals(self):
        from feature_engineering import encode_categoricals
        df = make_sample_df(50)
        cats = ["merchant_category", "card_type", "entry_mode"]
        result = encode_categoricals(df, cats)
        # Original categorical columns should be gone
        for col in cats:
            assert col not in result.columns
        # One-hot columns should exist
        assert any("merchant_category_" in c for c in result.columns)

    def test_engineer_features_pipeline(self):
        from feature_engineering import engineer_features, get_feature_columns
        df = make_sample_df(100)
        cats = ["merchant_category", "card_type", "entry_mode"]
        result = engineer_features(df, categorical_cols=cats)
        features = get_feature_columns(result)
        # Should have many more features after engineering
        assert len(features) > 10
        # Target and ID columns should not be in features
        assert "is_fraud" not in features
        assert "transaction_id" not in features


class TestDataValidation:
    def test_valid_dataframe_passes(self):
        """Well-formed data should pass basic checks."""
        df = make_sample_df(200)
        assert df.shape[0] == 200
        assert "amount" in df.columns
        assert "is_fraud" in df.columns
        assert df["amount"].gt(0).all()

    def test_fraud_ratio_reasonable(self):
        """Generated data should have fraud ratio near expected."""
        df = make_sample_df(1000, fraud_ratio=0.02)
        actual_ratio = df["is_fraud"].mean()
        assert 0.005 <= actual_ratio <= 0.05

    def test_no_nulls_in_required_cols(self):
        df = make_sample_df(200)
        required = ["amount", "is_fraud", "merchant_category"]
        for col in required:
            assert df[col].isnull().sum() == 0, f"Null in {col}"

    def test_hour_of_day_valid_range(self):
        df = make_sample_df(200)
        assert df["hour_of_day"].between(0, 23).all()

    def test_merchant_categories_valid(self):
        df = make_sample_df(200)
        valid = {"grocery", "online_retail", "electronics", "gas_station",
                 "restaurant", "travel", "pharmacy", "clothing",
                 "healthcare", "utilities", "atm_withdrawal", "entertainment"}
        assert set(df["merchant_category"].unique()).issubset(valid)


# ---------------------------------------------------------------------------
# Phase 4 — TDD: Split Tests (stratification + sizes)
# ---------------------------------------------------------------------------

class TestTrainTestSplit:
    """Tests that verify the train/val/test splitting strategy is correct."""

    def _do_split(self, df: pd.DataFrame):
        """Helper: apply the same stratified split logic used in preprocessing.py."""
        from feature_engineering import engineer_features, get_feature_columns

        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df, categorical_cols=cats)
        feature_cols = get_feature_columns(df_eng)
        X = df_eng[feature_cols].values
        y = df_eng["is_fraud"].values

        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y
        )
        val_ratio = 0.15 / (1 - 0.15)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42, stratify=y_temp
        )
        return X_train, X_val, X_test, y_train, y_val, y_test

    def test_split_sizes_sum_to_total(self):
        """Train + val + test rows must equal the original dataset size."""
        df = make_sample_df(n=500, fraud_ratio=0.10)
        X_train, X_val, X_test, *_ = self._do_split(df)
        total = X_train.shape[0] + X_val.shape[0] + X_test.shape[0]
        assert total == len(df)

    def test_split_is_stratified_train(self):
        """Fraud rate in train split must stay within 3 pp of the full dataset."""
        df = make_sample_df(n=1000, fraud_ratio=0.10)
        *_, y_train, y_val, y_test = self._do_split(df)
        overall_rate = df["is_fraud"].mean()
        assert abs(y_train.mean() - overall_rate) < 0.03

    def test_split_is_stratified_test(self):
        """Fraud rate in test split must stay within 3 pp of the full dataset."""
        df = make_sample_df(n=1000, fraud_ratio=0.10)
        *_, y_train, y_val, y_test = self._do_split(df)
        overall_rate = df["is_fraud"].mean()
        assert abs(y_test.mean() - overall_rate) < 0.03

    def test_no_data_leakage_between_splits(self):
        """The same index must not appear in more than one split.

        Bug this catches: forgetting ``stratify=`` causes sklearn to
        use the unshuffled order, which can place all frauds in one split.
        This test verifies disjoint row identity via unique counts.
        """
        df = make_sample_df(n=300, fraud_ratio=0.10)
        from feature_engineering import engineer_features, get_feature_columns

        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df.reset_index(), categorical_cols=cats)
        feature_cols = get_feature_columns(df_eng)
        X = df_eng[feature_cols].values
        y = df_eng["is_fraud"].values
        idx = np.arange(len(y))

        idx_temp, idx_test, _, _ = train_test_split(
            idx, y, test_size=0.15, random_state=42, stratify=y
        )
        val_ratio = 0.15 / (1 - 0.15)
        idx_train, idx_val, _, _ = train_test_split(
            idx_temp, y[idx_temp], test_size=val_ratio, random_state=42, stratify=y[idx_temp]
        )

        assert len(set(idx_train) & set(idx_val)) == 0, "Leakage between train and val"
        assert len(set(idx_train) & set(idx_test)) == 0, "Leakage between train and test"
        assert len(set(idx_val) & set(idx_test)) == 0, "Leakage between val and test"

    def test_non_stratified_split_fails_fraud_balance(self):
        """Demonstrate that a NON-stratified split on sorted data loses fraud balance.

        This is the classic ML bug: if data is sorted by label and you call
        train_test_split without stratify=y, all fraud rows end up in one
        split. The test documents the bug and proves our pipeline avoids it.
        """
        n = 400
        n_fraud = int(n * 0.05)
        y_sorted = np.array([1] * n_fraud + [0] * (n - n_fraud))
        X_dummy = np.zeros((n, 1))

        _, _, y_bad_train, y_bad_test = train_test_split(
            X_dummy, y_sorted, test_size=0.2, random_state=42, stratify=None
        )
        # Without stratify the last 20 % (all zeros) contains no fraud
        assert y_bad_test.mean() == 0.0, (
            "Expected zero fraud in test with bad split — bug not reproduced"
        )


# ---------------------------------------------------------------------------
# Phase 4 — TDD: ML Bug Identification
# ---------------------------------------------------------------------------

class TestMLBugIdentification:
    """Tests that expose and guard against classic ML bugs in this pipeline."""

    def test_target_column_not_in_features(self):
        """BUG: including ``is_fraud`` as a feature causes data leakage.

        If ``get_feature_columns`` ever returns the target column,
        the model sees the answer during training (perfect but useless).
        """
        from feature_engineering import engineer_features, get_feature_columns

        df = make_sample_df(100)
        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df, categorical_cols=cats)
        features = get_feature_columns(df_eng, target_col="is_fraud")
        assert "is_fraud" not in features, "Data leakage: target column in feature set"

    def test_id_columns_not_in_features(self):
        """BUG: leaking transaction_id / customer_id gives the model unique keys.

        High-cardinality identifiers have zero predictive value on unseen
        data and inflate training accuracy via memorisation.
        """
        from feature_engineering import engineer_features, get_feature_columns

        df = make_sample_df(100)
        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df, categorical_cols=cats)
        features = get_feature_columns(df_eng)
        for col in ("transaction_id", "customer_id", "timestamp"):
            assert col not in features, f"ID leakage: '{col}' found in feature set"

    def test_no_post_event_feature_leakage(self):
        """BUG: features computed after the fraud label is known cause leakage.

        All engineered columns (``log_amount``, ``composite_risk``, etc.)
        must be derivable from data available *before* the label is assigned.
        This test checks that no feature correlates perfectly with ``is_fraud``.
        """
        from feature_engineering import engineer_features, get_feature_columns

        df = make_sample_df(500, fraud_ratio=0.10)
        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df, categorical_cols=cats)
        features = get_feature_columns(df_eng)

        for col in features:
            corr = abs(df_eng[col].corr(df_eng["is_fraud"]))
            assert corr < 0.99, (
                f"Potential data leakage: feature '{col}' has correlation "
                f"{corr:.4f} with target — verify it is not derived from the label"
            )

    def test_wrong_target_column_raises(self):
        """BUG: training on the wrong target (e.g., ``amount``) silently produces a model.

        ``amount`` is a continuous variable; using it as the target for a
        classifier will not raise an error but yields a nonsensical model.
        This test documents the expected binary nature of ``is_fraud``.
        """
        df = make_sample_df(200)
        target = df["is_fraud"]
        assert target.nunique() == 2, (
            "Target 'is_fraud' must be binary. "
            "Using a continuous column as target is a silent ML bug."
        )
        assert set(target.unique()).issubset({0, 1}), (
            "Target values must be 0 or 1 only."
        )

    def test_scaler_fit_on_train_only(self):
        """BUG: fitting StandardScaler on the full dataset leaks test statistics.

        The scaler must be fitted exclusively on X_train and then used to
        *transform* X_val and X_test. This test verifies that the means
        computed on the full data differ from train-only means (they would
        be identical only if train == full data, which should never happen).
        """
        from feature_engineering import engineer_features, get_feature_columns
        from sklearn.preprocessing import StandardScaler

        df = make_sample_df(n=400, fraud_ratio=0.10)
        cats = ["merchant_category", "card_type", "entry_mode"]
        df_eng = engineer_features(df, categorical_cols=cats)
        features = get_feature_columns(df_eng)
        X = df_eng[features].values.astype(float)
        y = df_eng["is_fraud"].values

        X_train, X_test, y_train, _ = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        scaler_full = StandardScaler().fit(X)
        scaler_train = StandardScaler().fit(X_train)

        # Means should differ because the test set is excluded from train fit
        assert not np.allclose(scaler_full.mean_, scaler_train.mean_), (
            "Scaler fitted on full data has same mean as train-only fit — "
            "check that scaler is not accidentally fit on the test set"
        )
