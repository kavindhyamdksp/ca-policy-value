# CLAUDE.md — PolicyValue CA working brief

Distilled once from IMPLEMENTATION_PLAN.md §0–§6, ADR-0001..0007, SPEC §4–§6 and validation/.
Later sessions: read this + PROGRESS.md only. Do not re-read docs/research/01–04.

## Scope (ADR-0001) and non-goals
- Realized policy value for **industrial** decarbonization projects, federal + AB/ON/BC/QC:
  industrial carbon pricing (credit market, fund cap, AB floor, CCfD, QC C&T), CT/CCUS/CE ITCs,
  CCA 43.1/43.2/53 expensing, grid/gas emission factors, policy-regime robustness, decision drift.
- NOT: web app/server/DB, grant or utility-rebate data, buildings/BEPS, MACC workflow,
  credit-price forecasting, energy simulation, LLM calls in code, NS/SK/CFR (Phase 2).
- Outputs are scenario analyses, not tax/investment advice. Ledger CC BY 4.0, code Apache-2.0,
  no proprietary price data committed (users inject licensed prices via overrides).

## Kernel formulas (plan §4) — t = 1..N operating years, y(t) calendar year, τ tax, r discount
- Timing convention: t=0 is `project.in_service` (capex spent, available for use); y(t) = in_service.year + t.
  Oracle: in_service 2026-12-31 → operating years 2027..2046, N=20.
- **Carbon v_t** (ADR-0005):
  - not covered and province ≠ QC → 0.
  - QC (covered or not) → C&T path: last auction settlement × (1+g)^(y−obs_year), g = reserve escalation.
  - covered AB/ON/BC/fed: m = min(market_s(y), fund(y)); market base = latest obs held flat real
    (validation_v1: flat nominal) for AB; ratio-to-compliance-price for ON/BC/fed. low = lowest obs in
    range, high = fund/compliance price (derived band, never invented).
  - floor: if floor record status ≥ min_legal_status and y ≥ floor.effective_from → m = max(m, floor(y));
    otherwise the floor is only a grid/scenario dimension.
  - CCfD: y ≤ term_end → v = vs·max(strike, m) + (1−vs)·m; else v = m.
  - `upper_bound_headline`: v = headline(y) (fed benchmark path), always labelled.
  - C_t = ΔE_covered · v_t; ΔE = gas_GJ_avoided × EF_gas unless supplied.
- **Tax**: ρ = schedule(in_service year); labour not met → reduced rate; 0 if entity ineligible.
  ITC = ρ·s_elig·(capex − assistance), received at t = lag. UCC U = capex − ITC − assistance.
  Expensing-eligible class in window → CCA_1 = U·expensing_pct(y), rest DB at class rate;
  else DB with half-year rule. validation_v1 + ineligible → Class-8-like 20% DB (10% in yr 1).
  Non-taxable / tax_capacity none → no tax on flows, no CCA shield, ITC only if refundable & eligible.
- **Cash flow**: CF_0 = −capex_0; CF_t = (1−τ)(S_gas + C − E_el − O) + τ·CCA + ITC·[t=lag].
  Gas, electricity, opex escalate (1+e)^(t−1); carbon path does not (except QC path).
  NPV at r; IRR brentq on [−0.99, 3] (null + warning if multiple sign changes/roots); simple & discounted payback.
  Value stack sequential: base(no policy) → +carbon → +ITC → +CCA timing → +CCfD (order noted).
- **Robustness**: breakeven flat nominal p* with NPV=0 vs band [low, base, high, headline] (levelized at r).
  Grid: Cartesian product of chosen dims; NPV + GO per state; GO share; minimal GO conditions.
  MC: numpy default_rng(seed), vectorized; regimes from user probabilities; lognormal mean-preserving
  persistent shocks exp(N(0,σ)−σ²/2) on gas, elec, credit; shock hits MARKET price, then floor/CCfD;
  triangular capex; Bernoulli ITC eligibility p from eligibility_confidence (likely .9, case_by_case .6,
  not_listed .1). Report mean, P10/P50/P90, P(NPV>0).
- **Emissions**: on-site gas_GJ×EF_gas; grid MWh×EF_grid (avg ledger / marginal user); net annual,
  lifetime; abatement cost = −NPV / discounted tonnes (on-site and net bases).

