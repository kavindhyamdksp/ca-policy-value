"""Oracle cases: validation/params.yaml injected as overrides with conventions=validation_v1 (DoD §2.4-1)."""

from __future__ import annotations

import importlib.util
import sys
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PARAMS = yaml.safe_load((ROOT / "validation" / "params.yaml").read_text())


@cache
def oracle() -> ModuleType:
    """Import the frozen research model read-only (no bytecode written into validation/)."""
    path = ROOT / "validation" / "decision_sensitivity.py"
    spec = importlib.util.spec_from_file_location("decision_sensitivity", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    prev = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = prev
    return mod


def _ov(record: str, value: Any) -> dict[str, Any]:
    return {"record": record, "value": value, "reason": "validation/params.yaml (oracle acceptance test)"}


def common_overrides(prov: str) -> list[dict[str, Any]]:
    c = PARAMS["carbon"]
    head = {int(k): float(v) for k, v in c["headline_path"]["value"].items()}
    return [
        _ov("fed.carbon.benchmark_path", head),
        _ov("ref.tax.corporate", {prov: PARAMS["tax_rate"][prov]}),
        _ov("fed.nir.gas_ef", PARAMS["gas_ef_t_per_gj"]["value"]),
        _ov("fed.ct_itc.rate_schedule", {2026: PARAMS["itc"]["ct_rate"]["value"]}),
        _ov("fed.cca.expensing", {2026: 1.0}),
        _ov("qc.spede.auction_obs", {"settlement": c["qc_cap_and_trade_2026"]["value"], "year": 2026}),
        _ov("qc.spede.reserve_escalation", {"real_rate": c["qc_cat_escalation"]["value"]}),
        _ov("bc.obps.price", head),
        _ov("bc.obps.credit_obs", {"ratio": c["bc_obps_market_ratio"]["value"]}),
        _ov("ab.tier.fund_price", head),
        _ov("ab.tier.credit_obs", {"base": c["ab_tier_credit_market"]["value"], "year": 2026}),
        _ov("ab.tier.floor", {int(k): float(v) for k, v in c["ab_tier_floor"]["value"].items()}),
    ]


def ex1_case(prov: str, itc: bool, regime: str) -> dict[str, Any]:
    """Example 1 process heat pump. regime: none | market | headline."""
    hp = oracle().HP_IND
    return {
        "case_id": f"oracle-ex1-{prov}-{'itc' if itc else 'noitc'}-{regime}",
        "as_of": "2026-09-29",
        "min_legal_status": "announced",
        "conventions": "validation_v1",
        "facility": {
            "province": prov,
            "system": {"QC": "spede", "BC": "bc_obps", "AB": "tier", "ON": "eps"}[prov],
            "covered": regime != "none",
        },
        "project": {
            "in_service": "2026-12-31",
            "life_years": 20,
            "capex": [{"year": 0, "amount": hp.capex}],
            "technology_class": "heat_pump_process",
            "itc_eligible_share": hp.itc_eligible_share,
            "energy_deltas": {"natural_gas_gj": -hp.gas_gj_avoided, "electricity_mwh": hp.elec_mwh_added},
            "opex_delta": hp.om_delta,
        },
        "prices": {
            "natural_gas_gj": PARAMS["gas_delivered_ex_carbon_gj"]["value"][prov],
            "electricity_mwh": PARAMS["electricity_large_cents_kwh"]["value"][prov] * 10,
            "escalation": PARAMS["finance"]["energy_escalation"]["value"],
        },
        "finance": {
            "discount_rate": PARAMS["finance"]["discount_rate_nominal"]["value"],
            "itc_receipt_lag_years": 1,
        },
        "policy": {
            "credit_price_scenario": "upper_bound_headline" if regime == "headline" else "base",
            "itc_granted": itc,
            "grid_factor": "marginal",
            "marginal_grid_ef_g_kwh": 0.0,
        },
        "overrides": common_overrides(prov),
    }


EX3_SCENARIOS: dict[str, dict[str, Any]] = {
    "Headline": {"credit_price_scenario": "upper_bound_headline"},
    "Market $20, no floor": {"floor": "none"},
    "Market + 2030 floor": {"floor": "auto"},
    "CCfD $85 to 2040": {"floor": "auto", "ccfd": {"strike": 85, "term_end": 2040, "volume_share": 1.0}},
}


def ex3_case(capex: float, scenario: str) -> dict[str, Any]:
    return {
        "case_id": f"oracle-ex3-{int(capex / 1e6)}m-{scenario}",
        "as_of": "2026-09-29",
        "min_legal_status": "announced",
        "conventions": "validation_v1",
        "facility": {"province": "AB", "system": "tier", "covered": True},
        "project": {
            "in_service": "2026-12-31",
            "life_years": 20,
            "capex": [{"year": 0, "amount": capex}],
            "technology_class": "generic_abatement",
            "itc_measure": "none",
            "cca_class": "43.1",
            "opex_delta": 1_000_000,
            "covered_emissions_delta_t": -50_000,
        },
        "prices": {"escalation": 0.02},
        "finance": {"discount_rate": 0.08},
        "policy": {"itc_granted": True, **EX3_SCENARIOS[scenario]},
        "overrides": common_overrides("AB"),
    }
