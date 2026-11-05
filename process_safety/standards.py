"""Coverage map: Typical process-safety consultancy scope -> governing standards -> what this package implements.

OISD titles/editions come from data/oisd_standards.json (copied from the refinery-design-opensource repo, which fetched them from
oisd.gov.in on 2026-09-21 with `curl`). The standards' text was not read. International/statutory entries are from the user's
reference list and general knowledge; confirm current editions.
"""
from __future__ import annotations

import json
from importlib import resources

STATUTORY = {
    "OSHA PSM": "29 CFR 1910.119 (14 elements, highly hazardous chemicals)",
    "EPA RMP": "40 CFR Part 68",
    "CCPS RBPS": "Risk Based Process Safety (20 elements) - framework, not a regulation",
    "IEC 61511": "Functional safety, SIS for the process sector (with IEC 61508)",
    "ISO 45001": "Occupational health & safety management",
    "AIGA 099": "Process Safety Management guideline (industrial gases)",
    "MSIHC Rules 1989": "India: Manufacture, Storage and Import of Hazardous Chemicals Rules",
    "PESO": "India: petroleum/explosives/pressure-vessel safety rules (SMPV, Petroleum Rules)",
    "Seveso III": "EU Directive 2012/18/EU major-accident hazards",
}

# topic -> (standards, module.function or None, status)
TOPICS = {
    "PSV / relief sizing (overpressure scenarios)": (["API 520-I/II", "API 521", "API 526", "API 527", "OISD-STD-106", "ASME VIII UG-125..."], "relief.gas_area/steam_area/liquid_area/select_orifice", "implemented"),
    "Fire case relief (liquid-wetted)": (["API 521 s.4.4", "OISD-STD-106"], "relief.fire_relief_rate_kg_h, wetted_area_cylinder", "implemented"),
    "Fire case relief (vapour-filled)": (["API 521", "Safety 2018 4(1) 11 (doi:10.3390/safety4010011)"], "vapour_fire.simulate", "transient screening model; the API 521 F' shortcut is deliberately NOT coded (constants unverifiable)"),
    "Other relief scenarios (thermal expansion, tube rupture, flare header)": (["API 521 Part I", "API 520"], "scenarios.*", "thermal expansion / 10-13 rule / tube rupture / header Mach implemented; catalogue of all scenarios"),
    "Vessel sizing (separator, flare KO drum)": (["API 12J", "API 521", "GPSA"], "separator.*", "conceptual Souders-Brown + holdup sizing; K values are inputs"),
    "Flare & cold-vent radiation / dispersion": (["API 521", "OISD-STD-106", "OISD-STD-109"], "flare.*", "radiation implemented; dispersion not"),
    "SIL assessment (LOPA)": (["IEC 61511", "OISD-STD-152", "OISD-STD-153", "CCPS LOPA"], "sil.lopa", "implemented"),
    "SIL verification (PFDavg)": (["IEC 61511", "IEC 61508-6"], "sil.pfd_avg, sif_pfd, max_proof_test_interval_h", "implemented (no HFT/SFF check)"),
    "BLEVE / fireball": (["CCPS", "TNO Yellow Book"], "fireball.*", "radiation only; blast/fragments not"),
    "Pool/jet fire, explosion, dispersion (QRA)": (["CCPS", "OISD-STD-116", "PNGRB T4S"], "qra.effects", "screening models wired into the QRA; external Phast/RISKCURVES results can override any footprint"),
    "Bow-tie / barrier management / SCE": (["CCPS bow-tie", "Energy Institute"], "bowtie", "quantified bow-tie with RRW/RAW and SCE list"),
    "Occupied building risk / building radiation impact": (["API RP 752/753", "Purple Book"], "qra.buildings", "Purple Book discrete or custom curves; no BDL/P-I"),
    "MCLS, emergency planning zones, ERDMP": (["PNGRB ERDMP 2010", "MSIHC 1989", "MoEF EIA TGM"], "qra.emergency", "distances, zones A/B/C, Level 1/2/3 approximation"),
    "SIL verification / SRS / risk graph": (["IEC 61511-1:2016 Table 6", "IEC 61508-2 Route 1H"], "sil_lifecycle", "PFD + HFT/SFF; no SC or proof-test coverage"),
    "Fire & gas mapping": (["ISA TR84.00.07"], "fg_mapping", "2D geographic coverage + greedy optimiser"),
    "CHAZOP / What-if / SWIFT / PSSR / SIMOPS / PHA revalidation": (["CCPS", "OSHA 1910.119(e)(6)"], "pha", "worksheets, action tracking, revalidation"),
    "Thermal runaway (TMRad, TD24, Stoessel class)": (["Stoessel"], "thermal_runaway", "zero-order screening"),
    "ATEX / EPD / dust class": (["ATEX 2014/34/EU", "IEC 60079-10-1/-10-2"], "atex", "classification only; no zone extent or vent sizing"),
    "RAM": (["ISO 20815"], "ram", "Monte Carlo k-of-n with analytic check"),
    "Quantitative risk assessment (LSIR, IRPA, F-N, PLL, ALARP)": (["HSE R2P2", "Bevi / Purple Book", "CCPS CPQRA", "OISD-STD-118 (not read)"], "qra.study.run",
        "six-step workflow; generic frequencies only where a public source was read; criteria presets UK R2P2 and NL Bevi, India via custom"),
    "Layout / separation distances": (["OISD-STD-118", "OISD-STD-163"], None, "not implemented"),
    "Hazardous area classification": (["IEC 60079-10-1", "OISD-STD-113", "API RP 505"], "flammability.zone_from_release_hours", "only the duration rule of thumb; extents and ventilation analysis not implemented"),
    "F&G detector mapping": (["OISD-STD-116", "ISA TR84.00.07"], None, "not implemented (3D geometry tool)"),
    "Line sizing / hydraulics / erosional velocity": (["Darcy-Weisbach", "API RP 14E"], "hydraulics.incompressible_dp_kpa, isothermal_gas_outlet_kpa, erosional_velocity_m_s", "implemented"),
    "Control valve (liquid) / pump NPSH / affinity": (["IEC 60534-2-1", "Hydraulic Institute"], "hydraulics.kv_liquid, npsha_m, pump_affinity", "implemented (gas Cv not)"),
    "Surge / water hammer": (["Joukowsky"], "hydraulics.wave_speed_m_s, surge_screen", "screening only; method of characteristics not"),
    "Fire water hydraulics and demand": (["NFPA 13/15/24 (Hazen-Williams)", "OISD-STD-116/117 (not read)"], "fire_water.*", "arithmetic implemented; application rates are inputs"),
    "Pressure-vessel thickness / MAWP": (["ASME VIII-1 UG-27/UG-32"], "vessel_mech.*", "thin-wall formulas; S is an input"),
    "Release source terms / blowdown": (["CCPS", "TNO Yellow Book"], "release.*", "hole releases + adiabatic blowdown; flashing/two-phase not"),
    "Atmospheric dispersion (screening)": (["Briggs/Pasquill-Gifford"], "dispersion.*", "neutral-buoyancy Gaussian only; dense gas not"),
    "Explosion overpressure": (["TNT equivalence", "Kinney-Graham"], "explosion.*", "TNT/Brode only; multi-energy / Baker-Strehlow not"),
    "Injury probits (thermal, toxic)": (["Eisenberg", "TNO Purple Book"], "consequence.*", "implemented; constants to verify"),
    "Fault tree / event tree / availability / FMEA": (["IEC 61025", "IEC 62502", "IEC 60812"], "reliability.*", "implemented (independent events)"),
    "HAZOP worksheet generation": (["IEC 61882", "CCPS"], "hazop.generate/to_csv", "worksheet skeleton + generic cause prompts; the study itself is a team exercise"),
    "Combustion / flare emissions": (["GHG Protocol", "CPCB/MoEFCC rules (not read)"], "emissions.*", "element balance; efficiency/GWP are inputs"),
    "Reaction hazard screening (chemicals / pharma)": (["Stoessel", "DIERS"], "reaction_hazard.*", "dT_ad and MTSR only; calorimetry, criticality classes, runaway vent sizing not"),
    "Two-phase / flashing relief discharge": (["API 520-I Annex C (method named, not read)", "DIERS"], "twophase.*", "omega method, homogeneous equilibrium, choked and subcritical flux; bundled CoolProp saturated-liquid data for 18 fluids (two-point omega within 2.2% of direct HEM integration); no subcooled, mixture or reactive-system (DIERS) sizing"),
    "Near-field solid-flame radiation (view factor)": (["CCPS", "TNO Yellow Book"], "viewfactor.*", "numerical view factor from flat rectangular faces; no tilt model, no blockage"),
    "Pool fire (burn rate, flame, radiation)": (["CCPS", "TNO Yellow Book", "OISD-STD-116"], "pool_fire.*", "screening point-source; no wind tilt or spreading"),
    "Flammability, LOC, inerting / purging": (["NFPA 69", "CCPS", "API RP 2216"], "flammability.*", "Le Chatelier, LOC, purge cycles; limits/targets are inputs"),
    "Static electricity (relaxation, v.d)": (["API RP 2003", "OISD-RP-110", "IEC 60079-32-1"], "flammability.relaxation_time_s, pipe_charging_check", "screening; criterion is an input"),
    "Structural fire / passive fire protection": (["EN 1993-1-2", "EN 1991-1-2", "API 2218", "OISD-STD-116"], "structural_fire.*", "lumped steel temperature, ISO 834 + hydrocarbon curves; fire-test certification governs real PFP"),
    "Emergency depressuring / blowdown + MDMT": (["API 521 s.4.6"], "depressuring.*", "gas-phase isothermal/adiabatic bounds; liquid flashing not modelled"),
    "Overfill protection (alarm placement)": (["API 2350", "IEC 61511", "OISD-STD-108"], "overfill.*", "volume/time arithmetic; criteria are inputs"),
    "PSV inlet loss (3%) and outlet reaction force": (["API 520-II"], "relief_piping.*", "implemented; AIV/FIV and stress not"),
    "PSM management system (OSHA 14 elements, AIGA 99, RBPS)": (["OSHA 29 CFR 1910.119", "AIGA 99/20", "CCPS RBPS", "CSChE PSM Standard", "DOE-HDBK-1101-96"], "psm.*", "applicability, cadences, due dates, crosswalk, gap scoring; verified against OSHA text"),
    "MAH classification (Seveso sum rule)": (["Directive 2012/18/EU Annex I", "MSIHC Rules 1989 (schedules not read)", "OISD-STD-206/GDN"], "mah.*", "EU thresholds from official text; Indian MSIHC schedules not implemented"),
    "Gas pipeline design pressure / impact radius": (["49 CFR 192", "ASME B31.8 / B31.4", "OISD-STD-226 (not read)", "PNGRB T4S (not read)"], "pipeline.*", "US rule text verified; Indian requirements not implemented"),
    "LNG: impoundment, boil-off, regas duty, liquefaction work": (["49 CFR 193", "NFPA 59A", "EN 1473", "OISD-STD-194"], "lng.*, props.*", "impoundment + dispersion parameters verified from 49 CFR 193; siting models (LNGFIRE3, DEGADIS) not reproduced"),
    "LPG: vapour pressure, density, filling ratio, boil-off": (["API 2510/2510A", "NFPA 58", "OISD-STD-144/150/236", "IS 2825"], "lpg.*, props.*", "Lee-Kesler/Rackett correlations; code filling limits are inputs"),
    "US EPA RMP applicability and worst-case criteria": (["40 CFR 68"], "rmp.*", "77 toxics + 63 flammables parsed from the rule; distances are order-of-magnitude screening"),
    "Refinery/petrochemical flare-system loads (coincident relief)": (["API 521"], "flare_system.*", "aggregation arithmetic; cause-and-effect coincidence is an input"),
    "Furnace purge, peroxide decomposition, exotherm bookkeeping": (["NFPA 86/85", "API 556", "DIERS"], "plant_units.*", "bookkeeping only; project data required"),
    "Short-circuit levels, cable sizing, voltage drop, motor starting": (["IEC 60909", "IEC 60364", "IEEE 141/399"], "electrical.*", "hand-calculation forms; load-flow/short-circuit studies need software"),
    "Overcurrent relay curves and grading": (["IEC 60255-151", "IEEE C37.112"], "electrical.idmt_time_s, grading_check", "curve arithmetic; coordination study not implemented"),
    "Earthing: tolerable touch/step voltage, rod resistance": (["IEEE 80", "IEC 61936-1 / EN 50522"], "electrical.*", "tolerable voltages and rod only; grid design/mesh voltage not implemented"),
    "Lightning protection (rolling sphere, collection area)": (["IEC 62305", "NFPA 780", "IS/IEC 62305"], "electrical.*", "geometry and strike frequency; full risk assessment (R1-R4) not implemented"),
    "Hazardous-area electrical equipment selection (Ex)": (["IEC 60079-0/-14/-20-1", "OISD-STD-113", "NFPA 70/497"], "electrical.allowed_t_classes, gas_group_from_mesg, min_epl_for_zone", "selection arithmetic; classification extents not implemented"),
    "Arc flash (screening)": (["NFPA 70E Annex D", "IEEE 1584", "OSHA 1910.269 App. E"], "electrical.lee_*", "Lee method with OSHA applicability limits; IEEE 1584 not implemented"),
    "Occupational noise": (["OSHA 1910.95", "NIOSH REL", "IS/BS 7445 (environmental, not implemented)"], "noise.*", "OSHA dose/TWA verified; environmental noise limits not implemented"),
    "Machinery safety (PL, safeguard distance)": (["ISO 13849-1", "ISO 13855", "IEC 62061"], "mechanical_safety.required_pl, safeguard_distance_mm", "risk graph + PFH bands; pre-2024 ISO 13855 form"),
    "Lifting, dropped objects, vehicle/ship impact": (["ASME B30.9", "DNV-RP-C204", "NORSOK N-004"], "mechanical_safety.*", "energy and tension arithmetic; design codes govern"),
    "Pipe spans, thermal growth, bolt torque": (["ASME B31.3", "ASME PCC-1"], "mechanical_safety.*", "screening forms; stress analysis supersedes"),
    "Data centre: PUE, cooling-water balance, evaporative water, UPS battery, diesel storage": (["EN 50600 / ISO/IEC 22237 (PUE definition; not read)", "ASHRAE TC 9.9 (not read)"], "datacentre.*", "arithmetic with project inputs; no tier or thermal-envelope values coded"),
    "Data centre: redundancy availability (N+1, 2N)": (["Uptime Institute tiers (not read)", "ANSI/TIA-942 (not read)"], "datacentre.k_of_n_availability, dual_path_availability", "independent-units arithmetic; tier percentages deliberately not coded"),
    "Data centre: generic HAZID prompts (fuel, battery, suppression, electrical, cooling)": (["CCPS HAZID practice"], "datacentre.HAZID_PROMPTS", "checklist to seed a study; not a study"),
    "Gas suppression / clean-agent room design": (["NFPA 2001", "ISO 14520", "NFPA 75/76"], None, "not implemented (standards not read; manufacturer calculation governs)"),
    "Load flow, harmonics, transient stability, switching transients": (["IEEE 399", "IEEE 519", "IEC 60909"], None, "not implemented (software studies)"),
    "Illumination study": (["IS 3646 / EN 12464 / OISD-STD-113 (not read)"], None, "not implemented"),
    "Pulsation and vibration studies": (["API 618", "API 674", "API 688"], None, "not implemented"),
    "Escape, evacuation and rescue analysis; ESSA": (["ISO 13702", "NORSOK S-001"], None, "not implemented"),
    "Tank venting (atmospheric / low-pressure)": (["API 2000 (5th ed. 1998 implemented; 7th ed. NOT)", "OISD-STD-108", "API 650/620"], "tank_venting.*", "implemented, 5th-edition text read; vent hardware sizing/flow curves not"),
}


def oisd() -> dict:
    return json.loads(resources.files("process_safety").joinpath("data/oisd_standards.json").read_text())


def oisd_lookup(number: str) -> dict | None:
    return oisd()["standards"].get(number)
