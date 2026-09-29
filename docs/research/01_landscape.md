# 01 — Landscape: Existing Solutions for a "Canada Climate CapEx Engine"

*Prepared 2026-09-29. Scope: tools, data sources and services that connect Canadian policy, incentives, energy/emissions assumptions and project financials (NPV/IRR/payback/uncertainty) to corporate decarbonization investment decisions.*

**Tagging convention.** **[verified]** = directly supported by a source fetched during this research (URL in Sources). **[inferred]** = analyst judgement, general domain knowledge, or a search-snippet-level claim not confirmed by a fetch. Vendor marketing pages were fetched but are self-reported; "verified" means "the vendor/source says so", not "independently tested".

---

## 1. Executive summary

1. **The core calculation is not novel.** Project-level NPV/IRR/payback with a carbon-price input and Monte Carlo risk analysis has existed for years in **RETScreen Expert** (a Government of Canada tool: free Viewer, about CA$869/yr Professional, 800,000+ users claimed in 2023) [verified]. Enterprise MACC/abatement-portfolio tools with NPV/IRR/payback and carbon-price scenarios exist commercially. The clearest example is **SINAI Reduce** [verified]. Others are Arcadis Net Zero Catalyst, SLB's Decarbonization Planning Solution, Sweep, Persefoni Net Zero Navigator and IBM Envizi with Planning Analytics [verified at feature-claim level].
2. **Correction to the brief:** SINAI is **not Canadian**. It is headquartered in the US (San Francisco) and Brazil and was founded in 2017. It raised a US$22M Series A in September 2022 led by Energize Ventures (US$37M total). It is still operating and was named a Verdantix "Smart Innovator" in August 2025 [verified]. No acquisition was found.
3. **Canadian incentive data exists but is fragmented and not decision-grade.** On the discovery side:
   - helloDarwin: 10,000+ Canadian grants, CA$249–1,199/month [verified]
   - GrantMatch: 10,000+ programs; acquired by BDO Canada on 26 January 2026 [verified]
   - ISED Business Benefits Finder: open data, XLSX, now refreshed only annually, last release July 2025 [verified]
   - NRCan's energy-efficiency program directory [verified]
   - Encentiv's UtilityGenius: 4,000+ North American commercial and industrial rebate programs, including Canada [verified]

   What is missing: **no public or commercial Canadian equivalent of the DSIRE API or the Rewiring America Incentives API was found** that returns eligibility rules, amounts and stacking logic in a form a cash-flow model can consume. Confidence: moderate-high.
4. **Canadian carbon pricing is now primarily industrial, output-based, and badly mispriced relative to headline.** The consumer fuel charge ended on 1 April 2025 [verified]. Credit prices diverge sharply from the headline price:
   - Alberta TIER credits: about $18–20/t against a $95 headline [verified]
   - Ontario EPS about $72/t, BC about $65/t, federal OBPS areas about $37.50/t [verified, secondary source]

   The May 2026 Canada–Alberta implementation agreement reset the national path:

   | Year | Price / measure |
   |---|---|
   | 2027–29 | $100/t |
   | 2030 | $115/t |
   | 2035 | $130/t |
   | 2040 | $140/t |
   | 2030 → 2040 | Credit price floor rising from $60 to $110/t |
   | 2030–40 | Up to 75 Mt of carbon contracts for difference (CCfDs) |

   Sources for the table: [verified: Osler, Torys, EY]. **No commercial tool was found that explicitly values a capex project under OBPS benchmark mechanics** (a compliance cost avoided plus surplus credits generated, at an uncertain *credit* price rather than the headline price). ClearBlue Vantage models compliance positions and carbon-cost scenarios for TIER, EPS and Quebec, but does not evaluate projects [verified].
5. **The genuine gap is integration, not calculation.** Five pieces would need to come together, and no single tool found combines them:
   - a Canadian incentive rules/stacking engine
   - jurisdiction- and OBPS-aware carbon value, including the gap between credit price and headline price, price floors and CCfDs
   - Canadian energy-price and grid-intensity assumptions (for example CER Energy Futures 2026, CODERS)
   - probabilistic valuation of policy risk
   - source-level provenance

   Today consultants fill this gap (Dunsky, Navius, ICF, Blackstone Energy Services, Mantle Climate, Enerlife and others). Confidence that the *integrated* product does not exist in Canada: **moderate (~65–75%)**. Proprietary platforms such as Sphera, SINAI and ClearBlue could have unadvertised Canada packs.

---

## 2. Government and public tools

### 2.1 RETScreen Expert (NRCan / CanmetENERGY)

**What it does**
- Clean-energy decision-intelligence software run by Natural Resources Canada.
- Four analysis types: Benchmark, Feasibility, Performance and Portfolio [verified].
- Facility types covered: power plants, commercial and institutional buildings, residential, industrial, agricultural and transport fleets [verified].
- Available in 36–37 languages and uses NASA climate data. Windows only (8.1/10/11, .NET 4.8) [verified].

**Financials**
- The Finance worksheet covers IRR, simple payback, NPV and savings-to-investment ratio, with inflation, discount rate and debt inputs, plus cash-flow tables and charts [verified].
- Carbon can be entered as a "shadow carbon price – tax" or as carbon credits [verified: Save on Energy training deck].
- Incentives and grants can be entered as inputs [verified: OpenEI].
- These are **manually entered scalars**. There is no evidence of a built-in database of Canadian incentives, provincial OBPS benchmarks or credit-price paths [inferred, high confidence].

