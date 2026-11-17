"""Portfolio report: tender register + project schedules + capacity + HAZOP/PHA actions and revalidation, in one status page.

Inputs (all optional except what a section needs): `tenders` and `stage_probability` (see tender_register), `bid`, `projects` (each
a schedule input, or a `wbs` with `start`; plus `budget`, `actual_cost`, `status_date`, `tender_id`), `capacity_days_per_week`,
`calendar` (for capacity scaling), `pha` {"actions": [...], "revalidations": [{"unit", "last_pha", "mocs_since", "incidents_since"}]},
`today`, `horizon_days` (look-ahead for deadlines and starts; 30 when absent, and the notes say so).

Earned value per project uses the standard definitions: PV = BAC x planned percent, EV = BAC x reported percent, with percent weighted
by effort_days (else duration); SV = EV - PV; CV = EV - AC; SPI = EV / PV; CPI = EV / AC; EAC = BAC / CPI. The EAC form assumes the cost
performance to date continues. Nothing is guessed: no budget, no earned value; no actual cost, no cost index or EAC.
Capacity is compared across projects per owner and week, scaled by the working days in the week on the portfolio calendar.
"""
from __future__ import annotations

import datetime as dt
import html

from . import pha, schedule, tender_register as tr, wbs

DEFAULT_HORIZON_DAYS = 30


def _plan_input(p: dict, today: dt.date) -> dict:
    if "wbs" in p:
        d = wbs.to_schedule(p, p["start"])
        for k in ("calendar", "finish_by", "capacity_days_per_week"):
            if k in p:
                d[k] = p[k]
    else:
        d = {k: v for k, v in p.items() if k in ("start", "calendar", "activities", "finish_by", "capacity_days_per_week")}
    d["status_date"] = p.get("status_date", today.isoformat())
    return d


def _earned_value(p: dict, plan: dict) -> dict | None:
    bac = p.get("budget")
    if bac is None:
        return None
    eff = {a["id"]: a.get("effort_days") for a in (p.get("activities") or wbs.to_schedule(p, p["start"])["activities"])}
    rows = plan["activities"]
    w = [(eff.get(r["id"]) if eff.get(r["id"]) is not None else r["duration_days"], r) for r in rows]
    wsum = sum(x for x, _ in w)
    if wsum <= 0:
        return None
    planned = sum(x * r.get("planned_percent", 0.0) for x, r in w) / wsum
    reported = sum(x * r.get("percent_complete", 0.0) for x, r in w) / wsum
    pv, ev = bac * planned / 100.0, bac * reported / 100.0
    ac = p.get("actual_cost")
    cpi = ev / ac if ac else None
    return {"BAC": bac, "planned_percent": planned, "reported_percent": reported, "PV": pv, "EV": ev, "AC": ac, "SV": ev - pv,
            "SPI": ev / pv if pv > 0 else None, "CV": ev - ac if ac is not None else None, "CPI": cpi,
            "EAC": bac / cpi if cpi else None}


