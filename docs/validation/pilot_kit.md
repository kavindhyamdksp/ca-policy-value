# Design-partner pilot kit (M7)

For partners who agreed to run PolicyValue CA on a real project. Goal (gate G1): ≥3 partners run a real case,
and we learn whether the memo changes or sharpens a decision. Budget: 2–3 hours of partner time.

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
| 2. Pick a template | 10 min | Copy the closest golden case: heat pump (QC/BC) or AB abatement with CCfD |
| 3. Enter the case | 30–45 min | Fill in `facility`, `project`, `prices`, `finance`, `policy` per the [user guide](../user_guide.md). Add overrides with reasons for anything the partner knows better than the ledger. |
| 4. Run and read | 20 min | `pv run my-case.yaml`; walk through answer, value stack, breakeven vs band, grid, MC, provenance |
| 5. Stress it | 20 min | Add grid dimensions (`itc_granted`, `floor_status`, `ccfd`, `coverage`, `credit_scenario`); set MC regimes that reflect the partner's own policy views |
| 6. Compare | 15 min | Put the memo next to the partner's existing analysis. Where do they differ, and why? |
| 7. Feedback | 15 min | Complete the form below |

## Data handling

- Case files and outputs stay with the partner. We ask only for the feedback form and, if the partner agrees,
  an anonymized results.json (case_id renamed, capex rounded).
- Licensed prices go in `overrides` locally. The ledger stores only public observations (ADR-0007).
- The memo is a scenario analysis, not tax or investment advice; eligibility needs the partner's tax advisor.

## Troubleshooting

| Message | Fix |
|---|---|
| `record fed.nir.grid_ef unavailable` | Add an override with your grid intensity, or `grid_factor: marginal` + `marginal_grid_ef_g_kwh` |
| `supply prices.natural_gas_gj` | Enter your delivered gas price ex-carbon, $/GJ |
| `... below min_legal_status` | The record exists but is not yet law at your threshold; lower `min_legal_status` or override it |
| `phase-out unverified` | Your in-service year falls in 2030–2033; override `fed.cca.expensing` for that year |
| `province parsed as boolean` | Write `province: "ON"` with quotes |

## Feedback form

Copy into `docs/validation/pilots/NN-<segment>.md` (anonymized).

```markdown
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
11. Would your organization pay for support / custom modules / hosted convenience? rough range: ______
12. Anything else:
```

## G1 read-out

After ≥3 pilots, summarize against [DECISION.md](../../DECISION.md) gate G1: pilots completed, decisions
changed or sharpened, time to first memo, ledger corrections received, and willingness to keep using it.
Update DECISION.md, SPEC.md and IMPLEMENTATION_PLAN.md with the outcome.
