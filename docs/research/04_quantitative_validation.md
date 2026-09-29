# 04 — Quantitative validation: do policy, incentives, jurisdiction and uncertainty change decisions?

*Prepared 2026-09-29. Model: [`validation/decision_sensitivity.py`](../../validation/decision_sensitivity.py). Parameters: [`validation/params.yaml`](../../validation/params.yaml). Full output: [`validation/results.md`](../../validation/results.md). Seeded and reproducible (`python3 decision_sensitivity.py`).*

## Why this test

The original concept assumes that connecting policy and incentives to project economics changes corporate decisions. If decisions are dominated by energy prices and capex, a policy-aware engine is a nice-to-have. If policy terms regularly flip GO/NO-GO, the engine has a real job. We test that directly on three stylized projects.

**Caveats.** These are illustrative projects, not engineering estimates. Gas delivered prices, capex, COP and tax rates are [inferred] (see `params.yaml` status fields). Monte Carlo regime probabilities are **subjective judgements chosen to illustrate the mechanism**. The conclusions below rely on *relative* effects and on where decisions flip, not on the absolute NPVs.

## Example 1 — 2 MWth industrial process heat pump (retrofit, $3.5M)

Same project, five provinces, three carbon-value treatments, with and without the 30% Clean Technology ITC (and Class 43.1 expensing, tied to the same eligibility). NPV $M at 8% nominal over 20 years.

| Prov | ITC | Not covered | Covered, market credit value | Covered, headline value | Breakeven flat $/t |
|---|---|---|---|---|---|
| QC | yes | +0.70 | +0.70 | +0.70 | 31 |
| QC | no | −0.13 | −0.13 | −0.13 | 76 |
| ON | yes | −4.22 | −2.44 | −1.99 | 230 |
| ON | no | −5.05 | −3.27 | −2.82 | 276 |
| AB | yes | −3.41 | −2.11 | −1.07 | 177 |
| AB | no | −4.24 | −2.93 | −1.90 | 221 |
| BC | yes | −0.85 | +0.66 | +1.37 | 47 |
| BC | no | −1.68 | −0.17 | +0.54 | 92 |
| NS | yes | +1.65 | +2.51 | +3.81 | −93 |
| NS | no | +0.82 | +1.68 | +2.98 | −46 |

(QC cap-and-trade reaches every gas user, so coverage status does not matter there.)

**Findings**
1. **The biggest driver is jurisdiction, mostly through the electricity-to-gas price spread, not policy.** The same project ranges from −$4.2M (Ontario, not covered) to +$2.5M (Nova Scotia). Ontario and Alberta are deeply negative under every policy treatment. Their breakeven carbon values ($177–276/t) are far above anything realizable.
2. **Policy terms flip decisions in the marginal jurisdictions (QC, BC).** Four flips were detected:
   - QC: the ITC flips NO-GO to GO.
   - BC: coverage status flips it (a sub-threshold site loses, a covered site wins).
   - BC without ITC: the headline shortcut says GO, but realized market value says NO-GO.
   - BC covered: the ITC flips it.
3. **The headline-price shortcut is systematically wrong** for covered facilities outside Quebec. Valuing avoided tonnes at the $95–140 benchmark instead of the credit price overstates carbon value by 25% (ON) to about 5× (AB before its floor starts in 2030).
4. **ITC details are second-order but not trivial.** On the QC case:
   - a 1–3 year CRA processing lag costs $0.06–0.12M;
   - missing the labour requirements (rate falls to 20%) costs $0.20M;
   - slipping the in-service date into 2034 costs $0.50M against a +$0.70M base. The rate falls to 15% and the project also misses the pre-2030 Class 43.1 immediate-expensing window.
5. **Emissions assumptions change the story, even when they don't change the NPV.** Net of added grid emissions (average factors), the heat pump cuts 100% of on-site tonnes in QC, 88% in ON, 47% in AB and **17% in NS**. At an Ontario marginal gas-fired factor (~450 g/kWh) the ON figure falls to 29%. The best financial case (NS) is the worst climate case. A tool that reports "$/t abated" without the grid factor choice misleads.

**Tornado (ON, covered, market carbon, ITC granted; base −$2.44M)**

