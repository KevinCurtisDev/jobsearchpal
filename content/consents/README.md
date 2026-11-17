# Consent and acknowledgement wording

Shown **verbatim** next to each switch. File name: `<kind>.v<version>.md`. The version must
match `CURRENT_VERSIONS` in `backend/app/privacy/consent.py`, and the SHA-256 of the file is
stored with every consent record (`consents.wording_sha256`), so we can show exactly what
the person agreed to.

Rules: switches start **off**; one purpose per switch; no bundling with the terms; saying
no never blocks unrelated features; withdrawing is as easy as giving (same screen, one tap).
Changing the meaning of a wording = new file + version bump = everyone is asked again.
