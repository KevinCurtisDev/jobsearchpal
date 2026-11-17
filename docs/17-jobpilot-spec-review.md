# 17 · Review of the JobPilot build specification (v0.1) and revised extension plan

**Status:** Proposed for approval · 17 November 2026 · supersedes the matching parts of `docs/16` where they differ
**Scope:** analysis only. No implementation code. Section 13 of the spec asks us to wait for approval before generating a codebase; we do.

Labels used throughout: **[Verified]** = read in current documentation on 17 Nov 2026 (link given). **[Assumed]** = reasoned or remembered, must be tested in an E0 spike. **[Policy]** = depends on a third party's terms or on a solicitor.

---

## 0. Verdict

The spec is a good product concept and a sound local-first design. Four things in it need to change before it becomes our build plan.

1. **The name and brand.** JobPilot is unchecked (the spec says so). The extension ships as the Hearback extension (decision #22), because it is the acquisition path for the platform.
2. **In-page hiding and highlighting (F05, F12) on LinkedIn and Indeed.** The spec defers those adapters "until policy testing". Our answer is already clear enough to decide now: **no content scripts and no page changes on LinkedIn, Indeed or Glassdoor.** LinkedIn's help page on prohibited software lists bots and automated access to the Services ([LinkedIn](https://www.linkedin.com/help/linkedin/answer/a1341387)), and Indeed's Terms define an "Indeed App" to include any browser extension and are reported to prohibit "robots", "spiders" and other automated access ([Indeed Terms](https://www.indeed.com/legal)). The exact clauses must still be read by the solicitor **[Policy]**, but filtering ships only on sites where we have a clear basis (Tier A employer ATS pages, then Irish boards after a terms check).
3. **Stack details.** Keep WXT, TypeScript, Dexie and Zod. Drop Tailwind (it fights our token rule: no raw hex, CSS variables from `design/tokens.json`). No React inside content scripts. Replace Recharts and any spreadsheet library with small purpose-built code (§5).
4. **The data model needs one rule the spec leaves open:** the append-only `applicationEvents` store is the source of truth; `applications.statusId` is a projection that can be rebuilt (§3).

Nothing in the spec is rejected outright. F27 (email and calendar OAuth) and F29 (AI) are correctly marked "D" and stay out of the local edition.

---

## 1. Feasibility and phase for F01 to F29

Legend. **Feasibility:** ✅ reliable locally · 🟡 feasible with limits or needs a spike · 🔴 needs an external service or a policy decision. **Spec priority** is the A to D column in the spec. **Phase** is our E1 to E4 (see `docs/16` §13).

| # | Feature | Spec | Feasibility | Phase | Notes and changes |
| --- | --- | --- | --- | --- | --- |
| F01 | Universal job capture | A | ✅ Tier A, 🟡 others | E1 | JSON-LD first, then adapter, then selected text, then manual. Unknown stays unknown. |
| F02 | Job snapshots and versions | A | ✅ | E1 | Plain text only, with content hash. Store text, not HTML. |
| F03 | Application CRM (table and Kanban) | A | ✅ | E1 | Table in E1, Kanban in E1 late or E2 (keyboard-accessible drag alternative required). Status change appends an event. |
| F04 | Duplicate detection | A | ✅ | E1 | Exact keys first, then weighted fuzzy suggestion (§4). Never auto-merge. |
| F05 | Browser filtering (hide, highlight) | A | 🟡 | **E2**, Tier A only | Needs per-site optional host permission and listing adapters. Not on LinkedIn, Indeed, Glassdoor. "Viewed" means locally observed only. |
| F06 | Backups and portability | A | ✅ | E1 | Versioned JSON, dry-run import, merge or replace, encrypted export, CSV with formula escaping. At-rest encryption later (§7). |
| F07 | Reminders and tasks | A | ✅ not while Chrome is closed | E1 | Alarms minimum is 30 seconds and alarms are not guaranteed to persist across restarts, so reconcile on every worker start ([Chromium extensions thread quoting the docs](https://groups.google.com/a/chromium.org/g/chromium-extensions/c/k5upFLVnPqE)). |
| F08 | Search and preferences | A | ✅ | E1 | MiniSearch. Unknown values visible by default. |
| F09 | Candidate profile | B | ✅ | E2 | Matches `cv.schema.json`. Demographic fields not stored by default. |
| F10 | CV parsing and keyword coverage | B | 🟡 | E2 | pdf.js in an extension page, DOCX as zipped XML. Scanned PDFs: manual text. Spike S3. |
| F11 | Rule-based relevance | B | ✅ | E2 | Spec weights adopted, with coverage rule (§4). |
| F12 | Advanced discovery filters | B | 🟡 | E2, Tier A only | Hide only on explicit user rules. Advertised and observed dates stored separately. |
| F13 | Repost and change detection | B | ✅ locally | E2 | Wording: "seen before by you". Never claim a global history. Simhash plus version diff. |
| F14 | Direct application finder | B | 🟡 | E2 | Extract links already on the page and from JSON-LD `url`/`hiringOrganization`. User verifies. Never construct URLs. |
| F15 | Documents and templates | B | ✅ | E2 (CV library, versions), E3 (letter templates) | Blobs optional (§7). |
| F16 | Recruiter CRM | B | ✅ | E3 | Contact data is personal data about third parties: privacy wording needed, export and delete included. |
| F17 | Interview centre | B | ✅ | E2 (rounds, ICS), E3 (prep, question bank, STAR) | ICS needs correct timezones; store IANA zone per interview. |
| F18 | Analytics | B | ✅ | E2 | Kaplan-Meier, shrinkage, Wilson intervals, denominators shown (`docs/16` §4B). |
| F19 | Daily briefing | B | ✅ | E2 | Deterministic, local, generated on open. |
| F20 | Offer comparison | B | ✅ | E3 | No automatic FX. Tax pack is separate (`docs/16` E3). |
| F21 | Application autofill | C | 🟡 fragile | E3 | Fill, never submit. Highest store-review scrutiny. Spikes S4 and S7. |
| F22 | Company research | C | ✅ notes only | E3 | Live third-party data is Connect or later. |
| F23 | Job risk flags | C | 🟡 | E2 | Shows signals, never "scam". Solicitor reviews wording. |
| F24 | Saved searches and discovery | C | ✅ save and open | E3 | "Feed checks while Chrome runs" is out of the local edition: it needs network access. |
| F25 | Skills and salary intelligence | C | ✅ own data | E3 | Counts and sample sizes shown. Ranges are not salaries. |
| F26 | Priority and time tracking | C | ✅ | E3 (priority), later (timer) | Timer is low value; keep behind the backlog. |
| F27 | Email and calendar integration | D | 🔴 | E4 (platform) | Local substitute: paste an email, rules classify it (E2). |
| F28 | Cloud sync and backup | D | 🔴 | E4 (Connect) | Independently opt-in. File export stays the free route. |
| F29 | AI assistance | D | 🔴 | E4 (AI edition) | Preview of data sent, grounding rules from `prompts/README.md`. |

---

## 2. Verified platform facts and what is still assumed

| Topic | Finding | Status |
| --- | --- | --- |
| Side panel | Needs the `sidePanel` permission, available from Chrome 114 ([API reference](https://developer.chrome.com/docs/extensions/reference/sidePanel)). `sidePanel.open()` arrived in Chrome 116 and works from a user gesture ([API reference](https://developer.chrome.com/docs/extensions/reference/sidePanel/?authuser=3)). `openPanelOnActionClick` defaults to false ([API reference](https://developer.chrome.com/docs/extensions/reference/sidePanel?authuser=7)). | [Verified] |
| Service worker lifetime | Chrome stops a worker after 30 seconds of inactivity, when a single request takes over 5 minutes, or when a `fetch()` response takes over 30 seconds. Events and extension API calls reset the idle timer ([lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle.md.txt)). Design for unexpected termination. | [Verified] |
| Alarms | Minimum 30 seconds from Chrome 120; persistence across restarts is not guaranteed ([thread](https://groups.google.com/a/chromium.org/g/chromium-extensions/c/k5upFLVnPqE)). | [Verified] second-hand; confirm on the alarms reference page |
| Suggested minimum Chrome | **120** (sidePanel.open at 116, alarms behaviour at 120). | Proposal |
| `unlimitedStorage` as an optional permission | Microsoft's Edge documentation shows it inside `optional_permissions` ([Edge docs](https://learn.microsoft.com/en-us/microsoft-edge/extensions-chromium/developer-guide/declare-permissions)); Chrome's own permissions page was not confirmed. | [Assumed] for Chrome: spike S10 |
| Framework | WXT's own comparison lists WXT as maintained, with Plasmo and CRXJS "partial" ([WXT compare](https://wxt.dev/guide/resources/compare)). One 2026 post puts Plasmo's last release in September 2025 with 347 open issues ([ExtensionBooster](https://extensionbooster.net/blog/plasmo-alternatives-chrome-extension-framework-migration-guide-2026/)). WXT's comparison page is the project's own, so treat it as a claim. | Choose WXT; check release activity at kickoff |
| Optional host permissions and dynamic content scripts | Spec relies on optional host permissions for per-site enhancement. Whether `scripting.registerContentScripts` after a runtime grant behaves as needed, and survives browser restart, was **not** checked. | [Assumed]: spike S11 |
| MV3 CSP for pdf.js and WASM | Not checked. | [Assumed]: spike S3 |
| Chrome Web Store: permission justification, Limited Use, single purpose | Not re-read for this review. | [Policy]: re-read before submission |

---

## 3. Data model reconciled

Keep the spec's stores. Add the rules below.

1. **Identifiers.** The spec says UUIDs; `docs/16` said ULIDs. Decision: **ULID strings everywhere** (sortable, 128-bit, convertible to UUID bytes). One scheme means the platform import and the extension agree. If the owner prefers UUIDv7, it is a drop-in change.
2. **Source of truth.** `applicationEvents` is append-only and authoritative. `applications.statusId`, `appliedAt` and `outcome` are projections. A test must rebuild all projections from events and match. Imports are idempotent on event id.
3. **Money.** Integer minor units plus ISO 4217 currency plus period (year, month, day, hour). No floats, no implicit FX.
4. **Dates.** Date-only values are `YYYY-MM-DD` strings. Instants are ISO 8601 UTC. Interviews also store an IANA timezone name.
5. **Provenance.** Every captured field stores source (adapter, JSON-LD, selection, manual), confidence and time (spec section 5).
6. **Extra stores beyond the spec's 21:** `settings`, `dataPacks` (bundled data version and date), `importLog`, `backupMeta`, `schemaMeta`. Documents split into `documents` (metadata and extracted text) and `documentBlobs` (optional, may be disabled).
7. **Statuses.** Use the spec's 14 defaults. Custom stages map to a fixed set of reporting groups (`saved`, `applied`, `in_process`, `offer`, `closed_positive`, `closed_negative`, `withdrawn`). Analytics read only reporting groups.
8. **Merge.** Merging two jobs moves sources, snapshots, notes and applications to the survivor and writes a `merge` event; an unmerge is possible while the event exists.
9. **Platform tables.** `docs/04-data-model.md` keeps prose only for extension stores (rows beginning with a backticked name are parsed as database tables by the privacy test).

Message contract (content script to worker), all validated with Zod and sender checks (`sender.id`, origin, tab):

| Message | Direction | Returns |
| --- | --- | --- |
| `CAPTURE_JOB` | worker → content (on user action) | `JobDraft` with provenance |
| `SAVE_JOB` | page UI → worker | saved job id, duplicate candidates |
| `QUERY_LISTING_STATUS` | content → worker | per-listing flags only (saved, applied, hidden-by-rule), never full records |
| `GET_FILTER_RULES` | content → worker | enabled rules for the current origin only |
| `FILL_APPROVED_FIELDS` | page UI → content | list of field ids and values the user approved |

No message returns a whole record to a content script. No generic "query database" message exists.

---

## 4. Algorithms: merged

**Duplicates.** Order of checks: (1) adapter source ID or employer requisition ID, (2) canonical URL, (3) candidate generation by 64-bit simhash and an inverted index on normalised company and title (avoids quadratic scans), (4) the spec's weighted score on candidates: company 30, title 25, description 25, location 10, reference 10. Thresholds are **uncalibrated**: start with strong suggestion at 0.85 and weak suggestion at 0.65, calibrate on at least 100 labelled pairs from fixtures before the numbers are shown to users. Conflicting requisition IDs block any suggestion.

**Relevance.** Spec weights (skills 40, experience 20, role 15, location 10, salary 10, work mode 5). Score is the weighted sum of known criteria divided by the known weight; coverage is known weight divided by enabled weight. Proposal: if coverage is under 50% the headline shows "not enough information" and lists what is missing. Hard exclusions are flags, not score penalties. Keyword coverage from the CV (F10) is displayed separately and labelled as a review prompt, not as an employer ATS score.

**Everything else** (JD parser, BM25, Kaplan-Meier, beta-binomial, Wilson, salary regex, sponsor fuzzy match, suspicious signals) is unchanged from `docs/16` §4.

---

## 5. Architecture and dependency audit

Repository: keep the monorepo (`packages/core`, `data`, `storage`, `adapters`, `ui`, plus `extension/`). Adopt the spec's feature names as folders inside `core` (`capture`, `tracker`, `filters`, `match`, `documents`, `contacts`, `interviews`, `tasks`, `analytics`, `offers`, `autofill`, `backup`). Reason: `core` must run in the platform and in tests with no browser APIs. The spec's `repositories` become the `Storage` port.

Interfaces: `SiteAdapter` is adopted. `extractJob(document, url)` takes a document so it can run against saved fixtures in tests. `MatchingProvider` is adopted but its default implementation is synchronous and pure; the async signature exists for later providers.

Licences below are from memory and **must be confirmed** with a licence checker in CI before first release.

| Dependency | Verdict | Reason or alternative |
| --- | --- | --- |
| WXT | Use | Maintained build tool; pin version. |
| TypeScript, Vite, Vitest, Playwright | Use | Playwright extension tests need a persistent Chromium context: spike S12. |
| React (extension pages only) | Use | Shares components with the platform. Not in content scripts. |
| Tailwind | **Drop** | Conflicts with the token system. CSS Modules instead. |
| Dexie | Use | Migrations and live queries. |
| Zod | Use | Boundary validation. |
| MiniSearch | Use | Search; skip Fuse.js (two search libraries is one too many). |
| pdf.js | Use, lazy-loaded | Largest dependency. Worker file bundled locally. Spike S3 covers CSP. |
| Mammoth | Optional | Our own zipped-XML read with `fflate` is smaller; decide at spike S3. |
| Papa Parse | Optional | CSV is simple enough to write and fuzz-test ourselves. |
| Recharts | **Drop** | Heavy. Small SVG charts, accessible with a data table alternative. |
| dnd-kit | Optional | Needs keyboard-accessible reordering; a "move to" menu is the baseline. |
| Spreadsheet export (SheetJS and similar) | **Drop** | CSV and JSON only. |
| pdf-lib, docx, fflate | Use in E2 | CV export. |

---

## 6. Permissions per release

| Release | `permissions` | Host access |
| --- | --- | --- |
| E1 alpha | `storage`, `activeTab`, `scripting`, `sidePanel`, `alarms`, `notifications` | None at install. Capture on a toolbar click through `activeTab`. |
| E1 optional | `unlimitedStorage` (as optional, if S10 passes) | none |
| E2 | same | `optional_host_permissions` for the Tier A origins the user enables, one origin at a time, for auto-detect and filtering |
| E3 | same | adds ATS origins for autofill, each explained and optional |
| E4 Connect | same | optional host permission for the Hearback API origin only |

Never: `tabs`, `webRequest`, `cookies`, `history`, `<all_urls>` at install. No `externally_connectable` by default.

---

## 7. Encryption and backup order

1. E1: encrypted export (PBKDF2 and AES-GCM through Web Crypto, per-file random salt and IV, versioned header). Plain JSON export stays available with a warning.
2. E1: backup reminder every 30 days without an export.
3. Later (separate decision): at-rest encryption. It affects search indexes, worker restarts and lock UX, and does not protect against malware or an unlocked browser. Not required at launch. This answers the spec's open decision: **encrypted backups at launch, at-rest encryption not promised**.

---

## 8. Ranked risks

| # | Risk | Likelihood | Impact | Mitigation | Verified by |
| --- | --- | --- | --- | --- | --- |
| R1 | A site's terms or a store reviewer treats page modification or reading as prohibited | Medium | High | Tier model, no restricted-site content scripts, per-site terms record, solicitor review | Terms log in `docs/10`; store dry-run |
| R2 | Data loss on uninstall, profile loss or storage eviction | Medium | High | Backup reminder, encrypted export, S5 persistence check, optional folder backup (S9) | S1, S5, S9, import tests |
| R3 | Worker termination corrupts a multi-step write | Medium | High | Dexie transactions, idempotent writes, no globals | S1: 1,000 forced restarts |
| R4 | Store rejects broad permissions or weak justification | Medium | High | Minimal install permissions, optional hosts, written justification per permission | Pre-submission review |
| R5 | Dependency or maintainer account compromise | Low | Very high | Pinned lockfile, audit in CI, 2FA on the developer account, reproducible build | CI and release checklist |
| R6 | Adapter breakage when a site changes | High | Medium | Fixtures, JSON-LD first, manual fallback always visible, weekly fixture re-check | Fixture suite |
| R7 | Autofill fills wrongly or touches sensitive fields | Medium | High | Preview, per-field confidence, skip list, never submit | Fixtures per ATS |
| R8 | Match and risk scores read as verdicts | Medium | Medium | Coverage rule, reasons, wording rules in `docs/14` | Copy review |
| R9 | Spec scope exceeds a solo founder alongside platform and marketing | High | High | Phase gates; F26, F22, F24 and F16 at the back; launch on E2 core | Phase exit gates |
| R10 | Malicious job page injects markup or spoofs messages | Low | High | Text rendering only, sender and origin checks, narrow messages | Security tests |
| R11 | Name or trademark conflict | Medium | Medium | Hearback name decision (#22) before store listing | Search and IP check |
| R12 | Benchmark contribution breaks local-only promise | Low | High | Website upload route only (#30) | Network audit in CI |

---

## 9. Backlog (E1 first), user stories and estimates

Estimates are ideal days for one developer with Claude Code, unvalidated.

| Epic | Story | Acceptance test | Days |
| --- | --- | --- | --- |
| Foundations | As a developer I can build, load and test the extension from a clean checkout | `make` targets or scripts build; Playwright loads the extension | 3 |
| Foundations | CI network audit, permission diff, bundle budget | A fixture build that adds `fetch` fails CI | 2 |
| Storage | Schema v1 with migrations and projections rebuilt from events | Rebuild test passes; migration fixture passes | 4 |
| Capture | Save a job from a JSON-LD page via toolbar click | Fixture with valid and malformed JSON-LD | 3 |
| Capture | Greenhouse and Lever adapters, then Ashby and Workable | One fixture set per site | 5 |
| Capture | Manual and paste capture on any site | Works on a restricted-site tab with only URL and title | 2 |
| Tracker | Table, detail page, status events, notes, tags | Status change appends an event | 5 |
| Tracker | Kanban with keyboard alternative | axe and keyboard test | 3 |
| Dedupe | Exact keys, simhash candidates, merge dialog | Labelled pair fixtures | 4 |
| Reminders | Tasks, alarms, startup reconcile, badge | S6 passes | 3 |
| Backup | Versioned JSON export and import with dry-run, encrypted export, CSV | Corrupt and oversized file tests | 5 |
| Insight | Stage odds and "Should I move?" from the packs | Matches platform core outputs | 3 |
| UX | Side panel and popup, empty states, permission explainer | Design signed off | 6 |
| Release | Listing, privacy policy, reviewer notes | Dry-run checklist | 3 |

Total for E1: about 51 ideal days, which is roughly 10 to 13 calendar weeks at part-time pace. **That is longer than the E1 window in `docs/16` (Dec to late Jan).** The calendar in §11 moves accordingly.

---

## 10. First vertical slice (for approval, not started)

**Goal:** on a Greenhouse or JSON-LD job page, click the toolbar icon, review extracted fields, save, see it in the side panel list, export it, and re-import it with a dry-run, with the network audit green.

**Manifest shape (proposed):** MV3; `minimum_chrome_version` "120"; permissions `storage`, `activeTab`, `scripting`, `sidePanel`; `side_panel.default_path`; an `action`; no `host_permissions`; no static content scripts; default extension-page CSP.

**Commands (to run only after approval; names may differ by version):**

- Scaffold with the WXT initialiser using the React template, inside `extension/`.
- Install Dexie, Zod and MiniSearch in `packages/storage` and `packages/core`.
- Add scripts for `dev`, `build`, `test`, `lint`, and an `audit:network` script that scans the built bundle for network APIs.
- Run Playwright with a persistent Chromium context and the built extension loaded.

**Slice acceptance:** (1) saves from three fixture pages, (2) kills the worker mid-save and loses nothing, (3) export then import into an empty profile gives an identical event log, (4) restricted-site tab saves from URL, title and pasted text only, (5) axe has no serious issues on the side panel, (6) the bundle contains no network calls.

---

## 11. Timeline reconciliation

The spec's phases total roughly 12 to 22 weeks for a solo developer. Our E0 to E2 plus public v1.0 was 24 weeks including approvals and store review, which agrees once spikes are counted. The E1 backlog above shows E1 alone is likely 10 to 13 weeks, so the public v1.0 target moves from "late April to May 2027" to **"May to June 2027"**, subject to the owner re-baselining after E1. The platform launch date of 13 September 2027 remains an internal, at-risk target (decision #27).

---

## 12. Documentation and policy checks still to do (nothing here was checked live unless a link is given above)

1. Chrome: `permissions` and `optional_permissions` page for `unlimitedStorage`; `scripting.registerContentScripts` persistence; `alarms` reference; `storage` quotas; offscreen documents; default extension CSP and WASM; `sidePanel` behaviour on other Chromium browsers.
2. Chrome Web Store: single purpose, user data policy and Limited Use, permission justification, review times, account verification and trader status in the EU.
3. Terms to read in full: LinkedIn, Indeed, Glassdoor, IrishJobs.ie, Jobs.ie, Reed, publicjobs.ie, and each Tier A ATS vendor.
4. Data: UK Register of Licensed Sponsors and Irish critical skills list licence and update cadence.
5. Law: GDPR position for a local-only extension (we hold no data), then for Connect and contributions; ePrivacy; solicitor review of the scam-signal wording.
6. Competitor claims in the original discussion: not audited.

---

## 13. New owner decisions

See `decisions-needed.md` #31 to #36: at-rest encryption timing, document blobs, minimum Chrome version, monetisation, open-source licence, filtering scope.
