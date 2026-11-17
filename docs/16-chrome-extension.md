# 16 · Chrome extension: the first product

**Status:** proposal for owner approval, 17 November 2026. No implementation code is written until the owners approve this document (see §15). This document is the architectural review and revised build proposal; once approved it becomes the build reference for Track E in `02-build-stages.md`.

**Update, 17 November 2026.** The JobPilot build specification (v0.1) has since been reviewed. `docs/17-jobpilot-spec-review.md` maps all 29 of its features (F01 to F29) to phases, reconciles the data model, stack, permissions and algorithms, adds a risk register, backlog and first vertical slice, and **takes precedence over this document where they differ**. Main changes: no Tailwind; Recharts and spreadsheet libraries dropped; ULIDs everywhere; events are the source of truth; in-page filtering only on Tier A sites, never on LinkedIn, Indeed or Glassdoor; minimum Chrome 120 proposed; E1 is estimated at 10 to 13 weeks, so public v1.0 moves to May to June 2027.

---

## 0. Verdict in ten lines

1. **Build the extension first. It is the right front door**, because it is the only part of Hearback that can be useful on day one with no job data, no servers and no cost per user.
2. **"No AI, no backend, no accounts, local only" is a good v1, if it is treated as an edition, not as the architecture.** Design the code as a pure TypeScript core behind ports (storage, notifier, text generator, sync, data packs). The free edition plugs in local adapters; Connect and AI editions plug in others later.
3. **"Free for life" must have a written boundary:** *everything that runs on the user's device is free; users pay only for things that cost us server money* (job feed, email capture, AI, practice transcription). Publish it as a promise and never move a shipped local feature behind a paywall.
4. **The flywheel is data, not installs.** The asset Hearback needs is outcome data (company reply times, stage pass rates). The extension produces it locally; the platform needs a consented, user-initiated way to receive it. First bridge: export file → upload on the website (no network code in the extension). Second: optional Connect.
5. **LinkedIn and Indeed cannot be treated like other sites.** LinkedIn's own help page says it does not permit browser extensions that scrape, modify the appearance of, or automate activity on its services. The extension must not run content scripts on linkedin.com at all. This amends platform rule 3 (§8, ADR 0008).
6. **Best-supported job sites are Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Teamtailor, Personio and any page with `JobPosting` JSON-LD.** Workday is feasible but fragile and goes in Phase 3.
7. **Do not call it JobPilot.** Several JobPilot and JobCopilot AI auto-apply extensions already exist in the Chrome Web Store, and "pilot" signals auto-apply, which is the opposite of Hearback's rule 2. Use the Hearback brand (§12).
8. **Some things cannot be done locally and should not be faked:** cross-device sync, email reply capture, job matching feed, company reply badges, generative writing, reliable speech-to-text, commute routing (§11).
9. **Biggest hidden cost of "free forever" is adapter maintenance** (job sites change their pages). Budget for it in time, test with saved fixtures, and keep adapters data-driven so a later Connect edition can ship selector updates as data.
10. **Realistic plan:** spikes in December, tracker core alpha by March 2027, public v1.0 around May to June 2027, apply-assist in summer, Connect from autumn 2027. These are targets for approval, not commitments (§13).

---

## 1. Role in the business

```
Chrome Web Store search, founder posts, partners
        │
        ▼
Install Hearback (free for life, nothing leaves the browser)
        │  captures every job and application the user touches
        ▼
Weekly habit → personal history (the "spreadsheet", done properly)
        │  local insights work, but a single person has small n
        ▼
"Bring your history to Hearback" (export file, then optional Connect)
        │  consented, user-initiated, anonymised for benchmarks
        ▼
Platform: cohort odds, company reply badges, job matches, reply capture, AI writing
        │  more users → better benchmarks → more reason to connect
        └────────────────────────────────────────────► back to the top (referrals, reviews, word of mouth)
```

**What changes economically (hypotheses to test, not modelled yet):**

- Chrome Web Store search for "job application tracker" is a free, high-intent acquisition channel. It may be the cheapest sign-up source Hearback has, which matters because paid ads currently fail the €40 kill rule.
- Extension users are not yet accounts. The funnel gains new steps: install → weekly active → connect or export → paid. Every step needs a measure that does not break the privacy promise (§10, "Measuring without telemetry").
- A free local tracker can cannibalise paid conversion among people who only wanted a tracker. The paid plan therefore has to sell what local cannot do (§11), which is already most of the paid roadmap.
- Extension infrastructure cost is about zero per user. The new costs are founder time (adapter upkeep, support), the one-time Chrome Web Store registration fee (currently US$5; verify), and legal review.

### What "free for life" means (proposed wording, decision #23)

> If a feature runs on your computer, it is free, and it stays free. We charge only for things that cost us money to run on our servers, such as job feeds, email capture, AI writing and interview practice transcripts. We will not remove or lock a free feature after you have started using it.

