# Workflow: safety simulation, resizing and design, capex and opex of the installation

`python -m process_safety tool workflow` chains the toolkit's models into one audited run. You describe each unit once (process data from your simulator, what is installed, what you would install, your rates); the workflow screens it, resizes the safety devices, prices the installation and its running cost, tests the package against ALARP, and (optionally) feeds the shutdown-dependent work into the turnaround schedule and cost risk.

```
 your simulator (DWSIM, NeqSim, UniSim ...)       your rate book, opex book, quotes
        |  stream data, vessel data, set pressures          |
        v                                                   v
 1 SIMULATE / SCREEN -> 2 RESIZE / DESIGN -> 3 BILL OF QUANTITIES -> 4 CAPEX -> 5 OPEX -> 6 ALARP -> 7 SHUTDOWN MERGE
   fire relief load      PSV orifice          device scope           Monte     test,      cost vs     schedule, lost
   vapour-fire run       inlet line size      pipeline rerouting     Carlo,    calibration, benefit     days, opportunity
   inlet loss            blowdown valve       additional sensors     P50/P80,  support,     per unit    cost
                         (re-simulated)       PCN modification       contingency maintenance package
```

## What each stage does (and which module it uses)
| Stage | Content | Modules |
|---|---|---|
| 1 Simulate / screen | Liquid-wetted vessel: wetted area, fire heat input, relief rate, API 520 vapour area at fire relieving pressure, orifice letter. Vapour-filled vessel: transient fire run with the installed PSV (does it survive?). PSV inlet loss against the 3% rule at the valve's **rated** capacity | `relief`, `vapour_fire`, `hydraulics`, `relief_piping` |
| 2 Resize / design | New PSV orifice if the installed one is short; inlet line size from your list of candidate pipes; blowdown valve area for a target depressuring time, re-simulated until the vessel is protected (with an optional minimum practical size that can govern); the inlet loss re-screened on a rerouted (longer) line | `relief`, `depressuring`, `vapour_fire` |
| 3 Bill of quantities | Four scopes per unit, each with its own shutdown flag and duration: **device** (PSV, inlet line, blowdown valve and flare line), **pipeline rerouting** (demolition, new line, fittings, supports, tie-ins, civil), **additional sensors** (instruments, cable by length, junction boxes, loop checks) and **PCN modification** (I/O cards, controller changes, switches, OT firewall, engineering hours, FAT/SAT) | `design_workflow` |
| 4 Capex | Quantities x your rates with min/mode/max, indirects, shared rate factor, Monte Carlo P50/P80, contingency | `recommendation_cost` |
| 5 Opex | Incremental annual cost of the new equipment: blowdown valve proof tests, sensor calibration and proof tests, PCN support and licences, cybersecurity monitoring and patching, maintenance as a share of capex; lifecycle at your discount rate | `design_workflow`, `qra.alarp` (present value) |
| 6 ALARP | Package cost (capex P50 + opex) against the risk reduction: supplied, or **derived from the sensor voting change** (PFDavg before and after, demand rate, fatalities per event) | `sil`, `qra.alarp` |
| 7 Shutdown merge | Shutdown-dependent scopes become activities in a `shutdown_risk` model: change in duration, direct cost, lost operating days, opportunity cost and total cost | `shutdown_risk` |

## Taking numbers from a simulator
| Workflow input | Typical source in a flowsheet simulator |
|---|---|
| `fluid.M`, `k`, `Z`, `relieving_T_K`, `mu_Pa_s` | vapour stream at relieving conditions |
| `vessel.*`, `latent_heat_kJ_kg` | vessel datasheet; latent heat of the liquid at relieving pressure (see `fluid-data` for pure fluids) |
| `set_kpag`, `back_pressure_kpag`, `existing.*` | design basis and as-built records |
| `depressure.target_kpag`, `target_time_s` | your depressuring criterion |
Open simulators and what they can supply are listed in `docs/SIMULATION_TOOLS.md`. The workflow takes plain numbers and does not call any simulator.

## Worked example (illustrative inputs: two hypothetical units, made-up rates; run on 2026-11-06)
V-101 (liquid-wetted, 506 mm2 PSV installed): the fire case needs 663.6 mm2, so a J orifice is specified; the 9 m rerouted inlet still meets the 3% rule. V-201 (vapour-filled, 830 mm2 PSV): the transient run ruptures the vessel at 700.0 s as installed; a blowdown valve opening at 60 s protects it, with the 50 mm minimum practical size governing (1,963.5 mm2).

| Scope | Work | Base (mode) | P50 | P80 |
|---|---|---|---|---|
| V-101:device | shutdown | 14.2 | 15.3 | 17.2 |
| V-101:reroute | shutdown | 144.7 | 161.9 | 176.3 |
| V-201:device | shutdown | 200.4 | 220.6 | 248.0 |
| V-201:sensors | online | 68.9 | 77.9 | 85.0 |
| V-201:pcn | shutdown | 71.3 | 79.7 | 87.4 |

Portfolio capex: base 499.5, P50 557.3, P80 593.7 (contingency 94.1); 430.6 of the base is shutdown work.

| Unit | Annual opex | Parts | Lifecycle opex (PV) |
|---|---|---|---|
| V-101 | 2.7 | maintenance of new equipment 2.7 | 43.8 |
| V-201 | 18.1 | bdv proof test 0.6, sensor calibration and proof test 0.8, pcn support and licences 9.6, pcn cybersecurity monitoring and patching 1.5, maintenance of new equipment 5.7 | 298.0 |

Lifecycle cost at P50 (capex plus PV of opex over 25 years at 3.5%): 899.2. PCN support and maintenance are about 85% of V-201's running cost; the blowdown valve proof test is about 3%.

ALARP (package cost against benefit, at a disproportion factor of 3 with made-up risk numbers): V-101 cost-benefit ratio 2.48; V-201 2.83, with the V-201 benefit derived from changing 1oo1 pressure sensing to 2oo3 (PFDavg 8.76e-03 to 7.15e-04). The benefit counts only the risk change you supply or the voting change; the blowdown valve and PCN work are in the cost but not credited with a benefit of their own.

Merged into the example shutdown model (after inspection, before box-up), with the same seed: P50 duration -0.25 days, direct cost 477.1 at P50, total cost 452.4. Differences of a few tenths of a day are sampling noise (the added activities change the random stream); the cost increase is the signal.

## Safety of the change itself
Every modification needs management of change, a review of the PCN and SIS changes (FAT, SAT, proof-test and cybersecurity requirements of the standards your site cites; IEC 61511 and IEC 62443 are named here, not read), and a pre-startup safety review. Put them in the estimate and the schedule. Sensor additions change the SIF architecture: the workflow reports PFDavg only, not hardware fault tolerance, spurious trips or diagnostics (`sil_lifecycle` covers HFT and SFF).

## Limits
Screening models: relief sizing needs a code-compliant calculation and vendor data before purchase; the vapour-fire model is a transient screen with assumed flux and strength; no two-phase or multicomponent relief in this workflow (use `twophase` separately); no hydraulic network model for the rerouted line beyond the inlet loss check; no resource-loaded schedule; no unit rates are shipped, and the example numbers are placeholders.
