# Related open-source projects (GitHub survey, 2026-11-03)

Found with `gh search repos` (about 50 keyword queries across the toolkit's topics) plus direct checks of well-known libraries. Stars, licences and
dates are as of the survey. **Only READMEs and repository metadata were read; the code was not run or audited.** Most relevant projects are young and
low-star, and none covers the full breadth of this toolkit. Licences matter: no licence means all rights reserved, and GPL code must not be copied
into an MIT project (use such tools as separate programs, not as source).

## Closest functional overlaps
| Project | Licence | What it covers | How it relates to this toolkit |
|---|---|---|---|
| [CalebBell/fluids](https://github.com/CalebBell/fluids) (465★), [thermo](https://github.com/CalebBell/thermo) (796★), [chemicals](https://github.com/CalebBell/chemicals), [ht](https://github.com/CalebBell/ht) | MIT | ChEDL suite: piping hydraulics, API 520 relief sizing and API 526 rounding, separator K-factors, properties, heat transfer | Best independent cross-check for `relief`, `hydraulics`, `separator`, `props`. Maintained; use as a test oracle, not a replacement |
| [CoolProp/CoolProp](https://github.com/CoolProp/CoolProp) (1108★), [Cantera](https://github.com/Cantera/cantera) (879★) | MIT / BSD-like | high-accuracy properties; kinetics | what `props` approximates without dependencies |
| [Tahir-yamin/ReliefCraft-API520](https://github.com/Tahir-yamin/ReliefCraft-API520) | MIT | PSV sizing workbench: API 520/521/526, ASME VIII, CoolProp, scenario engine, drawings and reports; 45+ self-test assertions | overlaps `relief`; richer fluid properties and deliverables |
| [CCSR2002/PRD-Fire-Case-Sizing](https://github.com/CCSR2002/PRD-Fire-Case-Sizing) | none stated | web calculator, API 2000 and 520 fire heat load (uses the same tiered Q equations as `tank_venting`) | cross-check for `tank_venting.fire_heat_input_W`; do not copy (no licence) |
| [Mo-Somji/PRV-Program](https://github.com/Mo-Somji/PRV-Program), [amirsadafi/psv-sizing-api521](https://github.com/amirsadafi/psv-sizing-api521) | none stated | PyQt PRV design to API 520; PSV sizing per API 521 | small, unvetted |
| [SIHPCC/pyeldqm](https://github.com/SIHPCC/pyeldqm) (PyPI `pyeldqm`) | MIT | Gaussian plume/puff, **dense-gas Britter-McQuaid**, source models (pipeline, tank, two-phase), pool/jet fire, flash fire, BLEVE, AEGL/ERPG/IDLH database, evacuation | fills the dense-gas gap this toolkit flags in `dispersion`/`rmp`/`lng` |
| [lyullee/slabx](https://github.com/lyullee/slabx) (+ slabx-lh2, degali) | README says MIT; GitHub detects none, check the file | Python reimplementation of the SLAB dense-gas model (LNG example reproduces a field trial: 449 m vs 455 m measured), liquid-hydrogen extensions | closest open stand-in for the dense-gas models regulations name (DEGADIS/SLAB class) |
| [LiaungYip/arcflash](https://github.com/LiaungYip/arcflash) | MIT | IEEE 1584 (2018) AC arc flash, tested against the standard's annex examples and 144,000 cases from the official spreadsheet | covers what `electrical` deliberately does not (IEEE 1584 for enclosed equipment) |
| [ChrisPienaarThree/process-safety-toolkit](https://github.com/ChrisPienaarThree/process-safety-toolkit) | MIT (docs CC BY 4.0) | browser tools: What-If, HAZOP manager, LOPA manager, fault tree and PFD calculator, event tree, bow tie, with Excel workbooks and training guides | overlaps `hazop`, `sil`, `reliability`; adds study-management UIs |
| [Ahmedhassan676/Separator-Sizing](https://github.com/Ahmedhassan676/Separator-Sizing) | none stated | notebook following the Svrcek separator-sizing papers | overlaps `separator`; unlicensed |
| [Ianshaw93/hac-canvas](https://github.com/Ianshaw93/hac-canvas) | MIT | hazardous-area classification canvas (IEC 60079-10-1); **pre-build**, only a demo plot plan so far | watch; fills the extent-calculation gap in `electrical` |

## Risk and reliability engines
| Project | Licence | Notes |
|---|---|---|
| [rakhimov/scram](https://github.com/rakhimov/scram) (168★) | GPL-3.0 | probabilistic risk analysis: fault trees, event trees, MCS, uncertainty; C++ |
| [public-fta/pfta](https://github.com/public-fta/pfta), [yawnoc/sfta](https://github.com/yawnoc/sfta) | GPL-3.0 | Python fault-tree analysers |
| [idaholab/EMRALD](https://github.com/idaholab/EMRALD) | MIT | dynamic risk assessment (Idaho National Laboratory) |
| [volkm/dftlib](https://github.com/volkm/dftlib) | GPL-3.0 | dynamic fault trees |
| [hyperpolymath/BowtieRisk.jl](https://github.com/hyperpolymath/BowtieRisk.jl) | MPL-2.0 | bow-tie toolkit in Julia |
| [usman19zafar/SIS-Dynamic-and-SIL-t-Framework](https://github.com/usman19zafar/SIS-Dynamic-and-SIL-t-Framework), [rootkiller6788/mini-safety-instrumented-system](https://github.com/rootkiller6788/mini-safety-instrumented-system) | other / none | SIL(t) framework; a teaching SIS in C (IEC 61508/61511 voting, SIL/LOPA) |

## Process safety management and education
[ishandutta2007/Awesome-Process-Safety-Management](https://github.com/ishandutta2007/Awesome-Process-Safety-Management) (MIT list), [factplusfancy/pca_bare](https://github.com/factplusfancy/pca_bare)
(PSM-CAP app, PHP), [kannanpnp/bowtie](https://github.com/kannanpnp/bowtie), [ansafwat/pse-calculator-enb](https://github.com/ansafwat/pse-calculator-enb) (process safety event calculator),
and several student chemical-engineering calculator repos (unvetted).

## Gaussian-plume and misc.
Many small plume repos exist ([pktparticle/gaussianPlume](https://github.com/pktparticle/gaussianPlume), [yunhal/CH4_dispersion](https://github.com/yunhal/CH4_dispersion),
[AdrijaDhar/DispersionPro](https://github.com/AdrijaDhar/DispersionPro), [joshuanunn/really-simple-dispersion](https://github.com/joshuanunn/really-simple-dispersion)); they are comparable to
`dispersion` and share its limits. [HazemMancy/Flowstead](https://github.com/HazemMancy/Flowstead) is a GPL-3.0 process-simulation workbench for Android.

## What the survey did NOT find
No open repository covering the toolkit's full breadth; no open flare-radiation (API 521) tool; no open OISD, NFPA 59A or API 2510 implementations (the standards are paywalled);
no open Seveso/OSHA PSM data library beyond this toolkit's parsed tables. Search terms that returned only noise (Cloudflare "flare", gaming "relief valve", etc.) were discarded.

## Suggested uses
1. Add an optional cross-check test suite that compares `relief`, `hydraulics`, `separator` and `props` against `fluids`/`thermo`/CoolProp when installed.
2. Point users to `pyeldqm`/`slabx` for dense-gas consequence work and `arcflash` for IEEE 1584, rather than reimplementing them here.
3. Do not copy GPL or unlicensed code; cite and link instead.

## Added 2026-11-06 from a pasted list (existence, licence and version checked on GitHub and PyPI; code not read)
These sit next to the toolkit rather than overlap it: the toolkit does design-stage screening calculations, while these cover plant
monitoring, control and cyber-physical safety.

| Project | Licence | What it is (from its own metadata) | How it relates |
|---|---|---|---|
| [p4lsec/otsafe](https://github.com/p4lsec/otsafe) (8★, last push 2025-05-22) | Apache-2.0 | detection-as-code and safety modelling for cyber-physical systems | operational-technology security and control-loop safety; no process-safety calculations. Pairs with LOPA/SIL work on the security side of a SIF |
| [petrobras/BibMon](https://github.com/petrobras/BibMon) (107★, last push 2026-05-22; PyPI `bibmon` 1.2.0) | Apache-2.0 | predictive models for fault detection, soft sensing and process condition monitoring | operations-phase monitoring; could feed measured data into the reliability and proof-test inputs, not a design tool |
| [gressling/sproclib](https://github.com/gressling/sproclib) (PyPI `sproclib` 3.0.1) | MIT | Standard Process Control Library for chemical process control and plant design | control design and dynamics; the toolkit has no process control |
| [processpi](https://processpi.org) (PyPI `processpi` 0.2.1) | MIT | chemical engineering simulations, equipment design, unit conversions | general unit-operation calculations; check its coverage before assuming it matches the toolkit's API-based modules |
| [iapws](https://github.com/jjgomera/iapws) (PyPI 1.5.5) | **GPL v3** | IAPWS water and steam properties | use as a separate tool or test oracle only; do not copy source into this MIT project |
| [pyXSteam](https://github.com/drunsinn/pyXSteam) (PyPI 0.4.10) | not stated on PyPI | port of the XSteam water and steam tables | no licence stated means treat as all rights reserved until confirmed |

Not related: PyPI [`safety`](https://pypi.org/project/safety/) scans Python dependencies for vulnerabilities (software security, not process safety). The pasted
list also mentioned unnamed "Bowtie / SMS" scripts and a Reddit thread; neither was verified. The toolkit already has its own `bowtie` module.
