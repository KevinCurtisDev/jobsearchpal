# ADR 0001 · Monorepo with Docker, FastAPI and React

**Status:** Accepted · 2026-10-20

## Context
The platform needs a Python ecosystem (statistics, ML, NLP, document generation) and a modern,
accessible web front end. A small team (plus Claude Code) will build it in stages.

## Decision
- One Git repository with `backend/` (Python 3.12, FastAPI, SQLAlchemy, Celery),
  `frontend/` (React, TypeScript, Vite) and `infra/` (Docker Compose, Caddy).
- PostgreSQL (+ pgvector) as the single system of record; Redis for queues and short-lived data.
- Docker Compose for local development and the first production deployment.

## Consequences
- One place for docs, CI and versioning; atomic changes across API and UI.
- Python gives direct access to scikit-learn, LightGBM, lifelines, econml, WeasyPrint.
- A single backend image runs API, worker and scheduler — simple to operate early on.
