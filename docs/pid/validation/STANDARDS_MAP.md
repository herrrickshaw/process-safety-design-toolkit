# Standards map: DNV, IOGP, API and closely related documents against the nine P&ID sets

Screening aid, not certified design. Written 2026-11-11 for branch feature/source-term-rainout-pool. No text of any licensed standard is reproduced; values are short cited facts.

## Method and limits

- Read here (grade A): PGS 3 Purple Book, PGS 2 Yellow Book, four sections of 49 CFR Part 193 (eCFR). Downloaded into /private/tmp/claude-501/val_standards/open and /ecfr; text via pdftotext -layout.
- Recorded in `docs/SOURCE_TERM_SOURCES.md` as read from owner copies (not re-read here, so not re-graded): IOGP 434-01, 434-06, API 2510 (8th ed. via 49 CFR copy), API 520 Part I, DNV JFSH validation tables.
- IOGP: every download page I opened asks for name, email and company. I did not submit it. Pages give title, number and free status only.
- DNV: standards need a subscription; Phast technical documents sit behind the customer portal sign-in. Not accessed.
- API: api.org product URLs tried returned 404 or the IBR reading-room error page, so API editions below are marked unverified. Titles are the commonly used names, not confirmed at the publisher page. Contents of every API standard are therefore NOT stated here; the 'what it would check' column is scope-level only.
- Wall hit: IOGP name/email form (all 434 series pages), DNV portal sign-in, API reading-room registration. Items behind them are 'not read'.

## (a) Per-process tables

### LPG propane/n-butane bullet (sheets 3 to 6)

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| PGS 3 (CPR 18E) Guidelines for quantitative risk assessment, 'Purple Book' | Dutch ministry (VROM), publicatiereeksgevaarlijkestoffen.nl | 1999 first edition (PDF states later PGS 3 issue unchanged); file PGS3-1999-v0.1 | free PDF | Vessel LOC frequencies, direct ignition, P(BLEVE), 1.21 x set failure pressure, flash fire/VCE split (tested below) | yes, grade A (read here) |
| PGS 2 (CPR 14E) Methods for the calculation of physical effects, 'Yellow Book' | Dutch ministry (VROM) / TNO | file PGS2-1997-v0.1 (edition number not checked) | free PDF | Fireball radius, duration, radiated fraction, centre height (tested below) | yes, grade A (read here) |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Hole-class leak frequency for 150 mm line and vessel nozzle (sheet 4 basis 3.25e-4 /yr) | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | UKOOA/EI ignition curves behind the 1.9e-6 and 3.1e-6 jet-fire rows | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-03 Risk assessment data directory - Storage incident frequencies | IOGP | not captured | free PDF behind name/email/company form (registration) - not submitted (listed 'Download') | Storage incident frequencies, an independent cross-check on the vessel rows | no |
| IOGP Report 434-14 Risk Assessment Data Directory - Vulnerability of Humans | IOGP | not captured | listed 'Get it now' on the IOGP shop; form not checked | Vulnerability of humans: thermal dose criteria used for the 1 % and 50 % reach figures | no |
| IOGP Risk assessment data directory - Consequence modelling (report number not captured) | IOGP | not captured | listed on shop (GBP 0.00, 'Get it now') | Consequence-modelling data sheet: cross-check of jet and fireball modelling choices | no |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire-case vapour area (sheet 5: 1,227 / 2,414 mm2, Z, Kd 0.975) | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire heat input Q = 43,200 F A^0.82, F factors, jet-fire guidance, depressuring | no (ledger: no technical content read) |
| API Standard 526 Flanged steel pressure-relief valves (orifice letters) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Orifice letters L and N | no |
| API Standard 2510 Design and construction of LPG installations | API | 8th ed., May 2001 (ledger copy via 49 CFR 195.205); current edition unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Spacing, fire protection, high-level cutoff, thermal relief (ledger-read) | ledger: yes grade A from the 49 CFR copy; not re-read here |
| API Standard 2510A Fire-protection considerations for LPG storage facilities | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire-protection practice for LPG storage (water spray vs jet fire) | no |
| API RP 2218 Fireproofing practices in petroleum and petrochemical processing plants | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | PFP rating and the F = 0.3 placeholder | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Area classification around the bullet and PSV vent | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of occupied buildings against the 250 m / 490 m BLEVE reach | no |
| NFPA 58 Liquefied petroleum gas code | NFPA | unverified | not checked | Spacing and installation rules for LPG vessels | no |
| OISD-STD-144 LPG installations; OISD-STD-118 layouts (India) | OISD | unverified | not checked | Indian LPG layout and spacing rules | no |
| DNV Phast/Safeti technical documentation (theory and validation PDFs: discharge, UDM dispersion, JFSH jet fire, BLEVE) | DNV | versioned with software | customer portal sign-in (mysoftware.dnv.com knowledge centre) | JFSH jet-fire and two-phase source diameter (used via ledger) | ledger: JFSH eq 58 and Validation Table 13 used from an owner-supplied copy; not re-read here |

