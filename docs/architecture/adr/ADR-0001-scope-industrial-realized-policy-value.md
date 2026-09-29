# ADR-0001: Scope the product to realized policy value for industrial projects

- **Status:** Accepted (2026-09-29)
- **Context:** The original concept, a broad Canada Climate CapEx Engine, overlaps with RETScreen (NPV/IRR/MC), SINAI (MACC with NPV/IRR), helloDarwin and BDO (grant discovery), ClearBlue (compliance markets) and Audette et al. (buildings). Quantitative tests show policy terms flip decisions mainly for covered industrial facilities and near-margin projects. For buildings and sub-threshold sites outside QC they do not.
- **Decision:** Scope the MVP to (a) industrial carbon-pricing value realized at the facility, including QC C&T, floors and CCfDs, (b) clean-economy ITCs and CCA expensing as conditional cash flows, and (c) policy-regime robustness, for federal + AB/ON/BC/QC. Exclude grant discovery, utility rebates, buildings/BEPS, MACC portfolio workflow, credit-price forecasting and energy simulation.
- **Consequences:** A small buyer universe and a narrow but defensible value. The ledger stays ~55 records. Expansion (CFR, ÉcoPerformance, other provinces) must be justified by demand at G1/G2.
