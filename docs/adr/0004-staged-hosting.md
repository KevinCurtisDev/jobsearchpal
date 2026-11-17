# ADR 0004 · Staged hosting: one server for the private beta, then resilient lean

**Status:** Accepted · 2026-10-20

## Context
A single server is the cheapest way to run the private beta, but it is a single point of
failure. Once real users depend on the platform and payments start, an outage or lost data
would be costly and damage trust.

## Decision
- **Tier 0 (private beta, ≤ ~300 invited users, no payments):** one EU server running the full
  Docker Compose stack, with nightly off-site backups, weekly restore tests and uptime alerts.
- **Tier 1 (public beta onwards, before any payment):** two app servers behind a load
  balancer, managed PostgreSQL with a standby and point-in-time recovery, managed Redis,
  frontend on Cloudflare Pages.
- **Tier 2 (growth):** scale the database and app servers; separate worker pool.
- Triggers and the migration runbook are in `docs/12-deployment-and-ops.md`.
- From day one: no state on servers, config only via environment variables, scripted setup.

## Consequences
- Beta costs about €30–50 a month; Tier 1 about €80–130.
- The move to Tier 1 is a planned, rehearsed 30-minute maintenance window, not a rebuild.
- Beta users accept that short outages are possible.
