# 🛡️ FraudShield AI

> **Production-grade MLOps platform for real-time credit card fraud detection.**
> Built with a futuristic 3D fintech UI, automated ML pipeline, and full observability stack.

[![CI](https://github.com/your-org/fraudshield-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fraudshield-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [ML Pipeline](#ml-pipeline)
- [API Reference](#api-reference)
- [Monitoring](#monitoring)
- [CI/CD](#cicd)
- [Development Guide](#development-guide)

---

## Overview

FraudShield AI is a complete, production-ready fraud detection system that covers the entire MLOps lifecycle:

| Stage | Technology |
|-------|-----------|
| Data Ingestion | CSV upload, REST API streaming |
| Data Validation | Great Expectations (19 expectations) |
| Feature Engineering | Custom + SMOTE balancing |
| Model Training | XGBoost + LightGBM with MLflow tracking |
| Model Registry | MLflow Model Registry (champion/challenger) |
| Serving | FastAPI with WebSocket real-time feed |
| Orchestration | Apache Airflow (3 DAGs) |
| Drift Monitoring | Evidently AI + Grafana |
| Infrastructure | Docker Compose (12 services) |
| CI/CD | GitHub Actions (lint → test → build → deploy) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Port 80)                         │
│                     Next.js 14 + Three.js                        │
│           Glassmorphism UI · 3D Globe · Live Feed                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Nginx Reverse Proxy
         ┌─────────────────┼─────────────────────┐
         │                 │                     │
         ▼                 ▼                     ▼
   ┌──────────┐     ┌──────────┐         ┌──────────┐
   │ FastAPI  │     │ MLflow   │         │ Airflow  │
   │ :8000    │     │ :5000    │         │ :8080    │
   │ + WSS    │     │ UI+API   │         │ 3 DAGs   │
   └─────┬────┘     └────┬─────┘         └────┬─────┘
         │               │                    │
         └───────────────┼────────────────────┘
                         │
              ┌──────────▼──────────┐
              │     PostgreSQL      │
              │  fraudshield│mlflow │
              │  airflow databases  │
              └─────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │Prometheus│  │ Grafana  │  │  Redis   │
    │ :9090    │  │ :3001    │  │ :6379    │
    └──────────┘  └──────────┘  └──────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, Tailwind CSS, Framer Motion, Three.js |
| **Backend** | FastAPI, Pydantic v2, SQLAlchemy (async) |
| **Database** | PostgreSQL 16 |
| **ML Models** | XGBoost, LightGBM, SMOTE, scikit-learn |
| **Experiment Tracking** | MLflow 2.x |
| **Data Version Control** | DVC |
| **Orchestration** | Apache Airflow 2.9 (Celery) |
| **Data Validation** | Great Expectations 0.18 |
| **Drift Monitoring** | Evidently AI |
| **Metrics** | Prometheus + Grafana |
| **Cache/Broker** | Redis |
| **Containers** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |

---

## Quick Start

### Prerequisites
- Docker Desktop ≥ 24.0
- Docker Compose ≥ 2.24

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/fraudshield-ai.git
cd fraudshield-ai
cp .env.example .env   # edit secrets if needed
```

### 2. Launch Full Stack

```bash
make up
# or directly:
docker compose -f infrastructure/docker-compose.yml up -d
```

### 3. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | — |
| **API Docs** | http://localhost:8000/docs | — |
| **MLflow UI** | http://localhost:5000 | — |
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **Grafana** | http://localhost:3001 | admin / fraudshield |
| **Prometheus** | http://localhost:9090 | — |

### 4. Run the ML Pipeline

```bash
# Using DVC (inside ml container or locally with deps installed)
cd ml && dvc repro

# Or trigger via Airflow UI
# → DAGs → fraud_training_pipeline → Trigger
```

---

## Project Structure

```
fraudshield-ai/
├── frontend/                  # Next.js 14 app
│   ├── app/
│   │   └── (dashboard)/       # Dashboard pages
│   └── components/
│       ├── three/             # Three.js 3D scenes
│       ├── dashboard/         # KPI cards, feeds, gauges
│       └── ui/                # Sidebar, TopBar
│
├── backend/                   # FastAPI service
│   └── app/
│       ├── api/v1/            # REST + WebSocket endpoints
│       ├── core/              # Config, DB, security
│       ├── ml/                # Predictor & feature eng.
│       └── schemas/           # Pydantic models
│
├── ml/                        # MLOps pipeline
│   ├── src/                   # Pipeline stages
│   ├── great_expectations/    # Validation suite
│   ├── dvc.yaml               # Pipeline definition
│   └── params.yaml            # Hyperparameters
│
├── airflow/
│   └── dags/                  # 3 production DAGs
│
├── monitoring/
│   ├── prometheus/            # Scrape config
│   └── grafana/               # Dashboards & provisioning
│
├── infrastructure/
│   ├── docker-compose.yml     # Full stack (12 services)
│   └── nginx/nginx.conf
│
├── .github/workflows/         # CI + CD pipelines
├── tests/                     # Backend + ML tests
└── Makefile                   # Dev shortcuts
```

---

## ML Pipeline

The DVC pipeline consists of 6 stages:

```
ingest → validate → preprocess → train → evaluate → register
```

### Stage Details

| Stage | Script | Output |
|-------|--------|--------|
| `ingest` | `data_ingestion.py` | `data/raw/transactions.csv` |
| `validate` | `validate_data.py` | `data/raw/validation_report.json` |
| `preprocess` | `preprocessing.py` | `data/processed/*.pkl` |
| `train` | `train.py` | XGBoost + LightGBM models |
| `evaluate` | `evaluate.py` | `metrics.json`, plot files |
| `register` | `register_model.py` | MLflow Model Registry entry |

### Model Performance (Synthetic Data)

| Metric | XGBoost | LightGBM |
|--------|---------|----------|
| F1 Score | ~0.91 | ~0.90 |
| AUC-PR | ~0.93 | ~0.92 |
| ROC-AUC | ~0.98 | ~0.97 |
| Precision | ~0.90 | ~0.88 |
| Recall | ~0.93 | ~0.92 |

---

## API Reference

### Predict Single Transaction

```http
POST /api/v1/predict/
Content-Type: application/json

{
  "amount": 1547.99,
  "merchant_category": "online_retail",
  "card_type": "visa",
  "entry_mode": "online",
  "hour_of_day": 2,
  "day_of_week": 4,
  "merchant_risk_score": 0.82,
  "velocity_score": 0.71,
  "distance_from_home": 3421,
  "transaction_count_1h": 8
}
```

**Response:**
```json
{
  "fraud_probability": 0.8923,
  "is_fraud": true,
  "risk_level": "HIGH",
  "model_version": "3",
  "threshold_used": 0.5,
  "processing_time_ms": 14.2
}
```

### Batch Prediction

```http
POST /api/v1/predict/batch
Content-Type: application/json

{"transactions": [...]}
```

### Ingest CSV

```http
POST /api/v1/ingest/csv?score_fraud=true
Content-Type: multipart/form-data

file: transactions.csv
```

### WebSocket Live Feed

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/live-transactions");
ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  // data contains real-time transaction events
};
```

---

## Monitoring

### Grafana Dashboard

Access at **http://localhost:3001** (admin / fraudshield).

Pre-configured panels:
- API request rate & latency (P50/P99)
- Fraud detection rate over time
- Model prediction confidence distribution
- Active WebSocket connections

### Evidently AI Drift Reports

Generated daily by the `drift_monitoring_pipeline` DAG.
HTML reports saved to `ml/data/drift_reports/`.
JSON summaries served by the API at `GET /api/v1/analytics/drift`.

---

## CI/CD

### GitHub Actions Workflows

| Workflow | Trigger | Jobs |
|----------|---------|------|
| `ci.yml` | PR / push | Backend tests, ML tests, Frontend build |
| `cd-production.yml` | `v*.*.*` tag | Build & push to GHCR, SSH deploy, health check |

### Required GitHub Secrets

```
PROD_HOST        — Production server hostname
PROD_USER        — SSH username
PROD_SSH_KEY     — Private SSH key
```

---

## Development Guide

### Local Development (No Docker)

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# ML Pipeline
cd ml && pip install -r requirements.txt
python src/data_ingestion.py
python src/train.py
```

### Run Tests

```bash
make test
# or individually:
pytest tests/backend/ -v
pytest tests/ml/ -v
```

### Trigger Full ML Pipeline Manually

```bash
make ml-pipeline   # Uses DVC
# or
cd ml && dvc repro
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL URL |
| `MLFLOW_TRACKING_URI` | `http://mlflow:5000` | MLflow server URL |
| `MLFLOW_MODEL_NAME` | `fraudshield_classifier` | Registry model name |
| `FRAUD_THRESHOLD` | `0.5` | Classification threshold |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend API base URL |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built with ❤️ for the MLOps community</strong><br/>
  FraudShield AI · Production-grade fraud detection
</div>
