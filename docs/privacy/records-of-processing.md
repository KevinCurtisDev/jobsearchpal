# Record of Processing Activities (GDPR Art 30)

> **Generated** from `backend/app/privacy/data_inventory.toml` by `make privacy-docs`.
> Do not edit by hand. Engineering record only, not legal advice.

Inventory last reviewed: 2026-10-20

## Controller

| | |
| --- | --- |
| Controller | TBC — company to be incorporated (decisions-needed #15) |
| Establishment | Ireland |
| Lead supervisory authority | Data Protection Commission (Ireland) |
| UK regulator | Information Commissioner's Office |
| UK representative (UK GDPR Art 27) | TBC (decisions-needed #16) |
| Data protection officer | TBC (decisions-needed #17) |
| Privacy contact | privacy@<domain> |
| Minimum age | 16 (self-declared) |

## Processing activities

### Account identity (`account_identity`)

| | |
| --- | --- |
| Description | Email address, display name, locale, country, account status, plan |
| Purposes | Create and run the user's account; Sign-in by email code; Service emails |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `users`, `export:<user_id>.zip (object storage)` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Amazon Web Services EMEA SARL (Amazon SES) (eu-west-1 (Ireland)) |
| Transfers outside the EEA | Amazon Web Services EMEA SARL (Amazon SES): Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Passkeys and sign-in credentials (`authentication`)

| | |
| --- | --- |
| Description | WebAuthn public keys, credential ids, sign counts, authenticator metadata, nicknames |
| Purposes | Passwordless sign-in |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `passkey_credentials` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Sessions and devices (`sessions`)

| | |
| --- | --- |
| Description | Session token hashes, device label, user agent, keyed IP hash, last seen |
| Purposes | Keep users signed in; Show and revoke devices; Detect account takeover |
| Data subjects | users |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0001-security-and-fraud-prevention.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `sessions` |
| Retention | 90 days |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Upstash, Inc. (EU region (eu-west-1 or eu-central-1)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | Upstash, Inc.: US parent company: EU-US Data Privacy Framework if certified at signing, otherwise Standard Contractual Clauses + transfer impact assessment. Data stored in an EU region. |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### One-time codes, magic links, WebAuthn challenges, rate-limit counters (`transient_auth`)

| | |
| --- | --- |
| Description | Hashed codes and tokens, keyed hashes of email/IP in rate-limit keys |
| Purposes | Verify email ownership; Prevent brute force and bot sign-ups |
| Data subjects | users, people attempting sign up |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0001-security-and-fraud-prevention.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `auth:code:<hmac(email)>`, `auth:magic:<sha256(token)>`, `webauthn:challenge:<random>`, `rl:<scope>:<hmac(ip\|email)>` |
| Retention | At most 3600 seconds |
| On erasure | delete |
| Included in export | No — Exists for at most one hour and holds only hashes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Upstash, Inc. (EU region (eu-west-1 or eu-central-1)) |
| Transfers outside the EEA | Upstash, Inc.: US parent company: EU-US Data Privacy Framework if certified at signing, otherwise Standard Contractual Clauses + transfer impact assessment. Data stored in an EU region. |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 0 |

### Security audit log (`security_audit`)

| | |
| --- | --- |
| Description | Sign-ins, passkey changes, exports, deletions, consent changes; keyed IP hash |
| Purposes | Security investigation; Demonstrate correct handling of rights requests |
| Data subjects | users |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0001-security-and-fraud-prevention.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `audit_log` |
| Retention | 365 days |
| On erasure | anonymise |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Consent records (`consent_records`)

| | |
| --- | --- |
| Description | Append-only history of each consent: kind, version, granted/withdrawn, time, source |
| Purposes | Prove consent was given (GDPR Art 7(1)); Apply the user's current choices |
| Data subjects | users |
| Lawful basis | Legal obligation — Art 6(1)(c); GDPR Art 7(1) — controller must be able to demonstrate consent |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `consents` |
| Retention | 2190 days after account deletion (pseudonymised). On erasure user_id is replaced by subject_ref (keyed hash of the email) so the record proves consent without identifying the account. 6 years = Irish limitation period for contract claims; confirm with solicitor. |
| On erasure | retain legal |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### AI usage and cost records (`ai_usage`)

| | |
| --- | --- |
| Description | Feature, prompt version, model, token counts, cost — never prompt or response text |
| Purposes | Enforce fair-use quotas; Control AI costs |
| Data subjects | users |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0002-service-operation-and-cost-control.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `ai_usage` |
| Retention | 400 days |
| On erasure | anonymise |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### CVs, cover letters and job descriptions (`cv_content`)

| | |
| --- | --- |
| Description | Uploaded CV files, structured CV versions, suggestions, ATS checks, cover letters, saved screening answers, pasted job descriptions. May contain third-party data (referees) — the builder advises 'References available on request' and warns before saving referee contact details. |
| Purposes | Build, improve, tailor and export CVs and cover letters |
| Data subjects | users, third parties named in cvs |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `uploaded_files`, `cv_documents`, `cv_versions`, `cv_suggestions`, `ats_checks`, `job_description_parses`, `cover_letters`, `screening_answers`, `ai:cache:<sha256(prompt_version\|model\|input)>`, `cv-check upload (object storage, no account)` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Anthropic (Claude API) (United States) |
| Transfers outside the EEA | Anthropic (Claude API): Commercial terms with DPA and SCCs; transfer impact assessment. Contact details are removed before every call (app.privacy.ai_guard). Confirm API data-retention terms and request zero data retention if offered. |
| AI minimisation | Contact block and links removed; app.privacy.ai_guard blocks the call if an email, phone, PPSN, NI number, IBAN, postcode or URL remains |
| Storage rule | Standard (see security measures) |
| Built in stage | 2 |

### LinkedIn profile copy and suggestions (`linkedin_profile`)

| | |
| --- | --- |
| Description | Headline, About, industry, positions (employer, title, dates, description), skills and education names that the user imported from their own LinkedIn data export, a profile PDF or pasted text; checklist results and rewrite suggestions. The uploaded export ZIP is read in memory and never stored; only profile files are opened (never connections or messages); birth date, address, phone and email are dropped at parse time. |
| Purposes | Check the user's LinkedIn profile; Compare it with their CV; Suggest rewrites the user pastes into LinkedIn themselves |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `linkedin_profiles`, `linkedin_suggestions` |
| Retention | While the account exists; erased within 30 days of deletion. The user can delete the imported copy at any time from the LinkedIn screen; a new import replaces the old one |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Anthropic (Claude API) (United States) |
| Transfers outside the EEA | Anthropic (Claude API): Commercial terms with DPA and SCCs; transfer impact assessment. Contact details are removed before every call (app.privacy.ai_guard). Confirm API data-retention terms and request zero data retention if offered. |
| AI minimisation | Only headline, About, industry, the 4 most recent positions and skills are sent, through app.privacy.ai_guard; location and education are not sent |
| Storage rule | Standard (see security measures) |
| Built in stage | 3 |

### Launch waitlist and beta invites (`waitlist_and_beta_invites`)

| | |
| --- | --- |
| Description | Email address of people who asked to hear when Hearback launches or to join the private beta; invite codes and who redeemed them |
| Purposes | Tell people when they can sign up; Run the invitation-only private beta |
| Data subjects | prospective users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `waitlist_signups`, `beta_invites` |
| Retention | 365 days. Steps taken at the person's request before a contract (Art 6(1)(b)). Rows are also deleted 30 days after the public launch email is sent, or at once on request; nothing else is ever sent to these addresses |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Amazon Web Services EMEA SARL (Amazon SES) (eu-west-1 (Ireland)) |
| Transfers outside the EEA | Amazon Web Services EMEA SARL (Amazon SES): Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 4 |

### Job search preferences (`job_preferences`)

| | |
| --- | --- |
| Description | Target roles, locations, commute, remote preference, salary floor, excluded companies, digest time. Visa/permit status is optional and treated as high sensitivity (can indicate nationality). |
| Purposes | Match jobs to the user; Send the daily digest at the chosen time; Show visa-sponsor information when the user asks for it |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `user_preferences` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 6 |

### Job matches and scores (`match_results`)

| | |
| --- | --- |
| Description | Daily ranked matches, scores, reasons, confidence, model version, user actions |
| Purposes | Show the daily matches and explain them |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | Advisory only. No decision with legal or similarly significant effect is made; the user decides what to apply for. Reasons are always shown. |
| DPIA | `docs/privacy/dpia/0001-matching-scores-and-insights.md` |
| Stored in | `job_matches` |
| Retention | 180 days |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 6 |

### Applications, events, interviews and offers (`application_tracking`)

| | |
| --- | --- |
| Description | The user's tracker: applications, immutable action log, agency submissions, interview notes, offers, stories, pitches, question prep |
| Purposes | Run the tracker; Reply timings and next steps; Interview preparation |
| Data subjects | users, interviewers named by user |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `applications`, `application_events`, `agency_submissions`, `interviews`, `stories`, `pitches`, `question_prep`, `practice_sessions`, `offers` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Anthropic (Claude API) (United States) |
| Transfers outside the EEA | Anthropic (Claude API): Commercial terms with DPA and SCCs; transfer impact assessment. Contact details are removed before every call (app.privacy.ai_guard). Confirm API data-retention terms and request zero data retention if offered. |
| AI minimisation | Interview feedback sends the answer text only, after redaction |
| Storage rule | Standard (see security measures) |
| Built in stage | 7 |

### Captured employer emails — metadata (`inbound_email_metadata`)

| | |
| --- | --- |
| Description | Sender domain, received/sent time, link to application, classification label |
| Purposes | Track reply timings; Update the tracker automatically |
| Data subjects | users, employer contacts |
| Lawful basis | Contract — Art 6(1)(b); LIA: `docs/privacy/lia/0003-employer-contacts-in-captured-emails.md` |
| Third-party data | Employer contacts: legitimate interests of the user and Offerlight in tracking replies to the user's own applications — see LIA 0003 |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `inbound_addresses`, `inbound_emails` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Amazon Web Services EMEA SARL (Amazon SES) (eu-west-1 (Ireland)) |
| Transfers outside the EEA | Amazon Web Services EMEA SARL (Amazon SES): Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 8 |

### Captured employer emails — content (`inbound_email_content`)

| | |
| --- | --- |
| Description | Email body (encrypted at rest), raw message in storage, sender address, subject |
| Purposes | Classify the reply; Let the user read it in the tracker |
| Data subjects | users, employer contacts |
| Lawful basis | Contract — Art 6(1)(b); LIA: `docs/privacy/lia/0003-employer-contacts-in-captured-emails.md` |
| Third-party data | As inbound_email_metadata — see LIA 0003 |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `inbound_emails` |
| Retention | 90 days |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Amazon Web Services EMEA SARL (Amazon SES) (eu-west-1 (Ireland)) |
| Transfers outside the EEA | Amazon Web Services EMEA SARL (Amazon SES): Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 8 |

### Reply classification and rejection assessments (`reply_and_rejection_scores`)

| | |
| --- | --- |
| Description | Reply labels, probability the rejection was automated, signals, probable cause |
| Purposes | Explain likely reasons for rejection to the user |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | Advisory only and shown only to the user. Signals and uncertainty always shown. |
| DPIA | `docs/privacy/dpia/0001-matching-scores-and-insights.md` |
| Stored in | `reply_classifications`, `rejection_assessments` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 8 |

### Interview practice audio (`practice_audio`)

| | |
| --- | --- |
| Description | Audio track of a practice answer, uploaded only for transcription. Video never leaves the browser. |
| Purposes | Transcribe a practice answer |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `voice_practice`) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | `docs/privacy/dpia/0002-interview-practice-recordings.md` |
| Stored in | `recordings` |
| Retention | 1 days. Deleted by the transcription job immediately after processing; the daily retention job is the safety net (24 hours) |
| On erasure | delete |
| Included in export | No — Deleted within 24 hours of upload; never held long enough to export |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 10 |

### Interview practice transcripts and delivery metrics (`practice_transcripts`)

| | |
| --- | --- |
| Description | Transcript, words per minute, filler words, pauses, structure — no face, voice-tone or emotion analysis |
| Purposes | Give feedback on practice answers |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `voice_practice`) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | `docs/privacy/dpia/0002-interview-practice-recordings.md` |
| Stored in | `recordings` |
| Retention | 30 days. Kept longer only while the user has ticked 'Keep' on that recording |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Anthropic (Claude API) (United States) |
| Transfers outside the EEA | Anthropic (Claude API): Commercial terms with DPA and SCCs; transfer impact assessment. Contact details are removed before every call (app.privacy.ai_guard). Confirm API data-retention terms and request zero data retention if offered. |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 10 |

### Experiment assignments (`experiments`)

| | |
| --- | --- |
| Description | Random arm assignment of the user's own applications (for example CV A vs B) |
| Purposes | Measure which actions lead to interviews |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `experiments`) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `experiments`, `experiment_assignments` |
| Retention | Until consent is withdrawn or the account is deleted |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 9 |

### Contribution to anonymised benchmarks (`benchmark_contribution`)

| | |
| --- | --- |
| Description | Whether the user's outcomes may be included in aggregate cohort statistics (k >= 10). No personal data is stored in the aggregates. |
| Purposes | Publish cohort benchmarks so users know where they stand |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `benchmarks`) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | consents table, kind = benchmarks; read by the nightly aggregation job |
| Retention | Until consent is withdrawn or the account is deleted. Withdrawal excludes the user from the next nightly aggregation; published aggregates cannot identify anyone and are not recalculated retroactively |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 9 |

