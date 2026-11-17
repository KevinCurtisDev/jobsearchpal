# 12 · Deployment and operations

## Environments

| Environment | Purpose | How |
| --- | --- | --- |
| Local | Development | `make up` (infra/docker-compose.yml): hot reload, Mailpit, MinIO |
| Staging | Pre-release testing, ZAP scans | Auto-deploy from `main` |
| Production | Live | Deploy on tagged release (`v*`) with manual approval. Tier 0 during the private beta, Tier 1 from the public beta (see below) |

All data stays in the **EU** (Ireland region preferred). Staging never holds real user data.

## Hosting: start small, then step up

The same Docker images and code run at every tier; only configuration and where the
database lives change. Step up when a trigger is hit, not on a fixed date.

| Tier | When | Setup | Approx. monthly cost |
| --- | --- | --- | --- |
| **0 · Beta box** | Private beta: invited users only (up to ~300), **no payments** | One EU server running everything with `infra/docker-compose.beta.yml`: Caddy, API, worker, beat, PostgreSQL, Redis, nightly off-site backups. Frontend on Cloudflare Pages. Files in object storage from day one. | ~€30–50 |
| **1 · Resilient lean** | Public beta onwards, and **before taking any payment** | Frontend on Cloudflare Pages · **two** app servers behind a load balancer (`infra/docker-compose.prod.yml`) · **managed PostgreSQL with a standby** and point-in-time recovery · managed Redis (or sessions and rate limits in Postgres) · object storage · off-site nightly backup to a second provider · uptime monitoring | ~€80–130 |
| **2 · Growth** | Sustained load, or Phase 2–3 features (matching, transcription) need more CPU | Larger managed database · three or more app servers · a separate worker pool for CPU-heavy jobs · optionally a managed container platform | ~€250–400 |

All providers must be EU-based or EU-hosted. Example choices (confirm current prices):
Hetzner (servers, load balancer, object storage), Scaleway (managed PostgreSQL with HA,
point-in-time recovery), Upstash (managed Redis), Cloudflare (Pages, Turnstile).

### Triggers to move from Tier 0 to Tier 1

Move at the **first** of these:
- Two weeks before the public launch at the launch gate (date set by the owners once Stage 10 is in beta)
- Before the first real payment is taken
- More than ~300 weekly active users
- Any outage longer than one hour, or any backup restore test that fails

Triggers to move from Tier 1 to Tier 2: p95 API latency over 500 ms for a week, worker
queue backlog over 15 minutes on most days, or database CPU above 70% at peak.

### Rules that keep the move easy (apply from Stage 0)

- **No state on servers:** uploaded files and recordings go to object storage; sessions and
  rate limits live in Redis or Postgres, never in server memory or local disk.
- **Config only through environment variables** (`DATABASE_URL`, `REDIS_URL`, `S3_*`).
  Moving tiers changes `.env`, not code.
- **Background jobs are idempotent** and safe to re-run (`task_acks_late` is already on).
- **Server setup is scripted** (Terraform for servers, load balancer and DNS; cloud-init to
  install Docker and pull images), so a new server is ready in minutes.
- **DNS TTL of 5 minutes** on the app domain ahead of any move.

### Tier 0 safeguards (the beta box is a single point of failure)

- Nightly `pg_dump` to object storage at a **different provider**, encrypted, 30-day
  retention (the `backup` service in `docker-compose.beta.yml`).
- Weekly restore test into a throwaway container; record the result in `docs/STATUS.md`.
- Hetzner (or equivalent) server snapshots enabled.
- Uptime monitor on `/api/v1/ready` with phone alerts.
- Tell beta users that short outages are possible.
- Never store payment data on Tier 0 (no payments until Tier 1).

### Migration runbook: Tier 0 → Tier 1 (rehearse on staging first)

1. Provision with Terraform: managed PostgreSQL (with standby and PITR), managed Redis,
   two app servers, load balancer with health checks on `/api/v1/ready`.
2. Lower DNS TTL to 5 minutes at least a day before.
3. Announce a 30-minute maintenance window to beta users.
4. Put the beta box in maintenance mode (Caddy serves a maintenance page; workers stopped).
5. `pg_dump -Fc` from the beta box → `pg_restore` into the managed database. Check row counts
   on key tables (`users`, `cv_versions`, `applications`, `application_events`).
   For a near-zero-downtime move later, use logical replication instead.
