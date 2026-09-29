# 02 — Canadian Policy, Incentive & Energy-Data Landscape: Due Diligence for a Corporate Decarbonization Capex Tool

**As of:** 2026-09-29 | **Scope:** federal + ON, QC, AB, BC, NS (others noted) | **Audience:** product due diligence

**Tagging convention:** **[verified]** = stated in a source fetched during this research (see Sources; secondary sources such as law-firm bulletins are named). **[inferred]** = analyst judgement, standard engineering values, or a figure from general knowledge that was not re-confirmed in a fetched source during this session. Treat [inferred] figures as placeholders to verify before they go into a product.

**Research limitation:** The session's web-search budget ran out before gas tariffs (FortisBC, Énergir, Eastward Energy), municipal building-performance by-laws and industrial heat-pump or electrode-boiler capex could be confirmed. Those rows are marked [inferred]. The NIR 2026 Annex (electricity intensity tables) could not be parsed directly. Grid factors come from provincial and utility publications that feed or parallel the NIR.

---

## 0. Executive summary (decision-relevant)

1. **Industrial carbon pricing was reset in May 2026.** The Canada–Alberta Implementation Agreement (15 May 2026) and the federal announcement that followed replaced the $170/t-by-2030 benchmark for *all* industrial systems. The new path is **$95 (2026) → $100 (2027–29) → $115 (2030) → +$3/yr → $130 (2035) → 1.5%/yr → $140 (2040)** [verified: ICAP, Osler, EY, GLJ]. An updated federal benchmark is promised "later in 2026" [verified: ICAP]. The GGPPA Schedule 4 text still showed $110 for 2026 as of 28 Apr 2026 [verified: Justice Laws]. **The legal instruments therefore lag the policy. That lag is itself a maintenance problem.**
2. **The effective marginal carbon price is the credit market price, not the headline.** Credits are in heavy surplus: TIER about **$18–20/t** against a $95 headline, federal OBPS about **$37.50**, Ontario EPS about **$72–80** *(corrected in synthesis — see Errata)*, BC OBPS about **$65** [verified: carboncredits.com, IETA, Blakes]. Alberta will impose a **credit price floor from 2030 ($60 → $110 by 2040)** [verified]. It targets an "effective" price of $130 by 2040, backed by up to **$1.2B of joint Canada–Alberta CCfDs covering up to 75 Mt** [verified: Blakes, Osler]. A model that applies $95–170/t to avoided tonnes overstates the value by 3–5× today.
3. **Small emitters face no carbon price outside Quebec.** The consumer fuel charge was set to $0 on 1 Apr 2025, BC abolished its carbon tax, and Saskatchewan set its industrial price to $0 [verified]. A commercial building or mid-size plant below the output-based pricing thresholds (about 50 kt, opt-in about 10 kt) in ON, AB, BC or NS now has **zero carbon cost on gas**. In Quebec, cap-and-trade covers fuel distributors, so every user carries about **$45/t** (Aug 2026 auction: C$45.11) [verified: CARB/MELCCFP]. For most mid-market prospects the carbon lever is **zero** or a credit market price.
4. **The 30% Clean Technology ITC is the single biggest, most certain lever.** It is enacted, refundable, 30% through 2033, 15% in 2034, gone after 2034, and falls to 20% if labour requirements are not met [verified: IEA, CRA]. It is limited to *taxable Canadian corporations*, and eligible property is narrower than "decarbonization equipment." Air-source and ground-source heat pumps qualify. **Electric resistance and electrode boilers do not appear on the CT property list** [inferred from the NRCan technical-guide list]. Process heat pumps that recover waste heat are "case-by-case" [verified: NRCan]. A domestic-content requirement is under consultation and could cut the rate for imported equipment [verified: Finance Canada, Feb 2026].
5. **Other large levers:** 100% immediate expensing for Class 43.1/53 property available for use before 2030 (enacted in Bill C-15, 26 Mar 2026) [verified: EY]. Quebec ÉcoPerformance large-project stream: up to 75% of costs, $100/t over 10 years, $40M per request [verified]. Clean Fuel Regulations credits have risen to about **$358/t (June 2026)**. That is decisive for fleet and charging electrification but not for stationary heat [verified: MLT Aikins].
6. **Utility efficiency incentives are small and often exclude fuel switching.** Examples: Enbridge custom industrial capped at $250k per project [verified]; Hydro-Québec Solutions efficaces capped at $50k per project [verified]; IESO Retrofit pays for electricity *savings*, so electrification that raises load earns nothing [verified]. They are noise for large capex and useful only for smaller efficiency projects.
7. **Volatility is extreme.** At least 15 material federal or provincial changes hit the capex calculus in the last 24 months, roughly one every 6–7 weeks. Several more are pending before year-end 2026: the federal benchmark, TIER price-floor regulations, CFR amendments, the domestic-content decision, replacement vehicle GHG regulations and Clean Electricity Regulations changes.
8. **Machine-readability is poor.** There is no authoritative Canadian incentive API. Structured data exists for inventories (NIR CSV, OGL-Canada), BC LCFS credit prices (Excel) and California–Quebec auction results (PDF/CSV). Carbon price schedules, ITC rules and almost all program parameters are HTML or PDF prose that needs expert interpretation. **A curated rules database is feasible but is an ongoing editorial product (roughly 1–2 FTE plus expert review), not a data pipeline.**

---

## 1. Federal Clean Economy ITCs and accelerated CCA

### 1.1 Status table

| Credit | Rate (2026) | Phase-down | Key eligibility | Labour req. | Legislative status (Sep 2026) | 2025–26 changes | Tag |
|---|---|---|---|---|---|---|---|
| **Clean Technology (CT) ITC** | 30% refundable | 15% in 2034; nil after 2034 | Taxable Canadian corps (and certain REITs). Solar, wind, small hydro, storage, **air- and ground-source heat pumps**, active solar heating, non-road ZEVs, geothermal, waste-biomass heat/power, small nuclear. Excludes backup equipment, building structure and distribution ductwork/piping | Rate drops to 20% if prevailing-wage and apprenticeship rules are not met | Enacted (C-59, June 2024). Bill C-15 (RA 26 Mar 2026) expanded eligibility (waste biomass, small nuclear) | Domestic-content consultation (13 Feb – 13 Mar 2026); outcome pending | [verified] IEA, CRA, NRCan, Torys, Finance |
| **Clean Technology Manufacturing (CTM) ITC** | 30% | Phases down in the 2030s [inferred: 20% 2032, 10% 2033, 5% 2034, 0 after] | M&E for clean-tech manufacturing, critical-mineral extraction and processing | None | Enacted | Budget 2025 added antimony, indium, gallium, germanium and scandium (property acquired on or after 4 Nov 2025); polymetallic mining included | [verified] Gowling, McCarthy, Torys |
| **CCUS ITC** | 60% DAC / 50% other capture / 37.5% transport, storage and use | Full rates **extended to end-2035**; half rates 2036–2040 | Dedicated geological storage or concrete; **EOR excluded** | Yes | Extension enacted in C-15 | +5-year extension (Budget 2025) | [verified] Gowling, Torys |
| **Clean Hydrogen ITC** | 15–40% by carbon-intensity tier | Phase-down after 2033 [inferred] | Electrolysis; reforming with CCUS; methane pyrolysis added (property from 16 Dec 2024) | Yes | Enacted; pyrolysis expansion in C-15 | Pyrolysis confirmed | [verified] Gowling, Torys |
| **Clean Electricity ITC** | 15% | to 2034 [inferred] | Low-emitting generation, storage, inter-provincial transmission. Also open to Crowns, municipal and Indigenous-owned corps and pension investment corps; CIB and CGF added | Yes | **Enacted in Bill C-15, RA 26 Mar 2026** | Provincial Crown conditions (net-zero-2035 grid, ratepayer pass-through) removed; CIB/CGF financing not treated as "government assistance" | [verified] Finance Canada, Torys, Gowling |
| **EV Supply Chain ITC** | 10% (buildings) | 5% 2033–34; nil 2035 | $100M+ M&E thresholds | — | Draft; not in Budget 2025 | Stalled | [verified] Gowling |