Limits to state honestly: "for life" means the life of the product, not a guarantee the company or the browser platform exists forever. Say "free, and it stays free" in the store listing and avoid "lifetime" legal claims until the solicitor has read it.

---

## 2. Hard rules for the extension (E1 to E10)

These sit beside the twelve platform rules in `CLAUDE.md` and never override them.

| # | Rule |
| --- | --- |
| E1 | **Local edition makes no network requests to anything, ever.** No analytics, no crash reporting, no font or CDN loads, no update pings of our own. A CI test scans the built bundle and manifest (§6). |
| E2 | **No remote code.** Everything executable is in the package. Data packs are bundled and versioned with releases. |
| E3 | **No content scripts or UI injection on linkedin.com, indeed.com or glassdoor.com** (Tier C, §9). Manual capture only. |
| E4 | **Read only on user action or on a declared career-site pattern**, never in the background across tabs, never in bulk, never other people's profiles. |
| E5 | **Never submit anything for the user.** Autofill (Phase 3) fills visible fields only after a click and never presses submit. |
| E6 | **Never autofill or store special category fields:** diversity, disability, ethnicity, gender identity, religion, health. Leave them blank. |
| E7 | **Never invent experience.** The tailoring helper only reorders and highlights what the user wrote; the no-invention guard in `packages/core` is the shared check for any later AI text. |
| E8 | **Every score shows reasons, source and confidence**, and shows a waiting state until its data gate is met. |
| E9 | **The user owns the data:** one-click export (JSON and CSV), one-click delete, optional passphrase-encrypted backup, and a visible "what is stored" screen. |
| E10 | **Minimum permissions**, each justified in the store listing and in `docs/13` §16. No `<all_urls>` at install. |

---

## 3. What is verified and what is assumed