### Fairness audit demographics (`fairness_demographics`)

| | |
| --- | --- |
| Description | Optional gender, nationality group, age band, disability (yes/no/prefer not) — used only to test our models for bias |
| Purposes | Annual fairness audit of matching and scoring models |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `fairness_audit`); Art 9(2)(a) explicit consent |
| Third-party data | — |
| Special category | Yes |
| Profiling | No |
| DPIA | `docs/privacy/dpia/0003-fairness-audit-demographics.md` |
| Stored in | `fairness_demographics` |
| Retention | Until consent is withdrawn or the account is deleted |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Separate schema `sensitive`, column-level encryption, no foreign key exposed to product queries, never joined in product code, readable only by the audit job |
| Built in stage | 11 |

### Product news emails (marketing) (`email_preferences`)

| | |
| --- | --- |
| Description | Opt-in to occasional product news. The daily digest is not marketing: it is part of the service and its on/off switch and time live in user_preferences (contract). |
| Purposes | Send product news to people who opted in |
| Data subjects | users |
| Lawful basis | Consent — Art 6(1)(a) (consent kind `marketing`) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | consents table, kind = marketing |
| Retention | Until consent is withdrawn or the account is deleted. Opt-in consent required (ePrivacy Regulations S.I. 336 of 2011 in Ireland, PECR in the UK). Every email has a one-click unsubscribe that records a withdrawal. |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Amazon Web Services EMEA SARL (Amazon SES) (eu-west-1 (Ireland)) |
| Transfers outside the EEA | Amazon Web Services EMEA SARL (Amazon SES): Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 6 |

