"""Harvest bibliographic records on process-simulation and safety-modelling studies from open catalogue APIs.

Usage: python3 scripts/harvest_modelling_literature.py RAW_DIR [--source NAME ...]

Raw responses are cached in RAW_DIR (keep it outside the repository: it holds abstracts, which are not republished).
A rerun reads the cache and only requests what is missing. One request per second per service, generic User-Agent, no API keys.
A service that answers 401, 403 or 429 is dropped for the rest of the run; nothing is retried by another route.
Standard library only.
"""
import argparse
import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "literature-map/1.0 (research indexing script)"

# (query id, phrase groups). Every group must appear; each group is one phrase.
QUERIES = [
    # simulators x safety and design studies
    ("hysys-safety", ["Aspen HYSYS", "safety"]), ("aspenplus-safety", ["Aspen Plus", "safety"]),
    ("hysys-dynamic", ["HYSYS", "dynamic simulation"]), ("aspendyn-control", ["Aspen Plus Dynamics", "control"]),
    ("unisim", ["UniSim", "simulation"]), ("gproms", ["gPROMS", "model"]), ("proii", ["PRO/II", "simulation"]),
    ("chemcad", ["ChemCAD", "simulation"]), ("dwsim", ["DWSIM", "simulation"]), ("idaes", ["IDAES", "process"]),
    ("neqsim", ["NeqSim", "process"]), ("biosteam", ["BioSTEAM", "techno-economic"]), ("promax", ["ProMax", "simulation gas"]),
    ("modelica-process", ["Modelica", "chemical process"]), ("olga", ["OLGA", "transient multiphase"]),
    ("thermo-package", ["thermodynamic property package selection", "process simulation"]),
    ("sim-validation", ["process simulation", "validation plant data"]),
    # simulator-assisted hazard studies
    ("sim-hazop", ["dynamic simulation", "HAZOP"]), ("auto-hazop", ["automated HAZOP", "model"]),
    ("sim-lopa", ["process simulation", "layer of protection analysis"]), ("sil-sim", ["safety instrumented system", "dynamic simulation"]),
    ("inherent-sim", ["inherent safety index", "process simulation"]), ("inherent-opt", ["inherently safer design", "process simulator"]),
    ("relief-dyn", ["pressure relief", "dynamic simulation"]), ("flare-dyn", ["flare system", "dynamic simulation"]),
    ("blowdown", ["blowdown", "depressurisation model validation"]), ("blowdown-us", ["depressurization", "low temperature vessel simulation"]),
    ("runaway", ["runaway reaction", "simulation safety"]), ("ots", ["operator training simulator", "process safety"]),
    ("twin-safety", ["digital twin", "process safety"]), ("fdd-sim", ["fault detection", "chemical process simulator data"]),
    ("llm-safety", ["large language model", "process hazard analysis"]),
    # consequence, fire, explosion and risk tools
    ("phast", ["PHAST", "consequence analysis"]), ("safeti", ["Safeti", "quantitative risk assessment"]),
    ("aloha", ["ALOHA", "toxic release dispersion"]), ("effects", ["TNO EFFECTS", "consequence modelling"]),
    ("flacs-disp", ["FLACS", "dispersion"]), ("flacs-expl", ["FLACS", "explosion"]), ("fds", ["Fire Dynamics Simulator", "validation"]),
    ("fds-industrial", ["Fire Dynamics Simulator", "industrial facility"]), ("kfx", ["KFX", "fire simulation"]),
    ("firefoam", ["FireFOAM", "fire"]), ("openfoam-disp", ["OpenFOAM", "gas dispersion"]), ("openfoam-expl", ["OpenFOAM", "gas explosion"]),
    ("fluent-disp", ["ANSYS Fluent", "gas leak dispersion"]), ("fluent-fire", ["ANSYS Fluent", "jet fire"]),
    ("cfx", ["ANSYS CFX", "release dispersion"]), ("hyram", ["HyRAM", "hydrogen risk"]), ("degadis", ["dense gas dispersion model", "evaluation"]),
    ("model-eval", ["model evaluation protocol", "gas dispersion"]), ("model-uncert", ["consequence modelling", "uncertainty"]),
    ("qra-method", ["quantitative risk assessment", "process plant simulation"]), ("surrogate", ["surrogate model", "gas dispersion CFD"]),
    ("ml-consequence", ["machine learning", "consequence prediction release"]), ("domino", ["domino effect", "simulation escalation"]),
    ("bayes", ["Bayesian network", "process safety risk"]), ("dust-cfd", ["dust explosion", "CFD simulation"]),
    ("vce-cfd", ["vapour cloud explosion", "CFD"]), ("bleve", ["BLEVE", "numerical simulation"]),
    ("layout", ["facility layout", "consequence simulation"]), ("structural-fire", ["jet fire", "finite element structural response"]),
    # sector studies
    ("lng-sim", ["LNG liquefaction", "process simulation"]), ("lng-safety", ["LNG release", "CFD safety"]),
    ("h2-safety", ["hydrogen leak", "CFD safety study"]), ("nh3-safety", ["ammonia release", "dispersion modelling"]),
    ("co2-release", ["CO2 pipeline release", "dispersion modelling"]), ("co2-capture-sim", ["CO2 capture", "dynamic process simulation"]),
    ("refinery-sim", ["refinery", "process simulation HYSYS"]), ("biorefinery-sim", ["biorefinery", "Aspen Plus simulation techno-economic"]),
    ("battery-fire", ["battery energy storage", "gas explosion CFD"]), ("offshore-qra", ["offshore platform", "fire explosion CFD risk"]),
]


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _q(s):
    return urllib.parse.quote(s, safe="")


