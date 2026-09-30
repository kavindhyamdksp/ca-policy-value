"""Assemble a run into results.json (schema v1) and cashflows.csv; deterministic in case + ledger + seed."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

import numpy as np

from pv import __version__, robustness
from pv.case import Case
from pv.cashflow import Model, build, irr, npv, payback
from pv.ledger import OVERRIDE_URL, STATUS_RANK, Ledger, LedgerView

SCHEMA_VERSION = "pv.results/v1"


def _r(x: float | None, nd: int = 2) -> float | None:
    if x is None or not np.isfinite(x):
        return None
    v = round(float(x), nd)
    return 0.0 if v == 0 else v  # no negative zero


def _clean(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _clean(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [_clean(v) for v in obj]
    if isinstance(obj, bool | str) or obj is None:
        return obj
    if isinstance(obj, int | np.integer):
        return int(obj)
    if isinstance(obj, float | np.floating):
        return _r(float(obj), 6)
    return obj


def run_hash(case: Case, ledger: Ledger, seed: int | None) -> str:
    return hashlib.sha256(f"{case.digest()}|{ledger.digest}|{seed}".encode()).hexdigest()


def evaluate(case: Case, ledger: Ledger) -> tuple[dict[str, Any], Model, LedgerView]:
    view = ledger.view(case.as_of, case.min_legal_status, case.overrides)
    m = build(case, view)
    pol = case.policy
    path = m.path(pol.credit_price_scenario, pol.floor, pol.ccfd)
    cf = m.cashflows(path, granted=m.ti.granted)
    value = npv(cf, m.rate)
    rate_irr, irr_note = irr(cf)
    warnings = list(m.warnings)
    if irr_note:
        warnings.append(f"IRR not reported: {irr_note}")
    if pol.credit_price_scenario == "upper_bound_headline":
        warnings.append("Carbon valued at the headline benchmark: an UPPER BOUND, not a realizable price.")

    b = robustness.band(m)
    p_star = m.breakeven(m.ti.granted)
    g = robustness.grid(m) if case.robustness.grid else None
    mc = robustness.monte_carlo(m, case.robustness.monte_carlo) if case.robustness.monte_carlo else None
    stack = m.value_stack(pol.credit_price_scenario, pol.floor, pol.ccfd)
    disc_sum = float(m.disc[1:].sum())

    provenance, prov_warn = _provenance(view)
    warnings += prov_warn
    answer, deciding = _decision(value, g, m, b, p_star)

    res: dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "engine": f"policyvalue-ca {__version__}",
        "case_id": case.case_id,
        "run_hash": run_hash(case, ledger, mc.seed if mc else None),
        "inputs": {
            "case_sha256": case.digest(),
            "ledger_version": ledger.version,
            "ledger_sha256": ledger.digest,
            "seed": mc.seed if mc else None,
            "as_of": case.as_of.isoformat(),
            "min_legal_status": case.min_legal_status,
            "conventions": case.conventions,
        },
        "decision": {
            "answer": answer,
            "base_case": "GO" if value > 0 else "NO-GO",
            "npv": _r(value),
            "deciding_terms": deciding,
        },
        "metrics": {
            "npv": _r(value),
            "irr": _r(rate_irr, 6),
            "payback_simple_years": _r(payback(cf), 2),
            "payback_discounted_years": _r(payback(cf, m.rate), 2),
            "discount_rate": m.rate,
            "operating_years": [int(m.years[0]), int(m.years[-1])],
        },
        "value_stack": [
            {"step": s["step"], "npv": _r(s["npv"]), "delta": _r(s["delta"])}  # type: ignore[arg-type]
            for s in stack
        ],
        "carbon": {
            "kind": m.ci.kind,
            "scenario": pol.credit_price_scenario,
            "floor_mode": pol.floor,
            "floor_in_base": m.ci.floor_trusted if pol.floor == "auto" else pol.floor != "none",
            "ccfd": pol.ccfd.model_dump() if pol.ccfd else None,
            "covered_tonnes_per_yr": _r(m.tonnes, 1),
            "path": {str(y): _r(v, 4) for y, v in zip(m.years.tolist(), path.tolist(), strict=True)},
            "band_levelized": {k: _r(b[k]) for k in robustness.BAND_ORDER},
            "breakeven_flat": _r(p_star),
            "breakeven_position": robustness.breakeven_position(p_star, b),
        },
        "tax": {
            "rate": m.tau,
            "itc_measure": case.project.itc_measure,
            "eligibility": m.ti.eligibility,
            "itc_granted": m.ti.granted,
            "itc_rate_if_granted": m.ti.rho,
            "itc_amount": _r(m.itc(m.ti.granted)),
            "cca_class": case.project.cca_class if m.ti.granted else case.project.cca_class_if_ineligible,
        },
        "robustness": {
            "grid": _grid_json(g) if g else None,
            "monte_carlo": mc.as_dict() if mc else None,
        },
        "emissions": m.em.as_dict(disc_sum, value),
        "warnings": sorted(set(warnings)),
        "overrides": [o.model_dump() for o in case.overrides],
        "provenance": provenance,
    }
    return _clean(res), m, view


def _decision(
    value: float, g: dict[str, Any] | None, m: Model, b: dict[str, float], p_star: float | None
) -> tuple[str, list[str]]:
    terms: list[str] = []
    if g and g["n_states"] > 1:
        share = g["go_share"]
        if share == 1.0:
            answer = "GO"
        elif share == 0.0:
            answer = "NO-GO"
        else:
            answer = "DEPENDS-ON"
            for cond in g["minimal_go_conditions"][:4]:
                terms.append("GO if " + " and ".join(f"{k}={v}" for k, v in cond.items()))
    else:
        answer = "GO" if value > 0 else "NO-GO"
    if p_star is not None and m.ci.kind != "none":
        terms.append(f"breakeven carbon ${p_star:,.0f}/t vs base ${b['base']:,.0f}/t levelized")
    if m.ti.eligibility in ("case_by_case", "not_listed") and m.case.project.itc_measure == "ct":
        terms.append(f"CT ITC eligibility is {m.ti.eligibility} (granted in base: {m.ti.granted})")
    if answer != "DEPENDS-ON" and g and g["n_states"] > 1:
        terms.insert(0, f"{answer} in {g['go_count']} of {g['n_states']} policy states")
    return answer, terms


def _grid_json(g: dict[str, Any]) -> dict[str, Any]:
    return {
        "dimensions": g["dimensions"],
        "go_share": _r(g["go_share"], 4),
        "go_count": g["go_count"],
        "n_states": g["n_states"],
        "minimal_go_conditions": g["minimal_go_conditions"],
        "states": [{"state": s["state"], "npv": _r(s["npv"]), "go": s["go"]} for s in g["states"]],
    }


def _provenance(view: LedgerView) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    warns: list[str] = []
    for (rid, eff, status), use in sorted(view.used.items(), key=lambda kv: (kv[0][0], kv[0][1].isoformat())):
        r = use.record
        stale = r.is_stale(view.as_of)
        in_base = not use.scenario
        if r.overridden:
            warns.append(f"Override: {rid} = {r.value} ({r.override_reason})")
        if in_base and not r.overridden and STATUS_RANK.get(r.legal_status, 9) < STATUS_RANK["enacted"]:
            warns.append(f"Base case uses {r.legal_status} record {rid} (not yet law)")
        if stale:
            warns.append(f"Stale record {rid}: retrieved {r.retrieved}, past its {r.freshness} freshness SLA")
        rows.append(
            {
                "id": rid,
                "value": r.value,
                "unit": r.unit,
                "legal_status": status,
                "effective_from": eff.isoformat(),
                "used_in": "base" if in_base else "scenario",
                "overridden": r.overridden,
                "override_reason": r.override_reason or None,
                "stale": stale,
                "retrieved": r.retrieved.isoformat(),
                "sources": [
                    {
                        "url": s.url,
                        "title": s.title,
                        "publisher": s.publisher,
                        "retrieved": s.retrieved.isoformat(),
                    }
                    for s in r.sources
                    if s.url != OVERRIDE_URL or r.overridden
                ],
            }
        )
    return rows, warns


def to_json(res: dict[str, Any]) -> str:
    return json.dumps(res, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def cashflows_csv(m: Model) -> str:
    """Base-case annual cash flows with components (CAD nominal)."""
    c = m.case
    path = m.path(c.policy.credit_price_scenario, c.policy.floor, c.policy.ccfd)
    g = m.ti.granted
    itc = m.itc(g)
    cca = m.cca(g, itc)
    cf = m.cashflows(path, granted=g)
    carbon = np.concatenate([[0.0], m.tonnes * path])
    gas = np.concatenate([[0.0], m.gas_saving])
    elec = np.concatenate([[0.0], m.elec_cost])
    opex = np.concatenate([[0.0], m.opex])
    pretax = gas + carbon - elec - opex
    itc_col = np.zeros(m.n + 1)
    itc_col[min(m.lag, m.n)] = itc
    years = [int(c.project.in_service.year), *m.years.tolist()]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = [
        "t",
        "year",
        "capex",
        "gas_saving",
        "carbon_value",
        "electricity_cost",
        "opex_delta",
        "pretax",
        "cca",
        "itc",
        "cash_flow",
        "discounted_cash_flow",
    ]
    w.writerow(cols)
    for t in range(m.n + 1):
        row = [
            t,
            years[t],
            -m.capex_by_year[t],
            gas[t],
            carbon[t],
            elec[t],
            opex[t],
            pretax[t],
            cca[t],
            itc_col[t],
            cf[t],
            cf[t] * m.disc[t],
        ]
        w.writerow([row[0], row[1], *(f"{float(x) + 0.0:.2f}" for x in row[2:])])
    return buf.getvalue()
