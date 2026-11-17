# QRA workflow (`process_safety.qra`)

A dependency-free, screening-level quantitative risk assessment that chains the toolkit's consequence models into the six
classic steps. It produces location-specific individual risk (LSIR) contours, IRPA at receptors, F-N curves and PLL, judges them
against R2P2 or Bevi criteria, and re-runs candidate safeguards through an ALARP cost-benefit test.

> **Screening tool, not a safety case.** It uses neutral-gas Gaussian plumes, point-source fires, TNT blast and generic frequencies.
> Any decision should rest on validated consequence tools (DNV Phast/Safeti, RISKCURVES) and site data. Their footprints can be
> fed straight into this engine with `overrides`, so this package then does the frequency, risk integration, ALARP and mitigation
> bookkeeping.

## The six steps and where they live

| Step | Module | What it does |
|---|---|---|
| 1 Hazard identification | `hazid.py` | HAZID checklist register (natural, external, process, ignition, toxic, utilities, human, security, SIMOPS) per section; HAZOP worksheet per section via `hazop.generate`, with LOC-relevant deviations tagged; LOC register (one scenario per equipment item × hole size) |
| 2 Frequency analysis | `frequency.py`, `eta.py` | Parts count from `data/generic_frequencies.json` (sourced rows only) or study-supplied rows; fault-tree initiators (`reliability.FaultTree`: exact top-event probability, minimal cut sets, Birnbaum importance) with IPL PFD credits; event trees using Cox-Lees-Ang ignition and explosion probabilities |
| 3 Consequence analysis | `effects.py` | Source term (gas/liquid orifice flow, adiabatic flash + aerosol, duration from isolatable inventory), then lethality footprints for jet fire, pool fire, fireball, flash fire, VCE and toxic cloud, using Eisenberg thermal/blast probits and the toxic probits in `consequence.py` |
| 4 Risk calculation | `risk.py` | LSIR grid; LSIR and IRPA at receptors; expected fatalities per event with indoor/outdoor vulnerability; F-N curve; PLL; contributions by scenario and outcome |
| 5 Evaluation / ALARP | `alarp.py` | Regions (intolerable / tolerable if ALARP / broadly acceptable) for IR and F-N, using UK HSE R2P2, NL Bevi or custom criteria |
| 6 Mitigation | `mitigation.py` | Measures modify a copy of the study (frequency factors, inventory, ignition, population, conventions); each one is re-run to give ΔPLL, new IR and F-N, and an ALARP cost-benefit (VPF, disproportion factor, ICAF) |

Around them: `validate.py` (input and result consistency checks), `progress.py` (progress bar, elapsed time, ETA),
`study.py` (orchestration, sample mode, run-time projection) and `report.py` (HTML report with SVG map and F-N chart, Excel, CSV).

## Recommended workflow: small sample first, then scale

```bash
python3 -m process_safety qra example --out study.json        # copy the worked example and edit it
python3 -m process_safety qra validate study.json             # input checks: units, sums to 1, references, data provenance
python3 -m process_safety qra hazid study.json --out hazid/   # HAZID / HAZOP / LOC registers for the workshop
python3 -m process_safety qra run study.json --sample 3 --out sample/
python3 -m process_safety qra run study.json --out qra_out/
```

`--sample N` runs N LOC scenarios (at least one per section) on a grid twice as coarse. It runs every consistency check, re-runs the
sample at double angular resolution to test convergence, and projects the full-run time from the measured throughput. When
the sample is clean, the full run uses the study grid. Progress bars show the footprint build and the risk integration with
elapsed time and ETA (one line per 10% when output is not a terminal).

Python:
```python
from process_safety.qra import study, report
s = study.load("study.json")
smp = study.run(s, sample=3)            # check smp["validation_results"], smp["projection"]
out = study.run(s)
report.write_all(out, s, "qra_out")     # qra_report.html, qra_results.xlsx (if openpyxl), CSVs
```

## Study file (JSON)

See `process_safety/qra/examples/lpg_terminal.json` for a complete file. Key blocks:

* `materials`: `phase_stored` is `gas`, `liquid` or `pressurised_liquefied`, plus M, k, rho_liquid, Tb_K, Hv_kJ_kg, cp_liquid_kJ_kgK,
  Hc_MJ_kg, LFL_vol (volume fraction). Optional `toxic: {component, mole_fraction | mass_fraction, M[, probit: [a, b, n]]}`.
* `sections` (isolatable inventories): id, material, x/y (m, x east, y north), P_kpag, T_K, inventory_kg, release_height_m,
  bund_area_m2 or max_pool_area_m2, liquid_head_m, and `equipment`: items referencing a dataset type (`count` or `length_m` +
  `diameter_mm`), or carrying their own `rows: [{hole, freq, source}]`. Hole keys: `10mm`, `25mm`, `0.1D_max50`, `D/3`, `rupture`,
  or any `NNmm`; `hole_mm: {"D/3": 150}` fixes a size. Vessel/tank ruptures are instantaneous unless `instantaneous_rupture: false`.
