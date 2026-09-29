# ADR-0005: Carbon value = realized marginal value at the facility, never headline by default

- **Status:** Accepted (2026-09-29)
- **Context:** Output-based systems give free allocation, so a facility's marginal value of abatement is the price at which it can buy or sell credits. That price is capped by the fund price and shaped by credit-use limits. In 2026 credit prices are well below the headline (AB ~$20, ON ~$72–80, BC ~$65, federal OBPS ~$37.50). Sub-threshold sites realize $0 outside QC. QC C&T reaches all gas users (~$45). AB adds a floor from 2030 (announced; regulation pending). CCfDs guarantee a strike on contracted volume. The tornado analysis shows this assumption is the largest NPV swing factor for covered facilities.
- **Decision:** `realized_value(year) =`
  - `0` if not covered, outside QC;
  - QC: the C&T price path (all users);
  - covered: `market_scenario(year)`, bounded by `fund_price(year)`, then `max(·, floor(year))` if the floor's legal status meets the user's threshold (else it becomes a scenario);
  - with a CCfD: `max(strike, ·)` on the contracted volume and term.

  Headline is exposed as a named `upper_bound` scenario. The memo always shows the breakeven flat carbon price against the realizable band.
- **Consequences:** Correct by construction for the common error. Requires credit-price observations with dates, which are thin and partly proprietary; users may supply licensed prices locally. Position (long/short) and credit-use limits are modelled simply in the MVP (a fund-price cap only); detailed limits come in Phase 2.
