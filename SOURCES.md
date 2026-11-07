# Sources and verification status

| Item | Source | How obtained | Confidence |
|---|---|---|---|
| API 2000 5th ed. (Apr 1998): Tables 1B, 2B, 3B, 4B, Eq 1B/2B, wetted-area rules, 4.3.x rules | law.resource.org/pub/us/cfr/ibr/002/api.2000.1998.pdf (public) | text and page image read | high (5th ed. only) |
| API 520-I SI constants 13160, 17.9, 11.78, 190.5 | derived from isentropic orifice flow and unit conversion; tests assert agreement | first principles | high |
| API 520 Kd (0.975 gas, 0.65 liquid), Kv curve, Napier Kn, API 526 orifice areas | recalled from the standards | not verified against text | medium: verify |
| API 521 fire heat input C=43 200 / 70 900 W, exponent 0.82 | recalled; consistent with API 2000 Eq 2B note (43 200 A^0.82) | partially cross-checked | medium |
| API 521 vapour-filled F' expression | NOT used: constants/units unverifiable | web search found only discussion | n/a |
| Vapour-fire adequacy finding | Safety 2018, 4(1), 11, doi:10.3390/safety4010011 | abstract only (MDPI blocks automated access; repository abstract page read) | abstract only |
| EN 1993-1-2 yield retention vs temperature | recalled | not verified | medium: verify |
| Pool/jet fire flux values (100 / 250 kW/m2) | Scandpower-type values recalled | not verified | low-medium: inputs |
| Flare radiant fraction F = 0.048 sqrt(MW) (cap 0.4), allowable levels 1.58/4.73/6.31/9.46 kW/m2 | Honeywell training deck and other secondary sources via search | secondary | medium |
| Fireball D=5.8 m^(1/3), t=0.45 m^(1/3) (2.6 m^(1/6) above 30 t) | CCPS/TNO as widely quoted; Roberts 1982 (IChemE Symp. 71, open PDF) | not read | medium: verify |
| LOPA generic IPL PFDs (BPCS 0.1, relief valve 0.01, ...) | CCPS values as widely quoted | secondary | medium: replace with site data |
| IEC 61508-6 simplified PFDavg | validated numerically against exact failure-probability averaging | computed | high (simplified form ~1% conservative) |
| OISD standards list (105) | oisd.gov.in/oisd-standards, fetched with curl 2026-09-21 and re-checked 2026-11-03 (same 105) | fetched | high for titles/editions; contents not read |
| 10/13 rule (tube rupture) | API 521, per secondary summaries | secondary | medium |
| API 12J separator K range 0.061-0.107 m/s (vertical, mesh) | search summary | secondary | low-medium: input |

| Darcy-Weisbach, Colebrook, isothermal compressible flow, Joukowsky, Torricelli, Bernoulli | textbook; isothermal gas equation derived here from the momentum balance | tests assert the integrated equation residual and limits | high |
| Hazen-Williams SI form 6.05e5 Q^1.85/(C^1.85 d^4.87) | NFPA 13 SI form, recalled | cross-checked against Darcy-Weisbach within 25% | medium-high |
| API RP 14E erosional C=100; IEC 60534 FF = 0.96 - 0.28 sqrt(Pv/Pc), Kv definition | recalled | not verified against text | medium: verify |
| ASME VIII-1 UG-27/UG-32 formulas | recalled | round-trip tested, not checked against the code | medium: verify |
| Briggs open-country sigmas and plume rise | recalled from open literature | mass-conservation tested (plume integrates to Q/u) | medium: verify coefficients |
| Kinney-Graham overpressure | recalled | values checked for plausibility only (e.g. Z=10 -> ~10 kPa) | medium: verify |
| Probit constants (Eisenberg thermal; Cl2, NH3, H2S toxic) | recalled from CCPS/TNO literature | not verified | low-medium: verify before use |
| HAZOP guidewords and cause prompts | IEC 61882/CCPS common practice | generic checklist | n/a (prompts, not requirements) |

