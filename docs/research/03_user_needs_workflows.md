# 03 — User Needs, Workflows and Demand Drivers: Canada Climate CapEx Engine

*Research date: 2026-09-29. Tagging: **[verified]** means a cited source directly supports the claim. **[inferred]** means it is my synthesis or estimate from the evidence and has not been confirmed. Market-sizing numbers are marked with their year. Sources are numbered in the list at the end ([S#]).*

---

## 0. Bottom line (for decision-makers)

1. **The workflow is real, but the recurring user base is narrow.** The "MACC → NPV/IRR with carbon price and incentives → investment committee" workflow exists at large emitters, big real-estate owners and in federal and municipal assets, where it is sometimes required (federal GHG life-cycle cost analysis at $300/t for 40 years; FCM Green Municipal Fund "incremental life-cycle cost per tonne"). Most of this analysis is done **episodically, by consultants/ESCOs/engineers in Excel, RETScreen or energy-modelling tools**. It is not done continuously by an internal software user [verified for the requirements, inferred for the frequency].
2. **Canada's 2025–26 policy trend mostly *reduces* compliance-driven urgency.** The consumer carbon price was removed (Apr 2025). The CSA climate rule is paused. Transition plans are not mandated. The taxonomy is voluntary. Greenwashing rules were narrowed (Bill C-15, Mar 2026). The two biggest banks by assets dropped financed-emissions targets (Apr 2026). Alberta's industrial price path was cut from $170 by 2030 to $130 by 2035 [verified].
3. **Complexity, not mandates, is the strongest pain signal.** Several parameters that decide go/no-go are uncertain and fragmented:
   - 11 unlinked carbon markets.
   - Credit prices far below headline prices (TIER ~$18–30 vs $95).
   - An "effective marginal carbon price" that ranges from <$50 to >$130 where market prices look the same.
   - ITCs with 100% CRA audit and roughly a one-third denial rate.
   - Federal program applications that average 407 hours.

   These points favour a **parameter/scenario engine and compliance-cost forecaster sold to the advisors and large emitters who must price this uncertainty**. They do not favour a broad self-serve corporate SaaS [inferred].
4. **Strongest segments:**
   - (a) regulated large emitters (~1,000 priced facilities; roughly 55 companies ≥1 Mt), for carbon-compliance-cost and CCfD/ITC economics;
   - (f) consultants/ESCOs/engineering firms, who run these analyses repeatedly for MUSH, federal and CRE clients.
   - Commercial real estate is sizeable but served by funded incumbents (Audette, Deepki, etc.) and free tools (KingSett), and near-term regulatory pain is weak outside Vancouver/Montreal.

---

## 1. How decarbonization capex decisions are actually made today

### 1.1 The canonical corporate workflow
1. **Baseline and abatement inventory.** Site/energy teams list candidate projects. At ConocoPhillips, ideas are submitted on an internal platform ("FUEL") and a cross-functional GHG technology group meets monthly [verified, S30].
2. **MACC construction.** Projects are plotted by "breakeven cost of carbon that considers capital cost, operating costs and potential increased revenue" against cumulative abatement [verified, S30]. Consultants and vendors cite that ~50% of Scope 1–2 reductions in key sectors are "net-zero cost" on MACCs (Mars: goals reachable at <1% of sales) [verified, S29].
3. **Carbon price treatment.** This is split:
   - Many firms use a **shadow price** in capex appraisal. Among CDP respondents who use internal carbon pricing (ICP), 50.8% use shadow prices vs 15% internal fees. Median ICP was only ~US$22–25/t (2017–2020) [verified, S26].
   - Others deliberately **exclude** an ICP. ConocoPhillips states "an internal carbon price is not included in the economic analysis because the MACC provides an overall picture of which projects… would be economic at certain carbon price levels" [verified, S30].
   - Firms facing mandatory carbon pricing are ~5× more likely to adopt an ICP [verified, S26]. Academic work finds ICP adoption follows **actual** regulatory exposure, not stated national targets [verified, S27].
4. **Capital allocation.** Projects compete in normal capex cycles against hurdle rates. Two recurring structural fixes appear:
   - **Ring-fenced central funding.** ConocoPhillips created a "discretionary corporate funding mechanism" in 2019, and its project count rose from 45 to 100+ [verified, S30].
   - **Metric translation into NPV/tonne.** A City of Toronto-hosted energy-management guide recommends **NPV/tonne** as "the preferred metric" and "engage finance teams early to align on key metrics" [verified, S35].
5. **Investment committee / executive decision.** At ConocoPhillips this is annual, by the executive leadership team, using seven criteria including $/tCO2e, scalability and strategic value [verified, S30].

### 1.2 Mandated public-sector variants (institutionalised demand)
- **Federal real property (Greening Government Strategy).** "All major building retrofits, including significant energy performance contracts, require a GHG reduction life cycle cost analysis… period of 40 years and a carbon shadow price of $300 per tonne." TBS requires the analysis for major real-property funding proposals that do not reach net zero [verified, S36]. The companion LCCA appendix says that:
  - the **consultant/ESCO performs the analysis**;
  - hourly simulation tools (EnergyPlus, IESVE, eQUEST) are used for major projects, **RETScreen** for simpler ones;
  - the discount rate is Government of Canada borrowing cost [verified, S37].
- **Municipal (FCM Green Municipal Fund, Community Buildings Retrofit).** GHG-reduction-pathway feasibility studies must compute capital and operating costs over ≥20 years, **incremental life-cycle cost (ILCC)** and **$ILCC/tCO2e**, using the federal carbon price schedule ($170 by 2030) with documented post-2030 assumptions. Confirmed funding is shown separately and prospective funding goes in sensitivity analysis. A P.Eng/CEM/CEA must do the work [verified, S38].
- **Ontario broader public sector (O. Reg. 25/23).** Municipalities, school boards, universities, colleges and hospitals file annual energy/GHG reports and **five-year conservation & demand management plans** [verified, S39].

*Implication [inferred]:* these templated requirements create repeat, standardised analytical work for engineering consultants. That makes a "consultant-grade engine" wedge plausible.

### 1.3 Who owns it
| Role | Typical responsibility | Evidence |
|---|---|---|
| Energy manager / site engineering | Project identification, savings estimates, incentive applications | IESO SEM requires an "energy champion" [verified, S41]; O. Reg 25/23 plans [verified, S39] |
| Sustainability team | Targets, MACC, disclosure | EY: 92% of Canadian firms report board oversight of climate risk, but only **8%** have board oversight of **climate-related capital allocation** [verified, S20] |
| Corporate finance / FP&A / CFO | Hurdle rates, capex allocation | Deloitte (≈140 US energy/manufacturing finance execs): 73% have a decarb strategy, but **fewer than half** of finance execs had a decision-making role; **only 17%** view decarb spend as "a profitable investment" [verified, S23] |
| External consultants / ESCOs | Feasibility, LCCA, energy modelling | Federal LCCA and GMF studies are performed by consultants/ESCOs/P.Eng [verified, S37, S38] |

### 1.4 Tools in use
- **Excel** is the default for MACCs/LCCA [inferred; widely reported, not directly quantified in sources].
- **RETScreen** (NRCan, free) is explicitly accepted by the federal LCCA guide for simpler analyses and is used in health-care net-zero training [verified, S37, S52].
- **Free models from industry.** KingSett released a free, editable property-level decarbonization model (utility bills, capex, emission factors, inflation) built for its 5.4M sq ft portfolio [verified, S44].
- **Commercial platforms:**
  - **SINAI** (facility-level MACC with NPV, IRR, payback, capex/opex, carbon-price scenarios; clients include Siemens Energy and ArcelorMittal) [verified, S31];
  - **Audette** (Vancouver; AI retrofit roadmaps for CRE; partners include Onni and Colliers; 1,300 retrofit plans; CA$12.8M round) [verified, S42, S43];
  - carbon-accounting suites (Watershed median ~US$70k/yr, range $50–250k+) [verified, S47].
- **Carbon market analytics.** ClearBlue Markets reports clients need "market forecasts and regulatory clarity" to justify capex rather than buying compliance credits [verified, S19].

### 1.5 Why MACCs don't become capex (the "capital allocation gap")
- **Canada lags on integrating plans into capex.** EY 2025 Barometer:
  - only **26%** of assessed Canadian companies disclose capex allocated to transition (vs 42% globally);
  - **6%** report all elements of a robust transition plan (vs 22% globally);
  - 6% quantify climate financial impacts [verified, S20].
- CDP (2024) had the S&P/TSX60 among the lowest G20 performers on transition-plan disclosure (28%) [verified, S21].
- Verdantix 2025 (355 senior stakeholders): just over **26%** strongly agree their decarbonization strategy is fully integrated into business and investment planning. Nearly 40% have no consistent way for operational teams to access climate data [verified, S22].
- Verco (citing the TPI 2025 report): "only 0.5% of public companies have CapEx and decarbonisation goals aligned." Once easy wins are exhausted, IRRs "struggle to compete… within traditional corporate hurdle rates" [verified as quoted, S24].
- Energy projects lose to growth capex even when their risk-adjusted returns are better [verified, S25].

---

## 2. Demand drivers and suppressors: 2026 status

| Driver | 2026 status | Effect on demand | Tag |
|---|---|---|---|
| **Consumer carbon price** | Removed 1 Apr 2025. Voluntary OBPS facilities allowed to exit; 11 of 27 voluntary federal-OBPS participants exited by end-2025 | ↓ Removes carbon-cost line for small/mid firms and buildings | [verified, S12, S13] |
| **Industrial carbon pricing (large emitters)** | Survives, but weakened and fragmented. Alberta (Canada–AB MOU implementation, May–Jun 2026): $100 for 2027–29, $115 in 2030, +$3/yr to $130 by 2035, 1.5%/yr to $140 by 2040. Credit price floor $60 in 2030 rising to $110 in 2040. Direct-investment credits capped at 50% of capex/opex. Joint CfDs for up to 75 Mt (≤$600M per government). Lower stringency rates. Federal benchmark review in 2026 | ↑ Complexity (a good fit for modelling) but ↓ price level; strong need to value CfDs, floors and credit pathways | [verified, S8, S9, S14] |
| **Credit market prices** | TIER credits ~C$24.50 (Aug 2025), ~C$18 (late 2025), ~$28–30 (Sept 2025 IETA) vs $95 fund price. Ontario EPS ~$72, BC ~$65, federal OBPS areas ~$37.50 | Marginal price ≠ headline price, which makes project economics hard to call | [verified, S10, S11, S15] |
| **Effective marginal carbon price** | CCI (Jan 2026): systems with nearly identical market prices show MECP "ranging from below $50 to above $130/t". 77% of TIER scenarios that pass federal tests still fail to deliver $130 | ↑ Direct evidence that a modelling engine adds analytical value | [verified, S16] |
| **Clean economy ITCs** | Five ITCs in force. Bill C-15 (Royal Assent 26 Mar 2026) enacted the Clean Electricity ITC and extended CCUS rates. Domestic-content consultation Feb–Mar 2026, undecided | ↑ Incentive complexity; CRA backlog ↓ confidence | [verified, S5, S6] |
| **CSA climate disclosure rule** | Paused Apr 2025. Budget 2025 said it would "work with provinces" and revive/align with CSSB, but there is no mandate as of Sep 2026 | ↓ No compliance forcing function for issuers | [verified, S2, S3, S4]; "no mandate as of Sep 2026" [inferred from absence of any found announcement] |
| **Federal private-company (CBCA) disclosure** | Committed Oct 2024 and reaffirmed Nov 2025 per CCLI. Not in force | Latent ↑ | [verified, S48] |
| **Transition-plan mandate** | Budget 2025: "Transition planning: Not included" (PRI). The Taxonomy & Transition Planning Council was launched 8 Apr 2026 and is **voluntary**, with "no enforcement function"; draft methodology Jul 2026; first three sectors (electricity, transport, buildings) due end-2026 | Weak ↑ (voluntary taxonomy may shape transition-bond and lender criteria) | [verified, S7, S49, S50] |
| **OSFI B-15** | In force for FRFIs. Scope 3 financed-emissions disclosure moved to FY2028 (on-balance sheet) / FY2029 (off-balance sheet). Transition-plan and scenario expectations "unchanged", but implementation dates to be determined. AUM financed-emissions consultation paused Jan 2026 | ↑ Slow, lender-side data requests to borrowers; low urgency before 2028 | [verified, S1, S17] |
| **Bank commitments** | 4–5 big banks left NZBA (Jan 2025). RBC dropped its $500B sustainable-finance target (May 2025). **RBC and Scotiabank retired 2030 financed-emissions targets (30 Apr 2026)**; Scotiabank also dropped its 2050 financed net-zero goal. Both "maintain engagement on transition strategies" | ↓ Lender pull for borrower transition plans | [verified, S18, S53] |
| **Greenwashing law** | Bill C-15 (26 Mar 2026) removed the "internationally recognized methodology" test for business-level claims and curtailed private access to the Tribunal. The "adequate and proper substantiation" requirement remains | ↓ Greenhushing pressure eases; less need for defensible methodologies | [verified, S51] |
| **Municipal building performance standards** | **Vancouver**: GHG limits in force (office 25, retail 14 kgCO2e/m²/yr for 2026, enforced from the 2027 reporting year). 745 buildings reporting, but **90% already below the 2026 limits**. **Montreal**: A–F ratings for buildings ≥2,000 m²; zero-emission large buildings by 2040. **Toronto**: reporting bylaw in force (≥929 m²). BEPS still "developing a proposed approach" per City page; ~40,000 buildings in initial scope; TransformTO 2026–30 plan implied 4–5 yrs preparation | ↑ Medium-term retrofit capex planning in 3 cities; weak near-term pain | [verified, S54, S55, S56, S57, S58]; Toronto timing [inferred] |
| **Federal procurement / Greening Government** | $300/t shadow-price LCCA mandatory for major federal retrofits and EPCs | ↑ Steady consultant/ESCO demand | [verified, S36, S37] |
| **US policy (cross-border firms)** | OBBBA (Jul 2025): wind/solar must begin construction by 4 Jul 2026 or be in service by end-2027. 45V requires construction start by end-2027. 45Q survives to 2032. FEOC rules. US industrial decarb cancellations ($17B) exceed new investment ($15B) since 2018 | ↓ Cross-border capex re-prioritised; ↑ need for comparative jurisdiction modelling | [verified, S59, S60] |
| **Macro/ESG backlash** | GRESB Canadian participants fell to 78 (2025) from 85; 83% of North American GlobeScan respondents report "significant backlash". Global SLL volumes −52% H1 2025 vs H1 2024 | ↓ | [verified, S45, S61] |

---

## 3. Segment analysis

Counts are for Canada unless noted. "Evidence" rates how well the pain and willingness to pay (WTP) are supported: **High** (multiple primary sources), **Med**, **Low**.

| Segment | Size / count | Decision-maker | Decision frequency | Current tools | Pain intensity | WTP signal | Evidence |
|---|---|---|---|---|---|---|---|
| **(a) Large industrial emitters** (oil sands, cement, steel, chemicals, P&P, fertiliser, refining) | 1,862 facilities reported GHGs in 2023 (≥10 kt; 291 Mt = 42% of national) [verified, S62]. Priced facilities: TIER 528 compliance reports (2023) [verified, S11]; Ontario EPS ~200 [verified, S63]; BC OBPS ~120–130 [verified, S64, S65]; federal OBPS 41 (2025, 14 mandatory) [verified, S13]; QC/SK/Atlantic not verified. **55 companies emitted ≥1 Mt** (2021) [verified, S66]. Estimated ~1,000–1,200 priced facilities and ~300–500 parent firms [inferred] | Corporate development / strategy, CFO, environment & regulatory, investment committee | Annual compliance planning plus episodic major FIDs (years apart, e.g. Pathways FID now late 2027–early 2028) [verified, S67] | In-house Excel models, consultants, carbon-market advisors (ClearBlue), legal/tax advisors | **High and rising in complexity**: price path changes, credit floors, CfDs, DIC caps, 11 markets, ITC labour rules, 407-hour federal applications [verified, S8, S16, S19, S66] | High ability to pay (they already buy advisory). But few buyers, bespoke needs and strong in-house teams [inferred] | High |
| **(b) Commercial real estate / REITs / pension real estate** | 78 Canadian GRESB participants (2025) [verified, S45]; Vancouver 745 large buildings [verified, S54]; Toronto ~40,000 buildings in proposed BEPS scope [verified, S58] | VP Sustainability / asset management, capital planning, investment committee | Annual capex plans; retrofit timing tied to equipment end-of-life | Audette, Deepki, Measurabl-type platforms; KingSett free model; consultants [verified, S42, S44] | Medium. Biggest barrier is "lack of a strong business case": business-as-usual still pays better, plus valuation models and gas-HVAC lifecycles [verified, S33]. Regulation is not yet binding in Toronto; Vancouver mostly compliant | Medium; crowded and partly free | Med |
| **(c) Mid-market manufacturers and food processors** | Not verified (thousands of firms) | Owner/GM, plant manager, controller | Rare, reactive (equipment failure) | Utility programs, consultants, vendors' quotes | Low perceived need: **70.2%** say green investment is "not necessary to continue operations"; 64.6% cite lack of financing and support; 47% lack talent (EMC survey, n=700, 2024) [verified, S68]. CME: only 25% have 2050 targets; 44% cite lack of resources [verified, S69] | Low; subsidised tools (IESO SEM gives up to $5,000 for energy-management tools) [verified, S41] | Med |
| **(d) Municipalities / MUSH (hospitals, universities, school boards)** | 555+ PCP member municipalities [verified, S70]; Ontario BPS reporters under O. Reg 25/23 (count not verified) [verified, S39] | Facilities/energy manager, capital planning, council/board | 5-year CDM plans; grant-cycle-driven feasibility studies | RETScreen, Portfolio Manager, consultants funded by GMF [verified, S38, S52] | Medium: required LCCA-per-tonne analyses, grant stacking | Low direct WTP (procurement, grant-funded). Better reached via consultants [inferred] | Med |
| **(e) Lenders / banks / pensions (B-15)** | ~400 OSFI-regulated FIs [verified, S71]; 6 big banks drive most volume [inferred] | Climate risk, credit risk, sustainable finance teams | Annual portfolio exercises; deal-level for labelled loans | Vendor ESG data (MSCI, S&P etc.), Manifest Climate, internal models [inferred] | Falling: Scope 3 deadlines pushed to FY2028/29; transition-plan dates TBD; targets retired by RBC/Scotia [verified, S1, S53] | Medium-high budgets but long sales cycles; vendors entrenched [inferred] | Med |
| **(f) Consultants / ESCOs / engineering firms** | Count not verified. Federal LCCA and GMF studies must be done by consultants/ESCOs/P.Eng [verified, S37, S38]; CIB Building Retrofits Initiative >$1B committed, incl. $100M with Ameresco [verified, S40] | Practice leads, principals | **Continuous**: many studies per year across clients [inferred] | Excel templates, RETScreen, energy-modelling software | Medium-high: repeated re-work of carbon price paths, incentive rules and financing assumptions each engagement [inferred] | Medium: tool spend per seat is modest, but a time-savings case is plausible [inferred] | Med-Low (inferred pain; needs interviews) |
| **(g) Project developers seeking ITCs/CCfDs/CGF/CIB** | 1,763 clean-economy ITC claims ($1.6B) filed to 31 Mar 2026; CT ITC 1,261 claims ($1.23B) [verified, S72] | CFO, tax, project finance | Per project | Tax advisors (Leyton, Big 4), law firms | **High**: 100% audit rate, about one-third of claims denied, labour-rule penalties, CRA delays >1 year; 69–87% of claims still "in progress" [verified, S5, S73, S72] | Medium-high per deal but fragmented; advisors are the incumbent channel [inferred] | High |

**Strongest segments [inferred]:** (a) large emitters and (f) consultants/ESCOs, with (g) as a feature wedge (ITC/CCfD economics). CRE (b) is the largest visible segment but the most contested.

---

## 4. Pain-point evidence

### 4.1 Carbon price credibility and fragmentation
- Clean Prosperity (Feb 2024): "Firms and investors lack confidence that provincial carbon markets will deliver the revenue they need to justify big, long-term investments." Current policy gets 5–10 Mt of industrial reductions by 2030 vs a potential 33 Mt with broad CCfDs [verified, S74].
- CCI: the Alberta freeze put "billions" in projects and ~$5B of credits at risk [verified, S75]. Industrial pricing drives 20–48% of 2030 reductions; projects such as a $9B petrochemical plant, $2.7B steel upgrades and a $1.4B cement plant depend on it [verified, S76].
- CCS buildout is "stalled" by fragmented markets and depressed credit prices (Carbon Pulse panel, Nov 2025) [verified headline, S77].
- 11 unlinked Canadian carbon markets leave firms long in one province and short in another [verified, S19].

### 4.2 Incentive complexity and uptake
- **ITC uptake is far below fiscal projections.** PBO projects $103B in ITC costs to 2034–35, averaging $11.2B/yr in 2029–35 [verified, S78]. Actual claims to 31 Mar 2026 total only **$1.6B** [verified, S72]. Gowling notes credits remain "significantly underutilized… far less than the budgeted $10 billion per year" [verified, S5].
  - *Caveat [inferred]:* much of the projected cost is back-loaded to large electricity, CCUS and hydrogen projects, so the gap does not prove navigational failure.
- **Access friction.** "A significant number of eligible companies haven't figured out how to leverage the ITCs" (CleanTech North) [verified, S72]. There is a 100% audit rate, about one-third of claims are denied (ineligible property, available-for-use timing, labour non-compliance, unreported government assistance), and CRA pre-audit delays exceed one year in some cases [verified, S5, S6]. CRA received $23M (2025–26) and $28M (2026–27) for a 450% capacity increase from summer 2026 [verified, S73]. That may ease the delay pain.
- **Federal program friction.** Net Zero Accelerator applications took an average of **407 hours**; agreements took ~20 months; only 15 of 55 ≥1 Mt emitters applied and 2 signed [verified, S66]. RBC's leadership survey: incentives are seen as "untouchable" with "complex granting processes" [verified, S79].

### 4.3 Do incentives or carbon prices change go/no-go?
- **Yes, for a meaningful minority.** IESO Retrofit program evaluation (PY2023):
  - free-ridership was 22.7% (prescriptive) and 32.5% (custom);
  - in custom projects, ~45% of participants would have **delayed or cancelled** without the incentive;
  - in prescriptive projects, 23% would have delayed and 14% cancelled [verified, S80].

  So incentives change timing or go/no-go for roughly 35–45% of C&I projects, and roughly a quarter would proceed anyway.
- **Carbon price matters only when credible and binding.** ICP adoption tracks actual regulatory exposure [verified, S27]. Some sophisticated firms deliberately leave carbon price out of the NPV and use MACC breakevens instead [verified, S30].

### 4.4 Organisational pain
- Only 8% of Canadian firms have board oversight of climate capital allocation [verified, S20]. Fewer than half of finance execs had a decision role in the decarb strategy, and 17% see it as profitable [verified, S23]. The problem is **governance and economics**, not only analytics [inferred]. Better models do not fix a weak business case.

---

## 5. Counter-evidence (reasons demand may be weak)

1. **The mandate tide went out in 2025–26.** Consumer carbon price repealed. CSA rule paused. No transition-plan mandate. Voluntary taxonomy. Narrowed greenwashing law. Bank targets retired [verified; see §2].
2. **Economics, not tooling, are the binding constraint.**
   - REALPAC/CAGBC/Smart Prosperity: business-as-usual delivers better returns; barriers are capital, valuation, gas-HVAC lifecycles, skills and data [verified, S33].
   - EMC: 70% of manufacturers see no need [verified, S68].
   - Deloitte: 83% of finance execs do not see decarb as profitable [verified, S23].
3. **Decisions are infrequent and bespoke.** Large FIDs happen years apart (Pathways moved to late 2027–2028 and was scaled from 22 Mt to 6 Mt) [verified, S67]. Low usage frequency undermines SaaS retention [inferred].
4. **Free and incumbent substitutes are abundant.** RETScreen (free, government-endorsed), KingSett free model, GMF/TBS templates [verified, S37, S38, S44]. Funded vendors already sell MACC plus NPV/IRR (SINAI) and CRE roadmaps (Audette) [verified, S31, S42]. Carbon-market advisory (ClearBlue) and Big-4/law firms own the ITC and compliance channels [verified, S19; inferred for Big-4].
5. **Near-term BEPS pain is thin.** 90% of Vancouver's covered office/retail buildings already meet the 2026 limits [verified, S54]. Toronto BEPS is not yet adopted [verified, S57].
6. **ESG retrenchment.** GRESB Canadian participation is down, SLL volumes are down 52%, and US industrial decarbonization cancellations exceed new investment [verified, S45, S61, S60].
7. **Policy parameter volatility cuts both ways.** It raises the value of a well-maintained parameter set but also raises maintenance cost. Buyers may simply wait for clarity (2026 federal benchmark review, domestic-content rules) [inferred].

---

## 6. Adjacent opportunity assessment

| Opportunity | Demand evidence | Existing providers | Likely buyer | Assessment |
|---|---|---|---|---|
| **(i) ITC and utility incentive eligibility/stacking navigator** | Claims $1.6B vs ~$10B/yr budget; one-third denied; "companies haven't figured out how to leverage the ITCs"; 407-hr applications; incentives change 35–45% of C&I decisions [verified, S5, S66, S72, S80] | Tax advisors (Leyton, Ryan), law firms, grant platforms (e.g., hellodarwin), Efficiency Canada policy DB (login-gated) [verified, S81, S82] | CFO/tax at developers and mid/large firms; consultants | **Strong pain, contested channel.** Liability risk (denials, labour penalties) pushes buyers to advisors. Best as a component sold to advisors [inferred] |
| **(ii) Industrial carbon-compliance cost / credit-price forecaster** (OBPS/TIER/EPS/BC; CfD valuation; floors; DIC) | CCI: MECP ranges <$50 to >$130 at the same market price; new Alberta floors, CfDs and DIC caps (2026); 2026 federal benchmark review; ClearBlue clients want forecasts [verified, S8, S16, S19, S14] | ClearBlue Markets, Platts/S&P, Veyt, internal teams, consultants [verified, S10, S19] | ~300–500 emitter parents, traders, lenders, CCS developers [inferred] | **Strongest analytical fit.** Few buyers, high value per buyer; must beat specialist advisors on data freshness [inferred] |
| **(iii) BEPS compliance + retrofit financial planning** | Vancouver in force; Montreal 2040 path; Toronto ~40k buildings pending; CIB >$1B retrofits [verified, S40, S54, S55, S58] | Audette, Deepki, Brightly, KingSett model, consultants [verified, S42, S44] | REITs, pension RE, condo/co-op boards, property managers | **Large but crowded**; timing depends on Toronto adoption [inferred] |
| **(iv) Lender-side transition-plan credibility (B-15)** | OSFI's five credibility elements; Scope 3 from FY2028 [verified, S17, S1] | MSCI, S&P, Moody's, Manifest Climate, Arbor [verified, S83; others inferred] | Banks, insurers, pensions | **Weakening near-term.** Targets retired, dates TBD. Low priority [inferred] |
| **(v) Open, provenance-tracked Canadian climate-policy parameter dataset/API** | Fragmented parameters across 11 markets, 5 ITCs, provincial utility programs and municipal BEPS. GMF/TBS require documented carbon-price assumptions. Efficiency Canada DB is login-gated with no API found [verified, S38, S82] | CER Energy Futures, ECCC data, NGO trackers; no single maintained API found [inferred] | Consultants, researchers, modellers, fintech builders | **Good credibility wedge / top-of-funnel.** Monetisation weak alone; pairs well with (ii) and (vi) [inferred] |
| **(vi) Consultant-grade model templates / engine** | Mandated LCCA/ILCC workflows (TBS $300/t for 40 yrs; GMF $ILCC/t); consultants/ESCOs perform them [verified, S36, S37, S38] | Excel, RETScreen, in-house templates | Engineering firms, ESCOs, energy advisors | **Most repeatable usage.** Lower WTP per seat but high frequency; validate via interviews [inferred] |

---

## 7. Recommended validation next steps [inferred]
1. Interview 8–10 consultants/ESCOs doing GMF CBR and federal LCCA studies. Measure hours spent on carbon-price, incentive and financing assumptions per study.
2. Interview 5–8 large-emitter compliance/strategy leads (Alberta, Ontario, BC) about how they model TIER/EPS after the 2026 MOU and value CfDs. Test WTP against ClearBlue/advisor spend.
3. Track the 2026 federal benchmark review, Toronto BEPS bylaw vote, ITC domestic-content decision and the CSA restart. Each is a binary demand catalyst.

---

## Sources

- [S1] OSFI, Letter to Industry – Updating Guideline B-15 for final CSSB standards (20 Feb 2025): https://www.osfi-bsif.gc.ca/index%2ephp/en/guidance/guidance-library/letter-industry-we-are-updating-guideline-b-15-final-cssb-standards
- [S2] Torys, CSA climate disclosure rule on hold (Apr 2025): https://www.torys.com/en/our-latest-thinking/publications/2025/04/csa-climate-disclosure-rule-on-hold
- [S3] Bennett Jones, CSA pause on climate/diversity disclosure: https://www.bennettjones.com/Insights/Blogs/2025/04/CSA-Announces-Pause-on-Climate-Related-and-Diversity-Related-Disclosure-Projects
- [S4] Smith School ISF, Budget 2025 reaction (4 Nov 2025): https://smith.queensu.ca/centres/isf/news/ISF-budget-reaction.php
- [S5] Gowling WLG, Canada clean economy ITCs (2026): https://gowlingwlg.com/en/insights-resources/articles/2026/canada-clean-economy-investment-tax-credits
- [S6] Torys Quarterly Q2 2026, Clean economy ITCs: https://www.torys.com/en/our-latest-thinking/torys-quarterly/q2-2026/clean-economy-investment-tax-credits
- [S7] McCarthy Tétrault, Canada's new sustainable finance taxonomy / TTPC: https://www.mccarthy.ca/en/insights/blogs/canadian-securities-regulatory-monitor/canada-s-new-sustainable-finance-taxonomy-what-the-taxonomy-and-transition-planning-council-means-for-business
- [S8] Blakes, Implementation of the Canada–Alberta MOU (28 May 2026): https://www.blakes.com/insights/implementation-of-the-canada-alberta-mou-key-takeaways-for-carbon-markets-in-alberta/
- [S9] EY Global Tax News, Alberta revises industrial carbon prices (3 Jun 2026): https://globaltaxnews.ey.com/news/2026-1180-canada-alberta-revises-industrial-carbon-prices
- [S10] S&P Global, Alberta carbon market oversupply (Aug 2025): https://www.spglobal.com/energy/en/news-research/latest-news/energy-transition/080425-alberta-carbon-market-grapples-with-sustained-oversupply-2026-review-on-horizon
- [S11] IETA Business Brief – Alberta (Sep 2025): https://www.ieta.org/uploads/wp-content/2025/09/IETA-Business-brief-Alberta-19Sept.pdf
- [S12] IETA Business Brief – Canada OBPS (Sep 2025): https://www.ieta.org/uploads/wp-content/2025/09/IETA-Business-brief-Canada-OBPS-19Sept2Final.pdf
- [S13] ICAP, Canada federal OBPS factsheet: https://icapcarbonaction.com/en/ets-pdf-download/135
- [S14] CarbonCredits.com, Canada's carbon pricing reset in 2026 (1 Dec 2025): https://carboncredits.com/canadas-carbon-pricing-reset-in-2026-will-industry-step-up-or-stall-climate-progress/
- [S15] (same as S14 for provincial credit prices)
- [S16] Canadian Climate Institute, Outcomes Not Optics (Jan 2026): https://climateinstitute.ca/wp-content/uploads/2026/01/Canadian-Climate-Institute-Outcomes-Not-Optics-Canadian-carbon-markets-need-bold-reform-to-be-effective.pdf
- [S17] OSFI, Seeing the Forest through the Trees (speech): https://www.osfi-bsif.gc.ca/en/news/seeing-forest-through-trees-implementation-challenges-climate-risk-supervision ; OSFI deferral notice (29 Jan 2026): https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/deferral-public-consultation-guideline-b-15-disclosure-expectation-financed-emissions-related
- [S18] CTV, Four of Canada's biggest banks leave climate alliance (Jan 2025): https://www.ctvnews.ca/business/article/four-of-canadas-biggest-banks-leave-climate-alliance/
- [S19] ARC Energy Research Institute podcast, ClearBlue Markets' Michael Berends: https://www.arcenergyinstitute.com/carbon-markets-in-uncertain-times-insights-from-michael-berends-at-clearblue-markets/
- [S20] EY Canada, 2025 Global Climate Action Barometer – Canadian insights: https://www.ey.com/en_ca/insights/climate-change-sustainability-services/2025-ey-global-climate-action-barometer-shows-canadian-companies-lagging-on-climate-action
- [S21] CDP, Businesses disclosing transition plans jumps nearly 50% (2024): https://www.cdp.net/press-releases/15c-still-the-goal-businesses-disclosing-climate-transition-plans-jumps-nearly-50
- [S22] Verdantix, 2025 Global Corporate Survey takeaways (19 Sep 2025): https://www.verdantix.com/client-portal/blog/operationalizing-decarbonization--key-takeaways-from-the-2025-global-corporate-survey
- [S23] Deloitte, CFO survey on decarbonization strategy: https://www2.deloitte.com/us/en/insights/industry/dcom/cfo-survey-decarbonization-strategy.html
- [S24] Verco, The decarbonisation capex gap (30 Sep 2025): https://www.vercoglobal.com/latest/the-decarbonisation-capex-gap
- [S25] Plant Services, Energy projects are different: https://www.plantservices.com/energy/energy-management/article/11343635/energy-energy-projects-are-different-plant-services
- [S26] NUS ESI, Corporate internal carbon pricing: global trends and challenges: https://esi.nus.edu.sg/docs/default-source/esi-policy-briefs/corporate-internal-carbon-pricing_global-trends-and-challenges.pdf ; CDP ICP insight: https://www.cdp.net/insights/nearly-half-of-worlds-biggest-companies-factoring-cost-of-carbon-into-business-plans
- [S27] Trinks et al. (2022), External carbon costs and internal carbon pricing, RSER: https://research-repository.st-andrews.ac.uk/handle/10023/25934
- [S29] WBCSD, Weaving climate considerations into corporate operations: https://www.wbcsd.org/news/weaving-climate-considerations-into-corporate-operations/
- [S30] ConocoPhillips, Creating a pipeline of GHG reduction projects: https://conocophillips.com/sustainability/sustainability-news/story/creating-a-pipeline-of-ghg-reduction-projects
- [S31] SINAI, Plan cost-effective decarbonization with MACC: https://www.sinai.com/post/plan-cost-effective-decarbonization-with-macc
- [S33] Facilities Dive on REALPAC/CAGBC/PLACE report (Dec 2024): https://www.facilitiesdive.com/news/canadian-buildings-lack-a-strong-business-case-for-decarbonization-report/735259/ ; CAGBC report page: https://cagbc.org/news-resources/research-and-reports/decarbonizing-canadas-commercial-buildings
- [S35] City of Toronto / Green Will, Making the Case for Energy Management and Decarbonization Projects: https://www.toronto.ca/wp-content/uploads/2025/05/8dc9-Making-the-Case-for-Energy-Management-and-Decarbonization-Projects-Cheat-Sheet.pdf
- [S36] TBS, Greening Government Strategy: https://www.canada.ca/en/treasury-board-secretariat/services/innovation/greening-government/strategy.html
- [S37] CanadaBuys, Appendix L – GHG LCCA guidance: https://canadabuys.canada.ca/sites/default/files/webform/tender_notice/7875/appendix-l_ghg-lcca.pdf
- [S38] FCM GMF, CBR GHG reduction pathway feasibility study guidance: https://greenmunicipalfund.ca/sites/default/files/2022-02/cbr-ghg-reduction-pathway-feasibility-study-guidance-gmf.pdf
- [S39] Ontario Data Catalogue, BPS energy use and GHG emissions: https://data.ontario.ca/dataset/energy-use-and-greenhouse-gas-emissions-for-the-broader-public-sector
- [S40] Environment Journal, CIB commits up to $100M to Ameresco retrofits: https://environmentjournal.ca/cib-commits-to-fund-up-to-100m-in-ameresco-building-retrofits
- [S41] Save on Energy, Energy & climate planning incentive programs presentation: https://saveonenergy.ca/-/media/Files/SaveOnEnergy/training-and-support/cp/energy-and-climate-planning-incentive-programs-presentation.pdf
- [S42] Innovate BC, Audette profile: https://www.innovatebc.ca/blog/audette-is-powering-a-zero-carbon-economy
- [S43] BetaKit, Audette raises $12.8M: https://betakit.com/audette-raises-12-8-million-cad-to-level-up-decarbonization-of-buildings/
- [S44] SustainableBiz, KingSett releases decarbonization tool: https://alpha.sustainablebiz.ca/kingsett-releases-decarbonization-tool-for-buildings
- [S45] SustainableBiz, Canadian GRESB 2025 participation dips: https://sustainablebiz.ca/canadian-firms-improve-gresb-scores-2025-participation-dips
- [S47] Vendr, Watershed pricing: https://www.vendr.com/marketplace/watershed ; ERP Research, Sweep pricing: https://www.erpresearch.com/erp-add-ons/esg-sustainability/sweep/pricing
- [S48] CCLI submission, pre-budget consultations 2026: https://ccli.ubc.ca/wp-content/uploads/2026/03/CCLI_Submission_House-of-Commons-Finance-Committee_Pre-Budget-Consultations-2026-Federal-Budget.pdf
- [S49] PRI blog, Canada's budget sent a clear signal to investors: https://public.unpri.org/pri-blog/canadas-budget-sent-a-clear-signal-to-investors-now-carney-must-strengthen-the-foundations/13553.article
- [S50] CPA Ontario, Canada's Climate Competitiveness Strategy: https://www.cpaontario.ca/insights/blog/canada-climate-competitiveness-strategy
- [S51] MLT Aikins, Bill C-15 narrows anti-greenwashing provisions: https://www.mltaikins.com/insights/federal-government-narrows-scope-of-the-competition-acts-anti-greenwashing-provisions-as-bill-c-15-receives-royal-assent/ ; Gowling, Budget 2025 greenwashing: https://gowlingwlg.com/insights-resources/articles/2025/federal-government-reverses-course-on-greenwashing-rules-in-budget-2025
- [S52] Hospital News, Preparing Canada's health care buildings for net-zero: https://www.hospitalnews.com/preparing-canadas-health-care-buildings-for-net-zero-a-critical-step-toward-sustainable-health-care/
- [S53] ESG Today, Scotiabank and RBC drop financed emissions goals (Apr 2026): https://www.esgtoday.com/scotiabank-rbc-drop-financed-emissions-goals/ ; Advisor.ca, RBC scraps sustainable finance commitment: https://www.advisor.ca/news/rbc-scraps-sustainable-finance-commitment
- [S54] City of Vancouver, 2025 Energize Vancouver annual report: https://vancouver.ca/files/cov/2025-energize-vancouver-annual-report.pdf
- [S55] City of Montréal, Roadmap to zero-emission buildings by 2040: https://montreal.ca/en/articles/roadmap-to-zero-emission-buildings-2040-39260
- [S56] Efficiency Canada, Toronto moving ahead on BPS: https://www.efficiencycanada.org/toronto-moving-ahead-on-building-performance-standards-what-you-need-to-know/
- [S57] City of Toronto, Emissions performance standards page: https://www.toronto.ca/services-payments/water-environment/net-zero-homes-buildings/emissions-performance-standards/ ; communication on IE26.3 (2 Dec 2025): https://www.toronto.ca/legdocs/mmis/2025/ie/comm/communicationfile-199340.pdf
- [S58] REMI Network, Toronto BEPS (~40,000 buildings): https://reminetwork.com/?p=41791
- [S59] Kirkland & Ellis, OBBBA changes to energy tax credits (Aug 2025): https://www.kirkland.com/publications/kirkland-alert/2025/08/one-big-beautiful-bill-act-brings-big-changes-to-green-energy-tax-credits
- [S60] Latitude Media, Industrial decarbonization investments are struggling (Nov 2025): https://www.latitudemedia.com/news/industrial-decarbonization-investments-are-struggling/
- [S61] Environmental Finance, A labelled loan market in transition? (Sep 2025): https://www.environmental-finance.com/content/market-insight/a-labelled-loan-market-in-transition.html
- [S62] ECCC, Facility GHG reporting: overview of 2023 reported emissions: https://www.canada.ca/en/environment-climate-change/services/climate-change/greenhouse-gas-emissions/facility-reporting/overview-2023.html
- [S63] IETA Business Brief – Ontario EPS (Sep 2025): https://www.ieta.org/uploads/wp-content/2025/09/IETA-Business-brief-Ontario-EPS-Sept_2025.pdf
- [S64] IETA Business Brief – BC (Sep 2025): https://www.ieta.org/uploads/wp-content/2025/09/IETA-Business-brief-BC_Sept2025.pdf
- [S65] ICAP, BC OBPS factsheet: https://icapcarbonaction.com/en/ets-pdf-download/70
- [S66] Office of the Auditor General / CESD, Net Zero Accelerator audit (Apr 2024): https://www.canada.ca/content/canadasite/en/auditor-general/media-room/funding-offered-under-net-zero-accelerator-initiative-failing-to-attract-largest-emitters.html
- [S67] Mining Weekly, Oil producers target late 2027 for Pathways decision (19 Aug 2026): https://www.miningweekly.com/article/canadas-oil-producers-target-late-2027-for-pathways-carbon-capture-decision-2026-08-19
- [S68] SustainableBiz, SME hurdles in green manufacturing (EMC 2024 report): https://sustainablebiz.ca/small-medium-canada-business-hurdles-green-manufacturing-cleantech
- [S69] Design Engineering, CME survey on net-zero support: https://www.design-engineering.com/canadian-manufacturers-call-for-greater-support-in-transition-to-net-zero-1004038842/
- [S70] ICLEI Canada, PCP program (555+ municipalities): https://icleicanada.org/?p=64305
- [S71] OSFI by the Numbers 2024-25: https://www.osfi-bsif.gc.ca/en/about-osfi/reports-publications/osfi-annual-report-2024-2025-1/osfi-numbers-2024-25
- [S72] Environment Journal, Closing the cleantech financing gap (20 Jul 2026; CRA data to 31 Mar 2026): https://environmentjournal.ca/market-watch-closing-the-cleantech-financing-gap-for-canadian-companies/
- [S73] REMI Network, CRA to speed up delivery of clean tech rebates: https://www.reminetwork.com/?p=46764
- [S74] BNN Bloomberg, Canadian firms are delaying climate investments (Clean Prosperity, 22 Feb 2024): https://ampvideo.bnnbloomberg.ca/canadian-firms-are-delaying-climate-investments-trudeau-is-warned-1.2037884
- [S75] Canadian Climate Institute, Freezing Alberta's industrial carbon price (12 May 2025): https://climateinstitute.ca/news/freezing-albertas-industrial-carbon-price-will-undermine-investment-and-certainty-for-business/
- [S76] Canadian Climate Institute, Industrial carbon pricing fact sheet (Mar 2025): https://climateinstitute.ca/wp-content/uploads/2025/03/Fact-Sheet-Industrial-Carbon-Pricing.pdf
- [S77] Carbon Pulse, Canada's CCS buildout stalls (28 Nov 2025): https://carbon-pulse.com/462969/
- [S78] PBO, Long-term fiscal cost of major economic ITCs: https://pbo-dpb.ca/en/publications/RP-2425-011-S--long-term-fiscal-cost-major-economic-investment-tax-credits--couts-financiers-long-terme-grands-credits-impot-investissement-economique
- [S79] RBC, Overheard: what Canadian leaders told us about climate (Mar 2025): https://www.rbc.com/en/wp-content/uploads/sites/4/2025/03/Overheard-What-Canadian-leaders-told-us-about-climate-in-the-year-ahead.pdf
- [S80] IESO, PY2023 Retrofit Program Evaluation Report: https://www.ieso.ca/-/media/Files/IESO/Document-Library/conservation/EMV/2023/PY2023_2021-2024-CDM-Framework_Retrofit-Program_Evaluation-Report.pdf
- [S81] hellodarwin platform: https://hellodarwin.com/blog/hellodarwin-platform ; Leyton, Clean economy ITCs: https://leyton.com/ca/clean-economy-investment-tax-credits/
- [S82] Efficiency Canada, Energy Efficiency Policy Database: https://database.efficiencycanada.org/
- [S83] Arbor, OSFI B-15 guide: https://www.arbor.eco/blog/what-is-canadas-osfi-climate-risk-management-guideline-b-15 ; Manifest Climate Series A: https://betakit.com/with-series-a-funding-manifest-climate-can-scale-approach-to-helping-companies-see-climate-change-as-a-strategic-issue
