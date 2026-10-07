"""Ledger publication and maintenance views: static JSON/CSV/HTML export and the freshness review queue.

Everything here is a pure function of the ledger and a date, so exports are reproducible and can be
published as a static site (plan §8 static ledger site, §9 static JSON first).
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import json
from collections.abc import Callable
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from pv import __version__
from pv.ledger import FRESHNESS_SLA_DAYS, PRIMARY, Ledger, Record

EXPORT_SCHEMA = "pv.ledger-export/v1"

_HTML = Environment(
    loader=PackageLoader("pv", "templates"),
    undefined=StrictUndefined,
    autoescape=select_autoescape(["html", "j2"]),
    keep_trailing_newline=True,
)


def _sorted(ledger: Ledger) -> list[Record]:
    return sorted(ledger.records, key=lambda r: (r.id, r.effective_from, r.legal_status))


def days_left(r: Record, as_of: dt.date) -> int:
    """Days before the record breaches its freshness SLA (negative = stale)."""
    return FRESHNESS_SLA_DAYS[r.freshness] - (as_of - r.retrieved).days


def review_queue(ledger: Ledger, as_of: dt.date, within_days: int) -> list[dict[str, Any]]:
    """Entries due for re-verification within `within_days` (stale ones first), with their sources."""
    rows = []
    for r in _sorted(ledger):
        left = days_left(r, as_of)
        if left <= within_days:
            rows.append(
                {
                    "id": r.id,
                    "legal_status": r.legal_status,
                    "effective_from": r.effective_from.isoformat(),
                    "freshness": r.freshness,
                    "retrieved": r.retrieved.isoformat(),
                    "days_left": left,
                    "due": (r.retrieved + dt.timedelta(days=FRESHNESS_SLA_DAYS[r.freshness])).isoformat(),
                    "urls": sorted({s.url for s in r.sources}),
                    "file": r.file,
                }
            )
    rows.sort(key=lambda x: (x["days_left"], x["id"]))
    return rows


def sla_history(ledger_on: Callable[[dt.date], Ledger | None], as_of: dt.date, days: int) -> dict[str, Any]:
    """Freshness SLA over the `days` days ending at `as_of` (gate G1: "freshness SLA met for 60 days").

    `ledger_on(d)` returns the ledger as published on day d (None before the ledger existed). A day is clean
    when no record of that day's ledger is past its SLA on that day. The streak counts consecutive clean days
    ending at `as_of`; the criterion is met when the streak covers the whole window."""
    stale_days: list[dict[str, Any]] = []
    clean: list[bool] = []  # oldest → newest
    missing = 0
    for i in range(days - 1, -1, -1):
        d = as_of - dt.timedelta(days=i)
        led = ledger_on(d)
        if led is None or not led.records:
            missing += 1
            clean.append(False)
            continue
        ids = sorted({r.id for r in led.records if r.is_stale(d)})
        if ids:
            stale_days.append({"date": d.isoformat(), "stale": ids})
        clean.append(not ids)
    streak = clean[::-1].index(False) if False in clean else len(clean)  # clean days ending at as_of
    return {
        "as_of": as_of.isoformat(),
        "window_days": days,
        "streak_days": streak,
        "met": streak >= days,
        "days_without_ledger": missing,
        "stale_days": stale_days,
    }


def _row(r: Record, as_of: dt.date) -> dict[str, Any]:
    d = r.model_dump(mode="json")
    d["file"] = r.file
    d["days_left"] = days_left(r, as_of)
    d["has_primary_source"] = r.has_primary
    return d


def ledger_json(ledger: Ledger, as_of: dt.date) -> str:
    payload = {
        "schema": EXPORT_SCHEMA,
        "engine": f"policyvalue-ca {__version__}",
        "ledger_version": ledger.version,
        "ledger_sha256": ledger.digest,
        "as_of": as_of.isoformat(),
        "licence": "CC BY 4.0 (data), with OGL-Canada attributions — see ledger/LICENSE",
        "records": [_row(r, as_of) for r in _sorted(ledger)],
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


CSV_COLUMNS = (
    "id",
    "jurisdiction",
    "instrument",
    "parameter",
    "legal_status",
    "effective_from",
    "effective_to",
    "value",
    "unit",
    "currency_basis",
    "confidence",
    "freshness",
    "retrieved",
    "days_left",
    "primary_source_url",
    "recorded_at",
)


def ledger_csv(ledger: Ledger, as_of: dt.date) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_COLUMNS)
    for r in _sorted(ledger):
        primary = next((s.url for s in r.sources if s.source_type in PRIMARY), r.sources[0].url)
        w.writerow(
            [
                r.id,
                r.jurisdiction,
                r.instrument,
                r.parameter,
                r.legal_status,
                r.effective_from.isoformat(),
                r.effective_to.isoformat() if r.effective_to else "",
                json.dumps(r.value, sort_keys=True, ensure_ascii=False),
                r.unit,
                r.currency_basis,
                r.confidence,
                r.freshness,
                r.retrieved.isoformat(),
                days_left(r, as_of),
                primary,
                r.recorded_at.isoformat(),
            ]
        )
    return buf.getvalue()


def ledger_html(ledger: Ledger, as_of: dt.date) -> str:
    rows = [_row(r, as_of) for r in _sorted(ledger)]
    return _HTML.get_template("ledger.html.j2").render(
        rows=rows,
        version=ledger.version,
        digest=ledger.digest,
        as_of=as_of.isoformat(),
        engine=__version__,
        n_ids=len(ledger.ids()),
    )
