"""One-way sensitivity, CCfD strike solver and the shared vectorized evaluator."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pv import robustness
from pv.case import Case, CcfdStrike, MonteCarlo, Sensitivity
from pv.cashflow import npv
from tests.golden.oracle import ex3_case
from tests.unit.helpers import case, model, ov
from tests.unit.test_robustness import MC_AB

SENS = Sensitivity(
    capex=0.2, gas_price=0.3, electricity_price=0.3, opex=0.2, credit_price=0.25, discount_rate=0.02
)


def _hp(**kw: object) -> dict:
    """Heat pump at a covered ON facility: every sensitivity variable is live."""
    return case(
        facility={"province": "ON", "system": "eps", "covered": True},
        project={
            "life_years": 10,
            "energy_deltas": {"natural_gas_gj": -40_000, "electricity_mwh": 3_000},
            "opex_delta": 20_000,
            "covered_emissions_delta_t": None,
        },
        prices={"natural_gas_gj": 9.0, "electricity_mwh": 70.0, "escalation": 0.02},
        **kw,
    )


def test_base_draw_equals_deterministic_npv() -> None:
    m, _ = model(_hp())
    assert robustness.npv_draws(m, robustness.Draws.base(m))[0] == pytest.approx(
        robustness.deterministic_npv(m), abs=1e-6
    )


def test_sensitivity_rows_match_independent_reruns() -> None:
    raw = _hp()
    m, _ = model(raw)
    res = robustness.sensitivity(m, SENS)
    rows = {r["variable"]: r for r in res["rows"]}
    assert set(rows) == set(robustness.SENSITIVITY_VARIABLES)
    swings = [r["swing"] for r in res["rows"]]
    assert swings == sorted(swings, reverse=True)

    def rerun(**kw: object) -> float:
        mm, _ = model({**raw, **kw})
        return robustness.deterministic_npv(mm)

    capex_hi = {**raw["project"], "capex": [{"year": 0, "amount": 1_200_000}]}
    assert rows["capex"]["npv_high"] == pytest.approx(rerun(project=capex_hi), abs=1e-6)
    gas_lo = {**raw["prices"], "natural_gas_gj": 9.0 * 0.7}
    assert rows["gas_price"]["npv_low"] == pytest.approx(rerun(prices=gas_lo), abs=1e-6)
    elec_hi = {**raw["prices"], "electricity_mwh": 70.0 * 1.3}
    assert rows["electricity_price"]["npv_high"] == pytest.approx(rerun(prices=elec_hi), abs=1e-6)
    opex_lo = {**raw["project"], "opex_delta": 20_000 * 0.8}
    assert rows["opex"]["npv_low"] == pytest.approx(rerun(project=opex_lo), abs=1e-6)
    cf = m.cashflows(m.path("base"), granted=m.ti.granted)
    assert rows["discount_rate"]["npv_low"] == pytest.approx(npv(cf, 0.08), abs=1e-6)
    assert rows["discount_rate"]["npv_high"] == pytest.approx(npv(cf, 0.12), abs=1e-6)
    # credit price scales the market before the compliance-price cap: same as scaling the observation
    obs = m._view.get("on.eps.epu_obs").table()  # type: ignore[union-attr]
    scaled = {k: (v * 0.75 if k == "price" else v) for k, v in obs.items()}
    assert rows["credit_price"]["npv_low"] == pytest.approx(
        rerun(overrides=[ov("on.eps.epu_obs", scaled)]), abs=1e-6
    )
    assert rows["capex"]["npv_low"] > res["base_npv"] > rows["capex"]["npv_high"]


def test_sensitivity_flags_decision_changes() -> None:
    m, _ = model(_hp())
    rows = robustness.sensitivity(m, Sensitivity(capex=0.9))["rows"]
    base = robustness.deterministic_npv(m)
    assert rows[0]["decision_changes"] == any(
        (v > 0) != (base > 0) for v in (rows[0]["npv_low"], rows[0]["npv_high"])
    )


def _ex3_strike(**spec: object) -> tuple:
    raw = ex3_case(25e6, "CCfD $85 to 2040")
    raw["robustness"] = {"monte_carlo": MC_AB, "ccfd_strike": spec}
    return model(raw)


def test_strike_solver_brackets_npv_zero() -> None:
    m, c = _ex3_strike()
    out = robustness.ccfd_strike(m, c.robustness.ccfd_strike)
    s = out["npv_zero_strike"]
    assert s is not None and 0 < s < 85  # oracle: the $85 CCfD gives NPV +$6.0M
    assert (out["term_end"], out["volume_share"]) == (2040, 1.0)

    def at(strike: float) -> float:
        ccfd = c.policy.ccfd.model_copy(update={"strike": strike})  # type: ignore[union-attr]
        return m.npv_of(m.path("base", "auto", ccfd), True)

    assert at(s) >= 0 > at(s - 0.02)


def test_strike_solver_hurdle_and_target_probability() -> None:
    m, c = _ex3_strike(hurdle_rate=0.10, target_p=0.9)
    out = robustness.ccfd_strike(m, c.robustness.ccfd_strike)
    base, _ = _ex3_strike()
    assert (
        out["npv_zero_strike"]
        > robustness.ccfd_strike(base, base.case.robustness.ccfd_strike)["npv_zero_strike"]
    )
    s = out["target_p_strike"]
    mc = c.robustness.monte_carlo

    def p(strike: float) -> float:
        ccfd = c.policy.ccfd.model_copy(update={"strike": strike})  # type: ignore[union-attr]
        return float((robustness.mc_npvs(m, mc, ccfd)[0] > 0).mean())

    assert p(s) >= 0.9 > p(s - 0.02)


def test_strike_solver_edge_cases() -> None:
    cheap, c = _ex3_strike()
    cheap_case = cheap.case.model_copy(
        update={"project": cheap.case.project.model_copy(update={"opex_delta": 0.0})}
    )
    m0, _ = model(cheap_case.model_dump(mode="json"))
    assert robustness.ccfd_strike(m0, c.robustness.ccfd_strike)["npv_zero_strike"] == 0.0
    out = robustness.ccfd_strike(cheap, CcfdStrike(max_strike=10))
    assert out["npv_zero_strike"] is None and "stays negative" in out["note"]
    qc, _ = model(case(facility={"province": "QC", "system": "spede"}))
    assert "not applicable" in robustness.ccfd_strike(qc, CcfdStrike(term_end=2040))["note"]


def test_case_validation_for_strike() -> None:
    with pytest.raises(ValueError, match="term_end is required"):
        Case.model_validate(case(robustness={"ccfd_strike": {}}))
    with pytest.raises(ValueError, match="needs robustness.monte_carlo"):
        Case.model_validate(case(robustness={"ccfd_strike": {"term_end": 2040, "target_p": 0.5}}))


PROVS = st.sampled_from([("AB", "tier"), ("ON", "eps"), ("BC", "bc_obps"), ("QC", "spede")])


@settings(max_examples=40, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    PROVS, st.sampled_from(["low", "base", "high", "upper_bound_headline"]), st.booleans(), st.floats(0, 200)
)
def test_mc_collapses_to_deterministic_for_every_scenario_and_ccfd(
    pv_, scenario: str, with_ccfd: bool, strike: float
) -> None:
    """Regression: MC used to cap the headline scenario at the fund price and apply a CCfD in QC."""
    policy: dict = {"credit_price_scenario": scenario, "grid_factor": "marginal", "marginal_grid_ef_g_kwh": 0}
    if with_ccfd:
        policy["ccfd"] = {"strike": strike, "term_end": 2028}
    m, _ = model(
        case(
            facility={"province": pv_[0], "system": pv_[1], "covered": True},
            min_legal_status="announced",
            policy=policy,
        )
    )
    r = robustness.monte_carlo(m, MonteCarlo(draws=20, seed=1, itc_probability=1.0 if m.ti.granted else 0.0))
    assert r.mean == pytest.approx(robustness.deterministic_npv(m), rel=1e-9, abs=1e-3)


def test_sensitivity_is_deterministic_and_vectorized_shapes() -> None:
    m, _ = model(_hp())
    a = robustness.sensitivity(m, SENS)
    b = robustness.sensitivity(m, SENS)
    assert a == b
    d = robustness.Draws.base(m, 3)
    assert robustness.npv_draws(m, d).shape == (3,)
    assert np.allclose(robustness.npv_draws(m, d), robustness.npv_draws(m, d)[0])
