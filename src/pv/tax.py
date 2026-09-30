"""Tax measures: clean-economy ITCs and CCA schedules (plan §4.2)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pv.carbon import step_lookup
from pv.case import Case
from pv.ledger import LedgerError, LedgerView

F = NDArray[np.float64]

ELIGIBILITY_P = {"likely": 0.9, "case_by_case": 0.6, "not_listed": 0.1}
# Classes named for immediate expensing in fed.cca.expensing sources (EY on Bill C-15); 43.2 is not named.
EXPENSING_CLASSES = frozenset({"43.1", "53"})
VALIDATION_DB_RATE = 0.20  # validation_v1: Class-8-like declining balance when clean-tech ineligible

ITC_RECORDS = {"ct": "fed.ct_itc.rate_schedule", "ce": "fed.ce_itc.rate", "ccus": "fed.ccus_itc.rates"}


@dataclass(frozen=True)
class TaxInputs:
    rate: float  # combined corporate rate τ
    rho: float  # ρ if the claim is granted (0 if the entity/measure is ineligible)
    itc_share: float
    eligibility: str  # likely | case_by_case | not_listed | n/a
    granted: bool
    notes: tuple[str, ...] = ()

    @property
    def itc_rate(self) -> float:
        """Effective base-case rate (0 when the claim is not granted)."""
        return self.rho if self.granted else 0.0


def _truthy(v: object) -> bool:
    return v is True or (isinstance(v, str) and v.lower() in ("yes", "true", "eligible"))


def eligibility(case: Case, view: LedgerView) -> str:
    if case.project.itc_measure != "ct":
        return "n/a"
    if not view.has("fed.ct_itc.eligibility_classes"):
        return "case_by_case"
    table = view.get("fed.ct_itc.eligibility_classes").table()
    return str(table.get(case.project.technology_class, "not_listed"))


def tax_rate(case: Case, view: LedgerView) -> float:
    if case.finance.tax_rate is not None:
        return case.finance.tax_rate
    rec = view.get("ref.tax.corporate")
    return rec.num(case.facility.province)


def itc_rate(case: Case, view: LedgerView) -> tuple[float, list[str]]:
    """ρ for the measure, in-service year and labour flag; 0 if the entity is ineligible."""
    notes: list[str] = []
    measure = case.project.itc_measure
    if measure == "none":
        return 0.0, notes
    y = case.project.in_service.year
    if measure == "ct":
        entities = view.get("fed.ct_itc.entities").table()
        if not _truthy(entities.get(case.facility.entity, False)):
            notes.append(f"CT ITC: entity type {case.facility.entity} is not eligible")
            return 0.0, notes
        sched = view.get("fed.ct_itc.rate_schedule").series()
        rho = step_lookup(sched, y) or 0.0
        if not case.facility.labour_requirements_met and rho > 0:
            lab = view.get("fed.ct_itc.labour_rate")
            if lab.effective_to is not None and y > lab.effective_to.year:
                raise LedgerError(
                    f"fed.ct_itc.labour_rate has no rate for {y}; supply it via overrides[] with a reason"
                )
            rho = min(rho, lab.num())
            notes.append(f"labour requirements not met: CT ITC rate reduced to {rho:.0%}")
        return rho, notes
    rec = view.get(ITC_RECORDS[measure])  # CE / CCUS: user override required if not in the ledger
    if isinstance(rec.value, dict):
        key = "rate" if "rate" in rec.table() else next(iter(rec.table()))
        return rec.num(key), notes
    return rec.num(), notes


def resolve(case: Case, view: LedgerView, granted_override: bool | None = None) -> TaxInputs:
    elig = eligibility(case, view)
    granted = granted_override
    if granted is None:
        granted = case.policy.itc_granted if case.policy.itc_granted is not None else elig != "not_listed"
    rho, notes = itc_rate(case, view)
    if case.project.itc_measure == "ct" and elig == "case_by_case" and granted:
        notes.append("CT ITC eligibility for this technology class is case-by-case (NRCan guidance)")
    share = case.project.itc_eligible_share if case.project.itc_eligible_share is not None else 1.0
    return TaxInputs(
        rate=tax_rate(case, view) if case.facility.taxable else 0.0,
        rho=rho,
        itc_share=share,
        eligibility=elig,
        granted=granted,
        notes=tuple(notes),
    )


def itc_amount(case: Case, ti: TaxInputs, capex: float) -> float:
    """ITC if granted: ρ · s_elig · (capex − assistance)."""
    base = max(capex - case.project.other_assistance, 0.0)
    return ti.rho * ti.itc_share * base


def cca_schedule(
    case: Case, view: LedgerView, ucc: float, granted: bool, n: int, *, expensing_allowed: bool = True
) -> F:
    """CCA claims for t = 0..n (index 0 unused). Expensing window per the ledger, else half-year DB."""
    out = np.zeros(n + 1)
    cls = case.project.cca_class if granted else case.project.cca_class_if_ineligible
    y = case.project.in_service.year
    if case.conventions == "validation_v1" and not granted:
        rate = VALIDATION_DB_RATE
        pct = 0.0
    else:
        pct = 0.0
        if expensing_allowed and cls in EXPENSING_CLASSES and view.has("fed.cca.expensing"):
            sched = view.get("fed.cca.expensing").series()
            got = sched.get(y)
            if got is None:
                if y < min(sched) or y > max(sched):
                    got = 0.0
                else:
                    raise LedgerError(
                        f"fed.cca.expensing has no value for available-for-use year {y} (phase-out "
                        "unverified); supply it via overrides[] with a reason"
                    )
            pct = got
        rates = view.get("fed.cca.class_rates").table() if case.conventions != "validation_v1" else {}
        if case.conventions == "validation_v1":
            rate = VALIDATION_DB_RATE
        else:
            if cls not in rates:
                raise LedgerError(f"CCA class {cls} not in fed.cca.class_rates; supply it via overrides[]")
            rate = float(rates[cls])
    first = ucc * pct
    bal = ucc - first
    for i in range(1, n + 1):
        claim = bal * (rate / 2 if i == 1 else rate)
        out[i] = claim + (first if i == 1 else 0.0)
        bal -= claim
    return out.astype(np.float64)
