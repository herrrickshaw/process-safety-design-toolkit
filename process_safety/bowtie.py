"""Quantified bow-tie: threats -> prevention barriers -> top event -> mitigation barriers -> consequences, with escalation
factors, barrier importance and a safety-critical-element (SCE) list. Draws the bow-tie as SVG.

    f_top            = sum_i f_threat,i x prod(PFD of prevention barriers on threat i)
    f_consequence,j  = f_top x P(j | top) x prod(PFD of mitigation barriers on consequence j)
A barrier's PFD can be degraded by escalation factors (`escalation`: [{"factor", "pfd_if_present", "p_present"}]):
    PFD_eff = (1 - p) PFD + p PFD_degraded.
Threat frequencies may come from a fault tree (reliability.FaultTree) instead of a number.

Importance per barrier (same barrier name may appear on several legs and is treated as ONE physical barrier):
    RRW (risk reduction worth)     = R(barrier perfect, PFD = 0)^-1 x R  ... reported as R / R(PFD=0)
    RAW (risk achievement worth)   = R(barrier failed, PFD = 1) / R
Risk R is the severity-weighted consequence frequency sum (severity weights from the study; 1 if absent).
Barriers whose RAW exceeds `sce_raw_threshold` (default 10, a common screening choice - set yours) are listed as SCEs.
Independence of barriers is assumed (as in LOPA); a barrier that is not independent of its initiator must not be credited.
"""
from __future__ import annotations

import csv
import html
import math

from .reliability import FaultTree


def _threat_freq(t: dict) -> float:
    if "fault_tree" in t:
        spec = t["fault_tree"]
        ft = FaultTree()
        for n, p in spec["basic"].items():
            ft.event(n, p)
        for n, g in spec["gates"].items():
            ft.gate(n, g[0], g[1], g[2] if len(g) > 2 else None)
        return spec.get("initiator_per_yr", 1.0) * ft.probability(spec["top"])
    return t["frequency_per_yr"]


def _pfd(b: dict, override: dict) -> float:
    if b["name"] in override:
        return override[b["name"]]
    p = b["pfd"]
    for e in b.get("escalation", []):
        p = (1 - e["p_present"]) * p + e["p_present"] * e["pfd_if_present"]
    return min(1.0, p)


def evaluate(bt: dict, override: dict | None = None) -> dict:
    ov = override or {}
    threats = []
    for t in bt["threats"]:
        f0 = _threat_freq(t)
        f = f0 * math.prod(_pfd(b, ov) for b in t.get("barriers", []))
        threats.append({"name": t["name"], "initiating_per_yr": f0, "contribution_per_yr": f})
    f_top = sum(t["contribution_per_yr"] for t in threats)
    cons = []
    for c in bt["consequences"]:
        unm = f_top * c["probability"]
        mit = unm * math.prod(_pfd(b, ov) for b in c.get("barriers", []))
        cons.append({"name": c["name"], "probability_given_top": c["probability"], "unmitigated_per_yr": unm, "mitigated_per_yr": mit,
                     "severity_weight": c.get("severity_weight", 1.0), "category": c.get("category", "")})
    risk = sum(c["mitigated_per_yr"] * c["severity_weight"] for c in cons)
    return {"top_event": bt["top_event"], "top_per_yr": f_top, "threats": threats, "consequences": cons, "risk": risk}


def barriers(bt: dict) -> dict:
    out = {}
    for side, legs in (("prevention", bt["threats"]), ("mitigation", bt["consequences"])):
        for leg in legs:
            for b in leg.get("barriers", []):
                d = out.setdefault(b["name"], {"name": b["name"], "side": side, "legs": [], "pfd": b["pfd"], "type": b.get("type", ""),
                                               "owner": b.get("owner", ""), "escalation": [e["factor"] for e in b.get("escalation", [])]})
                d["legs"].append(leg["name"])
                if d["side"] != side:
                    d["side"] = "both"
    return out


def importance(bt: dict, sce_raw_threshold: float = 10.0) -> list[dict]:
    base = evaluate(bt)["risk"]
    rows = []
    for name, b in barriers(bt).items():
        r0 = evaluate(bt, {name: 0.0})["risk"]
        r1 = evaluate(bt, {name: 1.0})["risk"]
        rrw = base / r0 if r0 > 0 else math.inf
        raw = r1 / base if base > 0 else math.inf
        rows.append({**b, "legs": "; ".join(b["legs"]), "escalation": "; ".join(b["escalation"]), "RRW": rrw, "RAW": raw,
                     "SCE": raw >= sce_raw_threshold})
    return sorted(rows, key=lambda r: -r["RAW"])


def check(bt: dict) -> list[str]:
    errs = []
    if not bt.get("threats") or not bt.get("consequences"):
        errs.append("bow-tie needs at least one threat and one consequence")
    ps = sum(c["probability"] for c in bt.get("consequences", []))
    if ps > 1 + 1e-9:
        errs.append(f"consequence probabilities given the top event sum to {ps:.3f} > 1")
    for leg in bt.get("threats", []) + bt.get("consequences", []):
        for b in leg.get("barriers", []):
            if not 0 < b["pfd"] <= 1:
                errs.append(f"barrier {b['name']}: PFD {b['pfd']} outside (0, 1]")
            for e in b.get("escalation", []):
                if not (0 <= e["p_present"] <= 1 and b["pfd"] <= e["pfd_if_present"] <= 1):
                    errs.append(f"barrier {b['name']}: escalation factor {e['factor']} needs 0<=p_present<=1 and PFD <= pfd_if_present <= 1")
    for t in bt.get("threats", []):
        if "fault_tree" not in t and not t.get("frequency_per_yr", -1) >= 0:
            errs.append(f"threat {t['name']}: frequency_per_yr >= 0 or a fault_tree is required")
    return errs


