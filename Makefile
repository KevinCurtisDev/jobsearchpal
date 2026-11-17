COMPOSE = docker compose -f infra/docker-compose.yml --env-file .env

.PHONY: setup up down logs migrate revision test test-backend test-frontend lint fmt e2e tokens api-types shell-db beta-up beta-migrate backup-now restore-test privacy-docs privacy-check privacy-lock

setup: ## First-time setup
	@test -f .env || cp .env.example .env
	@command -v pre-commit >/dev/null && pre-commit install || echo "Install pre-commit for git hooks: pipx install pre-commit"
	cd frontend && npm ci

up: ## Start the full stack
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=100

migrate: ## Apply database migrations
	$(COMPOSE) run --rm api alembic upgrade head

revision: ## Create a migration: make revision m="add users"
	$(COMPOSE) run --rm api alembic revision --autogenerate -m "$(m)"

test: test-backend test-frontend

test-backend:
	cd backend && uv run pytest

test-frontend:
	cd frontend && npm test

lint:
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app
	cd frontend && npm run lint && npm run typecheck && npm run format:check

fmt:
	cd backend && uv run ruff format . && uv run ruff check --fix .
	cd frontend && npm run format

e2e:
	cd frontend && npx playwright test

# ── Privacy (docs/13-privacy-and-compliance.md) ──────
privacy-docs: ## Regenerate the Record of Processing Activities from the data inventory
	cd backend && uv run python -m app.privacy.ropa > ../docs/privacy/records-of-processing.md

privacy-check: ## Validate inventory, models, plans, consent wording and generated docs
	cd backend && uv run pytest tests/privacy -q --no-cov

privacy-lock: ## Re-lock consent wording after an approved non-material edit (typo fix)
	cd backend && uv run python -c "import hashlib,json,pathlib; d=pathlib.Path('../content/consents'); json.dump({f.stem: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(d.glob('*.v*.md'))}, open(d/'wording.lock.json','w'), indent=2); open(d/'wording.lock.json','a').write(chr(10))"

tokens: ## Regenerate CSS tokens from design/tokens.json
	cd frontend && npm run tokens

api-types: ## Regenerate the TypeScript API client types (API must be running)
	cd frontend && npm run api:generate

shell-db:
	$(COMPOSE) exec postgres psql -U offerlight

# ── Tier 0 beta box (run on the server) ──────────────
BETA = docker compose -f infra/docker-compose.beta.yml --env-file .env

beta-up: ## Start the single-server private beta stack
	$(BETA) up -d --build

beta-migrate:
	$(BETA) run --rm migrate

backup-now: ## Take an off-site backup immediately
	$(BETA) exec backup /usr/local/bin/backup.sh

restore-test: ## Restore the newest backup into a scratch database and check it
	$(BETA) exec backup /usr/local/bin/restore-test.sh
