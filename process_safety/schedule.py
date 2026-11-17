"""Dated critical-path schedule on a working calendar, with weekly resource load and progress against plan.

Model (docs/PROJECT_PIPELINE.md)
    * Activities with durations in working days (fractions allowed, zero = milestone) joined by links FS, SS or FF, each with a lag in
      working days (negative allowed). Time is a working-day index from the first working day on or after `start`; activity i occupies
      [ES, EF) with EF = ES + duration. Dates are the working dates of the days touched.
    * Forward pass: FS ES_j >= EF_i + lag; SS ES_j >= ES_i + lag; FF EF_j >= EF_i + lag; start-no-earlier; ES >= 0.
      Backward pass from the project finish (or from `finish_by` when given). Total float = LF - EF. Critical = within 1e-9 of the
      minimum float (zero without a deadline; the least-float path when a deadline is tighter than the plan).
    * Weekly load: an activity with an owner spreads its effort (default: its duration, i.e. one person full time) evenly over the
      working days it touches. Capacity per owner (working days per week) is scaled by the working days in each week, so a holiday week
      has less. Overload is reported, never levelled.
    * Progress: with a status date, planned percent of each activity is the share of its span elapsed at the end of the status day;
      reported percent_complete is carried through for the earned-value report in `portfolio`.
Not modelled: resource levelling, activity calendars (one calendar per schedule), constraints other than start-no-earlier and the
project deadline, personal leave, costs. Every number is an input; none is typed in.
"""
from __future__ import annotations

import bisect
import datetime as dt
import math

EPS = 1e-9
LINKS = ("FS", "SS", "FF")
ALL_DAYS = [0, 1, 2, 3, 4, 5, 6]


def _iso(s):
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


class Calendar:
    """Working days of the week (0 = Monday) minus holidays; maps a working-day index to a date and back."""

    def __init__(self, start: dt.date, workdays=(0, 1, 2, 3, 4), holidays=()):
        self.workdays = tuple(sorted(set(workdays)))
        self.holidays = frozenset(holidays)
        d = start
        while not self.is_work(d):
            d += dt.timedelta(days=1)
        self.first = d
        self._dates = [d]
        self._cursor = d

    def is_work(self, d: dt.date) -> bool:
        return d.weekday() in self.workdays and d not in self.holidays

    def _extend_to_index(self, i):
        while len(self._dates) <= i:
            self._step()

    def _step(self):
        self._cursor += dt.timedelta(days=1)
        if self.is_work(self._cursor):
            self._dates.append(self._cursor)

    def date_of(self, i: int) -> dt.date:
        self._extend_to_index(i)
        return self._dates[i]

    def count_through(self, d: dt.date) -> int:
        """Working days from the first one up to and including d."""
        while self._cursor < d:
            self._step()
        return bisect.bisect_right(self._dates, d)

    def week_working_days(self, monday: dt.date) -> int:
        return sum(self.is_work(monday + dt.timedelta(days=k)) for k in range(7))


def _links(a):
    out = []
    for p in a.get("predecessors", []):
        if isinstance(p, str):
            out.append((p, "FS", 0.0))
        else:
            out.append((p.get("id"), p.get("type", "FS"), p.get("lag", 0.0)))
    return out


def _topo(acts):
    ids = list(acts)
    indeg = {i: len(_links(acts[i])) for i in ids}
    succ = {i: [] for i in ids}
    for i in ids:
        for p, _, _ in _links(acts[i]):
            succ[p].append(i)
    order, q = [], [i for i in ids if indeg[i] == 0]
    while q:
        n = q.pop(0)
        order.append(n)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                q.append(s)
    return order if len(order) == len(ids) else None


