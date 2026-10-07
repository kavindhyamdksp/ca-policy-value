# PROGRESS.md — PolicyValue CA MVP build

Resume: read this + CLAUDE.md only, continue at the first unchecked item. Open gates: IMPLEMENTATION_PLAN.md §2.7.

## Setup
- [x] One-time distillation → CLAUDE.md, PROGRESS.md

## M1 Tooling
- [x] pyproject (hatchling), src/pv/, ruff, mypy strict, pytest + hypothesis, pre-commit
- [x] GitHub Actions: lint, type, test, ledger-validate; ubuntu + macOS; py3.11–3.13
- [x] LICENSE (Apache-2.0), ledger/LICENSE (CC BY 4.0 + OGL-Canada)

## M2 Ledger
- [x] JSON schema + pydantic models
- [x] loader (as_of / min_legal_status / overrides with reason)
- [x] validators per §5.4 incl. freshness SLAs
- [x] seed records per §3 (subagent verification)
- [x] ledger/CHANGELOG.md; tag ledger-v2026.10.0

## M3 Kernel
- [x] pv.carbon, pv.tax, pv.cashflow, pv.emissions
- [x] Case model (§2.3)
- [x] conventions: validation_v1 (test-only)
- [x] oracle tests: NPV ±$5k, breakeven ±$1/t — actual max |ΔNPV| $0.00, |ΔBE| 1e-12 $/t (16 NPVs, 8 BEs)

## M4 Robustness
- [x] breakeven vs realizable band
- [x] policy-state grid (GO share, minimal GO conditions)
- [x] seeded vectorized MC (reproduces oracle Ex3 CCfD P(NPV>0)≈76%)
- [x] property tests §5.2

## M5 Report + CLI
- [x] Jinja2 memo (FR-4) with provenance appendix, warnings, not-advice notice
- [x] results.json (schema v1 + hash) and cashflows.csv
- [x] Typer: validate, run, drift, ledger show

## M6 Golden, drift, docs
- [x] 3 golden cases + snapshots
- [x] drift test: ab.tier.floor announced→in_force flips golden_ab_abatement_ccfd
- [x] drift CI job on ledger/ PRs
- [x] README quick-start, docs/user_guide.md, docs/methodology.md

## M7 prep
- [x] docs/validation/pilot_kit.md

## Release
- [x] DoD checklist (8): 1 oracle ΔNPV $0.00 / ΔBE 1e-12 · 2 validate 0 errors, 0 stale · 3 memo lists 100% records + warnings (test) ·
  4 byte-identical (local reruns + CI 6-job fingerprint) · 5 floor drift flip (test) · 6 coverage 95%, mypy strict, ruff clean ·
  7 grid 0.8 ms, 10k MC 5.5 ms, CLI run 0.4 s · 8 fresh clone → HTML memo in 18 s
- [x] IMPLEMENTATION_PLAN.md: ticks, deviations (§2.5 D1–D13), §12 row v1.2
- [x] tag v0.1.0, gh release, PR #1 mvp→main (all 19 checks green incl. drift), merged

## M8 Post-MVP engineering (v0.2.0, 2026-09-30)
- [x] registry.yaml (record wiring, assumptions); expensing classes moved to ledger
- [x] vectorized evaluator; one-way sensitivity; CCfD strike solver (NPV, hurdle, target P)
- [x] fixes: MC vs deterministic carbon rules (D14); CCUS rate key + CE/CCUS window (D15)
- [x] results.v1 / case / record schemas + `pv schema`; stable case digest
- [x] `--overrides FILE` (run, drift); `pv case template`; `pv ledger due/export`; ledger-site workflow
- [x] tools: pilot scorecard (G1); pilot kit with partner outreach
- [x] owner decision 2026-09-30: free, non-commercial, open source; Phase 0/G0 removed (interviews, recruitment,
  competitor demos, demo kit deleted); G2 = open adoption
- [x] CI: wheel smoke test outside checkout, tools job, mypy on tools
- [x] ledger-v2026.10.1 content: fed.nir.grid_ef (NIR Annex 7), fed.ce_itc.rate (ITA 127.491), fed.cca.expensing_classes
- [x] docs: developer guide; user guide, methodology, architecture, README; plan v1.3 with gate register
- [ ] (user) merge, tag v0.2.0 + ledger-v2026.10.1, optional Pages — see plan §2.7
## M9 Primary-text pass (v0.2.1, ledger-v2026.10.2, 2026-10-06)
- [x] D2: fed.ccus_itc.rates proposed → in_force (ITA s. 127.44(1))
- [x] D4: fed.cca.expensing 2030–33 phase-out + Class 53 fixed fraction (Reg. 1100(2), 1104(4.01))
- [x] D18: enhanced first-year deduction is the whole year-1 claim (regression tests)
- [x] drift vs ledger-v2026.10.0: no NPV or decision change; docs, changelog, plan v1.5
- [ ] (user) merge, tag v0.2.1 + ledger-v2026.10.2
- [ ] (tax review) accelerated CCA outside expensing classes (plan §2.7 row)

## M10 Goals audit (2026-10-06)
- [x] G1 measurable: `pv ledger sla` (60-day freshness from git history), maintenance log, scorecard checks all 3 criteria + 0.25 FTE stop
- [x] weekly `freshness.yml` (due within 30 d, SLA history, fails when stale)
- [x] G2 scaffolding: CITATION.cff, CONTRIBUTING.md, ledger-correction + usage-report issue forms, README section
- [x] SPEC NFR: 72-state grid < 1 s test (was 12 states)
- [ ] (user) make the repository public (G2 cannot start while private)
- [ ] (maintainer) re-verify 12 records before 2027-01-07 and 18 before 2027-03-28 (plan §2.7)

- [ ] (user) M7 pilots: find ≥3 partners (docs/validation/pilot_kit.md) → G1 read-out
- [ ] (user) tax review of ITC/CCA records

## Unverified (omitted from ledger; kernel requires user input)
- fed.nir.grid_ef — RESOLVED 2026-09-30 (ECCC Data Mart file API: api/path_contents + api/file)
- fed.ce_itc.rate — RESOLVED 2026-09-30 (rate only; entities/labour pending tax review)
- bc.carbon_tax — gov.bc.ca page 404 and news release cert error; unused by kernel (non-covered BC = $0)
- ref.gas.delivered — no industrial $/GJ in OEB QRAM or FortisBC page; kernel: prices.natural_gas_gj required
- fed.cca.expensing 2030–33 — RESOLVED 2026-10-06 (Reg. 1100(2) A.1 + 1104(4.01): 75% / 55%; Class 53 100%)
- fed.ccus_itc.rates — RESOLVED 2026-10-06 (ITA s. 127.44(1): in_force)
- Partial: fed.carbon.benchmark_path 2028–29/2031–39 not stated (linear interpolation)

## Deviations
Recorded in IMPLEMENTATION_PLAN.md §2.5 (D1–D18). Biggest: D12 tax review not done; D1 now 2 records (gas reference by design, BC carbon tax unused).
