# ADR 0007 · Chrome extension first, built on a local-first shared core

**Status:** Proposed · 2026-11-17 (needs owner approval; see `docs/16-chrome-extension.md` §15)

## Context
The platform plan needs job data, servers and many users before it is useful, and its marketing
plan depends on sign-ups that are slow to win. A browser extension can be useful on day one with
no servers, no job data and no per-user cost, and it can be a free, trusted front door.
The owner wants to build the extension first, free for life, with no AI, backend, accounts or
cloud, and to keep all user data on the user's device.

## Decision
- Build the extension first (Track E in `docs/02-build-stages.md`) as the first public product.
- Put all deterministic logic in `packages/core` (pure TypeScript, no browser APIs) behind ports
  (`Storage`, `Notifier`, `DataPackProvider`, `TextGenerator`, `Sync`, `Telemetry`). The free
  edition plugs in local adapters. Connect and AI editions plug in others later, so nothing is
  rewritten.
- The local edition makes no network requests. This is enforced by a CI "network audit".
- Application state is an append-only event log (ULIDs) that mirrors the platform's
  `application_event`, so import and later sync are lossless and idempotent.
- The platform reuses `packages/core` and `packages/ui` in the browser (free tools, CV parsing,
  export preview). The Python backend re-implements only what must run on a server and is checked
  against the same golden fixtures.
- "Free for life" means: everything that runs on the user's device is free; users pay only for
  server-cost features (job feed, email capture, AI, practice transcripts).

## Consequences
- Platform Stages 5 to 7 (job data, matching, assisted apply) and the Tier 0 server can wait
  until Connect needs them; saves cost and time during the extension phase.
- CV parsing moves to the browser first; the server holds a CV only for AI requests (privacy win).
- Founder capacity is the main risk; the 13 September 2027 platform launch date must be
  re-baselined after Phase E1.
- Adapter maintenance (job sites change) is a permanent cost of "free forever".
