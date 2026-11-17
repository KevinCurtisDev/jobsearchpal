# LIA 0002 · Service operation, error monitoring and AI cost control

**Status:** Draft — sign-off required before Stage 1 goes live.
**Categories:** `application_logs`, `ai_usage`

## 1. Purpose
Run and fix the service; stop any one account using an unfair share of paid AI calls.

## 2. Necessity
- Logs hold request ids and user ids only. Emails, names, IPs, CV text, email bodies and
  transcripts are removed by `app.privacy.redaction` before anything is written (tested).
- Sentry: EU region, `send_default_pii=False`, request bodies never sent.
- `ai_usage` holds counts and cost, never prompt or response text.

## 3. Balancing
Low impact, expected by users, short retention (logs 30 days, AI usage 400 days so a full
year of cost can be compared), anonymised on account deletion.

## 4. Outcome
Legitimate interests apply. Mention in the privacy notice.
