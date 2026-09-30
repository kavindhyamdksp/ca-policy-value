---
# Structured results read by tools/gate_scorecard.py (G0). One entry per product demoed.
# values_obps_projects_with_regime_risk: yes = the product already values Canadian projects under OBPS
# mechanics with policy-regime risk (a DECISION.md kill criterion); no; or unknown.
demos: []
# Example entry (replace after each demo):
#   - product: SINAI Reduce
#     date: 2026-10-28
#     values_obps_projects_with_regime_risk: "no"
#     notes: "carbon price is a user-entered path; no credit-vs-headline distinction"
---

# Competitor demos (plan P0.5)

Status: **not started** — needs vendor demo bookings (user action). Required for G0: SINAI Reduce and
ClearBlue Vantage; VadiMAP for completeness.

## Checklist per product

Record what the product *does in the demo*, not what marketing claims. For each item: yes / partial / no,
plus one line of evidence (screen, report field, or the vendor's answer).

| # | Capability | What to look for |
|---|---|---|
| 1 | OBPS mechanics | Distinguishes covered vs non-covered sites; values abatement as avoided compliance cost or credits generated, per system (TIER, EPS, BC OBPS, fed OBPS, QC C&T) |
| 2 | Credit vs headline | Uses a credit/market price distinct from the headline benchmark; shows where the price comes from and its date |
| 3 | Floors and CCfDs | Models the AB TIER floor by legal status and a CCfD (strike, term, volume) as cash flows |
| 4 | ITC timing and eligibility | Clean Technology / CCUS / CE ITC rate by year, labour rule, eligibility as a judgement, receipt lag; CCA expensing |
| 5 | Policy-regime risk | Scenarios or probabilities over policy states (rollback, floor weaker, coverage change), not just price sensitivity |
| 6 | Provenance | Every policy number traceable to a dated source and legal status; change alerts when policy moves |
| 7 | Output | What a decision-maker receives (memo, dashboard, Excel); can it be audited? |
| 8 | Price / access | Licence model, indicative price, who in the buyer's organization uses it |

## Results

| Product | Date | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Values OBPS projects with regime risk? |
|---|---|---|---|---|---|---|---|---|---|---|
| SINAI Reduce | | | | | | | | | | |
| ClearBlue Vantage | | | | | | | | | | |
| VadiMAP | | | | | | | | | | |

After each demo, update the front matter above, then run
`python tools/gate_scorecard.py g0 docs/validation/interviews --demos docs/validation/competitor_demos.md`.
