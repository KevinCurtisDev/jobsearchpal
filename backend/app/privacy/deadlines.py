"""Legal deadlines, computed one way everywhere.

- Rights requests (Art 12(3)): "without undue delay and in any event within one month of
  receipt", extendable by two further months for complex or numerous requests, telling
  the person within the first month. A month runs to the same date in the next month,
  or the last day of that month if there is no such date (EDPB Guidelines 01/2022).
- Our own targets are stricter: export ready within 24 hours (automated), erasure
  completed within 30 days (ERASURE_DEADLINE_DAYS).
- Breach notification (Art 33): to the DPC within 72 hours of becoming aware, unless
  the breach is unlikely to result in a risk to people. UK users: the ICO, same 72 hours.
- Breach communication to people (Art 34): without undue delay when high risk.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta

from app.privacy.registry import ERASURE_DEADLINE_DAYS

BREACH_NOTIFY_HOURS = 72
EXPORT_TARGET_HOURS = 24


def add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def dsar_due(received: date) -> date:
    """Legal deadline for a rights request received on `received`."""
    return add_months(received, 1)


def dsar_extended_due(received: date) -> date:
    """Latest deadline if extended (person must be told before dsar_due)."""
    return add_months(received, 3)


def erasure_due(requested: date) -> date:
    """Our committed erasure deadline: the earlier of 30 days and the legal month."""
    return min(requested + timedelta(days=ERASURE_DEADLINE_DAYS), dsar_due(requested))


def breach_notify_by(aware_at: datetime) -> datetime:
    if aware_at.tzinfo is None:
        raise ValueError("aware_at must be timezone-aware")
    return aware_at + timedelta(hours=BREACH_NOTIFY_HOURS)
