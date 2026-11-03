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

**Excluded on purpose:** content of licensed standards or company documents (e.g. company design practices, vendor datasheets). Do not add them
to this repository.
