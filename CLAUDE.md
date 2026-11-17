# CLAUDE.md — instructions for Claude Code

You are building **Offerlight** (working name), a job search platform for Ireland and the UK.
Its mission: **built for offers received, not applications submitted.**

This file tells you how to work in this repository. Read it fully before doing anything.

> **Build order (17 November 2026):** Hearback has two products. The **Chrome extension is built
> first** (Track E, `docs/16-chrome-extension.md`, ADR 0007), as a free-for-life, local-only tool
> that is also the front door to the platform. The platform stages in `docs/02-build-stages.md`
> continue after, re-baselined (see `docs/STATUS.md`). **Nothing in Track E beyond E0 starts until
> the owners approve `docs/16` and answer decisions #22, #23, #24 and #27.**

---

## 1. Read these first, in order

1. `docs/00-overview.md` — what the product is, principles, scope
2. `docs/02-build-stages.md` — the stage plan (Track E first, then the platform stages). **Work one stage at a time, in order.**
3. `docs/STATUS.md` — which stage is current and what is done
4. The docs the current stage lists under "Read before starting"

Everything else in `docs/` is reference: open it when the current stage needs it.

| Topic | File |
| --- | --- |
| Architecture | `docs/01-architecture.md` |
| Tech stack and libraries | `docs/03-tech-stack.md` |
| Data model | `docs/04-data-model.md` |
| API | `docs/05-api-spec.md` |
| Security | `docs/06-security.md` |
| Design system | `docs/07-design-system.md`, `design/tokens.json` |
| Screens | `docs/08-screens.md` |
| ML and analytics | `docs/09-ml-and-analytics.md` |
| External APIs | `docs/10-external-apis.md` |
| Testing | `docs/11-testing-and-quality.md` |
| Deployment and ops | `docs/12-deployment-and-ops.md` |
| Privacy and compliance (GDPR) | `docs/13-privacy-and-compliance.md`, `backend/app/privacy/data_inventory.toml`, `docs/privacy/` |
| Content and writing rules | `docs/14-content-guidelines.md`, `content/` |
| AI prompts | `prompts/` |
| Cost efficiency | `docs/15-cost-efficiency.md` |
| Chrome extension (first product) | `docs/16-chrome-extension.md`, `docs/17-jobpilot-spec-review.md` (takes precedence over 16), `docs/adr/0007-*`, `docs/adr/0008-*`, `extension/README.md`, `packages/README.md` |
| Open decisions | `docs/decisions-needed.md` |
| Architecture decisions | `docs/adr/` |

---

## 2. Non-negotiable product rules

These come from the product concept. Never break them, even if a task seems to ask for it.

1. **Rules and data decide, AI writes.** Use rules, statistics or classical ML first. Use the
   generative AI API only for writing, reading messy text, and judging interview answers.
   See `docs/09-ml-and-analytics.md` for which method each feature uses.
2. **No auto-apply.** The platform prepares applications; the user always submits them on the
   employer's site.
3. **No LinkedIn scraping**, and no scraping of any site whose terms forbid it. Use the
   sources in `docs/10-external-apis.md` only. The extension may read the job page the user is
   viewing on Tier A career sites, on user action; it has **no content scripts or injected UI on
   linkedin.com, indeed.com or glassdoor.com**, never crawls, never automates (ADR 0008).
4. **Never invent experience.** AI output must not add skills, employers, dates, numbers or
   qualifications the user did not provide. Enforce this in code (see `prompts/README.md`).
5. **Every score is explained, calibrated and honest about uncertainty.** Show reasons,
   a confidence level and the data source (your data / Offerlight data / public data).
6. **No face, emotion or appearance analysis** in video practice. Timing and words only.
7. **Privacy:** never sell data; one-click export and delete; consent before benchmarks,
   experiments or demographic data; minimal personal data sent to third parties.
8. **Accessibility:** WCAG 2.2 AA on every screen. Real buttons, links, labels; visible focus;
   44px targets; meaning never by colour alone.
9. **Security:** passwordless (passkeys + email codes), bot protection on sign-up, secure
   defaults everywhere. See `docs/06-security.md`.
10. **Badges are earned, never bought.** No code path lets an employer pay to change a badge.
11. **Cost-efficient by default:** job APIs once a night, never per user; AI only when the user
    asks, on the cheapest model that passes the evals; no state on servers so hosting can step
    up from one server to two plus a managed database. See `docs/15-cost-efficiency.md`.
12. **GDPR by design, enforced in code.** Every table, column, cache key and processor is
    declared in `backend/app/privacy/data_inventory.toml` with its purpose, lawful basis,
    retention and erasure rule *before* the code that uses it is written. No personal data
    without an entry; no retention of "indefinitely"; no processor that is not listed; no
    personal data in logs; contact details never sent to AI (`app.privacy.ai_guard`);
    consent-based features call `consent.require()` first. See `docs/13-privacy-and-compliance.md`.

### Extension rules (Track E; apply to everything under `extension/` and `packages/`)

These come from `docs/16-chrome-extension.md` §2 and never override rules 1 to 12.

- **E1** The local edition makes no network requests (CI network audit). **E2** No remote code.
- **E3** Nothing injected or read on LinkedIn, Indeed or Glassdoor. **E4** Read only on user action or
  declared career-site patterns; no background or bulk reading.
