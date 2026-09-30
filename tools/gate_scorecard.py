"""Score anonymized interview / pilot notes against the binding gates in DECISION.md.

    python tools/gate_scorecard.py g0 docs/validation/interviews [--demos docs/validation/competitor_demos.md]
    python tools/gate_scorecard.py g1 docs/validation/pilots

Each note is `NN-<segment>.md` with a YAML front-matter block (templates in docs/validation/). Only the
whitelisted fields below are accepted, so personal data (names, employers, facilities) cannot slip into the
structured record. Exit code: 0 = gate criteria met (or no notes yet with --allow-empty), 1 = not met,
2 = invalid notes. The tool counts; the gate decision itself stays with the people in DECISION.md.
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

# DECISION.md gate G0 / G1 thresholds
G0_MIN_INTERVIEWS = 12
G0_SEGMENT_MIX = {"covered_facility": 6, "consultant": 4, "developer": 2}
G0_MIN_CONFIRMING = 6
G0_LEDGER_ONLY_FALLBACK = 3
G0_REQUIRED_DEMOS = ("SINAI", "ClearBlue")
G1_MIN_PARTNERS = 3


class _Note(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Interview(_Note):
    id: str
    date: dt.date
    segment: Literal["covered_facility", "consultant", "developer"]
    province: Literal["AB", "ON", "BC", "QC", "FED", "other"]
    carbon_method: str = Field(min_length=1, max_length=120)  # free text, e.g. "headline", "EPC quotes"
    criterion_a: YesNo  # interview guide §1 scoring: headline or rebuilt by hand each time = yes
    would_use_kernel_live: YesMaybeNo  # criterion (b): only "yes" counts
    would_use_ledger_alone: YesMaybeNo
    open_questions: dict[str, str] = {}  # SPEC §9 answers, keyed q1..q5


class Pilot(_Note):
    id: str
    date: dt.date
    segment: Literal["covered_facility", "consultant", "developer"]
    province: Literal["AB", "ON", "BC", "QC", "FED", "other"]
    ran_real_case: YesNo
    decision_changed_or_derisked: YesNo
    time_to_first_memo_min: int = Field(ge=0)
    would_use_next: YesMaybeNo
    ledger_corrections: int = Field(default=0, ge=0)


class Demo(_Note):
    product: str
    date: dt.date | None = None
    values_obps_projects_with_regime_risk: Annotated[
        Literal["yes", "no", "unknown"], BeforeValidator(_yes_no)
    ]
    notes: str = ""


def front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: no YAML front matter (--- ... ---)")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: front matter is not a mapping")
    return data


def load(directory: Path, model: type[_Note]) -> tuple[list[Any], list[str]]:
    notes: list[Any] = []
    errors: list[str] = []
    for p in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        if not NOTE.match(p.name):
            continue  # README and templates
        try:
            notes.append(model.model_validate(front_matter(p)))
        except (ValueError, ValidationError) as ex:
            errors.append(f"{p.name}: {str(ex).splitlines()[0] if isinstance(ex, ValueError) else ex}")
    return notes, errors


def score_g0(interviews: list[Interview], demos: list[Demo]) -> dict[str, Any]:
    mix: Counter[str] = Counter(i.segment for i in interviews)
    confirming = [i.id for i in interviews if i.criterion_a == "yes" and i.would_use_kernel_live == "yes"]
    ledger_only = [i.id for i in interviews if i.would_use_ledger_alone == "yes"]
    demoed = {d.product.lower(): d for d in demos}
    missing_demos = [p for p in G0_REQUIRED_DEMOS if not any(p.lower() in k for k in demoed)]
    incumbent = [d.product for d in demos if d.values_obps_projects_with_regime_risk == "yes"]
    checks = {
        f">= {G0_MIN_INTERVIEWS} interviews": len(interviews) >= G0_MIN_INTERVIEWS,
        **{f">= {n} {seg}": mix[seg] >= n for seg, n in G0_SEGMENT_MIX.items()},
        f">= {G0_MIN_CONFIRMING} confirm (a) and (b)": len(confirming) >= G0_MIN_CONFIRMING,
        "competitor demos done (SINAI, ClearBlue)": not missing_demos,
        "no incumbent values OBPS projects with regime risk": not incumbent,
    }
    passed = all(checks.values())
    if passed:
        outcome = "PASS: continue kernel (M7 pilots)"
    elif incumbent:
        outcome = "KILL CRITERION: an incumbent already does this (DECISION.md) — stop the kernel"
    elif len(interviews) >= G0_MIN_INTERVIEWS and len(ledger_only) >= G0_LEDGER_ONLY_FALLBACK:
        outcome = "FALLBACK: ledger only (M1-M2), per DECISION.md"
    elif len(interviews) >= G0_MIN_INTERVIEWS and not missing_demos:
        outcome = "FAIL: archive"
    else:
        outcome = "OPEN: evidence incomplete"
    return {
        "gate": "G0",
        "interviews": len(interviews),
        "segment_mix": dict(sorted(mix.items())),
        "confirming": confirming,
        "ledger_only_users": ledger_only,
        "demos": sorted(d.product for d in demos),
        "missing_demos": missing_demos,
        "incumbent_does_it": incumbent,
        "checks": checks,
        "outcome": outcome,
        "passed": passed,
    }


def score_g1(pilots: list[Pilot]) -> dict[str, Any]:
    real = [p for p in pilots if p.ran_real_case == "yes"]
    changed = [p.id for p in real if p.decision_changed_or_derisked == "yes"]
    times = sorted(p.time_to_first_memo_min for p in pilots)
    checks = {
        f">= {G1_MIN_PARTNERS} partners ran a real case and the memo changed/de-risked it": len(changed)
        >= G1_MIN_PARTNERS
    }
    return {
        "gate": "G1",
        "pilots": len(pilots),
        "ran_real_case": len(real),
        "changed_or_derisked": changed,
        "median_time_to_first_memo_min": times[len(times) // 2] if times else None,
        "would_use_next": dict(sorted(Counter(p.would_use_next for p in pilots).items())),
        "ledger_corrections": sum(p.ledger_corrections for p in pilots),
        "checks": checks,
        "not_assessed_here": ["ledger freshness SLA met for 60 days", "maintenance <= 15 h/month"],
        "outcome": "PASS (partner criterion)" if all(checks.values()) else "OPEN",
        "passed": all(checks.values()),
    }


def render(s: dict[str, Any]) -> str:
    lines = [f"# Gate {s['gate']} scorecard", "", f"**Outcome: {s['outcome']}**", ""]
    lines += [f"- [{'x' if ok else ' '}] {name}" for name, ok in s["checks"].items()]
    lines.append("")
    for k, v in s.items():
        if k not in ("gate", "checks", "outcome", "passed"):
            lines.append(f"- {k}: {v}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("gate", choices=["g0", "g1"])
    ap.add_argument("notes", type=Path)
    ap.add_argument("--demos", type=Path, help="G0: competitor-demo file with front matter `demos: [...]`")
    ap.add_argument("--allow-empty", action="store_true", help="exit 0 when there are no notes yet")
    a = ap.parse_args(argv)
    if a.gate == "g0":
        notes, errors = load(a.notes, Interview)
        demos: list[Demo] = []
        if a.demos and a.demos.exists():
            try:
                demos = [Demo.model_validate(d) for d in front_matter(a.demos).get("demos") or []]
            except (ValueError, ValidationError) as ex:
                errors.append(f"{a.demos.name}: {ex}")
        score = score_g0(notes, demos)
    else:
        notes, errors = load(a.notes, Pilot)
        score = score_g1(notes)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    print(render(score), end="")
    if errors:
        return 2
    if not notes and a.allow_empty:
        return 0
    return 0 if score["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
