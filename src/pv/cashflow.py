"""After-tax cash flows, NPV/IRR/payback and the policy value stack (plan §4.3)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq

from pv import carbon, emissions, tax
from pv.case import Case, Ccfd, Scenario
from pv.ledger import LedgerError, LedgerView

F = NDArray[np.float64]


def npv(cf: F, r: float) -> float:
    return float(np.sum(cf * (1 + r) ** -np.arange(len(cf), dtype=float)))


def irr(cf: F) -> tuple[float | None, str | None]:
    """IRR via brentq on [-0.99, 3]; None (with a reason) when it does not exist or is not unique."""
    nz = cf[cf != 0]
    changes = int(np.sum(np.sign(nz[1:]) != np.sign(nz[:-1])))
    if changes == 0:
        return None, "no sign change in cash flows"
    grid = np.linspace(-0.99, 3.0, 800)
    vals = np.array([npv(cf, g) for g in grid])
    roots = int(np.sum(np.sign(vals[1:]) != np.sign(vals[:-1])))
    if roots == 0:
        return None, "no IRR in [-99%, 300%]"
    if roots > 1:
        return None, "multiple IRRs (non-conventional cash flows)"
    i = int(np.argmax(np.sign(vals[1:]) != np.sign(vals[:-1])))
    return float(brentq(lambda x: npv(cf, x), grid[i], grid[i + 1], xtol=1e-12)), None


def payback(cf: F, r: float | None = None) -> float | None:
    """Simple (r=None) or discounted payback in years, interpolated within the crossing year."""
    flows = cf if r is None else cf * (1 + r) ** -np.arange(len(cf), dtype=float)
    cum = np.cumsum(flows)
    for i in range(1, len(cum)):
        if cum[i] >= 0:
            return float(i - 1 + (-cum[i - 1]) / flows[i])
    return None


@dataclass
class Model:
    """Numeric inputs resolved once from case + ledger; evaluation is pure and vectorizable."""

    case: Case
    years: NDArray[np.int64]
    rate: float
    tau: float
    esc: F
    gas_saving: F  # $/yr before escalation mult
    elec_cost: F
    opex: F
    tonnes: float  # covered tonnes avoided per year
    capex_by_year: F  # length n+1
    capex_total: float
    ti: tax.TaxInputs
    ci: carbon.CarbonInputs
    em: emissions.Emissions
    lag: int
    warnings: list[str] = field(default_factory=list)
    _view: LedgerView | None = None

    @property
    def n(self) -> int:
        return len(self.years)

    @property
    def disc(self) -> F:
        return (1 + self.rate) ** -np.arange(self.n + 1, dtype=float)

    def cca(self, granted: bool, itc: float, expensing: bool = True) -> F:
        assert self._view is not None
        ucc = max(self.capex_total - itc - self.case.project.other_assistance, 0.0)
        return tax.cca_schedule(self.case, self._view, ucc, granted, self.n, expensing_allowed=expensing)

    def itc(self, granted: bool) -> float:
        if not granted:
            return 0.0
        return tax.itc_amount(self.case, self.ti, self.capex_total)

    def cashflows(
        self,
        carbon_path: F,
        *,
        granted: bool,
        itc_on: bool | None = None,
        eligible_cca: bool | None = None,
    ) -> F:
        """Deterministic cash flows CF_0..CF_N. itc_on/eligible_cca split the value stack steps."""
        itc_on = granted if itc_on is None else itc_on
        eligible_cca = granted if eligible_cca is None else eligible_cca
        itc = self.itc(granted) if itc_on else 0.0
        cca = self.cca(eligible_cca, itc)
        pretax = self.gas_saving + self.tonnes * carbon_path - self.elec_cost - self.opex
        cf = -self.capex_by_year.copy()
        taxable = self.case.facility.taxable
        cf[1:] += pretax * (1 - self.tau) + (cca[1:] * self.tau if taxable else 0.0)
        cf[min(self.lag, self.n)] += itc
        return cf.astype(np.float64)

    def npv_of(self, carbon_path: F, granted: bool) -> float:
        return npv(self.cashflows(carbon_path, granted=granted), self.rate)

    def path(self, scenario: Scenario, floor_mode: str = "auto", ccfd: Ccfd | None = None) -> F:
        return carbon.realized(self.ci, scenario, floor_mode=floor_mode, ccfd=ccfd)

    def breakeven(self, granted: bool) -> float | None:
        """Flat nominal $/t with NPV = 0 (NPV is linear in a flat carbon price)."""
        ones = np.ones(self.n)
        v0 = self.npv_of(0 * ones, granted)
        v1 = self.npv_of(ones, granted)
        slope = v1 - v0
        if abs(slope) < 1e-9:
            return None
        return -v0 / slope

    def value_stack(self, scenario: Scenario, floor_mode: str, ccfd: Ccfd | None) -> list[dict[str, object]]:
        g = self.ti.granted
        zero = np.zeros(self.n)
        no_ccfd = self.path(scenario, floor_mode)
        full = self.path(scenario, floor_mode, ccfd)
        steps = [
            ("Base (no policy)", zero, False, False),
            ("+ carbon value", no_ccfd, False, False),
            ("+ ITC", no_ccfd, g, False),
            ("+ CCA timing (expensing / class)", no_ccfd, g, g),
            ("+ CCfD", full, g, g),
        ]
        out: list[dict[str, object]] = []
        prev = 0.0
        for i, (label, path, itc_on, ecca) in enumerate(steps):
            v = npv(self.cashflows(path, granted=g, itc_on=itc_on, eligible_cca=ecca), self.rate)
            out.append({"step": label, "npv": v, "delta": v if i == 0 else v - prev})
            prev = v
        return out


def _price(case: Case, view: LedgerView, carrier: str) -> float:
    p = case.prices
    if carrier == "gas":
        if p.natural_gas_gj is not None:
            return p.natural_gas_gj
        if view.has("ref.gas.delivered"):
            return view.get("ref.gas.delivered").num(case.facility.province)
        raise LedgerError("no delivered gas reference price in the ledger; supply prices.natural_gas_gj")
    if p.electricity_mwh is not None:
        return p.electricity_mwh
    return view.get("ref.electricity.large").num(case.facility.province) * 10.0  # ¢/kWh → $/MWh


def build(case: Case, view: LedgerView) -> Model:
    pr = case.project
    n = pr.life_years
    years = np.arange(pr.in_service.year + 1, pr.in_service.year + 1 + n, dtype=np.int64)
    t = np.arange(1, n + 1, dtype=float)
    esc = (1 + case.prices.escalation) ** (t - 1)
    gas_gj = -pr.energy_deltas.natural_gas_gj
    mwh = pr.energy_deltas.electricity_mwh
    gas_saving = gas_gj * _price(case, view, "gas") * esc if gas_gj else np.zeros(n)
    elec_cost = mwh * _price(case, view, "elec") * esc if mwh else np.zeros(n)
    opex = pr.opex_delta * esc
    capex = np.zeros(n + 1)
    for item in pr.capex:
        if item.year > n:
            raise ValueError(f"capex year {item.year} beyond project life {n}")
        capex[item.year] += item.amount
    em = emissions.compute(case, view)
    ti = tax.resolve(case, view)
    ci = carbon.resolve(case, view, years)
    m = Model(
        case=case,
        years=years,
        rate=case.finance.discount_rate,
        tau=ti.rate,
        esc=esc.astype(np.float64),
        gas_saving=np.asarray(gas_saving, dtype=np.float64),
        elec_cost=np.asarray(elec_cost, dtype=np.float64),
        opex=opex.astype(np.float64),
        tonnes=em.onsite_t_yr,
        capex_by_year=capex.astype(np.float64),
        capex_total=float(capex.sum()),
        ti=ti,
        ci=ci,
        em=em,
        lag=case.finance.itc_receipt_lag_years,
        warnings=[*ci.warnings, *ti.notes],
        _view=view,
    )
    return m
