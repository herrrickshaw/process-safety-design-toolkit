"""Data consistency checks, run before (inputs) and after (results) every QRA. Errors stop the run in strict mode; warnings are
reported in every output. The checks are deliberately boring: units in physical ranges, probabilities in [0, 1], distributions
summing to 1, references that resolve, and identities that must hold in the results."""
from __future__ import annotations

import math


class Report:
    def __init__(self):
        self.errors, self.warnings, self.passed = [], [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def ok(self, m):
        self.passed.append(m)

    def check(self, cond, msg_fail, msg_ok=None, warn=False):
        if cond:
            if msg_ok:
                self.ok(msg_ok)
        else:
            (self.warn if warn else self.err)(msg_fail)
        return cond

    def as_dict(self):
        return {"errors": self.errors, "warnings": self.warnings, "passed": self.passed}

    def __bool__(self):
        return not self.errors


REQ_MAT = {"gas": ["M", "k", "Hc_MJ_kg"], "liquid": ["rho_liquid", "Hc_MJ_kg", "Hv_kJ_kg", "cp_liquid_kJ_kgK", "Tb_K"],
           "pressurised_liquefied": ["M", "rho_liquid", "Hc_MJ_kg", "Hv_kJ_kg", "cp_liquid_kJ_kgK", "Tb_K", "LFL_vol"]}
REQ_SEC = ["id", "material", "x", "y", "P_kpag", "T_K", "inventory_kg", "equipment"]


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def inputs(study: dict, dataset: dict) -> Report:
    r = Report()
    mats = study.get("materials", {})
    r.check(bool(mats), "no materials defined")
    for name, m in mats.items():
        ph = m.get("phase_stored")
        if not r.check(ph in REQ_MAT, f"material {name}: phase_stored must be one of {list(REQ_MAT)}"):
            continue
        for k in REQ_MAT[ph]:
            r.check(_num(m.get(k)) and m[k] > 0, f"material {name}: {k} missing or not > 0")
        if _num(m.get("k")):
            r.check(1.0 < m["k"] < 1.7, f"material {name}: k = Cp/Cv = {m['k']} outside 1-1.7")
        if m.get("LFL_vol") is not None:
            r.check(0 < m["LFL_vol"] < 0.2, f"material {name}: LFL_vol should be a volume FRACTION (e.g. 0.021), got {m['LFL_vol']}")
        if ph == "pressurised_liquefied" and _num(m.get("Tb_K")):
            r.check(m["Tb_K"] < 330, f"material {name}: pressurised_liquefied with Tb {m['Tb_K']} K - is it really flashing?", warn=True)
        tox = m.get("toxic")
        if tox:
            from ..consequence import TOXIC_PROBITS
            r.check("probit" in tox or tox.get("component", "").lower() in TOXIC_PROBITS,
                    f"material {name}: toxic component {tox.get('component')!r} has no probit (give 'probit': [a, b, n])")
            f = tox.get("mole_fraction", tox.get("mass_fraction"))
            r.check(_num(f) and 0 < f <= 1, f"material {name}: toxic mole/mass fraction must be in (0, 1]")
        if ph == "pressurised_liquefied" and m.get("M", 0) > 29:
            r.warn(f"material {name}: vapour heavier than air (M {m['M']}) - flash-fire/toxic footprints use a NEUTRAL Gaussian plume; "
                   "consider a dense-gas override (Phast) for decisions")
    ids = set()
    for s in study.get("sections", []):
        for k in REQ_SEC:
            r.check(k in s, f"section {s.get('id', '?')}: missing {k}")
        if not all(k in s for k in REQ_SEC):
            continue
        r.check(s["id"] not in ids, f"duplicate section id {s['id']}")
        ids.add(s["id"])
        r.check(s["material"] in mats, f"section {s['id']}: material {s['material']!r} not defined")
        r.check(s["P_kpag"] >= 0, f"section {s['id']}: negative gauge pressure")
        r.check(150 < s["T_K"] < 900, f"section {s['id']}: T_K = {s['T_K']} outside 150-900 K (Kelvin?)")
        r.check(s["inventory_kg"] > 0, f"section {s['id']}: inventory must be > 0")
        m = mats.get(s["material"], {})
        if m.get("phase_stored") == "pressurised_liquefied" and _num(m.get("Tb_K")):
            r.check(s["T_K"] > m["Tb_K"], f"section {s['id']}: stored below its boiling point - not flashing", warn=True)
        for it in s["equipment"]:
            if "rows" not in it and "frequency_per_yr" not in it:
                if not r.check(it.get("type") in dataset["equipment"], f"section {s['id']}: equipment {it.get('type')!r} has no generic data; give rows/frequency_per_yr"):
                    continue
                eq = dataset["equipment"][it["type"]]
                if eq["unit"] == "per_m_yr":
                    r.check(_num(it.get("length_m")) and it["length_m"] > 0, f"section {s['id']}: {it['type']} needs length_m > 0")
                    d = it.get("diameter_mm")
                    r.check(_num(d), f"section {s['id']}: {it['type']} needs diameter_mm")
                    if _num(d) and "d_min_mm" in eq:
                        r.check(eq["d_min_mm"] <= d <= eq["d_max_mm"], f"section {s['id']}: diameter {d} mm outside {it['type']} band {eq['d_min_mm']}-{eq['d_max_mm']} mm")
            for row in it.get("rows", []):
                r.check(_num(row.get("freq")) and row["freq"] >= 0, f"section {s['id']}: equipment row frequency must be >= 0")
                r.check(row.get("source"), f"section {s['id']}: equipment {it.get('tag', it.get('type'))} row has no 'source' - record where the number came from", warn=True)
        if s.get("bund_area_m2") is not None:
            r.check(s["bund_area_m2"] > 0, f"section {s['id']}: bund_area_m2 must be > 0")
    for x in study.get("extra_scenarios", []):
        r.check(x.get("section") in ids, f"extra scenario {x.get('id')}: section {x.get('section')!r} not defined")
        for p in x.get("ipl_pfds", []):
            r.check(0 < p <= 1, f"extra scenario {x.get('id')}: IPL PFD {p} outside (0, 1]")
        if "fault_tree" in x:
            ft = x["fault_tree"]
            for n, p in ft.get("basic", {}).items():
                r.check(0 <= p <= 1, f"extra scenario {x['id']}: basic event {n} probability {p} outside [0, 1]")
    wx = study.get("weather", [])
    r.check(bool(wx), "no weather classes")
    r.check(abs(sum(w.get("p", 0) for w in wx) - 1) < 1e-6, f"weather probabilities sum to {sum(w.get('p', 0) for w in wx):.6f}, not 1",
            "weather probabilities sum to 1")
    for w in wx:
        r.check(w.get("stability", "").upper() in "ABCDEF" and len(w.get("stability", "")) == 1, f"weather {w.get('name')}: stability must be A-F")
        r.check(_num(w.get("u")) and w["u"] >= 1.0, f"weather {w.get('name')}: wind speed {w.get('u')} m/s < 1 - Gaussian plume invalid")
    rose = study.get("wind_rose", [])
    r.check(len(rose) in (4, 8, 12, 16, 36), f"wind rose has {len(rose)} sectors (use 4/8/12/16/36)")
    r.check(abs(sum(rose) - 1) < 1e-6 and all(p >= 0 for p in rose), f"wind rose sums to {sum(rose):.6f} (must be 1, all >= 0)", "wind rose sums to 1")
    ign = study.get("ignition", {})
    r.check(_num(ign.get("immediate_fraction")) and 0 <= ign["immediate_fraction"] <= 1,
            "ignition.immediate_fraction (share of ignitions that are immediate) is required in [0, 1] - Cox gives only the total")
    g = study.get("grid", {})
    if r.check(all(_num(g.get(k)) for k in ("x_min", "x_max", "y_min", "y_max", "step")), "grid needs x_min, x_max, y_min, y_max, step"):
        r.check(g["x_max"] > g["x_min"] and g["y_max"] > g["y_min"] and g["step"] > 0, "grid extents/step invalid")
        for s in study.get("sections", []):
            if _num(s.get("x")) and _num(s.get("y")):
                r.check(g["x_min"] <= s["x"] <= g["x_max"] and g["y_min"] <= s["y"] <= g["y_max"], f"section {s['id']} lies outside the grid", warn=True)
        n = (g["x_max"] - g["x_min"]) / g["step"] * (g["y_max"] - g["y_min"]) / g["step"]
        r.check(n <= 250_000, f"grid has ~{n:,.0f} cells - run with --sample first and coarsen", warn=True)
    for p in study.get("population", []):
        r.check(_num(p.get("people")) and p["people"] >= 0, f"population {p.get('name')}: people must be >= 0")
        r.check(0 <= p.get("indoor_fraction", 0) <= 1, f"population {p.get('name')}: indoor_fraction outside [0, 1]")
    for rc in study.get("receptors", []):
        r.check(rc.get("group") in ("worker", "public"), f"receptor {rc.get('name')}: group must be worker or public")
        r.check(0 <= rc.get("occupancy", 1) <= 1, f"receptor {rc.get('name')}: occupancy outside [0, 1]")
    for k, v in study.get("indoor_vulnerability", {}).items():
        if k.startswith("_"):
            continue
        r.check(_num(v) and 0 <= v <= 1, f"indoor_vulnerability {k} = {v} outside [0, 1]")
    al = study.get("alarp", {})
    if study.get("mitigation"):
        r.check(_num(al.get("vpf")) and al["vpf"] > 0, "alarp.vpf (value of preventing a fatality) is required for mitigation CBA - it is a policy input, no default")
    return r


def results(res: dict, scenarios: list[dict]) -> Report:
    r = Report()
    for s in scenarios:
        tot = sum(o["prob"] for o in s["branches"])
        r.check(abs(tot - 1) < 1e-9 or not s["branches"], f"event tree for {s['id']}: branch probabilities sum to {tot}")
        r.check(all(0 <= o["prob"] <= 1 for o in s["branches"]), f"event tree for {s['id']}: branch probability outside [0, 1]")
        r.check(s["frequency_per_yr"] >= 0, f"{s['id']}: negative frequency")
    r.ok("event-tree branch probabilities sum to 1 for every LOC") if not r.errors else None
    neg = sum(1 for row in res["grid"].ir for v in row if v < 0 or v != v)
    r.check(neg == 0, f"{neg} grid cells with negative/NaN risk", "all grid LSIR values finite and >= 0")
    loc_total = sum(s["frequency_per_yr"] for s in scenarios)
    mx = max((v for row in res["grid"].ir for v in row), default=0.0)
    r.check(mx <= loc_total * (1 + 1e-9), f"max LSIR {mx:.3e} exceeds total LOC frequency {loc_total:.3e} - impossible", "max LSIR <= total LOC frequency")
    a, b = res["pll"], res["pll_check"]
    r.check(abs(a - b) <= 1e-9 + 1e-6 * max(a, b), f"PLL mismatch: F-N events {a:.6e} vs population-weighted LSIR {b:.6e}",
            f"PLL identity holds (F-N events = population-weighted LSIR = {a:.3e}/yr)")
    fn = res.get("fn_curve", [])
    r.check(all(fn[i][1] >= fn[i + 1][1] - 1e-18 for i in range(len(fn) - 1)), "F-N curve not monotone non-increasing", "F-N curve monotone")
    for name, v in res["receptor_lsir"].items():
        r.check(v >= 0, f"receptor {name}: negative LSIR")
    g = res["grid"]
    secs = {s["id"]: (s["x"], s["y"]) for s in scenarios}
    over = set()
    for (sid, outcome, _w), e in res.get("effects", {}).items():
        if e is None:
            continue
        x, y = secs[sid]
        d = min(x - g.xs[0], g.xs[-1] - x, y - g.ys[0], g.ys[-1] - y)
        if e.reach > d:
            over.add(f"{sid}/{outcome.split('+')[0]} ({e.reach:.0f} m)")
    r.check(not over, "footprints extend past the grid edge - LSIR beyond the grid is not mapped (receptor, F-N and PLL results "
            f"are still exact): {', '.join(sorted(over)[:6])}{' ...' if len(over) > 6 else ''}", "all footprints inside the grid", warn=True)
    return r
