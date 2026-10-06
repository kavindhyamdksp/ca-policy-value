"""Plan §5.7 report checks and CLI smoke tests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from pv.case import Case, load_case
from pv.cli import app
from pv.ledger import load_ledger
from pv.report import render_html, render_markdown
from pv.results import cashflows_csv, evaluate

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "cases" / "golden_ab_abatement_ccfd.yaml"
runner = CliRunner()


def _warning_case() -> Case:
    raw = yaml.safe_load(AB.read_text())
    raw["min_legal_status"] = "announced"  # the announced floor enters the base case
    raw["as_of"] = "2027-06-30"  # market observations are now past their 100-day SLA
    raw["overrides"] = [
        {"record": "ab.tier.credit_obs", "value": {"base": 25}, "reason": "broker quote 2027-06-01"}
    ]
    return Case.model_validate(raw)


def test_memo_lists_every_record_and_warns() -> None:
    res, _, view = evaluate(_warning_case(), load_ledger())
    md = render_markdown(res)
    used = {k[0] for k in view.used}
    assert used and all(f"`{rid}`" in md for rid in used)
    assert len(res["provenance"]) == len(view.used)
    assert "Base case uses announced record ab.tier.floor" in md
    assert "Override: ab.tier.credit_obs" in md
    assert "Stale record" in md
    assert "not tax, legal, accounting or investment advice" in md
    for p in res["provenance"]:
        assert p["sources"] and all(s["url"] and s["retrieved"] for s in p["sources"])
    html = render_html(md, "t")
    assert html.startswith("<!doctype html>") and "<table>" in html and "<script" not in html


def test_cashflow_csv_totals_match_npv() -> None:
    res, m, _ = evaluate(load_case(AB), load_ledger())
    rows = cashflows_csv(m).strip().splitlines()
    assert rows[0].startswith("t,year,capex") and len(rows) == 22
    total = sum(float(r.split(",")[-1]) for r in rows[1:])
    assert abs(total - res["metrics"]["npv"]) < 1.0


def test_cli_validate_run_show_drift(tmp_path: Path) -> None:
    r = runner.invoke(app, ["validate", "--as-of", "2026-10-06", "--cases", str(ROOT / "cases")])
    assert r.exit_code == 0, r.output
    r = runner.invoke(app, ["validate", "--as-of", "2027-09-29"])
    assert r.exit_code == 1 and "stale" in r.output
    r = runner.invoke(app, ["validate", "--as-of", "2027-09-29", "--lenient"])
    assert r.exit_code == 0
    out = tmp_path / "o"
    r = runner.invoke(app, ["run", str(AB), "--out", str(out)])
    assert r.exit_code == 0, r.output
    assert {p.name for p in out.iterdir()} == {"results.json", "cashflows.csv", "memo.md", "memo.html"}
    assert json.loads((out / "results.json").read_text())["schema"] == "pv.results/v1"
    r = runner.invoke(app, ["ledger", "show", "--as-of", "2026-10-01"])
    assert r.exit_code == 0 and "ab.tier.floor" in r.output
    r = runner.invoke(app, ["ledger", "show", "ab.tier.floor"])
    assert r.exit_code == 0 and '"legal_status": "announced"' in r.output
    assert runner.invoke(app, ["ledger", "show", "nope"]).exit_code == 1
    ledger_dir = str(ROOT / "ledger")
    r = runner.invoke(
        app,
        [
            "drift",
            "--from",
            ledger_dir,
            "--to",
            ledger_dir,
            "--cases",
            str(ROOT / "cases"),
            "--json",
            str(tmp_path / "d.json"),
            "--fail-on-flip",
        ],
    )
    assert r.exit_code == 0, r.output
    assert "Flipped decisions: none" in r.output
    assert runner.invoke(app, ["--version"]).output.startswith("policyvalue-ca")


def test_cli_run_reports_missing_inputs(tmp_path: Path) -> None:
    raw = yaml.safe_load(AB.read_text())
    raw["project"]["energy_deltas"] = {"natural_gas_gj": -100}
    f = tmp_path / "c.yaml"
    f.write_text(yaml.safe_dump(raw))
    r = runner.invoke(app, ["run", str(f), "--out", str(tmp_path / "o")])
    assert r.exit_code == 2 and "natural_gas_gj" in r.output
