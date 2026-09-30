# User guide

This guide takes you from a fresh clone to a memo for your own project. Formulas and caveats are in
[methodology.md](methodology.md).

## 1. Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pv --version
```

Python 3.11–3.13. Everything runs offline; nothing you type leaves your machine.

## 2. Write a case

A case is one YAML file. Start from the closest golden case in `cases/` and edit it. Every field below is
optional unless marked **required**.

```yaml
case_id: my-project                # required; also the output folder name
as_of: 2026-10-15                  # required; ledger view date (records recorded after it are invisible)
min_legal_status: enacted          # announced | proposed | enacted | in_force — lower-status records become scenarios
facility:
  province: QC                     # required: AB | "ON" | BC | QC — always quote "ON"
  system: spede                    # tier | eps | bc_obps | fed_obps | spede | none
  covered: true                    # is the facility in an output-based pricing system?
  entity: taxable_corp             # taxable_corp | reit | crown | municipal | tax_exempt
  labour_requirements_met: true    # CT ITC labour rule
  tax_capacity: full               # full | none (no tax shield on operating flows or CCA)
project:
  in_service: 2027-06-30           # required; t=0 (capex, available-for-use date); year t is in_service.year + t
  life_years: 20                   # required
  capex: [{year: 0, amount: 3500000}]   # required; year relative to t=0
  technology_class: heat_pump_process   # required; looked up in fed.ct_itc.eligibility_classes
  itc_measure: ct                  # ct | ccus | ce | none
  itc_eligible_share: 0.85         # share of capex eligible for the ITC (default 1.0)
  cca_class: "43.1"                # class if clean-tech eligible (expensing window applies to 43.1/43.2/53)
  cca_class_if_ineligible: "8"     # class used when the ITC claim is denied
  other_assistance: 0              # grants etc.; reduces the ITC base and UCC
  energy_deltas: {natural_gas_gj: -50824, electricity_mwh: 4000}   # per year; negative = avoided
  opex_delta: 30000                # $/yr, + = cost (escalates)
  covered_emissions_delta_t: null  # t/yr covered emissions change; default = gas GJ × gas EF
prices:
  natural_gas_gj: 8.8              # your delivered tariff ex-carbon, $/GJ (required if gas changes: no ledger default yet)
  electricity_mwh: 60.5            # your tariff, $/MWh (default: ledger ref.electricity.large)
  escalation: 0.02                 # energy and opex escalation
  inflation: null                  # for credit prices held flat in real terms (default: escalation)
finance: {discount_rate: 0.08, itc_receipt_lag_years: 1, tax_rate: null}   # tax_rate default: ref.tax.corporate
policy:
  credit_price_scenario: base      # low | base | high | upper_bound_headline (labelled, never a default)
  floor: auto                      # auto (by legal status) | as_announced | half | none
  itc_granted: null                # null = granted unless the class is not_listed in NRCan guidance
  ccfd: {strike: 85, term_end: 2040, volume_share: 1.0}
  grid_factor: average             # average (ledger/override) | marginal (needs marginal_grid_ef_g_kwh)
  marginal_grid_ef_g_kwh: null
robustness:
  grid: [floor_status, itc_granted, ccfd, coverage, credit_scenario]   # any subset
  monte_carlo:
    draws: 10000
    seed: 20260929
    regimes:                       # probabilities must sum to 1; changes apply from from_year (default: all years)
      as_announced: {p: 0.55, floor_scale: 1.0}
      half_floor:   {p: 0.30, floor_scale: 0.5}
      rollback:     {p: 0.15, market_value: 15, floor_scale: 0.0}
    shocks: {gas_sigma: 0.30, elec_sigma: 0.15, credit_sigma: 0.35, capex_triangular: [0.9, 1.0, 1.3]}
    itc_probability: null          # default from eligibility: likely 0.9, case_by_case 0.6, not_listed 0.1
overrides:
  - {record: ab.tier.credit_obs, value: {base: 25}, reason: "broker quote 2026-10-10"}
