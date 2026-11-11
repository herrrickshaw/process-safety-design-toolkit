# UREA Rev B results (gen_pid_urea.py, 11 Nov 2026)

Rev B balance: coal 52.83 kg/s, urea 125.5 t/h = 1.100 Mt/a, NH3 1,708 t/d, mass closure error +0.022 % (Rev A +0.022 %), C, O, N, S exact, H = +2 x n(H2S) repo quirk. Rev A is recomputed from the same code with the Rev B changes switched off and is asserted against the recorded repo run. Numbers below are produced by the generator; the CSV has the same rows.

## Rating decision

The repo single-pass train made 1.10 Mt/a at 145 kg/s coal. With full recycle the same NH3 train makes 3.02 Mt/a (2.4 x Talcher 1.27 Mt/a, TEIA). Choice: size to 1.10 Mt/a (coal 52.8 kg/s). All flows are linear in the coal feed (asserted), so per-tonne ratios are the same for both options; only equipment sizes change. Owner may reverse the choice by changing UREA_TARGET_MTPA.

## (a) Validator-flagged metrics

| metric | Rev A | Rev B | reference | dev A % | dev B % | status |
|---|---|---|---|---|---|---|
| WGS K at 1673 K (gasifier) | 0.2031 | 0.3063 | 0.30682 | -33.8 | -0.2 | closed (fit 0.2 % low; fit error 0.67 % max) |
| WGS K at 643 K (HT exit) | 16.245 | 16.718 | 16.766 | -3.1 | -0.3 | closed |
| WGS K at 503 K (LT exit) | 117.72 | 128.52 | 128.61 | -8.5 | -0.1 | closed |
| WGS reaction heat, kJ/mol (stage mean) | 41.2 | 39.08 | 39.14 | 5.3 | -0.2 | closed (stage values 38.41 / 39.76 used) |
| syngas flow at 145 kg/s coal | 8584.5 | 8584.5 | 8584.7 | -0.0 | -0.0 | unchanged (flow independent of K) |
| syngas CO at 145 kg/s | 3794.1 | 3627.8 | 3627.3 | 4.6 | 0.0 | closed |
| syngas H2 at 145 kg/s | 1962.4 | 2128.7 | 2129.7 | -7.9 | -0.0 | closed |
| HT shift CO conversion | 0.7969 | 0.7908 | 0.7911 | 0.7 | -0.0 | closed |
| H2 after LT shift (S9) | 5647.7 | 5656.1 | 5656.6 | -0.2 | -0.0 | closed |
| NH3 synthesis heat, kJ/mol | 46.1 | 52.34 | 52.34 | -11.9 | 0.0 | closed (not independent) |
| NH3 Psat at -33 C (A4) | 1.1 | 1.1 | 1.029 | 6.9 | 6.9 | unchanged: 6.9 % within tolerance, A kept |
| ASU specific work, kWh/t O2 | 733.8 | 275.0 | 275.0 | 166.8 | 0.0 | closed against TDA mid value; flag: single source |
| NH3 per t urea | 1.6995 | 0.5671 | 0.5714 | 197.4 | -0.8 | closed (full recycle; stoich 0.5671) |
| CO2 per t urea | 1.2547 | 0.7328 | 0.7403 | 69.5 | -1.0 | closed (stoich 0.7328) |
| make-up gas per t NH3 | 2857 | 2655 | 2651 | 7.8 | 0.2 | closed by ASSUMED 90 % purge recovery (range 2,666-2,643); not calibrated |
| coal feed per t urea | 4.171 | 1.516 | 0.902 | 362.4 | 68.1 | reduced: coal quality, pet-coke blend, 90 % C conversion, methanation H2 loss; not closed (1.74 incl. fuel coal) |
| coal feed per t NH3 | 2.454 | 2.673 | 1.578 | 55.5 | 69.4 | worse by 14 points: methanation takes 14.8 % of H2 (the repo basis ignored it); real plants avoid the loss (wash) |
| coal LHV per t NH3 (feed only), GJ | 40.85 | 44.49 | 51.3 | -20.4 | -13.3 | reduced / same explanation |
| CO2 compression power, kWh/t CO2 | 149 | 126.0 | 126 | 18.3 | 0.0 | closed (now uses the reference itself) |
| urea reactor CO2 conversion at N/C 3.5 | 58.4 | 58.4 | 60.0 | -2.7 | -2.7 | unchanged (repo fit, within the 60-70 % range edge) |
| urea reactor conditions | 180 C 150 bar N/C 3.5 | 180 C 150 bar N/C 3.5 | 180-210 C, 140-250 atm, N/C 2.8-4 |  |  | unchanged, agrees |
| steam per t urea, t/t | not computed | 0.92 | 0.85-1.3 |  |  | closed by adoption of the sourced figure (not independent) |
| CO2 captured per t NH3 | 3.22 | 3.51 |  |  |  | unchanged (no reference) |
| K-401 make-up compression power | not computed | 18.8 | 7.43 kJ/mol equivalent (validator 55.95 MW at 145 kg/s) |  |  | added; consistent |
| K-601 CO2 compression power | not computed | 11.6 |  |  |  | added |
| cold-gas efficiency | 64.06 | 64.08 | 66.64 | -3.9 | -3.8 | unchanged (within 5 %) |
| pressure items without relief or reason (sheet 1) | 7 | 0 | 0 |  |  | closed: 14 PSV + VB-501 drawn, reasons for the rest (sheet 5) |

