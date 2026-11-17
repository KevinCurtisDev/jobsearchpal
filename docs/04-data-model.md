# 04 · Data model

PostgreSQL 16. All tables have `id uuid primary key default gen_random_uuid()`, `created_at`
and `updated_at timestamptz`. Times are stored in UTC. Soft deletes are **not** used for
personal data: deletion is real (see `13-privacy-and-compliance.md`).

Naming: snake_case, plural table names, foreign keys `<entity>_id`.

**Privacy classification is mandatory.** Every table here is declared in
`backend/app/privacy/data_inventory.toml` with its category, lawful basis, retention and
erasure rule. CI fails if a table in this file, or a SQLAlchemy model, is missing from the
inventory, or if a foreign key's `ON DELETE` does not match the declared erasure rule
(`CASCADE` for delete, `SET NULL` for anonymise/pseudonymise). See
`13-privacy-and-compliance.md`.

## Accounts and security (Stage 1)

| Table | Key columns | Notes |
| --- | --- | --- |
| `users` | email (citext, unique), email_verified_at, display_name, locale, country (IE/UK), status (pending, active, locked, deleting), deletion_requested_at, plan | No password column, ever |
| `passkey_credentials` | user_id, credential_id (bytea, unique), public_key (bytea), sign_count, transports (text[]), aaguid, backup_eligible, backup_state, nickname, last_used_at | From WebAuthn registration |
| `sessions` | user_id, token_hash (bytea, unique), created_at, last_seen_at, expires_at, absolute_expires_at, ip_hash, user_agent, device_label, revoked_at, step_up_at | Token itself only in the cookie |
| `consents` | user_id (nullable, SET NULL), subject_ref, pseudonymised_at, kind (consents: benchmarks, experiments, fairness_audit, marketing, voice_practice, question_bank; acknowledgements: terms, privacy_notice, age_16_plus), version, granted (bool), recorded_at, source (settings, onboarding, email_unsubscribe, admin_on_request), wording_sha256 | Append-only: no UPDATE except erasure pseudonymisation; enforced by a DB trigger |
| `audit_log` | user_id (nullable, SET NULL), actor, action, target_type, target_id, ip_hash, metadata jsonb, occurred_at | Security events: sign-in, passkey changes, exports, deletes, consent changes. `metadata` holds ids and counts only |
| `feature_flags` | key (unique), enabled, rollout_percent, notes | Model gates |
| `ai_usage` | user_id (nullable, SET NULL), feature, prompt_name, prompt_version, model, tokens_in, tokens_out, cost_eur, occurred_at | Quotas and cost tracking. Never prompt or response text |
| `data_subject_requests` | user_id (nullable, SET NULL), subject_ref, pseudonymised_at, requester_email (encrypted, cleared on close), kind (access, export, erasure, rectification, restriction, objection, other), channel (self_service, email, post), received_at, identity_verified_at, due_at, extended_until, extension_reason, status (open, waiting_for_requester, completed, refused), refusal_reason, closed_at, handled_by | Rights request register (self-service requests are logged here too) |
| `erasure_tombstones` | user_ref (keyed hash of user id), subject_ref (keyed hash of email), erased_at | Re-applied after any backup restore; kept 60 days |
| `privacy_incidents` | detected_at, aware_at, notify_by, summary, categories text[], approx_subjects, approx_records, risk (none, risk, high_risk), dpc_notified_at, ico_notified_at, subjects_informed_at, decision_reason, remedial_actions, closed_at | Breach register (Art 33(5)); no individual identities |

Short-lived data in Redis (not Postgres): email codes (hashed), magic-link tokens (hashed),
WebAuthn challenges, rate-limit counters.

## CV (Stage 2–3)

| Table | Key columns | Notes |
| --- | --- | --- |
| `uploaded_files` | user_id, kind (cv_upload, cv_export), s3_key, mime_type, size_bytes, sha256, scan_status, expires_at | Private bucket. Practice audio is **not** stored here (see `recordings`) |
| `cv_documents` | user_id, title, country_convention (IE, UK, EU, US), template (classic, modern, compact), age_neutral (bool) | One per CV "family" |
| `cv_versions` | cv_document_id, label ("Version A · General"), content jsonb (validated by `cv.schema.json`), source (upload, manual, tailored, ai_suggested), parent_version_id, job_id (nullable), created_by (user, system) | Immutable; edits create new versions |
| `cv_suggestions` | cv_version_id, kind (writing_rule, ai_rewrite, tailor), path (JSON pointer), before, after, reason, status (open, accepted, dismissed) | Every suggestion is reviewable |
| `ats_checks` | cv_version_id, file_id, passed (bool), checks jsonb | Re-extraction report |
| `skills` | esco_uri, preferred_label, alt_labels text[], skill_type | Loaded from ESCO |
| `job_description_parses` | user_id, raw_text, url, parsed jsonb (requirements with required flag) | For tailoring |

