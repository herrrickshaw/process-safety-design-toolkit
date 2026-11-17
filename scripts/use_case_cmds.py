"""Commands behind docs/USE_CASES.md: id -> list of (label, args, keys-to-show or None)."""
CASES = {
 "refinery-fire": [
  ("Size the PSV for a fire on a gas-filled drum", ["relief-gas","--W","12000","--T","400","--set-g","1500","--case","fire","--M","44","--k","1.13","--Z","0.9"], ["required_area_mm2","orifice","regime"]),
  ("Does that PSV protect a 20 mm wall vessel in a pool fire?", ["vapour-fire","--volume","15","--area","36","--D","2","--wall-mm","20","--M","20","--k","1.3","--p0-g","1000","--psv-area","830","--psv-set-g","1500"], ["t_relief_onset_s","t_rupture_s","peak_pressure_kpag","protected"]),
  ("Add a blowdown valve opening at 60 s", ["vapour-fire","--volume","15","--area","36","--D","2","--wall-mm","20","--M","20","--k","1.3","--p0-g","1000","--psv-area","830","--psv-set-g","1500","--bdv-area","800","--bdv-open-s","60"], ["t_rupture_s","protected"]),
 ],
 "flashing-lpg": [
  ("Vapour pressure and fill limit of a propane bullet", ["lpg","propane","--fill-C","15","--max-C","50"], ["vapour_pressure_kPag_at_max","max_fill_fraction_thermodynamic_ceiling"]),
  ("Bundled CoolProp data for saturated propane at 1900 kPa abs", ["fluid-data","propane","--P","1900"], ["saturated_liquid"]),
  ("Two-phase relief area, propane relieving at 1900 kPa abs", ["twophase","--fluid","propane","--P0","1900","--W","8","--Kd","0.85"], ["omega","G_kg_m2_s","G_hem_reference_kg_m2_s","required_area_mm2"]),
  ("Same duty with n-butane", ["twophase","--fluid","n-butane","--P0","1900","--W","8","--Kd","0.85"], ["omega","G_kg_m2_s","required_area_mm2"]),
  ("Same duty with ammonia", ["twophase","--fluid","ammonia","--P0","1900","--W","8","--Kd","0.85"], ["omega","G_kg_m2_s","required_area_mm2"]),
  ("Propane again, but relieving at only 300 kPa abs", ["twophase","--fluid","propane","--P0","300","--W","8","--Kd","0.85"], ["omega","G_kg_m2_s","eta_critical","required_area_mm2"]),
 ],
 "terminal-siting": [
  ("Burn rate, SEP and distances for a 20 m diameter pool", ["pool-fire","--area","314","--hc","44000","--hv","350","--cp","2.2","--tb","400"], ["diameter_m","flame_height_m","heat_release_MW","sep_mudan_croce_kW_m2","distance_m"]),
  ("Near-field flux at 15 m from the flame face (solid flame)", ["flame-flux","--width","20","--height","31","--distance","15","--sep","30.9","--tau","0.8"], ["view_factor","incident_kW_m2"]),
  ("Same at 40 m", ["flame-flux","--width","20","--height","31","--distance","40","--sep","30.9","--tau","0.8"], ["view_factor","incident_kW_m2"]),
  ("LNG tank impoundment and boil-off for the same site", ["lng","--tanks","160000","--heat-kw","100","--regas-kg-s","100"], None),
 ],
 "functional-safety": [
  ("How much risk reduction does the scenario need (LOPA)?", ["lopa","--ie","0.1","--ipl","0.1","0.01","--target","1e-6"], ["required_rrf","sil_needed"]),
  ("Can a 1oo2 pair deliver it with a yearly proof test?", ["pfd","--arch","1oo2","--lambda-du","2e-6","--ti-years","1","--beta","0.05"], None),
  ("What if the proof test slips to every 3 years?", ["pfd","--arch","1oo2","--lambda-du","2e-6","--ti-years","3","--beta","0.05"], None),
 ],
 "regulatory-screen": [
  ("Seveso tier for a chlorine and H2S inventory", ["seveso","Chlorine:H=6","Hydrogen sulphide:H=3"], None),
  ("OSHA PSM applicability for 700 kg chlorine", ["psm-check","--chemical","chlorine","--kg","700"], None),
  ("EPA RMP threshold for 1,200 kg chlorine", ["rmp-check","chlorine","--kg","1200"], None),
  ("Next due dates for PSM obligations", ["psm-due","--pha","2021-03-15","--audit","2023-06-01","--today","2026-11-03"], None),
 ],
 "electrical": [
  ("Arc flash at a 480 V, 20 kA board", ["arc-flash","--kv","0.48","--ka","20","--t","0.2","--dist-mm","455"], None),
  ("Relay operating time at 10 times pickup", ["idmt","--i","2000","--pickup","200","--tms","0.3"], None),
  ("Tolerable touch and step voltage on a crushed-rock surface", ["earthing","--rho-s","3000","--t","0.5","--rho","75","--hs","0.2"], None),
 ],
 "data-centre": [
  ("Cooling water, UPS battery and diesel for a 10 MW IT load", ["datacentre","--it-kw","10000","--facility-kw","13000","--delta-t","8","--autonomy-min","10","--gen-hours","48","--sfc","210"], None),
 ],
 "occupational": [
  ("Daily noise dose for a mixed shift", ["noise","95:2","90:4","100:0.5"], None),
  ("Minimum distance for a light curtain with a 0.2 s stop time", ["safeguard","--stop-s","0.2","--d-mm","30"], None),
 ],
}

