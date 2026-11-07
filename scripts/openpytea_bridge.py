"""Bridge from this toolkit to OpenPyTEA's equipment-cost correlations (optional, development-time; the package itself stays stdlib only).

OpenPyTEA (MIT, https://github.com/pbtamarona/OpenPyTEA, `pip install openpytea`) holds more than 150 published purchased-cost correlations
(Turton, Seider, Towler & Sinnott, Perry ...) and escalates them with CEPCI. The toolkit ships no unit rates, so this script turns a list
of equipment you size (with the toolkit or anything else) into a `rate_book` that `tool recs` and `tool workflow` can use, or into a plain
cost table.

    python scripts/openpytea_bridge.py list [--category "Pressure vessels"]       correlations, native size unit and valid size range
    python scripts/openpytea_bridge.py cost equipment.json [--out ratebook.json] [--into study.json --study-out new.json] [--csv table.csv]

equipment.json (see templates/openpytea_equipment.example.json):
    {"target_year": 2024, "currency_per_usd": 0.001, "currency": "kUSD",
     "spread": {"min": 0.8, "max": 1.5},                      # YOUR uncertainty around the correlation (required, no default)
     "items": [{"key": "eq_ko_drum", "name": "Flare KO drum", "category": "Pressure vessels", "type": "Horizontal",
                "process_type": "Fluids", "size": 12.5, "size_unit": "m3", "material": "Carbon steel", "num_units": 1}]}
`size_unit` is any unit `python -m process_safety convert --table` knows; it is converted to the unit the correlation uses. Use
"native" to give the number in the correlation's own unit (needed for two-parameter correlations: give a list).

What you get is a published-correlation estimate with OpenPyTEA's default installation factors (erection, piping, instrumentation,
electrical, civil, structural, lagging), in the target year's dollars. It is an AACE Class 4/5 style number, not a quote. Sizes outside
the correlation's stated range are reported (`in_range: false`) because OpenPyTEA extrapolates silently.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from process_safety import units  # noqa: E402

_TOKEN_FIX = [("^", ""), ("Hp", "hp"), ("/hr", "/h"), ("in.", "in"), ("ft3/min", "ft3/min"), ("Btu/hr", "Btu/h")]
_ALIASES = {"m3": "m3", "m2": "m2", "ft3": "ft3", "ft2": "ft2", "gal": "gal", "kW": "kW", "hp": "hp", "kg": "kg", "lb": "lb", "m": "m", "ft": "ft",
            "in": "in", "mm": "mm", "lb/h": "lb/h", "kg/h": "kg/h", "Btu/h": "Btu/h", "gpm": "gpm", "ft3/min": "ft3/min", "m3/s": "m3/s",
            "L/s": "L/s", "gal/min": "gpm", "m2": "m2"}


def native_unit(units_text: str) -> str | None:
    """The unit symbol at the end of a correlation's 'units' text ('volume, m^3' -> 'm3'), or None if it is not a plain known unit."""
    tail = units_text.split(",")[-1].strip()
    for a, b in _TOKEN_FIX:
        tail = tail.replace(a, b)
    return _ALIASES.get(tail)


def _openpytea():
    try:
        import openpytea
        from openpytea import equipment as eq
    except ImportError:
        sys.exit("OpenPyTEA is not installed: pip install openpytea   (optional; only this script needs it)")
    return openpytea, eq


def correlations(category: str | None = None):
    _, eq = _openpytea()
    df = eq.COST_DB_DF
    if category:
        df = df[df["category"].str.lower() == category.lower()]
    return df


def to_native(size, size_unit: str, native_text: str):
    if size_unit == "native":
        return size
    nu = native_unit(native_text)
    if nu is None:
        raise ValueError(f"the correlation's size unit is '{native_text}', which this bridge cannot convert; "
                         f"give the size in that unit with size_unit \"native\"")
    conv = lambda v: units.convert(v, size_unit, nu)  # noqa: E731
    return [conv(v) for v in size] if isinstance(size, (list, tuple)) else conv(size)


