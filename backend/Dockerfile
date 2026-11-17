# syntax=docker/dockerfile:1
FROM python:3.15-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
# WeasyPrint (Stage 2) needs Pango; libmagic for file type checks; ffmpeg for recordings (Stage 10)
RUN apt-get update && apt-get install -y --no-install-recommends \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libmagic1 ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

FROM base AS deps
ARG EXTRAS=""
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev ${EXTRAS}

FROM base AS dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
COPY --from=deps /app/.venv /app/.venv
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/api/v1/health || exit 1
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "--access-logfile", "-"]