**CT ITC notes for the model**
- **Heat pumps.** The NRCan guide covers mini-split, ducted, rooftop and VRF air-source systems. Systems that also exchange heat with *process exhaust or other sources* are decided case by case with the Class 43.1/43.2 Secretariat [verified: NRCan]. For industrial heat pumps upgrading waste heat, eligibility is uncertain. **The tool should show the ITC as "likely / uncertain / ineligible", not as a single rate.**
- **Electrode or electric boilers.** They are not among the CT property categories NRCan lists [verified list; conclusion inferred]. This matters because electrode boilers are a common electrification option for steam.
- **Credit base.** The credit is reduced by other government assistance, including provincial grants and possibly utility incentives [inferred from general ITC rules; the CE ITC carve-out for CIB/CGF confirms the principle, verified]. Stacking logic is therefore required.
- **Recapture.** Recapture applies if the property is converted to non-clean use within about 20 years [inferred].
- **Tax-exempt entities** (municipalities, universities, schools, hospitals, the "MUSH" sector) cannot claim the CT ITC. Only the CE ITC reaches some public entities [verified by eligibility lists].

### 1.2 Accelerated CCA (Classes 43.1/43.2/53)
- Bill C-15 reinstated **100% immediate expensing** for Class 43.1 clean-energy and energy-conservation equipment, Class 53 manufacturing and processing M&E, and ZEV Classes 54–56. It applies to property acquired after 31 Dec 2024 and available for use before 2030, phasing out 2030–2033 [verified: EY]. The Budget 2025 measure also covers **manufacturing and processing buildings** acquired from 4 Nov 2025 [verified: Gowling].
- Class 43.2 (the higher-efficiency sub-class, normally 50% declining balance) sits alongside [inferred].
- **Model effect.** For a taxable corporation with capacity to use the deduction, immediate expensing adds roughly **4–8% of capex in NPV terms** versus normal CCA. The exact figure depends on the discount rate and a tax rate of about 26.5% [inferred calculation].

---

## 2. Industrial carbon pricing

### 2.1 National price trajectory (post-May 2026)

| Year | Headline $/t CO2e (new) | Prior legislated federal schedule | Tag |
|---|---|---|---|
| 2025 | 95 | 95 | [verified] |
| 2026 | **95** (held) | 110 (GGPPA Sch. 4, current to 28 Apr 2026) | [verified: ICAP, Justice Laws] (conflict flagged) |
| 2027 | 100 | 125 | [verified] |
| 2028 | 100 | 140 | [verified] |
| 2029 | 100 | 155 | [verified] |
| 2030 | 115 | 170 | [verified] |
| 2031–2035 | +$3/yr → 130 | — | [verified] |
| 2036–2040 | +1.5%/yr → 140 | — | [verified] |

- The federal government stated that "the price schedule for all industrial carbon pricing systems in Canada will be updated to follow the same pricing trajectory as Alberta" [verified: Osler]. The updated benchmark is due later in 2026 [verified: ICAP].
- **The $170/t 2030 benchmark no longer stands** [verified].
- **Alberta TIER specifics:**
  - Credit price floor via "minimum transfer price" from 2030: $60 (2030), $80 (2035), $110 (2040). Regulation required by 31 Dec 2026. Pre-2030 credits remain transferable below the floor [verified: EY, GLJ].
  - The "effective price" target is $130 by 2040 [verified].
  - Direct-investment credits are capped at 50% of capex and opex, net of other public support [verified: Blakes].
  - Stringency (tightening) rates have been lowered for 2027–2040 [verified: Blakes, Osler; values not public in the sources].
  - Canada and Alberta will each provide up to $600M for CCfDs covering up to 75 Mt [verified].

### 2.2 System-by-system

| Jurisdiction | System | Threshold | 2026 headline | Observed credit/market price | Status notes | Data format | Tag |
|---|---|---|---|---|---|---|---|
| **Federal OBPS** (MB, PEI, YT, NU; parts of SK historically) | Output-based | 50 kt mandatory; 10 kt opt-in [inferred] | $95 (policy) / $110 (statute text) | ~$37.50 surplus-credit trades | Benchmark update due 2026 | Regs HTML; no price feed | [verified] carboncredits, ICAP; thresholds [inferred] |
| **Alberta TIER** | Output-based + fund | 100 kt; opt-in for smaller [inferred] | $95 | **~$18–20** market; $95 fund | New path to 2040; floor from 2030; CCfDs | Regs PDF/HTML; no official price series | [verified] Blakes, carboncredits, EY |
| **BC OBPS** (from 2024) | Output-based | 10 kt [inferred] | follows national [inferred] | ~$65 | Consumer carbon tax abolished 1 Apr 2025; OBPS proceeds fund the Clean Industry Fund | HTML | [verified] carboncredits (price), BC CIF page |
| **Ontario EPS** | Output-based | 50 kt mandatory; 10 kt opt-in | Statute schedule $110 (Enbridge); alignment with new path expected [inferred] | ~$72–80 (15–20% below the $95 2025 compliance price; ClearBlue ~$72) *(corrected — see Errata)* | ~200 facilities; opt-out amendments proposed in 2025 | O. Reg. 241/19 (HTML) | [verified] IETA, Enbridge |
| **Quebec** | Cap-and-trade (WCI, linked to California) | 25 kt emitters; **fuel distributors covered, so all users pay** | Market | **C$45.11** (Aug 2026 auction); reserve C$38.81 | Stable, but California market reform risk | **Auction results PDF/CSV (CARB)** | [verified] CARB |
| **Saskatchewan** | Provincial OBPS — **price set to $0 since 1 Apr 2025** | — | $0 | n/a | No agreement with Ottawa as of May 2026; federal backstop not reimposed | News only | [verified] CBC, The Logic |
| **Nova Scotia** | Provincial output-based system (since 2023) [inferred] | [inferred] | [inferred: follows national] | n/a | Not verified this session | — | [inferred] |
| **New Brunswick** | Provincial OBPS | [inferred] | [inferred] | n/a | Not verified this session | — | [inferred] |
| **Newfoundland & Labrador** | Performance standards (MGGA) | 25 kt [inferred] | [inferred] | n/a | Not verified this session | — | [inferred] |
| **NWT** | Direct tax on large emitters | — | — | — | Per ECCC page | HTML | [verified] ECCC |

