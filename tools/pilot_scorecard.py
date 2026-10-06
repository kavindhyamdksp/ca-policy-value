"""Summarize anonymized pilot feedback against the G1 pilot criterion in DECISION.md.

    python tools/pilot_scorecard.py docs/validation/pilots

Each note is `NN-<segment>.md` with a YAML front-matter block (template in docs/validation/pilot_kit.md).
Only the whitelisted fields below are accepted, so personal data (names, employers, facilities) cannot slip
into the structured record. Exit code: 0 = criterion met (or no notes yet with --allow-empty), 1 = not yet,
2 = invalid notes. The tool counts; the G1 judgement itself stays with the maintainer.
"""

from __future__ import annotations

import argparse
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


def score(pilots: list[Pilot]) -> dict[str, Any]:
    real = [p for p in pilots if p.ran_real_case == "yes"]
    changed = [p.id for p in real if p.decision_changed_or_derisked == "yes"]
    times = sorted(p.time_to_first_memo_min for p in pilots)
    met = len(changed) >= G1_MIN_PARTNERS
    return {
        "pilots": len(pilots),
        "ran_real_case": len(real),
        "changed_or_derisked": changed,
        "median_time_to_first_memo_min": times[len(times) // 2] if times else None,
        "would_use_next": dict(sorted(Counter(p.would_use_next for p in pilots).items())),
        "ledger_corrections": sum(p.ledger_corrections for p in pilots),
        "checks": {
            f">= {G1_MIN_PARTNERS} pilots ran a real case and the memo changed or de-risked it": met,
        },
        "not_assessed_here": ["ledger freshness SLA met for 60 days", "maintenance <= 15 h/month"],
        "outcome": "MET (pilot criterion)" if met else "OPEN",
        "passed": met,
    }


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
    a = ap.parse_args(argv)
    notes, errors = load(a.notes)
    s = score(notes)
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