def run(data: dict, today: dt.date | None = None) -> dict:
    today = today or (dt.date.fromisoformat(data["today"]) if data.get("today") else dt.date.today())
    horizon = data.get("horizon_days", DEFAULT_HORIZON_DAYS)
    notes, checks = [], []
    if "horizon_days" not in data:
        notes.append(f"look-ahead is the default {DEFAULT_HORIZON_DAYS} days; set horizon_days to change it")

    tenders = data.get("tenders", [])
    terr = tr.check({"tenders": tenders, "stage_probability": data.get("stage_probability", {})})
    checks += [f"FAIL: tenders: {e}" for e in terr] or ["PASS: tender register inputs"]
    if terr:
        dl, up, pipe, wr, bids = {"upcoming": [], "missed": [], "chase": []}, [], {}, {}, []
    else:
        dl = tr.deadlines(tenders, today, horizon)
        up = tr.upcoming_projects(tenders, today, horizon, include_open=True)
        pipe = tr.weighted_pipeline(tenders, data.get("stage_probability", {}))
        wr = tr.win_rate(tenders)
        bids = []
        if data.get("bid"):
            for e in tenders:
                if e["stage"] in tr.PRE_SUBMISSION:
                    try:
                        b = tr.bid_score(e, data["bid"])
                    except ValueError as ex:
                        checks.append(f"FAIL: bid configuration: {ex}")
                        break
                    bids.append({"id": e["id"], "title": e.get("title", ""), **b})
        if pipe.get("weighted_total") is None and pipe.get("unweighted_entries"):
            notes.append("weighted pipeline not computed: no probability for " + ", ".join(pipe["unweighted_entries"]))

    projects, load_acc = [], {}
    for p in data.get("projects", []):
        pid = p.get("id", "?")
        try:
            plan = schedule.plan(_plan_input(p, today))
        except (ValueError, KeyError) as ex:
            checks.append(f"FAIL: project {pid}: {ex}")
            continue
        checks.append(f"PASS: project {pid} schedule inputs")
        ev = _earned_value(p, plan)
        late = bool(plan["deadline"] and plan["deadline"]["late"])
        behind = (ev is not None and ev["SPI"] is not None and ev["SPI"] < 1 - 1e-9)
        projects.append({"id": pid, "name": p.get("name", pid), "tender_id": p.get("tender_id"), "start": plan["start"], "finish": plan["finish"],
                         "duration_days": plan["duration_days"], "critical_path": plan["critical_path"], "deadline": plan["deadline"],
                         "earned_value": ev, "late_vs_deadline": late, "behind_schedule": behind, "notes": plan["notes"]})
        for r in plan["load"]:
            k = (r["owner"], r["week_start"])
            load_acc[k] = load_acc.get(k, 0.0) + r["demand_days"]
        if ev and ev["EAC"] is not None:
            notes.append(f"{pid}: EAC = BAC / CPI assumes cost performance to date continues")

    cap = data.get("capacity_days_per_week", {})
    ccal = data.get("calendar", {})
    cal = schedule.Calendar(today, ccal.get("workdays", [0, 1, 2, 3, 4]), [dt.date.fromisoformat(h) for h in ccal.get("holidays", [])])
    load, overloads = [], []
    for (o, w), v in sorted(load_acc.items()):
        row = {"owner": o, "week_start": w, "demand_days": v}
        if o in cap:
            row["capacity_days"] = cap[o] * cal.week_working_days(dt.date.fromisoformat(w)) / len(cal.workdays)
            row["utilisation"] = v / row["capacity_days"] if row["capacity_days"] > 0 else float("inf")
            if v > row["capacity_days"] + schedule.EPS:
                overloads.append(row)
        load.append(row)

    planned_ids = {p.get("tender_id") for p in data.get("projects", [])}
    needs_plan = [{"id": e["id"], "client": e.get("client", ""), "title": e.get("title", ""), "start_expected": e.get("start_expected"),
                   "value": e.get("value")} for e in ([] if terr else tenders) if e["stage"] == "won" and e["id"] not in planned_ids]

    pha_out = {}
    if data.get("pha"):
        acts = data["pha"].get("actions", [])
        st = pha.action_status(acts, today)
        ageing = {}
        for r in st["rows"]:
            if r["ageing"]:
                ageing[r["ageing"]] = ageing.get(r["ageing"], 0) + 1
        pha_out["actions"] = {"total": len(acts), "overdue": st["overdue"], "closure_pct": st["closure_pct"], "by_owner": st["by_owner"],
                              "high_risk_open": st["high_risk_open"], "ageing": ageing}
        pha_out["revalidations"] = [{"unit": r["unit"], **pha.revalidation(r["last_pha"], r.get("mocs_since", 0), r.get("incidents_since", 0),
                                                                           r.get("years", 5), today)} for r in data["pha"].get("revalidations", [])]

    head = {"today": today.isoformat(), "open_tenders": sum(e["stage"] in tr.OPEN for e in tenders), "deadlines_in_window": len(dl["upcoming"]),
            "missed_bids": len(dl["missed"]), "awards_to_chase": len(dl["chase"]), "starts_in_window": len(up), "projects": len(projects),
            "projects_behind": sum(p["behind_schedule"] or p["late_vs_deadline"] for p in projects), "overloaded_owner_weeks": len(overloads),
            "won_without_plan": len(needs_plan), "actions_overdue": pha_out.get("actions", {}).get("overdue"),
            "revalidations_overdue": sum(r["overdue"] for r in pha_out.get("revalidations", [])),
            "weighted_pipeline": pipe.get("weighted_total"), "booked": pipe.get("booked")}
    return {"headline": head, "deadlines": dl, "upcoming_projects": up, "pipeline": pipe, "win_rate": wr, "bids": bids, "projects": projects,
            "load": load, "overloads": overloads, "needs_plan": needs_plan, "pha": pha_out, "notes": notes, "checks": checks,
            "limits": "Screening and tracking aid: the register is only as current as its last update; no resource levelling; the toolkit "
                      "holds no rates, win rates or durations."}


