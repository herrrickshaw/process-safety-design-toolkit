# How process simulation and safety studies are built: a literature map

Generated from `process_safety/data/modelling_studies.json` and `modelling_map.json` (compiled 2026-11-26). Regenerate: `python -m process_safety modelling --markdown > docs/MODELLING_STUDIES.md`.

## Read this first

* **Two layers.** A map of 2077 catalogue records (titles and abstracts screened by rule, **not read**), and 69 works (31 of them theses) whose full text, or the parts stated on each sheet, were read by AI research agents.
* **Quote check.** Before the audit corrections, each tool, step, choice, validation, sensitivity and limitation entry had to match an exact quote in the saved text. This shows the passage exists, not that the paraphrase or the study is right. Objectives, tool chains, lessons and caveats are the reader's own. No human has checked the sheets.
* **Not a systematic review.** The searches are not exhaustive, the read set is a purposive sample of openly available works (English-heavy), and several are student theses. Counts here do **not** estimate how common a practice is.
* **Not design guidance.** Use a published model's choices as questions to ask about yours, not as values to copy.

## Audit

Checked once on 2026-11-26 by three AI agents that had not written the sheets, against the saved texts. They covered 70 sheets, which include all 69 published here, and reported 121 findings, 24 of them marked wrong; the corrections were applied. Several false or unsupported claims that a named work contained errors were removed or reworded. The check was partial for long documents (targeted sections and searches, not every page listed as read), figures were not examined, and links, DOIs and bibliographic details were not verified online. The corrections were not audited again, corrected fields were not matched to quotes again, and the cross-study synthesis was not independently audited. No human has checked the sheets. One thesis sheet was left out because the thesis asks for the author's permission before material from it is published (its catalogue record stays in the map).

## What the read works did about validation

The kind each sheet records, from the parts read. Counts describe this sample only.

| Kind | Works |
|---|---|
| experiment | 33 |
| plant-data | 7 |
| code-to-code | 11 |
| literature-values | 3 |
| none-reported | 15 |

## How studies of each type are built

Synthesis across the read works. Each point is the compiler's reading and names the sheets it rests on; one or two sheets support an observation, not a rule.

### Simulation-assisted hazard identification and safeguard studies (HAZOP, LOPA, process safety time)

In these works a simulator is mostly used to say what a deviation does, how far it goes and how fast, rather than to replace the team study.

- One route sweeps a deviation over a continuous range in a flowsheet model, not as a single high or low case. This can expose jumps between operating branches in reactive units. (`janosovsky-2016-automated-model-hazop`)
- The model's own limits matter for the safety conclusion: the same authors later revisit their earlier simulations and show why model-parameter uncertainty such as reaction enthalpy should be carried through the deviation study. (`janosovsky-2018-cahazop-bottlenecks`)
- Dynamic response can change the screening result. Reactor studies simulate controller action and transients because a steady-state view does not show whether control moves a mild deviation into an unstable region. (`danko-2019-lopa-hazop-bifurcation`, `mokhtarname-2020-styrene-dynamic-hazop`)
- Boundary specifications and automatically inserted controllers decide what a dynamic model can show. In one air-separation study, holding pressures fixed gave a flow trend the thesis calls opposite to real plant behaviour. (`matos-2009-dynamic-hazop-air-separation`)
- Process safety time from a dynamic simulator depends on stated start and end points and on modelling choices such as the pipe pressure-drop correlation. Report each alarm, trip and relief time separately, and treat influential choices as sensitivity cases. (`akintoye-2016-pst-alarm-response`, `harun-2021-operator-response-columns`, `outomuro-2020-flare-hipps-dynamic`, `ruan-2026-dme-hazop-lopa`)
- A reconstruction of a past accident can be checked against recorded quantities; one overfill study used a deliberately simplified equipment surrogate and compared level and temperature with the investigation record and another model. (`isimite-2014-texas-city-dynamic-hazop`)
- Several of these sheets record no comparison with plant or test data for the dynamic response itself, so the simulated timing is an unvalidated model output there. (`akintoye-2016-pst-alarm-response`, `mokhtarname-2020-styrene-dynamic-hazop`, `ruan-2026-dme-hazop-lopa`, `matos-2009-dynamic-hazop-air-separation`)
- Inherent-safety indices are scored from a flowsheet's streams and inventories. The inventory basis and each sub-score need to be traceable. (`lozano-2020-inherent-safety-index`, `meramo-2020-h2-gasification-isi`)

### Relief, flare, blowdown, runaway and other dynamic models

These studies depend on transient behaviour, so what was fitted and what was predicted needs to be kept apart.

- For an existing plant, one flare-study method first rates the dynamic models against the normal historical operating range, then applies stated rules for each scenario's failures and the credit given to controllers. (`firth-2016-refinery-dynamic-relief-flare`)
- The coldest case for piping may not be simultaneous full-plant blowdown: partial blowdowns, liquid low points, connected units and sensor placement all matter when comparing with measurements. (`richardson-saville-1995-blowdown-validation`)
- In blowdown validation, pressure agreement is weak evidence when a discharge coefficient or relaxation time was fitted to the same test. Minimum temperature and its timing, and held-out tests, are the stronger checks. (`andreasen-2026-hyddown-validation-manual`, `zheng-2017-depressurisation-superheating`)
- Heat transfer, thermocouple response and behaviour near the CO2 triple point each need checking before a temperature mismatch is blamed on one cause. (`cirrone-2023-cryo-h2-tank-blowdown`, `zheng-2018-co2-pipeline-decompression-thesis`)
- Runaway vent sizing by dynamic simulation was checked against small-scale tests, which agreed without an exhaust line and differed with one. By contrast, steady-state feed sensitivities alone do not show a transient runaway. (`mizuta-2022-runaway-vent-sizing-dynamic`, `ferreira-da-silva-2018-pan-reactor-safety`)
- Start-up, compressor and operator-training models are compared with plant records. Logged transients test more than steady points, and the imposed or tuned inputs determine which outputs are real checks. (`liedman-mansson-2013-compressor-dynamic`, `rosslee-2020-once-through-boiler-startup`, `sangaran-haron-2017-ethylene-ots`)
- Discretisation can decide the answer: with phase change, an end-point exchanger model can remove the optimum being studied. (`jacobsen-2007-hysys-dynamic-c3mr`)

### Consequence analysis and quantitative risk assessment with integral tools

The usual chain is scenario list, hole size or release type, source term, consequence model, then frequencies, ignition, weather and population in a risk integrator. The read works show where results move.

- Analyst and method choices cause large spread: in a benchmark where teams assessed the same facility, frequency estimates still differed by orders of magnitude after site assumptions were aligned. Publish scenario definitions, pipe lengths, use factors, failure data and source-term averaging. (`lauridsen-2002-assurance-qra-benchmark`)
- The risk integrator is itself a source of difference: with identical frequencies and consequences, tools still gave different risk results. It can be tested separately with fixed footprints. (`boot-2013-qra-calculation-method-differences`)
- Regulatory method, representative substance, ignition probability and software version all change contours, so record them with every result. (`silva-2025-cetesb-vs-dutch-tank-depot-safeti`, `weber-2024-ips-qra-guideline-ammonia-riskcurves`)
- With matched inputs, different dense-gas packages can still change distances and the individual risk curve. Name the package and version and check decision distances with a second model. (`salazar-2016-dense-gas-models-ammonia-qra`, `cassim-2023-aloha-slab-npp-control-room`)
- Frequency effort belongs on the events that set the risk contour, which need not be those with the longest consequence range. (`ramos-2012-bayesian-qra-offshore-lng-terminal`)
- Uncertainty can be reported as a percentile band using a two-loop sampling design, with the location of exposed people treated as part of the scenario. (`schroeder-2024-hyram-qra-uncertainty`)
- Check that each generic hole size is physically possible for the equipment, and that the tool's printed inputs match the stated scenario. (`kwak-2023-hrs-urban-hyram-phast-lup`, `cassim-2023-aloha-slab-npp-control-room`)
- Comparisons with experiments are mixed and depend on tool, quantity and averaging rule: hydrogen and propane jet works report both over- and under-prediction, and dense-gas scores depend on segment and averaging choices. (`saturnino-2024-hydrogen-phast-hyram-aloha`, `shum-2021-hyram-propane-validation`, `witlox-2013-phast-udm-lng-phmsa-validation`, `sawyer-2007-aloha-low-wind-validation`, `chang-2019-jack-rabbit-ii-model-intercomparison`)

### CFD studies of dispersion, ventilation, fire and explosion

The model is built from geometry, a source description, mesh, turbulence and combustion settings and boundary conditions; several of these are first-order choices.

- The leak source is a modelling decision in its own right: expanded-jet sizing of the leak cell, local refinement, roughness and wind speed change the answer for jets and dense clouds. (`schleder-2015-flacs-barriers-lpg`, `quillatre-2017-lng-vapour-flacs-cfx-phast`)
- Turbulence and near-wall settings can dominate low-momentum buoyant leaks in small enclosures. (`ghatauray-2019-h2-passive-ventilation-cfd`)
- Validate the quantity the risk study uses. One offshore study validates and tests cloud volume, including its sensitivity to the concentration threshold and the scaling used to reuse one simulation for other cases. (`jones-2015-flacs-dispersion-era-frozen-cloud`)
- Detector and ventilation studies derive an acceptance cloud size from consequences first; changing fuel changes that criterion as well as the dispersion. (`giacopinelli-2016-flacs-gas-detection`, `miles-2021-h2-gas-turbine-enclosure`)
- Fire studies check both the physical and the grid non-dimensional numbers against the validation envelope, and test grid effects on every output used. (`clarke-2020-fds-live-fire-training`, `nrc-epri-2012-nureg1934-fire-modeling-guide`)
- Prescribed inputs can make a comparison circular, and a coupled predictive sub-model is not automatically better than a prescribed one. Check surface heat feedback and independent measurements. (`malkocevic-2025-fds-ventilation-geometry`, `saptogino-2020-firefoam-pool-fire`)
- A design rule fitted to a solver that omits a pressure-raising mechanism rests on removing that mechanism in practice; show validation points one by one. (`choi-2017-flacs-vented-explosion-vessels`)
- Parameters tuned on a test weaken that test as validation, so keep calibration and validation cases apart. (`tran-2019-openfoam-dense-gas-lng-validation`)

### Process flowsheet and equation-oriented models

These supply the stream and equipment data that safety studies build on, so their errors carry forward.

- Property methods are a main risk: a default cubic equation of state converged but was badly wrong for a reactive molten feed, and good binary fits did not make a flowsheet reliable for supercritical components. (`chagas-2021-unisim-sulfuric-acid`, `rossanese-2016-vcm-flowsheet-thermo-validation`)
- Real composition and phase envelope should be checked before simplifying a stream that feeds dispersion work. (`nair-2022-sour-gas-dispersion-uncertainty`)
- In equation-oriented work, initialisation is part of the model, and fitted data should be reported separately from validation data. (`akula-2022-idaes-mea-capture`)
- A parameter tuned on a data set makes comparison with that set calibration, not validation. (`gomes-2015-gproms-piperazine-capture`, `akula-2022-idaes-mea-capture`, `brucel-2025-steady-state-simulation-validation`)
- Say which part of a flowsheet the data test. Validated sub-models or one validated stage do not validate the integrated process. (`reeve-2020-leeds-bio-oil-reforming`, `usmani-2020-unisim-integrated-gasifier`, `dutta-2011-nrel-thermochemical-ethanol`)
- Switching from a rate-based steady-state model to an equilibrium dynamic one needs checks across the disturbance range, not only at the design point. (`zhang-2016-aspen-dynamics-mea-control`)
- Code-to-code benchmarks need matched property options and component data, and should report non-converged cases. Agreement between simulators is not agreement with a plant. (`andreasen-2022-dwsim-vs-hysys-separation`)

### How far to trust a result: evaluation protocols, blind tests and users

Method guidance and benchmark works describe how a model's credibility is established for a stated use.

- Evaluation protocols compare predictions with listed experiments using stated measures and acceptance ranges. A pass applies to the grid, source model and boundary treatment tested. (`kohout-2011-fds-lng-dispersion-mep`, `cruse-2026-drift-3-7-23-model-evaluation`, `smedis-1999-dense-gas-model-evaluation-draft`)
- Passing statistics are not sufficient on their own: rerun decision-relevant example cases for each model version, since hazard ranges can move. (`cruse-2026-drift-3-7-23-model-evaluation`)
- State whether predictions were blind, report point-wise and arc-wise scores separately, and flag runs outside a model's stated applicability. (`smedis-1999-dense-gas-model-evaluation-draft`, `skjold-2017-hysea-blind-prediction-vented-h2`)
- Users matter: analysts using the same CFD code, and teams using their own tools on one vented-explosion or risk problem, produced widely different answers. (`hall-1998-emu-cfd-dispersion-user-variability`, `skjold-2017-hysea-blind-prediction-vented-h2`, `lauridsen-2002-assurance-qra-benchmark`)
- Fire-model guidance expresses accuracy as bias and scatter for each output quantity within a stated validated range, with a rule for parameters outside it. (`nrc-epri-2014-nureg-1824-s1-fire-model-vv`, `nrc-epri-2012-nureg1934-fire-modeling-guide`)
- For plant models, agree the acceptance band from measurement variability before tuning, and keep data used for correction apart from data used to test. (`brucel-2025-steady-state-simulation-validation`)

## The map

2077 records: 450 thesis, 1109 journal, 125 conference, 88 report, 75 book-chapter, 46 preprint, 184 other. 1124 have an open link as reported by the catalogue (not checked). 354 were tagged from the title alone. Theses are listed in `docs/MODELLING_THESES.md`; search everything with `python -m process_safety modelling TEXT --tool T --study S`.

Records whose title or abstract mentions both the tool and the study type. The numbers reflect the search queries as much as the literature: do not read them as popularity.

| Tool | hazop-pha | lopa-sil | qra | dispersion | fire | explosion | relief-blowdown | reaction-hazard | inherent-safety | domino-structural | operability-ots | fault-diagnosis | data-driven | design-tea | validation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Aspen HYSYS | 10 | 5 | 8 | 4 | 5 | 9 | 7 |  | 6 | 1 | 108 | 4 | 6 | 37 | 45 |
| Aspen Plus | 15 | 2 | 5 | 2 |  | 8 | 2 | 1 | 11 |  | 29 | 2 | 11 | 85 | 44 |
| UniSim | 2 |  |  | 2 |  | 1 |  |  |  |  | 13 |  | 9 | 17 | 49 |
| gPROMS | 1 |  |  | 2 |  |  |  |  |  |  | 18 |  | 9 | 21 | 50 |
| CHEMCAD |  |  |  |  |  |  |  |  |  |  | 5 |  |  | 11 | 23 |
| DWSIM |  |  |  |  |  |  |  |  |  |  | 6 |  | 6 | 17 | 29 |
| FLACS | 1 |  | 12 | 54 | 11 | 90 | 3 | 1 | 1 | 5 | 1 |  | 2 |  | 36 |
| Aspen Plus Dynamics | 7 | 1 | 4 | 1 | 1 | 2 | 4 | 1 |  | 1 | 43 | 1 | 15 | 14 | 12 |
| PRO/II |  |  |  |  |  | 1 |  |  |  |  | 8 | 1 | 5 | 15 | 14 |
| Modelica / Dymola |  |  | 1 |  |  |  |  |  | 1 |  | 10 |  | 2 | 6 | 5 |
| IDAES |  |  |  |  |  | 1 |  |  |  |  | 1 |  | 14 | 20 | 13 |
| OLGA | 1 |  |  | 1 |  | 1 | 9 |  |  |  | 7 |  | 3 | 1 | 17 |
| PHAST | 10 | 1 | 20 | 13 | 16 | 26 | 1 |  |  | 3 |  |  | 1 |  | 7 |
| Fire Dynamics Simulator |  |  | 1 | 5 | 30 | 4 |  | 1 | 1 | 3 | 1 |  | 3 |  | 39 |
| OpenFOAM |  |  |  | 18 | 11 | 14 | 1 |  |  |  |  |  |  |  | 21 |
| HyRAM | 1 |  | 19 | 8 | 10 | 7 | 3 |  |  |  |  |  |  |  | 12 |
| FireFOAM |  |  |  | 2 | 28 | 2 |  |  | 1 |  |  |  |  |  | 23 |
| BioSTEAM |  |  |  |  |  |  |  |  |  |  |  |  | 1 | 26 | 11 |
| ALOHA | 2 |  | 5 | 10 | 2 | 5 |  |  |  |  |  |  | 1 | 2 | 3 |
| Safeti | 2 |  | 18 | 4 | 2 | 5 |  |  |  | 3 |  |  |  |  |  |
| ANSYS Fluent |  |  |  | 4 | 3 | 2 | 2 | 1 |  |  | 2 |  | 1 | 1 | 10 |
| NeqSim |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3 |
| ProMax |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 5 |

Column keys: `hazop-pha` hazop and hazard identification; `lopa-sil` lopa, sil and instrumented protection; `qra` quantitative and probabilistic risk assessment; `dispersion` release and dispersion; `fire` fire; `explosion` explosion; `relief-blowdown` relief, flare, depressuring and blowdown; `reaction-hazard` runaway reaction and thermal hazard; `inherent-safety` inherently safer design; `domino-structural` escalation, domino and structural response; `operability-ots` dynamic operability, start-up and operator training; `fault-diagnosis` fault detection and diagnosis; `data-driven` surrogates, machine learning, digital twins and language models; `design-tea` process design, optimisation and techno-economics; `validation` model validation, comparison and uncertainty.

## Study sheets

Grouped by the first study type each sheet lists.

## HAZOP and hazard identification

### Aplicacao do HAZOP dinamico na avaliacao de perigo operacional em uma coluna de destilacao de uma planta de separacao de ar

`matos-2009-dynamic-hazop-air-separation` · Juliana Schmitz Guarilha Costa Matos · 2009 · masters-thesis · Universidade Federal do Rio de Janeiro (EQ/UFRJ)