**Uncertainty**
- Sensitivity analysis plus a Risk Analysis based on Monte Carlo, which produces frequency distributions of the financial indicators [verified].

**Pricing and licensing**
- Viewer mode is free. Professional mode (save, print, premium features) needs an annual subscription, listed at CA$869/yr on Capterra [verified].

**Users**
- 800,000 users in all countries as of April 2023, with 45,000 added in the previous 12 months [verified]. Wikipedia cites 750,000+ as of 2021 [verified].

**Update cadence**
- Version 9.0 was released on 29 September 2022 [verified, Wikipedia]. No evidence of a major release since; minor 9.x updates are likely [inferred].
- The NRCan overview page was last modified on 13 January 2025 [verified].

**Known limitations**
- Only 2 reviews on Capterra; one says "the economic section could be improved" regarding equipment pricing [verified].
- Desktop only and Windows only.
- Built for single projects or portfolios of engineering measures. It is not designed for corporate capital allocation across many sites, or for audit trails of assumptions [inferred].

**Relevance: the strongest "already solved" evidence.** A Canadian government tool already delivers project NPV/IRR plus a carbon value plus Monte Carlo, globally and cheaply. Any new product has to justify itself on policy data integration, portfolio and enterprise workflow, and provenance, not on financial math.

### 2.2 Other NRCan and federal tools
- **HOT2000 / CanQuest.** Energy simulation and compliance tools for houses and commercial buildings. They produce engineering outputs, not financial ones [inferred].
- **ENERGY STAR Portfolio Manager (Canada).** Benchmarking tool, used for Ontario's Energy and Water Reporting and Benchmarking (EWRB) and Toronto reporting. It has no capex valuation [inferred; the Toronto Hydro and NRCan pages exist].
- **CIPEC.** Industrial energy-management network plus ISO 50001 cost-share support. It offers resources and funding, not a valuation engine [inferred from search results].
- **NRCan "Directory of Energy Efficiency and Alternative Energy Programs in Canada."** Covers federal, provincial and territorial programs, large municipalities and major utilities. Searchable by category or keyword; no update date is shown [verified]. It is a human-readable directory, not an API.
- **ISED Business Benefits Finder.** Open Government Licence, XLSX downloads. It was updated quarterly through 2022 and annually since; the latest release is July 2025 [verified]. The dataset is general business support, not decarbonization-specific, and has no eligibility or amount logic.
- **Clean Growth Hub (NRCan/ISED).** An advisory "front door" to federal cleantech programs. An evaluation found that more than half of clients had satisfaction issues, partly from confusion about its scope [verified]. This is indirect evidence that navigating incentives is a known pain point.
- **Canada Energy Regulator, Canada's Energy Future 2026.** Released 17 March 2026 with four scenarios (Current Measures, Higher, Lower, Canada Net Zero). The CER says it is explicitly "not a forecast" [verified]. It is a candidate public source for energy-price, demand and grid assumptions [inferred].
- **OBPS Proceeds Fund / Decarbonization Incentive Program.** Returns OBPS proceeds in Manitoba, New Brunswick, Ontario and Saskatchewan [verified: canada.ca, last modified 23 July 2026]. It is itself an incentive that any tool would need to model.

---

## 3. SINAI Technologies and commercial decarbonization-planning / MACC platforms

### 3.1 SINAI (the closest functional analogue)

**Features claimed on the SINAI Reduce page [verified]:**
- CAPEX and OPEX project analysis, with NPV, IRR, payback and profitability index
- "Carbon pricing and sensitivity analysis"
- Interactive MACC ranking projects by cost per tonne of CO2 and by ROI
- Scenario modelling across different carbon-price futures, and "stress-testing of investment assumptions"
- Facility-level planning, with targets aligned to SBTi or custom targets
- Project tracking against realized impact

**Customers and scale [verified]:**
- Customers include Siemens Energy, ArcelorMittal, Harley-Davidson, Emirates and Natura&Co.
- Claims 1,534 decarbonization projects modelled and 560 Mt of emissions tracked.

**Gaps:**
- There is no evidence of Canadian incentive data or OBPS-specific mechanics [inferred].
- "Stress-testing" appears to be scenario- or sensitivity-based. No Monte Carlo is advertised [inferred].

**Status:** Operating and hiring, with offices in the US and Brazil [verified].

**Implication:** SINAI already sells "investment-grade business cases for decarbonization" to heavy industry. A Canadian product competes with it head-on unless it wins on Canadian policy depth.