### 2.3 Output-based allocation: why marginal and average cost diverge (modelling note)
- A covered facility receives free allocation, equal to benchmark intensity × output × (1 − stringency). It pays only on emissions **above** that limit, so its **average** carbon cost per tonne emitted is small. Often it is only 5–20% of the headline price [inferred].
- **At the margin, each tonne avoided either saves a compliance-unit purchase or creates a surplus credit.** The marginal value of abatement is therefore the **price at which the facility can buy or sell credits**, capped at the fund or excess-emissions charge. Today that is the depressed market price ($18–65), not $95. Usage limits on credits and offsets (e.g., the TIER cap on credit use) can push some facilities' marginal price toward the fund price [inferred].
- **Product implication.** Carbon value = avoided t × **expected credit price path**, not avoided t × headline. The tool needs a scenario range: low = market price; mid = floor or CCfD strike; high = headline. The Alberta floor ($60 from 2030) and CGF CCfDs are the only instruments that turn the headline into bankable value.
- Electrification that moves emissions from a covered facility to the grid avoids facility tonnes. Grid emissions in ON, AB and NS are then priced through the electricity-sector OBPS/TIER benchmarks, which are embedded in power prices [inferred].

---

## 3. Clean Fuel Regulations and provincial LCFS

| Item | Value | Date | Tag |
|---|---|---|---|
| CFR avg credit price, Q2 2025 | $142.19/t | Apr–Jun 2025 | [verified] BC Bioenergy / ECCC report |
| CFR avg credit price, Q3 2025 | $216.65/t | 2025 Q3 | [verified] MLT Aikins |
| CFR credit price | **$358.18/t** | June 2026 | [verified] MLT Aikins |
| CFR price cap mechanics | Credit clearance mechanism about $300/t (2022$, CPI-indexed); fund contribution about $350/t (2022$, indexed) | — | [inferred] |
| CFR data | Annual credit market report (HTML) plus quarterly reports; weighted average, min/max, volumes | 2024 onward | [verified] ECCC |
| CFR amendments | Consultation 3 Dec 2025 – 15 Jan 2026 on domestic-content and credit-multiplier options; draft in CG-I pending | 2026 | [verified] ECCC |
| Pathways CCS | Alberta agreement preserves a "minimum 20% credit creation" for CCS under CFR | May 2026 | [verified] Torys |
| BC LCFS | ~C$497–502/t (late-2023 record); aviation fuel added 2026; **Excel dataset updated Sept 2026** | — | [verified] Argus, BC gov |

**Relevance.** Electricity used in EV charging (including fleet and forklift charging) generates CFR credits, as do biogas and RNG injection and some CCS on fuel production. At about $350/t, EV charging credits are worth roughly **$0.05–0.10 per kWh** delivered to vehicles [inferred: kWh displacing ~0.6–0.8 kg of fossil-fuel lifecycle CI per kWh after EER]. That is material for fleet business cases. Stationary heat electrification does **not** create CFR credits [inferred]. BC LCFS is similar and larger for transport. **Volatility:** CFR prices moved about 2.5× in 12 months [verified], so this lever needs a live price input, not a constant.

---

## 4. Other capital support programs

| Program | Jurisdiction | Lever size | Status (Sep 2026) | Eligible / key terms | Data format | Volatility | Tag |
|---|---|---|---|---|---|---|---|
| **Canada Growth Fund CCfDs and offtakes** | Federal | $7B of the $15B CGF earmarked (2023); bilateral, bespoke | Active. Budget 2025 says CGF "will continue" CCfDs. Joint Canada–Alberta CCfD pool up to $1.2B / 75 Mt | Large emitters, CCUS, low-carbon projects | Press releases only | Deal-by-deal | [verified] The Logic, Torys (Budget), Blakes |
| **Canada Infrastructure Bank** | Federal | Low-cost debt; e.g., $100M retrofit loan facilities via Scotiabank and BMO | Active; Building Retrofits Initiative delivered through bank partners | Commercial buildings (≥ ~$1M projects [inferred]) | HTML / press | Moderate | [verified] CIB release; thresholds [inferred] |
| **SIF Net Zero Accelerator** | Federal | Was up to $8B | **Sunset 4 Nov 2025**; successor is the Strategic Response Fund | Large projects | HTML | Just changed | [verified] ISED |
| **Low Carbon Economy Fund** | Federal | $2B total; Challenge and Implementation Readiness streams listed as open | Page last modified Oct 2024, so status is stale or uncertain | Orgs incl. private sector (Challenge) | HTML | Intermittent intakes | [verified] ECCC (page date) |
| **Clean Industry Fund** (formerly CleanBC Industry Fund) | BC | Funded from OBPS proceeds; three streams | Active (updated 1 Apr 2026). **Only BC OBPS-regulated operations** eligible | RFP-based | HTML/PDF RFPs | Annual intakes | [verified] BC gov |
| **ERA Industrial Transformation Challenge 2026** | AB | $50M call; ≤$10M/project; ≤50% cost share; min request $0.5M | Closed 17 Jun 2026; recurring annual calls | Demo / first-of-kind | HTML | Annual | [verified] ERA |
| **ÉcoPerformance – large industrial projects** | QC | Lesser of: payback cut to 1 yr, 75% of costs, **$100/t × 10 yrs of annual avoided tCO2e**; ≤$40M per request, $80M per site; min $15M investment | Active | SPEDE (cap-and-trade) emitters | HTML | Moderate | [verified] Quebec.ca |
| **Hydro-Québec Solutions efficaces** | QC | 10–15% of cost (simplified) or $0.01/kWh saved (custom); **cap $50k/project** | Active (Mar 2026 sheet) | Efficiency and demand measures | PDF | Annual tweaks | [verified] HQ |
| **IESO Save on Energy – Retrofit** | ON | Custom: greater of $1,800/kW peak or $0.20/kWh saved; ≤50–55% of cost | Active (v1.2, Jun 2025; 2025–2036 eDSM framework) | **Electricity savings only; fuel switching not an eligible measure** | PDF | New framework 2025 | [verified] IESO/SaveOnEnergy |
| **IESO SEM / Industrial Energy Efficiency** | ON | Performance incentives, larger projects | Active | Large industrials | PDF | — | [inferred] |
| **Enbridge Gas Industrial Custom** | ON | $0.30/m³ (first 50k m³) then $0.20/m³ saved; ≤75% incremental cost; **max $250k/project** | Active | Gas savings; fuel switching not addressed | HTML | Annual (OEB-approved DSM plans) | [verified] Enbridge |
| **BC Hydro / FortisBC C&I incentives** | BC | Typically ≤$100k–$1M per project; FortisBC offers some electrification/hybrid incentives [inferred] | Active | — | HTML | Annual | [inferred] |
| **Green Municipal Fund (FCM)** | Federal / municipal | Loans and grants for municipal buildings | Active [inferred] | Municipalities and partners | HTML | — | [inferred] |
| **Canada Greener Homes** | Federal | Residential only; out of scope | — | — | — | — | [inferred] |

