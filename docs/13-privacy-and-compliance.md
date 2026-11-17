# 13 · Privacy and compliance (GDPR by design)

> Engineering specification, not legal advice. The owners must have it reviewed by a
> solicitor and/or DPO before launch (`decisions-needed.md` #7, #15–#18).

Privacy is built in from Stage 0 and **enforced by code and CI**, not by memory. Where this
document and the data inventory disagree, the inventory wins and this document is fixed.

## 1. How it works — one source of truth

```
backend/app/privacy/
├── data_inventory.toml   ← every table, column, cache key, processor: purpose, basis, retention, erasure
├── registry.py           ← loads and validates it (rejects anything ambiguous or unlawful)
├── plans.py              ← generates the retention, erasure and export plans from it
├── consent.py            ← consent rules, versions, guards
├── redaction.py          ← personal-data detection; used for logs, Sentry and shared text
├── ai_guard.py           ← minimisation before every AI call
├── deadlines.py          ← one-month DSAR, 30-day erasure, 72-hour breach clocks
├── model_check.py        ← SQLAlchemy models vs inventory (FK ON DELETE, encryption, PII names)
└── ropa.py               ← generates docs/privacy/records-of-processing.md
backend/app/workers/privacy_tasks.py   ← nightly retention + erasure jobs
docs/privacy/                          ← ROPA (generated), LIAs, DPIAs, runbooks, notice outline
content/consents/                      ← exact consent wording, versioned and hash-locked
```

**What CI enforces** (`backend/tests/privacy/`, run by `make test` and `make privacy-check`):

| Check | Fails when |
| --- | --- |
| Inventory valid | A category lacks purpose, lawful basis, retention or erasure rule; consent basis without a consent kind; legitimate interests without an LIA; legal obligation without a legal reference; special category data without explicit consent, DPIA, `sensitive` schema and encryption; profiling without a DPIA; a processor outside the EEA without a transfer mechanism; a cache TTL longer than the erasure deadline; minimum age below 16 |
| Docs ↔ inventory | A table in `04-data-model.md` is not in the inventory, or vice versa |
| Models ↔ inventory | A model table is not classified; a declared column does not exist; FK `ON DELETE` does not match erasure (`CASCADE` for delete, `SET NULL` for anonymise/pseudonymise); a declared encrypted column is not encrypted; a column that looks personal sits in a `not_personal` table |
| Plans complete | A table with fixed retention has no retention action; a personal table is missing from erasure or export |
| ROPA current | `docs/privacy/records-of-processing.md` differs from what the inventory generates |
| Consent wording | A consent kind has no wording file, or its wording changed without a version bump |
| LIA/DPIA exist | A referenced assessment file is missing |
| Logs and AI | Personal data reaches a log line, a Sentry event, or AI input in tests |

## 2. Roles and regulators

| | |
| --- | --- |
| Controller | Offerlight (company to be incorporated in Ireland — decision #15) |
| Lead supervisory authority | Data Protection Commission (DPC), Ireland (one-stop shop) |
| UK | UK GDPR + DPA 2018, ICO. A UK representative is needed if there is no UK establishment (UK GDPR Art 27) — decision #16 |
| DPO | Recommended (large-scale profiling of job seekers may make it mandatory, Art 37(1)(b)) — decision #17 |
| Processors | Listed in the inventory with location, transfer mechanism and DPA status. No processor may receive data before its DPA is signed |

Other law in scope: ePrivacy (S.I. 336/2011; PECR in the UK) for cookies and marketing
email; EU AI Act (transparency for AI-generated text; no emotion recognition; employment
classification to assess — decision #18); European Accessibility Act; consumer law;
defamation (scam reports and badges).

## 3. The principles, and exactly how each is met

| Principle (Art 5) | Rule in this codebase |
| --- | --- |
| Lawfulness, fairness, transparency | One lawful basis per category, declared in the inventory; layered plain-language privacy notice generated from the same facts; Art 14 notice for employer contacts and recruiters |
| Purpose limitation | Purposes are listed per category. Data is not used for a new purpose without updating the inventory, the notice and, where needed, asking consent. **Never sold, never used for ads, never shown to employers** |
| Data minimisation | Only fields in `04-data-model.md`. No date of birth (age is self-declared 16+), no photo, no gender or nationality outside the opt-in fairness audit. Contact details never sent to AI. Raw IPs never stored (keyed hash) |
| Accuracy | Everything the user gave is editable; scores recalculate from corrected data |
| Storage limitation | Every category has a number of days or a defined event. Nothing is kept "indefinitely". The nightly job enforces it |
| Integrity and confidentiality | `docs/06-security.md`; application-level encryption for email bodies and special category data; encrypted backups |
| Accountability | Generated ROPA, audit log, rights-request register, breach register, LIAs, DPIAs, PR privacy checklist |

## 4. Lawful bases — the rule for choosing

- **Contract** for anything the user signed up for and that the service cannot work without
  (account, CVs, tracker, matching, the daily digest).
- **Consent** only where the user has a free, real choice and the feature works without it:
  benchmarks, experiments, voice practice, product news, question bank, fairness audit
  (explicit consent, Art 9(2)(a)).
- **Legitimate interests** for security, operations, employer contacts in captured replies,
  and job ads — each with an LIA in `docs/privacy/lia/`.
- **Legal obligation** for consent proof, tax records, the rights-request and breach
  registers, and erasure tombstones.

Consent is never used as a "belt and braces" second basis, and contract is never used for
something optional.

## 5. Consent

- Every switch starts **off**. Nothing is pre-ticked or bundled with the terms.
- Wording lives in `content/consents/<kind>.v<n>.md`, shown verbatim, hash-locked. The SHA-256
  of the wording is stored with each record.
- A consent is valid only if the user's latest record grants the **current** version
  (`consent.current_state`). A meaning change bumps the version and the user is asked again.
- Withdrawal is one tap on the same screen (or one click in an email) and takes effect
  immediately: guards (`consent.require`) run before every consent-based process.
- Records are append-only (DB trigger blocks UPDATE except erasure pseudonymisation).
- Terms acceptance, privacy-notice version shown and the 16+ declaration are recorded as
  **acknowledgements**, not consents.

## 6. Retention (generated, enforced nightly)

The full table, generated from the inventory, is in `docs/privacy/records-of-processing.md`.
The key numbers:

| Data | Kept |
| --- | --- |
| Account, CVs, tracker, stories, preferences | While the account exists; erased within 30 days of deletion |
| Sessions | 90 days |
| One-time codes, challenges, rate-limit keys | ≤ 1 hour (Redis TTL) |
| Security audit log | 12 months; anonymised on account deletion |
| Captured employer emails: body, sender, subject, raw file | 90 days (metadata kept) |
| Practice audio | Deleted after transcription; 24 hours at most |
| Practice transcripts | 30 days unless the user ticks "Keep" |
| Daily matches | 180 days |
| Raw job API payloads / job ads | 30 days / 365 days after last seen |
| AI usage records (no text) | 400 days |
| Billing records | 6 years after the subscription ends (tax law) |
| Consent records | Life of account + 6 years, pseudonymised after deletion |
| Rights requests | 3 years after closure |
| Erasure tombstones | 60 days (longer than backups) |
| Backups | 30 days |
| Application logs | 30 days |

## 7. Rights

Self-service in Settings → Privacy, with manual handling for everything else. Full
procedure: `docs/privacy/rights-requests-runbook.md`.

| Right | How | Deadline |
| --- | --- | --- |
| Access / portability | Download my data → ZIP from `export_plan()` with a README explaining each file | Ready in 24 h (legal: 1 month) |
| Erasure | Delete my account (step-up) → locked at once → nightly erasure plan → confirmation email | ≤ 30 days (normally next night) |
| Rectification | Edit anywhere | Immediate |
| Restriction | Email → account locked, processing paused | 1 month |
| Objection / withdraw consent | Switches, unsubscribe links | Immediate |
| Automated decisions (Art 22) | None with legal or similarly significant effect; every score explained ("How we calculate this") | — |
| Complaint | Privacy notice names the DPC and ICO | — |

## 8. Erasure — what "deleted" means here

Generated by `erasure_plan()`, in this order, in one transaction per user:

1. Collect object-storage keys (CV files, raw emails, audio) and delete the objects.
2. **Pseudonymise** rows kept for a legal obligation (consents, billing, rights requests):
   user link replaced by `subject_ref`, a keyed hash (`PRIVACY_PSEUDONYM_KEY`).
3. **Anonymise** rows kept for security statistics (audit log, AI usage, scam reports):
   user link set to NULL.
4. **Delete** everything else; child tables go by `ON DELETE CASCADE` (checked in CI).
5. Delete the user row; write a tombstone; audit-log the counts (no personal data).

Backups: kept 30 days, then gone. After any restore, tombstones are re-applied before the
service reopens (`docs/privacy/backup-and-restore.md`). Aggregates already published (k ≥ 10)
are not personal data and are not recalculated.

## 9. Sharing and transfers

- Only processors in the inventory, only from their stage, only after the DPA is signed.
- EU hosting for all primary stores. Transfers outside the EEA are listed with their
  mechanism (EU-US Data Privacy Framework where the recipient is certified, otherwise
  SCCs + transfer impact assessment).
- AI provider: contact block, links and anything matching personal-data patterns removed
  before every call (`ai_guard`); no CV is sent unless the user clicks an AI action.
- Organisations (Stage 12) see aggregates with k ≥ 10 only — never an individual's data.

## 10. Special category and sensitive data

- Only in the opt-in fairness audit (explicit consent): separate `sensitive` schema, separate
  DB role, column encryption, never joined in product code, deleted on withdrawal.
- Visa/permit status is optional, high sensitivity (can indicate nationality), never used in
  ranking, only to show sponsor information on request.
- CVs may reveal special category data the user chose to include (for example a disability
  charity role). We do not extract, infer or use it; the CV builder's age-neutral and
  photo-free defaults reduce it.

## 11. Children

Minimum age 16 (Ireland's digital age of consent; also satisfies the UK's 13). Self-declared
at sign-up; no date of birth collected. Accounts found to belong to under-16s are erased.

## 12. Cookies and tracking

Strictly necessary cookies only (`__Host-` session, CSRF). No consent banner is needed for
these. Analytics are cookieless and aggregate (Plausible EU or self-hosted Umami). **No
third-party trackers, pixels, fingerprinting or session replay** — CSP blocks them.

**Free self-checks** (CV check text, LinkedIn check, "Should I move?") follow the same rule:
answers are processed in the browser or in memory and not stored. "Should I move?" sends
nothing at all; analytics record only that a check was completed and its verdict category.

## 13. Breaches

`docs/privacy/breach-runbook.md`: contain → assess → notify the DPC (and ICO for UK users)
within 72 hours of awareness when there is a risk → tell people without undue delay when
there is a high risk → record every breach in `privacy_incidents`, notified or not.

## 14. Privacy in the build process

- **Definition of done** (CLAUDE.md) includes the privacy checks and the PR privacy checklist
  (`docs/privacy/pr-privacy-checklist.md`).
- Every stage lists its privacy gate in `02-build-stages.md`; a feature that relies on a
  DPIA ships behind a feature flag that stays off until the DPIA is signed.
- Claude Code must **stop and ask** before changing a lawful basis, a retention period, a
  consent wording, a processor, or anything in the inventory that affects data already
  collected.
- Test data is synthetic. Real CVs for the golden set (decision #10) need written consent,
  are anonymised, and never enter CI logs.

## 15. Documents the owners must complete before launch

| Document | Where | Before |
| --- | --- | --- |
| Records of processing | Generated: `docs/privacy/records-of-processing.md` | Stage 1 (keep current) |
| LIAs 0001–0004 | `docs/privacy/lia/` | Stage of each feature |
| DPIAs 0001–0003 | `docs/privacy/dpia/` | Stage 6, 10, 11 launches |
| Privacy notice | Outline: `docs/privacy/privacy-notice-outline.md` | A beta version before private beta wave 1 (real people's data); the final version before the launch gate |
| DPAs with every processor | Inventory lists them | Before first use |
| Transfer impact assessments | For US processors | Before first use |
| Breach and rights runbooks | `docs/privacy/` | Stage 1 |
| Terms, accessibility statement, right-of-reply process | Legal | Beta terms before wave 1; full set before the launch gate |

## 16. Extension and Connect (Track E)

Engineering note, not legal advice. Solicitor to confirm.

- **Local edition:** no data is transmitted to Hearback, so the data stays on the user's device and is
  not in `data_inventory.toml`. The website, waitlist and accounts stay under this framework. The
  store listing and website need an accurate privacy policy and store data-handling declarations
  that say exactly this. The solicitor confirms the controller position for locally processed data.
- **Free-text and documents** the user stores locally (CVs, notes) may include sensitive details;
  the extension never asks for special category data and never autofills such fields (rule E6).
- **Connect and uploads:** the user chooses to send data; import is consent-based (Art 6(1)(a) or
  contract, to be decided with the solicitor); benchmark contribution has its own consent, recorded on
  the website; anonymised at source by dropping free text and personal fields; erasure removes
  imported events and derived rows. New tables go into the inventory before code (see `docs/04`).
- **Chrome Web Store Limited Use** applies to raw, aggregated and derived data: transmit only what
  the disclosed single purpose needs, with disclosure and consent. Re-read the policy before Phase E4.
- **No telemetry in the local edition.** Measurement uses store statistics, tagged links the user
  chooses to open, and the website's cookieless analytics.
- **Permissions** are listed and justified in `docs/16` §10 and must match the store listing; a
  permission change needs this section updated in the same pull request.