def _table(rows: list[dict], cols: list[str]) -> str:
    if not rows:
        return "<p><em>none</em></p>"
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(_fmt(r.get(c)))}</td>" for c in cols) + "</tr>" for r in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.3g}" if abs(v) < 1000 else f"{v:,.0f}"
    if isinstance(v, (list, tuple)):
        return " ".join(str(x) for x in v)
    return str(v)


def write_html(rep: dict, path: str) -> None:
    h = rep["headline"]
    cards = "".join(f"<div class='c'><b>{html.escape(_fmt(v))}</b><span>{html.escape(k.replace('_', ' '))}</span></div>" for k, v in h.items())
    ev = [{"id": p["id"], "name": p["name"], "finish": p["finish"], **{k: p["earned_value"][k] for k in ("planned_percent", "reported_percent", "SPI", "CPI", "EAC")}}
          if p["earned_value"] else {"id": p["id"], "name": p["name"], "finish": p["finish"]} for p in rep["projects"]]
    pr = rep["pipeline"]
    stage_rows = [{"stage": s, **v} for s, v in pr.get("by_stage", {}).items()]
    pha_rows = [{"unit": r["unit"], "due": r["due"], "days_left": r["days_left"], "overdue": r["overdue"], "approach": r["approach"]}
                for r in rep["pha"].get("revalidations", [])]
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Portfolio status</title><style>body{font:14px system-ui,sans-serif;margin:16px;background:#fff;color:#1b1b1b}"
        "table{border-collapse:collapse;margin:6px 0 18px}td,th{border:1px solid #ccc;padding:3px 8px;text-align:left}th{background:#f0f0f0}"
        ".g{display:flex;flex-wrap:wrap;gap:8px}.c{border:1px solid #ccc;padding:6px 10px;min-width:110px}.c b{display:block;font-size:18px}"
        ".c span{color:#555;font-size:12px}h2{margin-top:22px}</style></head><body>",
        f"<h1>Portfolio status {html.escape(h['today'])}</h1><div class='g'>{cards}</div>",
        "<h2>Deadlines in the look-ahead window</h2>" + _table(rep["deadlines"]["upcoming"], ["id", "client", "title", "event", "date", "days_left", "stage"]),
        "<h2>Missed bids</h2>" + _table(rep["deadlines"]["missed"], ["id", "client", "title", "date", "days_left", "stage"]),
        "<h2>Submitted, award date passed (chase)</h2>" + _table(rep["deadlines"]["chase"], ["id", "client", "title", "date", "days_left"]),
        "<h2>Upcoming project starts</h2>" + _table(rep["upcoming_projects"], ["id", "client", "title", "date", "days_left", "confirmed", "value"]),
        "<h2>Pipeline by stage</h2>" + _table(stage_rows, ["stage", "count", "value", "weighted"]),
        "<h2>Bid scores</h2>" + _table(rep["bids"], ["id", "title", "score", "recommendation", "missing"]),
        "<h2>Projects</h2>" + _table(ev, ["id", "name", "finish", "planned_percent", "reported_percent", "SPI", "CPI", "EAC"]),
        "<h2>Capacity overloads</h2>" + _table(rep["overloads"], ["owner", "week_start", "demand_days", "capacity_days", "utilisation"]),
        "<h2>Won tenders without a plan</h2>" + _table(rep["needs_plan"], ["id", "client", "title", "start_expected", "value"]),
        "<h2>HAZOP revalidation</h2>" + _table(pha_rows, ["unit", "due", "days_left", "overdue", "approach"]),
        "<h2>Notes and limits</h2><ul>" + "".join(f"<li>{html.escape(n)}</li>" for n in rep["notes"] + [rep["limits"]]) + "</ul>",
        "<h2>Checks</h2><ul>" + "".join(f"<li>{html.escape(c)}</li>" for c in rep["checks"]) + "</ul></body></html>"]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
