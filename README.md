# PolicyValue CA

**What a decarbonization project is actually worth under Canadian policy as it really is.**

PolicyValue CA is an open, source-cited **ledger** of the Canadian carbon-pricing and clean-economy tax
parameters that decide industrial projects (federal + AB, ON, BC, QC), plus a deterministic **kernel**.
From the ledger and your project case it computes realized after-tax value, a policy value stack, the
breakeven carbon price against the facility's *realizable* band, policy-state robustness, optional seeded
Monte Carlo, and a cited decision memo. When the ledger changes, `pv drift` re-runs your saved cases and
flags decisions that flip.

It is a CLI and Python package. There is no server, no account and no network access at run time.

## Quick start (≈5 minutes)

Requires Python 3.11–3.13 and git.

```bash
git clone https://github.com/kavindhyamdksp/ca-policy-value.git
cd ca-policy-value
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pv run cases/golden_hp_qc.yaml
```

Output:

```
golden_hp_qc: DEPENDS-ON  NPV +0.15 $M  → out/golden_hp_qc/
```

Open `out/golden_hp_qc/memo.html` in a browser. The same folder holds `memo.md`, `results.json`
(schema `pv.results/v1`, with a hash of case + ledger + seed) and `cashflows.csv`.

Run all three golden cases, inspect the ledger and check its integrity:

```bash
pv run cases/*.yaml
pv ledger show                      # every record: status, value, unit, days left before its freshness SLA
pv ledger show ab.tier.floor        # one record with its sources
pv validate --cases cases           # schema, units, dates, primary sources, freshness
pv drift --from ledger-v2026.10.0   # re-run saved cases against the working-tree ledger
```

Start your own project from a template (every placeholder is marked `REPLACE`), keeping licensed prices in
an uncommitted file:

```bash
pv case template --kind heat_pump --out my-project.yaml
pv run my-project.yaml --overrides prices.local.yaml
```

More in the [user guide](docs/user_guide.md); formulas and caveats in the [methodology](docs/methodology.md);
extension points in the [developer guide](docs/developer_guide.md).

## Golden cases

| Case | What it shows |
|---|---|
| [`golden_hp_qc`](cases/golden_hp_qc.yaml) | 2 MWth process heat pump in Quebec. QC cap-and-trade reaches every gas user. The process-heat-pump class is *not listed* in NRCan's CT ITC guidance, so the ITC is denied in the base case; the grid shows the decision turns on it. |
| [`golden_hp_bc_covered`](cases/golden_hp_bc_covered.yaml) | The same heat pump at a BC OBPS facility. Credits valued at the observed market ratio, never at the headline price. Coverage status flips the decision. |
| [`golden_ab_abatement_ccfd`](cases/golden_ab_abatement_ccfd.yaml) | 50 kt/yr abatement at an Alberta TIER facility with an $85 CCfD. The announced TIER floor is not yet law, so with `min_legal_status: enacted` it is a scenario only, and the base case is NO-GO. When the floor regulation comes into force, `pv drift` shows the flip to GO. |

## What's in the box

| Path | Contents |
|---|---|
| [`ledger/`](ledger/) | 37 dated, cited entries (CC BY 4.0), JSON Schema, [changelog](ledger/CHANGELOG.md), [record format](ledger/RECORD_FORMAT.md) |
| [`src/pv/`](src/pv/) | Kernel: `ledger`, `registry`, `carbon`, `tax`, `cashflow`, `emissions`, `robustness`, `results`, `schemas`, `report`, `export`, `drift`, `cli` |
| [`tools/`](tools/) | Gate scorecards (G0/G1) and the demo-kit builder |
| [`cases/`](cases/) | Golden cases (also the drift set) |
| [`tests/`](tests/) | Unit, property (hypothesis), oracle, golden snapshot, drift, ledger, contract and tool tests |
| [`validation/`](validation/) | Frozen research-phase model — the oracle the kernel reproduces exactly |
| [`docs/`](docs/) | [User guide](docs/user_guide.md), [methodology](docs/methodology.md), [developer guide](docs/developer_guide.md), [spec](docs/product/SPEC.md), [architecture + ADRs](docs/architecture/), [research](docs/research/), [validation kit](docs/validation/) |
| [DECISION.md](DECISION.md), [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Verdict, gates, and the living plan |

## Why this exists (research summary)

- **The math is solved** (RETScreen, SINAI). **The Canada-specific policy layer is not.** Credit prices
  (AB ~$20, ON ~$72, BC ~$65, federal OBPS ~$37.50, QC C&T ~$45) sit far below the headline price;
  sub-threshold sites outside QC realize $0.
- **Policy terms flip decisions for covered industrial facilities and near-margin projects.** The carbon-value
  treatment is the largest NPV swing factor, and a CCfD moves P(NPV>0) from 0% to 76% in the Alberta example.
  → [quantitative validation](docs/research/04_quantitative_validation.md), [DECISION.md](DECISION.md)
- **Demand is the open risk.** Gate G0 needs ≥12 practitioner interviews; see the [recruitment plan](docs/validation/recruitment.md),
  [interview guide](docs/validation/interview_guide.md), [competitor-demo checklist](docs/validation/competitor_demos.md)
  and [pilot kit](docs/validation/pilot_kit.md). `python tools/build_demo_kit.py` builds the interview demo;
  `python tools/gate_scorecard.py g0 docs/validation/interviews` scores the notes against the gate.

## Development

```bash
pip install -e ".[dev]"
pytest -q                    # add --cov=pv for coverage
ruff check && mypy
```

CI runs lint, strict typing, the test matrix (ubuntu + macOS × Python 3.11–3.13) with a byte-identical
`results.json` check across the matrix, a wheel built and run from outside the checkout, ledger validation,
a weekly link check, and `pv drift` on every PR that touches `ledger/` or `cases/`. The static ledger site
(`pv ledger export`) deploys to GitHub Pages from the manual `ledger-site` workflow.

## Licences

Code: Apache-2.0 ([LICENSE](LICENSE)). Ledger data: CC BY 4.0 with OGL-Canada attributions ([ledger/LICENSE](ledger/LICENSE)).

*Nothing in this repository is tax, legal or investment advice. Policy parameters change often; check the
date and legal status of every value — the memo lists them all.*
