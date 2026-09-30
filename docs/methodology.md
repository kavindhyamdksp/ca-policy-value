# Methodology

How PolicyValue CA turns a case and the ledger into a decision. Every number in a memo is a ledger record,
a case input, or one of the formulas below (implemented in `src/pv/`). Decisions: [ADR-0002](architecture/adr/ADR-0002-bitemporal-git-ledger.md)
(ledger), [ADR-0003](architecture/adr/ADR-0003-deterministic-kernel-no-llm-in-valuation.md) (kernel),
[ADR-0005](architecture/adr/ADR-0005-carbon-value-model.md) (carbon value).

## Notation and timing

- t = 0 is the in-service (available-for-use) date: capex is spent and ITC/CCA rules are read for
  `in_service.year`. Operating years t = 1..N fall in calendar years y(t) = in_service.year + t.
- r is the nominal discount rate, τ the combined corporate tax rate, e the energy/opex escalation.
- All values are CAD nominal.

## 1. Ledger view

A run sees the ledger **as of** `case.as_of` (records with `recorded_at ≤ as_of`) and trusts records whose
`legal_status` is at or above `min_legal_status` (announced < proposed < enacted < in_force; observations
always pass; superseded/repealed never do). Records below the threshold are used only as labelled scenarios
(grid dimensions, bands, the headline upper bound). Overrides replace a record for this run only and are
reported. A record is **stale** when `as_of − retrieved` exceeds its freshness SLA (statute/guidance 180 days,
announcement and market observation 100 days, annual statistic 400 days).

Sparse year series (e.g. the national benchmark path) are interpolated linearly between stated years and
held flat beyond the last one. Rate schedules (ITC, expensing) use the value for the latest stated year ≤ y.

## 2. Realized carbon value v_t (`pv.carbon`)

| Facility | v_t |
|---|---|
| Not covered, outside QC | 0 in every scenario, including the headline upper bound |
| QC (covered or not — C&T reaches all gas users via distributors) | latest auction settlement × (1+g)^(y−y_obs), g = reserve escalation (5% real, plus inflation) |
| Covered AB/ON/BC/fed OBPS | m = min(market_s(y), fund(y)); floor; CCfD (below) |

- **Market, AB TIER** (`flat`): latest credit observation held flat in real terms: obs × (1+inflation)^(y−y_obs).
  Low = lowest observed price.
- **Market, ON EPS / BC OBPS / fed OBPS** (`ratio`): ratio = observed price ÷ the system's compliance price in
  the observation year; market(y) = ratio × compliance price(y). Low = the lowest observed ratio.
- **High** = the fund/compliance price itself (the cap on realizable value). Nothing in the band is invented:
  low/base/high all come from dated observations or legal price schedules.
- **Fund cap**: the system's trusted compliance or fund price series; if none is trusted, the national
  benchmark is used and a warning is issued.
- **Floor** (AB TIER minimum transfer price): if the floor record passes `min_legal_status` and
  y ≥ effective year, m = max(m, floor(y)). Otherwise it is only a grid/scenario dimension
  (`as_announced`, `half`, `none`).
- **CCfD**: for y ≤ term_end, v = s·max(strike, m) + (1−s)·m on contracted volume share s; after the term, v = m.
- **Headline** (`upper_bound_headline`): v = national benchmark path. Always labelled an upper bound.

Carbon cash flow C_t = ΔE · v_t, where ΔE is avoided covered tonnes per year: the supplied
`covered_emissions_delta_t`, else gas GJ avoided × EF_gas (province-specific NIR factor).

## 3. Tax measures (`pv.tax`)

- ITC rate ρ = schedule(in_service year) for the chosen measure (CT by default). If labour requirements are
  not met, the ledger's reduced rate applies. ρ = 0 if the entity type is ineligible for the measure.
- Eligibility of the technology class comes from NRCan's CT property guidance (`likely`, `case_by_case`,
  `not_listed`). By default the claim is granted unless the class is `not_listed`; set `policy.itc_granted`
  to assert your own view, and use the `itc_granted` grid dimension to test it.
- ITC = ρ · s_elig · (capex − other assistance), received at t = lag.
- UCC U = capex − ITC − assistance. If the claim is granted and the class (43.1 or 53; the fetched source does not
  name 43.2) is in the immediate-expensing window for the in-service year: CCA_1 = U · expensing%, remainder by declining balance
  at the class rate with the half-year rule. Otherwise declining balance at `cca_class_if_ineligible`.
- Non-taxable entities or `tax_capacity: none`: no tax on operating flows and no CCA shield; the ITC is kept
  only where the entity is eligible (the CT/CE ITCs are refundable for eligible entities).

## 4. Cash flow and metrics (`pv.cashflow`)

- CF_0 = −capex_0 (later capex items at their years).
- CF_t = (1−τ)·(S^gas_t + C_t − E^el_t − O_t) + τ·CCA_t + ITC·[t = lag], with gas savings, electricity cost and
  opex escalated by (1+e)^(t−1). Carbon paths carry their own escalation (§2).