### Grain ethanol 100 KLPD

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| NFPA 30 Flammable and combustible liquids code | NFPA | unverified | not checked | Class IB liquid tank farm, bunds, spacing | no |
| API Standard 2000 Venting atmospheric and low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Day/product tank venting and vacuum relief | no |
| API Standard 2350 Overfill protection for storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | High-high level trip on T-101 (sheet text: LIC-401 to ESD-1) | no |
| API Standard 650 Welded tanks for oil storage | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Atmospheric tank design | no |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire-case relief for columns and vessels | no (ledger: no technical content read) |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Column and vessel PSV sizing | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 526 Flanged steel pressure-relief valves (orifice letters) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Orifice selection | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Zone classification, tank farm and pumps | no |
| NFPA 68 Explosion protection by deflagration venting (dryer, DDGS) | NFPA | unverified | not checked | Dryer explosion venting (sheet 4 mentions explosion venting) | no |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for pumps, columns, pipework | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition probability of ethanol releases (curves not valid beyond gas/LPG-like fluids, per ledger note) | ledger says yes grade A from owner copy; not re-read here |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Control room and building siting | no |
| API RP 754 Process safety performance indicators (cited by IOGP 456) | API | 3rd ed. Aug 2021 per IOGP page | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Process-safety indicators for the plant | no |
| OISD-STD-144 LPG installations; OISD-STD-118 layouts (India) | OISD | unverified | not checked | Indian petroleum-class storage layout | no |

### CBG 10 TPD

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| DNV guidance on hydrogen consequence and risk modelling with Phast/Safeti (web page plus guidance document) | DNV | not captured | web page free; guidance document download not checked | Not hydrogen; DNV has no biogas-specific document found. Listed to show the gap checked | no |
| NFPA 58 Liquefied petroleum gas code | NFPA | unverified | not checked | Not LPG; compressed gas storage and cascade filling covered by PESO per the DPR, NFPA 58 is not the right code (gap noted) | no |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for compressors, vessels, pipework at 16 bar and 250 bar | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition of a methane release | ledger says yes grade A from owner copy; not re-read here |
| API Standard 618 Reciprocating compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Reciprocating compressors for 250 bar CBG cascade | no |
| API Standard 617 Axial and centrifugal compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Centrifugal compressors for the 5 mbar to 16 bar duty if used | no |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | PSV on the upgrader and storage vessels | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Relief and flaring of off-gas | no (ledger: no technical content read) |
| API Standard 537 Flare details for petroleum, petrochemical and natural gas industries | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare for the CH4-bearing membrane off-gas | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Zone classification around the 4 h gas holder | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of the gas holder and compressor house | no |
| IOGP Report 434-14 Risk Assessment Data Directory - Vulnerability of Humans | IOGP | not captured | listed 'Get it now' on the IOGP shop; form not checked | Toxic H2S and thermal harm criteria for the 2,000 ppmv raw gas | no |

### Biodiesel B100 20 KLPD

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| NFPA 30 Flammable and combustible liquids code | NFPA | unverified | not checked | Methanol (flammable liquid) tank farm and bund (sheet shows bund/sump) | no |
| API Standard 2000 Venting atmospheric and low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Methanol and ester tank venting and N2 blanket | no |
| API Standard 650 Welded tanks for oil storage | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Atmospheric tank design | no |
| API Standard 2350 Overfill protection for storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Overfill protection on methanol and ester tanks | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Zones around methanol handling | no |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Methanol flash vessel and reactor PSV | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire-case relief and vent for methanol vessels | no (ledger: no technical content read) |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for reactors, pumps, pipework | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition probability of methanol/ester releases | ledger says yes grade A from owner copy; not re-read here |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of control room | no |
| OISD-STD-144 LPG installations; OISD-STD-118 layouts (India) | OISD | unverified | not checked | Indian petroleum-class storage layout | no |

