# ADR-0002: Policy parameters live in a bitemporal, legal-status-aware YAML ledger in git

- **Status:** Accepted (2026-09-29)
- **Context:** Parameters change about every 6–7 weeks, and legal texts lag announcements. For example, the national carbon path was announced in May 2026 while GGPPA Sch. 4 still showed $110 for 2026, and the AB floor regulation is due 31 Dec 2026. Users must defend *which* information they relied on and when. Volume is small (~55 records).
- **Decision:** Store one YAML file per instrument, with records validated by JSON Schema. Each record carries `effective_from/to` (valid time), `recorded_at` (transaction time; git history is the audit log), `legal_status`, `sources[]` with retrieval dates, and `confidence`. Releases are git tags. The kernel filters by `as_of` and by minimum legal status.
- **Alternatives rejected:**
  - A database (Postgres/SQLite service) adds ops cost with no benefit at this scale.
  - A spreadsheet has poor diffing and review, and no schema.
  - Scraping into a pipeline doesn't work because the sources are prose that needs judgement.
- **Consequences:** Pull-request review becomes the editorial workflow. `pv drift` can compare any two tags. Contributors need no infrastructure.
