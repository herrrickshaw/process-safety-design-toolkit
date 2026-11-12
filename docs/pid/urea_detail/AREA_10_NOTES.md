> **Rev C2 note:** the balance was rebased on sourced values after this file was written (see REBASE_REVC.md). Flow and duty numbers quoted below are from the earlier Rev B balance and are superseded by the registers and the sheets; assumptions and open items still apply.

# Area 10 notes: coal and petcoke handling and preparation (sheets 101-113)

Generated with `scripts/urea_area_10.py` (stdlib only). Basis: Rev B stream 1 scaled to 3,850 t/d urea (K = 1.2784): blend 243.1 t/h, ash 35 % and moisture 12.8 % (`gen_pid_urea.COAL`).
Petcoke share 25 % (A; VENDOR_REFERENCE.md quotes Air Products / NETL materials "up to 25 %", the Talcher PFR gives 26.6 %): coal 182.4 t/h, petcoke 60.8 t/h.

## Sheets
| No | Tag | Unit | What the sheet shows |
|---|---|---|---|
| 101 | TP-1001 | wagon tippler, hopper, apron feeder | streams 101 -> 102; dust enclosure; level and feeder trips |
| 102 | BC-1001 | receiving belt | tramp metal, weigher, sampler, belt trips (HSG103 para 82 trip chain) |
| 103 | CR-1001 | screen and crusher | stream 103 -> 104; vent panel on dust collector |
| 104 | SY-1001 | stockyard, stacker/reclaimer | 15 d live storage (A), temperature probes, CO in cabin |
| 105 | PS-1001 | petcoke store and reclaim | 106 -> 107, ratio feeder, enclosed store |
| 106 | BN-1001 | blend and mill feed bunker | 105 + 107 -> stream 1 (Rev B), ESD feeder gate, vent panel |
| 107 | F-101 | coal mill (dry and grind) | stream 1 + hot inert gas 110 -> 108; duty 23.6 MW; O2, CO, temperature trips |
| 108 | BF-101 | pulse-jet bag filter, ID fan | 108 -> PC 109 + clean gas 111; rotary valves, two vent panels |
| 109 | V-1001 | PC storage bin (inerted) | 109 + N2 113 -> 112 + vent 114; two vent panels, O2/CO probes |
| 110 | LH-1001 | 4 pressurisation lock hoppers | PC 112 -> 115, HP N2 116, vent 117; PSV to filter; permissives |
| 111 | FV-1001 | pressurised feed vessel, 4 dense-phase lines | PC 115 + N2 118 -> 119-122 (to burners) |
| 112 | BL-1001 | burner feed line B1 (typical x4) | flow-back protection, fast isolation, purge (123-125) |
| 113 | IN-1001 | dust and explosion protection | LP N2 126 -> bin 113 + purge 127; O2/CO analysers, vent-panel trips |

All sheets use a local `sheet_solids` (in `urea_area_10.py`) because `sheet_package` draws a gate valve on every line; here ports carry device boxes (slide gate, rotary valve, chute) and an ESD ball valve where the unit holds pressurised gas, hot gas or a dust-explosion inventory.

## Balance (D from Rev B stream 1 and the parameters; every sheet asserts in = out)
- Mill: dry solids 212.0 t/h; PC at 2 % moisture 216.3 t/h; water evaporated 26.8 t/h; duty 23.6 MW; hot inert gas 476 t/h (once-through, no recycle credit).
- Lock hoppers: 4 x 68 m3, net HP N2 12.0 t/h (= vent to filter). Dense phase: loading 6.9 kg/kg, conveying N2 31.3 t/h. Total HP N2 demand 43.4 t/h, supplied by area 20 K-2004.
- PC bin 382 m3 (45 min); inerting N2 199 kg/h.