## Ledger record schema (SPEC FR-1, ADR-0002)
`id, jurisdiction, instrument, parameter, value (scalar | {year: v} series | table), unit,
currency_basis, effective_from, effective_to, legal_status ∈ {announced, proposed, enacted, in_force,
superseded, repealed} (+ `observation` for market/statistical data), sources[] {url, title, publisher,
published, retrieved, locator, excerpt, source_type ∈ primary_legal|primary_gov|secondary},
confidence ∈ {high, medium, low}, eligibility_confidence (tech classes), freshness (SLA family),
notes, reviewer, recorded_at, supersedes`.
- Validators (§5.4): schema; units whitelist; date logic; no overlapping periods per (id, status);
  ≥1 source; primary source for enacted/in_force; retrieved within SLA (credit prices 100 d,
  statutes 180 d); province codes guarded. URL reachability weekly, non-blocking.
- Loader: `as_of` (recorded_at ≤ as_of), `min_legal_status`, overrides (reason mandatory, never committed).

## Conventions
- src layout; dist `policyvalue-ca`; import `pv`; CLI `pv` (Typer); Python ≥3.11; hatchling.
- Deps only (plan §6): numpy, scipy, pydantic v2, PyYAML, jsonschema, Jinja2, markdown-it-py, Typer;
  dev: pytest, hypothesis, ruff, mypy, pre-commit, pytest-cov.
- YAML: always quote the key `"ON"` (bare ON parses as boolean true).
- Kernel pure: no network, no clock, no LLM in valuation. results.json carries sha256 of case+ledger+seed.
- `conventions: validation_v1` is test-only (oracle simplifications: flat nominal credit prices,
  20% DB when clean-tech ineligible, params floor table).
- The oracle `validation/` is frozen — never edit. Tests may import it read-only.
- Local venv: `.venv` (Python 3.14). Commands: `pytest -q -x --no-header -p no:cacheprovider`,
  `ruff check --quiet`, `mypy --no-error-summary src | head -40`. /usr/bin/grep, not `grep`.
- Git: branch `mvp`, commit per green checkpoint with PROGRESS.md, push per milestone, one PR at end.

## Oracle targets (validation/results.md; NPV $M, tolerance ±$5k NPV, ±$1/t breakeven)
Example 1 — process HP: capex 3.5M, s_elig 0.85, gas 50,824 GJ/yr (43,200/0.85), elec 4,000 MWh,
O&M 30k, EF 0.05, r 8%, esc 2%, lag 1, tax QC .265 BC .27 AB .23 ON .265; gas QC 8.8 BC 10.0;
elec large ¢/kWh QC 6.05 BC 8.42. ITC "no" also drops expensing (20% DB).
| Case | none | market | headline | IRR mkt | breakeven |
|---|---|---|---|---|---|
| QC ITC yes | +0.70 | +0.70 | +0.70 | 11.5% | 31 |
| QC ITC no | −0.13 | −0.13 | −0.13 | 7.5% | 76 |
| BC ITC yes | −0.85 | +0.66 | +1.37 | 11.5% | 47 |
| BC ITC no | −1.68 | −0.17 | +0.54 | 7.3% | 92 |
QC path 45.11×1.05^(y−2026); BC market = headline×0.68.
Example 3 — AB abatement 50 kt/yr, 20 y, opex +1.0M/yr escalated, τ .23, full expensing, no ITC:
at $25M capex: breakeven 75; Headline +17.63; Market $20 no floor −20.86; Market + 2030 floor −2.79;
CCfD $85 to 2040 +6.00. Levelized: 122 / 20 / 68 / 91 $/t.
Headline path: 2026 95, 2027–29 100, 2030 115, +3/yr to 2035 130, linear to 2040 140, flat after.
AB floor 2030..2040: 60,63,67,71,75,80,85,90,95,100,110 (0 before 2030); market = max(20, floor).
MC (seed 20260929, n 20k): Ex3 $25M merchant P(NPV>0) 0%, with CCfD 76% (reference, not a DoD gate).

## Definition of done (plan §2.4)
1. Oracle: params injected as overrides + `validation_v1` → Ex1 (QC ITC y/n, BC covered market) and
   Ex3 $25M (4 carbon cases): NPV ±$5k, breakeven ±$1/t.
2. Ledger: 100% schema-valid; enacted/in_force have ≥1 primary source; 0 stale at release.
3. Provenance: memo lists 100% of records used (value, status, URL, retrieved); warns on
   announced/proposed in base, overrides, stale.
4. Reproducibility: byte-identical results.json across runs and OS/Python matrix (ubuntu, macOS; 3.11–3.13).
5. Drift: `pv drift --from --to` lists changed records/value deltas/flips; ab.tier.floor
   announced→in_force flips golden_ab_abatement_ccfd.
6. Quality: ≥90% line coverage on src/pv excluding cli/report; mypy strict; ruff clean.
7. Performance: 3-dim grid case < 1 s; 10k-draw MC < 10 s.
8. Docs: `pip install -e . && pv run cases/golden_hp_qc.yaml` → HTML memo in < 10 min via README.
