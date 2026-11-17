# UREA validation (coal-to-urea, 1.10 Mt/a urea, gen_pid_urea.py)

Validator run 11 Nov 2026. Independent tool: venv_val (CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2, scipy). Scripts: /private/tmp/claude-501/val_urea/src/recompute.py and lint.py. Fetched documents: /private/tmp/claude-501/val_urea/refs/.

## Verdicts
| check | verdict |
|---|---|
| 1 Independent recomputation | 22 quantities: 16 agree, 6 differ. Stoichiometry, shift equilibria downstream of the gasifier, loop algebra, urea yield, heats and the NH3 saturation point all agree. Two real issues: the Moe water-gas-shift K at 1673 K is 34 % below the thermodynamic value (syngas CO +4.6 %, H2 -7.9 %, washed out after the shifts), and the repo ASU power (210.7 MW) implies a 7 % second-law efficiency (734 kWh/t O2 against a 52.7 kWh/t ideal minimum). |
| 2 Real-world references | 8 numeric comparisons, all grade A (documents read): 2 within tolerance, 6 explained, 0 unexplained. Three metrics have no usable reference (CO2 per t NH3, ASU power, steam: not computed here). Headline: the ratios per tonne of urea (NH3 1.70 vs 0.571, CO2 1.25 vs 0.740, coal 4.17 vs 0.90 t/t) are 2 to 4 times off because the repo urea train is single pass. Per-tonne-NH3 ratios (make-up gas, coal) are close to Talcher. |
| 3 Structural lint | 3 failures found in the original sheets, all fixed in the generator (see below); 0 left. |

## Check 1: recomputation
| metric | ours | reference / independent | source | grade | dev % | verdict |
|---|---|---|---|---|---|---|
| molar masses (9 species) | see script g/mol | chemicals/thermo g/mol | venv_val chemicals 1.5.2 | - |  <0.02 | agrees |
| WGS K at 1673 K (gasifier) | 0.2031 - | 0.3068 - | thermo 0.6.1 dH,dS from Cp integrals | - | -33.8 | disagrees: Moe fit used far outside its catalytic range (range not verified) |
| WGS K at 643 K (HT shift exit) | 16.245 - | 16.766 - | thermo | - | -3.1 | agrees |
| WGS K at 503 K (LT shift exit) | 117.72 - | 128.61 - | thermo | - | -8.5 | agrees (tol 10 pct) |
| WGS reaction heat (mean 570 K) | 41.2 kJ/mol | 39.14 kJ/mol | thermo | - | 5.3 | explained: A5 is the 298 K value (indep 41.1 at 298 K) |
| syngas flow | 8584.5 mol/s | 8584.7 mol/s | own elemental balance + thermo K | - | 0.0 | agrees |
| syngas CO | 3794.1 mol/s | 3627.3 mol/s | as above | - | 4.6 | explained: follows from Moe K at 1673 K |
| syngas H2 | 1962.4 mol/s | 2129.7 mol/s | as above | - | -7.9 | explained: follows from Moe K at 1673 K |
| HT shift CO conversion | 0.7969 - | 0.7911 - | thermo K | - | 0.7 | agrees |
| LT shift conversion of its feed | 0.8588 - | 0.8676 - | thermo K | - | -1.0 | agrees |
| H2 after LT shift (to AGR) | 5647.7 mol/s | 5656.6 mol/s | thermo K | - | -0.2 | agrees: shifts re-equilibrate, H2 robust to the gasifier K error |
| coal HHV | 17.59 MJ/kg | 16.92 MJ/kg | Channiwala-Parikh correlation typed by validator (not fetched) | C | 4.0 | agrees (tol 10 pct) |
| syngas CO+H2 HHV | 1634.6 MW | 1635.0 MW | thermo Hf, CoolProp latent heat | - | 0.0 | agrees |
| cold-gas efficiency | 64.07 pct | 66.64 pct | as above | C | -3.9 | agrees (tol 5 pct) |
| ammonia loop recycle | 28989 mol/s | 28989 mol/s | own steady-state solve of repo loop algebra | - | 0.0 | agrees |
| ammonia loop NH3 | 3469.3 mol/s | 3469.3 mol/s | as above | - | 0.0 | agrees |
| loop H balance, out vs make-up | 5647.7 mol H2/s eq | 5647.7 mol H2/s eq | own | - | 0.0 | agrees |
| urea from 0.584 x CO2 feed | 34.768 kg/s | 34.765 kg/s | chemicals MW | - | 0.01 | agrees |
| NH3 synthesis heat at 298 K | 46.1 kJ/mol NH3 | 45.56 kJ/mol NH3 | thermo Hf | - | 1.2 | agrees |
| NH3 synthesis heat at 700 K (ideal gas) | 46.1 kJ/mol NH3 | 52.34 kJ/mol NH3 | thermo Cp integrals | - | -11.9 | explained: A5 uses 298 K; converter runs 450 C, real-gas value higher |
| NH3 Psat at -33 C (A4 tank 1.1 bar) | 1.1 bar | 1.029 bar | CoolProp 8.0 | - | 6.9 | agrees (NBP -33.3 C) |
| ASU specific work (all O2+N2 to pure) | 733.8 kWh/t O2 | 175.6 kWh/t O2 | CoolProp/ideal-mixing: 52.7 kWh/t O2 minimum, divided by 0.30 second-law efficiency (assumed) | - | 318 | disagrees: repo ASU power implies 7 pct second-law efficiency; probably too high by about 3x; no fetched reference |
| K-401 make-up compression 40 to 200 bar |  MW | 55.95 MW | CoolProp isentropic, 75 pct, pure components | - | n/a | generator: not computed; added information |
| K-601 CO2 2 to 150 bar |  MW | 23.42 MW | CoolProp single-stage isentropic, 75 pct | - | n/a | generator: not computed; added information |

