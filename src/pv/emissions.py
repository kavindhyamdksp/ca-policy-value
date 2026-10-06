"""On-site and grid emissions (plan §4.5)."""

from __future__ import annotations

from dataclasses import dataclass

from pv.case import Case
from pv.ledger import LedgerError, LedgerView
from pv.registry import registry


def gas_ef(case: Case, view: LedgerView) -> float:
    """t CO2e per GJ of natural gas (province-specific if the record is a table)."""
    rec = view.get(registry().emissions.gas_ef)
    return rec.num(case.facility.province) if isinstance(rec.value, dict) else rec.num()


def grid_ef_g_kwh(case: Case, view: LedgerView) -> tuple[float, str]:
    if case.policy.grid_factor == "marginal":
        if case.policy.marginal_grid_ef_g_kwh is None:
            raise LedgerError("grid_factor=marginal requires policy.marginal_grid_ef_g_kwh")
        return case.policy.marginal_grid_ef_g_kwh, "marginal (user input)"
    rec = view.get(registry().emissions.grid_ef)
    v = rec.num(case.facility.province) if isinstance(rec.value, dict) else rec.num()
    return v, "average (overridden)" if rec.overridden else "average (ledger)"


@dataclass(frozen=True)
class Emissions:
    onsite_t_yr: float  # avoided on-site (covered) tonnes per year, + = reduction
    grid_t_yr: float  # added grid tonnes per year
    grid_basis: str
    grid_ef_g_kwh: float
    life_years: int

    @property
    def net_t_yr(self) -> float:
        return self.onsite_t_yr - self.grid_t_yr

    def as_dict(self, disc_sum: float, npv: float) -> dict[str, object]:
        def cost(t: float) -> float | None:
            dt_ = t * disc_sum
            return round(-npv / dt_, 2) if dt_ > 0 else None

        return {
            "onsite_avoided_t_per_yr": round(self.onsite_t_yr, 1),
            "grid_added_t_per_yr": round(self.grid_t_yr, 1),
            "net_avoided_t_per_yr": round(self.net_t_yr, 1),
            "net_share_of_onsite": round(self.net_t_yr / self.onsite_t_yr, 4) if self.onsite_t_yr else None,
            "lifetime_onsite_t": round(self.onsite_t_yr * self.life_years, 0),
            "lifetime_net_t": round(self.net_t_yr * self.life_years, 0),
            "grid_basis": self.grid_basis,
            "grid_ef_g_kwh": self.grid_ef_g_kwh,
            "abatement_cost_onsite_per_t": cost(self.onsite_t_yr),
            "abatement_cost_net_per_t": cost(self.net_t_yr),
        }


def compute(case: Case, view: LedgerView) -> Emissions:
    p = case.project
    if p.covered_emissions_delta_t is not None:
        onsite = -p.covered_emissions_delta_t
    elif p.energy_deltas.natural_gas_gj:
        onsite = -p.energy_deltas.natural_gas_gj * gas_ef(case, view)
    else:
        onsite = 0.0
    mwh = p.energy_deltas.electricity_mwh
    if mwh:
        ef, basis = grid_ef_g_kwh(case, view)
    else:
        ef, basis = 0.0, "no electricity change"
    return Emissions(onsite, mwh * ef / 1000.0, basis, ef, p.life_years)
