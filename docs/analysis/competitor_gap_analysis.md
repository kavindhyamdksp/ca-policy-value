# Competitor & gap analysis, differentiator tests, and alternative concepts

*Synthesis of research files [01](../research/01_landscape.md), [02](../research/02_policy_data_feasibility.md), [03](../research/03_user_needs_workflows.md) and [04](../research/04_quantitative_validation.md). As of 2026-09-29.*

## 1. What is already solved well (do not compete)

| Capability | Who solves it | Why it's "solved" |
|---|---|---|
| Project NPV/IRR/payback with a carbon-price input and Monte Carlo | **RETScreen Expert** (NRCan) | Free Viewer, ~CA$869/yr Pro, 800k+ users, government-branded, used in IESO training and accepted in federal LCCA guidance |
| Enterprise MACC / abatement portfolio with NPV, IRR, payback and carbon-price scenarios | **SINAI Reduce** (US/Brazil; clients include ArcelorMittal, Siemens Energy); Arcadis Net Zero Catalyst; SLB; Sweep | Funded, enterprise-sold, workflow-integrated |
| Discovering Canadian grants and programs | helloDarwin (10k+ programs), GrantMatch (now BDO), ISED Business Benefits Finder, NRCan directory, Encentiv (utility rebates) | Human-readable discovery, AI Q&A, advisory attached |
| Compliance-market intelligence and position management (TIER, EPS, QC) | **ClearBlue Markets Vantage** (Toronto; Deloitte Canada partnership) | Market data, forecasts, compliance scenarios. **Does not** value abatement projects |
| Commercial-real-estate retrofit roadmaps | Audette, VadiMAP, Autocase, CRREM; KingSett free model | Funded, crowded, partly free |
| Energy-system scenario data | CER Energy Futures 2026, CODERS, CANOE, PyPSA-Canada, MESSAGEix-Canada | Public; useful as *inputs* |
| ITC claim preparation and defence | Big-4, Leyton, Ryan, BDO, law firms | Liability-bearing advisors own the channel |

## 2. Where meaningful gaps remain (Canada)

| Gap | Evidence | Confidence the gap is real | Who partially fills it today |
|---|---|---|---|
| **G1. Realized (not headline) carbon value for a specific facility and project.** Covers coverage status, system, credit-market price, credit-use limits, the 2030 AB floor, CCfDs and QC C&T. | Credit prices $18–80 vs a $95 headline. CCI (Jan 2026): the effective marginal price ranges from <$50 to >$130 where market prices look alike; the CCI recommends "transparent analytics to estimate" it. The May 2026 reset changed every path. No tool advertises project valuation under output-based mechanics. | Moderate (60–70%) | ClearBlue (positions, not projects); consultants in Excel |
| **G2. Clean-economy tax measures as cash flows**: rate by available-for-use date, labour-requirement rate, eligibility confidence, assistance reduction, CCA expensing window, CRA timing | 100% audit rate; ~⅓ of claims denied; $1.6B claimed vs ~$10B/yr budgeted; eligibility for process heat pumps is case-by-case; electrode boilers are not on the CT property list | Moderate–high (70%) | Tax advisors (claim-level, not investment-appraisal-level) |
| **G3. Explicit policy-regime risk in project valuation**, including CCfD value | Carbon VIX (NBER 2024): uncertainty depresses investment like a price cut. The CCfD rationale is certainty. The quant test shows P(NPV>0) moves 0% → 76% with a CCfD. | Moderate–high (70%) | Nobody productizes it; RETScreen MC covers technical/financial inputs only |
| **G4. Provenance**: every policy parameter tied to its source, legal status (announced / proposed / enacted / in force), effective dates and retrieval date | None of 20+ tools advertise source-level provenance for financial assumptions. GMF studies still point at the superseded $170-by-2030 schedule. Legal texts lag policy (GGPPA still showed $110 for 2026 in Apr 2026). | Moderate (65–75%) | Manifest Climate (cited disclosure analysis — a UX precedent, different domain) |
| **G5. Canadian machine-readable incentive rules (DSIRE-equivalent)** | No Canadian API exists; DSIRE and Rewiring America show it is an editorially subsidised public good | High that the gap exists; **low that it's worth filling** (maintenance C$200–350k/yr; low value per record, see 04) | helloDarwin/BDO (discovery only) |

## 3. Testing the original concept's differentiators

