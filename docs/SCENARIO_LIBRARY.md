# Scenario library (qualitative toolkit)

Generated from `process_safety/data/scenario_library.json` (compiled 2026-11-07). 19 scenario families.
Regenerate: `python -c "from process_safety import scenario_library as s; print(s.markdown())" > docs/SCENARIO_LIBRARY.md`.

Qualitative scenario library. grade: read = source text read; search-summary = search-engine summary only; generic = standard hazard vocabulary with no specific source; none = no source read, fields left blank. Prompts are prompts, not requirements.

| Scenario | Family | Status | Grade | Quantified by | Main gaps |
|---|---|---|---|---|---|
| `biogas-cbg` Biogas and compressed-biogas (CBG) plant | bioenergy | partial | search-summary | dispersion, dense_gas, flammability, atex, jet_flame, fireball | No biogas-specific frequencies or digester model; Pressurised biomethane storage and compression barely covered by the sources found; Figures in the sources not verified from full text |
| `dust-explosion` Combustible dust explosion and venting | process-hazard | partial | search-summary | atex, dust_explosion | Vent-area sizing (NFPA 68, EN 14491) not implemented: standards paywalled and not read; NFPA 660 (2025) merges six legacy dust codes; mapping not done |
| `ammonia-bunkering` Ammonia fuel bunkering release | marine-energy | partial | search-summary | expansion, dense_gas, dispersion, consequence, qra | Aerosol and rainout are inputs, not predicted; dense_gas covers only low target concentrations and the EPA text says Britter-McQuaid is less justified for ammonia; Figures not verified from full text |
| `saf-hefa` Sustainable aviation fuel (HEFA and co-processing) plant | bioenergy | planned | search-summary | thermal_runaway, reaction_hazard, relief, fg_mapping, flammability | No incident reports found; Alcohol-to-jet and ethanol-plant hazards not covered by the sources found; Vendor and trade material only |
| `bess-thermal-runaway` Battery energy storage thermal runaway and enclosure explosion | bioenergy-adjacent | partial | search-summary | enclosure_ventilation, thermal_runaway, atex, flammability | Vent-gas source term must come from test data (not coded); Enclosure explosion pressure and vent sizing not implemented; Limit fraction is an input; the 25 percent figure is secondary-source only |
| `co2-dense-phase-pipeline` Dense-phase CO2 pipeline rupture | ccs | planned | search-summary | pipeline, dense_gas | Existing gas-pipeline fracture-control methods do not apply to dense-phase CO2; Needs a real-fluid equation of state; not implemented; Hazard distances not covered by the sources found |
| `lng-rollover-rpt` LNG rollover and rapid phase transition | lng | planned | search-summary | lng, relief | No stratification or rollover model; At least 24 rollover incidents since 1960 per one review (count not verified) |
| `flashing-release` Flashing liquefied-gas release (LPG, ammonia) | process-hazard | partial | read | expansion, twophase, release, dense_gas, jet_flame | Rainout and droplet size are inputs; No two-phase jet-flame correlations; Not wired into the QRA consequence step |
| `jet-fire` Jet fire and flame impingement on metal | process-hazard | partial | read | jet_flame, expansion, viewfactor, structural_fire, vapour_fire, flare, depressuring | Vapour Chamberlain only, not validated; Fire-temperature steel properties are recalled until EN 1993-1-2 is read |
| `dense-gas-dispersion` Dense-gas cloud dispersion | process-hazard | partial | read | dense_gas, dispersion, expansion | Far-field fit only; no flammable-limit distances; Aerosol correction not implemented; HSE CRR 17/1988 original not read (copy blocked) |
| `hydrogen-release` Hydrogen release, jet flame and enclosure accumulation | energy | blocked | search-summary | enclosure_ventilation | HyRAM+ (GPL-3.0) is the open tool; not copied, use as an external check; DNV Miller low-luminosity model not implemented; Sandia compatibility reference not read for thresholds |
| `cryogenic-spill-on-steel` Cryogenic spill on carbon steel | lng | planned | read | lng, props | NIST fits cover 304 stainless; no carbon-steel page; nickel-steel pages unreliable; No internationally standardised brittle-fracture hazard area method |
| `vce-multi-energy` Vapour cloud explosion, multi-energy method | process-hazard | blocked | search-summary | explosion | Blast curves are in the TNO Yellow Book; no open copy found; Only TNT equivalence implemented |
| `bleve` BLEVE: blast and fragments | process-hazard | partial | generic | fireball, vapour_fire, relief | Radiation only; no blast or fragment model |
| `boilover-slopover` Boilover and slopover in hydrocarbon tanks | storage | planned | none | - | No source read yet; hazards, events and barriers left blank rather than guessed |
| `domino-escalation` Domino escalation between units | process-hazard | planned | none | qra, viewfactor | No source read yet; escalation thresholds not coded |
| `layout-distances` Layout and separation distances | layout | blocked | none | - | OISD-STD-118: only unofficial copies marked for restricted circulation found, so no distances are shipped; a checker would take your distances as inputs |
| `hazardous-area-extents` Hazardous-area classification extents | layout | blocked | none | atex, flammability | IEC 60079-10-1 and EI 15 paywalled; only the duration rule is coded |
| `runaway-reaction-relief` Runaway reaction and two-phase relief (DIERS) | process-hazard | partial | generic | twophase, thermal_runaway, reaction_hazard, relief | Omega method coded; runaway vent-sizing methods not implemented and no open source read |

