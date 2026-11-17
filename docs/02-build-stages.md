# 02 · Build stages

Build in this order. Each stage ships something usable, ends with green CI, and updates
`docs/STATUS.md`. Do not start a stage until the previous one meets its acceptance criteria.

## Launch strategy: one public launch, with the full product

The owners have decided (21 October 2026) to launch publicly **once, with the full product**:
Stages 0–10 are complete before anyone outside the private beta can sign up. Features that
need Hearback's own data ship on day one in an honest **waiting-on-data** state (below),
not hidden and not faked.

| Period | Stages | Who can use it |
| --- | --- | --- |
| Build + private beta wave 1 | 0–3 (accounts, CV builder, tailoring, LinkedIn) | Owners, then 20–50 invited testers |
| Private beta wave 2 | 4–7 (marketing site and billing built but not public; jobs, matching, assisted apply, tracker with stage odds) | Wave 1 + up to 200 testers |
| Private beta wave 3 | 8–10 (reply capture, honest rejection, insights, interview prep) | Up to 500 testers |
| **Launch gate** (after Stage 10) | Public launch checklist below | Everyone |
| After launch | 11 (learned models, switched on as data gates are met), 12 (organisations; pilots can start during beta) | Everyone |

Rules for the beta: invitation only (sign-up gated by an invite code), free, beta terms and
privacy notice accepted, a feedback button on every screen. Testers who opt in to
benchmarks start filling the data that the waiting-on-data features need, so the beta is
also how those features warm up. **No payment is taken before the launch gate, and the platform is not marketed publicly before it.**
**Exception (17 November 2026): the free Chrome extension (Track E) is launched and marketed publicly
from its v1.0 (target May to June 2027), ahead of the platform. It takes no payment and sends
no data. This partly supersedes the 21 October 2026 "one public launch" decision (decisions #21, #27).**

### Waiting-on-data features

Each shows exactly what it is waiting for and how close it is (`app/insights/readiness.py`).
Thresholds match `09-ml-and-analytics.md` §Data maturity gates.

| Feature | At launch it shows | Fully live when |
| --- | --- | --- |
| Company reply-rate badges | "Collecting replies for this company: 6 of 15 tracked applications" | ≥ 15 tracked applications for that company |
| Where you stand vs similar candidates | Published averages, labelled "public data" | ≥ 200 users in the cohort |
| What works for you (personal effects) | "Unlocks after 20 tracked outcomes: you have 14" | 20 outcomes for that user |
| CV A/B tester verdict | Test runs from day one; "too early to call" with progress to a confident result | Planned sample size reached |
| Stage odds in the tracker | Published averages, low confidence | Hearback cohort ≥ 200 tracked applications at that stage |
| Learned ranking, scam classifier, reply classifier | Rules-based versions (fully working) | Gates in `09-ml-and-analytics.md` |

Legend: 🔑 needs a key, account or decision from the owners (see `decisions-needed.md`).

---

## Track E: Chrome extension (built first, from 17 November 2026)

**Status: proposal. Nothing beyond E0 starts until the owners approve `docs/16-chrome-extension.md` and
answer decisions #22, #23, #24 and #27.** Full design, feasibility and spikes: `docs/16`. Rules: `CLAUDE.md` E1 to E10.

The extension is free for life, local only (no AI, no backend, no accounts, no network in the local
edition) and is the front door to the platform. It is built from `extension/` and `packages/`.

| Phase | Target window | Goal | Who can use it |
| --- | --- | --- | --- |
| E0 Decisions and spikes | Nov to mid-Dec 2026 | Approvals, name clearance, store account, spikes S1 to S12 (S10 optional unlimitedStorage, S11 dynamic content scripts after a runtime host grant, S12 Playwright with a loaded extension) | Owners |
| E1 Tracker core | Mid-Dec 2026 to Mar 2027 (about 10 to 13 weeks, `docs/17` §9) | Capture, board, reminders, export and import, stage odds, backup | 10 to 20 trusted testers (unlisted listing); these become platform beta wave 1 candidates |
| E2 Job intelligence and CV | Mar to May 2027 | JD parser, keyword match, sponsor badge, suspicious-listing signals, CV import and check, LinkedIn check, personal insights | Alpha testers, then **public v1.0 (target May to June 2027)** |
| E3 Apply assist and prep | Jun to Jul 2027 | Autofill (fill, never submit), Workday, more adapters, interview prep, offer tools | Public |
| E4 Connect and optional editions | From Aug 2027 | Pairing, import and sync into the platform, data refresh packs, opt-in contributions, then AI edition | Public, opt-in |

Dates are targets for approval, not commitments. Re-baseline after each phase.

### E0: Decisions and spikes

Tasks
- [ ] Owners approve `docs/16`; answer decisions #22, #23, #24, #27 (and #25, #26, #28 to #30 before E1 exit)
- [ ] Brand clearance for the store name (trademark, CRO, domain); toolbar icons 16/32/48/128 from the reply-bubble mark
- [ ] Chrome Web Store developer account on a dedicated Google account with hardware keys 🔑
- [ ] Spikes S1 to S9 (docs/16 §13) with a written result each; update the feature list and §9 site tiers
- [ ] Collect golden sets: 30 labelled job descriptions, 20 to 50 real CVs with consent (decision #10), 100 labelled suspicious or ghost listings
- [ ] Design the extension surfaces in the design canvas (docs/08 "Extension surfaces")

Acceptance criteria
- Every spike has a recorded pass or fail; failed items are moved to a later phase or dropped in writing

### E1: Tracker core

Read before starting: `docs/16` §4 (A, B1, B6, F), §6, §7, and `docs/17` (overrides: stack, data model, permissions, backlog, first slice).

Tasks
- [ ] First vertical slice from `docs/17` §10 (needs owner approval before any code)
- [ ] Zod-validated message contracts (`CAPTURE_JOB`, `SAVE_JOB`, `QUERY_LISTING_STATUS`, `GET_FILTER_RULES`, `FILL_APPROVED_FIELDS`); no message returns a whole record; test: projections rebuild from events
- [ ] Monorepo setup: `packages/core`, `packages/storage`, `packages/adapters`, `packages/ui`, `extension/`; lint rule that `core` imports no browser APIs
- [ ] CI network audit, permission diff, offline Playwright run, reproducible build, bundle budgets (docs/16 §6.3)
- [ ] Dexie schema v1, event log, reducers, migrations with automatic pre-upgrade snapshot, fixtures per version
- [ ] Capture: JSON-LD adapter, Greenhouse, Lever, Ashby, Workable adapters with saved HTML fixtures; manual add; paste description
- [ ] Tier C handling: toolbar click uses tab URL and title only; no content scripts on LinkedIn, Indeed, Glassdoor (test asserts manifest matches)
- [ ] Board and list, event timeline, duplicate and repost detection, "Did you apply?" prompt on confirmation pages (always confirm)
- [ ] Reminders via alarms, notifications and badge; catch-up at browser start
- [ ] Export JSON and CSV, import JSON, spreadsheet CSV import wizard, passphrase-encrypted backup, 30-day backup reminder
- [ ] Stage odds from `content/hiring_stages.json`; "Should I move?" reused from `frontend/src/features/self-check`
- [ ] "What is stored" screen, delete everything, first-run screens; accessibility (axe, keyboard, 320 px side panel)

Acceptance criteria
- Network audit passes; every feature works offline; manifest has no `<all_urls>` and no host patterns outside the Tier A list
- 7 days of daily alpha use with no data loss; upgrade from schema v1 to a test v2 preserves all events
- Export then import into a fresh profile reproduces identical applications; encrypted backup round-trips
- Golden fixtures: each adapter extracts company, title, location, posted date on its saved pages

### E2: Job intelligence and CV

Read before starting: `docs/16` §4 (B2 to B5, C, D), `docs/09-ml-and-analytics.md`, `content/`.

Tasks
- [ ] Job description parser (requirements, must vs nice, seniority, salary, right-to-work phrases); keyword match with evidence lines
- [ ] Skills dictionary (pruned ESCO with attribution plus curated terms) and sponsor-register data pack with "last updated" and match confidence
- [ ] Suspicious-listing and stale-listing signals (signals, never a verdict); solicitor reads the wording
- [ ] CV import (pdf.js in an offscreen document, DOCX via fflate), correction screen, CV versions, CV check using `content/cv_conventions.json`, CV export to PDF and DOCX
- [ ] LinkedIn check on the extension's own pages (paste, and data-export ZIP parsed in the browser); never on linkedin.com
- [ ] Reply curves (Kaplan-Meier), personal what-works with shrinkage and waiting state, CV A/B tagging, weekly review, `.ics` export, scheduled backup to a folder (if S9 passes)
- [ ] Store listing, privacy policy, permission justifications, screenshots; submit with at least four weeks before the target public date

Acceptance criteria
- Job description requirement extraction F1 ≥ 0.85 on the 30 labelled descriptions; no output shows a score without reasons, source and confidence
- CV check agrees with a human reviewer on at least 85% of checks over 20 real CVs
- Scanned (image-only) PDFs produce a clear "can't read this file" message, never wrong data
- Public v1.0 only after four weeks of alpha with no data-loss bug and the listing approved

### E3: Apply assist and prep

Tasks
- [ ] Autofill: fill visible fields after a click, never submit, never touch special category fields; per-ATS fixtures; Workday adapter (spike S4) and file attach (spike S7)
- [ ] More adapters (SmartRecruiters, Teamtailor, Personio, Recruitee, BambooHR, Irish and UK sites after terms check)
- [ ] Cover-letter templates with merge fields; interview prep content; offer comparison and tax data pack (updated each April)

Acceptance criteria
- Autofill is correct on each supported ATS fixture, never presses submit, and leaves diversity and health questions blank

### E4: Connect and optional editions

Depends on platform Stage 1 (accounts) and Stage C. Read `docs/16` §6.2, `docs/13` §16.

Tasks
- [ ] Solicitor sign-off on import consent, benchmark consent and the Limited Use position 🔑
- [ ] Connect edition: `optional_host_permissions` prompt, pairing, idempotent event upload, revoke; store listing and privacy policy updated before release
- [ ] Data refresh packs and adapter selector updates delivered as signed data (never code)
- [ ] AI edition behind `TextGenerator`: platform-hosted first (prompts and schemas in `prompts/`), optional bring-your-own-key later; no-invention guard in `packages/core`; contact details never sent

Acceptance criteria
- Local-edition users are not disabled by the upgrade; idempotency test imports the same export twice and creates no duplicates; consent recorded before any contribution

---

## Stage 0 — Foundations

> **Track E change (17 Nov 2026):** the Tier 0 beta box, job-data and most platform infrastructure wait until Stage C or Connect needs them (docs/15). Keep the scaffold, CI and privacy foundations; do not pay for hosting yet.

**Goal:** a running, tested, deployable skeleton that every later stage builds on.

Read before starting: `01-architecture.md`, `03-tech-stack.md`, `07-design-system.md`, `12-deployment-and-ops.md`.

Tasks
- [ ] Initialise git, push to a private GitHub repo, protect `main` (PR + passing CI required)
- [ ] Confirm `make up` starts every service; `make test` and `make lint` pass
- [ ] Upgrade dependencies to current stable versions; commit `uv.lock` and `package-lock.json`
- [ ] Generate `frontend/src/styles/tokens.css` from `design/tokens.json` with a script (`npm run tokens`)
- [ ] Build the design-system components listed in `07-design-system.md` §Components, each with a test and an axe check
- [ ] Build `MarketingLayout` and `AppShell` (side nav, header, skip link, sample-data chip in dev)
- [ ] Alembic set up with an empty initial migration; `make migrate` works
- [ ] Structured logging with request IDs; `/api/v1/health` and `/api/v1/ready` (DB + Redis checks)
- [ ] Sentry wired for API, worker and frontend (DSN optional in dev) 🔑
- [ ] OpenAPI → TypeScript client generation (`npm run api:generate`)
- [ ] CI: lint, typecheck, unit tests, build images, CodeQL, dependency audit, secret scan, Trivy
- [ ] Staging environment deploys automatically from `main` 🔑 (hosting choice)
- [ ] **Tier 0 beta box** (`infra/docker-compose.beta.yml`): one EU server, Terraform + cloud-init setup, nightly off-site backup service, uptime alert on `/api/v1/ready` 🔑
- [ ] Frontend deploys to Cloudflare Pages from `main`
- [ ] Weekly automated restore test of the latest backup into a throwaway container
- [ ] Enforce the "no state on servers" rules in `12-deployment-and-ops.md` (files in object storage, sessions in Redis/Postgres)
- [ ] **Privacy foundations** (scaffold provided in `backend/app/privacy/`): `make privacy-check` runs in CI; log redaction and Sentry scrubbing on for API and worker; Sentry EU region; generated `docs/privacy/records-of-processing.md` committed
- [ ] Sign DPAs for Hetzner, backup storage and Sentry before they receive any data (decision #19) 🔑

Acceptance criteria
- Fresh clone → `make setup && make up && make migrate` → app shell loads at `localhost:5173`
- CI green on a pull request; a deliberately leaked fake secret is blocked by the secret scan
- Every component in the component list renders, passes axe, and matches the token values
- A log line containing an email, phone number or IP is redacted (test); `make privacy-check` passes in CI

---

## Stage 1 — Accounts and security

> **Track E change (17 Nov 2026):** add extension pairing to the design now (device tokens, docs/05 Connect) but build it in Stage C.

**Goal:** passwordless, bot-resistant sign-up and sign-in, sessions, and privacy controls.

Read before starting: `06-security.md` (all), `04-data-model.md` §Accounts, `08-screens.md` §Sign in, §Privacy and settings, `13-privacy-and-compliance.md`.

Tasks
- [ ] Models + migrations: `users`, `passkey_credentials`, `sessions`, `consents`, `audit_log`, `feature_flags`
- [ ] Email one-time code: request, verify, resend limits, uniform responses (no account enumeration)
- [ ] Magic link in the same email (single use, same expiry as the code)
- [ ] Passkeys (WebAuthn): register, authenticate, conditional UI (autofill), list, rename, remove
- [ ] Sign-up flow: email → code → offer to add a passkey; terms consent recorded with version and timestamp
- [ ] Bot protection: Turnstile verification 🔑, honeypot field, minimum form time, rate limits (IP, email, ASN), disposable-domain blocklist, MX check
- [ ] Sessions: opaque tokens, `__Host-` cookie, idle and absolute expiry, rotation on sign-in, device list, sign out one / all
- [ ] Step-up confirmation (fresh passkey or code within 10 minutes) for: delete data, add/remove passkey, change email
- [ ] New-device sign-in alert email
- [ ] Transactional email templates (code, alert, welcome) via provider 🔑; Mailpit in dev
- [ ] Privacy and settings screen: consent switches (benchmarks, experiments, fairness audit data, digest email), export my data (async ZIP), delete my account (step-up, 30-day hard delete job)
- [ ] Security headers and CSP verified in staging; CSRF protection on all state-changing requests
- [ ] AI-usage quotas per account (prevents automated abuse of paid AI calls)
- [ ] **GDPR by design (Stage 1 is where it becomes real):**
  - [ ] Models + migrations for `data_subject_requests`, `erasure_tombstones`, `privacy_incidents`; `consents` append-only trigger; `subject_ref`/`pseudonymised_at` columns; `EncryptedText` column type (sets `info["encrypted"]`)
  - [ ] Every model passes `model_check` (FK `ON DELETE` matches the inventory)
  - [ ] Sign-up records acknowledgements: terms, privacy-notice version, "I am 16 or older" (no date of birth)
  - [ ] Consent switches built from `consent.py` + `content/consents/` (default off, wording shown verbatim, `wording_sha256` stored, withdrawal one tap)
  - [ ] Export: async ZIP from `export_plan()` with a README explaining each file, purposes, recipients and retention; 24 h single-use link
  - [ ] Erasure: step-up → lock + revoke sessions → `process_erasures` runs the generated plan → confirmation email → tombstone
  - [ ] `enforce_retention` nightly job live; `dsar_deadline_check` daily job; `reapply_tombstones` command and its use in `restore-test`
  - [ ] Rights-request register screen for owners (admin, hardware-key sign-in)
  - [ ] Breach runbook tabletop dry-run scheduled (before the public beta)

Acceptance criteria
- Can sign up and sign in with email code alone, then with a passkey only, on Chrome, Safari, Firefox and a phone
- Unknown and known emails get identical responses and timing on `/auth/email/start`
- 6th wrong code locks that code; 4th code request within 15 minutes is refused with a clear message
- Submissions with the honeypot filled, a failed Turnstile token, or a disposable domain are rejected and logged
- Delete account requires step-up and removes all personal data within 30 days (test with a fixture user)
- Integration test: a fixture user with data in every Stage 1 table is erased; afterwards no row references them, legal-hold rows hold only `subject_ref`, and a restore + `reapply_tombstones` erases them again
- Export ZIP contains every table in `export_plan()` for the fixture user and nothing about any other user
- Withdrawing a consent stops the dependent processing on the next request (test)
- OWASP ZAP baseline scan in CI shows no high or medium findings on auth endpoints
- Sign-in and settings screens pass axe and keyboard-only testing

---

## Stage C: Connect (extension import and sync)

**Goal:** a user can bring their extension history into a Hearback account, keep it in sync, and opt in to benchmarks. Needs Stage 1 (accounts). Design: `docs/16` §6.2 and §14; API: `docs/05` Connect; privacy: `docs/13` §16.

Tasks
- [ ] Add new tables (devices, pairing, import batches) to `docs/04-data-model.md` **and** `data_inventory.toml` first; `make privacy-docs`; privacy gate
- [ ] Event import: ULID idempotency, `source = extension`, client timestamps, schema version, validation with the shared schema
- [ ] `/import-preview` (no account, browser-only insights, nothing stored) and `/app/connect` (pairing, devices, revoke, delete imported data)
- [ ] Benchmark consent captured on the website at import; contributions anonymised at source (free text and personal fields dropped)
- [ ] Include imported data in export and erasure plans

Acceptance criteria
- Importing the same export twice creates no duplicates; revoking a device stops uploads; erasure removes imported events and derived rows (fixture user)
- Privacy gate: `make privacy-check` passes; DPIA for benchmark contribution drafted; solicitor sign-off before any contribution is enabled

---

## Stage 2 — CV builder

> **Track E change (17 Nov 2026):** CV parsing, CV check and keyword checks run in the browser through `packages/core` and pdf.js first (same code as the extension). The server stores a CV only when the user asks for AI writing. Reduce backend parsing to the AI fallback and server-side rendering needs.

**Goal:** build or upload a CV, edit it as structured data, export ATS-safe PDF and Word.

Read before starting: `04-data-model.md` §CV, `08-screens.md` §CV builder, `14-content-guidelines.md`, `prompts/README.md`, `content/banned_phrases.json`, `content/cv_conventions.json`.

Tasks
- [ ] `cv.schema.json` (structured CV: contact, summary, roles with bullets, skills, education, extras) and Pydantic models
- [ ] Models: `cv_documents`, `cv_versions` (JSONB validated against schema), `uploaded_files`
- [ ] Upload: size limit (5 MB), magic-byte type check (PDF, DOCX only), virus scan hook, private S3 storage
- [ ] Parser: text extraction (pdfplumber, python-docx) in a sandboxed subprocess with timeout; rules-based section and contact parser; AI fallback for unparsed sections only, via `prompts/cv_parse.md`
- [ ] Editor UI: sections as forms, add/reorder achievements, skills chips, versions dropdown
- [ ] Country conventions (IE, UK, EU, US) from `content/cv_conventions.json`: length, photo, date of birth, spelling
- [ ] Templates: Classic, Modern, Compact — single column, standard headings — Jinja2 → HTML → PDF (WeasyPrint); DOCX (python-docx)
- [ ] ATS self-check: re-extract text from generated PDF and DOCX; verify headings, order, contact details, dates
- [ ] Writing checker (rules): banned phrases, missing numbers in achievements, tense consistency, bullet length, first-person pronouns, page length vs convention
- [ ] AI rewrite ("Improve wording") via `prompts/cv_rewrite.md` with the **no-invention guard** (see prompts/README.md); on request only, Haiku-class model by default, result cache, quotas (see 15-cost-efficiency.md)
- [ ] Age-neutral option (hide graduation dates)
- [ ] Golden test set: 20–50 anonymised CVs in `backend/tests/fixtures/cvs/` 🔑 with expected parse output

Acceptance criteria
- Privacy gate: CV uploads and AI parsing go through `ai_guard`; referee contact details trigger a warning; uploaded originals deleted on erasure (storage keys in the plan)
- Parsing accuracy on the golden set: ≥ 95% of contact fields and ≥ 90% of roles correct
- Every exported file passes the self-check; text order in the PDF matches the on-screen order
- The no-invention guard rejects any AI output that adds a skill, employer, date or number not in the input (unit tests with adversarial fixtures)
- Banned phrases list is enforced; each suggestion can be accepted or dismissed
- Editor is fully usable by keyboard and screen reader

---

## Stage 3 — Tailor to a job

> **Track E change (17 Nov 2026):** matched and missing requirements, the gap report and the free LinkedIn check use `packages/core` (shared with the extension); the server adds AI suggested edits only.

**Goal:** paste a job description, see matched and missing requirements, accept tailored edits.

Read before starting: `09-ml-and-analytics.md` §Tailoring, `08-screens.md` §Tailor, `prompts/tailor_suggestions.md`.

Tasks
- [ ] Job description parser: requirements, required vs nice to have, seniority, salary (rules + light AI fallback)
- [ ] Load the ESCO skills taxonomy (occupations, skills, synonyms) into Postgres; skill normaliser
- [ ] Matching: BM25 + ESCO synonym matching → matched / missing list with evidence (which CV line matched)
- [ ] Gap report: "I have this" (user adds evidence) vs "mark as a gap" (stays private, links to free courses)
- [ ] Suggested edits as diffs (before/after/why), accept, edit or reject each; the no-invention guard applies
- [ ] Save as a new CV version linked to the job; log `tailored` event
- [ ] Optional job URL fetch: allowlisted domains only, SSRF protections (see security doc)
- [ ] **LinkedIn profile** (`/app/linkedin`; scaffold in `backend/app/linkedin/`, rules in `content/linkedin_rules.json`):
  - [ ] Import: LinkedIn data export ZIP (in-memory, profile files only, never stored), profile PDF ("Save to PDF"), or paste per section. Show the user exactly which files we read and which we ignored
  - [ ] Models + migrations: `linkedin_profiles`, `linkedin_suggestions` (inventory entries exist)
  - [ ] Profile checklist (`profile_checks`) + manual checklist items with "Done" ticks
  - [ ] CV ↔ LinkedIn consistency (`consistency_checks`) against the chosen CV version
  - [ ] Rewrite on request: `prompts/linkedin_rewrite.md` with the no-invention guard, banned phrases (general + LinkedIn list), character limits enforced after generation; two headline options, About, up to 4 roles; each with Copy button and live character count; "ask" items become questions
  - [ ] Keyword gap panel shows "Available after job data is live" until Stage 5 (see Stage 5 task)
  - [ ] Tracker source option "LinkedIn — recruiter approached me" (Stage 7) so the effect can be measured honestly
  - [ ] Delete my LinkedIn copy (one tap) and inclusion in export/erasure

Acceptance criteria
- LinkedIn: the parser never opens files outside the allow-list (test with an export that contains messages and connections); birth date, address and phone never reach the database; nothing is uploaded to storage
- LinkedIn: rewrite output never exceeds the limits in `linkedin_rules.json`, never introduces an employer, title, date, number or skill absent from the inputs (adversarial fixtures), and contains no banned phrase
- LinkedIn screen passes axe and keyboard-only testing; every Copy button announces "Copied" to screen readers
- Privacy gate: tailoring and cover letters send CV text only through `ai_guard`; AI provider DPA signed (decision #19); `ai_usage` stores no prompt text
- On 30 labelled job descriptions, requirement extraction F1 ≥ 0.85
- No suggestion introduces a skill the user hasn't confirmed
- Saved version appears in the CV builder and in the A/B tester list later

---

## Stage 4 — Marketing site and billing (built now, switched on at the launch gate)

> **Track E change (17 Nov 2026):** the landing page's primary call to action becomes "Add to Chrome, free for life"; the waitlist stays for the platform. The free-for-life boundary (docs/16 §1) must appear in pricing copy. Entitlements must not lock anything the local extension already does.

**Goal:** landing page, guides, pricing and payments built and tested in the private beta. The
site stays behind the beta invite gate and Stripe stays in test mode until the launch gate.

Read before starting: `08-screens.md` §Marketing site, `13-privacy-and-compliance.md`, `12-deployment-and-ops.md` §Launch checklist.

Tasks
- [ ] Landing page exactly per design (hero, product preview, official data sources, problem stats with sources, feature tiles, how it works, promises, pricing, organisations, closing CTA, footer)
- [ ] Pricing via Stripe Checkout + Customer Portal 🔑; Stripe Tax for VAT; plans: Free, Monthly, Search pass
- [ ] Entitlements service (what each plan unlocks) — checked server-side on every gated endpoint
- [ ] Pay-what-you-can flow (self-declared, no proof required) 🔑 policy
- [ ] Interview guarantee: track eligibility conditions and auto-extend the pass 🔑 conditions
- [ ] Legal pages: terms, privacy policy, cookie notice (cookieless analytics), accessibility statement 🔑 legal review
- [ ] Privacy-friendly analytics (Plausible or self-hosted Umami)
- [ ] Free "CV check" entry point (upload → screening check → sign-up prompt)
- [ ] Beta invite gate: invite codes, waitlist sign-up on the public holding page (email only, consent recorded), beta terms
- [ ] **Move to Tier 1 before the launch gate and before any payment:** rehearse the Tier 0 → Tier 1 runbook on staging, then run it in production (two app servers, load balancer, managed PostgreSQL with standby and PITR, managed Redis) 🔑
- [ ] Launch checklist complete: pen test, accessibility audit, backups tested, incident runbook

- [ ] "Should I move?" self-check (`/should-i-move`): scoring in `frontend/src/features/self-check/` (provided and tested), questions in `questions.json`, nothing stored; axe and keyboard pass; usability test with 5 employed people on whether the result feels fair and not pushy
- [ ] How hiring works guide (`/how-hiring-works`), from `content/hiring_stages.json`, sources and "last checked" date on the page; axe and keyboard pass
- [ ] Guides (`/guides/<id>`) from `content/guides/*.md`: referrals, the end of the search, long searches, different starting points; sources and "last checked" shown; statutory figures re-checked each April 🔑 solicitor read of the redundancy and disability sections
- [ ] Self-check "in a year" reflection: lasts/fades tags and notes from `questions.json` (`in_a_year`), already scored and tested
- [ ] Tracker: "Who do I know there?" (`referral_status`), long-search prompt after 8 weeks without a first call; Offers tab "In a year" view (`offers.year_view`); "What works for you" adds referred vs cold once each has the minimum outcomes
- [ ] Free LinkedIn check (`/linkedin-check`): paste headline and About, get the rules checklist; no account, processed in memory, nothing stored, rules only (no AI), Turnstile + rate limit; prompt to sign up for the full check and rewrite

Acceptance criteria
- Privacy gate: privacy notice published from `docs/privacy/privacy-notice-outline.md` after solicitor review; Stripe, Scaleway, Upstash, Cloudflare and Plausible DPAs signed; UK representative and DPO decided (#16, #17); breach tabletop done
- Production runs on Tier 1; killing one app server causes no failed requests through the load balancer; a database failover completes in under 2 minutes
- Payments are switched on only after the Tier 1 move, at the launch gate
- Lighthouse: performance ≥ 90, accessibility 100, best practices ≥ 95 on the landing page
- Test-mode purchase, upgrade, cancel and refund all work; webhooks idempotent
- External pen test: no unresolved high or critical findings

---

## Stage 5 — Job ingestion

> **Track E change (17 Nov 2026):** deferred until after Stage C. Get job-data quotes first (decision #8); the extension phase needs no job feed.

**Goal:** a clean, de-duplicated, enriched job database for Ireland and the UK.

Read before starting: `10-external-apis.md` §Job sources and §Public data, `04-data-model.md` §Jobs, `09-ml-and-analytics.md` §Data pipeline.

Tasks
- [ ] Connector interface + connectors: Adzuna, Jooble, Careerjet 🔑; Greenhouse, Lever, Ashby, Workable public job boards (company list maintained in DB)
- [ ] **Once-nightly, incremental** fetching per source (only new or changed jobs), with a per-source call budget and alert (Adzuna free tier: 2,500 calls a month)
- [ ] Parse, embed and flag each canonical job **once**, shared by all users
- [ ] Respect each source's terms, rate limits and attribution requirements; store raw payloads for 30 days
- [ ] Normalise: title, company, location (geocode to county / city), remote type, salary range and currency, posted date
- [ ] Near-duplicate detection: MinHash/LSH over shingled title + company + description; canonical job id
- [ ] Company entity resolution: blocking + RapidFuzz similarity + registry ids; manual merge tool for admins
- [ ] Public data loaders (scheduled): UK register of licensed sponsors, Ireland Critical Skills list, Irish employment permits by company, CRO / Companies House lookups 🔑 API key
- [ ] Visa badges computed per job; permit counts labelled as past activity
- [ ] Expiry: mark jobs closed when they leave the source
- [ ] Admin screen: source health, ingestion counts, duplicate rates

- [ ] Nightly `role_skill_demand`: ESCO skill counts per role family over the last 90 days of ads; switches on the LinkedIn keyword gap (`keyword_gap`, hidden below 30 ads)

Acceptance criteria
- Privacy gate: LIA 0004 approved; raw payloads expire at 30 days and ads 365 days after last seen (retention job covers both tables)
- Nightly ingestion completes within 60 minutes for Ireland + UK; failures alert
- Duplicate rate after de-duplication < 2% on a hand-labelled sample of 500 jobs
- Company resolution precision ≥ 0.95 on a labelled sample

---

## Stage 6 — Matching and the daily digest

> **Track E change (17 Nov 2026):** deferred with Stage 5. Extension users who connect supply the first outcome data.

**Goal:** a ranked list of jobs each morning, each with reasons and honest badges.

Read before starting: `09-ml-and-analytics.md` §Matching and §Fake jobs, `08-screens.md` §Job matches and §Job detail.

Tasks
- [ ] Preferences: roles, locations, commute time, remote/hybrid, salary floor, visa status, excluded companies
- [ ] Cheap filters → hybrid retrieval (Postgres full-text BM25 + pgvector embeddings, reciprocal rank fusion)
- [ ] Scorer v0: transparent weighted rules with reasons ("Raises / Lowers"); shown as a score, not a probability, until calibration data exists
- [ ] Fake job rules v0: repost count, posting age vs median, salary vs market, missing registry entry, urgency language, payment requests
- [ ] "Report this job" with reasons; reports feed an admin review queue
- [ ] Commute-time filter using public transport data (OSRM/OpenTripPlanner or GTFS) — can start with straight-line distance
- [ ] Morning digest email (Celery beat, user's local time), unsubscribe link, one email a day max
- [ ] Job matches and job detail screens per design, filters working

Acceptance criteria
- Privacy gate: DPIA 0001 signed and AI Act question (#18) answered before matching is switched on for users; every score shows reasons and confidence; digest emails have one-click unsubscribe
- Digest generated for 10,000 synthetic users in under 30 minutes
- Every displayed score has at least two reasons and a source label
- Flagged listings show their reasons; hide-flagged filter works

---

## Stage 7 — Assisted apply and the tracker

> **Track E change (17 Nov 2026):** the platform tracker must import extension events (ULID idempotency, `source = extension`). Do not rebuild features the extension already does; reuse its schema and `packages/core`.

**Goal:** prepare applications in minutes and track them all in one place.

Read before starting: `08-screens.md` §Job detail and §Applications, `04-data-model.md` §Applications and events, `prompts/cover_letter.md`.

Tasks
- [ ] Assisted apply checklist: tailored CV version, cover letter draft (`prompts/cover_letter.md`), screening answers prefilled from the profile, open employer site
- [ ] Log `applied` on return (user confirms); never submit on the user's behalf
- [ ] Applications board (Saved, Applied, Screening, Interview, Offer, Closed) + list view; drag to move (with keyboard alternative)
- [ ] Every change writes an `application_event` with timestamp
- [ ] Agency tracking: record agency submissions; warn on duplicate submissions for the same role
- [ ] Reconnect and repitch: detect reposts of previously applied roles; prepare an updated version
- [ ] Manual add for applications made elsewhere

- [ ] Stage odds in the tracker: "Where your search stands" card, per-column odds, per-application progress ladder and messages (`app/insights/stage_odds.py`, scaffold provided and tested); usability test with 5 job seekers on whether the messages feel encouraging and honest

Acceptance criteria
- Privacy gate: tracker data in export and erasure plans (check with the fixture user)
- Keyboard users can move cards between columns
- Duplicate-submission warning appears in tests for agency + direct on the same canonical job

---

## Stage 8 — Reply capture and the honest rejection

> **Track E change (17 Nov 2026):** the extension has a paste-an-email classifier using the same rules; share the rule set and fixtures.

**Goal:** capture replies automatically, explain rejections, show company reply behaviour.

Read before starting: `09-ml-and-analytics.md` §Replies, §Survival, §Empirical Bayes, §Calibration; `10-external-apis.md` §Email.

Tasks
- [ ] Per-user forwarding address; inbound email webhook (signature verified), spam filtering, size limits
- [ ] Reply classifier: rules v0 (sender domains of hiring systems, template phrases) → TF-IDF + logistic regression v1 when ≥ 1,000 labelled replies
- [ ] User confirmation UI for low-confidence classifications (also creates labels)
- [ ] Auto-rejection likelihood: timing, send hour/day, sender type, template match; rules v0 → logistic model + isotonic calibration v1
- [ ] Honest rejection panel: likelihood, signals, probable cause (screening answers), what to try next, helpful yes/no
- [ ] Company reply statistics: Kaplan–Meier curves; competing risks (rejection / interview / assessment); Empirical Bayes shrinkage to sector priors; minimum sample size before showing badges
- [ ] Reply-rate badges with confidence; employer right-of-reply process 🔑
- [ ] "When to stop waiting" hints on tracker cards

Acceptance criteria
- Privacy gate: LIA 0003 approved; email bodies encrypted at rest; bodies, senders and subjects cleared at 90 days (test); company stats use sender domain only
- Reply classification accuracy ≥ 0.9 on a held-out labelled set (v1)
- Calibration: Brier score reported; reliability curve within ±5 points per decile on validation data
- Badges never shown below the minimum sample size

---

## Stage 9 — Insights

**Goal:** "Where you stand" and "What works for you", with honest statistics.

Read before starting: `09-ml-and-analytics.md` §Benchmarks, §Experiments, §Uplift; `08-screens.md` §Home and §What works.

Tasks
- [ ] Peer cohorts (role family, seniority, region); funnel benchmarks with Empirical Bayes shrinkage
- [ ] Diagnosis rules: where the funnel leaks → next action
- [ ] Momentum: weekly goals, progress, reframing copy (kind, factual, no health claims)
- [ ] Experiments framework: consented random assignment, assignment table, CUPED, stratified analysis
- [ ] CV A/B tester: random split between two versions, sample-size progress, "too early to call" until confident
- [ ] What-works effects: start with stratified comparisons + randomised tests; uplift models only after the data gate (see ML doc)
- [ ] "How we calculate this" explainers for every number
- [ ] Unlock-by-logging prompts ("log 6 more outcomes")

- [ ] Stage odds v1: Hearback pass rates per role family with shrinkage towards the public prior; label switches to "Hearback data" with confidence

Acceptance criteria
- Privacy gate: benchmarks and experiments run only for users whose current consent is valid; k ≥ 10 enforced in the query layer (test with a cohort of 9)
- No effect is shown without an interval; intervals crossing zero say "no clear effect"
- Simulation tests: the A/B tester's false-positive rate ≤ 5% on null data

---

## Stage 10 — Interview prep

**Goal:** turn interviews into offers.

Read before starting: `08-screens.md` §Interview prep, `14-content-guidelines.md` §Interview content, `content/core_questions.json`, `content/competencies.json`, `prompts/interview_feedback.md`, `06-security.md` §Recordings.

Tasks
- [ ] Interview records (from tracker), format guides, day checklist, questions to ask them, debrief and follow-up reminders
- [ ] STAR story builder (Situation, Task, Action, Result, optional Reflection), sources: CV and outside work
- [ ] Story checks (rules): missing result, "we" vs "I", no number/outcome, spoken length estimate (words ÷ 150 wpm)
- [ ] Competency tagging and coverage map
- [ ] Elevator pitch builder: present/past/future, 30/60/90 second versions, tailored per role
- [ ] Core question bank (11 questions) with "what they're really asking" and "how to answer"; link stories to questions
- [ ] Role-specific questions from the job description and the user's gaps
- [ ] Mock interviews: text first, then voice
- [ ] Video practice: MediaRecorder in browser; **video stays in the browser for playback and is never uploaded**; only the audio track is uploaded (pre-signed URL) for transcription, then deleted after processing unless kept; faster-whisper transcription in the worker; metrics: length vs target, words per minute, filler words, long pauses, structure; self-review checklist; **no face or emotion analysis**
- [ ] Anonymised "questions asked at this company" bank (consented)
- [ ] Offer comparison: take-home pay (Irish and UK tax tables, yearly config), commute time and cost, office days; negotiation script

Acceptance criteria
- Privacy gate: DPIA 0002 signed; no video upload endpoint exists (test); audio deleted after transcription and by the 24-hour safety net; voice practice requires `voice_practice` consent, text practice does not
- No video file ever reaches the server (test); uploaded audio is deleted after processing unless kept
- Delivery metrics match hand-counted values on 10 sample recordings within 5%
- Tabs and recorder are fully keyboard-operable; captions/transcripts available for recordings

---

## Launch gate — public launch (after Stage 10)

**Goal:** open sign-up to everyone, with every feature built and every waiting-on-data state honest.

Tasks
- [ ] All Stage 0–10 and Stage C acceptance criteria met; private beta wave 3 has run for at least 4 weeks
- [ ] Launch date re-baselined after Phase E1 (decision #27); the 13 September 2027 target is at risk if the platform runs in parallel with Track E at full scope
- [ ] Waiting-on-data states reviewed on every screen: each says what it waits for, shows progress, and never shows an invented number
- [ ] Beta feedback triaged; every "blocker" and "confusing" item fixed or consciously deferred
- [ ] Legal: terms, privacy notice, cookie notice, accessibility statement, guarantee conditions, DPIAs 0001–0002 signed, AI Act question answered (#5, #7, #18) 🔑
- [ ] All DPAs signed for processors in use (#19); UK representative and DPO decided (#16, #17) 🔑
- [ ] Production on Tier 1; restore test and failover drill passed in the last 30 days
- [ ] External pen test and accessibility audit: no unresolved high or critical findings
- [ ] Stripe live mode, Stripe Tax, refunds and guarantee extension tested end to end
- [ ] Launch plan (marketing) ready: waitlist email, founder story content, free tools live (CV check, LinkedIn check, How hiring works)
- [ ] Remove the invite gate; monitor errors, sign-ups and costs daily for the first two weeks

Acceptance criteria
- A new user can sign up without an invite, use every feature, pay, and delete their account, on desktop and phone
- No screen shows a number without its source and confidence

---

## Stage 11 — Learned models (gated by data)

Switch each on only when its gate in `09-ml-and-analytics.md` §Data maturity is met.

- [ ] LightGBM LambdaMART ranker on outcome labels; SHAP reasons; Platt/isotonic calibration; replaces scorer v0 behind a flag with an offline + online comparison
- [ ] Fake job classifier (gradient boosting) + Isolation Forest for new patterns; SHAP reasons
- [ ] Uplift models (two-model, X-learner, tree-based meta-learners) for tailoring, follow-ups, timing
- [ ] Contextual bandits (Thompson sampling) for a small exploration slice of the digest
- [ ] Monitoring: Brier score, calibration drift, PSI on features; weekly report; automatic rollback flag
- [ ] Annual fairness audit tooling (consented demographics, stored separately)
- [ ] Privacy gate: DPIA 0003 signed before any demographic data is collected; `sensitive` schema with its own DB role; a test fails if any module other than the audit job imports the fairness model

---

## Stage 12 — Organisations

Pilots with one or two organisations can start during private beta wave 2 or 3 (aggregates only, k ≥ 10, organisation contract reviewed first); the self-serve organisation product follows launch.

- [ ] Organisation accounts, seats, invitations, roles (admin, adviser)
- [ ] Cohort dashboards with anonymised, aggregated outcomes only (k-anonymity ≥ 10)
- [ ] Bulk licences and invoices; SSO (SAML/OIDC) if required 🔑
- [ ] Privacy gate: organisations see aggregates with k ≥ 10 only; membership data in export and erasure; organisation contract/DPA terms reviewed by a solicitor (the organisation may be a separate controller)
