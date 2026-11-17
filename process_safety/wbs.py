"""Work breakdown structure: numbered nodes, leaf estimates rolled up, a schedule built from the leaves, and structure-only templates.

Nodes are `{"code": "1.2.3", "name": ..., "duration_days"?, "effort_days"?, "cost"?, "owner"?, "predecessors"?, "percent_complete"?}`.
Only leaves carry estimates; a summary node carries none and is rolled up, so a parent always equals the sum of its children.
Percent complete rolls up weighted by effort_days (else duration_days); a leaf with neither has weight 0.

The templates (`hazop`, `qra`, `pha_revalidation`) are generic activity lists with links and **no numbers**: they are not the procedure
of IEC 61882 or of any company, which were not read. Estimates are left empty so `check` refuses to schedule them until a person has
filled them in. Costs are in whatever currency the caller uses; the module never converts.
"""
from __future__ import annotations

import re

from . import schedule

CODE = re.compile(r"^[1-9]\d*(\.[1-9]\d*)*$")


def _key(code):
    return tuple(int(x) for x in code.split("."))


def _nodes(data):
    return sorted(data.get("wbs", []), key=lambda n: _key(n["code"]) if CODE.match(str(n.get("code", ""))) else (10 ** 9,))


def _parent(code):
    return code.rsplit(".", 1)[0] if "." in code else None


def _leaf_codes(nodes):
    codes = [n["code"] for n in nodes]
    return {c for c in codes if not any(o.startswith(c + ".") for o in codes)}


def check(data: dict, require_estimates: bool = True) -> list[str]:
    errs = []
    nodes = data.get("wbs", [])
    if not nodes:
        return ["no wbs nodes"]
    codes = [n.get("code") for n in nodes]
    for c in codes:
        if not isinstance(c, str) or not CODE.match(c):
            errs.append(f"code {c!r} must be dotted positive integers such as 1 or 1.2.3")
    if len(codes) != len(set(codes)):
        errs.append("duplicate wbs code")
    if errs:
        return errs
    for n in nodes:
        p = _parent(n["code"])
        if p is not None and p not in codes:
            errs.append(f"{n['code']}: parent {p} does not exist")
    if errs:
        return errs
    leaves = _leaf_codes(nodes)
    for n in nodes:
        c = n["code"]
        is_leaf = c in leaves
        for k in ("duration_days", "effort_days", "cost"):
            v = n.get(k)
            if v is None:
                continue
            if not is_leaf:
                errs.append(f"{c}: summary node must not carry {k}; it is rolled up from its children")
            elif not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                errs.append(f"{c}: {k} must be a number >= 0")
        if is_leaf and require_estimates and n.get("duration_days") is None:
            errs.append(f"{c}: leaf has no duration_days (estimate needed before scheduling)")
        if "percent_complete" in n:
            if not is_leaf:
                errs.append(f"{c}: summary node must not carry percent_complete")
            elif not (isinstance(n["percent_complete"], (int, float)) and 0 <= n["percent_complete"] <= 100):
                errs.append(f"{c}: percent_complete must be in [0, 100]")
        if n.get("predecessors") and not is_leaf:
            errs.append(f"{c}: predecessors belong on leaves")
        for p, t, lag in schedule._links(n):
            if p not in leaves:
                errs.append(f"{c}: unknown predecessor {p}")
            if t not in schedule.LINKS:
                errs.append(f"{c}: link type {t!r} must be FS, SS or FF")
    if not errs:
        acts = {n["code"]: {"predecessors": n.get("predecessors", [])} for n in nodes if n["code"] in leaves}
        if schedule._topo(acts) is None:
            errs.append("predecessor network has a cycle")
    return errs


def roll_up(data: dict) -> list[dict]:
    nodes = _nodes(data)
    leaves = _leaf_codes(nodes)
    rows = []
    for n in nodes:
        c = n["code"]
        under = [m for m in nodes if m["code"] in leaves and (m["code"] == c or m["code"].startswith(c + "."))]
        w = [(m.get("effort_days") if m.get("effort_days") is not None else m.get("duration_days") or 0.0, m.get("percent_complete")) for m in under]
        wsum = sum(x for x, _ in w)
        pct = (sum(x * (p or 0.0) for x, p in w) / wsum) if wsum > 0 else None
        rows.append({"code": c, "name": n.get("name", c), "level": c.count(".") + 1, "leaf": c in leaves,
                     "effort_days": sum(m.get("effort_days") or 0.0 for m in under), "cost": sum(m.get("cost") or 0.0 for m in under),
                     "duration_days": n.get("duration_days") if c in leaves else None, "percent_complete": pct,
                     "owner": n.get("owner", ""), "predecessors": [p for p, _, _ in schedule._links(n)]})
    return rows


