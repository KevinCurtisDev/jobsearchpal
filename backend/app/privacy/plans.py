"""Turn the data inventory into concrete retention, erasure and export plans.

Nothing here is hand-written per table: if a table is added to the inventory, it is
automatically covered by retention, erasure and export. The plans are pure data (and SQL
text with validated identifiers) so they are unit-tested without a database; the Celery
jobs in `app/workers/privacy_tasks.py` execute them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.privacy.registry import Inventory, OnErasure, RetentionPolicy, Table

# ---------------------------------------------------------------------------------------------
# Retention
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RetentionAction:
    """One statement run by the nightly retention job. `:cutoff` = now() - days."""

    table: str
    kind: Literal["delete_rows", "clear_columns"]
    category: str
    days: int
    clock: str
    sql: str
    storage_keys: tuple[str, ...] = ()
    columns: tuple[str, ...] = ()
    select_keys_sql: str | None = None  # run first: objects are deleted before their keys


def _keys_sql(t: Table, keys: list[str] | tuple[str, ...], keep: str) -> str | None:
    if not keys:
        return None
    return (
        f"SELECT {', '.join(keys)} FROM {_qualified(t)} WHERE {t.retention_clock} < :cutoff{keep}"
    )


def _qualified(t: Table) -> str:
    return f"{t.schema_}.{t.name}"


def retention_plan(inv: Inventory) -> list[RetentionAction]:
    actions: list[RetentionAction] = []
    for t in inv.tables:
        default = inv.category(t.category)
        keep = f" AND NOT {t.keep_column}" if t.keep_column else ""
        if default.retention.policy is RetentionPolicy.FIXED:
            assert t.retention_clock and default.retention.days
            actions.append(
                RetentionAction(
                    table=t.name,
                    kind="delete_rows",
                    category=default.id,
                    days=default.retention.days,
                    clock=t.retention_clock,
                    sql=f"DELETE FROM {_qualified(t)} WHERE {t.retention_clock} < :cutoff{keep}",
                    storage_keys=tuple(t.storage_keys),
                    select_keys_sql=_keys_sql(t, t.storage_keys, keep),
                )
            )
        if default.retention.policy is RetentionPolicy.AFTER_ACCOUNT_DELETION:
            assert t.pseudonymise_column and default.retention.days
            actions.append(
                RetentionAction(
                    table=t.name,
                    kind="delete_rows",
                    category=default.id,
                    days=default.retention.days,
                    clock="pseudonymised_at",
                    sql=f"DELETE FROM {_qualified(t)} WHERE pseudonymised_at < :cutoff",
                )
            )
        # Column-level overrides with a shorter fixed retention than the row.
        by_category: dict[str, list[str]] = {}
        for col, cid in t.columns.items():
            if cid != t.category and inv.category(cid).retention.policy is RetentionPolicy.FIXED:
                by_category.setdefault(cid, []).append(col)
        for cid, cols in sorted(by_category.items()):
            cat = inv.category(cid)
            assert t.retention_clock and cat.retention.days
            sets = ", ".join(f"{c} = NULL" for c in sorted(cols))
            not_null = " OR ".join(f"{c} IS NOT NULL" for c in sorted(cols))
            actions.append(
                RetentionAction(
                    table=t.name,
                    kind="clear_columns",
                    category=cid,
                    days=cat.retention.days,
                    clock=t.retention_clock,
                    sql=(
                        f"UPDATE {_qualified(t)} SET {sets} "
                        f"WHERE {t.retention_clock} < :cutoff AND ({not_null}){keep}"
                    ),
                    storage_keys=tuple(sorted(c for c in cols if c in t.storage_keys)),
                    columns=tuple(sorted(cols)),
                    select_keys_sql=_keys_sql(
                        t, tuple(sorted(c for c in cols if c in t.storage_keys)), keep
                    ),
                )
            )
    return actions


# ---------------------------------------------------------------------------------------------
# Erasure (right to be forgotten, and account deletion)
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ErasureStep:
    order: int
    table: str
    action: Literal["collect_storage_keys", "anonymise", "pseudonymise", "delete", "via_cascade"]
    sql: str | None
    note: str = ""


def _user_root(inv: Inventory, t: Table) -> list[Table]:
    """Path from a table up to the table holding user_column (inclusive)."""
    path = [t]
    seen = {t.name}
    while path[-1].cascade_from:
        parent = inv.table(path[-1].cascade_from)
        if parent.name in seen:
            raise ValueError(f"cascade cycle at {parent.name}")
        seen.add(parent.name)
        path.append(parent)
    return path


def _select_for_user(inv: Inventory, t: Table, columns: str) -> str:
    """SELECT ... FROM t joined up the cascade chain to the user column, filtered by :user_id."""
    path = _user_root(inv, t)
    root = path[-1]
    if root.user_column is None:
        raise ValueError(f"table {t.name} has no route to a user")
    sql = f"SELECT {columns} FROM {_qualified(path[0])} t0"
    for i in range(1, len(path)):
        child, parent = path[i - 1], path[i]
        sql += f" JOIN {_qualified(parent)} t{i} ON t{i - 1}.{_fk_name(child, parent)} = t{i}.id"
    alias = f"t{len(path) - 1}"
    return f"{sql} WHERE {alias}.{root.user_column} = :user_id"


def _fk_name(child: Table, parent: Table) -> str:
    # Convention from docs/04: foreign keys are named <singular parent>_id.
    singular = parent.name[:-1] if parent.name.endswith("s") else parent.name
    return f"{singular}_id"


def erasure_plan(inv: Inventory) -> list[ErasureStep]:
    steps: list[ErasureStep] = []
    personal = [t for t in inv.personal_tables() if t.user_column or t.cascade_from]

    # 1. Object storage keys must be collected before rows disappear.
    for t in personal:
        for col in t.storage_keys:
            steps.append(
                ErasureStep(
                    0, t.name, "collect_storage_keys", _select_for_user(inv, t, f"t0.{col}")
                )
            )

    # 2. Rows kept for legal reasons: replace the user link with a keyed hash.
    # 3. Rows kept for security statistics: drop the user link.
    for t in personal:
        if not t.user_column or t.name == "users":
            continue
        rule = inv.category(t.category).on_erasure
        if rule is OnErasure.RETAIN_LEGAL:
            sql = (
                f"UPDATE {_qualified(t)} SET {t.pseudonymise_column} = :subject_ref, "
                f"{t.user_column} = NULL, pseudonymised_at = now() WHERE {t.user_column} = :user_id"
            )
            steps.append(ErasureStep(1, t.name, "pseudonymise", sql))
        elif rule is OnErasure.ANONYMISE:
            sql = (
                f"UPDATE {_qualified(t)} SET {t.user_column} = NULL "
                f"WHERE {t.user_column} = :user_id"
            )
            steps.append(ErasureStep(2, t.name, "anonymise", sql))

    # 4. Delete everything else that links directly to the user; children go by FK cascade.
    for t in personal:
        if t.name == "users":
            continue
        rule = inv.category(t.category).on_erasure
        if t.user_column and rule is OnErasure.DELETE:
            sql = f"DELETE FROM {_qualified(t)} WHERE {t.user_column} = :user_id"
            steps.append(ErasureStep(3, t.name, "delete", sql))
        elif t.cascade_from:
            steps.append(
                ErasureStep(
                    3, t.name, "via_cascade", None, f"ON DELETE CASCADE from {t.cascade_from}"
                )
            )

    # 5. Finally the user row itself.
    users = inv.table("users")
    steps.append(
        ErasureStep(4, "users", "delete", f"DELETE FROM {_qualified(users)} WHERE id = :user_id")
    )
    return sorted(steps, key=lambda s: (s.order, s.table))


# ---------------------------------------------------------------------------------------------
# Export (right of access, Art 15; portability, Art 20)
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExportEntry:
    table: str
    file: str
    sql: str
    excluded_columns: tuple[str, ...] = field(default=())


#: Columns never exported (security secrets with no meaning to the user).
EXPORT_EXCLUDED: dict[str, tuple[str, ...]] = {
    "passkey_credentials": ("public_key", "credential_id"),
    "sessions": ("token_hash",),
    "inbound_addresses": (),
}


def export_plan(inv: Inventory) -> list[ExportEntry]:
    entries: list[ExportEntry] = []
    for t in inv.personal_tables():
        if not (t.user_column or t.cascade_from):
            continue
        if not inv.category(t.category).export:
            continue
        excluded = EXPORT_EXCLUDED.get(t.name, ())
        # The exporter selects t0.* and drops excluded columns after reading.
        entries.append(
            ExportEntry(
                table=t.name,
                file=f"{t.name}.json",
                sql=_select_for_user(inv, t, "t0.*"),
                excluded_columns=excluded,
            )
        )
    return entries
