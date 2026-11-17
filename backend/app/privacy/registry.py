"""Load and validate the data inventory (data_inventory.toml).

The inventory is the single source of truth for what personal data we hold, why, on what
lawful basis, for how long, and what happens to it on erasure. Invalid inventories fail
loudly at import time in tests and CI — there is no "unknown" or "TBC" retention.
"""

from __future__ import annotations

import re
import tomllib
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

INVENTORY_PATH = Path(__file__).with_name("data_inventory.toml")

#: Erasure requests must be completed within this many days (GDPR Art 12(3): one month;
#: we use a stricter fixed number so the job and the promise to users are unambiguous).
ERASURE_DEADLINE_DAYS = 30

_IDENT = re.compile(r"^[a-z][a-z0-9_]{0,62}$")


class LawfulBasis(StrEnum):
    CONTRACT = "contract"  # Art 6(1)(b)
    CONSENT = "consent"  # Art 6(1)(a)
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Art 6(1)(f)
    LEGAL_OBLIGATION = "legal_obligation"  # Art 6(1)(c)
    NOT_APPLICABLE = "not_applicable"  # only for the not_personal category


class ConsentKind(StrEnum):
    """Things a user can switch on or off. Each needs a current version in consent.py."""

    BENCHMARKS = "benchmarks"
    EXPERIMENTS = "experiments"
    FAIRNESS_AUDIT = "fairness_audit"
    MARKETING = "marketing"
    VOICE_PRACTICE = "voice_practice"
    QUESTION_BANK = "question_bank"


class RetentionPolicy(StrEnum):
    ACCOUNT_LIFETIME = "account_lifetime"
    FIXED = "fixed"
    AFTER_ACCOUNT_DELETION = "after_account_deletion"
    UNTIL_WITHDRAWN = "until_withdrawn"
    TRANSIENT = "transient"
    NOT_APPLICABLE = "not_applicable"


class OnErasure(StrEnum):
    DELETE = "delete"
    ANONYMISE = "anonymise"
    RETAIN_LEGAL = "retain_legal"
    NOT_APPLICABLE = "not_applicable"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Retention(_Strict):
    policy: RetentionPolicy
    days: Annotated[int, Field(gt=0)] | None = None
    seconds: Annotated[int, Field(gt=0)] | None = None

    @model_validator(mode="after")
    def _days_when_needed(self) -> Self:
        needs_days = self.policy in (RetentionPolicy.FIXED, RetentionPolicy.AFTER_ACCOUNT_DELETION)
        if needs_days != (self.days is not None):
            raise ValueError(
                f"retention policy {self.policy} {'needs' if needs_days else 'must not have'} days"
            )
        needs_seconds = self.policy is RetentionPolicy.TRANSIENT
        if needs_seconds != (self.seconds is not None):
            raise ValueError(
                f"retention policy {self.policy} "
                f"{'needs' if needs_seconds else 'must not have'} seconds"
            )
        return self


class Processor(_Strict):
    id: str
    name: str
    service: str
    location: str
    outside_eea: bool
    transfer_mechanism: str | None = None
    dpa: str
    from_stage: int

    @model_validator(mode="after")
    def _transfer(self) -> Self:
        if self.outside_eea and not self.transfer_mechanism:
            raise ValueError(
                f"processor {self.id}: outside_eea requires transfer_mechanism (GDPR Ch. V)"
            )
        return self