def svg(bt: dict, res: dict | None = None, w: int = 1100) -> str:
    res = res or evaluate(bt)
    th, co = bt["threats"], bt["consequences"]
    n = max(len(th), len(co), 1)
    rowh = 70
    h = 60 + n * rowh
    cx, cy = w / 2, h / 2
    NAVY, GOLD, RED, GREEN = "#14284b", "#c9a227", "#c0392b", "#1e8449"
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="11">']

    def box(x, y, bw, bh, text, fill, col="#fff"):
        lines = [text[i:i + 24] for i in range(0, len(text), 24)][:3]
        t = "".join(f'<tspan x="{x + bw / 2}" dy="{0 if k == 0 else 12}">{html.escape(l)}</tspan>' for k, l in enumerate(lines))
        return (f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="4" fill="{fill}"/>'
                f'<text x="{x + bw / 2}" y="{y + bh / 2 - 6 * (len(lines) - 1) + 4}" text-anchor="middle" fill="{col}">{t}</text>')
    p.append(f'<circle cx="{cx}" cy="{cy}" r="58" fill="{RED}"/>')
    p.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="#fff" font-weight="bold">{html.escape(bt["top_event"][:22])}</text>'
             f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" fill="#fff">{res["top_per_yr"]:.2e} /yr</text>')
    for side, legs, xs in (("L", th, 10), ("R", co, w - 170)):
        for i, leg in enumerate(legs):
            y = 30 + i * rowh + (n - len(legs)) * rowh / 2
            label = leg["name"]
            r = (res["threats"] if side == "L" else res["consequences"])[i]
            val = r["initiating_per_yr"] if side == "L" else r["mitigated_per_yr"]
            p.append(f'<line x1="{xs + (160 if side == "L" else 0)}" y1="{y + 22}" x2="{cx + (-58 if side == "L" else 58)}" y2="{cy}" stroke="#9aa5b1"/>')
            p.append(box(xs, y, 160, 44, f"{label} ({val:.1e}/yr)", NAVY if side == "L" else "#7f8c8d"))
            bs = leg.get("barriers", [])
            for k, b in enumerate(bs):
                t = (k + 1) / (len(bs) + 1)
                x0 = xs + 160 if side == "L" else cx + 58
                x1 = cx - 58 if side == "L" else xs
                bx = x0 + (x1 - x0) * t - 38
                by = (y + 22) + (cy - (y + 22)) * t - 14 if side == "L" else cy + ((y + 22) - cy) * t - 14
                p.append(box(bx, by, 76, 28, f"{b['name'][:22]}", GOLD if b.get("type") != "procedural" else "#e8d9a8", NAVY))
    p.append(f'<text x="10" y="{h - 8}" fill="{GREEN}">threats (left) &#8594; prevention barriers &#8594; top event &#8594; mitigation barriers &#8594; consequences (right)</text></svg>')
    return "".join(p)


def report(bt: dict, path_prefix: str, sce_raw_threshold: float = 10.0) -> dict:
    res = evaluate(bt)
    imp = importance(bt, sce_raw_threshold)
    with open(path_prefix + "_barriers.csv", "w", newline="", encoding="utf-8-sig") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(imp[0]) if imp else ["name"])
        wr.writeheader()
        wr.writerows(imp)
    rows = "".join(f"<tr><td>{html.escape(b['name'])}</td><td>{b['side']}</td><td>{b['pfd']:.1e}</td><td>{b['RRW']:.3g}</td>"
                   f"<td>{b['RAW']:.3g}</td><td>{'YES' if b['SCE'] else ''}</td><td>{html.escape(b['escalation'])}</td></tr>" for b in imp)
    cons = "".join(f"<tr><td>{html.escape(c['name'])}</td><td>{c['unmitigated_per_yr']:.2e}</td><td>{c['mitigated_per_yr']:.2e}</td></tr>"
                   for c in res["consequences"])
    doc = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Bow-tie: {html.escape(bt['top_event'])}</title><style>"
           "body{font-family:Helvetica,Arial;max-width:1150px;margin:20px auto;color:#1f2933}table{border-collapse:collapse;width:100%;font-size:12px}"
           "th{background:#14284b;color:#fff;padding:5px;text-align:left}td{border-bottom:1px solid #e3e6ea;padding:4px}</style></head><body>"
           f"<h1 style='color:#14284b'>Bow-tie: {html.escape(bt['top_event'])}</h1>{svg(bt, res)}"
           f"<h2>Consequences</h2><table><tr><th>Consequence</th><th>Unmitigated /yr</th><th>Mitigated /yr</th></tr>{cons}</table>"
           f"<h2>Barrier importance (SCE if RAW &#8805; {sce_raw_threshold:g})</h2><table><tr><th>Barrier</th><th>Side</th><th>PFD</th><th>RRW</th>"
           f"<th>RAW</th><th>SCE</th><th>Escalation factors</th></tr>{rows}</table></body></html>")
    with open(path_prefix + "_bowtie.html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    return {"result": res, "importance": imp, "files": [path_prefix + "_barriers.csv", path_prefix + "_bowtie.html"]}
