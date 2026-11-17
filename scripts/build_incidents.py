"""Build process_safety/data/incidents.json from US Chemical Safety Board investigation pages (read 2026-11-06).

Facts (date, location, final report date, deaths where the page states them, the example recommendation) are as the CSB page states them;
`lesson` and `design_step` are this toolkit's mapping, in our words. deaths/injured are null when the page text read did not state them.
"""
import json
import os

B = "https://www.csb.gov/"
I = []


def add(id, name, date, place, report, deaths, injured, sector, url, rec, lesson, modules, steps, note=""):
    I.append(dict(id=id, name=name, date=date, location=place, final_report=report, deaths=deaths, injured=injured, sector=sector,
                  source=B + url, recommendation=rec, lesson=lesson, modules=modules, design_steps=steps, note=note))


add("texas-city-2005", "BP America Texas City refinery explosion", "2005-03-23", "Texas City, TX", "2007-03-20", 15, 180, "refining", "bp-america-texas-city-refinery-explosion/",
    "API 2005-4-I-TX-2 (text not captured)", "isomerisation unit restart: distillation tower flooded and overpressurised, geyser from a vent stack near occupied trailers: level protection, blowdown to a closed system, siting of occupied buildings",
    ["overfill", "separator", "flare_system", "explosion", "psm"], [4, 6, 8, 9], "CSB also issued reports on management of change and positive material verification")
add("kleen-energy-2010", "Kleen Energy natural gas explosion", "2010-02-07", "Middletown, CT", "2010-06-28", 6, None, "power", "kleen-energy-natural-gas-explosion/",
    "ASME 2010-07-I-CT-3: require inherently safer fuel gas piping cleaning methods in B31.1 instead of natural gas blows", "high-pressure natural gas (about 650 psi) used to blow debris from new piping found an ignition source: choose a method that removes the fuel from the activity",
    ["flammability", "explosion", "electrical"], [1, 11])
add("tesoro-anacortes-2010", "Tesoro Anacortes refinery fatal explosion and fire", "2010-04-02", "Anacortes, WA", "2014-05-01", 7, None, "refining", "tesoro-anacortes-refinery-fatal-explosion-and-fire-/",
    "API 2010-08-I-WA-10: revise API RP 941, Steels for Hydrogen Service at Elevated Temperatures", "a nearly forty-year-old heat exchanger failed catastrophically while a maintenance step switched streams between exchanger banks: damage-mechanism assessment and aging-asset integrity",
    ["psm", "hazop", "vessel_mech"], [5, 12])
add("t2-2007", "T2 Laboratories reactive chemical explosion", "2007-12-19", "Jacksonville, FL", "2009-09-15", 4, 13, "chemicals", "t2-laboratories-inc-reactive-chemical-explosion/",
    "ABET 2008-03-I-FL-3: add reactive hazard awareness to chemical engineering curricula", "runaway during production of a gasoline additive: reactive hazard screening and relief for runaway are design inputs, not afterthoughts",
    ["reaction_hazard", "thermal_runaway", "plant_units"], [1, 5, 6], "injured = taken to hospital")
add("imperial-sugar-2008", "Imperial Sugar dust explosion and fire", "2008-02-07", "Port Wentworth, GA", "2009-09-24", 14, 38, "food processing", "imperial-sugar-company-dust-explosion-and-fire/",
    "American Bakers Association 2008-05-I-GA-8: promote combustible dust hazard awareness and control", "massive accumulations of sugar dust throughout the packaging building fuelled the explosion: dust hazard analysis, housekeeping and explosion protection by design",
    ["atex", "flammability"], [3, 5, 11])
add("ddw-2003", "D.D. Williamson catastrophic vessel failure", "2003-04-11", "Louisville, KY", "2004-03-12", 1, None, "food additives", "d-d-williamson-and-co-catastrophic-vessel-failure/",
    "Commonwealth of Kentucky 2003-11-I-KY-7 (text not captured)", "a process vessel became overpressurised and failed, releasing aqueous ammonia: pressure relief on every vessel that can be overpressured",
    ["relief", "vessel_mech", "relief_piping"], [6], "the CSB announcement URL text cites lack of emergency relief valves; the report body was not read")
add("capeco-2009", "Caribbean Petroleum (CAPECO) refinery tank explosion and fire", "2009-10-23", "Bayamon, PR", "2015-10-21", None, None, "terminals", "caribbean-petroleum-corporation-capeco-refinery-tank-explosion-and-fire/",
    "API 2010-02-I-PR-7: revise ANSI/API 2350 to require automatic overfill prevention systems at bulk aboveground tanks storing flammable liquids with NFPA 704 rating 3 or higher", "tank overfill and vapour cloud: independent automatic overfill protection, not operator vigilance",
    ["overfill", "tank_venting", "explosion"], [4, 6, 8])
add("west-fertilizer-2013", "West Fertilizer explosion and fire", "2013-04-17", "West, TX", "2016-01-28", 14, None, "fertiliser storage", "west-fertilizer-explosion-and-fire-/",
    "FEMA 2013-02-I-TX-7 (training recommendation; text not captured)", "twelve volunteer firefighters and two members of the public killed: hazard communication to responders and siting of facilities relative to the community",
    ["mah", "rmp", "qra"], [2, 9, 10], "deaths = 12 firefighters + 2 public, as the page states")
