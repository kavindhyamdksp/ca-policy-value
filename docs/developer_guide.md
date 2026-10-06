# Developer guide

How the code is organized, where policy lives, and how to extend it without redesign. Formulas are in
[methodology.md](methodology.md); decisions in [architecture/](architecture/).

## Setup and checks

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q --cov=pv          # unit, property, oracle, golden, ledger, contract, tool tests (coverage gate 90%)
ruff check && ruff format --check
mypy                        # strict, src/ and tools/
pv validate --cases cases
```

CI (`.github/workflows/ci.yml`) runs the same, plus the OS × Python matrix with a byte-identical
`results.json` check, a wheel built and run from outside the checkout, and the tools job. `drift.yml` posts
the decision impact of every PR that touches `ledger/` or `cases/`. `freshness.yml` runs weekly: it lists
records due within 30 days (`pv ledger due`), reports the 60-day SLA history (`pv ledger sla`) and fails once
any record is stale, so a quiet repository still notifies the maintainer.

## Layers and where policy lives

| Layer | Holds | Rule |
|---|---|---|
| `ledger/records/**.yaml` | Every policy **value**, with sources, legal status and dates | No number without a fetched source ([RECORD_FORMAT.md](../ledger/RECORD_FORMAT.md)) |
| `src/pv/registry.yaml` (`pv.registry`) | **Wiring**: which record id supplies each model role (system → obs/price/floor records, ITC measure → rate/entity/labour records, CCA, emission factors, reference prices) and plan-level model assumptions (ITC eligibility probabilities) | No policy values; ids and assumptions only |
| `pv.case` | The typed case model (inputs) | User assumptions, never policy facts |
| `pv.carbon`, `pv.tax`, `pv.emissions`, `pv.cashflow` | Generic formulas over ledger + case | No record ids or policy constants in code |
| `pv.robustness` | Breakeven, grid, MC, sensitivity, strike solver over one vectorized evaluator (`npv_draws`) | Pure, seeded |
| `pv.results`, `pv.report`, `pv.export` | Serialization (results v1, CSV, memo, ledger export) | Deterministic; no clock |
| `pv.cli` | The only place that reads today's date or the filesystem layout | — |
| `tools/` | Maintainer tools outside the product: pilot scorecard | Not imported by `pv` |

The only policy-shaped code left is the model structure itself (ADR-0005: flat vs ratio market methods,
floor and CCfD rules, the QC cap-and-trade path), which a registry entry selects.

## Extension recipes

**Update or add a policy value.** Edit or add a record under `ledger/records/` following
RECORD_FORMAT.md, add a `ledger/CHANGELOG.md` entry, run `pv validate` and
`pv drift --from <last ledger tag>`. If golden outputs change, review the diff, then regenerate snapshots
with `PV_UPDATE_SNAPSHOTS=1 pytest tests/golden` in the same PR.

**Add an output-based pricing system (e.g. a new province's OBPS).**
1. Ledger: credit-price observation record, compliance/fund price series, optional floor record.
2. `registry.yaml` → `carbon.output_based.<system>`: `method: flat|ratio`, `obs`, `price`, `floor`.
3. `pv/case.py`: add the system to `System` (and the province to `Province` if new).
4. Province-keyed tables used by the kernel (`ref.tax.corporate`, `fed.nir.gas_ef`, `fed.nir.grid_ef`,
   `ref.electricity.*`) need a value for the new province, or users must override them.
5. If it is a new jurisdiction code, extend `jurisdiction` and the `id` prefix pattern in
   `ledger/schema/record.schema.json` and `Record.jurisdiction` in `pv/ledger.py`.
6. `tests/unit/test_registry.py` checks the registry, the literals and the ledger stay consistent.

**Add a cap-and-trade jurisdiction.** Same, under `carbon.cap_and_trade.<PROVINCE>` (`system`, `obs`,
`escalation`); every gas user in that province then carries the C&T path.

**Add an ITC measure.** Ledger rate record (scalar with a validity window, a year series, or a table
selected by `project.itc_rate_key`); `registry.yaml` → `tax.itc.<measure>` (`rate`, optional `entities`,
`labour_rate`, `eligibility`); add the measure to `Project.itc_measure`. Measures without an `entities` or
`labour_rate` record get an explicit "not checked" warning rather than silent assumptions.

**Add a grid dimension.** `GridDim` in `pv/case.py`; `robustness.dimensions` (its values) and
`robustness.state_npv` (how a state changes the path or the ITC). The memo renders any dimension.

**Add a sensitivity variable.** A field on `case.Sensitivity`, a name in
`robustness.SENSITIVITY_VARIABLES`, the mapping in `robustness.sensitivity`, and the enum in
`results.v1.schema.json`. Prefer a `Draws` multiplier so MC and sensitivity share the evaluator.

**Change an output.** `results.json` is a published contract (`src/pv/schemas/results.v1.schema.json`):
add keys only (optional), never rename or change meaning within v1; a breaking change needs `pv.results/v2`.
`tests/test_contracts.py` validates every golden result against the schema.

## Data sources outside the ledger

The ledger holds public, cited values only (ADR-0007). Licensed or private data enters a run through
overrides: in the case file, or in a separate uncommitted file passed with `--overrides` (`*.local.yaml`
is git-ignored). A future price-feed adapter should write such an overrides file rather than bypass the
ledger view, so provenance, warnings and the run hash keep working unchanged.

## Tests and fixtures

| Suite | Purpose |
|---|---|
| `tests/unit` | Formulas on hand-sized fixtures (`helpers.case()` builds a minimal case) |
| `tests/property` | Hypothesis properties from plan §5.2 |
| `tests/golden/test_oracle.py` | The frozen research oracle (`validation/`, never edited) reproduced exactly |
| `tests/golden/test_golden_cases.py` | Snapshots, byte-identical reruns, the floor drift flip |
| `tests/ledger` | Schema, validators, the shipped ledger valid at its release date |
| `tests/test_contracts.py` | Results/case schemas, external overrides, export, templates, CLI |
| `tests/tools` | Pilot scorecard on synthetic notes |

Synthetic fixtures only: tests never need network access, real pilot notes or licensed prices.
