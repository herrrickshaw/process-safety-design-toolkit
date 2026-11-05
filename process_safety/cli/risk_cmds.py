"""Risk-study commands: HAZOP skeleton, the QRA workflow, the JSON-driven study tools."""
from __future__ import annotations

import json
import os
import shutil
import sys

from .. import hazop
from .registry import command, emit

_PKG = os.path.dirname(os.path.dirname(__file__))


@command("hazop-csv", "write a HAZOP worksheet skeleton (CSV, opens in Excel)")
class HazopCsv:
    @staticmethod
    def add_arguments(hz):
        hz.add_argument("--node", required=True); hz.add_argument("--intent", default="")
        hz.add_argument("--params", nargs="*"); hz.add_argument("--out", required=True)

    @staticmethod
    def run(a, p):
        n = hazop.to_csv(hazop.generate(a.node, a.intent, a.params), a.out)
        emit({"rows": n, "file": a.out})


@command("qra", "quantitative risk assessment workflow (HAZID -> frequency -> consequence -> risk -> ALARP -> mitigation)")
class Qra:
    @staticmethod
    def add_arguments(q):
        q.add_argument("action", choices=["example", "validate", "run", "hazid", "buildings", "emergency"])
        q.add_argument("study", nargs="?", help="study JSON (see process_safety/qra/examples/lpg_terminal.json)")
        q.add_argument("--out", default="qra_out", help="output folder (run/hazid) or file (example)")
        q.add_argument("--sample", type=int, help="run only N LOC scenarios on a 2x coarser grid and project the full run time")
        q.add_argument("--grid-step", type=float, help="override grid step, m")
        q.add_argument("--no-mitigation", action="store_true")
        q.add_argument("--no-xlsx", action="store_true")
        q.add_argument("--quiet", action="store_true", help="no progress bar")

    @staticmethod
    def run(a, p):
        from ..qra import frequency as qfreq, hazid as qhazid, report as qreport, study as qstudy, validate as qvalidate
        ex = os.path.join(_PKG, "qra", "examples", "lpg_terminal.json")
        if a.action == "example":
            dst = a.out if a.out.endswith(".json") else "qra_study.json"
            shutil.copy(ex, dst)
            print(f"wrote {dst} - edit it, then: python3 -m process_safety qra validate {dst}")
            return 0
        if not a.study:
            print("give a study JSON (or run: python3 -m process_safety qra example)", file=sys.stderr)
            return 2
        st = qstudy.load(a.study)
        ds = qfreq.load_dataset(st.get("frequency_dataset"))
        if a.action == "validate":
            rep = qvalidate.inputs(st, ds)
            sc = qstudy.build_scenarios(st, ds) if rep else []
            emit({**rep.as_dict(), "loc_scenarios": len(sc), "total_loc_frequency_per_yr": sum(x["frequency_per_yr"] for x in sc)})
            return 0 if rep else 1
        if a.action == "hazid":
            os.makedirs(a.out, exist_ok=True)
            n1 = qhazid.write_csv(qhazid.hazid_register(st["sections"]), os.path.join(a.out, "hazid_register.csv"), qhazid.HAZID_COLUMNS)
            n2 = qhazid.write_csv(qhazid.hazop_rows(st["sections"]), os.path.join(a.out, "hazop_worksheet.csv"))
            sc = qstudy.build_scenarios(st, ds)
            qreport._csv(os.path.join(a.out, "loc_register.csv"), [{k: x[k] for k in ("id", "section", "equipment", "hole", "hole_mm", "instantaneous", "frequency_per_yr", "basis", "source")} for x in sc])
            print(f"{n1} HAZID rows, {n2} HAZOP rows, {len(sc)} LOC scenarios -> {a.out}/")
            return 0
        from ..qra import buildings as qbuild, emergency as qemerg
        out = qstudy.run(st, sample=a.sample, grid_step=a.grid_step, progress=not a.quiet, mitigate=not a.no_mitigation and a.action == "run",
                         dataset=ds)
        if a.action == "buildings":
            res = qbuild.assess(out, st, progress=not a.quiet)
            os.makedirs(a.out, exist_ok=True)
            emit({"buildings": res["buildings"], "files": qbuild.write(res, os.path.join(a.out, "qra"))})
            return 0
        if a.action == "emergency":
            res = qemerg.assess(out, st)
            os.makedirs(a.out, exist_ok=True)
            emit({"site_emergency_level": res["site_level"], "mcls": res["mcls"], "files": qemerg.write(res, st, os.path.join(a.out, "qra"))})
            return 0
        files = qreport.write_all(out, st, a.out, xlsx=not a.no_xlsx)
        if st.get("buildings"):
            files["buildings"] = qbuild.write(qbuild.assess(out, st, progress=not a.quiet), os.path.join(a.out, "qra"))[1]
        files["emergency"] = qemerg.write(qemerg.assess(out, st), st, os.path.join(a.out, "qra"))[2]
        emit(qstudy.summary(out))
        print("\n".join(f"{k}: {v}" for k, v in files.items()), file=sys.stderr)
        return 1 if out["validation_results"]["errors"] else 0


@command("tool", "JSON-driven study tools: bowtie, sif, fg, thermal, atex, ram, shutdown, recs, lngcost, pha (see process_safety/tools.py)")
class Tool:
    @staticmethod
    def add_arguments(tl):
        tl.add_argument("name", choices=["bowtie", "sif", "fg", "thermal", "atex", "ram", "shutdown", "recs", "lngcost", "pha", "example"])
        tl.add_argument("input", nargs="?", help="input JSON (tool example <name> copies a worked example)")
        tl.add_argument("--out", default="tool_out")
        tl.add_argument("--quiet", action="store_true")

    @staticmethod
    def run(a, p):
        from ..tools import run_tool
        exdir = os.path.join(_PKG, "examples")
        if a.name == "example":
            if not a.input:
                print("tool example <bowtie|sif|fg|thermal|atex|ram|shutdown|recs|lngcost|pha>", file=sys.stderr)
                return 2
            shutil.copy(os.path.join(exdir, f"{a.input}.json"), f"{a.input}.json")
            print(f"wrote {a.input}.json - run: python3 -m process_safety tool {a.input} {a.input}.json")
            return 0
        with open(a.input or os.path.join(exdir, f"{a.name}.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        summ = run_tool(a.name, data, a.out, progress=not a.quiet)
        emit(summ)
        return 1 if any(str(c).startswith("FAIL") for c in summ.get("checks", [])) else 0
