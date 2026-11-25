"""Tender and upcoming-project register: deadlines, missed bids, upcoming starts, weighted pipeline, bid score, win rate, intake triage.

The register holds what a person or a feed put in it. This module does not fetch anything from tender portals (stdlib only, offline,
and portal terms differ); `triage` only matches keyword rules against items the caller pastes or exports. All arithmetic is on dates
and values the caller gives. Stage probabilities, bid weights and thresholds are inputs: the toolkit holds no win-rate data, and the
weighted pipeline is "not computed" (None) when any open entry has neither a probability of its own nor a stage probability.

Entry: {"id", "client", "title", "service", "stage", "value", "probability"?, "published"?, "clarification_deadline"?,
"submission_deadline"?, "award_expected"?, "start_expected"?, "scores"?: {criterion: number}, "scope_text"?}. Dates are ISO.
Dates within an entry must be in the order published <= clarification <= submission <= award <= start.
"""
from __future__ import annotations

import datetime as dt
import re

STAGES = ("identified", "qualifying", "bid", "submitted", "won", "lost", "no_bid", "cancelled")
OPEN = ("identified", "qualifying", "bid", "submitted")
PRE_SUBMISSION = ("identified", "qualifying", "bid")
DATE_ORDER = ("published", "clarification_deadline", "submission_deadline", "award_expected", "start_expected")


def _d(s):
    return dt.date.fromisoformat(s) if s else None


def check(data: dict) -> list[str]:
    errs = []
    ents = data.get("tenders", [])
    ids = [e.get("id") for e in ents]
    if len(ids) != len(set(ids)):
        errs.append("duplicate tender id")
    for e in ents:
        i = e.get("id")
        if not i:
            errs.append("every entry needs an id")
        if e.get("stage") not in STAGES:
            errs.append(f"{i}: stage {e.get('stage')!r} must be one of {', '.join(STAGES)}")
        v = e.get("value")
        if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0):
            errs.append(f"{i}: value must be a number >= 0")
        p = e.get("probability")
        if p is not None and not (isinstance(p, (int, float)) and 0 <= p <= 1):
            errs.append(f"{i}: probability must be in [0, 1]")
        parsed, bad = [], False
        for k in DATE_ORDER:
            if e.get(k) is None:
                continue
            try:
                parsed.append((k, dt.date.fromisoformat(e[k])))
            except (TypeError, ValueError):
                errs.append(f"{i}: {k} {e[k]!r} is not an ISO date")
                bad = True
        if not bad:
            for (k1, d1), (k2, d2) in zip(parsed, parsed[1:]):
                if d2 < d1:
                    errs.append(f"{i}: dates out of order ({k2} {d2} is before {k1} {d1})")
    for s, p in data.get("stage_probability", {}).items():
        if s not in STAGES:
            errs.append(f"stage_probability: unknown stage {s!r}")
        elif not (isinstance(p, (int, float)) and 0 <= p <= 1):
            errs.append(f"stage_probability[{s}] must be in [0, 1]")
    if "today" in data:
        try:
            dt.date.fromisoformat(data["today"])
        except (TypeError, ValueError):
            errs.append("today must be an ISO date")
    return errs


def _row(e, event, d, today):
    return {"id": e["id"], "client": e.get("client", ""), "title": e.get("title", ""), "service": e.get("service", ""),
            "stage": e["stage"], "event": event, "date": d.isoformat(), "days_left": (d - today).days}


def deadlines(entries: list[dict], today: dt.date, horizon_days: int) -> dict:
    """upcoming: events in [today, today + horizon]; missed: submission deadline passed before the entry reached `submitted`;
    chase: submitted and the expected award date has passed."""
    up, missed, chase = [], [], []
    end = today + dt.timedelta(days=horizon_days)
    for e in entries:
        st = e["stage"]
        events = []
        if st in OPEN:
            events += [(k, _d(e.get(k))) for k in ("clarification_deadline", "submission_deadline", "award_expected")]
        if st == "won":
            events.append(("start_expected", _d(e.get("start_expected"))))
        for k, d in events:
            if d is None:
                continue
            if k in ("clarification_deadline", "submission_deadline") and st not in PRE_SUBMISSION:
                continue
            if today <= d <= end:
                up.append(_row(e, k, d, today))
        sub = _d(e.get("submission_deadline"))
        if st in PRE_SUBMISSION and sub is not None and sub < today:
            missed.append(_row(e, "submission_deadline", sub, today))
        aw = _d(e.get("award_expected"))
        if st == "submitted" and aw is not None and aw < today:
            chase.append(_row(e, "award_expected", aw, today))
    up.sort(key=lambda r: (r["days_left"], r["id"]))
    return {"upcoming": up, "missed": missed, "chase": chase}


