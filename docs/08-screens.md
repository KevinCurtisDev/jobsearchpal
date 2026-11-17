# 08 · Screens

Each screen matches its artboard in the design canvas (`design/README.md`). Every screen must
handle **loading**, **empty**, **error** and **offline** states, work at 320px wide, and pass
axe with no violations. App screens use `AppShell`; marketing screens use `MarketingLayout`.

Sample persona for fixtures and Storybook-style demos: Aoife Byrne, data analyst, Dublin.

---

## Marketing site — `/`

Sections in order:
1. **Header:** logo, nav (Features, How it works, Our promises, Pricing, For organisations), Sign in, "Start free" (primary, small).
2. **Hero:** tag "New · Job search built for Ireland and the UK"; H1 "Built for **offers received**, not applications submitted." (phrase in accent); sub "A CV that passes screening, jobs worth your time, and honest evidence of what gets you hired."; buttons "Start free" (→ `/sign-up`) and "Get a free CV check" (→ `/cv-check`); three ticks: free plan no card, we never sell your data, delete everything in one click.
3. **Product stage:** navy panel (radius 32) with an app window (today's matches: three job rows with badges and reply chance, one flagged fake listing) and two cards: honest rejection (amber tint) and what works (green tint). Label "Sample data shown."
4. **Built on official data:** caption + list: UK Register of Licensed Sponsors, Ireland's Critical Skills Occupations List, Irish employment permit statistics, Central Statistics Office, Irish and UK company registers.
5. **Problem:** "Job hunting feels like shouting into the void. The numbers agree." Three stats with coloured top rules: 55% no response is most frustrating; 67% suspected a fake posting; 1 in 5 hiring managers would reject an AI-written application. Source line (Resume Genius 2026, TopResume 2025). Replace with Irish/UK data when available.
6. **Features:** "Clarity at every step." Tiles: Visa certainty (violet, large, mini job card), Honest rejection (amber), Every score explained (blue, mini bars), What works for you (green, large, mini effect ranges), Company reply rates, Screening-ready CVs, Fake job flags (grey tiles).
7. **How it works:** three numbered cards (blue 1, violet 2, green 3) with links into the product.
8. **Our promises:** navy section; "We never sell your data. Period."; six promises with green ticks; "See your privacy controls".
9. **Pricing:** Free (€0, pay what you can), Monthly (€19), Search pass (€45 / 3 months, blue tint, "Best value", ≈€15/month, interview guarantee box, conditions placeholder).
10. **For organisations:** grey panel, "Talk to us".
11. **Closing CTA:** full-width accent blue, "Your next offer starts with a better CV.", "Start free" (white) + "See how it works" (ghost).
12. **Footer:** How we calculate scores, Annual fairness audit, Monthly scam and fake job report, Privacy, Terms, Accessibility statement.

Acceptance: Lighthouse accessibility 100; LCP < 2.5 s on 4G; no layout shift from fonts.

## Free CV check — `/cv-check`
Upload → screening check result (pass/fail list) + 3 top writing suggestions → prompt to create an account to save and fix. No account needed to see the result; file deleted after 24 hours.

## How hiring works — `/how-hiring-works` (free guide, no account)
Marketing layout. Sections: hero ("How hiring works, from the other side of the desk."); **Out of 100 applicants**: 10×10 dot grid (1 offer, 2 more final interviews, 5 more first screen, 92 hear nothing or a no) with a text legend and an accessible description, beside a **stage ladder** (applied ≈1 in 84 → first call ≈1 in 7, "about 12 times better" → final interviews ≈1 in 2 → offer, "your call"); **What happens at each stage** (6 steps, each "On their side" / "What helps you"); **Not every employer runs the same process** (large tech example as publicly reported, smaller employer, Irish public sector via publicjobs.ie); **What this means for you** (5 encouraging, honest points); CTA "Track your applications free". Every figure has a source link and a "last checked" date; content in `content/hiring_stages.json`; reviewed every 6 months.

## Should I move? — `/should-i-move` (free self-check, no account)
For people who are employed and unsure. Marketing layout, one page. Intro: "Eight questions about your current job. Your answers stay in your browser: nothing is sent or saved." Questions (one radio group each, from `frontend/src/features/self-check/questions.json`): day to day, stress, pay, growth, manager and team, fit with your life, security, time for a search. Result panel (shown after the last answer, focus moves to it, announced by a live region):
- **A direction, never a score:** stay / fix one thing first / explore quietly / time to look, with its plain-language explanation.
- **Your reasons:** the dimensions that pushed the answer, strong first. Each reason carries a small tag from `in_a_year.labels`: *lasts* (stress, growth, manager and team, commute and hours, security: "People rarely get used to this. A solid reason.") or *fades* (pay: "Feels big now, but the lift from fixing it tends to fade."). Day-to-day feeling is untagged.
- **Would this still bother you in a year?** shown whenever there are reasons. For explore and move, the new-job glow note (satisfaction rises after a move and drifts back within a year) framed as "move towards something specific". If every reason is one that fades, the fades-only note asks the reader to check the new job is also better on something that lasts. Sources linked. Never changes the verdict and never argues for staying.
- **Fix-first tip** for that one dimension (talk to your manager about workload, evidence-based pay review, etc.).
- **Wellbeing note** whenever stress affects sleep or health, shown above everything else (GP, Employee Assistance Programme); no clinical language, no diagnosis.
- **Pay unsure note** pointing to salary ranges in job ads.
- **What to expect** for explore and move: the out-of-100 funnel with source, a pace from the time answer ("about N good applications a week", assumption shown), and searching-while-employed tips.
- CTA by verdict: stay → "Keep your CV ready" (free CV check); fix first → "Read how to ask for a pay review / workload change" (guide); explore and move → "Start free" and "How hiring works".
Rules: no answers leave the browser; analytics count only "check completed" and the verdict category (no answers, no identifiers); never shame staying; never promise a better job.

## Free LinkedIn check — `/linkedin-check`
Paste headline and About → checklist (rules only) with character counts → "Create a free account for the CV comparison and rewrite". Nothing stored; the page says so.

## Sign in — `/sign-in`, `/sign-up`
Split layout: navy side panel (logo, "Your job search, kept private.", passkey benefits) + form.
States (one route, state machine):
1. **Start:** segmented Sign in / Create account. Sign in shows "Sign in with a passkey" (dark button) first, divider "or use your email". Email field (`autocomplete="username webauthn"`). Sign-up adds terms consent (required) and product updates (optional). Turnstile widget (usually invisible; shows "Human check passed"). Hidden honeypot. Button "Email me a sign-in code". Note: "We'll never ask for a password. Automated and bulk sign-ups are blocked."
2. **Code:** "Check your email", address shown, 10-minute expiry, one-time-code input, "Verify and continue", resend disabled with countdown, "Use a different email", anti-phishing note.
3. **Add a passkey** (after first sign-in / sign-up): "Create a passkey" or "Not now".
4. **Signed in:** confirmation + new-device alert note → `/app`.
Errors: wrong code (attempts left), expired code, too many requests (with time), Turnstile failure ("We couldn't confirm you're human. Try again.").

## Home · Where you stand — `/app`
Header: date, "Good morning, {name}", notifications, account. Main column: **Where you stand** card (headline diagnosis; funnel comparison table you vs similar candidates with bars; diagnosis box with next action button; footnote on cohort and shrinkage + "How we calculate this"); **Today's matches** (top 3, link to all). Aside: **Needs your attention** (interview invite, likely-automated rejection, reposted role), **This week** (goal progress + reframing line), **What works for you** unlock progress.
Empty state (new user): checklist — upload CV, set preferences, add a passkey.

## CV builder — `/app/cv`
Header: version select, Download Word, Download PDF. Three columns: **Editor** (Layout and conventions: country segmented IE/UK/EU/US with rules line, template Classic/Modern/Compact, age-neutral checkbox; Summary; Experience with achievements and inline warnings; Skills chips; Education), **Preview** (paper, single column, Arial-like export font, highlights for open suggestions, page count), **Checks** (Screening check pass list; Writing suggestions with action + dismiss; honesty note; "Tailor this CV to a job").

## Tailor to a job — `/app/tailor`
Stepper (Paste the job ✓, Review the match, Review changes, Save as a version). Left: job link + description + "what we found". Right: **How your CV matches** (n of N, progress, matched chips, missing list with Required/Nice-to-have tags and "I have this" / "Mark as a gap", honesty note), **Suggested changes** (before/after/why, accept/edit/reject, accept all), footer: back, "Save as Version B".

## LinkedIn profile — `/app/linkedin`
Nav item "LinkedIn" under CV tools (blue feature tint). Header: "Your LinkedIn profile", last imported date, "Import again", "Delete my LinkedIn copy".
Empty state: three import options as cards — **Use your LinkedIn data export (recommended)** with the steps (LinkedIn → Settings → Data privacy → Get a copy of your data → choose Profile, Positions, Skills, Education → upload the ZIP you're emailed), **Upload "Save to PDF"**, **Paste each section**. Note: "We never ask for your LinkedIn password and never read your messages or connections. We read only your profile files, and don't keep the upload."
Main: tabs or stacked cards —
1. **Profile check** — score-free list grouped High / Medium / Low with the evidence and a "Fix with suggestion" link; manual checklist with "Done" ticks (custom URL, location, Open to work options, photo tips, featured, contact info).
2. **Matches your CV?** — CV version select; rows for each mismatch (dates, title, missing role) showing CV vs LinkedIn side by side; "Use CV wording" / "Keep LinkedIn wording" choices.
3. **Keywords recruiters search for** — target role select; chips "On your CV, missing on LinkedIn" (green) and "In X% of ads — if you have this" (grey, with "I have this" / "Not me"); footnote "Based on N ads in the last 90 days · confidence"; before Stage 5: "Available once job data is live".
4. **Rewrite** — "Suggest a rewrite" (uses AI quota): two headline options, About, recent roles; each card has before/after, reason, live character count vs limit, **Copy** button (announces "Copied"), Dismiss; "ask" items show the question with an answer field. Footnote: "Paste these into LinkedIn yourself. We never post or edit for you. Nothing here invents experience."
Honesty note in the aside: "We can't see your profile views or LinkedIn's ranking. Log recruiter approaches in Applications to see what changes."

## Job matches — `/app/jobs`
Filter bar (keyword, commute, minimum salary, sort, visa-only checkbox, hide-flagged checkbox). Results count (`aria-live`). Job cards: title, meta, badges (visa, reply rate, info), score with label, reasons (Raises/Lowers/Warning), actions (View and apply, Save, Not for me, Report this job). Flagged card: critical border, reasons, "See why it's flagged". Aside: preferences summary, how matching works, reports note.

## Job detail — `/app/jobs/:id`
Back link; title, meta, badges (Critical Skills, permits issued, salary disclosed, reply rate, registered company). Main: **Why this match** (score, factors table with diverging bars in points, confidence, link), **How {company} replies** (reply curve chart, day-9 marker, likely-silent region, outcome split, confidence), **About the role**. Aside: **Assisted apply** (tailored CV ✓, cover letter review, screening answers to check, "Open the employer's application", "We never apply for you"), agency check, previous applications, permit data note.

## Applications — `/app/applications`
Header: Board/List toggle, "Add an application". Reply capture strip with forwarding address. Board: six columns with counts; cards are toggle buttons; empty Offer column shows reframing text. Detail panel by selection:
- **Honest rejection:** likelihood, "probably no person saw your CV", signals with strength, what probably happened (screening answer), what to try next, helpful yes/no, calibration note.
- **Agency duplicate warning**, waiting-day context.
- Generic: detail line + action.
Keyboard: card menu "Move to…".

**Stage odds (added):** a "Where your search stands" card above the board: chance at least one active application becomes an offer (e.g. "About 55%"), counts and odds per active stage (Applied "about 1 in 84 each", Screening "about 1 in 7", Interview "about 1 in 2"), the biggest contributor, one **next best step** with a button, and a footnote with source and confidence ("Low confidence: published averages, not yet your own data"). Each column with active cards shows its offer odds under the title. The detail panel shows **Your progress on this application**: a four-step ladder (passed / you are here / next, announced to screen readers) and a progress-framed message from `encouragement()`. Rejections after interview get the "competitive" message, never a score drop.

## What works for you — `/app/insights`
Header with data basis line. Main: **What changes your reply rate** (effect ranges for referral, tailoring, follow-up, applying early, cover letter; confidence badges; "no clear effect" when interval crosses zero; method note), **CV A/B tester** (table, status, progress to confidence, what differs, keep testing / stop and use B). Aside: **When to stop waiting**, **Where you lose ground**, **How we calculate this** (blue tint).

## Interview prep — `/app/interviews`
Tabs (Radix): Overview · STAR stories · Elevator pitch · Core questions · Video practice · Offers.
- **Overview:** next interview card (time, format, panel, add to calendar) with four progress tiles that jump to tabs; format guide; questions to ask them; interview-day checklist; after-interview debrief (questions asked, thank-you draft, follow-up reminder); adjustments guidance.
- **STAR stories:** competency coverage chips (covered vs "no story yet", dashed caution); story bank list (title, work/outside work, competencies, status); STAR builder for the selected story (Situation, Task, Action, Result, optional Reflection, each with guidance label), spoken-time estimate, story checks (✓ / !), Save, Practise on video.
- **Elevator pitch:** 30/60/90 segmented control; present/past/future blocks (blue/violet/green tints); word count and time; practise on video, edit, copy.
- **Core questions:** table of 11 questions (question, what they're really asking, how to answer, prep status); role-specific questions with "Practise in text" / "On video".
- **Video practice:** question card with target time; camera preview (16:9) with framing guide; Start recording (critical solid), Skip; audio-only option; privacy line. Video plays back from the browser only; just the audio is uploaded. Last take: metrics (length, pace, filler words, long pauses, structure) with verdict badges; biggest win next time; self-review checklist; "We measure timing and words only."
- **Offers:** comparison table (salary, take-home, office days, commute, left after commute), summary sentence, assumptions line, negotiation script. **Toggle: Today / In a year.** "In a year" keeps pay visible but moves it below the things people adapt to least: commute (minutes each way, from the offer), hours and flexibility, manager and team, and growth, each rated by the user 1 to 5 from what they learned in interviews ("Not sure" allowed). Summary sentence compares on those first ("Offer B pays €4,000 more; Offer A is 50 minutes a day shorter and you rated the manager higher"). No combined score, no recommendation. Below it: links to the counter-offer and resigning sections of *The end of the search*.

## Privacy and settings — `/app/settings`
Privacy promise (navy). **Your data** (download, delete with step-up). **Sign-in and security** (no-password badge, passkeys list with remove, add passkey, signed-in devices with sign out, sign out of all others, alerts note). **What you share** (switches: benchmarks, randomised tests, fairness audit data, daily email). **Reply capture** (forwarding address, Gmail/Outlook "coming later"). **Your plan** (pass, guarantee status, pay what you can). **Accessibility and display** (text size, reduce motion, increase contrast, plain-language explanations). Transparency links.

## Admin (internal, Stage 5+)
Source health, ingestion counts, duplicate review, company merge tool, job report queue, feature flags, model monitoring. Passkey-only, audit-logged.

## Guides — `/guides/<id>` (free, no account)
Marketing layout, one column, from `content/guides/*.md` (front matter: id, title, checked, review_every_months). "Last checked" date and sources on every page; reviewed every 6 months. Launch set:
- **Ask someone you know** (`referrals`): why referrals matter (sourced figure), who counts, a message template, second-degree chats.
- **The end of the search** (`ending-your-search`): handling the offer call, the year test, negotiating, resigning well, counter-offers ("Would the counter-offer fix the thing that would still bother you in a year?").
- **When the search is taking a long time** (`long-searches`): diagnose by stage from the tracker, a pace you can keep, wellbeing, statutory redundancy facts for Ireland and the UK (dated, linked, "not legal advice").
- **Searching from a different starting point** (`situations`): returners, career changers, graduates, disability and adjustments.
Linked from: the self-check result, the tracker (long-search prompt after 8 weeks with no first call, shown once, dismissible), the Offers tab, and the How hiring works page.

**Tracker addition:** every application has a "Who do I know there?" control (Not yet / Asked / Referred), stored as `applications.referral_status`. No contact names are asked for or stored.



---

## Extension surfaces (Track E; design canvas boards to add)

Specified in `docs/16-chrome-extension.md`; each handles loading, empty, error and offline states,
works with keyboard only, and passes axe. They use `design/tokens.json` and `packages/ui`.

| Surface | Purpose |
| --- | --- |
| Toolbar popup | Save this job, mark applied, add manually, today's follow-ups |
| Side panel | Main workspace beside a job page: Board, Job (keyword match, requirements, signals), CV check |
| Page chip (Tier A only) | Small Shadow DOM chip: "Save job" and, on confirmation pages, "Did you apply?" |
| Options dashboard | Applications, insights (waiting states), documents, LinkedIn check, backup and export, "what is stored", permissions explained |
| First-run | Three screens: what it does, what it never does, where your data lives (with "check it yourself") |
| Empty, waiting and backup-reminder states | Honest copy per `docs/14` |

## Export preview — `/import-preview` (no account, Stage C)

Upload a Hearback export file; insights are computed in the browser and nothing is stored. Prompts
to create an account to keep history and to opt in to benchmarks (consent recorded there).

## Connect — `/app/connect` (Stage C)

Pairing code, connected devices (revoke), import history, benchmark consent, delete imported data.
