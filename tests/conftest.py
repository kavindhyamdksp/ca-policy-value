from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "ledger" / "schema"


def src(kind: str = "primary_gov", retrieved: str = "2026-09-29") -> dict[str, Any]:
    return {
        "url": "https://example.gc.ca/x",
        "title": "t",
        "publisher": "p",
        "published": "2026-01-01",
        "retrieved": retrieved,
        "locator": "s.1",
        "excerpt": "short excerpt",
        "source_type": kind,
    }


def rec(rid: str, value: Any, **kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": rid,
        "jurisdiction": {"fed": "FED", "ab": "AB", "on": "ON", "bc": "BC", "qc": "QC"}.get(
            rid.split(".")[0], "FED"
        ),
        "instrument": "x",
        "parameter": "y",
        "value": value,
        "unit": "CAD/t",
        "currency_basis": "nominal",
        "effective_from": "2026-01-01",
        "effective_to": None,
        "legal_status": "in_force",
        "confidence": "high",
        "freshness": "statute",
        "sources": [src()],
        "recorded_at": "2026-09-29",
    }
    base.update(kw)
    return base


def write_ledger(tmp: Path, records: list[dict[str, Any]], name: str = "a.yaml") -> Path:
    (tmp / "records").mkdir(parents=True, exist_ok=True)
    (tmp / "schema").mkdir(exist_ok=True)
    (tmp / "schema" / "record.schema.json").write_text((SCHEMA / "record.schema.json").read_text())
    (tmp / "records" / name).write_text(yaml.safe_dump({"records": records}, sort_keys=False))
    return tmp


@pytest.fixture
def today() -> dt.date:
    return dt.date(2026, 9, 29)
