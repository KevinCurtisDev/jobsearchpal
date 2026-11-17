# Offerlight backend

Python 3.12 · FastAPI · SQLAlchemy (async) · Alembic · Celery · Redis · PostgreSQL + pgvector.

```bash
uv sync                      # install (add --extra cv --extra ml as stages need them)
uv run pytest                # tests
uv run ruff check . && uv run mypy app
uv run uvicorn app.main:app --reload   # needs Postgres + Redis (or use `make up` from the root)
```

Layout and conventions: `../docs/01-architecture.md` and `../CLAUDE.md`.