def urls_openalex(groups, thesis):
    expr = " AND ".join(f'"{g}"' for g in groups).replace(",", " ")
    flt = f"title_and_abstract.search:{expr}" + (",type:dissertation" if thesis else "")
    sel = "id,doi,title,publication_year,type,open_access,primary_location,cited_by_count,abstract_inverted_index,authorships,language"
    return f"https://api.openalex.org/works?filter={_q(flt)}&per-page={50 if thesis else 100}&select={sel}"


def urls_crossref(groups, thesis):
    flt = "&filter=type:dissertation" if thesis else ""
    sel = "DOI,title,author,issued,type,container-title,abstract,publisher,is-referenced-by-count,URL"
    return f"https://api.crossref.org/works?query.bibliographic={_q(' '.join(groups))}&rows=40{flt}&select={sel}"


def urls_doaj(groups, thesis):
    expr = " AND ".join(f'"{g}"' for g in groups).replace("/", " ")
    return f"https://doaj.org/api/search/articles/{_q(expr)}?pageSize=40"


def urls_hal(groups, thesis):
    expr = " AND ".join(f'text:"{g}"' for g in groups)
    fl = "halId_s,doiId_s,title_s,abstract_s,producedDateY_i,uri_s,authFullName_s,fileMain_s,docType_s,language_s"
    flt = "&fq=" + _q("docType_s:(THESE OR MEM OR HDR)") if thesis else ""
    return f"https://api.archives-ouvertes.fr/search/?q={_q(expr)}{flt}&fl={fl}&rows=40&wt=json"


def urls_datacite(groups, thesis):
    expr = " AND ".join(f'"{g}"' for g in groups)
    return f"https://api.datacite.org/dois?query={_q(expr)}&resource-type-id=dissertation&page%5Bsize%5D=40"


def urls_osti(groups, thesis):
    return f"https://www.osti.gov/api/v1/records?q={_q(' AND '.join(chr(34) + g + chr(34) for g in groups))}&rows=30"


# name -> (url builder, the thesis-only variants to request)
SOURCES = {
    "openalex": (urls_openalex, (True, False)),
    "crossref": (urls_crossref, (True, False)),
    "doaj": (urls_doaj, (False,)),
    "hal": (urls_hal, (True, False)),
    "datacite": (urls_datacite, (True,)),
    "osti": (urls_osti, (False,)),
}


def run_source(name, raw_dir, log):
    build, variants = SOURCES[name]
    done = failed = 0
    for thesis in variants:
        for qid, groups in QUERIES:
            url = build(groups, thesis)
            path = os.path.join(raw_dir, f"{name}__{qid}__{'thesis' if thesis else 'all'}.json")
            if os.path.exists(path):
                done += 1
                continue
            try:
                body = _get(url)
            except urllib.error.HTTPError as err:
                log.append((name, qid, err.code))
                if err.code in (401, 403, 429):
                    log.append((name, "STOPPED", err.code))
                    print(f"{name}: stopped on HTTP {err.code} after {done} queries")
                    return
                failed += 1
            except Exception as err:  # network or parse error: record and go on
                log.append((name, qid, type(err).__name__))
                failed += 1
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump({"query_id": qid, "groups": groups, "thesis_only": thesis, "source": name, "url": url,
                               "fetched": time.strftime("%Y-%m-%d"), "sha256": hashlib.sha256(url.encode()).hexdigest(), "body": body}, fh)
                done += 1
            time.sleep(1.1)
    print(f"{name}: {done} cached, {failed} failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir")
    ap.add_argument("--source", action="append", choices=sorted(SOURCES))
    a = ap.parse_args()
    os.makedirs(a.raw_dir, exist_ok=True)
    log = []
    threads = [threading.Thread(target=run_source, args=(n, a.raw_dir, log)) for n in (a.source or SOURCES)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with open(os.path.join(a.raw_dir, "_harvest_log.json"), "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=1)


if __name__ == "__main__":
    main()
