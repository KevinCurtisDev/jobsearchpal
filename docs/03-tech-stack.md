# 03 · Tech stack and libraries

Pin exact versions in lockfiles (`backend/uv.lock`, `frontend/package-lock.json`). Dependabot
proposes updates weekly. Prefer well-maintained, widely used libraries.

## Runtime and tooling

| Tool | Version | Use |
| --- | --- | --- |
| Docker + Compose v2 | current | Local stack and production images |
| Python | 3.12 | Backend, workers, ML |
| uv | current | Python dependency and environment manager |
| Node.js | 22 LTS | Frontend build and tooling |
| PostgreSQL | 16 + pgvector | Database and vector search |
| Redis | 7 | Queues, sessions, rate limits, cache |
| Caddy | 2 | Reverse proxy, TLS, security headers |
| MinIO | current | S3-compatible storage in development |
| Mailpit | current | Catch-all email in development |
| GitHub Actions | — | CI/CD |
| pre-commit | current | Local hooks: ruff, prettier, gitleaks, end-of-file fixers |

## Backend (Python)

| Library | Purpose |
| --- | --- |
| fastapi, uvicorn, gunicorn | API framework and servers |
| pydantic v2, pydantic-settings | Validation and configuration |
| sqlalchemy 2 (async), asyncpg, alembic | ORM, driver, migrations |
| pgvector (python) | Vector column type |
| redis | Redis client |
| celery | Background jobs and schedules |
| httpx | Outbound HTTP (with timeouts, retries via tenacity) |
| tenacity | Retries with backoff |
| structlog | Structured logging |
| sentry-sdk | Error tracking |
| prometheus-fastapi-instrumentator | Metrics |
| webauthn (py_webauthn) | Passkey registration and authentication |
| itsdangerous / secrets (stdlib) | Signed tokens, CSPRNG |
| email-validator, dnspython | Email syntax and MX checks |
| boto3 | S3 storage, pre-signed URLs |
| pdfplumber | PDF text extraction |
| python-docx | DOCX reading and writing |
| python-magic | File type detection by magic bytes |
| jinja2 | CV HTML templates, email templates |
| weasyprint | HTML → PDF rendering |
| anthropic | Claude API client (writing tasks) |
| stripe | Payments |
| rank-bm25 (or Postgres FTS) | Lexical retrieval |
| sentence-transformers | Self-hosted embeddings (small multilingual model) |
| scikit-learn | TF-IDF, logistic regression, isotonic calibration, Isolation Forest, NMF |
| lightgbm | Gradient-boosted classifier and LambdaMART ranker |
| shap | Explanations for tree models |
| lifelines | Kaplan–Meier, Cox, Weibull AFT, competing risks helpers |
| econml or causalml | Uplift / heterogeneous treatment effect models |
| statsmodels, scipy, numpy, pandas (or polars) | Statistics and data handling |
| datasketch | MinHash / LSH near-duplicate detection |
| rapidfuzz | Fuzzy string matching for company resolution |
| faster-whisper | Self-hosted speech-to-text for practice recordings |
| ffmpeg (system) | Audio extraction from recordings |
| pytest, pytest-asyncio, pytest-cov, httpx (test client), freezegun, respx | Testing |
| ruff, mypy | Lint, format, types |
| pip-audit | Dependency vulnerability audit |

## Frontend (TypeScript)

| Library | Purpose |
| --- | --- |
| react, react-dom | UI |
| typescript (strict) | Types |
| vite | Dev server and build |
| react-router | Routing |
| @tanstack/react-query | Server state |
| react-hook-form, zod, @hookform/resolvers | Forms and validation |
| @radix-ui/react-* | Accessible primitives (Dialog, Tabs, Switch, DropdownMenu, Tooltip, Toast) |
| @simplewebauthn/browser | Passkey ceremonies in the browser |
| openapi-typescript, openapi-fetch | Typed API client from the backend's OpenAPI |
| clsx | Class names |
| vitest, @testing-library/react, @testing-library/user-event, jsdom | Unit tests |
| @playwright/test, @axe-core/playwright | End-to-end and accessibility tests |
| eslint (typescript-eslint, jsx-a11y, react-hooks), prettier | Lint and format |

Charts are small, custom SVG components (funnel bars, effect ranges, reply curves) built to
the design spec with text alternatives, not a heavy chart library.

## Infrastructure and services

See `10-external-apis.md` for every external API, and `12-deployment-and-ops.md` for hosting.

## Extension and shared packages (Track E)

Verify current versions and maintenance status at kickoff of E1; pin in lockfiles.

| Tool | Use |
| --- | --- |
| WXT (or Vite + CRXJS) | Manifest V3 build, multi-browser output |
| TypeScript (strict), zod | Types and validation at every boundary |
| Dexie | IndexedDB access, migrations, live queries |
| React + CSS Modules + Radix | Side panel, popup, options dashboard (shared `packages/ui`) |
| Shadow DOM, vanilla or Preact | Tiny injected UI in content scripts |
| pdf.js (lazy), fflate | Read PDF and DOCX locally |
| pdf-lib, docx | Write PDF and DOCX locally |
| MiniSearch | User-facing search box |
| Web Crypto | Optional passphrase-encrypted backup |
| Vitest, Playwright (extension mode), axe | Tests, offline test, accessibility |
| dependency-cruiser, custom bundle scan | Layering rule and the network audit |

Not used in the local edition: analytics SDKs, CDNs, remote fonts, OCR, on-device LLMs.
