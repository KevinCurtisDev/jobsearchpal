# 10 · External APIs and data sources

Before integrating any source: read its current terms, rate limits, attribution and data
retention rules, and record them in the table's "Terms checked" column with a date.
Wrap every integration behind an interface in `backend/app/integrations/` with timeouts,
retries (tenacity, exponential backoff), circuit breaking, and recorded fixtures for tests (respx).

## Core services

| Service | Purpose | Stage | Env vars | Notes |
| --- | --- | --- | --- | --- |
| **Anthropic Claude API** | Writing tasks on request: CV wording, tailoring suggestions, cover letters, interview feedback, parse fallbacks | 2+ | `ANTHROPIC_API_KEY`, `AI_MODEL_WRITING`, `AI_MODEL_STRONG`, `AI_MONTHLY_BUDGET_EUR` | **Default: Haiku-class model** (Haiku 5.5 list price Oct 2026: $0.10 / $0.50 per million input/output tokens). Sonnet-class only where evals require. Batch API, prompt caching, result cache. Structured output; prompts in `prompts/`. Strip contact details. Check data-retention terms. |
| **Cloudflare Turnstile** | Human check on sign-up/sign-in | 1 | `TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET_KEY` | Free. Test keys exist for CI. Alternative: ALTCHA (self-hosted). |
| **Amazon SES (eu-west-1)** (default) *or* Postmark | Transactional email + inbound email for reply capture | 1, 8 | `EMAIL_PROVIDER`, `AWS_*` / `POSTMARK_SERVER_TOKEN`, `EMAIL_FROM`, `INBOUND_DOMAIN`, `INBOUND_WEBHOOK_SECRET` | SES about $0.10 per 1,000 sent and received (check plan; choose à la carte). Set up SPF, DKIM, DMARC. Inbound on a subdomain (e.g. `in.<domain>`). |
| **Stripe** | Checkout, subscriptions, customer portal, Stripe Tax (VAT) | 4 | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_PASS` | Webhooks idempotent. |
| **S3-compatible storage** | CV files, exports, practice audio | 2 | `S3_ENDPOINT`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_REGION` | Hetzner Object Storage or Cloudflare R2, EU. MinIO in dev. Lifecycle rule on `audio/`. |
| **Cloudflare Pages** | Hosting the built frontend | 0 | — | Free; site stays up if the API is down |
| **Sentry** (free tier) or self-hosted GlitchTip | Error tracking | 0 | `SENTRY_DSN`, `VITE_SENTRY_DSN` | EU data region; scrub PII. |
| Self-hosted **Umami** (or Plausible) | Cookieless analytics | 4 | `VITE_ANALYTICS_DOMAIN` | No cookies, no personal data. |

## Job sources (Stage 5)

| Source | Type | Coverage to verify | Env vars |
| --- | --- | --- | --- |
| Adzuna API | Aggregator | UK confirmed; check Ireland | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` |
| Jooble API | Aggregator | Check Ireland and UK | `JOOBLE_API_KEY` |
| Careerjet API | Aggregator | Check Ireland and UK; affiliate terms | `CAREERJET_AFFID` |
| Greenhouse Job Board API | Company careers boards | Public, per company board token | — |
| Lever Postings API | Company careers boards | Public, per company | — |
| Ashby Job Board API | Company careers boards | Public, per company | — |
| Workable widget/API | Company careers boards | Check terms per account | — |

**Not allowed:** scraping LinkedIn, Indeed, or Google's job listings; any source whose terms
prohibit automated access.

**LinkedIn profile feature (Stage 3):** uses no LinkedIn API and no automation. The user
downloads their own data from LinkedIn (Settings → Data privacy → Get a copy of your data) and
uploads the ZIP, or uploads "Save to PDF", or pastes text. We never ask for LinkedIn
credentials, never run extension code on linkedin.com (no reading, no injected UI, no automation; ADR 0008), and never post or edit on the
user's behalf. "Sign in with LinkedIn" is not offered.

## Public data (Stage 5+)

| Dataset | Use | Access |
| --- | --- | --- |
| UK Register of Licensed Sponsors: Workers (GOV.UK) | Visa sponsor badge | CSV download, refresh weekly |
| Ireland Critical Skills Occupations List (Dept. of Enterprise, Tourism and Employment) | Critical Skills badge | Published list; parse and review manually on change |
| Ireland employment permits issued by company (DETE statistics) | Permit history (past activity only) | Published statistics; refresh monthly |
| Companies House API (UK) | Registration status, company checks | Free API key: `COMPANIES_HOUSE_API_KEY` |
| CRO open data (Ireland) | Registration status | data.gov.ie datasets / CRO services; check terms |
| ESCO (EU skills taxonomy) | Skills matching, transferable skills | Download or API; CC BY |
| Indeed Hiring Lab job postings tracker (GitHub) | Market demand indicators (IE by county, UK by region) | CC BY 4.0 — cite the source |
| CSO PxStat API (Ireland) | Vacancies, earnings, employment | Open data API |
| ONS API (UK), Eurostat | Earnings, vacancies | Open data APIs |
| OpenStreetMap + OSRM / OpenTripPlanner, TFI GTFS (Ireland) | Commute time | Self-hosted routing; respect OSM attribution |
| `disposable-email-domains` list | Sign-up protection | GitHub list, refresh weekly |
| Irish and UK income tax / USC / PRSI / NI tables | Offer take-home calculator | Maintain yearly in `content/tax_tables/` |

## Self-hosted models (no external calls)

| Model | Use |
| --- | --- |
| sentence-transformers small multilingual embedding model | Job and CV embeddings (pgvector) |
| faster-whisper (English) | Practice recording transcription |
| scikit-learn / LightGBM models | Classifiers, rankers (trained in-house) |

## Later (not at launch)

| Service | Use | Notes |
| --- | --- | --- |
| Gmail API / Microsoft Graph | Direct inbox connection for reply capture | Requires Google/Microsoft app verification; Gmail restricted scopes need a recurring paid security assessment |
| SSO (SAML/OIDC) | Organisation accounts | Stage 12 |

## Chrome extension (Track E)

| Service | Purpose | Notes |
| --- | --- | --- |
| Chrome Web Store developer account | Publish the extension | One-time registration fee (currently US$5; verify). Dedicated account with hardware keys. EU trader status is decision #26 |
| Edge Add-ons | Same MV3 package for Edge | Phase after E2; free |
| Employer ATS pages (Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Teamtailor, Personio, Workday) | Read the job page the user is viewing | No API calls and no crawling. Record a per-site terms check and date here before enabling each adapter |
| Public data packs (UK sponsor register, Irish Critical Skills list, ESCO-lite, tax tables) | Bundled into releases | Same sources as above; attribution for ESCO (CC BY); "last updated" shown in the UI |

The local extension edition calls no external service at runtime.
