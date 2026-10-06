"""The shipped ledger passes every integrity check at release (DoD §2.4-2)."""

from __future__ import annotations

import datetime as dt

from pv.ledger import load_ledger, validate

RELEASE = dt.date(2026, 9, 30)  # ledger-v2026.10.1


def test_seed_ledger_valid_at_release() -> None:
    led = load_ledger()
    assert validate(led, RELEASE) == []
    assert len(led.records) >= 30


def test_enacted_records_have_primary_sources() -> None:
    for r in load_ledger().records:
        if r.legal_status in ("enacted", "in_force"):
            assert r.has_primary, r.id


def test_on_key_is_quoted_everywhere() -> None:
    for r in load_ledger().records:
        assert r.jurisdiction in ("FED", "AB", "ON", "BC", "QC")
        if isinstance(r.value, dict):
            assert "True" not in r.value
