"""Data contracts (results/case/record schemas), external overrides, ledger export, templates, CLI."""

from __future__ import annotations

import csv
import datetime as dt
import io
import json
from importlib import resources
from pathlib import Path

import jsonschema
import pytest
import yaml
from typer.testing import CliRunner

from pv import export, schemas
from pv.case import Case, load_case, load_overrides, with_overrides
from pv.cli import app
from pv.ledger import Ledger, _jsonable, load_ledger
from pv.results import evaluate

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "cases").glob("*.yaml"))
TEMPLATES = ("heat_pump", "abatement")
LEDGER = load_ledger()
TODAY = dt.date(2026, 9, 30)
runner = CliRunner()


# ---------------------------------------------------------------- schemas


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_golden_results_conform_to_results_v1(path: Path) -> None:
    res, _, _ = evaluate(load_case(path), LEDGER)
    assert schemas.validate_results(res) == []


def test_results_schema_rejects_drift_in_shape() -> None:
    res, _, _ = evaluate(load_case(CASES[0]), LEDGER)
    bad = {**res, "decision": {**res["decision"], "answer": "MAYBE"}}
    assert any("decision/answer" in e for e in schemas.validate_results(bad))
    bad = {**res, "unexpected": 1}
    assert schemas.validate_results(bad)


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_case_files_conform_to_generated_case_schema(path: Path) -> None:
    jsonschema.validate(_jsonable(yaml.safe_load(path.read_text())), schemas.case_schema())


def test_case_schema_rejects_unknown_fields() -> None:
    raw = _jsonable(yaml.safe_load(CASES[0].read_text()))
    raw["facility"]["typo"] = 1
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(raw, schemas.case_schema())


def test_schema_lookup() -> None:
    assert schemas.get("results")["title"].startswith("PolicyValue CA results")
    assert "records" in schemas.get("record")["properties"]
    assert schemas.get("case")["title"] == "PolicyValue CA case"


# ---------------------------------------------------------------- external overrides


def test_external_overrides_apply_after_case_overrides(tmp_path: Path) -> None:
    f = tmp_path / "prices.local.yaml"
    f.write_text(
        yaml.safe_dump(
            {"overrides": [{"record": "fed.nir.grid_ef", "value": {"BC": 40.0}, "reason": "site meter"}]}
        )
    )
    base = load_case(ROOT / "cases" / "golden_hp_bc_covered.yaml")
    merged = with_overrides(base, load_overrides(f))
    res, _, _ = evaluate(merged, LEDGER, overrides_file=f.name)
    assert res["emissions"]["grid_ef_g_kwh"] == 40.0  # later override wins over the case's 22.8
    assert res["inputs"]["overrides_file"] == "prices.local.yaml"
    assert res["inputs"]["case_sha256"] != base.digest()  # the merged overrides are part of the run hash
    assert schemas.validate_results(res) == []


@pytest.mark.parametrize("content", ["[]", "{}", "- {record: x, value: 1}"])
def test_external_overrides_are_validated(tmp_path: Path, content: str) -> None:
    f = tmp_path / "o.yaml"
    f.write_text(content)
    with pytest.raises(ValueError):
        load_overrides(f)


def test_case_digest_ignores_unset_optional_sections() -> None:
    c = load_case(CASES[0])
    assert c.digest() == Case.model_validate(c.model_dump(mode="json", exclude_none=True)).digest()


# ---------------------------------------------------------------- ledger export and review queue


def test_export_json_csv_html_cover_every_entry() -> None:
    doc = json.loads(export.ledger_json(LEDGER, TODAY))
    assert doc["schema"] == export.EXPORT_SCHEMA and doc["ledger_sha256"] == LEDGER.digest
    assert len(doc["records"]) == len(LEDGER.records)
    rows = list(csv.DictReader(io.StringIO(export.ledger_csv(LEDGER, TODAY))))
    assert tuple(rows[0]) == export.CSV_COLUMNS and len(rows) == len(LEDGER.records)
    assert all(r["primary_source_url"].startswith("http") for r in rows)
    html = export.ledger_html(LEDGER, TODAY)
    assert all(f"<code>{rid}</code>" in html for rid in LEDGER.ids())
    assert "<script" not in html
    assert export.ledger_json(LEDGER, TODAY) == export.ledger_json(load_ledger(), TODAY)  # reproducible


def test_export_html_escapes_record_text(tmp_path: Path) -> None:
    from tests.conftest import rec, write_ledger

    led = load_ledger(write_ledger(tmp_path, [rec("fed.x", 1, notes="<script>alert(1)</script>")]))
    html = export.ledger_html(led, TODAY)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_review_queue_orders_by_urgency() -> None:
    later = TODAY + dt.timedelta(days=150)
    q = export.review_queue(LEDGER, later, within_days=0)
    assert q and all(r["days_left"] <= 0 for r in q)
    assert [r["days_left"] for r in q] == sorted(r["days_left"] for r in q)
    assert {r["freshness"] for r in q} >= {"market_observation"}  # 100-day SLA passed
    assert export.review_queue(LEDGER, TODAY, within_days=-1) == []  # nothing stale today


