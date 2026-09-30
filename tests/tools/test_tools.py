"""Gate scorecards and the demo-kit builder, on synthetic notes (no real interview data)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tools import build_demo_kit, gate_scorecard

SEGMENTS = ["covered_facility"] * 6 + ["consultant"] * 4 + ["developer"] * 2


def _note(d: Path, i: int, seg: str, **fields: Any) -> None:
    fm = {"id": f"{i:02d}", "date": "2026-10-20", "segment": seg, "province": "AB", **fields}
    (d / f"{i:02d}-{seg}.md").write_text("---\n" + yaml.safe_dump(fm) + "---\n\nSynthetic note.\n")


def _interviews(d: Path, confirming: int, ledger_only: int = 0) -> Path:
    d.mkdir(exist_ok=True)
    for i, seg in enumerate(SEGMENTS, start=1):
        _note(
            d,
            i,
            seg,
            carbon_method="headline" if i <= confirming else "EPC quotes",
            criterion_a="yes" if i <= confirming else "no",
            would_use_kernel_live="yes" if i <= confirming else "maybe",
            would_use_ledger_alone="yes" if i <= ledger_only else "no",
        )
    (d / "README.md").write_text("ignored\n")
    return d


def _demos(p: Path, *, incumbent: bool = False) -> Path:
    demos = [
        {"product": "SINAI Reduce", "values_obps_projects_with_regime_risk": "yes" if incumbent else "no"},
        {"product": "ClearBlue Vantage", "values_obps_projects_with_regime_risk": "unknown"},
    ]
    p.write_text("---\n" + yaml.safe_dump({"demos": demos}) + "---\n")
    return p


@pytest.mark.parametrize(
    ("confirming", "ledger_only", "incumbent", "demos", "outcome", "code"),
    [
        (6, 0, False, True, "PASS", 0),
        (5, 3, False, True, "FALLBACK", 1),
        (5, 0, False, True, "FAIL", 1),
        (8, 0, True, True, "KILL", 1),
        (8, 0, False, False, "OPEN", 1),
    ],
)
def test_g0_outcomes(
    tmp_path: Path, confirming: int, ledger_only: int, incumbent: bool, demos: bool, outcome: str, code: int
) -> None:
    notes = _interviews(tmp_path / "i", confirming, ledger_only)
    args = ["g0", str(notes)]
    if demos:
        args += ["--demos", str(_demos(tmp_path / "demos.md", incumbent=incumbent))]
    assert gate_scorecard.main(args) == code
    ints, _ = gate_scorecard.load(notes, gate_scorecard.Interview)
    dms = (
        []
        if not demos
        else [
            gate_scorecard.Demo.model_validate(x)
            for x in gate_scorecard.front_matter(tmp_path / "demos.md")["demos"]
        ]
    )
    assert gate_scorecard.score_g0(ints, dms)["outcome"].startswith(outcome)


def test_notes_reject_personal_data_fields(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    d = tmp_path / "i"
    d.mkdir()
    _note(
        d,
        1,
        "consultant",
        carbon_method="x",
        criterion_a="yes",
        would_use_kernel_live="yes",
        would_use_ledger_alone="no",
        name="Jane Doe",
    )
    (d / "02-consultant.md").write_text("no front matter\n")
    assert gate_scorecard.main(["g0", str(d)]) == 2
    err = capsys.readouterr().err
    assert "01-consultant.md" in err and "02-consultant.md" in err


def test_empty_notes_allowed_only_on_request(tmp_path: Path) -> None:
    assert gate_scorecard.main(["g1", str(tmp_path / "none"), "--allow-empty"]) == 0
    assert gate_scorecard.main(["g1", str(tmp_path / "none")]) == 1


def test_g1_partner_criterion(tmp_path: Path) -> None:
    d = tmp_path / "p"
    d.mkdir()
    for i in range(1, 5):
        _note(
            d,
            i,
            "covered_facility",
            ran_real_case="yes",
            decision_changed_or_derisked="yes" if i < 4 else "no",
            time_to_first_memo_min=30 + i,
            would_use_next="yes",
            ledger_corrections=1,
        )
    notes, errors = gate_scorecard.load(d, gate_scorecard.Pilot)
    s = gate_scorecard.score_g1(notes)
    assert not errors and s["passed"] and s["changed_or_derisked"] == ["01", "02", "03"]
    assert s["median_time_to_first_memo_min"] == 33 and s["ledger_corrections"] == 4
    assert "PASS" in gate_scorecard.render(s)


def test_demo_kit_is_complete_and_deterministic(tmp_path: Path) -> None:
    a = build_demo_kit.build(tmp_path / "a")
    b = build_demo_kit.build(tmp_path / "b")
    assert [p.name for p in a] == [
        "index.html",
        "golden_ab_abatement_ccfd.html",
        "golden_hp_bc_covered.html",
        "golden_hp_qc.html",
    ]
    assert all(x.read_text() == y.read_text() for x, y in zip(a, b, strict=True))
    index = a[0].read_text()
    assert all(f'href="{p.name}"' in index for p in a[1:]) and "not tax, legal or investment advice" in index


def test_bare_yaml_yes_no_are_accepted(tmp_path: Path) -> None:
    d = tmp_path / "p"
    d.mkdir()
    (d / "01-consultant.md").write_text(
        "---\nid: '01'\ndate: 2026-11-15\nsegment: consultant\nprovince: BC\nran_real_case: yes\n"
        "decision_changed_or_derisked: no\ntime_to_first_memo_min: 40\nwould_use_next: maybe\n---\n"
    )
    notes, errors = gate_scorecard.load(d, gate_scorecard.Pilot)
    assert not errors and notes[0].ran_real_case == "yes" and notes[0].decision_changed_or_derisked == "no"
