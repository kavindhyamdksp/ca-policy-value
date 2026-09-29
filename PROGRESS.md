# PROGRESS.md — PolicyValue CA MVP build

Resume: read this + CLAUDE.md only, continue at the first unchecked item. Branch `mvp`.

## Setup
- [x] One-time distillation → CLAUDE.md, PROGRESS.md

## M1 Tooling
- [ ] pyproject (hatchling), src/pv/, ruff, mypy strict, pytest + hypothesis, pre-commit
- [ ] GitHub Actions: lint, type, test, ledger-validate; ubuntu + macOS; py3.11–3.13
- [ ] LICENSE (Apache-2.0), ledger/LICENSE (CC BY 4.0 + OGL-Canada)

## M2 Ledger
- [ ] JSON schema + pydantic models
- [ ] loader (as_of / min_legal_status / overrides with reason)
- [ ] validators per §5.4 incl. freshness SLAs
- [ ] seed records per §3 (subagent verification)
- [ ] ledger/CHANGELOG.md; tag ledger-v2026.10.0

## M3 Kernel
- [ ] pv.carbon, pv.tax, pv.cashflow, pv.emissions
- [ ] Case model (§2.3)
- [ ] conventions: validation_v1 (test-only)
- [ ] oracle tests: NPV ±$5k, breakeven ±$1/t

## M4 Robustness
- [ ] breakeven vs realizable band
- [ ] policy-state grid (GO share, minimal GO conditions)
- [ ] seeded vectorized MC
- [ ] property tests §5.2

## M5 Report + CLI
- [ ] Jinja2 memo (FR-4) with provenance appendix, warnings, not-advice notice
- [ ] results.json (schema v1 + hash) and cashflows.csv
- [ ] Typer: validate, run, drift, ledger show

## M6 Golden, drift, docs
- [ ] 3 golden cases + snapshots
- [ ] drift test: ab.tier.floor announced→in_force flips golden_ab_abatement_ccfd
- [ ] drift CI job on ledger/ PRs
- [ ] README quick-start, docs/user_guide.md, docs/methodology.md

## M7 prep
- [ ] docs/validation/interview_guide.md
- [ ] docs/validation/pilot_kit.md

## Release
- [ ] DoD checklist (8)
- [ ] IMPLEMENTATION_PLAN.md: ticks, deviations, §12 row
- [ ] tag v0.1.0, gh release, PR mvp→main, merge on green

## Unverified (omitted from ledger; kernel requires user input)
(none yet)

## Deviations
(none yet)
