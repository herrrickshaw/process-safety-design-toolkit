# BIODIESEL (B100, 20 KLPD batch) P&ID set: validation, 11 Nov 2026

Generator `scripts/gen_pid_biodiesel.py` (not modified). Full row list: `BIODIESEL_comparisons.csv`.

## Verdict
| Check | Verdict |
|---|---|
| 1 Independent recomputation | Stoichiometry, element balance, latent heats and most duties agree (12 of 16 quantities). Two cooler duties are 12-13 % low (cp A18). **Methanol recovery by flash at 80 C and 1.0 bar(a) does not close** (V-401, V-402). |
| 2 Real-world references | Oil, methanol, ratio, catalyst, glycerol, conversion, methanol-recovery heat agree. FFA 2 % and the 5 % wash water are off-reference. 12 comparisons, all grade A. |
| 3 Lint | No tag, stream or ESD-valve mismatch. Gaps: 9 vessels with no relief/vent or stated reason; individual instrument tags not in the equipment list. |

## Check 1: recomputation (venv_val: CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2)
| Quantity | Ours | Recomputed | Dev % | Verdict |
|---|---|---|---|---|
| Molar masses (TG 885.453, FAME 296.495, GLY 92.094) | | 885.432, 296.488, 92.094 | 0.002 | agrees |
| FAME per kg TG fed (98 %) | 0.98446 | 0.98446 | 0 | agrees |
| Glycerol/FAME mass ratio | 0.10354 | 0.10354 | 0 | agrees |
| Element balance C,H,O,Na | closed | max 0.0007 % off | | agrees |
| Methanol latent heat 65 C (80 C) | 1100 | 1100.1 (1069.2) | 0 (2.9) | agrees |
| Water latent heat 60 C; 0.2 bar Tsat | 2300; 60 C | 2357.7; 60.06 C | -2.4 | agrees |
| E-401 condenser, MJ/batch | 580.8 | 585.0 | -0.7 | agrees |
| E-101 | 89.9 | 91.3 | -1.6 | agrees |
| V-401 coil | 522.9 | 572.6 | -8.7 | agrees (<10 %) |
| V-402 coil | 446.7 | 458.7 | -2.6 | agrees |
| V-601 dryer | 25.4 | 26.0 | -2.4 | agrees |
| R-301 charge heating | 12.8 | 12.9 | -1.1 | agrees |
| E-501 cooler | 176.1 | 202.0 | -12.9 | disagrees: A18 cp 2.0 vs 2.28 kJ/kg/K (thermo, methyl oleate) |
| E-602 cooler | 176.0 | 199.3 | -11.7 | disagrees: same cause |
| Reactor working volume, m3 | 6.09 | 6.12 | -0.5 | agrees, 8 m3 at 80 % fill holds |
| **V-401 methanol recovered at 80 C, 1.0 bar(a)** | 99.5 % (A11) | **about 14.5 %** | | **disagrees** |
| **V-402 same, glycerol phase** | 99.5 % | needs 0.011 bar(a) | | **disagrees** |

VLE basis: UNIFAC-Dortmund (thermo), methanol Psat from CoolProp. Ester-phase feed (x_MeOH 0.238) boils at 77.4 C at 1 atm, gamma_MeOH 2.55 at 80 C. To leave the stated residual (0.7 kg per batch, x 0.0016, gamma 3.7) the equilibrium pressure at 80 C is 0.0104 bar(a). At 1.0 bar a single stage stops at x 0.21, 124 kg methanol left per batch. Glycerol phase: residual x 0.0084, equilibrium 0.0111 bar(a). Caveat: no measured methanol/methyl-oleate data were used; gamma would need to exceed about 100 to close the flash at 1 bar, so the conclusion is robust to UNIFAC error. Streams 13/14 (80 C, 1.0 bar) and A11 are mutually inconsistent: either run V-401/402 near 10-20 mbar (thin-film/vacuum) or add stripping gas/steam, or accept far lower recovery and push methanol to the wash/glycerol side.

## Check 2: real-world references (all read as text, grade A)
Sources: **[S]** Sheehan et al., NREL/SR-580-24089, May 1998, osti.gov/servlets/purl/1218369. **[N]** Van Gerpen et al., NREL/SR-510-36240, Jul 2004 (UNT copy; the official nrel.gov URL gave no response). **[E]** Al Hind Lubricants 18,000 KL/A biodiesel EIA executive summary, MPCB public hearing, Nov 2023. [E] is the same project family as the DPR sample [B], so it is not independent on process text.