| Burgess burning rate, Thomas flame height, Mudan-Croce SEP (140/20/0.12) | recalled from CCPS/open literature | formula-level tests only | medium: verify |
| Le Chatelier, z-rule LOC, purge equations | textbook; purge forms derived from mixing balances | tested by inversion | high (LOC rule is an estimate) |
| EN 1993-1-2 lumped steel forms; ISO 834 and hydrocarbon curves | recalled | curve values and bounds tested | medium-high: verify coefficients, constants (ca, eps, alpha_c) are inputs |
| Depressuring closed forms | derived from choked orifice flow; tests assert numeric = closed form within 1% | derived | high |
| v.d <= 0.5 m2/s charging limit; IP/EI 15 zone hours | recalled | informative | low-medium: use your standard |

| OSHA 1910.119 elements (c)-(p), cadences (5 y PHA, annual procedure certification, 3 y refresher and audit, 48 h investigation, retention), 10,000 lb flammables rule and exemptions | osha.gov regulation page | read in full via fetch | high |
| OSHA Appendix A threshold quantities (134 parsed) | osha.gov ...1910.119AppA | parsed from fetched text; Propyl Nitrate added manually (CAS printed non-standard) | high; completeness to confirm |
| AIGA 99/20 element titles (21) | asiaiga.org PDF contents page | read | high (titles only) |
| CCPS RBPS 20 elements | published literature | recalled | medium |
| OSHA -> AIGA crosswalk | author's mapping | not published by either body | low-medium |
| Seveso III Annex I Part 1 (21 categories) and 38 Part 2 substances, sum rule | EU Publications Office CELEX 32012L0018 | parsed from official 2012 text; rows with unparsed thresholds omitted | high for listed rows; later amendments not applied |
| 49 CFR 192.105 formula, 192.111 factors, 192.113 joint factors (subset), 192.115 derating, 192.903 PIR and HCA text | Cornell LII copy of eCFR | read | high (US rule) |
| India rules list | sigma-hse.co.in article | read | medium (consultancy summary, not the rules) |

| 49 CFR 193.2181 impoundment (110% / 100% rules), 193.2059 dispersion parameters (2.5% average concentration, 0.5 m receptor, F stability, 2.01 m/s, roughness 0.03 m) | Cornell LII eCFR | read | high (US rule) |
| 40 CFR 68: 68.22 endpoints/meteorology, 68.25 worst-case release rules, 68.115 thresholds, 68.130 Tables 1/3 (77 + 63), Appendix A endpoints | Cornell LII eCFR | read; tables parsed, counts match headings | high; mixture rule simplified |
| Lee-Kesler vapour pressure and Rackett density; critical constants | open-literature correlations; constants recalled | tested vs known values (propane 10.0 bar at 300 K; boiling points; densities within ~1%) | medium-high for non-polar hydrocarbons |
| Methane LNG properties (510 kJ/kg, 3.5/2.2 kJ/kgK, 50 MJ/kg) | recalled | not verified | medium: use project data |
| H2O2 decomposition enthalpy 98.2 kJ/mol | recalled | not verified | medium |

| OSHA 1910.95 Table G-16, dose D = 100 C/T, TWA = 16.61 log10(D/100) + 90, 85 dBA action level, 140 dB peak | osha.gov 1910.95 and App. A | read | high (US rule) |
| OSHA 1910.269 App. E Table 3: where the Lee arc-flash equation is acceptable | osha.gov | read | high |
| Lee equation constant 2.142e6 and 5.02 J/cm2 (1.2 cal/cm2) | patent and trade-press text via search | corroborated, standard not read | medium-high |
| IEEE 80-2000 touch/step constants and Cs formula; IEC 60255 curve constants; rolling-sphere radii | public secondary sources via search | corroborated, standards not read | medium-high |
| IEC 62305-2 collection area and Ng = 0.1 Td; IEC 60364 k factors; IEC 60079 T classes and gas groups; ISO 13849-1 risk graph and PFHd bands | recalled | not verified (two risk-graph corners corroborated) | medium: verify |
| ISO 13855 S = KT + C (pre-2024) | search summaries | corroborated; 2024 edition differs | medium: confirm edition |

**Excluded on purpose:** content of licensed standards or company documents (e.g. company design practices, vendor datasheets). Do not add them
to this repository.