def test_sla_history_counts_clean_days_ending_at_as_of() -> None:
    start = dt.date(2026, 10, 1)

    def published(d: dt.date) -> Ledger | None:
        return LEDGER if d >= start else None  # the ledger appears on 2026-10-01

    s = export.sla_history(published, dt.date(2026, 10, 10), 10)
    assert s["streak_days"] == 10 and s["met"] and s["stale_days"] == []
    s = export.sla_history(published, dt.date(2026, 10, 10), 60)
    assert s["streak_days"] == 10 and not s["met"] and s["days_without_ledger"] == 50
    breach = dt.date(2027, 1, 7) + dt.timedelta(days=1)  # first day past the 100-day SLA
    s = export.sla_history(published, breach + dt.timedelta(days=2), 5)
    assert s["streak_days"] == 0 and not s["met"]
    assert s["stale_days"][0]["date"] == breach.isoformat()
    assert "ab.tier.credit_obs" in s["stale_days"][0]["stale"]


def test_cli_ledger_sla_reads_git_history() -> None:
    r = runner.invoke(app, ["ledger", "sla", "--days", "3", "--as-of", "2027-06-30"])
    assert r.exit_code == 1 and "NOT YET" in r.output and "stale:" in r.output
    r = runner.invoke(app, ["ledger", "sla", "--days", "3", "--as-of", "2027-06-30", "--json"])
    assert r.exit_code == 1 and json.loads(r.output)["window_days"] == 3
    r = runner.invoke(app, ["ledger", "sla", "--ref", "no-such-ref"])
    assert r.exit_code == 2


# ---------------------------------------------------------------- templates


@pytest.mark.parametrize("kind", TEMPLATES)
def test_case_templates_parse_and_run(kind: str) -> None:
    text = (resources.files("pv") / "templates" / "cases" / f"{kind}.yaml").read_text()
    assert "SYNTHETIC PLACEHOLDER" in text
    c = Case.model_validate(yaml.safe_load(text))
    res, _, _ = evaluate(c, LEDGER)
    assert schemas.validate_results(res) == []


# ---------------------------------------------------------------- CLI


def test_cli_schema_template_due_export(tmp_path: Path) -> None:
    r = runner.invoke(app, ["schema", "results"])
    assert r.exit_code == 0 and json.loads(r.output)["title"].startswith("PolicyValue CA results")
    out = tmp_path / "case.schema.json"
    assert runner.invoke(app, ["schema", "case", "--out", str(out)]).exit_code == 0
    assert json.loads(out.read_text())["title"] == "PolicyValue CA case"

    tpl = tmp_path / "mine.yaml"
    assert runner.invoke(app, ["case", "template", "--kind", "abatement", "--out", str(tpl)]).exit_code == 0
    assert runner.invoke(app, ["case", "template", "--out", str(tpl)]).exit_code == 1  # never overwrites
    r = runner.invoke(app, ["run", str(tpl), "--out", str(tmp_path / "o"), "--no-html"])
    assert r.exit_code == 0, r.output

    r = runner.invoke(app, ["ledger", "due", "--as-of", "2027-03-01", "--within", "0"])
    assert r.exit_code == 0 and "STALE" in r.output
    r = runner.invoke(app, ["ledger", "due", "--as-of", "2026-09-30", "--json"])
    assert r.exit_code == 0 and isinstance(json.loads(r.output), list)

    site = tmp_path / "site"
    r = runner.invoke(app, ["ledger", "export", "--out", str(site), "--as-of", "2026-09-30"])
    assert r.exit_code == 0
    assert {p.name for p in site.iterdir()} == {"records.json", "records.csv", "index.html"}


def test_cli_run_and_drift_with_overrides_file(tmp_path: Path) -> None:
    f = tmp_path / "prices.local.yaml"
    f.write_text("- {record: ab.tier.credit_obs, value: {base: 30, low: 25}, reason: broker quote}\n")
    case = ROOT / "cases" / "golden_ab_abatement_ccfd.yaml"
    r = runner.invoke(app, ["run", str(case), "--out", str(tmp_path / "o"), "--overrides", str(f)])
    assert r.exit_code == 0, r.output
    res = json.loads((tmp_path / "o" / "results.json").read_text())
    assert res["inputs"]["overrides_file"] == "prices.local.yaml"
    assert any("Override: ab.tier.credit_obs" in w for w in res["warnings"])
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
            "--overrides",
            str(f),
        ],
    )
    assert r.exit_code == 0 and "Flipped decisions: none" in r.output
    bad = tmp_path / "bad.yaml"
    bad.write_text("- {record: x}\n")
    assert runner.invoke(app, ["run", str(case), "--overrides", str(bad)]).exit_code == 2
