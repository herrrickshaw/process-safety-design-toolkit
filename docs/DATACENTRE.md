# Data-centre helpers (`process_safety.datacentre`)

Screening arithmetic that a process-safety and engineering-design consultancy can apply to a data centre. Run
`python3 -m process_safety datacentre --it-kw 10000 --facility-kw 13000 --delta-t 8 --autonomy-min 10 --gen-hours 48 --sfc 210`
(supply only the inputs you have; `--sfc` is vendor data and has no default).

| Function | What it does | Basis |
|---|---|---|
| `pue` | total facility kW / IT kW | definition |
| `cooling_water_flow_m3_h` | flow to carry a heat load, Q = m cp dT | energy balance |
| `evaporative_water_l_per_kwh_it` | open-tower make-up per kWh of IT load, with blowdown at C cycles | latent heat 2.43 MJ/kg near 30 C; reproduces about 2.2 L/kWh at 3 cycles, 1.75 L at 6 |
| `battery_energy_kwh` | nameplate energy for a UPS autonomy: P t / (eta x usable DoD) x ageing | arithmetic |
| `diesel_storage_m3` | fuel volume for N hours at a generator load | arithmetic with vendor sfc |
| `k_of_n_availability`, `dual_path_availability`, `downtime_h_per_year` | N, N+1 and 2N availability and downtime | `reliability` (independent units) |
| `HAZID_PROMPTS` | generic hazard prompts per area, with the toolkit module that helps | checklist, not a study |

## What is deliberately not here
* **Uptime Institute tier availability figures, TIA-942 ratings, EN 50600 / ISO/IEC 22237 classes**: the documents were not read, so no
  percentages or class tables are coded. Use `k_of_n_availability` with your own unit availabilities.
* **ASHRAE inlet temperature and humidity envelopes**: not read; supply them as inputs to your own checks.
* **NFPA 75/76/72/13/2001 and ISO 14520 design values** (clean-agent concentrations, sprinkler densities): not read. Suppression design is
  a manufacturer calculation.
* **Indian rules** (National Building Code data-centre provisions, CEA regulations, MeitY/STQC certification, state fire NOC): not read.
* Common-cause failure: the availability helpers assume independent units and paths, which overstates availability.
* Water arithmetic covers evaporation and blowdown only, not treatment, source or discharge permits.
* Not a design or a safety case; a qualified engineer owns any use.

## Where the numbers come from
The 1.16 kWh heat per kWh of IT load, 85% evaporated and 3 cycles used in the worked test are an illustrative water-cooled plant, not
a standard. They match a hand calculation (1.46 L evaporated per kWh of IT, 2.19 L with blowdown at 3 cycles).
