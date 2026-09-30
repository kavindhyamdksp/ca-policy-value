"""Kernel wiring: which ledger record supplies each model role (registry.yaml).

Keeps policy-specific structure out of the calculation modules: `carbon`, `tax`, `emissions` and
`cashflow` read record ids and model assumptions from here, and values from the ledger.
"""

from __future__ import annotations

from functools import cache
from importlib import resources
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, field_validator


class _M(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OutputBased(_M):
    method: Literal["flat", "ratio"]  # flat: latest obs held flat real; ratio: obs / compliance price
    obs: str  # credit-price observation record
    price: str  # fund / compliance price series (cap on realized value)
    floor: str | None = None


class CapAndTrade(_M):
    system: str
    obs: str  # latest auction settlement (+ reserve for the low band)
    escalation: str  # reserve-price escalation rule


class Carbon(_M):
    headline: str
    output_based: dict[str, OutputBased]
    cap_and_trade: dict[str, CapAndTrade]


class Itc(_M):
    rate: str
    labour_rate: str | None = None
    entities: str | None = None
    eligibility: str | None = None


class Cca(_M):
    expensing: str
    expensing_classes: str
    class_rates: str
    expensing_classes_fallback: tuple[str, ...]


class Tax(_M):
    corporate_rate: str
    itc: dict[str, Itc]
    cca: Cca


class EmissionsIds(_M):
    gas_ef: str
    grid_ef: str


class PriceIds(_M):
    gas_reference: str
    electricity_reference: str


class Assumptions(_M):
    itc_eligibility_probability: dict[str, float]

    @field_validator("itc_eligibility_probability")
    @classmethod
    def _levels(cls, v: dict[str, float]) -> dict[str, float]:
        if set(v) != {"likely", "case_by_case", "not_listed"} or not all(0 <= p <= 1 for p in v.values()):
            raise ValueError(
                "itc_eligibility_probability needs p in [0, 1] for likely/case_by_case/not_listed"
            )
        return v


class Registry(_M):
    version: int
    carbon: Carbon
    tax: Tax
    emissions: EmissionsIds
    prices: PriceIds
    assumptions: Assumptions

    def systems(self) -> set[str]:
        """Every system a case may name (output-based, cap-and-trade, or none)."""
        return {*self.carbon.output_based, *(c.system for c in self.carbon.cap_and_trade.values()), "none"}

    def record_ids(self) -> set[str]:
        """Every ledger record id the registry wires into the kernel."""
        ids: set[str] = {self.carbon.headline, self.tax.corporate_rate}
        for s in self.carbon.output_based.values():
            ids |= {s.obs, s.price} | ({s.floor} if s.floor else set())
        for c in self.carbon.cap_and_trade.values():
            ids |= {c.obs, c.escalation}
        for i in self.tax.itc.values():
            ids |= {x for x in (i.rate, i.labour_rate, i.entities, i.eligibility) if x}
        cca = self.tax.cca
        ids |= {cca.expensing, cca.expensing_classes, cca.class_rates}
        ids |= {self.emissions.gas_ef, self.emissions.grid_ef}
        ids |= {self.prices.gas_reference, self.prices.electricity_reference}
        return ids


@cache
def registry() -> Registry:
    raw = yaml.safe_load((resources.files("pv") / "registry.yaml").read_text())
    return Registry.model_validate(raw)
