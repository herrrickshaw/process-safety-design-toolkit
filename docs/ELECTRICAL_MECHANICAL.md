# Electrical and mechanical safety: scope, sources and limits

Compiled 2026-11-03. "Read" = fetched and read from the primary text; "searched" = corroborated by public secondary sources, not the standard itself.

| Topic | Module | Basis | Status |
|---|---|---|---|
| Occupational noise exposure | `noise` | OSHA 1910.95 Table G-16, App. A dose and TWA formulas | **read** (primary) |
| Arc-flash applicability | `electrical.lee_applicable` | OSHA 1910.269 App. E Table 3 (Lee equation: open-air 3-phase to 15 kV, not enclosed, not above 15 kV); 2.0 cal/cm2 note | **read** (primary) |
| Arc-flash incident energy (screening) | `electrical.lee_*` | Lee equation E = 2.142e6 V Ibf t/D^2, boundary at 5.02 J/cm2 (1.2 cal/cm2) | searched (patent and trade-press text) |
| Earthing tolerable voltages | `electrical.tolerable_*`, `surface_layer_factor` | IEEE 80-2000 forms (0.116 / 0.157 body constants; Cs = 1 - 0.09 (1 - rho/rho_s)/(2 h_s + 0.09)) | searched; worked example Cs = 0.82 reproduced |
| Overcurrent relay curves | `electrical.idmt_time_s` | IEC 60255-151 constants (0.14/0.02, 13.5/1, 80/2, 120/1) | searched (vendor manuals) |
| Lightning rolling sphere | `electrical.protected_radius_*` | radii 20/30/45/60 m by LPL | searched; collection area and Ng = 0.1 Td recalled, flagged |
| Machinery safety | `mechanical_safety.required_pl`, `pl_from_pfhd` | ISO 13849-1 risk graph and PFHd bands | two corners corroborated; rest recalled |
| Safeguard distance | `mechanical_safety.safeguard_distance_mm` | ISO 13855 pre-2024 form S = KT + C | searched; **the 2024 edition changed the formula** |
| Fault levels, cables, power factor, motor start | `electrical` | textbook | derived and tested |
| Ex temperature class, gas group, EPL by zone | `electrical.allowed_t_classes`, `gas_group_from_mesg`, `min_epl_for_zone` | IEC 60079 | recalled, flagged |
| Lifting, dropped objects, impact energy | `mechanical_safety` | statics/dynamics | derived and tested; offshore added-mass factor recalled |
| Pipe span, thermal growth, bolt torque | `mechanical_safety` | beam theory, guided cantilever, T = K d F | derived and tested |

## Limits that matter
* **Arc flash:** the Lee equation is a screening method for open-air arcs. Switchgear, MCCs and panels need IEEE 1584 (2018) software; this package refuses
  enclosed three-phase equipment and voltages above 15 kV rather than return a number. PPE category tables (NFPA 70E) are paywalled and not reproduced.
* **Earthing:** tolerable touch/step voltages only. Grid resistance, mesh and step voltage design, and soil modelling are not implemented.
* **Protection:** relay curve arithmetic and a grading check, not a coordination study (needs fault levels at each node, CT/breaker data and curves of the real relays).
* **Machinery:** a performance level needs the full ISO 13849-1 architecture (category, MTTFd, DC, CCF); only the required-PL graph and the PFHd band lookup are here.
* **Mechanical integrity** (pressure parts, foundations, structures) is out of scope here: see `vessel_mech`, the relevant structural code, and a licensed engineer.
