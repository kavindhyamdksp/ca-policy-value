# Ledger changelog

Ledger releases are git tags `ledger-vYYYY.MM.N`. Each entry lists added, changed and removed records.
Run `pv drift --from <old tag> --to <new tag>` to see the decision impact on saved cases.

## ledger-v2026.10.0 — 2026-09-29 (seed, v0.1)

First release: 34 entries / 33 record ids, federal + AB/ON/BC/QC. Every value was read from a source
fetched on 2026-09-29 (retrieved date on each source). Human tax review of ITC/CCA records is pending
(plan §6); records carry `reviewer: ... human tax review pending`.

Added
- Federal carbon: `fed.carbon.benchmark_path` (announced), `fed.ggppa.schedule4`, `fed.fuel_charge`,
  `fed.obps.thresholds`, `fed.obps.credit_obs` (observation).
- Federal tax: `fed.ct_itc.rate_schedule`, `fed.ct_itc.labour_rate`, `fed.ct_itc.entities`,
  `fed.ct_itc.eligibility_classes`, `fed.ct_itc.domestic_content` (proposed), `fed.ccus_itc.rates`
  (proposed: only secondary sources state the rates), `fed.cca.expensing`, `fed.cca.class_rates`.
- Factors and instruments: `fed.nir.gas_ef` (province-specific, ECCC emission factors v4.0),
  `fed.cgf.ccfd`, `ab.ccfd.joint_pool` (announced).
- AB: `ab.tier.fund_price` (2026 in_force; 2027+ announced), `ab.tier.floor` (announced),
  `ab.tier.credit_obs`, `ab.tier.dic_cap` (announced), `ab.tier.threshold`.
- ON: `on.eps.price_schedule`, `on.eps.epu_obs`, `on.eps.thresholds`.
- BC: `bc.obps.price`, `bc.obps.credit_obs`, `bc.obps.threshold`.
- QC: `qc.spede.coverage`, `qc.spede.auction_obs`, `qc.spede.reserve_escalation`.
- Reference: `ref.tax.corporate`, `ref.electricity.large`, `ref.electricity.medium`.

Not included (could not be verified within the fetch budget; the kernel requires a user input instead)
- `fed.nir.grid_ef` — supply `overrides: [{record: fed.nir.grid_ef, ...}]` or use `grid_factor: marginal`.
- `fed.ce_itc.rate` — required only for `itc_measure: ce` (override).
- `bc.carbon_tax` — not used by the kernel (non-covered BC sites already realize $0).
- `ref.gas.delivered` — supply `prices.natural_gas_gj` (user tariff).

Known gaps recorded in notes
- `fed.carbon.benchmark_path`: 2028–29 and 2031–39 not stated by the fetched source; the kernel
  interpolates linearly between stated years.
- `fed.cca.expensing`: 2030–2033 phase-out percentages not stated; in-service in 2030–2033 requires an override.
- `fed.ct_itc.eligibility_classes`: process/waste-heat heat pumps and electric boilers are `not_listed`.