## QRA (0.7.0, checked 2026-11-05)
| Item | Source | How obtained | Confidence |
|---|---|---|---|
| Generic LOC frequencies: vessels 5e-6 rupture / 1e-4 10 mm; piping by diameter band; tanks; hoses 4e-2; transfer arm 3e-4 | US DOT PHMSA LNG Failure Rate Table rev. 2015-02-11 (FERC nominal), primis.phmsa.dot.gov | search-engine excerpts of the public PDF (direct fetch blocked by robots.txt) | medium-high: rows as printed; check the current FRT |
| Large atmospheric tank catastrophic 5e-6, major 1e-4 | HSE PCAG ch. 6K v12 (2012) | search excerpt | medium-high |
| HSE generic pressure-vessel catastrophic 2e-6 /vessel-yr | Nussey (2006) HSE vs Netherlands comparison, quoting FRED | search excerpt | medium-high |
| Cox, Lees & Ang (1990) ignition 0.01/0.07/0.30 gas, 0.01/0.03/0.08 liquid; explosion 0.04/0.12/0.30 | EU JRC RAPID-N property estimators citing Cox et al. 1990; CET journal table | read | high (as tabulated) |
| HSE R2P2: IR 1e-3 workers, 1e-4 public, 1e-6 broadly acceptable; N>=50 at 2e-4/yr intolerable | Risktec paper (traficom.fi), IGEM guidance note, EU criteria review | secondary, consistent | high |
| F-N lines 1e-2/N (max tolerable) and 1e-4/N (broadly acceptable) | IGEM note (states it derives from the R2P2 50-fatality point) | read | medium: IGEM rendering, not R2P2 text |
| Netherlands: PR 1e-6/yr; societal guide value 1e-3/N^2 for installations (N >= 10) | CET vol. 31 (2013); TU Delft notes; Jonkman et al. (2010) | secondary, consistent | high |
| Eisenberg probits: lung haemorrhage Pr = -77.1 + 6.91 ln P[Pa]; structural damage -23.8 + 2.92 ln P | Purdue P2SAC note; Crowl & Louvar problem sets | secondary, consistent | medium-high |
| Flare/jet flame length L = 0.00326 Q^0.478 (Q in W) | TCEQ technical basis (4.56e-3 q^0.478, cal/s, flame at 45 deg) = same curve; forum fits of API 521 Fig. | regulator doc + secondary | medium: API figure fit |
| India QRA criteria | no single national value found; OISD-STD-118 (2025), PNGRB T4S, MSIHC reference QRA | consultancy summaries only | n/a: use `custom` |

## Study tools (0.8.0, checked 2026-11-05)
| Item | Source | How obtained | Confidence |
|---|---|---|---|
| Stoessel criticality classes 1-5 (Tp, MTSR, MTT, TD24) | Masaryk Univ. safety lecture notes; TUV SUD Schweiz EPSC 2020 award lecture (worked examples: class 3, class 5) | read | high |
| Purple Book building vulnerability: > 0.3 barg 1 in/out; 0.1-0.3 barg 0.025 indoors, 0 outdoors; flame/35 kW/m2 -> 1 | DNV Phast vulnerability model theory note; US LNG QRA filings | read | high |
| Indoor fire vulnerability below 35 kW/m2 = 0 | assumption (not read in the Purple Book) | n/a | low: override |
| IEC 61511-1:2016 Table 6 minimum HFT (as corrected by COR1) | iteh.ai sample of IEC 61511-1:2016/COR1:2016 | read | high |
| IEC 61508-2 Route 1H tables (type A/B, SFF x HFT) | exida blog; PR electronics SIL poster | secondary, consistent | high |
| KSt classes St1 <= 200, St2 200-300, St3 > 300 bar.m/s | explosion-testing labs; OSHA NEP table as quoted | secondary, consistent | high |
| Damage criteria 37.5/12.5/4 kW/m2; 0.3/0.1/0.03 bar | MoEF EIA Technical Guidance Manual (thermal power plants, 2010), Table 3-19/3-21 | read | high (as Indian reporting basis) |
| H2S ERPG-3/2 = 100/30 ppm | recalled; example input only | not verified | medium: verify against AIHA |
| Spurious-trip approximations (2 ls^2 MTTR, 6 ls^2 MTTR) | ISA TR84.00.02 style, recalled | not verified | medium |
| FIBC type rules, gas zone by grade (medium/good, high dilution) | recalled summaries of IEC 61340-4-4 / IEC 60079-10-1 | not verified | medium: verify |
| PHMSA NPRM (28 Oct 2026) to revise 49 CFR 193 around NFPA 59A-2026; comments due 4 Jan 2027 | National Law Review (Van Ness Feldman summary, 2 Nov 2026) | read (summary, not the NPRM text) | medium: proposed rule, not final; re-check against the Federal Register notice |
| Early design choices, scale-up and thermal screening (CSB "about 60%" statistic as quoted) | Sigma-HSE article, 27 Nov 2025 | read; statistic not checked | medium |
| CCPS Process Safety Beacon | ccps.aiche.org | not read: bot check (HTTP 403), no bypass | n/a |

