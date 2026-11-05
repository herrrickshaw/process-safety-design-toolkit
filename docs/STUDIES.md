# Study tools beyond the core QRA

These are the services Indian process-safety consultancies list next to HAZOP/QRA/LOPA (Chola MS Risk, TÜV SÜD, UEES and
others), built as dependency-free tools. Each reads JSON, runs input checks, writes CSV/HTML and a `*_summary.json` with a
`checks` list, and has a worked example in `process_safety/examples/`.

```bash
python3 -m process_safety tool example bowtie          # copy an example (bowtie | sif | fg | thermal | atex | ram | pha)
python3 -m process_safety tool bowtie bowtie.json --out out/
python3 -m process_safety qra run study.json --out qra/ # QRA now also writes qra_buildings.* and qra_emergency.*
python3 -m process_safety qra buildings study.json --out qra/
python3 -m process_safety qra emergency study.json --out qra/
```

| # | Tool | Module | What it does | Key limits |
|---|---|---|---|---|
| 1 | Bow-tie | `bowtie.py` | Threats (number or fault tree) → prevention barriers → top event → mitigation barriers → consequences; escalation factors degrade a barrier's PFD; a barrier shared by several legs is one physical barrier; RRW / RAW importance; safety-critical-element (SCE) list; SVG diagram | Barrier independence assumed; SCE threshold (RAW ≥ 10) is a screening choice |
| 2 | Occupied buildings / radiation impact | `qra/buildings.py` | Re-reads every QRA event at each building: overpressure, heat flux, engulfment, cloud entry → occupant fatality via the Purple Book discrete model or a custom curve; building IR, IRPA, PLL; overpressure and flux exceedance frequencies; worst loads; top contributors | TNT/Kinney-Graham blast field (capped at 800 kPa), no impulse or reflection; indoor fire vulnerability below 35 kW/m² assumed 0; no indoor toxic model |
| 3 | MCLS, emergency zones, ERDMP level | `qra/emergency.py` | Distances to 37.5/12.5/4 kW/m², 0.3/0.1/0.03 bar, LFL and study-supplied toxic levels for every scenario, outcome and weather; worst case and credible (frequency cut-off) maxima; zones A/B/C; who is inside each zone; Level 1/2/3 by site boundary and unit radius; zone map | Zones are circles (any wind direction); steady-plume toxic distances overstate short releases; the Level 1/2/3 rule approximates PNGRB ERDMP and needs checking against it |
| 4 | SIL lifecycle | `sil_lifecycle.py` | SIL from RRF; IEC 61511 Table 6 minimum HFT and IEC 61508 Route 1H (SFF × HFT × type A/B); SIF PFDavg by subsystem; spurious trip rate and MTTF-spurious; calibrated risk graph (refuses uncalibrated paths); SRS skeleton | No systematic capability, proof-test coverage or diagnostic-interval modelling; risk-graph calibration is yours |
| 5 | F&G mapping | `fg_mapping.py` | 2D geographic coverage for point gas (radius), open path (beam width) and flame (cone, range, line of sight blocked by obstructions); ≥1 / ≥2 voting coverage per zone vs target; greedy placement optimiser; coverage map | Geographic only (no scenario/dispersion coverage); 2D; detector ranges are inputs; greedy optimiser can stall short of target |
| 6 | PHA management | `pha.py` | CHAZOP, What-if, SWIFT and PSSR worksheets; SIMOPS matrix and schedule clash check; HAZOP action register (overdue, ageing, closure, open high-risk); revalidation due date (OSHA 5-year) and early triggers; carry-forward diff of nodes and design intents | Prompts are generic checklists, not standard text |
| 7 | Thermal runaway / ATEX | `thermal_runaway.py`, `atex.py` | TMRad (zero-order Semenov), TD24/TD8, Stoessel criticality class with guidance, Semenov critical ambient temperature for storage; KSt dust class, zone from release grade, EPL and ATEX category, FIBC screening, explosion protection document register | Zero-order kinetics (not autocatalytic); gas zones only for medium/good and high dilution; no zone extent; no dust-vent sizing |
| 8 | RAM | `ram.py` | Monte Carlo of series stages with k-out-of-n redundancy, proportional or binary capacity, exponential or lognormal repair, planned shutdown; production and full-capacity availability with CI95; downtime criticality; sample run → runs needed for target precision → full run | Unlimited repair crews; no spares, logistics or preventive-maintenance scheduling |

## Consistency checks

| Tool | Identity or check |
|---|---|
| Bow-tie | Consequence branches conserve the top-event frequency; consequence probabilities ≤ 1; PFD and escalation bounds |
| Buildings | PLL = IR × occupancy × occupants; exceedance frequencies fall as the threshold rises; worst overpressure ≤ cap |
| Emergency | Zones nest A ≤ B ≤ C; distance search returns the threshold value (tested against the pool-fire field) |
| SIF | SIF PFD = sum of subsystem PFDs; risk graph refuses paths missing from the calibration |
| F&G | Coarse (4 m) vs fine grid coverage within 5 points; point-detector coverage equals πr²/area on an open square |
| Thermal | TMRad(TD24) = 24 h; Semenov point is a tangency (generation equals cooling, and their slopes match); exact vs R·T²/Ea approximation |
| RAM | Attributed downtime sums exactly to 1 − production availability; simulated full-capacity availability matches the analytic binomial product within its CI |

## Worked examples (illustrative inputs)

- **Bow-tie (LPG bullet):**
  - Top event 1.7e-4/yr, dominated by overfill.
  - The independent HH level trip is the only SCE (RAW 61). Gas detection + ESD has RAW 7.4.
- **SIF HH level:**
  - Target RRF 150, i.e. SIL 2, and the PFDavg meets it (6.6e-3).
  - It fails on architecture: a single type-A SDV with 40% SFF caps it at SIL 1 under Route 1H.
  - So the fix is redundancy or a better final element, not a shorter test interval.
- **Buildings (QRA example):**
  - Control room occupant IR is about 5e-4/yr, against a 1e-4 target, so it fails.
  - Loading-hose flash fires and VCEs dominate.
  - The admin building passes.
- **Emergency:**
  - The credible MCLS is about 1 km to LFL (4-inch propane line rupture, F stability).
  - Zone B is set by H₂S at ERPG-2, so the site is Level 3.
- **F&G:**
  - The as-drawn layout covers the bullet area at 2% for 2ooN.
  - The greedy optimiser adds 18 point detectors and reaches about 69% before stalling, against a 90% target.
  - Next step: a finer candidate grid or open-path detectors.
- **Thermal:** the nitration example is class 3. Storage at 35 °C has a 54 K margin to the Semenov critical ambient.
- **RAM:**
  - A 100-run sample sets 574 runs for ±0.05% precision.
  - Production availability is about 97.5% including 2% planned shutdown.
  - The single reactor train causes most of the unplanned loss.
- **PHA:**
  - One overdue high-risk action.
  - Revalidation is due in 15 days, with MOC and incident triggers.
  - One prohibited SIMOPS overlap: tanker loading with hot work.
