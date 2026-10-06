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


def _log(path: Path, rows: list[str]) -> Path:
    path.write_text("date,hours,area,note\n" + "".join(r + "\n" for r in rows))
    return path


def test_maintenance_budget_and_stop_criterion(tmp_path: Path) -> None:
    ok = _log(
        tmp_path / "ok.csv", ["2026-11-03,6,ledger,refresh", "2026-11-20,8.5,code,", "2026-12-01,3,docs,"]
    )
    entries, errors = pilot_scorecard.load_maintenance(ok)
    m = pilot_scorecard.maintenance(entries)
    assert not errors and m["within_budget"] and m["hours_by_month"] == {"2026-11": 14.5, "2026-12": 3.0}
    over = _log(tmp_path / "over.csv", ["2027-01-05,20,ledger,", "2027-01-06,24,ledger,"])
    m = pilot_scorecard.maintenance(pilot_scorecard.load_maintenance(over)[0])
    assert not m["within_budget"] and m["stop_criterion_months"] == ["2027-01"]  # 44 h > 0.25 FTE
    assert not pilot_scorecard.maintenance([])["within_budget"]  # no evidence is not a pass


def test_full_g1_readout(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    notes = tmp_path / "notes"
    notes.mkdir()
    for i in range(1, 4):
        _note(notes, i)
    log = _log(tmp_path / "log.csv", ["2026-11-03,6,ledger,refresh"])
    fresh = {"window_days": 60, "streak_days": 60, "met": True}
    s = pilot_scorecard.score(
        pilot_scorecard.load(notes)[0],
        pilot_scorecard.maintenance(pilot_scorecard.load_maintenance(log)[0]),
        fresh,
    )
    assert s["passed"] and s["outcome"] == "MET (G1)" and s["not_assessed_here"] == []
    s = pilot_scorecard.score(pilot_scorecard.load(notes)[0], None, {**fresh, "met": False, "streak_days": 9})
    assert not s["passed"] and s["not_assessed_here"] == ["maintenance <= 15 h/month"]
    bad = _log(tmp_path / "bad.csv", ["2026-11-03,-1,ledger,", "2026-11-04,2,coffee,"])
    assert pilot_scorecard.main([str(notes), "--maintenance-log", str(bad)]) == 2
    assert "bad.csv:2" in capsys.readouterr().err
    assert pilot_scorecard.main([str(notes), "--maintenance-log", str(log)]) == 0
    assert pilot_scorecard.main([str(notes), "--freshness-days", "3", "--as-of", "2027-06-30"]) == 1
