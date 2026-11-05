"""Glossary of the terms, abbreviations and quantities the toolkit uses, in one data table.

`python -m process_safety glossary [TERM]` searches it and `docs/GLOSSARY.md` is generated from it (a test keeps them in sync).
Definitions are short working definitions for orientation, not the wording of any standard; the standard named in each entry governs.
Entry: (term, expansion, definition, where it applies: a module or standard).
"""
from __future__ import annotations

CATEGORIES: dict[str, list[tuple[str, str, str, str]]] = {
    "Relief, venting and flare": [
        ("PSV / PRV", "Pressure safety valve / pressure relief valve", "A spring or pilot-operated valve that opens at its set pressure to stop pressure rising above a safe limit and recloses when it falls.", "relief; API 520/526"),
        ("Set pressure", "", "The gauge pressure at which a relief valve starts to open.", "relief"),
        ("Relieving pressure", "", "Absolute pressure upstream of the valve while it is relieving: set pressure plus the allowed accumulation, plus atmospheric.", "relief; API 520"),
        ("Accumulation", "", "The pressure rise above the maximum allowable working pressure while the valve relieves, as a fraction of it (10% single valve, 21% fire case).", "relief; API 520/521"),
        ("Back pressure", "", "Pressure at the valve outlet: superimposed (before opening) plus built-up (from flow through the discharge piping).", "relief; API 520-II"),
        ("MAWP", "Maximum allowable working pressure", "The highest gauge pressure a vessel may carry at its design temperature under its code.", "vessel_mech; ASME VIII"),
        ("Orifice letter", "", "The standard effective orifice area designation D to T for a relief valve; the required area is rounded up to the next letter.", "relief; API 526"),
        ("Kd, Kb, Kc, Kw, Kv", "Valve and flow coefficients", "Discharge coefficient (Kd), back-pressure correction (Kb), rupture-disk combination factor (Kc), liquid back-pressure factor (Kw) and viscosity correction (Kv).", "relief; API 520-I"),
        ("Omega method", "Leung omega parameter", "A one-number description of how fast a flashing or two-phase fluid expands as pressure falls; gives the choked mass flux and relief area for two-phase service.", "twophase; API 520-I Annex C"),
        ("Flashing flow", "", "A liquid near its boiling point that partly vaporises as pressure drops through the valve, so the discharge is a two-phase mixture and needs far more area than liquid sizing gives.", "twophase"),
        ("HEM", "Homogeneous equilibrium model", "Two-phase flow modelled as one fluid, with the phases moving together and in thermal equilibrium.", "twophase"),
        ("Critical (choked) flow", "", "Gas flow through an orifice at the speed of sound: downstream pressure no longer raises the flow. Occurs when P2/P1 is below the critical ratio.", "relief"),
        ("Conventional / balanced / pilot-operated", "Valve types", "Conventional valves are affected by back pressure; balanced bellows and pilot-operated valves tolerate more of it.", "relief; API 520-II"),
        ("Wetted area", "", "Vessel surface in contact with liquid up to a height (7.6 m for fire), which absorbs fire heat and boils liquid.", "relief; API 521"),
        ("Environment factor F", "", "Credit for insulation, water spray, drainage or earth cover that reduces fire heat input; 1.0 for a bare vessel.", "relief; API 521"),
        ("Fire case", "", "The relief scenario where an external fire heats the contents: heat input, vapour generated, then valve size.", "relief; API 521"),
        ("Depressuring / blowdown", "", "Deliberately venting a vessel's gas inventory to a safe place to lower pressure in a target time; also used for the pressure fall after a leak.", "depressuring, release; API 521"),
        ("BDV", "Blowdown valve", "A normally closed valve opened on demand to depressure equipment.", "vapour_fire"),
        ("MDMT", "Minimum design metal temperature", "The lowest metal temperature at which a vessel may be pressurised; depressuring can cool gas and metal below it.", "depressuring; ASME VIII"),
        ("Normal / emergency venting", "Tank breathing", "Normal venting handles thermal and liquid-movement breathing; emergency venting handles fire exposure of an atmospheric or low-pressure tank.", "tank_venting; API 2000"),
        ("Nm3/h", "Normal cubic metres per hour", "Gas volume flow expressed at standard conditions.", "tank_venting"),
        ("Rupture disk", "", "A thin pressure-bursting membrane used alone or upstream of a relief valve.", "relief"),
        ("Flare / KO drum", "Flare / knock-out drum", "The elevated burner that disposes of relieved gas, and the vessel upstream that removes liquid droplets from it.", "flare, separator"),
        ("Joukowsky surge", "", "The pressure rise ρ·a·Δv from an instantaneous change in liquid velocity in a pipe (water hammer).", "hydraulics"),
    ],
    "Fire, explosion and dispersion": [
        ("LOC", "Loss of containment", "A release of material from its designed boundary (a hole in a pipe, a vessel rupture).", "qra"),
        ("View factor", "Configuration factor", "The fraction of the radiation leaving one surface that reaches another; incident flux = emissive power x view factor x transmissivity.", "viewfactor"),
        ("Solid-flame model", "", "Treats a flame as a hot radiating solid of defined shape and surface emissive power; better than a point source close to the fire.", "viewfactor, pool_fire"),
        ("Pool fire", "", "A fire burning on a liquid pool; flame size follows the burning rate and pool diameter.", "pool_fire"),
        ("Jet fire", "", "A fire from a pressurised release that burns as a momentum-driven flame.", "qra.effects"),
        ("Flash fire", "", "A short, low-overpressure fire as a flammable cloud burns back to its source; harm is inside the cloud.", "qra.effects"),
        ("BLEVE", "Boiling-liquid expanding-vapour explosion", "Sudden rupture of a vessel holding liquid above its atmospheric boiling point, usually ending in a fireball.", "fireball"),
        ("Fireball", "", "The rising ball of burning vapour after a BLEVE or a large flash release; harm is by thermal radiation.", "fireball"),
        ("VCE", "Vapour cloud explosion", "Combustion of a flammable cloud fast enough, usually from confinement or congestion, to produce damaging overpressure.", "explosion"),
        ("TNT equivalence", "", "Representing the blast of a flammable release by a mass of TNT; the yield fraction is a study assumption.", "explosion"),
        ("Overpressure", "", "Blast pressure above atmospheric (kPa); damage and injury criteria are set at stated overpressures.", "explosion"),
        ("Scaled distance Z", "", "Distance divided by the cube root of the TNT-equivalent mass; blast curves are functions of Z.", "explosion"),
        ("LFL / UFL", "Lower / upper flammable limit", "The vapour concentration range, in air, in which a mixture can burn.", "flammability"),
        ("LOC (inerting)", "Limiting oxygen concentration", "The oxygen level below which a flammable mixture cannot burn; the basis of inerting and purging.", "flammability"),
        ("SEP", "Surface emissive power", "Thermal radiation leaving a flame surface, kW/m².", "pool_fire, flare"),
        ("Radiant fraction", "", "The share of a flame's combustion heat emitted as radiation.", "flare, pool_fire"),
        ("Atmospheric transmissivity τ", "", "The fraction of radiation that reaches a receptor after absorption by air; 1.0 is conservative.", "flare"),
        ("kW/m² harm levels", "", "Radiation thresholds used to place people and equipment, for example 37.5 (equipment damage), 12.5, 4.73 and 1.58 kW/m².", "flare, pool_fire"),
        ("Probit", "", "A transformation that turns a dose of heat, blast or toxic gas into a probability of an effect (fatality) through a normal distribution.", "consequence"),
        ("Thermal dose", "", "Radiation flux raised to a power and multiplied by exposure time; the input to a thermal probit.", "consequence"),
        ("Pasquill-Gifford class", "Atmospheric stability A to F", "A (very unstable) to F (stable) classes that set how fast a plume spreads sideways and vertically.", "dispersion"),
        ("Neutral vs dense gas", "", "A neutral-buoyancy plume mixes like air; a gas heavier than air slumps and spreads along the ground. The toolkit models the former only.", "dispersion"),
        ("PFP", "Passive fire protection", "Insulation or coatings that slow the heating of steel and vessels in a fire.", "structural_fire"),
        ("Am/V", "Section factor", "Heated surface area per unit volume of a steel section; a higher value heats faster.", "structural_fire"),
        ("Hydrocarbon curve / ISO 834", "Standard fire curves", "Temperature against time for a hydrocarbon pool fire (fast) and a cellulosic building fire (slower).", "structural_fire"),
        ("ATEX / hazardous area zone", "", "Classification of areas where explosive atmospheres may occur: zones 0/1/2 for gas and 20/21/22 for dust.", "atex; IEC 60079-10"),
        ("EPL", "Equipment protection level", "The level of protection an item of equipment needs for its zone (Ga, Gb, Gc, Da, Db, Dc).", "atex; electrical"),
        ("T-class / gas group", "", "The maximum surface temperature class and the gas group (by maximum experimental safe gap) that explosion-protected equipment must match.", "electrical"),
    ],
    "Risk, reliability and safety management": [
        ("FEL 1 / Class 5 estimate", "Front-end loading 1; AACE Class 5", "The concept-stage capital estimate, based on analog projects or capacity factoring, with a wide accuracy range; good for screening, not for a budget or investment decision.", "lng_cost"),
        ("Analog (cost estimating)", "Reference project", "A past project with published cost used, after adjustment for size, date, location and scope, to estimate a new one.", "lng_cost"),
        ("Capacity factoring / size exponent", "Six-tenths rule and variants", "Scaling cost with capacity raised to an exponent below 1 (0.6 to 0.8 for LNG trains) to reflect economies of scale.", "lng_cost"),
        ("Location factor / cost index", "", "Multipliers for where and when a plant is built relative to a reference (for example US Gulf Coast at a base date); the toolkit ships none and requires them as inputs.", "lng_cost"),
        ("PCN", "Process control network", "The network of controllers, I/O, switches and servers that runs the process control and safety systems; modifying it needs engineering, factory and site acceptance testing, cybersecurity measures and change control.", "design_workflow"),
        ("SIF voting (1oo1, 2oo3)", "Sensor voting architecture", "How many redundant sensors must agree to trip: 2oo3 tolerates one sensor failure without a spurious trip or a missed demand, at the cost of more instruments, cable and I/O.", "sil, design_workflow"),
        ("FAT / SAT", "Factory / site acceptance test", "Testing of control or safety system changes at the vendor (FAT) and after installation on site (SAT) before they go live.", "design_workflow"),
        ("Pipeline rerouting", "", "Replacing a line with a new route: demolition of the old line, new pipe, fittings, supports, tie-ins and civil work, with the hydraulic effect of the longer route checked.", "design_workflow"),
        ("HMB", "Heat and material balance", "The table of flow, composition, temperature, pressure, phase and energy for every stream in a flowsheet, for each operating case, produced by a process simulator.", "hmb"),
        ("PFS / PEFS / PSFS", "Process flow scheme / process engineering flow scheme / process safeguarding flow scheme", "Operator document names for the flow diagram, the P&ID-level engineering diagram, and the diagram showing the safeguards (relief, trips, detection) relied on by the studies; expansions assumed from common usage.", "plant_model"),
        ("Proteus / DEXPI", "P&ID exchange format", "An XML schema (ProteusXML) and information model (DEXPI) for exchanging piping and instrumentation diagram data between engineering tools.", "plant_model"),
        ("Why chain", "", "The reasoning from a process condition to a scenario, the gap it exposes, and the recommendation type a study raises, with the numbers at each step.", "scenario_ingest"),
        ("DEP / design practice", "Design and engineering practice", "A company's controlled document set stating mandatory (shall) and recommended (should) design requirements; projects run a gap analysis of their design against it.", "requirements_extract"),
        ("Process safeguarding memorandum", "", "A project document that records the safeguards (relief, trips, interlocks, detection) relied on to control each hazard and the basis for them, kept alongside the flow schemes.", "plant_model, scenario_ingest"),
        ("Process control narrative", "", "A written description of how the control and shutdown systems are intended to operate, including set points, interlocks and operating modes.", "design_workflow"),
        ("Shall / should", "Normative language", "In requirement documents, 'shall' states a mandatory requirement and 'should' a recommendation; 'shall not' a prohibition.", "requirements_extract"),
        ("Derogation", "", "A formal, recorded and approved departure from a mandatory (MUST) design requirement for a stated scope and period, backed by a justification, a risk assessment, compensating measures and an approver of enough seniority; it expires or is reviewed. Not available for statutory requirements, which need the regulator's exemption.", "compliance"),
        ("Must / should / can (compliance tiers)", "", "MUST: comply or hold an approved derogation. SHOULD: comply or explain (documented justification, discipline-level approval). CAN: optional, record whether adopted; no derogation is needed.", "compliance"),
        ("TA1 / TA2 / TA3", "Technical authority levels", "Tiers of engineering sign-off authority, here TA3 (site / discipline) < TA2 (project / regional discipline) < TA1 (principal / corporate); the approval matrix sets which a derogation needs from its tier and consequence class. Level meanings are an assumption to adapt.", "compliance"),
        ("PESTLE", "Political, Economic, Social, Technological, Legal, Environmental", "A checklist for mapping the wider consequences of a scenario; in the compliance module each factor is rated 0-5 for a derogation's failure scenario, a rating of 3 or more needs a management action, and the highest rating sets the consequence class.", "compliance"),
        ("Comply or explain", "", "The rule for recommended (SHOULD) requirements: follow them, or record why a different approach is acceptable; no formal derogation is required.", "compliance"),
        ("ICAF", "Implied cost of averting a fatality", "Cost of a risk-reduction measure divided by the fatalities it is expected to avert over its life; compared with the value of preventing a fatality in the ALARP cost-benefit test.", "recommendation_cost, qra.alarp"),
        ("Indirect costs", "", "Costs on top of direct construction cost: engineering, procurement, construction management, owner's cost, commissioning and escalation, usually as percentages of direct cost.", "recommendation_cost"),
        ("Safety study recommendation", "HAZOP / LOPA / QRA action", "A change proposed by a hazard study to reduce risk: for example a piping change, a civil protection, an electrical upgrade or an instrumented function.", "recommendation_cost"),
        ("Turnaround / shutdown", "Planned outage", "A planned period when a unit or plant is taken out of service for inspection, repair and reinstatement; its length and cost are the subject of schedule and cost risk analysis.", "shutdown_risk"),
        ("QSRA / QCRA", "Quantitative schedule / cost risk analysis", "Monte Carlo analysis of a project network (schedule) or cost estimate (cost) using ranges and risk events instead of single-point values.", "shutdown_risk"),
        ("P50 / P80", "Confidence levels", "The value that the outcome is at or below in 50% (P50) or 80% (P80) of simulated runs; contingency is often set as P80 minus the base estimate.", "shutdown_risk"),
        ("S-curve", "Cumulative probability curve", "The simulated outcomes sorted into cumulative probability against duration or cost, from which P-values are read.", "shutdown_risk"),
        ("Criticality index", "", "The share of simulation runs in which an activity lies on a zero-float (critical) path.", "shutdown_risk"),
        ("Opportunity cost (shutdown)", "Lost margin", "Contribution margin forgone for each operating day the plant is not producing, including ramp-down and ramp-up, less any production recoverable later.", "shutdown_risk"),
        ("On-stream factor", "Operating availability", "The share of the year a plant is operating; a shutdown overrun lowers it day for day.", "shutdown_risk"),
        ("HAZID", "Hazard identification", "A structured workshop listing hazards from a checklist of causes by area or activity.", "qra.hazid"),
        ("HAZOP", "Hazard and operability study", "A team review of each process node using guidewords (no, more, less) applied to parameters to find deviations and their causes.", "hazop; IEC 61882"),
        ("PHA", "Process hazard analysis", "The umbrella term for HAZOP, what-if and similar studies; revalidated on a cycle.", "pha; OSHA 1910.119"),
        ("CHAZOP / SWIFT / What-if", "", "Variants of a hazard review for control systems, with structured what-if questions, or open questions.", "pha"),
        ("LOPA", "Layer of protection analysis", "A semi-quantitative method that compares an initiating-event frequency, reduced by independent protection layers, with a tolerable frequency.", "sil; CCPS"),
        ("IPL", "Independent protection layer", "A safeguard that is independent, specific, dependable and auditable; each is credited with a probability of failure on demand.", "sil"),
        ("SIF / SIS", "Safety instrumented function / system", "An instrumented loop (sensor, logic solver, final element) that brings a process to a safe state.", "sil, sil_lifecycle; IEC 61511"),
        ("SIL", "Safety integrity level", "One of four discrete levels of required (SIL 1 to 4) or achieved risk reduction for a safety function.", "sil; IEC 61508/61511"),
        ("PFD / PFDavg", "Probability of failure on demand", "The chance a safety function fails when called; averaged over the proof-test interval for a low-demand function.", "sil"),
        ("RRF", "Risk reduction factor", "1 / PFD: how much a safeguard reduces risk. SIL 2 is a factor of 100 to 1,000.", "sil"),
        ("HFT / SFF", "Hardware fault tolerance / safe failure fraction", "Redundancy and the share of failures that are safe or detected; together they cap the SIL an architecture can claim.", "sil_lifecycle; IEC 61508 Route 1H"),
        ("λDU", "Dangerous undetected failure rate", "The rate per hour of failures that disable a safety function without being detected until a proof test.", "sil"),
        ("Proof test", "", "A periodic test that reveals hidden dangerous failures; a longer interval raises the average PFD.", "sil"),
        ("1oo2, 2oo3", "Voting architectures", "k-out-of-n logic: 1oo2 trips if either of two channels demands, 2oo3 if two of three do.", "sil, reliability"),
        ("Common-cause (β) factor", "", "The share of failures that hit redundant channels together; limits the benefit of redundancy.", "sil"),
        ("Bow-tie", "", "A diagram with threats and preventive barriers on the left of a top event and mitigating barriers and consequences on the right.", "bowtie"),
        ("SCE", "Safety-critical element", "A barrier whose failure would cause or fail to limit a major accident; the toolkit flags those with high risk-achievement importance.", "bowtie"),
        ("RRW / RAW", "Risk reduction / achievement worth", "How much risk falls if a barrier is perfect (RRW) and how much it rises if the barrier fails (RAW).", "bowtie"),
        ("QRA", "Quantitative risk assessment", "A study that estimates the frequency and consequence of accidents to produce individual and societal risk.", "qra; CCPS CPQRA"),
        ("IR / IRPA / LSIR", "Individual risk", "Chance of fatality per year to a person: at a location (LSIR) or for a person with a given occupancy pattern (IRPA).", "qra.risk"),
        ("PLL", "Potential loss of life", "Expected fatalities per year summed over all people and events.", "qra.risk"),
        ("F-N curve", "", "Frequency of N or more fatalities against N; used to judge societal risk.", "qra.risk"),
        ("ALARP", "As low as reasonably practicable", "The principle that risk between the intolerable and broadly acceptable limits must be reduced unless the cost is grossly disproportionate.", "qra.alarp; HSE R2P2"),
        ("VPF", "Value of a prevented fatality", "The monetary value used in a cost-benefit test of a risk-reduction measure; a policy input, not data.", "qra.alarp"),
        ("R2P2 / Bevi", "Risk criteria", "The UK HSE (Reducing Risks, Protecting People) and Dutch (Besluit externe veiligheid inrichtingen) individual and societal risk criteria used as presets.", "qra.alarp"),
        ("MCLS", "Maximum credible loss scenario", "The worst release the study treats as credible; sets emergency planning distances.", "qra.emergency"),
        ("ERDMP", "Emergency response and disaster management plan", "A site plan scaled to the consequence zones; PNGRB sets the Indian requirement for gas facilities.", "qra.emergency"),
        ("MAH", "Major accident hazard", "A hazard at a site that holds hazardous substances above set thresholds.", "mah"),
        ("Seveso III", "EU Directive 2012/18/EU", "The EU regime for sites with dangerous substances, with lower and upper tiers set by the sum of quantity-to-threshold ratios.", "mah"),
        ("MSIHC Rules", "Manufacture, Storage and Import of Hazardous Chemicals Rules, 1989", "The Indian regulations for hazardous chemical sites; the toolkit does not reproduce their schedules.", "mah; India"),
        ("OISD / PNGRB / PESO", "Indian regulators and bodies", "Oil Industry Safety Directorate (standards), Petroleum and Natural Gas Regulatory Board, and Petroleum and Explosives Safety Organisation (licensing).", "standards; India"),
        ("PSM", "Process safety management", "OSHA's 14-element management system for sites above threshold quantities of highly hazardous chemicals (29 CFR 1910.119).", "psm; OSHA"),
        ("RBPS", "Risk Based Process Safety", "The CCPS framework of 20 elements for managing process safety.", "psm; CCPS"),
        ("RMP", "Risk Management Program", "The US EPA program for sites above threshold quantities of regulated substances (40 CFR 68).", "rmp; EPA"),
        ("PSSR / MOC", "Pre-startup safety review / management of change", "Checks before startup of new or changed facilities, and the control of changes to them.", "psm"),
        ("FMEA / RPN", "Failure modes and effects analysis / risk priority number", "A review of how each component can fail; the RPN multiplies severity, occurrence and detection scores.", "reliability"),
        ("Fault tree / event tree", "", "A tree from a top event down to its causes (fault tree), and from an initiating event out to its outcomes (event tree).", "reliability, qra.eta"),
        ("RAM", "Reliability, availability and maintainability", "Study of how failures and repairs limit a production train's output.", "ram; ISO 20815"),
        ("TMRad / TD24 / MTSR", "Thermal runaway measures", "Time to maximum rate under adiabatic conditions, the temperature at which that is 24 hours, and the maximum temperature after cooling failure.", "thermal_runaway; Stoessel"),
    ],
    "Electrical, mechanical and exposure": [
        ("Arc flash", "", "An explosive electrical discharge through air; harm is by heat and pressure.", "electrical"),
        ("Incident energy", "", "Heat per unit area at a working distance from an arc (J/cm² or cal/cm²); sets protective clothing and the arc-flash boundary.", "electrical; IEEE 1584"),
        ("Arc-flash boundary", "", "The distance at which incident energy is 1.2 cal/cm², the onset of a second-degree burn.", "electrical"),
        ("IDMT / TMS", "Inverse definite minimum time / time multiplier setting", "A relay whose operating time falls as fault current rises; the TMS scales the curve.", "electrical; IEC 60255"),
        ("Touch / step voltage", "", "The voltage a person bridges by touching a grounded object or by stepping across the ground during a fault; limited by body-current criteria.", "electrical; IEEE 80"),
        ("Cs", "Surface-layer derating factor", "Reduces the tolerable voltages for a thin surface layer such as crushed rock.", "electrical; IEEE 80"),
        ("Rolling sphere", "", "A lightning protection method: any point a sphere of a set radius can touch is exposed to a strike.", "electrical; IEC 62305"),
        ("PL / PFHd", "Performance level / probability of dangerous failure per hour", "The level of a machinery safety function under ISO 13849-1, and its failure-rate band.", "mechanical_safety"),
        ("Safeguard distance", "", "The minimum distance from a hazard for a protective device, from stopping time and detection capability.", "mechanical_safety; ISO 13855"),
        ("TWA / dose / PEL", "Time-weighted average / noise dose / permissible exposure limit", "OSHA's 90 dBA for 8 hours equals 100% dose; every 5 dB rise halves the permitted time.", "noise; OSHA 1910.95"),
    ],
    "Hydraulics and process": [
        ("Reynolds number", "Re", "Ratio of inertial to viscous forces in a flow; sets the friction regime.", "hydraulics"),
        ("Darcy-Weisbach / Colebrook", "", "The pressure-drop equation for pipe flow, and the correlation for its friction factor in turbulent flow.", "hydraulics"),
        ("Erosional velocity", "", "A velocity limit (API RP 14E: C/√ρ) above which flow can erode pipe walls.", "hydraulics"),
        ("Kv / Cv", "Valve flow coefficients", "Flow through a valve at unit pressure drop, in metric (Kv, m³/h at 1 bar) or US (Cv) units.", "hydraulics"),
        ("NPSH", "Net positive suction head", "Pressure margin above vapour pressure at a pump suction; the available value must exceed the required.", "hydraulics"),
        ("Water hammer", "", "A pressure surge from a rapid change of liquid velocity, travelling at the pipe's wave speed.", "hydraulics"),
        ("Critical time 2L/a", "", "The round-trip time of a pressure wave; closures faster than this are treated as instantaneous.", "hydraulics"),
        ("Hazen-Williams", "", "An empirical friction formula for water in fire-fighting and distribution pipework (NFPA 13).", "fire_water"),
        ("Impoundment", "", "A bund or basin sized to hold a spill; 49 CFR 193.2181 sets it for LNG tanks.", "lng"),
        ("Boil-off", "", "Vapour generated by heat ingress into a cryogenic tank.", "lng, lpg"),
        ("Regasification duty", "", "The heat needed to warm and vaporise LNG to send-out gas.", "lng"),
        ("Potential impact radius", "PIR", "The radius within which a gas pipeline rupture could harm people (49 CFR 192.903).", "pipeline"),
    ],
    "Data centres": [
        ("PUE", "Power usage effectiveness", "Total facility power divided by IT power; 1.0 would mean no overhead.", "datacentre"),
        ("UPS / DoD", "Uninterruptible power supply / depth of discharge", "Battery-backed power to ride through an outage, and the usable share of battery capacity.", "datacentre"),
        ("N, N+1, 2N", "Redundancy", "Capacity for the load (N), with one spare unit (N+1), or two full independent paths (2N).", "datacentre"),
        ("Tier (Uptime / TIA-942)", "", "A classification of data-centre resilience; the toolkit deliberately codes no tier percentages.", "datacentre"),
    ],
    "Using the toolkit": [
        ("Screening", "", "A quick, conservative-or-order-of-magnitude calculation to decide what needs a full study; not a design.", "all modules"),
        ("Hard / soft range", "", "A hard range is physically impossible outside it (rejected); a soft range is the typical engineering range (warns).", "ranges"),
        ("Illustrative input", "", "A value chosen to show how a command works; replace it with site or vendor data before any decision.", "docs, examples"),
        ("Override hook", "", "The way an external consequence tool's footprints (Phast, RISKCURVES) replace the toolkit's own models inside a QRA study.", "qra.effects"),
    ],
}


