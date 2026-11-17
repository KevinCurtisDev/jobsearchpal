# 07 · Design system

**Look:** calm, clear, honest. Apple-inspired: system type, one blue accent, generous space,
white cards on a light grey ground, pill buttons. Colour is used to **mean** something
(feature areas and statuses), never as decoration. Deep navy panels signal trust.

Tokens: `design/tokens.json` (source of truth) → `frontend/src/styles/tokens.css`.

## 1. Colour

| Token | Hex | Use |
| --- | --- | --- |
| `--color-ink` | #1D1D1F | Primary text |
| `--color-graphite` | #424245 | Secondary body text |
| `--color-slate` | #6E6E73 | Captions, metadata (5.0:1 on white) |
| `--color-field-border` | #86868B | Inputs and UI parts (3.6:1) |
| `--color-hairline` | #E5E5EA | Card borders, dividers |
| `--color-divider` | #F0F0F3 | Row dividers inside cards |
| `--color-mist` | #F5F5F7 | Page ground in the app, panels |
| `--color-white` | #FFFFFF | Cards |
| `--color-navy` | #0B2A4F | Trust panels: hero stage, promises, sign-in side panel |
| `--color-accent` | #0066CC | Links, primary buttons (5.6:1 with white) |
| `--color-accent-hover` | #00509E | Primary hover |
| `--color-focus` | #0071E3 | Focus ring |

**Status pairs** (text on background, all ≥ 4.5:1): positive #146C2E/#E7F5EC,
caution #9A4A00/#FDF0E3, critical #B42318/#FCEBEB, info #0057B8/#E8F0FB,
Critical Skills #5B3CC4/#F1ECFB, neutral #515154/#F0F0F3.

**Feature tints** (marketing tiles and matching in-app cards): blue #EAF2FD (scores explained),
violet #F3EFFD (visa certainty), green #E9F6EE (what works), amber #FFF6EA (honest rejection).
Each feature keeps its colour everywhere it appears.

Rules: never encode meaning by colour alone — every status has an icon and words. Colours
that must be told apart also differ in lightness. Prefer blue/orange over red/green.

## 2. Typography

System stack: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Helvetica Neue", Arial, sans-serif`.
Load Inter (self-hosted, not Google CDN) as the fallback for non-Apple devices.

| Style | Size / weight | Use |
| --- | --- | --- |
| Display | 68 / 700, −0.03em | Landing hero only |
| Title 1 | 48 / 700, −0.025em | Marketing section titles |
| Title 2 | 34 / 700, −0.02em | App page titles |
| Title 3 | 24 / 600 | Card titles |
| Headline | 21 / 600 | Sub-sections |
| Body | 17 / 400, 1.5 | Marketing body, long text |
| Callout | 15 / 400, 1.5 | App body |
| Footnote | 13 / 400 | Metadata, notes |
| Caption | 12 / 600, +0.04em, uppercase | Eyebrows, "SAMPLE DATA" |

Minimums: app body 15px; never below 12px. Use `rem` in code so user text size settings apply.

## 3. Space, shape, depth

- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48, 64, 96, 120.
- Radius: inputs 10, chips 12, cards 18, panels 22, marketing tiles 28, hero stage 32, pills 980.
- Depth: light ground behind white cards. Only two shadows: CV paper preview, selected segment.
- No gradients, no glassmorphism, no emoji, no left-border accent cards.

## 4. Layout

- Marketing: centred container, max 1160px, side gutters 24px; sections 112–120px vertical padding.
- App: side nav 248px (white, right hairline) + content (flex `999 1 560px`). Below 900px the
  nav stacks above the content (later: collapses into a menu button).
- Content columns: main (flex `999 1 520px`) + aside (flex `1 1 320px`), wrapping on small screens.
- Wide tables scroll horizontally inside their card.
- Breakpoints: 600, 900, 1200, 1440. Every screen works at 320px wide.

## 5. Components

Build each as a React component with a CSS Module, a Vitest test and an axe test.

