"""Breakeven vs realizable band, discrete policy-state grid and seeded Monte Carlo (plan §4.4)."""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pv import carbon, tax
from pv.case import Ccfd, MonteCarlo, Scenario
from pv.cashflow import Model, npv

F = NDArray[np.float64]

BAND_ORDER = ("low", "base", "high", "upper_bound_headline")


def band(m: Model) -> dict[str, float]:
    """Levelized (flat-equivalent at r) realized carbon value of each scenario, $/t."""
    return {k: carbon.levelized(v, m.rate) for k, v in m.ci.band().items()}


def breakeven_position(p_star: float | None, b: dict[str, float]) -> str:
    if p_star is None:
        return "no carbon exposure"
    if p_star <= b["low"]:
        return "below the realizable band: GO even at the low credit price"
    if p_star <= b["base"]:
        return "within the band, at or below the base credit price"
    if p_star <= b["high"]:
        return "within the band, above the base credit price (needs high prices)"
    if p_star <= b["upper_bound_headline"]:
        return "above realizable prices; only the headline upper bound clears it"
    return "above the headline upper bound: NO-GO under any carbon view"


# ---------------------------------------------------------------- policy-state grid


def dimensions(m: Model, dims: tuple[str, ...]) -> dict[str, list[Any]]:
    c = m.case
    out: dict[str, list[Any]] = {}
    for d in dims:
        if d == "floor_status":
            if m.ci.floor.any():
                out[d] = ["as_announced", "half", "none"]
        elif d == "itc_granted":
            out[d] = [True, False]
        elif d == "ccfd":
            out[d] = [True, False] if c.policy.ccfd is not None else [False]
        elif d == "coverage":
            if m.ci.kind == "covered":
                out[d] = [True, False]
        elif d == "credit_scenario":
            out[d] = ["low", "base", "high"]
    return out


def state_npv(m: Model, state: dict[str, Any]) -> float:
    c = m.case
    scenario: Scenario = state.get("credit_scenario", c.policy.credit_price_scenario)
    floor_mode = state.get("floor_status", c.policy.floor)
    ccfd: Ccfd | None = c.policy.ccfd if state.get("ccfd", c.policy.ccfd is not None) else None
    path = m.path(scenario, floor_mode, ccfd)
    if not state.get("coverage", True):
        path = np.zeros(m.n)
    granted = state.get("itc_granted", m.ti.granted)
    return m.npv_of(path, granted)


def grid(m: Model) -> dict[str, Any]:
    dims = dimensions(m, m.case.robustness.grid)
    names = list(dims)
    states: list[dict[str, Any]] = []
    for combo in itertools.product(*(dims[n] for n in names)):
        st = dict(zip(names, combo, strict=True))
        v = state_npv(m, st)
        states.append({"state": st, "npv": v, "go": v > 0})
    n_go = sum(s["go"] for s in states)
    return {
        "dimensions": dims,
        "states": states,
        "go_share": n_go / len(states) if states else None,
        "go_count": n_go,
        "n_states": len(states),
        "minimal_go_conditions": minimal_conditions(dims, states),
    }


