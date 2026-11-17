# Privacy review checklist (every pull request that touches personal data)

Copy into the PR description when any box applies. Claude Code must complete it.

- [ ] New or changed table/column → `data_inventory.toml` updated; `make privacy-docs` run
- [ ] Lawful basis is the right one; consent only where the user has a real choice
- [ ] Retention set to a number of days or a defined event — never "indefinitely"
- [ ] Erasure: FK `ON DELETE` matches the inventory; export includes the new data
- [ ] Data minimisation: is every field needed for the stated purpose?
- [ ] No personal data in logs, metrics labels, URLs, analytics or error messages
- [ ] Data sent to a processor goes only to one listed in the inventory, from its stage
- [ ] AI calls use `ai_guard` (contact details never sent)
- [ ] New consent wording → new file in `content/consents/` and version bumped in `consent.py`
- [ ] Profiling or special category data → DPIA updated; feature off by default until signed
- [ ] Privacy notice needs a change? → flag to the owners