## Check 2: real-world references
Talcher Fertilizers (TFL) is a 2200 t/d NH3, 3850 t/d urea coal-gasification plant (EIA summary and pre-feasibility report, both fetched and read). UBA 2001 and EFMA 2000 are BAT documents. Talcher basis: 3850 t/d urea = 160.4 t/h; 2200 t/d NH3 = 91.7 t/h; coal feed 106.2 t/h + pet coke 38.5 t/h + fuel coal 134.0 t/h (PFR sec 3.5.2).

| metric | ours | reference / independent | source | grade | dev % | verdict |
|---|---|---|---|---|---|---|
| NH3 fed per t urea (S18/S22) | 1.6995 t/t | 0.5714 t/t NH3 per t urea (2200/3850 TPD) | Talcher Fertilizers EIA summary, coal-based 2200 MTPD NH3 / 3850 MTPD urea (OSPCB public-hearing doc) | A | 197.4 | explained: repo urea train is single pass, no carbamate recycle (S24 unconverted 2311 mol/s NH3 leaves the boundary); UBA states NH3 must be recycled |
| CO2 fed per t urea (S19/S22) | 1.2547 t/t | 0.7403 t/t (60480 Nm3/h at 22.414 L/mol, over 3850 TPD) | Pre-Feasibility Report, coal based ammonia and urea project, TFL Talcher (PARIVESH/environmentclearance.nic.in) | A | 69.5 | explained: same cause; stoich 0.733 t/t |
| make-up gas per t NH3 | 2856 Nm3/t NH3 | 2651 Nm3/t NH3 (243000 Nm3/h over 2200 TPD) | Pre-Feasibility Report, coal based ammonia and urea project, TFL Talcher (PARIVESH/environmentclearance.nic.in) | A | 7.7 | explained: 2 pct loop purge not recovered (A6); stoich 2630 |
| coal feed per t urea | 4.17 t/t (as-received, feed only) | 0.902 t/t coal+pet coke feed (106.2+38.5 t/h over 160.4 t/h urea) | Pre-Feasibility Report, coal based ammonia and urea project, TFL Talcher (PARIVESH/environmentclearance.nic.in) | A | 362 | explained mainly by single-pass urea (x3.0); with full recycle ours 1.39 t/t, still +54 pct: high-ash coal vs pet-coke blend, not quantified |
| coal feed per t NH3 | 2.454 t/t | 1.578 t/t (144.7 t/h over 91.7 t/h NH3) | Pre-Feasibility Report, coal based ammonia and urea project, TFL Talcher (PARIVESH/environmentclearance.nic.in) | A | 55.5 | explained (coal quality, 27 pct pet coke in reference, 90 pct carbon conversion); not quantified |
| coal LHV energy per t NH3 (feed only) | 40.85 GJ LHV/t NH3 | 51.3 GJ LHV/t NH3 = 1.7 x 28.8-31.5 (coal vs reforming factor; total incl. fuel) | EFMA BAT Booklet 1 Production of Ammonia, 2000 | A | -20.4 | explained: ours excludes fuel for steam and power; EFMA 1.7 is a relative factor at European conditions |
| CO2 compression power per t CO2 | 149 kWh/t CO2 (validator calc) | 126 kWh/t CO2 (Snam 115 minus 21-23 kWh/t urea, over 0.735 t CO2/t urea) | German Notes on BAT for Large Volume Solid Inorganic Chemicals: Urea, Umweltbundesamt, June 2001 | A | 18 | explained: single isentropic stage from 2 bar overstates; generator does not compute |
| urea reactor CO2 conversion at N/C 3.5 | 58.4 pct | 60.0 pct (60-70 pct at NH3:CO2 2.5-4) | German Notes on BAT for Large Volume Solid Inorganic Chemicals: Urea, Umweltbundesamt, June 2001 | A | -2.7 | agrees (marginally below the range) |
| urea reactor conditions | 180 C, 150 bar, N/C 3.5  | 180-210 C, 140-250 atm, N/C 2.8-4  | German Notes on BAT for Large Volume Solid Inorganic Chemicals: Urea, Umweltbundesamt, June 2001 | A | 0 | agrees |
| steam per t urea |  t/t | 0.85-1.3 (0.92 Stamicarbon) t/t | German Notes on BAT for Large Volume Solid Inorganic Chemicals: Urea, Umweltbundesamt, June 2001 | A | n/a | ours not computed |
| CO2 captured per t NH3 | 3.22 t/t |   |  | - | n/a | no reference found for total coal-route CO2 per t NH3 |
| ASU power per t O2 | 733.8 kWh/t O2 |   |  | - | n/a | no reference found (two attempts: NETL gasifipedia page, NETL supplement PDF had no figure) |