## Jet flame and material data (checked 2026-11-07)
| Item | Source | How obtained | Confidence |
|---|---|---|---|
| Chamberlain vapour jet-flame equations (source diameter, Kalghatgi still-air length, length in wind, angle, lift-off, W1, W2, F_s, SEP, frustum area); beta 2.85; SEP cap 350 kW/m2 | DNV "Theory - Jet Fire" (JFSH), Dec 2023, section 2, public PDF (myworkspace.dnv.com, phast technical documentation) | full text extracted and read; equations used, no text copied (PDF forbids reproduction) | medium-high: eqs (18) and (25) were ambiguous in extraction and settled by a continuity test; Chamberlain 1987 and Kalghatgi 1984 not read |
| Chamberlain field-trial inputs (trials 3A-D, 4A-C) | DNV JFSH validation document, Table 2 | read | used only for a plausibility run; measured results are plots only, so no per-test error exists |
| Chamberlain model accuracy claims (frustum length within about 10%, SEP within 10% of mean) | same validation document, section 2.1.2 | read | as stated by DNV, not independently checked |
| 304 stainless (UNS S30400) thermal conductivity and specific heat, 4-300 K, log10 polynomial fits (errors 2% and 5%); Young's modulus; linear expansion | NIST Cryogenic Material Properties, trc.nist.gov/cryogenics/materials/304Stainless/304Stainless_rev.htm | live page fetched; fit evaluated (15.1 W/m/K and 470 J/kg/K at 293 K) | high for 304; not yet in the code |
| Nickel steels Fe-2.25/3.25/5.0/9.0Ni fits | NIST cryogenic pages | live pages fetched | NOT USED: 2.25Ni and 9.0Ni pages list identical specific-heat and linear-expansion coefficients, and the UNS labels look wrong (S21800 is not a 9% Ni steel by my recollection, unchecked) |
| Carbon steel at low temperature (A516, A333) | none found | NIST index lists only nickel steels, 304, 304L, 310, 316 | gap |
| Steel strength retention and thermal properties at fire temperatures | EN 1993-1-2:2005 Table 3.1 and thermal annex | paywalled; only unofficial copies and drafts found, not read | still medium: `structural_fire` and `vapour_fire` values remain recalled |
| Creep and rupture of C and C-Mn steels | NIMS Creep Data Sheet, cds.nims.go.jp | site found; data not read; licence terms not found | pointer only |
| Hydrogen compatibility of structural materials | Sandia "Technical Reference for Hydrogen Compatibility of Materials", SAND2012-7321, public | introduction located; no threshold values read | pointer only |
| Ideal-gas thermochemistry to high T | NIST-JANAF tables (janaf.nist.gov), about 1,700 compounds, last data update 1998 | site read; no values taken | pointer only |
| Pure-component properties incl. enthalpy of combustion | NIST/TRC Web Thermo Tables, Lite edition free (about 150 compounds), Professional is a subscription | search summary | pointer only; flammability-limit open source not found |
| ATEX expansion equations (1)-(10): mass, momentum, energy conservation, choked ideal-gas vena contracta, velocity cap, sonic-air-jet verification and British Gas natural-gas validation cases | Witlox and Fernandez, IChemE Symposium Series 161 (Hazards 26), 2016, icheme.org open PDF | full text extracted and read; momentum and energy forms derived from (1)-(3) | high for the ideal-gas path; droplet and rainout correlations not read |
