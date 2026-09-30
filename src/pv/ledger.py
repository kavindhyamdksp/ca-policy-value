"""Policy ledger: load, validate, filter by as-of date and legal status, resolve overrides (ADR-0002)."""

from __future__ import annotations

import datetime as dt
import hashlib
import itertools
import json
import os
import subprocess
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Literal

import jsonschema
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

Scalar = float | int | str | bool
Value = float | int | str | dict[str, Scalar]

LegalStatus = Literal["announced", "proposed", "enacted", "in_force", "superseded", "repealed", "observation"]
MinStatus = Literal["announced", "proposed", "enacted", "in_force"]

STATUS_RANK: dict[str, int] = {"announced": 0, "proposed": 1, "enacted": 2, "in_force": 3}
FRESHNESS_SLA_DAYS: dict[str, int] = {
    "statute": 180,
    "guidance": 180,
    "announcement": 100,
    "market_observation": 100,
    "statistic": 400,
}
UNITS = frozenset(
    {"CAD/t", "CAD/GJ", "CAD/MWh", "cents/kWh", "fraction", "g/kWh", "t/GJ", "kt", "Mt", "CAD", "text"}
)
PROVINCES = frozenset({"AB", "ON", "BC", "QC"})
PRIMARY = frozenset({"primary_legal", "primary_gov"})
OVERRIDE_URL = "urn:pv:user-override"


class LedgerError(ValueError):
    """Raised for invalid ledger content or an unresolved record."""


