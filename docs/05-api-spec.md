# 05 · API specification

The source of truth is FastAPI's generated OpenAPI schema (`/api/openapi.json`, docs at
`/api/docs` in development only). This document defines conventions and the endpoint plan;
keep it in sync when you add endpoints.

## Conventions

- Base path: `/api/v1`. JSON only. UTF-8.
- **Auth:** session cookie `__Host-ol_session` (HttpOnly, Secure, SameSite=Lax, Path=/).
  No bearer tokens for the browser app.
- **CSRF:** every state-changing request (POST, PUT, PATCH, DELETE) must send header
  `X-CSRF-Token` matching the `__Host-ol_csrf` cookie (double-submit). Requests without it get 403.
- **Errors:** RFC 9457 `application/problem+json`: `type`, `title`, `status`, `detail`,
  `instance`, plus `errors` for field validation. Never leak stack traces or internal ids.
- **Pagination:** cursor based: `?limit=20&cursor=<opaque>` → `{ items, next_cursor }`.
- **Idempotency:** `Idempotency-Key` header on payment and other non-repeatable POSTs.
- **Rate limits:** `429` with `Retry-After`. Limits per route in `06-security.md`.
- **Scores:** any score in a response uses this shape:

```json
{
  "value": 0.41,
  "kind": "probability | score",
  "confidence": "high | medium | low",
  "source": "your_data | offerlight_data | public_data",
  "reasons": [{"label": "SQL, Power BI and A/B testing match", "direction": "raises", "weight": 0.12}],
  "n": 38,
  "model_version": "matcher-v0.3"
}
```

- **Effects** (insights) use: `estimate`, `ci_low`, `ci_high`, `unit`, `confidence`, `method`, `n`.

## Endpoints

### Health
| Method | Path | Notes |
| --- | --- | --- |
| GET | `/health` | Liveness |
| GET | `/ready` | DB + Redis readiness |

### Auth (Stage 1)
| Method | Path | Body / notes |
| --- | --- | --- |
| POST | `/auth/email/start` | `{email, turnstile_token, website (honeypot), form_started_at, intent: signin|signup, terms_version?}` → always `202 {sent: true}` |
| POST | `/auth/email/verify` | `{email, code}` or `{token}` (magic link) → sets session cookie; `{user, is_new, offer_passkey}` |
| POST | `/auth/passkey/register/options` | Auth required (or step-up) → WebAuthn creation options |
| POST | `/auth/passkey/register/verify` | Attestation response → stores credential |
| POST | `/auth/passkey/login/options` | `{email?}` → request options (empty allowCredentials for discoverable / conditional UI) |
| POST | `/auth/passkey/login/verify` | Assertion response → session cookie |
| POST | `/auth/step-up` | Passkey assertion or email code → marks session step-up for 10 minutes |
| POST | `/auth/logout` | Revokes current session |
| GET | `/auth/me` | Current user, plan, flags |
| GET | `/auth/sessions` | Signed-in devices |
| DELETE | `/auth/sessions/{id}` | Sign out a device (step-up not required) |
| POST | `/auth/sessions/revoke-others` | Sign out everywhere else |
| GET | `/auth/passkeys` | List |
| PATCH | `/auth/passkeys/{id}` | Rename |
| DELETE | `/auth/passkeys/{id}` | Step-up required; cannot remove the last credential if email sign-in disabled |

### Privacy and settings (Stage 1)
| Method | Path | Notes |
| --- | --- | --- |
| GET/PUT | `/me/consents` | Current consent state; PUT appends history |
| GET/PUT | `/me/preferences` | Job preferences, digest time |
| POST | `/me/export` | Starts async export → email with time-limited download link |
| DELETE | `/me` | Step-up required → status `deleting`, hard delete job in ≤ 30 days |

### CV (Stage 2–3)
| Method | Path | Notes |
| --- | --- | --- |
| POST | `/files/cv-upload` | Multipart, ≤ 5 MB, PDF/DOCX → `{file_id, parse_job_id}` |
| GET | `/jobs/{job_id}/status` | Background job status |
| GET/POST | `/cvs` | List / create document |
| GET | `/cvs/{id}/versions` | Versions |
| POST | `/cvs/{id}/versions` | New version from edited content (validated against schema) |
| GET | `/cv-versions/{id}` | Content + open suggestions |
| POST | `/cv-versions/{id}/check` | Run writing checker → suggestions |
| POST | `/cv-versions/{id}/improve` | AI wording suggestions (quota) |
| PATCH | `/suggestions/{id}` | accept / dismiss |
| POST | `/cv-versions/{id}/export` | `{format: pdf|docx, template}` → file + ATS check |
| POST | `/tailor/parse` | `{text | url}` → parsed requirements |
| POST | `/tailor/match` | `{cv_version_id, parse_id}` → matched, missing (with evidence) |
| POST | `/tailor/suggest` | → diff suggestions (quota) |