### 3.2 Other planning platforms (prioritizing abatement financial modelling)
- **Arcadis Net Zero Catalyst.** Cost-benefit analysis, MACC and multi-criteria scoring. Sold alongside Arcadis advisory, with pricing on request [verified]. A consultant-plus-software hybrid.
- **SLB Decarbonization Planning Solution.** MACC "optimized for both cost-effectiveness and emissions impact", with budget and timeline balancing and scenario planning. Aimed at energy and industrial clients; the product webinar is dated February 2026 [verified]. NPV and uncertainty are not stated.
- **Sweep.** SBTi target setting, a library of initiatives, year-by-year capex/opex, "MAC curve" prioritization, AI scenario simulation, and audit-ready reporting with "complete data lineage" [verified]. It was a Leader in the IDC MarketScape 2026 and a Verdantix Green Quadrant 2026 Leader [verified].
- **Persefoni Net Zero Navigator.** Built with Bain and launched in March 2023. It recommends actions and pathways; MACC, NPV and carbon price are not documented [verified].
- **IBM Envizi with Planning Analytics.** Integrates ESG data into IBM Planning Analytics for what-if and multivariate emissions planning [verified]. This is a route through finance planning (FP&A), not project valuation.
- **Schneider Electric Zeigo Activate.** For SMEs: baseline, roadmap and a marketplace of providers, with a freemium tier since September 2024 [verified]. Light on financial modelling.
- **Watershed.** Acquired Emitwise on 3 June 2025 [verified]. Its focus is accounting and Scope 3 plus reduction programs. Its reduction-planning page returned a 404, so details are unverified.
- **Clarasight** (formerly Climate Club, rebranded January 2024). Department-level emissions forecasting and target planning for professional-services, technology and pharma companies [verified]. It covers business travel and Scope 3, not capex.
- **Carbon Trail.** A MACC for fashion and retail brands [verified]. Not relevant to industrial capex.
- **Investor-side tools (MSCI, S&P Trucost, Planetrics/McKinsey).** Portfolio-level transition risk and carbon-price scenario analytics for issuers, not project capex [inferred].
- **Salesforce Net Zero Cloud / Agentforce; Microsoft Sustainability Manager.** Primarily accounting and disclosure. No retirement of Microsoft Sustainability Manager was found in a 2026 retirement list [verified negative]. Neither is a capex valuation tool [inferred].

### 3.3 Canadian sustainability software (mostly not capex tools)
- **Novisto (Montréal).** ESG data and reporting. Acquired London-based Minimum (carbon accounting) on 31 March 2026 after a US$27M raise [verified]. Accounting and reporting, not capex.
- **Manifest Climate (Toronto).** Pivoted to AI disclosure assessment with "100% cited" findings [verified]. No abatement modelling [verified]. Relevant only as a **provenance-UX precedent**.
- **Mantle Climate / Mantle314 (Toronto).** Consultancies (climate strategy, disclosure, embodied carbon), not software [verified].
- **ClearBlue Markets (Toronto).** Vantage "Position Optimization" launched on 9 April 2025 for Ontario EPS, Quebec's WCI cap-and-trade and Alberta TIER [verified]. It offers compliance-market scenarios (production, emissions, transactions, price volatility), jurisdiction aggregation and "cost impacts of various carbon pricing scenarios". Pricing runs from US$249/month (voluntary carbon market data) to enterprise [verified]. It partners with Deloitte Canada [verified, headline]. It does **not** list abatement-project NPV [verified negative]. This makes it the most credible incumbent to *extend* into the proposed product.

### 3.4 Market context
- Consolidation continues:
  - Diginex acquired Plan A (7 January 2026, €55M)
  - osapiens acquired Nasdaq Metrio (10 September 2026)
  - Watershed acquired Emitwise
  - Novisto acquired Minimum

  All verified. There are still more than 100 vendors [verified].
- Verdantix's March 2026 Green Quadrant notes a shift "from compliance-led approaches to platforms that support risk and operational decision-making" [verified]. Incumbents are moving toward decision support, which raises competitive risk.

---

## 4. Building-sector retrofit and financial tools

- **Audette (Victoria, BC).** Retrofit planning for commercial real-estate asset managers, covering portfolio and asset transition plans and carbon due diligence [verified]. It fills data gaps using "millions of physical building simulations" [verified]. It shows project cost, savings and emissions. NPV, IRR, incentives and building performance standards are not explicit on the site [verified]. Funding: a CA$1M seed in 2021 [verified]; a CA$12.8M raise per Goodmans [unverified snippet]. Status: operating [verified].
- **VadiMAP (Montréal).** AI-assisted audits that simulate up to 1,000 scenarios of measures per building [verified]. It incorporates "incentives, energy tariffs, and regulatory requirements" [verified, SBIZ November 2024]. It has partnered with Will Solutions to monetize carbon credits [verified]. It operates in Canada and France (125 buildings assessed as of 2024) and is working with Hydro-Québec [verified]. **This is the closest Canadian product that combines incentives, tariffs and carbon credit value**, but only for buildings and at small scale.
- **Autocase Carbonsight.** Building-portfolio decarbonization roadmaps with "what-if" risk analysis, launched in June 2023 [verified]. No Canada-specific features found.
- **CRREM.** Free stranding-risk pathways. Granular US and Canada pathways were in development with ULI and LBNL as of 2023 [verified]. Emissions-intensity pathways, not incentive-aware capex.
- **CaGBC.** No public financial tool. Its 2021 Decarbonizing Canada's Large Buildings study (RDH and Dunsky) costed deep retrofits across 50 archetypes [verified].
- **Toronto Metropolitan University BEACON.** Retrofit Pathways, CityRetrofit and a Commercial Building Stock Model. These are technical and emissions tools with no stated financial analysis [verified].

**Regulatory demand drivers:**
- Vancouver's large-building GHG limits began 1 June 2024, with fines after a 2026 grace period [verified].
- Toronto's Building Emissions Performance Standards are **not yet adopted**; reporting has applied since 2024–25 [verified].
- **US analogues:** DSIRE is a paid API with 2,500+ US policies across 124 technologies [verified]. The Rewiring America API covers residential IRA incentives, with state and utility coverage rolling out [verified]. Both are US-only. After US federal credit rollbacks in 2025 their value is shifting to state and utility data [inferred].

---

## 5. Industrial and energy project tools

