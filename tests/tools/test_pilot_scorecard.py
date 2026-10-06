"""Pilot scorecard on synthetic notes (no real pilot data)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tools import pilot_scorecard


def _note(d: Path, i: int, seg: str = "covered_facility", **fields: Any) -> None:
    fm = {
        "id": f"{i:02d}",
        "date": "2026-11-15",
        "segment": seg,
        "province": "AB",
        "ran_real_case": "yes",
        "decision_changed_or_derisked": "yes",
        "time_to_first_memo_min": 30 + i,
        "would_use_next": "yes",
        **fields,
    }
    (d / f"{i:02d}-{seg}.md").write_text("---\n" + yaml.safe_dump(fm) + "---\n\nSynthetic note.\n")


def test_criterion_met_with_three_changed_decisions(tmp_path: Path) -> None:
    for i in range(1, 5):
        _note(tmp_path, i, decision_changed_or_derisked="yes" if i < 4 else "no", ledger_corrections=1)
    (tmp_path / "README.md").write_text("ignored\n")
    notes, errors = pilot_scorecard.load(tmp_path)
    s = pilot_scorecard.score(notes)
    assert not errors and s["passed"] and s["changed_or_derisked"] == ["01", "02", "03"]
    assert s["median_time_to_first_memo_min"] == 33 and s["ledger_corrections"] == 4
    assert "MET" in pilot_scorecard.render(s)
    assert pilot_scorecard.main([str(tmp_path)]) == 0


def test_open_until_three_pilots_change_a_decision(tmp_path: Path) -> None:
    _note(tmp_path, 1)
    _note(tmp_path, 2, ran_real_case="no")  # a demo run does not count
    assert pilot_scorecard.main([str(tmp_path)]) == 1


def test_notes_reject_personal_data_fields(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _note(tmp_path, 1, name="Jane Doe")
    (tmp_path / "02-consultant.md").write_text("no front matter\n")
    assert pilot_scorecard.main([str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert "01-covered_facility.md" in err and "02-consultant.md" in err


def test_empty_notes_allowed_only_on_request(tmp_path: Path) -> None:
    assert pilot_scorecard.main([str(tmp_path / "none"), "--allow-empty"]) == 0
    assert pilot_scorecard.main([str(tmp_path / "none")]) == 1


def test_bare_yaml_yes_no_are_accepted(tmp_path: Path) -> None:
    (tmp_path / "01-consultant.md").write_text(
        "---\nid: '01'\ndate: 2026-11-15\nsegment: consultant\nprovince: BC\nran_real_case: yes\n"
        "decision_changed_or_derisked: no\ntime_to_first_memo_min: 40\nwould_use_next: maybe\n---\n"
    )
    notes, errors = pilot_scorecard.load(tmp_path)
    assert not errors and notes[0].ran_real_case == "yes" and notes[0].decision_changed_or_derisked == "no"