### Billing and tax records (`billing_records`)

| | |
| --- | --- |
| Description | Stripe customer and subscription ids, plan, invoices, amounts, VAT country |
| Purposes | Take payment; Keep accounting and tax records |
| Data subjects | users |
| Lawful basis | Legal obligation — Art 6(1)(c); Taxes Consolidation Act 1997 s.886 (Ireland) — records kept 6 years; UK HMRC equivalent |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `subscriptions` |
| Retention | 2190 days. 6 years from the end of the subscription (ended_at), whether or not the account still exists |
| On erasure | retain legal |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers); Stripe Payments Europe, Ltd. (Ireland (EU), with transfers to Stripe, Inc. (US)) |
| Transfers outside the EEA | Stripe Payments Europe, Ltd.: Stripe DPA with SCCs and EU-US Data Privacy Framework. Stripe is an independent controller for some payment data (fraud, regulatory). |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 4 |

### Plans, entitlements and guarantee tracking (`entitlements`)

| | |
| --- | --- |
| Description | What the user can use, and the state of the interview guarantee conditions |
| Purposes | Provide what the user paid for; Honour the guarantee |
| Data subjects | users |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `entitlements`, `guarantee_tracking` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 4 |

### Job advertisements (`public_job_ads`)

| | |
| --- | --- |
| Description | Job ads from licensed APIs and public ATS boards. May name a recruiter or hiring manager. |
| Purposes | Show and match job ads |
| Data subjects | recruiters named in ads |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0004-job-ads-and-company-data.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `job_postings` |
| Retention | 365 days |
| On erasure | delete |
| Included in export | No — Not data about our users; recruiters may request access or erasure through privacy@ (manual DSAR) |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 5 |

