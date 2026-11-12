# Safety source register for the coal-to-urea unit P&ID package

Grades: A = primary document or regulation text read; B = primary but secondary type (vendor bulletin, database entry, paper) read; C = snippet or not read in full. Documents were fetched into /private/tmp/claude-501/src_safety/. No licensed standard text used. Values are short paraphrases.

Note: the worktree /private/tmp/claude-501/wt_capacity did not exist when this was written, so the files are in /private/tmp/claude-501/safety_out/; copy to docs/pid/urea_detail/sources/.

Blocked: cdc.gov (NIOSH pocket guide) returned Akamai Access Denied, not bypassed. GESTIS-DUST-EX search form not scriptable. Licensed and not obtained: API 520/521/2000, NFPA 30/68/69/85/8503, IEC 61511, IIAR, ISO 6184.

## Fire relief load (NH3 vessels) [partly]
- Source: 29 CFR 1910.111 Storage and handling of anhydrous ammonia, para (b)(9) Table H-36 (US OSHA (regulation text), current eCFR text, ASME 1968 basis)
- URL: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.111
- Section: (b)(9)(i)-(ii), Table H-36 and note
- Read: Fire relief rate is tabulated as CFM air at 120% of set pressure versus outside surface area; for A above 2500 sq ft use 22.11*A^0.82 SCFM air (13,520 CFM at 2500 sq ft). Set pressure 110-125% of design for ASME U-68/69 containers. Bare-vessel basis, no insulation credit.
- Grade: A
- Package change: Gives a free, citable fire-case relief rate for NH3 storage and ammonia-wetted vessels; replace the 138 'not sized' PSVs for those items with 22.11*A^0.82 and say API 521 wetted-area method was not obtained. Not valid for hot process vessels or two-phase.

## Fire relief load (process vessels) [gap]
- Source: API 520 / API 521 / NFPA 30 (API / NFPA, -)
- URL: -
- Section: -
- Read: Standard not obtained (paywalled). HSE COMAH page only names methods (API, NFPA, DIERS, Leung, Fauske, Huff, Boyle) and says storage worst case is fire exposure.
- Grade: -
- Package change: State 'gap: standard not obtained' for hydrocarbon, syngas and hot-process fire cases.

## Relief design principles / DIERS pointer [partly]
- Source: Relief systems / vent systems (COMAH technical measures) (UK HSE, web page, undated)
- URL: https://www.hse.gov.uk/Comah/sragtech/techmeasventsyst.htm
- Section: General principles; sizing methods list
- Read: Overpressure causes listed: external fire, maloperation, utility failure, ambient change, reaction. Relief device must not be isolable from protected equipment; several tanks on one relief header need the simultaneous load at a pressure below the lowest design pressure. DIERS cited as accepted practice for reactive/two-phase systems. No numbers.
- Grade: B
- Package change: Add the common-header simultaneous-load check and the no-isolation rule to the relief notes; no sizing numbers.

## Blocked outlet relief basis [partly]
- Source: 29 CFR 1910.111 (pumps, compressors, hydrostatic relief) (US OSHA, current text)
- URL: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.111
- Section: (c)-(f) pump, compressor and liquid-line relief paragraphs
- Read: Positive-displacement pump needs a differential relief sized for full pump capacity; compressor discharge relief sized for full compressor capacity ahead of any shut-off; hydrostatic relief between each pair of liquid-NH3 valves.
- Grade: A
- Package change: Blocked-outlet load for NH3 pumps/compressors = rated capacity; add thermal-relief valves on trapped liquid NH3 lines.

## Tube rupture relief [gap]
- Source: API 521 / API 520 tube-rupture guidance (API, -)
- URL: -
- Section: -
- Read: Standard not obtained. No free regulator or DIERS text located; HSE CRR 136/1998 URL returned 404.
- Grade: -
- Package change: Keep tube-rupture case as 'not sized'; gap: standard not obtained.

