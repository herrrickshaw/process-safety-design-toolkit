"""Rules that tag a bibliographic record with the modelling tools and study types its title and abstract name.

The tags say what the text mentions, not that the work used the tool or did the study well. Tool names that are also ordinary
words or names in other fields (ALOHA, PHAST, FDS, Fluent, OLGA, SLAB, EFFECTS) need a second, context word.
"""
from __future__ import annotations

import re

_I = re.IGNORECASE
_HAZ = r"releas|dispers|toxic|hazard|consequence|explosion|\bfire|leak|\brisk"
_CFD = r"\bCFD\b|computational fluid|simulat|numerical"


def _r(pattern, flags=_I):
    return re.compile(pattern, flags)


# key: (label, family, pattern, context pattern or None)
TOOLS = {
    "aspen-plus": ("Aspen Plus", "process-simulator", _r(r"aspen\s?plus(?![\s-]*dynamics)"), None),
    "aspen-hysys": ("Aspen HYSYS", "process-simulator", _r(r"\b(aspen\s?)?hysys\b"), None),
    "aspen-dynamics": ("Aspen Plus Dynamics", "process-simulator", _r(r"aspen\s?(plus\s?)?dynamics"), None),
    "unisim": ("UniSim", "process-simulator", _r(r"\bunisim\b"), None),
    "gproms": ("gPROMS", "process-simulator", _r(r"\bgproms\b"), None),
    "proii": ("PRO/II", "process-simulator", _r(r"\bPRO[/ ]II\b", 0), _r(r"simulat|process|distill")),
    "chemcad": ("CHEMCAD", "process-simulator", _r(r"\bchemcad\b"), None),
    "dwsim": ("DWSIM", "process-simulator", _r(r"\bdwsim\b"), None),
    "idaes": ("IDAES", "process-simulator", _r(r"\bIDAES\b", 0), None),
    "neqsim": ("NeqSim", "process-simulator", _r(r"\bneqsim\b"), None),
    "biosteam": ("BioSTEAM", "process-simulator", _r(r"\bbiosteam\b"), None),
    "promax": ("ProMax", "process-simulator", _r(r"\bProMax\b", 0), _r(r"simulat|gas|amine|process")),
    "superpro": ("SuperPro Designer", "process-simulator", _r(r"\bsuperpro\b"), None),
    "olga": ("OLGA", "process-simulator", _r(r"\bOLGA\b", 0), _r(r"transient|multiphase|pipeline|flow assurance|wellbore|blowout")),
    "modelica": ("Modelica / Dymola", "process-simulator", _r(r"\bmodelica\b|\bdymola\b"), None),
    "phast": ("PHAST", "consequence-risk", _r(r"\bPHAST\b|\bPhast\b", 0), _r(_HAZ)),
    "safeti": ("Safeti", "consequence-risk", _r(r"\bSAFETI\b|\bSafeti\b", 0), None),
    "aloha": ("ALOHA", "consequence-risk", _r(r"\bALOHA\b", 0), _r(r"toxic|dispers|chemical|ammonia|chlorine|vapou?r|areal locations")),
    "effects-riskcurves": ("TNO EFFECTS / RISKCURVES", "consequence-risk",
                           _r(r"\bTNO[- ]EFFECTS\b|\bEFFECTS (software|code|program)|\bRISKCURVES\b", 0), _r(_HAZ)),
    "hyram": ("HyRAM", "consequence-risk", _r(r"\bHyRAM"), None),
    "dense-gas-codes": ("DEGADIS / SLAB / HEGADAS / HGSYSTEM", "consequence-risk",
                        _r(r"\bDEGADIS\b|\bHEGADAS\b|\bHGSYSTEM\b|\bSLAB (model|code|dense|dispersion)", 0), None),
    "aermod": ("AERMOD", "consequence-risk", _r(r"\bAERMOD\b", 0), None),
    "flacs": ("FLACS", "cfd", _r(r"\bFLACS"), _r(r"dispers|explosion|gas|fire|CFD")),
    "fds": ("Fire Dynamics Simulator", "cfd", _r(r"fire dynamics simulator|\bFDS\b"), _r(r"\bfire|smoke")),
    "kfx": ("KFX", "cfd", _r(r"\bKFX\b|Kameleon", 0), _r(r"fire|dispers|gas")),
    "firefoam": ("FireFOAM", "cfd", _r(r"\bfirefoam\b"), None),
    "openfoam": ("OpenFOAM", "cfd", _r(r"\bopenfoam\b"), None),
    "fluent": ("ANSYS Fluent", "cfd", _r(r"\bFluent\b|\bFLUENT\b", 0), _r(_CFD)),
    "cfx": ("ANSYS CFX", "cfd", _r(r"\bCFX\b", 0), _r(_CFD)),
    "blowdown-codes": ("Blowdown codes (HydDown, VessFire, BLOWSIM)", "consequence-risk", _r(r"\bhyddown\b|\bvessfire\b|\bblowsim\b"), None),
    "structural-codes": ("LS-DYNA / Autodyn / Abaqus", "structural", _r(r"\bLS-?DYNA\b|\bautodyn\b|\babaqus\b"), None),
    "matlab": ("MATLAB / Simulink", "general", _r(r"\bMATLAB\b|\bSimulink\b"), None),
}

