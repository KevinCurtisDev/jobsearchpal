# AI prompts

Generative AI is used only for writing, reading messy text, and judging interview answers.
Every prompt here is versioned, returns JSON validated against a schema in `schemas/`, and
is covered by evals in `backend/tests/evals/`.

| Prompt | Version | Used for | Schema |
| --- | --- | --- | --- |
| `cv_parse.md` | v1 | Fallback parsing of CV sections the rules parser could not handle | `schemas/cv_parse.json` |
| `cv_rewrite.md` | v1 | "Improve wording" suggestions on existing CV content | `schemas/suggestions.json` |
| `tailor_suggestions.md` | v1 | Rewording/reordering to match a job description | `schemas/suggestions.json` |
| `cover_letter.md` | v1 | Cover letter draft for assisted apply | `schemas/cover_letter.json` |
| `linkedin_rewrite.md` | v1 | Headline options, About and role descriptions for LinkedIn (copy-ready; the user pastes them in) | `schemas/linkedin_rewrite.json` |
| `interview_feedback.md` | v1 | Feedback on the content of a practice answer | `schemas/interview_feedback.json` |

## Rules for every AI call

1. **Untrusted input:** CV text, job descriptions and emails go inside `<document>` tags with
   an instruction that their contents are data, never instructions.
2. **Minimum data:** remove name, email, phone, address and links before sending.
3. **Structured output:** request JSON matching the schema; validate with Pydantic; on failure
   retry once, then fail gracefully ("We couldn't suggest changes right now").
4. **No-invention guard (mandatory, in code):** after validation, extract entities from the
   output — skills (ESCO match), employers, job titles, dates, numbers, qualifications — and
   check each exists in the input CV or in facts the user confirmed. Any new entity →
   discard that suggestion and log it. Unit-test this with adversarial fixtures.
5. **Banned phrases:** run the writing checker on AI output; regenerate or drop suggestions
   that contain banned phrases.
6. **Record** prompt name + version, model, token counts and cost in `ai_usage`.
7. **Quotas:** check the user's quota before the call.
8. **Models:** set by env (`AI_MODEL_WRITING` = Haiku-class default, `AI_MODEL_STRONG` = Sonnet-class
   only where evals require), never hard-coded. See `docs/15-cost-efficiency.md`.
9. **On request only:** AI runs when the user clicks; use the Batch API for overnight work,
   prompt caching for system prompts, and a result cache keyed on (prompt version, model, input).

## Prompt file format

Each prompt file has a front-matter block (`name`, `version`, `model_env`, `max_tokens`,
`temperature`), a `## System` section and a `## User` template using `{{placeholders}}`.
The loader in `backend/app/integrations/ai/prompts.py` (Stage 2) renders them with Jinja2
(autoescape off, strict undefined).