def minimal_conditions(dims: dict[str, list[Any]], states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Smallest partial assignments under which every completion is GO (prime implicants)."""
    if not states or not any(s["go"] for s in states):
        return []
    names = list(dims)
    go = {tuple(s["state"][n] for n in names): s["go"] for s in states}
    found: list[dict[str, Any]] = []
    for k in range(len(names) + 1):
        for subset in itertools.combinations(names, k):
            for vals in itertools.product(*(dims[n] for n in subset)):
                cond = dict(zip(subset, vals, strict=True))
                if any(all(f[n] == cond.get(n) for n in f) for f in found):
                    continue  # a smaller condition already implies this one
                if all(go[key] for key in go if all(key[names.index(n)] == v for n, v in cond.items())):
                    found.append(cond)
    return found


# ---------------------------------------------------------------- Monte Carlo


@dataclass(frozen=True)
class McResult:
    draws: int
    seed: int
    mean: float
    p10: float
    p50: float
    p90: float
    p_positive: float
    itc_probability: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "draws": self.draws,
            "seed": self.seed,
            "mean": round(self.mean, 2),
            "p10": round(self.p10, 2),
            "p50": round(self.p50, 2),
            "p90": round(self.p90, 2),
            "p_npv_positive": round(self.p_positive, 4),
            "itc_probability": self.itc_probability,
        }


def _lognormal(rng: np.random.Generator, sigma: float, n: int) -> F:
    return np.exp(rng.normal(0.0, sigma, n) - sigma**2 / 2) if sigma > 0 else np.ones(n)


def monte_carlo(m: Model, mc: MonteCarlo) -> McResult:
    """Vectorized over draws. Shocks hit the market price; fund cap, floor and CCfD apply after."""
    c = m.case
    rng = np.random.default_rng(mc.seed)
    n, years = mc.draws, m.years
    ci = m.ci

    # regimes → market and floor paths per draw
    names = list(mc.regimes)
    probs = np.array([mc.regimes[k].p for k in names])
    idx = np.searchsorted(np.cumsum(probs), rng.random(n), side="right").clip(0, len(names) - 1)
    scenario = c.policy.credit_price_scenario
    base_market = ci.headline if scenario == "upper_bound_headline" else ci.market[scenario]
    base_scale = carbon.floor_scale(ci, c.policy.floor)
    market = np.empty((n, m.n))
    floor = np.empty((n, m.n))
    for i, k in enumerate(names):
        r = mc.regimes[k]
        after = years >= (r.from_year if r.from_year is not None else years[0])
        mk = np.where(
            after, r.market_value if r.market_value is not None else base_market * r.market_scale, base_market
        )
        scale = r.floor_scale if r.floor_scale is not None else base_scale
        fl = np.where(after, ci.floor * scale, ci.floor * base_scale)
        sel = idx == i
        market[sel] = mk
        floor[sel] = fl
    shock = _lognormal(rng, mc.shocks.credit_sigma, n)[:, None]
    if ci.kind == "none":
        v = np.zeros((n, m.n))
    else:
        v = carbon.apply_rules(market * shock, ci.fund, floor, years, c.policy.ccfd)

    gm = _lognormal(rng, mc.shocks.gas_sigma, n)[:, None]
    em = _lognormal(rng, mc.shocks.elec_sigma, n)[:, None]
    lo, mode, hi = mc.shocks.capex_triangular
    cm = rng.triangular(lo, mode, hi, n) if hi > lo else np.full(n, mode)

    elig = m.ti.eligibility
    if mc.itc_probability is not None:
        p_itc: float | None = mc.itc_probability
    else:
        p_itc = tax.eligibility_probability(elig) if c.project.itc_measure == "ct" else None
    granted = rng.random(n) < p_itc if p_itc is not None else np.full(n, m.ti.granted)

    # cash flows, vectorized; ITC and UCC are affine in the capex multiplier
    disc = m.disc
    tau = m.tau
    assistance = c.project.other_assistance
    capex = m.capex_total * cm
    itc = np.where(granted, m.ti.rho * m.ti.itc_share * np.maximum(capex - assistance, 0.0), 0.0)
    ucc = np.maximum(capex - itc - assistance, 0.0)
    assert m._view is not None
    unit_g = tax.cca_schedule(c, m._view, 1.0, True, m.n)
    unit_d = tax.cca_schedule(c, m._view, 1.0, False, m.n)
    cca = np.where(granted[:, None], unit_g[None, :], unit_d[None, :]) * ucc[:, None]
    pretax = m.gas_saving * gm + m.tonnes * v - m.elec_cost * em - m.opex
    shield = cca[:, 1:] * tau if c.facility.taxable else 0.0
    flows = pretax * (1 - tau) + shield
    lag = min(m.lag, m.n)
    vals = -(m.capex_by_year[None, :] * cm[:, None]) @ disc + flows @ disc[1:] + itc * disc[lag]
    p10, p50, p90 = np.percentile(vals, [10, 50, 90])
    return McResult(
        n, mc.seed, float(vals.mean()), float(p10), float(p50), float(p90), float((vals > 0).mean()), p_itc
    )


def deterministic_npv(m: Model) -> float:
    c = m.case
    return npv(
        m.cashflows(
            m.path(c.policy.credit_price_scenario, c.policy.floor, c.policy.ccfd), granted=m.ti.granted
        ),
        m.rate,
    )