add("williams-olefins-2013", "Williams Olefins plant explosion and fire", "2013-06-13", "Geismar, LA", "2016-10-19", 2, None, "petrochemicals", "williams-olefins-plant-explosion-and-fire-/",
    "API 2013-3-I-LA-4: strengthen API 521 for a pressure vessel in a special operating status", "a pressure vessel in a special operating status ruptured (per the recommendation to strengthen API 521): relief and depressuring should cover non-routine operating modes",
    ["relief", "depressuring", "vapour_fire"], [5, 6, 7])
add("chevron-richmond-2012", "Chevron Richmond refinery fire", "2012-08-06", "Richmond, CA", "2015-01-28", None, None, "refining", "chevron-richmond-refinery-fire/",
    "API 2012-03-I-CA-26: revise API RP 939-C on sulfidation corrosion for low-silicon carbon steel piping", "release of flammable vapour; the recommendation concerns sulfidation corrosion of low-silicon carbon steel piping: material selection and inspection for damage mechanisms",
    ["psm", "pool_fire", "vapour_fire"], [1, 5, 12], "CSB issued interim, regulatory and final reports")
add("arkema-2017", "Arkema Crosby chemical plant fire", "2017-08-29", "Crosby, TX", "2018-05-24", None, None, "chemicals", "arkema-inc-chemical-plant-fire-/",
    "recommendation text not captured", "flooding from Hurricane Harvey disabled refrigeration; organic peroxides in trailers warmed and spontaneously combusted: loss of utilities and natural hazards in the design basis for temperature-sensitive materials",
    ["thermal_runaway", "reaction_hazard", "mah"], [1, 5, 10], "1.5 mile evacuation; the page does not state casualties")
add("didion-2017", "Didion Milling explosion and fire", "2017-05-31", "Cambria, WI", "2023-12-06", 5, 14, "food processing", "didion-milling-company-explosion-and-fire-/",
    "Didion Milling 2017-07-I-WI-1: engage a third party to develop a combustible dust process safety management system modelled on OSHA PSM", "combustible dust explosions killed five of 19 night-shift employees: dust PSM, hazard analysis and explosion protection",
    ["atex", "psm", "flammability"], [3, 5, 12])
add("pes-2019", "Philadelphia Energy Solutions refinery fire and explosions", "2019-06-21", "Philadelphia, PA", "2022-10-11", None, None, "refining", "philadelphia-energy-solutions-pes-refinery-fire-and-explosions-/",
    "API 2019-04-I-PA-4: update API RP 751 on hydrofluoric acid alkylation, including protection of critical safeguards", "vapour release in an alkylation unit ignited and caused multiple explosions: protect safeguards from the hazard they guard against",
    ["explosion", "psm", "hazop"], [4, 5, 8])
add("itc-2019", "Intercontinental Terminals tank fire", "2019-03-17", "Deer Park, TX", "2023-07-06", None, None, "terminals", "intercontinental-terminals-company-itc-tank-fire/",
    "API 2019-01-I-TX-6: update API STD 2610 on terminal and tank facilities", "massive tank fire at a terminal: tank farm layout, remote isolation, fire protection",
    ["pool_fire", "fire_water", "tank_venting", "structural_fire"], [4, 7, 9], "page status text says ongoing although a 2023 final report is listed")
add("tpc-2019", "TPC Port Neches explosions and fire", "2019-11-27", "Port Neches, TX", "2022-12-19", None, None, "petrochemicals", "tpc-port-neches-explosions-and-fire/",
    "American Chemistry Council 2020-02-I-TX-4: butadiene guidance on identifying and eliminating dead legs and the popcorn polymer hazard", "dead legs in butadiene service allow runaway popcorn polymer: line design and spare-equipment isolation",
    ["reaction_hazard", "plant_units", "hazop"], [3, 5])
add("oregon-ohio-2022", "BP-Husky Oregon (Toledo) refinery chemical release and fire", "2022-09-20", "Oregon, OH", "2024-06-24", 2, None, "refining", "bp---husky-oregon-chemical-release-and-fire-/",
    "API 2022-01-I-OH-5: develop or revise a publication such as API RP 556 on instrumentation (text partly captured)", "naphtha entered the fuel gas system during an upset and ignited: overfill/level safeguards, relief basis, and PHA accuracy (see also OSHA findings in DESIGN_AWARENESS.md)",
    ["overfill", "relief", "psm", "hazop"], [5, 6, 8])
add("pemex-2024", "PEMEX Deer Park hydrogen sulfide release", "2024-10-10", "Deer Park, TX", "2026-02-23", 2, 13, "refining", "pemex-deer-park-chemical-release-/",
    "ASME 2024-05-I-TX-4: develop written guidelines for marking equipment (text partly captured)", "workers removing an isolation blind from piping that normally carries H2S: positive isolation, marking and permit design",
    ["dispersion", "consequence", "psm"], [5, 11, 12], "page shows both 2026-02-23 and 'February 23, 2025' as release date; 2026-02-23 used")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "incidents.json")
json.dump({"compiled": "2026-11-06", "source": "US Chemical Safety and Hazard Investigation Board investigation pages (csb.gov), read 2026-11-06",
           "note": "facts as the CSB page states; lessons and design_steps are the toolkit's mapping (steps = rows of docs/DESIGN_AWARENESS.md section 1)", "incidents": I},
          open(out, "w"), indent=1)
print(len(I), "incidents")
