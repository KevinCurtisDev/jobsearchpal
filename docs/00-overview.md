# 00 · Product overview

## Mission

**Built for offers received, not applications submitted.** Most job tools measure how many
applications a user sends. Offerlight measures what gets people interviews and offers, and shows
the evidence. Promise to users: *other tools guess what might work; we measure what actually
worked, for people like you.*

Launch market: **Ireland**, then the **UK**. Local CV conventions, job sources and visa rules are
poorly served by US-built tools.

Source documents (owned by the product team):
- Concept overview doc (Claude Docs): https://claude.ai/code/artifact/c7e7c2a6-9a2e-48b9-802b-c765515b6416
- Design canvas: see `design/README.md`

## Extension first (from 17 November 2026)

Hearback is built in two layers, in this order:

1. **The Chrome extension** (`docs/16-chrome-extension.md`): free for life, no account, no AI, no
   server, all data on the user's device. It tracks applications as people apply, checks CVs and
   job postings with rules, and gives honest odds. It is also the front door to the platform.
2. **The platform** (this repo's stages): the account layer on top. Connect (import and sync),
   then the features that cost server money: job feed, reply capture, AI writing, practice transcripts.

Promise: *if it runs on your computer, it is free, and it stays free. You pay only for what costs
us money to run.* The extension and platform share one rules library (`packages/core`) and one
event schema, so a user's history moves between them without loss.

## The loop

```
Build the CV → Find matched jobs → Apply with tailored materials → Track outcomes → Learn what works
      ↑                                                                                   │
      └───────────────────────────── evidence feeds back ─────────────────────────────────┘
```

## Product areas

| Area | What it does | Build stage |
| --- | --- | --- |
| Chrome extension (first product) | Local tracker, job-page checks, CV tools, reminders, backup; no account, no AI, no network | Track E (E0 to E3) |
| Connect | Import extension history, sync, consented benchmarks, then optional AI edition | Stage C, Track E4 |
| Accounts and security | Passkeys, email codes, bot protection, sessions, privacy controls | 1 |
| CV builder | Upload or build, ATS-safe templates, local conventions, writing checker, screening self-check | 2 |
| Tailor to a job | Matched and missing requirements, honest gap report, suggested edits as diffs | 3 |
| LinkedIn profile | Import your own LinkedIn data export (no scraping, no login), profile checklist, CV ↔ LinkedIn consistency check, copy-ready rewrite; keyword gap against real job ads from Stage 5 | 3 (gap: 5) |
| Marketing site and billing | Landing page, pricing, Stripe, pay what you can, interview guarantee tracking | 4 |
| Job ingestion | Aggregator APIs and company careers boards, de-duplication, company resolution, visa data | 5 |
| Matching and daily digest | Ranked matches with reasons, visa badges, fake job flags, morning email | 6 |
| Assisted apply and tracker | Tailored CV + cover letter + screening answers, application board, agency tracking, reconnect and repitch | 7 |
| Reply capture and honest rejection | Forwarding inbox, reply classification, auto-rejection likelihood, company reply curves and badges | 8 |
| Insights | Where you stand, what works for you, CV A/B tester | 9 |
| Interview prep | STAR stories, competency coverage, elevator pitch, core questions, mock interviews, video practice, offer comparison | 10 |
| Learned models | Ranker, scam classifier, uplift models, bandits — switched on as data allows | 11 |
| Organisations | Accounts for universities, migrant-support groups, outplacement | 12 |

## Principles (also in CLAUDE.md)

1. Rules and data decide, AI writes.
2. Explained, calibrated, causal where it matters, honest about uncertainty.
3. The user stays in control: no auto-apply, no invented experience.
4. Privacy as a feature: never sell data, one-click export and delete.
5. Accessible to WCAG 2.2 AA.
6. Badges are earned, never bought.

## What we deliberately won't do

- No auto-apply bots
- No LinkedIn scraping
- No invented experience
- No live interview "copilots" (practice only)
- No face or emotion analysis
- No selling data, no badges for sale
- No extension code on LinkedIn, Indeed or Glassdoor; no autofill of diversity or health fields; no submitting forms for the user
- No unexplained scores

## Users

Primary persona used in the designs: **Aoife Byrne**, data analyst, Dublin, six years'
experience, Stamp 4 (no sponsorship needed). Other key groups: graduates, career changers,
returners, people new to Ireland who need visa clarity, people recently laid off.

## Business model (summary)

- Free for life: everything that runs on the user's device (the extension: tracker, CV and job-page checks, visa badges, suspicious-listing signals, reminders, backup) plus a free platform account for Connect (import, sync)
- Paid (server cost): job feed and matches, reply capture, AI writing, practice transcripts, advanced insights from cohort data
- Free / pay-what-you-can tier (CV tools, visa badges, fake job flags, tracker)
- Monthly €19, or Search pass €45 for 3 months with an interview guarantee (conditions TBC)
- Organisation contracts: universities, migrant-support organisations, outplacement, public
  employment services — target 30–50% of revenue
- Prices include Irish VAT (23%)