- **REopt (NLR, formerly NREL).** NREL was renamed the National Laboratory of the Rockies on 1 December 2025 [verified]. REopt is an open-source Julia package and API for optimizing behind-the-meter PV, wind, storage, CHP and geothermal heat pumps. It includes optional CO2 and health-emissions costs, portfolio screening (February 2024) and third-party financing [verified]. Incentive defaults are US-centric [inferred].
- **SAM (NLR).** A free desktop app with behind-the-meter, PPA and third-party-ownership financial models [verified]. It has stochastic/P50-P90 capability and US incentive structures [inferred].
- **HOMER Pro (UL Solutions).** Microgrid and hybrid optimization priced at US$125/249/379 per month [verified]. It has NPV/LCOE and sensitivity analysis, and emissions penalties are possible [inferred].
- **Industrial electrification.** CanmetENERGY's April 2026 Québec study covered 13 subsectors and estimated extra energy costs of CA$254M–656M per year [verified]. It is research, not a tool. Save on Energy (IESO) publishes an "Efficient Electrification Toolkit", but its financial features could not be verified. No Canadian industrial heat-pump business-case tool that models incentives and OBPS was found [inferred, moderate confidence].
- **Carbon credit and compliance tools.** ClearBlue (§3.3) plus consultants [verified]. There are also offset aggregators such as Will Solutions (Quebec) [verified via VadiMAP].

---

## 6. Open-source and academic work

- **Energy-system models (system-level, not firm capex):**
  - PyPSA-Canada (NRCan) and PyPSA-BC (Simon Fraser University) [verified]
  - CANOE, built on TEMOA at the University of Toronto; Ontario and Alberta first, using modelling to generate alternatives (MGA) for uncertainty [verified]
  - MESSAGEix-Canada, a sub-national integrated assessment model that includes federal and provincial OBPS (Nature, April 2026) [verified]
  - OSeMOSYS [inferred]
  - Proprietary: Navius gTech/IESD, CIMS (SFU), NATEM/ESMIA and Energy2020 [inferred; Navius reports for the Canadian Climate Institute exist]

  These are useful as **assumption sources** (price paths, grid intensity), not as competitors.
- **CODERS** (Energy Modelling Hub). Canadian generator, transmission, cost, demand and VRE capacity-factor data via an API key [verified]. A candidate public input for electricity assumptions.
- **Open-source MACC libraries.** Only niche ones were found (for example ggmacc, an R package for agriculture, and the MAgPIE land-use MACCs) [verified]. There is no maintained, general corporate-MACC library with finance built in [inferred, moderate].
- **Investment under policy uncertainty:**
  - "Carbon VIX" (Fuchs, Stroebel and Terstegge, NBER w32937, September 2024): uncertainty about carbon prices depresses decarbonization investment by an amount *similar to a fall in carbon prices*, consistent with real-options deferral [verified].
  - Canadian Climate Institute, "Closing the carbon-pricing certainty gap" (October 2022): identifies uncertainty about the price schedule and about credit values as real barriers, and recommends CCfDs, measures against credit oversupply and policy-contingent loans [verified].
  - Canadian Climate Institute, December 2025: TIER credits "below $20" with about 48 million surplus credits, making projects such as Pathways CCS "much less investable" [verified].
  - CCfDs are now policy: up to 75 Mt in 2030–40 under the May 2026 Canada–Alberta agreement [verified]. The first federal CCfD, via the Canada Growth Fund with Entropy, dates from 2023 [inferred from headline].
  - **No productized tool that operationalizes this literature at project level was found.**

---

## 7. Consulting services that fill the gap de facto

- **Dunsky Energy + Climate Advisors.** Pathway and retrofit costing, for example the CaGBC study [verified].
- **Navius Research.** gTech modelling for governments and NGOs [verified: report exists].
- **ICF Canada** [inferred].
- **Blackstone Energy Services.** Decarbonization roadmaps, funding and incentive support or administration, carbon policy advisory, and its blackPAC platform. Public-sector focus via Ontario's OECM purchasing marketplace [verified].
- **Mantle Climate.** Transition plans, disclosure and embodied carbon [verified].
- **Enerlife.** Building performance; active in Ontario policy consultations [verified: ERO comments].
- **Introba, Stantec and WSP.** Building decarbonization consulting [inferred / Stantec page].
- **Tax-credit and grant advisors.** Leyton, BDO (with GrantMatch), Ryan and Mentor Works [verified]. These are the de facto "incentive engine" for clean-tech investment tax credits (ITCs).

These consultancies typically deliver bespoke Excel models. That is **indirect evidence the integration is currently done by hand** [inferred], and it also makes them potential channel partners or competitors.

---

## 8. Comparison table

Legend: ✔ = present [verified], ◐ = partial or generic, ✖ = absent or not found, ? = unknown. "Incentives" means Canadian incentive data (not just an input field). "CP-prov" means province-specific carbon pricing, including OBPS or credit mechanics.