### 4.1 Municipal building performance standards
- **Vancouver:** annual GHG and heat energy limits for large office and retail buildings, with limits starting mid-decade and tightening to zero by 2040, plus a per-tonne penalty for exceedance [inferred; not re-verified this session].
- **Montréal:** By-law 21-042 requires GHG reporting and ratings for large buildings. The city is targeting zero-emission operation of large buildings by 2040 and has restricted fossil heating in new construction [inferred].
- **Toronto:** mandatory energy and water reporting (EWRB, Ontario Reg. 506/18 and municipal reporting); performance standards for existing buildings under TransformTO are being developed [inferred].
- **Relevance:** these create **compliance-driven** capex (avoided penalty or forced replacement at end of life) for commercial real estate. That is a strong, non-price lever for the building segment, but the rules are city-specific by-law PDFs. **Needs verification before product use.**

---

## 5. Electricity prices, gas prices and grid intensity

### 5.1 Electricity prices (Hydro-Québec comparison, rates as of 1 Apr 2025, ¢/kWh, taxes excluded) [verified]

| City | Small power 100 kW / 25 MWh | Medium 1 MW / 400 MWh | Large 5 MW / 3.06 GWh | Large 50 MW / 30.6 GWh |
|---|---|---|---|---|
| Montréal, QC | 13.09 | 9.71 | 5.83 | 5.52 |
| Toronto, ON | 20.38 | 17.27 | 12.80 | 12.66 |
| Ottawa, ON | 18.56 | 15.71 | 12.75 | 12.31 |
| Calgary, AB | 12.67 | 11.07 | 8.02 | 7.99 |
| Edmonton, AB | 22.15 | 12.30 | 10.17 | 8.05 |
| Vancouver, BC | 12.65 | 9.73 | 8.42 | 6.72 |
| Halifax, NS | 19.19 | 16.61 | 13.43 | 13.43 |
| Regina, SK | 15.47 | 12.94 | 9.57 | 8.05 |
| Winnipeg, MB | 10.77 | 7.92 | 6.00 | 5.09 |
| Moncton, NB | 17.95 | 15.89 | 11.13 | 10.63 |
| St. John's, NL | 14.52 | 12.14 | 11.15 | 7.66 |

Caveats:
- HQ raised business rates **3.8% on 1 Apr 2026** [verified]. The 2026 comparison edition had not been published on the HQ page when checked [verified].
- Ontario figures include the Global Adjustment for Class B. Class A (ICI) customers can pay materially less [inferred].
- Alberta wholesale prices collapsed: the pool averaged **$31.26/MWh in July 2026**, with 2027 flat forwards at $45/MWh [verified: TC Energy]. Alberta all-in industrial prices in 2026 are therefore likely below the April 2025 HQ figures [inferred].

### 5.2 Grid emission factors (latest available)

| Province | Value (g CO2e/kWh) | Basis / year | Source | Tag |
|---|---|---|---|---|
| Quebec | **2.5** | HQ supply mix incl. purchases, 2024 (0.6 in 2023) | HQ GHG emission rate 1990–2024 | [verified] |
| BC | **22.8** | BC integrated-grid factor, 2025 (4-yr rolling, incl. imports) | BC gov | [verified] |
| Ontario | **73.8** | Grid average 2024; +25% vs 2023 on gas generation | TAF (IESO data) | [verified] (secondary) |
| Alberta | **335** | Generation intensity 2024 (907 in 2005) | Alberta.ca | [verified] |
| Nova Scotia | **528** | NS Power CO2e intensity 2025 | NS Power emissions database | [verified] |
| Canada | ~100–140 | Generation intensity (NIR) | NIR / Climatiq mirrors | [inferred] |

**Modelling note.** For ON, the marginal emission factor (gas-fired, roughly 400–500 g/kWh) is 5–6× the average [inferred]. Electrification savings claimed in Ontario are very sensitive to average-versus-marginal choice. The tool should expose both. The NIR 2026 (submitted 14 Apr 2026, covering 1990–2024) is the authoritative source for all provinces. Its electricity annex is also released as CSV on the ECCC Data Mart under OGL-Canada [verified: open.canada.ca, dataset modified 11 Sep 2026].

### 5.3 Natural gas prices

| Market | Value | Date | Tag |
|---|---|---|---|
| AECO spot/forward | **$1.25/GJ** (Sep 2026), **$2.17/GJ** (2027), $2.53 (2028) | 4 Aug 2026 | [verified] TC Energy |
| Enbridge Gas (EGD zone) supply charge | 9.05 ¢/m³ ≈ **$2.39/GJ** commodity | 1 Jul 2026 QRAM | [verified] OEB (conversion at 0.0379 GJ/m³ [inferred]) |
| Ontario industrial delivered (commodity + transport + distribution) | ~$4–7/GJ | 2026 | [inferred] |
| Alberta industrial delivered | ~$3–5/GJ | 2026 | [inferred] |
| BC (FortisBC) C&I delivered | ~$8–12/GJ | 2026 | [inferred] |
| Quebec (Énergir) C&I delivered, incl. cap-and-trade | ~$9–14/GJ | 2026 | [inferred] |
| Nova Scotia (Eastward Energy) C&I delivered | ~$15–25/GJ | 2026 | [inferred] |

**Sources for automation:**
- Ontario: OEB QRAM PDFs, quarterly [verified].
- Alberta: AUC/utility gas cost flow-through, monthly.
- Quebec: Régie de l'énergie tariffs.
- BC: BCUC filings.
- Market reference: Statistics Canada tables and the CER market snapshot.
- All are PDF or HTML except StatCan (CSV/API) [inferred].

---

## 6. Parameter values for modelling

