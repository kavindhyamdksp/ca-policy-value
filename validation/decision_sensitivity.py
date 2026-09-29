"""
Validation-phase quantitative examples.

Question tested: do Canadian policy levers, jurisdiction and policy uncertainty materially
change corporate decarbonization investment decisions -- or is the decision dominated by
energy prices and capex, such that a policy-aware engine adds little?

This is research code, not the product. Deterministic, dependency-light, reproducible
(fixed RNG seed). Run:  python3 decision_sensitivity.py  > results.md
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace, field
from pathlib import Path

import numpy as np
import yaml
from scipy.optimize import brentq

P = yaml.safe_load((Path(__file__).parent / "params.yaml").read_text())
START_YEAR = 2027          # first operating year; capex at end of 2026 (t=0)
LIFE = 20
PROVS = ["QC", "ON", "AB", "BC", "NS"]


# ---------------------------------------------------------------- carbon price paths
def _interp_path(points: dict[int, float], years: range) -> np.ndarray:
    xs = sorted(points)
    ys = [points[x] for x in xs]
    return np.array([np.interp(y, xs, ys) for y in years])  # flat beyond ends


def headline(years: range) -> np.ndarray:
    return _interp_path(P["carbon"]["headline_path"]["value"], years)


def realized_carbon_path(prov: str, regime: str, years: range) -> np.ndarray:
    """$/t value of one avoided tonne of on-site gas combustion emissions.

    regime:
      'none'     -> site not covered by an industrial system (0, except QC where
                    cap-and-trade reaches every gas user via fuel distributors)
      'market'   -> covered facility; marginal value = credit/compliance-unit market price
      'headline' -> covered facility valued at headline benchmark (the naive approach)
    """
    c = P["carbon"]
    n = len(years)
    if prov == "QC":  # cap-and-trade applies to all users; covered or not
        base = c["qc_cap_and_trade_2026"]["value"]
        g = c["qc_cat_escalation"]["value"]
        return np.array([base * (1 + g) ** (y - 2026) for y in years])
    if regime == "none":
        return np.zeros(n)
    h = headline(years)
    if regime == "headline":
        return h
    if regime != "market":
        raise ValueError(regime)
    if prov == "AB":
        floor = _interp_path(c["ab_tier_floor"]["value"], years)
        floor[np.array(years) < 2030] = 0.0
        return np.maximum(c["ab_tier_credit_market"]["value"], floor)
    if prov == "ON":
        return h * (1 - c["on_eps_market_discount"]["value"])
    if prov == "BC":
        return h * c["bc_obps_market_ratio"]["value"]
    if prov == "NS":  # treated as federal-OBPS-like credit market (assumption)
        return h * c["fed_obps_market_ratio"]["value"]
    raise ValueError(prov)


# ---------------------------------------------------------------- project model
@dataclass(frozen=True)
class Project:
    name: str
    capex: float                  # $ at t=0 (incremental vs counterfactual)
    itc_eligible_share: float     # share of capex that is CT-ITC eligible (0 if ineligible)
    gas_gj_avoided: float         # GJ/yr fuel input avoided
    elec_mwh_added: float         # MWh/yr added
    om_delta: float               # $/yr incremental O&M (+ = cost)
    elec_class: str = "large"     # 'large' or 'medium'
    gas_adder: float = 0.0        # $/GJ adder (e.g., commercial vs industrial delivery)
    life: int = LIFE


@dataclass(frozen=True)
class Context:
    prov: str
    carbon_regime: str = "none"   # none | market | headline | custom
    taxable: bool = True
    itc_on: bool = True           # whether the ITC is actually obtained
    itc_delay_years: int = 1      # CRA processing lag (claims audited 100%)
    expensing: bool = True        # Class 43.1 immediate expensing (tied to clean-tech eligibility)
    gas_mult: float = 1.0
    elec_mult: float = 1.0
    capex_mult: float = 1.0
    custom_carbon: np.ndarray | None = field(default=None, compare=False)
    discount: float = P["finance"]["discount_rate_nominal"]["value"]
    esc: float = P["finance"]["energy_escalation"]["value"]


def cashflows(pr: Project, cx: Context) -> np.ndarray:
    years = range(START_YEAR, START_YEAR + pr.life)
    t = np.arange(1, pr.life + 1)
    esc = (1 + cx.esc) ** (t - 1)
    gas_p = (P["gas_delivered_ex_carbon_gj"]["value"][cx.prov] + pr.gas_adder) * cx.gas_mult * esc
    el_tab = P[f"electricity_{pr.elec_class}_cents_kwh"]["value"]
    el_p = el_tab[cx.prov] / 100 * 1000 * cx.elec_mult * esc          # $/MWh
    if cx.custom_carbon is not None:
        cp = cx.custom_carbon
    else:
        cp = realized_carbon_path(cx.prov, cx.carbon_regime, years)
    tco2 = pr.gas_gj_avoided * P["gas_ef_t_per_gj"]["value"]
    pretax = pr.gas_gj_avoided * gas_p + tco2 * cp - pr.elec_mwh_added * el_p - pr.om_delta * esc

    capex = pr.capex * cx.capex_mult
    cf = np.zeros(pr.life + 1)
    cf[0] = -capex
    if not cx.taxable:
        cf[1:] = pretax
        return cf
    tax = P["tax_rate"][cx.prov]
    itc = 0.0
    if cx.itc_on and pr.itc_eligible_share > 0:
        itc = P["itc"]["ct_rate"]["value"] * pr.itc_eligible_share * capex
        cf[min(cx.itc_delay_years, pr.life)] += itc
    ucc = capex - itc  # ITC reduces the depreciable base
    cca = np.zeros(pr.life + 1)
    if cx.expensing:
        cca[1] = ucc
    else:  # Class 8-like 20% declining balance, half-year rule
        bal = ucc
        for i in range(1, pr.life + 1):
            rate = 0.10 if i == 1 else 0.20
            cca[i] = bal * rate
            bal -= cca[i]
    cf[1:] += pretax * (1 - tax) + cca[1:] * tax  # assumes taxable capacity to use deductions
    return cf


def npv(cf: np.ndarray, r: float) -> float:
    return float(sum(c / (1 + r) ** i for i, c in enumerate(cf)))


def irr(cf: np.ndarray) -> float | None:
    f = lambda r: npv(cf, r)
    try:
        return brentq(f, -0.99, 3.0)
    except ValueError:
        return None


def payback(cf: np.ndarray) -> float | None:
    cum = np.cumsum(cf)
    for i in range(1, len(cum)):
        if cum[i] >= 0:
            return i - 1 + (-cum[i - 1]) / cf[i]
    return None


def breakeven_flat_carbon(pr: Project, cx: Context) -> float:
    """Flat nominal $/t (all years) at which NPV = 0 -- the 'carbon price the project needs'."""
    n = pr.life
    f = lambda p: npv(cashflows(pr, replace(cx, custom_carbon=np.full(n, p))), cx.discount)
    lo, hi = -2000.0, 5000.0
    if f(lo) > 0:
        return float("-inf")
    return brentq(f, lo, hi)


def fmt_m(x: float) -> str:
    return f"{x/1e6:+.2f}"


def fmt_pct(x):
    return "n/a" if x is None else f"{x*100:.1f}%"


def fmt_pb(x):
    return ">life" if x is None else f"{x:.1f}"


# ---------------------------------------------------------------- Example 1
HP_IND = Project(
    name="2 MWth industrial process heat pump (COP 3) displacing gas boiler, retrofit",
    capex=3_500_000,
    itc_eligible_share=0.85,
    gas_gj_avoided=43_200 / 0.85,     # 12,000 MWh_th useful heat at 85% boiler efficiency
    elec_mwh_added=12_000 / 3.0,
    om_delta=30_000,
)


def example1():
    out = ["## Example 1 - Industrial process heat pump (2 MWth, retrofit)\n"]
    tco2 = HP_IND.gas_gj_avoided * P["gas_ef_t_per_gj"]["value"]
    out.append(f"Capex ${HP_IND.capex/1e6:.1f}M; gas avoided {HP_IND.gas_gj_avoided:,.0f} GJ/yr "
               f"(~{tco2:,.0f} tCO2e/yr on site); electricity added {HP_IND.elec_mwh_added:,.0f} MWh/yr; "
               f"20-yr life; 8% nominal discount; taxable corporation.\n")
    out.append("NPV in $M. Carbon regimes: *none* = site below industrial thresholds; *market* = covered "
               "facility valued at credit-market price (AB with 2030+ floor); *headline* = covered facility "
               "valued at the benchmark price (the common shortcut). QC cap-and-trade applies to all gas users.\n")
    out.append("| Prov | ITC | none | market | headline | IRR (market) | Payback yrs (market) | Breakeven flat $/t |")
    out.append("|---|---|---|---|---|---|---|---|")
    rows = {}
    for prov in PROVS:
        for itc_on in (True, False):
            vals = {}
            for reg in ("none", "market", "headline"):
                cx = Context(prov=prov, carbon_regime=reg, itc_on=itc_on, expensing=itc_on)
                vals[reg] = npv(cashflows(HP_IND, cx), cx.discount)
            cxm = Context(prov=prov, carbon_regime="market", itc_on=itc_on, expensing=itc_on)
            cfm = cashflows(HP_IND, cxm)
            be = breakeven_flat_carbon(HP_IND, cxm)
            rows[(prov, itc_on)] = vals
            out.append(f"| {prov} | {'yes' if itc_on else 'no'} | {fmt_m(vals['none'])} | {fmt_m(vals['market'])} | "
                       f"{fmt_m(vals['headline'])} | {fmt_pct(irr(cfm))} | {fmt_pb(payback(cfm))} | {be:,.0f} |")
    # decision flips
    flips = []
    for prov in PROVS:
        for itc_on in (True, False):
            v = rows[(prov, itc_on)]
            if (v["market"] > 0) != (v["headline"] > 0):
                flips.append(f"{prov} (ITC {'yes' if itc_on else 'no'}): headline says "
                             f"{'GO' if v['headline']>0 else 'NO-GO'}, market-price says {'GO' if v['market']>0 else 'NO-GO'}")
            if (v["none"] > 0) != (v["market"] > 0):
                flips.append(f"{prov} (ITC {'yes' if itc_on else 'no'}): coverage status flips decision "
                             f"(not covered {'GO' if v['none']>0 else 'NO-GO'} vs covered {'GO' if v['market']>0 else 'NO-GO'})")
        a, b = rows[(prov, True)]["market"], rows[(prov, False)]["market"]
        if (a > 0) != (b > 0):
            flips.append(f"{prov} (covered, market): ITC eligibility flips decision")
    out.append("\n**Decision flips detected:**\n")
    out += [f"- {f}" for f in flips] or ["- none"]

    # net system emissions (grid factors)
    ef = {"QC": 2.5, "ON": 73.8, "AB": 335, "BC": 22.8, "NS": 528}
    out.append("\n**Net emissions effect (on-site avoided minus added grid emissions, average grid factor):**\n")
    out.append("| Prov | On-site t/yr avoided | Grid t/yr added | Net t/yr | Net as % of on-site |")
    out.append("|---|---|---|---|---|")
    for prov in PROVS:
        g = HP_IND.elec_mwh_added * ef[prov] / 1000
        out.append(f"| {prov} | {tco2:,.0f} | {g:,.0f} | {tco2-g:,.0f} | {(tco2-g)/tco2*100:.0f}% |")
    g_on_marg = HP_IND.elec_mwh_added * 450 / 1000
    out.append(f"\nOntario at a marginal (gas-fired) factor of ~450 g/kWh: grid adds {g_on_marg:,.0f} t/yr, "
               f"net {tco2-g_on_marg:,.0f} t/yr ({(tco2-g_on_marg)/tco2*100:.0f}% of on-site).")
    return "\n".join(out), rows


# ---------------------------------------------------------------- Example 2
HP_BLDG = Project(
    name="Commercial building: end-of-life boiler replacement, 500 kW air-source HP vs new gas boiler",
    capex=900_000 - 150_000,          # incremental over like-for-like gas boiler
    itc_eligible_share=720_000 / 750_000,  # ~80% of HP system cost eligible, all of it in the increment
    gas_gj_avoided=3_060 / 0.85,
    elec_mwh_added=850 / 2.5,
    om_delta=5_000,
    elec_class="medium",
    gas_adder=2.0,
)


def example2():
    out = ["## Example 2 - Commercial building heat pump at boiler end-of-life (not an industrial emitter)\n"]
    out.append("Incremental capex $0.75M (HP $0.90M vs gas boiler $0.15M); 3,060 GJ useful heat/yr; SCOP 2.5; "
               "medium-power electricity tariff; commercial gas = industrial + $2/GJ; no industrial carbon price "
               "(below thresholds) except QC cap-and-trade embedded in gas.\n")
    out.append("| Prov | Taxable owner + CT ITC NPV $M | Taxable, ITC denied NPV $M | Tax-exempt owner (hospital/university/municipal) NPV $M |")
    out.append("|---|---|---|---|")
    res = {}
    for prov in PROVS:
        a = npv(cashflows(HP_BLDG, Context(prov=prov)), 0.08)
        b = npv(cashflows(HP_BLDG, Context(prov=prov, itc_on=False, expensing=False)), 0.08)
        c = npv(cashflows(HP_BLDG, Context(prov=prov, taxable=False)), 0.08)
        res[prov] = (a, b, c)
        out.append(f"| {prov} | {fmt_m(a)} | {fmt_m(b)} | {fmt_m(c)} |")
    return "\n".join(out), res


# ---------------------------------------------------------------- Example 3
def example3():
    out = ["## Example 3 - Large Alberta emitter: which carbon-value assumption clears the hurdle?\n"]
    out.append("Generic abatement project at an AB TIER facility: abates 50 kt/yr for 20 years, +$1.0M/yr net opex, "
               "taxable (23%), immediate expensing assumed, no ITC. Capex is swept to cover projects from cheap to "
               "expensive abatement. Carbon value = credits generated/avoided x price.\n")
    abated = 50_000
    years = range(START_YEAR, START_YEAR + LIFE)
    yrs = np.array(years)
    h = headline(years)
    mkt_nofloor = np.full(LIFE, 20.0)
    mkt_floor = realized_carbon_path("AB", "market", years)
    ccfd = np.where(yrs <= 2040, np.maximum(85.0, mkt_floor), mkt_floor)
    scen = {
        "Headline": h,
        "Market $20, no floor": mkt_nofloor,
        "Market + 2030 floor": mkt_floor,
        "CCfD $85 to 2040": ccfd,
    }

    def value(capex, path):
        pr = Project(name="x", capex=capex, itc_eligible_share=0.0, gas_gj_avoided=0.0,
                     elec_mwh_added=0.0, om_delta=1_000_000)
        cf = cashflows(pr, Context(prov="AB", custom_carbon=np.zeros(LIFE)))
        cf[1:] += abated * path * (1 - P["tax_rate"]["AB"])
        return cf

    out.append("| Capex $M | Breakeven flat $/t | " + " | ".join(f"{k} NPV $M" for k in scen) + " | Decision spread |")
    out.append("|---|---|" + "---|" * len(scen) + "---|")
    res = {}
    for capex in (15e6, 25e6, 35e6, 45e6, 60e6):
        f = lambda p: npv(value(capex, np.full(LIFE, p)), 0.08)
        be = brentq(f, -500, 3000)
        vals = {k: npv(value(capex, path), 0.08) for k, path in scen.items()}
        gos = [k for k, v in vals.items() if v > 0]
        spread = ("all GO" if len(gos) == len(scen) else "all NO-GO" if not gos
                  else "FLIPS: GO only under " + ", ".join(gos))
        res[capex] = (be, vals)
        out.append(f"| {capex/1e6:.0f} | {be:,.0f} | " + " | ".join(fmt_m(v) for v in vals.values()) + f" | {spread} |")
    disc = 1.08 ** -np.arange(1, LIFE + 1)
    lev = {k: float((path * disc).sum() / disc.sum()) for k, path in scen.items()}
    out.append("\nLevelized (flat-equivalent at 8%) carbon value of each assumption: " +
               "; ".join(f"{k} ${v:,.0f}/t" for k, v in lev.items()) + ".")
    out.append(f"The carbon-value assumption decides the investment for any project whose breakeven lies between "
               f"${min(lev.values()):,.0f} and ${max(lev.values()):,.0f}/t. A CCfD (vs merchant credits with the "
               f"announced floor) decides it between ${lev['Market + 2030 floor']:,.0f} and ${lev['CCfD $85 to 2040']:,.0f}/t.")
    return "\n".join(out), res


# ---------------------------------------------------------------- Monte Carlo
def monte_carlo(n=20_000, seed=20260929):
    """Policy-regime + price uncertainty for Example 1 in AB and ON (covered facility), and Example 3.

    Regime probabilities are SUBJECTIVE, illustrative judgements. The point is to show whether an
    explicit, user-set policy-risk layer changes the answer vs a single deterministic path.
    """
    rng = np.random.default_rng(seed)
    years = range(START_YEAR, START_YEAR + LIFE)
    yrs = np.array(years)
    h = headline(years)
    out = ["## Monte Carlo - policy-regime and price uncertainty (illustrative probabilities)\n"]
    out.append(f"n = {n:,} draws, seed {seed}. Persistent log-normal shocks: gas sigma 0.30, electricity 0.15, "
               "credit price sigma 0.35; capex overrun triangular(-10%, 0, +30%); CT-ITC eligibility for a "
               "process heat pump is case-by-case, modelled as p(eligible)=0.6.\n")

    def regime_paths(prov, shock_sigma=0.35):
        """Return per-draw realized carbon paths. The log-normal shock applies to the MARKET price;
        any floor is applied afterwards (a legal floor is not itself shocked)."""
        u = rng.random(n)
        market = np.zeros((n, LIFE))
        floor = np.zeros((n, LIFE))
        if prov == "AB":
            ann = realized_carbon_path("AB", "market", years)          # max(20, floor) path
            fl = np.where(yrs >= 2030, ann, 0.0)                        # announced floor (0 before 2030)
            a = u < 0.55; b = (u >= 0.55) & (u < 0.85); c = u >= 0.85
            market[a] = 20.0; floor[a] = fl
            market[b] = 20.0; floor[b] = 0.5 * fl
            market[c] = 15.0
            desc = ("AB regimes: floor as announced p=0.55; floor at half strength p=0.30; policy rollback "
                    "(market $15, no floor) p=0.15. Shock applies to the $20 market price; floor applied after.")
        elif prov == "BC":
            a = u < 0.6; b = (u >= 0.6) & (u < 0.9); c = u >= 0.9
            market[a] = h * 0.68; market[b] = h * 0.40; market[c] = np.where(yrs >= 2029, 0.0, h * 0.68)
            desc = "BC regimes: credits at 68% of headline p=0.60; oversupply to 40% p=0.30; OBPS repealed from 2029 p=0.10"
        elif prov == "QC":
            base = realized_carbon_path("QC", "none", years)
            a = u < 0.85
            market[a] = base
            market[~a] = np.where(yrs >= 2029, 30.0, base)
            desc = "QC regimes: cap-and-trade continues (+5%/yr) p=0.85; market breakdown to $30 from 2029 p=0.15"
        else:  # ON
            a = u < 0.6; b = (u >= 0.6) & (u < 0.9); c = u >= 0.9
            market[a] = h * 0.8; market[b] = h * 0.45; market[c] = np.where(yrs >= 2029, 0.0, h * 0.8)
            desc = "ON regimes: EPU at 80% of headline p=0.60; oversupply to 45% p=0.30; EPS repealed from 2029 p=0.10"
        shock = np.exp(rng.normal(0, shock_sigma, (n, 1)) - shock_sigma ** 2 / 2)
        return np.maximum(market * shock, floor), desc

    tab = ["| Case | Deterministic NPV @ headline $M | Deterministic NPV @ market $M | MC mean $M | P10 | P50 | P90 | P(NPV>0) |",
           "|---|---|---|---|---|---|---|---|"]
    notes = []
    policy_only = ["| Case | Deterministic @ market $M | Policy-only MC mean $M | P10 | P50 | P90 | P(NPV>0) |",
                   "|---|---|---|---|---|---|---|"]
    for prov in ("QC", "BC", "AB", "ON"):
        carbon, desc = regime_paths(prov)
        notes.append(desc)
        gm = np.exp(rng.normal(0, 0.30, n) - 0.045)
        em = np.exp(rng.normal(0, 0.15, n) - 0.01125)
        cm = rng.triangular(0.9, 1.0, 1.3, n)
        elig = rng.random(n) < 0.6
        vals = np.empty(n)
        for i in range(n):
            cx = Context(prov=prov, custom_carbon=carbon[i], gas_mult=gm[i], elec_mult=em[i],
                         capex_mult=cm[i], itc_on=bool(elig[i]), expensing=bool(elig[i]))
            vals[i] = npv(cashflows(HP_IND, cx), 0.08)
        d_head = npv(cashflows(HP_IND, Context(prov=prov, carbon_regime="headline")), 0.08)
        d_mkt = npv(cashflows(HP_IND, Context(prov=prov, carbon_regime="market")), 0.08)
        p10, p50, p90 = np.percentile(vals, [10, 50, 90])
        tab.append(f"| Ex1 heat pump, {prov} covered | {fmt_m(d_head)} | {fmt_m(d_mkt)} | {fmt_m(vals.mean())} | "
                   f"{fmt_m(p10)} | {fmt_m(p50)} | {fmt_m(p90)} | {(vals>0).mean()*100:.0f}% |")
        # policy-only: same regimes, no energy/capex shocks, ITC granted -> isolates policy-regime risk
        carbon_p, _ = regime_paths(prov)
        vp = np.array([npv(cashflows(HP_IND, Context(prov=prov, custom_carbon=carbon_p[i])), 0.08) for i in range(n)])
        q10, q50, q90 = np.percentile(vp, [10, 50, 90])
        policy_only.append(f"| Ex1 heat pump, {prov} covered | {fmt_m(d_mkt)} | {fmt_m(vp.mean())} | {fmt_m(q10)} | "
                           f"{fmt_m(q50)} | {fmt_m(q90)} | {(vp>0).mean()*100:.0f}% |")

    # Example 3 under AB regimes
    carbon, _ = regime_paths("AB")
    cm = rng.triangular(0.9, 1.0, 1.3, n)
    pr_capex, opex, abated, tax = 25e6, 1e6, 50_000, P["tax_rate"]["AB"]
    disc = (1.08) ** -np.arange(1, LIFE + 1)
    esc = 1.02 ** np.arange(0, LIFE)
    base_cf = -(opex * esc) * (1 - tax)
    v3 = -pr_capex * cm + (pr_capex * cm) * tax / 1.08 + ((base_cf + abated * carbon * (1 - tax)) * disc).sum(axis=1)
    # with CCfD at $85 to 2040
    ccfd_carbon = np.where((yrs <= 2040)[None, :], np.maximum(85.0, carbon), carbon)
    v3c = -pr_capex * cm + (pr_capex * cm) * tax / 1.08 + ((base_cf + abated * ccfd_carbon * (1 - tax)) * disc).sum(axis=1)
    for label, v in (("Ex3 AB abatement ($25M capex), merchant credits", v3), ("Ex3 AB abatement ($25M capex), with $85 CCfD to 2040", v3c)):
        p10, p50, p90 = np.percentile(v, [10, 50, 90])
        tab.append(f"| {label} | - | - | {fmt_m(v.mean())} | {fmt_m(p10)} | {fmt_m(p50)} | {fmt_m(p90)} | {(v>0).mean()*100:.0f}% |")
    # policy-only Ex3 (capex fixed)
    w3 = -pr_capex + pr_capex * tax / 1.08 + ((base_cf + abated * carbon * (1 - tax)) * disc).sum(axis=1)
    w3c = -pr_capex + pr_capex * tax / 1.08 + ((base_cf + abated * ccfd_carbon * (1 - tax)) * disc).sum(axis=1)
    for label, v in (("Ex3 AB ($25M), merchant credits", w3), ("Ex3 AB ($25M), $85 CCfD to 2040", w3c)):
        q10, q50, q90 = np.percentile(v, [10, 50, 90])
        policy_only.append(f"| {label} | - | {fmt_m(v.mean())} | {fmt_m(q10)} | {fmt_m(q50)} | {fmt_m(q90)} | {(v>0).mean()*100:.0f}% |")
    out += [f"- {d}" for d in notes] + ["", "**Full uncertainty** (policy regimes + energy prices + capex skew (mean 1.067) + ITC eligibility p=0.6):", ""] + tab
    out += ["", "**Policy-regime risk only** (same regimes and credit-price shock; energy prices, capex fixed; ITC granted):", ""] + policy_only
    return "\n".join(out)


# ---------------------------------------------------------------- tornado
def tornado():
    """One-at-a-time swing on Example 1, ON covered facility, market carbon, ITC eligible."""
    base_cx = Context(prov="ON", carbon_regime="market")
    base = npv(cashflows(HP_IND, base_cx), 0.08)
    years = range(START_YEAR, START_YEAR + LIFE)
    tests = {
        "Gas price -30% / +30%": (replace(base_cx, gas_mult=0.7), replace(base_cx, gas_mult=1.3)),
        "Electricity price +20% / -20% (incl. Class A vs B)": (replace(base_cx, elec_mult=1.2), replace(base_cx, elec_mult=0.8)),
        "Carbon: not covered ($0) / headline": (replace(base_cx, carbon_regime="none"), replace(base_cx, carbon_regime="headline")),
        "CT ITC + expensing: denied / granted": (replace(base_cx, itc_on=False, expensing=False), base_cx),
        "Capex +30% / -10%": (replace(base_cx, capex_mult=1.3), replace(base_cx, capex_mult=0.9)),
        "Discount rate 10% / 6%": (replace(base_cx, discount=0.10), replace(base_cx, discount=0.06)),
    }
    rows = []
    for k, (lo, hi) in tests.items():
        a = npv(cashflows(HP_IND, lo), lo.discount)
        b = npv(cashflows(HP_IND, hi), hi.discount)
        rows.append((abs(b - a), k, a, b))
    rows.sort(reverse=True)
    out = ["## Tornado - what moves the NPV most? (Example 1, Ontario, covered facility, market carbon, ITC granted)\n",
           f"Base NPV {fmt_m(base)} $M.\n", "| Driver | Low case NPV $M | High case NPV $M | Swing $M |", "|---|---|---|---|"]
    for sw, k, a, b in rows:
        out.append(f"| {k} | {fmt_m(a)} | {fmt_m(b)} | {sw/1e6:.2f} |")
    return "\n".join(out)


def itc_timing():
    out = ["## ITC timing and phase-down sensitivity (Example 1, QC, ITC eligible)\n",
           "| Assumption | NPV $M |", "|---|---|"]
    for d in (1, 2, 3):
        out.append(f"| ITC received after {d} yr(s) | {fmt_m(npv(cashflows(HP_IND, Context(prov='QC', itc_delay_years=d)), 0.08))} |")
    # labour requirements not met -> 20%
    P["itc"]["ct_rate"]["value"] = 0.20
    out.append(f"| Labour requirements not met (20% rate) | {fmt_m(npv(cashflows(HP_IND, Context(prov='QC')), 0.08))} |")
    P["itc"]["ct_rate"]["value"] = 0.15
    out.append(f"| Available for use in 2034 (15% rate, and outside the pre-2030 expensing window) | "
               f"{fmt_m(npv(cashflows(HP_IND, Context(prov='QC', expensing=False)), 0.08))} |")
    P["itc"]["ct_rate"]["value"] = 0.30
    return "\n".join(out)


if __name__ == "__main__":
    print("# Decision-sensitivity results (generated by decision_sensitivity.py)\n")
    print(f"Parameters: params.yaml (as of {P['meta']['as_of']}). All figures CAD nominal, illustrative.\n")
    s1, _ = example1(); print(s1, "\n")
    s2, _ = example2(); print(s2, "\n")
    s3, _ = example3(); print(s3, "\n")
    print(tornado(), "\n")
    print(itc_timing(), "\n")
    print(monte_carlo())
