# Interview guide (Phase 0, gate G0)

Purpose: buy the primary evidence the research lacks. G0 passes if, of ≥12 interviews in the segment mix of
[DECISION.md](../../DECISION.md), **≥6** interviewees (a) value carbon at the headline price or rebuild the
carbon value by hand for each engagement **and** (b) would use a cited ledger + kernel on a live decision.
Fallback: ≥3 who would use the ledger alone → continue with the ledger only.

Format: 30 minutes, video or phone. One interviewer, one note-taker. Record nothing without consent.
Notes go to `docs/validation/interviews/NN-<segment>.md` **anonymized**: no names, employers or facility
identifiers; segment and province only.

## Segments (target mix)

| Segment | Target | Examples |
|---|---:|---|
| Covered-facility analysts / finance leads (AB TIER, ON EPS, BC OBPS, QC SPEDE) | 7+ | energy, process, corporate finance |
| Consultants / ESCOs | 3+ | engineering and energy-services firms |
| CCUS / CCfD developers | 2+ | project developers, CCfD counterparties |

## Opening (2 min)

"We're testing whether a cited, open dataset of Canadian carbon-pricing and clean-tax parameters, plus a
small valuation model, would help decisions like yours. There's nothing to sell today. Please don't share
anything confidential; you can decline any question."

## 1. Current method (8 min)

1. Think of the last decarbonization project you evaluated. What was it, roughly, and what decided it?
2. How did you put a value on avoided tonnes? Headline price, credit price, internal carbon price, or nothing?
   *Probe:* who chose that number, and where did it come from?
3. Does your facility buy or sell credits (EPCs, EPUs, performance credits, SPEDE allowances)? At what price
   did you last transact or quote?
4. How did you treat the AB floor, a CCfD, or the May 2026 price reset, if at all?
5. How did you treat the Clean Technology ITC and CCA expensing? Was eligibility certain? Timing?

**Score (a):** headline or hand-rebuilt each time = YES; sourced, maintained credit-price model = NO.

## 2. Rebuild effort and pain (5 min)

6. How often are these assumptions rebuilt: per project, per quarter, per budget cycle?
7. Roughly how many hours does that take, and who does it?
8. Has a policy change (price reset, floor, ITC rules) ever forced you to redo an analysis? What happened?
9. When you present to an investment committee, what do they challenge about the policy assumptions?

## 3. Tools and advisors (5 min)

10. Which tools do you use for these valuations (spreadsheets, RETScreen, SINAI, ClearBlue, internal models)?
11. Which advisors (tax, carbon-market, engineering) feed in, and what do they cost you in time or money?
12. What does your current approach get wrong, or leave out, that worries you?

## 4. Reaction to the demo (7 min)

Show the demo kit: the Example 1/3 tables and a mock memo (`pv run cases/golden_ab_abatement_ccfd.yaml`).

13. What's the first thing you'd check before trusting this memo?
14. Which part is most/least useful: breakeven vs realizable band, the policy-state grid, the MC, the
    provenance appendix, `pv drift`?
15. Would you use it on a live decision in the next 6 months? What would have to be true?
    **Score (b):** a concrete yes with a named decision = YES.
16. Would the ledger alone (without the model) be useful? How would you consume it?

## 5. Close (3 min)

17. Would you pilot it on a real case with us (≈2–3 hours of your time)? See the [pilot kit](pilot_kit.md).
18. Who else should we talk to?
19. Willingness to pay (only if natural): would your organization pay for support, custom modules or a
    hosted version? Roughly what budget line would that come from?

## Also record (for SPEC §9 open questions)

- Credit position (long/short/neutral) and whether credit-use limits bind.
- Preferred output (memo, Excel, API) and who reads it.
- Licence constraints on sharing credit prices; would they supply prices via local overrides?
- Any policy source we are missing.

## Synthesis sheet (one row per interview)

| # | Segment | Prov | (a) headline/hand-rebuilt | (b) would use on live decision | Ledger-only use | Pilot? | Top pain | Top objection |
|---|---|---|---|---|---|---|---|---|