| Parameter | Value | Unit | Source / date | Tag |
|---|---|---|---|---|
| Industrial carbon headline price 2026 | 95 | $/t | ICAP (May 2026) | [verified] |
| Headline 2027–2029 | 100 | $/t | ICAP / Osler | [verified] |
| Headline 2030 / 2035 / 2040 | 115 / 130 / 140 | $/t | ICAP / GLJ | [verified] |
| Prior (superseded) 2030 benchmark | 170 | $/t | GGPPA Sch. 4 | [verified] |
| TIER credit market price | ~18–20 | $/t | carboncredits; Blakes ("as low as C$20") | [verified] |
| Federal OBPS surplus credit price | ~37.50 | $/t | carboncredits (2026) | [verified] |
| Ontario EPU price | ~72–80 *(corrected)* | $/t | IETA (2025): 15–20% below compliance price of $95; ClearBlue via carboncredits.com ~$72 | [verified] |
| BC OBPS credit price | ~65 | $/t | carboncredits | [verified] |
| Alberta credit floor 2030 / 2035 / 2040 | 60 / 80 / 110 | $/t | GLJ / EY | [verified] |
| Quebec C&T settlement (Aug 2026) | 45.11 | C$/t | CARB auction #48 | [verified] |
| Quebec 2026 auction reserve | 38.81 | C$/t | CARB | [verified] |
| Carbon price for non-covered emitters (ON/AB/BC/NS/SK) | 0 | $/t | Fuel charge removed 1 Apr 2025 | [verified] |
| CFR credit price | ~358 (June 2026); 142–217 (2025) | $/t | MLT Aikins / ECCC | [verified] |
| Natural gas combustion EF | ~50 (49–51) | kg CO2e/GJ HHV | NIR standard factor (~1.92 kg CO2/m³) | [inferred] |
| CT ITC rate | 30% (20% w/o labour req.); 15% in 2034; 0 after | % of eligible capex | IEA / CRA | [verified] |
| CE ITC rate | 15% | % | Torys / Finance | [verified] (rate) |
| CCUS ITC capture (non-DAC) | 50% to 2035 | % | Gowling | [verified] |
| Immediate expensing (43.1, 53) | 100% yr-1, available for use before 2030 | — | EY (C-15) | [verified] |
| Corporate tax rate (combined, general) | ~26.5 (ON), 23 (AB), 27 (BC), 26.5 (QC), 29 (NS) | % | Provincial rates | [inferred] |
| Electricity price, large (5 MW) | QC 5.83; ON 12.80; AB 8.02 (Calgary); BC 8.42; NS 13.43 | ¢/kWh | HQ comparison Apr 2025 | [verified] |
| Electricity price, medium (1 MW) | QC 9.71; ON 17.27; AB 11.07; BC 9.73; NS 16.61 | ¢/kWh | HQ comparison Apr 2025 | [verified] |
| Grid EF | QC 2.5; BC 22.8; ON 73.8; AB 335; NS 528 | g CO2e/kWh | see §5.2 | [verified] |
| Ontario marginal grid EF | ~400–500 | g/kWh | gas CCGT/peaker | [inferred] |
| Gas delivered, industrial | AB 3–5; ON 4–7; QC 9–14; BC 8–12; NS 15–25 | $/GJ | see §5.3 | [inferred] |
| AECO commodity | 1.25 (Sep 26), 2.17 (2027 fwd) | $/GJ | TC Energy | [verified] |
| Industrial heat pump capex (≤150 °C, installed) | ~$800–2,000 per kW thermal | CAD | IEA/industry literature | [inferred] |
| Electrode boiler capex (installed, incl. electrical) | ~$150–400 per kW thermal (excl. grid upgrade) | CAD | industry literature | [inferred] |
| Grid connection / service upgrade | Highly site-specific; can exceed equipment cost | — | — | [inferred] |
| Heat pump COP (process, 80–120 °C lift) | 2–4 | — | — | [inferred] |
| Gas boiler efficiency | 80–90% | — | — | [inferred] |

### 6.1 Illustrative: cost per GJ of *useful* heat, 2026 [inferred calculation using the table above]
Assumptions: gas boiler 85% efficient; electrode boiler 99%; heat pump COP 3; EF 50 kg/GJ; large-power electricity rate.

| Province | Gas fuel only | + carbon at credit price | + carbon at $95 headline | Electrode boiler | Heat pump (COP 3) |
|---|---|---|---|---|---|
| QC (gas $11, carbon $45) | ~$12.9 | ~$15.6 (C&T) | — | ~$16.3 | ~$5.4 |
| ON (gas $5.5, EPU $38 — *see Errata: ~$75 is better supported*) | ~$6.5 | ~$8.7 | ~$12.1 | ~$35.9 | ~$11.9 |
| AB (gas $4, TIER $20) | ~$4.7 | ~$5.9 | ~$10.3 | ~$22.5 | ~$7.4 |
| BC (gas $10, credit $65) | ~$11.8 | ~$15.6 | ~$17.4 | ~$23.6 | ~$7.8 |
| NS (gas $20) | ~$23.5 | n/a | ~$29.1 | ~$37.7 | ~$12.4 |

Readings:
- Electrode boilers lose outside Quebec at any plausible carbon price.
- Heat pumps win on opex in QC, BC and NS. In ON and AB they win only if a real carbon price applies at the margin *and* capex is subsidised.
- Capex (heat pump roughly 3–10× a gas boiler per kW) usually dominates. The 30% CT ITC plus immediate expensing is therefore the swing factor.

---

## 7. Which levers can flip a decision?

Illustrative project: $5M heat-pump retrofit displacing 100,000 GJ/yr of gas, avoiding ~5,000 t/yr. Taxable corporation, 8% discount rate, 15-year life [inferred calculation].

| Lever | Order of magnitude | PV equivalent | Flip potential | Notes |
|---|---|---|---|---|
| CT ITC 30% | 30% of eligible capex | ~$1.2–1.5M (eligible share 80–100%) | **High** | Enacted and certain to 2033; eligibility of the specific kit is the risk |
| Immediate expensing | Timing benefit | ~$0.2–0.4M | Medium | Before-2030 window creates urgency |
| Carbon, covered facility at headline $95–130 | ~$5.5–6.5/GJ | ~$4–5M | **High (theoretical)** | Only if the facility is short and must pay the fund price |
| Carbon, covered facility at credit price $20–40 | ~$1–2/GJ | ~$0.9–1.7M | Medium | Today's reality in AB, ON and federal OBPS |
| Carbon, non-covered emitter (ON/AB/BC/NS) | $0 | $0 | None | Majority of mid-market sites |
| Quebec C&T (all users) | ~$2.3/GJ (≈$225k/yr) | ~$1.9M | Medium–High | Stable, market-based; embedded in gas bills |
| ÉcoPerformance (QC SPEDE) | Up to 75% of cost | Up to ~$3.75M (lesser-of test: $100/t × 5,000 t × 10 = $5M) | **Very high** | Discretionary; min $15M investment for the large-project stream |
| CGF CCfD | Converts headline to bankable strike | Could equal the carbon-at-headline row | **High for large emitters** | Bespoke, few deals; large projects only |
| CFR credits | ~$350/t | Fleet/charging only: ~$0.05–0.10/kWh | **High for fleets**; none for stationary heat | Price volatile |
| Utility incentives (Enbridge, HQ, IESO) | $50k–250k caps | <5% of capex | **Low (noise)** | Often exclude fuel switching; reduce ITC base |
| ERA / CIF / SRF grants | Up to $10M+ | Project-specific | High but competitive | Innovation or first-of-kind bias; low hit rate |
| Municipal BPS penalties | City-specific | Can force action | High for buildings in Vancouver/Montréal/Toronto | Compliance-driven, not price-driven |
| Electricity-gas price spread | Dominant opex driver | — | **Dominant** | QC/BC/NS favourable; ON/AB unfavourable |