def check(data: dict) -> list[str]:
    errs = []
    if _iso(data.get("start")) is None:
        errs.append("start must be an ISO date (YYYY-MM-DD)")
    cal = data.get("calendar", {})
    wd = cal.get("workdays", [0, 1, 2, 3, 4])
    if not wd or any(not isinstance(x, int) or not 0 <= x <= 6 for x in wd):
        errs.append("calendar.workdays needs at least one weekday number 0-6 (0 = Monday)")
    for h in cal.get("holidays", []):
        if _iso(h) is None:
            errs.append(f"holiday {h!r} is not an ISO date")
    for k in ("finish_by", "status_date"):
        if k in data and _iso(data[k]) is None:
            errs.append(f"{k} must be an ISO date")
    acts = data.get("activities", [])
    if not acts:
        return errs + ["no activities"]
    ids = [a.get("id") for a in acts]
    if any(not isinstance(i, str) or not i for i in ids):
        errs.append("every activity needs a non-empty string id")
    if len(ids) != len(set(ids)):
        errs.append("duplicate activity id")
    for a in acts:
        i = a.get("id")
        d = a.get("duration_days")
        if not isinstance(d, (int, float)) or isinstance(d, bool) or d < 0 or not math.isfinite(d):
            errs.append(f"{i}: duration_days must be a number >= 0")
        for k in ("effort_days",):
            if k in a and (not isinstance(a[k], (int, float)) or a[k] < 0):
                errs.append(f"{i}: {k} must be >= 0")
        if "percent_complete" in a and not (isinstance(a["percent_complete"], (int, float)) and 0 <= a["percent_complete"] <= 100):
            errs.append(f"{i}: percent_complete must be in [0, 100]")
        if "start_no_earlier" in a and _iso(a["start_no_earlier"]) is None:
            errs.append(f"{i}: start_no_earlier must be an ISO date")
        for p, t, lag in _links(a):
            if p not in ids:
                errs.append(f"{i}: unknown predecessor {p}")
            if t not in LINKS:
                errs.append(f"{i}: link type {t!r} must be one of FS, SS, FF")
            if not isinstance(lag, (int, float)) or not math.isfinite(lag):
                errs.append(f"{i}: lag must be a number")
    for o, c in data.get("capacity_days_per_week", {}).items():
        if not isinstance(c, (int, float)) or c < 0:
            errs.append(f"capacity for {o} must be >= 0")
    if not errs and _topo({a["id"]: a for a in acts}) is None:
        errs.append("precedence network has a cycle")
    return errs


def _calendar(data):
    cal = data.get("calendar", {})
    return Calendar(_iso(data["start"]), cal.get("workdays", [0, 1, 2, 3, 4]), [dt.date.fromisoformat(h) for h in cal.get("holidays", [])])


def plan(data: dict) -> dict:
    errs = check(data)
    if errs:
        raise ValueError("; ".join(errs))
    cal = _calendar(data)
    acts = {a["id"]: a for a in data["activities"]}
    order = _topo(acts)
    dur = {i: float(acts[i]["duration_days"]) for i in order}
    es, ef = {}, {}
    for i in order:
        lo = 0.0
        if acts[i].get("start_no_earlier"):
            lo = max(lo, float(cal.count_through(dt.date.fromisoformat(acts[i]["start_no_earlier"]) - dt.timedelta(days=1))))
        for p, t, lag in _links(acts[i]):
            if t == "FS":
                lo = max(lo, ef[p] + lag)
            elif t == "SS":
                lo = max(lo, es[p] + lag)
            else:
                lo = max(lo, ef[p] + lag - dur[i])
        es[i] = lo
        ef[i] = lo + dur[i]
    T = max(ef.values())
    deadline = None
    T_lim = T
    if data.get("finish_by"):
        T_lim = float(cal.count_through(dt.date.fromisoformat(data["finish_by"])))
        deadline = {"finish_by": data["finish_by"], "slack_working_days": T_lim - T, "late": T_lim - T < -EPS}
    succ = {i: [] for i in order}
    for j in order:
        for p, t, lag in _links(acts[j]):
            succ[p].append((j, t, lag))
    lf = {}
    for i in reversed(order):
        v = T_lim
        for j, t, lag in succ[i]:
            ls_j = lf[j] - dur[j]
            v = min(v, ls_j - lag if t == "FS" else ls_j - lag + dur[i] if t == "SS" else lf[j] - lag)
        lf[i] = v
    tf = {i: lf[i] - ef[i] for i in order}
    fmin = min(tf.values())
    crit = [i for i in order if tf[i] - fmin < EPS]

    t_status = None
    if data.get("status_date"):
        t_status = cal.count_through(dt.date.fromisoformat(data["status_date"]))

    rows = []
    for i in order:
        a = acts[i]
        s_idx = int(math.floor(es[i] + EPS))
        f_idx = s_idx if dur[i] == 0 else int(math.ceil(ef[i] - EPS)) - 1
        row = {"id": i, "name": a.get("name", i), "owner": a.get("owner", ""), "duration_days": dur[i], "es": es[i], "ef": ef[i],
               "start": cal.date_of(s_idx).isoformat(), "finish": cal.date_of(max(f_idx, s_idx)).isoformat(),
               "total_float_days": tf[i], "critical": i in crit}
        if "percent_complete" in a:
            row["percent_complete"] = a["percent_complete"]
        if t_status is not None:
            row["planned_percent"] = (100.0 if t_status >= es[i] - EPS else 0.0) if dur[i] == 0 else 100.0 * min(1.0, max(0.0, (t_status - es[i]) / dur[i]))
        rows.append(row)

    load = _load(cal, acts, order, dur, es, ef)
    caps = data.get("capacity_days_per_week", {})
    for r in load:
        cap = caps.get(r["owner"])
        if cap is not None:
            r["capacity_days"] = cap * cal.week_working_days(dt.date.fromisoformat(r["week_start"])) / len(cal.workdays)
            r["utilisation"] = r["demand_days"] / r["capacity_days"] if r["capacity_days"] > 0 else math.inf
    overloads = [r for r in load if "capacity_days" in r and r["demand_days"] > r["capacity_days"] + EPS]
    notes = []
    if any(a.get("owner") and "effort_days" not in a for a in acts.values()):
        notes.append("activities with an owner and no effort_days are loaded at one person full time over their duration")
    if t_status is not None and any("percent_complete" not in a for a in acts.values()):
        notes.append("activities without percent_complete count as 0 percent in the earned-value report")
    return {"start": cal.first.isoformat(), "finish": max(r["finish"] for r in rows), "duration_days": T, "critical_path": crit,
            "float_min": fmin, "deadline": deadline, "status_working_days": t_status, "activities": rows, "load": load,
            "overloads": overloads, "notes": notes}