### Raw job API payloads (`public_job_ads_raw`)

| | |
| --- | --- |
| Description | Unprocessed responses from job APIs, kept briefly for debugging the parser |
| Purposes | Debug job ingestion |
| Data subjects | recruiters named in ads |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0004-job-ads-and-company-data.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `job_postings_raw` |
| Retention | 30 days |
| On erasure | delete |
| Included in export | No — Not data about our users |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 5 |

### Scam and job reports (`user_reports`)

| | |
| --- | --- |
| Description | Reports users make about job ads, with free-text details |
| Purposes | Protect users from fake job ads |
| Data subjects | users, recruiters named in ads |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0004-job-ads-and-company-data.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `job_reports` |
| Retention | 730 days |
| On erasure | anonymise |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 5 |

### Organisation membership (`organisation_membership`)

| | |
| --- | --- |
| Description | Which organisation (university, outplacement firm) a user belongs to and their role. Organisations see aggregates only (k >= 10), never individual data. |
| Purposes | Give organisations aggregate progress reports |
| Data subjects | users, organisation staff |
| Lawful basis | Contract — Art 6(1)(b) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `org_members` |
| Retention | While the account exists; erased within 30 days of deletion |
| On erasure | delete |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 12 |

### Data protection rights requests (`rights_requests`)

