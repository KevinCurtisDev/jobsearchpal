# ADR 0008 · What the extension may read, and where it may talk to the network

**Status:** Proposed · 2026-11-17

## Context
Platform rule 3 says "no LinkedIn scraping" and `docs/10` said "never use a browser extension to
read pages". An extension that tracks applications has to read the job page the user is on.
LinkedIn's help page "Prohibited software and extensions" states that it does not permit browser
extensions that scrape, modify the appearance of, or automate activity on its services. Indeed
and Glassdoor terms are assumed to be similar until read (solicitor check).

## Decision
1. **Tier A sites** (public employer ATS and career pages): the extension may read the job posting
   the user is viewing, on a user action or on a declared career-site pattern. Never in the
   background across tabs, never in bulk, never automating actions, never submitting forms.
2. **Tier C sites** (LinkedIn, Indeed, Glassdoor): no content scripts, no DOM reading, no injected
   UI. Capture uses only the tab URL and title provided by the browser on a toolbar click, plus
   what the user types or pastes. LinkedIn features stay export-or-paste on Hearback's own pages.
3. **Network:** the local edition makes no requests. Any network feature ships in the Connect
   edition behind an `optional_host_permissions` prompt for the Hearback API only, after a
   Limited Use and privacy review. Data contribution to benchmarks is a user action on the
   Hearback website, not a background upload from the extension.
4. Rule 3 in `CLAUDE.md` and the LinkedIn paragraph in `docs/10` are updated to match.

## Consequences
- Marketing must say "track LinkedIn and Indeed jobs by saving the link", never "works on LinkedIn".
- Easy Apply applications are logged by hand.
- Some ATS sites may need a per-site terms check; record results in `docs/10`.

## Amendment, 17 November 2026 (JobPilot spec review)
- **Hiding, highlighting and badges on listing pages** change how a page looks. They are allowed
  only on Tier A sites that the user enables one origin at a time through an optional host
  permission, and only on explicit user rules. They are never added to LinkedIn, Indeed or
  Glassdoor (LinkedIn's help page on prohibited software and Indeed's Terms are the basis; the
  solicitor reads the clauses). A reveal-all toggle must always work, and unsupported pages
  fail safely by changing nothing.
- "Viewed" means observed by this extension on this device. No global posting history is claimed.
- Content scripts receive only per-listing flags and the rules for their own origin, never records.
- Whether `scripting.registerContentScripts` after a runtime grant behaves as needed is unverified (spike S11).
