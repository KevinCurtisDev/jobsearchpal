"""Check SQLAlchemy models against the data inventory.

Run in CI (tests/privacy/test_models_match_inventory.py). A model that is not in the
inventory, a column that cannot be classified, or a foreign key whose ON DELETE does not
match the declared erasure rule fails the build.
"""

from __future__ import annotations

import re

from sqlalchemy import MetaData
from sqlalchemy import Table as SATable

from app.privacy.registry import Inventory, OnErasure

#: Column names that suggest personal data. Such a column in a not_personal table fails.
PII_NAME_HINT = re.compile(
    r"(^|_)(email|phone|name|address|ip|dob|birth|ppsn|passport|user|body|transcript|cv)(_|$)"
)
#: Allowed in not_personal tables despite matching the hint (company or reference data).
PII_NAME_ALLOW = frozenset({"name", "normalized_name", "preferred_label", "company_name", "alias"})


def check(metadata: MetaData, inv: Inventory) -> list[str]:
    errors: list[str] = []
    known = {t.name: t for t in inv.tables}

    for sa in metadata.tables.values():
        entry = known.get(sa.name)
        if entry is None:
            errors.append(f"{sa.name}: table not in data_inventory.toml")
            continue
        cols = {c.name for c in sa.columns}
        schema = sa.schema or "public"
        if schema != entry.schema_:
            errors.append(f"{sa.name}: schema {schema} but inventory says {entry.schema_}")
        for ident in entry.identifiers()[2:]:
            if ident not in cols and ident != entry.cascade_from:
                errors.append(f"{sa.name}: inventory names column {ident!r} which does not exist")
        for col in entry.encrypted:
            if col in cols and not sa.columns[col].info.get("encrypted"):
                errors.append(
                    f"{sa.name}.{col}: must use the EncryptedText type (info['encrypted'])"
                )
        if entry.pseudonymise_column and "pseudonymised_at" not in cols:
            errors.append(f"{sa.name}: pseudonymised tables need a pseudonymised_at column")

        if not inv.is_personal(entry):
            for c in cols:
                if PII_NAME_HINT.search(c) and c not in PII_NAME_ALLOW:
                    errors.append(
                        f"{sa.name}.{c}: looks personal but the table is classified not_personal"
                    )
            continue

        errors += _check_foreign_keys(sa, entry.name, inv)
    return errors


def _check_foreign_keys(sa: SATable, name: str, inv: Inventory) -> list[str]:
    errors: list[str] = []
    entry = inv.table(name)
    rule = inv.category(entry.category).on_erasure
    for fk in sa.foreign_keys:
        target = fk.column.table.name
        ondelete = (fk.ondelete or "").upper()
        if entry.user_column and fk.parent.name == entry.user_column and target == "users":
            expected = "CASCADE" if rule is OnErasure.DELETE else "SET NULL"
            if ondelete != expected:
                errors.append(f"{name}.{fk.parent.name}: ON DELETE must be {expected} ({rule})")
        if entry.cascade_from and target == entry.cascade_from and ondelete != "CASCADE":
            errors.append(f"{name}.{fk.parent.name}: ON DELETE must be CASCADE (cascade_from)")
    if entry.cascade_from and not any(
        fk.column.table.name == entry.cascade_from for fk in sa.foreign_keys
    ):
        errors.append(f"{name}: no foreign key to cascade_from table {entry.cascade_from}")
    return errors
