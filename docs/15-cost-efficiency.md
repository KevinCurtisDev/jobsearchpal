# 15 · Cost efficiency

The platform is designed to run cheaply. Running costs should stay under ~5% of revenue
(excluding payment fees). These defaults apply unless an ADR changes them.

## Targets (monthly, excluding Stripe fees)

| Scale | Users | Target |
| --- | --- | --- |
| Private beta (Tier 0) | ≤ 300 invited | ~€50–100 |
| Early (Tier 1) | ~3,000 active free, ~150 paying | ~€100–180 |
| Established (Tier 1–2) | ~25,000 active free, ~1,500 paying | ~€500–900 |

## Rules

### 1. External APIs scale with sources, not users
- Job sources are fetched **once a night**, incrementally (only jobs posted or changed since
  the last run, sorted by date, stop at the first already-seen page).
- Every user is matched against our own database. No per-user calls to job APIs, ever.
- Each job description is parsed, embedded and flagged **once per canonical job** and shared
  by all users who see it.
- Public data (sponsor register, permits, ESCO, company registers) refreshes weekly or monthly,
  cached in Postgres. Company register lookups are cached for 30 days.
- Adzuna free tier (2,500 calls a month) is enough for Ireland at launch; budget a licence
  before UK expansion. Prefer free careers-board APIs (Greenhouse, Lever, Ashby, Workable).

### 2. The heavy lifting is traditional
Parsing, templates, PDF/Word export, the screening self-check, the writing checker, keyword
and skills matching, gap reports, story checks, scoring and delivery metrics all run without
generative AI (see `09-ml-and-analytics.md`).

### 3. Generative AI only on request, on the cheapest model that passes the evals
- AI runs only when the user clicks: "Suggest wording", "Draft cover letter",
  "Feedback on my answer". Never automatically on page load.
- **Default model: a Haiku-class Claude model** (`AI_MODEL_WRITING`). At the October 2026
  list price ($0.10 / $0.50 per million input/output tokens for Haiku 5.5) a tailoring
  suggestion costs about €0.002. Use a Sonnet-class model (`AI_MODEL_STRONG`) only for a
  feature whose evals fail on Haiku (likely candidate: interview feedback).
- **Batch API** (50% off) for anything not needed instantly, e.g. overnight cover letter
  drafts for saved jobs.
- **Prompt caching** for the fixed system prompts and rulebooks.
- **Result cache:** key = hash(prompt version, model, input). The same CV version + job never
  costs twice.
- Cover letters start from a template filled from the CV; AI only polishes on request.
- **Quotas:** free accounts get a small daily AI allowance; new accounts lower for 7 days;
  a global monthly budget cap (`AI_MONTHLY_BUDGET_EUR`) with alerts at 50/80/100%.
- **Free or self-hosted models:** not at launch. Free hosted tiers may use data for training
  (unacceptable for CVs) and self-hosting needs an always-on GPU that costs more than Haiku at
  our volumes. The model is a setting, so revisit if monthly AI spend passes ~€1,000.

### 4. Cheap, boring infrastructure
- Hosting tiers as in `12-deployment-and-ops.md`: one server for the private beta, two app
  servers + managed database from the public beta.
- Frontend on Cloudflare Pages (free).
- Email: **Amazon SES** (about $0.10 per 1,000) for sending and receiving. Free users get a
  weekly digest by default; daily for paid users.
- Object storage: Hetzner Object Storage or Cloudflare R2 (no egress fees).
- Embeddings and transcription run on our own CPU workers, overnight or queued.
- Monitoring: Sentry free tier or self-hosted GlitchTip; self-hosted Umami analytics;
  free uptime monitor.
- CI: GitHub Actions free minutes; cancel superseded runs (already configured).

### 5. Video practice stays in the browser
The video is recorded and played back **only in the user's browser**. Only the audio track is
uploaded for transcription and metrics, then deleted after processing unless the user keeps
the transcript. Cheaper, faster and more private.

### 6. Payments
Steer towards the 3-month search pass: Stripe's fixed per-payment fee makes one quarterly
payment cheaper than three monthly ones.

## Monitoring cost

`ai_usage` records every AI call with cost. A weekly cost report (Celery beat) lists spend by
service and by feature, and flags any feature whose cost per active user doubled week on week.

## Extension phase (Track E)

The local extension has no server and no per-user cost, so the extension phase needs no job-data
subscription and no beta server. Defer both until Connect or job matching needs them. The recurring
costs are the store registration (one-off), legal review, and founder time for adapter upkeep and
support. Re-estimate Tier 0 cost from the day Connect starts, not before.
