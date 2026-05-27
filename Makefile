# AirWatch Makefile
# Common dev tasks. Run `make` for the full list.

API_DIR := apps/api
WEB_DIR := apps/web

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ----- infrastructure -------------------------------------------------------

.PHONY: up
up: ## Start Postgres + Redis + API + worker + beat via Docker Compose
	docker compose -f infra/docker-compose.yml up -d --build

.PHONY: down
down: ## Stop and remove all containers
	docker compose -f infra/docker-compose.yml down

.PHONY: logs
logs: ## Tail logs from every service
	docker compose -f infra/docker-compose.yml logs -f

.PHONY: ps
ps: ## Show service status
	docker compose -f infra/docker-compose.yml ps

# ----- database -------------------------------------------------------------

.PHONY: migrate
migrate: ## Apply Alembic migrations to head
	cd $(API_DIR) && PYTHONPATH=. alembic upgrade head

.PHONY: migration
migration: ## Generate a new Alembic migration: make migration name=add_x
	cd $(API_DIR) && PYTHONPATH=. alembic revision --autogenerate -m "$(name)"

.PHONY: seed
seed: ## Seed the locations table
	cd $(API_DIR) && PYTHONPATH=. python app/scripts/seed_locations.py

# ----- backend dev ----------------------------------------------------------

.PHONY: api
api: ## Run the API locally (requires postgres + redis up)
	cd $(API_DIR) && PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: worker
worker: ## Run a Celery worker locally
	cd $(API_DIR) && PYTHONPATH=. celery -A app.worker.celery_app worker -l INFO

.PHONY: beat
beat: ## Run the Celery beat scheduler locally
	cd $(API_DIR) && PYTHONPATH=. celery -A app.worker.celery_app beat -l INFO

# ----- frontend -------------------------------------------------------------

.PHONY: web
web: ## Run the Vite dev server
	cd $(WEB_DIR) && npm run dev

.PHONY: web-build
web-build: ## Build the frontend for production
	cd $(WEB_DIR) && npm run build

# ----- quality gates --------------------------------------------------------

.PHONY: test
test: ## Run the Python test suite
	cd $(API_DIR) && PYTHONPATH=. pytest -q

.PHONY: lint
lint: ## Run ruff
	ruff check .

.PHONY: lint-fix
lint-fix: ## Run ruff with autofix
	ruff check . --fix

.PHONY: typecheck
typecheck: ## TypeScript typecheck on the web app
	cd $(WEB_DIR) && npm run typecheck

.PHONY: check
check: lint test typecheck ## Run all quality gates
	@echo "✓ all checks passed"

# ----- ops -----------------------------------------------------------------

.PHONY: ingest
ingest: ## Trigger an air ingest run via the admin endpoint
	curl -s -X POST 'http://localhost:8000/admin/ingest/air?hours=24' | python -m json.tool

.PHONY: loadtest
loadtest: ## Hammer the API. Override: make loadtest C=100 N=50
	cd $(API_DIR) && python scripts/loadtest.py \
		--base-url http://localhost:8000 \
		--concurrency $(or $(C),50) \
		--requests-per-client $(or $(N),20)
