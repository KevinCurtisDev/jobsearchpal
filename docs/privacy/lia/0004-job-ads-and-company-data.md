# LIA 0004 · Job ads, company data and scam reports

**Status:** Draft — sign-off required before Stage 5 launches.
**Categories:** `public_job_ads`, `public_job_ads_raw`, `user_reports`

## 1. Purpose
Show job ads from licensed APIs and public ATS boards; detect fake ads; let users report scams.
Some ads name a recruiter or hiring manager.

## 2. Necessity
- Sources are only those in `docs/10-external-apis.md` whose terms allow it. No LinkedIn scraping.
- Raw payloads 30 days; ads 365 days after last seen (needed for repost and "ghost job" signals).
- Recruiter names are never extracted into separate fields or used for profiling.
- Scam report text is redacted on save; reporter identity removed on account deletion.

## 3. Balancing
The ad was published by the employer for exactly this purpose: to reach job seekers.
Impact on named recruiters is minimal. Scam flags are about ads and companies (legal
persons), reviewed by a human before any public label (right-of-reply process, decision #13).

## 4. Outcome
Legitimate interests apply. Recruiters can use the employer section of the privacy notice
to object or ask for erasure (manual DSAR).