**Conclusion.** For most corporate capex decisions the ranking is:
1. The electricity-to-gas price spread and grid factor.
2. The CT ITC and expensing (if a taxable corporation and eligible equipment).
3. Carbon price exposure, *if* the site is a covered facility, using credit rather than headline prices. It is zero otherwise.
4. Quebec-specific grants.
5. Everything else, which is mostly noise (utility rebates).

A credible tool must model eligibility and stacking correctly more than it must track dozens of small programs.

---

## 8. Data feasibility

| Category | Authoritative source | Machine-readable? | Licence | Update cadence | Material changes, last 24 mo | Tag |
|---|---|---|---|---|---|---|
| Clean economy ITCs | ITA s.127.44–127.49; CRA and NRCan guides; Finance consultations | **No**: legislation HTML (Justice Laws XML exists [inferred]), guidance HTML | OGL-Canada / Crown copyright for statutes | Budget and FES cycles (2×/yr) plus technical guides | 5+ (Budget 2025, C-15, domestic-content consultation, CE ITC enactment, CTM expansion) | [verified] events |
| Industrial carbon price schedules | GGPPA Sch. 4; provincial regs; ECCC benchmark | **No**: statute HTML/PDF; no price API | OGL / Crown | Irregular, political | 6+ (SK $0, AB freeze, MOU, Implementation Agreement, new national path, floor, pending benchmark) | [verified] |
| Credit market prices | ECCC (none for OBPS); AB (none official); ON (none); QC/CA auctions | **Partial**: CARB auction results PDF/CSV quarterly; OTC prices proprietary (ClearBlue, Carbon Pulse, Argus) | CARB public; brokers paid | Quarterly / continuous | Continuous | [verified] |
| CFR credit prices | ECCC credit market reports | HTML reports, quarterly/annual; no API | OGL | Quarterly | Continuous; 2.5× move | [verified] |
| BC LCFS prices | BC gov | **Excel** download | BC OGL | Monthly/quarterly (updated Sep 2026) | Continuous | [verified] |
| Grid EFs | NIR (ECCC Data Mart CSV), provincial factors | **Yes (CSV)** for NIR; BC HTML; utility PDFs | **OGL-Canada** (commercial use OK with attribution) | Annual (April) | Annual refresh | [verified] |
| Electricity prices | HQ comparison (annual PDF); OEB RPP/GA; AESO pool (API) | Partial: HQ PDF; AESO and IESO have public APIs/CSVs [inferred]; tariffs PDF | HQ copyright; OEB/AESO public | Annual (HQ), monthly (GA), hourly (pool) | Rate cases annually | [verified] HQ |
| Gas prices | OEB QRAM, AUC, Régie, BCUC; StatCan | PDF (regulators); StatCan CSV/API | OGL / public | Quarterly (ON) or monthly | Continuous | [verified] OEB |
| Federal/provincial grant programs | ISED, ECCC, NRCan, ERA, BC, QC portals | **No** (HTML/PDF RFPs) | Crown / OGL | Intakes open and close; programs sunset (NZA Nov 2025) | Many | [verified] NZA sunset |
| Utility DSM incentives | Enbridge, IESO, HQ, BC Hydro, FortisBC, Efficiency NS | **No** (HTML/PDF, annual versions) | Proprietary (utility copyright) | Annual; mid-year tweaks | Many | [verified] |
| Municipal BPS | City by-laws | **No** (PDF) | Municipal copyright | Irregular | Some | [inferred] |

**Is there an authoritative Canadian incentive database or API?**
- **No equivalent of DSIRE exists** [inferred from research; no such API surfaced].
- ISED's **Business Benefits Finder** is a guided web tool, not an open API. It could not be fetched (SSL/robots) [inferred].
- NRCan's legacy **Directory of Energy Efficiency and Alternative Energy Programs** (OEE) timed out and appears to be a legacy, unmaintained listing [inferred].
- Some provinces run program finders. Commercial aggregators (e.g., hellodarwin, Leyton, Mentor Works) curate grant listings but hold proprietary data [verified: they appear repeatedly as secondary sources].

**US analogs:**
- **DSIRE** is run by the NC Clean Energy Technology Center (NC State) since 1995 and is "supported by EnergySage." Its API covers all 50 states and 124 technologies. Pricing is on request [verified: dsireusa.org]. It is a university-staffed editorial operation; exact cost is unknown [inferred: historically DOE-funded, multi-FTE].
- **Rewiring America Incentives API** is **free** under ToS and maintained by its policy and research team. It is residential-focused [verified: docs.rewiringamerica.org].
- Both show that incentive data is sustained as an **editorially maintained, subsidised public good**, not a scraped feed. Neither covers C&I capex well. **Neither covers Canada.**

---

## 9. Maintenance-burden assessment

**Change-event log, Oct 2024 – Sep 2026 (material to C&I capex)** [verified unless noted]:
1. Consumer fuel charge set to $0 (1 Apr 2025).
2. BC carbon tax eliminated (1 Apr 2025).
3. Saskatchewan industrial price set to $0 (1 Apr 2025).
4. Alberta TIER frozen at $95 (May 2025; reaffirmed Sep 2025).
5. EVAS 2026 target paused (Sep 2025).
6. Budget 2025 (4 Nov 2025): CCUS extension, CTM minerals, CE ITC changes, immediate expensing, NZA sunset.
7. Canada–Alberta MOU (27 Nov 2025): O&G cap shelved, CER suspended in AB, carbon price target $130.
8. CFR targeted-amendment consultation (Dec 2025 – Jan 2026).
9. Domestic-content ITC consultation (Feb – Mar 2026).
10. Bill C-15 Royal Assent (26 Mar 2026).
11. HQ rate increase of 3.8% for business (Apr 2026).
12. National electricity strategy and CER loosening announced (14 May 2026).
13. Canada–Alberta Implementation Agreement, new national price trajectory, AB credit floor and CCfDs (15–19 May 2026).
14. ERA 2026 call; CIF renamed and revised (Apr 2026).
15. EVAS formally repealed (Aug 2026).
16. CFR credit price rose ~2.5× (continuous).

