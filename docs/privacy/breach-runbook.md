# Personal data breach runbook

A personal data breach is any security incident that leads to the accidental or unlawful
destruction, loss, alteration, unauthorised disclosure of, or access to, personal data
(Art 4(12)). **Losing availability counts** (for example a ransomware lock-out or a lost
backup key), not only leaks.

## The clock
The 72 hours (Art 33) start when we become **aware** — when we have a reasonable degree
of certainty that a breach has happened, not when the investigation ends.
`app.privacy.deadlines.breach_notify_by(aware_at)` gives the deadline. Record `aware_at`
in `privacy_incidents` straight away.

## Steps
| # | When | Who | Action |
| --- | --- | --- | --- |
| 1 | Immediately | Whoever spots it | Tell the incident lead (owner on call). Do not delete evidence. |
| 2 | Within 1 hour | Incident lead | Contain: revoke keys/sessions, block access, take the affected service offline if needed. Open a `privacy_incidents` row with `aware_at`. |
| 3 | Within 24 hours | Incident lead + DPO | Assess: what data, how many people, which countries, likely consequences. Decide risk: **none**, **risk**, **high risk**. Write the reason in `decision_reason`. |
| 4 | Within 72 hours of `aware_at` | Owner | If risk or high risk: notify the **DPC** (online breach form). If UK users are affected: also notify the **ICO**. If facts are incomplete, notify anyway and send the rest in phases (Art 33(4)). |
| 5 | Without undue delay | Owner | If high risk: tell affected users directly in plain language (Art 34): what happened, likely effects, what we did, what they can do, contact point. |
| 6 | Same time | Owner | Tell processors/controllers involved; if a processor caused it, require their report. |
| 7 | Within 2 weeks | Team | Post-incident review; remedial actions in `remedial_actions`; close the row. |

**Every breach is recorded**, including ones not notified (Art 33(5)).

## Notification content (Art 33(3))
Nature of the breach (categories and approximate numbers of people and records); DPO or
contact point; likely consequences; measures taken or proposed, including mitigation.

## Processors
Every DPA must require processors to tell us without undue delay (target 24 hours) after
they become aware of a breach affecting our data.

## Practice
Run a tabletop exercise before the public beta and then yearly (Stage 4 checklist).