class Source(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    url: str
    title: str
    publisher: str
    published: dt.date | None
    retrieved: dt.date
    locator: str
    excerpt: str = ""
    source_type: Literal["primary_legal", "primary_gov", "secondary"]


class Record(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    jurisdiction: Literal["FED", "AB", "ON", "BC", "QC"]
    instrument: str
    parameter: str
    value: Value
    unit: str
    currency_basis: str
    effective_from: dt.date
    effective_to: dt.date | None = None
    legal_status: LegalStatus
    confidence: Literal["high", "medium", "low"]
    eligibility_confidence: dict[str, Literal["likely", "case_by_case", "not_listed"]] | None = None
    freshness: Literal["statute", "guidance", "announcement", "market_observation", "statistic"]
    sources: tuple[Source, ...] = Field(min_length=1)
    notes: str = ""
    reviewer: str = ""
    recorded_at: dt.date
    supersedes: str | None = None
    # Set by the loader, not stored in YAML.
    file: str = Field(default="", exclude=True)
    overridden: bool = Field(default=False, exclude=True)
    override_reason: str = Field(default="", exclude=True)

    @property
    def retrieved(self) -> dt.date:
        return max(s.retrieved for s in self.sources)

    @property
    def has_primary(self) -> bool:
        return any(s.source_type in PRIMARY for s in self.sources)

    def passes(self, min_status: MinStatus) -> bool:
        if self.legal_status == "observation":
            return True
        if self.legal_status in ("superseded", "repealed"):
            return False
        return STATUS_RANK[self.legal_status] >= STATUS_RANK[min_status]

    def is_stale(self, as_of: dt.date) -> bool:
        if self.overridden:
            return False
        return (as_of - self.retrieved).days > FRESHNESS_SLA_DAYS[self.freshness]

    def series(self) -> dict[int, float]:
        if not isinstance(self.value, dict):
            raise LedgerError(f"{self.id}: value is not a year series")
        return {int(k): float(v) for k, v in self.value.items() if not isinstance(v, str)}

    def table(self) -> dict[str, Scalar]:
        if not isinstance(self.value, dict):
            raise LedgerError(f"{self.id}: value is not a table")
        return dict(self.value)

    def num(self, key: str | None = None) -> float:
        v = self.value if key is None else self.table().get(key)
        if isinstance(v, bool) or not isinstance(v, int | float):
            raise LedgerError(f"{self.id}: {key or 'value'} is not numeric")
        return float(v)


class Override(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    record: str
    value: Value
    reason: str = Field(min_length=3)

    @field_validator("value", mode="before")
    @classmethod
    def _keys(cls, v: object) -> object:
        if isinstance(v, dict):
            if any(isinstance(k, bool) for k in v):
                raise ValueError('override key parsed as boolean — quote province codes ("ON")')
            return {str(k): val for k, val in v.items()}
        return v


# ---------------------------------------------------------------- loading


def _jsonable(obj: Any) -> Any:
    """YAML → JSON-compatible (dates to ISO strings, keys to strings) for schema checks and hashing."""
    if isinstance(obj, dict):
        return {("ON" if k is True else str(k)): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, dt.date):
        return obj.isoformat()
    return obj


def _bool_province_errors(raw: Any, where: str) -> list[str]:
    """Bare `ON` in YAML 1.1 parses as boolean true; flag it wherever a province code belongs."""
    errs: list[str] = []
    if isinstance(raw, dict):
        for k, v in raw.items():
            if isinstance(k, bool):
                errs.append(f'{where}: key {k!r} is a boolean — quote province codes ("ON")')
            if k == "jurisdiction" and isinstance(v, bool):
                errs.append(f'{where}: jurisdiction {v!r} is a boolean — quote "ON"')
            errs += _bool_province_errors(v, where)
    elif isinstance(raw, list):
        for v in raw:
            errs += _bool_province_errors(v, where)
    return errs


_SCHEMA: dict[str, Any] | None = None


def schema() -> dict[str, Any]:
    global _SCHEMA
    if _SCHEMA is None:
        _SCHEMA = json.loads((default_ledger_dir() / "schema" / "record.schema.json").read_text())
    return _SCHEMA


def default_ledger_dir() -> Path:
    env = os.environ.get("PV_LEDGER")
    if env:
        return Path(env)
    repo = Path(__file__).resolve().parents[2] / "ledger"
    if (repo / "schema").is_dir():
        return repo
    return Path(str(resources.files("pv") / "_ledger"))


@dataclass(frozen=True)
class Ledger:
    records: tuple[Record, ...]
    version: str
    digest: str
    errors: tuple[str, ...] = ()

    def ids(self) -> list[str]:
        return sorted({r.id for r in self.records})

    def view(
        self,
        as_of: dt.date,
        min_legal_status: MinStatus = "enacted",
        overrides: Iterable[Override] = (),
    ) -> LedgerView:
        visible = [r for r in self.records if r.recorded_at <= as_of]
        by_id: dict[str, list[Record]] = {}
        for r in visible:
            by_id.setdefault(r.id, []).append(r)
        for ov in overrides:
            by_id[ov.record] = [_override_record(ov, by_id.get(ov.record, []), as_of)]
        return LedgerView(by_id, as_of, min_legal_status, self.version, self.digest)


def _override_record(ov: Override, existing: list[Record], as_of: dt.date) -> Record:
    base = existing[0] if existing else None
    src = Source(
        url=OVERRIDE_URL,
        title=f"User override: {ov.reason}",
        publisher="case file",
        published=None,
        retrieved=as_of,
        locator="overrides[]",
        source_type="secondary",
    )
    return Record(
        id=ov.record,
        jurisdiction=base.jurisdiction if base else "FED",
        instrument=base.instrument if base else "override",
        parameter=base.parameter if base else ov.record,
        value=ov.value,
        unit=base.unit if base else "text",
        currency_basis=base.currency_basis if base else "n/a",
        effective_from=min((r.effective_from for r in existing), default=dt.date(1900, 1, 1)),
        legal_status=max(existing, key=lambda r: STATUS_RANK.get(r.legal_status, 9)).legal_status
        if existing
        else "in_force",
        confidence="low",
        freshness=base.freshness if base else "statute",
        sources=(src,),
        recorded_at=as_of,
        overridden=True,
        override_reason=ov.reason,
    )


@dataclass
class Use:
    record: Record
    scenario: bool  # True when used outside the base case (grid, upper bound, below min status)


@dataclass
class LedgerView:
    """Filtered ledger for one run. Tracks every record the kernel touches (provenance)."""

    by_id: dict[str, list[Record]]
    as_of: dt.date
    min_legal_status: MinStatus
    version: str
    digest: str
    used: dict[tuple[str, dt.date, str], Use] = field(default_factory=dict)

    def _mark(self, recs: Iterable[Record], scenario: bool) -> None:
        for r in recs:
            key = (r.id, r.effective_from, r.legal_status)
            prev = self.used.get(key)
            self.used[key] = Use(r, scenario and (prev.scenario if prev else True))

    def has(self, rid: str) -> bool:
        return bool(self.by_id.get(rid))

    def entries(self, rid: str, *, trusted: bool = True) -> list[Record]:
        """Entries for an id; trusted=True applies min_legal_status."""
        recs = self.by_id.get(rid, [])
        if trusted:
            recs = [r for r in recs if r.overridden or r.passes(self.min_legal_status)]
        return sorted(recs, key=lambda r: (r.effective_from, STATUS_RANK.get(r.legal_status, 9)))

    def get(self, rid: str, *, trusted: bool = True, scenario: bool = False) -> Record:
        """Latest (by effective_from, as of the view date) entry for an id."""
        every = self.entries(rid, trusted=trusted)
        recs = [r for r in every if r.effective_from <= self.as_of] or every
        if not recs:
            status = self.by_id.get(rid)
            why = (
                f"below min_legal_status={self.min_legal_status}"
                if status
                else "not in ledger (unverified or out of scope)"
            )
            raise LedgerError(f"record {rid} unavailable: {why}; supply it via overrides[] with a reason")
        rec = recs[-1]
        self._mark([rec], scenario)
        return rec

    def series(self, rid: str, *, trusted: bool = True, scenario: bool = False) -> dict[int, float]:
        """Merge year series across entries; higher legal status wins on overlapping years."""
        recs = self.entries(rid, trusted=trusted)
        if not recs:
            self.get(rid, trusted=trusted)  # raises with a clear message
        out: dict[int, float] = {}
        rank: dict[int, int] = {}
        for r in recs:
            rr = 9 if r.overridden else STATUS_RANK.get(r.legal_status, 9)
            for y, v in r.series().items():
                if y not in out or rr >= rank[y]:
                    out[y], rank[y] = v, rr
        self._mark(recs, scenario)
        return out

    def untrusted_only(self, rid: str) -> bool:
        return self.has(rid) and not self.entries(rid, trusted=True)


def _load_file(path: Path, rel: str, validate: bool) -> tuple[list[Record], list[str]]:
    raw = yaml.safe_load(path.read_text())
    errs = _bool_province_errors(raw, rel)
    doc = _jsonable(raw)
    if validate:
        v = jsonschema.Draft202012Validator(schema())
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
            loc = "/".join(str(p) for p in e.absolute_path)
            errs.append(f"{rel}:{loc}: {e.message[:200]}")
    recs: list[Record] = []
    if isinstance(doc, dict) and isinstance(doc.get("records"), list):
        for i, item in enumerate(doc["records"]):
            try:
                recs.append(Record.model_validate({**item, "file": rel}))
            except Exception as ex:  # pydantic ValidationError; keep going to report all errors
                errs.append(f"{rel}:records/{i}: {str(ex).splitlines()[0]}")
    return recs, errs


def _digest(records: Iterable[Record]) -> str:
    payload = sorted(
        (json.dumps(_jsonable(r.model_dump(mode="json")), sort_keys=True) for r in records),
    )
    return hashlib.sha256("\n".join(payload).encode()).hexdigest()


def load_ledger(root: Path | None = None, *, version: str | None = None, strict: bool = True) -> Ledger:
    """Load every ledger/records/**/*.yaml. strict=True raises on any schema or model error."""
    root = root or default_ledger_dir()
    files = sorted((root / "records").rglob("*.yaml"))
    recs: list[Record] = []
    errs: list[str] = []
    for f in files:
        r, e = _load_file(f, str(f.relative_to(root)), validate=True)
        recs += r
        errs += e
    if strict and errs:
        raise LedgerError("ledger invalid:\n  " + "\n  ".join(errs))
    return Ledger(tuple(recs), version or _version_of(root), _digest(recs), tuple(errs))


def _version_of(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "describe", "--tags", "--match", "ledger-v*", "--dirty"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip() or "working"
    except (OSError, subprocess.CalledProcessError):
        return "working"


def load_ledger_at(ref: str, repo: Path | None = None) -> Ledger:
    """Load the ledger as committed at a git ref (tag/commit), without touching the working tree."""
    repo = repo or default_ledger_dir().parent
    if Path(ref).is_dir():
        return load_ledger(Path(ref), version=ref)

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout

    names = [n for n in git("ls-tree", "-r", "--name-only", ref, "ledger/records").splitlines() if n]
    recs: list[Record] = []
    errs: list[str] = []
    for n in sorted(names):
        if not n.endswith(".yaml"):
            continue
        raw = yaml.safe_load(git("show", f"{ref}:{n}"))
        doc = _jsonable(raw)
        for i, item in enumerate(doc.get("records", [])):
            try:
                recs.append(Record.model_validate({**item, "file": n}))
            except Exception as ex:
                errs.append(f"{n}:records/{i}: {str(ex).splitlines()[0]}")
    if errs:
        raise LedgerError(f"ledger at {ref} invalid:\n  " + "\n  ".join(errs))
    return Ledger(tuple(recs), ref, _digest(recs))


# ---------------------------------------------------------------- validators (plan §5.4)


def validate(ledger: Ledger, today: dt.date) -> list[str]:
    """All integrity checks beyond the JSON schema. Returns human-readable errors (empty = valid)."""
    errs = list(ledger.errors)
    groups: dict[tuple[str, str], list[Record]] = {}
    for r in ledger.records:
        where = f"{r.file}:{r.id}"
        if r.unit not in UNITS:
            errs.append(f"{where}: unit {r.unit!r} not in whitelist")
        prefix = r.id.split(".")[0]
        expected = {"fed": "FED", "ab": "AB", "on": "ON", "bc": "BC", "qc": "QC"}.get(prefix)
        if expected and r.jurisdiction != expected:
            errs.append(f"{where}: jurisdiction {r.jurisdiction} does not match id prefix {prefix}")
        if r.effective_to and r.effective_to < r.effective_from:
            errs.append(f"{where}: effective_to before effective_from")
        for s in r.sources:
            if s.published and s.published > s.retrieved:
                errs.append(f"{where}: source published after retrieved ({s.url})")
            if s.retrieved > today:
                errs.append(f"{where}: retrieved date {s.retrieved} is in the future")
            if len(s.excerpt.split()) > 25:
                errs.append(f"{where}: excerpt longer than 25 words ({s.url})")
        if r.recorded_at > today:
            errs.append(f"{where}: recorded_at in the future")
        if r.legal_status in ("enacted", "in_force") and not r.has_primary:
            errs.append(f"{where}: {r.legal_status} record needs a primary source")
        if r.is_stale(today):
            sla = FRESHNESS_SLA_DAYS[r.freshness]
            errs.append(f"{where}: stale — retrieved {r.retrieved}, SLA {sla} days ({r.freshness})")
        if isinstance(r.value, dict) and r.unit != "text":
            for k, v in r.value.items():
                if isinstance(v, bool):
                    errs.append(f"{where}: value[{k}] is boolean; use a number or text")
        groups.setdefault((r.id, r.legal_status), []).append(r)
    for (rid, status), recs in groups.items():
        if status == "observation":  # point observations may accumulate
            continue
        recs = sorted(recs, key=lambda r: r.effective_from)
        for a, b in itertools.pairwise(recs):
            if a.effective_to is None or a.effective_to >= b.effective_from:
                errs.append(f"{rid}: overlapping effective periods for status {status}")
    return errs


def freshness_report(records: Iterable[Record], as_of: dt.date) -> Mapping[str, int]:
    """Days remaining before each record breaches its SLA (negative = stale)."""
    return {r.id: FRESHNESS_SLA_DAYS[r.freshness] - (as_of - r.retrieved).days for r in records}
