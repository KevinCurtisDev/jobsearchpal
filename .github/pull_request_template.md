## What and why

<!-- One or two sentences. Link the stage task: docs/02-build-stages.md, Stage N -->

## How it was tested

- [ ] Unit tests added or updated
- [ ] `make lint` and `make test` pass
- [ ] UI changes checked with axe and keyboard only
- [ ] Screenshots for UI changes (desktop and 320px wide)

## Checklist

- [ ] Follows the non-negotiable rules in CLAUDE.md
- [ ] Security checklist (docs/06-security.md) considered if this touches auth, uploads, external calls or personal data
- [ ] Database changes include an Alembic migration
- [ ] Docs updated (API, data model, screens) and docs/STATUS.md ticked
- [ ] No secrets, no personal data in logs
- [ ] Touches personal data? Privacy checklist completed (docs/privacy/pr-privacy-checklist.md), `data_inventory.toml` updated and `make privacy-docs` run