def upcoming_projects(entries: list[dict], today: dt.date, horizon_days: int, include_open: bool = False) -> list[dict]:
    end = today + dt.timedelta(days=horizon_days)
    out = []
    for e in entries:
        d = _d(e.get("start_expected"))
        if d is None or not today <= d <= end:
            continue
        if e["stage"] == "won" or (include_open and e["stage"] in OPEN):
            r = _row(e, "start_expected", d, today)
            r["confirmed"] = e["stage"] == "won"
            r["value"] = e.get("value")
            out.append(r)
    out.sort(key=lambda r: (r["date"], r["id"]))
    return out


def weighted_pipeline(entries: list[dict], stage_probability: dict) -> dict:
    """Value times probability over open entries. weighted_total is None when any open entry cannot be weighted."""
    by_stage, unweighted, total, no_date = {}, [], 0.0, 0.0
    by_month: dict[str, float] = {}
    for e in entries:
        if e["stage"] not in OPEN:
            continue
        v = float(e.get("value") or 0.0)
        p = e.get("probability", stage_probability.get(e["stage"]))
        s = by_stage.setdefault(e["stage"], {"count": 0, "value": 0.0, "weighted": 0.0})
        s["count"] += 1
        s["value"] += v
        if p is None:
            unweighted.append(e["id"])
            continue
        w = v * p
        s["weighted"] += w
        total += w
        if e.get("award_expected"):
            m = e["award_expected"][:7]
            by_month[m] = by_month.get(m, 0.0) + w
        else:
            no_date += w
    ok = not unweighted
    if not ok:
        for s in by_stage.values():
            s["weighted"] = None
    return {"weighted_total": total if ok else None, "by_stage": by_stage, "by_award_month": dict(sorted(by_month.items())) if ok else {},
            "unscheduled_weighted": no_date if ok else None, "unweighted_entries": unweighted,
            "open_value": sum(s["value"] for s in by_stage.values()),
            "booked": sum(float(e.get("value") or 0.0) for e in entries if e["stage"] == "won")}


def bid_score(entry: dict, cfg: dict) -> dict:
    """score = sum(w_i s_i) / (scale_max sum(w_i)) in [0, 1]; thresholds are required inputs."""
    for k in ("weights", "scale_max", "bid_threshold", "review_threshold"):
        if k not in cfg:
            raise ValueError(f"bid configuration needs {k}")
    w, smax = cfg["weights"], cfg["scale_max"]
    if not w or sum(w.values()) <= 0 or smax <= 0 or min(w.values()) < 0:
        raise ValueError("weights must be non-negative with a positive sum, and scale_max positive")
    sc = entry.get("scores", {})
    missing = [k for k in w if k not in sc]
    if missing:
        return {"score": None, "recommendation": "incomplete", "missing": missing}
    for k in w:
        if not 0 <= sc[k] <= smax:
            raise ValueError(f"score {k} must be in [0, {smax}]")
    s = sum(w[k] * sc[k] for k in w) / (smax * sum(w.values()))
    rec = "bid" if s >= cfg["bid_threshold"] else "review" if s >= cfg["review_threshold"] else "no bid"
    return {"score": s, "recommendation": rec, "missing": []}


def win_rate(entries: list[dict]) -> dict:
    def tally(es):
        won = sum(e["stage"] == "won" for e in es)
        lost = sum(e["stage"] == "lost" for e in es)
        return {"won": won, "lost": lost, "rate": won / (won + lost) if won + lost else None}
    svc = {}
    for e in entries:
        if e["stage"] in ("won", "lost"):
            svc.setdefault(e.get("service", ""), []).append(e)
    return {"overall": tally(entries), "by_service": {k: tally(v) for k, v in sorted(svc.items())}}


def _has(term, text):
    return re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", text) is not None


def triage(items: list[dict], rules: dict) -> list[dict]:
    """Candidates from raw items {title, text?, source?}. Whole-word, case-insensitive matches. An excluded term anywhere drops the
    item; an item is kept when a service term or an include term matches. Order of the input is kept."""
    out = []
    for it in items:
        text = f"{it.get('title', '')} {it.get('text', '')}".lower()
        if any(_has(t, text) for t in rules.get("exclude", [])):
            continue
        services = [s for s, terms in rules.get("services", {}).items() if any(_has(t, text) for t in terms)]
        terms = [t for ts in rules.get("services", {}).values() for t in ts if _has(t, text)]
        terms += [t for t in rules.get("include", []) if _has(t, text)]
        if not services and not any(_has(t, text) for t in rules.get("include", [])):
            continue
        out.append({"title": it.get("title", ""), "source": it.get("source", ""), "services": services, "terms": terms, "score": len(terms),
                    "suggested_entry": {"id": None, "title": it.get("title", ""), "source": it.get("source", ""),
                                        "service": services[0] if services else "", "stage": "identified"}})
    return out
