"""Plan §5.2 property tests."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from pv import robustness
from pv.case import MonteCarlo
from tests.unit.helpers import case, model, ov

PROVS = st.sampled_from([("AB", "tier"), ("ON", "eps"), ("BC", "bc_obps"), ("QC", "spede")])
SCEN = st.sampled_from(["low", "base", "high", "upper_bound_headline"])
SETTINGS = settings(max_examples=40, deadline=None, suppress_health_check=[HealthCheck.too_slow])


def _raw(prov: str, system: str, covered: bool, capex: float, tonnes: float, **kw: object) -> dict:
    return case(
        facility={"province": prov, "system": system, "covered": covered},
        project={
            "in_service": "2026-12-31",
            "life_years": 15,
            "capex": [{"year": 0, "amount": capex}],
            "technology_class": "heat_pump_air_source",
            "covered_emissions_delta_t": -tonnes,
            "opex_delta": 50_000,
        },
        **kw,
    )


@SETTINGS
@given(PROVS, st.floats(1e5, 5e7), st.floats(0, 1e5), st.floats(0, 300), st.floats(0, 300))
def test_npv_monotone_in_flat_carbon_price(pv_, capex: float, tonnes: float, p1: float, p2: float) -> None:
    m, _ = model(_raw(*pv_, True, capex, tonnes))
    lo, hi = sorted((p1, p2))
    assert m.npv_of(np.full(m.n, lo), True) <= m.npv_of(np.full(m.n, hi), True) + 1e-6


@SETTINGS
@given(st.floats(0, 0.6), st.floats(0, 0.6), st.floats(1e5, 5e7))
def test_npv_monotone_in_itc_rate(r1: float, r2: float, capex: float) -> None:
    lo, hi = sorted((r1, r2))
    vals = []
    for r in (lo, hi):
        m, _ = model(
            _raw("AB", "tier", True, capex, 1000, overrides=[ov("fed.ct_itc.rate_schedule", {2026: r})])
        )
        vals.append(m.npv_of(m.path("base"), True))
    assert vals[0] <= vals[1] + 1e-6


@SETTINGS
@given(
    st.sampled_from([("AB", "tier"), ("ON", "eps"), ("BC", "bc_obps"), ("AB", "none")]),
    SCEN,
    st.floats(0, 1e5),
    st.sampled_from(["auto", "as_announced", "half", "none"]),
)
def test_non_covered_outside_qc_has_zero_carbon_value(pv_, scenario: str, tonnes: float, floor: str) -> None:
    m, _ = model(
        _raw(
            *pv_,
            False,
            1e6,
            tonnes,
            policy={
                "ccfd": {"strike": 85, "term_end": 2040},
                "grid_factor": "marginal",
                "marginal_grid_ef_g_kwh": 0,
            },
        )
    )
    assert not m.path(scenario, floor, m.case.policy.ccfd).any()  # type: ignore[arg-type]


@SETTINGS
@given(PROVS, st.floats(1e5, 5e7), st.floats(1, 1e5), st.booleans())
def test_breakeven_round_trip(pv_, capex: float, tonnes: float, granted: bool) -> None:
    m, _ = model(_raw(*pv_, True, capex, tonnes))
    p = m.breakeven(granted)
    assert p is not None
    scale = capex + abs(p) * tonnes * m.n  # magnitude of the terms that cancel
    assert m.npv_of(np.full(m.n, p), granted) == pytest.approx(0, abs=1e-9 * scale + 1e-6)


@SETTINGS
@given(PROVS, SCEN, st.floats(0, 200), st.integers(2027, 2050), st.floats(0, 1), st.floats(0, 1e5))
def test_ccfd_value_non_negative(
    pv_, scenario: str, strike: float, end: int, vs: float, tonnes: float
) -> None:
    m, _ = model(
        _raw(
            *pv_,
            True,
            1e6,
            tonnes,
            min_legal_status="announced",
            policy={
                "ccfd": {"strike": strike, "term_end": end, "volume_share": vs},
                "grid_factor": "marginal",
                "marginal_grid_ef_g_kwh": 0,
            },
        )
    )
    stack = m.value_stack(scenario, "auto", m.case.policy.ccfd)  # type: ignore[arg-type]
    assert stack[-1]["delta"] >= -1e-6  # type: ignore[operator]


@SETTINGS
@given(PROVS, st.floats(1e5, 5e7), st.floats(0, 1e5), st.booleans(), st.integers(0, 2**31))
def test_mc_collapses_to_deterministic(pv_, capex: float, tonnes: float, granted: bool, seed: int) -> None:
    raw = _raw(
        *pv_,
        True,
        capex,
        tonnes,
        policy={"itc_granted": granted, "grid_factor": "marginal", "marginal_grid_ef_g_kwh": 0},
    )
    m, _ = model(raw)
    mc = MonteCarlo(draws=50, seed=seed, itc_probability=1.0 if granted else 0.0)
    r = robustness.monte_carlo(m, mc)
    det = robustness.deterministic_npv(m)
    assert r.mean == pytest.approx(det, rel=1e-9, abs=1e-3)
    assert r.p10 == pytest.approx(det, rel=1e-9, abs=1e-3)