| Component | Variants / props | Spec |
| --- | --- | --- |
| `Button` | primary, secondary, tertiary, danger, white (on dark), ghostLight; sizes md (44px), lg (48px), sm (36px, only inside dense cards with 44px hit area preserved by padding) | Pill, 15–17px, weight 500. One primary per view. Icon-only buttons require `aria-label`. |
| `Link` | inline, "more" (with chevron) | Accent colour, underline on hover |
| `Badge` | positive, caution, critical, info, criticalSkills, neutral; with icon | Pill, 12–13px, weight 500, icon + words |
| `Card` / `Panel` | card (radius 18), panel (22), tile (28, tinted) | White on mist; padding 24–32 |
| `Field` | text, email, textarea, select; helper text, error | Label above, 44–48px tall, border field-border, error 2px critical + icon + message, `aria-describedby` |
| `OneTimeCodeInput` | — | Single input, `inputmode="numeric"`, `autocomplete="one-time-code"`, letter-spaced |
| `Checkbox` | — | 20px, accent colour, label clickable, 44px row |
| `Switch` | — | `role="switch"`, 52×32, on = positive solid; label + description via `aria-labelledby/-describedby` |
| `SegmentedControl` | — | Buttons with `aria-pressed`; selected = ink fill, white text |
| `Tabs` | — | Radix Tabs; pill tab list; selected = ink fill. Arrow-key navigation. |
| `Stepper` | — | `<ol>`, current step `aria-current="step"`, done steps say ", done" for screen readers |
| `ProgressBar` | — | Native `<progress>` with visible label and value text |
| `Table` | — | Real `<table>`, `<caption>`, `scope` on headers; scroll container |
| `ScoreWithReasons` | probability or score | Big number + label; reasons list with Raises/Lowers words and diverging bars; confidence + source line; "How we calculate this" link |
| `EffectRange` | — | Dot (estimate) + bar (interval) on a zero line; `role="img"` with full text label; text line under it |
| `FunnelComparison` | — | Table: stage, you, bars (you vs similar), similar; legend |
| `ReplyCurve` | — | SVG step/line of % heard back by day; highlighted day; shaded "likely silent" region; text summary |
| `JobCard` | standard, flagged | Title link, meta line, badges, score block, reasons row, actions |
| `KanbanColumn` / `ApplicationCard` | — | Cards are buttons (`aria-pressed` when selected); keyboard move via menu |
| `AppShell` | — | Skip link, side nav (`aria-current="page"`), header with page title, account button |
| `MarketingHeader` / `Footer` | — | |
| `SampleDataChip` | — | Caption style, caution colours. Dev and demo only. |
| `Recorder` | video, audio-only | Camera preview, record button (label changes to "Stop recording"), timer, framing hint, privacy line |
| `MetricRow` | — | Name, target, value, verdict badge |

## 6. Accessibility (WCAG 2.2 AA)

- Contrast: 4.5:1 text, 3:1 large text and UI parts. Verified for every token pair above.
- Visible focus: 3px `--color-focus` outline, 2px offset, on every interactive element.
- Targets ≥ 44×44px (WCAG 2.5.8 needs 24px; we choose 44).
- Keyboard: everything operable; logical order; skip link; no keyboard traps; drag-and-drop
  always has a button alternative.
- Semantics: landmarks (`header`, `nav`, `main`, `aside`, `footer`), one `h1` per page,
  ordered headings, real buttons/links/labels; tables with captions.
- Charts: `role="img"` + full text alternative, and a visible text summary.
- Forms: labels always visible; errors in text with icon, linked by `aria-describedby`;
  don't rely on placeholder text.
- Motion: respect `prefers-reduced-motion`; no auto-playing media.
- Zoom: works at 200% text and 400% zoom (reflow).
- Language: `lang="en-IE"` (or `en-GB`), plain English, sentences under 25 words.
- Media: recordings get transcripts; any video content gets captions.
- User settings: text size, reduce motion, increase contrast, plain-language explanations.

## 7. Content style (UI copy)

Plain, kind, specific. Numbers with units. Rejections framed as likelihoods, never verdicts.
Always say where a number came from and how sure we are. See `14-content-guidelines.md`.