Sources:
- TEIA: Talcher EIA summary, OSPCB public hearing document, https://ospcboard.odisha.gov.in/wp-content/plugins/hearing/uploads/files_1500360215_1557856781.pdf
- TPFR: Pre-Feasibility Report TFL Talcher, https://environmentclearance.nic.in/writereaddata/modification/Corrigendum/Attach_file/210620175WDEN3TUAnnexure-AdditionalDocuments.pdf (Table E.1: 243000 Nm3/h synthesis gas, 60480 Nm3/h CO2, 2200 / 3850 TPD)
- UBA: https://www.umweltbundesamt.de/system/files/medien/publikation/long/3230.pdf (June 2001)
- EFMA Booklet 1: https://www.diquima.upm.es/old_diquima/docencia/tqi/docs/amonia00.pdf (2000; coal 1.7 relative energy; POX total 36.9 GJ LHV/t NH3 for heavy feed; reforming 28.8-31.5)

## Check 3: structural lint (stdlib script, lint.py)
Original sheets, 3 failures: (1) stream S26 had an HMB column but no diamond on sheet 1; (2) XV-502 is used in scenario sheet 3 (ESD-2) but was not on the P&ID; (3) BDV-101 is used in scenarios (ESD-1) but was not on the P&ID. After the fix: 27 diamonds = 27 HMB columns; 27 equipment tags, 0 duplicates, all on the drawing; 4 PSVs, each with a destination (flare header FL-1, or scrubber); all 8 ESD/BDV valves named in the scenarios are on sheet 1; no text outside the frame; 2 estimated text overlaps (sheet 3 label pair, approximate width model) not checked visually.
Open (not fixed, needs a design decision): relief devices exist only for R-101, R-401/V-401 loop, T-501, R-601. R-201, R-202, R-301, C-301, C-302, C-601 and V-102 are pressure equipment with no PSV and no stated reason on the sheets; add "relief by others / to be sized in HAZOP" or draw them.

## Generator fixes made (scripts/gen_pid_urea.py, sheets regenerated, closure asserts pass: error +0.022 %)
1. Added XV-502 on sheet 1 at V-401 liquid outlet (position from XVP).
2. Added BDV-101 on sheet 1 on flare header FL-1 (take-off from R-101 outlet is conceptual, A) and "XV-502" to the ESD logic note.
3. Added S26 diamond and "N2 vent" stub on ASU-101.
No assumed (A) value was changed. Regenerated docs/pid/UREA_PID_Set_RevA.html and .pdf.

## What to change (ranked)
1. Title and headline "1.10 Mt/a urea" is the repo single-pass result, not a plant rating. The same 59 kg/s NH3 with carbamate recycle gives 104 kg/s urea (3.3 Mt/a) and 1.39 t coal/t urea; Talcher's NH3:urea ratio 0.571 confirms recycle. Add a short sourced benchmark box on sheet 2 or retitle (was not done here: the owner decides).
2. ASU power 210.7 MW (S, repo) is about 3x a realistic value: raise against the repo, or label it "repo, not representative".
3. Methanation consumes about 15 % of H2 (open item already on sheet 1): real plants shift to CO below about 0.5 %; NH3 and urea are overstated by roughly that fraction in the repo basis.
4. The Moe K at 1673 K gives CO/H2 split 5-8 % off; harmless for the NH3 chain, matters for syngas cooler duty.
5. Add relief or stated reason for the 7 unprotected pressure items.
6. A5: use the 700 K heat of ammonia synthesis (about 52 kJ/mol) for R-401 duty.
Still unvalidated: heat duties of coolers and reboilers (not computed in generator), vessel sizing, flare and relief loads, water and steam per t urea (UBA 0.85-1.3 t/t, not in generator).