class Category(_Strict):
    id: str
    name: str
    description: str
    data_subjects: list[str]
    purposes: Annotated[list[str], Field(min_length=1)]
    lawful_basis: LawfulBasis
    retention: Retention
    on_erasure: OnErasure
    export: bool
    processors: list[str]
    source: Literal["user", "system", "inbound_email", "public_sources"]
    stage: int

    consent_kind: ConsentKind | None = None
    lia_ref: str | None = None
    legal_ref: str | None = None
    dpia_ref: str | None = None
    special_category: bool = False
    art9_condition: Literal["explicit_consent"] | None = None
    sensitivity: Literal["normal", "high", "special"] = "normal"
    profiling: bool = False
    automated_decision_note: str | None = None
    export_exempt_reason: str | None = None
    export_fields_note: str | None = None
    third_party_basis: str | None = None
    ai_minimisation: str | None = None
    storage_rule: str | None = None
    stored_in: str | None = None
    retain_note: str | None = None
    retention_note: str | None = None

    @property
    def personal(self) -> bool:
        return self.lawful_basis is not LawfulBasis.NOT_APPLICABLE

    @model_validator(mode="after")
    def _rules(self) -> Self:
        errors: list[str] = []
        b = self.lawful_basis
        if self.personal:
            if not self.data_subjects:
                errors.append("personal data needs data_subjects")
            if self.retention.policy is RetentionPolicy.NOT_APPLICABLE:
                errors.append("personal data needs a retention policy")
            if self.on_erasure is OnErasure.NOT_APPLICABLE:
                errors.append("personal data needs an on_erasure rule")
        else:
            if self.retention.policy is not RetentionPolicy.NOT_APPLICABLE:
                errors.append("not_applicable basis must have not_applicable retention")
        if (b is LawfulBasis.CONSENT) != (self.consent_kind is not None):
            errors.append("consent_kind is required for, and only for, the consent basis")
        if b is LawfulBasis.LEGITIMATE_INTERESTS and not self.lia_ref:
            errors.append("legitimate_interests requires lia_ref (legitimate interests assessment)")
        if b is LawfulBasis.LEGAL_OBLIGATION and not self.legal_ref:
            errors.append("legal_obligation requires legal_ref")
        if self.special_category:
            if self.art9_condition is None or self.sensitivity != "special":
                errors.append("special category needs art9_condition and sensitivity=special")
            if not self.dpia_ref or not self.storage_rule:
                errors.append("special category needs dpia_ref and storage_rule")
        elif self.art9_condition is not None:
            errors.append("art9_condition set on non-special category")
        if self.profiling and not (self.dpia_ref and self.automated_decision_note):
            errors.append("profiling requires dpia_ref and automated_decision_note")
        if self.on_erasure is OnErasure.RETAIN_LEGAL and b is not LawfulBasis.LEGAL_OBLIGATION:
            errors.append("retain_legal is only allowed for the legal_obligation basis")
        if self.retention.policy is RetentionPolicy.AFTER_ACCOUNT_DELETION and (
            self.on_erasure is not OnErasure.RETAIN_LEGAL
        ):
            errors.append("after_account_deletion retention requires on_erasure=retain_legal")
        if (
            self.retention.policy is RetentionPolicy.UNTIL_WITHDRAWN
            and b is not LawfulBasis.CONSENT
        ):
            errors.append("until_withdrawn retention requires the consent basis")
        if not self.export and not self.export_exempt_reason:
            errors.append("export=false requires export_exempt_reason")
        if errors:
            raise ValueError(f"category {self.id}: " + "; ".join(errors))
        return self


class Table(_Strict):
    name: str
    category: str
    stage: int
    schema_: str = Field("public", alias="schema")
    user_column: str | None = None
    cascade_from: str | None = None
    retention_clock: str | None = None
    keep_column: str | None = None
    pseudonymise_column: str | None = None
    encrypted: list[str] = []
    storage_keys: list[str] = []
    columns: dict[str, str] = {}
    notes: str | None = None

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    def column_category(self, column: str) -> str:
        return self.columns.get(column, self.category)

    def categories(self) -> set[str]:
        return {self.category, *self.columns.values()}

    def identifiers(self) -> list[str]:
        cols = [self.user_column, self.cascade_from, self.retention_clock, self.keep_column]
        cols += [self.pseudonymise_column, *self.encrypted, *self.storage_keys, *self.columns]
        return [self.name, self.schema_, *(c for c in cols if c)]


class Ephemeral(_Strict):
    key: str
    store: Literal["redis", "object_storage"]
    category: str
    ttl_seconds: Annotated[int, Field(gt=0)]


class Controller(_Strict):
    name: str
    establishment: str
    lead_supervisory_authority: str
    uk_regulator: str
    uk_representative: str
    privacy_contact: str
    dpo: str


