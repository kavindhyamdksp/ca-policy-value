"""Realized carbon value per tonne by year (plan §4.1, ADR-0005). Pure functions over ledger + case."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pv.case import Case, Ccfd, Scenario
from pv.ledger import LedgerView

F = NDArray[np.float64]

HEADLINE = "fed.carbon.benchmark_path"


@dataclass(frozen=True)
class SystemSpec:
    obs: str  # credit-price observation record
    method: str  # "flat": obs held flat in real terms; "ratio": obs / compliance price, applied to the path
    price: str  # fund / compliance price series (cap on realized value)
    floor: str | None = None


SYSTEMS: dict[str, SystemSpec] = {
    "tier": SystemSpec("ab.tier.credit_obs", "flat", "ab.tier.fund_price", "ab.tier.floor"),
    "eps": SystemSpec("on.eps.epu_obs", "ratio", "on.eps.price_schedule"),
    "bc_obps": SystemSpec("bc.obps.credit_obs", "ratio", "bc.obps.price"),
    "fed_obps": SystemSpec("fed.obps.credit_obs", "ratio", "fed.ggppa.schedule4"),
}
QC_OBS = "qc.spede.auction_obs"
QC_ESC = "qc.spede.reserve_escalation"


def path_from_series(series: dict[int, float], years: NDArray[np.int64], *, zero_before: bool = False) -> F:
    """Linear interpolation between stated years, flat beyond the ends (optionally zero before the first)."""
    xs = np.array(sorted(series), dtype=float)
    ys = np.array([series[int(x)] for x in xs], dtype=float)
    out = np.interp(years.astype(float), xs, ys)
    if zero_before:
        out = np.where(years < xs[0], 0.0, out)
    return np.asarray(out, dtype=np.float64)


def step_lookup(series: dict[int, float], year: int) -> float | None:
    """Value for the latest stated year <= `year` (None if before the first)."""
    keys = [k for k in sorted(series) if k <= year]
    return series[keys[-1]] if keys else None


@dataclass(frozen=True)
class CarbonInputs:
    """Resolved carbon paths for a case (all arrays over operating years)."""

    years: NDArray[np.int64]
    kind: str  # none | qc | covered
    market: dict[str, F]  # low / base / high (before cap/floor)
    fund: F  # cap (inf if none)
    floor: F  # announced/legal floor path (0 before effective)
    floor_trusted: bool
    headline: F
    warnings: tuple[str, ...] = ()

    def band(self) -> dict[str, F]:
        """Realizable band paths: low/base/high under the base floor treatment, plus headline."""
        mode = "as_announced" if self.floor_trusted else "none"
        out = {s: realized(self, s, floor_mode=mode) for s in ("low", "base", "high")}
        out["upper_bound_headline"] = realized(self, "upper_bound_headline")
        return out


def resolve(case: Case, view: LedgerView, years: NDArray[np.int64]) -> CarbonInputs:
    n = len(years)
    warns: list[str] = []
    zeros = np.zeros(n)
    kind = case.carbon_kind
    infl = 0.0 if case.conventions == "validation_v1" else _inflation(case)

    if kind == "none":
        return CarbonInputs(
            years, kind, dict.fromkeys(("low", "base", "high"), zeros), zeros, zeros, False, zeros
        )

    if kind == "qc":
        obs = view.get(QC_OBS)
        t = obs.table()
        y0 = int(t.get("year", obs.effective_from.year))
        esc = view.get(QC_ESC).table()
        real = float(esc["real_rate"])
        g = (
            real
            if case.conventions == "validation_v1" or esc.get("plus_inflation") in (None, "no", False)
            else ((1 + real) * (1 + infl) - 1)
        )
        grow = (1 + g) ** (years - y0)
        base = obs.num("settlement") * grow
        low = obs.num("reserve") * grow if "reserve" in t else base
        path = base.astype(np.float64)
        return CarbonInputs(
            years,
            kind,
            {"low": low.astype(np.float64), "base": path, "high": path},
            np.full(n, np.inf),
            zeros,
            False,
            path,
            ("QC cap-and-trade applies to all gas users; the C&T path is also the upper bound.",),
        )

    spec = SYSTEMS.get(case.facility.system)
    if spec is None:
        raise ValueError(
            f"system {case.facility.system!r} is not an output-based system for {case.facility.province}"
        )
    headline = path_from_series(view.series(HEADLINE, trusted=False, scenario=True), years)

    if view.entries(spec.price):
        price_series = view.series(spec.price)
        fund = path_from_series(price_series, years)
    else:
        price_series = view.series(HEADLINE, trusted=False, scenario=True)
        fund = headline
        warns.append(
            f"{spec.price} not trusted at min_legal_status={case.min_legal_status}; "
            "national benchmark used as cap"
        )

    obs = view.get(spec.obs)
    t = obs.table()
    y0 = int(t.get("year", obs.effective_from.year))
    if spec.method == "flat":
        drift = (1 + infl) ** (years - y0)
        base = obs.num("base") * drift
        low = (obs.num("low") if "low" in t else obs.num("base")) * drift
    else:
        ref = step_lookup(price_series, y0) or next(iter(price_series.values()))
        ratio = obs.num("ratio") if "ratio" in t else obs.num("price") / ref
        ratios = [ratio]
        if "discount_high" in t:
            ratios.append(1 - obs.num("discount_high"))
        if "discount_low" in t:
            ratios.append(1 - obs.num("discount_low"))
        base = ratio * fund
        low = min(ratios) * fund
    market = {"low": low.astype(np.float64), "base": base.astype(np.float64), "high": fund.copy()}

    floor = zeros
    trusted = False
    if spec.floor and view.has(spec.floor):
        trusted = not view.untrusted_only(spec.floor)
        rec = view.get(spec.floor, trusted=trusted, scenario=not trusted)
        floor = path_from_series(
            view.series(spec.floor, trusted=trusted, scenario=not trusted), years, zero_before=True
        )
        floor = np.where(years < rec.effective_from.year, 0.0, floor).astype(np.float64)
        if not trusted:
            warns.append(
                f"{spec.floor} is {rec.legal_status} (below min_legal_status={case.min_legal_status}): "
                "excluded from the base case, available as a scenario"
            )
    return CarbonInputs(years, kind, market, fund, floor, trusted, headline, tuple(warns))


def _inflation(case: Case) -> float:
    return case.prices.inflation if case.prices.inflation is not None else case.prices.escalation


def floor_scale(ci: CarbonInputs, mode: str) -> float:
    if mode == "auto":
        return 1.0 if ci.floor_trusted else 0.0
    return {"as_announced": 1.0, "half": 0.5, "none": 0.0}[mode]


def apply_rules(market: F, fund: F, floor: F, years: NDArray[np.int64], ccfd: Ccfd | None) -> F:
    """v = CCfD(max(min(market, fund), floor)). Broadcasts over leading draw dimensions."""
    m = np.maximum(np.minimum(market, fund), floor)
    if ccfd is None:
        return m
    within = years <= ccfd.term_end
    guaranteed = ccfd.volume_share * np.maximum(ccfd.strike, m) + (1 - ccfd.volume_share) * m
    return np.where(within, guaranteed, m).astype(np.float64)


def realized(
    ci: CarbonInputs,
    scenario: Scenario,
    *,
    floor_mode: str = "auto",
    ccfd: Ccfd | None = None,
) -> F:
    """Realized $/t path for one scenario."""
    if ci.kind == "none":
        return np.zeros(len(ci.years))
    if scenario == "upper_bound_headline":
        return ci.headline.copy()
    if ci.kind == "qc":
        return ci.market[scenario].copy()
    return apply_rules(ci.market[scenario], ci.fund, floor_scale(ci, floor_mode) * ci.floor, ci.years, ccfd)


def levelized(path: F, rate: float) -> float:
    """Flat-equivalent value of a path at discount rate `rate` (t = 1..N)."""
    disc = (1 + rate) ** -np.arange(1, len(path) + 1, dtype=float)
    return float((path * disc).sum() / disc.sum())
