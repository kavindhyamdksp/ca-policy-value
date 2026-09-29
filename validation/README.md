# Validation model (research phase — frozen)

`decision_sensitivity.py` is the research-phase model behind [docs/research/04_quantitative_validation.md](../docs/research/04_quantitative_validation.md). It is **not** product code. It serves as the **oracle** for the MVP kernel's acceptance test (IMPLEMENTATION_PLAN §2.4-1).

- `params.yaml`: every parameter carries `status` (verified/inferred) and `source`.
- `results.md`: generated output (seed 20260929).

Run: `pip install numpy scipy pyyaml && python3 decision_sensitivity.py > results.md`

Note: YAML keys `"ON"` are quoted because YAML 1.1 parses a bare `ON` as boolean `true`. The ledger schema must guard against this, for example with a validator for province codes.