### SAF-HEFA 30,000 t/yr feed

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| API RP 941 Steels for hydrogen service at elevated temperatures (Nelson curves) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Hydrotreater (R-201 at 50 bar(a), 300-350 C, hydrogen) metallurgy, Nelson curves | no |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | PSV-201/202/203/205 sizing (sheet says capacity not sized) | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire, cooling-water-loss and power-failure relief loads; EDV depressuring; sheet 4 S4/S5 loads | no (ledger: no technical content read) |
| API Standard 537 Flare details for petroleum, petrochemical and natural gas industries | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare FL-501 sizing, radiation and KOD (sheet says not quantified) | no |
| API Standard 618 Reciprocating compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Recycle/make-up hydrogen compressor K-201 (gamma 1.41, 75 %) | no |
| API Standard 617 Axial and centrifugal compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Recycle compressor alternative | no |
| API Standard 560 Fired heaters for general refinery service | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Stage heaters / fired duty if used | no |
| DNV guidance on hydrogen consequence and risk modelling with Phast/Safeti (web page plus guidance document) | DNV | not captured | web page free; guidance document download not checked | Hydrogen jet fire and release guidance for the high-pressure H2 loop | no |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for hydrogen-service pipework, compressors, reactors | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition probability; note ledger says curves are for hydrocarbons, hydrogen not covered by what was read | ledger says yes grade A from owner copy; not re-read here |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Hydrogen zone classification | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting | no |
| API Standard 2000 Venting atmospheric and low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Product tank venting | no |
| NFPA 30 Flammable and combustible liquids code | NFPA | unverified | not checked | Jet-range product tankage | no |

### Fruit and vegetable processing

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of boiler house and refrigeration machinery room | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Ammonia/refrigerant machinery room classification only if ammonia used (refrigerant not named in source) | no |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | PSV for steam boiler and refrigeration receivers (scope borderline: boiler code governs) | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for pressure equipment if the refrigeration inventory is screened | ledger says yes grade A from owner copy; not re-read here |
| API RP 754 Process safety performance indicators (cited by IOGP 456) | API | 3rd ed. Aug 2021 per IOGP page | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Process-safety indicators | no |

### LNG 2.0 mtpa

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| 49 CFR Part 193 LNG facilities: federal safety standards (sections 193.2057, .2059, .2067, .2181 read) | US Government (eCFR) | eCFR text as of 2025-12-01 | free | Impoundment 110 %, thermal and dispersion exclusion method, wind load (tested below) | yes, grade A for the four sections (read here) |
| NFPA 59A Production, storage and handling of LNG (cited by 49 CFR 193) | NFPA | 2001 edition is the one 49 CFR 193.2057 incorporates | not checked (NFPA offers read-only viewing after registration - not accessed) | Exclusion-zone sections 2.2.3.2 to 2.2.3.4 that 49 CFR 193 incorporates | no |
| EN 1473 Installation and equipment for LNG - onshore design | CEN | unverified | paid | European onshore LNG design, spill design cases and spacing | no |
| API Standard 620 Design and construction of large welded low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | LNG tank design (low-pressure, 1.1 bar(a) TK-501) | no |
| API Standard 625 Tank systems for refrigerated liquefied gas storage | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Refrigerated tank system requirements | no |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare and relief loads, fire case, BDV on K-301, PSV on V-401 | no (ledger: no technical content read) |
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Relief valve sizing | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 537 Flare details for petroleum, petrochemical and natural gas industries | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare FL-601 | no |
| API Standard 617 Axial and centrifugal compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Refrigerant and BOG compressors K-301/K-501 | no |
| API Standard 618 Reciprocating compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | BOG compressor if reciprocating | no |
| API Standard 560 Fired heaters for general refinery service | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Regeneration heater (5.5 MW) if fired | no |
| DNV-RP-G105 Development and operation of liquefied natural gas bunkering facilities (not biogas or hydrogen) | DNV | 2019-09, amended 2021-10 | paid (Rules and Standards Explorer+ subscription per DNV page) | LNG bunkering only; relevant only if the plant loads ships | no: paywalled |
| DNV Phast/Safeti technical documentation (theory and validation PDFs: discharge, UDM dispersion, JFSH jet fire, BLEVE) | DNV | versioned with software | customer portal sign-in (mysoftware.dnv.com knowledge centre) | LNG pool spread, vapour dispersion, fire; models not valid for ignition curves (434-06 note) | ledger: JFSH eq 58 and Validation Table 13 used from an owner-supplied copy; not re-read here |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for cryogenic and refrigerant systems | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ledger note: not valid for LNG or refrigerated condensed gases | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-03 Risk assessment data directory - Storage incident frequencies | IOGP | not captured | free PDF behind name/email/company form (registration) - not submitted (listed 'Download') | Storage incident frequencies | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of control and process buildings | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Zone classification of refrigerant (propane, mixed refrigerant) areas | no |