* `extra_scenarios`: HAZOP/LOPA-derived scenarios with `frequency_per_yr` or a `fault_tree`, and `ipl_pfds`.
* `ignition`: `immediate_fraction` (required; Cox gives only the total), optional `factor`, `explosion_factor` or `p_total`.
* `weather` (stability A-F, u >= 1 m/s, probability), `wind_rose` (probability the wind blows from each equal sector, starting at north, clockwise).
* `grid`, `receptors` (group worker/public, occupancy), `population` (people, indoor_fraction), `indoor_vulnerability` (per outcome).
* `criteria`: `uk_hse_r2p2`, `nl_bevi`, or a dict. `alarp`: vpf, currency, disproportion_factor, lifetime_yr, discount_rate.
* `mitigation`: measures with capex, opex_per_yr and `changes` (see `mitigation.py`).
* `conventions`: overrides of `study.DEFAULT_CONVENTIONS` (Cd, aerosol factor, exposure time, VCE yield, sector subdivisions...).
* `overrides`: replace a computed footprint with external results:
  `{"<scenario id>": {"<outcome>": {"type": "radial", "table": [[r_m, p], ...]}}}` or
  `{"type": "footprint", "length_m": L, "half_width_m": W, "p": 1}`, optionally keyed by weather name.
* `frequency_dataset`: path to your own dataset JSON, merged over the generic one (e.g. OGP 434-1 or company data).

## Models and their limits

| Outcome | Model | Main limitation |
|---|---|---|
| Discharge | Gas: choked/subcritical orifice. Liquid: Bernoulli with head | No two-phase flashing flow (Bernoulli overstates saturated-liquid rates); no pipe-friction decay of rupture rates |
| Flash / aerosol | φ = cp(T−Tb)/Hv, airborne = min(1, 2φ) | Aerosol factor is a rule of thumb (`aerosol_factor`) |
| Jet fire | Point source, Hajek-Ludwig radiant fraction, L = 0.00326 Q^0.478, p = 1 within L/2 in all directions | Jet direction unknown, so the near field is treated radially (conservative) |
| Pool fire | Burgess / Thomas / point source; burn-off area capped by the bund | No spreading dynamics, no wind tilt |
| Fireball | CCPS/Roberts; whole liquefied inventory | No BLEVE blast or fragments |
| Flash fire | p = 1 inside the ground-level LFL footprint (neutral Gaussian); instantaneous clouds as a hemisphere at LFL | **Dense gases (propane, LPG) spread wider and shorter; use overrides for decisions** |
| VCE | TNT equivalence (yield 5%) on the flammable mass to the LFL distance; Eisenberg lung probit + p = 1 in the cloud | No congestion/confinement (multi-energy/BST); outdoor blast lethality is low by design; set `blast_threshold_kpa` or building vulnerabilities for occupied buildings |
| Toxic | Gaussian plume of the toxic component, probit dose with exposure = release duration | Neutral gas only; no instantaneous toxic puffs |

Wind directions: each sector is split into equal-weight rays, at least `sector_subdivisions` (12) and adaptively more for thin
plumes (angular step ≤ ⅓ of the plume's angular width). Sending one ray per sector leaves spokes on the map and can miss receptors
entirely (see CHANGELOG 0.7.0).

## Consistency checks (every run)

Inputs: required fields, physical ranges (Kelvin, k, LFL as a fraction), weather and wind rose summing to 1, wind ≥ 1 m/s,
probabilities in [0, 1], piping diameter inside its data band, references (materials, sections) that resolve, a source on every
study-supplied frequency row, grid size, VPF present when measures are defined, and a warning for heavier-than-air vapour.
Results: event-tree branches sum to 1 for every LOC, LSIR finite and ≥ 0, max LSIR ≤ total LOC frequency, **PLL from the F-N events
equals Σ people × vulnerability-weighted LSIR** (two independent accumulations), F-N curve monotone, footprints that run past the
grid edge, and (sample mode) angular convergence.

## Worked example: illustrative LPG / fuel terminal

Four sections: a 60 t propane bullet with pumps, an LPG road-tanker loading bay, a 12-inch sour fuel-gas header and a bunded diesel
tank. 18 LOC scenarios (including a fault-tree overfill-overpressure rupture), 2 weather classes, an 8-sector rose. Full run: 10 412
events, about 5 s for the base case and 17 s with three measures. Every consistency check passes.

| Result | Value | R2P2 region |
|---|---|---|
| Max LSIR | 1.2e-2 /yr at the loading bay | - |
| PLL | 5.1e-2 /yr (99% from loading-hose rupture, 4e-2 per hose-year in the PHMSA table) | - |
| Loading-bay operator IRPA | 6.0e-4 /yr | tolerable if ALARP |
| Control-room operator IRPA | 6.7e-5 /yr | tolerable if ALARP |
| Village edge LSIR | 9.7e-5 /yr (F-stability flash fires from the hose) | tolerable if ALARP, just under 1e-4 |
| F-N | exceeds 1e-2/N at small N | intolerable |

ALARP: the loading-hose ERC/breakaway coupling (credited 0.1 on hose rupture) removes 90% of PLL at a cost/benefit ratio of 0.03.
Implement. The extra fuel-gas SDVs and relocating the admin building fail the CBA at a disproportion factor of 3. Many inputs
(pump rows, weather, population, VPF, costs, the 0.1 ERC credit) are placeholders, so these numbers show the method, not a site.

## Not implemented

Dense-gas dispersion, two-phase discharge, jet direction and impingement, congestion-based blast (TNO multi-energy, BST), building
vulnerability models (API RP 752/753), escalation/domino effects, time-varying releases, population time-of-day sets, and
uncertainty propagation. For these, use the override hook with a validated tool.