## Assumptions (all tag A; none is a licensor or vendor figure)
| parameter | value | range | meaning |
|---|---|---|---|
| pet_frac | 0.25 | 0.20-0.30 | petcoke mass share of the blend (VENDOR_REFERENCE: up to 25 %; PFR 26.6 %) |
| rho_coal | 800 | 700-900 | coal bulk density kg/m3 |
| rho_pet | 750 | 650-850 | petcoke bulk density kg/m3 |
| pc_moist | 0.02 | 0.01-0.05 | pulverised-coal moisture at mill outlet, mass fraction |
| pc_rho_bulk | 500 | 400-600 | pulverised coal bulk density kg/m3 |
| t_pc_out | 80 | 70-95 | mill outlet gas / PC temperature C |
| t_gas_in | 250 | 200-300 | hot inert gas to mill, C |
| cp_solid | 1.2 | 1.0-1.4 | dry coal specific heat kJ/kg/K |
| cp_gas | 1.05 | 1.0-1.1 | inert gas specific heat kJ/kg/K |
| cp_w | 4.18 | 4.1-4.2 | liquid water specific heat kJ/kg/K |
| hfg | 2260 | 2250-2270 | latent heat of water kJ/kg (textbook value typed here; replace by a property run) |
| mill_loss | 0.05 | 0.03-0.10 | mill and duct heat loss, fraction of duty |
| store_days_coal | 15 | 7-30 | coal stockyard live storage, days |
| store_days_pet | 10 | 5-20 | petcoke storage, days |
| belt_factor | 1.5 | 1.2-2.0 | conveyor rating over average flow |
| bunker_min | 30 | 15-60 | mill feed bunker residence, min |
| bin_min | 45 | 30-90 | PC storage bin residence, min |
| fill | 0.85 | 0.75-0.90 | bin working fill fraction |
| lh_fill | 0.8 | 0.7-0.9 | lock hopper fill fraction |
| n_lh | 4 | 3-6 | lock hoppers in staggered duty |
| lh_cycle_min | 30 | 15-60 | lock hopper cycle time, min |
| p_fv | 55 | 50-60 | feed vessel / lock hopper top pressure, bar abs (gasifier 45 bar + burner and line drop) |
| t_fv | 60 | 40-80 | feed vessel gas temperature C |
| eq_recovery | 0.6 | 0.4-0.7 | gas recovered by pressure equalisation between lock hoppers |
| rho_dense | 350 | 250-450 | dense-phase mixture density kg/m3 (must stay below bulk density) |
| rho_part | 1500 | 1300-1800 | PC particle density kg/m3 |
| v_dense | 6 | 3-8 | dense-phase line velocity m/s |
| n_burner | 4 | 2-6 | burner feed lines (licensor sets the count) |
| inert_changes | 2 | 1-4 | inerting purge changes per hour of ullage |
| inert_extra | 1.1 | 1.0-1.3 | allowance for filter and ducts on bin ullage |
| purge_seal | 0.05 | 0.02-0.10 | instrument and seal purge N2, t/h |
| o2_limit | 8 | from dust tests | placeholder O2 alarm limit vol % until explosibility tests set it (HSG103 para 25) |

The latent heat of water (2,260 kJ/kg) is a textbook value typed here as A; no property package is available.

## REV C item raised by this area
Rev B takes stream 1 into R-101 at 12.8 % moisture. The mill dries to 2 % (A), so the PC reaching the burners (216.3 t/h) is 26.8 t/h lighter than stream 1. The gasifier water/steam balance should be re-run with dried PC. Inside area 10 mass closes (stream 1 at the mill inlet; 108/109 downstream).

## Sources actually fetched and read for the safety content
- HSE, *Safe handling of combustible dusts: Precautions against explosions*, HSG103, 2nd ed. 2003, free web version (hse.gov.uk/pubns/priced/hsg103.pdf, read via pdftotext). Used: para 25-29 (inerting: safe O2 limit by test, reliable supply with reserve, asphyxiation), para 33 ff (zones 20/21/22), para 50-51 (self-heating piles; CO from smouldering dust), para 60-63 (explosion relief vents, ducted to a safe place), para 80-82 (isolation between units; trips from vent-panel switches), para 90-93 (fire in dust plant; no water on coal dust).
- Not used: NFPA 652/68/69/85, EN 14491, ISO 80079; nothing from them is quoted. No Kst, Pmax, MIE or limiting-O2 value exists for the actual blend, so **vent areas, the O2 alarm limit (placeholder 8 %) and CO alarms are not sized**.
- Talcher context and petcoke share: `coal-to-urea-design-opensource/docs/VENDOR_REFERENCE.md`, `docs/pid/validation/UREA_VALIDATION.md` (PFR sec 3.5.2).

## Gaps
Number and size of mills (vendor), hot-gas generator and fuel, pyrite rejects, mill power, dust emission and stack, petcoke composition (Rev B uses one blend composition), receipt logistics, lock-hopper valve and cycle logic (licensor), burner count (A 4), zoning drawing, fire-water for coal dust, vent areas, relief sizing of pressurised vessels (needs N2 supply capacity).
Stream ids 101-127 are used; other areas using the 1xx range must avoid them.