## Biogas and compressed-biogas (CBG) plant (`biogas-cbg`)

Status **partial**, grade **search-summary**.

**Hazards**
* methane fire and explosion
* hydrogen sulphide toxicity (denser than air, pools in low areas)
* air ingress creating an explosive atmosphere
* gas holder and digester overpressure

**Initiating events**
* pressure build-up in digester or gas containment
* air injection for H2S control
* compressor or upgrading-stage release
* confined-space entry into digesters

**Credible outcomes**
* flash fire
* jet fire
* vapour cloud explosion
* BLEVE (pressurised storage)
* toxic cloud

**Barriers named in the sources**
* sealing against air entry to digester and gasholder
* division into fire sectors (bioreactor and gasholder, consumption, compressor)
* explosion-risk zoning
* gas detection
* forced ventilation before confined-space entry

**HAZID prompts**
* What can introduce air into the digester or gasholder, and what keeps the mixture outside the flammable range?
* Where does H2S collect if the gas escapes, and who can enter that space?
* What is the largest flammable inventory between upgrading and the compressor, and what isolates it?
* How are the fire sectors separated and what is the escalation path between them?

**Gaps**
* No biogas-specific frequencies or digester model
* Pressurised biomethane storage and compression barely covered by the sources found
* Figures in the sources not verified from full text