| | |
| --- | --- |
| Description | Requests to access, export, erase, rectify, restrict or object; deadlines; outcome |
| Purposes | Handle rights requests within the legal deadline and prove we did |
| Data subjects | users, recruiters named in ads, employer contacts |
| Lawful basis | Legal obligation — Art 6(1)(c); GDPR Art 12 and Art 5(2) accountability |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `data_subject_requests` |
| Retention | 1095 days. Requester identity reduced to subject_ref (keyed hash) once the request is closed |
| On erasure | retain legal |
| Included in export | Yes |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Erasure tombstones (`erasure_tombstones`)

| | |
| --- | --- |
| Description | Keyed hash of an erased user's id and email, erased_at. Used to re-apply erasure after a backup restore. |
| Purposes | Make erasure stick after a backup restore |
| Data subjects | former users |
| Lawful basis | Legal obligation — Art 6(1)(c); GDPR Art 17 — erasure must remain effective |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `erasure_tombstones` |
| Retention | 60 days. Longer than the backup retention (30 days) so every backup that could contain the user has expired |
| On erasure | retain legal |
| Included in export | No — Created after erasure; holds only a keyed hash |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Personal data breach register (`privacy_incidents`)

| | |
| --- | --- |
| Description | Every personal data breach, its facts, effects and remedial action — including breaches not notified |
| Purposes | Comply with GDPR Art 33(5); Learn from incidents |
| Data subjects | users, former users |
| Lawful basis | Legal obligation — Art 6(1)(c); GDPR Art 33(5) |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | `privacy_incidents` |
| Retention | 2190 days. Holds counts and categories, not individual identities |
| On erasure | retain legal |
| Included in export | No — Register contains no individual-level personal data |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Scaleway SAS (France (EU)); Off-site backup object storage (provider per decisions-needed #2) (EU, different provider from the servers) |
| Transfers outside the EEA | None |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 1 |

### Application and error logs (`application_logs`)

| | |
| --- | --- |
| Description | Request ids, user ids (never emails), routes, errors. PII is redacted by app.privacy.redaction before anything is written. |
| Purposes | Operate and debug the service |
| Data subjects | users |
| Lawful basis | Legitimate interests — Art 6(1)(f); LIA: `docs/privacy/lia/0002-service-operation-and-cost-control.md` |
| Third-party data | — |
| Special category | No |
| Profiling | No |
| DPIA | Not required (screened) |
| Stored in | Container logs on the server (rotated) and Sentry (EU region) |
| Retention | 30 days. Enforced by log-shipper/Sentry retention settings, not by the database job |
| On erasure | delete |
| Included in export | No — Operational logs keyed by user id only; available on request through a manual DSAR |
| Recipients | Hetzner Online GmbH (Germany / Finland (EU)); Functional Software, Inc. (Sentry) (EU data region (de.sentry.io)) |
| Transfers outside the EEA | Functional Software, Inc. (Sentry): EU data region; US parent: Sentry DPA with SCCs |
| AI minimisation | Not sent to AI |
| Storage rule | Standard (see security measures) |
| Built in stage | 0 |

## Technical and organisational security measures (Art 32)

Applies to every activity above; detail in `docs/06-security.md`.

- Encryption in transit (TLS 1.2+, HSTS) and at rest (provider disk encryption; application-level encryption for email bodies and special category data; GPG-encrypted backups).
- Passwordless authentication; step-up for sensitive actions; admin access with hardware keys only; least-privilege database roles.
- Personal data redacted from logs and error reports (`app.privacy.redaction`).
- Data minimisation before AI calls (`app.privacy.ai_guard`).
- EU hosting; processors bound by DPAs; transfers covered as listed.
- Automated retention and erasure jobs generated from this inventory; restore procedure re-applies erasures from tombstones.
- Breach procedure with 72-hour notification clock (`docs/privacy/breach-runbook.md`).

## Processors

| Processor | Service | Location | Outside EEA | Transfer mechanism | DPA | From stage |
| --- | --- | --- | --- | --- | --- | --- |
| Hetzner Online GmbH | Servers, load balancer and object storage (all hosting tiers) | Germany / Finland (EU) | No | — | Sign the data processing agreement in the Hetzner console before Stage 0 deploy | 0 |
| Scaleway SAS | Managed PostgreSQL (Tier 1+) | France (EU) | No | — | Accept the Scaleway DPA before Tier 1 | 4 |
| Upstash, Inc. | Managed Redis (Tier 1+): sessions cache, rate limits, job queue | EU region (eu-west-1 or eu-central-1) | Yes | US parent company: EU-US Data Privacy Framework if certified at signing, otherwise Standard Contractual Clauses + transfer impact assessment. Data stored in an EU region. | Sign the Upstash DPA before Tier 1 | 4 |
| Off-site backup object storage (provider per decisions-needed #2) | Encrypted nightly database backups (GPG, key held by owners) | EU, different provider from the servers | No | — | Sign before Stage 0 backups start | 0 |
| Cloudflare, Inc. | Turnstile bot check, Pages static hosting, DNS | Global network; EU customer data localisation where available | Yes | EU-US Data Privacy Framework (verify certification at signing) + Cloudflare DPA with SCCs | Accept the Cloudflare DPA before Stage 1 | 1 |
| Amazon Web Services EMEA SARL (Amazon SES) | Transactional email (codes, alerts, digests) and inbound reply capture | eu-west-1 (Ireland) | Yes | Processing in eu-west-1; US parent: AWS DPA with SCCs, EU-US Data Privacy Framework | AWS GDPR DPA (part of the AWS service terms) — confirm before Stage 1 | 1 |
| Anthropic (Claude API) | Writing suggestions, messy-text parsing, interview answer feedback — only when the user asks | United States | Yes | Commercial terms with DPA and SCCs; transfer impact assessment. Contact details are removed before every call (app.privacy.ai_guard). Confirm API data-retention terms and request zero data retention if offered. | Sign the Anthropic DPA before Stage 2 | 2 |
| Stripe Payments Europe, Ltd. | Payments and invoices. Stripe holds card data; we never see card numbers. | Ireland (EU), with transfers to Stripe, Inc. (US) | Yes | Stripe DPA with SCCs and EU-US Data Privacy Framework. Stripe is an independent controller for some payment data (fraud, regulatory). | Stripe DPA (part of the Stripe Services Agreement) — confirm before Stage 4 | 4 |
| Functional Software, Inc. (Sentry) | Error monitoring. PII scrubbing on (send_default_pii = false + app.privacy.redaction). | EU data region (de.sentry.io) | Yes | EU data region; US parent: Sentry DPA with SCCs | Accept the Sentry DPA before Stage 0 error monitoring goes live | 0 |
| Plausible Insights OÜ (or self-hosted Umami — no processor) | Cookieless, aggregate page analytics. No personal data stored. | Germany (EU) | No | — | Accept the Plausible DPA before Stage 4 | 4 |

## Automated retention (nightly job)

| Table | Action | Category | After | Clock |
| --- | --- | --- | --- | --- |
| `sessions` | delete rows | `sessions` | 90 days | `created_at` |
| `consents` | delete rows | `consent_records` | 2190 days | `pseudonymised_at` |
| `audit_log` | delete rows | `security_audit` | 365 days | `occurred_at` |
| `ai_usage` | delete rows | `ai_usage` | 400 days | `occurred_at` |
| `data_subject_requests` | delete rows | `rights_requests` | 1095 days | `closed_at` |
| `erasure_tombstones` | delete rows | `erasure_tombstones` | 60 days | `erased_at` |
| `privacy_incidents` | delete rows | `privacy_incidents` | 2190 days | `closed_at` |
| `waitlist_signups` | delete rows | `waitlist_and_beta_invites` | 365 days | `created_at` |
| `beta_invites` | delete rows | `waitlist_and_beta_invites` | 365 days | `created_at` |
| `job_postings_raw` | delete rows | `public_job_ads_raw` | 30 days | `fetched_at` |
| `job_postings` | delete rows | `public_job_ads` | 365 days | `last_seen_at` |
| `job_reports` | delete rows | `user_reports` | 730 days | `created_at` |
| `job_matches` | delete rows | `match_results` | 180 days | `created_at` |
| `inbound_emails` | clear body_text, from_address, raw_s3_key, subject | `inbound_email_content` | 90 days | `received_at` |
| `recordings` | delete rows | `practice_transcripts` | 30 days | `created_at` |
| `recordings` | clear audio_s3_key | `practice_audio` | 1 days | `created_at` |
| `subscriptions` | delete rows | `billing_records` | 2190 days | `ended_at` |

## Table classification

| Table | Default category | Column overrides | User link | Stage |
| --- | --- | --- | --- | --- |
| `users` | `account_identity` | — | `id` | 1 |
| `passkey_credentials` | `authentication` | — | `user_id` | 1 |
| `sessions` | `sessions` | — | `user_id` | 1 |
| `consents` | `consent_records` | — | `user_id` | 1 |
| `audit_log` | `security_audit` | — | `user_id` | 1 |
| `feature_flags` | `not_personal` | — | — | 1 |
| `ai_usage` | `ai_usage` | — | `user_id` | 1 |
| `data_subject_requests` | `rights_requests` | — | `user_id` | 1 |
| `erasure_tombstones` | `erasure_tombstones` | — | — | 1 |
| `privacy_incidents` | `privacy_incidents` | — | — | 1 |
| `uploaded_files` | `cv_content` | — | `user_id` | 2 |
| `cv_documents` | `cv_content` | — | `user_id` | 2 |
| `cv_versions` | `cv_content` | — | via `cv_documents` | 2 |
| `cv_suggestions` | `cv_content` | — | via `cv_versions` | 2 |
| `ats_checks` | `cv_content` | — | via `cv_versions` | 2 |
| `skills` | `not_personal` | — | — | 2 |
| `job_description_parses` | `cv_content` | — | `user_id` | 3 |
| `linkedin_profiles` | `linkedin_profile` | — | `user_id` | 3 |
| `linkedin_suggestions` | `linkedin_profile` | — | via `linkedin_profiles` | 3 |
| `role_skill_demand` | `not_personal` | — | — | 5 |
| `waitlist_signups` | `waitlist_and_beta_invites` | — | — | 4 |
| `beta_invites` | `waitlist_and_beta_invites` | — | `redeemed_by_user_id` | 4 |
| `job_sources` | `not_personal` | — | — | 5 |
| `job_postings_raw` | `public_job_ads_raw` | — | — | 5 |
| `job_postings` | `public_job_ads` | — | — | 5 |
| `companies` | `not_personal` | — | — | 5 |
| `company_aliases` | `not_personal` | — | — | 5 |
| `company_visa_data` | `not_personal` | — | — | 5 |
| `critical_skills_occupations` | `not_personal` | — | — | 5 |
| `company_reply_stats` | `not_personal` | — | — | 8 |
| `job_flags` | `not_personal` | — | — | 5 |
| `job_reports` | `user_reports` | — | `user_id` | 5 |
| `user_preferences` | `job_preferences` | — | `user_id` | 6 |
| `job_matches` | `match_results` | — | `user_id` | 6 |
| `applications` | `application_tracking` | — | `user_id` | 7 |
| `application_events` | `application_tracking` | — | `user_id` | 7 |
| `agencies` | `not_personal` | — | — | 7 |
| `agency_submissions` | `application_tracking` | — | via `applications` | 7 |
| `cover_letters` | `cv_content` | — | `user_id` | 7 |
| `screening_answers` | `cv_content` | — | `user_id` | 7 |
| `inbound_addresses` | `inbound_email_metadata` | — | `user_id` | 8 |
| `inbound_emails` | `inbound_email_metadata` | `body_text` → `inbound_email_content`, `raw_s3_key` → `inbound_email_content`, `from_address` → `inbound_email_content`, `subject` → `inbound_email_content` | `user_id` | 8 |
| `reply_classifications` | `reply_and_rejection_scores` | — | via `inbound_emails` | 8 |
| `rejection_assessments` | `reply_and_rejection_scores` | — | via `applications` | 8 |
| `cohorts` | `not_personal` | — | — | 9 |
| `benchmarks` | `not_personal` | — | — | 9 |
| `experiments` | `experiments` | — | `user_id` | 9 |
| `experiment_assignments` | `experiments` | — | via `applications` | 9 |
| `effect_estimates` | `not_personal` | — | — | 9 |
| `interviews` | `application_tracking` | — | via `applications` | 10 |
| `stories` | `application_tracking` | — | `user_id` | 10 |
| `pitches` | `application_tracking` | — | `user_id` | 10 |
| `question_prep` | `application_tracking` | — | `user_id` | 10 |
| `practice_sessions` | `application_tracking` | — | `user_id` | 10 |
| `recordings` | `practice_transcripts` | `audio_s3_key` → `practice_audio` | via `practice_sessions` | 10 |
| `reported_questions` | `not_personal` | — | — | 10 |
| `offers` | `application_tracking` | — | via `applications` | 10 |
| `fairness_demographics` | `fairness_demographics` | — | `user_id` | 11 |
| `subscriptions` | `billing_records` | — | `user_id` | 4 |
| `entitlements` | `entitlements` | — | `user_id` | 4 |
| `guarantee_tracking` | `entitlements` | — | `user_id` | 4 |
| `organisations` | `not_personal` | — | — | 12 |
| `org_members` | `organisation_membership` | — | `user_id` | 12 |
| `org_cohorts` | `not_personal` | — | — | 12 |
