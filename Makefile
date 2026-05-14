.PHONY: help up down build dev-frontend dev-backend ml-pipeline lint test clean logs

# ─── Help ────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  FraudShield AI — MLOps Platform"
	@echo "  ================================"
	@echo ""
	@echo "  make up           Start full stack (Docker)"
	@echo "  make down         Stop all containers"
	@echo "  make build        Rebuild all Docker images"
	@echo "  make dev-frontend Run Next.js dev server"
	@echo "  make dev-backend  Run FastAPI dev server"
	@echo "  make ml-pipeline  Run DVC ML pipeline"
	@echo "  make lint         Lint all code"
	@echo "  make test         Run all tests"
	@echo "  make logs         Tail all container logs"
	@echo "  make clean        Remove all containers, volumes, networks"
	@echo ""

# ─── Docker ──────────────────────────────────────────────────────────────────
up:
	docker compose -f infrastructure/docker-compose.yml up -d

down:
	docker compose -f infrastructure/docker-compose.yml down

build:
	docker compose -f infrastructure/docker-compose.yml build --no-cache

logs:
	docker compose -f infrastructure/docker-compose.yml logs -f

clean:
	docker compose -f infrastructure/docker-compose.yml down -v --remove-orphans
	docker system prune -f

# ─── Development ─────────────────────────────────────────────────────────────
dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ─── ML Pipeline ─────────────────────────────────────────────────────────────
ml-pipeline:
	cd ml && dvc repro

ml-train:
	cd ml && python src/train.py

ml-validate:
	cd ml && great_expectations checkpoint run fraud_data_checkpoint

# ─── Code Quality ─────────────────────────────────────────────────────────────
lint:
	cd backend && ruff check app/ --fix
	cd ml && ruff check src/ --fix
	cd frontend && npm run lint

test:
	cd backend && pytest ../tests/backend/ -v --tb=short
	cd ml && pytest ../tests/ml/ -v --tb=short

# ─── Setup ───────────────────────────────────────────────────────────────────
setup-frontend:
	cd frontend && npm install

setup-backend:
	cd backend && pip install -r requirements.txt

setup-ml:
	cd ml && pip install -r requirements.txt && dvc init --no-scm

setup: setup-frontend setup-backend setup-ml
	@echo "✅ FraudShield AI setup complete"