- NPV at r. IRR by Brent's method on [−99%, 300%], reported as null with a warning when cash flows have no
  sign change or more than one root. Simple and discounted payback, interpolated within the crossing year.
- **Value stack**, sequential: base without policy (no carbon, no ITC, ineligible CCA class) → + carbon →
  + ITC → + CCA timing (eligible class and expensing) → + CCfD. The order is reported because interactions
  are non-additive.

## 5. Robustness (`pv.robustness`)

- **Breakeven**: the flat nominal p* with NPV = 0 (exact, since NPV is linear in a flat carbon price),
  compared with the realizable band levelized at r: Σ v_t d_t / Σ d_t with d_t = (1+r)^−t.
- **Policy-state grid**: the Cartesian product of the chosen dimensions (`floor_status`, `itc_granted`,
  `ccfd`, `coverage`, `credit_scenario`); dimensions that cannot apply (e.g. a floor outside AB) are dropped.
  Reports NPV and GO per state, the GO share, and the minimal GO conditions: the smallest partial
  assignments under which every remaining state is GO (prime implicants).
- **Answer**: GO if every grid state is GO, NO-GO if none is, DEPENDS-ON otherwise (without a grid: the
  base-case NPV sign). `base_case` in results.json is always the base-case sign.
- **Monte Carlo** (numpy `default_rng(seed)`, vectorized over draws): regimes drawn from the user's
  probabilities, each able to scale or replace the market price and scale the announced floor from a given
  year; a persistent, mean-preserving log-normal shock exp(N(0,σ) − σ²/2) on the **market** price, after which
  the fund cap, floor and CCfD strike are applied; independent log-normal shocks on gas and electricity;
  triangular capex multiplier; Bernoulli ITC eligibility with p from the eligibility map (likely 0.9,
  case-by-case 0.6, not listed 0.1) unless overridden. ITC and UCC scale with the capex draw. Reports mean,
  P10/P50/P90 and P(NPV > 0). With all σ = 0, one regime, degenerate capex and p ∈ {0, 1}, the MC mean equals
  the deterministic NPV (property-tested).

## 6. Emissions (`pv.emissions`)

On-site avoided t/yr = −gas GJ × EF_gas (or the supplied covered delta). Grid added t/yr = MWh × EF_grid / 1000
(g/kWh), average from the ledger or an override, marginal from user input. Net = on-site − grid; lifetime =
× N. Abatement cost = −NPV / Σ tonnes_t d_t, on the on-site and net bases (negative = the project pays).

## 7. Reproducibility

The kernel reads no clock and makes no network calls; the CLI passes dates in. `results.json` is serialized
with sorted keys and rounded values and carries `run_hash` = sha256(case digest | ledger content digest |
seed). CI compares the results.json SHA-256 across ubuntu/macOS × Python 3.11–3.13.

## 8. Validation against the research oracle

`conventions: validation_v1` (test-only) reproduces the simplifications of `validation/decision_sensitivity.py`:
credit prices flat nominal (inflation 0), QC escalation 5% nominal, and a 20% declining-balance class with the
half-year rule when clean-tech is ineligible. With `validation/params.yaml` injected as overrides, the kernel
reproduces Example 1 (QC with/without ITC; BC not covered/market/headline) and Example 3 at $25M (all four
carbon cases) to within $0.01 of NPV and 10⁻¹² $/t of breakeven (tolerances: $5k, $1/t). The seeded Monte
Carlo reproduces the oracle's Example 3 distribution (with the $85 CCfD, P(NPV > 0) ≈ 76%).

## Caveats

- **Credit prices are sparse, dated observations**, several from secondary sources citing licensed data.
  Supply licensed prices locally through overrides.
- **In-force provincial schedules vs the announced national path.** Ontario's EPS and BC's OBPS in-force
  compliance schedules rise to $170 in 2030, above the May 2026 national trajectory ($115 in 2030), and no
  alignment was recorded at release. The kernel follows the in-force law, so ON/BC market values and the
  "high" band can exceed the headline benchmark. Treat this as a legal-status effect, and watch `pv drift`.
- **AB fund price** is in force for 2026 only; later years are announced. At `min_legal_status: enacted` the
  2026 price is held flat as the cap.
- **ITC eligibility is a judgement.** Process and waste-heat heat pumps and electric boilers are not listed in
  NRCan's guidance at release. Obtain tax advice; model the uncertainty with the grid and MC.
- **Unverified at release** (user input required): average grid intensity, delivered gas prices, the Clean
  Electricity ITC rate, and the 2030–2033 expensing phase-out percentages.
- Credit-use limits, long/short positions, banking and offsets are not modelled (a fund-price cap only).
- Capex spread over several years is treated as available for use at t = 0 for ITC/CCA purposes.
- Scenario analysis only; not tax, legal, accounting or investment advice.
