# Decisions needed from the owners

Claude Code must stop and ask when a task depends on an open item here.

| # | Decision | Needed by | Default if no answer | Status |
| --- | --- | --- | --- | --- |
| 1 | Final product name and domain | Stage 1 (WebAuthn `rp_id` depends on the domain — changing it later invalidates passkeys) | — (blocking) | Open |
| 2 | Hosting providers for Tier 0 and Tier 1 (see 12-deployment-and-ops.md) | Stage 0 (Tier 0); Stage 4 (Tier 1) | Hetzner servers + load balancer + object storage; Scaleway managed PostgreSQL; Upstash Redis; Cloudflare Pages | Open |
| 3 | Email provider | Stage 1 | Amazon SES, à la carte pricing (Postmark if simpler inbound is preferred) | Open |
| 4 | Bot protection: Cloudflare Turnstile or self-hosted ALTCHA | Stage 1 | Turnstile | Open |
| 5 | Interview guarantee conditions | Stage 4 | e.g. ≥ 3 matched applications a week, all tracked | Open |
| 6 | Final prices and pay-what-you-can policy | Stage 4 | €0 / €19 / €45 | Open |
| 7 | Legal review: terms, privacy notice (outline in `docs/privacy/`), retention periods in the inventory, DPIAs, defamation process for scam reports and badges | Launch gate, Stage 8 (badges) | — (blocking for launch) | Open |
| 8 | Job API accounts and terms (Adzuna, Jooble, Careerjet) | Stage 5 | — | Open |
| 9 | Companies House API key; CRO data access route | Stage 5 | — | Open |
| 10 | Golden test set: 20–50 anonymised real CVs with consent | Stage 2 | Synthetic CVs only (weaker) | Open |
| 11 | AI provider budget (monthly cap) | Stage 2 | €200/month in beta | Open |
| 12 | Data science lead for Stages 8–11 | Stage 8 | Claude Code with owner review | Open |
| 13 | Minimum sample size and right-of-reply process for company badges | Stage 8 | n ≥ 15; email contact for employers | Open |
| 14 | Launch segment (all of Ireland vs migrants/graduates/career changers first) | Stage 4 | All of Ireland | Open |
| 15 | Legal entity (controller) name and address, Irish establishment | Stage 1 (privacy notice, ROPA) | — (blocking for launch) | Open |
| 16 | UK representative under UK GDPR Art 27 (if no UK establishment) and whether the ICO data protection fee applies | Launch gate | Appoint a UK representative service | Open |
| 17 | Data protection officer: appoint (internal or outsourced) or document why not required | Stage 4 | Appoint an outsourced DPO (large-scale profiling of job seekers) | Open |
| 18 | EU AI Act: confirm whether matching/scoring falls under Annex III (employment) and which obligations apply | Stage 6 | Legal review; keep scores advisory, explained and human-decided | Open |
| 19 | Sign the DPAs and transfer assessments listed in `data_inventory.toml` [[processors]] | Before each processor's first use | — (blocking per processor) | Open |
| 20 | Approve LIAs 0001–0004 and DPIAs 0001–0003 in `docs/privacy/` | Stage of each feature | — (feature flag stays off) | Open |
| 21 | Public launch date and beta wave sizes | After Stage 7 | Launch gate after Stage 10 + 4 weeks of wave 3; waves of 50 / 200 / 500 | Decided: full-product launch (21 Oct 2026); date open. **Partly superseded 17 Nov 2026:** the free extension launches publicly first (see #27) |
| 22 | Extension name and store title. Recommendation: Hearback brand, not "JobPilot" (crowded in the store, implies auto-apply). Needs trademark, CRO and domain checks | Before the store listing (E0 exit) | "Hearback: Job Application Tracker and CV Check" if the name clears | Open |
| 23 | Wording and boundary of "free for life": everything that runs on the device is free; pay only for server-cost features. Solicitor reads the public wording | Before listing and pricing copy | Wording in `docs/16` §1 | Open |
| 24 | Policy for LinkedIn, Indeed and Glassdoor: no content scripts, no UI injection, capture by URL, title and paste only (ADR 0008) | E0 | As ADR 0008 | Open (recommended: approve) |
| 25 | Open-source the extension and `packages/core` after v1.0 (trust and store review help; clone and brand risk) and under which licence | Before v1.0 | Decide after E1; do not publish before | Open |
| 26 | Chrome Web Store publisher identity: trader or non-trader status, public contact details, dedicated account and security keys | E0 (account), before listing (status) | Dedicated account now; status after company incorporation (#15) | Open |
| 27 | Platform re-baseline: pause platform Stages 2 to 7 and Tier 0 hosting while Track E runs; set new beta waves and launch date after E1 | End of E1 | Keep 13 Sep 2027 as an internal target only; make no public date claim | Open |
| 28 | Platform free tier boundary: is a free Connect account (import, sync) free forever, with paid features limited to server-cost items (job feed, reply capture, AI, practice)? | Before E4 | Yes, as in `docs/00` business model | Open |
| 29 | Browsers: Chrome first; Edge after E2; Firefox and Safari later (Safari needs Apple developer fee and Xcode) | E2 | Chrome, then Edge | Open |
| 30 | Benchmark contribution route and consent: website upload only, never a background upload from the extension; solicitor and Limited Use review | Before E4 | Website upload only | Open |
| 31 | Local data at rest: encrypted backups at launch and at-rest encryption not promised (recommended), or encrypted records at launch | Before E1 exit | Encrypted export only (`docs/17` §7) | Open |
| 32 | Store optional document blobs (CVs, letters) in the extension, and ask for optional `unlimitedStorage` if the spike S10 passes | E2 | Extracted text only until S10 passes | Open |
| 33 | Minimum Chrome version | E0 | 120 (side panel open at 116, alarm behaviour at 120; `docs/17` §2) | Open |
| 34 | Monetisation of the extension: free for life (recommended, decision #23) or any one-time purchase. A payment or licence check adds an external service | Before listing | Free for life | Open |
| 35 | Scope of in-page hide and highlight (F05, F12): Tier A employer ATS pages only, per-site opt-in; Irish boards only after a terms check; never LinkedIn, Indeed or Glassdoor | E2 | Tier A only | Open (recommended: approve) |
| 36 | ID scheme: ULID (recommended, sortable, matches platform import) or UUIDv7 | E0 | ULID | Open |
