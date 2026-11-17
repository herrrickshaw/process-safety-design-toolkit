# Open-source ways to simulate the process and its costs

Searched and checked on 2026-11-06. Licences are read from each repository's licence file or GitHub metadata; activity is the last push date on GitHub. **None of these tools was run for this page**; capability statements come from repository descriptions, documentation pages and search summaries, so test a tool on a case you know before relying on it. The toolkit does not depend on any of them: they are references, cross-checks or places to get inputs.

## What a simulator gives the toolkit
A flowsheet simulator produces the stream compositions, pressures and temperatures, equipment duties and sizes that the toolkit takes as inputs: relieving conditions and omega for `relief` and `twophase`, depressuring volumes and gas properties for `depressuring`, equipment lists for the cost estimators, and throughput for the shutdown margin. The cost estimators in turn replace the commercial costing link (UniSim with Cleopatra) with open parts.

## Flowsheet and thermodynamic simulators
| Tool | Licence (checked) | Activity | Fit | Caveats |
|---|---|---|---|---|
| [DWSIM](https://dwsim.org) | GPL-3.0 | GitHub repo DanWBR/dwsim shows **archived**, last push 2026-07-17, 544 stars | Steady-state and dynamic sequential-modular simulator, CAPE-OPEN, Python scripting. Published comparisons exist for LNG-type cycles (PRICO against Aspen Plus; boil-off re-liquefaction cycles): abstracts only seen, so the agreement is not confirmed | Archived repository: check dwsim.org for where development continues. GPL: use as a separate program, never copy source into this MIT toolkit. A paid third-party capital cost add-on exists |
| [NeqSim](https://github.com/equinor/neqsim) and [neqsim-python](https://pypi.org/project/neqsim) | Apache-2.0 | active (push 2026-11-05), 163 and 116 stars | Thermodynamics and process simulation for oil and gas, from Equinor; Python wrapper over a Java library (needs Java) | LNG examples not confirmed in this search; verify properties against CoolProp for your fluids |
| [COCO simulator](https://www.cocosimulator.org) | not checked | site reachable | CAPE-OPEN flowsheeting, free to use per its site | Licence terms unverified: do not assume open source |
| [IDAES-PSE](https://github.com/IDAES/idaes-pse) | custom licence text (GitHub reports "Other"); read it | active (push 2026-11-04), 355 stars | Equation-oriented flowsheets in Pyomo with optimisation, plus a **costing framework** (see below) | Steeper learning curve; the licence is not a standard one |
| [Pyomo](https://github.com/Pyomo/pyomo) | Sandia-copyright licence text (GitHub reports "Other"); read it | active, 2,559 stars | The modelling and optimisation layer under IDAES; DAE tools for custom dynamic models | A toolbox, not a simulator |
| [OpenModelica](https://github.com/OpenModelica/OpenModelica) | OSMC Public License (GitHub reports "Other") | active, 1,474 stars | General dynamic modelling, usable for custom blowdown or flare network models | Not process-specific; licence is the OSMC-PL |
| [Cantera](https://github.com/Cantera/cantera) | BSD-style (Caltech) text | active, 882 stars | Thermochemistry and kinetics (combustion, reactors); relevant to `reaction_hazard` and flame modelling | Not a flowsheet simulator |

## Properties (already used here as oracles)
CoolProp (MIT), `thermo`, `chemicals`, `fluids` (MIT) feed `docs/VALIDATION.md` and `data/fluid_screening.json`. See `docs/LITERATURE.md`.

## Process-safety dynamics
| Tool | Licence | Notes |
|---|---|---|
| [HydDown](https://github.com/andr1976/HydDown) | MIT, 47 stars, last push 2026-09-30 | Blowdown and depressurisation of **pure gas-phase** species with CoolProp and wall heat transfer. A natural independent check of `depressuring.py` and the vessel-fire models; pure species only, no multicomponent or two-phase |
| The toolkit | MIT | `depressuring`, `release`, `vapour_fire`, `flare_system`, `twophase` are screening models; multicomponent, two-phase and network dynamics need a rigorous tool (gPROMS Flare and ProSim DEP are commercial; no open equivalent was found) |

## Costing and techno-economics
| Tool | Licence | What it does |
|---|---|---|
| [IDAES costing framework](https://idaes-pse.readthedocs.io/en/main/reference_guides/core/costing/costing_framework.html) and [SSLW library](https://idaes-pse.readthedocs.io/en/main/reference_guides/model_libraries/generic/costing/process_costing_sslw.html) | custom text | Costing blocks on flowsheet units, costs normalised to a CE index of 500; the library uses base and purchase cost correlations from Seider et al. (textbook) for compressors, heat exchangers, pumps, flash units, reactors, turbines. HX1D (shell-and-tube area) not supported |
| [BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam), [thermosteam](https://github.com/BioSTEAMDevelopmentGroup/thermosteam) | University of Illinois/NCSA Open Source License | Open-source process simulation with techno-economic analysis: installed cost by Lang factor or bare-module factors |
| [OpenPyTEA](https://github.com/pbtamarona/OpenPyTEA) | MIT, 40 stars, push 2026-11-05 | Equipment cost estimation, cash flow and uncertainty evaluation for process plants |
| [ORIMIZ open-fel1-lng-cost](https://github.com/ORIMIZ-Consulting/open-fel1-lng-cost) | MIT | LNG liquefaction concept cost by analogs; the data behind `lng_cost` |
| NETL QGESS | US government publication | Method for equipment-factored estimates; see `docs/COST_ESTIMATION.md` |

## A workable open chain for an LNG-type case
1. Properties and fluid screening: CoolProp, `fluiddata` (this toolkit).
2. Flowsheet: NeqSim or DWSIM (or IDAES for an optimisation-oriented model) for stream and equipment data.
3. Safety screens on that data: `relief`, `twophase`, `depressuring`, `flare_system`, `qra`; independent check with HydDown for pure-gas blowdowns.
4. Plant cost: `lng_cost` (analogs) now; IDAES/SSLW or BioSTEAM factors for an equipment-factored check.
5. Safety modification cost: `recommendation_cost`; shutdown cost and lost days: `shutdown_risk`.

## Gaps found
No open-source equivalent of a commercial two-phase flare network or blowdown dynamic tool was found; the multicomponent LNG liquefaction cycle models in the open tools were not verified against plant data here; the DWSIM source repository is archived. Add rows only after testing.
