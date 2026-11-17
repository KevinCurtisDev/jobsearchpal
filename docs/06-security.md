# 06 · Security

Target: **OWASP ASVS 4.0 Level 2** for the web app and API, plus the OWASP Top 10 for LLM
applications for AI features. An independent penetration test happens before public launch
(Stage 4) and yearly after.

## 1. Authentication: passwordless

There are **no passwords**. Two methods:

1. **Passkeys (WebAuthn / FIDO2)** — primary. Phishing-resistant, bound to our domain.
2. **Email one-time code + magic link** — for first sign-in, new devices and recovery.

### 1.1 Passkeys

Library: `webauthn` (py_webauthn) on the server, `@simplewebauthn/browser` in the browser.

| Setting | Value |
| --- | --- |
| `rp_id` | The registrable domain, e.g. `offerlight.example` (env `WEBAUTHN_RP_ID`) |
| `rp_name` | `Offerlight` |
| Expected origin | `https://app.<domain>` and `https://<domain>` (env `WEBAUTHN_ORIGINS`) |
| `user_verification` | `required` (biometric or device PIN) |
| `resident_key` | `preferred` (discoverable credentials enable autofill sign-in) |
| `attestation` | `none` (privacy; we don't need device make) |
| Algorithms | ES256 (-7), then RS256 (-257) |
| Challenge | 32 random bytes, stored in Redis keyed to the browser's pre-auth cookie, 5-minute TTL, single use |
| `user.id` | Random 64-byte handle per user (not the email, not the DB id) |
| Sign count | Store and check; if a non-zero counter goes backwards, flag the credential and alert |
| Conditional UI | Email field has `autocomplete="username webauthn"`; call `startAuthentication({ useBrowserAutofill: true })` on page load |

Registration is offered right after the first email-code sign-in and in Settings. Removing a
passkey or adding one from Settings requires step-up.

### 1.2 Email one-time code and magic link

| Rule | Value |
| --- | --- |
| Code | 6 digits from `secrets.randbelow`, stored as HMAC-SHA256 with server pepper (`AUTH_CODE_PEPPER`) |
| Magic link token | 32 random bytes (base64url), stored hashed, single use |
| Expiry | 10 minutes for both; one active code per email (new request invalidates the old) |
| Attempts | Max 5 wrong codes per issued code, then it is burned |
| Sends | Max 3 per email per 15 minutes; max 10 per IP per hour; resend button disabled 60 s |
| Response | `/auth/email/start` always returns `202 {sent: true}` with constant-time handling, whether or not the account exists (no account enumeration) |
| Comparison | `hmac.compare_digest` |
| Link binding | The magic link only signs in on the browser that requested it (checks the pre-auth cookie); otherwise it asks for the code. This blocks forwarded-link phishing. |
| Email content | States the domain, never asks the user to share the code, includes "wasn't you?" guidance |

### 1.3 Sessions

| Rule | Value |
| --- | --- |
| Token | 32 random bytes; only its SHA-256 hash is stored (`sessions.token_hash`) |
| Cookie | `__Host-ol_session`; `Secure; HttpOnly; SameSite=Lax; Path=/` |
| Idle timeout | 14 days (sliding) |
| Absolute timeout | 60 days |
| Rotation | New token on every sign-in and step-up; old revoked |
| Step-up | Fresh passkey assertion or email code within the last 10 minutes for: delete account, export data, add/remove passkey, change email |
| Device list | Users see and revoke sessions; "sign out of all other devices" |
| Alerts | Email on sign-in from a new device |

### 1.4 CSRF

SameSite=Lax cookies **plus** double-submit token: `__Host-ol_csrf` cookie (not HttpOnly) is
echoed in `X-CSRF-Token` on state-changing requests. Webhooks are exempt but verify signatures.

## 2. Bot and automated (including AI agent) sign-up protection

Layered, so no single bypass works:

| Layer | Implementation |
| --- | --- |
| Human check | **Cloudflare Turnstile** (privacy-friendly, usually invisible). Verify server-side at `https://challenges.cloudflare.com/turnstile/v0/siteverify`; check `success`, `hostname`, `action` (`signup`/`signin`) and token age. Fail closed in production. Alternative if Cloudflare is not wanted: ALTCHA (self-hosted proof of work). |
| Honeypot | Hidden `website` field (off-screen, `tabindex=-1`, `aria-hidden`); any value → silent reject |
| Form timing | Reject submissions under 2 seconds after the form rendered (`form_started_at`, signed) |
| Rate limits | Redis sliding windows per IP, per /24 (IPv4) or /64 (IPv6), per email, per ASN; stricter on `/auth/*` |
| Email quality | Syntax (email-validator), MX record exists (dnspython), disposable-domain blocklist (`disposable-email-domains` list, refreshed weekly), plus-address normalisation for rate limits |
| Verification | Account stays `pending` until the email code/link is used; pending accounts expire after 24 h |
| Velocity alerts | Alert when sign-ups per hour exceed 3× the 7-day baseline; admin can turn on "challenge everyone" |
| Paid-feature quotas | Per-account daily quotas on AI endpoints and exports; new accounts get lower quotas for 7 days |
| Passkeys | User verification required, which a headless agent cannot satisfy without a real authenticator |

Log every rejection reason (without personal data) for tuning.

## 3. Security headers and CSP

Set in Caddy (production) and FastAPI middleware (API responses, dev):

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' https://challenges.cloudflare.com; style-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; font-src 'self'; connect-src 'self' https://<s3-bucket-host>; frame-src https://challenges.cloudflare.com https://js.stripe.com; frame-ancestors 'none'; form-action 'self'; base-uri 'none'; object-src 'none'; upgrade-insecure-requests
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(self), microphone=(self), geolocation=(), payment=(self "https://js.stripe.com"), usb=(), interest-cohort=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-site
```

No inline scripts. If Stripe.js is added, extend `script-src` and `frame-src` narrowly.

## 4. Rate limits (starting values)

| Route group | Limit |
| --- | --- |
| `/auth/email/start` | 3 / 15 min per email; 10 / h per IP |
| `/auth/email/verify` | 10 / 15 min per IP; 5 wrong attempts per code |
| `/auth/passkey/*` | 30 / 15 min per IP |
| AI endpoints (`improve`, `suggest`, `feedback`, cover letters) | Plan-based daily quota + 20 / min per user |
| Uploads | 20 / h per user |
| Everything else | 300 / min per user, 100 / min per IP unauthenticated |

## 5. Data protection

- TLS 1.2+ everywhere (Caddy automatic HTTPS). Internal traffic on private networks.
- Encryption at rest: managed database and bucket encryption. Field-level encryption
  (`cryptography` Fernet / AES-GCM with keys from the secret manager) for: inbound email
  bodies, fairness-audit demographics (separate table and key), interview recordings' transcripts.
- Personal data never in logs. Log user ids, not emails. Hash IPs with a rotating salt.
- Backups encrypted, tested monthly by restoring to staging.

## 6. Files and uploads

- Max 5 MB for CVs; 20 MB and 5 minutes for practice audio (video never leaves the browser).
- Check type by magic bytes (`python-magic`), not extension. Accept PDF and DOCX only for CVs.
- Reject DOCX with macros (`.docm` content types) and PDFs with JavaScript/launch actions.
- Parse in a separate subprocess with CPU/memory limits and a 20 s timeout.
- Optional ClamAV scan (`clamd` container) before parsing.
- Store in a private bucket under random keys; serve via short-lived pre-signed URLs (5 min).
- Practice audio: upload directly from the browser with a pre-signed PUT restricted to size and
  content type; deleted after transcription unless `keep=true`, with a 30-day lifecycle rule as backstop.

## 7. Outbound requests (SSRF)

Job URL fetching and any user-supplied URL: allowlist of job-board and careers domains,
resolve DNS and block private, loopback, link-local and metadata IP ranges, no redirects to
non-allowlisted hosts, 5 s timeout, 2 MB response cap.

## 8. AI (LLM) security

- CVs, job descriptions and emails are **untrusted input**. Wrap them in clear delimiters and
  tell the model to treat them as data. Never give the model tools or the ability to act.
- Require structured output (JSON matching a schema); validate it; reject on failure.
- **No-invention guard** (see `prompts/README.md`): compare entities in output vs input.
- Send the minimum personal data: strip contact details before sending CV text to the AI API.
- Per-user quotas and a global monthly cost cap with alerting.
- Record `model`, prompt version and token usage per call (`ai_usage` table).
- Check the AI provider's data-retention and training terms and record them in the
  sub-processor list.

## 9. Supply chain and code security

- GitHub: branch protection, required reviews, signed commits recommended, secret scanning
  with push protection, Dependabot (security + version updates), CodeQL (Python + JS/TS).
- CI: `pip-audit`, `npm audit --audit-level=high`, `gitleaks`, Trivy image scan,
  OWASP ZAP baseline against staging.
- Images: slim base images, non-root user, read-only root filesystem where possible,
  pinned by digest in production.
- Secrets: never in the repo. Local `.env`; production from the host's secret manager.

## 10. Admin access

Separate admin role; passkey-only sign-in; access to personal data logged in `audit_log`;
least privilege; no shared accounts.

## 11. Recordings and video practice

Video is recorded and played back only in the user's browser and never uploaded. Only audio is
uploaded for transcription; it is encrypted at rest, deleted after processing unless kept, never
used for model training. No analysis of faces, emotions or appearance.

## 12. Incident response (summary)

Severity levels, on-call contact, containment steps, user notification, and the 72-hour GDPR
breach notification to the Data Protection Commission when required. Full runbook in
`12-deployment-and-ops.md`.

## Security checklist for every PR touching auth, uploads, external calls or personal data

- [ ] Input validated with Pydantic; sizes and types limited
- [ ] AuthZ checked: the user owns the resource (no IDOR)
- [ ] Rate limit applied
- [ ] No personal data in logs or error messages
- [ ] CSRF enforced for state changes
- [ ] Outbound calls have timeouts and SSRF protection
- [ ] Tests cover the failure and abuse cases

## 13. Extension and Connect security (Track E)

Full list: `docs/16-chrome-extension.md` §10. Summary:

- Page content is hostile input: extract text, render with `textContent`, validate every message with
  zod, check sender, no `externally_connectable`, no `web_accessible_resources` unless essential.
- `chrome.storage.local.setAccessLevel('TRUSTED_CONTEXTS')` so content scripts cannot read the store.
- Device tokens (Connect): random, scoped to import and read-own-data, stored hashed, revocable in
  Settings, rotated on re-pairing, never logged. Pairing codes are single use and expire in minutes.
- Publisher account: dedicated Google account, hardware keys, recovery tested; store takeover is
  the largest extension risk. Reproducible builds; signed release tags.
- CI network audit and permission diff (docs/16 §6.3) are required checks on `main`.
