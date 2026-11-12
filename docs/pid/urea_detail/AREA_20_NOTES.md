> **Rev C2 note:** the balance was rebased on sourced values after this file was written (see REBASE_REVC.md). Flow and duty numbers quoted below are from the earlier Rev B balance and are superseded by the registers and the sheets; assumptions and open items still apply.

# Area 20 notes: air separation (sheets 201-216)

Generated with `scripts/urea_area_20.py`. Basis: Rev B streams 25 (air 574.2 t/h), 2 (O2 133.7), 14 (N2 to loop 75.5), 26 (surplus N2 365.0), scaled by K = 1.2784. Rev B closure 25 = 2 + 14 + 26 (O2 and N2 only) is asserted.
Stream 26 is split: 43.4 t/h HP N2 for area 10 (lock hoppers and dense-phase conveying, imported from `urea_area_10`) and a vent of 321.6 t/h.

## Sheets
| No | Tag | Unit | Template |
|---|---|---|---|
| 201 | FA-2001 | air intake filter and silencer | package |
| 202 | K-2001 | main air compressor (6 bar, 35.4 MW D) | compressor |
| 203 | C-2001 | direct-contact air cooler, chilled water 203 t/h | column |
| 204 | AD-2001 A/B | molecular-sieve adsorbers, regen heater 2.6 MW | package |
| 205 | CB-2001 | cold box with main heat exchanger (209 O2, 210 HP N2, 213 waste N2) | package |
| 206 | C-2002 | HP column (crude O2 36 mol %, A) | column |
| 207 | C-2003 | LP column (reflux 113.5 t/h, D from closure) | column |
| 208 | T-2001, P-2001A/B | LOX backup storage (516 m3, 4 h) and pumps | tank |
| 209 | E-2005 | LOX vaporiser, 14.8 MW (D, A properties) | hx |
| 210 | T-2002, P-2002A/B | LIN backup storage (206 m3, 2 h) and pumps | tank |
| 211 | E-2006 | LIN vaporiser, 8.7 MW | hx |
| 212 | K-2002 | oxygen compressor (1.3 to 50 bar, 16.5 MW D), O2 service | compressor |
| 213 | K-2003 | N2 compressor to loop (5.2 to 40 bar, 5.8 MW D) = stream 14 | compressor |
| 214 | K-2004 | HP N2 compressor to area 10 (5.2 to 58 bar, 4.0 MW D) | compressor |
| 215 | HD-2001 | O2 header to R-101 (filter, vent, ESD, standby inlet) | package |
| 216 | HD-2002 | N2 headers and waste-N2 vent | package |

## Power check (finding for Rev C)
Bottom-up train power (stages, k = 1.4, efficiencies A): MAC 35.4 + O2 16.5 + loop N2 5.8 + gasifier N2 4.0 = 61.7 MW = 461 kWh/t O2. Rev B ASU-101 is 36.8 MW (275 kWh/t O2, TDA range 250-300, one source, "ton" undefined). The Rev B figure seems not to include compression of O2 to 50 bar and of N2 to 40/58 bar. Not forced to close; reconcile in Rev C.

