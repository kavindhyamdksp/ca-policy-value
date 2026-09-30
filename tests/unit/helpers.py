from __future__ import annotations

import datetime as dt
from typing import Any

from pv.case import Case
from pv.cashflow import Model, build
from pv.ledger import load_ledger

LEDGER = load_ledger()
AS_OF = dt.date(2026, 10, 15)


def ov(record: str, value: Any) -> dict[str, Any]:
    return {"record": record, "value": value, "reason": "unit-test fixture"}


def case(**kw: Any) -> dict[str, Any]:
    """Minimal standard-convention case; nested dict updates via keyword sections."""
    raw: dict[str, Any] = {
        "case_id": "unit",
        "as_of": AS_OF.isoformat(),
        "min_legal_status": "enacted",
        "facility": {"province": "AB", "system": "tier", "covered": True},
        "project": {
            "in_service": "2026-12-31",
            "life_years": 3,
            "capex": [{"year": 0, "amount": 1_000_000}],
            "technology_class": "heat_pump_air_source",
            "covered_emissions_delta_t": -1_000,
        },
        "prices": {"escalation": 0.0, "inflation": 0.0},
        "finance": {"discount_rate": 0.10, "tax_rate": 0.25},
        "policy": {"grid_factor": "marginal", "marginal_grid_ef_g_kwh": 400},
        "overrides": [],
    }
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(raw.get(k), dict):
            raw[k] = {**raw[k], **v}
        else:
            raw[k] = v
    return raw


def model(raw: dict[str, Any]) -> tuple[Model, Case]:
    c = Case.model_validate(raw)
    return build(c, LEDGER.view(c.as_of, c.min_legal_status, c.overrides)), c