### Coal-to-urea

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | PSV-101/401/501/601 sizing (sheet marks all A) | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Relief and flare loads, FL-101; sheet says no safety content in repo | no (ledger: no technical content read) |
| API Standard 537 Flare details for petroleum, petrochemical and natural gas industries | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare FL-101 | no |
| API Standard 617 Axial and centrifugal compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Syngas and CO2 compressors | no |
| API Standard 618 Reciprocating compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Synthesis-gas reciprocating compressors | no |
| API RP 941 Steels for hydrogen service at elevated temperatures (Nelson curves) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | High-pressure hydrogen-rich syngas and 450 C, 200 bar ammonia converter metallurgy | no |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequency for 150-200 bar equipment; ammonia and syngas | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition probability of syngas; not an ammonia toxic scenario | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-14 Risk Assessment Data Directory - Vulnerability of Humans | IOGP | not captured | listed 'Get it now' on the IOGP shop; form not checked | Toxic (ammonia, CO, H2S) vulnerability criteria | no |
| DNV Phast/Safeti technical documentation (theory and validation PDFs: discharge, UDM dispersion, JFSH jet fire, BLEVE) | DNV | versioned with software | customer portal sign-in (mysoftware.dnv.com knowledge centre) | Ammonia release, toxic dispersion (capability per DNV FAQ; document not read) | ledger: JFSH eq 58 and Validation Table 13 used from an owner-supplied copy; not re-read here |
| DNV guidance on hydrogen consequence and risk modelling with Phast/Safeti (web page plus guidance document) | DNV | not captured | web page free; guidance document download not checked | Hydrogen-rich gas guidance | no |
| API Standard 2000 Venting atmospheric and low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Atmospheric ammonia storage venting if refrigerated, T-501 | no |
| API Standard 620 Design and construction of large welded low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Refrigerated ammonia tank if low-pressure | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting against toxic release and explosion | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Zone classification | no |
| API Standard 560 Fired heaters for general refinery service | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Reformer/gasifier-side fired items | no |

### Refinery 15 Mt/yr

