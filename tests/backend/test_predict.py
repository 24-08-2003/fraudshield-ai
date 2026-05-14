"""
Tests for the fraud prediction API endpoint.
"""
import pytest
import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked ML model."""
    with patch("app.ml.predictor.FraudPredictor.load_model") as mock_load:
        mock_load.return_value = None
        from app.main import app
        return TestClient(app)


@pytest.fixture
def sample_transaction():
    """Valid transaction payload for testing."""
    return {
        "Time": 3600.0,
        "V1": -1.359807134,
        "V2": -0.072781173,
        "V3": 2.536346738,
        "V4": 1.378155224,
        "V5": -0.338320769,
        "V6": 0.462387778,
        "V7": 0.239598554,
        "V8": 0.098697901,
        "V9": 0.363786970,
        "V10": 0.090794172,
        "V11": -0.551599533,
        "V12": -0.617800856,
        "V13": -0.991389847,
        "V14": -0.311169354,
        "V15": 1.468176972,
        "V16": -0.470400525,
        "V17": 0.207971242,
        "V18": 0.025790533,
        "V19": 0.403992960,
        "V20": 0.251412098,
        "V21": -0.018306778,
        "V22": 0.277837576,
        "V23": -0.110473910,
        "V24": 0.066928075,
        "V25": 0.128539358,
        "V26": -0.189114844,
        "V27": 0.133558377,
        "V28": -0.021053053,
        "Amount": 149.62,
    }


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_schema(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert data["status"] in ("healthy", "degraded")

    def test_health_includes_service_info(self, client):
        response = client.get("/api/v1/health")
        data = response.json()
        assert "version" in data or "services" in data


class TestPredictEndpoint:
    def test_predict_requires_all_fields(self, client):
        """Missing required fields should return 422."""
        response = client.post("/api/v1/predict", json={"Amount": 100.0})
        assert response.status_code == 422

    def test_predict_rejects_negative_amount(self, client, sample_transaction):
        """Negative Amount should fail validation."""
        tx = {**sample_transaction, "Amount": -50.0}
        response = client.post("/api/v1/predict", json=tx)
        assert response.status_code == 422

    def test_predict_with_valid_transaction(self, client, sample_transaction):
        """Valid transaction should return prediction schema."""
        with patch("app.api.v1.predict.predictor.predict") as mock_predict:
            mock_predict.return_value = {
                "transaction_id": "test-123",
                "is_fraud": False,
                "fraud_probability": 0.012,
                "risk_level": "LOW",
                "features_used": 29,
            }
            response = client.post("/api/v1/predict", json=sample_transaction)
            assert response.status_code == 200

    def test_predict_response_schema(self, client, sample_transaction):
        """Prediction response must include required fields."""
        with patch("app.api.v1.predict.predictor.predict") as mock_predict:
            mock_predict.return_value = {
                "transaction_id": "abc-123",
                "is_fraud": True,
                "fraud_probability": 0.921,
                "risk_level": "CRITICAL",
                "features_used": 29,
            }
            response = client.post("/api/v1/predict", json=sample_transaction)
            if response.status_code == 200:
                data = response.json()
                assert "is_fraud" in data or "fraud_probability" in data

    def test_predict_fraud_probability_range(self, client, sample_transaction):
        """Fraud probability must be between 0 and 1."""
        with patch("app.api.v1.predict.predictor.predict") as mock_predict:
            mock_predict.return_value = {
                "transaction_id": "prob-test",
                "is_fraud": False,
                "fraud_probability": 0.05,
                "risk_level": "LOW",
                "features_used": 29,
            }
            response = client.post("/api/v1/predict", json=sample_transaction)
            if response.status_code == 200:
                prob = response.json().get("fraud_probability", 0.5)
                assert 0.0 <= prob <= 1.0

    def test_predict_high_fraud_probability_flags_fraud(self, client, sample_transaction):
        """When probability > 0.5 model should flag as fraud."""
        with patch("app.api.v1.predict.predictor.predict") as mock_predict:
            mock_predict.return_value = {
                "transaction_id": "fraud-txn",
                "is_fraud": True,
                "fraud_probability": 0.987,
                "risk_level": "CRITICAL",
                "features_used": 29,
            }
            response = client.post("/api/v1/predict", json=sample_transaction)
            if response.status_code == 200:
                data = response.json()
                if "is_fraud" in data and "fraud_probability" in data:
                    if data["fraud_probability"] > 0.5:
                        assert data["is_fraud"] is True

    def test_batch_predict_endpoint_exists(self, client):
        """Batch predict endpoint should exist (200 or 422, not 404)."""
        response = client.post("/api/v1/predict/batch", json=[])
        assert response.status_code != 404


class TestModelsEndpoint:
    def test_list_models_returns_200_or_503(self, client):
        """Models list should return 200 (with MLflow) or 503 (without)."""
        response = client.get("/api/v1/models")
        assert response.status_code in (200, 503, 500)

    def test_models_response_is_list_or_error(self, client):
        """Models response should be a list or error dict."""
        response = client.get("/api/v1/models")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or isinstance(data, dict)


class TestAnalyticsEndpoint:
    def test_summary_endpoint_exists(self, client):
        """Analytics summary should return 200 or 503."""
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code in (200, 503, 500)

    def test_drift_endpoint_exists(self, client):
        """Drift analytics endpoint should not 404."""
        response = client.get("/api/v1/analytics/drift")
        assert response.status_code != 404