## Dust explosion inputs: coal [partly]
- Source: Comparison of the explosion characteristics and flame speeds of pulverised coals and biomass in the ISO standard 1 m3 dust explosion equipment, Table 1 (Huescar Medina et al., Fuel 151 (2015) 91-101 (White Rose accepted manuscript, CC BY-NC-ND), 2015)
- URL: https://eprints.whiterose.ac.uk/97723/1/Fuel
- Section: Table 1 and text lines on KSt/Pmax/MEC ranges
- Read: Literature coals: KSt 30-220 bar m/s, Pmax 5-10 bar, MEC 60-120 g/m3. 1 m3 results: Kellingley 80 / 8.2, Colombian 129 / 8.5, brown coal 151 / 10.0, Spanish lignite 107 / 8.8, German lignite 105 / 8.7 (KSt / Pmax). 20 L sphere under-reads Pmax versus 1 m3. All St1.
- Grade: B
- Package change: Screening vent inputs for coal: St1, KSt up to 220 and Pmax 10 bar (upper envelope, tag A) until the real coal is tested; use 1 m3 values, not 20 L Pmax. Vent area equation (EN 14491 / NFPA 68) not obtained.

## Dust explosion inputs: coal (second view) [partly]
- Source: Dust explosibility results table (vendor page) (explosiontesting.co.uk, undated)
- URL: https://explosiontesting.co.uk/explosion_ind_10.html
- Section: results table
- Read: Coal dust 85 bar m/s, 6.4 bar g, St1; wood dust 224 / 10.3 St2. Vendor page, test sample not stated.
- Grade: C
- Package change: Cross-check only.

## Dust explosion inputs: lignite fractions [partly]
- Source: Lignite sieving study (Chemical Engineering Transactions 77 (AIDIC), 2019)
- URL: https://www.aidic.it/cet/19/77/080.pdf
- Section: abstract and results
- Read: KSt and (dP/dt)max rise as particle size falls (read abstract and intro only).
- Grade: B
- Package change: Mill product fineness drives KSt; use the finest cut for vent sizing.

## Dust explosion inputs: petcoke [gap]
- Source: (no free source found) (-, -)
- URL: -
- Section: -
- Read: No measured petroleum-coke KSt/Pmax found in free sources.
- Grade: -
- Package change: Keep petcoke dust data as assumed (use coal envelope) and flag for test.

## Dust explosion inputs: urea [partly]
- Source: Storage, handling and transport of solid fertilizers, sect. 6.3 Urea (Fertilizers Europe, Issue 2015)
- URL: https://www.fertilizerseurope.com/wp-content/uploads/2007/08/Final-version-Storage-handling-and-transport-of-solid-fertilizers-18112015.pdf
- Section: 6.3 Urea
- Read: States urea dust does not give a dust-explosion hazard, citing a private communication from a producer; urea also decomposes above 133 C releasing NH3 and can rupture a confined container. Single secondary claim, not a measured KSt.
- Grade: C
- Package change: Do not delete urea dust protection from granulation/bagging sheets on this basis; treat as unresolved and test or check GESTIS-DUST-EX.

## Dust explosion database [gap]
- Source: GESTIS-DUST-EX (IFA (DGUV), live database)
- URL: https://staubex.ifa.dguv.de/explosuche.aspx?lang=e
- Section: search form
- Read: Site reachable; the search form is an ASP.NET postback and my scripted POST returned a server error. Not read. Needs a manual browser lookup for coal, lignite, petroleum coke, urea.
- Grade: -
- Package change: Manual lookup would close coal/petcoke/urea KSt and Pmax with one source.

## Dust explosion protection principles [partly]
- Source: HSG103 Safe handling of combustible dusts (2nd ed.) (UK HSE, 2003)
- URL: https://www.hse.gov.uk/pubns/priced/hsg103.pdf
- Section: paras 25-29 inerting; 61-62 venting; Appendix A and Table 1
- Read: Vent design needs vessel volume, dust KSt/Pmax from a 20 L or larger apparatus, vessel strength and panel opening pressure; inerting limit must be found experimentally with safety margin and reliable inert gas supply; St classes St1 0-200, St2 200-300, St3 300-600 bar m/s. Table 1 values are not for direct design.
- Grade: A
- Package change: Add dust data sheet requirement (volume, KSt, Pmax, Pstat, Pred) to Area 10 notes.

