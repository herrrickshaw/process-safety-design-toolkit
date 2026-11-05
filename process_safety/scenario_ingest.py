"""Scenario ingestion and the "why" chain: read a HAZOP/LOPA/PHA register, classify its recommendations, compare them with what the HMB
scenarios and P&ID review say a study should raise, and tell the story behind each recommendation (condition -> scenario -> gap ->
recommendation type -> cost scope).

Register columns (CSV or list of dicts; extras kept): id, node (unit tag or node name), deviation, cause, consequence, safeguards,
recommendation, owner, status, severity. Matching a register row to a unit is by the unit tag appearing in the node text. Classification is
by keyword (`recommendation_catalog`), best two matches per text. The cross-check is only as good as the register's wording: a "not found in
the register" result means the register does not mention the topic at that node, which is a prompt to look, not proof of an omission.
"""
from __future__ import annotations

from . import hmb, pid_review, plant_model, recommendation_catalog as rc


def read_register(src) -> list[dict]:
    rows = plant_model.read_csv(src) if isinstance(src, str) else [dict(r) for r in (src or [])]
    for i, r in enumerate(rows, 1):
        r.setdefault("id", i)
    return rows


def classify_register(rows: list[dict]) -> dict:
    texts = [str(r.get("recommendation") or "") for r in rows if r.get("recommendation")]
    t = rc.tally(texts)
    for r in rows:
        r["rec_ids"] = rc.classify(str(r.get("recommendation") or ""))[:2] if r.get("recommendation") else []
    return {"n_rows": len(rows), "n_with_recommendation": len(texts), "tally": t["counts"], "unmatched": t["unmatched"],
            "no_safeguards_but_consequence": [r["id"] for r in rows if r.get("consequence") and not r.get("safeguards") and not r.get("recommendation")]}


def _mentions(row: dict, cid: str) -> bool:
    blob = " ".join(str(row.get(k) or "") for k in ("deviation", "cause", "consequence", "safeguards", "recommendation")).lower()
    return any(rc._has(" " + blob + " ", k) for k in rc.CATALOG[cid]["keywords"]) or cid in row.get("rec_ids", [])


def rationale(m: dict, params: dict | None = None, register: list[dict] | None = None, isolation_inventory_kg: float | None = None) -> dict:
    """Merge P&ID findings and HMB scenarios into one table of reasons per (unit, recommendation type), and compare with the register."""
    findings = pid_review.review(m, isolation_inventory_kg)
    scn = hmb.scenarios_for(m, params)
    reg = register or []
    items: dict[tuple, dict] = {}
    for f in findings:
        for cid in f["rec_ids"]:
            e = items.setdefault((f["unit"], cid), {"unit": f["unit"], "rec_id": cid, "reasons": [], "sources": set()})
            e["reasons"].append(f"P&ID {f['rule']} ({f['severity']}): {f['message']}")
            e["sources"].add("pid_review")
    for s in scn:
        if s["status"] in ("gap", "review") and s["rec_ids"]:
            for cid in s["rec_ids"]:
                e = items.setdefault((s["unit"], cid), {"unit": s["unit"], "rec_id": cid, "reasons": [], "sources": set()})
                e["reasons"].append(f"HMB {s['scenario']} ({s['status']}): {s['why']}")
                e["sources"].add("hmb")
    out = []
    for (unit, cid), e in sorted(items.items()):
        rows = [r for r in reg if unit and unit.lower() in str(r.get("node", "")).lower()]
        hit = [r["id"] for r in rows if _mentions(r, cid)]
        c = rc.CATALOG[cid]
        out.append({"unit": unit, "rec_id": cid, "recommendation": c["title"], "cost_scope": c["scope"], "reasons": e["reasons"], "sources": sorted(e["sources"]),
                    "register_rows_at_node": [r["id"] for r in rows], "register_mentions": hit,
                    "in_register": bool(hit) if reg else None,
                    "response": c["response"]})
    return {"pid_findings": findings, "hmb_scenarios": scn, "rationale": out,
            "gaps_not_in_register": [r for r in out if r["in_register"] is False],
            "triggered_counts": _count([r["rec_id"] for r in out])}


def _count(ids):
    d: dict[str, int] = {}
    for i in ids:
        d[i] = d.get(i, 0) + 1
    return dict(sorted(d.items(), key=lambda kv: -kv[1]))


def workflow_skeleton(m: dict, rat: dict) -> dict:
    """A starting `tool workflow` input for the units with device-type triggers, filled from the model; `todo` lists what is still missing."""
    dev = {"PSV-ADD", "PSV-UPSIZE", "BDV", "RELIEF-PIPING", "INTERFACE-DP"}
    units, todo = [], []
    by = {u["tag"]: u for u in m["units"]}
    for tag in sorted({r["unit"] for r in rat["rationale"] if r["rec_id"] in dev and r["unit"] in by}):
        u = by[tag]
        area, devs = hmb.device_area(m, tag)
        vap = next((s for s in m["streams"] if s.get("from") == tag and str(s.get("phase", "")).startswith("vap")), {})
        entry = {"tag": tag, "mode": "liquid_wetted" if u.get("level_pct") else "vapour_filled",
                 "set_kpag": min((d["set_kpag"] for d in devs if d.get("set_kpag") is not None), default=None),
                 "fluid": {"M": vap.get("mw"), "k": vap.get("k"), "Z": vap.get("Z"), "relieving_T_K": (vap["T_C"] + 273.15) if vap.get("T_C") is not None else None},
                 "vessel": {k: u.get(k) for k in ("D_m", "L_m", "volume_m3", "latent_heat_kJ_kg", "orientation") if u.get(k) is not None},
                 "existing": {"psv_area_mm2": area}, "install": {}}
        for path, v in (("set_kpag", entry["set_kpag"]), ("fluid.M", entry["fluid"]["M"]), ("fluid.k", entry["fluid"]["k"]), ("fluid.relieving_T_K", entry["fluid"]["relieving_T_K"]),
                        ("vessel.D_m", u.get("D_m")), ("install.* (quantities, rate keys, shutdown durations)", None)):
            if v is None:
                todo.append(f"{tag}: {path}")
        units.append(entry)
    return {"units": units, "todo": todo, "note": "fill the todo items, add rate_book and opex_book, then run: python -m process_safety tool workflow"}
