"""Build the Phase 0 demo kit (plan P0.3) from the golden cases: one summary page plus each case's memo.

    python tools/build_demo_kit.py --out out/demo_kit

Regenerated from the kernel and the bundled ledger each time, so the kit never drifts from what the tool
actually computes. Output is deterministic for a given ledger (no dates or clocks).
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path
from typing import Any

from pv.case import load_case
from pv.ledger import load_ledger
from pv.report import CSS, render_html, render_markdown
from pv.results import evaluate

ROOT = Path(__file__).resolve().parents[1]
BLURB = {
    "golden_hp_qc": "Process heat pump, Quebec: cap-and-trade reaches every gas user; the decision turns on "
    "CT ITC eligibility for a class NRCan does not list.",
    "golden_hp_bc_covered": "The same heat pump at a BC OBPS facility: credits valued at the observed market "
    "ratio, never the headline price; coverage flips the decision.",
    "golden_ab_abatement_ccfd": "50 kt/yr abatement at an Alberta TIER emitter: the announced floor is not "
    "law, so the base case is NO-GO; the CCfD and floor decide it.",
}


def _m(x: float | None) -> str:
    return "n/a" if x is None else f"{x / 1e6:+.2f}"


def _d(x: float | None) -> str:
    return "n/a" if x is None else f"${x:,.0f}"


def summary_row(res: dict[str, Any]) -> str:
    c, rob = res["carbon"], res["robustness"]
    mc = rob["monte_carlo"]
    strike = rob.get("ccfd_strike")
    cells = [
        f'<a href="{res["case_id"]}.html">{html.escape(res["case_id"])}</a>'
        f"<br><small>{html.escape(BLURB.get(res['case_id'], ''))}</small>",
        f"<b>{res['decision']['answer']}</b><br><small>base {res['decision']['base_case']}</small>",
        _m(res["metrics"]["npv"]),
        f"{_d(c['breakeven_flat'])} vs {_d(c['band_levelized']['base'])} "
        f"<small>(headline {_d(c['band_levelized']['upper_bound_headline'])})</small>",
        f"{mc['p_npv_positive'] * 100:.0f}%" if mc else "—",
        _d(strike["npv_zero_strike"]) if strike else "—",
    ]
    return "<tr>" + "".join(f"<td>{x}</td>" for x in cells) + "</tr>"


def build(out: Path) -> list[Path]:
    ledger = load_ledger()
    out.mkdir(parents=True, exist_ok=True)
    rows, written = [], []
    for path in sorted((ROOT / "cases").glob("golden_*.yaml")):
        res, _, _ = evaluate(load_case(path), ledger)
        page = out / f"{res['case_id']}.html"
        page.write_text(render_html(render_markdown(res), f"Decision memo — {res['case_id']}"))
        written.append(page)
        rows.append(summary_row(res))
    index = out / "index.html"
    index.write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>PolicyValue CA demo kit</title><style>{CSS}</style></head><body>\n"
        "<h1>PolicyValue CA — what policy terms are really worth to a project</h1>\n"
        "<p>Three worked cases computed by the open kernel from a cited ledger "
        f"(<code>{html.escape(ledger.version)}</code>). Carbon is valued at the facility's "
        "<em>realizable</em> credit price; the headline benchmark appears only as a labelled upper bound."
        "</p>\n"
        "<table><thead><tr><th>Case</th><th>Answer</th><th>NPV $M</th>"
        "<th>Breakeven vs realizable base $/t</th><th>P(NPV&gt;0)</th><th>CCfD strike for NPV≥0</th></tr>"
        "</thead><tbody>\n" + "\n".join(rows) + "\n</tbody></table>\n"
        "<h2>Questions for you</h2><ol>"
        "<li>What carbon price did your last project use, and where did it come from?</li>"
        "<li>Would a memo like these change or de-risk a live decision?</li>"
        "<li>Which ledger values would you trust, override, or correct?</li></ol>\n"
        "<p><em>Scenario analysis from public sources and illustrative inputs; not tax, legal or investment "
        "advice.</em></p>\n</body></html>\n"
    )
    return [index, *written]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=Path("out/demo_kit"))
    a = ap.parse_args(argv)
    for p in build(a.out):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