## Limiting O2 for coal mill / bunker [partly]
- Source: Pulverized Fuel System Fires, Plant Service Bulletin 16 (Babcock & Wilcox, undated bulletin)
- URL: https://www.babcock.com/assets/PDF-Downloads/Plant-Service-Bulletins/Pulverized-Fuel-System-Fires-PSB-16.pdf
- Section: inerting section
- Read: Inerting medium (steam, CO2, N2) must bring O2 to 15 vol% or less to stop a pulverizer fire; water only after inerting to avoid raising dust; do not open a mill with burning contents; mill must cool before opening.
- Grade: B
- Package change: Set mill-circuit inerting trip basis at O2 <=15 vol% (A) with the MAIN low O2 alarm below it; NFPA 69/85/8503 not obtained.

## CO / O2 alarm levels in coal circuit [gap]
- Source: NFPA 85/8503, vendor CO2 bulletins (NFPA / Kidde, -)
- URL: -
- Section: -
- Read: Not obtained: NFPA paywalled; Kidde bulletin URL returned 404. HSG103 only says set oxygen control level with a safety margin.
- Grade: -
- Package change: Keep CO alarm set point as assumed; gap: standard not obtained.

## O2 line velocity [closed]
- Source: EIGA Doc 13/20 Oxygen pipeline and piping systems (EIGA (free download), 2020)
- URL: https://www.eiga.eu/uploads/documents/DOC013.pdf
- Section: 4.4.2-4.4.3, Figures 2-3 equations; Appendix B
- Read: Impingement curve (to 200 C): V=30 m/s for 0.3-1.5 MPa abs; P*V=45 MPa*m/s for 1.5-10 MPa abs; V=4.5 m/s for 10-20 MPa abs. Non-impingement: 60 m/s for 0.3-1.5 MPa; P*V=80 for 1.5-10; 8 m/s for 10-20 MPa. Velocity on minimum flow area, normal operation not relief. Exemption pressures: 304/316 3.18 mm 1.38 MPa, 6.35 mm 2.58 MPa; Monel 400, copper, brass 20.68 MPa; Inconel 625 6.90 MPa. Filtration of particles 150 micron or smaller as a mitigation.
- Grade: A
- Package change: Check every O2 and HP O2 line against these curves (e.g. 4 MPa abs carbon-steel limit 11.3 m/s); specify Monel/copper alloy at impingement points above exemption pressure.

## O2 cleaning [partly]
- Source: EIGA Doc 13/20 (EIGA, 2020)
- URL: https://www.eiga.eu/uploads/documents/DOC013.pdf
- Section: 3.2.5, 4.3.3.3, 6.5
- Read: Dry oil-free air/N2 defined as dew point -40 C or lower and oil 0.5 mg/m3 or less; ultra-high-purity systems NVR 1000 ug/m3 or less; acceptance by white-light grey-metal finish, UVA check of bore and wipes (EIGA Doc 33). Numeric residue limit for ordinary service is not in Doc 13.
- Grade: A
- Package change: Add cleaning note and UVA inspection to ASU O2 sheets; numeric mg/m2 limit remains open (Doc 33 not fetched).

## H2S, NH3, CO exposure limits for detector set points [closed]
- Source: EH40/2005 Workplace exposure limits (4th ed. 2020) (UK HSE, 2020)
- URL: https://www.hse.gov.uk/pubns/priced/eh40.pdf
- Section: Table 1
- Read: Ammonia 25 ppm 8 h, 35 ppm 15 min; hydrogen sulphide 5 ppm 8 h, 10 ppm 15 min; carbon monoxide 20 ppm 8 h, 100 ppm 15 min.
- Grade: A
- Package change: Proposed alarm basis (derived, tag D): low alarm at 8-h WEL, high alarm at 15-min STEL; replace assumed values in AREA notes.

## US limits cross-check [partly]
- Source: OSHA annotated Table Z-1 (US OSHA, current)
- URL: https://www.osha.gov/annotated-pels/table-z-1
- Section: ammonia and carbon monoxide rows
- Read: Ammonia OSHA PEL 50 ppm (NIOSH REL 25 TWA, 35 STEL); CO OSHA PEL 50 ppm (NIOSH ceiling 200, TWA 35). H2S is under Z-2 and was not read.
- Grade: A
- Package change: Cross-check only.