| Claim | Status | Source or test |
| --- | --- | --- |
| `chrome.storage.local` quota is 10 MB (5 MB before Chrome 114), raised by the `unlimitedStorage` permission; local data is cleared when the extension is removed | **Verified this session** | Chrome extensions storage reference |
| `chrome.storage.sync` is about 100 KB total with small per-item limits, and syncs through the user's Google account | **Verified** (quota); implication: unsuitable for personal data and not "no cloud" | Chrome extensions storage reference |
| LinkedIn does not permit third-party software, including browser plug-ins and extensions, that scrapes, modifies the appearance of, or automates activity on its services | **Verified this session** | LinkedIn Help: "Prohibited software and extensions"; User Agreement s8.2 |
| Chrome Web Store Limited Use policy applies to raw data and to aggregated, anonymised or derived data, and requires use only for the disclosed single purpose | **Verified this session** | Chrome Web Store User Data policy |
| Several "JobPilot", "JobCopilot" and "Job Pilot" AI auto-apply extensions already exist in the Chrome Web Store | **Verified this session** | Store search |
| MV3 service workers stop when idle, so no state may live in memory | Documented (re-verify at kickoff) | Chrome MV3 docs |
| No remotely hosted code; bundled WASM needs `wasm-unsafe-eval` in the extension CSP | Documented (re-verify) | Chrome MV3 docs |
| `chrome.alarms` minimum period is 30 seconds; alarms only fire while Chrome is running | Documented (re-verify) | Chrome alarms reference |
| Content scripts cannot open the extension's IndexedDB directly (they run against the page's origin); they must message the service worker | Documented (re-verify) | Chrome docs |
| IndexedDB in the extension origin is not evicted like web-origin storage | **Assumption: spike S5** | Test with `navigator.storage.persist()` and low-disk simulation |
| JSON-LD `JobPosting` is present on most Irish and UK employer career pages | **Assumption: spike S2** | Test 30 real pages |
| pdf.js text extraction in an offscreen document is accurate enough for CV import | **Assumption: spike S3** | Test 20 real CVs (decision #10) |
| Setting a file input programmatically works on Greenhouse, Lever, Ashby (DataTransfer technique) | **Assumption: spike S7** | Test per ATS |
| Chrome on-device speech recognition and the on-device Prompt API are available enough to rely on | **Assumption: unverified, spike S8; do not plan on it** | Availability varies by Chrome version and hardware |
| Chrome Web Store review time for a new extension with content scripts is days to weeks | **Assumption** | Budget four weeks; check developer dashboard |
| Indeed and Glassdoor terms restrict automated collection similarly to LinkedIn | **Assumption: treat as true until read**; solicitor check | Read current terms |

---

## 4. Feature catalogue, feasibility and phase

Legend. **Feasibility:** ✅ reliable locally · 🟡 feasible with limits or needs a spike · 🔴 not reliably possible without an external service. **Phase:** 1 Tracker core, 2 Job intelligence and CV, 3 Apply assist and prep, 4 Connect and optional editions.

### A. Capture and track

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| A1 | Save a job from a career page in one click | Schema.org `JobPosting` JSON-LD first, then per-ATS DOM adapters, then visible-text fallback | ✅ on Tier A, 🟡 on others | 1 |
| A2 | Manual add and "paste job description" box | Popup/side panel form; works on any site including Tier C | ✅ | 1 |
| A3 | Application board and list, with event log | Saved, Applied, Screening, Interview, Offer, Closed; every change is an event | ✅ | 1 |
| A4 | "Did you apply?" prompt on ATS confirmation pages | URL and text patterns per ATS; always asks the user to confirm | 🟡 spike per ATS | 1 (Greenhouse, Lever, Ashby), then more |
| A5 | Duplicate and repost detection | Canonical URL, then normalised company + title + location, then 64-bit simhash of the description (Hamming ≤ 3) | ✅ | 1 |
| A6 | Follow-up and deadline reminders | `chrome.alarms` + `chrome.notifications` + badge count; missed reminders shown on next browser start | ✅ (not while Chrome is closed) | 1 |
| A7 | Calendar export | `.ics` file download; no Google or Microsoft API | ✅ | 2 |
| A8 | Import from the user's own spreadsheet | CSV mapping wizard (the founder story as a feature) | ✅ | 1 |
| A9 | Export everything | JSON (lossless) and CSV (spreadsheet-friendly) | ✅ | 1 |

### B. Honest insight (all local)

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| B1 | Stage odds ("Where your search stands") | Published pass rates from `content/hiring_stages.json`, labelled "public data, low confidence" | ✅ | 1 |
| B2 | Reply-time curves and "likely ghosted" status | Kaplan-Meier with right-censoring for applications still open; rule: no reply after N days, N from the curve | ✅ | 2 |
| B3 | What is working for you | Stratified comparisons by CV version, source, early vs late, company size; beta-binomial shrinkage toward published priors; Wilson intervals; waiting state until 20 outcomes | ✅ | 2 |
| B4 | CV A/B tagging | Each application stores the CV version; verdict "too early to call" with progress | ✅ | 2 |
| B5 | Weekly review page | Counts, replies, open follow-ups, one honest sentence | ✅ | 2 |
| B6 | "In a year" reflection | Reuses the self-check scoring | ✅ | 1 (as the first free tool inside the extension) |

### C. Job-page intelligence (rules and bundled data only)

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| C1 | Job description parser | Heading lexicon, bullet segmentation, cue words ("must", "essential" vs "desirable", "bonus"), years-of-experience and seniority regex, salary regex for € and £ | ✅ target F1 ≥ 0.85 on 30 labelled descriptions | 2 |
| C2 | CV ↔ job keyword match | BM25 plus skill-set coverage over a curated skills dictionary (pruned ESCO, CC BY, plus tech terms); shows each requirement with its evidence line, never one opaque score | ✅ (no semantic understanding; state it) | 2 |
| C3 | Right-to-work and sponsorship phrases | Phrase rules ("no sponsorship", "must have the right to work in…") | ✅ | 2 |
| C4 | Visa sponsor badge | Bundled compact data pack from the UK Register of Licensed Sponsors and the Irish Critical Skills list; fuzzy company match with confidence; "last updated" shown | 🟡 freshness lags releases; false matches possible | 2 |
| C5 | Suspicious-listing signals | Weighted rules (fee to apply, messaging-app contact, free-mail contact for a named company, vague company, urgency language); shows signals, never says "this is a scam" | 🟡 false-positive and defamation risk; wording reviewed by solicitor | 2 |
| C6 | Stale and ghost-job signals | Posted date and valid-through from JSON-LD, repost count seen locally | 🟡 partial | 2 |
| C7 | Salary extraction and comparison | Regex plus the user's own saved jobs | 🟡 many ads give none | 2 |
| C8 | Commute time | Needs routing data | 🔴 external service (straight-line distance only) | 4 |

### D. Documents (all local)

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| D1 | Master profile and CV versions | Structured JSON matching `cv.schema.json` | ✅ | 2 |
| D2 | CV import from PDF and DOCX | pdf.js in an offscreen or options page (lazy-loaded); DOCX as zipped XML via `fflate`; rules parser; manual correction screen | 🟡 spike S3; scanned PDFs unsupported (no OCR in v1; say so) | 2 |
| D3 | CV check (screening-safety and Irish/UK conventions) | Rules over extracted text and layout: columns, tables, images, header and footer text, dates, length, photo; `content/cv_conventions.json` | ✅ | 2 |
| D4 | CV export | PDF with real selectable text (`pdf-lib` with embedded fonts) and DOCX (`docx` library) from templates | ✅ moderate effort | 2 |
| D5 | LinkedIn check | Paste headline and About; rules in `content/linkedin_rules.json`; LinkedIn data-export ZIP parsed in the browser (port of `backend/app/linkedin/export_parser.py`). Runs on the extension's own pages, never on linkedin.com | ✅ | 2 |
| D6 | Tailoring helper without AI | Matched and missing requirements with evidence; reorder bullets by relevance; surface matched skills; "I have this" adds evidence the user types; gap stays private | ✅ limited (no rewriting) | 2 |
| D7 | Cover letter from a template | Merge fields (company, role, matched skills); user edits | 🟡 mediocre without AI; say so | 3 |

### E. Apply assist and prep

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| E1 | Form autofill (fill, never submit) | Field classifier by label, `name`, `autocomplete`, ARIA; native value setter plus `input` and `change` events for React forms; file attach via `DataTransfer` | 🟡 fragile on Workday; spike S4 and S7; crowded category with the most store scrutiny | 3 |
| E2 | Interview prep content | STAR builder, competency coverage from `content/competencies.json`, core questions, pitch timer | ✅ | 3 |
| E3 | Offer comparison and take-home | Yearly Irish and UK tax data pack; "In a year" view | ✅ (yearly data update) | 3 |
| E4 | Practice recording with transcript | Recording works (`MediaRecorder`); transcript needs speech-to-text. Chrome's built-in recognition may send audio to a server, so it breaks local-only; on-device availability unverified; WASM Whisper is large and slow | 🔴 for reliable local use; timer-only practice is ✅ | 4 (via platform) |

### F. Data safety and portability

| # | Feature | Method | Feasibility | Phase |
| --- | --- | --- | --- | --- |
| F1 | Passphrase-encrypted backup | Web Crypto: PBKDF2 (or Argon2 WASM later) + AES-GCM; versioned file format | ✅ | 1 |
| F2 | Scheduled backup to a user-chosen folder | File System Access API from an extension page; re-permission prompts after restart | 🟡 spike S9 | 2 |
| F3 | Backup reminder | Alarm every 30 days if no export | ✅ | 1 |
| F4 | Cross-device sync | `chrome.storage.sync` is too small and is Google's cloud; file export/import is the free workaround | 🔴 needs a service (Connect) | 4 |
| F5 | Email reply capture | Needs inbound email or the Gmail API; reading Gmail's page is fragile and risks store policy. Local alternative: paste an email, rules classify it ("automated rejection", "interview invite", "request for information") | 🔴 automatic; ✅ paste | 2 (paste) / platform |

---

## 5. Manifest V3 constraints and what they force

| Constraint | Consequence for the design |
| --- | --- |
| Service worker is ephemeral | No state in memory. Every handler loads what it needs from IndexedDB; timers use `chrome.alarms`, never `setInterval`. |
| No remote code, no `eval` | Bundle everything; no CDN; data packs ship with releases. |
| Content scripts cannot reach the extension database | Content scripts only extract and message the service worker; the worker owns storage. |
| Content scripts run in an isolated world | Autofill into React-controlled inputs needs the native value setter and synthetic events, sometimes a `MAIN` world helper; spike S4. |
| Page DOM parsing and PDF work need a DOM | Use offscreen documents (`DOM_PARSER`, `BLOBS`) or extension pages, not the worker. |
| Broad host permissions trigger long review and scary warnings | Use `activeTab` + `scripting` for on-demand capture on any site; static content scripts only for Tier A ATS domains; offer `optional_host_permissions` for "detect jobs on any career site". |
| Storage is bound to the browser profile and removed on uninstall | Backup and export are core features, not extras. |
| Alarms and notifications only work while Chrome runs | Reminders catch up at browser start; do not promise "we'll remind you at 9am". |
| Side Panel API gives a persistent UI | Use it as the main working surface next to a job page; popup for quick actions. |

---

## 6. Revised architecture

### 6.1 Repository layout (monorepo, extends ADR 0001)

```
packages/
  core/        pure TypeScript, no browser APIs, no DOM: domain model, event reducers, scoring
               (stage odds, Kaplan-Meier, shrinkage), text pipeline (tokenise, BM25, synonyms),
               JD parser, CV checks, scam signals, ICS, export schema (zod), no-invention guard
  data/        versioned data packs built from /content: hiring stages, competencies, questions,
               LinkedIn rules, banned phrases, skills (ESCO-lite), sponsor register, tax tables
  storage/     StorageAdapter interface; IndexedDB (Dexie) implementation; later a Remote adapter
  adapters/    site adapters (jsonld, greenhouse, lever, ashby, workable, smartrecruiters,
               teamtailor, personio, workday, generic) each with saved HTML fixtures and tests
  ui/          design-system components and tokens shared with frontend/ (React + CSS Modules)
extension/     WXT (or Vite + CRXJS; verify maintenance at kickoff) app: background worker,
               content scripts, side panel, popup, options dashboard, offscreen documents,
               editions/ (local, connect, ai)
frontend/      platform web app (existing); imports packages/core and packages/ui
backend/       platform API (existing)
```

**Rule:** `packages/core` may not import `chrome`, `window`, `document` or any package that does. Enforced by lint (`no-restricted-imports` plus dependency-cruiser) in CI. This is what makes the same rules run in the extension, the website's free tools and (via shared fixtures) the Python backend.

**One implementation per rule.** `packages/core` is canonical for deterministic, client-side features. The Python backend re-implements only what must run server-side (nightly matching, scam classifier training) and is checked against the same golden fixtures. This replaces the plan to parse CVs on the server first (see `docs/02` Stage 2 and 3 changes).

### 6.2 Ports and editions (how AI and cloud come later without a rewrite)

| Port (interface in `core`) | Local edition | Later editions |
| --- | --- | --- |
| `Storage` | IndexedDB | `RemoteStorage` over the platform API with the same event schema |
| `Notifier` | `chrome.notifications` | adds email digests (platform) |
| `DataPackProvider` | bundled packs | adds fresher packs and adapter selector updates, fetched as data (never code) |
| `TextGenerator` | `NullGenerator` (returns "not available in this edition", UI hides buttons) | (a) platform-hosted via account; (b) bring-your-own-key direct to the provider; (c) Chrome on-device model if verified. All return JSON validated by the schemas in `prompts/schemas/`, then pass the no-invention guard |
| `Sync` | none | pairing code + token, event upload by ULID (idempotent) |
| `Telemetry` | `NullTelemetry` | opt-in, aggregate, platform-side only |

**Editions are build flavours of one codebase**, chosen at build time (`EDITION=local|connect`). A capability registry (`features.ts`) lists what each edition enables. The local build's manifest contains no host permissions beyond Tier A career sites, no `identity`, and no network code. Connect adds one `optional_host_permissions` entry for the Hearback API, requested at runtime when the user clicks "Connect", so existing users are not disabled by a permission change. One store listing, updated honestly when Connect ships.

### 6.3 Gates enforced in CI (the "network audit")

- Built local bundle contains no `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `sendBeacon`, `importScripts` of remote URLs, or remote `<script>`/`<link>`/font URLs (static scan plus an allow-list for the extension's own origin).
- Manifest permissions diff: any new permission or host pattern fails the build unless `docs/13` §16 and the store listing text are updated in the same pull request.
- Playwright run with a network blocker: every feature works offline.
- Reproducible build: the published zip hashes match a CI build of the tagged commit.
- Bundle size budgets (initial worker, side panel, lazy chunks for pdf.js and skills dictionary).

### 6.4 Technology choices (challenged)

| Choice | Recommendation | Why |
| --- | --- | --- |
| Framework | WXT (maintained; confirmed in review, see `docs/17` §2), or Vite + CRXJS if WXT is unsuitable. Verify release activity at kickoff. Tailwind is not used: CSS Modules and tokens only. | MV3 manifest generation, HMR, multi-browser builds. Avoid hand-rolled webpack. |
| UI in side panel and options page | React + CSS Modules + shared tokens | Same components as the platform. Radix primitives for accessibility. |
| UI injected into pages | Shadow DOM, vanilla or Preact, tiny | Keeps injected code small and isolated from page CSS. No React in content scripts. |
| Database | IndexedDB through **Dexie** | Mature, migrations, live queries. A heavier engine (SQLite WASM on OPFS) is overengineering for v1; keep as a Phase 4 option if analytics need joins. |
| Search | MiniSearch for the user-facing search box; BM25 in `core` for scoring | Scoring must match the platform's semantics. |
| Validation | zod at every boundary (storage, messages, import) | Same schemas as the web app. |
| State | No global state library; events plus reducers in `core`, Dexie live queries in UI | Fewer dependencies. |
| PDF read | pdf.js, lazy-loaded | Largest dependency; not in the worker. |
| PDF write | pdf-lib (embedded fonts, selectable text) | No headless browser available. |
| DOCX write | `docx` | Mature. |
| Zip | `fflate` | Small. |
| Dependencies overall | Pin, audit weekly, justify each in the pull request | Supply chain is the main store-takeover risk. |
| Not recommended | Redux, Firebase, any analytics SDK, any CDN, Tesseract OCR (size), on-device LLMs in v1, `<all_urls>` at install | Size, privacy, review risk. |

---

## 7. Local data model (IndexedDB, schema v1)

**Principle:** an append-only **event log is the source of truth**; application state is derived by reducers in `core`. This mirrors the platform's `application_event` table, so import into the platform is lossless and idempotent, and every stat can be recomputed if a bug is fixed.

| Store | Key | Contents | Notes |
| --- | --- | --- | --- |
| `events` | ULID | `type`, `entityId`, `ts` (UTC ISO), `deviceId`, `schemaVersion`, `payload` | Types: `job_saved`, `applied`, `stage_changed`, `reply_received`, `follow_up_set`, `note_added`, `cv_version_used`, `closed`, `deleted`. Append-only; corrections are new events |
| `applications` | applicationId | Derived view: job ref, current stage, timestamps, CV version, source, reply days | Rebuildable from `events`. Never the only copy |
| `jobs` | jobId | Canonical URL, company, title, location, salary, posted/valid-through, parsed requirements, description (gzip via `CompressionStream`), simhash, capture method, `capturedAt` | Description stored compressed (about 5 to 15 KB each) |
| `companies` | companyId | Normalised name, aliases, sponsor-badge result, size band (user-entered) | Legal suffixes stripped (Ltd, Limited, DAC, PLC, Teoranta) |
| `documents` | docId | CV versions (structured JSON), original file blob (optional), LinkedIn text, cover-letter templates | Original blobs optional to save space |
| `profile` | singleton | Name, contact, links, right to work, preferences | Never includes special category fields |
| `reminders` | id | Due date, application ref, state | Re-created from events on startup |
| `settings` | key | Preferences, backup stamps, data-pack versions | |
| `meta` | key | `schemaVersion`, `deviceId`, migration history | |

**Design rules (review of typical pitfalls):**

- IDs are ULIDs (sortable, collision-free across devices). Timestamps are UTC with a hybrid logical clock field reserved so a later sync merge can resolve conflicts. Deletions are tombstone events.
- Do not over-normalise: IndexedDB has no joins. Denormalise display fields into `applications`; keep `events` as the audit trail.
- Do not store derived statistics as truth (they go stale); cache them with the event count they were computed from.
- Indexes only on fields queried (stage, updatedAt, canonicalUrl, simhash prefix). No personal data in index keys that are not needed.
- Migrations are versioned Dexie upgrades. Before any upgrade the extension writes an automatic snapshot the user can download. Every historical schema version has a fixture and a migration test.
- Growth is user-controlled: a storage screen shows size by store, with "delete job descriptions older than X".
- Request `unlimitedStorage` (benign, avoids quota failures when many descriptions are stored); justify it in the listing.

**Export format v1** (`hearback-export.json`): `{ format: "hearback-export", version, exportedAt, deviceId, events[], documents[], profile, settings }`, validated by a zod schema shared with the platform's import endpoint and the website's browser-only preview. Optional encrypted wrapper (F1).

---

## 8. Policy changes this forces on the platform rules

**Rule 3 (no scraping) stays; its wording is clarified, and the old line in `docs/10` ("never use a browser extension to read pages") is replaced** (ADR 0008):

- The extension may read the job posting the user is viewing, on user action or on declared Tier A career-site patterns, when the site's terms do not prohibit it.
- It never reads LinkedIn, Indeed or Glassdoor pages, never crawls, never runs in the background across tabs, never collects other people's profiles or contact details, and never automates actions on any site.
- LinkedIn features remain export-or-paste only, running on Hearback's own pages.

---

## 9. Site compatibility

| Tier | Sites | What the extension does | Status |
| --- | --- | --- | --- |
| **A: read the open job page** | Greenhouse (`boards.greenhouse.io`, `job-boards.greenhouse.io`, embeds), Lever (`jobs.lever.co`), Ashby (`jobs.ashbyhq.com`), Workable (`apply.workable.com`), SmartRecruiters, Teamtailor, Recruitee, BambooHR, Personio, plus Irish and UK public-sector and board sites (`publicjobs.ie`, Civil Service Jobs, IrishJobs.ie, Jobs.ie; terms to check per site) | Auto-detect, "Save job", "Did you apply?" prompt, keyword match, badges. Method: JSON-LD, then adapter, then visible text | JSON-LD coverage: spike S2. Ashby is a single-page app: spike |
| **A2: any career page with JSON-LD** | Thousands of employer sites | On click through `activeTab`, or auto-detect if the user grants optional host access | Spike S2 |
| **B: heavy or legacy ATS** | Workday (`myworkdayjobs.com`), iCIMS, Taleo, SuccessFactors | Read on click; autofill only after fixtures prove it. Workday is a single-page app with tenant variation | Phase 3; Workday spike S4 |
| **C: restricted** | LinkedIn, Indeed, Glassdoor | **No content scripts, no DOM reading, no UI injected.** The user clicks the toolbar icon on the tab; the extension uses only the tab's URL and title from the browser, plus fields the user types or pastes. "Apply on company site" links usually lead to Tier A pages where capture is automatic. Easy Apply applications are logged manually | Policy, not engineering. Never advertise "works on LinkedIn"; say "track LinkedIn and Indeed jobs by saving the link" |

Marketing claims must match this table (see `Marketing/02-copy/extension-launch.md`).

---

## 10. Security, privacy and Chrome Web Store compliance

### Store policy fit

- **Single purpose** (proposed statement for the dashboard): "Track job applications and check job postings and your CV, with all data kept in your browser." Every feature in §4 serves that purpose. No new-tab override, no search-engine change, no unrelated utilities.
- **Limited Use:** the policy covers raw and derived data. Local-only use is simple. Anything transmitted later (Connect, contributions) must be necessary to the single purpose, disclosed, and consented. **Contribution to benchmarks is therefore designed as a user action on the Hearback website (upload the export, tick the benchmark consent), not a background upload from the extension.** Confirm with the solicitor and re-read the policy before Phase 4.
- **Listing integrity:** no keyword stuffing, no implying LinkedIn or Indeed endorsement or logos, no incentivised or gated reviews (do not ask only happy users), accurate permission and data-handling declarations, working privacy-policy URL and support contact.
- **Publisher account:** use a dedicated Google account with hardware security keys and recovery set up; store takeover is the largest real-world extension threat. EU trader status and public contact details are a decision (#26), tied to company incorporation (#15).
- **Review risk:** new extension with content scripts may take days to weeks; budget four weeks (assumption). Submit a minimal permission set first.

### Permissions (proposed, local edition)

| Permission | Why | Warning shown |
| --- | --- | --- |
| `storage`, `unlimitedStorage` | Local database and settings | None |
| `alarms`, `notifications` | Reminders | "Display notifications" |
| `sidePanel` | Main working surface | None |
| `activeTab`, `scripting` | Read the open page on click (A2, Tier C URL and title) | None |
| `offscreen` | PDF and DOM parsing | None |
| Static content-script matches: Tier A domains only | Auto-detect, "Did you apply?" prompt | "Read and change your data on these sites" for the listed hosts |
| `optional_host_permissions: https://*/*` | "Detect jobs on any career site" if the user opts in | Requested at runtime |
| Not requested: `tabs`, `history`, `cookies`, `webRequest`, `identity`, `<all_urls>`, `clipboardRead` | Not needed | |

### Extension security

- Treat all page data as hostile: extract text only, render with `textContent`, never `innerHTML` from page data.
- Validate every message with zod; check `sender.id` and sender context; no `externally_connectable`; avoid `web_accessible_resources` (they enable extension fingerprinting).
- Strict extension CSP; no inline script.
- `chrome.storage.local.setAccessLevel('TRUSTED_CONTEXTS')` so content scripts cannot read the store directly.
- Minimal dependencies, lockfile, weekly audit, signed tags, reproducible builds.
- Backups are optionally passphrase-encrypted; never store the passphrase.

### Privacy position (details in `docs/13` §16)

- With zero transmission, Hearback does not receive the data in the local edition. The website, waitlist and any account remain under the existing GDPR framework. Solicitor to confirm the controller position for locally processed data and the wording of the privacy policy (a policy is still required for the listing and the website).
- **Measuring without telemetry:** use Chrome Web Store dashboard statistics (installs, uninstalls, ratings), tagged links from the extension to the website (opened by the user, UTM-tagged), the website's cookieless analytics, an optional in-extension "Send feedback" that opens an email draft, and a short opt-in survey on the website. Do not add an analytics SDK to the local build.

---

## 11. What cannot be done reliably without external services

| Capability | Why not local | Where it lives |
| --- | --- | --- |
| Cross-device sync and phone access | Needs a store both devices can reach; `storage.sync` is too small and is Google's cloud | Connect (platform) |
| Automatic reply capture from email | Needs inbound email or the Gmail API (restricted scopes, paid assessment); Gmail DOM reading is fragile | Platform Stage 8; extension keeps "paste an email" |
| Daily matched jobs and fresh listings | Needs licensed job data and a nightly pipeline; scraping is not allowed | Platform Stages 5 to 6 |
| Company reply-rate badges, cohort benchmarks | Need many users' outcomes; no single user has enough n | Platform, fed by consented imports |
| Generative writing and judging interview answers | Needs a model | AI edition or platform |
| Reliable speech-to-text for practice | Local options send audio away, or are large and slow | Platform (faster-whisper) |
| Commute routing | Needs map and transit data | Platform |
| Fresh sponsor-register data between releases | Bundled data ages | Connect data refresh |
| Email digests and push reminders when Chrome is closed | Needs a server | Platform |
| Organisation dashboards | Need accounts and consent | Platform Stage 12 |

---

## 12. Naming and brand

- **Do not use "JobPilot".** Verified in the store search: JobPilot, JobPilot AI, JobCopilot and Job Pilot AI auto-apply or autofill extensions already exist, so the name is crowded and unprotectable, and "pilot" implies automation that contradicts rule 2.
- **Recommended:** the Hearback brand. Store title along the lines of "Hearback: Job Application Tracker and CV Check" (the store name field allows up to 75 characters and the summary up to 132; the manifest `short_name` is much shorter; confirm current limits). The brand check (trademark in EUIPO and UK IPO, CRO, domain) is a gate before the store listing, because the name appears in the store and cannot easily be changed (decision #22).
- Use the reply-bubble mark. The extension toolbar icon needs 16, 32, 48 and 128 px versions in the existing marks (task in Track E0).

---

## 13. Roadmap, dependencies and milestones (targets for approval)

Assumes one founder with Claude Code building and 2 to 4 hours a week of marketing. Dates are targets from 17 November 2026; re-baseline after each phase.

| Phase | Window | Deliverable | Depends on | Exit gate |
| --- | --- | --- | --- | --- |
| **E0 Decisions and spikes** | Nov to mid-Dec 2026 | Approvals (§15), name checks, store developer account, spikes S1 to S9, spike report with go/no-go per feature | This document approved | Each spike has a recorded result; feature list updated |
| **E1 Tracker core** | Mid-Dec 2026 to Mar 2027 | Monorepo, `core`, `storage`, events, capture (JSON-LD + Greenhouse, Lever, Ashby, Workable + manual and paste), board, reminders, JSON/CSV export and import, spreadsheet import, stage odds, "Should I move?", encrypted backup, accessibility pass, network audit in CI | E0; design of extension surfaces (§14) | Alpha to 10 to 20 trusted testers via an unlisted store listing; 7 days of daily use without data loss |
| **E2 Job intelligence and CV** | Mar to May 2027 | JD parser, keyword match, right-to-work phrases, sponsor badge, suspicious-listing signals, CV import and check, LinkedIn check, CV versions and A/B tagging, personal "what works", weekly review, .ics, scheduled backup | E1; golden sets (decision #10); data packs | Parser F1 ≥ 0.85; CV check validated on 20 real CVs; keyboard and axe pass |
| **Public v1.0** | Target May to June 2027 (moved by the E1 estimate in `docs/17` §9) | Public store listing; marketing begins (`Marketing/02-copy/extension-launch.md`) | E2 core; privacy policy and listing approved; store review time (allow four weeks) | No data-loss bugs in 4 weeks of alpha; listing approved |
| **E3 Apply assist and prep** | Jun to Jul 2027 | Autofill (fill, never submit), Workday adapter, more ATS adapters, cover-letter templates, interview prep, offer comparison and tax pack | E2; spikes S4, S7 | Autofill correct on fixtures for each supported ATS; never submits; no special category fields |
| **E4 Connect and optional editions** | From Aug to Dec 2027 | Pairing, import into the platform, sync, data refresh packs, opt-in contributions, then AI edition | Platform Stages 1 and C (accounts, Connect import); solicitor sign-off; Limited Use review | Idempotent import test; consent recorded; store listing and privacy policy updated before release |

**Dependencies that can slip the plan:** brand and trademark clearance (#22); Chrome Web Store review time; founder capacity (extension upkeep plus platform plus marketing); golden test sets; ATS page changes.

**Platform impact on dates:** the public launch of the platform on 13 September 2027 is **at risk** if the platform build continues in parallel with Track E on the current scope. Re-baseline after E1 (see `STATUS.md` and decision #27). Do not state new dates publicly until then.

### Spikes (E0)

| # | Question | Pass condition |
| --- | --- | --- |
| S1 | Does the worker + IndexedDB pattern survive repeated worker shutdowns and browser restarts? | No lost writes in 1,000 forced restarts |
| S2 | What share of 30 real Irish and UK career pages expose usable `JobPosting` JSON-LD? | ≥ 60% usable; otherwise adapters move up |
| S3 | pdf.js on 20 real CVs: text order, columns, headers | ≥ 85% of sections correctly detected |
| S4 | Workday: can we read the posting and fill text fields reliably? | Works on 3 tenants |
| S5 | Is extension IndexedDB persisted under low-disk conditions? | Persisted or recovered from automatic snapshot |
| S6 | Do alarms and notifications catch up after sleep and restart? | Missed reminders shown at next start |
| S7 | File attach on Greenhouse, Lever, Ashby | Works on all three or documented fallback |
| S8 | Local speech recognition and on-device model availability | Record result only; not a dependency |
| S9 | Folder backup via the File System Access API | Survives browser restart or re-prompts cleanly |

---

## 14. Platform changes, summarised

Full detail is in the handoff and `02-build-stages.md`. In short:

1. The platform becomes the **account layer** on top of the extension: Connect (import, sync, benchmarks), then the server-cost features (job feed, reply capture, AI, practice).
2. **Event model:** `application_event` accepts imported events (ULID ids, client timestamps, `source = extension`, schema version) and imports idempotently.
3. **Browser-first processing:** CV parsing, CV check, keyword match and the free tools run in the browser through `packages/core`, so the server receives a CV only when the user asks for AI writing. This also reduces personal data held.
4. **Preview without account:** the website accepts an export file and shows insights in the browser, storing nothing, like the existing free checks.
5. **Sequence:** defer job ingestion and the Tier 0 server until Connect needs them. This avoids €300 to €500 a month of job data and about €30 to €50 of hosting during the extension phase.
6. **Surfaces to design** (design canvas): popup, side panel (board, job, CV check), page overlay chip, options dashboard, empty states, backup reminder, permission explainer, "what is stored", export/import, waiting-on-data states. Reuse `design/tokens.json`.
7. **Marketing site:** primary call to action becomes "Add to Chrome, free for life"; waitlist stays for the platform.

---

## 15. Decisions for the owners

See `decisions-needed.md` #22 to #30. Nothing in Track E beyond E0 starts until #22 (name), #23 (free-for-life wording), #24 (LinkedIn and Indeed policy) and #27 (platform re-baseline) are answered.
