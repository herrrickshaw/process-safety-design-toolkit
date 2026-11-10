# Propane jet fire: model comparison against the experiments, and a design recommendation

Screening aid, not certified design. Every number below is traced to a document read in this project, a toolkit run, or marked unverified.

## 1. What was pasted, checked against the sources

The pasted AI-assistant text conflicts with the primary documents in many places. Checked against RIVM 620550005/2012 ([report](https://www.rivm.nl/bibliotheek/rapporten/620550005.pdf)) and the DNV JFSH validation ([DNV](https://mysoftware.dnv.com/download/public/phast/technical_documentation/07_fire_models/JFSH%20Jet%20Fire%20Model%20Validation.pdf)):

| Pasted claim | What the sources say |
|---|---|
| JIVE 8051 is a "high-butane LPG, 55 to 85 % weight fraction" mix at about 2.5 kg/s | 8051 is commercial butane, 95.6 % n-butane, **6.86 kg/s**, 40 mm orifice, 18.85 barg. The 2.5 kg/s figure belongs to a different test (SA 8052, 2.52 kg/s) |
| Measured flame length 22 to 26 m | The 8051 report gives no length. RIVM reads **18.3 m** off a flame-occurrence figure (20 % contour at 6 m height); the 50 % contour is about 16.6 m |
| "40 % and 60 % flame-occurrence profiles" | RIVM quotes 20 % and 50 % |
| JIVE has pure-propane trials at 1.5 kg/s, 12.7 mm, heat flux 200 kW/m2 | No such test in RIVM or DNV. The propane horizontal jet fires in these validations are **Project AA tests 3026 and 3029**: 16.1 and 18.0 kg/s, 52 mm, 97 % propane |
| JFSH-Cook radiant fraction 0.50, Barker 0.36, Cracknell 0.54 (propane) | RIVM: JFSH-Cook **0.35**, Barker **0.26**, Cracknell **0.31** (averages for the two propane tests) |
| JFSH-Cook predicts about 36 m, "twice the real length" | JFSH-Cook gives 38.3 and 49.4 m against 31.1 and 30.7 m measured: **+23 % and +61 %**, not +100 % |
| Barker "overestimates by nearly 50 %", Cracknell "by 30 %", Cracknell most conservative | Barker +21 % and +28 %; Cracknell +10 % and +14 %. RIVM rates Barker good and Cracknell reasonable to good for both propane tests, and JFSH-Cook reasonable (3026) and poor (3029). Cracknell is the **least** conservative of the three |
| API 2510 0.10 gpm/ft2 and NFPA 15 0.25 gpm/ft2 | API 2510 (2001) clause 10.3.3 gives 0.10 gpm/ft2 (4.1 L/min/m2): read. NFPA 15 0.25 gpm/ft2 (10.2 L/min/m2) appears in a GAPS guideline snippet only; NFPA 15 was not read. The pasted 30 psi nozzle pressure disagrees with a secondary source that gives 20 psi (1.4 bar) for outdoor hazards: confirm in NFPA 15 |
| "Split-density deluge: 10.2 L/min/m2 over the first 20 m, 4.1 beyond" | No source. The HSL deluge paper (Hazards XVI, in the project ledger) says something else, see section 3 |

## 2. The propane comparison (Project AA 3026 and 3029)

Values from RIVM Tables 4 and 5 and the toolkit run with DNV's post-expansion inputs; deviations from the measured value.

| Quantity | Measured | Barker | Cracknell | JFSH-Cook (SAFETI-NL) | DNV Phast | Toolkit (DNV-Cook default) |
|---|---|---|---|---|---|---|
| 3026 flame length (m) | 31.1 | 37.7 (+21 %) | 34.3 (+10 %) | 38.3 (+23 %) | 38.9 (+25 %) | 39.0 (+25 %) |
| 3029 flame length (m) | 30.7 (a) | 39.4 (+28 %) | 34.9 (+14 %) | 49.4 (+61 %) | 50.0 (+63 %) | 50.3 (+64 %) |
| 3026 mean SEP (kW/m2) | 331 | 231 (-30 %) | 178 (-46 %) | 253 (-24 %) | 245.9 (-26 %) | 268 (-19 %) |
| 3029 mean SEP (kW/m2) | 294 | 231 (-21 %) | 182 (-38 %) | 197 (-33 %) | 192.5 (-35 %) | 214 (-27 %) |
| Radiant fraction | not reported | 0.27 / 0.26 | 0.30 / 0.32 | 0.35 | not given | 0.345 / 0.349 |
| Flame lift-off angle (deg) | not reported | 36 / 46 | 12 / 15 | 0 | not given | 0 |
| Distance to 35 kW/m2 (m) | not reported | 37 / 36 | 44 / 46 | 54 / 65 | not given | not computed (horizontal) |
| Distance to 9.8 kW/m2 (m) | not reported | 56 / 57 | 60 / 65 | 69 / 80 | not given | not computed (horizontal) |

(a) 30.7 m is from a Shell internal document; the report quoted 25.9 m, judged erroneous by RIVM.
SEP values are mean flame values over 10 to 15 s (RIVM Table 5 note 5), so they are comparable.

Reading: Cracknell is the closest on length; every model under-predicts mean SEP because the flame area is over-predicted while the radiated heat is about right (section 5 of `ASSUMPTIONS_VS_FACTS.md`). For radiation distances the lower-SEP, shorter-flame models (Cracknell, Barker) give **shorter** reach than JFSH-Cook; JFSH-Cook is the conservative choice. For a design reach, use JFSH-Cook (the toolkit default) unless a justified lower model is adopted.

## 3. What the experiments and standards mean for a propane vessel

Facts used (all from this project's sources):
* API 2510 (2001): fire relief sized to API RP 520 and 521 (7.1.6.2); independent high-level alarm and cutoff (7.1.2.3, 7.1.2.5); water spray 0.10 gpm/ft2 (10.3.3); fireproofing for 1.5 h to UL 1709 (10.7); spacing Table 1 (50 to 200 ft by tank size), explicitly **not** protection against a major incident (5.1.1.2).
* HSL, Hazards XVI: a deluge rated for pool fire (9.8 L/min/m2) is **inadequate against a 2 kg/s propane jet fire**; up to double the water protects if every nozzle works and the system is effective within 100 s. (The 9.8 L/min/m2 here is close to the 10.2 of NFPA 15, so the NFPA density is still a pool-fire density.)
* HSL 2-tonne propane BLEVE tests: the vessel can fail at 16.5 to 24.4 barg **with the relief valve working** (hot BLEVE).
* Toolkit jet-fire result for the default 25 mm hot leak (DNV-Cook): flame 10.8 m, mean SEP at the 350 kW/m2 cap, 35 kW/m2 reach 9.6 m, TDU 2000 reach 10.2 m, 50 % and 1 % lethality reach 13.5 m and 19.1 m. A vessel inside the flame length is in direct impingement.

## 4. Recommendation (generic propane bullet, reference vessel V3)

Reference vessel (assumed geometry in the relief workbook): 3.2 m diameter, 12 m long horizontal bullet, 105 m3, 85 % full, set 1724 kPag. Replace with the actual vessel; the structure of the recommendation does not change.

1. **Layout first.** Keep vessels and their supports outside the jet-fire reach of credible release points: at least the 19 m (1 % lethality) of the 25 mm leak, longer for larger holes or line-fed releases (a 10 min hole of 168 mm for this vessel gives 109 m at 1 % lethality in the toolkit run). The API 2510 table spacing is a minimum, not a major-incident distance.
2. **Do not rely on water spray as the jet-fire protection.** API 2510's 0.10 gpm/ft2 over the 143 m2 shell (cylinder 120.6 m2 plus heads 22.2 m2) is about **580 L/min**, 700 L/min with a 20 % margin (the margin is a common practice, not from a read source). NFPA 15 at 0.25 gpm/ft2 would be about **1,450 L/min**. Both are pool-fire densities: HSL shows they fail against a jet. Use spray for exposure cooling of neighbouring vessels and pool-fire cases, and size it to the standard that the authority enforces.
3. **Passive fire protection** on the shell in the jet-fire zone and on all supports and the vapour-space steel, to the API 2510 requirement of 1.5 h to UL 1709 as a floor, with a jet-fire-rated product tested to a jet-fire standard (the test standard to confirm; ISO 22899-1 is the usual candidate and was not verified here). Fireproofing is also what permits a reduced fire environment factor in API 521; the 0.3 used in the workbook is a placeholder that must be justified per API 521.
4. **Relief:** fire case for V3 bare: 28,863 kg/h, 1,227 mm2, API 526 orifice L (workbook `Propane_Vessel_Relief_Sizing.xlsx`); 8,659 kg/h and 368 mm2 if credited fire-protected. Confirm against API 520, 521, 526 editions (not read). A larger valve does not stop a hot BLEVE: the HSL tests failed with the valve open.
5. **Prevent and limit the release:** independent high-level alarm and cutoff (API 2510); remotely operated, fire-safe emergency isolation valves on liquid lines close to the vessel; excess-flow protection where practicable; fire and gas detection tied to isolation and deluge. Line-fed release rates come from the vessel pressure at the discharge, not the vessel pressure: a measured near-orifice pressure drove the JIVE 8051 discrepancy.
6. **Consequence of failure:** BLEVE of V3 (45 t of liquid) failing at 1.21 times set pressure gives, in the toolkit, a 35 kW/m2 distance of about 250 m and 1 % lethality about 490 m. These are screening distances from an extract-checked method (Yellow Book 6.5.7); they show why spacing cannot be the only barrier.

## 5. What this does not settle

* Vessel actual dimensions, set pressure, contents, release points and layout (the other assistant asked the same questions).
* NFPA 15, API 520/521/526 and ISO 22899-1 text: not read here.
* The flame-length bias (+10 % to +64 %) and the missing lift-off mean reach distances carry a 25 to 40 % uncertainty (DNV states 33 % for length, 40 % for radiation).