## (b) Not closed, and why

- Coal per t urea 1.52 t/t against Talcher 0.90 t/t (coal + pet coke) is +68 %; per t NH3 2.67 against 1.58 (+69 %). Causes not separable here: Indian high-ash coal against a pet-coke blend, 90 % carbon conversion (repo), and the 14.8 % H2 lost to methanation. Talcher's own gasifier and wash design is not public.
- Purge recovery 90 % is an assumption (A) that happens to land the make-up within 0.2 % of Talcher; the range 0.85-0.95 gives 2,653-2,656 against the loop-only value 2,857 without recovery. It is not evidence.
- ASU power rests on one document (TDA / DOE-FE-0026142, 'ton' undefined); a second independent source was not found. The validator's 175.6 kWh/t O2 depends on an assumed second-law efficiency and was not adopted.
- Gasifier K: the thermodynamic K is for the equilibrium CO + H2O = CO2 + H2; the DLR rig reaches this equilibrium near 1495 K (GAP_CLOSURE_THERMO), so 1673 K is an assumption of the repo, not verified.
- Methanation complete conversion, knock-out ideality (no CO2 or H2S in the condensate), complete carbamate recycle and the 40 C separator temperature are assumptions (A).
- Not computed: E-101/102/103/401/602 and C-301/302 duties, vessel sizes, flare load, steam balance (no property model in the stdlib toolkit).

## (c) Safety items

Present now: relief schedule with 26 rows (14 PSV + VB-501 drawn, 7 sized by screening, others with a reason or 'not sized: needs ...'); ESD cause-and-effect matrix 15 initiators x 12 final elements, every XV, BDV, detector and trip tag drawn on sheet 1; SIF list 10 functions with ASSUMED SIL; detection / mitigation basis (8 items); hazard identification 10 nodes; 5 inherently-safer notes; KO-101 and flare shown.
Still gaps (standards not obtained): API 520/521/2000/620/537 (relief and flare sizing, tank venting), IEC 61511 and LOPA (SIL), OISD-STD-116/117/118/144, NFPA 15/24, IIAR 2, EN 14620, PESO SMPV(U), API 941, EIGA/CGA O2 standards, dense-phase CO2 relief method, NH3 dispersion and layout distances (no consequence model run), fire-water demand, scrubber and flare capacity.

## (d) Verify with a licensor / vendor

- Urea licensor: reactor and stripper design, carbamate recycle fraction, steam (0.92 t/t is Stamicarbon supplier data via UBA 2001), NH3 and CO2 losses, passivation air and vent handling, relief cases for R-601 and C-601 (two-phase).
- Gasifier licensor: carbon conversion, K (equilibrium) approach, quench vs radiant cooler, slag lock-hopper cycle, relief and blowdown, O2-service rules.
- ASU vendor: specific power (275 kWh/t O2 is a range 250-300 from one report), N2 export, cold-box relief.
- Syngas purification: methanation vs nitrogen wash, purge-gas recovery rate, inert level in the loop (S13 is assumed to remove CH4).
- Ammonia storage and refrigeration: tank type and size, containment, scrubber.
## Independent re-check after the rebuild (tests/crosscheck/urea_revb_constants.py --check-json, venv_val, scipy brentq with exact thermo K)

Gasifier CO +0.02 %, H2 -0.03 % against the generator (previously +4.6 % and -7.9 % against the Moe K); HT conversion 0.7911 vs 0.7908 (reference 0.7911), LT 0.8676 vs 0.8677 (reference 0.8676); H2 after LT shift 2060.9 vs 2060.8 mol/s; urea = NH3/2 exactly, 0.5671 t NH3 and 0.7328 t CO2 per t urea; loop NH3 and purge reproduced; loop nitrogen balance exact. Structural lint: 30 diamonds = 30 HMB columns; 31 equipment tags all drawn; 53 instrument/valve tags on sheets 3-7 all on sheet 1; 15 relief devices on sheet 1 and in the schedule; every pressure item has a schedule row.
