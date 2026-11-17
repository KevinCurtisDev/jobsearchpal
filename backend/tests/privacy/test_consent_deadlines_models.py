from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, MetaData, String, Table, Text

from app.db.base import Base
from app.privacy import consent
from app.privacy.consent import Acknowledgement, ConsentRecord, ConsentRequiredError
from app.privacy.deadlines import breach_notify_by, dsar_due, dsar_extended_due, erasure_due
from app.privacy.model_check import check
from app.privacy.registry import ConsentKind, load_inventory

T0 = datetime(2026, 10, 20, 9, 0, tzinfo=UTC)


def rec(
    kind: str, granted: bool, version: int = 1, minutes: int = 0, source: str = "settings"
) -> ConsentRecord:
    return ConsentRecord(kind, version, granted, T0 + timedelta(minutes=minutes), source)


# ---- consent ---------------------------------------------------------------------------------


def test_consent_defaults_to_off() -> None:
    assert not consent.current_state([], ConsentKind.BENCHMARKS)
    with pytest.raises(ConsentRequiredError):
        consent.require([], ConsentKind.BENCHMARKS)


def test_latest_record_wins_and_withdrawal_is_immediate() -> None:
    records = [rec("benchmarks", True), rec("benchmarks", False, minutes=5)]
    assert not consent.current_state(records, ConsentKind.BENCHMARKS)
    records.append(rec("benchmarks", True, minutes=10))
    assert consent.current_state(records, ConsentKind.BENCHMARKS)


def test_old_version_is_not_valid_consent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(consent.CURRENT_VERSIONS, ConsentKind.EXPERIMENTS, 2)
    records = [rec("experiments", True, version=1)]
    assert not consent.current_state(records, ConsentKind.EXPERIMENTS)
    assert consent.needs_reconsent(records, ConsentKind.EXPERIMENTS)


def test_invalid_records_rejected() -> None:
    with pytest.raises(ValueError, match="unknown consent kind"):
        consent.validate_new_record(rec("analytics", True))
    with pytest.raises(ValueError, match="only withdraw"):
        consent.validate_new_record(rec("marketing", True, source="email_unsubscribe"))
    with pytest.raises(ValueError, match="current version"):
        consent.validate_new_record(rec("marketing", True, version=0))
    consent.validate_new_record(rec("marketing", False, source="email_unsubscribe"))
    consent.validate_new_record(rec(Acknowledgement.TERMS, True, source="onboarding"))


# ---- deadlines -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("received", "due"),
    [
        (date(2026, 1, 15), date(2026, 2, 15)),
        (date(2026, 1, 31), date(2026, 2, 28)),
        (date(2028, 1, 31), date(2028, 2, 29)),
        (date(2026, 12, 20), date(2027, 1, 20)),
    ],
)
def test_dsar_one_month(received: date, due: date) -> None:
    assert dsar_due(received) == due


def test_extension_and_erasure_and_breach() -> None:
    assert dsar_extended_due(date(2026, 1, 31)) == date(2026, 4, 30)
    assert erasure_due(date(2026, 2, 1)) == date(2026, 3, 1)  # month shorter than 30 days
    assert erasure_due(date(2026, 3, 1)) == date(2026, 3, 31)
    assert breach_notify_by(T0) == T0 + timedelta(hours=72)
    with pytest.raises(ValueError):
        breach_notify_by(datetime(2026, 1, 1))


# ---- models vs inventory ---------------------------------------------------------------------


def test_real_models_match_inventory() -> None:
    import app.models  # noqa: F401  (registers every model)

    assert check(Base.metadata, load_inventory()) == []


def _users(md: MetaData) -> Table:
    return Table("users", md, Column("id", String, primary_key=True), Column("email", String))


def test_model_check_catches_mistakes() -> None:
    md = MetaData()
    _users(md)
    Table("mystery", md, Column("id", String, primary_key=True))
    Table(
        "audit_log", md,
        Column("id", String, primary_key=True),
        Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),  # should be SET NULL
        Column("occurred_at", DateTime),
    )  # fmt: skip
    Table(
        "cv_documents", md,
        Column("id", String, primary_key=True),
        Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),
    )  # fmt: skip
    Table(
        "cv_versions", md,
        Column("id", String, primary_key=True),
        Column("cv_document_id", ForeignKey("cv_documents.id")),  # missing CASCADE
    )  # fmt: skip
    Table("skills", md, Column("id", String, primary_key=True), Column("user_email", String))
    Table(
        "inbound_emails", md,
        Column("id", String, primary_key=True),
        Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),
        Column("received_at", DateTime), Column("body_text", Text),
        Column("raw_s3_key", String), Column("from_address", String), Column("subject", String),
    )  # fmt: skip
    Table(
        "recordings", md, Column("id", String, primary_key=True), Column("keep", Boolean),
    )  # fmt: skip
    errors = "\n".join(check(md, load_inventory()))
    assert "mystery: table not in data_inventory.toml" in errors
    assert "audit_log.user_id: ON DELETE must be SET NULL" in errors
    assert "cv_versions.cv_document_id: ON DELETE must be CASCADE" in errors
    assert "skills.user_email: looks personal" in errors
    assert "inbound_emails.body_text: must use the EncryptedText type" in errors
    assert "recordings: inventory names column 'created_at' which does not exist" in errors
    assert "recordings: no foreign key to cascade_from table practice_sessions" in errors
    assert "cv_documents" not in errors
