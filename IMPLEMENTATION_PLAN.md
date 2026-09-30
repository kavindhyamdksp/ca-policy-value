# IMPLEMENTATION_PLAN.md — PolicyValue CA

*Plan version **v1.3** — 2026-09-30. This is the single, living plan for the project. It is updated whenever research or validation changes the product definition. See the [revision history](#12-plan-revision-history) at the end.*

**Governing documents:**
- [DECISION.md](DECISION.md): the REFOCUS verdict, gates G0–G2 and kill criteria
- [SPEC.md](docs/product/SPEC.md): the product specification
- [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) and [ADRs](docs/architecture/adr/): architecture decisions

---

## 0. Summary

| | |
|---|---|
| **What we build** | An open, provenance-tracked **ledger** of the Canadian policy parameters (~45 records at v0.1, ~55 at target) that decide industrial decarbonization projects (federal + AB, ON, BC, QC), plus a deterministic **kernel**. The kernel turns the ledger plus a user's project case into realized after-tax project value, a policy value stack, the breakeven carbon price vs the facility's realizable band, policy-state robustness and optional seeded Monte Carlo. It renders a cited decision memo and re-runs saved cases when the ledger changes (`pv drift`). |
| **What we don't build** | Grant discovery, utility-rebate database, buildings/BEPS, MACC portfolio workflow, credit-price forecasting, energy simulation, hosted SaaS. |
| **Smallest defensible MVP** | Ledger v0.1 (~45 records) + kernel + CLI (`validate`, `run`, `drift`, `ledger show`) + Markdown/HTML memo + 3 golden cases + CI. No UI, no server, no AI. |
| **Effort** | Phase 0 validation: ~40 h over ≤6 weeks. Phase 1 MVP: ~110–150 h: 8 weeks at 15–20 h/week to the `v0.1.0` release, then pilots (M7) to week 12. Runs in parallel with Phase 0. |
| **Operating cost** | $0 (GitHub, Actions, Pages). Maintenance target ≤ 15 h/month. |
| **Gates** | G0 problem validation → G1 MVP usefulness → G2 expansion (see DECISION.md). Gates block evidence-dependent product and policy decisions only; reversible engineering proceeds in parallel (§2.6). Every open gate, its evidence and its next action: **[§2.7 gate register](#27-gate-register-what-is-blocked-why-and-what-clears-it)**. |
| **Status (2026-09-30)** | v0.1.0 released (M1–M6). v0.2.0 engineering complete (§2.6): registry, contracts, sensitivity, CCfD strike solver, ledger export/review queue, gate tooling, ledger-v2026.10.1. Next critical path: G0 interviews and competitor demos (user-run). |

---

## 1. Phase 0 — Problem validation (Gate G0)

The research is secondary-only. Phase 0 buys the missing primary evidence cheaply, using the validation artefacts already in this repo.

### 1.1 Work items

| # | Task | Output | Est. | Status (2026-09-30) |
|---|---|---|---|---|
| P0.1 | Recruitment list:<br>• 20 covered-facility analysts/finance leads (AB TIER, ON EPS, BC OBPS, QC SPEDE), found via ECCC facility data, IETA/CME/CIAC contacts, LinkedIn<br>• 10 consultants/ESCOs (Dunsky, Blackstone, Enerlife, Introba, WSP, Stantec, Ameresco)<br>• 5 CCUS/CCfD developers | `docs/validation/recruitment.md` (no personal data committed) | 4 h | ✅ plan, channels, screening, outreach, aggregate tracker. Contacting people: **user** |
| P0.2 | Interview guide covering current carbon-value method, ITC handling, how often assumptions are rebuilt, tools and advisors, last decision where policy mattered, willingness to use or pay | `docs/validation/interview_guide.md` | 3 h | ✅ (+ structured note template) |
| P0.3 | Demo kit: 2-page PDF/HTML built from `docs/research/04_quantitative_validation.md` (Examples 1, 3 and the MC table), plus a mock memo | `docs/validation/demo_kit/` | 6 h | ✅ as a builder: `python tools/build_demo_kit.py` regenerates it from the golden cases (not committed, so it never drifts) |
| P0.4 | ≥12 interviews, 30 min each | Anonymized notes in `docs/validation/interviews/` | 15 h | ⛔ **gate: user** — template ready (`interviews/README.md`) |
| P0.5 | Competitor demos: SINAI Reduce, ClearBlue Vantage (plus VadiMAP for completeness). Checklist: OBPS mechanics, credit vs headline, floors/CCfD, ITC timing and eligibility, policy-regime risk, provenance | `docs/validation/competitor_demos.md` | 6 h | ⛔ **gate: user** (vendor demos) — checklist and structured results block ready |
| P0.6 | Synthesis against the G0 criteria; update DECISION.md, SPEC.md and this plan | Gate memo | 4 h | ⏳ counting automated (`tools/gate_scorecard.py g0`); judgement and doc updates after P0.4/P0.5 |

### 1.2 G0 acceptance criteria
- ≥12 interviews completed with the segment mix in DECISION.md.
- ≥6 interviewees (a) currently value carbon at headline or rebuild it by hand per engagement, **and** (b) would use a cited ledger + kernel on a live decision (per DECISION.md).
- Fallback: if the kernel criterion fails but ≥3 interviewees would use the ledger alone, continue with M1–M2 only (ledger), per DECISION.md.
- Competitor demos confirm no incumbent values projects under OBPS mechanics with policy-regime risk. If one does, stop the kernel; see kill criteria.
- Answers to SPEC §9 open questions recorded.

---

## 2. Phase 1 — MVP build (Gate G1)

### 2.1 Milestones

| Milestone | Scope | Depends on | Est. | Status |
|---|---|---|---|---|
| **M1** Repo & tooling | `pyproject.toml` (hatchling), `src/pv/`, ruff, mypy (strict on `src/`), pytest + hypothesis, pre-commit, GitHub Actions (lint, type, test, ledger-validate), Apache-2.0 + CC BY 4.0 notices | — | 6 h | ✅ done (v0.1.0) |
| **M2** Ledger schema + seed records | JSON Schema; pydantic models; loader with `as_of` and `min_status` filters; ~45 seed records (§3); validators (§5.4); `ledger/CHANGELOG.md`; tag `ledger-v2026.10.0` | M1 | 30–40 h | ✅ done — 34 entries; tag `ledger-v2026.10.0` (§2.5) |
| **M3** Kernel core | `carbon`, `tax`, `cashflow`, `emissions` per §4 formulas; typed `Case` model (§2.3) | M2 | 25–30 h | ✅ done — oracle reproduced exactly |
| **M4** Robustness | Breakeven solver; discrete policy-state grid; vectorized seeded MC | M3 | 12–15 h | ✅ done |
| **M5** Reporting + CLI | Jinja2 memo (Markdown → HTML via `markdown-it-py`); JSON results schema v1; CSV cash flows; Typer CLI: `pv validate`, `pv run`, `pv drift`, `pv ledger show` | M3–M4 | 15–20 h | ✅ done |
| **M6** Golden cases, drift CI, docs | 3 golden cases; drift job on ledger PRs; README quick-start; user guide; methodology doc (formulas and caveats) | M5 | 12–15 h | ✅ done |
| **M7** Design-partner pilots | ≥3 partners run real cases; collect feedback; fix issues | M6, G0 pass | 10–15 h | ⛔ gated (G0, partners). Prepared: pilot kit, `pv case template`, `--overrides` for licensed prices, structured feedback form, `gate_scorecard.py g1` |
| **M8** Post-MVP engineering (v0.2.0) | Ungated work pulled forward so pilots and Phase 2 need no redesign (§2.6) | M6 | ~15 h | ✅ done 2026-09-30 |

### 2.2 Target layout
See [ARCHITECTURE.md § Repository layout](docs/architecture/ARCHITECTURE.md#repository-layout-target).

### 2.3 Case input model (YAML → pydantic `Case`)

```yaml
case_id: hp-qc-demo
as_of: 2026-10-15              # ledger view date
min_legal_status: enacted       # announced|proposed|enacted|in_force; lower-status records become scenarios
facility:
  province: QC                  # AB|ON|BC|QC
  system: spede                 # tier|eps|bc_obps|fed_obps|spede|none
  covered: true
  entity: taxable_corp          # taxable_corp|reit|crown|municipal|tax_exempt
  labour_requirements_met: true
  tax_capacity: full            # full|none (deferred: Phase 2)
project:
  in_service: 2027-06-30
  life_years: 20
  capex: [{year: 0, amount: 3500000}]
  technology_class: heat_pump_process   # maps to ledger eligibility table
  itc_eligible_share: 0.85              # optional override of ledger default
  other_assistance: 0                   # reduces ITC base and UCC
  energy_deltas: {natural_gas_gj: -50824, electricity_mwh: 4000}
  opex_delta: 30000
  covered_emissions_delta_t: null       # default: computed from gas EF
prices:                                  # user tariffs; ledger reference defaults if omitted
  natural_gas_gj: 8.8
  electricity_mwh: 60.5
  escalation: 0.02
finance: {discount_rate: 0.08, itc_receipt_lag_years: 1}
policy:
  credit_price_scenario: base            # low|base|high|upper_bound_headline
  ccfd: {strike: 85, term_end: 2040, volume_share: 1.0}   # optional
  grid_factor: average                   # average|marginal
  marginal_grid_ef_g_kwh: null
robustness:
  grid: [floor_status, itc_granted, ccfd]
  monte_carlo: {draws: 10000, seed: 20260929, regimes: {...}, shocks: {...}}
overrides:
  - {record: ab.tier.credit_obs, value: 25, reason: "broker quote 2026-10-10"}
```

### 2.4 Phase 1 acceptance criteria (MVP definition of done)

1. **Correctness vs oracle.** Run with `validation/params.yaml` values injected as overrides **and** `conventions: validation_v1`. This is a test-only setting that reproduces the oracle's simplifications: credit prices flat nominal, Class 8-like 20% declining balance when clean-tech ineligible, annual floor table as in params. With those settings, the kernel reproduces `validation/results.md` Example 1 (QC ITC yes/no, BC covered market) and Example 3 ($25M, all four carbon cases). NPV must match within ±$5k and breakeven within ±$1/t.
2. **Ledger integrity.**
   - 100% of records pass schema validation.
   - Every `enacted`/`in_force` record has ≥1 primary source.
   - Zero records past their freshness SLA at release.
3. **Provenance.** Every memo lists 100% of ledger records used, with value, status, source URL and retrieved date. It warns on any `announced`/`proposed` record used in the base case, any override, and any stale record.
4. **Reproducibility.** Same case + ledger tag + seed → byte-identical `results.json` across two runs and two machines (CI matrix: ubuntu, macOS; Python 3.11–3.13).
5. **Drift.**
   - `pv drift --from <tag> --to <tag>` lists changed records and value deltas per case, and flags flipped decisions.
   - A test fixture that changes `ab.tier.floor` from `announced` to `in_force` produces the expected flip on `golden_ab_abatement_ccfd`.
6. **Quality.**
   - ≥90% line coverage on `src/pv` (excluding `cli`/`report`).
   - mypy strict passes; ruff clean.
7. **Performance.** A single case with a 3-dimension grid runs in < 1 s. 10k-draw MC runs in < 10 s on a 2020-class laptop.
8. **Docs.** A new user can run `pip install -e . && pv run cases/golden_hp_qc.yaml` and get an HTML memo in < 10 minutes by following the README.

### 2.5 MVP build record and deviations (v0.1.0, 2026-09-29)

All eight §2.4 criteria were checked at release; results are in the v0.1.0 release notes and PR. Deviations from this plan:

| # | Plan | As built | Why |
|---|---|---|---|
| D1 | ~45 seed records | 34 entries / 33 ids. Not verified within the fetch budget, so omitted and left to user input: `fed.nir.grid_ef`, `fed.ce_itc.rate`, `bc.carbon_tax`, `ref.gas.delivered` | §3 entry rule: no value without a fetched source |
| D2 | `fed.ccus_itc.rates` in_force | `proposed` | Only secondary sources stated the rates; the CRA page gave none |
| D3 | Process heat pumps case-by-case | `fed.ct_itc.eligibility_classes`: process/waste-heat heat pumps and electric boilers `not_listed` | NRCan guidance does not mention them; base case denies the CT ITC unless the user asserts it |
| D4 | CCA expensing 2030–33 phase-out; Classes 43.1/43.2/53 | Only 2025–29 (100%) and 2034 (0%) entered; kernel expenses 43.1 and 53 only | The fetched sources give no phase-out percentages and do not name 43.2; in-service 2030–33 requires an override |
| D5 | Gas EF from NIR Annex 6 (~50 kg/GJ) | Province-specific CO2 factors from ECCC *Emission factors and reference values* v4.0 (0.0500–0.0512 t/GJ) | NIR Annex 6 not retrievable; ECCC table is primary |
| D6 | Benchmark path $100 for 2027–29 | Record holds only stated years (2026, 2027, 2030, 2035, 2040); the kernel interpolates linearly (2028 ≈ $105) | ICAP states 2027 and 2030 only; the headline is an upper-bound scenario, so the base case is unaffected |
| D7 | ON/BC "ratio-to-headline" | Ratio to the system's **in-force** compliance schedule (ON EPS, BC OBPS reach $170 in 2030), capped at that schedule | Legal-status-aware: no alignment with the May 2026 national path was recorded; the "high" band can exceed the headline |
| D8 | Answer GO/NO-GO/DEPENDS-ON | Answer from the policy-state grid (all/none/some GO) plus `base_case` (NPV sign); `pv drift` flags a flip in either | The drift acceptance test concerns the base case; the grid answer is invariant to a floor's legal status |
| D9 | — | `pv drift` evaluates each case as of max(case `as_of`, ledger's latest `recorded_at`) | Otherwise records recorded after a saved case's date are invisible to drift |
| D10 | Per-province MC regimes | Generic regimes (`market_scale`, `market_value`, `floor_scale`, `from_year`) set in the case | Same expressiveness; reproduces the oracle Ex3 distribution (CCfD P(NPV>0) ≈ 76%) |
| D11 | Timing | t=0 is `project.in_service`; y(t) = in_service.year + t; multi-year capex treated as available at t=0 for ITC/CCA | Matches the oracle; documented in docs/methodology.md |
| D12 | Tax-literate review before v0.1 (§6) | **Not done.** ITC/CCA records carry `reviewer: … human tax review pending` | No reviewer available in the build; open risk for pilots |
| D13 | mypy strict | Strict, with `python_version = 3.12` for type-checking | numpy ≥2.3 stubs use PEP 695 syntax; runtime 3.11 is tested in CI |

Updates in v0.2.0 (2026-09-30):

| # | Change | Why |
|---|---|---|
| D1 | **Partly resolved.** `fed.nir.grid_ef` (ECCC NIR 1990–2024 Annex 7 xlsx via the Data Mart file API; 2024 consumption intensity) and `fed.ce_itc.rate` (ITA s. 127.491, 15%) added in ledger-v2026.10.1. Still user input: `ref.gas.delivered` (by design), `bc.carbon_tax` (unused) | Primary sources became retrievable (the Data Mart page is a JS app; its API is not) |
| D4 | Expensing-eligible classes moved from kernel code to the ledger (`fed.cca.expensing_classes`: 43.1, 53, 54–56). Phase-out percentages still unverified (gate in §2.7) | Policy facts carry provenance; no policy constants in code |
| D14 | MC now mirrors the deterministic carbon rules: the headline upper bound is not capped or CCfD-adjusted, and QC paths take no CCfD | Bug: MC and deterministic results disagreed in those two cases; regression property test added |
| D15 | Table-valued ITC rates need `project.itc_rate_key`; scalar CE/CCUS rates apply only inside their validity window; unchecked entity/labour rules produce a warning | Bug: CCUS silently used the first key (DAC 60%) for every project |
| D16 | Record ids and plan-level assumptions moved to `src/pv/registry.yaml` | Keep policy structure out of formula modules; new systems/provinces become records + a registry entry |
| D17 | Case digest omits unset optional fields (one-time change of all case/run hashes in v0.2.0) | Additive model fields no longer change existing cases' hashes |

### 2.6 v0.2.0 engineering record (M8, 2026-09-30)

Ungated engineering done in parallel with Phase 0, so that the gates, when they clear, lead straight to
execution. None of it changes a policy value or a gate criterion.

| Area | Delivered | Serves |
|---|---|---|
| Policy config out of code | `pv.registry` + `registry.yaml` (record wiring, eligibility probabilities); expensing classes in the ledger | Phase 2 provinces/systems as records + config; D12 review |
| Contracts | `pv.results/v1` JSON Schema (additive-only), case schema generated from the model, `pv schema` | Integrations, Excel/CSV round-trip, static API |
| Analyses | One-way sensitivity (tornado); CCfD strike solver (NPV ≥ 0, hurdle rate, target P(NPV>0) with common random numbers); shared vectorized evaluator | SPEC §9 Q2 (CCfD wedge) can be tested in G0 demos; Phase 2 CCfD bid module largely built |
| Data boundary | `--overrides FILE` for licensed/private values (git-ignored `*.local.yaml`), recorded in results and the run hash | Pilots with licensed prices; future price-feed adapters write override files |
| Ledger operations | `pv ledger due` (review queue), `pv ledger export` (JSON/CSV/static HTML), manual `ledger-site` Pages workflow | Freshness SLA (G1), static ledger site (Phase 2), static JSON API (Phase 3) |
| Pilot enablement | `pv case template` (synthetic placeholders), updated pilot kit | M7 |
| Validation tooling | `tools/gate_scorecard.py` (G0/G1 counting, personal-data-proof note schema), `tools/build_demo_kit.py`, recruitment plan, competitor-demo checklist | P0.1, P0.3, P0.5, P0.6, G1 read-out |
| Quality | Bugs D14/D15 fixed with regression tests; wheel built and run outside the checkout in CI; mypy strict on `tools/`; 122 tests, 97% coverage | DoD §2.4-6 |
| Ledger | ledger-v2026.10.1: +3 records (37 entries / 36 ids); drift vs v2026.10.0: no NPV or decision change | D1 |

### 2.7 Gate register (what is blocked, why, and what clears it)

Only items below are open. Everything else in this plan is done or is scoped out by ADR-0001.

| Gate / blocker | Why work cannot safely continue past it | Evidence or input that clears it | Already prepared | Next executable action once cleared |
|---|---|---|---|---|
| **G0 problem validation** (P0.4 interviews, P0.5 competitor demos) | Whether the kernel is worth continuing is a demand question; only practitioner evidence can answer it (DECISION.md) | ≥12 anonymized notes in `docs/validation/interviews/` in the segment mix; SINAI and ClearBlue demo results in `competitor_demos.md` | Recruitment plan, interview guide, demo kit builder, note templates, competitor checklist, `gate_scorecard.py g0` (PASS/FALLBACK/FAIL/KILL/OPEN) | Run the scorecard; P0.6 synthesis; record the verdict and SPEC §9 answers in DECISION.md, SPEC.md and this plan |
| **G1 / M7 design-partner pilots** | Needs G0 pass and real partners with live projects | ≥3 pilot notes in `docs/validation/pilots/` with `decision_changed_or_derisked: yes`; freshness SLA held 60 days; maintenance ≤15 h/month | Pilot kit, case templates, `--overrides`, feedback form with structured front matter, `gate_scorecard.py g1`, `pv ledger due` | Fix issues found in pilots; G1 read-out; choose Phase 2 items from partner demand |
| **D12 human tax review** (ITC/CCA records) | ITC/CCA treatment is legal interpretation; a wrong eligibility or class statement can harm users (§10) | Signed-off review by a tax-literate reviewer of `fed.ct_itc.*`, `fed.ce_itc.rate`, `fed.ccus_itc.rates`, `fed.cca.*` and methodology §3 | Records flagged `human tax review pending`; warnings where the kernel does not check entity/labour rules; `pv ledger export` gives the reviewer a single browsable file | Apply findings to records (and `reviewer`), release a ledger tag, re-run `pv drift` |
| **CCA expensing phase-out 2030–2033** (D4) | Percentages are policy values; no primary source retrieved. Secondary sources (BDO, Advisor.ca) state 75% (2030–31) and 55% (2032–33), and one names Class 43.2, conflicting with EY | Primary text: ITA/Income Tax Regulations as amended by Bill C-15, or a Finance Canada/CRA page stating the percentages and classes | Kernel stops with a clear message for in-service 2030–2033; override path documented | Add 2030–2033 to `fed.cca.expensing`; update `fed.cca.expensing_classes` if 43.2 is confirmed; drift |
| **CE ITC qualifying entity and labour rule** | Mapping the case's entity types to s. 127.491 "qualifying entity" and applying s. 127.46 are interpretations | Tax review (above) of the mapping and the labour reduction | Rate in ledger; kernel warns that both are unchecked; registry supports `entities`/`labour_rate` per measure | Add `fed.ce_itc.entities` (and a labour record) and wire them in `registry.yaml`; the labour rule shape for CE (a reduction, not a replacement rate) needs a small kernel change |
| **`fed.ccus_itc.rates` legal status** (D2) | Only secondary sources state the rates; the record stays `proposed` | Primary legal text (ITA s. 127.44) or CRA page stating the rates | `itc_rate_key` makes the component explicit; grid/MC can treat the ITC as uncertain | Update the record's status and sources; drift |
| **Policy events** (§7): AB TIER floor regulation (due 2026-12-31), federal benchmark publication, ON EPS alignment, ITC domestic content, NIR 2027 | External facts that have not happened yet | The published regulation/benchmark/decision | Legal-status model; drift test proves the floor flip on `golden_ab_abatement_ccfd`; `pv ledger due` | Update records, tag a ledger release, publish the drift report |
| **Credit-use limits and long/short position** (SPEC FR-2 `position`) | Per-system credit-use and banking rules are policy data not yet in the ledger, and whether they matter is a pilot question | Primary sources for TIER/EPS/OBPS credit-use limits; partner demand in G0/G1 | Fund-price cap; caveat in methodology | Add records + a position field and rule in `pv.carbon` |
| **Partial tax capacity** (loss carryforward) | Loss rules are tax interpretation (D12) and demand is unproven | Tax review + partner demand | `tax_capacity: full/none` | Add a carryforward schedule to `pv.cashflow` |
| **Phase 2 data scope**: CFR, ÉcoPerformance, Clean Industry Fund, NS/NB/NL/SK | Scope is gated by partner demand (ADR-0001) and each needs verified records | G1 partner demand; primary sources | Registry: a new system/province is records + one registry entry (developer guide) | Add records and registry entries per province |
| **AI-assisted source monitoring** (ADR-0006) | Needs an LLM credential and a maintenance-load trigger (>10 h/month) | Maintenance log over the trigger; user-provided API key | Deterministic parts: `pv ledger due`, weekly link check | Build the drafting job on top of `pv ledger due` output |
| **Publishing**: Pages ledger site, `v0.2.0`/`ledger-v2026.10.1` tags | Outward-facing actions on the user's account | User enables Pages; user merges and tags | `ledger-site` workflow (manual); changelog | Dispatch the workflow; tag and release |

---

## 3. Data sources — seed ledger (v0.1)

Each record's source is taken from the research files and re-verified when entered. **[V]** = verified in research; **[C]** = confirm before entry (flagged [inferred] in research).

| Record id | Content | Legal status (as of 2026-09) | Primary / secondary source | |
|---|---|---|---|---|
| `fed.carbon.benchmark_path` | $95 (2026) → $100 (2027–29) → $115 (2030) → +$3/yr → $130 (2035) → 1.5%/yr → $140 (2040) | announced (benchmark publication "later in 2026") | ICAP 2026-05-19; Osler; Blakes; EY | V |
| `fed.ggppa.schedule4` | Legislated OBPS excess-emissions charge ($110 for 2026, etc.) | in_force (pending amendment) | Justice Laws GGPPA Sch. 4 | V |
| `fed.fuel_charge` | $0 from 2025-04-01 | in_force | ECCC | V |
| `fed.obps.thresholds` | 50 kt mandatory; 10 kt opt-in | in_force | ECCC OBPS page | C |
| `fed.obps.credit_obs` | ~$37.50/t (Dec 2025 observation) | observation | carboncredits.com citing ClearBlue | V |
| `fed.ct_itc.rate_schedule` | 30% until 2033; 15% in 2034; 0 after | in_force | ITA s.127.45; CRA | V |
| `fed.ct_itc.labour_rate` | 20% if labour requirements not met | in_force | CRA | V |
| `fed.ct_itc.entities` | Taxable Canadian corporations; certain REITs | in_force | CRA | V |
| `fed.ct_itc.eligibility_classes` | ASHP/GSHP: likely; process/waste-heat HP: case-by-case; electrode/resistance boilers: not listed; solar/wind/storage: likely | in_force (guidance) | NRCan CT property technical guidance | V (classes) / C (per-class mapping) |
| `fed.ct_itc.domestic_content` | Consultation 2026-02-13 to 03-13; outcome pending | proposed | Finance Canada | V |
| `fed.ccus_itc.rates` | 60% DAC / 50% capture / 37.5% T&S&U to 2035; half 2036–2040 | in_force (C-15) | ITA; Gowling; Torys | V |
| `fed.ce_itc.rate` | 15%; eligible entities incl. Crowns, municipal, Indigenous-owned corps — **rate entered 2026-09-30 from ITA s. 127.491; entities pending tax review** | in_force (C-15, 2026-03-26) | Finance; Torys; Justice Laws | V (rate entered) |
| `fed.cca.expensing` | 100% first-year for Classes 43.1/53 (and ZEV classes) available for use before 2030; phase-out 2030–2033 | in_force (C-15) | EY tax alert | V (phase-out schedule: C) |
| `fed.cca.class_rates` | 43.1 = 30%, 43.2 = 50%, 53 = 50% DB (normal rates) | in_force | ITR Schedule II | C |
| `fed.nir.grid_ef` | Average grid factors: QC 2.5, ON 73.8, AB 335, BC 22.8 g/kWh (+NS 528 reference) — **entered 2026-09-30 from NIR Annex 7 (2024 consumption intensity): QC 2.565, ON 73.313, AB 346.102, BC 18.064** | observation (annual) | NIR 2026 CSV (ECCC Data Mart); HQ; BC gov; Alberta.ca; TAF/IESO | V (entered) |
| `fed.nir.gas_ef` | ~50 kg CO2e/GJ (HHV) | observation | NIR Annex 6 | C |
| `fed.cgf.ccfd` | Program exists; bilateral terms | in_force (program) | CGF; Budget 2025 | V |
| `ab.tier.fund_price` | $95 for 2026; national path after | in_force (2026) / announced (2027+) | EY 2026-06-03; Blakes | V |
| `ab.tier.floor` | Minimum transfer price $60 (2030) → $80 (2035) → $110 (2040); regulation due 2026-12-31 | announced | EY; GLJ | V |
| `ab.tier.credit_obs` | ~$18–20/t | observation | Blakes 2026-05; carboncredits (ClearBlue) | V |
| `ab.tier.dic_cap` | Direct-investment credits ≤50% of capex/opex net of public support | announced | Blakes | V |
| `ab.tier.threshold` | 100 kt (opt-in below) | in_force | TIER Reg. | C |
| `ab.ccfd.joint_pool` | Up to $1.2B (≤$600M each govt), up to 75 Mt | announced | Blakes; Osler | V |
| `on.eps.price_schedule` | $50 (2022) + $15/yr; alignment with national path pending | in_force (O. Reg. 241/19) | Enbridge; IETA brief | V (alignment: C) |
| `on.eps.epu_obs` | 15–20% below compliance price (2025); ~$72 (Dec 2025) | observation | IETA 2025-09; carboncredits (ClearBlue) | V |
| `on.eps.thresholds` | 50 kt mandatory; 10 kt opt-in | in_force | IETA; O. Reg. 241/19 | V |
| `bc.obps.price` | Regulatory level ~$80 (per ClearBlue); path alignment pending | C | BC gov; carboncredits | C |
| `bc.obps.credit_obs` | ~$65/t | observation | carboncredits (ClearBlue) | V |
| `bc.carbon_tax` | Repealed 2025-04-01 | in_force | BC gov | V |
| `bc.obps.threshold` | 10 kt | in_force | BC OBPS Reg. | C |
| `qc.spede.coverage` | Emitters ≥25 kt plus fuel distributors, so all gas users carry the price | in_force | MELCCFP; ICAP | V |
| `qc.spede.auction_obs` | C$45.11 settlement (Aug 2026); reserve C$38.81 | observation | CARB/MELCCFP auction summary | V |
| `qc.spede.reserve_escalation` | 5% + inflation per year | in_force | WCI regs | C |
| `ref.electricity.{prov}` | HQ comparison 2025 large/medium ¢/kWh (reference default only) | observation | HQ comparison 2025 | V |
| `ref.gas.{prov}` | Delivered gas reference (default only; user tariff expected) | observation | OEB QRAM; AUC; Régie; BCUC | C |
| `ref.tax.{prov}` | Combined general corporate rates | in_force | CRA / provincial finance | C |

**Entry rule:** a **[C]** record may be committed only after its primary source is fetched and cited. Otherwise it stays out of v0.1 and the kernel requires a user input for it.

---

## 4. Models (formulas the kernel implements)

Notation: year index *t* = 1..N (operating years), *y(t)* calendar year, τ tax rate, *r* discount rate.

**4.1 Realized carbon value per tonne, `v_t`** (ADR-0005)
- Not covered and province ≠ QC → `v_t = 0`.
- QC (covered or not) → `v_t = p^{C&T}_{y}` for the chosen scenario (default: last auction settlement escalated at the reserve rate).
- Covered (AB, ON, BC, fed OBPS):
  - `m_t = min(market^{s}_{y}, fund_{y})`, where `market^{s}` is built from dated observations: base = the latest observation held flat in real terms, or the ratio-to-headline method for ON/BC; low and high as ledger-defined bands.
  - If the floor record passes `min_legal_status` and `y ≥ floor.effective_from`: `m_t = max(m_t, floor_{y})`. Otherwise the floor is available only as a grid dimension.
  - CCfD: for `y ≤ term_end`, `v_t = volume_share·max(strike, m_t) + (1−volume_share)·m_t`; else `v_t = m_t`.
- `upper_bound_headline`: `v_t = headline_{y}`. Always labelled as such.
- Carbon cash flow: `C_t = ΔE^{covered}_t · v_t`, where `ΔE` = avoided covered tonnes (gas GJ × EF unless supplied).

**4.2 Tax measures**
- ITC rate: `ρ = schedule(y_in_service)`; if `!labour_ok` and the measure has a labour rule → reduced rate. ITC is zero if the entity is not eligible for that measure.
- `ITC = ρ · s_elig · (capex − assistance)`, received at `t = lag`.
- UCC base: `U = capex − ITC − assistance`.
- CCA: if the class is expensing-eligible and in-service within the window → `CCA_1 = U·expensing_pct(y)`, and the remainder follows the declining balance at the class rate. Otherwise declining balance with the half-year rule.
- If `tax_capacity = none` or the entity is non-taxable: no tax on operating flows, no CCA shield, and ITC only if the measure is refundable and the entity is eligible.

**4.3 Cash flow and metrics**
- `CF_0 = −capex_0`
- `CF_t = (1−τ)·(S^{gas}_t + C_t − E^{el}_t − O_t) + τ·CCA_t + ITC·[t = lag]`
- NPV at *r*.
- IRR via `brentq` on [−0.99, 3]. Returns `null` (with a warning) if there are multiple sign changes and multiple roots.
- Simple and discounted payback.
- **Value stack:** NPV(base without policy) → +carbon → +ITC → +CCA-timing → +CCfD. Computed sequentially and reported with order noted, since interactions are non-additive.

**4.4 Robustness**
- **Breakeven carbon price:** the flat nominal `p*` with NPV(v_t = p*) = 0, compared with the realizable band [low, base, high, headline].
- **Policy-state grid:** Cartesian product of the user-selected discrete dimensions. For each state: NPV and GO/NO-GO. Report the GO share and the minimal set of conditions under which GO holds.
- **Monte Carlo:** regimes sampled from user probabilities; the price shock applies to the market price and floors/CCfD strikes are applied after the shock; log-normal, mean-preserving persistent shocks on gas, electricity and credit prices; triangular capex; Bernoulli ITC eligibility with p from the ledger `eligibility_confidence` map (likely = 0.9, case-by-case = 0.6, not listed = 0.1; user-overridable). Numpy `default_rng(seed)`, vectorized over draws. Reports mean, P10/P50/P90 and P(NPV>0).

**4.5 Emissions**
- On-site: `gas_GJ × EF_gas`.
- Grid: `MWh × EF_grid` (average from the ledger; marginal from user input).
- Report net annual and lifetime tonnes, and abatement cost as `−NPV / discounted tonnes` (both the on-site and net bases).

---

## 5. Test strategy

| Layer | What | Tooling |
|---|---|---|
| 5.1 Unit | Each formula in §4 against hand-computed fixtures (e.g., a 3-year toy project; ITC on a $1M asset with 1-year lag; floor activation year boundary; QC path for a non-covered site) | pytest |
| 5.2 Property | NPV monotone non-decreasing in carbon price and ITC rate; zero carbon value for a non-covered non-QC site under any scenario; breakeven round-trip (NPV at p* ≈ 0); CCfD value ≥ 0; MC mean → deterministic value as σ → 0, regimes collapse and capex/eligibility distributions are degenerate | hypothesis |
| 5.3 Golden / oracle | Kernel vs `validation/results.md` (acceptance §2.4-1); golden case JSON snapshots, regenerated only with a reviewed PR | pytest + snapshot files |
| 5.4 Ledger | Schema; units whitelist; date logic; no overlapping periods per (id, status); primary source for enacted/in_force; `retrieved` ≤ SLA; URL reachability (weekly, non-blocking) | jsonschema, custom validators, lychee link checker |
| 5.5 Reproducibility | Byte-identical `results.json` across runs and OS matrix | CI matrix |
| 5.6 Drift | Synthetic ledger change → expected flip detected | pytest fixture ledgers |
| 5.7 Report | Memo contains every used record id; warnings present for announced/override/stale | pytest (string/HTML assertions) |

CI gates: lint, type, unit/property/golden, ledger validation and drift on PRs touching `ledger/` must all pass.

---

## 6. Dependencies

| Type | Dependency | Notes |
|---|---|---|
| Runtime | Python ≥3.11, numpy, scipy, pydantic v2, PyYAML, jsonschema, Jinja2, markdown-it-py, Typer | All permissive licences; no network at runtime |
| Dev | pytest, hypothesis, ruff, mypy, pre-commit, lychee (CI) | |
| Data | ECCC NIR CSV; CARB auction results; government and legal pages (§3) | OGL / public; no paid data |
| People | Tax-literate reviewer for ITC/CCA records (~5 h per release; e.g., a CPA contact or design-partner tax team) | Required before v0.1 release |
| People | 3+ design partners (G1) | From Phase 0 interviews |
| Accounts | GitHub repo under `kavindhyamdksp`; GitHub Actions; Pages (Phase 2) | Free tier |

---

## 7. Policy events to track (drive ledger releases)

| Event | Expected | Records affected |
|---|---|---|
| Updated federal carbon-pricing benchmark published | "Later in 2026" | `fed.carbon.benchmark_path` (announced → enacted), `on.eps.*`, `bc.obps.*`, `fed.ggppa.schedule4` |
| Alberta TIER floor regulation | By 2026-12-31 | `ab.tier.floor`, `ab.tier.dic_cap` |
| CT/CE ITC domestic-content decision | Pending (consultation closed 2026-03-13) | `fed.ct_itc.*`, `fed.ce_itc.*` |
| Ontario EPS amendments to the new path | Pending | `on.eps.price_schedule` |
| NIR 2027 release | April 2027 | `fed.nir.*` |
| HQ price comparison 2026 edition | 2026 | `ref.electricity.*` |
| Quarterly QC/CA auctions | Quarterly | `qc.spede.auction_obs` |
| Federal Budget / Fall Economic Statement | Annual | all tax records |

---

## 8. Phase 2 — Expansion

Engineering that needed no new evidence was pulled forward into v0.2.0 (§2.6): the CCfD strike solver
(target NPV, IRR hurdle and P(NPV>0)), the static ledger export and Pages workflow, the CSV/JSON contracts
that a spreadsheet round-trip builds on, and the registry that makes a new province a data change. What
remains below needs G1 evidence (partner demand) or new verified ledger data; see §2.7.

| Item | Trigger / justification | Est. | Status |
|---|---|---|---|
| CCfD bid module: strike solver for a target P(NPV>0) or IRR | Developers in G0/G1 ask for it | — | ✅ built in v0.2.0 (`robustness.ccfd_strike`) |
| CCfD volume/term optimization | Needs the objective a counterparty scores bids on (SPEC §9 Q2, G0) | 8 h | ⛔ G0 answer |
| Credit-use limits and long/short position modelling (TIER credit-use caps, EPS rules) | Covered-facility partners need it | 15 h | ⛔ evidence + demand |
| CFR credits (fleets, charging, RNG) | Partner demand; CFR credit price rose from ~$142 (Q2 2025, ECCC via BC Bioenergy) to ~$358/t (June 2026, MLT Aikins), which makes it decisive for fleets | 15 h | ⛔ demand + records |
| QC ÉcoPerformance large-project stream; BC Clean Industry Fund | QC/BC partners | 10 h | ⛔ demand + records |
| NS, NB, NL, SK, federal-OBPS provinces | Partner demand | 3–5 h per province (records + registry entry) | ⛔ demand + records |
| Static ledger site, with citations | ≥3 external ledger users | — | ✅ built (`pv ledger export`, `ledger-site` workflow); publishing is a user action. Per-record history view: 4 h, after demand |
| AI-assisted source monitoring → draft ledger PRs (ADR-0006) | Maintenance > 10 h/month | 12 h | ⛔ trigger + credential; review queue built |
| Excel add-in or CSV round-trip template | Consultant partners | 6 h | ⏳ contracts ready (case schema, results schema, cashflows.csv, records.csv); template after demand |

## 9. Phase 3 — Only if G2 passes

- Hosted read-only ledger API (static JSON on Pages first; a serverless function only if needed).
- Institutional co-maintenance (NGO, university energy-modelling hub) or a data-licence partnership (e.g., for licensed credit-price feeds).
- Optional hosted memo generation for non-technical users.

---

## 10. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| No primary demand (G0 fails) | Medium | High | Gate before most build effort; the ledger alone remains a low-cost fallback |
| Incumbent (SINAI, ClearBlue+Deloitte) ships an equivalent | Medium | High | Open-source/provenance positioning; partner rather than compete; kill criterion |
| Policy change outpaces maintenance | Medium | Medium | Narrow scope; legal-status model; drift CI; events calendar (§7); AI monitoring in Phase 2 |
| ITC eligibility misstatement → user harm | Medium | High | Confidence levels, not binaries; tax-reviewer sign-off; prominent not-advice notice |
| Credit-price data thin or proprietary | High | Medium | Dated public observations + scenario bands + local overrides |
| Scope creep toward a broad platform | Medium | Medium | ADR-0001; expansion only via gate triggers |

---

## 11. Timeline (indicative, part-time 15–20 h/week)

| Week | Phase 0 | Phase 1 |
|---|---|---|
| 1 | P0.1–P0.3 (recruit, guide, demo kit) | M1 |
| 2–3 | Interviews begin; competitor demos | M2 (ledger) |
| 4–5 | Interviews continue | M3 (kernel) |
| 6 | **G0 decision** | M4 (robustness) |
| 7 | — | M5 (report + CLI) |
| 8 | — | M6 (golden, drift, docs) → release `v0.1.0` |
| 9–12 | — | M7 pilots → **G1 decision** |

If G0 fails in week 6, stop at M3. Release only the ledger (M2) and archive the kernel branch.

Parallel tracks from 2026-09-30: engineering (M8 done) no longer waits on G0; the critical path is P0.4–P0.6
(user-run). Ledger maintenance (`pv ledger due`, §7 events) continues on its own cadence.

---

## 12. Plan revision history

| Version | Date | Change | Driver |
|---|---|---|---|
| v0 | 2026-09-29 | Starting hypothesis: broad "Canada Climate CapEx Engine" (policy + incentives + energy/emissions + NPV/IRR/payback/uncertainty for corporate decisions) | Assignment brief |
| v1.0 | 2026-09-29 | **Refocused** to PolicyValue CA:<br>• dropped grant/rebate database, buildings, MACC workflow and generic NPV positioning<br>• added realized carbon value model, legal-status-aware bitemporal ledger, CCfD valuation, policy-state robustness and decision drift<br>• ledger scope cut from ~150+ to ~45–55 records<br>• AI limited to ledger monitoring<br>• gates G0–G2 added | Research 01–04: incumbents solve the math, discovery and workflow; incentive breadth is noise at industrial scale; carbon-value treatment is the top swing factor; CCfD shifts P(NPV>0) 0%→76%; broad demand weakened in 2025–26 |
| v1.1 | 2026-09-29 | Independent verification pass:<br>• MC applies price shocks to market price, then floors (CCfD result now 0%→76%)<br>• derived carbon-value bands ($20–122/t) replace hard-coded ones<br>• ITC 2034 case also loses the expensing window<br>• AB floor uses EY's annual table<br>• G0/G1 wording aligned with DECISION.md<br>• oracle acceptance test uses a `validation_v1` conventions mode<br>• ledger size stated as ~45 (v0.1) / ~55 (target) | Reviewer findings; see `docs/research/04` robustness note |
| v1.3 | 2026-09-30 | **v0.2.0 engineering (M8)** pulled forward past gates where no evidence was needed:<br>• registry; results/case schemas; sensitivity; CCfD strike solver; `--overrides`; ledger export/review queue; case templates; gate scorecards; demo kit builder; packaging CI<br>• bugs fixed: MC vs deterministic carbon rules (D14), CCUS rate selection (D15)<br>• ledger-v2026.10.1: grid intensity and CE ITC rate from primary sources; expensing classes into the ledger<br>• gate register §2.7; Phase 2 split into built vs gated | Execution rule: gates block evidence-dependent decisions only |
| v1.2 | 2026-09-29 | **MVP v0.1.0 built** (M1–M6; M7 kit prepared):<br>• ledger `ledger-v2026.10.0`, 34 source-verified entries, 4 records left to user input<br>• kernel reproduces the oracle exactly (ΔNPV < $0.01, Δbreakeven < 10⁻¹² $/t)<br>• 3 golden cases, drift CI, docs; deviations D1–D13 in §2.5 | Build session; source fetches 2026-09-29 |
