# LNG liquefaction set (2.0 mtpa): validation, Rev A, 11 Nov 2026

Generator: `scripts/gen_pid_lng.py` (unchanged; no generator error found, so nothing regenerated). Tool: CoolProp 8.0 in the isolated venv. Comparison rows: `LNG_comparisons.csv`.

## Verdict per check
1. **Independent recomputation: arithmetic holds, physics of the refrigeration side does not.** 18 quantities recomputed. 12 agree. 6 disagree or are physically unsound (details below). The closure asserts are sound; they close on the repo's own numbers, which are the weak part.
2. **Real-world references: thin.** 6 comparisons (grade A: 3 from the FERC Freeport FEIS, grade C: 3 search snippets). Public per-train compressor power for a C3MR plant was not obtained: the Air Products PDFs returned 404, core.ac.uk and mdpi.com blocked automated access (Cloudflare challenge / HTTP 403), and I stopped on those hosts. Tank boil-off rate: no reference found.
3. **Lint: 10 failures** (list below).

## Is the drawn power picture credible?
Partly, and by compensating errors.
- Headline 297 kWh/t (64,261 kW over 216.2 t/h shipped LNG) sits inside the 275-375 kWh/t range quoted by Air Products (grade C). But it omits the 10,844 kW subcooling loop. At the LRC loop's own COP (0.405) that loop adds 26.8 MW and the figure becomes 421 kWh/t, above the range.
- The NG cooling duties are the cause. The repo uses constant cp x dT. A CoolProp enthalpy integral at 50 bar gives 25,915 kW for 233 K to 173 K (repo 11,027 kW, -57 %) because the gas condenses in that span. The 173 K to 114 K span is 12,165 kW (repo 10,844, -11 %). The mixed-refrigerant side is therefore under-specified by more than a factor of two, and the low LRC COP (0.405) partly hides it.
- Minimum work for the feed (298 K, 50 bar gas to saturated liquid at 1.1 bar) is 129 kWh/t. Second-law efficiency of the drawn power is 43 %, plausible only because of the two errors above.
- LRC loop: dew point 173.15 K of a heavy-rich blend (N2 5, CH4 30, C2H6 35, C3H8 30 mol %) is 0.0909 bar, so the suction is a vacuum (about 0.19 kg/m3, about 7e5 m3/h by hand calculation) and the pressure ratio is 589. Staging into 3 steps changes power by +0.2 % (27,280 kW), so staging is not the fix; the evaporating pressure is. The Freeport FEIS (grade A) describes multi-stage MR and propane compressors; ours is one machine.
- K-202 (PMR) suction is 236,297 m3/h, 2.1 times the 110,000 m3/h top of the frame range the repo uses for K-201.
- V-102 (47.3 m3) gives 396 s on K-201 flow but 97 s on the combined 228.7 kg/s that A6 routes to it. About 210 m3 is needed for 5 min at 70 % fill.
- Fuel: flash gas plus BOG is 81 MW (LHV); gas-turbine fuel for 64.3 MW shaft at an assumed 33 % is about 195 MW. The header covers about 42 %. The set states that driver fuel is not computed, so shipped LNG (1.895 mtpa) is overstated against a real plant that draws feed gas for fuel.

## Check 1 table (ours vs CoolProp)
| Quantity | Ours | Recomputed | Dev. | Verdict |
|---|---|---|---|---|
| Molar masses | table | CoolProp | <0.003 % | agrees |
| CO2 removed | 10,989 kg/h | 10,990 | 0.01 % | agrees |
| Water removed | 160 kg/h | 159.7 | 0.2 % | agrees |
| K-201 propane loop | 9,330 kW, 55.88 kg/s | 9,330.3, 55.88 | 0.00 % | agrees (same method as repo) |
| K-202 propane loop | 27,390 kW | 27,389.5 | 0.00 % | agrees |
| K-301 LRC loop | 27,219 kW, PR 589 | 27,218.5, PR 589 | 0.00 % | arithmetic agrees, physics unsound |
| End flash T, vapour | 108.43 K, 4.63 mass % | 108.431 K, 4.63 % | 0.0 % | agrees |
| TK-501 BOG | 0.3862 kg/s | 0.3862 (latent 346 kJ/kg) | 0.0 % | agrees; bulk-liquid latent 648 kJ/kg gives 0.206 (upper bound, N2-rich fresh BOG) |
| LNG density | 475.18 | 475.18 | 0.0 % | agrees |
| K-401 | 322.6 kW | 230 isentropic (307 at eta 0.75) | 5 % | agrees |
| NG duty 233-173 K | 11,027 kW | 25,915 | -57 % | **disagrees** |
| NG duty 173-114 K | 10,844 kW | 12,165 | -11 % | explained |
| V-102 residence, both circuits | 97 s | 300 s wanted | -68 % | **disagrees** |

## Check 2 table
| Metric | Ours | Reference | Source | Grade | Verdict |
|---|---|---|---|---|---|
| Specific power | 297 kWh/t (421 with subcooling loop) | 275-375 kWh/t | Air Products LNG pages (snippet; PDF 404) | C | agrees without loop, above with it |
| Specific power | 297 | 293 (1054 kJ/kg) | Scribd copy of a paper table | C | agrees (1.4 %), low weight |
| Fuel/own use of gas | 5.2 % of sweet gas | 1.8 % (0.08 of 4.48 mtpa) | FERC FEIS Freeport LNG, EIS-0487, 2014 (energy.gov PDF, read) | A | explained (37.6 mol % N2 flash gas, different basis) |
| Compression | single-stage LRC, PR 589 | multi-stage MR and propane compressors | same FEIS | A | unexplained |
| Drivers | not stated | electric motors | same FEIS | A | explained (open item) |
| Tank BOR | 0.122 %/d | no reference found | - | - | open |

## Lint (sheet 1 vs 2 and scenario sheets)
Counts: 4 sheets; 20 distinct stream diamonds on sheet 1; 19 HMB columns plus 21-23 in the supplementary list; 17 equipment-list tags, all on the drawing; 0 duplicate tags; 0 clipped text; 2 of 2 drawn PSVs have a flare destination (PSV-201 to F1, PSV-501 to FL-601).
Failures (10):
1. Stream 6 (water removed): HMB column, no diamond on sheet 1.
2. Stream 18 (fuel gas header): HMB column, only a text label "strm 18", no diamond.
3. XV-504 is named on scenario sheet 3 but is not on sheet 1.
4-9. No relief device and no stated reason: V-101, T-301, V-201A/B, V-401 (the code comment says "PSV on V-401" but none is drawn), V-301, E-301 shell.
10. Drawing shows PSV-501; equipment list and scenarios say PSV-501A/B.

## What to change (by importance)
1. Replace the constant-cp NG duty ledger (repo `liquefaction.py`) with an enthalpy integral; re-derive LRC and subcooling duties. (A: trim_cp 2.3, liq_cp 2.9.)
2. Give the MR loop a physical evaporating pressure (suction a few bar) and multi-stage compression; add the subcooling loop and propane K-202 to the repo total power (currently omitted).
3. Resize V-102 on combined propane flow, or draw two receivers (A6).
4. Add driver fuel demand (or electric drive) and show the feed-gas draw; state driver type.
5. Add PSVs or state reasons for V-101, T-301, V-201A/B, V-401, V-301, E-301; fix PSV-501 naming; add diamonds 6 and 18; remove or draw XV-504.
6. Fetch a C3MR plant document with compressor MW and propane/MR split (Air Products, operator disclosure) to replace the grade C rows.