| Tool / provider | Type | Target user | Canadian incentives | CP-prov / OBPS | Project NPV/IRR/payback | Uncertainty / Monte Carlo | Provenance / audit | Pricing | Status (Sep 2026) |
|---|---|---|---|---|---|---|---|---|---|
| RETScreen Expert (NRCan) | Desktop project analysis | Engineers, energy managers | ◐ manual input field | ◐ manual carbon tax/credit scalar | ✔ | ✔ Monte Carlo + sensitivity | ✖ | Free Viewer; ~CA$869/yr Pro | Active; v9.0 (2022) |
| SINAI Reduce | Enterprise MACC/planning | Heavy industry, CPG, finance | ✖ (not found) | ◐ carbon-price scenarios (generic) | ✔ NPV, IRR, payback, PI | ◐ sensitivity / stress-test | ? | Enterprise quote | Active; US/BR HQ |
| Arcadis Net Zero Catalyst | MACC + advisory | Corporates | ✖ | ? | ◐ cost-benefit | ? | ? | On request | Active |
| SLB Decarb. Planning | MACC optimizer | Energy/industrial | ✖ | ? | ◐ cost-effectiveness | ? | ? | Enterprise | Active (2026) |
| Sweep | Carbon mgmt + planning | Large enterprise | ✖ | ✖ | ◐ capex/opex, MAC | ◐ scenarios | ✔ data lineage (reporting) | Enterprise | Active; GQ Leader 2026 |
| Persefoni Net Zero Navigator | Pathway planning | Enterprise, FIs | ✖ | ✖ | ✖ (not documented) | ✖ | ◐ | Enterprise | Active |
| IBM Envizi + Planning Analytics | Emissions FP&A | Finance + sustainability | ✖ | ✖ | ◐ via FP&A | ◐ what-if | ◐ | Enterprise | Active; GQ Leader |
| ClearBlue Vantage | Compliance-market intelligence | Large emitters (TIER/EPS/QC) | ✖ | ✔ TIER, EPS, QC | ✖ | ◐ price-volatility scenarios | ? | From US$249/mo to enterprise | Active (Apr 2025 launch) |
| Audette | CRE retrofit planning | Asset managers | ? | ✖ | ◐ cost/savings | ? | ? | Per building/yr | Active |
| VadiMAP | Building audit + scenarios | Utilities, engineers, CRE | ◐ incentives in model | ◐ credit monetization | ◐ payback | ◐ 1,000 scenarios (deterministic) | ? | One-time or subscription | Active; CA+FR |
| Autocase Carbonsight | Portfolio roadmap | CRE/ESG | ✖ | ✖ | ◐ | ◐ what-if | ? | SaaS | Status unclear |
| helloDarwin | Grant discovery + AI | SMEs, advisors | ✔ 10k+ programs | ✖ | ✖ | ✖ | ◐ | CA$249–1,199/mo | Active |
| GrantMatch (BDO) | Grant matching + advisory | SMEs, municipalities | ✔ 10k+ programs | ✖ | ✖ | ✖ | ? | Advisory / SaaS | Acquired by BDO Jan 2026 |
| Encentiv UtilityGenius | C&I rebate data | Contractors, program admins | ◐ utility rebates (lighting/HVAC/EV) | ✖ | ✖ | ✖ | ? | Commercial | Active |
| Business Benefits Finder (ISED) | Open dataset | Businesses | ◐ general, no rules | ✖ | ✖ | ✖ | ◐ gov source | Free (OGL) | Annual refresh (Jul 2025) |
| DSIRE / Rewiring America APIs | Incentive APIs | US developers | ✖ (US only) | ✖ | ✖ | ✖ | ✔ | Paid / free dev access | Active (US) |
| REopt / SAM (NLR) | Open optimization / finance | Analysts, developers | ✖ (US defaults) | ◐ emissions cost input | ✔ | ◐ (SAM stochastic) | ◐ open code | Free | Active; NREL → NLR |
| HOMER Pro (UL) | Microgrid optimization | Developers | ✖ | ◐ | ✔ NPV/LCOE | ◐ sensitivity | ✖ | US$125–379/mo | Active |
| CANOE / PyPSA-Canada / MESSAGEix-Canada / CODERS | Open system models & data | Researchers, policy | ✖ | ◐ system-level OBPS (MESSAGEix) | ✖ firm-level | ◐ MGA | ✔ open | Free | Active / in development |
| Consultants (Dunsky, Navius, Blackstone, Mantle, ICF…) | Services | Large orgs, governments | ✔ (manual expertise) | ✔ (manual) | ✔ bespoke Excel | ◐ | ◐ report-level | $$ per engagement | Active |

---

## 9. Gap analysis

### 9.1 Solved well (low novelty; do not compete here)
| Capability | Evidence | Confidence |
|---|---|---|
| Single-project NPV/IRR/payback with a carbon-price input and Monte Carlo | RETScreen (free/cheap, Canadian, 800k users); HOMER; SAM/REopt | High |
| Enterprise MACC and prioritizing an abatement portfolio with NPV/IRR and carbon-price scenarios | SINAI Reduce (explicit NPV/IRR/PI, carbon-price futures); Arcadis; SLB; Sweep | High |
| Discovering Canadian grants (human-readable, with AI Q&A) | helloDarwin, GrantMatch/BDO, Business Benefits Finder, NRCan directory, Clean Growth Hub | High |
| Market intelligence and position management for compliance carbon markets | ClearBlue Vantage (TIER, EPS, QC) | High |
| Energy-system scenario data | CER EF2026, CODERS, CANOE, PyPSA-Canada, MESSAGEix-Canada | High |