| Driver | Swing $M |
|---|---|
| Carbon treatment (not covered ↔ headline) | 2.23 |
| Electricity price ±20% (e.g., Class A vs Class B) | 1.71 |
| Gas price ±30% | 1.40 |
| CT ITC + expensing (denied ↔ granted) | 0.83 |
| Capex −10% / +30% | 0.81 |
| Discount rate 6–10% | 0.07 |

For a covered facility, **the carbon-value assumption is the single largest swing factor**, ahead of energy prices. Policy inputs (carbon treatment plus ITC) together account for about 43% of the summed swings (3.06 of 7.05).

## Example 2 — Commercial building heat pump at boiler end-of-life (not an industrial emitter)

Incremental capex $0.75M; NPV $M.

| Prov | Taxable owner + CT ITC | Taxable, ITC denied | Tax-exempt owner (MUSH) |
|---|---|---|---|
| QC | −0.33 | −0.53 | −0.63 |
| ON | −0.73 | −0.92 | −1.17 |
| AB | −0.62 | −0.82 | −0.99 |
| BC | −0.37 | −0.57 | −0.69 |
| NS | −0.26 | −0.46 | −0.55 |

**Findings.** Nothing flips. Below the industrial thresholds there is no carbon price outside Quebec, and utility rebates are small or exclude fuel switching (research file 02). The case is negative everywhere at these assumptions. Owner tax status is worth $0.3–0.45M because tax-exempt owners cannot claim the ITC, but it does not change the answer. **For buildings, the decision is set by the energy spread, capex and (where it exists) a building performance standard, not by incentive modelling.** This supports excluding buildings from the refocused MVP.

## Example 3 — Large Alberta emitter: which carbon-value assumption clears the hurdle?

Generic project abating 50 kt/yr for 20 years with +$1M/yr net opex. Capex swept from $15M to $60M. NPV $M.

| Capex $M | Breakeven flat $/t | Headline | Market $20, no floor | Market + 2030 floor | CCfD $85 to 2040 | Outcome |
|---|---|---|---|---|---|---|
| 15 | 54 | +25.5 | −13.0 | +5.1 | +13.9 | **Flips**: NO-GO only on merchant credits |
| 25 | 75 | +17.6 | −20.9 | −2.8 | +6.0 | **Flips**: GO only at headline or with CCfD |
| 35 | 96 | +9.8 | −28.7 | −10.7 | −1.9 | **Flips**: GO only at headline |
| 45 | 117 | +1.9 | −36.6 | −18.5 | −9.7 | **Flips**: GO only at headline |
| 60 | 148 | −9.9 | −48.4 | −30.3 | −21.5 | All NO-GO |