```

### Overrides

Any ledger record can be overridden. `reason` is mandatory, and every override appears in the memo's
warnings and provenance appendix. Use overrides for licensed prices (ClearBlue, Argus…) — they are never
committed to the ledger — and for values the ledger does not yet carry:

| Missing from ledger v2026.10.0 | Supply instead |
|---|---|
| `fed.nir.grid_ef` (average grid intensity) | `overrides: [{record: fed.nir.grid_ef, value: {QC: 2.5}, reason: ...}]`, or `grid_factor: marginal` |
| `ref.gas.delivered` | `prices.natural_gas_gj` |
| `fed.ce_itc.rate` (only for `itc_measure: ce`) | override `fed.ce_itc.rate` |
| CCA expensing phase-out for in-service 2030–2033 | override `fed.cca.expensing`, e.g. `{2031: 0.5}` |
| CT ITC labour rate after 2033 | override `fed.ct_itc.labour_rate` |

If a required value is missing, `pv run` stops and names the record or field to supply.

## 3. Run and read the memo

```bash
pv run my-project.yaml             # → out/my-project/{memo.html, memo.md, results.json, cashflows.csv}
pv run cases/*.yaml --out out      # several cases → out/<case_id>/
pv run my-project.yaml --ledger-ref ledger-v2026.10.0   # value against a released ledger tag
```

The memo sections:

1. **Answer** — GO / NO-GO / DEPENDS-ON. With a policy-state grid, GO means GO in every state, NO-GO in
   none; otherwise DEPENDS-ON, with the smallest sets of conditions that guarantee GO.
2. **Value stack** — NPV without policy, then adding carbon value, the ITC, CCA timing and the CCfD in that
   order (interactions are non-additive, so order matters).
3. **Breakeven vs realizable band** — the flat carbon price the project needs, against the levelized
   low / base / high realizable value and the headline upper bound.
4. **Robustness** — the grid table and Monte Carlo percentiles.
5. **Emissions** — on-site avoided, grid added, net, and abatement cost.
6. **Assumptions, overrides, warnings** — including any announced/proposed record used in the base case,
   any override, and any record past its freshness SLA.
7. **Provenance appendix** — every ledger record used, with value, legal status, source links and retrieval dates.
8. **Not-advice notice.**

`results.json` holds the same content in machine-readable form; `cashflows.csv` holds the annual base-case
cash flows by component (open it in Excel).

## 4. Keep decisions current: `pv drift`

```bash
pv drift --from ledger-v2026.10.0                   # released tag → your working-tree ledger
pv drift --from ledger-v2026.10.0 --to ledger-v2026.11.0 --cases my-cases/ --json drift.json
pv drift --from old-ledger-dir/ --to new-ledger-dir/ --fail-on-flip
```

Drift re-runs every case in `--cases` under both ledgers and lists changed records, NPV deltas, and cases
whose answer or base-case decision flipped, with the changed records each case used. Each run is evaluated
as of the later of the case's `as_of` and the ledger's latest recording, so new records are visible.

## 5. Inspect and validate the ledger

```bash
pv ledger show                       # all records with legal status, value, unit, days left before stale
pv ledger show fed.ct_itc.rate_schedule
pv validate                          # exits 1 on any error; --lenient reports stale records as warnings
pv validate --as-of 2026-09-29 --cases cases
```

To add or update a record, follow [ledger/RECORD_FORMAT.md](../ledger/RECORD_FORMAT.md): every number must
come from a source you fetched, with a retrieval date, a locator and a ≤25-word excerpt; `enacted`/`in_force`
records need a primary (legal or government) source. Open a PR: CI validates the ledger and posts the drift
report so reviewers see the decision impact.

## 6. Use from Python

```python
from pv.case import load_case
from pv.ledger import load_ledger
from pv.results import evaluate

res, model, view = evaluate(load_case("cases/golden_hp_qc.yaml"), load_ledger())
print(res["decision"], res["carbon"]["breakeven_flat"])
```

## Limits (MVP)

Industrial projects in AB, ON, BC and QC plus federal measures only. No grant or utility-rebate data, no
buildings, no credit-price forecasts (prices are dated observations or your inputs), no energy simulation.
Credit-use limits and long/short positions are modelled simply (fund-price cap only). See
[methodology.md](methodology.md#caveats).
