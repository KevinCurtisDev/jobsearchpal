"""Generate the Record of Processing Activities (GDPR Art 30) from the data inventory.

    cd backend && uv run python -m app.privacy.ropa > ../docs/privacy/records-of-processing.md

(`make privacy-docs` does this.) CI fails if the committed file is out of date, so the
record always matches the code.
"""

from __future__ import annotations

from app.privacy.plans import retention_plan
from app.privacy.registry import Category, Inventory, LawfulBasis, RetentionPolicy, load_inventory

_BASIS = {
    LawfulBasis.CONTRACT: "Contract — Art 6(1)(b)",
    LawfulBasis.CONSENT: "Consent — Art 6(1)(a)",
    LawfulBasis.LEGITIMATE_INTERESTS: "Legitimate interests — Art 6(1)(f)",
    LawfulBasis.LEGAL_OBLIGATION: "Legal obligation — Art 6(1)(c)",
}


def _retention(c: Category) -> str:
    r = c.retention
    text = {
        RetentionPolicy.ACCOUNT_LIFETIME: (
            "While the account exists; erased within 30 days of deletion"
        ),
        RetentionPolicy.FIXED: f"{r.days} days",
        RetentionPolicy.AFTER_ACCOUNT_DELETION: (
            f"{r.days} days after account deletion (pseudonymised)"
        ),
        RetentionPolicy.UNTIL_WITHDRAWN: "Until consent is withdrawn or the account is deleted",
        RetentionPolicy.TRANSIENT: f"At most {r.seconds} seconds",
        RetentionPolicy.NOT_APPLICABLE: "n/a",
    }[r.policy]
    note = c.retention_note or c.retain_note
    return f"{text}. {note}" if note else text


def _esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render(inv: Inventory) -> str:
    procs = {p.id: p for p in inv.processors}
    out: list[str] = [
        "# Record of Processing Activities (GDPR Art 30)",
        "",
        "> **Generated** from `backend/app/privacy/data_inventory.toml` by `make privacy-docs`.",
        "> Do not edit by hand. Engineering record only, not legal advice.",
        "",
        f"Inventory last reviewed: {inv.last_reviewed}",
        "",
        "## Controller",
        "",
        "| | |",
        "| --- | --- |",
        f"| Controller | {_esc(inv.controller.name)} |",
        f"| Establishment | {inv.controller.establishment} |",
        f"| Lead supervisory authority | {inv.controller.lead_supervisory_authority} |",
        f"| UK regulator | {inv.controller.uk_regulator} |",
        f"| UK representative (UK GDPR Art 27) | {_esc(inv.controller.uk_representative)} |",
        f"| Data protection officer | {_esc(inv.controller.dpo)} |",
        f"| Privacy contact | {inv.controller.privacy_contact} |",
        f"| Minimum age | {inv.minimum_age} (self-declared) |",
        "",
        "## Processing activities",
        "",
    ]
    for c in inv.categories:
        if not c.personal:
            continue
        tables = [t.name for t in inv.tables if c.id in t.categories()]
        eph = [e.key for e in inv.ephemeral if e.category == c.id]
        where = ", ".join(f"`{x}`" for x in tables + eph) or _esc(c.stored_in or "")
        basis = _BASIS[c.lawful_basis]
        if c.consent_kind:
            basis += f" (consent kind `{c.consent_kind}`)"
        if c.art9_condition:
            basis += "; Art 9(2)(a) explicit consent"
        if c.lia_ref:
            basis += f"; LIA: `{c.lia_ref}`"
        if c.legal_ref:
            basis += f"; {_esc(c.legal_ref)}"
        recipients = [f"{procs[p].name} ({procs[p].location})" for p in c.processors if p in procs]
        transfers = [
            f"{procs[p].name}: {_esc(procs[p].transfer_mechanism or '')}"
            for p in c.processors
            if p in procs and procs[p].outside_eea
        ]
        rows = [
            ("Description", c.description),
            ("Purposes", "; ".join(c.purposes)),
            ("Data subjects", ", ".join(s.replace("_", " ") for s in c.data_subjects)),
            ("Lawful basis", basis),
            ("Third-party data", c.third_party_basis or "—"),
            ("Special category", "Yes" if c.special_category else "No"),
            ("Profiling", (c.automated_decision_note or "Yes") if c.profiling else "No"),
            ("DPIA", f"`{c.dpia_ref}`" if c.dpia_ref else "Not required (screened)"),
            ("Stored in", where),
            ("Retention", _retention(c)),
            ("On erasure", c.on_erasure.value.replace("_", " ")),
            ("Included in export", "Yes" if c.export else f"No — {c.export_exempt_reason}"),
            ("Recipients", "; ".join(recipients) or "None"),
            ("Transfers outside the EEA", "; ".join(transfers) or "None"),
            ("AI minimisation", c.ai_minimisation or "Not sent to AI"),
            ("Storage rule", c.storage_rule or "Standard (see security measures)"),
            ("Built in stage", str(c.stage)),
        ]
        out += [f"### {c.name} (`{c.id}`)", "", "| | |", "| --- | --- |"]
        out += [f"| {k} | {_esc(v)} |" for k, v in rows]
        out.append("")

    out += [
        "## Technical and organisational security measures (Art 32)",
        "",
        "Applies to every activity above; detail in `docs/06-security.md`.",
        "",
        "- Encryption in transit (TLS 1.2+, HSTS) and at rest (provider disk encryption;"
        " application-level encryption for email bodies and special category data;"
        " GPG-encrypted backups).",
        "- Passwordless authentication; step-up for sensitive actions; admin access with"
        " hardware keys only; least-privilege database roles.",
        "- Personal data redacted from logs and error reports (`app.privacy.redaction`).",
        "- Data minimisation before AI calls (`app.privacy.ai_guard`).",
        "- EU hosting; processors bound by DPAs; transfers covered as listed.",
        "- Automated retention and erasure jobs generated from this inventory;"
        " restore procedure re-applies erasures from tombstones.",
        "- Breach procedure with 72-hour notification clock (`docs/privacy/breach-runbook.md`).",
        "",
        "## Processors",
        "",
        "| Processor | Service | Location | Outside EEA | Transfer mechanism | DPA | From stage |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for p in inv.processors:
        out.append(
            f"| {_esc(p.name)} | {_esc(p.service)} | {_esc(p.location)} | "
            f"{'Yes' if p.outside_eea else 'No'} | {_esc(p.transfer_mechanism or '—')} | "
            f"{_esc(p.dpa)} | {p.from_stage} |"
        )
    out += [
        "",
        "## Automated retention (nightly job)",
        "",
        "| Table | Action | Category | After | Clock |",
        "| --- | --- | --- | --- | --- |",
    ]
    for a in retention_plan(inv):
        action = "delete rows" if a.kind == "delete_rows" else f"clear {', '.join(a.columns)}"
        out.append(f"| `{a.table}` | {action} | `{a.category}` | {a.days} days | `{a.clock}` |")
    out += [
        "",
        "## Table classification",
        "",
        "| Table | Default category | Column overrides | User link | Stage |",
        "| --- | --- | --- | --- | --- |",
    ]
    for t in inv.tables:
        overrides = ", ".join(f"`{k}` → `{v}`" for k, v in t.columns.items()) or "—"
        link = (
            f"`{t.user_column}`"
            if t.user_column
            else (f"via `{t.cascade_from}`" if t.cascade_from else "—")
        )
        out.append(f"| `{t.name}` | `{t.category}` | {overrides} | {link} | {t.stage} |")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(load_inventory()), end="")
