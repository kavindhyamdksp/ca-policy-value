# ADR-0007: Open licences; no redistribution of proprietary price data

- **Status:** Accepted (2026-09-30): the owner confirmed a free, non-commercial, open-source project (DECISION.md).
- **Context:** The ledger's value as a credibility and distribution asset depends on open reuse. Government sources are OGL-Canada (commercial reuse with attribution). Credit-market prices from ClearBlue, Argus or Carbon Pulse are licensed and not redistributable.
- **Decision:** Code under Apache-2.0. Ledger data under CC BY 4.0, keeping required OGL-Canada attributions per source. The ledger stores only public observations (auction results, government reports, public secondary citations with dates). Users can inject licensed prices locally through overrides, and these are never committed.
- **Consequences:** Anyone, including competitors, can reuse the ledger. That is acceptable and serves the wedge strategy. Monetization, if any, comes from support, custom modules, hosted convenience or institutional co-maintenance.
