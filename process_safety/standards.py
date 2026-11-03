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
    "Pool/jet fire, explosion, dispersion (QRA)": (["CCPS", "OISD-STD-116", "PNGRB T4S"], None, "not implemented - use DNV Phast/Safeti or add models"),
    "Layout / separation distances": (["OISD-STD-118", "OISD-STD-163"], None, "not implemented"),
    "Hazardous area classification": (["IEC 60079-10-1", "OISD-STD-113", "API RP 505"], None, "not implemented"),
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
    "Tank venting (atmospheric / low-pressure)": (["API 2000 (5th ed. 1998 implemented; 7th ed. NOT)", "OISD-STD-108", "API 650/620"], "tank_venting.*", "implemented, 5th-edition text read; vent hardware sizing/flow curves not"),
}


def oisd() -> dict:
    return json.loads(resources.files("process_safety").joinpath("data/oisd_standards.json").read_text())


def oisd_lookup(number: str) -> dict | None:
    return oisd()["standards"].get(number)
