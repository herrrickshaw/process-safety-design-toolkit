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

**Excluded on purpose:** content of licensed standards or company documents (e.g. company design practices, vendor datasheets). Do not add them
to this repository.