| Hypothesized differentiator | Verdict | Reason |
|---|---|---|
| Financial economics (NPV/IRR/payback) | ✖ Not a differentiator | RETScreen (free/cheap) and SINAI already do it |
| Uncertainty (Monte Carlo) | ◐ Only if it is *policy-regime* uncertainty | RETScreen already has MC on inputs. Policy-regime risk is novel, and matters only near the margin (04) |
| Policy + incentives connected to the decision | ◐ Narrowly | A handful of levers decide outcomes. Incentive breadth is noise at industrial scale (02, 04) |
| Energy/emissions assumptions | ◐ | Energy prices dominate, but users can already type them into any tool. **Grid-factor choice (average vs marginal) is an under-served credibility issue** (04, Ex1: NS net reduction only 17%) |
| Canada/jurisdiction specificity | ✔ for policy mechanics | Coverage thresholds, credit markets, floors, QC C&T and ITC rules are Canadian-specific and hard. The energy-price part is generic |
| Corporate investment workflow (portfolio, IC memo) | ✖ vs SINAI | Only worth building as a thin output (decision memo), not a platform |
| Provenance / reproducibility | ✔ | Unclaimed, cheap to do well, and valued where assumptions must be defended (P.Eng sign-off, CRA audit, investment committees, CCfD bids) |

**Result:** the original "engine" concept is mostly **already built** (the math, discovery and workflow parts). It is **only defensible in its narrow, Canada-specific policy-value layer (G1–G4)**.

## 4. Alternative concepts evaluated

Scores 1 (poor) to 5 (strong). "Differentiation" is relative to the incumbents above. "Feasibility" covers data availability and maintenance load for a very small team.

| # | Concept | Pain evidence | Differentiation | Data & maintenance feasibility | Build cost (inverse) | Buyer access / WTP | Total /25 |
|---|---|---|---|---|---|---|---|
| A | Original broad Canada Climate CapEx Engine (SaaS) | 3 | 1 | 2 | 1 | 2 | 9 |
| B | Canadian C&I incentive rules API ("DSIRE for Canada") | 3 | 4 | 1 | 2 | 2 | 12 |
| C | ITC eligibility and claim-readiness navigator | 4 | 2 | 3 | 3 | 2 (liability → advisors) | 14 |
| **D** | **Realized policy value engine for industrial projects** (carbon value + ITC/CCA + CCfD + policy-regime risk, with a decision memo) | 4 | 4 | 4 | 4 | 3 | **19** |
| **E** | **Open, provenance-tracked Canadian climate-policy parameter ledger** | 3 | 4 | 4 | 5 | 2 (weak alone) | **18** |
| F | Building BEPS compliance and retrofit planner | 2 | 1 | 3 | 2 | 3 | 11 |
| G | Lender-side transition-plan credibility (B-15) | 2 | 2 | 3 | 2 | 2 | 11 |
| H | Credit-price / compliance-cost forecaster | 4 | 1 (ClearBlue) | 2 (paid OTC data) | 3 | 3 | 13 |

**Selected: D built on E.** E (the ledger) is the open, low-cost foundation. It is a credibility and distribution asset and is useful even if D fails. D (the valuation kernel and decision memo) is the product that answers the question the evidence says matters: *what is this project actually worth to this facility under Canadian policy as it really is, and how robust is that to policy risk?* The combination avoids the incumbents' strengths:
- It is not a MACC platform (SINAI).
- It is not grant discovery (helloDarwin/BDO).
- It is not market intelligence (ClearBlue). Market prices are an *input* with provenance.
- It is not buildings (Audette et al.).

## 5. Competitive risks to the selected concept

1. **Incumbent extension.** SINAI adds a Canada pack, or ClearBlue/Deloitte adds project valuation. *Mitigation:* be open-source and provenance-first, so it is cheap to adopt or partner with. Position as the layer they could license or cite, not a head-on platform.
2. **Consultant substitution.** Large emitters pay advisors. *Mitigation:* target advisors as users (they rebuild these assumptions on every engagement) as well as in-house analysts.
3. **Small buyer universe.** About 300–500 parent firms of about 1,000 priced facilities, plus a consultant tier. *Implication:* keep operating cost near zero. Monetize, if at all, through support, custom cases or data licensing, not seat-based SaaS.
4. **Policy volatility.** About 15 material changes in 24 months. *Mitigation:* scope the ledger to the ~45 (v0.1) to ~55 (target) records that move decisions. Model legal status explicitly. Re-run saved cases on every ledger change ("decision drift").
5. **Liability.** ITC eligibility and carbon value are judgement calls. *Mitigation:* output scenario ranges and eligibility confidence, never a single "you qualify". Cite every source. Include a clear not-advice notice.
