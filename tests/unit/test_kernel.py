"""Plan §5.1: formulas against hand-computed fixtures."""

from __future__ import annotations

import numpy as np
import pytest

from pv import carbon
from pv.cashflow import irr, npv, payback
from pv.ledger import LedgerError
from tests.unit.helpers import case, model, ov


def test_three_year_toy_project_by_hand() -> None:
    # $1M capex, no ITC (itc_measure none), no carbon (not covered), $500k/yr pre-tax saving via opex.
    m, _ = model(
        case(
            facility={"province": "AB", "system": "none", "covered": False},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1_000_000}],
                "technology_class": "x",
                "itc_measure": "none",
                "cca_class": "8",
                "opex_delta": -500_000,
            },
        )
    )
    cf = m.cashflows(np.zeros(3), granted=False)
    # CCA class 8 at 20% with half-year rule: 100k, 180k, 144k; tax 25%
    want = [-1_000_000, 375_000 + 25_000, 375_000 + 45_000, 375_000 + 36_000]
    assert cf.tolist() == pytest.approx(want)
    assert npv(cf, 0.10) == pytest.approx(sum(c / 1.1**i for i, c in enumerate(want)))
    r, why = irr(cf)
    assert why is None and npv(cf, r) == pytest.approx(0, abs=1e-6)  # type: ignore[arg-type]
    assert payback(cf) == pytest.approx(2 + (1_000_000 - 820_000) / 411_000)


def test_itc_on_1m_asset_one_year_lag_and_ucc() -> None:
    m, _ = model(
        case(
            facility={"province": "AB", "system": "none", "covered": False},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1_000_000}],
                "technology_class": "heat_pump_air_source",
                "itc_eligible_share": 1.0,
            },
            finance={"discount_rate": 0.1, "tax_rate": 0.25, "itc_receipt_lag_years": 1},
        )
    )
    assert m.ti.eligibility == "likely" and m.ti.granted and m.ti.itc_rate == 0.30
    cf = m.cashflows(np.zeros(3), granted=True)
    # ITC 300k at t=1; UCC 700k fully expensed (2026 in window) → shield 175k at t=1
    assert cf[1] == pytest.approx(300_000 + 175_000)
    assert cf[2] == pytest.approx(0) and cf[3] == pytest.approx(0)


def test_labour_rule_and_assistance_reduce_itc() -> None:
    m, c = model(
        case(
            facility={"province": "AB", "system": "none", "covered": False, "labour_requirements_met": False},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1_000_000}],
                "technology_class": "heat_pump_air_source",
                "other_assistance": 200_000,
            },
        )
    )
    assert m.ti.itc_rate == pytest.approx(0.20)
    assert m.itc(True) == pytest.approx(0.20 * 800_000)


def test_ineligible_entity_gets_no_itc_or_tax_shield() -> None:
    m, _ = model(
        case(
            facility={"province": "AB", "system": "none", "covered": False, "entity": "municipal"},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1e6}],
                "technology_class": "heat_pump_air_source",
            },
        )
    )
    assert m.ti.itc_rate == 0 and m.tau == 0
    assert any("not eligible" in n for n in m.ti.notes)


def test_not_listed_class_defaults_to_denied() -> None:
    m, _ = model(
        case(
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1e6}],
                "technology_class": "heat_pump_process",
                "covered_emissions_delta_t": -1000,
            }
        )
    )
    assert m.ti.eligibility == "not_listed" and not m.ti.granted


