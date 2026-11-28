"""HMB compilation audit: balance closure, design-versus-model comparison and P&ID linking on a `plant_model` dictionary.

Every check ends as "pass", "fail" or "not_checked". Missing or unreadable data is always "not_checked" with the reason: it is never
counted as zero (unlike the quick screen `hmb.balance`) and never as a pass. The overall verdict is "pass" only if nothing failed AND
nothing was left unchecked.

Balances (steady state, no accumulation), per unit and over the whole plant (boundary streams):
    mass       in - out = 0
    component  in + generation - out = 0       component mass flows; composition basis ("mass" or "mole") must be declared;
                                               mole fractions need `molar_masses` (kg/kmol) from the caller, none are built in
    energy     H_in + duty + work - H_out = 0  stream `H_kW` on one declared `enthalpy_basis`; unit `duty_kW` (heat into the process,
                                               0 for adiabatic) is required; `work_kW` (shaft work into the process) is optional
Reactions: a unit with `reactive: true` or `generation_kg_h` needs `generation_kg_h` {component: +made / -consumed} for the component
balance, and `enthalpy_basis: "formation"` for the energy balance. The generation must itself sum to zero mass. It is taken as given:
no stoichiometry or element balance is verified, and a generation back-calculated from the stream table proves nothing.

Extra input keys (beside the `plant_model` sections): model_streams (simulation results, list or CSV path), component_basis,
molar_masses, enthalpy_basis, audit (tolerance overrides). A stream may carry `line_no` and `source`.

The default tolerances are judgment, not taken from a standard: set your project's own in `audit`. The report records those used.
Standard library only.
"""
from __future__ import annotations

import math

from . import plant_model

PASS, FAIL, NC, REVIEW = "pass", "fail", "not_checked", "review"
BOUNDARY = (None, "", "feed", "product", "battery_limit")
DEFAULTS = {
    "mass_tol": 0.01,              # |residual| / larger of in and out
    "component_tol": 0.01,         # |residual| / larger of component in and out
    "trace_floor": 1e-4,           # component residuals below this fraction of the unit throughput pass
    "energy_tol": 0.02,            # |residual| / (|duty|+|work|), or / sum|H_in| when both are zero
    "energy_floor_kW": 1e-6,
    "composition_sum_tol": 1e-3,
    "compare_mass_rel": 0.02,
    "compare_T_abs_C": 2.0,
    "compare_P_rel": 0.02,
    "compare_P_floor_kPa": 5.0,
    "compare_H_rel": 0.02,
    "compare_fraction_abs": 0.01,
}
KNOWN_STREAM_KEYS = {"id", "from", "to", "phase", "T_C", "P_kpag", "mass_kg_h", "mw", "k", "Z", "rho_kg_m3", "components", "H_kW",
                     "line_no", "source", "component_basis", "hazard", "name", "description"}
NUMERIC_KEYS = ("T_C", "P_kpag", "mass_kg_h", "H_kW")


