"""Tax measures: clean-economy ITCs and CCA schedules (plan §4.2)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pv.carbon import step_lookup
from pv.case import Case
from pv.ledger import LedgerError, LedgerView
from pv.registry import registry

F = NDArray[np.float64]

VALIDATION_DB_RATE = 0.20  # validation_v1: Class-8-like declining balance when clean-tech ineligible


def eligibility_probability(eligibility: str) -> float | None:
    """Plan §4.4 Bernoulli p for an eligibility confidence level (registry assumption)."""
    return registry().assumptions.itc_eligibility_probability.get(eligibility)


def _expensing_table(view: LedgerView) -> dict[str, object]:
    cca = registry().tax.cca
    if view.has(cca.expensing_classes):
        return dict(view.get(cca.expensing_classes).table())
    return {c: "eligible" for c in cca.expensing_classes_fallback}


def _fixed_fraction(v: object) -> float | None:
    """A numeric class entry is a first-year fraction that holds for the whole enhanced window."""
    return float(v) if isinstance(v, int | float) and not isinstance(v, bool) and v > 0 else None


def expensing_classes(view: LedgerView) -> frozenset[str]:
    """CCA classes eligible for the enhanced first-year deduction (ledger), or the registry fallback for
    older ledgers. An entry is `eligible` (follows fed.cca.expensing) or a fixed first-year fraction."""
    return frozenset(k for k, v in _expensing_table(view).items() if _truthy(v) or _fixed_fraction(v))


def expensing_fraction(view: LedgerView, cls: str, year: int) -> float:
    """Enhanced first-year deduction as a fraction of UCC for `cls` available for use in `year` (0 = none).

    The fed.cca.expensing series sets the window and the phased fraction; a class whose entry is a number
    keeps that fraction for every year in which the series is positive (Reg. 1100(2) A.1(f)(i): Class 53)."""
    ids = registry().tax.cca
    if not view.has(ids.expensing) or cls not in expensing_classes(view):
        return 0.0
    sched = view.get(ids.expensing).series()
    got = sched.get(year)
    if got is None:
        if year < min(sched) or year > max(sched):
            return 0.0
        raise LedgerError(
            f"{ids.expensing} has no value for available-for-use year {year}; "
            "supply it via overrides[] with a reason"
        )
    fixed = _fixed_fraction(_expensing_table(view)[cls])
    return fixed if fixed is not None and got > 0 else got


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
    rid = registry().tax.itc.get(case.project.itc_measure)
    if rid is None or rid.eligibility is None:
        return "n/a"
    if not view.has(rid.eligibility):
        return "case_by_case"
    table = view.get(rid.eligibility).table()
    return str(table.get(case.project.technology_class, "not_listed"))


def tax_rate(case: Case, view: LedgerView) -> float:
    if case.finance.tax_rate is not None:
        return case.finance.tax_rate
    rec = view.get(registry().tax.corporate_rate)
    return rec.num(case.facility.province)


def itc_rate(case: Case, view: LedgerView) -> tuple[float, list[str]]:
    """ρ for the measure, in-service year and labour flag; 0 if the entity is ineligible."""
    notes: list[str] = []
    measure = case.project.itc_measure
    if measure == "none":
        return 0.0, notes
    y = case.project.in_service.year
    ids = registry().tax.itc[measure]
    if ids.entities is not None:
        entities = view.get(ids.entities).table()
        if not _truthy(entities.get(case.facility.entity, False)):
            notes.append(f"{measure.upper()} ITC: entity type {case.facility.entity} is not eligible")
            return 0.0, notes
    if measure == "ct":
        sched = view.get(ids.rate).series()
        rho = step_lookup(sched, y) or 0.0
        if ids.labour_rate is not None and not case.facility.labour_requirements_met and rho > 0:
            lab = view.get(ids.labour_rate)
            if lab.effective_to is not None and y > lab.effective_to.year:
                raise LedgerError(
                    f"{ids.labour_rate} has no rate for {y}; supply it via overrides[] with a reason"
                )
            rho = min(rho, lab.num())
            notes.append(f"labour requirements not met: CT ITC rate reduced to {rho:.0%}")
        return rho, notes
    rec = view.get(ids.rate)  # CE / CCUS: user override required if not in the ledger
    unchecked = [
        x
        for x, rid in (("qualifying-entity status", ids.entities), ("labour rule", ids.labour_rate))
        if not rid
    ]
    if unchecked:
        notes.append(
            f"{measure.upper()} ITC: {' and '.join(unchecked)} not checked by the kernel; "
            "confirm with a tax advisor"
        )
    if not rec.overridden and (
        y < rec.effective_from.year or (rec.effective_to is not None and y > rec.effective_to.year)
    ):
        window = f"{rec.effective_from}..{rec.effective_to or 'open'}"
        notes.append(f"{measure.upper()} ITC: in-service year {y} is outside {ids.rate} ({window}); rate 0")
        return 0.0, notes
    if isinstance(rec.value, dict):
        table = rec.table()
        key = case.project.itc_rate_key or ("rate" if "rate" in table else None)
        if key is None or key not in table:
            raise LedgerError(
                f"{ids.rate} holds several rates; set project.itc_rate_key to one of: "
                + ", ".join(sorted(table))
            )
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
    """CCA claims for t = 0..n (index 0 unused).

    Enhanced first-year deduction (ledger window and fraction): year 1 claims exactly that fraction of UCC
    (Reg. 1100(2) A.1 already includes the year's normal allowance, and no half-year rule applies); the
    remainder follows declining balance from year 2. Otherwise declining balance with the half-year rule."""
    out = np.zeros(n + 1)
    cls = case.project.cca_class if granted else case.project.cca_class_if_ineligible
    y = case.project.in_service.year
    if case.conventions == "validation_v1" and not granted:
        rate = VALIDATION_DB_RATE
        pct = 0.0
    else:
        ids = registry().tax.cca
        pct = expensing_fraction(view, cls, y) if expensing_allowed else 0.0
        rates = view.get(ids.class_rates).table() if case.conventions != "validation_v1" else {}
        if case.conventions == "validation_v1":
            rate = VALIDATION_DB_RATE
        else:
            if cls not in rates:
                raise LedgerError(f"CCA class {cls} not in {ids.class_rates}; supply it via overrides[]")
            rate = float(rates[cls])
    first = ucc * pct if pct > 0 else ucc * rate / 2
    bal = ucc
    for i in range(1, n + 1):
        claim = first if i == 1 else bal * rate
        out[i] = claim
        bal -= claim
    return out.astype(np.float64)