[Open copy read](http://www.tpqb.eq.ufrj.br/download/aplicacao-do-hazop-dinamico.pdf) · read: Chapter VI (method and model conversion), parts of chapter VII (results), chapter VIII (conclusions)

**Objective.** Use dynamic simulation to check and extend a conventional HAZOP of the lower column of a cryogenic air separation plant.

**Tools.**
- Aspen Hysys (steady state) (version: not stated): Existing company steady-state model used as the starting point and comparison.
- Aspen Plus Dynamics (version: 11.1): Rebuilt steady-state then dynamic model on which the HAZOP deviations were simulated.

**How the study was built.**
1. Choose the most self-contained subsystem whose deviations have visible safety or operability consequences, starting from the existing conventional HAZOP section.
2. Rebuild the HYSYS model in the second simulator and tune the reflux ratio until the steady state is close to the original.
3. Convert to dynamic mode after adding tray dimensions, then check that the dynamic base case matches the steady state.
4. Apply the deviation after 5 hours of simulated normal operation.
5. When automatically inserted controllers hide a deviation, weaken or neutralise them and repeat the run to expose the uncontrolled response.

**Modelling choices.**
- Substitute simulator: A different simulator from the company's was used because only it was available at the university with dynamics.
- Blocked line representation: The solver would not converge with a fully closed valve, so it was left 2% open.
- Reflux ratio disturbance: The ratio could only be changed in the steady-state model, so a series of steady-state cases was exported to dynamics one by one.

**Tool chain.** Conventional HAZOP worksheet selects deviations; Hysys steady-state model is converted to Aspen steady state, exported to Aspen Dynamics, and each deviation response is compared back against the HAZOP.

**Validation (code-to-code).** Only the steady states of the two simulators were compared: after tuning, shelf-stream flow differed by -7.42% and kettle flow by +5.42%, which the author judged acceptable. The dynamic responses were not validated against plant data.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- With column pressures held fixed, raising a feed pressure produced the opposite shelf and kettle flow trend to that expected in the real plant.
- The whole plant could not be simulated dynamically because of licence availability and limited experience with the tool.
- The conclusions assume that the simulation can reproduce real plant behaviour.

**Reusable lesson (compiler's).** Before using a pressure-driven or flow-driven dynamic model for HAZOP, check what the boundary specifications and auto-inserted controllers hold constant: a fixed pressure can reverse or erase the consequence you are looking for.

**Caveats.** Master's thesis; text is in Portuguese. The external-fire case was imitated by raising ambient temperature with software default heat-transfer values and is not a fire load model. Section VII.1 says the result of raising the F2 feed pressure (less shelf flow, more kettle flow) is the opposite of what is expected in real plant operation and attributes this to fixed column pressures; section VIII.1 lists the same trend as an observation of the dynamic study on a hazard for which the conventional HAZOP had identified no cause.

### Dynamic simulation of Texas City Refinery explosion for safety studies

`isimite-2014-texas-city-dynamic-hazop` · Joseph Isimite, Philip Rubini · 2014 · conference · IChemE Hazards 24, Symposium Series 159 (University of Hull)

[Open copy read](https://www.icheme.org/media/8953/xxiv-paper-58.pdf) · read: Full paper

**Objective.** Reproduce the raffinate splitter start-up of the 2005 Texas City accident dynamically, then use the model for a more-temperature HAZOP scenario.

**Tools.**
- Aspen HYSYS (version: not stated): Dynamic filling and heating of the column.

**How the study was built.**
1. Replace the flooded distillation column with a tank separator because no separation was taking place while it filled.
2. Set vessel liquid volume as column internal volume less the volume taken by internals.
3. Lump the many feed hydrocarbons into four carbon-number groups from C5 to C8.
4. Take initial conditions from published investigation data and run the accident timeline in stages as heat input changes.
5. Rerun with a guide-word deviation plus the failures of the day, and plot it against the reconstructed incident.

**Modelling choices.**
- Feed rate: Averaged to 16.3 kg/s because reported rates varied.
- Dynamic HAZOP scenario: More temperature: all four burners lit from 10:00, with the bottom level valve closed.

**Tool chain.** Investigation report data build the HYSYS dynamic model, which is then reused for the deviation scenario.

**Validation (plant-data).** Compared with accident records: simulated liquid level 47.9 m at 1:12 pm against 48 m at 1:02 pm in the CSB report, and temperature said to match another published UniSim simulation closely.

**Sensitivity or uncertainty.** One alternative heat-input scenario; complete feed vaporisation occurred much earlier than on the incident day.

**Limitations the authors state.**
- The significance lies in extending the model to dynamic HAZOP rather than in a rigorous reconstruction.
- Behaviour downstream of the column was not studied.

**Reusable lesson (compiler's).** A deliberately simplified equipment surrogate can be fit for an overfill scenario if you state which phenomena it drops and check level and temperature against records.

**Caveats.** The year is not printed in the saved text (the page header gives Symposium Series 159, Hazards 24). The level agreement compares a simulated value at 1:12 pm with a reported value at 1:02 pm. The paper notes it has been suggested that the vapour behaviour on the day cannot be accurately predicted by standard tray-separation models in commercial simulators.

### Automated Model-based HAZOP Study in Process Hazard Analysis

`janosovsky-2016-automated-model-hazop` · Ján Janošovský, Juraj Labovský, Ľudovít Jelemenský · 2016 · journal · Chemical Engineering Transactions, vol. 48

[Open copy read](https://www.aidic.it/cet/16/48/085.pdf) · [DOI](https://doi.org/10.3303/CET1648085) · read: Full paper

**Objective.** Present a software tool that generates HAZOP deviations, runs them in a commercial simulator and produces a HAZOP-like report, shown on an ammonia synthesis reactor system.

**Tools.**
- Aspen HYSYS (version: v8.4): Simulation engine for each deviation.
- In-house automated HAZOP tool (version: not stated): Builds the deviation list, drives HYSYS, stores a snapshot of each state and supports analysis and reporting.

**How the study was built.**
1. Connect to an open simulation case and check which streams and units can be deviated.
2. Let the user choose streams, parameters and deviation ranges, from which the deviation list is generated and then simulated.
3. After each run, save a snapshot of key process variables for all streams.
4. Interrogate the snapshots with fixed questions such as loss of reaction, runaway possibility, the most sensitive stream and unexpected vapour.
5. Sweep the deviation magnitude continuously and look at the rate of change to find step changes.

**Modelling choices.**
- Deviation magnitude: Deviations are expressed as percent of design value; feed temperature was swept from +30% to -30% (175 to 325 degC).
- Human role: Results are evaluated with a human expert team; the tool is support, not replacement.

**Tool chain.** Tool generates deviations, HYSYS solves them, snapshots go to a shared database, and the analysis module writes a HAZOP-like table.

**Validation (none-reported).** No numerical comparison. The authors note that the simulated multiple steady states resemble the behaviour described by Morud and Skogestad (1998).

**Sensitivity or uncertainty.** Deviation-magnitude sweeps found a drop of about 60% in reactor outlet temperature near an 18% feed-temperature deviation, attributed to a shift between steady states.

**Limitations the authors state.**
- Uncertainty in any model input can strongly change the results of a model-based HAZOP.
- The method is only as complete as the mathematical model is reliable.

**Reusable lesson (compiler's).** Sweep each deviation over a wide continuous range and flag discontinuities: a single high or low value can miss a jump to another operating branch.

**Caveats.** Short conference-style paper; property package, reactor kinetics and solver mode are not stated. No comparison with plant data.

### Computer Aided HAZOP Study Implementation Bottlenecks in Chemical Industry

`janosovsky-2018-cahazop-bottlenecks` · Ján Janošovský, Matej Danko, Juraj Labovský, Ľudovít Jelemenský · 2018 · journal · Chemical Engineering Transactions, vol. 67

[Open copy read](https://www.aidic.it/cet/18/67/039.pdf) · [DOI](https://doi.org/10.3303/CET1867039) · read: Full paper

**Objective.** Review where simulation-based HAZOP results can mislead, using an alkylpyridine N-oxidation CSTR and an ammonia synthesis reactor.

**Tools.**
- Aspen HYSYS (version: not stated): Ammonia synthesis case.
- MATLAB (version: not stated): Authors' own N-oxidation reactor model.

**How the study was built.**
1. Use HAZOP guide words to generate the simulation inputs, then grade the severity of each simulated state.
2. Give each qualitative deviation a numerical size and duration before it can be simulated.
3. Extend the deviation range far enough, including the return path, to detect multiple steady states.
4. Perturb an uncertain model parameter (here the reaction enthalpy) and see whether the map of safe operating points moves.

**Modelling choices.**
- Safe window, N-oxidation case: Reactor temperature to be held within 110 to 125 degC.
- Parameter perturbation: Reaction enthalpy raised by 10%.

**Validation (none-reported).** This is a retrospective critique of the authors' earlier simulations; no new comparison with measurements is reported.

**Sensitivity or uncertainty.** A 10% higher reaction enthalpy greatly moved the simulated safe operating regions. Below 210 degC fresh-feed temperature the ammonia reactor temperature dropped rapidly.

**Limitations the authors state.**
- Simulation-based HAZOP results still need verification and further analysis by experienced engineers.
- Too narrow a deviation range can hide potentially severe events.

**Reusable lesson (compiler's).** For reactive nodes, propagate model-parameter uncertainty (the paper tested reaction enthalpy) through the deviation study; a safe-region result computed with one parameter set is not a safety conclusion.

**Caveats.** Short paper; HYSYS version and model details are deferred to earlier publications.

### Use of LOPA and HAZOP Concepts for Complex Automated Hazard Identification

`danko-2019-lopa-hazop-bifurcation` · Matej Danko, Ján Janošovský, Juraj Labovský, Zuzana Labovská et al. · 2019 · journal · Chemical Engineering Transactions, vol. 77

[Open copy read](https://www.aidic.it/cet/19/77/135.pdf) · [DOI](https://doi.org/10.3303/CET1977135) · read: Full paper

**Objective.** Combine steady-state, bifurcation and dynamic analysis to test, layer by layer, whether process design and basic control contain HAZOP deviations in a propylene glycol CSTR.

**Tools.**
- Own mathematical model (steady-state algebraic and dynamic ODE reactor model with PI control) (version: not stated): Solves steady-state branches, bifurcation maps and dynamic deviation responses; the software used is not named in the paper.

**How the study was built.**
1. Write the reactor and jacket mass and energy balances as both a steady-state system and a dynamic system.
2. Plot steady-state solution diagrams for the most influential deviation, with and without controller movement of the manipulated variable.
3. Build a two-parameter bifurcation map of disturbance variable against manipulated variable that marks stable, oscillating and unstable regions.
4. Overlay each deviation before and after controller action, then confirm suspect cases with a dynamic run.
5. Record the results as a HAZOP table with impact, likelihood, risk matrix rank, safeguards and recommendations.

**Modelling choices.**
- Kinetics: Taken from the Fogler textbook.
- Safety limit: 97 degC, above which much of the mixture evaporates.
- Control model: Proportional-integral controller.

**Tool chain.** Steady-state branches feed the bifurcation map, which picks deviations for dynamic runs; results populate the HAZOP table.

**Validation (none-reported).** None reported in the parts read.

**Sensitivity or uncertainty.** Four propylene oxide feed deviations are shown (A +30%, B +66%, C +120%, D -17%). The text says all except A can become dangerous because controller action can move them into oscillating or unstable regions, but also that for B the controller got the system out of the oscillation region. The conclusions name C and D as most hazardous, with process control initiating temperature oscillation.

**Limitations the authors state.**
- Once a controller is added, ordinary steady-state diagrams can no longer predict the response because the manipulated variable changes continuously.

**Reusable lesson (compiler's).** Credit the control system only after simulating it: for exothermic reactors, test whether controller action itself moves a mild deviation into an unstable regime.

**Caveats.** Not a commercial simulator study and the solving software is not named. The abstract refers to PID control while section 2.2 describes PI action. No frequency calculation or PFD values are given beyond broad likelihood classes. The statement that all deviations except A can become dangerous through controller action sits beside the statement that for B the controller moved the system out of the oscillation region.

### Toward HAZOP 4.0 Approach for Managing the Complexities of the Hazard and Operability of an Industrial Polymerization Reactor

`mokhtarname-2020-styrene-dynamic-hazop` · R. Mokhtarname, A. A. Safavi, L. Urbas, F. Salimi et al. · 2020 · conference · IFAC World Congress 2020 preprints

[Open copy read](http://web.archive.org/web/20240411163259id_/https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/1256.pdf) · read: Full paper (figures not readable); re-extracted from the fetched PDF in reading order

**Objective.** Support a conventional HAZOP of two cascade styrene polymerisation reactors with a first-principles dynamic model that handles deviation size, double failures and propagation.

**Tools.**
- MATLAB (version: not stated): First-principles dynamic model of the reactors and condensers with control loops.

**How the study was built.**
1. Complete a conventional HAZOP without safeguards and tag entries by complexity: amplitude and time dependence, multiple failures, or domino effect.
2. Screen a few credible scenarios for simulation using accident lessons and operator experience.
3. Model polymerisation kinetics with the method of moments plus material and energy balances for reactor and condenser.
4. Rerun the screened scenarios with the basic control loops present.
5. Vary the failure size and add a second failure to find where control stops coping.

**Modelling choices.**
- Vapour-liquid equilibrium: Ideal behaviour assumed, with Flory-Huggins activity for the polymer solution.
- Kinetic constants: Taken from published experimental work (Hui et al., 1972).

**Tool chain.** Conventional HAZOP worksheet selects scenarios; the MATLAB model returns consequences for the team.

**Validation (none-reported).** None reported in the parts read.

**Sensitivity or uncertainty.** With the pressure valve also failed, feed temperatures above 387 K gave a sudden pressure and temperature rise ending in thermal runaway; smaller steps gave a higher steady temperature.

**Limitations the authors state.**
- Model development cost and effort, and verification of both model and simulated faults, remain open practical issues.
- Multiple-failure and domino studies become tedious for complex processes with many interacting parameters.

**Reusable lesson (compiler's).** Tag HAZOP rows that depend on magnitude, timing, double failure or propagation, and spend dynamic-modelling effort only on those.

**Caveats.** The plant is described as real and industrial but no comparison with plant data is shown. Preprint conference version retrieved from a web archive.

### Quantitative HAZOP-LOPA analysis of a dimethyl ether distillation unit based on aspen plus steady-state and dynamic simulation

`ruan-2026-dme-hazop-lopa` · Jindi Ruan, Gang Tao, Lijing Zhang · 2026 · conference · Journal of Physics: Conference Series, vol. 3345 (AMCE-2026)

[Open copy read](https://doi.org/10.1088/1742-6596/3345/1/012036) · [DOI](https://doi.org/10.1088/1742-6596/3345/1/012036) · read: Full paper

**Objective.** Quantify a HAZOP of a dimethyl ether column with LOPA frequencies, steady-state safe windows and dynamic operator response times.

**Tools.**
- Aspen Plus (version: not stated): Steady-state flowsheet and feed deviation sensitivity.
- Aspen Plus Dynamics (version: not stated): Control-failure transients and response times.

**How the study was built.**
1. Run a guide-word HAZOP on the column nodes and treat consequences as LOPA scenarios and causes as initiating events.
2. Sweep feed flow and feed temperature and tabulate the deviation at which each monitored variable reaches its threshold.
3. Turn on tray hydraulics so the percentage of flooding load becomes a deviation limit.
4. Export to dynamics, add control loops, settle for an hour and check recovery from small step disturbances.
5. For each control failure, take the time to reach a design safety threshold as the available operator response time.

**Modelling choices.**
- Property method: NRTL.
- Protection layer PFDs: About 0.01 for a SIL 1 interlock or a relief valve (and about 0.1 for alarm plus operator), referred to CCPS and IEC 61511.
- Initiating event frequency check: A value of 0.1 per year for a valve failing open was compared with an OREDA-2015 fail-to-open-on-demand rate of the same order.
- Dynamic pressure limit: 17.0 bar top pressure, about 60% above normal operating pressure.

**Tool chain.** HAZOP deviations feed LOPA arithmetic; the Aspen Plus model gives steady-state thresholds and is exported to Dynamics for response times, which then guide alarm versus SIF allocation.

**Validation (none-reported).** A section headed model validation says tray composition trends are consistent with distillation theory and compares base-case outputs with design or operating values. The T1 top and bottom pressures and the 80% reactor conversion among them are also given as model design parameters or block specifications. No measured plant or experimental data are described.

**Sensitivity or uncertainty.** Feed flow and temperature swept from -50% to +50%; dynamic cases gave response times from a few minutes (complete condenser failure) to several hours.

**Limitations the authors state.**
- Only one compound-fault combination was examined.

**Reusable lesson (compiler's).** Use dynamic response times to decide which LOPA operator credits are plausible, but check first that the validation is independent of the inputs and that every number agrees across text, tables and conclusions.

**Caveats.** Section 4.3 gives the overall safe window for feed flow as -30% to +11% (flooding load), while the abstract and the end of section 4.4 use -30% to +40%; Table 5 places the 80% flooding threshold at +11%. For complete condenser failure section 5 says the top temperature reaches 120 degrees C at about 20 min and that the response time is about 4-5 min, without stating from when the latter is counted. The 0.1 per year frequency for a control valve failing open is supported by comparison with an OREDA-2015 rate for a differently named mode, fail to open on demand. Interlock and relief-valve PFDs are generic order-of-magnitude values, and the 17 bar dynamic limit is not tied to a stated vessel design pressure.

## LOPA, SIL and instrumented protection

### Determination of Alarm Safety Response Time

`akintoye-2016-pst-alarm-response` · Ayo Akintoye, Steve Harrow · 2016 · conference · IChemE Hazards 26, Symposium Series 161 (Amec Foster Wheeler)

[Open copy read](https://www.icheme.org/media/11753/hazards-26-paper-16-determination-of-alarm-safety-response-time.pdf) · read: Full text; figure and table images were not readable in the saved text

**Objective.** Describe how process safety time for alarms and safety instrumented functions is estimated by hand and then confirmed with dynamic simulation, applied to a para-xylene plant column.

**Tools.**
- Aspen HYSYS Dynamics (version: not stated): Confirmed and adjusted hand-calculated PST for hazard scenarios.

**How the study was built.**
1. Take hazard scenarios needing protective functions from the SIL/LOPA reviews.
2. First estimate PST as the margin between alarm set point and the hazardous value divided by an estimated rate of change from mass or energy balance.
3. Simulate each scenario from steady state, including equipment, pipelines and shutdown valves, by applying the scenario's disturbance (for low sump level, feed stopped together with a failed level transmitter).
4. Record the PST for each scenario in the instrument database and cause-and-effect matrix and use it for SIF response time.
5. Use PST in alarm classification to test whether an alarm can be credited and to set its priority.

**Modelling choices.**
- Hazard point: Where the true failure condition is uncertain, the equipment design limit is assumed.
- PST start and end: In the applied cases PST runs from the alarm set point to the equipment or inventory limit.
- Operator time criterion: A minimum of the order of 20-30 min for a safety alarm layer, attributed by the authors to EEMUA 191.

**Tool chain.** SIL/LOPA scenarios feed a hand estimate, then HYSYS Dynamics, then the instrument database, cause-and-effect matrix and alarm rationalisation.

**Validation (none-reported).** The hand estimate is said to be reaffirmed and adjusted by simulation; no numerical comparison is given in the text.

**Sensitivity or uncertainty.** None reported in the parts read.

**Reusable lesson (compiler's).** Define PST start and end points explicitly: this paper quotes a standard definition starting at the initiating failure but measures from the alarm set point.

**Caveats.** Numerical PST results are in figures and tables that did not extract. The 20-30 minute operator-time criterion should be checked against the guideline itself, which was not read here; another paper in this set (harun-2021) cites 10 minutes from the same guideline. The editions cited are BS EN 61511 (2004) and EEMUA 191 (2007).

### Selected process safety systems analysed using dynamic simulations: A study of the Flare and the High Integrity Pressure Protection Systems

`outomuro-2020-flare-hipps-dynamic` · Ana Xiao Outomuro Somozas · 2020 · masters-thesis · Aalborg University

[Open copy read](https://vbn.aau.dk/ws/files/335444154/Master_Thesis_Ana_Outomuro.pdf) · read: Methodology chapters 4-5, results and discussion chapters 6-7, conclusions, part of the appended draft paper

**Objective.** Test whether dynamic simulation improves on steady-state design for a flare network, and find the process safety time (PST) available to a HIPPS and how much model detail that PST needs.

**Tools.**
- Aspen HYSYS Dynamics (version: V9): Dynamic emergency depressurisation of three flare networks and blockage-driven pressure build-up for HIPPS timing.
- Aspen HYSYS Event Scheduler (version: V9): Triggers the downstream blockage at a set simulation time.
- Aspen Flare System Analyzer (existing models) (version: not stated): Source of flare piping and fittings data and the steady-state reference.

**How the study was built.**
1. Build the HYSYS flare network from existing flare analyser data and first run it with fixed source pressures to compare against that reference before going dynamic.
2. For the dynamic depressurisation case, open every blowdown valve at once and switch boundaries to zero-flow sources with a pressure boundary at the flare.
3. Add a third, more detailed flare case that includes dead legs and inactive relief and control valve tail pipes, to test how much hold-up volume matters.
4. For HIPPS, model the blockage as a normally fully open valve that closes, with the ESD valves assumed to fail, so pressure builds upstream.
5. Compute PST from the pressure trace as the time between reaching the HIPPS set point and reaching the maximum allowable working pressure.
6. Compare several pipe pressure-drop correlations for their effect on the HIPPS time response.

**Modelling choices.**
- Equation of state: Peng-Robinson; C7+ fractions as lumped hypothetical components.
- Flare run length and time step: 15 min simulated at a 0.01 s step; the 15 min follows the API 521 depressuring recommendation as quoted by the author.
- HIPPS pressure settings: ESD alarm 140 bar, HIPPS alarm 155 bar, design pressure (MAWP) 170 bar.
- HIPPS boundaries: Well inlets are fixed-flow sources so inflow stays constant during the blockage; the outlet is a pressure boundary.
- Pipe pressure-drop model: Beggs and Brill (1973 and 1979), HTFS homogeneous, Tulsa Unified and a simplified friction model compared; the author prefers Tulsa as it generally gives the shortest PST.
- Flare pipe discretisation: Flare piping split into many segments or increments to offset the weakness of the pipe pressure-drop method for compressible gas.

**Tool chain.** Flare analyser piping data and steady-state plant simulation compositions feed the HYSYS dynamic flare models; the HIPPS study is a separate HYSYS flowsheet whose pressure traces give PST.

**Validation (code-to-code).** A fixed-pressure HYSYS run was set up to be checked against the existing flare analyser model (peak load, relief rates, pipe pressure drops); the sections read report no numerical agreement for that check. No plant or test data for HIPPS PST.

**Sensitivity or uncertainty.** Pipe correlation, feed rate, blockage location and elevation ratio were varied; the quoted conclusion is that the simplified friction model gave unreliable, longer (less conservative) PST.

**Limitations the authors state.**
- The HYSYS pipe segment cannot represent phase slip; the author judges this negligible for the mostly vapour flare lines studied.
- Irregularities in the Tulsa-model pressure curves are attributed to possible numerical instability in the software, not physics.
- The finding that elevation detail matters little is not conclusive: elevation ratios were varied on only one 100 m segment.

**Reusable lesson (compiler's).** When a simulator supplies PST for a fast safeguard such as a HIPPS, treat the pipe pressure-drop correlation and boundary specification as sensitivity cases and report the shortest credible time. The tabulated values ranged from about 1.5 s to about 211 s; the largest comes from the simplified friction model, which the author considers unreliable (the four flow correlations reach 164 s).

**Caveats.** The HIPPS layout is hypothetical. Section 7.1 labels Case 1 as Beggs and Brill (1979), although Case 1 is defined as the 1973 version. With the Tulsa model, PST rises between 180,000 and 200,000 kg/h in scenarios 2 and 4; the author flags this and suggests numerical instability. Section 7.1 links the longer PST of the 1979 Beggs and Brill case to over-estimated pressure drop, while the conclusions link the longer PST of the simplified model to under-estimated pressure drop.

### Assessment of Operators' Response Time on Safe Operation of Distillation Columns: A Process Dynamic Analysis

`harun-2021-operator-response-columns` · Darmawan Ahmad Mukharror, Zalina Harun, Zulfan Adi Putra, Nik Abdul Hadi Md Nordin · 2021 · conference · IChemE Hazards 31, Symposium Series 168

[Open copy read](https://www.icheme.org/media/27725/hazards-31-paper-29-harun.pdf) · read: Full paper

**Objective.** Follow up a LOPA on two refinery columns by simulating cooling water and reflux failures to find operator response time and check relief behaviour.

**Tools.**
- iCON-Symmetry (version: v2020.3): Dynamic models of two columns and their overpressure scenarios.

**How the study was built.**
1. Take LOPA concerns (relief adequacy and time for operators to isolate) as the questions for the dynamic study.
2. Build each column from drawings, datasheets, cause-and-effect matrix, relief load calculations, control valve data and control narratives.
3. Include equipment sizes, elevations and the control configuration.
4. Run each event and measure the time from the initiating failure to relief valve opening.
5. Rerun the worst case with staggered relief valve set pressures to study chattering.

**Modelling choices.**
- Property method: Advanced Peng-Robinson, chosen for light hydrocarbons.
- Scope exclusion: Structural effects of relief forces were assumed to add no hazard.
- Protection layer credit: The existing high-high pressure alarm was not treated as an independent protection layer.

**Tool chain.** LOPA findings define scenarios; plant documents feed the dynamic model; the timings go into updated operating procedures.

**Validation (code-to-code).** Relief valve adequacy from the simulation is said to agree with the relief load calculation documents; no numbers are compared and there is no plant-data validation.

**Sensitivity or uncertainty.** Two columns, two failure types and three relief set-pressure arrangements. In column C-1 cooling water failure all five relief valves opened in about 9 min.

**Reusable lesson (compiler's).** Report the time between each alarm, trip and relief event separately. Then ask whether the window left for the operator is realistic before it goes into a procedure or LOPA credit.

**Caveats.** The updated procedure gives operators two minutes (C-1) and one minute (C-2) after the high-high pressure alarm, while the paper itself cites a 10 minute EEMUA 191 benchmark for acceptable operator response; the authors say control-room operators can quickly push the safety switch, and no human-factors assessment is shown. The conclusion that fewer relief valves would suffice rests on the dynamic simulation, with no relief sizing review of it presented. The text gives one Option 1 set point as 10%, while Table 1 lists 22.4 barg for that valve.

## Quantitative and probabilistic risk assessment

### Assessment of Uncertainties in Risk Analysis of Chemical Establishments. The ASSURANCE project. Final summary report

`lauridsen-2002-assurance-qra-benchmark` · Kurt Lauridsen, Igor Kozine, Frank Markert, Aniello Amendola et al. · 2002 · official-report · Risoe National Laboratory, Risoe-R-1344(EN), with EC Joint Research Centre

[Open copy read](https://backend.orbit.dtu.dk/ws/files/7712279/ris_r_1344.pdf) · read: uncertainty framing, chapters 3 to 5 (plant, qualitative phase, frequency and consequence comparison), chapters 7 and 8; the land-use planning chapter only in part

**Objective.** Benchmark exercise in which seven teams independently analysed the same ammonia storage plant, to measure and explain the spread between quantitative risk analyses.

**Tools.**
- Each team's own QRA methods and tools (not named in the parts read) (version: not stated): Quantitative risk analysis of the common plant
- Fault trees, event trees and generic data (version: not stated): Frequency assessment, in different combinations between teams

**How the study was built.**
1. Give all teams one documented reference plant, with a single site visit, shared question-and-answer material, common assumptions and fictitious data where needed.
2. Let each team do hazard identification and screening, then compare the selected scenarios and the ranking conventions.
3. Each team quantifies its own scenarios plus a common set of reference scenarios, so that results can be compared item by item.
4. Tabulate each team's top-event frequencies and underlying assumptions (pipe length, use factor, components, failure causes, data source) to find causes of deviation.
5. Rerun the frequencies with agreed site characteristics (pipe length, use factor, number of transfers, tanks in use) to remove deviation caused by ambiguous inputs.
6. Break consequence modelling into outflow, pool, dispersion and dose-response stages and list the sources of uncertainty at each.

**Modelling choices.**
- Common engineering assumptions: Imposed where possible in the quantitative phase to remove their influence on the comparison.
- Scenario definition for catastrophic tank rupture: Left to the teams at first; definitions ranged from instantaneous loss of the whole inventory to partial roof failure, giving different source terms.
- Ammonia evaporation fraction for release onto water: Teams assumed anywhere from 8% to 60% of the total release evaporated, a main reason this scenario showed the largest consequence discrepancy.
- Source-term to dispersion interface: Time-varying release rates had to be reduced to average, maximum, minimum or corrected values by judgement when the dispersion model could not take them.
- Dense or passive dispersion model: An analyst judgement; the dispersion models used were all box models with similar structure.

**Tool chain.** Hazard identification and screening produce the scenario list; frequency structures and generic data give top-event frequencies; outflow, pool evaporation, dispersion and probit steps give consequences; both are combined into individual and societal risk and then compared for land-use planning.

**Validation (code-to-code).** Team-to-team comparison only. After fixing common site characteristics the authors say the frequency spread was considerably reduced, basically to 1 to 2 orders of magnitude, except for loading-arm scenario 17; their summary table still lists maximum-to-minimum frequency ratios of 615 for loading-arm scenario 4 and 248 for scenario 7*, besides 14000 for scenario 17. The ranking of least probable scenarios agreed among the probabilistic teams, and the largest differences overall were in frequencies.

**Sensitivity or uncertainty.** A case study fixed common site characteristics and recalculated frequencies; the authors also give a qualitative star ranking of factors, with scenario definition ranked highest.

**Limitations the authors state.**
- The qualitative ranking of uncertainty factors comes from this exercise and is not claimed to hold for all plants and analyses.
- Part of the frequency spread came from limited access to plant staff and an ambiguously worded scenario set, which may be particular to the exercise.
- Parameter uncertainty was the only one of the three uncertainty types that could be measured.

**Reusable lesson (compiler's).** Before comparing or trusting QRA numbers, fix and publish scenario definitions, pipe lengths, use factors, transfer counts, failure-data source and source-term averaging; much of the spread comes from these choices rather than from the solver.

**Caveats.** Single facility and one substance (toxic ammonia); the exercise dates from about 2000 and tools have changed. The report masks the plant and uses altered surroundings and fictitious population data. Figures were not readable in the text extraction.

### Análise de Riscos da Unidade de Craqueamento Catalítico da REDUC

`pinto-2007-reduc-fcc-risk-analysis-phast` · Geovani Moraes Pinto, Rodrigo Sgambato Roberto · 2007 · bachelor-thesis · Universidade Federal do Rio de Janeiro, Escola de Química

[Open copy read](https://pantheon.ufrj.br/server/api/core/bitstreams/385eb2f4-dcc4-4b27-86dd-55709f6876d8/content) · read: chapter III method, chapter V frequencies, start of chapter VI, scenario result tables, chapters VII-VIII

**Objective.** Assess hazards of a refinery fluid catalytic cracking unit with a preliminary hazard analysis, fault and event trees and PHAST consequence modelling.

**Tools.**
- PHAST (version: 6.51): Consequence simulation of five pipe-rupture scenarios.

**How the study was built.**
1. Select initiating events from the preliminary hazard analysis that can harm the outside population or environment.
2. Quantify each with a fault tree using per-metre pipe rates and per-item component rates for a counted list of line lengths, valves and flanges.
3. Multiply by event-tree probabilities for immediate ignition, delayed ignition and explosion.
4. Replace each refinery stream with a representative pure component or simple mixture.
5. Tabulate inputs and effect distances per scenario for two weather cases and draw circles on a satellite image.

**Modelling choices.**
- weather cases: F stability with 1.0 m/s and A stability with 5.0 m/s, meant to bracket least and most dispersion.
- inventory: Release over 10 minutes, the assumed detection and valve-closure time.
- failure frequency source: Values from the TNO guidelines for quantitative risk assessment.
- vulnerable area: Largest effect distance rotated into a circle, while noting the area actually hit depends on wind or jet direction.

**Tool chain.** Hazard analysis picks events; fault trees give frequencies; event trees split them; PHAST 6.51 supplies effect distances.

**Validation (none-reported).** No comparison reported.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The quantitative work rests on assumptions; a more precise study needs more detailed plant and inventory data.

**Reusable lesson (compiler's).** A usable template for the per-scenario input and result sheet. Tie the chosen weather pairs to local meteorological data.

**Caveats.** Undergraduate final project. Chapter VII of the saved text defines individual and societal risk and shows tolerability criteria; no calculated individual-risk contours or F-N curve for the unit were found in it (figure content is not extracted). Two event-tree figures are both numbered V.6.

### Desenvolvimento de Metodologia Bayesiana de Análise Quantitativa de Risco para Terminais Offshore de GNL: Aplicação para o Porto de Suape

`ramos-2012-bayesian-qra-offshore-lng-terminal` · Marilia Abílio Ramos · 2012 · masters-thesis · Universidade Federal de Pernambuco

[Open copy read](https://attena.ufpe.br/bitstream/123456789/11886/1/Disserta%c3%a7%c3%a3o_marilia_ramos.pdf) · read: chapter 3 method, section 6.1 consequences, start of 6.2 frequencies, sections 6.2.4-6.3 event trees and risk, chapter 7

**Objective.** Build a QRA method for a hypothetical offshore LNG terminal in which initiating-event frequencies come from Bayesian population-variability analysis of generic failure data.

**Tools.**
- PHAST (version: 6.5413): Consequence distances for line ruptures and tank catastrophic rupture.
- RiskCurves (version: 7.6.8): Individual risk contours.

**How the study was built.**
1. Run a preliminary hazard analysis, then carry only representative scenarios from the two highest severity classes, as initiating events, into simulation.
2. Model pipe ruptures with the PHAST line-rupture model and the storage tank with the catastrophic-rupture model.
3. Update a diffuse lognormal prior with several generic failure databases (population-variability stage only, since no plant data exist).
4. Build event trees with immediate and delayed ignition branches and multiply them by the initiating frequency.
5. Combine frequencies and consequences in a risk tool and identify which initiating event sets the contour.

**Modelling choices.**
- LNG composition: Treated as pure methane.
- release duration: 2 minutes assuming automatic isolation, following the Purple Book.
- release duration, loading arms: 30 seconds, because nearby workers can start the emergency system.
- release surface: Directly on water with no bund, chosen as conservative because dike areas could not be estimated.
- weather: Day and night averages from three years (2006-2008) of MM5 mesoscale simulation taken from a nearby refinery environmental study.
- delayed ignition probability: 0.2, as very few ignition sources offshore (Cox, Lees and Ang).
- explosion: Excluded because the offshore cloud has no confinement.
- jet fire in risk sum: Frequencies kept in the event trees but jet fire left out of the risk because its ranges were negligible beside flash and pool fire.

**Tool chain.** PHAST consequence distances plus event-tree frequencies (initiating frequencies from the Bayesian step) are combined in RiskCurves.

**Validation (none-reported).** No comparison with experiment or another consequence tool for this study.

**Sensitivity or uncertainty.** Not a parametric study; the risk contours are recomputed without the dominant initiating event to show its influence.

**Limitations the authors state.**
- The dominant loading-arm frequency rests on opinions from only two experts and is therefore quite uncertain.
- With no plant-specific data only the first Bayesian stage was applied, so frequencies rest on generic data.

**Reusable lesson (compiler's).** Rank initiating events by their contribution to the risk contour, not by consequence reach: here the largest-range event was not the one that set the intolerable contour. Spend frequency effort on the one that does.

**Caveats.** Master's thesis. Section 6.2.4 places gas-release event EI03 above 100 kg/s and EI04 between 10 and 100 kg/s, and assigns them immediate-ignition probabilities of 0.04 and 0.09; the thesis's Table 3.4 gives 0.09 for the higher band and 0.04 for the middle band for a low-reactivity gas. Figure 6.17 is captioned EI06 but the heading inside the tree reads EI05 (with the EI06 frequency). The author notes that the terminal offshore distance was set from the consequence results and that a new distance could be set from the risk results; the finding that the shore is unaffected should be read with that choice in mind.

### Quantifying Safety with a QRA: To Agree on the Results, the Method Should Be Explicit

`boot-2013-qra-calculation-method-differences` · Hans Boot · 2013 · journal · Chemical Engineering Transactions vol. 31 (TNO)

[Open copy read](https://www.aidic.it/cet/13/31/002.pdf) · read: whole paper

**Objective.** Explain why QRA tools give different individual and societal risk results, drawn from TNO comparisons made while rebuilding RISKCURVES.

**Tools.**
- RISKCURVES (version: not stated in the body; reference list cites 9.05): Rebuilt QRA tool compared with its previous version and other packages.
- SAFETI-NL (version: not stated in the body; reference list cites 6.54): Comparison package.
- EFFECTS (version: not stated): TNO consequence tool that supplies the model chains to RISKCURVES.

**How the study was built.**
1. Separate consequence-model differences from risk-integration differences by feeding identical lethality footprints into the risk engine.
2. Report how a time-varying release is turned into a dispersion source (segments, average rate or representative rate).
3. Report probits or thresholds for both indoor and outdoor lethality.
4. Report dominant model parameters and any departure from defaults with a reason.
5. Report the risk integration discretisation: grid size, steps and interpolation.

**Modelling choices.**
- toxic footprint representation: Warns that collapsing a footprint into blocks of effective cloud width can seriously underestimate risk, especially near the source.
- indoor toxic lethality: Prefers an indoor dose calculation using ventilation rate over the shortcut of 10 percent of outdoor lethality, which can be very optimistic at high dose.

**Tool chain.** EFFECTS-style consequence models feed RISKCURVES; externally computed footprints can be injected through a damage definition.

**Validation (code-to-code).** Even with identical frequencies and consequences, risk results differed between tools. For toxic individual risk, differences of the order of 50 percent were found, mostly at short range.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Current guidelines leave too many degrees of freedom and the internal calculation method and resolution are often unclear.

**Reusable lesson (compiler's).** Verify a risk-integration engine separately from the consequence models, using fixed footprints. This is directly reusable as a test design for open QRA code.

**Caveats.** Written by the developer of one of the compared tools. No tabulated comparison data or case definition, so the quoted differences cannot be reproduced from the paper. The paper also cites a Belgian tank-park benchmark with larger differences (stated as up to 400 percent); it is second-hand.

### Risk Assessment of a Hydrogen Refueling Station in an Urban Area

`kwak-2023-hrs-urban-hyram-phast-lup` · Jongbeom Kwak, Haktae Lee, Somin Park, Jaehyuk Park et al. · 2023 · journal · Energies 16(9), 3963 (Ajou University)

[Open copy read](http://web.archive.org/web/20261028194701id_/https://www.mdpi.com/1996-1073/16/9/3963) · [DOI](https://doi.org/10.3390/en16093963) · read: HTML text of method, results, discussion and conclusions; table contents and figures were mostly not rendered

**Objective.** Judge whether a hydrogen refuelling station in central Seoul is acceptably sited, using HyRAM jet-fire and overpressure results and a French land-use-planning severity and frequency matrix.

**Tools.**
- HyRAM (version: not stated): Jet-fire heat flux and overpressure for leak scenarios.
- PHAST (version: 8.0): Overpressure impact diameters, including catastrophic rupture, without the mitigation wall.

**How the study was built.**
1. Take weather from a national worst-case and alternative-leak-scenario guideline for flammable gases.
2. Take leak scenario frequencies from a Sandia report for the largest hydrogen inventories.
3. Compute heat flux at chosen points and compare with the national code safety distance.
4. Add a catastrophic rupture case in the second tool because the first did not simulate it.
5. Count exposed people from district population density times effect area, excluding the station footprint, and place each scenario on the severity-frequency matrix.

**Modelling choices.**
- population density: 3919 persons per km2 for the district.
- overpressure thresholds: French land-use values: 200 mbar (5 percent lethality), 140 mbar (1 percent), 50 mbar (irreversible effects).
- notional nozzle: Birch et al. formulation among the options offered.
- rupture frequency: At or below 1e-6 per year taken as typical of general QRAs.

**Tool chain.** HyRAM gives jet-fire and overpressure results; PHAST effect diameters plus population density set the severity class, which is paired with a frequency class in the matrix.

**Validation (none-reported).** No comparison with data; the two tools are not systematically compared.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Results do not credit safety measures that would shorten the fatality distances.
- The 2D integral and engineering tools may not capture the rise of buoyant hydrogen; CFD is suggested.
- Initiators such as vehicle impact, power loss and natural events were not covered.

**Reusable lesson (compiler's).** Check that every scenario hole size is physically possible for the pipe bore before taking generic leak frequencies; here the tabulated large leak exceeded the orifice diameter and the tool could not run it.

**Caveats.** The publisher site refused the fetch, so a Wayback copy was read. Tool version for HyRAM, weather values and several tables are missing from the text. The authors lower the large-leak frequency by argument without quantifying it, and the safety conclusion partly rests on a mitigation wall and on that argument.

### Uncertainty Quantification and Sensitivity Analysis for Quantitative Risk Assessments of Hydrogen Infrastructure

`schroeder-2024-hyram-qra-uncertainty` · Benjamin Schroeder, Dusty Brooks · 2024 · official-report · Sandia National Laboratories, SAND2024-09878

[Open copy read](https://www.osti.gov/servlets/purl/2463031) · read: chapter 1 methodology, chapter 2 results (overview and sensitivity conclusions, cases 3-4), chapter 3 summary, appendix A

**Objective.** Propagate input uncertainty through the HyRAM+ default hydrogen QRA and rank which inputs drive potential loss of life.

**Tools.**
- HyRAM+ (version: V5.0): Deterministic QRA engine evaluated repeatedly with sampled inputs.
- SciPy Latin hypercube sampler (version: not stated): Generated the input samples.

**How the study was built.**
1. Define the system as a component count (valves, instruments, joints, hose, pipe lengths) with state conditions and fuelling demand.
2. Combine component leak frequencies per leak size with fault trees, then use an event sequence diagram to reach jet fire, explosion, no ignition or shutdown.
3. Give leak frequencies, dispenser failure probabilities and occupant positions distributions, and sample them with Latin hypercube sampling.
4. Compare the sampled risk distribution with the deterministic result.
5. Separate occupant location as an outer epistemic loop so that other sensitivities can be ranked by linear regression, checked with scatter plots.

**Modelling choices.**
- leak sizes: Five sizes from 0.01 to 100 percent of pipe flow area.
- ignition probability: Flow-rate bands with immediate values 0.008, 0.053 and 0.23 and delayed values 0.004, 0.027 and 0.12.
- overpressure model: BST method with Mach flame speed 0.35 for delayed ignition.
- harm models: Eisenberg thermal probit with a 30 s exposure (an overpressure head-impact probit is also used).
- detection and isolation: Probability 0.9 that a release is detected and mitigated before posing risk.
- occupants: Nine, uniformly distributed 1-20 m along and 1-12 m across the jet axis.

**Tool chain.** Sampled inputs go through repeated HyRAM+ QRA runs, then regression and scatter-plot analysis.

**Validation (none-reported).** No comparison with data or another code. Only a consistency check: the deterministic result was verified with both the HyRAM+ Python backend and the GUI.

**Sensitivity or uncertainty.** Occupant location dominates; once conditioned on location, full-bore leak frequencies of instruments and then joints lead. Doubling pressure had little effect on the rankings.

**Limitations the authors state.**
- Only parametric uncertainty in selected inputs was treated; physical release model and implicit assumption uncertainties were not.
- Linear regression in single-loop sampling probably understates the effect of strongly nonlinear location variables.
- Published hydrogen failure frequency data are scarce.

**Reusable lesson (compiler's).** Report a hydrogen QRA result with a percentile band, and treat where people stand as part of the scenario definition. A two-loop design stops location from hiding frequency sensitivities.

**Caveats.** The report gives different low ends for the risk spread in two places (to about 1e-14 in the results, about 1e-12 in the summary). Demonstration case is the tool default system, not a real site.

### Evaluation of IPS guidelines regarding Quantitative Risk Analysis

`weber-2024-ips-qra-guideline-ammonia-riskcurves` · Maria Weber · 2024 · masters-thesis · Chalmers University of Technology

[Open copy read](https://odr.chalmers.se/server/api/core/bitstreams/1a66ed58-da9a-40d2-84a8-96afcba495c1/content) · read: chapter 1 scope and bias, chapter 2 method, chapter 3 QRA results, sensitivity and guideline evaluation

**Objective.** Test the Swedish IPS QRA guideline by applying it to a fictitious ammonia plant and judging how usable it is.

**Tools.**
- RiskCurves (spelt RiskCurve in the thesis) (version: 12.0.1): All calculations from source strength through consequence to individual and societal risk.

**How the study was built.**
1. Take generic loss-of-containment scenarios by equipment type from the BEVI manual, and add specific ones from a HAZID.
2. Screen pipelines, keeping only long ones or those crossing a road.
3. Enter weather as a combined matrix of wind direction, wind speed and stability class.
4. Build population as separate residential and operating areas with day and night fractions and time present.
5. Check that the models and vulnerability criteria selected in the software match what the guideline prescribes.
6. Run one-at-a-time sensitivity on influential inputs, then test relocation and smaller storage tanks as risk reductions.

**Modelling choices.**
- frequency source: BEVI for most components, with site data preferred when it exists.
- runaway reaction frequency: Set to 1e-3 as a conservative judgement because it could not be derived.
- delayed ignition method: BEVI delayed-ignition method is recommended only with SAFETI; IOGP is the second, for petroleum-based products; the Moosemiller method is given for other substances.
- ignition probability for ammonia: Calculated instead of taking standard values, because toxicity dominated the pure-ammonia results.
- weather classes: Guideline pairs of wind speed and day/night stability, for example 2 m/s with B by day and F by night, 5 m/s with C or D; wind rose supplied for the site.
- risk grid: Guideline recommends 50 x 50 m cells.
- risk criteria for a new site: Individual risk upper limit 1e-6 per year and negligible level 1e-8 per year.

**Tool chain.** Single tool: RiskCurves.

**Validation (none-reported).** No validation; the inputs and settings were checked by a supervisor.

**Sensitivity or uncertainty.** Filling degree, surface roughness, population data and pump/compressor failure frequency varied one at a time. Population changes left individual risk unchanged (expected); roughness and filling degree visibly changed the contours. None breached the upper societal limit; population and roughness are judged most influential.

**Limitations the authors state.**
- The software behaves largely as a black box; the equations used for source strength could not be traced against the guideline.
- Equipment density, which drives delayed ignition probability, is a subjective choice.
- The author is employed by a consultancy that helped develop the guideline, and the tool vendor supplied the licence.

**Reusable lesson (compiler's).** Treat surface roughness as a first-class uncertainty in toxic-dominated risk contours. Report which ignition-probability method was used and whether it is tied to a particular software.

**Caveats.** Master's thesis on a fictitious site. The method states a factor-of-two variation; Table 3.2 lists filling degree as 40, 80 and 100% under the halved, original and doubled columns. The results call pumps prominent contributors to the risk and also report that changing pump and compressor frequency did not result in larger individual risk. No numerical contour distances to reproduce were found in the saved text.

### Risk assessment of a liquid storage terminal: comparison of Brazilian and Dutch methodologies

`silva-2025-cetesb-vs-dutch-tank-depot-safeti` · Edmilson P. Silva, Fernanda A. Lima, Isabela M. P. Souza, André P. Soares et al. · 2025 · conference · ESREL SRA-E 2025 (Petrobras)

[Open copy read](https://rpsonline.com.sg/proceedings/esrel-sra-e2025/pdf/ESREL-SRA-E2025-P6321.pdf) · [DOI](https://doi.org/10.3850/978-981-94-3281-3_ESREL-SRA-E2025-P6321-cd) · read: whole paper

**Objective.** Re-run a published Dutch benchmark flammable-liquid depot under both Brazilian CETESB P4.261 rules and Dutch rules, and explain the differences in risk.

**Tools.**
- Safeti (version: 9.0 (original benchmark used 6.54)): Updated Dutch-method risk calculation and Brazilian-method risk.
- Phast (version: not stated): Consequence distances under the Brazilian method.

**How the study was built.**
1. Reuse a published fictitious depot with its layout, surrounding population and ignition sources.
2. Change only the aspects and criteria specific to the second country, keeping the rest of the base case.
3. Assign representative substances by the national rules, and screen out low-hazard liquids from the QRA.
4. First re-run the home method in the newer software version to isolate the version effect.
5. Trace contour differences back to individual effect distances for the dominant tank scenarios.

**Modelling choices.**
- failure frequencies: BEVI manual for equipment and CONCAWE data for pipelines.
- representative substances (Brazil): n-decane for crude oil, n-hexane for gasoline, n-nonane for jet fuel.
- explosion model: TNO multi-energy with unconfined strength 10 and 10 percent efficiency.
- fatality assumptions: Thermal exposure capped at 20 s for pool and jet fires in the probit.

**Tool chain.** Phast/Safeti consequence results feed Safeti individual and societal risk.

**Validation (code-to-code).** Dutch-method hazard distances were compared between Safeti 6.54 (published) and 9.0, with no consistent direction of change.

**Sensitivity or uncertainty.** None reported in the parts read.

**Reusable lesson (compiler's).** Record the software version with every risk contour and re-baseline after upgrades. In this comparison the authors link the main Brazil-Netherlands differences to the representative substance for crude oil and the immediate-ignition probability.

**Caveats.** Short conference paper. Weather frequencies and risk grid settings were not found in the text (the hazard table uses D5 and F1.5). The paper says the version 9.0 Dutch-method and CETESB hazard distances were very similar except for Tank 01, but tabulates distances for Tank 01 only. The authors say a more detailed analysis of one difference in the pump and loading areas was not feasible because some radiation ranges were not reported in the original work. The 1e-6 per year contour around the crude tank is reported at about 250 m with version 9.0 against about 160 m with 6.54, and the originally published F-N curve shows more fatalities. The text read is a reading-order re-extraction of the saved PDF.

## Release and dispersion

### Evaluation of CFD modelling of gas dispersion near buildings and complex terrain

`hall-1998-emu-cfd-dispersion-user-variability` · R. C. Hall · 1998 · conference · IChemE Symposium Series No. 144; WS Atkins Safety and Reliability

[Open copy read](https://www.icheme.org/media/10275/xiv-paper-24.pdf) · read: whole paper

**Objective.** Report how much CFD dispersion results vary with the way the same code is applied by four organisations, and their accuracy against wind-tunnel data, plus a complex-terrain chlorine application.

**Tools.**
- STAR-CD (version: not stated): Main CFD code, shared by the four partners for the cases it covered
- ADREA-HF (version: not stated): Second CFD code, developed for atmospheric dispersion
- HGSYSTEM (version: not stated in the text body (reference list cites the 3.0 manual)): Simple-model comparison, scoping and two-phase jet source for the site study

**How the study was built.**
1. Isolate user effect by having all partners use the same CFD code for each test case.
2. Invent new test geometries and run them blind, without access to the wind-tunnel data.
3. Compare partners qualitatively, on hazard-relevant cloud quantities, with point-based geometric bias and variance, and against a simple model.
4. For the complex-terrain site, work in stages: simple-model scoping, flat-terrain CFD, coarse far-field terrain model, then a finer near-field model with buildings.
5. Convert the two-phase jet to a pure vapour source in CFD at the point where little aerosol remains.

**Modelling choices.**
- Mesh design: Each modeller used own or published domain rules with no consensus; mesh design and numerics were a main cause of variability.
- Turbulence model: Changing the k-epsilon model in STAR-CD had little effect, but switching ADREA-HF to k-epsilon could double a hazard range.
- Source conditions: Treated as fundamental; variability was greatest for large instantaneous releases with uncertain initial cloud.
- Inlet turbulence: Velocity profiles were similar across partners but turbulence profiles differed considerably, some unrealistically.

**Tool chain.** In the site study HGSYSTEM scoping and jet calculations provide a vapour source with entrainment sinks to the CFD; a coarse far-field terrain run was meant to give boundary conditions to the near-field run, which proved difficult and was simplified.

**Validation (experiment).** Blind comparison with wind-tunnel data for part of the cases. Separately, at the 1% source-concentration level the four partners' maximum hazard ranges differed by factors of 1.5 to 5; the authors report STAR-CD hazard ranges tending to exceed experimental values.

**Sensitivity or uncertainty.** Effects of turbulence model, mesh resolution and differencing scheme were observed. Finer meshes and higher-order differencing tended to reduce scatter against experiment, but there was little evidence that large cell counts (about 120k to 180k) were much better than 60k to 80k, and bias depended on the turbulence model.

**Limitations the authors state.**
- Mesh-independent solutions were not attainable for practical 3D building-wake dispersion with the computers of the time.
- A finer, numerically better solution need not match experiment better, because mesh and turbulence errors can cancel.
- In the site study the near-field domains were too small for some transient clouds.

**Reusable lesson (compiler's).** Budget for analyst training and independent checking: sign errors, unit conversions, specification reading, mesh rules, source conditions and inlet turbulence all contributed to large differences between analysts using the same CFD code.

**Caveats.** Short conference overview of a longer 1997 project report. Computing power and codes are dated. The publication year is not printed in the extracted text and is inferred from the symposium series number. Some partners were new to the code, so the measured spread includes learning effects.

### SMEDIS Final Report (draft): Scientific Model Evaluation of Dense Gas Dispersion Models

`smedis-1999-dense-gas-model-evaluation-draft` · SMEDIS project partners (coordinated by HSE, with CERC and EdF as main partners) · 1999 · other-report · EU SMEDIS project; draft hosted by the Atmospheric Dispersion Modelling Liaison Committee

[Open copy read](https://admlc.com/wp-content/uploads/2021/06/smedis_draft_final_report-1.pdf) · read: chapter 1, the conclusions of chapter 2, most of chapter 4 (database, validation procedure, results, conclusion) and part of the data selection appendix

**Objective.** Develop and test a protocol for independent evaluation of dense gas dispersion models (scientific assessment, verification, validation), with emphasis on aerosols, obstacles and complex terrain.

**Tools.**
- Dense gas dispersion models in four classes (screening, integral, shallow-layer, CFD) (version: versions listed per model in the report's Table 1.1): Subjects of evaluation: 28 models
- REDIPHEM database (version: not stated): Main source of processed experimental data

**How the study was built.**
1. Write a Model Evaluation Report for each model from a uniform template, using only developer-supplied information and agreeing it with the developer.
2. Select validation datasets by questionnaire to partners on prior use, availability and quality.
3. Classify candidate scenarios by source type, complex effect, gas density and atmosphere, and pick cases to cover the cells.
4. Fix the cases each model class must run, with fewer for shallow-layer and CFD models than for integral and screening tools.
5. Compare both arc-wise and point-wise quantities, using paired measures of bias and scatter plus factor-of-n fractions.
6. Require users to document setup, changed parameters and any model modifications, and to use one model version for all runs.

**Modelling choices.**
- Primary statistics: Mean relative bias and mean relative square error as principal measures, supported by factor-of-n fractions; geometric measures kept for comparison with earlier work.
- Blindness: Users were given the observations, because model improvement during the project was allowed.
- Runs beyond model scope: Users could voluntarily run cases their model could not properly represent, to see the effect, with such mismatches flagged.
- Wind-tunnel data: Allowed alongside field trials, with tunnel cases scaled to full-size equivalents.

**Tool chain.** Developer information feeds the assessment report; processed datasets are issued as spreadsheet workbooks; model proponents return results in a template; two partners compute statistics centrally and add them to each evaluation report.

**Validation (experiment).** Preliminary analysis of the first set of results. Point-wise scores were lower than arc-wise scores. The authors conclude that FAC2 and the spread measures generally improved with model complexity; the chapter body notes that shallow-layer models were an exception for spread, and that on the bias measures integral models looked best except for terrain. Some groups had small samples.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Only the first result set was fully analysed, for lack of resources.
- There are large gaps in data for dense gas releases with complex effects, especially without wind-tunnel data.
- Assessments used only supplied documents, often poorly organised, and the models themselves were not run by assessors.
- Measurement uncertainty, needed to define acceptable agreement, was not always available.

**Reusable lesson (compiler's).** Report arc-wise and point-wise scores separately, state whether predictions were blind, and flag every run outside a model's stated applicability; each of these changes what a pass score means.

**Caveats.** A draft with placeholders, typographic errors and model identities removed from results; do not cite its numbers as final. Validation was not blind and many proponents were developers. The year is taken from file path markers and workshop date in the text.

### Evaluation of Fire Dynamics Simulator for Liquefied Natural Gas Vapor Dispersion Hazards

`kohout-2011-fds-lng-dispersion-mep` · Andrew Joseph Kohout · 2011 · masters-thesis · University of Maryland, College Park

[Open copy read](https://api.drum.lib.umd.edu/server/api/core/bitstreams/9bd45c27-dd2b-4726-84c7-1a9210d5c577/content) · read: abstract, parts of chapter 6 (scientific assessment), chapter 7, start of chapter 8 and the statistical measures table, validation summary, uncertainty analyses, chapter 9; individual trial sections only sampled

**Objective.** Apply the US LNG vapour dispersion model evaluation protocol (scientific assessment, verification, validation) to FDS and recommend how it should be used for siting studies.

**Tools.**
- Fire Dynamics Simulator (FDS) (version: 5.5.1): CFD (large eddy) dispersion model under evaluation
- ABS/FERC pool spread model (version: not stated): Calculated the vapour source term supplied to FDS for spills

**How the study was built.**
1. Assess the model's physics against the protocol's qualitative criteria, noting what needs separate sub-models such as flashing, jetting and pool spread.
2. For verification, review the developer's quality assurance evidence and verification guide rather than auditing code line by line.
3. Compute each spill's vapour source with a separate pool spread model from flow rate and duration.
4. Drive field-trial runs with the measured transient upwind wind, and run until a quasi-steady wind field exists before opening the gas source.
5. Score the protocol's field and wind-tunnel trials, split into unobstructed and obstructed groups and short and long time averages.
6. Turn the observed underprediction bounds into recommended concentration safety factors for each flow-field class.

**Modelling choices.**
- Grid: A base grid of 2 x 2 x 1 m was used for the Maplin Sands, Burro, Coyote and Thorney Island field trials and the CHRC tunnel tests; some other series used other base grids.
- Wind boundary condition: Transient measured wind was used; the imposed fluctuations decay across the domain, which the author links partly to more far-field overprediction.
- Surface roughness: The protocol's roughness values are considered generally low, which can make the model look more conservative than it is.
- Time averaging: Short averages are recommended for flammable centreline concentration because longer averages smooth peaks.
- Recommended safety factors: 2 (half LFL) without obstructions and 3 (one third LFL) with obstructions or sloped terrain.

**Tool chain.** Spill flow rate and duration feed the ABS/FERC pool spread model; its pool area and vaporisation rate become the FDS gas source; measured weather sets the boundary conditions; FDS outputs are scored with statistical performance measures.

**Validation (experiment).** Compared with the protocol's experiments. For unobstructed field trials the author finds good agreement or overprediction of maximum arc-wise concentrations over land and a tendency to underpredict over water. The obstructed Falcon 1 and 3 field trials were underpredicted by about a factor of 2 (Falcon 4 overpredicted). Unobstructed sloped wind-tunnel cases were underpredicted by about a factor of 3, and obstructed scaled wind-tunnel cases agreed worse, mostly underpredicted by a factor of 2 or more.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The recommendations depend on the settings used in the study, including grid resolution.
- The source term strongly controls the result but is outside what the protocol examines.
- Scatter in point-by-point concentrations is wide, with many near-zero predictions away from the plume centreline.

**Reusable lesson (compiler's).** A protocol evaluation is only valid for the grid, source model and boundary treatment tested; carry those settings, and the matching safety factor, into the application study or re-validate.

**Caveats.** Masters thesis; this is not a regulatory approval of FDS. The model version is old. Safety factors are the author's recommendation from this setup.

### Dispersion modelling for explosion risk analysis

`jones-2015-flacs-dispersion-era-frozen-cloud` · Tim Jones · 2015 · conference · IChemE Symposium Series 160, Hazards 25 (MMI Engineering)

[Open copy read](https://www.icheme.org/media/8683/paper-63-hazards-25.pdf) · read: entire paper

**Objective.** Validate FLACS flammable cloud volumes against offshore-module release experiments and test the frozen-cloud shortcut used in explosion risk analysis.

**Tools.**
- FLACS (version: not stated (v10.1 user manual is cited)): CFD dispersion in a naturally ventilated offshore module

**How the study was built.**
1. Convert point concentration measurements into flammable volume by assigning each monitor a cell volume, so the validation target matches the explosion-analysis input.
2. Run a grid sensitivity on one experiment at three cell sizes before choosing the grid.
3. Pick further cases that span release position and direction, flow rate, wind and module wall layout.
4. Investigate an outlier by changing wind speed within experimental error, refining the wake mesh and lowering the cloud concentration threshold.
5. Test frozen-cloud scaling by grouping experiments with the same release and wind direction and predicting each from the others.

**Modelling choices.**
- Grid: 0.5 m, because 0.25 m was not worth its cost given the small differences.
- Turbulence and geometry: FLACS k-epsilon; large objects resolved on grid and small ones as sub-grid drag and turbulence sources.
- Error band: Factor of 1.5 on measured volume, as the experimental report gave no error bars.
- Frozen-cloud extrapolation range: Software guidance limits the mix factor to 0.5 to 2.

**Tool chain.** FLACS concentrations become flammable cloud volumes, which would feed explosion risk analysis; frozen-cloud scaling by mass rate over ventilation rate substitutes for extra CFD runs.

**Validation (experiment).** 1999 joint-industry offshore module releases. The author reports good agreement apart from two cases with jet impingement on a vessel (over-predicted) and C17, under-predicted by about a factor of 4 (about 3 after higher wind and refined wake). Table 2 also shows A02 (240 against 152 m3) and A15 (1656 against 1088 m3) slightly above the paper's factor-1.5 band. For C17, a 4% threshold gave similar measured and computed volumes.

**Sensitivity or uncertainty.** Three grid sizes, wind speed and wake resolution, and flammable-limit threshold.

**Limitations the authors state.**
- The validation data used for the frozen-cloud check are limited and grouped wind directions were not truly constant.
- Frozen-cloud predictions scatter widely and should be verified with CFD for each parameter group before use.

**Reusable lesson (compiler's).** Validate the quantity the risk analysis consumes (cloud volume), report its sensitivity to the concentration threshold, and verify frozen-cloud scaling per release group before relying on it.

**Caveats.** Short consultancy paper. The conclusions say case C17 was over-predicted although the tables and results text show it under-predicted. Grid study based on a single experiment.

### Quantitative dispersion analysis of leakages of flammable and/or toxic substances on environments with barriers or semi-confined

`schleder-2015-flacs-barriers-lpg` · Adriana Miralles Schleder · 2015 · phd-thesis · University of Sao Paulo and Universitat Politecnica de Catalunya

[Open copy read](http://web.archive.org/web/20231228162809id_/https://teses.usp.br/teses/disponiveis/3/3135/tde-20062016-102201/publico/AdrianaMirallesSchleder.pdf) · [DOI](https://doi.org/10.11606/t.3.2016.tde-20062016-102201) · read: reproducibility and grid-dependence part of chapter 3, guiding principles (3.4), field-test set-up (chapter 4), chapter 5 and chapter 6

**Objective.** Assess FLACS for dense-gas releases around obstacles, derive user guidelines, and test them against new propane field releases with and without a fence.

**Tools.**
- FLACS (version: not stated (user manual v10.0 is in the references)): All CFD dispersion simulations, including grid and sensitivity studies
- FLACS jet utility (version: not stated): Estimated the expanded jet area used to size the leak-region cells

**How the study was built.**
1. Test grid dependence by changing each macro-grid cell dimension on its own by 10 and 20 percent, leaving the leak micro-grid unchanged.
2. Represent all objects, including small ones, in the geometry before gridding.
3. Estimate the expanded jet area first, then size the leak cell so the jet sits in one cell no more than twice its area.
4. Grade from fine leak cells to the coarse macro grid, limiting the cell-to-cell change.
5. Place monitor points at the field sensor positions and compare with a factor-of-two criterion and time traces.

**Modelling choices.**
- Grid (field tests): 1 m cubic macro cells; leak cells 0.04 m wide and high from the jet area, and 0.20 m long.
- Domain: Extends 50 m along the jet, starting just upstream of the release.
- Recommended macro cell size for similar dense-gas cases: Height no more than 0.5 and length and width no more than 1.0 m.
- Wind representation: Held constant, although measured speed and direction varied widely during the trials.
- CFLC: Guideline value 20 for dispersion; may be raised with local refinement but lowered again if unstable.

**Tool chain.** A one-dimensional jet utility sizes the leak cells; the time-dependent release rate from the trial drives FLACS; monitor outputs are compared with oxygen-sensor-derived concentrations.

**Validation (experiment).** New LPG trials, one open and one with a fence. FAC2 for centreline peaks 75% and 83%, for all working sensors 70% and 72%; the author quotes mean errors of 13% (unobstructed) and 18% (obstructed) at a snapshot. Concentrations 2 m from the release were badly under-predicted.

**Sensitivity or uncertainty.** Reproducibility, grid dependence and a local input sensitivity study. Cell height mattered most (up to 27% change from baseline) and width least; discharge height, wind speed, atmospheric pressure and mass flow were the most sensitive inputs.

**Limitations the authors state.**
- The simulated cloud diluted faster than measured and missed accumulation linked to wind variation.
- The guiding principles apply to dense-gas releases with obstacles similar to those studied.

**Reusable lesson (compiler's).** Size the leak cell from the expanded jet, refine the vertical direction for dense gas, and do not expect a steady-wind run to reproduce light, shifting-wind transients.

**Caveats.** Only two usable trials. The guideline chapter limits micro-cell aspect ratio to below two while the field-test chapter states no larger than five and uses 0.04 m by 0.20 m cells. The 13% and 18% errors describe one instant, not the whole record.

### The benefits of using CFD for designing gas detection systems

`giacopinelli-2016-flacs-gas-detection` · Pablo Giacopinelli, Rohan Samaraweera · 2016 · conference · IChemE Symposium Series 161, Hazards 26 (Gexcon UK)

[Open copy read](https://www.icheme.org/media/11810/hazards-26-poster-05-the-benefits-of-using-cfd-for-designing-gas-detection-systems.pdf) · read: methodology, explosion, ventilation and dispersion studies, most of the results and the conclusions

**Objective.** Compare gas detector layouts on two bridge-linked offshore platforms against a large set of simulated leaks, with the danger criterion set from explosion loads on the drilling platform and from gas concentration at target buildings on the production platform.

**Tools.**
- FLACS (version: 10.3): Explosion, ventilation and dispersion simulations

**How the study was built.**
1. Model geometry as completely as possible, since missing detail is a main error source.
2. Run explosions over cloud size, position and ignition points to find the smallest cloud exceeding target design loads.
3. Run ventilation for eight wind directions to find air change rates and flow patterns.
4. Choose leak positions, directions, rates and winds that give clouds both significant and hard to detect, using the flow patterns.
5. Score each detector layout on fraction detected, time to alarm and detection before the dangerous volume or building impairment.

**Modelling choices.**
- Leak rates: 1.5, 6, 24 and 96 kg/s, including sonic jets and low-momentum diffusive leaks.
- Wind cases: Calm, 4.8, 8 and 14.9 m/s.
- Ventilation scaling: Air change rate assumed linear in wind speed.
- Selection basis: Worst-case, challenging scenarios; no frequency or risk weighting.
- Dangerous cloud, drilling platform: 264 m3, from explosion loads against design accidental loads.

**Tool chain.** Explosion runs set the dangerous-cloud criterion; ventilation runs guide leak and detector choice; transient dispersion monitor histories are used to score detector layouts.

**Validation (none-reported).** No comparison with measurements is presented for this study.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The study was not risk based: leak frequencies and wind probability were not used.

**Reusable lesson (compiler's).** Derive the cloud size that detectors must catch from consequences, and report detection-before-impairment, not just detection: a layout can look good on the second measure and fail the first.

**Caveats.** Case study authored by the FLACS vendor. Grid, source-term set-up and validation were not found in the paper. The drilling-platform results text mentions 336 leak scenarios (also the stated number of explosion runs) and the conclusions give 304 drilling and 224 production dispersion runs; the stated total of 560 equals 336 plus 224, not 304 plus 224.

### Estudo sobre a modelagem da dispersao atmosferica de gases densos decorrente de liberacoes acidentais em analise quantitativa de risco

`salazar-2016-dense-gas-models-ammonia-qra` · Marcio Piovezan Salazar · 2016 · masters-thesis · Escola Politecnica, Universidade de Sao Paulo

[Open copy read](http://web.archive.org/web/20240915214047id_/https://cetesb.sp.gov.br/escolasuperior/wp-content/uploads/sites/30/2018/02/MarcioPiovezanSalazar-Disserta%C3%A7%C3%A3o-de-Mestrado.pdf) · read: Portuguese original: abstract, chapters 3 to 5 (method, results, conclusions); literature review not read

**Objective.** Test how the choice of dense gas dispersion model, as embedded in common risk software, changes ammonia hazard distances and individual risk.

**Tools.**
- Phast (UDM) (version: 6.7): Integral dense gas dispersion
- Effects (SLAB) (version: 5.5): Dense gas dispersion with the SLAB model
- ALOHA (DEGADIS-based and Gaussian) (version: 5.4.4): Dense gas and passive plume runs

**How the study was built.**
1. Define two release cases from a pressurised ammonia tank: whole inventory over 10 minutes, and a 10 mm hole in the bottom.
2. Hold source term, weather and topography as uniform as possible across the tools.
3. Compare downwind distances to concentrations representing 1% and 50% fatality.
4. Add a Gaussian plume run to show what ignoring dense gas behaviour does.
5. Combine the distances with assigned scenario frequencies into individual risk against distance for each tool.

**Modelling choices.**
- Weather: Wind 3.0 m/s at 10 m, stability class C, relative humidity 80%, plus stated air and ground temperatures, taken from the state agency (CETESB) guidance.
- Surface roughness: 0.30 m, as flat open terrain.
- Discharge coefficient: 0.62.
- Scenario frequencies: 1.0E-05 per year for the 10 mm hole and 5.0E-07 per year for the 10-minute inventory release (RIVM).
- Dense to passive transition: Only Phast let the user set the transition criterion; its default is a density difference of 0.0015.

**Tool chain.** A common release definition feeds each risk package's dispersion model; the distances to the two lethality levels, with fixed frequencies, give individual risk against distance.

**Validation (code-to-code).** No experimental comparison of its own. Distances from the dense gas models stayed within a factor of 2, which the author relates to published performance; the largest differences were between Phast UDM and Effects SLAB, and individual risk curves differed, mostly farther from the source.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Results hold only for the scenarios and conditions used and cannot be generalised to other conditions or substances.

**Reusable lesson (compiler's).** Even with matched inputs, the dispersion package can change the individual risk curve; name the package and version in the risk result and check decision distances with a second model.

**Caveats.** Masters thesis, two release scenarios, one substance, older tool versions, and no comparison of its own with measurements. The mean distances in Tables 19 and 20 equal the average of the three dense gas results, without the Gaussian plume. One sentence in section 4.3 labels the 22% and 29% deviations as scenario 1 and scenario 2, whereas Table 20 shows both are the scenario 2 Phast deviations at the two concentration levels.

### Relevance of the current modelling methods for the prediction of LNG vapour dispersion and development to be carried on

`quillatre-2017-lng-vapour-flacs-cfx-phast` · Pierre Quillatre · 2017 · conference · IChemE Symposium Series 162, Hazards 27 (ENGIE Lab CRIGEN)

[Open copy read](https://www.icheme.org/media/15425/paper-02.pdf) · read: entire paper

**Objective.** Compare FLACS, ANSYS CFX and Phast with cold LNG vapour vent releases and give practical set-up guidance.

**Tools.**
- FLACS (version: not stated): Cartesian porosity CFD predictions and source and wind sensitivities
- ANSYS CFX (version: not stated): General-purpose CFD predictions and turbulence-constant sensitivities
- Phast (version: not stated): Integral-model comparison
- HYSYS (version: not stated): Release rate, temperature and composition at the vent, including heavy-component condensation

**How the study was built.**
1. Select time windows of the field campaign where release and weather are stable and extract release, wind and gas data.
2. Compute the vent source term with a process simulator and take inflow conditions from measured meteorology.
3. Start from each developer's recommended numerical set-up.
4. Compare plume path with infrared and camera images and concentration decay with sensors, case by case.
5. After the base comparison, vary ground roughness, source meshing, turbulence constants and wind speed.

**Modelling choices.**
- FLACS source representation: Area leak resolved by 12 cells (at least 4), not a point leak; leak cell surface must equal the real source area.
- Source turbulence: 5% intensity and length scale 15% of vent diameter.
- FLACS grid: Developer guidance: at most 1 m cells at domain boundaries and stretch ratios below 1.1.
- CFX mesh: Adaptive on concentration gradients, from 5 mm near the vent to 1 m far away.
- Turbulent Schmidt number (CFX): 0.9, which gave longer distances than 0.7 and closer agreement.
- Ground roughness: No higher than 5 mm recommended.

**Tool chain.** HYSYS defines the vent stream; that source and measured meteorology drive FLACS, CFX and Phast; concentration decay and plume path are compared.

**Validation (experiment).** ENGIE Montoir LNG vapour vent tests. 6-inch horizontal: LFL distance errors of -1% (FLACS) and +20% (CFX), Phast 23% short. 6-inch vertical: FLACS and CFX distances judged pertinent, CFX conservative at about +41%, Phast strongly under-predicting near-field concentration. 18-inch vertical: FLACS and CFX under-predicted LFL distance by around 47% and 31%, Phast by around 18%.

**Sensitivity or uncertainty.** Roughness, FLACS leak meshing, CFX turbulence constants and wind speed. A point leak shortened distances by 27% to 39% against a 12-cell area leak.

**Limitations the authors state.**
- Even the best code can be non-conservative for low-momentum cold heavy releases, especially at low concentrations.
- Predicting 20% LFL distances with confidence in any atmospheric condition was judged very unlikely.

**Reusable lesson (compiler's).** For elevated cold jets, treat the leak mesh, roughness and wind speed as part of the source definition and test them; a dedicated safety CFD code is not automatically conservative.

**Caveats.** Short paper showing only part of the results; mesh sizes for the actual runs and code versions are not given. The 18-inch FLACS error is quoted as about -47% in one place and -48% in another.

### Determining safety parameters for small scale passive hydrogen venting schemes (fuel cell and nuclear enclosures)

`ghatauray-2019-h2-passive-ventilation-cfd` · Tara Singh Ghatauray · 2019 · phd-thesis · London South Bank University

[Open copy read](http://web.archive.org/web/20240629141729id_/https://openresearch.lsbu.ac.uk/download/aeb92dea2a7ce400f2d25e16fe10c313ba6f6fb7202424a9f71e9191c2661ad0/14216530/Tara%20Ghatauray%20Thesis%20Submission%2028.04.19%20Revised%20Sept%2019.pdf) · read: abstract opening, CFD workflow and statistics (3.9-3.10), CFD approach table, ANSYS Fluent comparison (5.9), helium-hydrogen comparison and CFD discussion in chapter 6, appendix E

**Objective.** Find passive vent arrangements that keep a small fuel-cell enclosure below flammable concentrations, using helium experiments and CFD with two commercial codes.

**Tools.**
- SolidWorks Flow Simulation (version: not stated): Main CFD predictions for all vent arrangements
- ANSYS Fluent (version: 19.2 in the section 3.9.6 heading; the reference list cites 18.2): Second code, tested with several RANS, LES and DES settings on one cross-flow case

**How the study was built.**
1. Run helium release tests as a hydrogen analogue for the vent arrangements, then simulate them in CFD.
2. Extend the CFD domain to the outer enclosure of the test rig and refine locally around plume, stratified layer and vents.
3. Test at least three mesh levels for every ventilation configuration and compare concentration-height profiles.
4. For the second code, import the same CAD geometry, extract the fluid volume, use a symmetry half-model and sweep turbulence and wall treatments.
5. Score predictions with fractional bias, normalised mean square error and geometric mean statistics.
6. In CFD, repeat the cross-flow case with hydrogen in place of helium to test the analogue.

**Modelling choices.**
- Turbulence (main code): k-epsilon variant with damping functions in SolidWorks Flow Simulation.
- Fluent RANS mesh: 511363 cells on a symmetry half-model.
- Fluent LES/DES: Refined to a 6.1 million cell equivalent small domain, which gave close agreement for the four further variants shown.
- Outer boundaries (LES/DES): Pressure outlets.

**Tool chain.** Helium experiments provide profiles for both codes; the SolidWorks CAD model is reused in Fluent; helium and hydrogen runs are then compared.

**Validation (experiment).** Helium concentration profiles in the test enclosure. The author found no Fluent RANS configuration closely matched the cross-flow case, while SolidWorks did well on peak and layer depth and refined LES/DES settings correlated very well.

**Sensitivity or uncertainty.** Mesh levels per configuration; in an example, the coarse mesh under-predicted and well-refined meshes over-predicted stratified layer depth. Turbulence models and wall treatments were swept in Fluent.

**Limitations the authors state.**
- Complex or finer meshes often exceeded the available computing capacity.
- The domain matched the rig's outer enclosure; a larger one might have helped but was costly.

**Reusable lesson (compiler's).** For low-momentum buoyant leaks in small enclosures, treat turbulence and near-wall settings as first-order uncertainties: two commercial codes and several k-epsilon variants can disagree widely on stratification.

**Caveats.** Chapter 5 says fine meshes were chosen in all instances, while the chapter 6 mesh example says the coarse mesh under-predicted and the well-refined meshes over-predicted stratified-layer depth, with a medium mesh predicting well on that occasion; agreement at one mesh level does not show grid independence. The Fluent study covers one case and includes LES runs with a symmetry plane, which the author says is not generally recommended for LES. SolidWorks training and software access were funded by the industrial collaborator BOC Ltd.

### On numerical modelling of atmospheric gas dispersion using CFD approach

`tran-2019-openfoam-dense-gas-lng-validation` · Tran Le Vu · 2019 · phd-thesis · Nanyang Technological University, School of Mechanical and Aerospace Engineering

[Open copy read](https://dr.ntu.edu.sg/server/api/core/bitstreams/7800b1c7-2143-4c4d-b7f7-858bc7d28159/content) · read: abstract, start of chapter 4 (flat-terrain boundary layer set-up), chapter 5 and chapter 6

**Objective.** Build an OpenFOAM atmospheric boundary layer and dense gas dispersion model and evaluate it for LNG vapour against wind-tunnel and field data.

**Tools.**
- OpenFOAM (version: 5.0): Custom boundary layer and gas dispersion solvers
- CoolProp (version: not stated): Temperature-dependent properties of air and methane
- FLACS (published results) (version: not stated): Code-to-code comparator through statistics taken from the literature

**How the study was built.**
1. First show that the inlet wind and turbulence profiles stay the same along an empty domain, using mesh, turbulence-model and roughness studies.
2. Run a steady boundary layer solution before the transient gas release and use it as the initial field.
3. Do mesh studies on peak concentration separately for the wind-tunnel and field cases.
4. Derive the LNG spill source from an assumed vaporisation rate with reported spill mass and duration, giving pool diameter and vapour flow.
5. Tune ground heat transfer and turbulent Schmidt number on one field test, then apply the chosen set to the other tests.
6. Score with the LNG protocol's statistical measures and compare with published commercial-code scores.

**Modelling choices.**
- Turbulence closure: RANS, with modified k-epsilon performing better than SST k-omega for unobstructed cases.
- Turbulent Schmidt number: Calibrated: 0.3 for wind-tunnel dense gas and 0.15 for LNG, much below the solver default of 1.
- LNG vaporisation rate: Assumed 0.167 kg per square metre per second for the Burro spill source.
- Ground thermal condition: Fixed temperature, giving most heat input, chosen as it best matched peaks and offsets neglected latent and radiative heat.

**Tool chain.** A steady boundary layer solver gives initial and inlet fields to the transient dispersion solver; a hand source calculation sets the vapour inlet; CoolProp supplies property fits; scores are compared with published FLACS values.

**Validation (experiment).** Hamburg wind-tunnel and Burro field tests. The author reports all protocol statistical measures within acceptance ranges and better scores than published FLACS values. The conclusions call near-source peaks quite conservative, whereas chapter 5 also reports under-prediction at 57 m for Burro8 and describes the Burro9 arc-wise result as under-predicted (accurate at 800 m). Parameters were tuned on DA0120 and Burro9, which are among the scored tests.

**Sensitivity or uncertainty.** Mesh, turbulence model, roughness, ground heat model and turbulent Schmidt number; the Schmidt number had a significant effect, and the coarsest Burro mesh agreed better than finer ones before retuning.

**Limitations the authors state.**
- Validation covers only unobstructed tests.
- Only neutral stratification is validated for the boundary layer model.
- The LNG source is single phase, not a two-phase spill.
- The assumed source term may account for much of the near-source error.

**Reusable lesson (compiler's).** Keep calibration and validation cases separate. Parameters tuned on a test, including one that compensates missing physics, make that test's pass scores weaker evidence.

**Caveats.** Key parameters were selected on DA0120 and Burro9, which are also among the scored tests. Tuned Schmidt numbers differ between the wind-tunnel and LNG cases. FLACS scores are taken from the literature; for the wind-tunnel comparison the author notes that FLACS was validated on larger tests, so the sets may not match. The tables label the scatter measure RMSE although the acceptance range matches the protocol's mean relative square error.

### Overcoming Uncertainties in Sour Natural Gas Dispersion Modelling

`nair-2022-sour-gas-dispersion-uncertainty` · SreeRaj Rajappan Nair · 2022 · phd-thesis · University of Warwick, School of Engineering

[Open copy read](https://wrap.warwick.ac.uk/id/eprint/180942/1/WRAP_Theses_Nair_2022.pdf) · read: sections 3.5 to 4.5 in part, 4.6.3, selected parts of chapter 5 (grid and turbulence sensitivity, validation summary), 6.7 and chapter 7; part of the literature review on equations of state

**Objective.** Develop a way to choose consequence models and key parameters for hydrogen sulphide bearing natural gas pipeline leaks, using composition screening, integral-model sensitivity and an OpenFOAM model.

**Tools.**
- Aspen HYSYS (version: not stated): Phase envelopes and flash calculations of sour gas compositions
- ALOHA (version: 5.4.7): Parameter screening for pure methane and pure hydrogen sulphide
- Canary by Quest (version: not stated): Multicomponent source term and parameter sensitivity
- OpenFOAM (version: v17.12): CFD dispersion model (rhoReactingBuoyantFoam, modified)

**How the study was built.**
1. Screen the real multicomponent composition with a process simulator phase envelope before choosing a dispersion model class.
2. Check whether simplifying to methane or three components hides liquid or aerosol phases at release conditions.
3. Screen release and weather parameters with integral tools.
4. In CFD, first establish the wind profile in a steady run and use it to initialise the transient release run.
5. Validate against the Prairie Grass field trial with grid and turbulence-treatment sensitivity, using factor-of-two criteria.

**Modelling choices.**
- Property package: Peng-Robinson in HYSYS for phase behaviour, preferred by the author over SRK and NRTL, citing vendor and other sources.
- CFD grid: About 2 million cells chosen after four grids; the two finest were treated as equivalent.
- Inflow turbulence: Synthetic eddy inflow cost far more run time without significantly different estimates.
- When composition matters: The author finds toxic distances very sensitive above about 15 mol% hydrogen sulphide, where multicomponent thermodynamics should be used.

**Tool chain.** HYSYS phase behaviour guides the model class and composition sets; ALOHA and Canary screen source and weather parameters; OpenFOAM with a steady-state wind field then simulates selected compositions.

**Validation (experiment).** CFD against one Prairie Grass field trial run: the author reports comparable values on one side of the centreline, overprediction near the centreline and underprediction farther from it, and says performance statistics were satisfactory at the 400 m and 800 m arcs.

**Sensitivity or uncertainty.** Composition, release and weather parameters, four meshes and several turbulence treatments. Water saturation changed distances by about 1%.

**Limitations the authors state.**
- Little data exists for hydrogen sulphide rich releases, so validation used a sulphur dioxide field trial.
- The CFD runs represented natural gas by only methane and hydrogen sulphide.
- Different tools can give substantially different distances for one accident, apparently more so for liquid or two-phase storage.

**Reusable lesson (compiler's).** Check the phase envelope of the real composition before simplifying it, and record the equation of state and expansion method as sensitivity inputs to the dispersion study.

**Caveats.** The literature review says Peng-Robinson or Soave-Redlich-Kwong should not be used when the H2S fraction exceeds a few percent; chapters 4 and 7 report using Peng-Robinson in HYSYS for compositions up to 29% H2S, and no reconciliation was found in the parts read. In the grid check, the text and Figure 68 give FAC5 values (50 to 55%) below the FAC2 values (75 to 79%), although a factor-of-five band contains the factor-of-two band. Validation rests on one trial run with a different gas. Canary version not stated.

### Potential impact of accidental releases of hazardous gases on the immediate habitability of a nuclear power plant

`cassim-2023-aloha-slab-npp-control-room` · M. R. A. Cassim · 2023 · masters-thesis · North-West University

[Open copy read](https://repository.nwu.ac.za/bitstreams/a9bec3af-d029-4d74-921b-14d04b3fead2/download) · read: chapter 4 methodology, chapter 5 results, chapter 6 conclusions and recommendations; contents of chapter 3

**Objective.** Estimate worst-case toxic and flammable consequences for a nuclear plant control room from chlorine, aqueous ammonia and pipeline methane releases.

**Tools.**
- ALOHA (version: not stated): Toxic dispersion with indoor concentration, jet-fire radiation and vapour cloud overpressure.
- SLAB (version: not stated): Cross-check of the chlorine dense-gas result only.

**How the study was built.**
1. Choose one substance for each behaviour class: neutrally buoyant, dense and flammable.
2. Define a worst case for each: the whole content of the largest container or pipe, with a ten-minute release assumed.
3. Apply regulatory worst-case weather (class F, 1.5 m/s).
4. Model the aqueous ammonia as an evaporating pool giving a neutrally buoyant plume, not as a dense two-phase release.
5. Compare outdoor and indoor concentrations at the control room using an assumed air-change rate.
6. For SLAB, derive the extra inputs it needs (liquid fraction, release temperature, source area) outside the code.

**Modelling choices.**
- toxic endpoints in the method chapter: 200 ppm ammonia, 3 ppm chlorine and 50 000 ppm methane regardless of exposure time (the results use AEGL tiers).
- surface roughness: Urban value of 100 cm for a site with many obstacles, following US EPA guidance.
- terrain: Flat; complex terrain ignored.

**Tool chain.** The release opening diameter taken from the ALOHA source model was used to set up the SLAB source.

**Validation (code-to-code).** Chlorine concentrations from SLAB and ALOHA at four distances are tabulated; the author judges them comparable and adequate for screening or emergency planning. Thermal radiation distances from ALOHA are also compared with hand calculations. No experimental comparison.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- SLAB has no source-term model, which the author offers as a possible cause of the differences from ALOHA.
- ALOHA does not predict fragment trajectories from a blast or their effect on people.

**Reusable lesson (compiler's).** Keep one scenario input table and check every tool printout against it. A printout that does not match the stated scenario invalidates the result even if the plots look plausible.

**Caveats.** Master's mini-dissertation. The methane source input table (Table 4-10) gives 26 bar and a 300 mm pipe, while the ALOHA printout shows 257 atmospheres and a 30-inch pipe. The indoor chlorine concentration is given as 27 ppm in one sentence of the results text and 24.7 ppm elsewhere in the text, table and printout. For the 2 kW/m2 zone the results text gives 243 m, while Table 5-4 and the printout give 700 m. The results text calls 5 000 ppm the lower flammability limit, while the printout lists LEL as 50 000 ppm and labels 5 000 ppm as 10% LEL. Tool versions not stated. Consequence only, no frequencies. DEGADIS is reviewed but not run.

### Benchmark Analysis of Accident Modelling Software Applied to Hydrogen Storage

`saturnino-2024-hydrogen-phast-hyram-aloha` · Lorenza Saturnino · 2024 · masters-thesis · Politecnico di Torino

[Open copy read](https://webthesis.biblio.polito.it/32320/1/tesi.pdf) · read: abstract, chapter 5 (method), jet dispersion study, large-scale jet fire modelling set-up, parts of the jet fire results, and chapter 7

**Objective.** Benchmark three consequence tools against published hydrogen jet dispersion and jet fire experiments.

**Tools.**
- Phast (version: 9.0): Hydrogen jet dispersion and jet fire
- HyRAM+ (version: 5.1.1): Hydrogen plume dispersion and jet flame length and radiation
- ALOHA (version: 5.4.7): Large jet fire runs (radiation contours and flame length) and a direct-source flammable-contour run using Phast discharge rates; could not produce results for most small and medium jets

**How the study was built.**
1. Choose experiments as ground truth for completeness of set-up data and ease of extracting results.
2. State an assumption for every missing input, such as tank volume, gas temperature and stability class.
3. Where weather and release height are unknown, vary them in the tool that accepts them and see which dominates.
4. Pass the discharge coefficient computed by one tool into the tool that requires it as input.
5. Transform sensor coordinates into each tool's axis system before comparing radiation.
6. Compare predictions with measured values on scatter plots.

**Modelling choices.**
- Assumed storage for the small-jet tests: A pressurised tank equivalent to 50 L, because the paper did not give the volume.
- Stability class for small jets: Class F (moderately stable) for the night-time tests.
- Stability for large jet fires: Class D, judged from an overcast site photograph.
- Wind below tool limit: ALOHA run at 1 m/s because the measured 0.83 m/s was below its limit.
- Jet fire set-up in Phast: Source term from a vessel run, then a standalone jet fire model for radiation at sensor positions.

**Tool chain.** Phast discharge results give the discharge coefficient for HyRAM, tank settings and flow data for ALOHA trials, and the source term for a standalone Phast jet fire calculation.

**Validation (experiment).** Both Phast and HyRAM generally underestimated centreline hydrogen concentration, Phast less so, with discrepancy growing at higher concentration. Both generally overpredicted flame length. HyRAM radiation was consistently low; for Phast the abstract and conclusions describe its radiation errors differently. For the large jet fires, ALOHA flame lengths (2 and 5 m) were far below the measured 17.4 and 48.5 m, which the author attributes to its jet fire model being designed for upward vertical releases.

**Sensitivity or uncertainty.** Wind speed had more effect than release height on Phast concentrations at the heights and speeds tried. For the flame-length cases, changing atmospheric stability class affected Phast dispersion but not its jet fire results.

**Limitations the authors state.**
- Assumed atmospheric and wind inputs add uncertainty.
- Concentrations were read from published log-scale graphs, which may add error.
- ALOHA could not handle most of the small and medium jet experiments.

**Reusable lesson (compiler's).** Keep a table of assumed inputs next to each benchmark case and do not assume a screening tool covers the case; a non-conservative concentration bias matters when distances to flammable limits are the output.

**Caveats.** Student thesis with many assumed inputs and graph-digitised data; no statistical measures seen in the parts read. The abstract says Phast overpredicted large jet fire radiation, whereas the conclusions say it overpredicted in one test and underpredicted in another.

### Model Evaluation Report on DRIFT Version 3.7.23

`cruse-2026-drift-3-7-23-model-evaluation` · Helen Cruse, Rory Hetherington, Simon Coldrick · 2026 · official-report · UK Health and Safety Executive, Research Report RR1231

[Open copy read](https://www.hse.gov.uk/research/assets/docs/rr1231.pdf) · read: key messages, executive summary, sections 1 to 3, 4.1, 4.2, 4.4 to 4.6, 6.1, 6.6 and 7; per-trial validation plots and appendices not read

**Objective.** Regulator's own evaluation of a new version of the DRIFT dense gas dispersion model against a purpose-built Model Evaluation Protocol before use in its statutory advice.

**Tools.**
- DRIFT (version: 3.7.23): Model under evaluation
- DRIFT (previous version in regulatory use) (version: 3.6.14): Baseline for the exemplar scenario comparison
- LNG Model Validation Database (version: 12): Starting point of the validation database

**How the study was built.**
1. Run a scientific assessment by completing a model questionnaire and testing pass/fail qualitative criteria.
2. Treat verification as evidence gathered from the developer and documentation and record it in the evaluation report.
3. Assemble a validation database so the regulator can validate independently of the developer, starting from the LNG protocol database and adding passive releases, more substances and jet releases.
4. Compare arc-wise maximum concentration and cloud width, matching the model averaging time to the experimental one.
5. Score field and wind-tunnel data separately with statistical performance measures against stated acceptance ranges.
6. Run a set of exemplar scenarios typical of the real regulatory use in both old and new versions, and explain every significant difference from model physics changes.

**Modelling choices.**
- Acceptance measures: Statistical performance measures and acceptance ranges taken from the LNG protocol applied to all trials, including non-dense ones.
- Averaging time for wind-tunnel cases: Set to 1 s because the plume meander model does not apply to controlled tunnel inflow.
- Out-of-scope trials: Some wind-tunnel cases (sloping terrain releases and off-axis sensor sets) were excluded as outside model capability.
- Comparability between versions: Database revision changed inputs and measurements, so scores of older and newer model versions need care.
- Exemplar outputs compared: The quantities used for land-use zones: distances and widths of toxic dose isopleths, and flammable concentration isopleths.

**Tool chain.** Questionnaire and qualitative criteria, then developer verification evidence, then validation runs scored by statistical measures, then exemplar runs through a spreadsheet tool that extracts and compares outputs of two model versions.

**Validation (experiment).** For field trials all five measures for concentration and cloud width were within the acceptance ranges. For wind-tunnel concentrations DRIFT tended to underpredict and FAC2 was 0.49 against a criterion above 0.5; the other measures passed.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The model handles only flat terrain, with buildings and fences represented as cuboids or rectangles.
- The expansion region from liquid storage to a cloud containing solids, as for carbon dioxide, is not modelled.
- One added hydrogen fluoride dataset had been used during development, so that comparison is not fully independent.

**Reusable lesson (compiler's).** Pass statistics are not enough: also rerun the decision-relevant exemplar cases on every model version, because a version that passes validation can still move hazard ranges substantially.

**Caveats.** The evaluating organisation is also the model's regulatory user. Verification relies on developer evidence. A significant difference between versions that is explained by physics changes is not thereby shown to be correct.

## Fire

### Nuclear Power Plant Fire Modeling Analysis Guidelines (NPP FIRE MAG), NUREG-1934 / EPRI 1023259, Final Report

`nrc-epri-2012-nureg1934-fire-modeling-guide` · U.S. Nuclear Regulatory Commission, Electric Power Research Institute · 2012 · guideline · US NRC Office of Nuclear Regulatory Research and EPRI

[Open copy read](http://web.archive.org/web/20250226112138id_/https://www.nrc.gov/docs/ML1231/ML12314A165.pdf) · read: abstract, grid-sensitivity and V&V sections of chapter 2, sections 2.3.7 to 2.5, and parts of chapter 4 on uncertainty and sensitivity; appendices not read

**Objective.** Give a staged process for applying fire models, including FDS, in nuclear plant fire hazard analysis, with validation applicability, grid and uncertainty treatment.

**Tools.**
- FDS (version: version 5 (cited manuals)): CFD fire model among five covered model tools

**How the study was built.**
1. Define goals, characterise scenarios, select models, compute, analyse sensitivity and uncertainty, then document.
2. Compute the characteristic fire diameter and set trial cell sizes by its ratio to cell size, then refine until differences are small relative to expected model accuracy.
3. Check geometry files made by pre-processors against what was intended.
4. Compare scenario non-dimensional parameters with the validation experiments' ranges.
5. If outside range, vary inputs conservatively into range and see whether the conclusion changes; justify anything else separately.
6. Apply tabulated model bias and scatter to estimate the probability that a damage threshold is exceeded.

**Modelling choices.**
- Resolution ratio: Characteristic diameter over cell size of 5 to 10 usually favourable for gross smoke movement.
- Cells across openings: At least three across any flow path and the fire.
- Dominant input: Heat release rate is almost always among the controlling parameters.
- Sensitivity shortcut: Use power-law dependence, for example hot-layer temperature rise with heat release to the two-thirds power.

**Tool chain.** Scenario definition leads to model choice and applicability check, then computation, then bias and scatter adjustment and sensitivity before documentation.

**Validation (literature-values).** The guide summarises bias and scatter derived from the separate NUREG-1824 verification and validation study.

**Sensitivity or uncertainty.** Method guidance: grid series and input sensitivity are prescribed rather than a single study reported.

**Limitations the authors state.**
- The validation experiments were chosen for nuclear plant spaces, so many applications fall outside their range.
- Measurement uncertainty that is overestimated leads to underestimated model error.

**Reusable lesson (compiler's).** Make grid acceptance relative to known model error, and keep an explicit applicability table with a rule for every parameter that falls outside it.

**Caveats.** Written for nuclear power plant applications; the FDS manuals cited are for version 5 and the bias and scatter statistics come from NUREG-1824. The guide expects that study to be updated from time to time and notes that new model releases occur, so check for current validation statistics. Applicability outside nuclear plants is not addressed in the sections read.

### Verification and Validation of Selected Fire Models for Nuclear Power Plant Applications, Supplement 1 (Draft Report for Comment), NUREG-1824 Supplement 1 / EPRI 3002002182

`nrc-epri-2014-nureg-1824-s1-fire-model-vv` · U.S. Nuclear Regulatory Commission, Office of Nuclear Regulatory Research, Electric Power Research Institute · 2014 · guideline · US NRC and EPRI (regulator and industry research report)

[Open copy read](http://web.archive.org/web/20260421102312id_/https://www.nrc.gov/docs/ML1433/ML14338A237.pdf) · read: executive summary, chapter 1, parts of chapters 3 and 4, section 5.1, the summary of validation results and chapter 6; individual experiment comparisons not read

**Objective.** Quantify the predictive capability of five fire models against experiments representative of nuclear plant fires, as bias and scatter that analysts can apply to predictions.

**Tools.**
- Fire Dynamics Tools (FDTs) (version: 1805.1): Empirical correlation library under validation
- CFAST (version: 6.3.1): Zone model under validation
- MAGIC (version: 4.1.3): Zone model under validation
- FDS (version: 6.0.0): CFD model under validation
- FIVE (version: Rev2): Empirical correlation library under validation

**How the study was built.**
1. Define the application's typical fire scenarios and the predicted quantities that matter to them.
2. Select experiments with public, well-documented data and a well-characterised heat release rate.
3. Express each experiment and plant scenario with normalised parameters to check whether an application lies inside the validated range.
4. Estimate experimental uncertainty by combining measurement uncertainty with the effect of input uncertainty propagated through simple models.
5. For each model and output quantity compute a bias factor and a relative standard deviation that accounts for experimental uncertainty.
6. Apply them to a prediction: correct for bias, then compute the probability that the true value exceeds a damage threshold.

**Modelling choices.**
- Evaluation standard: Follows ASTM E1355 for evaluating deterministic fire models.
- Accuracy format: Quantitative uncertainty table replaces the earlier qualitative colour chart.
- Experimental data uncertainty: Where reports gave none, it was estimated from the few that did, plus engineering judgement.
- Version binding: Metrics apply only to the listed model versions, not earlier ones.

**Tool chain.** Experimental data and uncertainty estimates feed each model's comparison; the bias and scatter table is then applied to application predictions, to be combined with input-parameter uncertainty.

**Validation (experiment).** FDS was generally the most accurate, then zone models, then correlations, with exceptions. Zone and CFD models all overpredicted smoke concentration by roughly a factor of three.

**Sensitivity or uncertainty.** Input uncertainties were propagated through simple models to estimate experimental uncertainty; this is not a sensitivity study of an application.

**Limitations the authors state.**
- Verification of the models is not addressed directly; references are given instead.
- Not all plant scenarios are covered and experimental data are limited, so users must judge applicability.
- The analyst remains responsible for justifying the model for each application.

**Reusable lesson (compiler's).** Publish model accuracy as bias and scatter per output quantity, with the validated range in dimensionless terms, so a prediction can be turned into a probability of exceeding a limit.

**Caveats.** This is the draft for public comment (the text carries a November 2014 date); any later version was not read, so numbers may differ. The executive summary says verification is not addressed directly, while the conclusions say the five models have been verified by the study as appropriate for fire-protection applications within their assumptions. Read from a Web Archive copy. Fire in compartments for nuclear plants, not process-plant jet or pool fires.

### Assessing the current live fire training structure environment in eThekwini using CFD

`clarke-2020-fds-live-fire-training` · Thomas Benjamin Bayliss Clarke · 2020 · masters-thesis · Durban University of Technology

[Open copy read](http://web.archive.org/web/20210622113905id_/https://openscholar.dut.ac.za/bitstream/10321/3504/3/T.Clarke%20%2821019827%29%20Thesis%20-%20Rev%2014%20FM%20Sig%20Only_Redacted.pdf) · [DOI](https://doi.org/10.51415/10321/3504) · read: abstract, FDS description and limitations, design-fire inputs, section 2.4 (validation range and grid study), conclusions and recommendations

**Objective.** Use FDS to identify heat, gas-temperature and toxic hazards to trainee firefighters on two floors of an existing training building.

**Tools.**
- Fire Dynamics Simulator (FDS) (version: 6 (the text gives minor release 6.6.0)): Low-Mach CFD fire simulation of both floors
- FDS Validation Guide (version: not stated): Source of the non-dimensional validation ranges and model uncertainty statistics

**How the study was built.**
1. Specify the heat release rate history, fire size and location, fuel chemistry and soot and CO yields as inputs.
2. Build a validation envelope only from test series that resemble the case, then check the model's own experimental and numerical non-dimensional numbers against it.
3. Where a parameter falls outside, restrict the output locations rather than extrapolate.
4. Run a series of cell sizes that all keep the plume resolution index inside the validated range, stepping by 10 mm, and plot the quantities of interest near peak heat release.
5. Turn predictions into probability of exceeding tenability limits using the published model bias and scatter.

**Modelling choices.**
- Cell size: 110 mm on the ground floor and 70 mm on the first floor.
- Fuel: Wood pallets, with chemical formula, CO and soot yields and heat of combustion tabulated.
- Design fire size: Limited so that the training fire does not become ventilation controlled.
- Restarts versus coarser grid: Preferred restarting an interrupted run over coarsening the grid.

**Tool chain.** A design-fire HRR feeds FDS; device outputs feed tenability and garment exposure calculations with model-uncertainty probabilities.

**Validation (none-reported).** No comparison of this study's results with measurements. Applicability is argued by showing the case parameters lie within validation-guide ranges; the one exception, a ground-floor distance ratio, was handled by limiting target distance.

**Sensitivity or uncertainty.** Ten cell sizes per floor. A separate comparison showed that CO volume fraction changed far more than temperature or heat flux with coarsening or with restarts.

**Limitations the authors state.**
- Results are estimates of what would be measured in real training; the author recommends further validated test series for targets farther from the fire.
- Ground-floor target distances had to be restricted to stay within validation.

**Reusable lesson (compiler's).** Check both the physics and the grid non-dimensional numbers against the validation envelope, and test grid effects on every output you will use: species such as CO can move far more than temperature.

**Caveats.** Master's thesis with no fire measurements from this building; being inside a validation-guide parameter range is not a test of this particular model. Section 2.2 calls the tall-stack fire ultra-fast and the short-stack fire medium but gives the same growth coefficient, 0.01172 kW/s2, for both.

### Modellierung des Abbrandverhaltens von Ein- und Mehrkomponentenbrennstoffen unter Verbrennungsbedingungen in Poolfeuern

`saptogino-2020-firefoam-pool-fire` · Primpuna Habib Saptogino · 2020 · phd-thesis · RWTH Aachen University

[Open copy read](http://web.archive.org/web/20240910020709id_/http://publications.rwth-aachen.de/record/782730/files/782730.pdf) · [DOI](https://doi.org/10.18154/rwth-2020-02035) · read: German text: section 6.1 (results and liquid-grid sensitivity), chapter 7 (FireFOAM coupling and results) and chapter 8; earlier theory and experiment chapters not read

**Objective.** Model the transient evaporation rate of single and multi-component pool fires and couple it to FireFOAM so that the CFD flame heat feedback drives the fuel inlet.

**Tools.**
- FireFOAM (OpenFOAM) (version: OpenFOAM 2.3.0): LES of an n-heptane pool fire, supplying heat feedback to the evaporation model
- MATLAB (version: not stated): Liquid-phase evaporation model returning burning rate and surface temperature
- ICEM-CFD (version: 14.5): Mesh generation

**How the study was built.**
1. Define the pool surface as an externally coupled inlet for fuel velocity and temperature.
2. Start the CFD from a small initial burning rate and exchange data every second of simulated time, computing evaporation from the CFD convective and radiative heat flux.
3. Build a block domain scaled on pool diameter D (11 D wide, 20 D high) with a circular fuel inlet.
4. Compare the coupled burning rate with both the uncoupled evaporation model and the measurement to isolate the source of error.

**Modelling choices.**
- Turbulence: LES, as implemented in FireFOAM.
- Combustion: Eddy dissipation model with infinitely fast chemistry and a single global heptane reaction.
- Radiation: Finite-volume discrete ordinates with the gas treated as grey.
- CFD mesh: 260 000 hexahedral cells.
- Time stepping: Adaptive, with maximum Courant number 1.

**Tool chain.** Two-way loop: FireFOAM surface heat flux goes to the MATLAB evaporation model, which returns fuel inlet velocity and surface temperature to FireFOAM.

**Validation (experiment).** The stand-alone evaporation model differed from measured boiling-phase burning rates by 8% (n-heptane) and 2% (ethanol), with larger deviations in start-up and preheating. The coupled FireFOAM run gave a burning rate almost twice both the uncoupled calculation and experiment; its surface heat input was about twice that of the uncoupled calculation, and the author attributes this to over-predicted radiative and convective heat input.

**Sensitivity or uncertainty.** For the stand-alone evaporation model: liquid-phase cell count (20 to 200; 50 chosen), initial temperature, pool geometry, mass-transfer coefficient and Lewis number, Stefan flow and ignition energy. No gas-phase CFD mesh study was seen in the sections read.

**Limitations the authors state.**
- Small errors in flame heat input strongly change the computed burning rate, and the coupled FireFOAM heat input was too high.
- The author suggests more detailed combustion and radiation models could improve agreement.

**Reusable lesson (compiler's).** Do not assume a coupled, predictive burning rate is better than a prescribed one: check the surface heat feedback on its own first, because evaporation amplifies its error.

**Caveats.** Useful as a reported failure. Small laboratory pool only. No gas-phase grid study was found in the parts read, so mesh error cannot be separated from model error.

### A new approach to predicting fire dynamics in enclosed spaces depending on ventilation conditions and geometry (Serbian)

`malkocevic-2025-fds-ventilation-geometry` · Damir E. Malkočević · 2025 · phd-thesis · University of Nis, Faculty of Occupational Safety

[Open copy read](https://fedorani.ni.ac.rs/fedora/get/o:3243/bdef:Content/get) · read: Serbian text with English abstract: limitations (1.3), FDS and mesh-resolution background, chapter 5 ISO 9705 set-up and results, parts of chapter 6; not every scenario or the final conclusions

**Objective.** Use FDS to quantify how opening size, number and position, partitions and changing ventilation alter the heat release history in room and container-sized enclosures.

**Tools.**
- Fire Dynamics Simulator (FDS) (version: 6.9.1): All numerical fire experiments
- PyroSim (version: 2024.1): Pre-processor used to set up the numerical mesh
- RISE Fire Database / CBUF calorimetry (version: not stated): Source of the sofa heat release curve and burnt-mass data

**How the study was built.**
1. Take the design fire from published furniture calorimetry (peak 1366 kW and total energy) before simulating the enclosure.
2. Compute the characteristic fire diameter from the peak heat release and derive the resolution index for a trial cell size.
3. Extend the computational domain beyond the room, 2.4 m above the vent and 0.2 m outside walls and ceiling, so open boundaries do not distort the vent flow.
4. For the ISO 9705 room, vary the opening dimensions across numbered scenarios (SC_8 also has its opening at floor level instead of 1.2 m) and classify each as fuel or ventilation controlled by equivalence ratio.
5. Correlate the ventilation factor with computed heat release across scenarios.

**Modelling choices.**
- Cell size: 0.1 m cubes for the ISO 9705 room.
- Wall materials: Concrete floor and ceiling and solid brick walls, with thermal properties listed in the text.
- Room geometry and openings: ISO 9705 room (2.4 m wide, 3.6 m long, 2.4 m high) with a single vent opening.
- Initial conditions: 20 degrees C and 101 kPa.

**Tool chain.** Calorimeter heat release data become the FDS fire input; FDS heat release histories per ventilation scenario are compared with the same reference curve and then correlated with ventilation factor.

**Validation (experiment).** The fuel-controlled ISO 9705 scenario SC_8 is compared with the CBUF calorimeter record; the author reports a relative difference of 0.003 and says it meets US NRC criteria. For ventilation-limited cases the computed peak heat release fell below the reference. The 6, 9 and 12 m container models are compared in the same way with a handbook polyethylene heat release curve (reported 0.003, 0.007 and 0.005).

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Fire spread between rooms or buildings is outside the scope.
- Smoke generation and combustion-product concentrations are not studied.

**Reusable lesson (compiler's).** When the heat release curve is an input, agreement with that same curve mainly shows that the fire was not oxygen limited. Validate with independent measurements such as temperatures or vent flows.

**Caveats.** The CBUF sofa data (peak 1366 kW) are listed as simulation parameters, and the same record is the comparison for SC_8. Chapter 5 reports a relative difference of 0.003 for SC_8. Equation 1.1 defines that measure from the predicted and measured peak rises, while Table 5.3 gives an SC_8 peak of 1498.14 kW against 1366 kW, which the same chapter states is 9.67% higher. How the 0.003 value was obtained could not be confirmed from the parts read.

## Explosion

### Application of FLACS to develop a standard for explosion venting of empty vessels

`choi-2017-flacs-vented-explosion-vessels` · Ji-eun Choi · 2017 · masters-thesis · University of Stavanger (external supervisor from Gexcon)

[Open copy read](http://web.archive.org/web/20240815191701id_/https://core.ac.uk/download/249953508.pdf) · read: abstract, software description and stated limitations, chapter 4 (validation and grid sensitivity), simulation set-up in chapter 5, conclusion, chapter 6 experiment comparison and appendix Table 10

**Objective.** Use many FLACS vented-explosion runs in empty cubical enclosures to propose a modified, less conservative vent-area recommendation.

**Tools.**
- FLACS (version: not stated (user manual v10.6 is in the references)): All vented and closed-vessel explosion simulations
- CASD and Flowvis (version: not stated): Geometry, scenario and grid pre-processing, and post-processing

**How the study was built.**
1. Check vent openings in the porosity field, because grid matching can change the effective vent area.
2. Compare peak internal and external overpressure with published vented-chamber tests before running the parameter study.
3. Compare a fixed standard cell size with a size scaled to enclosure dimension, using the deflagration index and flame speed in closed boxes.
4. Run the matrix over gas type, volume, vent area and then ignition position, two vents and elongation, with monitors inside and outside.
5. Plot all results against an existing correlation and draw the proposed curve to enclose them.

**Modelling choices.**
- Cell size, validation cases: 0.05 m, following the recommendation of earlier work cited as Klausen (2016).
- Cell size, parameter study: 0.1 m accepted after a 13 to 18 percent difference in comparison metrics.
- Initial state and mixture: Same equivalence ratio for every gas, starting without turbulence.
- Vent panel: Pressure relief panel on one front face of each enclosure.

**Tool chain.** Validation runs and grid check lead to a parameter matrix whose peak pressures are fitted by a modified empirical vent equation.

**Validation (experiment).** Six Harrison and Eyre vented tests: the author calls agreement satisfactory with a 30% margin but notes larger deviations at the quarter-area vent, where tabulated internal-pressure ratios are 0.35 and 0.46. Chapter 6 adds comparisons with Bauwens (propane) and Skjold et al. (hydrogen) tests, described as showing rather similar behaviour; Table 10 gives simulated against measured pressures of 0.09/0.06, 0.086/0.07 and 0.073/0.08 bar for propane and 0.35/0.146, 0.248/0.12 and 0.23/0.19 bar for hydrogen.

**Sensitivity or uncertainty.** Closed-box runs comparing the standard 0.1 m cells with a volume-adjusted size (0.025, 0.04, 0.05 and 0.1 m for 2, 4, 20 and 125 m3, so the two coincide at 125 m3), plus physical variations in ignition position, number of vents and length-to-diameter ratio.

**Limitations the authors state.**
- FLACS does not model acoustic instabilities, which can dominate pressure in some vented empty enclosures.
- The proposal assumes internal turbulence and acoustics do not affect pressure, so other measures must remove them.

**Reusable lesson (compiler's).** A design rule fitted to a solver that omits a pressure-raising mechanism depends on assurance that the mechanism is removed in practice. Show validation points one by one: here two internal-pressure points are under-predicted by more than half.

**Caveats.** Master's thesis. In Table 2 the similarity index is headed experiment over simulation, but the listed values equal simulation over experiment (for test B3, 286 mbar measured, 271 mbar simulated, index 0.95). Read that way, 3 of the 12 indices (0.35, 0.46 and 0.68) are outside the stated 30% margin, all under-predictions. The Harrison and Eyre validation used 0.05 m cells and the parameter study 0.1 m; the grid check compares two sizes in closed boxes. The author states that any guideline based on the proposal must require measures that remove internal turbulence and acoustic effects.

### Blind-prediction: estimating the consequences of vented hydrogen deflagrations for homogeneous mixtures in 20-foot ISO containers

`skjold-2017-hysea-blind-prediction-vented-h2` · T. Skjold, H. Hisken, S. Lakshmipathy, G. Atanga et al. · 2017 · conference · 7th International Conference on Hydrogen Safety (ICHS2017), Hamburg

[Open copy read](https://zenodo.org/records/1165364/files/Skjold_2017_ICHS-225_pp639-652.pdf) · read: whole paper (figures read only through the text, apart from the discussion page, which was viewed as an image to check a number)

**Objective.** Compare blind predictions from CFD tools and a phenomenological model, submitted before the experiments were complete, with vented hydrogen deflagration tests in shipping containers; engineering-correlation results, not part of the original blind study, are also compared.

**Tools.**
- FLACS (version: 10.2, 10.4 and 10.5 across submissions): CFD predictions by several modellers
- ANSYS CFX (version: 17.0): CFD predictions
- IMPETUS Afea Solver (version: not stated): Structural response of container walls, loaded from FLACS results
- Engineering correlations (NFPA 68, EN 14994, FM Global, Molkov forms) (version: as referenced in the paper's Table 3): Simple venting predictions

**How the study was built.**
1. Define simple, fully specified explosion scenarios and collect predictions with a deadline before the experiments are completed.
2. Repeat each experimental scenario so that experimental scatter can be shown next to model scatter.
3. Record each submission's code version, grid and special settings.
4. For structural response, pass CFD pressure-time loads one way to a structural solver or to a simple static estimate.
5. Compare pressure histories and sensor scatter with bands of plus or minus 30% and a factor of two, and compare maxima against the experimental spread.

**Modelling choices.**
- Mixture and ignition: Quiescent homogeneous 15 vol.% hydrogen in air, back-wall ignition, doors open, with and without a bottle basket obstacle.
- Grid resolution: Chosen by each modeller; one automatically generated grid did not follow the tool's guidance for confined explosions and should have been twice as fine.
- Obstacle representation in engineering models: Treating the bottle basket as one obstacle followed the experimental trend better than other treatments.

**Tool chain.** CFD pressure loads from one submission feed a structural finite element solver, and from another a static deflection formula; all predictions are collected centrally and compared with measurements.

**Validation (experiment).** The authors say most predictions from the CFD tools and phenomenological model agreed reasonably with experiment and all captured the obstacle's pressure increase, but highest and lowest predictions differed by a ratio of about 23 in both scenarios. Engineering models, which were not part of the blind study, had ratios below 10 and did better overall for these simple scenarios.

**Sensitivity or uncertainty.** Several modellers submitted multiple grids; the same CFD tool showed large scatter across users and grid resolutions.

**Limitations the authors state.**
- Pressure measurements had noise and drift and several were discarded.
- Using one container for all six tests affects repeatability, especially of structural measurements.
- The better showing of engineering models may not carry over to more complex cases.
- It could not be determined whether other CFD codes show the same user spread, since each had one modeller group.

**Reusable lesson (compiler's).** Do not treat one CFD run as the answer for vented explosion pressure: follow the tool's grid rules, show results for more than one resolution or analyst, and compare with a simple correlation.

**Caveats.** Lean, low-pressure tests (relatively weak explosions) with weak signals. Coordinated by the vendor of one of the tools. One withdrawn and one resubmitted non-blind prediction. Covers only the first of two blind studies.

### Assessment of enclosure ventilation safety for hydrogen fuelled gas turbines

`miles-2021-h2-gas-turbine-enclosure` · Daniel Miles, Tristan Vye, Aidan Wimshurst · 2021 · conference · IChemE Symposium Series 168, Hazards 31 (Frazer-Nash Consultancy)

[Open copy read](https://www.icheme.org/media/27745/hazards-31-paper-56-vye.pdf) · read: entire paper

**Objective.** Adapt the dilution-ventilation criterion for gas turbine enclosures to hydrogen by setting a new limiting cloud size with explosion modelling and then checking detectability with ventilation CFD.

**Tools.**
- FLACS CFD (version: not stated): Explosion overpressure of gas clouds in the enclosure
- ANSYS Fluent (version: not stated): Leak dispersion in the ventilated turbine enclosure

**How the study was built.**
1. Reproduce the published methane enclosure explosion tests in the explosion code first.
2. Swap to hydrogen and blends with the same geometry, congestion and cloud sizes, then find the cloud size that keeps the original overpressure limit.
3. Run ventilation alone to locate low-velocity zones and choose worst-case leak positions and directions.
4. Represent the leak as mass, momentum and energy sources in a small volume, with momentum from choked flow.
5. Repeat identical leak cases for hydrogen, changing gas properties, flammable limit and allowable cloud volume, and compare concentrations at the outlet detector plane.

**Modelling choices.**
- Fluent formulation: Steady two-species solution with full buoyancy and ideal-gas mixture density.
- Turbulence and basis: k-epsilon, stated to follow the HSE joint-industry CFD best-practice guidance.
- Overpressure criterion: The methane limit of 0.1% of enclosure volume was rejected for hydrogen.
- Leak cases: Six worst-case positions and directions.

**Tool chain.** FLACS sets the permissible hydrogen cloud volume (about five times smaller than for methane in the case studied); Fluent then examines whether leaks at that size can be detected at the ventilation outlet.

**Validation (experiment).** FLACS methane runs against HSE joint-industry enclosure explosion pressures, reported as close with slight over-prediction. No dispersion validation is presented for the Fluent model.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The limiting cloud size may not transfer to other enclosures because volume and congestion effects were not studied.

**Reusable lesson (compiler's).** Changing fuel changes the acceptance cloud size as well as the dispersion, so derive the criterion first and then re-run the ventilation study.

**Caveats.** The paper gives no mesh details, grid study or code versions, and shows pressure results only in normalised form. Hydrogen explosion predictions are not validated against hydrogen data in this paper.

## Relief, flare, depressuring and blowdown

### Blowdown of Onshore and Offshore Installations

`richardson-saville-1995-blowdown-validation` · S M Richardson, G Saville · 1995 · conference · IChemE Symposium Series No 139 (Imperial College London)

[Open copy read](https://www.icheme.org/media/25367/major-hazards-onshore-and-offshore-ii-icheme-symposium-series-139-1995-43-richardson.pdf) · read: whole paper text; the comparison plots were not examined

**Objective.** Present the BLOWDOWN program and its validation against small-scale tests and full-installation blowdown measurements, with design lessons on minimum temperatures.

**Tools.**
- BLOWDOWN (version: not stated): simulates fluid and wall temperatures, efflux rate, composition and phase during depressurisation

**How the study was built.**
1. Split each vessel into gas, liquid hydrocarbon and free-water zones, and divide pipelines into axial elements of adaptive size.
2. March in discrete pressure steps rather than time steps.
3. Apply zone-specific wall heat transfer (convection, boiling) with transient conduction through the wall and insulation to the surroundings.
4. Include connected piping and liquid drainage to low points; in the gas plant case, allowing liquid collection lowered the predicted minimum wall temperature by over 30 K.

**Modelling choices.**
- thermodynamics: Rigorous properties from an extended corresponding-states method, because errors here distort the whole phase path.
- topside flow assumptions: Quasi-steady, homogeneous two-phase flow in topsides pipework (relaxed for pipelines).
- no tuning: The authors state there are no adjustable parameters.

**Validation (experiment).** Small-scale vessel and pipeline tests: bulk fluid and wall temperature discrepancy stated as 3 K. Full-installation comparisons (offshore platform, onshore gas plant) are described as generally adequate with somewhat wider stated bands, and with poor agreement at a few locations (see limitations).

**Sensitivity or uncertainty.** Case study on one platform: blowing down a single train rather than all of them lowers minimum wall temperature by about 20 K through lower back-pressure.

**Limitations the authors state.**
- Outside wall temperatures on two flare laterals downstream of one blowdown valve agreed badly; the authors attribute this to possible very cold supersonic flow after a choked expansion.
- Local steep temperature gradients near tees, bends and expansions are not captured.
- Slow sensor response limits comparison on short time scales.

**Reusable lesson (compiler's).** Do not assume full-plant simultaneous blowdown is the coldest case for flare piping: run partial blowdowns, include liquid low points and connected upstream/downstream units, and check sensor placement before judging model error.

**Caveats.** Authored by the code developers; comparisons are mostly graphical and qualitative apart from the quoted bands; older work and a proprietary code; text is a scan-to-text conversion.

### Unpicking Oversimplification: Relief and Flare Studies for Complex Plant using Dynamic Process Modelling

`firth-2016-refinery-dynamic-relief-flare` · Ben Firth · 2016 · conference · IChemE Hazards 26, Symposium Series No 161 (Flexible Process Consultants Ltd)

[Open copy read](https://www.icheme.org/media/11782/hazards-26-paper-45-unpicking-oversimplification-relief-and-flare-studies-for-complex-plant-using-dynamic-process-modelling.pdf) · read: whole paper (figures as text only)

**Objective.** Describe an auditable procedure for a plant-wide dynamic relief and flare study of a legacy refinery covering two flare systems, to check relief devices and header capacity.

**Tools.**
- dynamic process simulator (product used not identified) (version: not stated): linked unit models run through relief, utility-failure and operator-error scenarios; the paper names Dynsim, HYSYS, UniSim and gPROMS only as available tools

**How the study was built.**
1. Collect deeper equipment data than a conventional relief study (tray and exchanger geometry, valve trim, actuator speeds), mark it up and have a second engineer check the inputs.
2. Treat historian data as distributions rather than one snapshot, to find realistic worst-case operating states.
3. Build the steady-state model first, then the dynamic model, then several initial conditions, and review them with plant engineers.
4. Rate the model against plant data and resolve each discrepancy with site process engineers; use site controller schemes and tunings.
5. Build each scenario from initiating event, initial condition and optional latent failure, and run it through scripted events so it is repeatable.
6. Do sensitivity runs on initial conditions, controller modes and latent failures to find the worst credible case, and report each event as a narrative plus peaks and trends.

**Modelling choices.**
- latent failures: One per scenario for unit cases where possible, to add conservatism without double jeopardy; one per major operating unit for site-wide events.
- operator and controller credit: Unit cases put controllers in manual and take no operator action, run for at least 30 simulated minutes unless steady; site-wide cases let realistic controllers act.
- model coupling: Unit models linked through shared utilities and headers (fuel gas, flare, heat integration) so knock-on relief loads appear.

**Tool chain.** Plant data and P&ID-derived PFD feed a steady-state model, then a rated dynamic model, then scripted scenarios; slug-flow results were passed to a mechanical model and results supported HAZOP, LOPA and SIL work.

**Validation (plant-data).** The method requires rating the models so that temperatures, pressures, compositions and valve positions sit within the normal historical range, and says the study's units were rated and matched to plant data. No numerical agreement is reported and no relief transient is compared with measurement in a quantified way.

**Sensitivity or uncertainty.** Described as part of the method; one high-pressure to low-pressure separator example shows that initial liquid levels change the relief case from vapour to two-phase.

**Limitations the authors state.**
- The author notes the standard gives little guidance on dynamic modelling studies, so the team had to define its own practice.
- A single plant snapshot can be unrepresentative (unusual settings, fouling, bad instruments, ambient or transient conditions).

**Reusable lesson (compiler's).** For brownfield flare studies, rate the model on historian distributions and script every scenario with a stated latent-failure and controller-credit rule, so reviewers can challenge the assumptions behind the load.

**Caveats.** Consultancy conference paper reporting its own project; software product, thermodynamics and flare hydraulics not described; claimed savings are not independently checked.

### Modeling of depressurization-induced superheating for compressed liquefied gases

`zheng-2017-depressurisation-superheating` · Wentian Zheng, Haroun Mahgerefteh, Didier Jamois, Jerome Hebrard et al. · 2017 · journal · Industrial & Engineering Chemistry Research (accepted manuscript, UCL Discovery)

[Open copy read](https://discovery.ucl.ac.uk/id/eprint/10056715/1/Mahgerefteh_Modeling%20of%20Depressurization-Induced%20Superheating%20for%20Compressed%20Liquefied%20Gases_AAM.pdf) · read: introduction, model theory, numerical method, validation, parameter studies, conclusions

**Objective.** Develop a two-zone blowdown model that allows the liquid to stay superheated during rapid depressurisation of CO2 and CO2 mixtures.

**Tools.**
- REFPROP (GERG-2004 EoS) (version: not stated): thermodynamic and transport properties
- BLOWSIM (version: not stated): comparison blowdown code without liquid superheat

**How the study was built.**
1. Write separate mole and entropy-based energy balances for vapour and liquid zones, with condensate dropping instantly into the liquid.
2. Delay liquid flashing with a linear relaxation law toward equilibrium vapour fraction, governed by a relaxation time.
3. Select the choked discharge sub-model by the phase at the orifice (vapour, two-phase mass-flux maximisation, or Bernoulli for liquid).
4. Integrate the ODE system without interphase source terms, then add them explicitly within the same step.
5. Check time-step convergence and compare pressure and both zone temperatures against two independent experiment sets.

**Modelling choices.**
- equation of state: GERG-2004 rather than cubic equations, for better accuracy near the critical and supercritical region.
- relaxation time: Constant, picked in all cases to give the best agreement with the measurements.
- heat transfer: Churchill-Chu natural convection to vapour and Rohsenow boiling to liquid; through-wall gradient neglected for steel.
- time step and relaxation time: 0.001 s time step; relaxation time 0.5 s for the vessel release tests and 0.01 s for the short-pipe tests.

**Tool chain.** REFPROP properties feed the two-zone ODE model; results are compared with measurements and with BLOWSIM.

**Validation (experiment).** Two experiment sets (vessel releases and short-pipe releases). Authors report good agreement for pressure and both zone temperatures; the relaxation time was fitted to these data and the comparison code under-predicted depressurisation rate.

**Sensitivity or uncertainty.** Relaxation time varied from 0.005 to 0.5 s; orifice diameter and nitrogen impurity varied. Longer relaxation gave more liquid superheat; vapour temperature was not noticeably affected.

**Limitations the authors state.**
- No bulk fluid motion is assumed, so pipeline use is limited to isolated lines.
- A constant relaxation time is used because data and correlations are lacking; dedicated CO2 correlations are left for future work.
- Fire exposure is possible in principle but run time would be prohibitive.

**Reusable lesson (compiler's).** If a non-equilibrium blowdown model has a relaxation time chosen to fit the test, treat the agreement as calibration and hold out tests before predicting new geometries or compositions.

**Caveats.** Accepted manuscript; fitted parameter differs by a factor of 50 between the two test sets; agreement described qualitatively.

### Numerical Modelling of the Rapid Depressurisation and Outflow of High Pressure Containments in the Framework of Carbon Capture and Sequestration

`zheng-2018-co2-pipeline-decompression-thesis` · Wentian Zheng · 2018 · phd-thesis · University College London

[Open copy read](https://discovery.ucl.ac.uk/id/eprint/10049915/1/Wentian%20Zheng%20PhD%20thesis_revised.pdf) · read: contents, chapter 3 (solid CO2 formation: theory, numerics, validation, conclusions), chapter 7 conclusions and start of future work

**Objective.** Extend transient flow models for rupture and puncture decompression of CO2 pipelines, including solid CO2 formation, non-equilibrium and stratified two-phase flow.

**Tools.**
- in-house homogeneous equilibrium pipe-flow model (finite volume, HLLC solver) (version: not stated): decompression and solid fraction prediction
- GERG 2008 and extended Peng-Robinson EoS (version: not stated): properties above and below the CO2 triple point

**How the study was built.**
1. Solve conservation of mass, momentum and energy along the pipe, including wall heat transfer and friction.
2. Set zero velocity at the closed end and obtain the choked rupture-plane condition from local wave relations with isentropic flow.
3. Replace the equilibrium sound speed, which goes to zero at the triple point, with a homogeneous frozen mixture value.
4. Verify the solver on a Riemann problem and an independent isentrope analysis before using experimental data.
5. Check grid convergence, then simulate a full-bore rupture test and compare intact-end pressure and temperature histories.

**Modelling choices.**
- mesh and Courant number: 500 cells and CFL 0.5 for the validation run.
- friction and heat transfer: Chen friction-factor correlation; Rohsenow correlation on the assumption that boiling dominates.
- flow model choice in other chapters: Relaxation model for non-equilibrium and a two-fluid model for punctures, each compared with the equilibrium model.

**Tool chain.** Equation-of-state flash results feed the finite-volume flow solver; thesis chapter 6 provides jet expansion conditions intended as dispersion model input.

**Validation (experiment).** Full-bore rupture pipeline test: temperature agreement good down to the triple point, then degrading, with the model under-predicting CO2 temperature. Pressure agreement is described as excellent; puncture tests in a later chapter are reported as good.

**Sensitivity or uncertainty.** Grid convergence checks and a comparison of two sound-speed formulations.

**Limitations the authors state.**
- The equilibrium assumption breaks down once solids can separate and settle, so predicted solid distribution along the pipe may be wrong.
- With a pure-CO2 relaxation-time correlation the non-equilibrium model performed less well.

**Reusable lesson (compiler's).** In CO2 blowdown, check how the sound speed and equation of state behave at the triple point, and do not read solid accumulation locations from a homogeneous model.

**Caveats.** Pipeline outflow for consequence assessment rather than process-vessel blowdown; only chapters 3 and 7 were read in detail; chapter 3 validation uses a single test.

### Physical model of non-adiabatic blowdown of cryo-compressed hydrogen storage tanks

`cirrone-2023-cryo-h2-tank-blowdown` · Donatella Cirrone, Dmitriy Makarov, Sergii Kashkarov, Andreas Friedrich et al. · 2023 · journal · International Journal of Hydrogen Energy 48(90) (Ulster University repository copy)

[Open copy read](https://pure.ulster.ac.uk/ws/files/128446467/1-s2.0-S0360319923025235-main.pdf) · [DOI](https://doi.org/10.1016/j.ijhydene.2023.05.182) · read: introduction, experiments, model, calculation assumptions, convergence checks, validation, thermocouple inertia, CFD use, conclusions (figures as text only)

**Objective.** Build and validate a blowdown model for cryo-compressed hydrogen tanks including heat transfer through tank and discharge pipe walls, and use it as a CFD source term.

**Tools.**
- MATLAB (version: not stated): implements the blowdown algorithm
- CoolProp (version: not stated): real-gas hydrogen properties
- ANSYS Fluent (version: 2020R2): jet dispersion using a volumetric source driven by the blowdown results

**How the study was built.**
1. Choose validation tests that span the extremes of initial pressure for each nozzle size and both initial temperatures.
2. Add heat transfer in the short discharge pipe before an isentropic real nozzle and a notional-nozzle expansion.
3. Test whether a constant pipe-wall temperature can replace transient wall conduction, weighing accuracy against run time.
4. Check convergence in time step, wall nodes and solver tolerances.
5. Fit a discharge coefficient test by test and report the range.
6. Pass transient notional-nozzle mass, momentum, energy and turbulence terms to CFD as constant-size volumetric sources.

**Modelling choices.**
- equation of state: Helmholtz-energy formulation; the authors state the Abel-Noble equation is not applicable to high-pressure cryogenic storage.
- wall discretisation: 20 wall nodes as an accuracy and run-time compromise.
- discharge coefficient: Fitted per test, optimum values 0.6 to 0.8.

**Tool chain.** CoolProp properties feed the MATLAB blowdown model; its transient notional-nozzle results are fitted against time and applied as volumetric sources in Fluent.

**Validation (experiment).** PRESLHY tank blowdown tests: tank pressure and temperature reproduced well. The authors also state differences were within experimental accuracy, somewhat larger for the bigger release nozzles, which they link to thermocouple inertia. The discharge coefficient was fitted per test. In the CFD jet comparison, sensors near the nozzle were predicted somewhat colder than measured (possibly sensor inertia), with good agreement further downstream.

**Sensitivity or uncertainty.** Time step, solver tolerance, wall nodes, wall thickness, external heat-transfer coefficient, pipe-wall treatment, discharge coefficient and three model variants (adiabatic versus heat transfer, two equations of state). The CFD source-volume size comparison shown is attributed to earlier work.

**Limitations the authors state.**
- For other geometries and scenarios, transient pipe-wall conduction should be solved for accurate estimates.
- Closed thermocouples may lag in the fastest blowdowns; open ones respond faster but may be less accurate when cold.
- The authors say further research is envisaged to assess validity and applicability for larger hydrogen storages and longer discharge lines once detailed experiments are available.

**Reusable lesson (compiler's).** Compare against an adiabatic baseline to show what wall heat transfer changes, and examine thermocouple response before attributing fast-transient temperature error to the model.

**Caveats.** Small 2.81 L tank; per-test fitted discharge coefficient; pipe-wall initial temperature taken from the experiment; agreement is mostly graphical, with no numerical error metric seen in the parts read.

### HydDown Documentation, Release 0.50.0 (theory and validation chapters)

`andreasen-2026-hyddown-validation-manual` · Anders Andreasen · 2026 · other-report · HydDown open-source project documentation

[Open copy read](https://andr1976.github.io/HydDown/_downloads/HydDown.pdf) · read: introduction/background, parts of theory located by search, chapter 4 validation (most of it)

**Objective.** Document an open-source Python vessel filling, depressurisation and fire-load model and compare it with experiments and commercial simulators.

**Tools.**
- HydDown (version: 0.50.0): lumped vessel filling, discharge and fire calculations
- CoolProp (version: not stated): thermodynamic back end
- Honeywell UniSim Design (dynamics mode) (version: not stated): code-to-code reference for wall conduction and fire heat load

**How the study was built.**
1. Use the lumped wall heat balance for steel cylinders and check against 1-D transient conduction that the result does not change.
2. For lined composite cylinders with very different layer properties, switch to bi-material 1-D transient conduction rather than lumping the properties.
3. For the nitrogen vessel test, set the orifice discharge coefficient to match the measured pressure before comparing temperatures.
4. For two-phase fire cases, use the non-equilibrium option with pool-fire heat load and relief-valve cycling.

**Modelling choices.**
- simplifications: Mainly pure substances; the documentation also lists no gas-phase temperature stratification and, by default, no through-wall gradient.
- discharge coefficient: Set or adjusted to match the measured pressure in the nitrogen (0.8) and multi-component scrubber (0.97) tests; the KIT helium case reuses 0.9 from an earlier study.

**Tool chain.** CoolProp properties feed the HydDown energy balance, flow-device and heat-transfer routines.

**Validation (experiment).** KIT helium composite-tank test: minimum gas temperature 182.3 K simulated against 177.5 K measured (4.8 K difference), with the simulated minimum earlier (about 75 s against 100 s); final gas temperature 237 K simulated against 216 K measured. The author reports that adding an earlier study's thermocouple thermal model improved the predicted time of the measured minimum and the final measured temperature. The document also gives other experimental cases (with weaker final-temperature or timing agreement in places), fire tests and code-to-code comparisons with UniSim.

**Sensitivity or uncertainty.** Wall-model choice checked for steel cases; liner material swapped (polymer to aluminium) to show its effect on gas temperature. No systematic parameter study seen in the parts read.

**Limitations the authors state.**
- A very slow hydrogen depressurisation fitted gas temperature less well than fast ones, which the author suggests points to missing detail in heat transfer.
- Composite wall properties are uncertain and strongly influence results.
- No good Type III discharge dataset with wall layer details was found, so that case is only illustrative.

**Reusable lesson (compiler's).** State for each validation case which inputs were fitted (such as discharge coefficient), because pressure agreement is then not evidence; judge the model on minimum and final temperatures and their timing.

**Caveats.** Developer-written software documentation, not peer reviewed as read; several tank geometries and properties were assumed from similar vessels. The fire heat load table gives an incident heat flux of 100 kW/m2 while the captions of Figures 4.17 and 4.18, as extracted, give 100 W/m2.

## Runaway reaction and thermal hazard

### Operational Safety of the Polymerization Reactors

`ferreira-da-silva-2018-pan-reactor-safety` · Sara Patrícia Ferreira Da Silva · 2018 · masters-thesis · Instituto Superior Tecnico, Lisbon (internship at SGL Composites)

[Open copy read](https://fenix.tecnico.ulisboa.pt/downloadFile/1689244997259085/Dissertacao.pdf) · read: abstract, objectives, chapter 6 (kinetics and adiabatic test), chapter 7 (Aspen runs and pilot tests), conclusions

**Objective.** Judge whether runaway or explosion is possible in acrylonitrile copolymerisation reactors under feed, cooling, agitation, pH and inventory deviations, using simulation and pilot tests.

**Tools.**
- Aspen Plus (Polymers template) (version: not stated): steady-state sensitivity of reactor temperature to feed-flow deviations

**How the study was built.**
1. Take copolymerisation kinetic parameters from handbook and article values and compare the two sources.
2. Define components, flowsheet, kinetics and industrial inlet conditions, and establish the stationary state.
3. Vary one feed flow at a time with the sensitivity module and record overflow temperature.
4. Cover the deviations the simulation did not (cooling, agitation, inerting, pH, unreacted monomer) by pilot-reactor experiments.

**Modelling choices.**
- scale: A 12 m3 reactor in simulation; pilot experiments in a 5.7 L reactor with conditions adjusted to suit.
- adiabatic approximation: Adiabatic behaviour was approximated by draining the pilot reactor jacket, which the author says is not fully insulated.

**Tool chain.** Kinetic data feed the Aspen Plus model; pilot tests are run separately and are not used to calibrate or check the model in the parts read.

**Validation (none-reported).** No comparison of Aspen predictions with plant or pilot measurements was found in the sections read.

**Sensitivity or uncertainty.** One-at-a-time feed-flow variations in the steady-state model.

**Limitations the authors state.**
- Controller lag and operator response are not represented, so real behaviour may differ from the simulation.

**Reusable lesson (compiler's).** Steady-state feed-flow sensitivities show operating-point temperature changes only. A runaway assessment also needs transient heat generation against removal, calorimetry and credible loss-of-cooling and agitation cases.

**Caveats.** Masters thesis; software version not stated. The conclusions say there is no need for concern about explosion or runaway, at least considering the operating procedures, operator training and experience and existing control instrumentation. The same chapter says the cooling-loss, agitation-loss, adiabatic and unreacted-monomer scenarios affect reactor safety and are hard to control, with the mass solidifying within minutes and temperature rising, and that accidents are avoided because the reactor is stopped and cleaned out.

### Dynamic Simulation and Verification Test for Vent Sizing of Runaway Reaction

`mizuta-2022-runaway-vent-sizing-dynamic` · Yuto Mizuta, Motohiko Sumino, Hiroaki Nakata, Yuichiro Izato et al. · 2022 · journal · Chemical Engineering Transactions 90 (Mitsubishi Chemical; Yokohama National University)

[Open copy read](https://www.aidic.it/cet/22/90/074.pdf) · [DOI](https://doi.org/10.3303/CET2290074) · read: whole paper (figures as text only)

**Objective.** Size a safety valve for a runaway in an MEKPO production reactor with a dynamic model that includes inventory loss and a vent gas line, compare it with the ISO 4126-10 method, and test it at 40 mL scale.

**Tools.**
- Aspen Plus, Aspen Dynamics and Aspen Custom Modeler (version: not stated): dynamic reactor model with a custom two-phase safety-valve routine
- ARSST (reactive system screening calorimeter) (version: not stated): source of reaction kinetics and related parameters

**How the study was built.**
1. Pick the sizing scenario after hazard identification; here loss of reactor cooling.
2. Define reaction stoichiometry, rate and heats of formation from calorimetry, then check the model against that same calorimeter run.
3. Code the missing two-phase safety-valve flow model (ISO omega method) in Custom Modeler and couple it as a subroutine.
4. Repeat runs over vent sizes to find the size that prevents the pressure rise, for a closed reactor and one with an exhaust line.
5. Test at small scale with valve diameters chosen by keeping the ratio of vent area to liquid volume constant.

**Modelling choices.**
- vent flow and gas generation: Unlike the ISO method, gas and vapour rate is computed from kinetics and phase equilibrium and valve diameter is an input.
- relief scenario geometry: Safety valve on the reactor top with an assumed set pressure of 400 kPag; results also compared with and without an exhaust gas line.

**Tool chain.** ARSST data give the reaction model; Aspen property data and Aspen Dynamics solve the reactor; the Custom Modeler valve routine returns vent flow; predicted vent sizes are scaled to the 40 mL test.

**Validation (experiment).** Small-scale tests agreed well with the model without an exhaust line; with an exhaust line the measurements differed from the calculation.

**Sensitivity or uncertainty.** Vent size and presence of an exhaust line; the ISO method gave a larger required size than both dynamic models, exceeding the 1.5 m reactor diameter.

**Limitations the authors state.**
- The small-test scaling law needs more study.
- The smaller computed vent sizes include no safety allowance.
- With the exhaust line, experiment and simulation did not correspond because pressure rose faster than a safety valve can handle.
- In one exhaust-line case predicted to be adequately relieved, pressure rose to about 1,000 kPag.

**Reusable lesson (compiler's).** When dynamic simulation reduces a required vent size, check valve opening time and pressure-rise rate and test the unfavourable configuration; removing volatile solvent early can make the later runaway worse.

**Caveats.** Short paper; kinetics, property method and numerical results of the comparison plots are not tabulated. The text itself reports pressure-rise rate far above the cited ISO limit for valve relief, so the reduced vent size is not demonstrated for that case. Not a design basis.

## Inherently safer design

### Diseño de seguridad inherente

`lozano-2020-inherent-safety-index` · Álvaro Lozano Blázquez · 2020 · bachelor-thesis · Universidad Politécnica de Madrid

[Open copy read](http://web.archive.org/web/20231015011215id_/https://oa.upm.es/62862/1/TFG_ALVARO_LOZANO_BLAZQUEZ.pdf) · read: Parts of chapter 4 (index sub-scores), chapter 5 acetone and cumene cases and comparison, chapter 6 conclusions

**Objective.** Score alternative or example process routes with the Heikkila Inherent Safety Index, including a conventional versus reactive-distillation cumene comparison.

**Tools.**
- Aspen Plus (version: V10): Estimated reaction heats where the literature flowsheet did not report them.

**How the study was built.**
1. Take flows, temperatures, pressures and conversions from published flowsheets, and use the simulator to fill in missing reaction heats from operating conditions and conversions.
2. Normalise reaction heat by the mass entering the reactor over a nominal one hour, then map it to the sub-index band.
3. Estimate inventory from the inlet flows of the main units inside battery limits over one hour, excluding off-battery streams.
4. Set flammability, explosivity and toxicity sub-scores from the worst compound using public chemical database properties.
5. Sum the sub-indices and compare routes line by line to see which sub-scores drive the difference.

**Modelling choices.**
- Index method: Heikkila Inherent Safety Index; the cumene reactive-distillation route scored lower (safer) than the conventional route by 4 points.
- Reactive section as reactor: For reactive distillation the reactive section of the column is scored as the reactor for equipment safety.

**Tool chain.** Literature flowsheet data feed Aspen Plus reaction-heat estimates, which feed manual index scoring.

**Validation (none-reported).** None reported in the parts read.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The sub-indices and the way of determining them are not absolute and may miss parameters of a particular process.
- The author sees equipment and process-structure sub-indices as the most problematic because they rest on accident statistics.

**Reusable lesson (compiler's).** State the inventory basis explicitly. An hour of inlet flow is not equipment hold-up, and in intensified designs such as reactive distillation that choice can decide whether the minimisation benefit appears at all.

**Caveats.** Bachelor thesis in Spanish; the simulator has a minor role. The structure sub-index is set to 0 (recommended) even where the text notes serious fire hazards. Read from a web archive copy.

### Process Analysis of Hydrogen Production via Biomass Gasification under Computer-Aided Safety and Environmental Assessments

`meramo-2020-h2-gasification-isi` · Samir I. Meramo-Hurtado, Plinio Puello, Amaury Cabarcas · 2020 · journal · ACS Omega 5(31)

[Open copy read](https://pmc.ncbi.nlm.nih.gov/articles/PMC7424729/) · [DOI](https://doi.org/10.1021/acsomega.0c02344) · read: Process simulation, inherent safety index and process route index results, conclusions, methodology sections

**Objective.** Screen a conceptual biomass-to-hydrogen process for environmental impact and inherent safety using simulator output.

**Tools.**
- Aspen Plus (version: not stated): Steady-state flowsheet supplying flows, conditions and properties for the indices.
- WARGUI (US EPA waste reduction algorithm) (version: not stated): Environmental impact calculation.

**How the study was built.**
1. Simulate the steady-state flowsheet with biomass as a non-conventional solid defined by proximate and ultimate analyses.
2. Break biomass into its constituent elements in a yield reactor using the analyses.
3. Score the chemical sub-indices from reaction heat, interaction, hazardous substance and corrosivity on a worst-case basis.
4. Score process sub-indices from a one-hour residence-time inventory inside battery limits, maximum temperature and pressure, equipment type and process structure.
5. Add the Process Route Index alongside the inherent safety index.

**Modelling choices.**
- Property method: Peng-Robinson with the Boston-Mathias modification.
- Gasifier assumptions: Steady state, isothermal gasification, char as solid carbon, no tar.
- Inventory basis: One-hour hydraulic retention time for equipment inside battery limits.
- Structure sub-index: Set by judgement using reported experience from coal gasification and similar combustion processes.

**Tool chain.** Aspen Plus mass and energy balances feed the safety indices and the WAR software.

**Validation (literature-values).** Only the biomass-to-syngas conversion (83%) is said to be within literature expectations. For the safety results, the PRI is compared with values for other processes and the ISI with a neutral score of 24; this is not validation of the indices.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Area and equipment size outside battery limits are unknown at conceptual stage, so scoring treats units as inside battery limits.
- The structure sub-index is hard to assign because it has no firm definition.

**Reusable lesson (compiler's).** Keep sub-index scores consistent between text, tables and totals, and trace each score to a stream, property source or judgement; index studies are easy to build on a flowsheet and hard to check without this.

**Caveats.** Section 2.3.1 text gives a chemical sub-index total of 18 with a corrosivity score of 1, while Table 6 and the conclusions give 19 with corrosivity 2; the reported ISI of 35 equals 19 plus the process total of 16. The text attributes a 61.5 v/v% flammable range to methane, while Table 4 lists 61.5 for carbon monoxide and 10 for methane. In the saved HTML text the first four values in each row of Table 10 (headed ash, C, H, N) are the same as the four values in Table 9 (moisture, volatiles, fixed carbon, ash).

## Dynamic operability, start-up and operator training

### Optimal operation of cooling cycle/LNG process

`jacobsen-2007-hysys-dynamic-c3mr` · Magnus Glosli Jacobsen · 2007 · masters-thesis · NTNU, Department of Chemical Engineering (external adviser from Norsk Hydro)

[Open copy read](https://skoge.folk.ntnu.no/diplom/diplom07/jacobsen_magnus-glosli/diplom.pdf) · read: abstract, section 2.4, ammonia case study (modelling, optimisation, discussion, conclusions), section 4.3-4.4 and appendix model specifications

**Objective.** Study degrees of freedom and control of refrigeration cycles in dynamic HYSYS, first for an ammonia cycle and then for a C3-MR LNG process.

**Tools.**
- Aspen HYSYS (version: 2004.2): Steady-state and dynamic models and controller tests.

**How the study was built.**
1. Build the steady-state case close to the published reference study to allow comparison.
2. Do a degrees-of-freedom analysis to allocate valves and compressor work before adding controllers.
3. Tune controllers from step responses fitted as approximate transfer functions.
4. Step the optimising valve and allow long settling between steps to locate the optimum in the dynamic model.
5. Replace the main cryogenic exchanger with shell-and-tube units using the detailed rating model; model most other exchangers with the basic model at first to find approximate UA values.

**Modelling choices.**
- Property package, ammonia cycle: Soave-Redlich-Kwong.
- Property package, appendix specifications for C3-MR: Peng-Robinson.
- Heat exchanger rating model, ammonia cycle: Detailed zoned model for the condenser and basic UA model for the vaporizer. A run with the basic end-point model on the condenser showed no subcooling optimum.
- C3-MR simplifications: Fractionation column omitted; main exchanger replaced by shell-and-tube exchangers; multistage compressors split into separate units.

**Validation (code-to-code).** The qualitative conclusion of an earlier modelling study (some condenser subcooling is optimal) is reproduced in dynamic HYSYS; the numerical value differs. No plant data. The C3-MR dynamic model was not completed or validated.

**Sensitivity or uncertainty.** Heat exchanger model fidelity and valve position were varied; the optimum was very flat.

**Limitations the authors state.**
- Dynamic mode does not allow an initial liquid level or holdup to be specified in heat exchangers.
- Basic end-point exchanger rating should not be used where phase change occurs.
- There was not enough time to complete the LNG model in the desired detail.
- Unexplained small spikes appeared when superheat reached zero; model or numerical cause unknown.

**Reusable lesson (compiler's).** Check that the heat exchanger discretisation can represent the effect you are optimising; with phase change an end-point UA model can remove the optimum entirely.

**Caveats.** Old software version; diploma work; no data validation. The appendix property statement is read as applying to the C3-MR case because it sits among its model specifications.

### Dynamic simulation of a centrifugal compressor system

`liedman-mansson-2013-compressor-dynamic` · Johan Liedman, Robert Månsson · 2013 · masters-thesis · Chalmers University of Technology

[Open copy read](https://publications.lib.chalmers.se/records/fulltext/179072/179072.pdf) · read: introduction, chapter 3 modelling and scenarios, chapter 4 validation, start of chapter 5, conclusions

**Objective.** Build and check a dynamic model of an offshore two-stage gas compression system and use it to study shutdown, start-up and step changes for a planned modification.

**Tools.**
- Aspen HYSYS Dynamics (version: 7.3): dynamic compressor, anti-surge and control model

**How the study was built.**
1. Enter vendor compressor curves, motor and compressor inertia and driver torque-speed data; extrapolate other speeds when only one speed curve exists.
2. Specify flows at gas inlets and pressures at outlets so the volume upstream of the compressor behaves realistically.
3. Replace the software surge-line polynomial with a molecular-weight-independent surge correlation in a spreadsheet where surge varies with gas weight.
4. Validate the as-built version on gas-sampled steady states and on logged shutdown and start-up transients before changing it to the new design.
5. Check start-up duration against the plant (6.5 s simulated, 5 to 7 s observed).
6. In shutdown studies from near the surge line, vary surge margin, anti-surge valve Cv and speed, inertia and discharge volume.

**Modelling choices.**
- property package: Peng-Robinson for gas; NRTL for the water/TEG cooling medium.
- wall heat effects: No wall heat transfer or wall heat storage.
- heat exchanger model: Simple flow-scaled UA; a more detailed model was rejected as slow and giving unreasonable results.

**Tool chain.** Vendor datasheets and curves plus gas samples feed the existing-system model; after validation it is rebuilt with the new compressor data for scenario runs.

**Validation (plant-data).** Gas-sampled steady states showed temperature and some pressure differences, and the authors found it hard to draw conclusions given measurement uncertainty. They conclude that dynamic behaviour for start-up time, flow and pressures was similar to the plant and that start-up time fell within the plant's range. In logged shutdown and start-up, changes in flow, pressure and temperature were faster in the simulation, temperature transients agreed poorly, and in the shutdown the model surged in both stages while the readings showed no sign of first-stage surge.

**Sensitivity or uncertainty.** Surge margin, anti-surge valve size and opening speed, inertia, discharge volume, curve extrapolation and controller tuning.

**Limitations the authors state.**
- Temperature predictions are doubtful without wall heat transfer and storage.
- Faster model dynamics can overstate the tendency to surge.
- The software handles surge poorly and its default low-speed curve extrapolation tends to overestimate head.
- Plant logs resolved no faster than one reading per second.

**Reusable lesson (compiler's).** Validate compressor trips against logged transients, not only steady points, and review pipe volumes, wall thermal mass, sensor response and off-curve extrapolation before sizing anti-surge hardware from the model.

**Caveats.** Master's thesis; control tunings were not the plant's; dynamic datasets lacked gas composition and some inlet flows, so comparison is mainly qualitative.

### Operator Training Simulator for Ethylene Plant

`sangaran-haron-2017-ethylene-ots` · Sritharan Sangaran, Saharudin Haron · 2017 · journal · Chemical Engineering Transactions 56 (Universiti Teknologi Malaysia; Petronas Chemical Olefins)

[Open copy read](https://www.aidic.it/cet/17/56/271.pdf) · [DOI](https://doi.org/10.3303/CET1756271) · read: whole paper

**Objective.** Describe how an operator training simulator for an ethylene cracker was built and accepted, covering start-up, shutdown and upsets.

**Tools.**
- DYNSIM (version: not stated): dynamic process model acting as the virtual plant

**How the study was built.**
1. Verify the design heat and material balance, fix the scope to training needs and treat utilities as boundaries.
2. Mark up P&IDs with system experts, choose which isolation and safety valves to include, then build and join the flowsheets using equipment data.
3. Run a model acceptance test of the flowsheets against the marked-up P&IDs, without complex control loops, logging a punch list.
4. Import DCS graphics, controls and shutdown logic from the plant into the simulator.
5. At factory acceptance, trigger each malfunction from steady state and compare with expected response; repeat testing on site.
6. Have experienced panel operators shut the model down and start it up again through the DCS graphics.

**Modelling choices.**
- thermodynamics: Soave-Redlich-Kwong.
- equipment fidelity: Performance curves for rotating machines, actual exchanger and column geometry, and vessel heat loss so that shutdown cooling is represented.

**Tool chain.** Design heat and material balance and P&IDs build the DYNSIM model; plant data are used to realign it; DCS and ESD logic are linked through vendor software into the training stations.

**Validation (plant-data).** Steady-state plant values compared with design balance and two model versions; initial mismatches came from set points and balance data that differed from the operating plant and were corrected using plant data. No quantitative transient agreement reported.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- A model built from design mass and energy balances did not reflect the operating plant and had to be realigned to plant data.
- Testing quality suffers when testers do not know the plant and its control system; experienced panel operators are needed.

**Reusable lesson (compiler's).** For a simulator of an existing plant, calibrate to operating data and actual controller set points from the start, and budget experienced operators for acceptance testing of start-up and shutdown.

**Caveats.** Short paper with little numerical detail; the closing claim of accurate transient behaviour is not backed by transient data in the text; software version not stated.

### Integrated process and control modelling of water recirculation in once-through boilers during low load and transient operation

`rosslee-2020-once-through-boiler-startup` · Pieter Johannes Rosslee · 2020 · masters-thesis · University of Cape Town

[Open copy read](https://open.uct.ac.za/server/api/core/bitstreams/479bc285-31f6-4278-a520-ca8fd3cd9907/content) · read: abstract, scope and assumptions, sections 3.6-3.7 model, chapter 4 validation, chapter 6 plant implementation, chapter 7

**Objective.** Model the start-up recirculation loop of a large once-through boiler with its controls, validate it on plant data, and design a better control strategy.

**Tools.**
- Flownex (version: not stated): integrated thermo-fluid and control simulation

**How the study was built.**
1. Lump parallel tubes into representative pipes and apportion furnace heat to them as scaled fractions of fuel input.
2. Represent steam outlet pressure and pump and feedwater flows as boundary conditions, and the separators with a two-phase tank element.
3. Solve the steady state with an external routine that adjusts recirculation flow to close the tank energy balance, then release the boundary and start the transient.
4. Compare steady states at several loads with averaged control-system readings.
5. Drive a six-hour cold start with recorded pressure, load and feedwater temperature and compare unforced outputs such as inlet temperature, steam flow and vessel level.

**Modelling choices.**
- two-phase model and scope: Homogeneous two-phase flow; main steam valve as a pressure boundary.
- numerics: Time step 0.1 s with integration weighting factor 0.7.
- heat input calibration: Boiler efficiency function raised to 103% to correct under-predicted evaporator heat during start-up.

**Tool chain.** Plant control-system records are imported by script as time-varying boundary inputs; the validated model is then used to test control changes, later implemented on a unit in commissioning.

**Validation (plant-data).** Steady states at three loads compared with plant control-system data: generally good, with the largest errors in economiser temperatures and pressure drops, attributed to circulation-flow changes. In a six-hour cold start, compared graphically, the author judges economiser inlet temperature sufficiently accurate and finds main steam flow in good agreement except at very low loads and suspected mill-purge events; collecting-vessel level was also compared.

**Sensitivity or uncertainty.** Single-parameter transient changes (pressure, circulation flow, feedwater temperature, load) with controls off, then with controls on.

**Limitations the authors state.**
- Measured fuel input is uncertain, for example unmetered heat from mill purging.
- Furnace heat split was scaled linearly from full load and could be improved.
- Superheater and downstream pressure control are omitted behind a fixed-pressure boundary.

**Reusable lesson (compiler's).** Replaying recorded boundary data through a start-up model is a practical transient check, but report which inputs and calibration factors were imposed or tuned so the remaining outputs can be judged fairly.

**Caveats.** Master's thesis with an industry sponsor; calibration factor above 100 percent absorbs modelling error; some steady-state calibration also adjusted boundary values and circulation flow; software version not found in the parts read.

## Process design, optimisation and techno-economics

### Process Design and Economics for Conversion of Lignocellulosic Biomass to Ethanol: Thermochemical Pathway by Indirect Gasification and Mixed Alcohol Synthesis

`dutta-2011-nrel-thermochemical-ethanol` · A. Dutta, M. Talmadge, J. Hensley, M. Worley et al. · 2011 · official-report · National Renewable Energy Laboratory, NREL/TP-5100-51400

[Open copy read](http://web.archive.org/web/20250320125116id_/https://www.nrel.gov/docs/fy11osti/51400.pdf) · read: section 2.3 (Aspen Plus model), parts of 3.3, 3.4, 3.8-3.9, sections 5-7, Appendix G start

**Objective.** Document a benchmark process design and economic model for ethanol from woody biomass by indirect gasification and mixed alcohol synthesis, with research targets.

**Tools.**
- Aspen Plus (version: 2004.1): Plant-wide mass and energy balances.

**How the study was built.**
1. Represent real species from the component database and treat biomass, ash and char as non-conventional solids.
2. Assign property packages by plant area rather than using one for the whole plant.
3. Model complex absorption sub-systems in separate simulations and import their results.
4. Predict gasifier gas with temperature correlations fitted to pilot data and close char by mass difference.
5. Set reformer conversions to stated research targets with outlet at shift equilibrium.
6. Let the model adjust steam-cycle water flow to close the heat balance found by pinch analysis.

**Modelling choices.**
- Gas and high-pressure property method: RKS with Boston-Mathias modification for much of the plant.
- Alcohol, steam and electrolyte areas: NRTL with ideal gas for alcohol separation; ASME 1967 steam tables for the steam cycle.
- Gasifier model basis: Correlations from a 9 tonne per day pilot facility, mostly 1,500 to 1,672 degrees F.
- Alcohol synthesis kinetics: Kinetic model supplied by Dow under confidentiality, based on bench and pilot data.

**Tool chain.** Pilot-data correlations, target reformer conversions, a confidential kinetic model and separate absorber simulations feed one Aspen Plus balance; its results drive pinch analysis, equipment costing and a minimum selling price with sensitivity cases.

**Validation (experiment).** Only components are tied to data: gasifier correlations come from pilot runs, and the alcohol kinetic model is shown in parity plots against experiments. The integrated plant is a forward-looking design with no plant validation.

**Sensitivity or uncertainty.** One-parameter and feedstock scenarios on minimum ethanol selling price; less than plus or minus 20% price uncertainty for plus or minus 30% capital cost uncertainty.

**Limitations the authors state.**
- Reformer targets were mostly shown at bench scale; continuous pilot operation was still to be demonstrated.
- The gasifier and tar reformer were not commercially available.

**Reusable lesson (compiler's).** For a plant that does not exist, tabulate which blocks are data correlations, which are targets and which are rigorous, and keep that distinction with every headline result.

**Caveats.** Conceptual nth-plant design built on future research targets; part of the kinetics is confidential and so not reproducible. Read from a Wayback copy of the NREL PDF. Software version is old.

### Modelling of an industrial plant for vinyl chloride production

`rossanese-2016-vcm-flowsheet-thermo-validation` · Giovanni Rossanese · 2016 · masters-thesis · Universita degli Studi di Padova, Dipartimento di Ingegneria Industriale

[Open copy read](http://web.archive.org/web/20260216212505id_/https://thesis.unipd.it/retrieve/06ca9d3f-eff6-4d39-8d3d-a1b4678732a9/GIOVANNI_ROSSANESE_1144780_assignsubmission_file_Rossanese_Giovanni_1080770.pdf) · read: abstract, thermodynamic package and validation (section 3.2 and chapter 4), start of reactor modelling, HCl column results and thermodynamic checks in chapter 6, conclusions

**Objective.** Build a whole-plant vinyl chloride flowsheet and establish how far its thermodynamic model and results can be trusted by regression on binary data and comparison with literature plant data.

**Tools.**
- gPROMS ProcessBuilder (version: not stated): Flowsheet simulation
- Multiflash (Infochem) (version: not stated): Property package with DIPPR pure-component data, also used from Excel for regression

**How the study was built.**
1. Choose the thermodynamic model family from component non-ideality and operating pressure.
2. Identify which binary pairs control the key separations and gas solubilities, and gather data near operating conditions.
3. Regress interaction parameters by least squares on temperature or pressure with the same property engine the flowsheet uses.
4. Check dataset consistency from the pattern and size of residuals.
5. Check pure-component vapour pressures against data, because binary parameters cannot correct errors in them.
6. Test the effect of parameter sets and an alternative equation of state on the sensitive column against a reference temperature profile and spot flashes.

**Modelling choices.**
- Property model: NRTL for the liquid with Redlich-Kwong for the vapour, as the pressure limit of an ideal vapour was judged too low.
- Non-randomness parameter: Fixed at the default 0.3 for all binaries.
- Side-reaction pre-exponential factor: Adjusted until direct chlorination selectivity reached 99%.
- Dropping one regressed binary set: The vinyl chloride and HCl parameters were left out of the final flowsheet because the results were closer to practice without them.

**Tool chain.** Literature binary data are regressed through the Excel interface to the property engine; the resulting property file is imported by the process simulator, whose column results are checked against a reference temperature profile and direct property-engine flashes.

**Validation (literature-values).** Binary data were fitted and plant-section results compared with literature values; several parts were close to expected values, but HCl and vinyl chloride equilibria with EDC were not reliable. With the full parameter set no vapour was predicted at one HCl column stage condition.

**Sensitivity or uncertainty.** Full versus reduced parameter sets and SRK on the HCl column; reactor design and kinetic parameter sensitivities. Direct chlorination was not affected by the binary parameters.

**Limitations the authors state.**
- The HCl column works above HCl's critical temperature, so the Antoine vapour pressure is used outside its validity.
- Simulation results are only partly accurate because of the thermodynamic representation.
- More data are needed for systems with HCl above its critical temperature.

**Reusable lesson (compiler's).** Good binary fits do not validate a flowsheet: check supercritical components and pure vapour pressures, and test the sensitive column with parameter sets switched on and off against an independent profile.

**Caveats.** Masters thesis with software-vendor support. The comparison data are from literature. A kinetic factor was tuned to a target selectivity, so that selectivity is not validation. Chapter 4 presents NRTL as an activity coefficient model, while the conclusions refer to an NRTL equation of state. Safety use is not the topic; it is a process simulation verification example.

### Modeling and Control of Post-Combustion CO2 Capture Process Integrated with a 550MWe Supercritical Coal-fired Power Plant

`zhang-2016-aspen-dynamics-mea-control` · Qiang Zhang · 2016 · phd-thesis · West Virginia University

[Open copy read](https://researchrepository.wvu.edu/cgi/viewcontent.cgi?article=8079&context=etd) · [DOI](https://doi.org/10.33915/etd.7038) · read: abstract, literature review (parts), chapters 3 and 4 (to the pressure-drop model), conclusions and future work; control chapters 5-7 only through the conclusions

**Objective.** Build steady-state (Aspen Plus) and pressure-driven dynamic (Aspen Plus Dynamics) models of MEA capture integrated with a supercritical coal plant, then design PID, linear and nonlinear MPC and robust controllers.

**Tools.**
- Aspen Plus (RateSep) (version: not stated): Rate-based steady-state capture model used for sizing and optimisation.
- Aspen Plus Dynamics (version: not stated): Equilibrium-based pressure-driven dynamic model and control test bed.
- Aspen Exchanger Design & Rating (version: not stated): Sized exchangers to give hold-up volumes and metal mass.

**How the study was built.**
1. Build and optimise the rate-based steady-state model by sensitivity runs on temperatures, lean loading, pressures and packing height.
2. Before export, size columns, exchangers and vessels and add volumes and metal mass, because they set accumulation rates.
3. Connect units through flow devices so that pressure and flow can be solved together.
4. Replace rate-based columns by equilibrium columns and correct them with a fitted CO2 Murphree efficiency correlation checked against the rate-based model off design.
5. Replace the default dynamic packing pressure-drop equation with a fitted correlation so off-design hydraulics match the steady-state model.
6. Identify reduced models from the dynamic simulation for use inside model-predictive control.

**Modelling choices.**
- Property method: Electrolyte NRTL for the liquid and Redlich-Kwong for the vapour in the rate-based model.
- Reaction treatment: CO2 absorption and desorption reactions kinetically controlled, the rest at equilibrium in steady state.
- Dynamic-model reaction treatment: Kinetic reactions replaced by equilibrium reactions with literature equilibrium constants, as the dynamic tool does not support the rate-based tower.
- Number of trains simulated dynamically: Two trains only, although three to six are needed, because of computing cost.
- Packing choice: Random packing in the absorber and structured in the stripper, because the Aspen Plus model was considered validated for that arrangement.

**Tool chain.** Rate-based Aspen Plus results size the plant and calibrate efficiency and pressure-drop correlations; the exported Aspen Plus Dynamics model is then used to identify linear and nonlinear models for controllers.

**Validation (code-to-code).** The equilibrium dynamic model with fitted efficiency and pressure-drop corrections is compared with the rate-based model (parity plots, good match). The abstract also says the steady-state model is validated with pilot-plant data, but no such comparison was found in the sections read or by text search.

**Sensitivity or uncertainty.** Steady-state sensitivity on temperatures, loading, stripper and absorber pressure and packing height, used to lower reboiler heat duty from 4.05 to 3.07 GJ/ton CO2.

**Limitations the authors state.**
- The dynamic tool lacks the rate-based column model, forcing the equilibrium substitute and corrections.
- The default steam turbine performance curve is only an approximation for load-following dynamics.
- MEA degradation is not modelled.

**Reusable lesson (compiler's).** When moving from rate-based steady state to an equilibrium dynamic model, test the two against each other over the whole disturbance range, including hydraulics, not only at the design point.

**Caveats.** The abstract says the steady-state model is validated with pilot-plant data; no such comparison was found in the sections read or by a text search of the saved text. No comparison of the dynamic results with plant or experimental data was found. Software versions not stated.

### Modelling advanced reforming of bio-compounds for hydrogen production

`reeve-2020-leeds-bio-oil-reforming` · Jennifer Sarah Reeve · 2020 · phd-thesis · University of Leeds

[Open copy read](https://etheses.whiterose.ac.uk/id/eprint/27925/1/Reeve_JS_SCAPE_PhD_2020.pdf) · read: abstract, sections 3.2-3.4, 5.2.5, 6.3-6.4, 7.3.5, parts of chapter 8; literature review and cost chapters only in part

**Objective.** Assess sorption-enhanced chemical looping reforming of bio-oil with equilibrium flowsheets and economics, then study the reduction-calcination step with a dynamic packed-bed model and acetic acid kinetics.

**Tools.**
- Aspen Plus (version: not stated): Equilibrium flowsheets giving heat and material balances for thermodynamic and techno-economic work.
- gPROMS ModelBuilder (version: 4.1.0): Dynamic distributed reactor model and kinetic parameter estimation.

**How the study was built.**
1. Represent bio-oil first by single model compounds and then by a surrogate mixture matched to elemental composition and thermogravimetric curve.
2. Model reformers as Gibbs-minimisation reactors for the feasibility stage, stated as a simplifying assumption.
3. Emulate a cyclic fixed bed in steady state with a series of reactor blocks, passing the solid bed state from one stage to the next.
4. Replace separation systems that are outside the study aim with recovery-specified separator blocks and literature energy use.
5. Build the dynamic reactor model hierarchically: validate each sub-process separately, then combine.
6. Test the fitted kinetic model on extra experiments not used in fitting.

**Modelling choices.**
- Property method: Peng-Robinson, citing simulator guidance for hydrogen-rich high temperature and pressure service and similar literature models.
- Reactor idealisation: Adiabatic Gibbs blocks for the looping stages; adiabatic specified-reaction equilibrium reactor for water-gas shift.
- PSA idealisation: Split-fraction separator with 90% H2 recovery.
- Discretisation: Backward finite differences along the axis; 50 to 1000 intervals tested with minimal effect; DASOLV integrator.

**Tool chain.** Aspen Plus equilibrium balances feed the cost model and give the off-gas composition used as feed to the gPROMS reduction-calcination model; measured kinetics fitted in gPROMS feed later reactor comparisons.

**Validation (experiment).** Reduction and sorption-enhanced reforming sub-models compared graphically with literature experiments (authors report excellent agreement). Fitted kinetic model outlet concentrations: average absolute deviation 10.64%, with 4.34% for H2 and 18.46% for CO. Against an Aspen Plus equilibrium reactor, the authors report a good estimate from 600 to 700 degrees C and divergence outside that range.

**Sensitivity or uncertainty.** Reduction-calcination model varied feed gas, temperature, pressure, flux and sorbent capacity; mesh interval count also checked.

**Limitations the authors state.**
- The steady-state flowsheet cannot describe the dynamics of the cyclic process and is only for preliminary economics.
- The combined reduction-calcination model still needs experimental validation over a range of conditions.
- A full dynamic cycle model is blocked by lack of bio-oil kinetics.
- The fitted power-law kinetic model is not readily extrapolated outside the experimental pressure range and needs caution at low temperature or high pressure, where methane formation (not modelled) is likely.

**Reusable lesson (compiler's).** Validating sub-models separately does not validate their combination; say so explicitly and keep the claim for the combined model at the feasibility level.

**Caveats.** The abstract places the dynamic reactor model in Chapter 7, while the body presents it in Chapter 6. Aspen Plus version not stated.

### Modelling of a low emission thermally integrated gasifier for clean gas production from agricultural and forestry residues

`usmani-2020-unisim-integrated-gasifier` · Sameer Usmani · 2020 · masters-thesis · Southern Cross University

[Open copy read](https://researchportal.scu.edu.au/view/delivery/61SCU_INST/1277106940002368/1377106930002368) · [DOI](https://doi.org/10.25918/thesis.76) · read: abstract and chapter 4 (model description, validation, start of results) and its conclusions

**Objective.** Model a two-stage thermally integrated steam gasifier for hardwood in UniSim and check whether heat from the hot stage can drive the low-temperature stage.

**Tools.**
- UniSim Design (version: not stated): Steady-state two-stage gasification model.

**How the study was built.**
1. Define biomass as a hypothetical solid from literature proximate and ultimate analyses.
2. Split the process into a low-temperature and a high-temperature stage with separate reactor modules.
3. Specify oxidation-type steps as conversion reactions and methanation, shift and reforming as equilibrium reactions.
4. Validate only the low-temperature stage against laboratory char yields, averaging scattered replicates.
5. Represent heat conduction through a dividing wall with a pair of linked exchangers, since the tool cannot transfer heat directly between units.

**Modelling choices.**
- Property package: Peng-Robinson, justified by earlier gasification studies.
- Thermal assumptions: Adiabatic gasification stages.
- Heat loss: 20% assumed in transfer from stage 2 to stage 1.

**Validation (experiment).** Low-temperature stage only, against the author's heating-chamber experiments at 10, 15 and 20 l/min air: carbon error 1.6% to 6.4%; gas production error up to 10.62%. The integrated concept and high-temperature stage are not validated.

**Sensitivity or uncertainty.** Air flow, high-temperature stage temperature and steam/biomass ratio (1.0 to 4.0) varied for heat transfer, syngas composition and heating value.

**Limitations the authors state.**
- The tool cannot represent biomass physical structure, dust or impurities.
- Tar cannot be analysed with this model.
- The author says an equilibrium model suffices for the proof-of-concept scope, but detailed kinetic, particle and reactor models are required.

**Reusable lesson (compiler's).** Say which part of a flowsheet the data actually test; agreement on one stage's solid yield says little about downstream gas composition.

**Caveats.** The abstract has an unfinished validation sentence (dots in place of text). At 10 l/min the section 4.5 text gives 123 g of carbon from experiment and 125 g from the model, while Table 20 lists 125 g experimental and 123 g UniSim. The text gives a maximum gas-production error of 10.7% and Table 22 lists 10.62%. The assumption list gives a biomass flow of 1 kg/h, while Table 19 lists 10 kg/h. UniSim version not stated.

## Model validation, comparison and uncertainty

### Atmospheric Dispersion Model Validation in Low Wind Conditions

`sawyer-2007-aloha-low-wind-validation` · Patrick Shawn Sawyer · 2007 · official-report · National Security Technologies for US DOE, DOE/NV/25946-277

[Open copy read](https://www.osti.gov/servlets/purl/934686) · read: abstract, chapter 1, parts of chapter 2, chapters 3-5

**Objective.** Test ALOHA, EPIcode and SCIPUFF against near-field releases of three gases in winds mostly below 2 m/s.

**Tools.**
- ALOHA (version: 5.4.1): One of three models under test.
- EPIcode (version: 7.0): Comparison model.
- SCIPUFF (version: AFTAC 1.3.6 (Breeze)): Comparison model.

**How the study was built.**
1. Release each gas as repeated short and long releases, to represent puffs and plumes, inside rings of point sensors.
2. Use time-averaged release rate and wind from a wind-sensor array as model inputs.
3. Assign stability class from the measured standard deviation of wind direction.
4. Compare the highest two-minute average on each ring with predicted centreline concentration.
5. Score with FAC2, correlation, NMSE, fractional bias, VG and MG, split by distance, flow rate, species and release duration.

**Modelling choices.**
- surface roughness: 0.0003 m for the dry lake bed, from published guidance.
- evaluation standard: ASTM D6589-05.

**Tool chain.** Same measured inputs were given to the three models separately.

**Validation (experiment).** Factor-of-two fractions over all data were 0.4000 for ALOHA, 0.4583 for EPIcode and 0.4250 for SCIPUFF, with low correlation coefficients; the author finds ALOHA biased to under-prediction.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- ALOHA forced a higher wind speed than observed in 19 of 30 experiments because of its minimum for the stability class, which the author gives as a reason for its under-prediction.
- ALOHA is not designed for these low-wind conditions and tended to under-predict, so it needs caution.
- Some detector points rose with distance because of meander, lofting and sensor spacing; denser arrays are needed.

**Reusable lesson (compiler's).** Log the inputs the tool actually used, not only those you wanted to enter: a forced higher wind speed changes the comparison and, per the author, lowered ALOHA's predicted concentrations.

**Caveats.** The species discussion describes the SCIPUFF geometric-mean-bias values as under-prediction, while Table 8 lists values below 1, which the report defines as over-prediction. Table 6B prints the same 100 m MG (1.4227) for ALOHA and EPIcode. The report uses ammonia as its buoyant-gas case. Small releases (mean rates under about 20 kg/h) and ranges to 100 m only.

### Validation of PHAST Dispersion Model as Required for USA LNG Siting Applications

`witlox-2013-phast-udm-lng-phmsa-validation` · Henk W. M. Witlox, Mike Harper, Robin Pitblado · 2013 · journal · Chemical Engineering Transactions vol. 31 (DNV)

[Open copy read](https://www.aidic.it/cet/13/31/009.pdf) · read: whole paper

**Objective.** Summarise the validation of the Phast Unified Dispersion Model against the LNG model evaluation protocol database for US siting approval.

**Tools.**
- Phast (UDM dispersion with PVAP pool model) (version: 6.7 for inputs; approval covers 6.6 and 6.7): Model under validation.

**How the study was built.**
1. Take the experiment list from the prescribed evaluation protocol and state for each how it is represented in the model.
2. Represent LNG field spills as low-momentum elevated horizontal releases with almost complete immediate rainout, so a pool forms.
3. Split time-varying pool evaporation into constant-rate segments, and pick the segment to match the averaging window.
4. Compute MG, VG, relative bias and error, factor-of-two fraction and safety factors on concentration, width and distance to LFL.
5. Submit input-uncertainty sensitivity (wind, stability, roughness, pressure, humidity, composition) with the statistics.

**Modelling choices.**
- surface for Burro inputs: Roughness 0.0002 m; pool on shallow water.
- LNG representation: Pure methane in the example input table.
- flammable endpoint safety factor: Approval recommends using half LFL, consistent with Phast defaults for flammables.

**Tool chain.** Discharge/pool rate segments from PVAP feed the UDM dispersion calculation.

**Validation (experiment).** Authors report excellent short-average Burro and Coyote results and under-prediction for Maplin Sands; for long averages, excellent Thorney Island, good Burro and over-predicted Coyote concentrations; wind-tunnel concentrations consistently under-predicted with slightly over-predicted widths. Cited earlier work on a wider large-scale set (overlapping these field tests) gives overall agreement within a factor of two.

**Sensitivity or uncertainty.** Sensitivity to experimental input uncertainty was part of the submission; results are not given in this paper.

**Limitations the authors state.**
- Phast assumes uniform roughness, so approval notes it may be unsuitable for high aspect-ratio pools, highly varying terrain or large obstacles.
- Long averaging times with strongly time-varying pools are hard to model with the segment approach.

**Reusable lesson (compiler's).** State the segment-selection and averaging-time rule alongside any validation score, because the score depends on it. Check wind-tunnel and field results separately.

**Caveats.** Vendor-authored summary. The conclusions describe over-prediction for the scaled wind-tunnel experiments, while the results section says concentrations were consistently under-predicted there; the wind-tunnel MG values in Table 4 (defined as observed over predicted) are above 1, in line with the results section. The suggested explanation for the Maplin Sands and wind-tunnel results relies partly on verbal communication with the regulators.

### Modelling and Validation of CO2 Capture Processes with Piperazine

`gomes-2015-gproms-piperazine-capture` · Mariana Rodrigues Ferreira de Sousa Gomes · 2015 · masters-thesis · Universidade do Porto, with Process Systems Enterprise

[Open copy read](https://repositorio-aberto.up.pt/bitstream/10216/79641/2/35866.pdf) · [DOI](https://doi.org/10.34626/dsb8-kh59) · read: abstract, chapters 3, 4, 5.1 and 7

**Objective.** Extend a vendor capture model library to piperazine solvent, validate the absorber against pilot data and compare and optimise process configurations.

**Tools.**
- gPROMS ModelBuilder (version: 4.1.0): Flowsheet simulation and optimisation.
- gCCS capture library (version: not stated): Rate-based two-film column and auxiliary unit models.
- gSAFT (version: not stated): Physical property package for gas and liquid.

**How the study was built.**
1. Add missing solvent transport property correlations to the library, checking how much the results depend on poorly known ones.
2. Choose a fitted viscosity form that stays physical outside the measured temperature range.
3. Initialise columns at an easy condition, save the solution, then move inputs to the target in small steps.
4. Tune the solvent diffusivity multiplier to reduce CO2 removal deviation against pilot runs.
5. Solve the stripper loop open first, then close recycles with recycle-breaker blocks once outlets match inlets.
6. Compare configurations with the same lean solvent, flue gas and utility conditions.

**Modelling choices.**
- Thermodynamics: SAFT-VR based package that treats CO2-amine reaction implicitly as association, avoiding explicit ionic species.
- Column assumptions: Two-film, distributed axially, films not discretised, reactions only in the liquid bulk, equilibrium at the interface.
- Packing substitution: Mellapak 250Y used because data for the pilot packing were not available to the author.
- Unmeasured inlet condition: Flue gas assumed water saturated, as only CO2 content was reported.

**Tool chain.** Validated absorber (and an intercooled version) is placed into five full capture flowsheets, which are then subjected to sensitivity analysis and gPROMS optimisation.

**Validation (experiment).** University of Texas pilot absorber, 15 runs plus 2 intercooled runs. CO2 removal deviations in the printed table reach -13% (run 1); the abstract and conclusions state a maximum of -12%. Rich loading deviations are much smaller. The diffusivity factor was adjusted against these removal data.

**Sensitivity or uncertainty.** Intercooling temperature and position, stripper pressure, L/G and piperazine concentration; surface tension checked and found minor.

**Limitations the authors state.**
- Column and flash models only initialise within a narrow range far from operating conditions, making initialisation very time consuming.
- Diffusivity data for piperazine are scarce, so values were adjusted toward experimental results.
- The stripper could not be defined from the pilot data beyond its pressure.

**Reusable lesson (compiler's).** If a parameter is tuned on a data set, call the comparison with that set calibration, and keep independent runs for validation.

**Caveats.** The calibration and validation data overlap, although the author calls the model predictive. Maximum deviation text (-12%) disagrees with the table (-13%). Later chapters call the stripper validated although the validation chapter gives no stripper comparison. Several numbers are missing from the extracted text.

### Jack Rabbit II Inter-model Comparison Exercise

`chang-2019-jack-rabbit-ii-model-intercomparison` · Joseph C. Chang, Steve R. Hanna, Tom Mazzola · 2019 · conference · RACIE Symposium, UC Davis (presentation slides)

[Open copy read](https://racielive.aqrc.ucdavis.edu/sites/g/files/dgvnsk8021/files/inline-files/Chang_JRII_model_comparison_v1.1.pdf) · read: all slides as extracted text, including backup input and statistics slides; figures not viewed

**Objective.** Compare 17 dense-gas dispersion models, including PHAST, ALOHA and SLAB, with three Jack Rabbit II large chlorine release trials.

**Tools.**
- PHAST (version: not stated): Run by DNV GL as one of the participating models.
- ALOHA and SLAB-R (version: not stated): Run by RAND as participating models.

**How the study was built.**
1. Choose a trial subset and exclude near-field sensors affected by the mock urban array.
2. Issue common recommended inputs for source, roughness and meteorology, while letting modellers use their own source model.
3. Request the same outputs from every model: arc maxima at fixed distances, cloud widths and heights, contours and time series.
4. Keep saturated sensor readings but flag them, since true concentrations were probably higher.
5. Score with geometric mean bias, geometric variance and factor-of-two and factor-of-five fractions on the closest arcs.

**Modelling choices.**
- source specification: Two alternative recommended source terms were tabulated: a single constant primary release, or a primary release modified for rainout plus a secondary release from evaporating rainout.
- surface roughness: 0.5 mm for the playa in the recommended inputs.

**Tool chain.** Each participant ran their own model from the shared input sheet.

**Validation (experiment).** Model predictions of arc maximum concentration spread over about 1 to 1.5 orders of magnitude, with observations always inside the range. On average widths were over-predicted and heights under-predicted, with cross-sectional area unbiased. The authors name ESCAPE, HPAC and IDDM as apparently better performers.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- Participants were not on equal footing because some had helped plan the trials and had seen the data.
- Real accidents add uncertainty beyond this exercise: unknown source terms, unclear surface deposition and uncertain health effects.
- Many models do not represent the obstacle array.

**Reusable lesson (compiler's).** For a dense-gas screening code, publish MG, VG and FAC2 on this common input set and expect inter-model spread of an order of magnitude. Hand-picking one tool does not remove that uncertainty.

**Caveats.** Slide deck, three trials only, with emission estimates marked as still subject to change; the saved text says nothing about peer review. Per-model scores are in a table whose text layout is partly broken in extraction, so they are not repeated here; read the original slide before citing a number for one model. DEGADIS is not among the models listed.

### Modelagem e simulacao de uma unidade industrial de producao de acido sulfurico integrada a uma planta de geracao de energia eletrica

`chagas-2021-unisim-sulfuric-acid` · Marcelo Martins das Chagas · 2021 · masters-thesis · Universidade Federal de Uberlandia

[Open copy read](https://repositorio.ufu.br/server/api/core/bitstreams/f02e6682-08c3-4682-b00e-1e3657d46586/content) · [DOI](https://doi.org/10.14393/ufu.di.2021.8015) · read: abstract, section 3.2 (model development), sections 4.1-4.5 (key parts) and chapter 5 conclusions; in Portuguese

**Objective.** Simulate an industrial sulfuric acid plant with integrated power generation, comparing the free COCO simulator and UniSim against design data and some operating data.

**Tools.**
- UniSim Design (version: R460.2): Simulated all circuits including turbines, converter, sulfur furnace and absorbers.
- COCO Simulator (version: not stated): Parallel model of turbines, converter and gas-steam circuits.
- Maple (version: not stated): Independent stoichiometric energy and material balance of the sulfur furnace to judge the simulator.

**How the study was built.**
1. Back-calculate turbine section isentropic efficiencies from the energy balance, treating an extraction turbine as two turbines in series.
2. Represent each catalyst pass as an adiabatic equilibrium reactor and compare outlet temperature and conversion with design values pass by pass.
3. Integrate gas and steam circuits only after the converter model has been checked, simplifying the economisers to one exchanger with fixed duty.
4. Test several symmetric and asymmetric property configurations for the sulfur furnace and build an independent hand-style model as reference.
5. Model the absorption towers as adiabatic equilibrium reactors when no suitable absorber thermodynamics is available.

**Modelling choices.**
- Water and steam properties: ASME Steam in UniSim, preferred over IF-97 for accuracy and wider range.
- Converter gas properties: Peng-Robinson; switching to ideal gas made no difference at the low pressure and high temperature involved.
- Sulfur furnace and absorbers: Peng-Robinson gas with UNIFAC liquid, selected because it gave the smallest furnace errors.
- Liquid sulfur component: Library sulfur at 150 degrees C chosen as closest to operating temperature.

**Tool chain.** Checked turbine and converter sub-models are connected into integrated gas and steam circuits; superheater predictions then set turbine power. Maple serves as a separate reference for the furnace.

**Validation (plant-data).** Compared mainly with plant design values, plus December 2020 operating values for turbine power. SO2 conversion: authors give a maximum relative error of 3.1%. Integrated gas and steam circuit: largest temperature error, for extraction steam, 15.26% in UniSim and 7.56% in COCO; turbine power about 6% high in UniSim and 1 to 2.5% high in COCO. Furnace outlet temperature: all-Peng-Robinson 19.1% below design, Peng-Robinson gas with UNIFAC liquid 9.5% above, Maple model 0.3%. Absorbers: simulated outlet gas temperatures 102.3 and 98.5 degrees C against 82.0 in design.

**Sensitivity or uncertainty.** Thermodynamic-package sensitivity for the converter and sulfur furnace.

**Limitations the authors state.**
- Turbine efficiency variation with steam flow was not modelled, which matters at reduced capacity.
- Absorber differences come mainly from the equilibrium-reactor simplification, with no mass transfer along the packing.
- The author concludes UniSim is not suitable for liquid sulfur combustion without first adjusting thermodynamic parameters.

**Reusable lesson (compiler's).** A default cubic equation of state for both phases can converge and still be badly wrong for a reactive molten feed; keep an independent energy balance for any high-temperature unit.

**Caveats.** Most comparisons are against design-basis values rather than measurements. The UniSim furnace error is 9.5% in the abstract and 9.6% in the conclusions. The Portuguese summary gives divergences of up to 6.7% for the integrated steam and gas circuit, while Table 17 lists a maximum of 15.26% (extraction steam, UniSim). Text is in Portuguese.

### Validation of the HyRAM+ physics models for use with propane

`shum-2021-hyram-propane-validation` · Jessica G. Shum, Ethan S. Hecht, Myra L. Blaylock · 2021 · official-report · Sandia National Laboratories, SAND2021-3244

[Open copy read](https://www.osti.gov/servlets/purl/1821534) · read: abstract, introduction, chapter 2 model description, start of flame length, heat flux section, trajectory text, conclusions

**Objective.** Check HyRAM+ jet flame length, heat flux, flame trajectory and unignited dispersion against published propane experiments.

**Tools.**
- HyRAM+ (version: not stated (cites the version 3.0 technical reference manual)): Model under validation, driven through Python objects.
- CoolProp (version: not stated): Propane thermodynamic properties for the leak calculation.

**How the study was built.**
1. Take experiment conditions from each paper as inputs and fill gaps with stated assumptions or calculations.
2. Where pressure and mass flow disagree, keep the measured mass flow and back-calculate pressure.
3. Compare flame lengths and widths across several independent datasets.
4. Compute heat flux twice, with predicted and with measured flame length, to expose compensating errors.
5. Compare centreline concentration, velocity and radial profiles for unignited jets.

**Modelling choices.**
- orifice and under-expansion: Isentropic orifice flow with the default Yuceil-Otugen notional nozzle only.
- equation of state: CoolProp near the leak, ideal gas elsewhere.

**Tool chain.** Orifice flow feeds the notional nozzle, then the jet or flame model.

**Validation (experiment).** Conclusions: flame lengths and widths over-predicted by around 65% in three of four cases, the fourth closer to 20% off. Heat flux was closer with the over-long predicted flame (errors around 65%) than with the measured length (closer to 85%). Flame trajectory matched at the high Reynolds number but buoyancy was much over-predicted at the lower one. Unignited centreline mole fraction was within 15%, with radial profiles wider than measured.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The data are low-pressure; more validation is needed at propane autogas storage pressures.
- All dispersion cases were unchoked, so choked flows remain unvalidated.
- Flame length and heat flux errors offset, so correcting one requires correcting the other.

**Reusable lesson (compiler's).** Validate intermediate quantities (flame length) as well as the end quantity (heat flux); otherwise compensating errors pass unnoticed.

**Caveats.** The percentage statements are not equivalent: sections 3 and 5 say measured flame lengths were about 65% of the predicted lengths, while the abstract and conclusions speak of over-prediction by around 65%. Section 3 describes five flame-length sources (one within about 20%, four with measured about 65% of predicted); the conclusions say three of four cases were over-predicted by about 65% and the fourth was closer to 20% off. The dispersion cases were all unchoked and the flame data were at low source pressure.

### Advanced Process Modeling and Optimization of Amine-Based Carbon Capture Process

`akula-2022-idaes-mea-capture` · Paul Terhemba Jide Akula · 2022 · phd-thesis · West Virginia University

[Open copy read](https://researchrepository.wvu.edu/cgi/viewcontent.cgi?params=/context/etd/article/12334/&path_info=Advanced_Process_Modeling_and_Optimization_of_Amine_Based_Carbon.pdf) · [DOI](https://doi.org/10.33915/etd.11370) · read: abstract, sections 1.3, 2.2, 2.7-2.9 (parts), 5.1-5.2 (packed column, validation, exchanger), 6.2-6.7 (parts), chapter 7; transport and two-film chapters not read in detail

**Objective.** Build equation-oriented, rate-based unit models and a thermodynamic sub-model for MEA CO2 capture in IDAES, validate them against pilot data, and optimise a reference plant at part load.

**Tools.**
- IDAES (version: not stated): Platform for the column, exchanger, reboiler and condenser models and the plant-wide optimisation.
- IPOPT (version: not stated): Solved the discretised packed-bed equations.
- Parmest (Pyomo) (version: not stated): Regressed thermodynamic parameters from experimental data.

**How the study was built.**
1. Regress standard-state and ion-pair/water interaction parameters from selected vapour-liquid equilibrium and heat-of-absorption data before building the columns.
2. Screen published binary parameter sets with thermodynamic consistency tests before adopting one.
3. Discretise each packed bed along its height and solve the differential-algebraic system simultaneously.
4. Initialise in stages: mass balances first, then switch on mass transfer and then heat transfer with continuation parameters.
5. Fit exchanger heat-transfer parameters on one subset of pilot runs and validate on the rest.
6. Use the validated unit models for steady-state plant-wide optimisation of part load and variable capture.

**Modelling choices.**
- Vapour-phase property model: Second-virial-coefficient truncated virial equation, chosen as single-root and adequate at low to moderate pressure.
- Liquid-phase property model: Symmetric electrolyte-NRTL with a reformulated parameter structure to remove a singularity when ions are absent.
- Reaction set: Two reversible reactions represent CO2-loaded MEA chemistry, following Morgan et al. (2017).
- Mesh: Pyomo DAE finite difference with 20 finite elements for the packed bed model.

**Tool chain.** Parmest regression feeds the property package; property, transport and hydraulic sub-models feed IDAES unit models; those are assembled into the plant model solved and optimised with IPOPT.

**Validation (experiment).** Absorber capture compared with NCCC pilot runs (seven cases in the table; the author cites a largest deviation of 4% of CO2 capture against gas-side data), temperature profiles against NCCC and TCM 2015 baseline data (rich loading absolute percentage deviation 4.1% for the TCM run), and plate exchanger duty with 4% error.

**Sensitivity or uncertainty.** None reported in the parts read.

**Limitations the authors state.**
- The explicit two-film (second generation) column model still has numerical problems that limit industrial use.
- Measurement and model uncertainty were not included in the validation comparison.
- Validation of the stage-wise column with dynamic data is left to future work.

**Reusable lesson (compiler's).** In an equation-oriented model, design the initialisation sequence as part of the model, and report which data were used for fitting and which for validation.

**Caveats.** The text states a largest absorber deviation of 4% of CO2 capture against gas-side data, while Table 18 lists case 5 as 67.60 predicted against 59.03 gas-side (58.89 liquid-side); how the 4% was calculated is not stated there. IDAES version not stated.

### Evaluation of an Open-source Chemical Process Simulator Using a Plant-wide Oil and Gas Separation Plant Flowsheet Model as Basis

`andreasen-2022-dwsim-vs-hysys-separation` · Anders Andreasen · 2022 · journal · Periodica Polytechnica Chemical Engineering 66(3), 503-511

[Open copy read](https://pp.bme.hu/ch/article/download/19678/9410) · [DOI](https://doi.org/10.3311/PPch.19678) · read: whole paper

**Objective.** Rebuild a published HYSYS oil and gas separation plant model in DWSIM and compare the two at one operating point and over randomly sampled conditions.

**Tools.**
- DWSIM (version: v6.7.0): Rebuilt plant-wide flowsheet.
- Aspen HYSYS (version: v11): Reference commercial simulator.
- Python wrapper with Latin hypercube sampling (version: not stated): Ran the same sampling plan in both simulators.

**How the study was built.**
1. Align thermodynamic options to what both tools support before comparing, changing the reference setup if needed.
2. Enter the same externally estimated pseudo-component properties in both models instead of relying on DWSIM's built-in estimation.
3. Compare fluid characterisation and phase envelope first, then product streams, driver duties, compressor temperatures and exchanger duties.
4. Check that recycle mass-balance errors are small enough not to explain differences.
5. Run a Latin hypercube parametric study over 10 independent variables and report unconverged cases.

**Modelling choices.**
- Equation of state: Peng-Robinson, with liquid density and departure functions from the equation of state.
- Heavy end: Pseudo-components specified by molecular weight and liquid density, with critical properties and acentric factor estimated by Twu methods.

**Tool chain.** A Python wrapper drives both simulators with the same sampling plan; results are compared statistically.

**Validation (code-to-code).** Against HYSYS only. Single point: differences typically below 1%; two exchangers (20-HA-03 and 25-HA-01) differ by -5.8% and -3.9% (30 kW and 24 kW). The paper explains the first by its very small temperature difference and says the same of 25-HA-02. Parametric study: 9 of 100 samples did not converge in DWSIM; R-squared at least 0.99 for liquid flow, power and Reid vapour pressure.

**Sensitivity or uncertainty.** 100 Latin hypercube samples over 10 variables, 91 converged.

**Limitations the authors state.**
- DWSIM solved only 91% of the defined parametric cases.
- The author suggests possible slight instability in phase-split calculation, needing further study.

**Reusable lesson (compiler's).** A fair code-to-code benchmark needs matched property options and component data, and should report non-converged and rerun cases as results.

**Caveats.** Code-to-code agreement is not plant accuracy; no measured data. Some samples with unexpected deviations were manually re-run, which the reader should weigh.

### Investigation of Co-Current and Counter-Current Multiphase Flow in Upstream Drilling and Production Applications

`fleifel-2025-olga-well-multiphase` · Hazem Fleifel · 2025 · phd-thesis · Louisiana State University

[Open copy read](https://repository.lsu.edu/cgi/viewcontent.cgi?params=/context/gradschool_dissertations/article/8030/&path_info=Hazem_Fleifel_Dissertation_Final.pdf) · read: abstract, chapter 2 methodology and results (to the small-scale experiments), chapter 3 equations and data fit, section 3.7 and chapter 4

**Objective.** Use transient 1-D simulation, with small-scale visual experiments, to study gas removal during bullheading well kill and the operating window of liquid-assisted gas lift.

**Tools.**
- OLGA (version: not stated (manual cited as 2020)): Transient multiphase simulation of both well operations.

**How the study was built.**
1. Reduce the real annulus-tubing well to two vertical pipes joined by a near-lossless check valve, which also stabilises the numerics.
2. Set geometry, fluids, back pressure and thermal boundary conditions from a published large-scale experiment.
3. History-match pressure traces from two shallow-well test cases by tuning pipe roughness and valve discharge coefficient.
4. Hold the fitted parameters fixed when extrapolating to other shallow and deep well scenarios.
5. Sweep gas and liquid rates and plot maximum injection pressure and average holdup as contour maps.
6. Probe an unexpected simulated trend with a dimensionally scaled small-scale experiment.

**Modelling choices.**
- Grid: 402 cells for the bullheading well: 200 each in annulus and tubing and 2 for the check valve.
- Matched parameters: Roughness 0.00198 in (0.05 mm) and valve discharge coefficient 0.289.
- Gas density: Peng-Robinson equation of state (as described in chapter 3).
- Definition of a data fit: Matching pressure histories at several locations for given rates.

**Tool chain.** Published large-scale data set the simulation geometry; the simulated trend motivates a small-scale air-water experiment; in the gas-lift part, history-matched parameters feed scenario sweeps.

**Validation (experiment).** Bullheading: the large-scale experiments (4 points) show gas removal rising monotonically with liquid rate, whereas simulation shows an up-down-up trend; small-scale air-water tube tests (6 ft, 1 in) show the up-down-up trend qualitatively. Gas lift: two shallow-well cases history-matched (figures only).

**Sensitivity or uncertainty.** Wide sweeps of gas and liquid injection rates for shallow and deep wells.

**Limitations the authors state.**
- The gas-lift study ignores the reservoir.
- Further large-scale experiments with other fluids, especially non-Newtonian drilling fluids, are recommended.

**Reusable lesson (compiler's).** State separately what the simulator matched, what it contradicted and what was only checked qualitatively at another scale.

**Caveats.** The Chapter 4 conclusions say the 1-D simulation results fit the large-scale experiments successfully, whereas section 2.5 says the experiments (four points) seem to show gas removal efficiency rising monotonically while the simulation shows an up-down-up trend. The small-scale air-water test is compared with the simulated behaviour only by the shape of the trend. Section 3.4.2 prints vector-form conservation equations that include species-diffusion and reaction-heat terms, while section 2.4 prints one-dimensional phase balances. OLGA version not stated.

## Method guidance and model evaluation

### Experimental methods in chemical engineering - Validation of steady-state simulation

`brucel-2025-steady-state-simulation-validation` · Caroline Brucel, Emilie Thibault, Gregory Scott Patience, Paul R. Stuart · 2025 · journal · Canadian Journal of Chemical Engineering (CC BY; Polytechnique Montreal repository copy)

[Open copy read](https://publications.polymtl.ca/62512/1/2025_Brucel_Experimental_methods_chemical_engineeringValidation_steadystate.pdf) · [DOI](https://doi.org/10.1002/cjce.25601) · read: abstract, parts of the theory section (process data, reconciliation, technique classification), the Kraft mill case study and conclusions; two-column layout

**Objective.** Set out how to validate steady-state simulations against plant data and operator expectations, illustrated on a Kraft pulp mill washing department.

**Tools.**
- CADSIM Plus (version: 3.4 (as cited in the reference list)): Case-study steady-state simulation of the washing department.
- EXPLORE (CanmetENERGY) (version: 2.0 (as cited in the reference list)): Cleaned one year of plant data.

**How the study was built.**
1. Remove errors, shutdowns and unsteady periods from historical data before using it.
2. First verify with operators that major equipment is present and correctly connected.
3. Run informal (face) validation by consulting several operators one at a time on whether the model is realistic.
4. Follow with sensitivity analysis (one-at-a-time, then multi-variable) as formal validation of how inputs and parameters move the outputs.
5. Aim for simulated values within one standard deviation of measurement variability.

**Modelling choices.**
- Data treatment: Ten-minute averages over one year of operation.
- Operating regimes modelled: Most common regime (mode) and a best-performance stable period.

**Tool chain.** Cleaned historian data set the inputs and the comparison statistics; expert feedback and sensitivity runs drive model corrections.

**Validation (plant-data).** Washing department case: five variables compared; authors report all simulated values within one standard deviation of the treated data after validation. An error in a knotter parameter was found during informal validation.

**Sensitivity or uncertainty.** One-at-a-time then multi-variable analysis as the formal validation step.

**Limitations the authors state.**
- Measurements covered only part of the flowsheet (24 measurements for 95 streams), so informal validation was needed.
- Weekly weighed knotter reject data are less reliable than the frequent averaged measurements.

**Reusable lesson (compiler's).** Agree the acceptance band from measured variability before tuning, and report separately the data used to correct the model and data held back to test it.

**Caveats.** Simulation results that fell outside expected ranges (treated data and expert ranges) led to model modifications, and the final values are judged against the treated data; no separate hold-out data set is described. Software versions appear only in the reference list.