def _load(cal, acts, order, dur, es, ef):
    acc = {}
    for i in order:
        a = acts[i]
        owner = a.get("owner")
        if not owner or dur[i] <= 0:
            continue
        effort = float(a.get("effort_days", dur[i]))
        for k in range(int(math.floor(es[i] + EPS)), int(math.ceil(ef[i] - EPS))):
            overlap = max(0.0, min(ef[i], k + 1) - max(es[i], k))
            if overlap <= 0:
                continue
            d = cal.date_of(k)
            monday = d - dt.timedelta(days=d.weekday())
            acc[(owner, monday.isoformat())] = acc.get((owner, monday.isoformat()), 0.0) + effort * overlap / dur[i]
    return [{"owner": o, "week_start": w, "demand_days": v} for (o, w), v in sorted(acc.items())]


def from_shutdown(sd: dict, start: str, workdays=None) -> dict:
    """Schedule input from a `shutdown` model: mode durations, same links, calendar days unless workdays is given."""
    acts = [{"id": a["id"], "name": a.get("name", a["id"]), "duration_days": a["duration_days"]["mode"],
             "predecessors": list(a.get("predecessors", [])), "safety_critical": bool(a.get("safety_critical", False))}
            for a in sd["activities"]]
    return {"start": start, "calendar": {"workdays": list(workdays or ALL_DAYS)}, "activities": acts}


def gantt_svg(p: dict, path: str, width: int = 900) -> None:
    rows = p["activities"]
    left, top, rh = 220, 30, 22
    t_end = max(r["ef"] for r in rows) or 1.0
    scale = (width - left - 20) / t_end
    h = top + rh * len(rows) + 30
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" font-family="sans-serif" font-size="11">',
           f'<rect width="{width}" height="{h}" fill="#ffffff"/>',
           f'<text x="8" y="16" font-weight="bold">Schedule {p["start"]} to {p["finish"]} ({p["duration_days"]:g} working days; red = critical)</text>']
    step = max(1, int(round(t_end / 10)))
    for t in range(0, int(math.ceil(t_end)) + 1, step):
        x = left + t * scale
        out.append(f'<line x1="{x:.1f}" y1="{top - 4}" x2="{x:.1f}" y2="{h - 22}" stroke="#dddddd"/>')
        out.append(f'<text x="{x:.1f}" y="{h - 8}" text-anchor="middle" fill="#555555">{t}</text>')
    for n, r in enumerate(rows):
        y = top + n * rh
        label = (r["name"] if len(r["name"]) <= 32 else r["name"][:31] + "…")
        out.append(f'<text x="8" y="{y + 14}">{_esc(label)}</text>')
        x, w = left + r["es"] * scale, max(r["duration_days"] * scale, 2.0)
        out.append(f'<rect x="{x:.1f}" y="{y + 3}" width="{w:.1f}" height="{rh - 8}" fill="{"#c0392b" if r["critical"] else "#2e6da4"}"/>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
