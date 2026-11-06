"""Input templates and running a filled template."""
from __future__ import annotations

import json
import sys

from .. import templating
from .registry import REGISTRY, command, emit


@command("template", "write a fill-in input template for a command (JSON or CSV), with units for SI or US customary")
class Template:
    @staticmethod
    def add_arguments(t):
        t.add_argument("name", nargs="?", help="command name (omit with --all or --list)")
        t.add_argument("--system", choices=("si", "us"), default=None, help="units written into the template (default: the global --units)")
        t.add_argument("--format", choices=("json", "csv"), default="json")
        t.add_argument("--all", action="store_true", help="every command as one CSV table (SI and US columns)")
        t.add_argument("--list", action="store_true", help="list the command names that have templates")

    @staticmethod
    def run(a, p):
        from .. import units
        if a.list:
            print("\n".join(REGISTRY))
            return 0
        if a.all:
            sys.stdout.write(templating.csv_all())
            return 0
        if not a.name or a.name not in REGISTRY:
            p.error("give a command name (python -m process_safety template --list)")
        system = a.system or units.active_system()
        if a.format == "csv":
            import csv
            w = csv.writer(sys.stdout, lineterminator="\n")
            rows = templating.describe(a.name, system)
            w.writerow(["parameter", "flag", "required", "type", "unit", "default", "hard_min", "hard_max", "soft_min", "soft_max", "help"])
            for r in rows:
                w.writerow([r["name"], r["flag"], "yes" if r["required"] else "", r["type"], r["unit"] or "", "" if r["default"] is None else r["default"],
                            *["" if r[k] is None else r[k] for k in ("hard_min", "hard_max", "soft_min", "soft_max")], r["help"]])
            return 0
        sys.stdout.write(templating.dump(templating.template(a.name, system)))
        return 0


@command("run", "run a filled-in input template (JSON from the template command); its units field sets SI or US")
class Run:
    @staticmethod
    def add_arguments(r):
        r.add_argument("file", help="filled template JSON (or - for stdin)")

    @staticmethod
    def run(a, p):
        from ..__main__ import main
        try:
            filled = json.load(sys.stdin if a.file == "-" else open(a.file, encoding="utf-8"))
            argv = templating.to_argv(filled)
        except (OSError, ValueError, KeyError) as e:
            p.error(str(e))
        return main(argv)


@command("convert", "convert a value between SI and US-customary units (use it to prepare the SI-only JSON tool inputs)")
class Convert:
    units = {"value": "-"}     # the unit comes from the SRC argument, so --units must not rescale the value

    @staticmethod
    def add_arguments(c):
        c.add_argument("value", nargs="?", type=float)
        c.add_argument("src", nargs="?", help="unit of the value, e.g. psig, degF, ft, lb/h")
        c.add_argument("dst", nargs="?", help="unit to convert to, e.g. kPag, degC, m, kg/h")
        c.add_argument("--across-atmosphere", action="store_true",
                       help="convert between a GAUGE and an ABSOLUTE pressure unit (adds or subtracts 101.325 kPa); refused without this flag")
        c.add_argument("--table", action="store_true", help="list every unit, its dimension and the factor to the SI base unit")

    @staticmethod
    def run(a, p):
        from .. import units
        if a.table:
            rows = [{"unit": u.symbol, "dimension": u.dimension, "to_base_factor": u.to_base, "offset": u.offset} for u in units.UNITS.values()]
            emit({"base_units": "m, m2, m3, kg, Pa (gauge or absolute by dimension), K, kg/s, m3/s, kg/m3, ...", "units": rows})
            return 0
        if a.value is None or not a.src or not a.dst:
            p.error("give VALUE SRC DST, e.g. convert 150 psig kPag (or --table)")
        try:
            if a.across_atmosphere:
                g_first = units.unit(a.src).dimension == "pressure_gauge"
                r = (units.gauge_to_abs if g_first else units.abs_to_gauge)(a.value, a.src, a.dst)
            else:
                r = units.convert(a.value, a.src, a.dst)
            emit({"value": a.value, "from": a.src, "to": a.dst, "result": r})
        except units.UnitError as e:
            p.error(str(e))
        return 0
