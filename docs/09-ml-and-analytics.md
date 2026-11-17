# 09 · ML and analytics

**Principle:** rules and data decide, AI writes. Methods in order of preference:
1. Rules, templates, curated data
2. Classical statistics and information retrieval
3. Classical machine learning on our own servers
4. Generative AI — writing, messy text, judging interview answers only

**Four rules for every score:** explained (reasons), calibrated (85% means 85%), causal where
advice is given, honest about uncertainty (confidence + source label).

## Data maturity gates

Models switch on behind feature flags only when their gate is met. Until then the v0 method runs,
and the UI shows the waiting-on-data state from `app/insights/readiness.py` (see
`02-build-stages.md` §Waiting-on-data features).

| Model | v0 (launch) | Gate to switch on v1/v2 |
| --- | --- | --- |
| Reply classifier | Rules (sender domains, phrases) | ≥ 1,000 user-confirmed labels |
| Auto-rejection likelihood | Rules on timing/sender/template, shown as "likely / possibly / unlikely" | ≥ 500 labelled rejections; calibration error < 5 pts |
| Company reply curves | Sector priors from public/aggregate data | Per company: ≥ 15 tracked applications to show a badge |
| Funnel benchmarks | Published external figures, labelled "public data" | Cohort ≥ 200 users |
| Matching | Weighted rules → "score" (not probability) | ≥ 20,000 applications with outcomes → LightGBM ranker + calibration |
| Fake job detection | Rules | ≥ 300 verified reports → classifier |
| What-works effects | Stratified comparisons + randomised tests | Uplift models when ≥ 5,000 treated + control applications per action |
| Bandits | Off | Ranker live and stable for 8 weeks |

## Data pipeline (Stage 5)

- **Near-duplicates:** MinHash (128 permutations) over 5-word shingles of normalised
  title + company + description; LSH bands tuned for Jaccard ≥ 0.8; canonical job = earliest.
- **Company entity resolution:** normalise names (strip Ltd/Limited/DAC/PLC/UC, punctuation),
  block on first token + country, score with RapidFuzz `token_set_ratio` + domain match +
  registry id; auto-merge ≥ 95, review queue 85–95.
- **Topic trends:** NMF on TF-IDF of listings per month for market indicators.

## Tailoring (Stage 3)

- Requirement extraction: rules (bullets under "Requirements"/"Essential"/"Nice to have",
  modal verbs) + AI fallback with schema.
- Matching: BM25 between each requirement and CV lines + ESCO synonyms; a requirement is
  "shown" when score ≥ threshold **and** evidence line exists. Show the evidence line.
- AI suggestions limited to rewording and reordering existing content (no-invention guard).

## Stage odds and encouragement (Stage 7 v0; Stage 9 v1)

- v0: `app/insights/stage_odds.py` with published pass rates in `content/hiring_stages.json`
  (Gem: application→screen 8%, screen→final 33%, final→offer 45%). P(offer | stage) is the
  product of the remaining pass rates. Source "public", confidence "low".
- Pipeline: P(at least one offer) = 1 − Π(1 − p_stage)^n_stage, assuming independence (a
  simplification, which is why confidence stays ≤ medium); expected offers = Σ n·p.
