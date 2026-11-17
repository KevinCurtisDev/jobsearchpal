# 14 · Content guidelines

## Voice

Calm, plain, kind, specific. Like a good career adviser who respects your time.

- Sentences under 25 words. Paragraphs of three sentences or fewer.
- Numbers with units ("within 9 days", "+9 points").
- Say where a number comes from and how sure we are.
- Never blame the user. Rejections are likelihoods, never verdicts.
- No hype words ("revolutionary", "supercharge"), no emoji, no exclamation marks in product UI.
- Irish/UK English spelling by default (organise, colour, CV).

## CV writing rulebook (enforced by the writing checker)

- Banned and discouraged phrases: `content/banned_phrases.json` (e.g. "spearheaded",
  "results-driven", "dynamic", "synergy", "leveraged", "passionate about", "proven track record").
- Achievements start with a plain verb (Led, Built, Cut, Designed, Grew, Ran).
- Each role has at least one achievement with a number or clear outcome — **only numbers the
  user provides**. If missing, ask; never invent.
- Present tense for the current role, past tense for previous roles.
- No first-person pronouns in bullets.
- Bullets: 1–2 lines (≤ 30 words).
- Country conventions: `content/cv_conventions.json`.

## Interview content

- Core questions: `content/core_questions.json` (11 questions; each with what they're really
  asking and how to answer).
- Competencies: `content/competencies.json`.
- STAR guidance: Situation (1–2 sentences), Task (your responsibility), Action ("I", most of the
  time here), Result (outcome, a number if you have one), Reflection (optional: what you learned).
  Target 60–120 seconds spoken (~150–300 words).
- Elevator pitch: present → past → future; 30, 60 and 90-second versions.
- Video practice feedback: always lead with what worked, then one biggest improvement.

## Marketing claims

- Every statistic on the site has a source line. Prefer Irish/UK data.
- No testimonials until they are real and consented. No customer logos without permission.
- Guarantee wording always links to its conditions.

## LinkedIn wording

- First person, plain, warm; short paragraphs. LinkedIn is not a CV — never paste CV bullets
  unchanged.
- The general banned phrases apply, plus the LinkedIn list in `content/linkedin_rules.json`.
- Never promise more profile views, recruiter messages or a better "ranking". Say what we
  check and why; point to the tracker for evidence.
- "Open to work": present both options neutrally; it's the user's choice.
- Photo: written tips only. We never analyse photos (CLAUDE.md rule 6).
- Re-check LinkedIn's character limits every 6 months and update `linkedin_rules.json`
  (headline 220, About 2,600, role title 100, role description 2,000 as of October 2026).


## Guides and the "in a year" idea

- Guides live in `content/guides/*.md` with a `checked` date; every figure has a linked
  source; legal and statutory facts say "general information, not legal advice" and link to
  Citizens Information, GOV.UK or nidirect.
- The hedonic treadmill is **hinted, not taught**. Don't use the term "hedonic treadmill" in
  product copy; say what it means in plain words ("feels big now, then becomes normal").
- Never use it to talk people out of moving or to dismiss pay. Being paid fairly matters;
  the point is to move towards something that will still matter in a year.
- No unsourced statistics about counter-offers (for example "80% leave within six months"
  has no reliable source).
