"""The data inventory is complete, consistent and matches the docs and the models."""

import copy
import re
import tomllib
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.privacy.consent import CURRENT_VERSIONS
from app.privacy.registry import (
    INVENTORY_PATH,
    ConsentKind,
    Inventory,
    LawfulBasis,
    load_inventory,
)

REPO = Path(__file__).resolve().parents[3]
DOCS = REPO / "docs"


def _raw() -> dict[str, Any]:
    with INVENTORY_PATH.open("rb") as fh:
        return tomllib.load(fh)


def _category(data: dict[str, Any], cid: str) -> dict[str, Any]:
    return next(c for c in data["categories"] if c["id"] == cid)


def test_inventory_is_valid() -> None:
    inv = load_inventory()
    assert inv.personal_tables()
    assert inv.minimum_age >= 16


def test_every_consent_kind_has_a_version_and_a_category_or_use() -> None:
    inv = load_inventory()
    used = {c.consent_kind for c in inv.categories if c.consent_kind}
    for kind in ConsentKind:
        assert kind in CURRENT_VERSIONS
    # question_bank feeds a not_personal table after redaction, so it has no category
    assert set(ConsentKind) - used == {ConsentKind.QUESTION_BANK}


def test_every_special_category_lives_in_sensitive_schema_and_is_encrypted() -> None:
    inv = load_inventory()
    for t in inv.tables:
        if any(inv.category(c).special_category for c in t.categories()):
            assert t.schema_ == "sensitive"
            assert t.encrypted


def test_every_processor_used_is_declared_and_transfers_documented() -> None:
    inv = load_inventory()
    procs = {p.id: p for p in inv.processors}
    for c in inv.categories:
        for p in c.processors:
            assert p in procs
            if procs[p].outside_eea:
                assert procs[p].transfer_mechanism


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: _category(d, "sessions").pop("lia_ref"), "lia_ref"),
        (lambda d: _category(d, "practice_audio").pop("consent_kind"), "consent_kind"),
        (lambda d: _category(d, "fairness_demographics").pop("art9_condition"), "art9_condition"),
        (lambda d: _category(d, "match_results").pop("dpia_ref"), "dpia_ref"),
        (lambda d: _category(d, "billing_records").pop("legal_ref"), "legal_ref"),
        (lambda d: _category(d, "cv_content").update(retention={"policy": "fixed"}), "days"),
        (lambda d: _category(d, "cv_content").update(on_erasure="retain_legal"), "retain_legal"),
        (lambda d: _category(d, "cv_content").update(export=False), "export_exempt_reason"),
        (lambda d: _category(d, "cv_content").update(processors=["nope"]), "unknown processor"),
        (lambda d: d["processors"][2].pop("transfer_mechanism"), "transfer_mechanism"),
        (lambda d: d["tables"][2].pop("retention_clock"), "retention_clock"),
        (lambda d: d["tables"].append({"name": "x", "category": "nope", "stage": 1}), "unknown category"),
        (lambda d: d["tables"].append({"name": "users", "category": "account_identity", "stage": 1}), "duplicate"),
        (lambda d: d["tables"].append({"name": "x", "category": "cv_content", "stage": 2}), "user_column"),
        (lambda d: d["tables"].append({"name": "x;drop", "category": "not_personal", "stage": 2}), "identifier"),
        (lambda d: d["ephemeral"].append({"key": "k", "store": "redis", "category": "cv_content", "ttl_seconds": 99999999}), "TTL"),
        (lambda d: d.update(minimum_age=13), "minimum_age"),
        (lambda d: _category(d, "cv_content").update(retention={"policy": "indefinite"}), "retention"),
    ],
)  # fmt: skip
def test_inventory_rejects_ambiguous_or_unlawful_entries(mutate: Any, message: str) -> None:
    data = copy.deepcopy(_raw())
    mutate(data)
    with pytest.raises(ValidationError, match=message):
        Inventory.model_validate(data)


def test_every_table_in_the_data_model_doc_is_classified() -> None:
    doc = (DOCS / "04-data-model.md").read_text()
    documented: set[str] = set()
    for line in doc.splitlines():
        m = re.match(r"^\| (`[a-z_]+`(?:, `[a-z_]+`)*) \|", line)
        if m:
            documented |= set(re.findall(r"`([a-z_]+)`", m.group(1)))
    inventory = {t.name for t in load_inventory().tables}
    assert documented - inventory == set(), "tables in docs/04 missing from the inventory"
    assert inventory - documented == set(), "tables in the inventory missing from docs/04"


def test_lia_and_dpia_documents_exist() -> None:
    inv = load_inventory()
    refs = {c.lia_ref for c in inv.categories if c.lia_ref}
    refs |= {c.dpia_ref for c in inv.categories if c.dpia_ref}
    for ref in refs:
        assert (REPO / ref).is_file(), f"missing {ref}"


def test_records_of_processing_is_up_to_date() -> None:
    from app.privacy.ropa import render

    committed = DOCS / "privacy" / "records-of-processing.md"
    assert committed.read_text() == render(load_inventory()), "run `make privacy-docs`"


def test_not_personal_category_only_for_reference_data() -> None:
    inv = load_inventory()
    np = inv.category("not_personal")
    assert np.lawful_basis is LawfulBasis.NOT_APPLICABLE
    for t in inv.tables:
        if t.category == "not_personal":
            assert t.user_column is None and t.cascade_from is None


def test_every_consent_has_wording_and_wording_changes_need_a_version_bump() -> None:
    import hashlib
    import json

    folder = REPO / "content" / "consents"
    lock = json.loads((folder / "wording.lock.json").read_text())
    for kind, version in CURRENT_VERSIONS.items():
        name = f"{kind}.v{version}"
        path = folder / f"{name}.md"
        assert path.is_file(), f"missing wording {path.name}"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert lock.get(name) == digest, (
            f"{path.name} changed. If the meaning changed, create v{version + 1} and bump "
            "CURRENT_VERSIONS; for a typo fix, run `make privacy-lock` with owner approval."
        )