def to_schedule(data: dict, start: str) -> dict:
    """Schedule input from the leaves; calendar, finish_by, status_date and capacity are passed through from the WBS file."""
    nodes = _nodes(data)
    leaves = _leaf_codes(nodes)
    acts = []
    for n in nodes:
        if n["code"] not in leaves:
            continue
        a = {"id": n["code"], "name": f"{n['code']} {n.get('name', '')}".strip(), "duration_days": n.get("duration_days", 0.0)}
        for k in ("predecessors", "owner", "effort_days", "percent_complete", "start_no_earlier"):
            if n.get(k) is not None:
                a[k] = n[k]
        acts.append(a)
    out = {"start": start, "activities": acts}
    for k in ("calendar", "finish_by", "status_date", "capacity_days_per_week"):
        if k in data:
            out[k] = data[k]
    return out


def summary_dates(data: dict, plan: dict) -> dict:
    by = {r["id"]: r for r in plan["activities"]}
    out = {}
    for n in _nodes(data):
        c = n["code"]
        under = [by[k] for k in by if k == c or k.startswith(c + ".")]
        if under:
            out[c] = {"start": min(r["start"] for r in under), "finish": max(r["finish"] for r in under)}
    return out


def dictionary_rows(data: dict) -> list[dict]:
    desc = {n["code"]: n.get("description", "") for n in data.get("wbs", [])}
    return [{"code": r["code"], "level": r["level"], "name": r["name"], "type": "work package" if r["leaf"] else "summary",
             "owner": r["owner"], "duration_days": r["duration_days"], "effort_days": r["effort_days"], "cost": r["cost"],
             "predecessors": " ".join(r["predecessors"]), "description": desc.get(r["code"], "")} for r in roll_up(data)]


def template(kind: str, nodes: list[str] | None = None) -> list[dict]:
    """Generic structure with links and no numbers. `nodes` are the HAZOP/PHA nodes, or the QRA scenario groups, one work package each."""
    nodes = nodes or ["Node 1"]
    L: list[tuple[str, str, list[str]]] = []          # (code, name, predecessors)

    def add(code, name, preds=()):
        L.append((code, name, list(preds)))

    if kind == "hazop":
        add("1", "Mobilisation")
        add("1.1", "Kick-off and scope confirmation")
        add("1.2", "Collect design basis (P&IDs, cause and effects, datasheets)")
        add("1.3", "Confirm team, facilitator and scribe")
        add("2", "Preparation")
        add("2.1", "Node selection and design intents", ["1.1", "1.2"])
        add("2.2", "Worksheet and risk matrix set-up", ["1.1"])
        add("2.3", "Issue pre-reads", ["2.1", "2.2", "1.3"])
        add("3", "Workshop")
        prev = "2.3"
        for k, nd in enumerate(nodes, 1):
            add(f"3.{k}", f"Review {nd}", [prev])
            prev = f"3.{k}"
        add("4", "Reporting")
        add("4.1", "Draft worksheets", [prev])
        add("4.2", "Draft report", ["4.1"])
        add("4.3", "Client review", ["4.2"])
        add("4.4", "Issue final report", ["4.3"])
        add("5", "Close-out")
        add("5.1", "Hand over action register", ["4.4"])
        add("5.2", "Action closure follow-up", ["5.1"])
    elif kind == "qra":
        add("1", "Mobilisation")
        add("1.1", "Kick-off and scope confirmation")
        add("1.2", "Collect data (layout, inventories, weather, population)")
        add("2", "Hazard identification")
        add("2.1", "Release scenarios and loss-of-containment register", ["1.2"])
        add("2.2", "Frequency data selection", ["1.2"])
        add("3", "Consequence modelling")
        prev = "2.1"
        for k, nd in enumerate(nodes, 1):
            add(f"3.{k}", f"Model {nd}", [prev])
            prev = f"3.{k}"
        add("4", "Risk summation")
        add("4.1", "Individual risk, societal risk and contours", [prev, "2.2"])
        add("4.2", "ALARP review", ["4.1"])
        add("5", "Reporting")
        add("5.1", "Draft report", ["4.2"])
        add("5.2", "Client review", ["5.1"])
        add("5.3", "Issue final report", ["5.2"])
    elif kind == "pha_revalidation":
        add("1", "Review")
        add("1.1", "Collect previous PHA and its action register")
        add("1.2", "Review management of change and incidents since the last study", ["1.1"])
        add("1.3", "Review action closure status", ["1.1"])
        add("2", "Workshop")
        prev = None
        for k, nd in enumerate(nodes, 1):
            add(f"2.{k}", f"Revalidate {nd}", [prev] if prev else ["1.2", "1.3"])
            prev = f"2.{k}"
        add("3", "Report")
        add("3.1", "Update worksheets and action register", [prev])
        add("3.2", "Issue report", ["3.1"])
    else:
        raise ValueError(f"unknown template {kind!r}; use hazop, qra or pha_revalidation")
    return [{"code": c, "name": n, **({"predecessors": p} if p else {})} for c, n, p in L]