## Assumptions (tag A unless D)
| parameter | value | range | meaning |
|---|---|---|---|
| p_air_in | 0.98 | 0.97-0.99 | air after intake filter, bar abs |
| p_mac | 6 | 5-8 | main air compressor discharge, bar abs |
| eta_air | 0.8 | 0.75-0.85 | MAC isentropic efficiency per stage |
| eta_gas | 0.75 | 0.70-0.80 | O2 and N2 compressor isentropic efficiency (K-401 uses 0.75 A in gen_pid_urea) |
| k_diatomic | 1.4 | D | ideal diatomic gas heat-capacity ratio (kinetic theory: 7/5) |
| r_stage_max | 3.5 | 3-4 | maximum pressure ratio per stage |
| cp_air | 1.005 | 1.00-1.01 | air specific heat kJ/kg/K |
| cp_n2 | 1.04 | 1.03-1.05 | N2 specific heat kJ/kg/K |
| cp_w | 4.18 | 4.1-4.2 | water kJ/kg/K |
| t_dcc_out | 15 | 10-20 | air out of direct-contact cooler, C |
| w_in | 8 | 5-12 | chilled water in, C |
| w_out | 25 | 20-30 | water out of DCC, C |
| regen_frac | 0.1 | 0.05-0.20 | regeneration N2 as fraction of air flow |
| t_regen | 180 | 150-250 | regeneration gas temperature, C |
| x_b | 0.36 | 0.30-0.40 | HP column sump O2 mole fraction (crude oxygen) |
| p_hp | 5.5 | 5-6 | HP column pressure, bar abs |
| p_lp | 1.4 | 1.3-1.6 | LP column pressure at the sump, bar abs |
| p_o2_lp | 1.3 | 1.2-1.4 | O2 gas from cold box, bar abs |
| p_n2_hp | 5.2 | 4.8-5.4 | HP N2 from cold box, bar abs |
| p_n2_lp | 1.1 | 1.05-1.2 | waste N2, bar abs |
| lox_h | 4 | 1-8 | LOX backup, h at full O2 flow |
| lin_h | 2 | 1-4 | LIN backup, h at ammonia-loop N2 flow |
| refill_lox_h | 48 | 24-72 | LOX refill time, h |
| refill_lin_h | 24 | 12-48 | LIN refill time, h |
| rho_lox | 1140 | 1100-1150 | LOX density kg/m3 (textbook) |
| rho_lin | 807 | 790-810 | LIN density kg/m3 (textbook) |
| rho_rich | 900 | 800-1000 | crude oxygen liquid density kg/m3 |
| L_o2 | 213 | 200-220 | O2 latent heat kJ/kg (textbook) |
| L_n2 | 199 | 190-205 | N2 latent heat kJ/kg (textbook) |
| cp_o2 | 0.92 | 0.91-0.93 | O2 kJ/kg/K |
| t_hw_in | 80 | 60-90 | vaporiser hot water in, C |
| t_hw_out | 50 | 40-60 | vaporiser hot water out, C |

Typed textbook property values (latent heats, liquid densities, cp) are tag A: no property package or fetched table was available. Column temperatures (HP -176/-178/-175 C, LP -190/-194/-193/-181 C) are screening values (A, +/- 5 K); no VLE run.

## O2 service (what was read and what was not taken)
EIGA Doc 13/20 *Oxygen pipeline and piping systems* (eiga.eu/uploads/documents/DOC013.pdf, read via pdftotext): sec 4.2 (fire triangle; ignition mechanisms particle impact, adiabatic compression, promoted ignition by organics, friction, arcing), sec 4.4 (velocity limits from the impingement curve, Figure 2, and non-impingement curve, Figure 3, by metal and pressure), sec 6.1 (cleaning). No number from it is used. The line-list velocities on O2 sheets (212, 215) are the generic 25 m/s gas rule and are **not** oxygen design velocities; those NPS must be redone from the curves. EIGA Doc 10 and Doc 27 (O2 compressors) are named in Doc 13 but were not read. HSE HSG103 para 28 (inert-gas asphyxiation) is used for N2 vents. CGA standards and licensor O2 practice are not available (gap).

## Gaps
Argon, CO2, water of air and impure fractions are not in Rev B; refrigeration (expander, liquid make) and cold-box heat leak are not modelled; adsorber bed volume and cycle; main condenser-reboiler duty; LOX hydrocarbon purge; column pressure drop; real air recovery (Rev B recovers 100 % of O2); intercooler duties; drivers; relief sizing (all PSVs "not sized", destination safe location, never flare for O2/N2); LOX/LIN impounding and spacing (no standard fetched).
Stream ids 201-239 are used (209, 2, 14, 26, 215 appear on more than one sheet on purpose).