def test_floor_activation_year_boundary() -> None:
    raw = case(
        min_legal_status="announced",
        project={
            "in_service": "2027-12-31",
            "life_years": 4,
            "capex": [{"year": 0, "amount": 1e6}],
            "technology_class": "x",
            "itc_measure": "none",
            "covered_emissions_delta_t": -1000,
        },
        overrides=[ov("ab.tier.credit_obs", {"base": 20, "year": 2026})],
    )
    m, c = model(raw)
    path = m.path("base")
    assert m.years.tolist() == [2028, 2029, 2030, 2031]
    assert path.tolist() == pytest.approx([20, 20, 60, 63])  # ledger floor from 2030 (announced, trusted)
    # below min status the floor is only a scenario
    raw["min_legal_status"] = "enacted"
    m2, _ = model(raw)
    assert m2.path("base").tolist() == pytest.approx([20, 20, 20, 20])
    assert m2.path("base", floor_mode="as_announced").tolist() == pytest.approx([20, 20, 60, 63])
    assert any("ab.tier.floor" in w for w in m2.warnings)


def test_qc_path_for_non_covered_site() -> None:
    m, _ = model(
        case(
            facility={"province": "QC", "system": "none", "covered": False},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1e6}],
                "technology_class": "x",
                "covered_emissions_delta_t": -1000,
            },
        )
    )
    assert m.ci.kind == "qc"
    base = m.path("base")
    # latest auction settlement (Aug 2026) escalated at 5% real + 0% inflation from 2026
    assert base[0] == pytest.approx(45.11 * 1.05) and base[2] == pytest.approx(45.11 * 1.05**3)
    assert np.array_equal(m.path("upper_bound_headline"), base)


def test_non_covered_outside_qc_is_zero_even_under_headline() -> None:
    m, _ = model(case(facility={"province": "ON", "system": "eps", "covered": False}))
    for s in ("low", "base", "high", "upper_bound_headline"):
        assert not m.path(s).any()  # type: ignore[arg-type]


def test_ratio_method_on_and_fund_cap() -> None:
    m, _ = model(case(facility={"province": "ON", "system": "eps", "covered": True}))
    base = m.path("base")
    # 72 / 95 (2025 compliance price) × compliance price path, capped at the fund price
    assert base[0] == pytest.approx(72 / 95 * 125)
    assert (m.path("high") <= m.ci.fund + 1e-9).all()
    assert (m.path("low") <= base + 1e-9).all()


def test_ccfd_volume_and_term() -> None:
    ci = carbon.CarbonInputs(
        np.array([2039, 2040, 2041]),
        "covered",
        {"base": np.full(3, 20.0)},
        np.full(3, 100.0),
        np.zeros(3),
        True,
        np.full(3, 100.0),
    )
    from pv.case import Ccfd

    v = carbon.realized(ci, "base", ccfd=Ccfd(strike=85, term_end=2040, volume_share=0.5))
    assert v.tolist() == pytest.approx([52.5, 52.5, 20])


def test_value_stack_sums_to_full_npv() -> None:
    m, c = model(
        case(
            project={
                "in_service": "2026-12-31",
                "life_years": 10,
                "capex": [{"year": 0, "amount": 1e6}],
                "technology_class": "heat_pump_air_source",
                "covered_emissions_delta_t": -5000,
            },
            policy={
                "ccfd": {"strike": 85, "term_end": 2035},
                "grid_factor": "marginal",
                "marginal_grid_ef_g_kwh": 400,
            },
        )
    )
    stack = m.value_stack("base", "auto", c.policy.ccfd)
    full = m.npv_of(m.path("base", "auto", c.policy.ccfd), m.ti.granted)
    assert sum(s["delta"] for s in stack) == pytest.approx(full)  # type: ignore[misc]
    assert stack[-1]["delta"] >= 0  # type: ignore[operator]


