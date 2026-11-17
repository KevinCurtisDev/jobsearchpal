# LIA 0003 · Employer contacts in captured emails

**Status:** Draft — sign-off required before Stage 8 (reply capture) launches.
**Categories:** `inbound_email_metadata`, `inbound_email_content`
**Data subjects:** recruiters and hiring staff who reply to a user's application.

## 1. Purpose
The user forwards, or gives employers, their Offerlight address so replies are tracked.
We process the sender's address, the subject and the body to classify the reply and time it.

## 2. Necessity
- Only replies to the user's own applications, received at the user's own inbound address.
- Bodies and sender addresses are cleared after 90 days; only the sender **domain** and
  timings stay. Bodies are encrypted at rest.
- Company-level reply statistics use domains and timings only, never sender names.

## 3. Balancing
- **Expectations:** a recruiter replying to a candidate expects the candidate to read,
  file and act on the reply. Tracking it in a tool is within that expectation.
- **Impact:** low; no marketing to the sender, no profile of the sender, no sharing.
- **Transparency (Art 14):** informing each sender individually would involve
  disproportionate effort (Art 14(5)(b)); the privacy notice has a public section for
  employers and recruiters with a contact route.

## 4. Outcome
Legitimate interests apply, with the 90-day limit and domain-only statistics as conditions.
