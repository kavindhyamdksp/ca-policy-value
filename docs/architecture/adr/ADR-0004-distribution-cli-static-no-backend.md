# ADR-0004: Ship as a Python package, CLI and static outputs; no hosted backend in the MVP

- **Status:** Accepted (2026-09-29)
- **Context:** The buyer universe is small and the priority is low operating cost. Target users (analysts, consultants) work in Excel and Python and need offline, confidential use, since project data is commercially sensitive.
- **Decision:** Distribute as a pip-installable package (`policyvalue-ca`) with a Typer CLI. Outputs are Markdown/HTML memos plus JSON/CSV. The ledger is browsable on GitHub, with a static MkDocs site in Phase 2. A thin Excel export (CSV) covers spreadsheet users. A hosted UI or API is considered only if G2 shows paying demand.
- **Consequences:** $0 hosting and no data-custody burden. Adoption requires a CLI or notebook comfort, mitigated by golden example cases and an HTML memo. We cannot observe usage directly; design partners report it.
