# ADR 0005 · Cost-efficient defaults

**Status:** Accepted · 2026-10-20

## Context
Early estimates with per-request AI on a large model and premium email came to ~€675 a month
early on and ~€5,800 at established scale. Most of that was avoidable.

## Decision
- Job APIs called once a night, incrementally; users matched against our own database.
- Shared, once-per-job processing of job descriptions.
- Generative AI only on user request, on a Haiku-class model by default, with batch, prompt
  caching, a result cache and quotas. No free or self-hosted LLM at launch.
- Amazon SES for email; weekly digests for free users.
- Practice video stays in the browser; only audio is uploaded.
- Details in `docs/15-cost-efficiency.md`.

## Consequences
- Estimated running costs fall to ~€50–100 a month early and ~€500–900 at established scale
  (plus Stripe fees).
- Haiku output quality must pass the AI evals before launch; features that fail use the
  stronger model.
- UK expansion needs a paid job-data licence or more free sources.
