# Build prompt: free local Chrome extension (for the extension build factory)

Paste everything below the line into the factory. Fill in the three brand values first.

---

## 0. Brand values (fill in; do not hard-code anywhere else)

- BRAND_NAME: `<e.g. MyWorkspacePal, or the final platform name>`
- STORE_TITLE: `<BRAND_NAME>: Job Application Tracker and CV Check` (max 75 characters)
- PLATFORM_DOMAIN: `<e.g. myworkspacepal.com>`

"JobPilot" is only an internal codename for the concept. It must not appear in the manifest, UI strings, store listing, package names or documentation. All brand strings live in one file, `packages/core/src/brand.ts`, and in the extension's i18n messages, so a rename is a one-file change. A test fails if the string "JobPilot" appears in any shipped file.

## 1. Role

You are building the free-for-life, local-only Chrome extension that is the first product of the platform at PLATFORM_DOMAIN. It is the front door to the platform: useful on day one with no account, no server and no AI, and it lets the user take their data to the platform later by choice. You work in the existing repository. You do not redesign the plan; you implement it in small, tested, reviewable steps.

## 2. Read first, in this order, before writing anything

1. `CLAUDE.md` (all of it, especially the non-negotiable rules and extension rules E1 to E11)
2. `docs/17-jobpilot-spec-review.md` (takes precedence over docs/16 where they differ)
3. `docs/16-chrome-extension.md`
4. `docs/adr/0007-*` and `docs/adr/0008-*`
5. `docs/02-build-stages.md` (Track E), `docs/STATUS.md`, `docs/decisions-needed.md`
6. `docs/06-security.md` section 13, `docs/13-privacy-and-compliance.md` section 16
7. `extension/README.md`, `packages/README.md`

If any file is missing or contradicts another, stop and report; do not guess. The repository may use an older working name (Offerlight or Hearback) in places; follow the brand values above for anything user-facing and do not rename old docs unless asked.

## 3. Mission and product rules

Build a local-first job application tracker with job capture, honest insight, CV tools and backup, as specified in docs/17 section 1 (features F01 to F29, phased E1 to E4). Local edition means:

- No network requests of any kind. No analytics, no telemetry, no fonts or images from a CDN, no remote code.
- No accounts, no backend, no cloud storage, no AI. All data stays in the browser on the device.
- Never submit anything for the user. Never auto-apply.
- Never invent experience or fill special-category fields (health, ethnicity, religion, and similar).
- Every score shows its reasons, data source and confidence, and has a waiting state when data is thin.
- Never claim a vacancy is a "scam" or a "ghost job"; show signals and let the user decide.
- No LinkedIn, Indeed or Glassdoor content scripts, DOM reading, UI injection or hide/highlight. On those sites the user clicks the toolbar icon and the extension uses only the tab URL and title plus text the user types or pastes.
- In-page hide or highlight is E2 and only on Tier A sites the user enables one origin at a time.
- Anything free that runs on the device stays free; never design a paywall into the local edition.

## 4. Scope of this run

Work only on **Phase E1 (tracker core)**, in this order. Stop at each checkpoint and report before continuing.

**Checkpoint A: first vertical slice** (docs/17 section 10). On a Greenhouse page or any page with `JobPosting` JSON-LD: click the toolbar icon, review extracted fields, save, see it in the side panel list, export JSON, re-import with a dry run, and a CI network audit passes. Acceptance: (1) saves from three fixture pages; (2) killing the service worker mid-save loses nothing; (3) export then import into an empty profile reproduces an identical event log; (4) a tab on a restricted site saves from URL, title and pasted text only; (5) axe finds no serious issues in the side panel; (6) the built bundle contains no network calls.

**Checkpoint B: E1 backlog** (docs/17 section 9) in this order: foundations and CI gates, storage schema v1 with migrations and projections rebuilt from events, capture adapters (JSON-LD, Greenhouse, Lever, then Ashby and Workable), manual and paste capture, tracker table and detail, status events, Kanban with a keyboard alternative, duplicate detection, reminders and tasks, backup and CSV, stage odds, UX polish, release pack.

Do not start E2 or later features (filtering, CV import, matching, autofill, interview centre, recruiter CRM, analytics beyond stage odds).

## 5. Technical decisions (fixed; change only through an ADR and the owner)

