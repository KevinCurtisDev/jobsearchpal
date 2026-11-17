# 11 · Testing and quality

## Test layers

| Layer | Tools | What | Target |
| --- | --- | --- | --- |
| Unit (backend) | pytest | Services, scoring, parsing, auth logic, rules | ≥ 85% line coverage on `services/`, `auth/`, `ml/` |
| API | pytest + httpx AsyncClient | Routes, auth, CSRF, permissions, errors | Every endpoint: happy path + auth failure + validation failure |
| Integration | pytest + Docker services (Postgres, Redis, MinIO) | Repositories, migrations, Celery tasks | Runs in CI with service containers |
| External APIs | respx fixtures | Connectors, email, Stripe, Turnstile | No live calls in CI |
| Unit (frontend) | Vitest + Testing Library | Components, hooks, forms | Every design-system component |
| Accessibility | @axe-core/playwright + manual | Every page, every state | Zero axe violations; manual keyboard + screen reader pass per stage (VoiceOver + NVDA) |
| End to end | Playwright | Critical journeys | Sign-up with code, passkey sign-in (virtual authenticator), upload CV → export, tailor, apply, log reply |
| Security | ZAP baseline, pip-audit, npm audit, Trivy, CodeQL, gitleaks | CI on every PR; ZAP nightly on staging | No high/critical |
| Performance | Lighthouse CI, k6 (later) | Landing and app pages; API latency | LCP < 2.5 s; p95 API < 300 ms for reads |

Passkeys in E2E: use Playwright's Chrome DevTools Protocol `WebAuthn.addVirtualAuthenticator`.

## Quality sets for AI and parsing

- **CV parse golden set:** 20–50 anonymised CVs (PDF/DOCX) with expected JSON. Metric:
  field-level accuracy. Run on every change to the parser.
- **AI output evals** (`backend/tests/evals/`), run nightly and on prompt changes:
  - No banned phrases (from `content/banned_phrases.json`)
  - **No invention:** every skill, employer, date, number and qualification in the output
    exists in the input (entity diff); zero tolerance
  - Schema-valid JSON 100%
  - Length limits respected
  - Human review sample of 20 outputs per prompt version, scored 1–5 for "sounds like a person"
- **Classifier sets:** reply classification, requirement extraction, duplicate pairs,
  company pairs — held-out, versioned, never trained on.

## Statistical checks

- Simulate null data for the A/B tester and effect estimates: false-positive rate ≤ 5%.
- Calibration checks for any displayed probability: reliability curve and Brier score.
- Survival code tested against lifelines reference outputs on synthetic data.

## Code quality gates (CI)

- Python: `ruff check`, `ruff format --check`, `mypy --strict app`
- TypeScript: `tsc --noEmit`, `eslint` (incl. jsx-a11y), `prettier --check`
- Tests and coverage thresholds
- Docker images build; Trivy scan
- Conventional commit title on the PR
