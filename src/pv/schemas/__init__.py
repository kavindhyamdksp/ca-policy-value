"""Published data contracts: results.json (pv.results/v1), case files, and ledger record files."""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any, Literal

import jsonschema

from pv.case import Case
from pv.ledger import schema as record_schema

SchemaName = Literal["case", "results", "record"]


@cache
def results_schema() -> dict[str, Any]:
    text = (resources.files("pv") / "schemas" / "results.v1.schema.json").read_text()
    loaded: dict[str, Any] = json.loads(text)
    return loaded


def case_schema() -> dict[str, Any]:
    """JSON Schema of a case file, generated from the pydantic model (for editors and other tools)."""
    out = Case.model_json_schema(mode="validation")
    out["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    out["title"] = "PolicyValue CA case"
    return out


def get(name: SchemaName) -> dict[str, Any]:
    if name == "case":
        return case_schema()
    if name == "results":
        return results_schema()
    return record_schema()


def validate_results(res: dict[str, Any]) -> list[str]:
    """Schema errors in a results dict (empty = valid)."""
    v = jsonschema.Draft202012Validator(results_schema())
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:200]}" for e in v.iter_errors(res)]
