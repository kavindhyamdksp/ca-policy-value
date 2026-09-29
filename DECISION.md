# Validation decision

**Date:** 2026-09-29  **Decision:** **REFOCUS**

| Scope | Verdict |
|---|---|
| Original concept: broad "Canada Climate CapEx Engine" connecting policy, incentives, energy/emissions and NPV/IRR/payback/uncertainty for corporate decarbonization decisions | **DO NOT BUILD** as specified |
| Refocused concept: **PolicyValue CA**, an open, provenance-tracked ledger of the Canadian policy parameters that decide industrial decarbonization projects, plus a deterministic kernel that turns them into *realized* project value, breakeven carbon price and policy-regime risk | **Build a minimal MVP behind explicit validation gates** (see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)) |

## Why not the original concept

1. **The core is already solved.** Project NPV/IRR/payback with a carbon input and Monte Carlo is in RETScreen, which is free or ~CA$869/yr, government-branded and has 800k+ users. Enterprise MACC with NPV/IRR and carbon-price scenarios is sold by SINAI and others. Canadian grant discovery is sold by helloDarwin and BDO/GrantMatch. Compliance-market intelligence is sold by ClearBlue. ([gap analysis](docs/analysis/competitor_gap_analysis.md))
2. **Broad incentive coverage is expensive and low-value.** A curated Canadian incentive rules base runs to ~120–200 records and 250–500 edits a year, costing C$200–350k/yr ([02](docs/research/02_policy_data_feasibility.md)). Meanwhile, utility rebates and most programs are noise at industrial scale ([04](docs/research/04_quantitative_validation.md)).
3. **Broad corporate demand is weak and falling in 2025–26:**
   - the consumer carbon price was removed;
   - the CSA climate rule is paused;
   - there is no transition-plan mandate and the taxonomy is voluntary;
   - greenwashing rules were narrowed;
   - two big banks retired their financed-emissions targets.

   Most decisions are infrequent and made by consultants. Economics, not analytics, is the binding constraint for mid-market firms and buildings. ([03](docs/research/03_user_needs_workflows.md))
4. **For buildings and sub-threshold sites outside Quebec, policy terms do not flip decisions** in our tests. There is no carbon price, and ITC effects are $0.2–0.45M but not decisive. That removes the largest visible segment from the original concept's value proposition.

## Why the refocused concept is worth a small, gated build

1. **Policy terms flip decisions for covered industrial facilities and near-margin projects:**
   - The carbon-value treatment (coverage, credit price vs headline, floor, CCfD) was the **single largest NPV swing factor** for a covered Ontario facility.
   - Across Alberta abatement projects with breakevens of $54–117/t, the GO/NO-GO answer depended entirely on which carbon-value assumption was used. The assumptions are worth $20–122/t levelized.
   - A CCfD moved P(NPV>0) from **0% to 76%** (0% to 86% on policy risk alone).
   - The ITC flipped heat-pump decisions in QC and BC.

   ([04](docs/research/04_quantitative_validation.md))
2. **The headline-price shortcut is a consequential and likely common error.** How common is untested: the evidence is guidance that prescribes headline or shadow schedules, and G0 tests it. It overstates value 1.25× in Ontario, ~1.5× in BC and ~5× in Alberta before 2030. Credit markets are oversupplied; the CCI finds effective marginal prices ranging from <$50 to >$130/t where market prices look alike, and calls for "transparent analytics".
3. **No product combines** realized facility-level carbon value, clean-economy tax measures as cash flows, explicit policy-regime/CCfD risk and source-level provenance for Canada. Confidence is moderate (60–75%); enterprise tools are opaque, which is why demos are a gate.
4. **It is cheap to build and maintain when scoped.** About 55 ledger records and roughly 85–130 h/yr of maintenance ([data feasibility](docs/analysis/data_feasibility.md)). It needs no servers: a git repo, Python and a static site. The open ledger has standalone value (for consultants, researchers and GMF/LCCA studies still pointing at the superseded $170-by-2030 schedule) even if the kernel fails to find buyers.

## What this decision is *not* confident about

- **Primary demand.** All demand evidence is secondary. No user interviews were possible in this assignment. This is the largest open risk.
- **Buyer universe.** It is small: ~1,000 priced facilities, ~300–500 parent firms, plus consultants. It may support an open-source tool plus services, not a venture-scale SaaS.
- **Incumbent opacity.** SINAI and ClearBlue enterprise tiers may already do parts of G1–G3 privately.
- **Timing.** Rules change within months: the federal benchmark publication (late 2026), the AB floor regulation (by 31 Dec 2026) and the ITC domestic-content decision are all pending.

## Gates (binding)

| Gate | When | Pass criteria | If failed |
|---|---|---|---|
| **G0: Problem validation** | Before or alongside Phase 1, ≤ 6 weeks | At least 12 interviews (≥6 covered-facility analysts or finance leads, ≥4 consultants/ESCOs, ≥2 CCfD/CCUS developers). At least 6 confirm they currently value carbon at headline or build it by hand each time **and** would use a cited ledger + kernel on a live decision. Demos of SINAI and ClearBlue confirm they do not value projects under OBPS mechanics with policy-regime risk. | Stop the kernel. Keep only the open ledger if ≥3 interviewees would use it; otherwise archive. |
| **G1: MVP usefulness** | End of Phase 1 | At least 3 design partners run the kernel on a real project or CCfD bid and say the memo changed or de-risked the decision. Ledger freshness SLA met for 60 days. Maintenance ≤ 15 h/month. | Stop at Phase 1; publish the ledger only. |
| **G2: Expansion** | End of Phase 2 | At least 2 paying or committed users (support contract, custom module, or data licence), or an institutional host (NGO, university, association) willing to co-maintain the ledger. | Keep as open-source maintenance mode; no hosted product. |

## Kill criteria (any one)

- An incumbent ships Canadian project-level valuation under OBPS mechanics with policy-regime risk before G1.
- The scoped ledger needs more than 0.25 FTE to keep within its freshness SLA.
- Interviews show covered facilities already get realized carbon value from their market advisors and would not change workflow.