6. Update `.env` on the new servers (`DATABASE_URL`, `REDIS_URL`), deploy images, run
   `alembic upgrade head` once.
7. Smoke test through the load balancer: sign in with a passkey and an email code, open a CV,
   export a PDF.
8. Switch DNS to the load balancer. Watch error rates for an hour.
9. Keep the beta box stopped but intact for 7 days as a fallback, then delete it and its data.
10. Update `docs/STATUS.md` and the incident runbook with the new topology.

## Docker images

- `backend/Dockerfile` — multi-stage, Python 3.12 slim, `uv sync --frozen`, non-root user,
  WeasyPrint system libraries, healthcheck. Same image runs `api`, `worker`, `beat` with
  different commands.
- `frontend/Dockerfile` — Node 22 build stage → static files served by Caddy (prod) or
  nginx-unprivileged (standalone).
- Tag images with the git SHA; push to GitHub Container Registry (GHCR).

## CI/CD (GitHub Actions)

- `ci.yml` on every PR and push to `main`: lint, typecheck, tests (with Postgres + Redis
  service containers), build images, Trivy, pip-audit, npm audit, gitleaks.
- `codeql.yml`: weekly and on PRs.
- `deploy.yml` (create in Stage 0 once hosting is chosen): on `main` → staging; on tag →
  production with environment approval. Steps: build and push images → run migrations
  (`alembic upgrade head`) as a one-off job → rolling restart → smoke test `/api/v1/ready`.
- Required repository secrets are listed in `.env.example` (production values live in the
  hosting provider's secret manager and GitHub Environments, never in the repo).

## GitHub repository settings

- Private repo; `main` protected: PRs required, 1 approval (or Claude Code + owner review),
  status checks required, linear history, no force push.
- Enable: Dependabot alerts and security updates, secret scanning + push protection,
  CodeQL, private vulnerability reporting.
- Environments `staging` and `production` with required reviewers on production.

## Database

- Migrations with Alembic; every migration reversible where possible; never drop columns
  holding user data in the same release that stops using them (expand → migrate → contract).
- Backups: daily automated snapshots, 30-day retention, point-in-time recovery; monthly
  restore test into staging (with anonymisation if any real data is involved).

## Scheduled jobs (Celery beat)

| Job | When (Europe/Dublin) |
| --- | --- |
| Job ingestion | 01:00 daily |
| Public data refresh (sponsor register, permits, disposable domains) | Weekly, Sunday 03:00 |
| Matching + digest build | 05:30 daily; send at each user's chosen time |
| Company reply statistics | 04:00 daily |
| Retention clean-up (recordings, raw payloads, pending accounts, deletions) | Hourly |
| Benchmark and effect recomputation | Nightly |
| Model monitoring report | Weekly, Monday 07:00 |

## Observability

- Logs: JSON (structlog) with `request_id`, `user_id` (no emails), route, latency.
- Errors: Sentry (EU region), PII scrubbing on.
- Metrics: Prometheus format from API and workers; dashboards for latency, error rate,
  queue depth, ingestion counts, AI spend, sign-up rejections.
- Alerts: error rate > 2% for 5 min, queue backlog > 15 min, ingestion failure, AI spend
  > 80% of budget, sign-up velocity anomaly, certificate expiry.

## Incident runbook (summary)

1. Triage severity (S1 data breach or outage → S3 minor).
2. Contain (feature flag off, revoke keys, block IPs, maintenance mode).
3. Communicate (status page, users if affected).
4. Personal-data breach: assess within 24 h; notify the Data Protection Commission within
   72 hours when required; notify affected users without undue delay when high risk.
5. Post-incident review within 5 working days; actions tracked as issues.

## Launch checklist (end of Stage 4)

- [ ] Pen test complete, highs fixed
- [ ] Accessibility audit (automated + manual + one external review)
- [ ] Privacy policy, terms, DPIA, records of processing, sub-processor list published/filed
- [ ] Backups restored successfully in a test
- [ ] Monitoring and alerts firing in a drill
- [ ] Rate limits and bot protection tuned on staging traffic
- [ ] Email domain authenticated (SPF, DKIM, DMARC at `p=quarantine` or stricter)
- [ ] `security.txt` published; SECURITY.md contact live
- [ ] Support inbox and response process ready
