# Design standards reading map

Generated from `process_safety/data/design_recommendations.json`. Regenerate with `python -m process_safety library --map-markdown > docs/DESIGN_STANDARDS_RECOMMENDATIONS.md`. One row: `python -m process_safety library --activity ID`.

Which catalogue documents to open for a design activity or material product form. This is a reading list, not a requirement set: the law that applies, the contract and the adopted design code decide which documents govern, and in what order. Material rows name specification families by product form; grade selection, impact testing, sour-service and corrosion limits come from the design code and a materials engineer.

## By design activity

### Set up or audit a process safety management system (`psm-system`)

| Document | Title | Access |
|---|---|---|
| [29 CFR 1910.119](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) | Process safety management of highly hazardous chemicals | free |
| [40 CFR Part 68](https://www.ecfr.gov/current/title-40) | Chemical accident prevention provisions (Risk Management Program) | free |
| [Directive 2012/18/EU](https://eur-lex.europa.eu/eli/dir/2012/18/oj) | Control of major-accident hazards involving dangerous substances (Seveso III) | free |
| [SI 2015/483](https://www.legislation.gov.uk/uksi/2015/483/contents) | Control of Major Accident Hazards Regulations 2015 (COMAH) | free |
| [MSIHC Rules 1989](https://moef.gov.in/) | Manufacture, Storage and Import of Hazardous Chemicals Rules | free |
| [CCPS RBPS](https://www.aiche.org/ccps/publications) | Guidelines for Risk Based Process Safety | paid |
| [OSHA 3133](https://www.osha.gov/sites/default/files/publications/osha3133.pdf) | Process Safety Management Guidelines for Compliance | free |
| [API RP 754](https://publications.api.org/) | Process safety performance indicators for the refining and petrochemical industries | paid |
| [IOGP 456](https://www.iogp.org/bookstore/) | Process safety: recommended practice on key performance indicators | free |
| [HSG254](https://www.hse.gov.uk/pubns/books/hsg254.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg254.pdf)) | Developing process safety indicators | free |
| [ISO 45001](https://www.iso.org/search.html?q=ISO%2045001) | Occupational health and safety management systems | paid |
| [AIGA 099](https://www.asiaiga.org/) | Process safety management guideline for industrial gases | free |

### Inherently safer design and safety in the project design stages (`inherently-safer`)

| Document | Title | Access |
|---|---|---|
| [CCPS Inherently Safer](https://www.aiche.org/ccps/publications) | Inherently Safer Chemical Processes: A Life Cycle Approach | paid |
| [CCPS Engineering Design](https://www.aiche.org/ccps/publications) | Guidelines for Engineering Design for Process Safety | paid |
| [CCPS Capital Projects](https://www.aiche.org/ccps/publications) | Guidelines for Integrating Process Safety into Engineering Projects | paid |
| [DOE-STD-1189](https://www.standards.doe.gov/) | Integration of Safety into the Design Process | free |
| [ISO 17776](https://www.iso.org/search.html?q=ISO%2017776) | Offshore installations: major accident hazard management during design | paid |
| [Kletz and Amyotte, Inherently Safer](https://shop.elsevier.com/) | Process Plants: A Handbook for Inherently Safer Design | paid |

### HAZID, HAZOP, FMEA and other hazard evaluation (`hazard-identification`)

| Document | Title | Access |
|---|---|---|
| [IEC 61882](https://webstore.iec.ch/) | Hazard and operability studies (HAZOP studies): application guide | paid |
| [CCPS HEP](https://www.aiche.org/ccps/publications) | Guidelines for Hazard Evaluation Procedures | paid |
| [IEC 31010](https://webstore.iec.ch/) | Risk management: risk assessment techniques | paid |
| [IEC 60812](https://webstore.iec.ch/) | Failure modes and effects analysis (FMEA and FMECA) | paid |
| [CCPS Revalidating PHA](https://www.aiche.org/ccps/publications) | Revalidating Process Hazard Analyses | paid |
| [IS 15656](https://standards.bis.gov.in/) | Hazard identification and risk analysis: code of practice | mixed |
| [DOE-HDBK-1100](https://www.standards.doe.gov/) | Chemical Process Hazards Analysis | free |

### LOPA, SIL determination, SIS design and verification (`lopa-sil`)

| Document | Title | Access |
|---|---|---|
| [IEC 61511 (all parts)](https://webstore.iec.ch/) | Functional safety: safety instrumented systems for the process industry sector | paid |
| [IEC 61508 (all parts)](https://webstore.iec.ch/) | Functional safety of electrical/electronic/programmable electronic safety-related systems | paid |
| [ISA-TR84.00.02](https://www.isa.org/standards-and-publications/isa-standards) | Safety integrity level verification of safety instrumented functions | paid |
| [CCPS LOPA](https://www.aiche.org/ccps/publications) | Layer of Protection Analysis: Simplified Process Risk Assessment | paid |
| [CCPS IEs and IPLs](https://www.aiche.org/ccps/publications) | Guidelines for Initiating Events and Independent Protection Layers in LOPA | paid |
| [CCPS Enabling Conditions](https://www.aiche.org/ccps/publications) | Guidelines for Enabling Conditions and Conditional Modifiers in LOPA | paid |
| [PDS Data Handbook](https://www.sintef.no/en/) | Reliability data for safety equipment | paid |
| [EEMUA 222](https://www.eemua.org/) | Guide to the application of IEC 61511 | paid |

### Alarm management, control room and control-system security (`alarms-control-cyber`)

| Document | Title | Access |
|---|---|---|
| [IEC 62682](https://webstore.iec.ch/) | Management of alarm systems for the process industries | paid |
| [ISA-18.2](https://www.isa.org/standards-and-publications/isa-standards) | Management of alarm systems for the process industries | paid |
| [EEMUA 191](https://www.eemua.org/) | Alarm systems: a guide to design, management and procurement | paid |
| [ISA-101.01](https://www.isa.org/standards-and-publications/isa-standards) | Human machine interfaces for process automation systems | paid |
| [ISO 11064 (series)](https://www.iso.org/search.html?q=ISO%2011064%20%28series%29) | Ergonomic design of control centres | paid |
| [API RP 1168](https://publications.api.org/) | Pipeline control room management | paid |
| [IEC 62443 (series)](https://webstore.iec.ch/) | Security for industrial automation and control systems | paid |
| [NIST SP 800-82](https://csrc.nist.gov/pubs/sp/800/82/r3/final) ([PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf)) | Guide to Operational Technology (OT) Security | free |

### Quantitative risk assessment and risk criteria (`qra`)

| Document | Title | Access |
|---|---|---|
| [CCPS CPQRA](https://www.aiche.org/ccps/publications) | Guidelines for Chemical Process Quantitative Risk Analysis | paid |
| [PGS 3 (CPR 18E) Purple Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Guidelines for quantitative risk assessment | free |
| [PGS 2 (CPR 14E) Yellow Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for the calculation of physical effects | free |
| [PGS 1 (CPR 16) Green Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for the determination of possible damage to people and objects | free |
| [Reference Manual Bevi Risk Assessments](https://www.rivm.nl/en) | Dutch reference manual for quantitative risk assessment | free |
| [IOGP 434 series](https://www.iogp.org/bookstore/) | Risk Assessment Data Directory (process release, ignition, vulnerability and other data sheets) | free |
| [NORSOK Z-013](https://standard.no/en/sectors/petroleum/norsok-standards/) | Risk and emergency preparedness assessment | mixed |
| [CCPS Risk Criteria](https://www.aiche.org/ccps/publications) | Guidelines for Developing Quantitative Safety Risk Criteria | paid |

### Overpressure protection, depressuring, venting and flare (`relief-flare`)

| Document | Title | Access |
|---|---|---|
| [API STD 520 Part I](https://publications.api.org/) | Sizing, selection and installation of pressure-relieving devices: sizing and selection | paid |
| [API RP 520 Part II](https://publications.api.org/) | Sizing, selection and installation of pressure-relieving devices: installation | paid |
| [API STD 521](https://publications.api.org/) | Pressure-relieving and depressuring systems | paid |
| [API STD 526](https://publications.api.org/) | Flanged steel pressure-relief valves | paid |
| [API STD 2000](https://publications.api.org/) | Venting atmospheric and low-pressure storage tanks | paid |
| [API RP 576](https://publications.api.org/) | Inspection of pressure-relieving devices | paid |
| [ISO 4126 (all parts)](https://www.iso.org/search.html?q=ISO%204126%20%28all%20parts%29) | Safety devices for protection against excessive pressure | paid |
| [ASME BPVC VIII Div 1](https://www.asme.org/codes-standards) | Rules for construction of pressure vessels | paid |
| [ASME BPVC XIII](https://www.asme.org/codes-standards) | Rules for overpressure protection | paid |
| [CCPS Pressure Relief and Effluent Handling](https://www.aiche.org/ccps/publications) | Guidelines for Pressure Relief and Effluent Handling Systems | paid |
| [DIERS Project Manual](https://www.aiche.org/ccps/publications) | Emergency relief system design using DIERS technology | paid |
| [API STD 537](https://publications.api.org/) | Flare details for petroleum, petrochemical and natural gas industries | paid |

### Reactive chemistry and thermal runaway (`reactive-hazards`)

| Document | Title | Access |
|---|---|---|
| [CCPS Reactivity Essential Practices](https://www.aiche.org/ccps/publications) | Essential Practices for Managing Chemical Reactivity Hazards | paid |
| [CCPS Reactive Evaluation](https://www.aiche.org/ccps/publications) | Guidelines for Chemical Reactivity Evaluation and Application to Process Design | paid |
| [HSG143](https://www.hse.gov.uk/pubns/books/hsg143.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg143.pdf)) | Designing and operating safe chemical reaction processes | free |
| [Stoessel, Thermal Safety of Chemical Processes](https://www.icheme.org/) | Thermal Safety of Chemical Processes: Risk Assessment and Process Design (F. Stoessel) | paid |
| [ASTM E537](https://store.astm.org/standards/e537) | Standard Test Method for Thermal Stability of Chemicals by Differential Scanning Calorimetry | paid |
| [ASTM E698](https://store.astm.org/standards/e698) | Standard Test Method for Kinetic Parameters for Thermally Unstable Materials Using Differential Scanning Calorimetry and the Flynn/Wall/Ozawa Method | paid |
| [ASTM E1231](https://store.astm.org/standards/e1231) | Standard Practice for Calculation of Hazard Potential Figures of Merit for Thermally Unstable Materials | paid |
| [ASTM E1981](https://store.astm.org/standards/e1981) | Standard Guide for Assessing Thermal Stability of Materials by Methods of Accelerating Rate Calorimetry | paid |
| [UN Manual of Tests and Criteria](https://unece.org/transport/dangerous-goods/un-manual-tests-and-criteria) | Test methods for classifying explosives, self-reactives, peroxides and flammables | free |
| [CAMEO Chemicals](https://cameochemicals.noaa.gov/) | Hazardous material datasheets and reactivity compatibility prediction | free |

### Release, dispersion, fire and explosion modelling (`consequence-modelling`)

| Document | Title | Access |
|---|---|---|
| [PGS 2 (CPR 14E) Yellow Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for the calculation of physical effects | free |
| [CCPS VCE/BLEVE/Flash Fire](https://www.aiche.org/ccps/publications) | Guidelines for Vapor Cloud Explosion, Pressure Vessel Burst, BLEVE and Flash Fire Hazards | paid |
| [Casal, Effects and Consequences](https://shop.elsevier.com/) | Evaluation of the Effects and Consequences of Major Accidents in Industrial Plants (J. Casal) | paid |
| [ALOHA](https://www.epa.gov/cameo/aloha-software) | Areal Locations of Hazardous Atmospheres dispersion and consequence model | free |
| [FDS and Smokeview](https://pages.nist.gov/fds-smv/) | Fire Dynamics Simulator and visualisation tool, with user and validation guides | free |
| [NUREG-1805](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1805/index.html) | Fire Dynamics Tools: quantitative fire hazard analysis methods | free |
| [HyRAM+](https://energy.sandia.gov/programs/sustainable-transportation/hydrogen/hydrogen-safety-codes-and-standards/hyram/) | Hydrogen and alternative fuels risk assessment models (Sandia) | mixed |
| [EPA OCA guidance](https://www.epa.gov/rmp/rmp-guidance-offsite-consequence-analysis) | Risk Management Program guidance for offsite consequence analysis | free |

### Layout, spacing, occupied buildings and blast loading (`facility-siting`)

| Document | Title | Access |
|---|---|---|
| [API RP 752](https://publications.api.org/) | Management of hazards associated with location of process plant permanent buildings | paid |
| [API RP 753](https://publications.api.org/) | Management of hazards associated with location of process plant portable buildings | paid |
| [API RP 756](https://publications.api.org/) | Management of hazards associated with location of process plant tents | paid |
| [CCPS Facility Siting](https://www.aiche.org/ccps/publications) | Guidelines for Siting and Layout of Facilities | paid |
| [CCPS Occupied Buildings](https://www.aiche.org/ccps/publications) | Guidelines for Evaluating Process Plant Buildings for External Explosions, Fires, and Toxic Releases | paid |
| [ASCE Blast Design](https://ascelibrary.org/) | Design of Blast-Resistant Buildings in Petrochemical Facilities | paid |
| [UFC 3-340-02](https://www.wbdg.org/dod/ufc/ufc-3-340-02) ([PDF](https://www.wbdg.org/FFC/DOD/UFC/ufc_3_340_02_2008_c2.pdf)) | Structures to Resist the Effects of Accidental Explosions | free |
| [DNV-RP-C204](https://www.dnv.com/rules-standards/) | Design against accidental loads | free |
| [API RP 2FB](https://publications.api.org/) | Design of offshore facilities against fire and blast loading | paid |
| [GAP.2.5.2](https://axaxl.com/) | Oil and chemical plant layout and spacing | mixed |

### Fire water, foam, water spray and extinguishing systems (`fire-protection-active`)

| Document | Title | Access |
|---|---|---|
| [NFPA 11](https://www.nfpa.org/codes-and-standards/nfpa-11-standard-development/11) | Low-, Medium-, and High-Expansion Foam | mixed |
| [NFPA 13](https://www.nfpa.org/codes-and-standards/nfpa-13-standard-development/13) | Installation of Sprinkler Systems | mixed |
| [NFPA 15](https://www.nfpa.org/codes-and-standards/nfpa-15-standard-development/15) | Water Spray Fixed Systems for Fire Protection | mixed |
| [NFPA 20](https://www.nfpa.org/codes-and-standards/nfpa-20-standard-development/20) | Installation of Stationary Pumps for Fire Protection | mixed |
| [NFPA 24](https://www.nfpa.org/codes-and-standards/nfpa-24-standard-development/24) | Installation of Private Fire Service Mains and Their Appurtenances | mixed |
| [NFPA 25](https://www.nfpa.org/codes-and-standards/nfpa-25-standard-development/25) | Inspection, Testing, and Maintenance of Water-Based Fire Protection Systems | mixed |
| [API RP 2001](https://publications.api.org/) | Fire protection in refineries | paid |
| [API RP 2030](https://publications.api.org/) | Application of fixed water spray systems for fire protection in the petroleum and petrochemical industries | paid |
| [API RP 2021](https://publications.api.org/) | Management of atmospheric storage tank fires | paid |
| [ISO 13702](https://www.iso.org/search.html?q=ISO%2013702) | Control and mitigation of fires and explosions on offshore production installations | paid |
| [EI Model Code of Safe Practice Part 19](https://www.energyinst.org/technical/publications) | Fire precautions at petroleum refineries and bulk storage installations | mixed |
| [IS 15325](https://standards.bis.gov.in/) | Design and installation of fixed automatic high and medium velocity water spray system | mixed |

### Passive fire protection and structural fire (`fire-protection-passive`)

| Document | Title | Access |
|---|---|---|
| [API RP 2218](https://publications.api.org/) | Fireproofing practices in petroleum and petrochemical processing plants | paid |
| [UL 1709](https://www.shopulstandards.com/) | Rapid rise fire tests of protection materials for structural steel | mixed |
| [ISO 22899 (series)](https://www.iso.org/search.html?q=ISO%2022899%20%28series%29) | Determination of the resistance to jet fires of passive fire protection materials | paid |
| [ISO 20088 (series)](https://www.iso.org/search.html?q=ISO%2020088%20%28series%29) | Resistance to cryogenic spillage of insulation materials | paid |
| [EN 1993-1-2](https://standards.cencenelec.eu/) | Eurocode 3: design of steel structures, structural fire design | paid |
| [EN 1991-1-2](https://standards.cencenelec.eu/) | Eurocode 1: actions on structures exposed to fire | paid |
| [ASTM E1529](https://store.astm.org/standards/e1529) | Standard Test Methods for Determining Effects of Large Hydrocarbon Pool Fires on Structural Members and Assemblies | paid |
| [API RP 583](https://publications.api.org/) | Corrosion under insulation and fireproofing | paid |

### Fire and gas detection (`fire-gas-detection`)

| Document | Title | Access |
|---|---|---|
| [NFPA 72](https://www.nfpa.org/codes-and-standards/nfpa-72-standard-development/72) | National Fire Alarm and Signaling Code | mixed |
| [ISA-TR84.00.07](https://www.isa.org/standards-and-publications/isa-standards) | Guidance on the evaluation of fire, combustible gas and toxic gas system effectiveness | paid |
| [IEC 60079-29 (series)](https://webstore.iec.ch/) | Gas detectors: performance, selection, installation, use and maintenance | paid |
| [EN 54 (series)](https://standards.cencenelec.eu/) | Fire detection and fire alarm systems | paid |
| [ISO 26142](https://www.iso.org/search.html?q=ISO%2026142) | Hydrogen detection apparatus: stationary applications | paid |
| [IS 2189](https://standards.bis.gov.in/) | Selection, installation and maintenance of automatic fire detection and alarm systems | mixed |

### Combustible dust hazards (`combustible-dust`)

| Document | Title | Access |
|---|---|---|
| [NFPA 660](https://www.nfpa.org/codes-and-standards/nfpa-660-standard-development/660) | Combustible Dusts and Particulate Solids | mixed |
| [NFPA 68](https://www.nfpa.org/codes-and-standards/nfpa-68-standard-development/68) | Explosion Protection by Deflagration Venting | mixed |
| [NFPA 69](https://www.nfpa.org/codes-and-standards/nfpa-69-standard-development/69) | Explosion Prevention Systems | mixed |
| [EN 1127-1](https://standards.cencenelec.eu/) | Explosive atmospheres: explosion prevention and protection, basic concepts and methodology | paid |
| [EN 14491](https://standards.cencenelec.eu/) | Dust explosion venting protective systems | paid |
| [ASTM E1226](https://store.astm.org/standards/e1226) | Standard Test Method for Explosibility of Dust Clouds | paid |
| [ASTM E1515](https://store.astm.org/standards/e1515) | Standard Test Method for Minimum Explosible Concentration of Combustible Dusts | paid |
| [ASTM E2019](https://store.astm.org/standards/e2019) | Standard Test Method for Minimum Ignition Energy of a Dust Cloud in Air | paid |
| [ASTM E2021](https://store.astm.org/standards/e2021) | Standard Test Method for Hot-Surface Ignition Temperature of Dust Layers | paid |
| [ASTM E1491](https://store.astm.org/standards/e1491) | Standard Test Method for Minimum Autoignition Temperature of Dust Clouds | paid |
| [GESTIS-DUST-EX](https://www.dguv.de/ifa/gestis/gestis-staub-ex/index-2.jsp) | Database of combustion and explosion characteristics of dusts | free |
| [HSG103](https://www.hse.gov.uk/pubns/books/hsg103.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg103.pdf)) | Safe handling of combustible dusts | free |

### Flammability limits, inerting, flame arresters and explosion protection (`gas-explosion-flammability`)

| Document | Title | Access |
|---|---|---|
| [NFPA 69](https://www.nfpa.org/codes-and-standards/nfpa-69-standard-development/69) | Explosion Prevention Systems | mixed |
| [NFPA 68](https://www.nfpa.org/codes-and-standards/nfpa-68-standard-development/68) | Explosion Protection by Deflagration Venting | mixed |
| [NFPA 67](https://www.nfpa.org/codes-and-standards/nfpa-67-standard-development/67) | Explosion Protection for Gaseous Mixtures in Pipe Systems | mixed |
| [ISO 16852](https://www.iso.org/search.html?q=ISO%2016852) | Flame arresters: performance requirements, test methods and limits for use | paid |
| [ASTM E681](https://store.astm.org/standards/e681) | Standard Test Method for Concentration Limits of Flammability of Chemicals (Vapors and Gases) | paid |
| [ASTM E918](https://store.astm.org/standards/e918) | Standard Practice for Determining Limits of Flammability of Chemicals at Elevated Temperature and Pressure | paid |
| [ASTM E2079](https://store.astm.org/standards/e2079) | Standard Test Methods for Limiting Oxygen (Oxidant) Concentration in Gases and Vapors | paid |
| [ASTM E659](https://store.astm.org/standards/e659) | Standard Test Method for Autoignition Temperature of Chemicals | paid |
| [ASTM E582](https://store.astm.org/standards/e582) | Standard Test Method for Minimum Ignition Energy and Quenching Distance in Gaseous Mixtures | paid |
| [EN 1839](https://standards.cencenelec.eu/) | Determination of explosion limits and limiting oxygen concentration for gases and vapours | paid |

### Hazardous area classification and Ex equipment (`area-classification`)

| Document | Title | Access |
|---|---|---|
| [IEC 60079-10-1](https://webstore.iec.ch/) | Classification of areas: explosive gas atmospheres | paid |
| [IEC 60079-10-2](https://webstore.iec.ch/) | Classification of areas: explosive dust atmospheres | paid |
| [API RP 505](https://publications.api.org/) | Classification of locations for electrical installations at petroleum facilities classified as Class I, Zone 0, 1 and 2 | paid |
| [API RP 500](https://publications.api.org/) | Classification of locations for electrical installations at petroleum facilities classified as Class I, Division 1 and 2 | paid |
| [NFPA 497](https://www.nfpa.org/codes-and-standards/nfpa-497-standard-development/497) | Classification of Flammable Liquids, Gases, or Vapors and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas | mixed |
| [NFPA 499](https://www.nfpa.org/codes-and-standards/nfpa-499-standard-development/499) | Classification of Combustible Dusts and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas | mixed |
| [EI 15](https://www.energyinst.org/technical/publications) | Model Code of Safe Practice Part 15: area classification for installations handling flammable fluids | mixed |
| [IS 5572](https://standards.bis.gov.in/) | Classification of hazardous areas (other than mines) having flammable gases and vapours for electrical installation | mixed |
| [IEC 60079-0](https://webstore.iec.ch/) | Explosive atmospheres: equipment, general requirements | paid |
| [IEC 60079-14](https://webstore.iec.ch/) | Electrical installations design, selection and erection | paid |
| [IEC 60079-17](https://webstore.iec.ch/) | Electrical installations inspection and maintenance | paid |
| [Directive 2014/34/EU](https://eur-lex.europa.eu/eli/dir/2014/34/oj) | Equipment and protective systems for potentially explosive atmospheres (ATEX equipment) | free |
| [Directive 1999/92/EC](https://eur-lex.europa.eu/eli/dir/1999/92/oj) | Protection of workers at risk from explosive atmospheres (ATEX workplace) | free |

### Static electricity, lightning, earthing and arc flash (`static-lightning-electrical`)

| Document | Title | Access |
|---|---|---|
| [NFPA 77](https://www.nfpa.org/codes-and-standards/nfpa-77-standard-development/77) | Static Electricity | mixed |
| [IEC TS 60079-32-1](https://webstore.iec.ch/) | Electrostatic hazards: guidance | paid |
| [API RP 2003](https://publications.api.org/) | Protection against ignitions arising out of static, lightning and stray currents | paid |
| [API RP 545](https://publications.api.org/) | Lightning protection of aboveground storage tanks for flammable or combustible liquids | paid |
| [IEC 62305 (series)](https://webstore.iec.ch/) | Protection against lightning | paid |
| [NFPA 780](https://www.nfpa.org/codes-and-standards/nfpa-780-standard-development/780) | Installation of Lightning Protection Systems | mixed |
| [IEEE 1584](https://standards.ieee.org/) | Guide for performing arc-flash hazard calculations | paid |
| [NFPA 70E](https://www.nfpa.org/codes-and-standards/nfpa-70e-standard-development/70e) | Electrical Safety in the Workplace | mixed |
| [IEEE 80](https://standards.ieee.org/) | Guide for safety in AC substation grounding | paid |
| [IS 3043](https://standards.bis.gov.in/) | Code of practice for earthing | mixed |

### Pressure vessel, exchanger and piping design (`pressure-equipment-piping`)

| Document | Title | Access |
|---|---|---|
| [ASME BPVC VIII Div 1](https://www.asme.org/codes-standards) | Rules for construction of pressure vessels | paid |
| [ASME B31.3](https://www.asme.org/codes-standards) | Process piping | paid |
| [ASME BPVC II Part D](https://www.asme.org/codes-standards) | Materials: properties (allowable stresses, external pressure charts) | paid |
| [ASME B16.5](https://www.asme.org/codes-standards) | Pipe flanges and flanged fittings (NPS 1/2 through NPS 24) | paid |
| [ASME PCC-1](https://www.asme.org/codes-standards) | Pressure boundary bolted flange joint assembly | paid |
| [TEMA Standards](https://www.tema.org/) | Standards of the Tubular Exchanger Manufacturers Association | paid |
| [API STD 660](https://publications.api.org/) | Shell-and-tube heat exchangers | paid |
| [EN 13445 (series)](https://standards.cencenelec.eu/) | Unfired pressure vessels | paid |
| [EN 13480 (series)](https://standards.cencenelec.eu/) | Metallic industrial piping | paid |
| [PD 5500](https://knowledge.bsigroup.com/) | Specification for unfired fusion welded pressure vessels | paid |
| [Directive 2014/68/EU](https://eur-lex.europa.eu/eli/dir/2014/68/oj) | Pressure Equipment Directive | free |
| [IS 2825](https://standards.bis.gov.in/) | Code for unfired pressure vessels | mixed |
| [SMPV(U) Rules 2016](https://peso.gov.in/) | Static and Mobile Pressure Vessels (Unfired) Rules | free |

### Atmospheric and pressurised storage, overfill and bunding (`storage-tanks`)

| Document | Title | Access |
|---|---|---|
| [API STD 650](https://publications.api.org/) | Welded tanks for oil storage | paid |
| [API STD 620](https://publications.api.org/) | Design and construction of large, welded, low-pressure storage tanks | paid |
| [API STD 625](https://publications.api.org/) | Tank systems for refrigerated liquefied gas storage | paid |
| [API STD 2000](https://publications.api.org/) | Venting atmospheric and low-pressure storage tanks | paid |
| [API STD 2350](https://publications.api.org/) | Overfill prevention for storage tanks in petroleum facilities | paid |
| [API STD 2510](https://publications.api.org/) | Design and construction of LPG installations | paid |
| [NFPA 30](https://www.nfpa.org/codes-and-standards/nfpa-30-standard-development/30) | Flammable and Combustible Liquids Code | mixed |
| [NFPA 58](https://www.nfpa.org/codes-and-standards/nfpa-58-standard-development/58) | Liquefied Petroleum Gas Code | mixed |
| [NFPA 59A](https://www.nfpa.org/codes-and-standards/nfpa-59a-standard-development/59a) | Production, Storage, and Handling of Liquefied Natural Gas (LNG) | mixed |
| [HSG176](https://www.hse.gov.uk/pubns/books/hsg176.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg176.pdf)) | The storage of flammable liquids in tanks | free |
| [EN 14620 (series)](https://standards.cencenelec.eu/) | Site-built tanks for refrigerated liquefied gases | paid |
| [OISD standards list](https://www.oisd.gov.in/) | Oil Industry Safety Directorate standards, guidelines and recommended practices | mixed |
| [Petroleum Rules 2002](https://peso.gov.in/) | Petroleum Rules | free |

### Inspection, risk-based inspection and fitness for service (`mechanical-integrity`)

| Document | Title | Access |
|---|---|---|
| [API 510](https://publications.api.org/) | Pressure vessel inspection code: in-service inspection, rating, repair and alteration | paid |
| [API 570](https://publications.api.org/) | Piping inspection code: in-service inspection, rating, repair and alteration | paid |
| [API STD 653](https://publications.api.org/) | Tank inspection, repair, alteration and reconstruction | paid |
| [API RP 580](https://publications.api.org/) | Risk-based inspection | paid |
| [API RP 581](https://publications.api.org/) | Risk-based inspection methodology | paid |
| [API 579-1/ASME FFS-1](https://publications.api.org/) | Fitness-for-service | paid |
| [API RP 571](https://publications.api.org/) | Damage mechanisms affecting fixed equipment in the refining industry | paid |
| [API RP 578](https://publications.api.org/) | Guidelines for a material verification program for new and existing assets | paid |
| [API RP 584](https://publications.api.org/) | Integrity operating windows | paid |
| [BS 7910](https://knowledge.bsigroup.com/) | Guide to methods for assessing the acceptability of flaws in metallic structures | paid |
| [ASME PCC-2](https://www.asme.org/codes-standards) | Repair of pressure equipment and piping | paid |
| [EEMUA 159](https://www.eemua.org/) | Above ground flat bottomed storage tanks: a guide to inspection, maintenance and repair | paid |

### Materials selection and damage mechanisms (`materials-corrosion`)

| Document | Title | Access |
|---|---|---|
| [API RP 571](https://publications.api.org/) | Damage mechanisms affecting fixed equipment in the refining industry | paid |
| [ASME BPVC II Part D](https://www.asme.org/codes-standards) | Materials: properties (allowable stresses, external pressure charts) | paid |
| [ISO 21457](https://www.iso.org/search.html?q=ISO%2021457) | Materials selection and corrosion control for oil and gas production systems | paid |
| [NORSOK M-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Materials selection | mixed |
| [NACE MR0175 / ISO 15156](https://www.ampp.org/standards) | Materials for use in H2S-containing environments in oil and gas production | paid |
| [NACE MR0103 / ISO 17945](https://www.ampp.org/standards) | Metallic materials resistant to sulfide stress cracking in corrosive petroleum refining environments | paid |
| [API RP 941](https://publications.api.org/) | Steels for hydrogen service at elevated temperatures and pressures in petroleum refineries and petrochemical plants | paid |
| [API RP 939-C](https://publications.api.org/) | Guidelines for avoiding sulfidation corrosion failures in oil refineries | paid |
| [API RP 945](https://publications.api.org/) | Avoiding environmental cracking in amine units | paid |
| [API RP 751](https://publications.api.org/) | Safe operation of hydrofluoric acid alkylation units | paid |
| [API RP 932-B](https://publications.api.org/) | Design, materials, fabrication, operation and inspection guidelines for corrosion control in hydroprocessing reactor effluent air cooler systems | paid |
| [NACE SP0403](https://www.ampp.org/standards) | Avoiding caustic stress corrosion cracking of carbon steel refinery equipment and piping | paid |
| [NACE SP0198](https://www.ampp.org/standards) | Control of corrosion under thermal insulation and fireproofing materials | paid |
| [API RP 583](https://publications.api.org/) | Corrosion under insulation and fireproofing | paid |

### Welding, examination and material verification (`welding-nde`)

| Document | Title | Access |
|---|---|---|
| [ASME BPVC IX](https://www.asme.org/codes-standards) | Welding, brazing and fusing qualifications | paid |
| [ASME BPVC V](https://www.asme.org/codes-standards) | Nondestructive examination | paid |
| [API RP 582](https://publications.api.org/) | Welding guidelines for the chemical, oil and gas industries | paid |
| [API RP 577](https://publications.api.org/) | Welding processes, inspection and metallurgy | paid |
| [API RP 578](https://publications.api.org/) | Guidelines for a material verification program for new and existing assets | paid |
| [API STD 1104](https://publications.api.org/) | Welding of pipelines and related facilities | paid |
| [ISO 15614 (series)](https://www.iso.org/search.html?q=ISO%2015614%20%28series%29) | Specification and qualification of welding procedures: welding procedure test | paid |
| [ISO 9712](https://www.iso.org/search.html?q=ISO%209712) | Non-destructive testing: qualification and certification of personnel | paid |
| [ASNT SNT-TC-1A](https://www.asnt.org/) | Personnel qualification and certification in nondestructive testing | paid |
| [EN 10204](https://standards.cencenelec.eu/) | Metallic products: types of inspection documents (material certificates) | paid |
| [NACE SP0472](https://www.ampp.org/standards) | Methods and controls to prevent in-service environmental cracking of carbon steel weldments in refining | paid |

### Hydrogen service (`hydrogen`)

| Document | Title | Access |
|---|---|---|
| [NFPA 2](https://www.nfpa.org/codes-and-standards/nfpa-2-standard-development/2) | Hydrogen Technologies Code | mixed |
| [NFPA 55](https://www.nfpa.org/codes-and-standards/nfpa-55-standard-development/55) | Compressed Gases and Cryogenic Fluids Code | mixed |
| [ASME B31.12](https://www.asme.org/codes-standards) | Hydrogen piping and pipelines | paid |
| [CGA G-5](https://portal.cganet.com/Publication/index.aspx) | Hydrogen | mixed |
| [CGA G-5.4](https://portal.cganet.com/Publication/index.aspx) | Standard for hydrogen piping systems at user locations | mixed |
| [EIGA Doc 121](https://www.eiga.eu/publications/) | Hydrogen pipeline systems | free |
| [ISO/TR 15916](https://www.iso.org/search.html?q=ISO/TR%2015916) | Basic considerations for the safety of hydrogen systems | paid |
| [ISO 22734](https://www.iso.org/search.html?q=ISO%2022734) | Hydrogen generators using water electrolysis | paid |
| [ISO 19880-1](https://www.iso.org/search.html?q=ISO%2019880-1) | Gaseous hydrogen fuelling stations: general requirements | paid |
| [API RP 941](https://publications.api.org/) | Steels for hydrogen service at elevated temperatures and pressures in petroleum refineries and petrochemical plants | paid |
| [ASTM G142](https://store.astm.org/standards/g142) | Standard Test Method for Determination of Susceptibility of Metals to Embrittlement in Hydrogen Containing Environments at High Pressure, High Temperature, or Both | paid |
| [NASA NSS 1740.16](https://ntrs.nasa.gov/citations/19970033338) ([PDF](https://ntrs.nasa.gov/api/citations/19970033338/downloads/19970033338.pdf)) | Safety Standard for Hydrogen and Hydrogen Systems | mixed |
| [H2Tools](https://h2tools.org/) | Hydrogen safety best practices and lessons learned portal (PNNL) | mixed |
| [29 CFR 1910.103](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.103) | Hydrogen | free |

### Oxygen and oxygen-enriched service (`oxygen`)

| Document | Title | Access |
|---|---|---|
| [CGA G-4](https://portal.cganet.com/Publication/index.aspx) | Oxygen | mixed |
| [CGA G-4.4](https://portal.cganet.com/Publication/index.aspx) | Oxygen pipeline and piping systems | mixed |
| [CGA G-4.1](https://portal.cganet.com/Publication/index.aspx) | Cleaning of equipment for oxygen service | mixed |
| [EIGA Doc 13](https://www.eiga.eu/publications/) | Oxygen pipeline and piping systems | free |
| [EIGA Doc 04](https://www.eiga.eu/publications/) | Fire hazards of oxygen and oxygen enriched atmospheres | free |
| [NFPA 53](https://www.nfpa.org/codes-and-standards/nfpa-53-standard-development/53) | Materials, Equipment, and Systems Used in Oxygen-Enriched Atmospheres | mixed |
| [ASTM G63](https://store.astm.org/standards/g63) | Standard Guide for Evaluating Nonmetallic Materials for Oxygen Service | paid |
| [ASTM G88](https://store.astm.org/standards/g88) | Standard Guide for Designing Systems for Oxygen Service | paid |
| [ASTM G93](https://store.astm.org/standards/g93) | Standard Practice for Cleaning Methods and Cleanliness Levels for Material and Equipment Used in Oxygen-Enriched Environments | paid |
| [ASTM G94](https://store.astm.org/standards/g94) | Standard Guide for Evaluating Metals for Oxygen Service | paid |
| [ASTM G128](https://store.astm.org/standards/g128) | Standard Guide for Control of Hazards and Risks in Oxygen Enriched Systems | paid |

### LNG and LPG facilities (`lng-lpg`)

| Document | Title | Access |
|---|---|---|
| [NFPA 59A](https://www.nfpa.org/codes-and-standards/nfpa-59a-standard-development/59a) | Production, Storage, and Handling of Liquefied Natural Gas (LNG) | mixed |
| [NFPA 58](https://www.nfpa.org/codes-and-standards/nfpa-58-standard-development/58) | Liquefied Petroleum Gas Code | mixed |
| [NFPA 59](https://www.nfpa.org/codes-and-standards/nfpa-59-standard-development/59) | Utility LP-Gas Plant Code | mixed |
| [49 CFR Part 193](https://www.ecfr.gov/current/title-49) | Liquefied natural gas facilities: federal safety standards | free |
| [EN 1473](https://standards.cencenelec.eu/) | Installation and equipment for LNG: design of onshore installations | paid |
| [API STD 625](https://publications.api.org/) | Tank systems for refrigerated liquefied gas storage | paid |
| [API STD 2510](https://publications.api.org/) | Design and construction of LPG installations | paid |
| [API PUBL 2510A](https://publications.api.org/) | Fire-protection considerations for the design and operation of LPG storage facilities | paid |
| [SIGTTO publications](https://www.sigtto.org/) | Liquefied gas terminal and ship safety publications | mixed |
| [IGC Code](https://www.imo.org/) | International Code for the Construction and Equipment of Ships Carrying Liquefied Gases in Bulk | paid |

### Ammonia, chlorine and other toxic service (`ammonia-chlorine-toxics`)

| Document | Title | Access |
|---|---|---|
| [29 CFR 1910.111](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.111) | Storage and handling of anhydrous ammonia | free |
| [IIAR 2](https://www.iiar.org/) | Safe design of closed-circuit ammonia refrigeration systems | mixed |
| [CGA G-2](https://portal.cganet.com/Publication/index.aspx) | Anhydrous ammonia | mixed |
| [Chlorine Institute pamphlets](https://www.chlorineinstitute.org/) | Chlorine safety, piping, materials, transport and emergency pamphlets (e.g. Pamphlet 1 Chlorine Basics, Pamphlet 6 piping systems) | mixed |
| [Euro Chlor GEST publications](https://www.eurochlor.org/) | Chlorine industry materials, equipment and safety recommendations | mixed |
| [API RP 751](https://publications.api.org/) | Safe operation of hydrofluoric acid alkylation units | paid |
| [AEGL values](https://www.epa.gov/aegl) | Acute Exposure Guideline Levels for airborne chemicals | free |
| [AIHA ERPG](https://www.aiha.org/) | Emergency Response Planning Guidelines | free |
| [NIOSH IDLH](https://www.cdc.gov/niosh/idlh/default.html) | Immediately Dangerous to Life or Health values | free |

### Carbon dioxide, battery storage, biogas and fuel cells (`energy-transition`)

| Document | Title | Access |
|---|---|---|
| [DNV-RP-F104](https://www.dnv.com/rules-standards/) | Design and operation of carbon dioxide pipelines | free |
| [ISO 27913](https://www.iso.org/search.html?q=ISO%2027913) | Carbon dioxide capture, transportation and geological storage: pipeline transportation systems | paid |
| [CGA G-6](https://portal.cganet.com/Publication/index.aspx) | Carbon dioxide | mixed |
| [NFPA 855](https://www.nfpa.org/codes-and-standards/nfpa-855-standard-development/855) | Installation of Stationary Energy Storage Systems | mixed |
| [UL 9540A](https://www.ul.com/services/ul-9540a-test-method) | Test method for evaluating thermal runaway fire propagation in battery energy storage systems | mixed |
| [ISO 24252](https://www.iso.org/search.html?q=ISO%2024252) | Biogas systems: non-household and non-gasification | paid |
| [NFPA 820](https://www.nfpa.org/codes-and-standards/nfpa-820-standard-development/820) | Fire Protection in Wastewater Treatment and Collection Facilities | mixed |
| [DNV-RP-A203](https://www.dnv.com/rules-standards/) | Technology qualification | free |

### Cross-country and subsea pipelines (`pipelines`)

| Document | Title | Access |
|---|---|---|
| [ASME B31.4](https://www.asme.org/codes-standards) | Pipeline transportation systems for liquids and slurries | paid |
| [ASME B31.8](https://www.asme.org/codes-standards) | Gas transmission and distribution piping systems | paid |
| [ASME B31.8S](https://www.asme.org/codes-standards) | Managing system integrity of gas pipelines | paid |
| [API STD 1160](https://publications.api.org/) | Managing system integrity for hazardous liquid pipelines | paid |
| [ISO 13623](https://www.iso.org/search.html?q=ISO%2013623) | Pipeline transportation systems | paid |
| [DNV-ST-F101](https://www.dnv.com/rules-standards/) | Submarine pipeline systems | free |
| [49 CFR Part 192](https://www.ecfr.gov/current/title-49) | Transportation of natural and other gas by pipeline: minimum federal safety standards | free |
| [49 CFR Part 195](https://www.ecfr.gov/current/title-49) | Transportation of hazardous liquids by pipeline | free |
| [SI 1996/825](https://www.legislation.gov.uk/uksi/1996/825/contents) | Pipelines Safety Regulations 1996 | free |
| [PNGRB Integrity Management System Regulations](https://www.pngrb.gov.in/) | Integrity management system for pipelines and city gas networks | free |
| [NACE SP0169](https://www.ampp.org/standards) | Control of external corrosion on underground or submerged metallic piping systems | paid |

### Offshore installations (`offshore`)

| Document | Title | Access |
|---|---|---|
| [ISO 10418](https://www.iso.org/search.html?q=ISO%2010418) | Offshore production installations: process safety systems | paid |
| [API RP 14C](https://publications.api.org/) | Analysis, design, installation and testing of safety systems for offshore production facilities | paid |
| [API RP 14J](https://publications.api.org/) | Design and hazards analysis for offshore production facilities | paid |
| [ISO 13702](https://www.iso.org/search.html?q=ISO%2013702) | Control and mitigation of fires and explosions on offshore production installations | paid |
| [ISO 15544](https://www.iso.org/search.html?q=ISO%2015544) | Offshore production installations: emergency response requirements and guidelines | paid |
| [NORSOK S-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Technical safety | mixed |
| [NORSOK Z-013](https://standard.no/en/sectors/petroleum/norsok-standards/) | Risk and emergency preparedness assessment | mixed |
| [DNV-OS-A101](https://www.dnv.com/rules-standards/) | Safety principles and arrangements | free |
| [DNV-OS-D301](https://www.dnv.com/rules-standards/) | Fire protection | free |
| [Directive 2013/30/EU](https://eur-lex.europa.eu/eli/dir/2013/30/oj) | Safety of offshore oil and gas operations | free |

### Permits, isolation, confined space, hot work and change control (`safe-operations`)

| Document | Title | Access |
|---|---|---|
| [HSG250](https://www.hse.gov.uk/pubns/books/hsg250.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg250.pdf)) | Guidance on permit-to-work systems | free |
| [HSG253](https://www.hse.gov.uk/pubns/books/hsg253.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg253.pdf)) | The safe isolation of plant and equipment | free |
| [29 CFR 1910.147](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147) | Control of hazardous energy (lockout/tagout) | free |
| [29 CFR 1910.146](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.146) | Permit-required confined spaces | free |
| [NFPA 51B](https://www.nfpa.org/codes-and-standards/nfpa-51b-standard-development/51b) | Fire Prevention During Welding, Cutting, and Other Hot Work | mixed |
| [NFPA 350](https://www.nfpa.org/codes-and-standards/nfpa-350-standard-development/350) | Safe Confined Space Entry and Work | mixed |
| [API RP 2009](https://publications.api.org/) | Safe welding, cutting and hot work practices in the petroleum and petrochemical industries | paid |
| [API STD 2015](https://publications.api.org/) | Requirements for safe entry and cleaning of petroleum storage tanks | paid |
| [API RP 2201](https://publications.api.org/) | Safe hot tapping practices in the petroleum and petrochemical industries | paid |
| [CCPS Management of Change](https://www.aiche.org/ccps/publications) | Guidelines for the Management of Change for Process Safety | paid |
| [CCPS Pre-Startup](https://www.aiche.org/ccps/publications) | Guidelines for Performing Effective Pre-Startup Safety Reviews | paid |

### Emergency planning and response (`emergency-response`)

| Document | Title | Access |
|---|---|---|
| [CCPS Emergency Planning](https://www.aiche.org/ccps/publications) | Guidelines for Technical Planning for On-Site Emergencies | paid |
| [PNGRB ERDMP Regulations](https://www.pngrb.gov.in/) | Emergency response and disaster management plan regulations | free |
| [NDMA chemical disaster guidelines](https://ndma.gov.in/) | National Disaster Management Guidelines: Chemical Disasters (Industrial) | free |
| [Emergency Response Guidebook](https://www.phmsa.dot.gov/training/hazmat/erg/emergency-response-guidebook-erg) | PHMSA Emergency Response Guidebook (initial isolation and protective action distances) | free |
| [ISO 15544](https://www.iso.org/search.html?q=ISO%2015544) | Offshore production installations: emergency response requirements and guidelines | paid |
| [29 CFR 1910.120](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.120) | Hazardous waste operations and emergency response | free |

## Materials: specification families by product form and service

### Carbon and low-alloy steel pipe (`cs-pipe-general`)

| Document | Title | Access |
|---|---|---|
| [ASTM A53](https://store.astm.org/standards/a53) | Standard Specification for Pipe, Steel, Black And Hot- Dipped, Zinc- Coated Welded And Seamless | paid |
| [ASTM A106](https://store.astm.org/standards/a106) | Standard Specification for Seamless Carbon Steel Pipe for High-Temperature Service | paid |
| [ASTM A524](https://store.astm.org/standards/a524) | Standard Specification for Seamless Carbon Steel Pipe for Atmospheric and Lower Temperatures | paid |
| [ASTM A335](https://store.astm.org/standards/a335_a335m) | Standard Specification for Seamless Ferritic Alloy-Steel Pipe for High-Temperature Service | paid |
| [ASTM A671](https://store.astm.org/standards/a671) | Standard Specification for Electric-Fusion-Welded Steel Pipe for Atmospheric and Lower Temperatures | paid |
| [ASTM A672](https://store.astm.org/standards/a672) | Standard Specification for Electric-Fusion-Welded Steel Pipe for High-Pressure Service at Moderate Temperatures | paid |
| [ASTM A691](https://store.astm.org/standards/a691) | Standard Specification for Carbon and Alloy Steel Pipe, Electric-Fusion-Welded for High-Pressure Service at High Temperatures | paid |
| [API SPEC 5L](https://publications.api.org/) | Line pipe | paid |
| [ASTM A999](https://store.astm.org/standards/a999_a999m) | Standard Specification for General Requirements for Alloy and Stainless Steel Pipe | paid |
| [ASTM A530](https://store.astm.org/standards/a530_a530m) | Standard Specification for General Requirements for Specialized Carbon and Alloy Steel Pipe | paid |

### Low-temperature and cryogenic carbon and nickel steels (`low-temperature`)

| Document | Title | Access |
|---|---|---|
| [ASTM A333](https://store.astm.org/standards/a333) | Standard Specifications For Seamless And Welded Steel Pipe For Low-Temperature Service | paid |
| [ASTM A334](https://store.astm.org/standards/a334_a334m) | Standard Specification for Seamless and Welded Carbon and Alloy-Steel Tubes for Low-Temperature Service | paid |
| [ASTM A350](https://store.astm.org/standards/a350_a350m) | Standard Specification for Carbon and Low-Alloy Steel Forgings, Requiring Notch Toughness Testing for Piping Components | paid |
| [ASTM A352](https://store.astm.org/standards/a352_a352m) | Standard Specification for Steel Castings, Ferritic and Martensitic, for Pressure-Containing Parts, Suitable for Low-Temperature Service | paid |
| [ASTM A420](https://store.astm.org/standards/a420_a420m) | Standard Specification for Piping Fittings of Wrought Carbon Steel and Alloy Steel for Low-Temperature Service | paid |
| [ASTM A320](https://store.astm.org/standards/a320_a320m) | Standard Specification for Alloy-Steel and Stainless Steel Bolting for Low-Temperature Service | paid |
| [ASTM A516](https://store.astm.org/standards/a516_a516m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, for Moderate- and Lower-Temperature Service | paid |
| [ASTM A537](https://store.astm.org/standards/a537_a537m) | Standard Specification for Pressure Vessel Plates, Heat-Treated, Carbon-Manganese-Silicon Steel | paid |
| [ASTM A203](https://store.astm.org/standards/a203_a203m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Nickel | paid |
| [ASTM A353](https://store.astm.org/standards/a353_a353m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Double-Normalized and Tempered 9 % Nickel | paid |
| [ASTM A553](https://store.astm.org/standards/a553_a553m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched and Tempered 7 %, 8 %, and 9 % Nickel | paid |
| [ASTM A522](https://store.astm.org/standards/a522_a522m) | Standard Specification for Forged or Rolled 8 and 9% Nickel Alloy Steel Flanges, Fittings, Valves, and Parts for Low-Temperature Service | paid |
| [ASTM E208](https://store.astm.org/standards/e208) | Standard Test Method for Conducting Drop-Weight Test to Determine Nil-Ductility Transition Temperature of Ferritic Steels | paid |
| [ASTM E23](https://store.astm.org/standards/e23) | Standard Test Methods for Notched Bar Impact Testing of Metallic Materials | paid |
| [ASTM E1921](https://store.astm.org/standards/e1921) | Standard Test Method for Determination of Reference Temperature, T0, for Ferritic Steels in the Transition Range | paid |

### Austenitic and duplex stainless steel (`stainless-duplex`)

| Document | Title | Access |
|---|---|---|
| [ASTM A240](https://store.astm.org/standards/a240_a240m) | Standard Specification for Chromium and Chromium-Nickel Stainless Steel Plate, Sheet, and Strip for Pressure Vessels and for General Applications | paid |
| [ASTM A312](https://store.astm.org/standards/a312_a312m) | Standard Specification for Seamless, Welded, and Heavily Cold Worked Austenitic Stainless Steel Pipes | paid |
| [ASTM A358](https://store.astm.org/standards/a358_a358m) | Standard Specification for Electric-Fusion-Welded Austenitic Chromium-Nickel Stainless Steel Pipe for High-Temperature Service and General Applications | paid |
| [ASTM A213](https://store.astm.org/standards/a213_a213m) | Standard Specification for Seamless Ferritic and Austenitic Alloy-Steel Boiler, Superheater, and Heat-Exchanger Tubes | paid |
| [ASTM A249](https://store.astm.org/standards/a249_a249m) | Standard Specification for Welded Austenitic Steel Boiler, Superheater, Heat-Exchanger, and Condenser Tubes | paid |
| [ASTM A269](https://store.astm.org/standards/a269) | Standard Specification for Seamless and Welded Austenitic Stainless Steel Tubing for General Service | paid |
| [ASTM A182](https://store.astm.org/standards/a182_a182m) | Standard Specification for Forged or Rolled Alloy and Stainless Steel Pipe Flanges, Forged Fittings, and Valves and Parts for High-Temperature Service | paid |
| [ASTM A403](https://store.astm.org/standards/a403_a403m) | Standard Specification for Wrought Austenitic Stainless Steel Piping Fittings | paid |
| [ASTM A351](https://store.astm.org/standards/a351_a351m) | Standard Specification for Castings, Austenitic, for Pressure-Containing Parts | paid |
| [ASTM A790](https://store.astm.org/standards/a790_a790m) | Standard Specification for Seamless and Welded Ferritic/Austenitic Stainless Steel Pipe | paid |
| [ASTM A789](https://store.astm.org/standards/a789_a789m) | Standard Specification for Seamless and Welded Ferritic/Austenitic Stainless Steel Tubing for General Service | paid |
| [ASTM A928](https://store.astm.org/standards/a928_a928m) | Standard Specification for Ferritic/Austenitic (Duplex) Stainless Steel Pipe Electric Fusion Welded with Addition of Filler Metal | paid |
| [ASTM A815](https://store.astm.org/standards/a815_a815m) | Standard Specification for Wrought Ferritic, Ferritic/Austenitic, and Martensitic Stainless Steel Piping Fittings | paid |
| [ASTM A890](https://store.astm.org/standards/a890_a890m) | Standard Specification for Castings, Iron-Chromium-Nickel-Molybdenum Corrosion-Resistant, Duplex (Austenitic/Ferritic) for General Application | paid |
| [ASTM A995](https://store.astm.org/standards/a995) | Standard Specification for Castings, Austenitic-Ferritic (Duplex) Stainless Steel, for Pressure-Containing Parts | paid |
| [ASTM A262](https://store.astm.org/standards/a262) | Standard Practices for Detecting Susceptibility to Intergranular Attack in Austenitic Stainless Steels | paid |
| [ASTM A923](https://store.astm.org/standards/a923) | Standard Test Methods for Detecting Detrimental Intermetallic Phase in Duplex Austenitic/Ferritic Stainless Steels | paid |
| [ASTM G48](https://store.astm.org/standards/g48) | Standard Test Methods for Pitting and Crevice Corrosion Resistance of Stainless Steels and Related Alloys by Use of Ferric Chloride Solution | paid |
| [ASTM A380](https://store.astm.org/standards/a380) | Standard Practice for Cleaning, Descaling, and Passivation of Stainless Steel Parts, Equipment, and Systems | paid |
| [ASTM A967](https://store.astm.org/standards/a967) | Standard Specification for Chemical Passivation Treatments for Stainless Steel Parts | paid |

### Pressure-vessel plate (`vessel-plate`)

| Document | Title | Access |
|---|---|---|
| [ASTM A516](https://store.astm.org/standards/a516_a516m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, for Moderate- and Lower-Temperature Service | paid |
| [ASTM A515](https://store.astm.org/standards/a515_a515m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, for Intermediate- and Higher-Temperature Service | paid |
| [ASTM A285](https://store.astm.org/standards/a285) | Standard Specification for Pressure Vessel Plates, Carbon Steel, Low- and Intermediate-Tensile Strength | paid |
| [ASTM A537](https://store.astm.org/standards/a537_a537m) | Standard Specification for Pressure Vessel Plates, Heat-Treated, Carbon-Manganese-Silicon Steel | paid |
| [ASTM A387](https://store.astm.org/standards/a387_a387m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Chromium-Molybdenum | paid |
| [ASTM A204](https://store.astm.org/standards/a204_a204m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Molybdenum | paid |
| [ASTM A302](https://store.astm.org/standards/a302_a302m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Manganese-Molybdenum and Manganese-Molybdenum-Nickel | paid |
| [ASTM A533](https://store.astm.org/standards/a533_a533m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched and Tempered, Manganese-Molybdenum and Manganese-Molybdenum-Nickel | paid |
| [ASTM A542](https://store.astm.org/standards/a542_a542m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched-and-Tempered, Chromium-Molybdenum, and Chromium-Molybdenum-Vanadium | paid |
| [ASTM A841](https://store.astm.org/standards/a841_a841m) | Standard Specification for Steel Plates for Pressure Vessels, Produced by Thermo-Mechanical Control Process (TMCP) | paid |
| [ASTM A263](https://store.astm.org/standards/a263) | Standard Specification for Stainless Chromium Steel-Clad Plate | paid |
| [ASTM A264](https://store.astm.org/standards/a264) | Standard Specification for Stainless Chromium-Nickel Steel-Clad Plate | paid |
| [ASTM A265](https://store.astm.org/standards/a265) | Standard Specification for Nickel and Nickel-Base Alloy-Clad Steel Plate | paid |
| [ASTM A20](https://store.astm.org/standards/a20_a20m) | Standard Specification for General Requirements for Steel Plates for Pressure Vessels | paid |
| [ASTM A435](https://store.astm.org/standards/a435_a435m) | Standard Specification for Straight-Beam Ultrasonic Examination of Steel Plates | paid |
| [ASTM A578](https://store.astm.org/standards/a578_a578m) | Standard Specification for Straight-Beam Ultrasonic Examination of Rolled Steel Plates for Special Applications | paid |

### Forgings, castings, flanges and fittings (`forgings-castings-fittings`)

| Document | Title | Access |
|---|---|---|
| [ASTM A105](https://store.astm.org/standards/a105_a105m) | Standard Specification for Carbon Steel Forgings for Piping Applications | paid |
| [ASTM A181](https://store.astm.org/standards/a181_a181m) | Standard Specification for Carbon Steel Forgings, for General-Purpose Piping | paid |
| [ASTM A182](https://store.astm.org/standards/a182_a182m) | Standard Specification for Forged or Rolled Alloy and Stainless Steel Pipe Flanges, Forged Fittings, and Valves and Parts for High-Temperature Service | paid |
| [ASTM A266](https://store.astm.org/standards/a266_a266m) | Standard Specification for Carbon Steel Forgings for Pressure Vessel Components | paid |
| [ASTM A336](https://store.astm.org/standards/a336_a336m) | Standard Specification for Alloy Steel Forgings for Pressure and High-Temperature Parts | paid |
| [ASTM A694](https://store.astm.org/standards/a694_a694m) | Standard Specification for Carbon and Alloy Steel Forgings for Pipe Flanges, Fittings, Valves, and Parts for High-Pressure Transmission Service | paid |
| [ASTM A216](https://store.astm.org/standards/a216_a216m) | Standard Specification for Steel Castings, Carbon, Suitable for Fusion Welding, for High-Temperature Service | paid |
| [ASTM A217](https://store.astm.org/standards/a217_a217m) | Standard Specification for Steel Castings, Martensitic Stainless and Alloy, for Pressure-Containing Parts, Suitable for High-Temperature Service | paid |
| [ASTM A351](https://store.astm.org/standards/a351_a351m) | Standard Specification for Castings, Austenitic, for Pressure-Containing Parts | paid |
| [ASTM A234](https://store.astm.org/standards/a234_a234m) | Standard Specification for Piping Fittings of Wrought Carbon Steel and Alloy Steel for Moderate and High Temperature Service | paid |
| [ASTM A860](https://store.astm.org/standards/a860_a860m) | Standard Specification for Wrought High-Strength Ferritic Steel Butt-Welding Fittings | paid |
| [ASTM A961](https://store.astm.org/standards/a961) | Standard Specification for Common Requirements for Steel Flanges, Forged Fittings, Valves, and Parts for Piping Applications | paid |
| [ASME B16.5](https://www.asme.org/codes-standards) | Pipe flanges and flanged fittings (NPS 1/2 through NPS 24) | paid |
| [ASME B16.9](https://www.asme.org/codes-standards) | Factory-made wrought buttwelding fittings | paid |
| [ASME B16.11](https://www.asme.org/codes-standards) | Forged fittings, socket-welding and threaded | paid |

### Bolting (`bolting`)

| Document | Title | Access |
|---|---|---|
| [ASTM A193](https://store.astm.org/standards/a193) | Standard Specification for Alloy-Steel and Stainless Steel Bolting Materials for High-Temperature Service | paid |
| [ASTM A194](https://store.astm.org/standards/a194_a194m) | Standard Specification for Carbon Steel, Alloy Steel, and Stainless Steel Nuts for Bolts for High Pressure or High Temperature Service, or Both | paid |
| [ASTM A320](https://store.astm.org/standards/a320_a320m) | Standard Specification for Alloy-Steel and Stainless Steel Bolting for Low-Temperature Service | paid |
| [ASTM A453](https://store.astm.org/standards/a453_a453m) | Standard Specification for High-Temperature Bolting, with Expansion Coefficients Comparable to Austenitic Stainless Steels | paid |
| [ASTM A540](https://store.astm.org/standards/a540_a540m) | Standard Specification for Alloy-Steel Bolting for Special Applications | paid |
| [ASTM A354](https://store.astm.org/standards/a354) | Standard Specification for Quenched and Tempered Alloy Steel Bolts, Studs, and Other Externally Threaded Fasteners | paid |
| [ASTM A449](https://store.astm.org/standards/a449) | Standard Specification for Hex Cap Screws, Bolts and Studs, Steel, Heat Treated, 120/105/90 ksi Minimum Tensile Strength, General Use | paid |
| [ASTM F593](https://store.astm.org/standards/f593) | Standard Specification for Stainless Steel Bolts, Hex Cap Screws, and Studs | paid |
| [ASTM F594](https://store.astm.org/standards/f594) | Standard Specification for Stainless Steel Nuts | paid |
| [ASTM F1554](https://store.astm.org/standards/f1554) | Standard Specification for Anchor Bolts, Steel, 36, 55, and 105-ksi Yield Strength | paid |
| [ASTM F3125](https://store.astm.org/standards/f3125) | Standard Specification for High Strength Structural Bolts, Steel and Alloy Steel, Heat Treated, 120 ksi (830 MPa) and 150 ksi (1040 MPa) Minimum Tensile Strength, Inch and Metric Dimensions | paid |
| [ASME PCC-1](https://www.asme.org/codes-standards) | Pressure boundary bolted flange joint assembly | paid |

### Boiler, heater and exchanger tube (`exchanger-tube`)

| Document | Title | Access |
|---|---|---|
| [ASTM A178](https://store.astm.org/standards/a178_a178m) | Standard Specification for Electric-Resistance-Welded Carbon Steel and Carbon-Manganese Steel Boiler and Superheater Tubes | paid |
| [ASTM A179](https://store.astm.org/standards/a179_a179m) | Standard Specification for Seamless Cold-Drawn Low-Carbon Steel Heat-Exchanger and Condenser Tubes | paid |
| [ASTM A192](https://store.astm.org/standards/a192_a192m) | Standard Specification for Seamless Carbon Steel Boiler Tubes for High-Pressure Service | paid |
| [ASTM A209](https://store.astm.org/standards/a209_a209m) | Standard Specification for Seamless Carbon-Molybdenum Alloy-Steel Boiler and Superheater Tubes | paid |
| [ASTM A210](https://store.astm.org/standards/a210_a210m) | Standard Specification for Seamless Medium-Carbon Steel Boiler and Superheater Tubes | paid |
| [ASTM A213](https://store.astm.org/standards/a213_a213m) | Standard Specification for Seamless Ferritic and Austenitic Alloy-Steel Boiler, Superheater, and Heat-Exchanger Tubes | paid |
| [ASTM A214](https://store.astm.org/standards/a214_a214m) | Standard Specification for Electric-Resistance-Welded Carbon Steel Heat-Exchanger and Condenser Tubes | paid |
| [ASTM A249](https://store.astm.org/standards/a249_a249m) | Standard Specification for Welded Austenitic Steel Boiler, Superheater, Heat-Exchanger, and Condenser Tubes | paid |
| [ASTM A789](https://store.astm.org/standards/a789_a789m) | Standard Specification for Seamless and Welded Ferritic/Austenitic Stainless Steel Tubing for General Service | paid |
| [ASTM B111](https://store.astm.org/standards/b111) | Standard Specification for Copper and Copper-Alloy Seamless Condenser Tubes and Ferrule Stock | paid |
| [ASTM B163](https://store.astm.org/standards/b163) | Standard Specification for Seamless Nickel and Nickel Alloy Condenser and Heat-Exchanger Tubes | paid |
| [ASTM B338](https://store.astm.org/standards/b338) | Standard Specification for Seamless and Welded Titanium and Titanium Alloy Tubes for Condensers and Heat Exchangers | paid |
| [ASTM A450](https://store.astm.org/standards/a450_a450m) | Standard Specification for General Requirements for Carbon and Low Alloy Steel Tubes | paid |
| [ASTM A1016](https://store.astm.org/standards/a1016_a1016m) | Standard Specification for General Requirements for Ferritic Alloy Steel, Austenitic Alloy Steel, and Stainless Steel Tubes | paid |

### Nickel and high-nickel alloys (`nickel-alloys`)

| Document | Title | Access |
|---|---|---|
| [ASTM B127](https://store.astm.org/standards/b127) | Standard Specification for Nickel-Copper Alloy Plate, Sheet, and Strip | paid |
| [ASTM B160](https://store.astm.org/standards/b160) | Standard Specification for Nickel Rod and Bar | paid |
| [ASTM B162](https://store.astm.org/standards/b162) | Standard Specification for Nickel Plate, Sheet, and Strip | paid |
| [ASTM B168](https://store.astm.org/standards/b168) | Standard Specification for Nickel-Chromium-Aluminum Alloys, Nickel-Chromium-Iron Alloys, Nickel-Chromium-Cobalt-Molybdenum Alloy, Nickel-Iron-Chromium-Tungsten Alloy, and Nickel-Chromium-Molybdenum-Copper Alloy Plate, Sheet, and Strip | paid |
| [ASTM B409](https://store.astm.org/standards/b409) | Standard Specification for Nickel-Iron-Chromium Alloy Plate, Sheet, and Strip | paid |
| [ASTM B424](https://store.astm.org/standards/b424) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Copper Alloys Plate, Sheet, and Strip | paid |
| [ASTM B443](https://store.astm.org/standards/b443) | Standard Specification for Nickel-Chromium-Molybdenum-Columbium Alloy and Nickel-Chromium-Molybdenum-Silicon Alloy Plate, Sheet, and Strip | paid |
| [ASTM B462](https://store.astm.org/standards/b462) | Standard Specification for Forged or Rolled Nickel Alloy Pipe Flanges, Forged Fittings, and Valves and Parts for Corrosive High-Temperature Service | paid |
| [ASTM B564](https://store.astm.org/standards/b564) | Standard Specification for Nickel Alloy Forgings | paid |
| [ASTM B574](https://store.astm.org/standards/b574) | Standard Specification for Low-Carbon Nickel-Chromium-Molybdenum, Low-Carbon Nickel-Molybdenum-Chromium, Low-Carbon Nickel-Molybdenum-Chromium-Tantalum, Low-Carbon Nickel-Chromium-Molybdenum-Copper, and Low-Carbon Nickel-Chromium-Molybdenum-Tungsten | paid |
| [ASTM B575](https://store.astm.org/standards/b575) | Standard Specification for Low-Carbon Nickel-Chromium-Molybdenum, Low-Carbon Nickel-Chromium-Molybdenum-Copper, Low-Carbon Nickel-Chromium-Molybdenum-Tantalum, Low-Carbon Nickel-Chromium-Molybdenum-Tungsten, and Low-Carbon Nickel-Molybdenum-Chromium | paid |
| [ASTM B619](https://store.astm.org/standards/b619) | Standard Specification for Welded Nickel and Nickel-Cobalt Alloy Pipe | paid |
| [ASTM B622](https://store.astm.org/standards/b622) | Standard Specification for Seamless Nickel and Nickel-Cobalt Alloy Pipe and Tube | paid |
| [ASTM B626](https://store.astm.org/standards/b626) | Standard Specification for Welded Nickel and Nickel-Cobalt Alloy Tube | paid |
| [ASTM B366](https://store.astm.org/standards/b366) | Standard Specification for Factory-Made Wrought Nickel and Nickel Alloy Fittings | paid |
| [ASTM G28](https://store.astm.org/standards/g28) | Standard Test Methods for Detecting Susceptibility to Intergranular Corrosion in Wrought, Nickel-Rich, Chromium-Bearing Alloys | paid |

### Titanium and zirconium (`titanium-zirconium`)

| Document | Title | Access |
|---|---|---|
| [ASTM B265](https://store.astm.org/standards/b265) | Standard Specification for Titanium and Titanium Alloy Strip, Sheet, and Plate | paid |
| [ASTM B338](https://store.astm.org/standards/b338) | Standard Specification for Seamless and Welded Titanium and Titanium Alloy Tubes for Condensers and Heat Exchangers | paid |
| [ASTM B348](https://store.astm.org/standards/b348) | Standard Specification for Titanium and Titanium Alloy Bars and Billets | paid |
| [ASTM B363](https://store.astm.org/standards/b363) | Standard Specification for Seamless and Welded Unalloyed Titanium and Titanium Alloy Welding Fittings | paid |
| [ASTM B367](https://store.astm.org/standards/b367) | Standard Specification for Titanium and Titanium Alloy Castings | paid |
| [ASTM B381](https://store.astm.org/standards/b381) | Standard Specification for Titanium and Titanium Alloy Forgings | paid |
| [ASTM B861](https://store.astm.org/standards/b861) | Standard Specification for Titanium and Titanium Alloy Seamless Pipe | paid |
| [ASTM B862](https://store.astm.org/standards/b862) | Standard Specification for Titanium and Titanium Alloy Welded Pipe | paid |
| [ASTM B550](https://store.astm.org/standards/b550_b550m) | Standard Specification for Zirconium and Zirconium Alloy Bar and Wire | paid |
| [ASTM B658](https://store.astm.org/standards/b658_b658m) | Standard Specification for Seamless and Welded Zirconium and Zirconium Alloy Pipe | paid |

### Aluminium and copper alloys (`aluminium-copper`)

| Document | Title | Access |
|---|---|---|
| [ASTM B209](https://store.astm.org/standards/b209) | Standard Specification for Aluminum and Aluminum-Alloy Sheet and Plate | paid |
| [ASTM B221](https://store.astm.org/standards/b221) | Standard Specification for Aluminum and Aluminum-Alloy Extruded Bars, Rods, Wire, Profiles, and Tubes | paid |
| [ASTM B241](https://store.astm.org/standards/b241_b241m) | Standard Specification for Aluminum and Aluminum-Alloy Seamless Pipe and Seamless Extruded Tube | paid |
| [ASTM B247](https://store.astm.org/standards/b247) | Standard Specification for Aluminum and Aluminum-Alloy Die Forgings, Hand Forgings, and Rolled Ring Forgings | paid |
| [ASTM B928](https://store.astm.org/standards/b928) | Standard Specification for High Magnesium Aluminum-Alloy Sheet and Plate for Marine Service | paid |
| [ASTM B42](https://store.astm.org/standards/b42) | Standard Specification for Seamless Copper Pipe, Standard Sizes | paid |
| [ASTM B43](https://store.astm.org/standards/b43) | Standard Specification for Seamless Red Brass Pipe, Standard Sizes | paid |
| [ASTM B88](https://store.astm.org/standards/b88) | Standard Specification for Seamless Copper Water Tube | paid |
| [ASTM B152](https://store.astm.org/standards/b152_b152m) | Standard Specification for Copper Sheet, Strip, Plate, and Rolled Bar | paid |
| [ASTM B466](https://store.astm.org/standards/b466_b466m) | Standard Specification for Seamless Copper-Nickel Pipe and Tube | paid |
| [ASTM B819](https://store.astm.org/standards/b819) | Standard Specification for Seamless Copper Tube for Medical Gas Systems | paid |

### Plastics, FRP, lined pipe, elastomers and gaskets (`nonmetallic`)

| Document | Title | Access |
|---|---|---|
| [ASME B31.3](https://www.asme.org/codes-standards) | Process piping | paid |
| [ASME NM.1](https://www.asme.org/codes-standards) | Thermoplastic piping systems | paid |
| [ASME RTP-1](https://www.asme.org/codes-standards) | Reinforced thermoset plastic corrosion-resistant equipment | paid |
| [ASTM D1784](https://store.astm.org/standards/d1784) | Standard Classification System and Basis for Specification for Rigid Poly(Vinyl Chloride) (PVC) Compounds and Chlorinated Poly(Vinyl Chloride) (CPVC) Compounds | paid |
| [ASTM D1785](https://store.astm.org/standards/d1785) | Standard Specification for Poly(Vinyl Chloride) (PVC) Plastic Pipe, Schedules 40, 80, and 120 | paid |
| [ASTM D2513](https://store.astm.org/standards/d2513) | Standard Specification for Polyethylene (PE) Gas Pressure Pipe, Tubing, and Fittings | paid |
| [ASTM D2837](https://store.astm.org/standards/d2837) | Standard Test Method for Obtaining Hydrostatic Design Basis for Thermoplastic Pipe Materials or Pressure Design Basis for Thermoplastic Pipe Products | paid |
| [ASTM D2992](https://store.astm.org/standards/d2992) | Standard Practice for Obtaining Hydrostatic or Pressure Design Basis for “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe and Fittings | paid |
| [ASTM D2996](https://store.astm.org/standards/d2996) | Standard Specification for Filament-Wound “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe | paid |
| [ASTM D3299](https://store.astm.org/standards/d3299) | Standard Specification for Glass-Fiber-Reinforced Thermoset Resin Corrosion-Resistant Tanks | paid |
| [ASTM D3350](https://store.astm.org/standards/d3350) | Standard Specification for Polyethylene Plastics Pipe and Fittings Materials | paid |
| [ASTM F714](https://store.astm.org/standards/f714) | Standard Specification for Polyethylene (PE) Plastic Pipe (DR-PR) Based on Outside Diameter | paid |
| [ASTM F441](https://store.astm.org/standards/f441_f441m) | Standard Specification for Chlorinated Poly(Vinyl Chloride) (CPVC) Plastic Pipe, Schedules 40 and 80 | paid |
| [ASTM D471](https://store.astm.org/standards/d471) | Standard Test Method for Rubber Property—Effect of Liquids | paid |
| [ASTM D2000](https://store.astm.org/standards/d2000) | Standard Classification System for Rubber Products in Automotive Applications | paid |
| [ASTM F104](https://store.astm.org/standards/f104) | Standard Classification System for Nonmetallic Gasket Materials | paid |
| [NORSOK M-710](https://standard.no/en/sectors/petroleum/norsok-standards/) | Qualification of non-metallic materials and manufacturers | mixed |
| [ISO 23936 (series)](https://www.iso.org/search.html?q=ISO%2023936%20%28series%29) | Non-metallic materials in contact with media related to oil and gas production | paid |

### Insulation and corrosion under insulation (`insulation-cui`)

| Document | Title | Access |
|---|---|---|
| [API RP 583](https://publications.api.org/) | Corrosion under insulation and fireproofing | paid |
| [NACE SP0198](https://www.ampp.org/standards) | Control of corrosion under thermal insulation and fireproofing materials | paid |
| [ASTM C795](https://store.astm.org/standards/c795) | Standard Specification for Thermal Insulation for Use in Contact with Austenitic Stainless Steel | paid |
| [ASTM C692](https://store.astm.org/standards/c692) | Standard Test Method for Evaluating the Influence of Thermal Insulations on External Stress Corrosion Cracking Tendency of Austenitic Stainless Steel | paid |
| [ASTM C871](https://store.astm.org/standards/c871) | Standard Test Methods for Chemical Analysis of Thermal Insulation Materials for Leachable Chloride, Fluoride, Silicate, and Sodium Ions | paid |
| [ASTM C1617](https://store.astm.org/standards/c1617) | Standard Test Method for Quantitative Accelerated Laboratory Evaluation of Extraction Solutions Containing Ions Leached from Thermal Insulation on Aqueous Corrosion of Carbon Steel | paid |
| [ASTM G189](https://store.astm.org/standards/g189) | Standard Guide for Laboratory Simulation of Corrosion Under Insulation | paid |
| [ASTM C1055](https://store.astm.org/standards/c1055) | Standard Guide for Heated System Surface Conditions that Produce Contact Burn Injuries | paid |
| [ASTM C1057](https://store.astm.org/standards/c1057) | Standard Practice for Determination of Skin Contact Temperature from Heated Surfaces Using a Mathematical Model and Thermesthesiometer | paid |

### Wet H2S (sour) service (`sour-service`)

| Document | Title | Access |
|---|---|---|
| [NACE MR0175 / ISO 15156](https://www.ampp.org/standards) | Materials for use in H2S-containing environments in oil and gas production | paid |
| [NACE MR0103 / ISO 17945](https://www.ampp.org/standards) | Metallic materials resistant to sulfide stress cracking in corrosive petroleum refining environments | paid |
| [NACE TM0177](https://www.ampp.org/standards) | Laboratory testing of metals for resistance to sulfide stress cracking and stress corrosion cracking in H2S | paid |
| [NACE TM0284](https://www.ampp.org/standards) | Evaluation of pipeline and pressure vessel steels for resistance to hydrogen-induced cracking | paid |
| [NACE TM0316](https://www.ampp.org/standards) | Four-point bend testing of materials for oil and gas applications | paid |
| [NACE SP0472](https://www.ampp.org/standards) | Methods and controls to prevent in-service environmental cracking of carbon steel weldments in refining | paid |
| [ASTM G39](https://store.astm.org/standards/g39) | Standard Practice for Preparation and Use of Bent-Beam Stress-Corrosion Test Specimens | paid |
| [ASTM F1624](https://store.astm.org/standards/f1624) | Standard Test Method for Measurement of Hydrogen Embrittlement Threshold in Steel by the Incremental Step Loading Technique | paid |
