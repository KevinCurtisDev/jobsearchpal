# Rights requests runbook (DSARs and other requests)

Applies to every request from a person about their data, however it arrives: in the
app, by email to the privacy contact, by post, or via support. **There is no required
form or wording** — "send me everything you have on me" is an access request.

## Deadlines (code: `app.privacy.deadlines`)
| | Deadline |
| --- | --- |
| Legal deadline | One month from receipt (`dsar_due`) |
| Extension | Up to two more months if complex or numerous (`dsar_extended_due`); tell the person within the first month, with reasons |
| Our targets | Self-service export ready within 24 hours; erasure completed within 30 days (`erasure_due`) |
| Fee | None. Only for manifestly unfounded or excessive requests (Art 12(5)), decided by an owner and recorded |

## Self-service (most requests)
| Right | Where | What happens |
| --- | --- | --- |
| Access + portability (Art 15, 20) | Settings → Privacy → Download my data | Async ZIP built from `export_plan()`: one JSON file per table, original uploaded files, a `README.html` explaining each file, purposes, recipients and retention (from the inventory). Link emailed, valid 24 h, single use. |
| Erasure (Art 17) | Settings → Privacy → Delete my account (step-up) | Account locked and sessions revoked at once; `process_erasures` runs the generated erasure plan the same night; confirmation email sent to the address before it is erased. Legal-hold rows are pseudonymised, not deleted (listed in the confirmation). |
| Rectification (Art 16) | Everywhere | All profile and CV data is editable. Scores are recalculated from corrected data. |
| Withdraw consent / object (Art 7(3), 21) | Settings → Privacy switches; unsubscribe link | Takes effect immediately (next request / next nightly job). |
| Restriction (Art 18) | Email | Manual: set `users.status = locked` (processing paused), record in `data_subject_requests`. |

Self-service actions are also written to `data_subject_requests` (channel `self_service`) so
the register is complete.

## Manual requests (email, post, non-users such as recruiters)
1. Log in `data_subject_requests` on the day received: `received_at`, `due_at = dsar_due()`.
2. **Verify identity proportionately:** for an account holder, a sign-in or a code sent to the
   account email is enough. Never ask for ID documents by default.
3. Search: the account (if any), `inbound_emails` (for employer contacts: search by sender
   address), `job_postings` (for named recruiters), `job_reports`, logs (by user id).
4. Respond in writing in plain language. For access: the export ZIP plus the Art 15(1)
   information (purposes, categories, recipients, retention, rights, source, any automated
   decision-making — there is none with legal effect).
5. Redact other people's personal data from what you send (Art 15(4)).
6. Close the row: `closed_at`, outcome. Requester identity is reduced to `subject_ref`.

## Refusals
Only an owner can refuse, only for a reason in the GDPR, recorded in `refusal_reason`, and
the person is told of their right to complain to the DPC (or ICO) and to a judicial remedy.

## The daily check
`dsar_deadline_check` (Stage 1) emails the owners about any open request due within 7 days.
