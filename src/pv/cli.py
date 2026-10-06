"""`pv` command line: validate, run, drift, schema, case template, ledger show/due/export/sla."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from importlib import resources
from pathlib import Path
from typing import Annotated, Literal

import typer

from pv import __version__, schemas
from pv import export as ledger_export
from pv.case import load_case, load_overrides, with_overrides
from pv.drift import drift as run_drift
from pv.drift import render as render_drift
from pv.ledger import (
    FRESHNESS_SLA_DAYS,
    LedgerError,
    Override,
    load_ledger,
    load_ledger_at,
    published_on,
)
from pv.ledger import (
    validate as validate_ledger,
)
from pv.report import render_html, render_markdown
from pv.results import cashflows_csv, evaluate, to_json

CaseKind = Literal["heat_pump", "abatement"]

app = typer.Typer(no_args_is_help=True, add_completion=False, help="PolicyValue CA: realized policy value.")
ledger_app = typer.Typer(no_args_is_help=True, help="Inspect, maintain and publish the policy ledger.")
app.add_typer(ledger_app, name="ledger")
case_app = typer.Typer(no_args_is_help=True, help="Start a new case.")
app.add_typer(case_app, name="case")

LedgerOpt = Annotated[
    Path | None, typer.Option("--ledger", help="Ledger directory (default: bundled ledger/)")
]
OverridesOpt = Annotated[
    Path | None,
    typer.Option(
        "--overrides",
        help="YAML list of {record, value, reason} applied after the case's own overrides "
        "(for licensed or private values kept out of committed case files)",
    ),
]


def _date(s: str | None) -> dt.date:
    return dt.date.fromisoformat(s) if s else dt.date.today()  # CLI only; the kernel never reads the clock


def _show_version(value: bool) -> None:
    if value:
        typer.echo(f"policyvalue-ca {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", callback=_show_version, is_eager=True, help="Show version and exit.")
    ] = False,
) -> None:
    """PolicyValue CA: realized policy value for Canadian industrial decarbonization projects."""


@app.command()
def validate(
    ledger: LedgerOpt = None,
    as_of: Annotated[
        str | None, typer.Option(help="Check freshness as of this date (default: today)")
    ] = None,
    strict: Annotated[
        bool, typer.Option("--strict/--lenient", help="Lenient: stale records warn only")
    ] = True,
    cases: Annotated[Path | None, typer.Option(help="Also parse every case YAML in this directory")] = None,
) -> None:
    """Validate the ledger (schema, units, dates, overlaps, primary sources, freshness SLAs)."""
    led = load_ledger(ledger, strict=False)
    errs = validate_ledger(led, _date(as_of))
    stale = [e for e in errs if ": stale" in e]
    hard = errs if strict else [e for e in errs if e not in stale]
    for e in errs:
        typer.echo(("ERROR " if e in hard else "WARN  ") + e, err=True)
    n_case = 0
    for p in sorted(cases.glob("*.yaml")) if cases else []:
        try:
            load_case(p)
            n_case += 1
        except Exception as ex:
            hard.append(f"{p}: {ex}")
            typer.echo(f"ERROR {p}: {str(ex).splitlines()[0]}", err=True)
    typer.echo(
        f"{len(led.records)} records, {len(led.ids())} ids, {n_case} cases: "
        f"{len(hard)} errors, {len(errs) - len(hard)} warnings (ledger {led.version})"
    )
    raise typer.Exit(1 if hard else 0)


@app.command()
def run(
    case_files: Annotated[list[Path], typer.Argument(help="Case YAML file(s)")],
    out: Annotated[Path, typer.Option(help="Output directory")] = Path("out"),
    ledger: LedgerOpt = None,
    ledger_ref: Annotated[str | None, typer.Option(help="Use the ledger at this git tag/commit")] = None,
    html: Annotated[bool, typer.Option("--html/--no-html")] = True,
    overrides: OverridesOpt = None,
) -> None:
    """Value case(s): writes results.json, cashflows.csv, memo.md and memo.html per case."""
    led = load_ledger_at(ledger_ref) if ledger_ref else load_ledger(ledger)
    extra = _extra_overrides(overrides)
    for f in case_files:
        try:
            case = with_overrides(load_case(f), extra)
            res, model, _ = evaluate(case, led, overrides_file=overrides.name if overrides else None)
        except (LedgerError, ValueError) as ex:
            typer.echo(f"{f}: {ex}", err=True)
            raise typer.Exit(2) from ex
        d = out / case.case_id if len(case_files) > 1 or out == Path("out") else out
        d.mkdir(parents=True, exist_ok=True)
        (d / "results.json").write_text(to_json(res))
        (d / "cashflows.csv").write_text(cashflows_csv(model))
        md = render_markdown(res)
        (d / "memo.md").write_text(md)
        if html:
            (d / "memo.html").write_text(render_html(md, f"Decision memo — {case.case_id}"))
        npv = res["metrics"]["npv"]
        typer.echo(f"{case.case_id}: {res['decision']['answer']}  NPV {npv / 1e6:+.2f} $M  → {d}/")


@app.command()
def drift(
    from_ref: Annotated[str, typer.Option("--from", help="Old ledger: git ref or directory")],
    to_ref: Annotated[
        str, typer.Option("--to", help="New ledger: git ref, directory, or WORKTREE")
    ] = "WORKTREE",
    cases: Annotated[Path, typer.Option(help="Directory of saved cases")] = Path("cases"),
    json_out: Annotated[
        Path | None, typer.Option("--json", help="Also write the drift report as JSON")
    ] = None,
    fail_on_flip: Annotated[bool, typer.Option(help="Exit 1 if any decision flips")] = False,
    overrides: OverridesOpt = None,
) -> None:
    """Re-run saved cases against two ledger versions; list record changes and flipped decisions."""
    a = load_ledger_at(from_ref)
    b = load_ledger() if to_ref == "WORKTREE" else load_ledger_at(to_ref)
    d = run_drift(sorted(cases.glob("*.yaml")), a, b, extra_overrides=_extra_overrides(overrides))
    typer.echo(render_drift(d))
    if json_out:
        json_out.write_text(json.dumps(d, indent=2, sort_keys=True, default=str) + "\n")
    raise typer.Exit(1 if fail_on_flip and d["flips"] else 0)


def _extra_overrides(path: Path | None) -> tuple[Override, ...]:
    if path is None:
        return ()
    try:
        return load_overrides(path)
    except (OSError, ValueError) as ex:
        typer.echo(f"{path}: {ex}", err=True)
        raise typer.Exit(2) from ex


def _write(text: str, out: Path | None) -> None:
    if out is None:
        typer.echo(text, nl=False)
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        typer.echo(f"wrote {out}", err=True)


@app.command()
def schema(
    name: Annotated[schemas.SchemaName, typer.Argument(help="case | results | record")],
    out: Annotated[Path | None, typer.Option(help="Write to this file instead of stdout")] = None,
) -> None:
    """Print a JSON Schema: case files, results.json (pv.results/v1) or ledger record files."""
    _write(json.dumps(schemas.get(name), indent=2, sort_keys=True) + "\n", out)


@case_app.command("template")
def case_template(
    kind: Annotated[
        CaseKind, typer.Option(help="heat_pump (fuel switching) or abatement (large emitter, CCfD)")
    ] = "heat_pump",
    out: Annotated[Path | None, typer.Option(help="Write to this file instead of stdout")] = None,
) -> None:
    """Print a commented case template with synthetic placeholder values to replace."""
    text = (resources.files("pv") / "templates" / "cases" / f"{kind}.yaml").read_text()
    if out is not None and out.exists():
        typer.echo(f"{out} exists; not overwriting", err=True)
        raise typer.Exit(1)
    _write(text, out)


@ledger_app.command("show")
def ledger_show(
    record_id: Annotated[str | None, typer.Argument(help="Record id (omit to list all)")] = None,
    ledger: LedgerOpt = None,
    as_of: Annotated[str | None, typer.Option(help="View date (default: today)")] = None,
) -> None:
    """List ledger records, or show one record with its sources."""
    led = load_ledger(ledger)
    when = _date(as_of)
    recs = [r for r in led.records if r.recorded_at <= when and (record_id is None or r.id == record_id)]
    if not recs:
        typer.echo(f"no record {record_id!r}", err=True)
        raise typer.Exit(1)
    if record_id is None:
        for r in sorted(recs, key=lambda r: (r.id, r.effective_from)):
            days = FRESHNESS_SLA_DAYS[r.freshness] - (when - r.retrieved).days
            v = json.dumps(r.value)
            typer.echo(
                f"{r.id:34} {r.legal_status:11} {r.effective_from}  {v[:48]:48} {r.unit:9} "
                f"{'STALE' if days < 0 else f'{days}d'}"
            )
        typer.echo(f"{len(recs)} entries · ledger {led.version}")
        return
    for r in recs:
        typer.echo(json.dumps(r.model_dump(mode="json"), indent=2, ensure_ascii=False))


@ledger_app.command("due")
def ledger_due(
    within: Annotated[int, typer.Option(help="List entries due within this many days")] = 30,
    ledger: LedgerOpt = None,
    as_of: Annotated[str | None, typer.Option(help="Reference date (default: today)")] = None,
    json_out: Annotated[bool, typer.Option("--json", help="Print JSON instead of a table")] = False,
) -> None:
    """Review queue: entries that breach (or will breach) their freshness SLA, with source URLs."""
    led = load_ledger(ledger)
    rows = ledger_export.review_queue(led, _date(as_of), within)
    if json_out:
        typer.echo(json.dumps(rows, indent=2))
        return
    for r in rows:
        state = "STALE" if r["days_left"] < 0 else f"{r['days_left']}d"
        typer.echo(f"{r['id']:34} {r['legal_status']:11} {r['freshness']:18} due {r['due']}  {state}")
    typer.echo(f"{len(rows)} entries due within {within} days · ledger {led.version}")


@ledger_app.command("export")
def ledger_export_cmd(
    out: Annotated[Path, typer.Option(help="Output directory")] = Path("out/ledger"),
    ledger: LedgerOpt = None,
    ledger_ref: Annotated[str | None, typer.Option(help="Export the ledger at this git tag/commit")] = None,
    as_of: Annotated[str | None, typer.Option(help="Freshness reference date (default: today)")] = None,
) -> None:
    """Write the ledger as records.json, records.csv and a static index.html (publishable as-is)."""
    led = load_ledger_at(ledger_ref) if ledger_ref else load_ledger(ledger)
    when = _date(as_of)
    out.mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(ledger_export.ledger_json(led, when))
    (out / "records.csv").write_text(ledger_export.ledger_csv(led, when))
    (out / "index.html").write_text(ledger_export.ledger_html(led, when))
    typer.echo(f"{len(led.records)} entries → {out}/ (records.json, records.csv, index.html)")


@ledger_app.command("sla")
def ledger_sla(
    days: Annotated[int, typer.Option(min=1, help="Window that must be free of stale records")] = 60,
    ref: Annotated[
        str, typer.Option(help="Git ref whose first-parent history is the published ledger")
    ] = "HEAD",
    as_of: Annotated[str | None, typer.Option(help="Last day of the window (default: today)")] = None,
    json_out: Annotated[bool, typer.Option("--json", help="Print JSON instead of a summary")] = False,
) -> None:
    """Freshness SLA history (gate G1): was every record within its SLA on each of the last N days?
    Exit 0 if the whole window was clean, 1 otherwise."""
    try:
        s = ledger_export.sla_history(published_on(ref), _date(as_of), days)
    except (LedgerError, subprocess.CalledProcessError) as ex:
        typer.echo(f"cannot read ledger history at {ref}: {ex}", err=True)
        raise typer.Exit(2) from ex
    if json_out:
        typer.echo(json.dumps(s, indent=2))
    else:
        verdict = "MET" if s["met"] else "NOT YET"
        typer.echo(
            f"Freshness SLA, {s['window_days']} days to {s['as_of']}: {verdict} — "
            f"{s['streak_days']} consecutive clean days"
        )
        if s["days_without_ledger"]:
            typer.echo(f"  {s['days_without_ledger']} days in the window predate the ledger")
        for d in s["stale_days"]:
            typer.echo(f"  {d['date']} stale: {', '.join(d['stale'])}")
    raise typer.Exit(0 if s["met"] else 1)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