class Inventory(_Strict):
    schema_version: Literal[1]
    last_reviewed: str
    minimum_age: Annotated[int, Field(ge=16)]
    controller: Controller
    processors: list[Processor]
    categories: list[Category]
    tables: list[Table]
    ephemeral: list[Ephemeral]

    # ---- lookups -------------------------------------------------------------------------

    def category(self, category_id: str) -> Category:
        return self._categories[category_id]

    def table(self, name: str) -> Table:
        return self._tables[name]

    @property
    def _categories(self) -> dict[str, Category]:
        return {c.id: c for c in self.categories}

    @property
    def _tables(self) -> dict[str, Table]:
        return {t.name: t for t in self.tables}

    def is_personal(self, table: Table) -> bool:
        return any(self.category(c).personal for c in table.categories())

    def personal_tables(self) -> list[Table]:
        return [t for t in self.tables if self.is_personal(t)]

    # ---- cross-reference validation -------------------------------------------------------

    @model_validator(mode="after")
    def _cross_references(self) -> Self:
        errors: list[str] = []
        cats = {c.id: c for c in self.categories}
        procs = {p.id: p for p in self.processors}
        tables = {t.name: t for t in self.tables}
        for label, ids in (
            ("category", [c.id for c in self.categories]),
            ("processor", [p.id for p in self.processors]),
            ("table", [t.name for t in self.tables]),
        ):
            dupes = {i for i in ids if ids.count(i) > 1}
            if dupes:
                errors.append(f"duplicate {label} ids: {sorted(dupes)}")

        for c in self.categories:
            errors += [
                f"category {c.id}: unknown processor {p}" for p in c.processors if p not in procs
            ]

        bound: set[str] = {"not_personal"}
        for t in self.tables:
            for ident in t.identifiers():
                if not _IDENT.match(ident):
                    errors.append(f"table {t.name}: invalid identifier {ident!r}")
            for cid in t.categories():
                if cid not in cats:
                    errors.append(f"table {t.name}: unknown category {cid}")
                    continue
                bound.add(cid)
            if any(cid not in cats for cid in t.categories()):
                continue
            personal = any(cats[c].personal for c in t.categories())
            if personal:
                if (t.user_column is None) == (
                    t.cascade_from is None
                ) and t.name not in _NO_USER_LINK_OK:
                    errors.append(
                        f"table {t.name}: personal tables need exactly one of "
                        "user_column or cascade_from"
                    )
                if t.cascade_from and t.cascade_from not in tables:
                    errors.append(f"table {t.name}: cascade_from unknown table {t.cascade_from}")
                needs_clock = any(
                    cats[c].retention.policy is RetentionPolicy.FIXED for c in t.categories()
                )
                if needs_clock and not t.retention_clock:
                    errors.append(f"table {t.name}: fixed retention needs retention_clock")
                needs_pseudo = any(
                    cats[c].on_erasure is OnErasure.RETAIN_LEGAL and t.user_column
                    for c in t.categories()
                )
                if needs_pseudo and not t.pseudonymise_column:
                    errors.append(
                        f"table {t.name}: retain_legal with a user link needs pseudonymise_column"
                    )
                if (
                    any(cats[c].special_category for c in t.categories())
                    and t.schema_ != "sensitive"
                ):
                    errors.append(
                        f"table {t.name}: special category data must live in the 'sensitive' schema"
                    )
            if t.keep_column and not t.retention_clock:
                errors.append(f"table {t.name}: keep_column without retention_clock")

        for e in self.ephemeral:
            if e.category not in cats:
                errors.append(f"ephemeral {e.key}: unknown category {e.category}")
                continue
            bound.add(e.category)
            if e.ttl_seconds > ERASURE_DEADLINE_DAYS * 86400:
                errors.append(f"ephemeral {e.key}: TTL longer than the erasure deadline")

        for c in self.categories:
            if c.personal and c.id not in bound and not c.stored_in:
                errors.append(
                    f"category {c.id}: not bound to any table or ephemeral key and no stored_in"
                )

        if errors:
            raise ValueError("data inventory invalid:\n  - " + "\n  - ".join(errors))
        return self


#: Personal tables that intentionally have no direct user link (they hold hashes or counts).
_NO_USER_LINK_OK = frozenset(
    {
        "erasure_tombstones",
        "privacy_incidents",
        "job_postings",
        "job_postings_raw",
        "waitlist_signups",
    }
)


@lru_cache(maxsize=1)
def load_inventory(path: Path = INVENTORY_PATH) -> Inventory:
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    return Inventory.model_validate(data)
