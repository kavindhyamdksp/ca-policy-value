# Product specification: PolicyValue CA

*Version 0.1 — 2026-09-29. Status: pre-MVP, gated by [DECISION.md](../../DECISION.md).*

## 1. One-liner

**What a decarbonization project is actually worth under Canadian policy as it really is.** PolicyValue CA pairs an open, source-cited ledger of the Canadian carbon-pricing and clean-economy tax parameters that decide industrial projects with a transparent engine. The engine turns them into realized project value, the breakeven carbon price and robustness to policy change.

## 2. Problem

Analysts evaluating industrial abatement projects in Canada face a small number of policy terms that decide GO/NO-GO. Those terms are hard to get right and change every few weeks:

- **Carbon value is not the headline price.** A covered facility realizes the credit-market price, which in 2026 is about $18–20 in AB, ~$72–80 in ON, ~$65 in BC, ~$37.50 under the federal OBPS and ~$45 under QC C&T. That price sits under system-specific rules, a 2030 AB floor that is announced but not yet regulated, and optional CCfDs. A site below threshold realizes $0 outside Quebec.
- **Clean-economy tax measures are conditional cash flows,** not a flat 30%. The rate depends on the available-for-use date, labour compliance and eligibility (often case-by-case). The credit base is reduced by other assistance, and CRA timing adds delay. Expensing windows interact with all of this.
- **Policy risk is real and priced by investors,** but it is not represented in the tools analysts use. A CCfD's value *is* the removal of that risk.
- **Assumptions must be defended** to investment committees, CRA auditors, P.Eng sign-off, funders and CCfD counterparties. Today they are rebuilt by hand in Excel on each engagement, often from stale sources. For example, GMF guidance still cites the superseded $170-by-2030 path.

Evidence: [research 01–04](../research/), summarized in the [gap analysis](../analysis/competitor_gap_analysis.md).

## 3. Users and jobs-to-be-done

