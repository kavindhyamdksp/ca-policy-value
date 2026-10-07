"""Summarize anonymized pilot feedback against gate G1 in DECISION.md.

    python tools/pilot_scorecard.py docs/validation/pilots \
        --maintenance-log docs/validation/maintenance_log.csv --freshness-days 60

Each note is `NN-<segment>.md` with a YAML front-matter block (template in docs/validation/pilot_kit.md).
Only the whitelisted fields below are accepted, so personal data (names, employers, facilities) cannot slip
into the structured record. Exit code: 0 = criterion met (or no notes yet with --allow-empty), 1 = not yet,
2 = invalid notes. With --maintenance-log and --freshness-days the other two G1 criteria (maintenance
<= 15 h/month; freshness SLA held for 60 days, read from git history) and the 0.25 FTE stop criterion are
assessed too. The tool counts; the G1 judgement itself stays with the maintainer.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Annotated, Any, Literal

import yaml
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, ValidationError


def _yes_no(v: object) -> object:
    """Bare yes/no in YAML 1.1 parse as booleans; accept them as the words."""
    return {True: "yes", False: "no"}.get(v, v) if isinstance(v, bool) else v


YesNo = Annotated[Literal["yes", "no"], BeforeValidator(_yes_no)]
YesMaybeNo = Annotated[Literal["yes", "maybe", "no"], BeforeValidator(_yes_no)]
NOTE = re.compile(r"^\d{2,3}-[a-z0-9_-]+\.md$")

G1_MIN_PARTNERS = 3  # DECISION.md gate G1
G1_MAX_HOURS_PER_MONTH = 15.0  # DECISION.md gate G1
# DECISION.md stop criterion: "more than 0.25 FTE". Assumes 1 FTE = 1,950 h/yr (37.5 h x 52 weeks).
STOP_HOURS_PER_MONTH = 0.25 * 1950 / 12


class Pilot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    date: dt.date
    segment: Literal["covered_facility", "consultant", "developer", "researcher", "other"]
    province: Literal["AB", "ON", "BC", "QC", "FED", "other"]
    ran_real_case: YesNo
    decision_changed_or_derisked: YesNo
    time_to_first_memo_min: int = Field(ge=0)
    would_use_next: YesMaybeNo
    ledger_corrections: int = Field(default=0, ge=0)


class MaintenanceEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    date: dt.date
    hours: float = Field(gt=0, le=24)
    area: Literal["ledger", "code", "pilots", "docs", "other"]
    note: str = ""


def load_maintenance(path: Path) -> tuple[list[MaintenanceEntry], list[str]]:
    """Maintenance log CSV: date,hours,area,note (one row per session)."""
    entries: list[MaintenanceEntry] = []
    errors: list[str] = []
    with path.open(newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            try:
                entries.append(MaintenanceEntry.model_validate(row))
            except ValidationError as ex:
                errors.append(f"{path.name}:{i}: {str(ex).splitlines()[0]}: {ex.errors()[0]['msg']}")
    return entries, errors


def maintenance(entries: list[MaintenanceEntry]) -> dict[str, Any]:
    """Hours per calendar month against the G1 budget and the 0.25 FTE stop criterion."""
    months: dict[str, float] = {}
    for e in entries:
        key = f"{e.date:%Y-%m}"
        months[key] = round(months.get(key, 0.0) + e.hours, 2)
    return {
        "hours_by_month": dict(sorted(months.items())),
        "within_budget": bool(months) and max(months.values()) <= G1_MAX_HOURS_PER_MONTH,
        "stop_criterion_months": sorted(k for k, v in months.items() if v > STOP_HOURS_PER_MONTH),
    }


def front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: no YAML front matter (--- ... ---)")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: front matter is not a mapping")
    return data


def load(directory: Path) -> tuple[list[Pilot], list[str]]:
    notes: list[Pilot] = []
    errors: list[str] = []
    for p in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        if not NOTE.match(p.name):
            continue  # README and templates
        try:
            notes.append(Pilot.model_validate(front_matter(p)))
        except ValidationError as ex:
            errors.append(f"{p.name}: {ex}")
        except ValueError as ex:
            errors.append(str(ex))
    return notes, errors


def score(
    pilots: list[Pilot],
    maint: dict[str, Any] | None = None,
    freshness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """G1 checks. Criteria without evidence (maint/freshness None) are listed as not assessed."""
    real = [p for p in pilots if p.ran_real_case == "yes"]
    changed = [p.id for p in real if p.decision_changed_or_derisked == "yes"]
    times = sorted(p.time_to_first_memo_min for p in pilots)
    met = len(changed) >= G1_MIN_PARTNERS
    checks = {f">= {G1_MIN_PARTNERS} pilots ran a real case and the memo changed or de-risked it": met}
    not_assessed = []
    if freshness is None:
        not_assessed.append("ledger freshness SLA met for 60 days")
    else:
        checks[f"ledger freshness SLA met for {freshness['window_days']} days"] = bool(freshness["met"])
    if maint is None:
        not_assessed.append(f"maintenance <= {G1_MAX_HOURS_PER_MONTH:g} h/month")
    else:
        checks[f"maintenance <= {G1_MAX_HOURS_PER_MONTH:g} h/month (every logged month)"] = maint[
            "within_budget"
        ]
    passed = all(checks.values())
    outcome = "OPEN"
    if passed:
        outcome = "MET (assessed criteria only)" if not_assessed else "MET (G1)"
    out: dict[str, Any] = {
        "pilots": len(pilots),
        "ran_real_case": len(real),
        "changed_or_derisked": changed,
        "median_time_to_first_memo_min": times[len(times) // 2] if times else None,
        "would_use_next": dict(sorted(Counter(p.would_use_next for p in pilots).items())),
        "ledger_corrections": sum(p.ledger_corrections for p in pilots),
        "checks": checks,
        "not_assessed_here": not_assessed,
        "outcome": outcome,
        "passed": passed,
    }
    if freshness is not None:
        out["freshness_streak_days"] = freshness["streak_days"]
    if maint is not None:
        out["maintenance_hours_by_month"] = maint["hours_by_month"]
        if maint["stop_criterion_months"]:
            out["STOP CRITERION (> 0.25 FTE) in"] = maint["stop_criterion_months"]
    return out


def render(s: dict[str, Any]) -> str:
    lines = ["# Pilot scorecard (gate G1)", "", f"**Outcome: {s['outcome']}**", ""]
    lines += [f"- [{'x' if ok else ' '}] {name}" for name, ok in s["checks"].items()]
    lines.append("")
    lines += [f"- {k}: {v}" for k, v in s.items() if k not in ("checks", "outcome", "passed")]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("notes", type=Path)
    ap.add_argument("--allow-empty", action="store_true", help="exit 0 when there are no notes yet")
    ap.add_argument(
        "--maintenance-log", type=Path, help="CSV date,hours,area,note (assesses the hours criterion)"
    )
    ap.add_argument(
        "--freshness-days",
        type=int,
        default=0,
        help="assess the freshness SLA over this many days of git history",
    )
    ap.add_argument(
        "--as-of", type=dt.date.fromisoformat, default=None, help="last day of the freshness window"
    )
    a = ap.parse_args(argv)
    notes, errors = load(a.notes)
    maint = None
    if a.maintenance_log is not None:
        entries, merr = load_maintenance(a.maintenance_log)
        errors += merr
        maint = maintenance(entries)
    freshness = None
    if a.freshness_days > 0:
        from pv.export import sla_history  # imported lazily: the pilot criterion alone needs no git
        from pv.ledger import published_on

        freshness = sla_history(published_on(), a.as_of or dt.date.today(), a.freshness_days)
    s = score(notes, maint, freshness)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print(render(s), end="")
    if errors:
        return 2
    if not notes and a.allow_empty:
        return 0
    return 0 if s["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