### `cv.schema.json` (outline)

```json
{
  "contact": {"name": "", "email": "", "phone": "", "location": "", "links": []},
  "summary": "",
  "roles": [{"title": "", "employer": "", "start": "YYYY-MM", "end": "YYYY-MM|present",
             "location": "", "achievements": [{"id": "", "text": ""}]}],
  "skills": [{"name": "", "esco_uri": null}],
  "education": [{"qualification": "", "institution": "", "end": "YYYY"}],
  "extras": [{"heading": "Volunteering|Certifications|Languages|Projects", "items": [""]}]
}
```

The full JSON Schema lives in `backend/app/schemas/cv.schema.json` (create in Stage 2).

## LinkedIn profile (Stage 3; keyword gap from Stage 5)

| Table | Key columns | Notes |
| --- | --- | --- |
| `linkedin_profiles` | user_id (unique), source (export, pdf, pasted), headline, about, industry, positions jsonb (company, title, description, start, end), skills text[], education jsonb (school, degree, end), imported_at | One per user; a new import replaces it. The uploaded ZIP/PDF is never stored |
| `linkedin_suggestions` | linkedin_profile_id, section (headline, about, position), position_index, kind (rewrite, ask), before, after, reason, prompt_version, status (open, copied, dismissed) | "Copied" is recorded when the user presses Copy; we never edit LinkedIn |
| `role_skill_demand` | role_family, esco_uri, preferred_label, n_ads, n_ads_with_skill, window_days, computed_at | Not personal. Nightly from `job_postings` |

## Jobs and companies (Stage 5–6)

| Table | Key columns | Notes |
| --- | --- | --- |
| `job_sources` | name, kind (aggregator, ats_board), config jsonb, enabled, last_run_at | |
| `job_postings_raw` | source_id, external_id, payload jsonb, fetched_at | Kept 30 days |
| `job_postings` | canonical_id, source_id, external_id, url, title, company_id, location_text, county, city, country, remote_type, salary_min, salary_max, currency, salary_disclosed, posted_at, first_seen_at, last_seen_at, closed_at, description, minhash bytea, embedding vector(384), repost_count | |
| `companies` | name, normalized_name, country, registry_id (CRO / Companies House), registry_status, website_domain, sector | |
| `company_aliases` | company_id, alias, source | Entity resolution |
| `company_visa_data` | company_id, uk_sponsor_licensed, uk_sponsor_routes text[], ie_permits_by_year jsonb, source_dates jsonb | Past activity only |
| `critical_skills_occupations` | country, occupation_code, title, valid_from, valid_to | Ireland list |
| `company_reply_stats` | company_id, n_applications, km_curve jsonb, median_days, p_reply_21d, reply_rate_raw, reply_rate_shrunk, confidence, computed_at | Shown only above minimum n |
| `job_flags` | job_id, kind (stale, reposted, salary_outlier, no_registry, payment_request, urgency_language, user_reports), score, reasons jsonb | Fake job detection |
| `job_reports` | job_id, user_id, reason, details, status (open, verified_scam, dismissed), reviewed_by | Admin review |
| `user_preferences` | user_id, roles text[], locations jsonb, max_commute_minutes, remote_types text[], salary_floor, visa_status, excluded_company_ids uuid[], digest_time_local | |
| `job_matches` | user_id, job_id, run_date, rank, score, probability (nullable until calibrated), confidence, reasons jsonb, model_version, shown_at, action (saved, dismissed, applied) | |

## Applications and the action log (Stage 7–8)

| Table | Key columns | Notes |
| --- | --- | --- |
| `applications` | user_id, job_id (nullable for manual), company_id, role_title, status (saved, applied, screening, interview, offer, closed), closed_reason (rejected, withdrawn, accepted, no_reply), cv_version_id, cover_letter_id, source (job_board, careers_page, agency, referral, other), agency_id, referral_status (none, asked, referred; default none — no third-party names stored) | |
| `application_events` | application_id, user_id, type (saved, tailored, applied, followed_up, reply_received, rejected, interview_invited, assessment, interview_held, offer_received, offer_accepted, withdrawn), occurred_at, metadata jsonb | **Immutable action log** — the foundation for survival and uplift models |
| `agencies` | name, normalized_name, website_domain | |
| `agency_submissions` | application_id, agency_id, submitted_at, role_reference | Duplicate warnings |
| `cover_letters` | user_id, application_id, content, status (draft, final) | |
| `screening_answers` | user_id, question_key, answer, updated_at | Reusable profile answers |
| `inbound_addresses` | user_id, local_part (unique), active | e.g. `aoife.k7@in.<domain>` |
| `inbound_emails` | user_id, inbound_address_id, from_address, from_domain, subject, received_at, sent_at, body_text (encrypted), raw_s3_key, application_id | from_address, subject, body_text and raw_s3_key cleared at 90 days; metadata kept |
| `reply_classifications` | inbound_email_id, label (rejection, interview_invite, assessment, info_request, other), probability, model_version, confirmed_by_user | |
| `rejection_assessments` | application_id, inbound_email_id, p_automated, signals jsonb, probable_cause, model_version, helpful (bool, nullable) | |

