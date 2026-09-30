"""Decision drift: re-run saved cases against two ledger versions (SPEC FR-5)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from pv.case import Case, load_case
from pv.ledger import Ledger, LedgerError, Record
from pv.results import evaluate


def _key(r: Record) -> tuple[str, str, str]:
    return (r.id, r.legal_status, r.effective_from.isoformat())


def _brief(r: Record) -> dict[str, Any]:
    return {"value": r.value, "legal_status": r.legal_status, "effective_from": r.effective_from.isoformat()}


def diff_ledgers(a: Ledger, b: Ledger) -> list[dict[str, Any]]:
    """Per record id: added, removed or changed (value, legal status or effective dates)."""
    ids = sorted({r.id for r in a.records} | {r.id for r in b.records})
    out: list[dict[str, Any]] = []
    for rid in ids:
        ra = sorted((r for r in a.records if r.id == rid), key=_key)
        rb = sorted((r for r in b.records if r.id == rid), key=_key)
        before = [_brief(r) for r in ra]
        after = [_brief(r) for r in rb]
        if before == after:
            continue
        change = "added" if not ra else "removed" if not rb else "changed"
        out.append({"id": rid, "change": change, "before": before, "after": after})
    return out


def _latest_recording(led: Ledger) -> dt.date:
    return max((r.recorded_at for r in led.records), default=dt.date(1900, 1, 1))


def rerun(case: Case, led: Ledger) -> dict[str, Any]:
    """Evaluate a saved case against a ledger.

    View date: the later of the case as_of and the ledger's last recording, so new records are visible.
    """
    as_of = max(case.as_of, _latest_recording(led))
    c = case.model_copy(update={"as_of": as_of})
    try:
        res, _, _ = evaluate(c, led)
    except (LedgerError, ValueError) as ex:
        return {"error": str(ex).splitlines()[0]}
    return {
        "answer": res["decision"]["answer"],
        "base_case": res["decision"]["base_case"],
        "npv": res["metrics"]["npv"],
        "as_of": as_of.isoformat(),
        "records": sorted({p["id"] for p in res["provenance"]}),
    }


def drift(case_paths: list[Path], a: Ledger, b: Ledger) -> dict[str, Any]:
    changes = diff_ledgers(a, b)
    changed_ids = {c["id"] for c in changes}
    cases = []
    for p in case_paths:
        case = load_case(p)
        ra, rb = rerun(case, a), rerun(case, b)
        flipped = (
            "answer" in ra
            and "answer" in rb
            and (ra["answer"] != rb["answer"] or ra["base_case"] != rb["base_case"])
        )
        used = set(ra.get("records", [])) | set(rb.get("records", []))
        cases.append(
            {
                "case_id": case.case_id,
                "file": str(p),
                "before": {k: v for k, v in ra.items() if k != "records"},
                "after": {k: v for k, v in rb.items() if k != "records"},
                "npv_delta": round(rb["npv"] - ra["npv"], 2) if "npv" in ra and "npv" in rb else None,
                "flipped": flipped,
                "changed_records_used": sorted(used & changed_ids),
            }
        )
    return {
        "from": a.version,
        "to": b.version,
        "record_changes": changes,
        "cases": cases,
        "flips": [c["case_id"] for c in cases if c["flipped"]],
    }


def render(d: dict[str, Any]) -> str:
    lines = [
        f"# Ledger drift: {d['from']} → {d['to']}",
        "",
        f"## Record changes ({len(d['record_changes'])})",
        "",
    ]
    for c in d["record_changes"]:
        b = "; ".join(f"{x['legal_status']} {x['value']}" for x in c["before"]) or "—"
        a = "; ".join(f"{x['legal_status']} {x['value']}" for x in c["after"]) or "—"
        lines.append(f"- `{c['id']}` {c['change']}: {b} → {a}")
    lines += [
        "",
        "## Saved cases",
        "",
        "| Case | Before | After | ΔNPV $ | Flipped | Changed records used |",
        "|---|---|---|---:|---|---|",
    ]
    for c in d["cases"]:
        delta = "" if c["npv_delta"] is None else f"{c['npv_delta']:+,.0f}"
        lines.append(
            f"| {c['case_id']} | {_cell(c['before'])} | {_cell(c['after'])} | {delta} | "
            f"{'**FLIP**' if c['flipped'] else 'no'} | {', '.join(c['changed_records_used']) or '—'} |"
        )
    lines += ["", f"Flipped decisions: {', '.join(d['flips']) or 'none'}"]
    return "\n".join(lines) + "\n"


def _cell(x: dict[str, Any]) -> str:
    if "error" in x:
        return f"error: {x['error']}"
    return f"{x['answer']}, base {x['base_case']} ({float(x['npv']):,.0f})"