### LinkedIn profile (Stage 3)
| Method | Path | Notes |
| --- | --- | --- |
| POST | `/linkedin/import` | Multipart `{file}` (ZIP ≤ 20 MB or PDF ≤ 5 MB) or JSON `{headline, about, positions[], skills[]}`; processed in memory → profile + `{files_read, files_ignored}` |
| GET | `/linkedin` | Current imported profile, checklist findings, consistency findings (with `cv_version_id` query) |
| DELETE | `/linkedin` | Delete the imported copy and its suggestions |
| POST | `/linkedin/rewrite` | `{cv_version_id, target_role, confirmed_skills[]}` → suggestions (quota) |
| PATCH | `/linkedin/suggestions/{id}` | `{status: copied | dismissed}` |
| GET | `/linkedin/keyword-gap` | `{role_family}` → gaps, n_ads, confidence, reason (Stage 5+) |
| POST | `/public/linkedin-check` | No account; `{headline, about, turnstile_token}` → checklist only; nothing stored |

### Jobs and matching (Stage 5–6)
| Method | Path | Notes |
| --- | --- | --- |
| GET | `/matches?date=today` | Ranked matches with score objects and badges; filters: `visa_only`, `hide_flagged` |
| GET | `/job-postings/{id}` | Detail, reasons, company reply stats, visa data, flags |
| POST | `/job-postings/{id}/save` | |
| POST | `/job-postings/{id}/dismiss` | `{reason?}` |
| POST | `/job-postings/{id}/report` | `{reason, details}` |
| GET | `/companies/{id}/reply-stats` | KM curve points, competing outcomes, confidence |

### Applications (Stage 7–8)
| Method | Path | Notes |
| --- | --- | --- |
| GET/POST | `/applications` | Board data / manual add |
| PATCH | `/applications/{id}` | Status change → writes event |
| POST | `/applications/{id}/events` | Log follow-up, interview, outcome |
| GET | `/applications/{id}/assist` | Assisted-apply bundle: CV version, cover letter draft, screening answers |
| POST | `/applications/{id}/agency-submissions` | Record agency submission |
| GET | `/applications/{id}/rejection` | Honest rejection assessment |
| POST | `/rejections/{id}/feedback` | `{helpful: bool}` |
| GET | `/me/inbound-address` | Forwarding address |
| POST | `/webhooks/inbound-email` | Provider webhook, signature verified, no session |
| POST | `/webhooks/stripe` | Stripe webhook, signature verified |

### Stage odds (Stage 7)
| Method | Path | Notes |
| --- | --- | --- |
| GET | `/applications/odds` | `{p_at_least_one_offer, expected_offers, active, biggest_contributor, per_stage[], source, confidence, reason, next_step}` |
| GET | `/applications/{id}/progress` | `{stage, ladder[], message, source, confidence}` |
| GET | `/public/hiring-stages` | The published benchmarks and sources behind the guide (cached) |

### Insights (Stage 9)
| Method | Path |
| --- | --- |
| GET | `/insights/where-you-stand` |
| GET | `/insights/what-works` |
| GET/POST | `/experiments/cv-ab` |
| GET | `/insights/reply-timing?role_family=` |

### Interview prep (Stage 10)
| Method | Path | Notes |
| --- | --- | --- |
| GET/POST/PATCH/DELETE | `/stories` | STAR stories; response includes checks + coverage |
| GET | `/stories/coverage` | Competency coverage map |
| GET/PUT | `/pitches?application_id=&length=` | Elevator pitch |
| GET | `/interview-questions/core` | From `content/core_questions.json` + user prep status |
| GET | `/interview-questions/role?application_id=` | Role-specific |
| POST | `/practice-sessions` | `{mode, question_key}` |
| POST | `/practice-sessions/{id}/recording-url` | Pre-signed S3 PUT (short TTL, size cap, content-type fixed) |
| POST | `/practice-sessions/{id}/recording-complete` | Starts transcription + metrics |
| GET | `/practice-sessions/{id}` | Transcript, metrics, feedback |
| POST | `/practice-sessions/{id}/feedback` | AI content feedback (quota) |
| PATCH | `/recordings/{id}` | `{keep: bool}` |
| GET/POST | `/interviews` | Records, checklist, notes |
| POST | `/offers/compare` | Take-home and commute comparison |

### Billing (Stage 4)
| Method | Path |
| --- | --- |
| POST | `/billing/checkout` |
| POST | `/billing/portal` |
| GET | `/billing/entitlements` |

### Connect (Stage C and Track E4; not built until approved)

Planned only. All routes are rate limited, idempotent, and consent-checked.

- `POST /api/v1/connect/pairing-code` (signed-in web session): returns a short-lived one-time code.
- `POST /api/v1/connect/pair`: the extension exchanges the code for a **device token** (scoped,
  revocable, stored hashed). Bearer device tokens are used only by paired extensions; the browser
  app keeps cookie sessions and CSRF as above.
- `POST /api/v1/import/events`: batch of events from an export or a paired device; ULIDs make it
  idempotent; schema validated by the shared zod/JSON schema; returns counts accepted and skipped.
- `POST /api/v1/import/preview` (no account): validates an export file and returns nothing stored;
  insights are computed in the browser.
- `GET /api/v1/connect/devices`, `DELETE /api/v1/connect/devices/{id}`: list and revoke.
- `GET /api/v1/data-packs/{name}`: later; returns data (never code) such as fresher sponsor lists
  and adapter selector updates, signed.