**Sources** (read: summary)
* [Scarponi et al., biogas plant risk (CET 43)](https://www.aidic.it/cet/15/43/321.pdf) (summary)
* [Trento fault-tree study, fire in the digester](https://iris.unitn.it/handle/11572/153780) (summary)
* [Baker Engineering, safe design of RNG facilities](https://www.gasprocessingnews.com/articles/2022/06/safe-design-and-operation-of-renewable-natural-gas-facilities) (summary)

## Combustible dust explosion and venting (`dust-explosion`)

Status **partial**, grade **search-summary**.

**Hazards**
* deflagration of dust clouds in vessels, silos and filters

**Initiating events**
* dust cloud formation with an ignition source

**Credible outcomes**
* deflagration
* pressure piling
* secondary dust explosion

**Barriers named in the sources**
* explosion venting
* suppression
* isolation
* inerting

**HAZID prompts**
* Which equipment can hold a dust cloud, and which ignition sources are credible there?
* What happens to the explosion path if the vent discharges into an occupied area?

**Gaps**
* Vent-area sizing (NFPA 68, EN 14491) not implemented: standards paywalled and not read
* NFPA 660 (2025) merges six legacy dust codes; mapping not done

**Sources** (read: summary)
* [Explosion panel sizing guide (inputs Kst, Pmax, Pred, Pstat, L/D)](https://powderprocess.net/Safety/Explosion_Panel_Sizing.html) (summary)
* [Archon Blast (commercial, based on NFPA 68 2018)](https://archon-engineering.squarespace.com/software/archon-blast) (summary)

## Ammonia fuel bunkering release (`ammonia-bunkering`)

Status **partial**, grade **search-summary**.

**Hazards**
* toxic ammonia cloud
* flashing and aerosol release

**Initiating events**
* transfer hose or arm rupture
* pipe rupture
* tank-truck or ship-to-ship transfer leak

**Credible outcomes**
* toxic cloud (probit fatality)
* AEGL-1 to AEGL-3 distances

**Barriers named in the sources**
* safety and control zones
* emergency shutdown on transfer
* emergency plans benchmarked to AEGL-3 scenarios

**HAZID prompts**
* What is the largest release between the two emergency shutdown points, and how fast do they close?
* How does ambient temperature change the safety zone (winter zones were larger in one study)?

**Gaps**
* Aerosol and rainout are inputs, not predicted
* dense_gas covers only low target concentrations and the EPA text says Britter-McQuaid is less justified for ammonia
* Figures not verified from full text

**Sources** (read: summary)
* [MDPI Energies 2025, ammonia truck bunkering probit](https://www.mdpi.com/1996-1073/18/19/5099) (summary)
* [PNNL, QRA during truck-to-ship ammonia bunkering](https://fathoms.pnnl.gov/publications/quantitative-risk-analysis-during-truck-ship-ammonia-bunkering) (summary)
* [UK P&I Club, ship-to-ship ammonia transfer trial](https://www.ukpandi.com/news-and-resources/news/article/worlds-first-pilot-trial-of-ship-to-ship-sts-ammonia-transfer/) (summary)

## Sustainable aviation fuel (HEFA and co-processing) plant (`saf-hefa`)

Status **planned**, grade **search-summary**.

**Hazards**
* high-pressure hydrogen reactors
* larger exotherms and water formation at higher renewable feed ratios
* corrosion
* carbon monoxide, nitrogen and carbon dioxide hazards on biomass routes
* seal compatibility (low aromatics)

**Initiating events**
* reactor temperature excursion
* loss of quench or hydrogen supply
* new equipment added to older plant with older detection standards

**Credible outcomes**
* reactor runaway
* hydrogen release fire
* toxic or asphyxiant exposure

**Barriers named in the sources**
* current fire and gas detection standards for new equipment
* reactor protection
* gas detection for CO on biomass routes

**HAZID prompts**
* How does a higher renewable feed ratio change the reactor exotherm margin against the trip and relief basis?
* Does the existing detection and zoning cover the new hydrogen and CO sources?

**Gaps**
* No incident reports found
* Alcohol-to-jet and ethanol-plant hazards not covered by the sources found
* Vendor and trade material only

**Sources** (read: summary)
* [BriSafe, putting the safety in SAF](https://britsafe.org/safety-management/2025/sustainable-aviation-fuels-how-do-we-put-the-safety-in-saf) (summary)
* [Topsoe Q and A on co-processing](https://www.digitalrefining.com/qanda/435) (summary)

## Battery energy storage thermal runaway and enclosure explosion (`bess-thermal-runaway`)

Status **partial**, grade **search-summary**.

**Hazards**
* flammable vent gas (hydrogen) in an enclosure
* thermal runaway propagation

**Initiating events**
* cell thermal runaway
* gas accumulation in a container or battery room

**Credible outcomes**
* enclosure deflagration
* fire

**Barriers named in the sources**
* explosion control required by NFPA 855 for containers of about small ISO size or larger
* NFPA 69 concentration limit via mechanical purge ventilation
* UL 9540A test data as the source term

**HAZID prompts**
* What is the vent-gas rate and composition from the test data, and where does it accumulate?
* What ventilation rate keeps the room below the chosen fraction of the lower flammable limit?

**Gaps**
* Vent-gas source term must come from test data (not coded)
* Enclosure explosion pressure and vent sizing not implemented
* Limit fraction is an input; the 25 percent figure is secondary-source only

**Sources** (read: summary)
* [Jensen Hughes, BESS explosion prevention with CFD](https://www.jensenhughes.com/insights/designing-bess-explosion-prevention-systems-using-cfd-based-methodology) (summary)
* [WVU dissertation on battery enclosure explosions](https://researchrepository.wvu.edu/etd/11874) (summary)

## Dense-phase CO2 pipeline rupture (`co2-dense-phase-pipeline`)

Status **planned**, grade **search-summary**.

**Hazards**
* running ductile and brittle fracture
* solids formation near a dense release
* dense cold cloud

**Initiating events**
* pipeline rupture
* leak transitioning to running fracture

**Credible outcomes**
* decompression wave and fracture propagation
* dense CO2 dispersion

**Barriers named in the sources**
* crack arrestors (toroidal rings studied)
* fracture-control design for dense-phase service

**HAZID prompts**
* Does the decompression wave outrun the crack at the operating pressure and impurity content?

**Gaps**
* Existing gas-pipeline fracture-control methods do not apply to dense-phase CO2
* Needs a real-fluid equation of state; not implemented
* Hazard distances not covered by the sources found

**Sources** (read: summary)
* [UCL, brittle fracture in CO2 pipelines](https://discovery.ucl.ac.uk/id/eprint/10051724/1/Manuscript_01.pdf) (summary)
* [Surrey pipeline safety group](https://www.surrey.ac.uk/fire-and-explosion-modelling-group/pipeline-safety) (summary)

## LNG rollover and rapid phase transition (`lng-rollover-rpt`)

Status **planned**, grade **search-summary**.

**Hazards**
* sudden mixing of stratified layers releasing boil-off vapour
* physical explosion on LNG-water contact

**Initiating events**
* stratification in a tank
* LNG spill onto water

**Credible outcomes**
* tank overpressure
* relief discharge
* RPT overpressure with no combustion

**Barriers named in the sources**
* tank relief capacity sized for rollover
* managing stratification

**HAZID prompts**
* Can the relief system pass the rollover vapour rate if stratification is not managed?

**Gaps**
* No stratification or rollover model
* At least 24 rollover incidents since 1960 per one review (count not verified)

**Sources** (read: summary)
* [Shebeko, rollover and RPT review (Fire and Explosion Safety 2023)](https://www.fire-smi.ru/jour/article/download/1198/732) (summary)

## Flashing liquefied-gas release (LPG, ammonia) (`flashing-release`)

Status **partial**, grade **read**.

**Hazards**
* two-phase jet and aerosol cloud
* rainout and pool formation

**Initiating events**
* hole, rupture or relief discharge from liquefied-gas storage

**Credible outcomes**
* aerosol cloud
* pool fire from rainout
* jet fire
* toxic cloud

**Barriers named in the sources**
* isolation
* blowdown
* bunding for rainout

**HAZID prompts**
* How much of the release is airborne and how much rains out, and what pool does the rainout form?

**Gaps**
* Rainout and droplet size are inputs
* No two-phase jet-flame correlations
* Not wired into the QRA consequence step

**Sources** (read: summary, text)
* [Witlox and Fernandez, ATEX atmospheric expansion (Hazards 26)](https://www.icheme.org/media/11832/hazards-26-paper-04-modelling-and-validation-of-atmospheric-expansion-and-near-field-dispersion-for-pressurised-vapour-or-two-phase-orifice-releases.pdf) (text)
* [HSE RR1189, QUADVENT flashing releases](https://hse.gov.uk/researcH/rrhtm/rr1189.htm) (summary)

## Jet fire and flame impingement on metal (`jet-fire`)

Status **partial**, grade **read**.

**Hazards**
* radiant flux
* flame impingement on vessels and pipes
* vessel failure from heat-up

**Initiating events**
* pressurised vapour release ignited

**Credible outcomes**
* jet fire
* vessel rupture
* escalation

**Barriers named in the sources**
* passive fire protection
* depressuring
* deluge (not reliable over a whole LPG vessel surface per HSE tests)

**HAZID prompts**
* What is the flame length and where does it touch equipment?
* How long to the failure temperature and can depressuring beat it?

**Gaps**
* Vapour Chamberlain only, not validated
* Fire-temperature steel properties are recalled until EN 1993-1-2 is read

**Sources** (read: summary, text)
* [DNV JFSH theory, Jet Fire](https://myworkspace.dnv.com/download/public/phast/technical_documentation/07_fire_models/JFSH%20Jet%20Fire%20Model%20Theory.pdf) (text)
* [HSE RR1187](https://www.hse.gov.uk/Research/rrhtm/rr1187.htm) (summary)

## Dense-gas cloud dispersion (`dense-gas-dispersion`)

Status **partial**, grade **read**.

**Hazards**
* dense cloud slumping and spreading

**Initiating events**
* liquefied or cold dense-gas release

**Credible outcomes**
* toxic cloud
* flash fire
* vapour cloud explosion

**Barriers named in the sources**
* wind and terrain awareness
* detection and shutdown

**HAZID prompts**
* Is the release dense under the actual wind and source conditions (criterion), or passive?

**Gaps**
* Far-field fit only; no flammable-limit distances
* Aerosol correction not implemented
* HSE CRR 17/1988 original not read (copy blocked)

**Sources** (read: text)
* [EPA TSCREEN workbook, section 5.4 (Britter-McQuaid)](https://gaftp.epa.gov/aqmg/SCRAM/models/screening/tscreen/tscrd.pdf) (text)

## Hydrogen release, jet flame and enclosure accumulation (`hydrogen-release`)

Status **blocked**, grade **search-summary**.

**Hazards**
* low-luminosity jet flame
* accumulation in enclosures
* embrittlement of structural materials

**Initiating events**
* leak or rupture from high-pressure hydrogen equipment

**Credible outcomes**
* jet flame
* deflagration in an enclosure

**Barriers named in the sources**
* ventilation
* detection

**HAZID prompts**
* Where can hydrogen accumulate and is the detection placed for a buoyant gas?

**Gaps**
* HyRAM+ (GPL-3.0) is the open tool; not copied, use as an external check
* DNV Miller low-luminosity model not implemented
* Sandia compatibility reference not read for thresholds

**Sources** (read: summary)
* [HyRAM+ (Sandia)](https://github.com/sandialabs/hyram) (summary)
* [Sandia hydrogen compatibility technical reference](https://www.osti.gov/servlets/purl/1055634) (summary)

## Cryogenic spill on carbon steel (`cryogenic-spill-on-steel`)

Status **planned**, grade **read**.

**Hazards**
* brittle fracture from cold spill
* thermal stress

**Initiating events**
* LNG or LN2 spill onto structure

**Credible outcomes**
* fracture from weld flaws
* cascading damage

**Barriers named in the sources**
* spill containment
* low-temperature steels

**HAZID prompts**
* Which structure can a spill reach, and is its steel rated for the spill temperature?

**Gaps**
* NIST fits cover 304 stainless; no carbon-steel page; nickel-steel pages unreliable
* No internationally standardised brittle-fracture hazard area method

**Sources** (read: summary, text)
* [NIST cryogenic 304 stainless page](https://trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm) (text)
* [NTNU, permanent effect of a cryogenic spill on carbon steel](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/2352006) (summary)

## Vapour cloud explosion, multi-energy method (`vce-multi-energy`)

Status **blocked**, grade **search-summary**.

**Hazards**
* blast from a congested or confined flammable cloud

**Initiating events**
* delayed ignition of a flammable cloud

**Credible outcomes**
* blast overpressure

**Barriers named in the sources**
* spacing
* blast-resistant buildings

**HAZID prompts**
* Which parts of the cloud are congested enough to act as separate blast sources?

**Gaps**
* Blast curves are in the TNO Yellow Book; no open copy found
* Only TNT equivalence implemented

**Sources** (read: summary)
* [Chalmers, blast loads from vapour cloud explosions](https://research.chalmers.se/publication/548147) (summary)

## BLEVE: blast and fragments (`bleve`)

Status **partial**, grade **generic**.

**Hazards**
* fireball
* blast
* fragments

**Initiating events**
* fire exposure of a pressurised liquefied-gas vessel

**Credible outcomes**
* fireball
* blast wave
* missiles

**Barriers named in the sources**
* pressure relief with fire protection
* depressuring
* water deluge

**HAZID prompts**
* Can the vessel survive the fire long enough for depressuring to work?

**Gaps**
* Radiation only; no blast or fragment model

## Boilover and slopover in hydrocarbon tanks (`boilover-slopover`)

Status **planned**, grade **none**.

**Credible outcomes**
* tank fire escalation

**HAZID prompts**
* What water can reach a hot-oil layer in a tank fire?

**Gaps**
* No source read yet; hazards, events and barriers left blank rather than guessed

## Domino escalation between units (`domino-escalation`)

Status **planned**, grade **none**.

**Credible outcomes**
* escalation

**HAZID prompts**
* Which units are within the escalation threshold of each credible primary event?

**Gaps**
* No source read yet; escalation thresholds not coded

## Layout and separation distances (`layout-distances`)

Status **blocked**, grade **none**.

**HAZID prompts**
* Do the inter-distances meet the governing standard for each pair of facilities?

**Gaps**
* OISD-STD-118: only unofficial copies marked for restricted circulation found, so no distances are shipped; a checker would take your distances as inputs

## Hazardous-area classification extents (`hazardous-area-extents`)

Status **blocked**, grade **none**.

**HAZID prompts**
* What are the release grade, ventilation and extent for each source?

**Gaps**
* IEC 60079-10-1 and EI 15 paywalled; only the duration rule is coded

## Runaway reaction and two-phase relief (DIERS) (`runaway-reaction-relief`)

Status **partial**, grade **generic**.

**Credible outcomes**
* two-phase relief discharge

**HAZID prompts**
* Is the relief sized for the two-phase runaway flow rather than vapour only?

**Gaps**
* Omega method coded; runaway vent-sizing methods not implemented and no open source read

