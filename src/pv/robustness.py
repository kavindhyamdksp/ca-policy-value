"""Breakeven vs realizable band, discrete policy-state grid and seeded Monte Carlo (plan §4.4)."""

from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from pv import carbon, tax
from pv.case import Ccfd, CcfdStrike, MonteCarlo, Scenario, Sensitivity
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


# ---------------------------------------------------------------- vectorized evaluation


@dataclass(frozen=True)
class Draws:
    """Per-draw inputs for vectorized NPV: realized carbon paths and multipliers on the base case."""

    carbon: F  # (k, N) realized $/t
    capex: F  # (k,) multipliers
    gas: F
    elec: F
    opex: F
    granted: NDArray[np.bool_]

    @classmethod
    def base(cls, m: Model, k: int = 1, carbon_paths: F | None = None) -> Draws:
        c = m.case
        path = m.path(c.policy.credit_price_scenario, c.policy.floor, c.policy.ccfd)
        ones = np.ones(k)
        return cls(
            np.tile(path, (k, 1)) if carbon_paths is None else carbon_paths,
            ones,
            ones,
            ones,
            ones,
            np.full(k, m.ti.granted),
        )


def base_market(m: Model) -> F:
    """Market path of the case's scenario (headline for the upper-bound scenario), before rules."""
    s = m.case.policy.credit_price_scenario
    return m.ci.headline if s == "upper_bound_headline" else m.ci.market[s]


def realized_draws(m: Model, market: F, floor: F, ccfd: Ccfd | Literal["case"] | None = "case") -> F:
    """Realized $/t per draw from (shocked) market paths, mirroring carbon.realized:
    output-based → fund cap, floor, CCfD; QC and the headline upper bound → the path itself."""
    c = m.case
    if m.ci.kind == "none":
        return np.zeros_like(market)
    if m.ci.kind == "qc" or c.policy.credit_price_scenario == "upper_bound_headline":
        return market
    contract = c.policy.ccfd if ccfd == "case" else ccfd
    return carbon.apply_rules(market, m.ci.fund, floor, m.years, contract)


def _unit_cca(m: Model, granted: NDArray[np.bool_]) -> tuple[F, F]:
    """CCA schedules per $1 of UCC (granted, denied); computed only for the states that occur."""
    assert m._view is not None
    zero = np.zeros(m.n + 1)
    g = tax.cca_schedule(m.case, m._view, 1.0, True, m.n) if granted.any() else zero
    d = tax.cca_schedule(m.case, m._view, 1.0, False, m.n) if not granted.all() else zero
    return g, d


def npv_draws(m: Model, d: Draws, rate: float | None = None) -> F:
    """NPV per draw. ITC and UCC are affine in the capex multiplier; CCA is linear in UCC."""
    c = m.case
    r = m.rate if rate is None else rate
    disc = (1 + r) ** -np.arange(m.n + 1, dtype=float)
    tau = m.tau
    assistance = c.project.other_assistance
    capex = m.capex_total * d.capex
    itc = np.where(d.granted, m.ti.rho * m.ti.itc_share * np.maximum(capex - assistance, 0.0), 0.0)
    ucc = np.maximum(capex - itc - assistance, 0.0)
    unit_g, unit_d = _unit_cca(m, d.granted)
    cca = np.where(d.granted[:, None], unit_g[None, :], unit_d[None, :]) * ucc[:, None]
    pretax = (
        m.gas_saving * d.gas[:, None]
        + m.tonnes * d.carbon
        - m.elec_cost * d.elec[:, None]
        - m.opex * d.opex[:, None]
    )
    shield = cca[:, 1:] * tau if c.facility.taxable else 0.0
    flows = pretax * (1 - tau) + shield
    lag = min(m.lag, m.n)
    out = -(m.capex_by_year[None, :] * d.capex[:, None]) @ disc + flows @ disc[1:] + itc * disc[lag]
    return np.asarray(out, dtype=np.float64)


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


