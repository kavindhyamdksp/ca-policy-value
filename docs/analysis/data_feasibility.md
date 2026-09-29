# Data feasibility findings

*Condensed from [research file 02](../research/02_policy_data_feasibility.md) and scoped to the refocused concept (realized policy value for industrial projects). As of 2026-09-29.*

## 1. Verdict

**Feasible as a small, editorially maintained ledger. Not feasible as an automated incentive-data pipeline.** The levers that decide outcomes are few (≈45 records at v0.1, ~55 at target, for federal + AB/ON/QC/BC). Most are published only as legal or program prose, so they need a human to read them. Price and emissions series are partly machine-readable. Broad incentive coverage (≈120–200 records, 250–500 edits/yr, C$200–350k/yr) is out of scope.

## 2. Source catalogue for the MVP ledger

| Record family | Authoritative source | Format | Licence | Cadence | Automation |
|---|---|---|---|---|---|
| Industrial carbon headline path | ECCC benchmark; ICAP/Finance announcements; GGPPA Sch. 4; provincial regs | HTML/PDF prose | OGL-Canada / Crown | Irregular, political | Manual, with page-change monitoring |
| System rules: thresholds, credit-use limits, AB floor, DIC caps | TIER Reg., O. Reg. 241/19, BC OBPS, OBPS Regs, QC RSPEDE | HTML/PDF | Crown | 1–2×/yr | Manual |
| Credit-market price observations | CARB/QC auction results (CSV/PDF, quarterly); ECCC CFR reports; secondary: ClearBlue, IETA, law-firm bulletins; OTC is paid | Mixed | Public / proprietary | Quarterly+ | Semi-automated for QC; others manual with a cited observation date |
| CCfD terms | CGF releases; Canada–AB agreement | Press releases | Crown | Deal-by-deal | Manual |
| Clean-economy ITCs (CT, CCUS, CE, CH, CTM) | ITA s.127.44–127.49; CRA pages; NRCan technical guides; Finance consultations | HTML (Justice Laws XML) | OGL / Crown | Budget + FES (2×/yr) | Manual; monitor for changes |
| CCA classes 43.1/43.2/53 and expensing window | ITA regs; Finance/EY/law-firm summaries | HTML | Crown | Budget cycle | Manual |
| Grid emission factors | NIR (ECCC Data Mart CSV); BC, HQ, AESO, NS Power publications | CSV + PDF | OGL-Canada | Annual (April) | **Automatable** (NIR CSV) |
| Reference electricity prices | HQ annual comparison (PDF); AESO/IESO data | PDF / API | HQ copyright; public | Annual / hourly | Defaults only. The user supplies the tariff for real cases |
| Reference gas prices | OEB QRAM, AUC, Régie, BCUC; StatCan | PDF; CSV | Public / OGL | Monthly–quarterly | Defaults only. The user supplies the tariff |
| Gas combustion emission factor | NIR Annex | CSV/PDF | OGL | Annual | Automatable |

**Licensing.** Federal data under the Open Government Licence – Canada allows commercial reuse with attribution. Statute text is Crown copyright, but facts and parameters are not copyrightable. Commercial credit-price feeds (ClearBlue, Argus, Carbon Pulse) cannot be redistributed. The ledger stores dated public observations and lets users plug in licensed prices locally.

## 3. Maintenance estimate (scoped)

| Item | Records | Changes/yr | Effort/yr |
|---|---|---|---|
| Carbon systems (federal + AB, ON, BC, QC) | ~20 | ~10–15 | ~30–50 h |
| Credit-price observations | ~5 series | quarterly | ~15–20 h |
| ITC/CCA measures | ~12 | ~4–8 | ~20–40 h (needs tax-literate review) |
| CCfD / floors | ~4 | ~2–4 | ~10 h |
| EF / reference prices | ~15 | annual | ~10 h (mostly scripted) |
| **Total** | **~55** | **~30–45** | **~85–130 h/yr (≈0.05–0.07 FTE)** plus an ad-hoc expert review budget |

Against the broad-incentive alternative (≈1–1.5 FTE), this is a 15–20× reduction. It works because the quantitative test (04) shows breadth adds little decision value.

## 4. Known data risks

1. **Legal status lags policy.** The national path was announced in May 2026, but the benchmark publication is only "later in 2026" and the AB floor regulation is due 31 Dec 2026. The ledger must hold announced/proposed/enacted/in-force as separate states. The kernel must let users choose which states to trust.
2. **Credit prices are thin and partly proprietary.** Use dated public observations plus user override. Always present as scenario bands.
3. **ITC eligibility is judgement.** Store eligibility as confidence levels per technology class (e.g., ASHP "likely", process heat pump "case-by-case", electrode boiler "not listed"). Never a binary.
4. **Unverified items from research** to confirm before release: NS/NB/NL system parameters; delivered gas tariffs for BC, QC and NS; OBPS thresholds; CTM and Clean Hydrogen phase-down years; whether provincial grants reduce the CT ITC base in each case.