| Persona | Context | Job to be done | Frequency |
|---|---|---|---|
| **Facility / corporate analyst at a covered emitter** (AB, ON, BC, QC) | Compliance planning, capital planning, FIDs | "Tell me the realized carbon and tax value of this project at my facility, the breakeven carbon price, and how that changes under policy scenarios, so I can defend it at investment committee." | Several cases per quarter |
| **Consultant / ESCO / engineering firm** | Feasibility studies, federal LCCA, GMF studies, client decarbonization plans | "Give me a current, cited set of Canadian policy parameters and a reproducible calculation I can drop into my deliverable without re-researching each time." | Continuous across clients |
| **CCfD / CCUS / clean-electricity developer** | CGF/CCfD negotiations, ITC-dependent project finance | "What strike price and term do I need, and how much does the CCfD raise P(NPV>0)?" | Per deal |
| *Secondary:* policy analysts, NGOs, researchers | Policy evaluation (e.g., CCI's call for transparent effective-price analytics) | "An open, versioned record of what the parameters were on any date." | Ad hoc |

**Explicit non-users (MVP):** building owners and REITs, SMEs looking for grants, carbon accountants, and lenders assessing portfolios.

## 4. Scope

### In scope (MVP)
- **Jurisdictions:** federal, AB, ON, BC, QC.
- **Levers:**
  - industrial carbon pricing: headline path, system rules, credit-price observations, AB floor, CCfD;
  - QC cap-and-trade;
  - Clean Technology ITC, CCUS ITC and Clean Electricity ITC (rates, phase-downs, labour rule, eligibility classes);
  - CCA Class 43.1/43.2/53 immediate expensing window;
  - grid emission factors (average; marginal as user input) and the natural-gas emission factor.
- **Calculations:**
  - project cash flows and NPV/IRR/payback;
  - a policy value stack (waterfall);
  - breakeven carbon price vs realizable band;
  - discrete policy-state robustness ("GO in k of n states");
  - optional seeded Monte Carlo over user-stated regime probabilities and price shocks;
  - on-site and net system emissions.
- **Outputs:** a decision memo (Markdown + HTML) with a provenance appendix; machine-readable results (JSON/CSV).
- **Decision drift:** re-run saved cases against a new ledger version and report which decisions or values changed and why.

### Out of scope (MVP), with reason
- Grant/utility-rebate discovery and a broad incentive database: solved by others, and noise at industrial scale.
- MACC portfolio optimization and IC workflow: SINAI.
- Credit-price forecasting: ClearBlue. Prices are dated observations or user inputs.
- Buildings and BEPS: policy terms don't flip the decision; the segment is crowded.
- Engineering simulation of energy savings: the user supplies energy deltas (RETScreen, vendor data).
- Hosted SaaS, accounts, multi-tenant UI.
- CFR, ÉcoPerformance, NS/SK/NB/NL: Phase 2.

## 5. Functional requirements

### FR-1 Ledger
1. Each parameter is a **record** with:
   - `id`, `jurisdiction`, `instrument`, `parameter`, `value` (scalar, time series or table), `unit`, `currency_basis` (nominal/real, year)
   - `effective_from`, `effective_to`
   - `legal_status` ∈ {announced, proposed, enacted, in_force, superseded, repealed}
   - `sources[]`: url, title, publisher, published date, retrieved date, excerpt/locator, source type (primary legal / primary gov / secondary)
   - `confidence` ∈ {high, medium, low}; `eligibility_confidence` for technology classes
   - `notes`, `reviewer`, `recorded_at`, `supersedes`
2. The ledger is **bitemporal.** "What was believed on date X about value in year Y" must be answerable from git history plus `recorded_at`.
3. Validation: schema, units, date consistency, no overlapping effective periods for the same key and status, every record has ≥1 source, and a primary source is required for `enacted`/`in_force`.
4. Freshness: each record family has a review SLA (e.g., credit prices 100 days; statutes 180 days). CI flags breaches.

### FR-2 Case definition (user input, YAML)
Facility:
- province, system, covered (bool), position (short/long/neutral), taxable (bool), entity type, labour-requirement compliance (bool)

Project:
- capex schedule, in-service date, life
- energy deltas by carrier (GJ gas, MWh electricity), other opex, emissions deltas (computed or supplied)
- technology class (maps to ITC/CCA eligibility), eligible-share override

Finance:
- discount rate, escalation, tax-rate override, ITC receipt lag

Policy view:
- ledger version/as-of date
- minimum legal status to trust (e.g., treat `announced` as a scenario, not base)
- credit-price scenario set, optional CCfD (strike, volume, term), regime probabilities

Overrides: any ledger value can be overridden, with a mandatory `reason`. Overrides are shown in the memo.

### FR-3 Kernel
- **Realized carbon value per tonne by year.** Handles:
  - coverage (none → $0 outside QC);
  - system market price, with scenario low/base/high;
  - the floor (from its effective date, legal-status aware);
  - CCfD as `max(strike, market)` on contracted volume and term, market price beyond;
  - QC C&T for all gas users;
  - a headline scenario, available but labelled as an *upper bound*, never as the base.
- **Tax measures:** ITC rate by in-service year and labour flag; eligible share; reduction of the ITC base and UCC for other assistance; refundable timing lag; CCA expensing window vs normal declining-balance classes; non-taxable entities get no ITC or CCA.
- **Metrics:** NPV, IRR, discounted and simple payback, policy value stack, breakeven flat carbon price, and the realizable carbon band for the facility.
- **Robustness:** a discrete policy-state grid (e.g., floor as announced / half / none × ITC granted / denied × CCfD yes / no) reporting the share of GO states. Optional Monte Carlo with a fixed seed, reporting P10/P50/P90 and P(NPV>0).
- **Emissions:** on-site change; grid change at average (ledger) and marginal (user) factors; lifetime tonnes; $/t on a cost-of-abatement basis.

### FR-4 Outputs
The decision memo has these sections:
1. Answer: GO / NO-GO / DEPENDS-ON, with the deciding policy terms.
2. Value stack waterfall.
3. Breakeven vs realizable carbon band.
4. Robustness table.
5. Emissions.
6. Assumptions and overrides.
7. **Provenance appendix:** every ledger record used, with its value, legal status, source links and retrieved date, plus warnings for stale or non-in-force records.
8. Not-advice notice.

Results are also emitted as JSON (schema-versioned) and CSV cash flows.

### FR-5 Decision drift
`pv drift` re-runs all saved cases under `cases/` against two ledger versions and lists changed records, changed values and **flipped decisions**. It is suitable for CI on each ledger PR, so every ledger change shows its decision impact.

## 6. Non-functional requirements

| Area | Requirement |
|---|---|
| Transparency | Pure, documented deterministic functions. Every number in a memo traces to an input, a ledger record, or a formula in the code. |
| Reproducibility | Same case + same ledger version + same seed → byte-identical JSON results. Ledger versions are git tags. |
| Provenance | 100% of ledger records have sources. Memos list every record used. |
| Cost | $0 hosting in MVP (GitHub, GitHub Actions, GitHub Pages). No paid data. |
| Maintainability | Ledger maintenance ≤ 15 h/month; code ≤ ~3k LOC in the kernel; minimal dependencies. |
| Performance | A single case with a 64-state grid runs in < 1 s. 10k-draw MC runs in < 10 s on a laptop (vectorized numpy). |
| Liability | Outputs are scenario analyses, not tax or investment advice. Eligibility is expressed as confidence levels. |
| Accessibility | CLI + Markdown/HTML. No proprietary runtime. Works offline. |

## 7. Use of AI

- **Where it adds value:** monitoring source pages for changes and drafting a proposed ledger diff (value, dates, excerpt, legal-status change) for **human review**. Optionally, drafting the narrative section of a memo from the computed JSON, which is clearly labelled.
- **Where it is not used:** any number in the valuation path, eligibility determinations, or auto-merging ledger changes. Valuation is deterministic code.
- AI features are optional and off by default; the product is fully functional without them.

## 8. Success metrics

| Metric | Target by G1 |
|---|---|
| Design partners who ran a real case | ≥ 3 |
| Partners reporting the memo changed or de-risked a decision | ≥ 2 |
| Ledger records past freshness SLA | 0 for 60 consecutive days |
| Maintenance hours/month | ≤ 15 |
| Reproducibility test failures | 0 |
| External citations or forks of the ledger | ≥ 3 (a signal for the open-ledger wedge) |

## 9. Open questions (to resolve at G0)

1. Do covered-facility analysts value carbon at headline, at market price, or leave it out (ConocoPhillips-style breakevens)? The memo must support the breakeven framing either way.
2. Is CCfD bid/strike analysis the sharpest wedge, or annual compliance-driven project screening?
3. Would consultants adopt an open ledger in client deliverables, and would they contribute corrections?
4. Is there an institutional home for the ledger (CCI, Clean Prosperity, a university energy-modelling hub) to share maintenance?
5. What is the minimum acceptable ITC eligibility treatment for a tax reviewer to accept the memo as an input?