**Pending by mid-2027:**
- Federal benchmark publication and OBPS, EPS and BC regulation amendments to the new path.
- TIER floor regulation (by 31 Dec 2026).
- Saskatchewan negotiation.
- CFR draft amendments (CG-I).
- Domestic-content decision.
- Replacement vehicle GHG rules.
- CER amendments.
- Annual NIR, HQ comparison and utility DSM plans.

**Implied workload** for a curated rules DB covering federal plus 5 provinces, C&I scope [inferred]:
- **Records:** ~15 federal tax and price items; ~10 carbon-pricing systems, each with price path, thresholds, credit-use limits and benchmarks; ~30–60 grant programs; ~40–100 utility incentive offers; ~10 municipal by-laws; ~10 energy-price and EF series. **Total ~120–200 structured records**, plus eligibility rules (e.g., CT property classes and stacking).
- **Change rate:** policy items change about 1–2×/yr each; utility offers about 1×/yr plus intake windows; price series monthly or quarterly. That is **~250–500 record edits a year**, about 15–25% needing tax or policy expert judgement (ITC eligibility, allocation mechanics).
- **Staffing:** ~1.0–1.5 FTE policy/data analyst plus ~0.2–0.3 FTE senior tax/climate-policy reviewer, plus engineering for price-feed ingestion (NIR CSV, CARB, BC LCFS, AESO, OEB). Rough cost: **C$200–350k/yr** fully loaded [inferred]. This excludes paid OTC carbon-credit price data, which would add a licence fee from ClearBlue, Carbon Pulse or Argus [inferred].
- **Risk:** the key values (effective carbon price, ITC eligibility of specific equipment) are **judgement calls, not lookups**. Liability and disclaimers matter; outputs must be framed as scenario ranges with dated sources.

**Recommendations for product scope** [inferred]:
- Model the **few big levers** precisely: CT/CE/CCUS ITCs with eligibility flags, CCA, carbon (headline vs credit vs floor scenarios, covered vs non-covered), CFR for fleets, QC ÉcoPerformance.
- Treat utility rebates as a user-entered line item, or as a thin optional layer.
- Automate price and EF feeds where CSVs exist.
- Timestamp every parameter and show "last verified."

---

## 10. Sources

**Federal ITCs / CCA**
- Gowling WLG, "Clean economy investment tax credits – Budget 2025": https://gowlingwlg.com/en/insights-resources/articles/2025/clean-economy-investment-tax-credits-budget-2025
- McCarthy Tétrault, Budget 2025 clean economy ITCs: https://www.mccarthy.ca/en/insights/blogs/canadian-era-perspectives/federal-government-proposes-expansion-of-clean-economy-tax-credits-and-other-tax-incentives-in-budget-2025
- Torys Quarterly Q2 2026, clean economy ITCs: https://www.torys.com/en/our-latest-thinking/torys-quarterly/q2-2026/clean-economy-investment-tax-credits
- Finance Canada, "Legislation passes to implement Budget 2025" (Mar 2026): https://www.canada.ca/en/department-finance/news/2026/03/legislation-passes-to-implement-budget-2025-canada-strong.html
- Finance Canada, domestic content consultation (13 Feb 2026): https://www.canada.ca/en/department-finance/news/2026/02/government-launches-consultations-on-potential-domestic-content-requirement-for-clean-technology-and-clean-electricity-investment-tax-credits.html
- Gowling WLG, domestic content consultation: https://gowlingwlg.com/en/insights-resources/articles/2026/finance-consults-on-adding-domestic-content-to-clean-economy-investment-tax-credits
- EY, Bill C-15 CCA measures: https://www.ey.com/en_gl/technical/tax-alerts/canada-substantively-enacts-capital-cost-allowance-and-other-business-income-tax-measures-in-bill-c-15
- CRA, Clean Technology ITC: https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/corporations/business-tax-credits/clean-economy-itc/clean-technology-itc.html
- IEA Policies DB, CT ITC: https://www.iea.org/policies/20380-clean-technology-ct-investment-tax-credit-itc
- NRCan CT ITC technical guidance: https://natural-resources.canada.ca/taxes/income-tax/corporations/federal-tax-credits/clean-economy-itc/clean-technology-itc/technical-guidance-ct-property
- NRCan air-source heat pump guide: https://natural-resources.canada.ca/taxes/income-tax/corporations/federal-tax-credits/clean-economy-itc/clean-technology-itc/air-source-heat-pump-systems

**Carbon pricing**
- ICAP, "Canada publishes new carbon price trajectory" (May 2026): https://icapcarbonaction.com/en/news/canada-publishes-new-carbon-price-trajectory
- ICAP, Canada federal OBPS: https://icapcarbonaction.com/en/node/1147
- Osler, Canada–Alberta implementation agreement: https://www.osler.com/en/insights/updates/future-of-canadas-carbon-markets-anchored-by-canada-alberta-mou-implementation-agreement/
- Torys, "A carbon and crude compromise" (May 2026): https://www.torys.com/en/our-latest-thinking/publications/2026/05/a-carbon-and-crude-compromise
- Blakes, MOU implementation takeaways: https://www.blakes.com/insights/implementation-of-the-canada-alberta-mou-key-takeaways-for-carbon-markets-in-alberta/
- EY, Alberta revises industrial carbon prices (3 Jun 2026): https://globaltaxnews.ey.com/news/2026-1180-canada-alberta-revises-industrial-carbon-prices
- GLJ, Canada's carbon pricing reset (28 May 2026): https://www.gljpc.com/canadas-carbon-pricing-reset-a-new-trajectory-and-2040-outlook/
- Carbon Pulse (headline only): https://carbon-pulse.com/514302/
- Cassels, Canada–Alberta MOU (Nov 2025): https://cassels.com/insights/canada-alberta-mou-a-grand-bargain-on-climate-and-pipelines/
- Castanet / CP, Alberta freeze (Sep 2025): https://www.castanetkamloops.net/news/Alberta/572902/Alberta-to-maintain-industrial-carbon-price-freeze-for-2026-leaving-Ottawa-to-act
- carboncredits.com, Canada carbon pricing reset 2026: https://carboncredits.com/canadas-carbon-pricing-reset-in-2026-will-industry-step-up-or-stall-climate-progress/
- Justice Laws, GGPPA Schedule 4: https://www.laws.justice.gc.ca/eng/acts/G-11.55/page-25.html
- ECCC, Industrial carbon pricing: https://www.canada.ca/en/environment-climate-change/services/climate-change/pricing-pollution-how-it-will-work/putting-price-on-carbon-pollution/industry.html
- ECCC, OBPS: https://www.canada.ca/en/environment-climate-change/services/climate-change/pricing-pollution-how-it-will-work/output-based-pricing-system.html
- IETA, Ontario EPS brief (Sep 2025): https://www.ieta.org/uploads/wp-content/2025/09/IETA-Business-brief-Ontario-EPS-Sept_2025.pdf
- Enbridge, federal carbon pricing / EPS: https://www.enbridgegas.com/business-industrial/commercial-industrial/large-volume-services-rates/federal-carbon-pricing
- CARB, Aug 2026 joint auction summary: https://ww2.arb.ca.gov/sites/default/files/2026-08/nc-aug_2026_summary_results_report.pdf
- CBC, Saskatchewan industrial carbon tax (Mar 2025): https://www.cbc.ca/lite/story/1.7495019
- The Logic, Saskatchewan (28 May 2026): https://thelogic.co/news/carbon-pricing-scheme-scott-moe-saskatchewan/
- Torys, Budget 2025 Climate Competitiveness Strategy: https://www.torys.com/en/our-latest-thinking/publications/2025/11/budget-2025-the-climate-competitiveness-strategy