def test_missing_records_require_user_input() -> None:
    with pytest.raises(LedgerError, match="natural_gas_gj"):
        model(
            case(
                project={
                    "in_service": "2026-12-31",
                    "life_years": 3,
                    "capex": [{"year": 0, "amount": 1e6}],
                    "technology_class": "x",
                    "energy_deltas": {"natural_gas_gj": -100},
                }
            )
        )
    with pytest.raises(LedgerError, match="fed.nir.grid_ef"):  # bitemporal: recorded 2026-09-30
        model(
            case(
                as_of="2026-09-29",
                policy={"grid_factor": "average"},
                project={
                    "in_service": "2026-12-31",
                    "life_years": 3,
                    "capex": [{"year": 0, "amount": 1e6}],
                    "technology_class": "x",
                    "energy_deltas": {"electricity_mwh": 100},
                },
            )
        )
    with pytest.raises(LedgerError, match="phase-out"):
        model(
            case(
                project={
                    "in_service": "2031-06-30",
                    "life_years": 3,
                    "capex": [{"year": 0, "amount": 1e6}],
                    "technology_class": "heat_pump_air_source",
                }
            )
        )
    with pytest.raises(LedgerError, match="fed.ccus_itc.rates unavailable: below min_legal_status"):
        model(
            case(
                project={
                    "in_service": "2026-12-31",
                    "life_years": 3,
                    "capex": [{"year": 0, "amount": 1e6}],
                    "technology_class": "x",
                    "itc_measure": "ccus",
                }
            )
        )


def _itc_case(measure: str, in_service: str = "2026-12-31", **project: object) -> dict:
    return case(
        min_legal_status="proposed",
        project={
            "in_service": in_service,
            "life_years": 3,
            "capex": [{"year": 0, "amount": 1e6}],
            "technology_class": "x",
            "itc_measure": measure,
            **project,
        },
    )


def test_ce_itc_rate_window_and_warning() -> None:
    m, _ = model(_itc_case("ce"))
    assert m.ti.rho == 0.15  # ITA s.127.491 specified percentage
    assert any("qualifying-entity status and labour rule not checked" in w for w in m.warnings)
    late, _ = model(_itc_case("ce", "2035-06-30"))
    assert late.ti.rho == 0.0 and any("outside fed.ce_itc.rate" in w for w in late.warnings)


def test_table_valued_itc_rate_needs_an_explicit_key() -> None:
    with pytest.raises(LedgerError, match="set project.itc_rate_key to one of: capture_2036_2040"):
        model(_itc_case("ccus"))
    m, _ = model(_itc_case("ccus", itc_rate_key="capture_to_2035"))
    assert m.ti.rho == 0.5  # not the first key (dac_to_2035 = 0.6)
    with pytest.raises(LedgerError, match="itc_rate_key"):
        model(_itc_case("ccus", itc_rate_key="nope"))


def test_emissions_and_abatement_cost() -> None:
    m, _ = model(
        case(
            policy={"grid_factor": "marginal", "marginal_grid_ef_g_kwh": 500},
            project={
                "in_service": "2026-12-31",
                "life_years": 3,
                "capex": [{"year": 0, "amount": 1e6}],
                "technology_class": "x",
                "covered_emissions_delta_t": None,
                "energy_deltas": {"natural_gas_gj": -20_000, "electricity_mwh": 1000},
            },
            prices={"natural_gas_gj": 5, "electricity_mwh": 50, "escalation": 0.0},
        )
    )
    ef_ab = 0.0511
    assert m.em.onsite_t_yr == pytest.approx(20_000 * ef_ab)
    assert m.em.grid_t_yr == pytest.approx(500)
    d = m.em.as_dict(disc_sum=2.0, npv=-1000.0)
    assert d["abatement_cost_net_per_t"] == pytest.approx(round(1000 / ((20_000 * ef_ab - 500) * 2), 2))


def test_irr_edge_cases() -> None:
    assert irr(np.array([1.0, 1.0]))[0] is None
    r, why = irr(np.array([-100.0, 230.0, -132.0]))  # two roots: 10% and 20%
    assert r is None and why is not None and "multiple" in why
    assert payback(np.array([-10.0, 1.0])) is None
    assert payback(np.array([-10.0, 20.0]), 0.1) == pytest.approx(10 / (20 / 1.1))
