"""Golden cases (plan §5.3/§5.5/§5.6): snapshots, reproducibility, and the ab.tier.floor drift flip."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from pv.case import load_case
from pv.drift import diff_ledgers, drift
from pv.ledger import load_ledger, load_ledger_at
from pv.results import evaluate, to_json

ROOT = Path(__file__).resolve().parents[2]
CASES = sorted((ROOT / "cases").glob("golden_*.yaml"))
SNAP = Path(__file__).parent / "snapshots"
LEDGER = load_ledger()


def _stable(res: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(res))
    out["inputs"].pop("ledger_version")  # git-describe label; content is pinned by ledger_sha256
    return out


def test_three_golden_cases_exist() -> None:
    assert [p.stem for p in CASES] == ["golden_ab_abatement_ccfd", "golden_hp_bc_covered", "golden_hp_qc"]


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_snapshot(path: Path) -> None:
    res, _, _ = evaluate(load_case(path), LEDGER)
    snap = SNAP / f"{path.stem}.json"
    got = _stable(res)
    if os.environ.get("PV_UPDATE_SNAPSHOTS") == "1" or not snap.exists():
        snap.write_text(json.dumps(got, indent=2, sort_keys=True) + "\n")
    assert got == json.loads(snap.read_text()), "snapshot changed: review, then PV_UPDATE_SNAPSHOTS=1"


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_byte_identical_reruns(path: Path) -> None:
    case = load_case(path)
    a = to_json(evaluate(case, LEDGER)[0])
    b = to_json(evaluate(case, load_ledger())[0])
    assert a == b


def test_golden_expectations() -> None:
    res = {p.stem: evaluate(load_case(p), LEDGER)[0] for p in CASES}
    ab = res["golden_ab_abatement_ccfd"]
    assert ab["decision"]["base_case"] == "NO-GO"
    assert not ab["carbon"]["floor_in_base"]
    assert any("ab.tier.floor" in w for w in ab["warnings"])
    assert ab["robustness"]["grid"]["n_states"] == 3 * 2 * 3
    qc = res["golden_hp_qc"]
    assert qc["tax"]["eligibility"] == "not_listed" and not qc["tax"]["itc_granted"]
    assert qc["decision"]["answer"] == "DEPENDS-ON"
    assert any(c == {"itc_granted": True} for c in qc["robustness"]["grid"]["minimal_go_conditions"])
    bc = res["golden_hp_bc_covered"]
    assert bc["carbon"]["kind"] == "covered" and bc["decision"]["base_case"] == "GO"


def _ledger_with_floor_in_force(tmp: Path) -> Path:
    dst = tmp / "ledger"
    shutil.copytree(ROOT / "ledger", dst)
    f = dst / "records" / "ab" / "tier_floor.yaml"
    doc = yaml.safe_load(f.read_text())
    rec = doc["records"][0]
    rec["legal_status"] = "in_force"
    rec["recorded_at"] = "2027-01-05"
    rec["sources"].append(
        {
            "url": "https://kings-printer.alberta.ca/example-floor-regulation",
            "title": "TIER floor regulation (fixture)",
            "publisher": "Alberta King's Printer",
            "published": "2026-12-31",
            "retrieved": "2027-01-05",
            "locator": "s. 1",
            "excerpt": "fixture",
            "source_type": "primary_legal",
        }
    )
    f.write_text(yaml.safe_dump(doc, sort_keys=False).replace("\n  ON:", '\n  "ON":'))
    return dst


def test_drift_floor_in_force_flips_ab_ccfd(tmp_path: Path) -> None:
    """DoD §2.4-5: ab.tier.floor announced → in_force flips golden_ab_abatement_ccfd."""
    new = load_ledger(_ledger_with_floor_in_force(tmp_path), version="fixture-floor-in-force")
    d = drift(CASES, LEDGER, new)
    assert [c["id"] for c in d["record_changes"]] == ["ab.tier.floor"]
    assert d["record_changes"][0]["after"][0]["legal_status"] == "in_force"
    ab = next(c for c in d["cases"] if c["case_id"] == "golden_ab_abatement_ccfd")
    assert ab["flipped"] and ab["before"]["base_case"] == "NO-GO" and ab["after"]["base_case"] == "GO"
    assert ab["npv_delta"] > 0 and ab["changed_records_used"] == ["ab.tier.floor"]
    assert d["flips"] == ["golden_ab_abatement_ccfd"]
    others = [c for c in d["cases"] if c["case_id"] != "golden_ab_abatement_ccfd"]
    assert all(not c["flipped"] and c["npv_delta"] == 0 for c in others)


def test_diff_detects_add_remove(tmp_path: Path) -> None:
    dst = _ledger_with_floor_in_force(tmp_path)
    (dst / "records" / "ab" / "tier_credit_obs.yaml").unlink()
    d = diff_ledgers(LEDGER, load_ledger(dst))
    assert {c["id"]: c["change"] for c in d} == {"ab.tier.floor": "changed", "ab.tier.credit_obs": "removed"}


def test_load_ledger_at_git_tag() -> None:
    tags = subprocess.run(
        ["git", "-C", str(ROOT), "tag", "-l", "ledger-v2026.10.0"], capture_output=True, text=True
    )
    if "ledger-v2026.10.0" not in tags.stdout:
        pytest.skip("ledger tag not fetched in this checkout")
    led = load_ledger_at("ledger-v2026.10.0", ROOT)
    assert led.version == "ledger-v2026.10.0" and len(led.records) >= 30
