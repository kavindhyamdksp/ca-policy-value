# Contributing

PolicyValue CA is free, non-commercial and open source. The most valuable contribution is a **ledger
correction**: a value, date or legal status that has changed, with the source that shows it.

## Ledger corrections

**Without git:** open a [ledger correction issue](../../issues/new?template=ledger-correction.yml) with the
record id (`pv ledger show` lists them), what is wrong, and the source URL and excerpt.

**As a pull request:**
1. Edit the record under `ledger/records/` following [RECORD_FORMAT.md](ledger/RECORD_FORMAT.md). Every
   number must be read from a page you fetched; quote ≤ 25 words verbatim; `enacted`/`in_force` records need
   a primary source (statute, regulation or government page).
2. Change `retrieved` and `recorded_at` to the date you checked, and keep the old source if it still applies.
3. Run `pv validate --strict --cases cases` and `pv drift --from origin/main` locally.
4. Add a line to [ledger/CHANGELOG.md](ledger/CHANGELOG.md) under an *Unreleased* heading.

CI validates the ledger and posts the drift report (which saved-case decisions change) on the PR. A
maintainer reviews every ledger change by hand; tax records (ITC, CCA) also need the tax reviewer.

Never commit licensed or proprietary prices: use `--overrides` with a git-ignored `*.local.yaml` file.

## Code

Setup, checks and extension recipes (a new province, system or tax measure) are in the
[developer guide](docs/developer_guide.md). Pull requests need passing tests (coverage ≥ 90%), `ruff check`,
`ruff format --check` and `mypy` (strict). Keep the kernel pure: no network, clock or LLM calls in the
valuation path. Policy values belong in the ledger and record wiring in `src/pv/registry.yaml`, never in code.

## Using it?

Tell us, even briefly: a short note in an issue (no client data) is how the project measures adoption
(gate G2 in [DECISION.md](DECISION.md)). Design-partner pilots follow the [pilot kit](docs/validation/pilot_kit.md).

By contributing you agree that code is licensed under Apache-2.0 and ledger data under CC BY 4.0.
