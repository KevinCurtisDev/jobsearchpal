# Design

## Design canvas

All screens, with sample data, are in the Claude design canvas:

**https://claude.ai/artifact/SMKK99kfu6Fzimm2QNPabr**

The canvas is private until its owner shares it (Share menu on the canvas page). If you can't
open it, build from the written specs — they are complete:

- `docs/07-design-system.md` — tokens, components, layout, accessibility
- `docs/08-screens.md` — every screen, its route, content, states and acceptance criteria
- `design/tokens.json` — machine-readable tokens (source of truth)

## Screens in the canvas

| Artboard | Route | Spec |
| --- | --- | --- |
| Marketing site | `/` | 08-screens.md §Marketing site |
| Design foundations | — | 07-design-system.md |
| Sign in and sign up | `/sign-in`, `/sign-up` | §Sign in |
| Home · Where you stand | `/app` | §Home |
| CV builder | `/app/cv` | §CV builder |
| LinkedIn profile | `/app/linkedin` | §LinkedIn profile |
| Tailor to a job | `/app/tailor` | §Tailor |
| Job matches | `/app/jobs` | §Job matches |
| Job detail and assisted apply | `/app/jobs/:id` | §Job detail |
| Applications and honest rejection | `/app/applications` | §Applications |
| What works for you | `/app/insights` | §What works |
| Interview prep and offers | `/app/interviews` | §Interview prep |
| Privacy, data and settings | `/app/settings` | §Privacy and settings |

## Tokens

`tokens.json` → `frontend/src/styles/tokens.css` via `frontend/scripts/build-tokens.mjs`
(`npm run tokens`). Never hard-code colours or sizes in components; use the CSS variables.