### 9.2 Partially solved
| Capability | What exists | What's missing | Confidence gap is real |
|---|---|---|---|
| Incentives feeding a cash-flow model | RETScreen/HOMER input fields; VadiMAP (buildings) "incorporates incentives"; Encentiv (C&I prescriptive rebates incl. Canada) | A machine-readable Canadian **rules engine**: eligibility, amounts, caps, timing and stacking or clawback interactions (e.g. the Clean Technology ITC phase-down to 15% in 2034 and nil after 2034 *(corrected — see Errata)*; CCUS ITC full rates extended to 2035 [verified]; interactions with provincial utility and OBPS-fund grants [inferred]). No DSIRE-equivalent API for Canada. | Moderate-high (70–80%) |
| Carbon pricing in project economics | Generic carbon-price scalars and scenarios (RETScreen, SINAI); ClearBlue for compliance positions | Project value under **output-based** mechanics (benchmark × output, surplus-credit generation, credit price vs headline, provincial divergence, the post-May-2026 national path, credit floors from 2030, CCfD strike-price value) | Moderate (60–70%). Proprietary tools (Sphera, SINAI, ClearBlue enterprise) may do parts of this privately |
| Uncertainty | RETScreen Monte Carlo on technical and financial inputs; scenario and stress-tests elsewhere | **Policy-regime uncertainty**: stochastic credit prices, the probability of policy reversal, incentive sunset risk, real-options timing (invest now vs defer), which the Carbon VIX and Canadian Climate Institute evidence shows drives decisions | Moderate-high (70%) |
| Buildings: regulation-aware retrofit economics | Audette, VadiMAP, CRREM, Carbonsight | Vancouver penalties plus Toronto's (still pending) BEPS plus utility incentives plus federal ITCs in a single valuation | Moderate (55–65%). Building incumbents could add this readily |

### 9.3 Apparently unsolved in Canada (candidate wedge)
1. **An integrated, source-cited "policy-to-cash-flow" layer for Canada.** It would link each incentive, carbon-price and energy-price assumption to its legal or program source, effective dates and version, then flow through to project NPV/IRR distributions. Evidence: none of the 20+ tools reviewed advertise source-level provenance for *financial assumptions*. The nearest precedents are Manifest's "100% cited" disclosure assessments and Sweep's reporting lineage [verified]. Confidence: moderate (65–75%).
2. **Facility-level OBPS/TIER/EPS/cap-and-trade project valuation under credit-price uncertainty, including CCfD value.** This is highly topical: the policy was reset in May 2026, the Alberta credit floor regulation is due by 31 December 2026, and CCfDs run 2030–40. Today it is served by ClearBlue for positions and by consultants for project cases. Confidence: moderate (60–70%).
3. **Portfolio capital allocation across provinces that respects each jurisdiction's regime** (for example the same heat-pump project valued differently in Ontario, Alberta and Quebec). Confidence: moderate (~60%) [inferred].

### 9.4 Skeptical counterpoints (risks to the thesis)
- **Build-vs-extend risk.** Adding Canadian carbon mechanics is a data project for SINAI or ClearBlue; incumbents already hold customers and data. ClearBlue plus Deloitte Canada is a natural bundle [inferred].
- **RETScreen anchors price expectations.** It is free or about CA$869, carries Government of Canada branding and is already taught in Canadian utility training (IESO Save on Energy) [verified].
- **Data maintenance burden.** Canadian incentives churn constantly: GrantMatch and helloDarwin each track 10,000+ programs, and even ISED cut Business Benefits Finder releases to annual [verified]. Policy volatility (the 2025 consumer price removal, the 2026 national reset) raises both the value of the product and the cost of keeping it current.
- **Buyer concentration.** OBPS-covered facilities are a limited set of large emitters who already retain consultants [inferred]. Toronto BEPS is not yet adopted, which weakens near-term building demand in the largest market [verified].
- **Unverifiable internals.** Enterprise tools (Sphera, Enablon, SINAI and ClearBlue enterprise tiers) are opaque. Absence in marketing does not mean absence in product. Demos or customer interviews are needed before claiming white space.

### 9.5 Recommended validation steps
1. Book demos of SINAI Reduce, ClearBlue Vantage, VadiMAP and Audette. Ask specifically about OBPS benchmark mechanics, Canadian incentive stacking, Monte Carlo on policy variables, and assumption provenance.
2. Interview 5–10 OBPS-covered facility finance leads and 3–5 consultants (Dunsky, Blackstone, Navius) on current workflows and willingness to pay.
3. Check whether helloDarwin, GrantMatch/BDO or Encentiv license data via API. Partnering beats rebuilding.
4. Track the Alberta price-floor regulation (due 31 December 2026) and the federal benchmark update, since these define the core model.

---

## 10. Sources