| standard | publisher | edition | access | what it would check in our set | read? |
|---|---|---|---|---|---|
| API Standard 520 Part I Sizing and selection (relief devices) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Relief sizing across units | ledger: owner scanned copy read, grade A for clauses cited; not re-read here |
| API Standard 520 Part II Installation | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Relief inlet/outlet piping | no |
| API Standard 521 Pressure-relieving and depressuring systems | API | unverified (ledger holds only the 6th-ed product page and a 9th-ed ballot draft) | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fire case, blowdown, depressuring; flare load basis | no (ledger: no technical content read) |
| API Standard 526 Flanged steel pressure-relief valves (orifice letters) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Orifice standardisation | no |
| API Standard 537 Flare details for petroleum, petrochemical and natural gas industries | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Flare design | no |
| API Standard 560 Fired heaters for general refinery service | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Fired heaters (CDU/VDU/coker) | no |
| API RP 941 Steels for hydrogen service at elevated temperatures (Nelson curves) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Hydrotreater, hydrocracker, reformer hydrogen service | no |
| API Standard 617 Axial and centrifugal compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Process compressors | no |
| API Standard 618 Reciprocating compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Make-up hydrogen compressors | no |
| API Standard 672 Packaged integrally geared centrifugal air compressors | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Air compressors | no |
| API Standard 650 Welded tanks for oil storage | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Crude and product tankage | no |
| API Standard 2000 Venting atmospheric and low-pressure storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Tank venting | no |
| API Standard 2350 Overfill protection for storage tanks | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Tank overfill | no |
| API Standard 2510 Design and construction of LPG installations | API | 8th ed., May 2001 (ledger copy via 49 CFR 195.205); current edition unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | LPG spheres/bullets from FCC LPG (17.8 wt% yield) | ledger: yes grade A from the 49 CFR copy; not re-read here |
| API Standard 2510A Fire-protection considerations for LPG storage facilities | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | LPG fire protection | no |
| API RP 505 Classification of locations for electrical installations (Zones 0, 1, 2) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Area classification | no |
| API RP 752 Management of hazards associated with location of process plant permanent buildings | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Siting of buildings | no |
| API RP 14C Safety systems for offshore production platforms (analysis method, often borrowed for onshore SAC tables) | API | unverified | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Safety-system analysis method (offshore origin) | no |
| API RP 754 Process safety performance indicators (cited by IOGP 456) | API | 3rd ed. Aug 2021 per IOGP page | paid (publisher page not verifiable from here: api.org 404, IBR reading room needs registration - not accessed) | Process-safety indicators | no |
| IOGP Report 456 Process safety - recommended practice on key performance indicators (NOT release frequencies) | IOGP | 3rd edition, May 2023, 90 pp (shop page) | free PDF behind name/email/company form (registration) - not submitted | KPI practice for the operating site | no |
| IOGP Report 434-01 Risk assessment data directory - Process release frequencies | IOGP | portal page says 'version 3.0, September 2019'; the project ledger records its owner copy as v1.1 May 2021 (UNRECONCILED) | free PDF behind name/email/company form (registration) - not submitted | Release frequencies for the equipment counts | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-06 Risk assessment data directory - Ignition probabilities | IOGP | owner copy v1.1 May 2021 per ledger; portal page for it says 'Currently unavailable' | free PDF behind name/email/company form (registration) - not submitted | Ignition probabilities | ledger says yes grade A from owner copy; not re-read here |
| IOGP Report 434-03 Risk assessment data directory - Storage incident frequencies | IOGP | not captured | free PDF behind name/email/company form (registration) - not submitted (listed 'Download') | Storage incident frequencies | no |
| IOGP Risk assessment data directory - Riser and pipeline release frequencies (report number not captured) | IOGP | not captured | portal page fetched but gave no document detail; form not checked | Pipeline release frequencies for crude and product lines | no |
| DNV Phast/Safeti technical documentation (theory and validation PDFs: discharge, UDM dispersion, JFSH jet fire, BLEVE) | DNV | versioned with software | customer portal sign-in (mysoftware.dnv.com knowledge centre) | Consequence modelling of releases | ledger: JFSH eq 58 and Validation Table 13 used from an owner-supplied copy; not re-read here |
| NFPA 30 Flammable and combustible liquids code | NFPA | unverified | not checked | Tank-farm spacing | no |
| OISD-STD-144 LPG installations; OISD-STD-118 layouts (India) | OISD | unverified | not checked | Indian refinery layout (OISD-STD-118 family) | no |

Distinct documents mapped across the nine tables: 41. Read here with grade A: 3 (PGS 3, PGS 2, 49 CFR 193 sections). Read per ledger from owner copies: 5 groups (434-01, 434-06, API 2510, API 520-1, DNV JFSH).

Corrections to the brief: IOGP Report 456 is the process-safety KPI practice (3rd ed. May 2023), not process release frequencies (that is 434-01). DNV-RP-G105 is LNG bunkering. I found no IOGP Report 589 on the portal pages I searched; not mapped. No DNV recommended practice for biogas was found.

## (b) Values tested against freely readable standards

