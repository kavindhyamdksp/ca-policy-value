from __future__ import annotations

import time

import numpy as np
import pytest

from pv import robustness
from pv.case import MonteCarlo
from tests.golden.oracle import ex3_case
from tests.unit.helpers import LEDGER, case, model

MC_AB = {
    "draws": 20_000,
    "seed": 20260929,
    "regimes": {
        "floor_as_announced": {"p": 0.55, "floor_scale": 1.0},
        "floor_half": {"p": 0.30, "floor_scale": 0.5},
        "rollback": {"p": 0.15, "market_value": 15, "floor_scale": 0.0},
    },
    "shocks": {"credit_sigma": 0.35, "capex_triangular": [0.9, 1.0, 1.3]},
}


def _ex3(**policy: object) -> dict:
    raw = ex3_case(25e6, "Market + 2030 floor")
    raw["policy"] = {**raw["policy"], **policy}
    return raw


def test_band_and_breakeven_position() -> None:
    m, _ = model(_ex3())
    b = robustness.band(m)
    assert round(b["base"]) == 68 and round(b["upper_bound_headline"]) == 122
    assert b["low"] <= b["base"] <= b["high"]
    be = m.breakeven(True)
    assert "only the headline" not in robustness.breakeven_position(be, b)
    assert robustness.breakeven_position(10, b).startswith("below")
    assert robustness.breakeven_position(1e4, b).startswith("above the headline")
    assert robustness.breakeven_position(None, b) == "no carbon exposure"


def test_grid_go_share_and_minimal_conditions() -> None:
    raw = _ex3(ccfd={"strike": 85, "term_end": 2040})
    raw["robustness"] = {"grid": ["floor_status", "itc_granted", "ccfd"]}
    m, _ = model(raw)
    g = robustness.grid(m)
    assert g["n_states"] == 3 * 2 * 2
    # At $25M only the CCfD clears the hurdle (oracle Example 3)
    assert all(s["go"] == s["state"]["ccfd"] for s in g["states"] if s["state"]["floor_status"] != "none")
    assert {"ccfd": True} in g["minimal_go_conditions"] or any(
        c.get("ccfd") is True for c in g["minimal_go_conditions"]
    )
    for cond in g["minimal_go_conditions"]:
        assert all(s["go"] for s in g["states"] if all(s["state"][k] == v for k, v in cond.items()))


def test_minimal_conditions_logic() -> None:
    dims = {"a": [True, False], "b": [True, False]}
    states = [{"state": {"a": a, "b": b}, "go": a or b} for a in (True, False) for b in (True, False)]
    assert robustness.minimal_conditions(dims, states) == [{"a": True}, {"b": True}]
    assert robustness.minimal_conditions(dims, [{**s, "go": False} for s in states]) == []
    all_go = [{**s, "go": True} for s in states]
    assert robustness.minimal_conditions(dims, all_go) == [{}]


def test_grid_skips_inapplicable_dimensions() -> None:
    m, _ = model(
        case(
            facility={"province": "QC", "system": "spede", "covered": True},
            robustness={"grid": ["floor_status", "coverage", "itc_granted"]},
        )
    )
    assert list(robustness.dimensions(m, m.case.robustness.grid)) == ["itc_granted"]


def test_mc_matches_oracle_ex3_distribution() -> None:
    """Oracle MC (results.md): Ex3 $25M merchant P(NPV>0)=0%, mean −10.65M; with $85 CCfD 76%, mean +2.46M."""
    m, _ = model(_ex3())
    r = robustness.monte_carlo(m, MonteCarlo.model_validate(MC_AB))
    assert r.p_positive < 0.01 and r.mean / 1e6 == pytest.approx(-10.65, abs=0.25)
    m2, _ = model(_ex3(ccfd={"strike": 85, "term_end": 2040}))
    r2 = robustness.monte_carlo(m2, MonteCarlo.model_validate(MC_AB))
    assert r2.p_positive == pytest.approx(0.76, abs=0.02)
    assert r2.mean / 1e6 == pytest.approx(2.46, abs=0.15)


def test_mc_is_seeded_and_fast() -> None:
    m, _ = model(_ex3())
    mc = MonteCarlo.model_validate({**MC_AB, "draws": 10_000})
    t0 = time.perf_counter()
    a = robustness.monte_carlo(m, mc)
    elapsed = time.perf_counter() - t0
    b = robustness.monte_carlo(m, mc)
    assert a == b and elapsed < 10  # DoD §2.4-7
    c = robustness.monte_carlo(m, mc.model_copy(update={"seed": 1}))
    assert c != a


def test_three_dim_grid_under_one_second() -> None:
    raw = _ex3(ccfd={"strike": 85, "term_end": 2040})
    raw["robustness"] = {"grid": ["floor_status", "itc_granted", "ccfd"]}
    t0 = time.perf_counter()
    m, _ = model(raw)
    robustness.grid(m)
    assert time.perf_counter() - t0 < 1.0


def test_regime_probabilities_must_sum_to_one() -> None:
    with pytest.raises(ValueError):
        MonteCarlo.model_validate({"regimes": {"a": {"p": 0.5}}})


def test_mc_non_covered_and_uses_ledger_eligibility() -> None:
    m, _ = model(case(facility={"province": "ON", "system": "eps", "covered": False}))
    r = robustness.monte_carlo(m, MonteCarlo(draws=500))
    assert r.itc_probability == 0.9  # heat_pump_air_source: likely
    assert np.isfinite(r.mean)
    assert LEDGER.version