## Insights and experiments (Stage 9)

| Table | Key columns | Notes |
| --- | --- | --- |
| `cohorts` | key (role_family, seniority, region), size, computed_at | |
| `benchmarks` | cohort_id, stage, rate_raw, rate_shrunk, n, computed_at | |
| `experiments` | user_id (nullable for global), kind (cv_ab, follow_up_timing, …), arms jsonb, status, started_at, ended_at | |
| `experiment_assignments` | experiment_id, application_id, arm, assigned_at, randomization_seed | |
| `effect_estimates` | scope (global, cohort, user), action, estimate, ci_low, ci_high, method, n, confidence, computed_at | |

## Interview prep (Stage 10)

| Table | Key columns | Notes |
| --- | --- | --- |
| `interviews` | application_id, scheduled_at, format (phone, video, in_person, panel, assessment_centre, technical), interviewers jsonb, checklist jsonb, notes | |
| `stories` | user_id, title, source (work, outside_work), situation, task, action, result, reflection, competencies text[], checks jsonb, est_seconds | |
| `pitches` | user_id, application_id (nullable), length_seconds (30, 60, 90), present, past, future | |
| `question_prep` | user_id, question_key, status (not_started, prepared), story_id, notes | Links to `content/core_questions.json` keys |
| `practice_sessions` | user_id, mode (text, voice, video), question_key or text, created_at | |
| `recordings` | practice_session_id, audio_s3_key (nullable; cleared after transcription, max 24 h), duration_s, transcript, metrics jsonb (wpm, fillers, pauses, length_vs_target, structure), keep (bool), created_at | Video never uploaded. Deleted at 30 days unless kept |
| `reported_questions` | company_id, question_text, role_family, reported_at | Anonymised, consented |
| `offers` | application_id, salary, currency, office_days, commute_minutes, commute_cost_month, benefits jsonb, year_view jsonb (user's own 1–5 ratings or null: hours_flex, manager_team, growth) | |

## Billing and organisations (Stage 4, 12)

| Table | Key columns |
| --- | --- |
| `subscriptions` | user_id (nullable, SET NULL), subject_ref, pseudonymised_at, stripe_customer_id, stripe_subscription_id, plan (free, monthly, search_pass), status, current_period_end, ended_at, vat_country, pay_what_you_can (bool) |
| `entitlements` | user_id, feature, granted_until, source (plan, guarantee_extension, org) |
| `guarantee_tracking` | user_id, pass_started_at, eligible (bool), conditions_state jsonb, extended_at |
| `organisations`, `org_members`, `org_cohorts` | name, kind; user_id, role; aggregated metrics only |

## Launch waitlist and private beta (Stage 4)

| Table | Key columns | Notes |
| --- | --- | --- |
| `waitlist_signups` | email (citext, unique), source, consent_text_version, created_at, notified_at | Deleted 30 days after the launch email, or on request |
| `beta_invites` | code_hash, wave (1, 2, 3), invited_email (encrypted, nullable), redeemed_by_user_id (nullable, CASCADE), redeemed_at, created_at | Invite-only sign-up until the launch gate |

## Fairness audit (Stage 11) — schema `sensitive`

| Table | Key columns | Notes |
| --- | --- | --- |
| `fairness_demographics` | user_id, gender, nationality_group, age_band, disability (all encrypted, all optional with "prefer not to say"), consent_version, recorded_at | Special category data. Separate schema, separate DB role, read only by the audit job, never joined in product code. Deleted on withdrawal |

## Indexes and performance notes

- `job_postings`: GIN index on `to_tsvector('english', title || ' ' || description)`;
  HNSW index on `embedding`; btree on `(country, posted_at desc)`, `canonical_id`.
- `application_events`: btree on `(application_id, occurred_at)` and `(user_id, type, occurred_at)`.
- `job_matches`: unique `(user_id, job_id, run_date)`.

## Extension local schema and import mapping (Track E)

The extension keeps its own data in the browser (IndexedDB), described in
`docs/16-chrome-extension.md` §7: an append-only event log (source of truth), derived application
views, captured jobs, companies, documents, profile, reminders, settings. It is not a server
database and is not in the data inventory while the local edition makes no network requests.

Mapping when Connect or "upload your export" arrives (Stage C): each extension event becomes one
platform `application_event` row (the ULID is kept as an idempotency key, `source` records that it
came from the extension, client time and schema version are stored); jobs map to the job and
company tables; CV versions map to the CV tables. **New tables for devices, pairing and import
batches must be added to this document and to `data_inventory.toml` in the same pull request, with
purpose, lawful basis, retention and erasure, before any code uses them.** (The privacy test
compares the two lists, so no placeholder table rows are added here.)
