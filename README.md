# Offerlight

> Working name. Job search for Ireland and the UK — **built for offers received, not applications submitted.**

This folder is a complete development package. Point Claude Code at it and start with `CLAUDE.md`.

> **Build order:** the Chrome extension is built first (`docs/16-chrome-extension.md`), then the platform.

## What's inside

```
offerlight/
├── CLAUDE.md                 # How Claude Code should work in this repo (start here)
├── README.md                 # This file
├── SECURITY.md               # How to report vulnerabilities
├── Makefile                  # make up / test / lint / migrate …
├── .env.example              # Every environment variable, documented
├── docs/                     # Product, architecture, stages, specs
│   ├── 00-overview.md
│   ├── 01-architecture.md
│   ├── 02-build-stages.md    # The build plan, stage by stage
│   ├── 03-tech-stack.md
│   ├── 04-data-model.md
│   ├── 05-api-spec.md
│   ├── 06-security.md
│   ├── 07-design-system.md
│   ├── 08-screens.md
│   ├── 09-ml-and-analytics.md
│   ├── 10-external-apis.md
│   ├── 11-testing-and-quality.md
│   ├── 12-deployment-and-ops.md
│   ├── 13-privacy-and-compliance.md   # GDPR by design — start here for anything about personal data
│   ├── 14-content-guidelines.md
│   ├── 15-cost-efficiency.md
│   ├── 16-chrome-extension.md  # The first product: review, architecture, roadmap
│   ├── 17-jobpilot-spec-review.md  # JobPilot spec reconciled: F01-F29, data model, risks, backlog, first slice
│   ├── STATUS.md             # Progress tracker (Claude Code keeps this current)
│   ├── decisions-needed.md   # Decisions only the owners can make
│   ├── privacy/              # Generated record of processing, LIAs, DPIAs, breach and rights runbooks
│   └── adr/                  # Architecture decision records
├── design/                   # Design tokens and the link to the design canvas
├── content/                  # Data files: banned phrases, interview questions, consent wording, …
├── prompts/                  # Versioned AI prompts and their output schemas
├── backend/                  # Python 3.12 · FastAPI · SQLAlchemy · Celery
│   └── app/privacy/          # data_inventory.toml: every piece of personal data, its basis and retention
├── frontend/                 # React · TypeScript · Vite
├── extension/                # Chrome extension (Track E; not started, see its README)
├── packages/                 # Shared TypeScript: core rules, data packs, storage, adapters, ui (Track E)
├── infra/                    # Docker Compose (dev, beta box, prod), Caddy, backups
└── .github/                  # CI, CodeQL, Dependabot, PR template
```

## Quick start

Requirements: Docker Desktop (or Docker Engine + Compose v2), Git, Make.
Optional for working outside Docker: Python 3.12 with `uv`, Node 22.

```bash
make setup     # copies .env.example to .env, installs git hooks
make up        # starts Postgres, Redis, Mailpit, MinIO, API, worker, scheduler, frontend
make migrate   # creates the database tables
open http://localhost:5173
```

## Putting it on GitHub

The folder is already a git repository with one initial commit on `main`. Create a private
GitHub repo and push:

```bash
gh repo create offerlight --private --source=. --push
# or: git remote add origin git@github.com:<you>/offerlight.git && git push -u origin main
```

Then in GitHub: protect `main` (require pull requests and passing CI), enable Dependabot
alerts, secret scanning and push protection. See `docs/12-deployment-and-ops.md`.

## Starting Claude Code

Open this folder in Claude Code and give it this first prompt:

> Read CLAUDE.md, then docs/00-overview.md, docs/02-build-stages.md and docs/STATUS.md.
> We are on Stage 0. Check that the scaffold runs and its tests pass, then work through the
> Stage 0 tasks one branch and pull request at a time. Ask me before anything listed in
> docs/decisions-needed.md.

After each stage, review the pull requests, check `docs/STATUS.md`, and tell Claude Code to
start the next stage.

## Status

The scaffold runs and its tests pass. Product features are built stage by stage — see
`docs/02-build-stages.md` and `docs/STATUS.md`.
