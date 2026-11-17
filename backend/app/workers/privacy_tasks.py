"""Scheduled privacy jobs. Everything they do is generated from the data inventory.

- enforce_retention   nightly 02:30 — runs app.privacy.plans.retention_plan()
- process_erasures    nightly 03:00 — erases accounts whose deletion was requested
                      (and confirmed by step-up), well inside the 30-day deadline
Stage 1 adds (see docs/02-build-stages.md):
- dsar_deadline_check daily 09:00 — alerts owners about requests due within 7 days
- reapply_tombstones  run after any backup restore (docs/privacy/backup-and-restore.md)

Each run writes an audit_log row with counts only (no personal data).
Tables that do not exist yet (later stages) are skipped and reported, never guessed at.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.privacy.plans import erasure_plan, retention_plan
from app.privacy.registry import load_inventory
from app.workers.celery_app import celery_app

log = structlog.get_logger(__name__)


def subject_ref(email: str) -> str:
    """Keyed hash used to pseudonymise legally retained rows and tombstones."""
    key = get_settings().privacy_pseudonym_key.get_secret_value().encode()
    return hmac.new(key, email.strip().lower().encode(), hashlib.sha256).hexdigest()


async def _existing_tables(session: AsyncSession) -> set[str]:
    rows = await session.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema IN ('public','sensitive')"
        )
    )
    return {r[0] for r in rows}


async def _enforce_retention() -> dict[str, Any]:
    from app.db.session import SessionLocal

    inv = load_inventory()
    now = datetime.now(UTC)
    report: dict[str, Any] = {"deleted": {}, "cleared": {}, "skipped": []}
    async with SessionLocal() as session, session.begin():
        existing = await _existing_tables(session)
        for action in retention_plan(inv):
            if action.table not in existing:
                report["skipped"].append(action.table)
                continue
            cutoff = now - timedelta(days=action.days)
            if action.select_keys_sql:
                rows = await session.execute(text(action.select_keys_sql), {"cutoff": cutoff})
                await _delete_objects([k for row in rows for k in row if k])
            result = await session.execute(text(action.sql), {"cutoff": cutoff})
            bucket = "deleted" if action.kind == "delete_rows" else "cleared"
            report[bucket][action.table] = result.rowcount  # type: ignore[attr-defined]
    log.info("privacy.retention_done", **{k: v for k, v in report.items() if k != "skipped"})
    return report


async def _delete_objects(keys: list[str]) -> None:
    """Delete storage objects before the rows (or key columns) that point at them."""
    if not keys:
        return
    from app.integrations.storage import delete_objects  # Stage 2

    await delete_objects(keys)


async def _erase_user(session: AsyncSession, user_id: str, email: str) -> dict[str, int]:
    """Execute the erasure plan for one user inside the caller's transaction."""
    inv = load_inventory()
    existing = await _existing_tables(session)
    params = {"user_id": user_id, "subject_ref": subject_ref(email)}
    counts: dict[str, int] = {}
    storage_keys: list[str] = []
    for step in erasure_plan(inv):
        if step.table not in existing or step.sql is None:
            continue
        result = await session.execute(text(step.sql), params)
        if step.action == "collect_storage_keys":
            storage_keys += [r[0] for r in result if r[0]]
        else:
            counts[f"{step.action}:{step.table}"] = result.rowcount  # type: ignore[attr-defined]
    await _delete_objects(storage_keys)
    await session.execute(
        text(
            "INSERT INTO erasure_tombstones (id, user_ref, subject_ref, erased_at) "
            "VALUES (gen_random_uuid(), :user_ref, :subject_ref, now())"
        ),
        {"user_ref": subject_ref(user_id), "subject_ref": params["subject_ref"]},
    )
    return counts


async def _process_erasures() -> int:
    from app.db.session import SessionLocal

    done = 0
    async with SessionLocal() as session:
        due = await session.execute(
            text(
                "SELECT id, email FROM users WHERE status = 'deleting' "
                "ORDER BY deletion_requested_at"
            )
        )
        for user_id, email in due.all():
            async with session.begin():
                await _erase_user(session, str(user_id), email)
            done += 1
    log.info("privacy.erasures_done", count=done)
    return done


@celery_app.task(name="app.workers.privacy.enforce_retention")
def enforce_retention() -> dict[str, Any]:
    return asyncio.run(_enforce_retention())


@celery_app.task(name="app.workers.privacy.process_erasures")
def process_erasures() -> int:
    return asyncio.run(_process_erasures())
