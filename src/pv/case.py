"""Typed project case (plan §2.3). YAML → pydantic `Case`."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from pv.ledger import MinStatus, Override

Province = Literal["AB", "ON", "BC", "QC"]
System = Literal["tier", "eps", "bc_obps", "fed_obps", "spede", "none"]
Scenario = Literal["low", "base", "high", "upper_bound_headline"]
FloorMode = Literal["auto", "as_announced", "half", "none"]
GridDim = Literal["floor_status", "itc_granted", "ccfd", "coverage", "credit_scenario"]


class _M(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Facility(_M):
    province: Province
    system: System = "none"
    covered: bool = False
    entity: Literal["taxable_corp", "reit", "crown", "municipal", "tax_exempt"] = "taxable_corp"
    labour_requirements_met: bool = True
    tax_capacity: Literal["full", "none"] = "full"

    @field_validator("province", mode="before")
    @classmethod
    def _bare_on(cls, v: object) -> object:
        if v is True:
            raise ValueError('province parsed as boolean — quote it: province: "ON"')
        return v

    @property
    def taxable(self) -> bool:
        return self.entity in ("taxable_corp", "reit") and self.tax_capacity == "full"


class CapexItem(_M):
    year: int = Field(ge=0)
    amount: float


class EnergyDeltas(_M):
    natural_gas_gj: float = 0.0  # negative = gas avoided
    electricity_mwh: float = 0.0  # positive = electricity added


class Project(_M):
    in_service: dt.date
    life_years: int = Field(ge=1, le=60)
    capex: tuple[CapexItem, ...] = Field(min_length=1)
    technology_class: str
    itc_measure: Literal["ct", "ccus", "ce", "none"] = "ct"
    itc_eligible_share: float | None = Field(default=None, ge=0, le=1)
    cca_class: str = "43.1"
    cca_class_if_ineligible: str = "8"
    other_assistance: float = Field(default=0.0, ge=0)
    energy_deltas: EnergyDeltas = EnergyDeltas()
    opex_delta: float = 0.0  # $/yr, + = cost, escalates
    covered_emissions_delta_t: float | None = None  # t/yr, negative = abatement

    @property
    def capex_total(self) -> float:
        return sum(c.amount for c in self.capex)


class Prices(_M):
    natural_gas_gj: float | None = None
    electricity_mwh: float | None = None
    escalation: float = 0.02
    inflation: float | None = None  # for flat-real credit prices; defaults to escalation


class Finance(_M):
    discount_rate: float = Field(default=0.08, gt=-0.99)
    itc_receipt_lag_years: int = Field(default=1, ge=0)
    tax_rate: float | None = Field(default=None, ge=0, lt=1)


class Ccfd(_M):
    strike: float = Field(ge=0)
    term_end: int
    volume_share: float = Field(default=1.0, ge=0, le=1)


class Policy(_M):
    credit_price_scenario: Scenario = "base"
    floor: FloorMode = "auto"
    itc_granted: bool | None = None  # None: granted unless the class is not_listed
    ccfd: Ccfd | None = None
    grid_factor: Literal["average", "marginal"] = "average"
    marginal_grid_ef_g_kwh: float | None = None


class Regime(_M):
    p: float = Field(ge=0, le=1)
    market_scale: float = 1.0
    market_value: float | None = None
    floor_scale: float | None = None  # scale on the announced floor; None = base-case floor treatment
    from_year: int | None = None  # regime changes apply for y >= from_year (default: all years)


class Shocks(_M):
    gas_sigma: float = 0.0
    elec_sigma: float = 0.0
    credit_sigma: float = 0.0
    capex_triangular: tuple[float, float, float] = (1.0, 1.0, 1.0)


class MonteCarlo(_M):
    draws: int = Field(default=10_000, ge=1, le=1_000_000)
    seed: int = 20260929
    regimes: dict[str, Regime] = {"base": Regime(p=1.0)}
    shocks: Shocks = Shocks()
    itc_probability: float | None = Field(default=None, ge=0, le=1)  # default: from eligibility map

    @model_validator(mode="after")
    def _probs(self) -> MonteCarlo:
        total = sum(r.p for r in self.regimes.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"regime probabilities sum to {total}, not 1")
        return self


class Robustness(_M):
    grid: tuple[GridDim, ...] = ()
    monte_carlo: MonteCarlo | None = None


class Case(_M):
    case_id: str
    as_of: dt.date
    min_legal_status: MinStatus = "enacted"
    conventions: Literal["standard", "validation_v1"] = "standard"
    facility: Facility
    project: Project
    prices: Prices = Prices()
    finance: Finance = Finance()
    policy: Policy = Policy()
    robustness: Robustness = Robustness()
    overrides: tuple[Override, ...] = ()

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()

    @property
    def carbon_kind(self) -> Literal["none", "qc", "covered"]:
        if self.facility.province == "QC":
            return "qc"
        if self.facility.covered and self.facility.system != "none":
            return "covered"
        return "none"


def load_case(path: str | Path) -> Case:
    raw = yaml.safe_load(Path(path).read_text())
    return Case.model_validate(raw)