## IDLH values [gap]
- Source: NIOSH Pocket Guide / IDLH (CDC NIOSH, -)
- URL: https://www.cdc.gov/niosh/npg/npgd0028.html
- Section: -
- Read: Blocked: Akamai Access Denied (403) on cdc.gov. Not bypassed. H2S OSHA Z-2 ceiling/peak also not read.
- Grade: -
- Package change: IDLH-based high-high alarm values stay open.

## Refrigerated NH3 tank containment [partly]
- Source: Guidance for inspection of atmospheric refrigerated ammonia storage tanks (2008 ed., issue 2014) (Fertilizers Europe, 2014)
- URL: https://www.fertilizerseurope.com/wp-content/uploads/2019/08/Guidance_for_inspection_of_atmospheric__refrigerated_ammonia_storage_tanksVJ_website.pdf
- Section: sect. 3.2 types; failure modes; commissioning
- Read: Survey of 22 tanks: virtually all have secondary containment, over 80% full-height concrete or steel wall. Listed types: tank with full-height bund holding full contents with impervious floor and roof cover; tank-in-tank; partial bund; earth dyke; single wall. Rollover/mixing of aqueous and anhydrous layers can exceed PSV capacity and lift the shell; preferable weak roof-to-shell weld on new tanks. Commissioning: N2 purge to O2 below 4%, later step below 0.5% before NH3. Detectors test every 6 months, bund visual check yearly.
- Grade: B
- Package change: Bund = 100% of tank contents with impervious floor (document as A); add rollover case and weak roof weld, O2 purge limits, detector proof-test interval to Area 60 storage sheet.

## NH3 water spray / vent scrubbing / bund volume rule [gap]
- Source: (no free source found) (-, -)
- URL: -
- Section: -
- Read: No free regulator text for water-spray density or vent scrubbing located. IIAR / NFPA paywalled.
- Grade: -
- Package change: Keep as open; gap: standard not obtained.

## Fire water demand, foam, detector placement [gap]
- Source: OISD-STD-116 and OISD-STD-117 (OISD (India), -)
- URL: https://www.oisd.gov.in/
- Section: -
- Read: Official PDF not found on the site root; only Scribd copies surfaced (not used). Snippet-level only: flow basis 4 hydrant/foam outlets plus 1 monitor; spray demand governs if higher.
- Grade: C
- Package change: Fire protection concept sheets stay at placeholder; needs official OISD PDF download.

## PSM regulatory frame [closed]
- Source: 29 CFR 1910.119 Process safety management (US OSHA, current)
- URL: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119
- Section: (d)(3)(i)(D), PHA, MI
- Read: Process safety information must include relief system design and design basis; PHA required before start.
- Grade: A
- Package change: Add a relief design-basis register as a named deliverable.

## Urea / carbamate incident: leak [closed]
- Source: Leakage of ammonium carbamate in a urea production plant (accident 29603) (BARPI / ARIA (France), 2005 record)
- URL: https://www.aria.developpement-durable.gouv.fr/accident/29603_en/?lang=en
- Section: summary
- Read: Carbamate leak at the synthesis condenser bypass valve during start-up after 5-week outage; mis-seated carbon-steel screwed flange corroded; about 5 t NH3 equivalent released to 60 m and reached a city; a small leak was noticed 10 h before and left under watch; sewer reconfigured to a retention basin.
- Grade: B
- Package change: Add start-up leak-watch trigger (any carbamate leak = shutdown) and positive material check on bypass valve flanges; carbamate containment to retention.

## Urea / off-gas incident: H2/O2 explosion [closed]
- Source: Explosion in an urea manufactory (HIAD event) (EU Clean Hydrogen Knowledge Hub (HIAD), undated entry)
- URL: https://knowledge.clean-hydrogen.europa.eu/hiad/incidents/explosion-urea-manufactory
- Section: root cause section
- Read: Passivation oxygen plus hydrogen carried in CO2 feed gave a flammable H2/O2 mix in the high-pressure carbamate scrubber after NH3/CO2 were absorbed; probable ignition by oil traces; scrubber was built to withstand internal explosion.
- Grade: B
- Package change: Highest-value finding for a coal CO2 source (H2 in CO2): add H2 analysis and O2 dosing limit on urea reactor off-gas, oil-free scrubber, and note design-to-contain.

