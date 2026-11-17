# Build status

Claude Code keeps this file current. Update it at the end of every task.

**Current track:** Track E0 — Chrome extension decisions and spikes (extension is built first, 17 Nov 2026; awaiting owner approval of `docs/16-chrome-extension.md`). Platform Stage 0 scaffold exists; further platform work is paused except privacy foundations, until the launch plan is re-baselined (decision #27).
**Current stage (platform):** Stage 0 — Foundations
**Hosting tier:** none yet (Tier 0 beta box is a Stage 0 task and hosts the private beta; move to Tier 1 before the launch gate and before any payment)
**Launch strategy:** one public launch with the full product after Stage 10; private beta waves after Stages 3, 7 and 10 (see `02-build-stages.md`)

| Stage | Name | Status | Notes |
| --- | --- | --- | --- |
| E0 | Extension: decisions and spikes | 🟡 Proposed, awaiting approval | `docs/16` written; no code |
| E1 | Extension: tracker core | ⚪ Not started | Target mid-Dec 2026 to Mar 2027 (`docs/17` §9) |
| E2 | Extension: job intelligence and CV (public v1.0) | ⚪ Not started | Target Mar to May 2027; public v1.0 May to June 2027 |
| E3 | Extension: apply assist and prep | ⚪ Not started | Target Jun to Jul 2027 |
| E4 | Extension: Connect and optional editions | ⚪ Not started | From Aug 2027; needs Stage 1 and Stage C |
| C | Connect (platform side of import and sync) | ⚪ Not started | After Stage 1 |
| 0 | Foundations | 🟡 In progress | Scaffold provided: compose stack, API skeleton with health, security headers, rate limiting, email-code and bot-protection logic with tests; frontend shell with tokens |
| 1 | Accounts and security | ⚪ Not started | |
| 2 | CV builder | ⚪ Not started | |
| 3 | Tailor to a job | ⚪ Not started | |
| 4 | Marketing site and billing (switched on at the launch gate) | ⚪ Not started | |
| 5 | Job ingestion | ⚪ Not started | |
| 6 | Matching and daily digest | ⚪ Not started | |
| 7 | Assisted apply and tracker | ⚪ Not started | |
| 8 | Reply capture and honest rejection | ⚪ Not started | |
| 9 | Insights | ⚪ Not started | |
| 10 | Interview prep | ⚪ Not started | |
| — | **Launch gate: public launch with the full product** | ⚪ Not started | After Stage 10 and private beta wave 3 |
| 11 | Learned models | ⚪ Not started | Gated by data |
| 12 | Organisations | ⚪ Not started | |

## Already in the scaffold

- `backend/app/auth/email_codes.py` — code generation, HMAC hashing, verification, attempt limits (tested)
- `backend/app/auth/bot_protection.py` — honeypot, form timing, disposable domains, Turnstile verification (tested)
- `backend/app/core/rate_limit.py` — sliding-window limiter with Redis and in-memory backends (tested)
- `backend/app/core/security_headers.py` — security headers middleware (tested)
- `backend/app/api/routes/auth.py` — `/auth/email/start` and `/auth/email/verify` using an in-memory/Redis store (tested); sessions and passkeys are Stage 1 tasks
- `backend/app/privacy/` — data inventory (every planned table classified), validator, generated retention/erasure/export plans, consent rules, redaction for logs/Sentry/AI, legal deadline helpers, model checker, ROPA generator (tested; Stage 1 wires them to real models)
- `backend/app/linkedin/` — LinkedIn export parser, profile checklist, CV ↔ LinkedIn consistency and keyword-gap logic, minimised AI input (tested; routes and UI are Stage 3)
- `backend/app/workers/privacy_tasks.py` — nightly retention and erasure jobs (run once Stage 1 models exist)
- Frontend: tokens, AppShell, Button and Badge components, routes for every screen (placeholders), tests

## Log

| Date | Change |
| --- | --- |
| 2026-11-17 | JobPilot spec reviewed: `docs/17-jobpilot-spec-review.md` (F01 to F29 matrix, data model, dependency audit, risks, backlog, first slice); decisions #31 to #36; ADR 0008 amended; v1.0 target moved to May to June 2027. No code |
| 2026-11-17 | Extension-first strategy: `docs/16-chrome-extension.md`, ADR 0007 and 0008, Track E and Stage C in `02-build-stages.md`, rules E1 to E10 in `CLAUDE.md`, decisions #22 to #30, `extension/` and `packages/` placeholders. Platform docs 00, 01, 03, 04, 05, 06, 08, 09, 10, 13, 15 updated. No code |
| 2026-10-20 | Development package created |
| 2026-10-22 | "In a year" (hedonic adaptation) reflection in the self-check, Offers "In a year" view, referral status, four guides in `content/guides/` |
| 2026-10-22 | "Should I move?" free self-check: questions, browser-only scoring with tests, route, spec, stage task |
| 2026-10-21 | One full-product launch: stages regrouped into private beta waves + launch gate; waiting-on-data states (`app/insights/readiness.py`) |
| 2026-10-21 | Working name Hearback; How hiring works guide and tracker stage odds (`app/insights/stage_odds.py`, `content/hiring_stages.json`, docs 02/05/08/09) |
| 2026-10-21 | LinkedIn profile feature: export parser (in memory, profile files only), checklist, CV ↔ LinkedIn consistency, keyword gap, rewrite prompt; Stage 3 tasks, screens, API, inventory entries |
| 2026-10-20 | GDPR by design: data inventory as code (`backend/app/privacy/`), generated ROPA, retention/erasure/export plans, consent ledger rules, log/Sentry/AI redaction, privacy CI checks, LIAs, DPIAs, runbooks, consent wording (docs/13, ADR 0006) |
| 2026-10-20 | Added staged hosting (Tier 0 beta box → Tier 1 resilient lean), backup service, cost-efficiency defaults (docs/15, ADR 0004–0005) |