# key: (label, pattern, True if it is a safety study)
STUDIES = {
    "hazop-pha": ("HAZOP and hazard identification",
                  _r(r"\bHAZOP\b|hazard and operability|hazard identification|process hazards? analys"), True),
    "lopa-sil": ("LOPA, SIL and instrumented protection",
                 _r(r"\bLOPA\b|layers? of protection|safety instrumented|safety integrity|functional safety"), True),
    "qra": ("Quantitative and probabilistic risk assessment",
            _r(r"\bQRA\b|quantitative risk|probabilistic risk|individual risk|societal risk|bayesian network|fault tree|event tree|"
               r"bow[- ]?tie"), True),
    "dispersion": ("Release and dispersion", _r(r"dispersion (model|simulat|of (gas|vapou?r|toxic|hydrogen|ammonia|carbon|CO2|LNG|methane|chlorine))|"
                                                r"(gas|toxic|vapou?r|hydrogen|ammonia|CO2|LNG|chlorine) (cloud )?(dispersion|release|leak)|"
                                                r"accidental release|toxic release"), True),
    "fire": ("Fire", _r(r"jet fires?\b|pool fires?\b|flash fires?\b|fireballs?\b|fire (safety|hazard|risk|scenario|simulation|model|spread)|"
                        r"thermal radiation"), True),
    "explosion": ("Explosion", _r(r"explosion|deflagration|deflagration-to-detonation|detonation (of|in) |\bBLEVE\b"), True),
    "relief-blowdown": ("Relief, flare, depressuring and blowdown",
                        _r(r"pressure[- ]relief|relief (valve|system|sizing|load|device|vent)|flare (system|network|load|design|header)|"
                           r"\bblow[- ]?down\b|depressuri[sz]|overpressure protection|emergency vent"), True),
    "reaction-hazard": ("Runaway reaction and thermal hazard",
                        _r(r"runaway reaction|thermal runaway|reaction hazard|reactive hazard"), True),
    "inherent-safety": ("Inherently safer design", _r(r"inherent(ly)?[- ]safe"), True),
    "domino-structural": ("Escalation, domino and structural response",
                          _r(r"domino effect|escalation|structural (response|integrity) .{0,40}(fire|blast|explosion)|"
                             r"(fire|blast|explosion) .{0,30}structural"), True),
    "operability-ots": ("Dynamic operability, start-up and operator training",
                        _r(r"operator training|abnormal situation|(start-?up|shut-?down) .{0,40}simulat|dynamic simulation|controllability"), False),
    "fault-diagnosis": ("Fault detection and diagnosis", _r(r"fault (detection|diagnosis)|anomaly detection"), False),
    "data-driven": ("Surrogates, machine learning, digital twins and language models",
                    _r(r"digital twin|surrogate model|machine[- ]learning|deep learning|neural network|large language model"), False),
    "design-tea": ("Process design, optimisation and techno-economics",
                   _r(r"techno-?economic|process design|process optimi[sz]ation|heat integration|optimi[sz]ation of .{0,40}process"), False),
    "validation": ("Model validation, comparison and uncertainty",
                   _r(r"validat|benchmark|compar(ed|ison) (with|to|against) .{0,40}(experiment|plant|measure)|uncertainty (analysis|quantification)|"
                      r"sensitivity analysis"), False),
}

DOMAIN = _r(r"chemical|refiner|petrochemic|petroleum|\boil\b|\bgas(es)?\b|\bLNG\b|\bLPG\b|hydrogen|ammonia|offshore|pipeline|reactor|"
            r"distillation|process (plant|industr|system|safety|simulat)|\bCO2\b|carbon dioxide|biofuel|biorefin|biomass|bioethanol|"
            r"battery energy|\bdust\b|hydrocarbon|methane|propane|methanol|solvent|storage tank|industrial (plant|facilit)")
MODELLING = _r(r"simulat|\bmodel|\bCFD\b|numerical|software|computational")
OFF_TOPIC = _r(r"clinical|patients?\b|covid|tumou?r|cancer|epidemi|slotted aloha|wireless|LoRa(WAN)?\b|stock market|MS COCO|"
               r"coco dataset|nuclear reactor core|supernova|galax")


def tools_in(text: str) -> list[str]:
    return [k for k, (_, _, pat, ctx) in TOOLS.items() if pat.search(text) and (ctx is None or ctx.search(text))]


def studies_in(text: str) -> list[str]:
    return [k for k, (_, pat, _) in STUDIES.items() if pat.search(text)]


def include(text: str) -> bool:
    """A record is mapped if it names a modelling tool in a process setting, or is a modelled safety study in a process setting."""
    if OFF_TOPIC.search(text):
        return False
    tools = [t for t in tools_in(text) if TOOLS[t][1] != "general"]
    studies = studies_in(text)
    safety = any(STUDIES[s][2] for s in studies)
    process_tool = any(TOOLS[t][1] in ("process-simulator", "consequence-risk") for t in tools)
    if tools and (process_tool or (DOMAIN.search(text) and studies)):
        return True
    return bool(safety and DOMAIN.search(text) and MODELLING.search(text))
