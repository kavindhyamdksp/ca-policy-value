"""`pv` command line: validate, run, drift, ledger show."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from pv import __version__
from pv.case import load_case
from pv.drift import drift as run_drift
from pv.drift import render as render_drift
from pv.ledger import (
    FRESHNESS_SLA_DAYS,
    LedgerError,
    load_ledger,
    load_ledger_at,
)
from pv.ledger import (
    validate as validate_ledger,
)
from pv.report import render_html, render_markdown
from pv.results import cashflows_csv, evaluate, to_json

app = typer.Typer(no_args_is_help=True, add_completion=False, help="PolicyValue CA: realized policy value.")
ledger_app = typer.Typer(no_args_is_help=True, help="Inspect the policy ledger.")
app.add_typer(ledger_app, name="ledger")

LedgerOpt = Annotated[
    Path | None, typer.Option("--ledger", help="Ledger directory (default: bundled ledger/)")
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
) -> None:
    """Value case(s): writes results.json, cashflows.csv, memo.md and memo.html per case."""
    led = load_ledger_at(ledger_ref) if ledger_ref else load_ledger(ledger)
    for f in case_files:
        try:
            case = load_case(f)
            res, model, _ = evaluate(case, led)
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
) -> None:
    """Re-run saved cases against two ledger versions; list record changes and flipped decisions."""
    a = load_ledger_at(from_ref)
    b = load_ledger() if to_ref == "WORKTREE" else load_ledger_at(to_ref)
    d = run_drift(sorted(cases.glob("*.yaml")), a, b)
    typer.echo(render_drift(d))
    if json_out:
        json_out.write_text(json.dumps(d, indent=2, sort_keys=True, default=str) + "\n")
    raise typer.Exit(1 if fail_on_flip and d["flips"] else 0)


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


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
