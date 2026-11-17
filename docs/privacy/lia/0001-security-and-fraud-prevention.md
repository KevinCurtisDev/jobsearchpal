# LIA 0001 · Security, fraud and bot prevention

**Status:** Draft — owner and solicitor/DPO sign-off required before Stage 1 goes live.
**Categories:** `sessions`, `transient_auth`, `security_audit`

## 1. Purpose test
- Keep accounts secure: sessions, device list, new-device alerts, step-up checks.
- Stop automated and AI-driven sign-ups that would abuse paid AI features and pollute statistics.
- Investigate security incidents and show that rights requests were handled.
- Recital 49 GDPR recognises network and information security as a legitimate interest.

## 2. Necessity test
| Data | Why it is needed | Less intrusive alternative considered |
| --- | --- | --- |
| Keyed hash of IP (never the raw IP) | Rate limits, spotting attacks from one source | Raw IP — rejected; no IP — rejected (no rate limiting) |
| User agent, device label | Let users recognise and revoke devices | None that keeps the device list useful |
| One-time codes (hashed), challenges | Verify email ownership; passkey ceremonies | — |
| Audit events (ids and counts only) | Investigate account takeover; prove handling of requests | Shorter retention — 12 months chosen to cover a yearly review cycle |

## 3. Balancing test
- **Reasonable expectations:** people expect a service to protect their account.
- **Impact:** low — hashed identifiers, no profiling, no marketing use, no sharing.
- **Safeguards:** keyed hashes with a secret pepper; 90-day session records; 1-hour transient
  data; 12-month audit log anonymised on account deletion; access limited to owners.
- **Vulnerable people:** none specifically affected.

## 4. Outcome
Legitimate interests apply. Explain in the privacy notice (section "Keeping your account safe").
Right to object: handled case by case; security logging cannot be switched off for an active account.