| Metric | Ours | Reference | Dev % | Verdict |
|---|---|---|---|---|
| Oil per t B100 | 1.0417 t/t (S) | 1.04 [S Tbl 13]; 1.037 [S 5.5.3] | +0.2 | agrees |
| Fresh methanol per t B100 | 106.6 kg/t | 110.2 (0.096 + methoxide as methanol, my sum) [S Tbl 13]; "typically 100" [S 5.5.3] | -3.3 (+6.6) | agrees |
| MeOH:TG | 6:1 | 6:1 [N, S] | 0 | agrees |
| NaOH | 0.96 % of oil | 0.3-1.5 % [N] | in range | agrees |
| Crude glycerol per t B100 | 137 kg/t | 150 kg/t [S Tbl 13] | -8.5 | agrees |
| Crude glycerin / biodiesel | 0.096 m3/KL (pure) | 0.20 (3600 / 18000 KL/A) [E] | -52 | unexplained: reference above stoichiometric ceiling (about 0.092 m3/KL), likely typo |
| Reaction T, batch time | 40 C, 6 h | 65 C (25-85) [N]; 60 C [S]; 40 C, 6 h [E] | -38 vs 65 | explained: DPR low-T scheme |
| Wash water | 5 % of ester | 20 % continuous, 30-40 % batch [S p.148]; none [E] | -75 | explained: A13 vs no-wash DPR |
| FFA, NaOH single stage | 2.0 wt% (A1) | pretreat above about 1 % [N] | | **unexplained: outside alkali window** |
| TG conversion | 98 % | 99 % overall, 98 % reported [S 5.5.1.2] | -1 | agrees |
| Methanol recovery heat | 220 MJ/t | 224.7 MJ/t (53,676 kcal/t) [S Tbl 94] | -1.9 | agrees (different unit operation) |
| Oil heating | 23 MJ/t | 107 MJ/t to 60 C [S Tbl 90] | -78 | explained: 40 vs 60 C |

Tolerance counts: 7 within, 3 explained, 2 unexplained. Sheehan removes methanol from the ester by water wash and distils the aqueous stream (column top 64.49 C, equal to CoolProp 64.48 C); no source read here shows an atmospheric hot flash of the ester. No Indian EC/EMP with a mass balance was found (a Sureshwaram EC fetched by mistake was a distillery and was discarded). Utilities per t (power, steam), water use and plant counts: no independent reference found for this scheme.

Open items answered: crude glycerol 13.7 % vs DPR 10 %: DPR 10 % matches pure glycerol (ours 10.1 %); the rest is soap (16 % of stream 17, from the 2 % FFA), NaOH, water; Sheehan crude is 15 %. Not an error. Fresh methanol 3.1 % below the DPR line: stoichiometric need is 10.9 % of triglyceride (mine); Sheehan says about 10 % of oil, 100 kg per t biodiesel typical. DPR 11 % agrees with the references. No wash: supported by [E] but the B100 would carry soap, Na and glycerol; Sheehan washes.

## Check 3: lint (stdlib parse of the generated HTML)
- Stream diamonds 1-22 on sheet 1 = HMB columns 1-22 on sheet 2, none missing (a second "7" is the legend sample). 0 failures.
- 48 equipment-list tags: all on sheet 1. No duplicate tags. 0 failures.
- ESD valves XV-201/202/203/301A/B/901 named in scenarios exist on sheet 1. Scenario text uses generic TCV-301 and PSV-301 for the A/B pair (minor).
- PSV-301A/B discharge to FA-301 and a safe location: 1 of 1 stated.
- No relief/vent or stated reason: V-302, V-401, V-402 (heated to 80 C), M-301, V-601, V-901, T-101, T-701A/B, T-801 = 9.
- Instrument tags drawn but not in the equipment list: FCV-501, LIC-501, AT-501, LSH-311, PAL-951 and others (only family rows exist).
- Text outside frame: none (width heuristic).

## What to change (ranked)
1. V-401/V-402: state vacuum (about 10-20 mbar(a)) or stripping, or lower A11; change stream 13/14 pressure and add a vacuum package to the equipment list. Cause: A11 with A17.
2. A1 FFA 2 % with NaOH: either add acid esterification pretreatment or lower FFA to 1 % or less.
3. Wash vs no-wash: decide; if no wash, state how soap and Na are held to B100 spec (IS 15607 limits not read).
4. A18: use cp about 2.25 for FAME; E-501/E-602 rise 12-13 %.
5. Relief/vent reasons for the 9 vessels; list instrument tags.
6. Sheet-2 glycerol note: add "10 % is pure-glycerol basis".

No generator change was made; no error in arithmetic, units or tags was found.
