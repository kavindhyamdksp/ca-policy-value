# Interview notes (gate G0)

One file per interview: `NN-<segment>.md`, e.g. `01-covered_facility.md`. **Anonymized**: no names,
employers, facility identifiers or contact details — segment and province only. Nothing without consent.

The front matter is the structured record read by `tools/gate_scorecard.py`; unknown fields are rejected,
so personal data cannot be added to it. Free-text notes go below the front matter (anonymized too).

```markdown
---
id: "01"
date: 2026-10-20
segment: covered_facility          # covered_facility | consultant | developer
province: AB                       # AB | "ON" | BC | QC | FED | other
carbon_method: "headline $95"      # what they actually used, in a few words (guide Q2)
criterion_a: "yes"                 # guide §1 scoring: headline or rebuilt by hand each time = yes
would_use_kernel_live: "maybe"     # guide Q15: only a concrete yes with a named decision = yes
would_use_ledger_alone: "yes"      # guide Q16
open_questions:                    # SPEC §9, optional
  q1: "values at headline; board wants breakeven"
  q2: "annual compliance screening matters more than CCfD bids"
---

## Notes
- Current method: …
- Rebuild effort: …
- Tools/advisors: …
- Reaction to demo: …
- Also record: credit position, preferred output, licence constraints, missing sources.
```