**Clean fuels**
- 7Gen, CFR credit price 2026: https://www.7gen.com/blog/cfr-credit-price-canada-ev-fleet
- MLT Aikins, CFR credit market and CDR (Aug 2026): https://www.mltaikins.com/insights/canadas-clean-fuel-credit-market-and-carbon-dioxide-removal-the-case-for-legislative-reform/
- BC Bioenergy, ECCC Q2 2025 CFR report: https://bcbioenergy.ca/news/eccc-released-q2-2025-clean-fuel-regulations-credit-market-report/
- ECCC, CFR credit market report June 2024: https://www.canada.ca/en/environment-climate-change/services/managing-pollution/energy-production/fuel-regulations/clean-fuel-regulations/compliance/credit-market-report-june-2024.html
- ECCC, CFR targeted amendments consultation: https://www.canada.ca/en/environment-climate-change/corporate/transparency/consultations/share-view-ideas-targeted-amendments-clean-fuel-regulations.html
- BC LCFS credit market: https://www2.gov.bc.ca/gov/content/industry/electricity-alternative-energy/transportation-energies/renewable-low-carbon-fuels/credit-market
- Argus, BC LCFS credits pass C$500: https://www.argusmedia.com/pt/news-and-insights/latest-market-news/2515591-british-columbia-lcfs-credits-pass-c-500

**Other policy**
- The Logic, Carney loosens clean electricity rules (14 May 2026): https://thelogic.co/briefing/mark-carney-promises-to-loosen-clean-electricity-rules-in-a-new-national-strategy/
- Medicine Hat News, EVAS repealed (20 Aug 2026): https://medicinehatnews.com/?p=5235861

**Programs**
- ISED, Net Zero Accelerator (sunset): https://ised-isde.canada.ca/site/ised/en/programs-and-initiatives/strategic-response-fund/strategic-response-fund/net-zero-accelerator-initiative
- ECCC, Low Carbon Economy Fund: https://www.canada.ca/en/environment-climate-change/services/climate-change/low-carbon-economy-fund.html
- The Logic, CGF CCfDs (2023): https://thelogic.co/news/ottawa-to-use-nearly-half-of-15b-growth-fund-to-guarantee-carbon-prices-for-heavy-polluters/
- CIB, Scotiabank building retrofits: https://cib-bic.ca/en/medias/articles/canada-infrastructure-bank-commits-100-million-towards-building-retrofits-with-scotiabank/
- BC Clean Industry Fund: https://www2.gov.bc.ca/gov/content/environment/climate-change/industry/clean-industry-fund
- ERA Industrial Transformation Challenge 2026: https://www.eralberta.ca/funding-technology/industrial-transformation-challenge-2026/
- Quebec ÉcoPerformance, large industrial projects: https://www.quebec.ca/agriculture-environnement-et-ressources-naturelles/energie/reussir-ses-projets-transition-energetique/aide-financiere/programme-ecoperformance/implantation-grand-projet-industriel
- Hydro-Québec Solutions efficaces (Mar 2026): https://pannes.hydroquebec.com/data/affaires/pdf/feuillet-programme-solutions-efficaces-mars2026.pdf
- IESO Retrofit Program Requirements v1.2: https://www.saveonenergy.ca/-/media/Files/SaveOnEnergy/Industry/Retrofit-Documents/Retrofit-Program-Requirements.pdf
- Enbridge Industrial Custom Engineering Program: https://www.enbridgegas.com/business-industrial/incentives-conservation/programs-and-incentives/retrofits-custom-projects/industrial-custom-engineering-program

**Energy prices / emissions**
- Hydro-Québec, Comparison of Electricity Prices 2025: https://pannes.hydroquebec.com/data/documents-donnees/pdf/comparaison-prix-2025-en.pdf
- Hydro-Québec, rates page: https://www.hydroquebec.com/business/customer-space/rates/comparison-electricity-prices.html
- Hydro-Québec GHG emission rate 1990–2024: https://pannes.hydroquebec.com/data/developpement-durable/pdf/hq-ghg-emission-rate-1990-2024.pdf
- BC electricity emission intensity factors: https://www2.gov.bc.ca/gov/content/environment/climate-change/data/electricity
- Alberta GHG reduction performance: https://www.alberta.ca/albertas-greenhouse-gas-emissions-reduction-performance
- Nova Scotia Power air emissions: https://www.nspower.ca/clean-energy/air-emissions-reporting
- TAF, GTHA electricity grid emissions 2024: https://carbon.taf.ca/2024/electricity-grid
- IESO, 2025 APO: https://ieso.ca/Powering-Tomorrow/2025/Seven-Graphs-and-a-Map-2025-Annual-Planning-Outlook
- Open Canada, Canada's Official GHG Inventory (OGL): https://open.canada.ca/data/en/dataset/779c7bcf-4982-47eb-af1b-a33618a05e5b
- UNFCCC, Canada 2026 NID: https://unfccc.int/documents/656424
- OEB, Enbridge QRAM 1 Jul 2026: https://oeb.ca/sites/default/files/qram-enbridge-20260701-en.pdf
- TC Energy, Alberta power market update Aug 2026: https://www.tcenergy.com/siteassets/pdfs/power/alberta-power-marketing/power-market-updates/2026/tce-market-update-august-2026.pdf

**Data / licensing / analogs**
- Open Government Licence – Canada: https://open.canada.ca/en/open-government-licence-canada
- DSIRE: https://www.dsireusa.org/ and https://www.dsireusa.org/dsire-api/
- Rewiring America API: https://www.rewiringamerica.org/api and https://docs.rewiringamerica.org/

---

## Errata (added during synthesis, 2026-09-29)

- **Ontario EPU price.** This file originally stated ~$34–42/t. The IETA brief cited here says EPUs trade at a 15–20% discount to the *annual compliance price*, and Ontario's schedule ($50 in 2022 + $15/yr) puts the 2025 compliance price at $95, implying ~$76–81/t. ClearBlue (via carboncredits.com, Dec 2025) cites ~$72/t. The synthesis and models use **~80% of headline (~$72–80/t)**. The §6.1 illustrative Ontario row therefore understates Ontario carbon value at the margin.
