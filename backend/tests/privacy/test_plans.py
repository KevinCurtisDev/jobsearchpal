from app.privacy.plans import erasure_plan, export_plan, retention_plan
from app.privacy.registry import OnErasure, RetentionPolicy, load_inventory


def test_every_fixed_retention_category_has_an_action() -> None:
    inv = load_inventory()
    planned = {(a.table, a.category) for a in retention_plan(inv)}
    for t in inv.tables:
        for cid in t.categories():
            cat = inv.category(cid)
            if cat.retention.policy in (
                RetentionPolicy.FIXED,
                RetentionPolicy.AFTER_ACCOUNT_DELETION,
            ):
                assert (t.name, cid) in planned, f"{t.name}/{cid} has no retention action"


def test_email_bodies_cleared_at_90_days_but_metadata_kept() -> None:
    actions = [a for a in retention_plan(load_inventory()) if a.table == "inbound_emails"]
    assert len(actions) == 1
    a = actions[0]
    assert a.kind == "clear_columns" and a.days == 90
    assert set(a.columns) == {"body_text", "raw_s3_key", "from_address", "subject"}
    assert a.select_keys_sql and "raw_s3_key" in a.select_keys_sql
    assert a.sql.startswith("UPDATE public.inbound_emails SET body_text = NULL")


def test_practice_audio_gone_in_a_day_and_kept_recordings_respected() -> None:
    actions = {(a.table, a.category): a for a in retention_plan(load_inventory())}
    audio = actions[("recordings", "practice_audio")]
    assert audio.days == 1 and audio.columns == ("audio_s3_key",)
    transcripts = actions[("recordings", "practice_transcripts")]
    assert transcripts.days == 30 and "AND NOT keep" in transcripts.sql


def test_erasure_covers_every_personal_table() -> None:
    inv = load_inventory()
    steps = erasure_plan(inv)
    covered = {s.table for s in steps if s.action != "collect_storage_keys"}
    for t in inv.personal_tables():
        if t.user_column or t.cascade_from:
            assert t.name in covered, f"{t.name} not covered by erasure"
    assert steps[-1].table == "users" and steps[-1].action == "delete"


def test_erasure_order_keys_then_legal_then_anonymise_then_delete() -> None:
    steps = erasure_plan(load_inventory())
    orders = [s.order for s in steps]
    assert orders == sorted(orders)
    by_table = {s.table: s for s in steps if s.action != "collect_storage_keys"}
    assert by_table["consents"].action == "pseudonymise"
    assert by_table["subscriptions"].action == "pseudonymise"
    assert by_table["audit_log"].action == "anonymise"
    assert by_table["cv_versions"].action == "via_cascade"
    assert by_table["cv_documents"].action == "delete"
    keys = [s for s in steps if s.action == "collect_storage_keys"]
    assert {s.table for s in keys} >= {"uploaded_files", "inbound_emails", "recordings"}
    rec = next(s for s in keys if s.table == "recordings")
    assert rec.sql is not None and "JOIN public.practice_sessions t1" in rec.sql


def test_anonymised_tables_drop_the_user_link() -> None:
    inv = load_inventory()
    for s in erasure_plan(inv):
        if s.action == "anonymise":
            assert s.sql and "= NULL" in s.sql
            assert inv.category(inv.table(s.table).category).on_erasure is OnErasure.ANONYMISE


def test_export_includes_every_exportable_personal_table() -> None:
    inv = load_inventory()
    exported = {e.table for e in export_plan(inv)}
    for t in inv.personal_tables():
        if (t.user_column or t.cascade_from) and inv.category(t.category).export:
            assert t.name in exported
    sessions = next(e for e in export_plan(inv) if e.table == "sessions")
    assert "token_hash" in sessions.excluded_columns


def test_generated_sql_only_uses_bound_parameters() -> None:
    inv = load_inventory()
    sql = [a.sql for a in retention_plan(inv)] + [s.sql or "" for s in erasure_plan(inv)]
    for s in sql:
        assert "'" not in s and ";" not in s
