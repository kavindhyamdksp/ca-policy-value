# ADR-0006: AI is limited to source-change monitoring and drafting ledger diffs for human review

- **Status:** Accepted (2026-09-29)
- **Context:** The main operating cost is noticing and interpreting policy changes across ~30 source pages (Finance, CRA, NRCan, ECCC, AB, ON, BC, QC, CGF, CARB). Reading prose and proposing structured changes is a good fit for an LLM. Deciding values unaided is not.
- **Decision:** Phase 2 adds an optional scheduled job. It fetches the monitored sources, detects content changes (hash/diff), and asks an LLM to draft a proposed ledger diff with verbatim excerpts, locators and a suggested `legal_status`. The job opens a PR labelled `needs-human-review`. Merges are always human, and `pv drift` output is attached so reviewers see the decision impact. Nothing AI-generated enters the kernel.
- **Consequences:** Maintenance time falls without an automation-accuracy risk. The feature is optional (works without an API key). Model costs are bounded (tens of pages per week).