**Government / public tools**
- NRCan — RETScreen Expert overview video page: https://natural-resources.canada.ca/science-data/science-research/research-centres/video-overview-retscreen-expert-platform
- NRCan — RETScreen tools page: https://natural-resources.canada.ca/maps-tools-publications/tools-applications/retscreen
- Save on Energy — Financial Analysis with RETScreen Expert (training deck): https://saveonenergy.ca/-/media/Files/SaveOnEnergy/training-and-support/ee/Financial-Analysis-with-RETScreen-Expert.pdf
- Capterra — RETScreen pricing: https://www.capterra.com/p/156830/RETScreen/
- Energy Manager — RETScreen hits 800,000 users: https://www.energy-manager.ca/retscreen-energy-management-software-hits-800000-global-users-milestone/
- Wikipedia — RETScreen: https://en.wikipedia.org/wiki/RETScreen
- OpenEI — RETScreen: https://openei.org/wiki/RETScreen_Clean_Energy_Project_Analysis_Software
- Open Government — Business Benefits Finder dataset: https://open.canada.ca/data/en/dataset/4e75337e-70d0-4ed7-92d1-3b85192ec6b1
- NRCan — Directory of Energy Efficiency and Alternative Energy Programs: https://oee.rncan.gc.ca/corporate/statistics/neud/dpa/policy_e/programs.cfm?attr=0
- NRCan — Evaluation summary, Clean Growth Hub: https://natural-resources.canada.ca/corporate/transparency/summary-evaluation-clean-growth-hub-hub
- ISED — Clean technology funding and resources: https://ised-isde.canada.ca/site/clean-growth-hub
- CER — Canada's Energy Future 2026: https://www.cer-rec.gc.ca/en/data-analysis/canada-energy-future/2026/executive-summary/index.html
- Atlantica Energy — EF2026 summary (release date, scenarios): https://www.atlanticaenergy.org/what-does-the-canadas-energy-future-2026-report-predict-for-atlantic-canada/
- ECCC — Industrial carbon pricing in Canada: https://www.canada.ca/en/environment-climate-change/services/climate-change/pricing-pollution-how-it-will-work/putting-price-on-carbon-pollution/industry.html
- Save on Energy — Efficient electrification toolkit: https://saveonenergy.ca/Training-and-Support/commercial/efficient-electrification
- CanmetENERGY — Québec industrial electrification (AEE INTEC, 2026): https://www.aee-intec.at/wp-content/uploads/2026/05/Zadoorian_S.pdf

**Carbon pricing / policy**
- EY — Alberta revises industrial carbon prices (June 2026): https://taxnews.ey.com/news/2026-1180-canada-alberta-revises-industrial-carbon-prices
- Torys — A carbon and crude compromise (May 2026): https://www.torys.com/our-latest-thinking/publications/2026/05/a-carbon-and-crude-compromise
- Osler — Canada–Alberta MOU implementation agreement (25 May 2026): https://www.osler.com/en/insights/updates/future-of-canadas-carbon-markets-anchored-by-canada-alberta-mou-implementation-agreement/?pdf=1
- Canadian Climate Institute — How to fix Alberta's broken carbon market (December 2025): https://climateinstitute.ca/how-to-fix-albertas-broken-carbon-market/
- Canadian Climate Institute — Closing the carbon-pricing certainty gap (2022): https://climateinstitute.ca/publications/closing-the-carbon-pricing-certainty-gap
- CarbonCredits.com — Canada's carbon pricing reset in 2026: https://carboncredits.com/canadas-carbon-pricing-reset-in-2026-will-industry-step-up-or-stall-climate-progress/
- Leyton — Clean technology tax credits, Budget 2025: https://leyton.com/ca/insights/articles/clean-technology-tax-credits-federal-budget-2025-whats-new
- Environment Journal — Clean economy ITCs (2024): https://environmentjournal.ca/federal-government-launches-clean-economy-investment-tax-credits-itcs
- NBER — Carbon VIX (w32937): https://nber.org/papers/w32937
- Global News — First federal carbon contract for difference (Entropy): https://globalnews.ca/news/10182096/feds-sign-first-carbon-contract-for-difference-with-calgary-based-entropy/

**Commercial platforms**
- SINAI — home: https://www.sinai.com/
- SINAI — Reduce: https://www.sinai.com/platform/reduce
- SINAI — About: https://sinai.com/about
- SINAI — Verdantix Smart Innovator post: https://www.sinai.com/post/sinai-a-smart-innovator-in-carbon-accounting-built-for-decisions
- Decarbonfuse — SINAI US$22M Series A: https://decarbonfuse.com/posts/sinai-technologies-secures-22-million-series-a-to-help-global-companies-meet-net-zero-commitments
- Sweep — Decarbonization strategy: https://www.sweep.net/en-us/decarbonization-strategy
- Persefoni — Net Zero Navigator: https://www.persefoni.com/blog/introducing-net-zero-navigator
- IBM — Envizi with Planning Analytics: https://www.ibm.com/products/envizi/sustainability-planning
- Net Zero Compare — Zeigo Activate: https://netzerocompare.com/software/zeigo-activate
- Net Zero Compare — Arcadis Net Zero Catalyst: https://netzerocompare.com/software/arcadis-net-zero-catalyst
- SLB — Decarbonization planning webinar (2026): https://www.slb.com/resource-library/webinar/di/2026/decarbonization-planning-for-impact-uncovering-actionable-business-value
- Business Travel Mag — Clarasight rebrand: https://thebusinesstravelmag.com/sustainability-heavyweights-join-rebranded-climate-club/
- Carbon Trail — June 2025 product update: https://carbontrail.net/blog/june-2025-product-update/
- Signalbase — Watershed acquires Emitwise: https://www.trysignalbase.com/news/acquisitions/emitwise-acquired-by-watershed-acquisition
- Verdantix — Carbon software consolidation 2026 (Diginex/Plan A): https://www.verdantix.com/insights/blog/carbon-software-consolidation-will-continue-in-2026--diginex-acquires-plan-a
- Verdantix — Consolidation heats up: https://research.verdantix.com/vantage/blog/consolidation-heats-up-in-carbon-management-software
- Verdantix — Green Quadrant Enterprise Carbon Management 2026 press release: https://www.verdantix.com/insights/press-release/verdantix-green-quadrant-report-shows-firms-turning-to-operational-decarbonization-to-unlock-financial-value-and-strengthen-competitiveness
- Schneider IM — Microsoft products retiring in 2026: https://www.schneider.im/lu/microsoft-products-retiring-in-2026/
- ESG Today — Novisto acquires Minimum: https://www.esgtoday.com/novisto-acquires-carbon-accounting-software-provider-minimum/
- Manifest Climate — home: https://www.manifestclimate.com/
- Decarbonfuse — ClearBlue Vantage Position Optimization: https://decarbonfuse.com/posts/clearblue-markets-launches-new-position-optimization-solution-powered-by-vantage
- Net Zero Compare — ClearBlue Vantage: https://netzerocompare.com/software/clearblue-vantage
- Deloitte Canada — Deloitte and ClearBlue partnership: https://www.deloitte.com/ca/en/about/press-room/deloitte-canada-and-clearblue-markets-join-forces-to-unlock-carbon-value.html