- Monorepo: `packages/core` (pure TypeScript, no `chrome`, `window` or `document`, lint-enforced), `packages/storage`, `packages/adapters`, `packages/ui`, `extension/`. Feature folders inside `core` as in docs/17 section 5.
- WXT, TypeScript strict, React in extension pages only, CSS Modules with variables from `design/tokens.json` (no raw hex, no Tailwind), Radix primitives for dialogs, tabs, menus and switches. Injected UI (when it exists) uses Shadow DOM and vanilla or Preact, with no React.
- Dexie (IndexedDB), Zod at every boundary (storage, messages, import), MiniSearch for search. Vitest and Playwright. Add no dependency that docs/17 section 5 marks as dropped (Tailwind, Recharts, spreadsheet libraries). Each new dependency needs a one-line justification, a pinned version and a licence check in CI.
- Data model: docs/17 section 3. ULID ids; append-only `applicationEvents` are the source of truth and application status is a projection that a test rebuilds from events; money as integer minor units plus currency plus period; date-only values as `YYYY-MM-DD`; instants as ISO UTC; automatic pre-upgrade snapshot; idempotent import by event id.
- Messages (content script to worker): `CAPTURE_JOB`, `SAVE_JOB`, `QUERY_LISTING_STATUS`, `GET_FILTER_RULES`, `FILL_APPROVED_FIELDS` as Zod-validated, versioned unions. Validate sender, origin and tab. No message returns a whole record and there is no generic database message.
- Service worker is ephemeral: register listeners synchronously, keep no state in globals, make writes idempotent, wrap multi-record changes in Dexie transactions, reconcile alarms on every start.
- Permissions for E1: `storage`, `activeTab`, `scripting`, `sidePanel`, `alarms`, `notifications`. No host permissions at install. No `tabs`, `webRequest`, `cookies`, `history`, `<all_urls>`, `externally_connectable`. `unlimitedStorage` only as an optional permission and only if spike S10 passes. Minimum Chrome version 120 unless the owner decides otherwise (decision #33).
- Render captured text as text. No `eval`, no remote scripts, no `innerHTML` with captured content, safe URL schemes only, size caps on imports.
- Backups: versioned JSON with checksum, dry-run import with merge or replace, passphrase-encrypted export (Web Crypto: PBKDF2 and AES-GCM, random salt and IV per file), CSV with spreadsheet-formula escaping, a 30-day backup reminder, a "what is stored" screen and delete-everything.

## 6. Gates that must exist in CI before feature work continues

1. Network audit: the built bundle is scanned for `fetch`, `XMLHttpRequest`, `WebSocket`, `sendBeacon`, `EventSource`, remote `import()` and external URLs in scripts. A deliberate test fixture proves it fails when it should.
2. Permission diff: CI fails if the built manifest differs from the approved list.
3. Offline Playwright run with the network blocked.
4. Bundle size budgets, set after the first slice and recorded in the repo.
5. `core` purity lint, licence check, dependency audit, reproducible build.
6. axe checks and keyboard tests on every new screen; WCAG 2.2 AA; 44 px targets; focus visible; meaning never by colour alone.
7. Brand test: the string "JobPilot" is absent from shipped files.

## 7. Working method

- Follow the repository's rules: branch per task named `stage-E1/<short-description>`, small commits in Conventional Commits style, one pull request per task using `.github/pull_request_template.md`, never commit to `main`, never commit secrets. If the folder is not a git repository, say so and ask before running `git init`.
- Use the task list. Write tests with the code. Update the relevant doc when behaviour changes.
- Use saved HTML fixtures for every adapter (synthetic or properly permitted, redacted). Each adapter must offer a manual-capture fallback in the UI when extraction fails.
- Treat every claim about Chrome behaviour as unverified until you have read the current documentation or tested it. Record results in `docs/17` section 12 as "verified (link, date)" or "tested (spike id)". Never invent documentation citations.
- Run the spikes S1, S2, S5, S6, S10, S11 and S12 early, and report results before building features that depend on them.

## 8. Stop and ask the owner when

- a task needs an answer to decisions #22 (name), #23, #24, #26, #27 or #31 to #36 and the default in `docs/decisions-needed.md` is not acceptable to you;
- a spike fails or a Chrome behaviour contradicts the docs;
- you want a new permission, a new dependency, a network call, or to read or modify a page on any site not in Tier A;
- anything would change what a user's stored data means, add personal-data collection of any kind, or touch the store listing wording;
- something conflicts with CLAUDE.md rules 1 to 12 or E1 to E11.

## 9. Report format at each checkpoint

One short section each: what was built; acceptance results with evidence (test names, CI links); spike results; permissions and dependencies added; open questions; what you need from the owner. No code walk-throughs, no recap of steps.

Do not generate a full codebase in one pass. Start with Checkpoint A.
