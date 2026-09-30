"""DoD §2.4-1: kernel reproduces validation/results.md (NPV ±$5k, breakeven ±$1/t)."""

from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from pv import carbon
from pv.case import Case
from pv.cashflow import build, irr
from pv.ledger import load_ledger
from tests.golden.oracle import EX3_SCENARIOS, ex1_case, ex3_case, oracle

NPV_TOL = 5_000.0
BE_TOL = 1.0
LEDGER = load_ledger()

# Published results.md figures ($M, 2 d.p.) — the kernel must also round to these.
EX1_PUBLISHED = {
    ("QC", True): {"none": 0.70, "market": 0.70, "headline": 0.70, "be": 31, "irr": 0.115},
    ("QC", False): {"none": -0.13, "market": -0.13, "headline": -0.13, "be": 76, "irr": 0.075},
    ("BC", True): {"none": -0.85, "market": 0.66, "headline": 1.37, "be": 47, "irr": 0.115},
    ("BC", False): {"none": -1.68, "market": -0.17, "headline": 0.54, "be": 92, "irr": 0.073},
}
EX3_PUBLISHED = {
    "be": 75,
    "Headline": 17.63,
    "Market $20, no floor": -20.86,
    "Market + 2030 floor": -2.79,
    "CCfD $85 to 2040": 6.00,
}
EX3_LEVELIZED = {
    "Headline": 122,
    "Market $20, no floor": 20,
    "Market + 2030 floor": 68,
    "CCfD $85 to 2040": 91,
}


def _model(raw: dict) -> tuple[object, Case]:
    case = Case.model_validate(raw)
    view = LEDGER.view(dt.date(2026, 9, 29), case.min_legal_status, case.overrides)
    return build(case, view), case


def _run(raw: dict) -> tuple[float, float | None, np.ndarray]:
    m, case = _model(raw)
    path = m.path(case.policy.credit_price_scenario, case.policy.floor, case.policy.ccfd)  # type: ignore[attr-defined]
    cf = m.cashflows(path, granted=m.ti.granted)  # type: ignore[attr-defined]
    return float(np.sum(cf * 1.08 ** -np.arange(len(cf)))), m.breakeven(m.ti.granted), cf  # type: ignore[attr-defined]


@pytest.mark.parametrize("prov", ["QC", "BC"])
@pytest.mark.parametrize("itc", [True, False])
@pytest.mark.parametrize("regime", ["none", "market", "headline"])
def test_example1(prov: str, itc: bool, regime: str) -> None:
    o = oracle()
    cx = o.Context(prov=prov, carbon_regime=regime, itc_on=itc, expensing=itc)
    want = o.npv(o.cashflows(o.HP_IND, cx), cx.discount)
    got, be, cf = _run(ex1_case(prov, itc, regime))
    assert abs(got - want) <= NPV_TOL, (got, want)
    assert round(got / 1e6, 2) == pytest.approx(EX1_PUBLISHED[(prov, itc)][regime], abs=0.011)
    if regime == "market":
        want_be = o.breakeven_flat_carbon(o.HP_IND, cx)
        assert be is not None and abs(be - want_be) <= BE_TOL
        assert round(be) == pytest.approx(EX1_PUBLISHED[(prov, itc)]["be"], abs=1)
        r, _ = irr(cf)
        assert r is not None and r == pytest.approx(EX1_PUBLISHED[(prov, itc)]["irr"], abs=0.0006)


@pytest.mark.parametrize("scenario", list(EX3_SCENARIOS))
def test_example3_25m(scenario: str) -> None:
    got, be, _ = _run(ex3_case(25e6, scenario))
    assert abs(got / 1e6 - EX3_PUBLISHED[scenario]) <= 0.005 + NPV_TOL / 1e6
    assert be is not None and abs(be - EX3_PUBLISHED["be"]) <= BE_TOL


def test_example3_matches_oracle_exactly_and_levelized_band() -> None:
    o = oracle()
    _, res = o.example3()
    want_be, want = res[25e6]
    for scenario in EX3_SCENARIOS:
        got, be, _ = _run(ex3_case(25e6, scenario))
        assert abs(got - want[scenario]) <= NPV_TOL
        assert be is not None and abs(be - want_be) <= BE_TOL
        m, case = _model(ex3_case(25e6, scenario))
        path = m.path(case.policy.credit_price_scenario, case.policy.floor, case.policy.ccfd)  # type: ignore[attr-defined]
        assert round(carbon.levelized(path, 0.08)) == EX3_LEVELIZED[scenario]
