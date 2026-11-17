# DPIA 0003 · Fairness audit demographics

**Status:** Draft. Sign-off required before any demographic data is collected (Stage 11).

## 1. Processing
Optional gender, nationality group, age band and disability (yes / no / prefer not to say),
collected only with explicit consent (`fairness_audit`, Art 9(2)(a)), used only to measure
whether matching and scoring treat groups differently.

## 2. Necessity and proportionality
Bias testing cannot be done without group labels. Collection is optional, never affects
the user's results, and every field has "prefer not to say".

## 3. Risks
| Risk | Likelihood | Severity |
| --- | --- | --- |
| Data breach exposing special category data | Remote | High |
| Data used in product decisions | Remote | High |

## 4. Measures
Separate `sensitive` schema and DB role; column encryption; never joined in product code
(enforced by a test that only `app/ml/fairness_audit.py` imports the model); results
published only as aggregates with k ≥ 10; deleted immediately on withdrawal.

## 5. Residual risk — to be completed
## 6. Sign-off