TEXT = {
 "refinery-fire": ("Refinery or gas plant: fire on a gas-filled drum", "oil and gas, refining",
  "A 15 m3 drum holds gas at 1000 kPag with a PSV set at 1500 kPag. You need a PSV for the fire case and want to know if the valve alone keeps the vessel intact.",
  "The fire-case valve at 1500 kPag set pressure is a J orifice (733 mm2 required, 830 mm2 installed), yet the vessel still ruptures at 700 s because the wall weakens while the valve holds pressure at about 1503 kPag. Opening a blowdown valve at 60 s avoids rupture in the hour simulated. The lesson is the one API 521 draws: sizing the valve is not the same as protecting the vessel. Flux, film coefficient and strength curve are assumptions listed in `vapour_fire.py`."),
 "flashing-lpg": ("LPG or light-hydrocarbon bullet: flashing relief", "LPG, petrochemicals, terminals",
  "A bullet relieves saturated liquid that flashes as pressure falls. Gas-only or liquid-only sizing would be wrong; the omega method sizes the two-phase case, here with omega and density taken from the bundled CoolProp table instead of typed in.",
  "For 8 kg/s and Kd 0.85, propane relieving at 1900 kPa abs needs 896 mm2; n-butane 949 mm2 and ammonia 906 mm2, so the fluid matters little at the same relieving pressure. The relieving pressure matters a lot: propane at 300 kPa abs (omega 14.5 against 4.6) needs 3199 mm2, 3.6 times the area. The omega-method flux agrees with a direct isentropic integration of the same fluid in CoolProp to within 1% in the table (see `docs/VALIDATION.md`). Design choice: the lowest relieving pressure the system can tolerate drives the area, so check the set pressure and back pressure before the valve size. Kb and Kc are not applied, and the table is saturated pure liquid only; mixtures, subcooled liquid and runaway reactions need other methods."),
 "terminal-siting": ("Terminal siting: how far is far enough from a pool fire", "tank farms, LNG and LPG terminals",
  "A 20 m diameter bunded pool fire is credible. You want radiation at a boundary or a neighbouring unit, close in and far out.",
  "The solid-flame view factor falls from 0.265 at 15 m to 0.088 at 40 m, giving 6.6 and 2.2 kW/m2. The point-source model in `pool-fire` gives a very different answer (12.5 kW/m2 at 37.9 m from the pool centre) because it radiates 25% of the heat release, while the Mudan-Croce SEP of 30.9 kW/m2 implies about 6% (SEP x flame side area is about 61 MW of 1059 MW). The two models disagree by a factor of about four in the far field. Neither is validated against a test here: run both, report both, and use the conservative one for siting until an engineer chooses."),
 "functional-safety": ("Functional safety: from LOPA to a proof-test interval", "all process industries",
  "A scenario with initiating frequency 0.1/yr and two protection layers must reach 1e-6/yr.",
  "LOPA asks for a risk reduction factor of 100 (SIL 1). A 1oo2 pair with a dangerous undetected rate of 2e-6/h and a 5% common-cause factor reaches PFDavg 5.3e-4 with a yearly proof test (SIL 3 band) and 2.1e-3 with a three-yearly one (SIL 2 band). Stretching the test interval cost one SIL band. Architectural constraints (HFT/SFF) are in `sil_lifecycle`, not in this command."),
 "regulatory-screen": ("Regulatory screen for a new chlorine installation", "chemicals, water treatment, pharma",
  "Before design you want to know which regimes a chlorine and hydrogen sulphide inventory falls under.",
  "Seveso III lower tier; OSHA PSM covered (700 kg against a 680.4 kg threshold); EPA RMP covered (1200 kg against 1134 kg); and the sample PHA and audit dates are already overdue on 2026-11-03. These are applicability screens from the rule text; Indian MSIHC schedules are not reproduced, so an Indian site needs them checked separately."),
 "electrical": ("Electrical: arc flash, relay time, earthing", "power, utilities, process plant",
  "A 480 V board with 20 kA available needs a first-pass incident energy, a relay time and tolerable earthing voltages.",
  "Open-air Lee method gives 4.75 cal/cm2 at 455 mm and a 905 mm boundary; the applicability check passes only for open-air three-phase, so enclosed gear needs IEEE 1584 (not implemented). The relay curve gives 0.89 s at ten times pickup. Tolerable touch voltage for a 50 kg person is 770 V on the 3000 ohm m surface layer."),
 "data-centre": ("Data centre: supporting-system sizing", "data centres, GCC infrastructure",
  "A 10 MW IT hall with 13 MW facility load needs first-pass cooling water, battery and diesel numbers.",
  "PUE 1.3, cooling water 1077 m3/h at 8 K rise, 2193 kWh nameplate battery for 10 minutes, 156 m3 diesel for 48 hours at the supplied fuel consumption (a vendor value, never defaulted). No tier or ASHRAE value is coded; see `docs/DATACENTRE.md`."),
 "occupational": ("Occupational: noise and machine guarding", "any workplace",
  "A worker spends a shift at mixed noise levels, and a light curtain must stop a machine safely.",
  "Dose 125% and TWA 91.6 dBA exceed the OSHA permissible level; the minimum light-curtain distance for a 0.2 s stop time is 500 mm (pre-2024 ISO 13855 form, so confirm the edition)."),
}