Levelized at 8%, the four assumptions are worth **$20/t** (merchant), **$68/t** (announced floor from 2030, using EY's annual floor table), **$91/t** (CCfD $85 to 2040) and **$122/t** (headline).

**Findings.**
- For large-emitter abatement with a breakeven anywhere between **~$20 and ~$122/t**, the carbon-value assumption decides the investment. That band covers much of the real pipeline: efficiency, fuel switching, electrification and cheaper CCS.
- A CCfD (vs merchant credits with the announced floor) is decisive for projects with a breakeven between **~$68 and ~$91/t**.
- Alberta's floor (from 2030) and CCfDs are the instruments that turn the headline into bankable value, as the Canadian Climate Institute and Clean Prosperity argue (file 03).
- *Caveat:* credits banked before the floor regulation may still trade below the floor (EY, Blakes). The deterministic floor case is therefore optimistic in the early 2030s.

## Monte Carlo — explicit policy-regime risk

20,000 draws, seed 20260929. Policy regimes are drawn with stated probabilities; for example, AB: floor as announced 0.55 / floor at half strength 0.30 / rollback 0.15. A log-normal shock (σ 0.35) applies to the **market** credit price. Any floor is applied *after* the shock, because a legal floor is not itself uncertain within a regime. Two variants are reported so that policy risk is not confused with other risk.

**Full uncertainty** (policy regimes + gas σ 0.30 + electricity σ 0.15 + capex triangular −10%/0/+30% (mean +6.7%) + CT-ITC eligibility for a process heat pump at p = 0.6, since NRCan treats these case by case):

| Case | Deterministic @ headline | Deterministic @ market | MC mean | P10 | P50 | P90 | P(NPV>0) |
|---|---|---|---|---|---|---|---|
| Ex1 heat pump, QC | +0.70 | +0.70 | +0.12 | −1.54 | +0.01 | +1.91 | 50% |
| Ex1 heat pump, BC covered | +1.37 | +0.66 | −0.13 | −2.01 | −0.26 | +1.91 | 43% |
| Ex1 heat pump, AB covered | −1.07 | −2.11 | −2.94 | −4.12 | −2.93 | −1.78 | 0% |
| Ex1 heat pump, ON covered | −1.99 | −2.44 | −3.32 | −4.95 | −3.37 | −1.63 | 1% |
| Ex3 AB, $25M capex, merchant credits | — | — | −10.65 | −23.16 | −6.80 | −2.43 | 0% |
| Ex3 AB, $25M capex, $85 CCfD to 2040 | — | — | +2.46 | −1.83 | +2.65 | +6.29 | **76%** |

**Policy-regime risk only** (same regimes and credit-price shock; energy prices and capex fixed; ITC granted):

| Case | Deterministic @ market | MC mean | P10 | P50 | P90 | P(NPV>0) |
|---|---|---|---|---|---|---|
| Ex1 heat pump, QC | +0.70 | +0.60 | +0.02 | +0.54 | +1.24 | 91% |
| Ex1 heat pump, BC covered | +0.66 | +0.34 | −0.47 | +0.29 | +1.14 | 70% |
| Ex1 heat pump, AB covered | −2.11 | −2.44 | −3.09 | −2.15 | −2.08 | 0% |
| Ex1 heat pump, ON covered | −2.44 | −2.83 | −3.80 | −2.90 | −1.85 | 0% |
| Ex3 AB, $25M, merchant credits | — | −9.32 | −22.27 | −3.61 | −2.20 | 0% |
| Ex3 AB, $25M, $85 CCfD to 2040 | — | +3.79 | −0.45 | +6.00 | +6.00 | **86%** |

**Findings**
- **Uncertainty modelling matters only near the margin.** Far from breakeven (AB and ON heat pumps) it adds nothing; the deterministic answer is already clear.
- **Near the margin, policy-regime risk alone is material.** It cuts the probability of a positive NPV to 91% for the QC heat pump and 70% for BC, although both are deterministic "GO"s.
- **Adding ITC-eligibility risk, capex skew and energy-price risk turns both into roughly coin-flips** (50% and 43%). ITC-eligibility risk is itself a policy-interpretation risk. Energy-price and capex risk are not policy, and they account for much of the remaining drop. A policy-aware tool must still carry them to give an honest answer.
- **A CCfD moves the probability of a positive NPV from 0% to 76%** (full uncertainty) or **0% to 86%** (policy risk only) for the $25M Alberta project. This is a direct, quantitative expression of the "carbon-pricing certainty gap". It is also the calculation a large emitter needs when deciding whether to bid for a CCfD and at what strike.
- *Robustness note:* an earlier draft applied the price shock to the floor path itself and reported 16% → 72%. Shocking only the market price is the more defensible treatment and strengthens the conclusion.

## Overall answer to the test

| Hypothesis | Result |
|---|---|
| Policy/incentives materially affect decisions | **Yes, but conditionally.** They matter for covered industrial facilities and for projects near breakeven (≈$20–122/t). They are noise for most building and sub-threshold projects outside Quebec. |
| Jurisdiction matters | **Yes, strongly**, but mostly via energy prices. RETScreen and Excel already handle those as inputs. The policy-specific jurisdiction effects are coverage rules, credit-market price and QC cap-and-trade. |
| Headline vs realized carbon value matters | **Yes.** It is the single largest swing factor for covered facilities. How often practitioners actually use the headline is untested (the evidence is guidance that prescribes headline schedules); this is tested at G0. |
| Uncertainty matters | **Near the margin only.** There, explicit policy-regime risk (and CCfD value) changes the answer. |
| Incentive breadth matters | **No.** A few levers (CT/CCUS ITC + CCA expensing, industrial carbon value, QC C&T, CCfD) carry the decision. Utility rebates are noise at industrial scale. |

**Implication for the product.** Value is concentrated in a narrow, hard-to-get-right layer: **the realized value of Canadian carbon pricing and clean-economy tax measures to a specific facility and project, with explicit policy risk**. It is not in breadth of incentives, in generic NPV/IRR, or in buildings. See [`DECISION.md`](../../DECISION.md).