- v1 (Stage 9): Hearback pass rates per role family and seniority, beta-binomial shrinkage
  towards the public prior; switch per cohort when n ≥ 200 tracked applications at that
  stage; company-level only above the badge minimum (decision #13). Source "Hearback data".
- Behavioural design rules (the psychology, applied honestly):
  - **Progress framing:** show how much a stage improved the odds ("about 12 times better"),
    not how low they are. Low starting odds are shown once, next to the reason (it's the same
    for everyone), so a rejection is normalised rather than personal.
  - **Goal gradient:** the ladder shows how close each application is to an offer.
  - **One next step:** a single, concrete, controllable action per view (implementation
    intention), never a list of chores.
  - **Effort where it counts:** messages point to the controllable lever for that stage
    (fit and quality at application, preparation at interview).
  - **Never:** streaks, guilt, loss framing, countdowns, leaderboards, or odds shown as a
    personal prediction. Always the source and confidence.

## LinkedIn profile (Stage 3, gap from Stage 5)

No model to train; everything except the rewrite is rules and counts.
- Checklist: rules in `content/linkedin_rules.json` (limits, missing sections, first-line
  length, third person, clichés).
- CV ↔ LinkedIn consistency: employer matching on normalised names (legal suffixes removed)
  with a similarity threshold (0.85; titles 0.75), then year-level date comparison.
- Keyword gap: share of recent ads (90 days, per role family) requiring each ESCO skill
  (`role_skill_demand`, computed nightly). Suggest skills in ≥ 20% of ads that the profile
  never mentions; skills already on the CV first ("honest, easy win"); others phrased as
  "if you have this". Hidden under 30 ads; confidence low < 100, medium < 300, high ≥ 300.
- We never claim an effect on profile views (LinkedIn's ranking is not public). Measure
  instead with the tracker's "LinkedIn — recruiter approached me" source.

## Matching (Stage 6, 11)

1. Hard filters: location/commute, remote type, salary floor, excluded companies, visa needs.
2. Retrieval: Postgres full-text (BM25-like `ts_rank_cd`) top 200 + pgvector cosine top 200
   (embeddings: small multilingual sentence-transformers model, self-hosted) → reciprocal rank
   fusion (k = 60).
3. Scoring v0: weighted features with fixed weights → reasons from the top contributing features.
4. Scoring v1: LightGBM LambdaMART on labels (applied < replied < interviewed < offered);
   SHAP values → top 3 raises / lowers; Platt or isotonic calibration on "reply within 21 days".
5. Monitoring: Brier score, reliability curve, NDCG@10 offline; PSI on top features weekly.

## Fake job detection (Stage 6, 11)

Features: repost count (90 days), posting age vs role median, salary z-score vs market,
salary disclosed, company registry match/status, domain age, email domain free-mail,
urgency phrases, payment/training-fee phrases, user reports. v0 rules with reasons; v1
gradient boosting + Isolation Forest for novelty; SHAP reasons. Public report names a company
**only** when a scam is verified and legally reviewed.

## Replies and the honest rejection (Stage 8)

- Classifier v1: TF-IDF (word 1–2 grams + char 3–5 grams) + logistic regression, class weights;
  labels: rejection, interview_invite, assessment, info_request, other.
- Auto-rejection features: minutes from apply to reply, local send hour, weekend, sender is
  no-reply / hiring-system domain, template similarity (MinHash vs known templates), body length.
- Calibration: isotonic regression on held-out data. Display: "Likely automated · 86%" only when
  calibrated; before that, words only.
- Probable cause: rules linking screening answers to role requirements (e.g. years of
  experience below required, location, right to work).

## Survival analysis (Stage 8)

- Kaplan–Meier (lifelines) for time to first reply per company and per sector; censor at
  "today" for open applications and at 60 days.
- Competing risks: cumulative incidence for rejection vs interview vs assessment
  (Aalen–Johansen).
- Factors: Cox PH or Weibull AFT with seniority, sector, source, days-since-posting; show
  hazard ratios in plain language ("referrals hear back about twice as fast").
- "When to stop waiting": day by which 80% of eventual replies arrive.

## Empirical Bayes (Stage 8–9)

Beta-binomial shrinkage for rates with small samples:

```
prior: Beta(α, β) fitted to the sector (method of moments)
shrunk_rate = (successes + α) / (n + α + β)
```

Show n and a confidence label (high ≥ 50, medium 15–49, low < 15; below 15 badges are hidden).
Same method for users' funnel rates toward their cohort.

## Experiments and causal effects (Stage 9)

- **Randomised tests (preferred):** consented users; assignment at application level with a
  stored seed; arms balanced within user.
- **CUPED:** use the user's pre-period reply rate as covariate to reduce variance.
- **Stratification:** by role family, seniority, source; never compare raw CV versions across
  different job mixes.
- **Uplift (v2):** two-model and X-learner (econml/causalml), tree-based meta-learners;
  validate with Qini curves; report intervals by bootstrap.
- **Display:** estimate + interval; intervals crossing zero → "no clear effect yet".
- **CV A/B tester:** sequential test with alpha spending (or a Bayesian beta-binomial with a
  decision threshold) to avoid peeking bias; "too early to call" until reached.

## Interview prep metrics (Stage 10)

- Transcription: faster-whisper (small/medium English model) on CPU workers; word timestamps.
- Words per minute = words ÷ speaking minutes; comfortable range 130–160.
- Filler words: dictionary ("um", "uh", "er", "like" as filler, "you know", "sort of", "kind of",
  "basically", "actually") with simple context rules.
- Long pauses: gaps > 3 s between word timestamps.
- Length vs target: per question type (pitch 60–90 s, behavioural 90–120 s).
- Structure: STAR presence via rules on transcript sections + AI judgement (`prompts/interview_feedback.md`).
- **Not measured, ever:** faces, expressions, eye contact by video analysis, emotion, appearance, accent.

## Fairness

Annual audit with consented demographics stored separately: compare ranking exposure and
outcome-score calibration across gender, nationality and age band. Protected characteristics
and obvious proxies are excluded from model features. Publish the results.

## Evaluation datasets

Keep versioned labelled sets in `backend/tests/fixtures/` (small) and an encrypted bucket
(large): CV parse golden set, requirement extraction set, reply classification set,
duplicate pairs, company pairs.

## Hedonic adaptation ("in a year") — how it's used

People adapt quickly to some gains (a pay rise, a title, novelty) and slowly or not at all to
some daily costs (a long commute, chronic stress, a difficult manager). Job satisfaction after a
voluntary move typically rises and then declines over the following year (Boswell, Boudreau and
Tichy 2005, the honeymoon-hangover effect); longer commutes are associated with lower life
satisfaction that pay doesn't offset (Stutzer and Frey 2008).

Rules:
- Used **only as reflection**: tags and notes in the self-check, an "In a year" view of the
  user's own offers, and the counter-offer guide. It never changes a verdict, never produces a
  score and never recommends staying or leaving.
- Durability tags are fixed per question in `questions.json`, reviewed with the content, not
  learned from users.
- Referral comparison in "What works for you": referred vs cold first-call rate, shown only when
  each group has at least the `what_works` readiness threshold of outcomes.


## Client-side methods and parity (Track E)

The extension runs the v0 methods in the browser, in `packages/core`: stage odds from published
averages, Kaplan-Meier reply curves with right-censoring, beta-binomial shrinkage toward published
priors, Wilson intervals, BM25 keyword matching with a skills dictionary, simhash duplicate
detection, rule-based job-description parsing and suspicious-listing signals. Same four rules for
every score (explained, calibrated, causal where advice is given, honest about uncertainty).

- **Parity:** where the Python backend implements the same rule (stage odds, LinkedIn checks, readiness),
  both are tested against the same golden fixtures in `content/fixtures/` (to be created in E1).
- **Small n:** one person's history is small; the extension shows waiting states (20 outcomes) and
  published averages labelled "public data". Cohort and company statistics need many users and
  arrive through the platform (gates above).
- **No learned models run in the extension.** Learned models stay server-side behind their gates.
