# ADR 0006 · GDPR by design, enforced by a machine-readable data inventory

**Status:** Accepted · 2026-10-20

## Context
The owners require personal data to be handled "correctly, without any ambiguity" from the
first line of code. Privacy rules kept only in documents drift from the code: a new column
is added without a retention period, a table is forgotten by the delete job, a log line
leaks an email, a CV is sent to an AI provider with its contact block.

## Decision
- One source of truth: `backend/app/privacy/data_inventory.toml` declares every table,
  column override, cache key and processor with purpose, lawful basis, retention, erasure
  and export behaviour.
- A strict validator (`registry.py`) rejects ambiguous or unlawful entries (no basis, no
  LIA for legitimate interests, no explicit consent for special category data, no
  "indefinite" retention, non-EEA processors without a transfer mechanism, minimum age < 16).
- Retention, erasure and export plans are **generated** from the inventory, so new tables
  are covered automatically; CI checks the SQLAlchemy models (FK `ON DELETE`, encryption,
  classification) and `04-data-model.md` against it.
- The Record of Processing Activities is generated from it and must be current in CI.
- Redaction is applied centrally to logs, Sentry events and AI input.
- Consent wording is versioned and hash-locked; only a grant of the current version counts.

## Consequences
- Adding personal data takes one more step (an inventory entry) — deliberately.
- Legal choices (lawful bases, retention periods) are visible in one reviewable file that
  a solicitor/DPO can sign off, and every change shows up in a pull request diff.
- The inventory is engineering's interpretation, not legal advice; it needs owner and
  legal review (decisions #7, #15–#20).
