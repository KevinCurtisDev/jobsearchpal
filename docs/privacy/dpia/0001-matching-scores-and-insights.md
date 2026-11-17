# DPIA 0001 · Matching, scores and insights

**Status:** Draft. Sign-off required before Stage 6 launch.

## 1. Processing
Daily job matching (BM25 + ESCO, later LightGBM ranker), match probability, honest-rejection
assessment, reply-time estimates, cohort benchmarks (consent, k ≥ 10), experiments (consent).
Categories: `match_results`, `reply_and_rejection_scores`, `benchmark_contribution`, `experiments`.

## 2. Necessity and proportionality
- Scores are advisory and shown only to the user; no employer sees them; nothing is decided
  automatically about the person (Art 22 not engaged). The user chooses what to apply for.
- Every score shows reasons, a confidence level and the data source (rule 5 in CLAUDE.md).
- Inputs exclude special category data and proxies (photos, age, gender, nationality).
  Visa status is used only for sponsor information the user asks for.
- Benchmarks and experiments are opt-in.

## 3. Risks
| Risk | Likelihood | Severity | Notes |
| --- | --- | --- | --- |
| Discouragement from a low score leads someone not to apply | Possible | Medium | Wording, uncertainty, "we could be wrong" |
| Biased ranking disadvantages a group | Possible | High | Fairness audit (DPIA 0003) |
| Re-identification from benchmarks | Remote | Medium | k ≥ 10, shrinkage, no small cohorts |
| EU AI Act classification (Annex III, employment) | To be assessed | High | Legal review: decisions-needed #18 |

## 4. Measures
Calibration and monitoring (docs/09), explanation screen, opt-in for aggregate use,
annual fairness audit, model cards, kill switch per model via feature flags.

## 5. Residual risk — to be completed by owners
## 6. Sign-off — owner, solicitor/DPO, date
