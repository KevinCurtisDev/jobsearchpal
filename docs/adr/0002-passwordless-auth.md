# ADR 0002 · Passwordless authentication

**Status:** Accepted · 2026-10-20

## Context
Job seekers store CVs, employment history and interview recordings. Passwords are the most
common cause of account takeover (reuse, phishing). Bots and automated agents create fake
accounts to abuse paid AI features.

## Decision
- No passwords. Passkeys (WebAuthn, user verification required) as the primary method;
  email one-time code plus magic link for first sign-in, new devices and recovery.
- Server-side opaque sessions in secure `__Host-` cookies; step-up for sensitive actions.
- Layered bot protection: Turnstile, honeypot, timing, rate limits, disposable-domain
  blocking, email verification before activation, AI-usage quotas.

## Consequences
- Phishing-resistant sign-in for most users; no password storage or reset flows to secure.
- Email becomes the recovery channel — its security matters (anti-phishing copy, short TTLs,
  link bound to the requesting browser).
- The WebAuthn `rp_id` is tied to the final domain: choose the domain before Stage 1.
