"""Kernel wiring (registry.yaml): consistency with the case model and the ledger."""

from __future__ import annotations

import typing
from pathlib import Path

import pytest

from pv import tax
from pv.case import Province, System
from pv.ledger import load_ledger
from pv.registry import Registry, registry
from tests.conftest import rec, write_ledger
from tests.unit.helpers import AS_OF, LEDGER, case, model, ov

# Wired into the kernel but deliberately absent from the ledger (plan §2.5 D1): users supply them.
USER_INPUT_RECORDS = {"fed.nir.grid_ef", "fed.ce_itc.rate", "ref.gas.delivered"}


def test_registry_matches_case_literals() -> None:
    reg = registry()
    assert reg.systems() == set(typing.get_args(System))
    assert set(reg.carbon.cap_and_trade) <= set(typing.get_args(Province))


def test_every_wired_record_is_in_ledger_or_documented_user_input() -> None:
    missing = registry().record_ids() - set(LEDGER.ids())
    assert missing == USER_INPUT_RECORDS


def test_expensing_classes_come_from_the_ledger() -> None:
    view = LEDGER.view(AS_OF)
    assert tax.expensing_classes(view) == {"43.1", "53", "54", "55", "56"}
    assert "43.2" not in tax.expensing_classes(view)
    assert any(k[0] == "fed.cca.expensing_classes" for k in view.used)


def test_expensing_classes_override_changes_cca() -> None:
    base, _ = model(case(project={"cca_class": "43.1"}))
    none, _ = model(case(overrides=[ov("fed.cca.expensing_classes", {"53": "eligible"})]))
    assert base.cca(True, 0.0)[1] == pytest.approx(1_000_000)  # 100% expensing in 2027
    assert none.cca(True, 0.0)[1] == pytest.approx(1_000_000 * 0.30 / 2)  # half-year DB at 30%


def test_fallback_for_ledgers_without_the_classes_record(tmp_path: Path) -> None:
    root = write_ledger(tmp_path, [rec("fed.cca.expensing", {2027: 1.0}, unit="fraction")])
    view = load_ledger(root).view(AS_OF)
    assert tax.expensing_classes(view) == frozenset(registry().tax.cca.expensing_classes_fallback)


def test_eligibility_probability_from_registry() -> None:
    assert tax.eligibility_probability("case_by_case") == 0.6
    assert tax.eligibility_probability("n/a") is None


def test_registry_rejects_incomplete_assumptions() -> None:
    raw = registry().model_dump()
    raw["assumptions"]["itc_eligibility_probability"] = {"likely": 0.9}
    with pytest.raises(ValueError, match="itc_eligibility_probability"):
        Registry.model_validate(raw)