def cost_item(item: dict, target_year: int) -> dict:
    openpytea, eq = _openpytea()
    df = eq.COST_DB_DF
    match = df[(df["category"].str.lower() == item["category"].lower()) & (df["type"].str.lower() == item["type"].lower())]
    if match.empty:
        raise ValueError(f"{item['key']}: no correlation for category '{item['category']}', type '{item['type']}' (run: list)")
    row = match.iloc[0]
    if len(match) > 1:
        print(f"warning: {item['key']}: {len(match)} correlations match; using {row['key']} (see `list`)", file=sys.stderr)
    param = to_native(item["size"], item.get("size_unit", "native"), str(row["units"]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        e = eq.Equipment(name=item["name"], param=param, process_type=item.get("process_type", "Fluids"), category=item["category"],
                         type=item["type"], material=item.get("material"), num_units=item.get("num_units", 1), target_year=target_year)
    lo, hi = row["s_lower"], row["s_upper"]
    p = param if not isinstance(param, (list, tuple)) else None
    in_range = None if (p is None or lo != lo or hi != hi) else bool(lo <= p <= hi)
    return {"key": item["key"], "name": item["name"], "correlation": row["key"], "source": str(row["source"]), "native_size": param,
            "native_unit": str(row["units"]), "valid_range": [None if lo != lo else float(lo), None if hi != hi else float(hi)], "in_range": in_range,
            "cost_year": int(row["cost_year"]), "target_year": target_year, "num_units": item.get("num_units", 1),
            "purchased_usd": float(e.purchased_cost), "direct_usd": float(e.direct_cost)}


def build(spec: dict) -> dict:
    for k in ("target_year", "currency_per_usd", "currency", "spread", "items"):
        if k not in spec:
            raise ValueError(f"missing '{k}' (the spread and currency are yours to choose; there is no default)")
    sp = spec["spread"]
    if not (0 < sp["min"] <= 1 <= sp["max"]):
        raise ValueError("spread needs 0 < min <= 1 <= max")
    results, rate_book = [], {}
    for item in spec["items"]:
        r = cost_item(item, spec["target_year"])
        results.append(r)
        per_unit = r["direct_usd"] / r["num_units"] * spec["currency_per_usd"]
        rate_book[item["key"]] = {"unit": f"each installed (OpenPyTEA direct cost, {spec['target_year']} USD, {spec['currency']})",
                                  "rate": {"min": per_unit * sp["min"], "mode": per_unit, "max": per_unit * sp["max"]},
                                  "note": f"{r['correlation']}: {r['source']}; default installation factors; not a quote"
                                          + ("" if r["in_range"] in (True, None) else "; SIZE OUTSIDE THE CORRELATION'S RANGE")}
    return {"currency": spec["currency"], "target_year": spec["target_year"], "items": results, "rate_book": rate_book}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--category")
    c = sub.add_parser("cost")
    c.add_argument("equipment")
    c.add_argument("--out")
    c.add_argument("--csv")
    c.add_argument("--into", help="a `tool recs` / `tool workflow` study JSON whose rate_book gets these entries")
    c.add_argument("--study-out")
    a = ap.parse_args(argv)
    if a.cmd == "list":
        df = correlations(a.category)
        w = csv.writer(sys.stdout, lineterminator="\n")
        w.writerow(["category", "type", "size_unit", "size_unit_known_to_bridge", "valid_min", "valid_max", "cost_year", "source"])
        for _, r in df.iterrows():
            w.writerow([r["category"], r["type"], r["units"], native_unit(str(r["units"])) or "no", r["s_lower"], r["s_upper"], r["cost_year"], r["source"]])
        return 0
    spec = json.load(open(a.equipment, encoding="utf-8"))
    try:
        res = build(spec)
    except (ValueError, KeyError, units.UnitError) as e:
        sys.exit(f"error: {e}")
    out = json.dumps(res, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out + "\n")
    else:
        print(out)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "name", "native_size", "native_unit", "in_range", "purchased_usd", "direct_usd", "source"])
            for r in res["items"]:
                w.writerow([r["key"], r["name"], r["native_size"], r["native_unit"], r["in_range"], round(r["purchased_usd"], 2), round(r["direct_usd"], 2), r["source"]])
    if a.into:
        study = json.load(open(a.into, encoding="utf-8"))
        study.setdefault("rate_book", {}).update(res["rate_book"])
        study["currency"] = res["currency"]
        open(a.study_out or a.into, "w", encoding="utf-8").write(json.dumps(study, indent=1) + "\n")
    bad = [r["key"] for r in res["items"] if r["in_range"] is False]
    if bad:
        print("warning: size outside the correlation's range: " + ", ".join(bad), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
