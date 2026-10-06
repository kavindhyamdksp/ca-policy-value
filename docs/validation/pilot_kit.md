# Design-partner pilot kit (M7)

PolicyValue CA is free and open source, offered at no cost; pilots are not sales conversations. A pilot is
a practitioner running it on a real project with us, so we learn whether the memo changes or sharpens a
decision and what to fix. Goal (gate G1): ≥3 partners run a real case. Budget: 2–3 hours of partner time.

## Finding pilot partners

Anyone who evaluates industrial decarbonization projects in AB, ON, BC or QC: facility energy or
compliance analysts, consultants, CCUS/CCfD developers, and researchers. Useful channels: your own network
and LinkedIn, industry association events (IETA, CME, CIAC), and university or NGO energy groups.

Keep contact details in a private list outside this repository. A short invitation:

> I've built a free, open-source tool that values Canadian industrial decarbonization projects under the
> carbon-pricing and clean-tax rules as they actually apply — credit prices, floors, CCfDs, ITCs — with a
> cited source for every number. Would you try it on one real or recent project (2–3 hours)? Your data
> stays on your machine, and your feedback shapes the next version.

## What the partner needs

- A laptop with Python 3.11–3.13 and git (or we can run it together on a screen share — the partner's data
  stays on the partner's machine either way).
- One live or recent project: capex, in-service date, life, annual energy deltas (gas GJ, electricity MWh),
  opex change, and the facility's coverage status. Energy deltas come from the partner's engineering work;
  the tool does not simulate energy.
- Their own gas and electricity tariffs and, if they have them, licensed credit prices (entered as
  overrides — never committed or shared).

## Session plan

| Step | Time | What happens |
|---|---:|---|
| 1. Install | 10 min | `pip install -e .`, then `pv run cases/golden_hp_qc.yaml` and open the memo |
| 2. Pick a template | 10 min | `pv case template --kind heat_pump --out my-case.yaml` (or `--kind abatement` for a large emitter with a CCfD); every placeholder is marked REPLACE |
| 3. Enter the case | 30–45 min | Fill in `facility`, `project`, `prices`, `finance`, `policy` per the [user guide](../user_guide.md). Add overrides with reasons for anything the partner knows better than the ledger. |
| 4. Run and read | 20 min | `pv run my-case.yaml`; walk through answer, value stack, breakeven vs band, grid, MC, provenance |
| 5. Stress it | 20 min | Add grid dimensions (`itc_granted`, `floor_status`, `ccfd`, `coverage`, `credit_scenario`), a one-way `sensitivity` block, and MC regimes that reflect the partner's own policy views; developers can add `ccfd_strike` to solve for the strike they need |
| 6. Compare | 15 min | Put the memo next to the partner's existing analysis. Where do they differ, and why? |
| 7. Feedback | 15 min | Complete the form below |

## Data handling

- Case files and outputs stay with the partner. We ask only for the feedback form and, if the partner agrees,
  an anonymized results.json (case_id renamed, capex rounded).
- Licensed prices go in a separate local file, `pv run my-case.yaml --overrides prices.local.yaml`
  (`*.local.yaml` is git-ignored). The ledger stores only public observations (ADR-0007). Outputs list
  override values, so treat `out/` as confidential too.
- The memo is a scenario analysis, not tax or investment advice; eligibility needs the partner's tax advisor.

## Troubleshooting

| Message | Fix |
|---|---|
| `set project.itc_rate_key to one of: …` | The ITC rate record holds several rates (CCUS): name the component, e.g. `capture_to_2035` |
| `supply prices.natural_gas_gj` | Enter your delivered gas price ex-carbon, $/GJ |
| `... below min_legal_status` | The record exists but is not yet law at your threshold; lower `min_legal_status` or override it |
| `phase-out unverified` | Your in-service year falls in 2030–2033; override `fed.cca.expensing` for that year |
| `province parsed as boolean` | Write `province: "ON"` with quotes |

## Feedback form

Copy into `docs/validation/pilots/NN-<segment>.md` (anonymized). The front matter is the structured record
summarized by `python tools/pilot_scorecard.py docs/validation/pilots`; only these fields are accepted.

```markdown
---
id: "NN"
date: 2026-11-15
segment: covered_facility      # covered_facility | consultant | developer | researcher | other
province: AB                   # AB | "ON" | BC | QC | FED | other
ran_real_case: yes             # yes | no
decision_changed_or_derisked: no   # yes | no (question 4)
time_to_first_memo_min: 45
would_use_next: maybe          # yes | maybe | no (question 9)
ledger_corrections: 0          # count of ledger errors reported (question 7)
---
Pilot NN · segment: ______ · province: __ · date: ____-__-__

1. Project type and size (bucket): ______
2. Did the memo's answer (GO / NO-GO / DEPENDS-ON) match your prior view?  yes / no — why?
3. Carbon value you used before vs the memo's realizable base ($/t): ____ vs ____
4. Did anything in the memo change, or sharpen, the decision or its conditions?  (describe)
5. Which section was most useful? least useful?
6. Which ledger values did you override, and why?
7. Anything wrong or missing in the ledger (value, status, source)?
8. Time to first memo (minutes): ____   Blockers: ______
9. Would you use it on the next live decision?  yes / maybe / no — what would change your answer?
10. Would you rely on `pv drift` alerts when policy changes?  yes / no
11. May we mention your organization type (not name) as a pilot in the project README?  yes / no
12. Anything else:
```

## G1 read-out

After ≥3 pilots, run `python tools/pilot_scorecard.py docs/validation/pilots` and summarize against
[DECISION.md](../../DECISION.md) gate G1: pilots completed, decisions changed or sharpened, time to first
memo, ledger corrections received, and whether partners would use it again.
Update DECISION.md, SPEC.md and IMPLEMENTATION_PLAN.md with the outcome.