**Incentive data**
- helloDarwin — platform: https://hellodarwin.com/platform
- BDO Canada — acquires GrantMatch: https://www.bdo.ca/about/news/bdo-canada-acquires-grantmatch
- Business Wire — CLEAResult and Encentiv Energy: https://www.businesswire.com/news/home/20250617258705/en/CLEAResult-and-Encentiv-Energy-Partner-to-Advance-Utility-Incentive-Delivery-for-Commercial-Customers
- NC Clean Energy Technology Center — DSIRE API: https://nccleantech.ncsu.edu/?p=13484
- Rewiring America — Incentive API: https://www.rewiringamerica.org/tools/incentive-api

**Buildings**
- Audette — home: https://www.audette.io/
- BetaKit — Audette seed round (2021): https://betakit.com/?p=311578
- Goodmans — Audette raises $12.8M (snippet only): https://goodmans.ca/insights/post/goodmans-tech-blog/audette-raises-12.8-million-to-help-decarbonize-the-planet
- SBIZ — VadiMAP: https://sustainablebiz.ca/vadimap-builds-custom-decarbonization-paths-for-building-owners
- VadiMAP — home: https://www.vadimap.com/
- Autocase — Carbonsight launch: https://autocase.com/carbonsight-launch-building-portfolio-decarbonization-planning-tool-unveiled/
- ULI — Granular CRREM pathways for the US and Canada: https://urbanland.uli.org/sustainability/creating-more-granular-crrem-pathways-for-the-united-states-and-canada
- CaGBC — Decarbonize: https://www.cagbc.org/decarbonize
- TMU BEACON — Retrofit policy support tools: https://www.torontomu.ca/beacon/projects/retrofit-policy-support-tools/
- City of Toronto — Emissions performance standards: https://www.toronto.ca/services-payments/water-environment/net-zero-homes-buildings/emissions-performance-standards/
- Efficiency Canada — Toronto BPS: https://www.efficiencycanada.org/toronto-moving-ahead-on-building-performance-standards-what-you-need-to-know/
- The Energy Mix — Vancouver large-building limits: https://www.theenergymix.com/vancouver-sets-2040-decarbonization-deadline-for-large-buildings/

**Industrial / energy project tools and open source**
- NLR — REopt software updates: https://www.nrel.gov/reopt/curriculum/software-updates
- US DOE — NREL renamed National Laboratory of the Rockies: https://www.energy.gov/eere/articles/energy-department-renames-nrel-national-lab-rockies
- SAM — home: https://sam.nrel.gov/
- Capterra — HOMER Pro pricing: https://www.capterra.com/p/182590/HOMER-Pro/pricing/
- CODERS / COPPER documentation: https://sesit-copper.readthedocs.io/en/latest/CODERS%20Connections/
- University of Toronto — CANOE model: https://sustainablesystems.civmin.utoronto.ca/canoe/
- PyPSA — Models list (PyPSA-Canada, PyPSA-BC): https://docs.pypsa.org/latest/home/models/
- Nature npj Climate Action — MESSAGEix-Canada pathways (2026): https://www.nature.com/articles/s44168-026-00355-5
- GitHub — ggmacc: https://github.com/aj-sykes92/ggmacc
- Canadian Climate Institute — Navius modelling report: https://climateinstitute.ca/wp-content/uploads/2025/02/Navius-Research-Modelling-Report.pdf

**Consulting**
- Partners in Project Green — Mantle Climate spotlight: https://partnersinprojectgreen.com/blog/member-spotlight-mantle-climate/
- Environment Journal — Mantle Developments spin-off: https://environmentjournal.ca/?p=3030
- OECM — Blackstone Energy Services: https://oecm.ca/supplier-partners/blackstone-energy-services/
- Canadian Renewable Energy Association — Dunsky profile: https://renewablesassociation.ca/leading-member/dunsky-energy-climate-advisors/
- Ontario Environmental Registry — Enerlife comments (2026): https://ero.ontario.ca/public/public_uploads/2026-05/Enerlife%20Comments%20ERO%20026-0300.pdf

---

## Errata (added during synthesis, 2026-09-29)

- **CT ITC phase-down.** §9.2 originally described the Clean Technology ITC as phasing down to 20%/10%/5% over 2032–2034. That schedule belongs to the *Clean Technology Manufacturing* ITC. The CT ITC is 30% for property available for use before 2034, 15% in 2034 and nil after 2034 (CRA: eligible from 28 Mar 2023 to 31 Dec 2034). Corrected in the text.
- **Ontario EPS credit price.** The ~$72/t figure here (ClearBlue via carboncredits.com) is consistent with IETA's "15–20% below the compliance price". File 02's original ~$34–42 was wrong and has been corrected.