def mc_npvs(m: Model, mc: MonteCarlo, ccfd: Ccfd | Literal["case"] | None = "case") -> tuple[F, float | None]:
    """NPV per draw (and the ITC probability used). Shocks hit the market price; cap, floor and CCfD
    apply after. The draw sequence depends only on the seed, so varying `ccfd` uses common random numbers."""
    c = m.case
    rng = np.random.default_rng(mc.seed)
    n, years = mc.draws, m.years
    ci = m.ci

    # regimes → market and floor paths per draw
    names = list(mc.regimes)
    probs = np.array([mc.regimes[k].p for k in names])
    idx = np.searchsorted(np.cumsum(probs), rng.random(n), side="right").clip(0, len(names) - 1)
    market0 = base_market(m)
    base_scale = carbon.floor_scale(ci, c.policy.floor)
    market = np.empty((n, m.n))
    floor = np.empty((n, m.n))
    for i, k in enumerate(names):
        r = mc.regimes[k]
        after = years >= (r.from_year if r.from_year is not None else years[0])
        mk = np.where(
            after, r.market_value if r.market_value is not None else market0 * r.market_scale, market0
        )
        scale = r.floor_scale if r.floor_scale is not None else base_scale
        fl = np.where(after, ci.floor * scale, ci.floor * base_scale)
        sel = idx == i
        market[sel] = mk
        floor[sel] = fl
    shock = _lognormal(rng, mc.shocks.credit_sigma, n)[:, None]
    v = realized_draws(m, market * shock, floor, ccfd)

    gm = _lognormal(rng, mc.shocks.gas_sigma, n)
    em = _lognormal(rng, mc.shocks.elec_sigma, n)
    lo, mode, hi = mc.shocks.capex_triangular
    cm = rng.triangular(lo, mode, hi, n) if hi > lo else np.full(n, mode)

    if mc.itc_probability is not None:
        p_itc: float | None = mc.itc_probability
    else:
        p_itc = tax.eligibility_probability(m.ti.eligibility) if c.project.itc_measure == "ct" else None
    granted = rng.random(n) < p_itc if p_itc is not None else np.full(n, m.ti.granted)
    return npv_draws(m, Draws(v, cm, gm, em, np.ones(n), granted)), p_itc


def monte_carlo(m: Model, mc: MonteCarlo) -> McResult:
    """Seeded, vectorized over draws; reports mean, P10/P50/P90 and P(NPV>0)."""
    vals, p_itc = mc_npvs(m, mc)
    p10, p50, p90 = np.percentile(vals, [10, 50, 90])
    return McResult(
        mc.draws,
        mc.seed,
        float(vals.mean()),
        float(p10),
        float(p50),
        float(p90),
        float((vals > 0).mean()),
        p_itc,
    )


# ---------------------------------------------------------------- one-way sensitivity


SENSITIVITY_VARIABLES = ("capex", "gas_price", "electricity_price", "opex", "credit_price", "discount_rate")


def sensitivity(m: Model, spec: Sensitivity) -> dict[str, Any]:
    """One-way (tornado) sensitivity: each variable at its low and high value, all else at the base case.
    Relative ± on capex, energy prices, opex and the market credit price (applied before cap, floor and
    CCfD); absolute ± on the discount rate. Sorted by NPV swing."""
    base = float(npv_draws(m, Draws.base(m))[0])
    two = Draws.base(m, 2)
    rows: list[dict[str, Any]] = []
    for name in SENSITIVITY_VARIABLES:
        delta = getattr(spec, name)
        if delta is None:
            continue
        if name == "discount_rate":
            lo_in, hi_in = m.rate - delta, m.rate + delta
            vals = [float(npv_draws(m, Draws.base(m), rate=r)[0]) for r in (lo_in, hi_in)]
        else:
            lo_in, hi_in = 1 - delta, 1 + delta
            mult = np.array([lo_in, hi_in])
            if name == "credit_price":
                c = m.case
                floor = carbon.floor_scale(m.ci, c.policy.floor) * m.ci.floor
                d = replace(two, carbon=realized_draws(m, base_market(m)[None, :] * mult[:, None], floor))
            else:
                field_ = {"capex": "capex", "gas_price": "gas", "electricity_price": "elec", "opex": "opex"}[
                    name
                ]
                d = replace(two, **{field_: mult})
            vals = [float(v) for v in npv_draws(m, d)]
        rows.append(
            {
                "variable": name,
                "low_input": lo_in,
                "high_input": hi_in,
                "npv_low": vals[0],
                "npv_high": vals[1],
                "swing": abs(vals[1] - vals[0]),
                "decision_changes": any((v > 0) != (base > 0) for v in vals),
            }
        )
    rows.sort(key=lambda r: (-r["swing"], r["variable"]))
    return {"base_npv": base, "rows": rows}


