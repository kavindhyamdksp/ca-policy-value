# PolicyValue CA

**What a decarbonization project is actually worth under Canadian policy as it really is.**

This repository holds the research, validation decision, product specification, architecture decisions and implementation plan for a Canadian climate-investment decision tool. It began as a broad *"Canada Climate CapEx Engine"* hypothesis. After research and quantitative testing it was **refocused**.

> **Decision (2026-09-29): REFOCUS.** Do not build the broad engine: RETScreen, SINAI, helloDarwin/BDO and ClearBlue already cover most of it. Build a small, gated MVP of **PolicyValue CA** instead. It is an open, source-cited ledger of the Canadian carbon-pricing and clean-economy tax parameters that decide industrial projects, plus a deterministic kernel. The kernel computes *realized* project value, the breakeven vs realizable carbon price, policy-regime robustness (including CCfDs) and a cited decision memo. → [DECISION.md](DECISION.md)

## Key findings

- **The math is solved.** RETScreen (free or ~CA$869/yr, 800k+ users) already does NPV/IRR plus a carbon input plus Monte Carlo. SINAI sells MACC with NPV/IRR and carbon-price scenarios.
- **The Canada-specific policy layer is not.** Credit prices (AB ~$20, ON ~$72–80, BC ~$65, fed OBPS ~$37.50, QC C&T ~$45) are far below the $95 headline. Sub-threshold sites outside QC face $0. The May 2026 reset replaced the $170-by-2030 path with $115 (2030) → $140 (2040), and added an AB floor from 2030 and CCfDs.
- **Policy terms flip decisions, but only in specific places.** They matter for covered industrial facilities and near-margin projects:
  - the carbon-value treatment is the largest NPV swing factor;
  - for AB abatement projects with breakevens of $54–117/t the answer depends entirely on the carbon assumption;
  - a CCfD moves P(NPV>0) from 0% to 76%.

  They do not change building or sub-threshold projects outside QC. → [quantitative validation](docs/research/04_quantitative_validation.md)
- **Broad incentive coverage is expensive and not decisive.** It would cost about C$200–350k/yr to maintain. The scoped ledger is ~55 records and ~85–130 h/yr. → [data feasibility](docs/analysis/data_feasibility.md)
- **Demand is the open risk.** All evidence so far is secondary. Gate G0 requires ≥12 interviews before most build effort.

## Repository map

| Path | Contents |
|---|---|
| [DECISION.md](DECISION.md) | Verdict, rationale, gates G0–G2, kill criteria |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Execution-ready plan: MVP, milestones, data sources, formulas, tests, acceptance criteria, dependencies, phases (living document) |
| [docs/research/](docs/research/) | Research files 01–04 with full source lists |
| [docs/analysis/competitor_gap_analysis.md](docs/analysis/competitor_gap_analysis.md) | What's solved, the gaps, differentiator tests, alternative concepts scored |
| [docs/analysis/data_feasibility.md](docs/analysis/data_feasibility.md) | Source catalogue, licensing, maintenance estimate, data risks |
| [docs/product/SPEC.md](docs/product/SPEC.md) | Product specification |
| [docs/architecture/](docs/architecture/) | Architecture overview and ADRs 0001–0007 |
| [validation/](validation/) | Reproducible research-phase model (`decision_sensitivity.py`), parameters with provenance, results |

## Reproduce the validation results

```bash
pip install numpy scipy pyyaml
cd validation && python3 decision_sensitivity.py > results.md
```

## Status

Pre-MVP. No production code has been written yet, by design. The next step is Phase 0 (problem validation interviews) in parallel with milestone M1–M2 (tooling and ledger). See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

*Nothing in this repository is tax, legal or investment advice. Policy parameters change often; check the dates and legal status of every value.*