- **E5** Never submit anything for the user. **E6** Never autofill or store special category fields.
- **E7** Never invent experience; the no-invention guard lives in `packages/core`.
- **E8** Every score shows reasons, source and confidence, with a waiting state.
- **E9** One-click export and delete; optional encrypted backup. **E10** Minimum permissions, each
  justified; no `<all_urls>` at install.
- **E11** In-page hide or highlight only on Tier A sites the user enabled one by one; never on LinkedIn, Indeed or Glassdoor. Ids are ULIDs; the event log is the source of truth.
- `packages/core` imports nothing from `chrome`, `window` or `document` (lint-enforced).
- "Free for life": never move a shipped local feature behind a paywall.

---

## 3. How to work

### One stage at a time

- Check `docs/STATUS.md` for the current stage. Do not start a later stage early.
- For each stage, work through its task checklist in `docs/02-build-stages.md`.
- A stage is done only when every acceptance criterion passes and CI is green.
- When a stage is done: update `docs/STATUS.md`, tick the tasks, and summarise what changed.

### Git and GitHub

- `main` is protected. Never commit directly to it.
- Branch per task: `stage-<n>/<short-description>` (for example `stage-1/passkey-login`).
- Small, focused commits with clear messages (Conventional Commits: `feat:`, `fix:`, `docs:`,
  `test:`, `chore:`, `refactor:`).
- Open a pull request per task using `.github/pull_request_template.md`. CI must pass.
- Never commit secrets. `.env` is git-ignored; use `.env.example` for new variables.

### Commands

```bash
make setup        # first-time setup: copy .env, install pre-commit hooks
make up           # start the full stack with Docker Compose
make down         # stop it
make logs         # follow logs
make migrate      # run database migrations
make test         # backend + frontend tests
make lint         # ruff, mypy, eslint, prettier, typecheck
make fmt          # auto-format
make e2e          # Playwright end-to-end and accessibility tests
make privacy-check  # data inventory, models, retention/erasure/export plans, consent wording
make privacy-docs   # regenerate docs/privacy/records-of-processing.md from the inventory
```

Local URLs once `make up` is running:

| Service | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| Backend API docs | http://localhost:8000/api/docs (dev only) |
| Mailpit (dev email inbox) | http://localhost:8025 |
| MinIO console (dev file storage) | http://localhost:9001 |

### Code conventions

**Python (backend/)**
- Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, managed with `uv`.
- `ruff` for lint and format, `mypy --strict` for types, `pytest` for tests.
- Layers: `api/routes` (HTTP only) → `services` (business logic) → `repositories` (DB access).
  Keep routes thin. Business rules live in services and are unit-tested.
- Every scoring function returns its value **and** its reasons and confidence.
- Settings only via `app/core/config.py` (environment variables). No hard-coded secrets or URLs.

**TypeScript (frontend/)**
- React + TypeScript (strict) + Vite. React Router for routes, TanStack Query for server data,
  React Hook Form + Zod for forms.
- Styling: CSS Modules using the CSS variables in `src/styles/tokens.css` (generated from
  `design/tokens.json`). **No raw hex colours in components.**
- Accessible primitives: use Radix UI primitives for dialogs, tabs, menus, switches.
- Test with Vitest + Testing Library; end-to-end with Playwright + axe.

**General**
- Write tests with the code, not after. New business logic needs unit tests.
- Keep functions small and named for what they do. Prefer clarity over cleverness.
- Update the relevant doc when you change behaviour, an API or the data model.

### Definition of done (every task)

- [ ] Code, tests and docs updated
- [ ] `make lint` and `make test` pass locally; CI green
- [ ] New UI meets the design spec and passes the axe check
- [ ] No new secrets, no PII in logs
- [ ] Personal data touched? `data_inventory.toml` updated, `make privacy-docs` run,
      `make privacy-check` passes, PR privacy checklist completed
- [ ] Database changes have an Alembic migration
- [ ] Security checklist in `docs/06-security.md` considered for anything touching auth,
      uploads, external calls or personal data

### When to stop and ask the human

Stop and ask (do not guess) when:
- a task needs a decision listed in `docs/decisions-needed.md` that is still open;
- you need a paid account, API key or contract (job APIs, email provider, Stripe, hosting);
- a requirement conflicts with the non-negotiable rules above;
- a change adds an extension permission or host pattern, any network request in the local edition,
  a new site to read, or anything that transmits user data (needs owner approval and an update to
  `docs/13` §16 and the store listing text);
- a change would affect data already collected from users (migrations that drop data,
  changes to consent or retention).
- a change would alter a lawful basis, retention period, consent wording, processor,
  transfer outside the EEA, or would add special category data or profiling
  (these need owner and solicitor/DPO approval — see `docs/13-privacy-and-compliance.md` §14).

---

## 4. Design reference

- The visual design lives in a Claude design canvas (linked in `design/README.md`).
  It contains every screen with sample data. If you cannot open it, the written specs in
  `docs/07-design-system.md` and `docs/08-screens.md` are complete enough to build from.
- Look: calm, Apple-inspired. System font stack, one blue accent (#0066CC), generous white
  space, white cards on a light grey ground (#F5F5F7), pill buttons, colour-coded feature tints.
