# ADR-0003: Deterministic, pure-function valuation kernel; no AI in the valuation path

- **Status:** Accepted (2026-09-29)
- **Context:** Outputs feed investment committees, CRA-audited ITC claims and CCfD negotiations. Users need to reproduce and audit every number. LLM outputs are non-deterministic and hard to audit.
- **Decision:** The kernel is written as pure Python functions over typed inputs (pydantic), using numpy/scipy only. Monte Carlo takes an explicit seed and is vectorized. The kernel makes no network I/O, reads no wall-clock time (the `as_of` date is an input) and calls no LLM. Results carry a hash of the case, the ledger version and the seed.
- **Consequences:** Byte-identical re-runs, simple testing (golden files plus property tests) and a low dependency surface. AI is confined to optional tooling around the ledger (ADR-0006).