def _isnum(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _end(v, tags):
    """Unit tag, or None for a plant boundary. An unknown name is returned unchanged."""
    return v if v in tags else (None if v in BOUNDARY else v)


def _finding(area, status, item, message):
    return {"area": area, "status": status, "item": str(item), "message": message}


def component_flows(s: dict, basis: str | None, molar_masses: dict, sum_tol: float):
    """({component: kg/h}, None) or (None, reason)."""
    w = s.get("mass_kg_h")
    if not _isnum(w) or w < 0:
        return None, "mass flow missing or invalid"
    if w == 0:
        return {}, None
    comps = s.get("components")
    if not isinstance(comps, dict) or not comps:
        return None, "no composition"
    basis = s.get("component_basis") or basis
    if basis not in ("mass", "mole"):
        return None, "composition basis (mass or mole) not declared"
    if not all(_isnum(x) and x >= 0 for x in comps.values()):
        return None, "composition has a missing, non-numeric or negative fraction"
    total = sum(comps.values())
    if abs(total - 1.0) > sum_tol:
        return None, f"composition sums to {total:.5g}, not 1"
    if basis == "mole":
        miss = sorted(c for c, x in comps.items() if x > 0 and not (_isnum(molar_masses.get(c)) and molar_masses[c] > 0))
        if miss:
            return None, "molar_masses missing for " + ", ".join(miss)
        denom = sum(x * molar_masses[c] for c, x in comps.items() if x > 0)
        return {c: w * x * molar_masses[c] / denom for c, x in comps.items() if x > 0}, None
    return {c: w * x / total for c, x in comps.items()}, None


def _check(status, reason="", **numbers):
    return {"status": status, "reason": reason, **numbers}


def _mass_check(ins, outs, tol):
    bad = [str(s.get("id")) for s in ins + outs if not (_isnum(s.get("mass_kg_h")) and s["mass_kg_h"] >= 0)]
    if bad:
        return _check(NC, "mass flow missing or invalid on stream " + ", ".join(bad))
    i, o = sum(s["mass_kg_h"] for s in ins), sum(s["mass_kg_h"] for s in outs)
    res = i - o
    ref = max(i, o)
    rel = res / ref if ref else 0.0
    return _check(PASS if abs(rel) <= tol else FAIL, "", in_kg_h=i, out_kg_h=o, residual_kg_h=res, residual_rel=rel, tol=tol)


def _component_check(ins, outs, generation, ctx):
    p = ctx["p"]
    flows, reasons = {}, []
    for s in ins + outs:
        f, why = component_flows(s, ctx["basis"], ctx["mm"], p["composition_sum_tol"])
        if f is None:
            reasons.append(f"stream {s.get('id')}: {why}")
        flows[s.get("id")] = f
    if reasons:
        return _check(NC, "; ".join(reasons), components=[])
    names = set(generation)
    for f in flows.values():
        names |= set(f)
    tot_i = sum(sum(flows[s["id"]].values()) for s in ins)
    tot_o = sum(sum(flows[s["id"]].values()) for s in outs)
    floor = p["trace_floor"] * max(tot_i, tot_o)
    rows = []
    for c in sorted(names):
        i = sum(flows[s["id"]].get(c, 0.0) for s in ins)
        o = sum(flows[s["id"]].get(c, 0.0) for s in outs)
        g = generation.get(c, 0.0)
        res = i + g - o
        limit = max(p["component_tol"] * max(i + max(g, 0.0), o), floor)
        rows.append({"component": c, "in_kg_h": i, "generation_kg_h": g, "out_kg_h": o, "residual_kg_h": res,
                     "limit_kg_h": limit, "status": PASS if abs(res) <= limit + 1e-12 else FAIL})
    failed = [r["component"] for r in rows if r["status"] == FAIL]
    return _check(FAIL if failed else PASS, "does not close for " + ", ".join(failed) if failed else "", components=rows)


def _generation(u: dict, ctx):
    """(is_reactive, generation dict or None, check-or-None for the generation's own mass conservation)."""
    gen = u.get("generation_kg_h")
    reactive = bool(u.get("reactive")) or gen is not None
    if not reactive:
        return False, {}, None
    if not isinstance(gen, dict) or not gen or not all(_isnum(x) for x in gen.values()):
        return True, None, None
    net, gross = sum(gen.values()), sum(abs(x) for x in gen.values()) / 2
    ok = abs(net) <= ctx["p"]["mass_tol"] * gross if gross else net == 0
    return True, gen, _check(PASS if ok else FAIL, "" if ok else f"generation_kg_h sums to {net:+.6g} kg/h: a reaction cannot make or destroy mass")


def _energy_check(ins, outs, units, reactive, ctx):
    basis = ctx["enthalpy_basis"]
    if not basis:
        return _check(NC, "enthalpy_basis not declared: stream enthalpies cannot be assumed to share a reference")
    if reactive and str(basis).lower() != "formation":
        return _check(NC, 'reactive unit: the energy balance needs enthalpy_basis "formation"')
    reasons = []
    bad = [str(s.get("id")) for s in ins + outs if not _isnum(s.get("H_kW"))]
    if bad:
        reasons.append("H_kW missing or invalid on stream " + ", ".join(bad))
    noq = [u["tag"] for u in units if not _isnum(u.get("duty_kW"))]
    if noq:
        reasons.append("duty_kW not given for " + ", ".join(noq) + " (state 0 if adiabatic)")
    badw = [u["tag"] for u in units if u.get("work_kW") is not None and not _isnum(u["work_kW"])]
    if badw:
        reasons.append("work_kW invalid for " + ", ".join(badw))
    if reasons:
        return _check(NC, "; ".join(reasons))
    hi, ho = sum(s["H_kW"] for s in ins), sum(s["H_kW"] for s in outs)
    q = sum(u["duty_kW"] for u in units)
    w = sum(u.get("work_kW") or 0.0 for u in units)
    res = hi + q + w - ho
    gross = sum(abs(u["duty_kW"]) + abs(u.get("work_kW") or 0.0) for u in units)
    ref, ref_name = (gross, "duty plus work") if gross else (sum(abs(s["H_kW"]) for s in ins), "inlet enthalpy magnitude")
    limit = max(ctx["p"]["energy_tol"] * ref, ctx["p"]["energy_floor_kW"])
    return _check(PASS if abs(res) <= limit else FAIL, "", H_in_kW=hi, duty_kW=q, work_kW=w, H_out_kW=ho, residual_kW=res,
                  limit_kW=limit, reference=ref_name)


def balances(m: dict, ctx: dict) -> tuple[list[dict], dict]:
    tags = {u["tag"] for u in m["units"]}
    rows, gens, any_reactive, missing_gen, gen_checks = [], {}, False, [], []
    for u in m["units"]:
        ins = [s for s in m["streams"] if s.get("to") == u["tag"]]
        outs = [s for s in m["streams"] if s.get("from") == u["tag"]]
        reactive, gen, gcheck = _generation(u, ctx)
        any_reactive |= reactive
        if gen is None:
            missing_gen.append(u["tag"])
        else:
            for c, x in gen.items():
                gens[c] = gens.get(c, 0.0) + x
        if gcheck:
            gen_checks.append(gcheck)
        row = {"unit": u["tag"], "reactive": reactive, "inlets": [s["id"] for s in ins], "outlets": [s["id"] for s in outs],
               "generation": gcheck}
        if not ins or not outs:
            why = "no streams in the table" if not ins and not outs else f"no {'inlet' if not ins else 'outlet'} stream in the table"
            for k in ("mass", "component", "energy"):
                row[k] = _check(NC, why, **({"components": []} if k == "component" else {}))
        else:
            row["mass"] = _mass_check(ins, outs, ctx["p"]["mass_tol"])
            row["component"] = (_check(NC, "reactive unit: generation_kg_h missing or invalid", components=[]) if gen is None
                                else _component_check(ins, outs, gen, ctx))
            row["energy"] = _energy_check(ins, outs, [u], reactive, ctx)
        rows.append(row)

    feeds = [s for s in m["streams"] if _end(s.get("from"), tags) is None]
    prods = [s for s in m["streams"] if _end(s.get("to"), tags) is None]
    dangling = sorted({str(s.get(e)) for s in m["streams"] for e in ("from", "to") if _end(s.get(e), tags) not in tags | {None}})
    overall = {"unit": "WHOLE PLANT", "reactive": any_reactive, "inlets": [s["id"] for s in feeds], "outlets": [s["id"] for s in prods],
               "generation": None}
    blocker = ("stream ends name unknown units: " + ", ".join(dangling)) if dangling else \
              ("no boundary inlet and outlet streams" if not feeds or not prods else "")
    if blocker:
        for k in ("mass", "component", "energy"):
            overall[k] = _check(NC, blocker, **({"components": []} if k == "component" else {}))
    else:
        overall["mass"] = _mass_check(feeds, prods, ctx["p"]["mass_tol"])
        overall["component"] = (_check(NC, "generation_kg_h missing for " + ", ".join(missing_gen), components=[]) if missing_gen
                                else _component_check(feeds, prods, gens, ctx))
        overall["energy"] = _energy_check(feeds, prods, m["units"], any_reactive, ctx)
    return rows, overall


def link_pid(m: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Link streams to P&ID lines: by the stream's `line_no`, else by a unique (from, to) pair. Returns links, equipment, findings."""
    tags = {u["tag"] for u in m["units"]}
    lines = m["lines"]
    by_no = {}
    for ln in lines:
        by_no.setdefault(str(ln.get("line_no")), []).append(ln)
    links, findings, used = [], [], set()
    for s in m["streams"]:
        ends = (_end(s.get("from"), tags), _end(s.get("to"), tags))
        no, method, status, why, hit = s.get("line_no"), "", NC, "", None
        if not lines:
            why = "no P&ID line list or Proteus XML given"
        elif no not in (None, ""):
            method = "line_no"
            cands = by_no.get(str(no), [])
            if not cands:
                status, why = FAIL, f"line {no} is not on the P&ID line list"
            else:
                def ends_of(ln):
                    return (_end(ln.get("from"), tags), _end(ln.get("to"), tags))
                same = [ln for ln in cands if ends_of(ln) == ends]
                hit = (same or cands)[0]
                got = ends_of(hit)
                if same:
                    status = PASS
                elif hit.get("from") in (None, "") and hit.get("to") in (None, ""):
                    why = f"line {no} has no end points on the P&ID list, so connectivity cannot be compared"
                else:
                    status, why = FAIL, (f"line {no} runs {got[0] or 'boundary'} to {got[1] or 'boundary'} on the P&ID but stream runs "
                                         f"{ends[0] or 'boundary'} to {ends[1] or 'boundary'} in the HMB")
        elif ends == (None, None):
            why = "both ends are the plant boundary"
        else:
            method = "end points"
            cands = [ln for ln in lines if (ln.get("from") or ln.get("to")) and (_end(ln.get("from"), tags), _end(ln.get("to"), tags)) == ends]
            if len(cands) == 1:
                hit, status = cands[0], PASS
                why = "matched on end points only: add line_no to the stream to confirm"
            else:
                why = f"{len(cands)} P&ID lines join these end points" + (": add line_no to the stream" if cands else "")
        line_no = hit.get("line_no") if hit else no
        if hit:
            used.add(id(hit))
        valve_tags = [v.get("tag") for v in m["valves"] if line_no and v.get("line") == line_no]
        inst_tags = [i.get("tag") for i in m["instruments"] if line_no and i.get("line") == line_no]
        links.append({"stream": s.get("id"), "line_no": line_no, "method": method, "status": status, "reason": why,
                      "line_tags": [str(t) for t in valve_tags + inst_tags if t]})
        if status != PASS:
            findings.append(_finding("P&ID link", status, s.get("id"), why))
    for ln in lines:
        if id(ln) not in used:
            findings.append(_finding("P&ID link", REVIEW, ln.get("line_no"), "P&ID line has no matching HMB stream (may be a utility or minor line)"))
    equipment = []
    for u in m["units"]:
        t = u["tag"]
        row = {"unit": t, "type": u.get("type", ""), "duty_kW": u.get("duty_kW"), "work_kW": u.get("work_kW"),
               "instruments": [str(x.get("tag")) for x in m["instruments"] if x.get("unit") == t],
               "valves": [str(x.get("tag")) for x in m["valves"] if x.get("unit") == t],
               "relief_devices": [str(x.get("tag")) for x in m["relief_devices"] if x.get("unit") == t]}
        equipment.append(row)
        if not any(t in (s.get("from"), s.get("to")) for s in m["streams"]):
            findings.append(_finding("P&ID link", REVIEW, t, "equipment is in the unit list or P&ID but no HMB stream connects to it"))
    return links, equipment, findings


def compare(design: list[dict], model: list[dict], p: dict, basis: str | None = None) -> tuple[list[dict], list[dict]]:
    """Design HMB against model (simulation) results, stream by stream. `ratio` is signed difference / limit."""
    rows, findings = [], []
    d = {s.get("id"): s for s in design}
    r = {s.get("id"): s for s in model}
    if len(r) != len(model):
        raise ValueError("duplicate stream id in model_streams")
    for sid in list(d) + [x for x in r if x not in d]:
        if sid not in d or sid not in r:
            findings.append(_finding("design vs model", REVIEW if sid not in d else NC, sid,
                                     "stream is in the model results but not in the design HMB" if sid not in d else "stream has no model result"))
            continue
        a, b = d[sid], r[sid]

        def add(prop, x, y, limit):
            if x is None and y is None:
                return
            if not (_isnum(x) and _isnum(y)):
                rows.append({"stream": sid, "property": prop, "design": x, "model": y, "difference": None, "limit": None, "ratio": None,
                             "status": NC})
                findings.append(_finding("design vs model", NC, sid, f"{prop}: a number is missing on one side"))
                return
            diff = y - x
            ratio = diff / limit if limit else (0.0 if diff == 0 else math.copysign(1e9, diff))
            st = PASS if abs(diff) <= limit + 1e-12 else FAIL
            rows.append({"stream": sid, "property": prop, "design": x, "model": y, "difference": diff, "limit": limit, "ratio": ratio, "status": st})
            if st == FAIL:
                findings.append(_finding("design vs model", FAIL, sid, f"{prop}: design {x:.6g}, model {y:.6g} (limit {limit:.4g})"))

        def mag(k):
            return abs(a[k]) if _isnum(a.get(k)) else 0.0

        add("mass_kg_h", a.get("mass_kg_h"), b.get("mass_kg_h"), p["compare_mass_rel"] * mag("mass_kg_h"))
        add("T_C", a.get("T_C"), b.get("T_C"), p["compare_T_abs_C"])
        add("P_kpag", a.get("P_kpag"), b.get("P_kpag"), max(p["compare_P_rel"] * mag("P_kpag"), p["compare_P_floor_kPa"]))
        add("H_kW", a.get("H_kW"), b.get("H_kW"), p["compare_H_rel"] * mag("H_kW"))
        ca, cb = a.get("components") or {}, b.get("components") or {}
        if ca or cb:
            ba, bb = a.get("component_basis") or basis, b.get("component_basis") or basis
            if not ca or not cb or ba != bb or ba not in ("mass", "mole"):
                findings.append(_finding("design vs model", NC, sid, "composition not compared: missing on one side, or basis undeclared or different"))
            else:
                for c in sorted(set(ca) | set(cb)):
                    add(f"x[{c}] ({ba})", ca.get(c, 0.0), cb.get(c, 0.0), p["compare_fraction_abs"])
        wired = any(b.get(e) not in (None, "") for e in ("from", "to"))     # no end given at all: the model has no connectivity
        for e in ("from", "to") if wired else ():
            x, y = a.get(e), b.get(e)
            if (x if x not in BOUNDARY else None) != (y if y not in BOUNDARY else None):
                findings.append(_finding("design vs model", FAIL, sid, f"'{e}' is {x} in the design HMB and {y} in the model"))
    return rows, findings


def _stream_findings(streams: list[dict], tags: set, label: str) -> list[dict]:
    out = []
    for s in streams:
        extra = sorted(k for k, v in s.items() if k not in KNOWN_STREAM_KEYS and v not in (None, ""))
        if extra:
            out.append(_finding("input", REVIEW, s.get("id"), f"{label}: column(s) not read: {', '.join(extra)} (check the name and unit suffix)"))
        for k in NUMERIC_KEYS:
            v = s.get(k)
            if v not in (None, "") and not _isnum(v):
                out.append(_finding("input", FAIL, s.get("id"), f"{label}: {k} value {v!r} is not a plain number (unit typed into the cell?)"))
        if _isnum(s.get("mass_kg_h")) and s["mass_kg_h"] < 0:
            out.append(_finding("input", FAIL, s.get("id"), f"{label}: negative mass flow"))
        for e in ("from", "to"):
            if _end(s.get(e), tags) not in tags | {None}:
                out.append(_finding("input", FAIL, s.get("id"), f"{label}: '{e}' names {s.get(e)}, which is not a unit"))
    return out


def _with_sources(streams: list[dict], raw, label: str) -> None:
    for i, s in enumerate(streams):
        if not s.get("source"):
            s["source"] = f"{raw} row {i + 2}" if isinstance(raw, str) else f"input {label}[{i}]"


def audit(data: dict, base_dir: str | None = None) -> dict:
    """Run every check on a spec dictionary and return the report dictionary used by `hmb_report`."""
    over = data.get("audit") or {}
    unknown = sorted(set(over) - set(DEFAULTS))
    if unknown:
        raise ValueError("unknown audit tolerance(s): " + ", ".join(unknown))
    p = {**DEFAULTS, **over}
    if not all(_isnum(v) and v >= 0 for v in p.values()):
        raise ValueError("audit tolerances must be non-negative numbers")
    m = plant_model.load(data, base_dir=base_dir)
    if not m["streams"]:
        raise ValueError("no streams: nothing to audit")
    ids = [s.get("id") for s in m["streams"]]
    if any(i in (None, "") for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("every stream needs a unique, non-blank id")
    tags = [u["tag"] for u in m["units"]]
    if len(set(tags)) != len(tags):
        raise ValueError("duplicate unit tag")
    _with_sources(m["streams"], data.get("streams"), "streams")
    model = plant_model._section(data.get("model_streams"), base_dir)
    _with_sources(model, data.get("model_streams"), "model_streams")
    ctx = {"p": p, "basis": data.get("component_basis"), "mm": data.get("molar_masses") or {}, "enthalpy_basis": data.get("enthalpy_basis")}

    units, overall = balances(m, ctx)
    links, equipment, findings = link_pid(m)
    findings = _stream_findings(m["streams"], set(tags), "design HMB") + _stream_findings(model, set(tags), "model results") + findings
    for row in units + [overall]:
        for k in ("mass", "component", "energy"):
            c = row[k]
            if c["status"] != PASS:
                msg = c["reason"] or ("residual %.6g kg/h (%.2f%%)" % (c["residual_kg_h"], 100 * c["residual_rel"]) if k == "mass"
                                      else "residual %.6g kW against a limit of %.4g kW" % (c.get("residual_kW", 0), c.get("limit_kW", 0)))
                findings.append(_finding(f"{k} balance", c["status"], row["unit"], msg))
        if row["generation"] and row["generation"]["status"] == FAIL:
            findings.append(_finding("reaction", FAIL, row["unit"], row["generation"]["reason"]))
    if model:
        comparison, cf = compare(m["streams"], model, p, ctx["basis"])
        findings += cf
    else:
        comparison = []
        findings.append(_finding("design vs model", NC, "all streams", "no model_streams given: model results were not audited"))

    flows = {s["id"]: component_flows(s, ctx["basis"], ctx["mm"], p["composition_sum_tol"])[0] for s in m["streams"]}
    order = {FAIL: 0, NC: 1, REVIEW: 2}
    findings.sort(key=lambda f: order[f["status"]])
    count = {k: sum(1 for f in findings if f["status"] == k) for k in order}
    verdict = FAIL if count[FAIL] else (NC if count[NC] else PASS)
    return {"name": m["name"], "verdict": verdict, "counts": count, "units": units, "overall": overall, "links": links,
            "equipment": equipment, "comparison": comparison, "findings": findings, "streams": m["streams"], "component_kg_h": flows, "tolerances": p,
            "enthalpy_basis": ctx["enthalpy_basis"], "component_basis": ctx["basis"], "notes": m["notes"],
            "limits": "Screening audit of the numbers supplied. A pass means the tables are consistent within the tolerances shown; it does "
                      "not show that the design, the thermodynamic method or the P&ID is correct."}
