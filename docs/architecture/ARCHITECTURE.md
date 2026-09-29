# Architecture overview

*Version 0.1 — 2026-09-29. Decisions are recorded as ADRs in [`adr/`](adr/).*

## Shape

```mermaid
flowchart LR
  subgraph Ledger["Ledger (git, YAML, CC BY 4.0)"]
    R[records/*.yaml] --> S[JSON Schema + validators]
  end
  subgraph Kernel["Kernel (Python, pure functions)"]
    L[ledger loader<br/>as-of + legal-status filter] --> C[carbon value]
    L --> T[tax measures<br/>ITC + CCA]
    L --> E[emissions factors]
    C --> F[cash-flow + metrics]
    T --> F
    E --> M[emissions accounting]
    F --> B[breakeven + policy-state grid]
    F --> MC[seeded Monte Carlo]
  end
  CASE[cases/*.yaml<br/>user project case] --> L
  B --> OUT[results.json / cashflows.csv]
  MC --> OUT
  M --> OUT
  OUT --> MEMO[decision memo<br/>Markdown/HTML + provenance appendix]
  R -. two versions .-> DRIFT[pv drift: re-run saved cases,<br/>report flipped decisions]
  MON[optional source monitor<br/>AI-drafted diffs, human review] -. PR .-> R
```

## Components

| Component | Responsibility | Tech |
|---|---|---|
| `ledger/` | Versioned policy parameters with provenance and legal status | YAML, JSON Schema, git tags (`ledger-vYYYY.MM.N`) |
| `pv.ledger` | Load, validate, filter by `as_of` and minimum legal status, resolve overrides | pydantic v2 |
| `pv.carbon` | Realized carbon value path per facility/scenario (coverage, market, floor, CCfD, QC C&T) | numpy |
| `pv.tax` | ITC rate by in-service year and labour flag; eligible base net of assistance; CCA schedules | pure Python |
| `pv.cashflow` | Annual after-tax cash flows; NPV, IRR, payback; value stack | numpy + scipy (`brentq`) |
| `pv.robustness` | Breakeven carbon; discrete policy-state grid; seeded MC (vectorized) | numpy |
| `pv.emissions` | On-site and grid emissions, average vs marginal | pure Python |
| `pv.report` | Memo rendering (Markdown → HTML) and provenance appendix | Jinja2 |
| `pv.cli` | `validate`, `run`, `drift`, `ledger show` | Typer |
| CI | Tests, ledger validation, freshness SLA, link check, drift on ledger PRs | GitHub Actions |
| Static site (Phase 2) | Browsable ledger with history and citations | MkDocs Material → GitHub Pages |

## Key design rules

1. **No number without a source or a formula.** Ledger values cite sources; kernel values are pure functions of case + ledger + seed.
2. **Headline carbon price is never the default.** It is available only as a labelled upper-bound scenario (ADR-0005).
3. **Legal status is first-class.** An `announced` value is a scenario until it is `enacted` or `in_force`; the user chooses the trust threshold (ADR-0002).
4. **Determinism.** No network calls, clocks or LLMs in the valuation path. MC uses an explicit seed (ADR-0003).
5. **Zero operating cost.** No servers in the MVP (ADR-0004).

## Repository layout (target)

```
ledger/
  schema/record.schema.json
  records/
    federal/{carbon_benchmark.yaml, ct_itc.yaml, ccus_itc.yaml, ce_itc.yaml, cca_expensing.yaml, nir_factors.yaml}
    ab/{tier.yaml, tier_floor.yaml, tier_credit_obs.yaml}
    on/{eps.yaml, epu_obs.yaml}
    bc/{obps.yaml, credit_obs.yaml}
    qc/{spede.yaml, auction_obs.yaml}
    instruments/{ccfd_canada_alberta.yaml}
  CHANGELOG.md
src/pv/{__init__,ledger,carbon,tax,cashflow,robustness,emissions,report,cli}.py
src/pv/templates/memo.md.j2
cases/{golden_hp_qc.yaml, golden_hp_bc_covered.yaml, golden_ab_abatement_ccfd.yaml}
tests/{unit,property,golden,ledger}/
validation/   # research-phase models (frozen)
docs/
```