## Urea reactor other incidents (Mangalore 2000, Ghorashal 1991) [gap]
- Source: search summaries only (Scribd, conference slides) (-, -)
- URL: -
- Section: -
- Read: Snippets only: weldolet HAZ corrosion at the reactor-stripper carbamate line; stripper failure. Primary reports not fetched.
- Grade: C
- Package change: None until primary reports are fetched.

## Sulphur pit / tank incident [closed]
- Source: Fire in a molten sulfur tank level-gauge chamber (CC1000077) (Association for the Study of Failure (shippai.org), 5 Mar 1991)
- URL: https://www.shippai.org/fkd/en/cfen/CC1000077.html
- Section: whole entry
- Read: Pyrophoric iron sulfide formed in a closed steel chamber (low O2, moisture, H2S in sulfur), ignited on opening, H2S burned and tank was damaged; fix was open-type gauge frame, stainless steel and periodic tank gas analysis.
- Grade: B
- Package change: Add FeS note to sulphur pit/tank: no closed dead-space chambers, stainless for gauge pockets, gas analysis, vent pipes kept open.

## Pyrophoric iron sulfide guidance [partly]
- Source: Pyrophoric materials create fire and explosion hazard (WorkSafeBC, web alert)
- URL: https://www.worksafebc.com/resources/health-safety/hazard-alerts/pyrophoric-materials-fire-explosion-hazard
- Section: alert text
- Read: Explains iron sulfide formation in tanks and prevention of fires on exposure to oxygen (fetched, skimmed only).
- Grade: C
- Package change: Supporting.

## Acid gas / H2S release incident [partly]
- Source: Toxic gas release during maintenance, Deer Park 10 Oct 2024 (IChemE Lessons Learned Database, 2024)
- URL: https://www.icheme.org/media/30060/deer-park-incident-summary-10-oct-24.pdf
- Section: summary
- Read: Contractors opened a flange on a live pressurised acid-gas line instead of the isolated one; 2 fatalities, 13 injuries; lessons on positive line identification and permit-to-work.
- Grade: B
- Package change: Add physical line marking, double isolation and H2S detection at acid-gas flanges on AGR/Claus sheets.

## Claus furnace / waste-heat boiler explosions [gap]
- Source: Why sulfur plants fail (Hydrocarbon Processing, Oct 2022) (Hydrocarbon Processing, 2022)
- URL: https://hydrocarbonprocessing.com/magazine/2022/october-2022/special-focus-plant-safety-and-environment/why-sulfur-plants-fail-an-in-depth-study-of-sulfur-recovery-unit-failures-part-1/
- Section: -
- Read: Search snippet only (about one SRU explosion every two years); article not fetched.
- Grade: C
- Package change: None.

## Coal gasification incident [closed]
- Source: Incident Reports Volume 4, Eastman Kingsport (29 Nov 2020) (US Chemical Safety Board, 18 Feb 2026)
- URL: https://www.csb.gov/assets/1/6/Incident_Reports_Volume_4_2026-02-18.pdf
- Section: item 2, pp. 7-8
- Read: Corroded welded pipe support fatigue-cracked, water supply to the gasifier lost, stuck-open check valve, hot syngas backflowed and ruptured two quench water connections, autoignition fire at about 1000 psi; PHA wrongly assumed low level would trip the gasifier.
- Grade: A
- Package change: Add loss-of-quench-water as an explicit gasifier trip with independent flow measurement, and check-valve testing in the MI list. (An AIChE abstract dated it 2017; CSB date used.)

## Gasification reactor depressurisation [partly]
- Source: Explosion in an ammonia plant (HIAD event 214) (EU Clean Hydrogen Knowledge Hub, 21 Dec 1997)
- URL: https://knowledge.clean-hydrogen.europa.eu/hiad/incidents/explosion-ammonia-plant-1
- Section: root cause
- Read: Burner flange leak, substituted stud-bolt material and unassessed repair overpressure caused flange failure and reactor depressurisation, refractory ejection and syngas fire.
- Grade: B
- Package change: Add flange bolt material verification to gasifier burner MI.

## Ammonium nitrate / fertiliser fire frame [partly]
- Source: West Fertilizer explosion and fire page (US Chemical Safety Board, -)
- URL: https://www.csb.gov/west-fertilizer-explosion-and-fire-/
- Section: -
- Read: Fetched, not read in depth; AN not part of this unit.
- Grade: C
- Package change: None.