| id | process | quantity | ours | standard | source | deviation | verdict |
|---|---|---|---|---|---|---|---|
| C1 | LPG | Pressure-vessel instantaneous LOC frequency | 5e-7 /yr (sheet 6 frequency basis, A10) | 5e-7 /yr (G.1 instantaneous) | PB Table 3.3, PDF p.43 | 0 % | agree |
| C2 | LPG | Pressure-vessel continuous 10 min release | 5e-7 /yr | 5e-7 /yr (G.2) | PB Table 3.3, PDF p.43 | 0 % | agree |
| C3 | LPG | Pressure-vessel 10 mm continuous leak | 1e-5 /yr | 1e-5 /yr (G.3) | PB Table 3.3, PDF p.43 | 0 % | agree |
| C4 | LPG | P(BLEVE | instantaneous release with direct ignition), stationary | 0.7 | 0.7 | PB section 4.x text after Table 4.7, PDF p.76 | 0 % | agree |
| C5 | LPG | Vessel failure pressure for BLEVE | 1.21 x set = 2,086 kPag (2.209 MPa abs) | 1.21 x opening pressure of the relief device | PB PDF p.76 | 0 % | agree |
| C6 | LPG | Mass in BLEVE | 45,490 kg (= whole inventory: 105.1 m3 x 0.85 x 509.3) | whole tank inventory | PB PDF p.76 | 0 % (arithmetic: 105.1 x 0.85 x 509.3 = 45,497 kg, 0.02 % off the sheet) | agree |
| C7 | LPG | Flash fire / explosion split after ignition of a vapour cloud | 0.6 flash fire / 0.4 VCE | 0.6 / 0.4 | PB section 4.8, PDF p.78 | 0 % | agree |
| C8 | LPG | Multi-energy blast class and obstructed fraction | class 10; fobstr 0.08 | class 10 (highest); fobstr default 0.08 | PB section 4.8, PDF p.78 | 0 % | agree |
| C9 | LPG | Fireball radius, 45,490 kg | 105.8 m (sheet 6) | 3.24 x m^0.325 = 105.77 m (my calculation from the book's constants) | YB eq 6.90, PDF p.642 | +0.03 % | agree |
| C10 | LPG | Fireball duration | 13.85 s | 0.852 x m^0.26 = 13.85 s | YB eq 6.91, PDF p.642 | 0.0 % | agree |
| C11 | LPG | Fireball centre height | 211.5 m | 2 x r = 211.5 m | YB eq 6.22, PDF p.594 | 0.0 % | agree |
| C12 | LPG | Radiated fraction Fs at 2.209 MPa | 0.348 | 0.00325 x P^0.32 = 0.3484 | YB eq 6.21, PDF p.589 | 0.0 % | agree |
| C13 | LPG | Direct ignition probability, propane/butane jet <10 kg/s (2.34 kg/s case) | jet-fire rows imply 1.9e-6/3.25e-4 = 0.006 (UKOOA large), 3.1e-6/3.25e-4 = 0.010 (small), 2.3e-5/3.25e-4 = 0.071 (Cox); butane 0.003 / 0.003 / 0.071 (ratios are my inference from sheet 4) | 0.2 (gas, average/high reactivity; propane and butane are listed 'average' in Table 4.7) | PB Tables 4.5 and 4.7, PDF p.75 | Purple Book is 3x (Cox) to 20-80x (UKOOA) higher; not a transcription error: different ignition models | DISAGREE (model choice, 80x spread); see section (d) |
| C14 | LPG | Pipe leak frequency, 150 mm supply line, 200 m | 3.25e-4 /yr (IOGP 434-01, hole class 10-50 mm) | 2e-6 /m/yr leak (DN 75-150) x 200 m = 4.0e-4 /yr | PB Table 3.7, PDF p.47 | -19 % | agree (same order; definitions differ: PB leak = 10 mm effective) |
| C15 | LPG | Pipe full-bore rupture frequency, same line | not shown on sheet 4 (title says 'supply-line break') | 3e-7 /m/yr x 200 m = 6.0e-5 /yr | PB Table 3.7, PDF p.47 | n/a | GAP: break frequency not stated |
| C16 | LNG | Impoundment volume, single tank | 70,209.6 m3 = 1.10 x 63,826.9 m3 | 110 % of the tank's maximum liquid capacity (100 % if dike designed for surge) | 49 CFR 193.2181(a),(c) | 0.0 % | agree (US rule; applicability to India not assessed) |
| C17 | LNG | Thermal radiation / dispersion exclusion basis | no exclusion-zone distance or dispersion criterion on the LNG sheets (grep of generator found none) | method fixed by rule: LNGFIRE3 for radiation; 2.5 % average gas concentration with DEGADIS 2.1 or alternate validated model for dispersion | 49 CFR 193.2057, 193.2059(b)(1) | n/a | GAP |
| C18 | LNG | Design wind load | not stated | 150 mph sustained unless justified (or 0.5 % in 50 yr) | 49 CFR 193.2067(b)(2) | n/a | not tested |

Tally: 18 rows; 14 agree (C1-C12, C14, C16), 1 disagree (C13), 2 gaps (C15, C17), 1 not tested (C18). Agreement on C9-C12 shows the workbook uses the Yellow Book constants; it is not independent validation of fireball physics. Yellow Book worked example (8,996 kg propane, 19 bar) gives 62.5 m and 9.09 s; my calculation with the same equations gives 62.46 m and 9.09 s (PGS 2 PDF p.811).

## (c) Standards to obtain for the real design (ranked)

1. API 520 Part I and II, API 521, API 526: every relief load and orifice in all nine sets is A or not sized; sheet 5 says API area is not proof of protection and Z is provisional. Only 520-1 has been read (owner copy).
2. IOGP 434-01 and 434-06 (current editions), plus 434-03 and 434-14: release and ignition bases for LPG, refinery, SAF. Obtain via the IOGP form by the owner; reconcile the version conflict (v1.1 May 2021 in ledger vs v3.0 Sep 2019 on portal).
3. API 2510 (current edition), 2510A, NFPA 58, OISD-STD-144/118: LPG spacing, PFP, water spray, thermal relief: sheet 5 and 6 rely on these and the 250 m / 490 m BLEVE reach exceeds any table spacing.
4. API 537 and 521 flare sections: flare capacity, radiation and KOD are 'not quantified' on SAF, urea, LNG and refinery sheets.
5. API 941, 617, 618: hydrogen-service metallurgy and compressors for SAF, urea and refinery.
6. API 650, 620, 625, 2000, 2350, NFPA 30: tankage for ethanol, biodiesel, SAF products, ammonia and LNG; overfill trips are drawn but unsized.
7. EN 1473 and NFPA 59A (2001 edition cited by 49 CFR 193): LNG exclusion zones and spill design cases: none on the LNG sheets.
8. API RP 505 and RP 752: zone classification and building siting for every set.
9. DNV Phast technical documents and hydrogen guidance (via DNV portal): discharge, dispersion and hydrogen jet fire validation; DNV-RP-F123 only if hydrogen pipelines are in scope.
10. IOGP 456 and API RP 754: operating-phase KPIs; not a design check.

## (d) Contradictions and open points against standards I could read

1. **Ignition probability (C13).** Purple Book Table 4.5 gives 0.2 for a propane or butane release below 10 kg/s; sheet 4 jet-fire rows imply 0.003 to 0.07. A Dutch-style QRA would therefore give jet-fire frequencies 3x to 80x higher than sheet 4. Sheet 4 should show both bases, or state why the UKOOA curves (offshore data, per ledger) suit an Indian onshore site.
2. **Sheet 4 title says 'supply-line break' but the frequency basis lists only the 10-50 mm leak class (C15).** Purple Book full-bore rupture for 200 m of DN 150 is 6.0e-5 /yr, about one fifth of the leak frequency; it belongs on the sheet.
3. **Sheet 6 citation wording.** 'Purple Book frequencies 5e-7, 5e-7 and 1e-5 per year (Tables 3.3, 4.5)': the three frequencies are all in Table 3.3; Table 4.5 holds direct-ignition probability (0.7 for a propane release above 10,000 kg). The sheet does not show the product 5e-7 x 0.7 (ignition) x 0.7 (BLEVE) = 2.5e-7 /yr that a Purple Book chain would use; check which is intended. This is a wording and chain question, not a numeric error.
4. **Both 1.21 x set and P(BLEVE)=0.7 are Purple Book conventions**, not physics. Sheet 5 itself says HSL trials failed API-sized relief under jet impingement; sheet 6 should say the 1.21 factor is a convention.
5. **LNG sheets have no thermal or dispersion exclusion zone (C17).** Method is fixed by 49 CFR 193.2057/2059 for US plants; the set only sizes impoundment (agrees, C16).
6. **Version conflict** on IOGP 434-01 (v1.1 May 2021 in ledger vs v3.0 Sep 2019 on portal): the toolkit's oracle tables may be a different edition than the one currently published.
7. Nothing I could read contradicts a sheet value outright. Most sheet values (relief, flare, hydrogen, ammonia, tank) have no freely readable standard to test against.

## Not tested

Sheet 3 jet-fire flame lengths, 35 kW/m2 reach of 251.6 m and 490 m lethality reach (YB equations not extracted); fire-case relief constants; all hydrogen, biogas, ammonia and tank-fire values.