# ---------------------------------------------------------------- CCfD strike solver


def _bisect_min(ok: Callable[[float], bool], hi: float, tol: float) -> float | None:
    """Smallest x in [0, hi] with ok(x), for ok monotone (False → True); None if ok(hi) is False."""
    if ok(0.0):
        return 0.0
    if not ok(hi):
        return None
    lo = 0.0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi


def ccfd_strike(m: Model, spec: CcfdStrike) -> dict[str, Any]:
    """Minimum CCfD strike ($/t, nominal) for NPV >= 0 at the discount rate (or a hurdle rate), and
    optionally for P(NPV>0) >= target under the case's Monte Carlo. Term and volume share come from the
    spec or the case's CCfD. Realized value is monotone in the strike, so bisection is exact to `tol`."""
    c = m.case
    term = spec.term_end if spec.term_end is not None else (c.policy.ccfd.term_end if c.policy.ccfd else None)
    vs = spec.volume_share
    if vs is None:
        vs = c.policy.ccfd.volume_share if c.policy.ccfd else 1.0
    out: dict[str, Any] = {
        "term_end": term,
        "volume_share": vs,
        "hurdle_rate": spec.hurdle_rate,
        "target_p": spec.target_p,
        "npv_zero_strike": None,
        "target_p_strike": None,
        "note": None,
    }
    if m.ci.kind != "covered" or c.policy.credit_price_scenario == "upper_bound_headline" or term is None:
        out["note"] = (
            "not applicable: a CCfD settles against an output-based credit market (covered facility, "
            "non-headline scenario, term_end set)"
        )
        return out
    rate = spec.hurdle_rate
    floor_mode = c.policy.floor

    def contract(strike: float) -> Ccfd:
        return Ccfd(strike=strike, term_end=term, volume_share=vs)

    def npv_ok(strike: float) -> bool:
        path = m.path(c.policy.credit_price_scenario, floor_mode, contract(strike))
        d = Draws.base(m, 1, path[None, :])
        return float(npv_draws(m, d, rate=rate)[0]) >= 0

    out["npv_zero_strike"] = _bisect_min(npv_ok, spec.max_strike, spec.tolerance)
    if out["npv_zero_strike"] is None:
        out["note"] = f"NPV stays negative up to a ${spec.max_strike:,.0f}/t strike"
    elif out["npv_zero_strike"] == 0.0:
        out["note"] = "NPV >= 0 without a CCfD"
    if spec.target_p is not None:
        mc = c.robustness.monte_carlo
        assert mc is not None  # enforced by the case model
        target = spec.target_p

        def p_ok(strike: float) -> bool:
            return float((mc_npvs(m, mc, contract(strike))[0] > 0).mean()) >= target

        out["target_p_strike"] = _bisect_min(p_ok, spec.max_strike, spec.tolerance)
    return out


def deterministic_npv(m: Model) -> float:
    c = m.case
    return npv(
        m.cashflows(
            m.path(c.policy.credit_price_scenario, c.policy.floor, c.policy.ccfd), granted=m.ti.granted
        ),
        m.rate,
    )