def entries() -> list[dict]:
    out = []
    for cat, items in CATEGORIES.items():
        for term, expansion, definition, where in items:
            out.append({"category": cat, "term": term, "expansion": expansion, "definition": definition, "applies_to": where})
    return out


def search(query: str) -> list[dict]:
    """Case-insensitive match on the term, its expansion or the definition text; term matches are listed first."""
    q = query.strip().lower()
    hits = [e for e in entries() if q in e["term"].lower() or q in e["expansion"].lower() or q in e["definition"].lower()]
    return sorted(hits, key=lambda e: (q not in e["term"].lower(), q not in e["expansion"].lower(), e["term"].lower()))


def markdown() -> str:
    lines = ["# Glossary", "",
             "Generated from `process_safety/glossary.py` (`python -m process_safety glossary --markdown`); a test keeps this file in sync. "
             "These are short working definitions for orientation, not the wording of any standard: the standard named in each entry governs. "
             "Search from the command line with `python -m process_safety glossary TERM`.", ""]
    for cat, items in CATEGORIES.items():
        lines += [f"## {cat}", "", "| Term | Meaning | Applies to |", "|---|---|---|"]
        for term, expansion, definition, where in items:
            name = f"**{term}**" + (f" ({expansion})" if expansion else "")
            lines.append(f"| {name} | {definition} | {where} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
