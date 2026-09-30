from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from pv.ledger import LedgerError, Override, load_ledger, validate
from tests.conftest import rec, src, write_ledger

D = dt.date


def test_load_and_view_filters_status(tmp_path: Path) -> None:
    root = write_ledger(
        tmp_path,
        [
            rec("ab.tier.fund_price", {2026: 95}, effective_to="2026-12-31"),
            rec(
                "ab.tier.fund_price",
                {2027: 100, 2030: 115},
                legal_status="announced",
                effective_from="2027-01-01",
                freshness="announcement",
                sources=[src("secondary")],
            ),
        ],
    )
    led = load_ledger(root, version="t")
    v = led.view(D(2026, 10, 1), "enacted")
    assert v.series("ab.tier.fund_price") == {2026: 95.0}
    v2 = led.view(D(2026, 10, 1), "announced")
    assert v2.series("ab.tier.fund_price") == {2026: 95.0, 2027: 100.0, 2030: 115.0}
    assert v.untrusted_only("ab.tier.fund_price") is False


def test_as_of_hides_future_recordings(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("fed.x.y", 1, recorded_at="2026-09-29")])
    led = load_ledger(root)
    with pytest.raises(LedgerError, match="not in ledger"):
        led.view(D(2026, 1, 1)).get("fed.x.y")


def test_override_requires_reason_and_replaces(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("fed.x.y", 1)])
    led = load_ledger(root)
    with pytest.raises(ValueError):
        Override(record="fed.x.y", value=2, reason="")
    v = led.view(D(2026, 10, 1), overrides=[Override(record="fed.x.y", value=2, reason="broker quote")])
    r = v.get("fed.x.y")
    assert r.num() == 2 and r.overridden and r.override_reason == "broker quote"
    # overrides can supply records missing from the ledger
    v = led.view(D(2026, 10, 1), overrides=[Override(record="qc.a.b", value=0.05, reason="user input")])
    assert v.get("qc.a.b").num() == 0.05
    assert {u.record.id for u in v.used.values()} == {"qc.a.b"}


def test_min_status_blocks_and_scenario_access(tmp_path: Path) -> None:
    root = write_ledger(
        tmp_path,
        [
            rec(
                "ab.tier.floor",
                {2030: 60},
                legal_status="announced",
                sources=[src("secondary")],
                freshness="announcement",
            )
        ],
    )
    v = load_ledger(root).view(D(2026, 10, 1), "enacted")
    assert v.untrusted_only("ab.tier.floor")
    with pytest.raises(LedgerError, match="below min_legal_status"):
        v.get("ab.tier.floor")
    assert v.series("ab.tier.floor", trusted=False, scenario=True) == {2030: 60.0}
    (use,) = v.used.values()
    assert use.scenario


def test_validators(tmp_path: Path, today: dt.date) -> None:
    root = write_ledger(
        tmp_path,
        [
            rec("fed.a.b", 1, sources=[src("secondary")]),  # in_force without primary
            rec("fed.c.d", 1, unit="furlongs"),  # unit
            rec(
                "fed.e.f",
                1,
                freshness="market_observation",
                legal_status="observation",
                sources=[src(retrieved="2026-01-01")],
            ),  # stale
            rec("ab.g.h", 1, jurisdiction="BC"),  # prefix mismatch
            rec("fed.i.j", 1, effective_from="2026-01-01"),
            rec("fed.i.j", 2, effective_from="2026-06-01"),  # overlap (first has no end)
            rec("fed.k.l", 1, effective_to="2025-01-01"),  # bad dates
        ],
    )
    errs = validate(load_ledger(root), today)
    joined = "\n".join(errs)
    for needle in (
        "needs a primary",
        "not in whitelist",
        "stale",
        "does not match",
        "overlapping",
        "effective_to before",
    ):
        assert needle in joined, needle


def test_bare_on_is_rejected(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("ref.grid", {"QC": 2.5}, unit="g/kWh")])
    p = root / "records" / "a.yaml"
    text = p.read_text()
    assert "QC: 2.5" in text
    p.write_text(text.replace("QC: 2.5", "{QC: 2.5, ON: 73.8}").replace("value:\n    {", "value: {"))
    with pytest.raises(LedgerError, match="quote"):
        load_ledger(root)


def test_schema_errors_reported(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("fed.a.b", 1, legal_status="rumoured")])
    led = load_ledger(root, strict=False)
    assert any("rumoured" in e for e in led.errors)
    with pytest.raises(LedgerError):
        load_ledger(root)


def test_digest_stable(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("fed.a.b", 1), rec("fed.c.d", 2)])
    assert load_ledger(root).digest == load_ledger(root).digest
