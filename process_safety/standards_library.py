"""Standards and literature library: process-safety, design and materials documents (`data/standards_library.json`) and a
reading map by design activity and material product form (`data/design_recommendations.json`).

It is an index. No standard's text is reproduced, editions are not recorded, and the recommendation map says which documents to
open, not what they require. `title_source` is 'publisher-page' when the title was read from the publisher's page by
scripts/check_standards_library.py 
'search-listing' when it came from a web-search result and 'compiler' when it was typed and not compared. `check` is the result of
one automated request: ok, pdf, missing, blocked (the site refuses automated clients) or error; 'robots' means the site's
robots.txt disallows this kind of agent, so the page was not requested.
"""
from __future__ import annotations

import json
from importlib import resources

KINDS = ["regulation", "standard", "guidance", "book", "database", "data-tool", "investigation", "journal", "association",
         "course", "access-route", "article"]

CATEGORIES = {
    "regulation": "Laws and regulations by jurisdiction",
    "psm": "Process safety management frameworks and guidance",
    "hazard-risk": "Hazard identification, risk assessment and reliability",
    "instrumented-safety": "Functional safety, instrumentation, alarms and control-system security",
    "relief-flare": "Relief, depressuring, venting and flare",
    "equipment-codes": "Pressure equipment, piping, tanks, heat transfer and rotating equipment codes",
    "integrity-inspection": "Mechanical integrity, inspection and fitness for service",
    "corrosion-materials-selection": "Materials selection, corrosion and damage mechanisms",
    "astm-pipe-tube": "ASTM steel pipe and tube specifications",
    "astm-plate-structural": "ASTM plate and structural steel specifications",
    "astm-forging-casting-fitting": "ASTM forging, casting, flange and fitting specifications",
    "astm-bolting-bar": "ASTM bolting, bar and fastener specifications",
    "astm-nonferrous": "ASTM nickel, titanium, zirconium, aluminium and copper specifications",
    "astm-nonmetallic": "ASTM plastics, FRP, elastomer, gasket and insulation standards",
    "astm-test-mechanical": "ASTM mechanical, metallurgical and chemical-analysis test methods",
    "astm-test-corrosion": "ASTM corrosion test methods and practices",
    "astm-test-hydrogen-oxygen": "ASTM oxygen-compatibility and hydrogen-embrittlement standards",
    "astm-test-nde": "ASTM nondestructive examination standards",
    "astm-test-flammability-reactivity": "ASTM flash point, flammability, dust and thermal-reactivity test methods",
    "astm-test-fire": "ASTM fire test methods",
    "astm-test-electrical-ppe": "ASTM electrical, arc-flash and protective-equipment standards",
    "astm-test-gas-analysis": "ASTM gas analysis methods",
    "welding-nde": "Welding, hot work and examination qualification",
    "fire-protection": "Fire protection: active, passive, detection and fire modelling",
    "explosion-dust": "Explosion, deflagration, blast and combustible dust",
    "hazardous-area-electrical": "Hazardous areas, electrical safety, static and lightning",
    "layout-human-factors": "Layout, facility siting, buildings and human factors",
    "reactive-hazards": "Reactive hazards, flammable liquids and hazardous materials storage",
    "substance-specific": "Substance-specific and energy-transition safety",
    "pipeline-offshore": "Pipelines and offshore",
    "safe-operations": "Safe work and operations",
    "consequence-reports": "Open research reports on fire and release modelling",
    "data-tools": "Modelling tools, chemical property and exposure data",
    "incidents": "Incident investigations and loss databases",
    "india-standards": "India: standards and agencies",
    "books": "Books, handbooks and learning",
    "journals-research": "Journals, open-access repositories and research centres",
    "articles-digital-refining": "Digital Refining articles on safety and design (unread; found by search)",
    "access-routes": "Where to read or buy standards lawfully",
}

_CACHE: dict[str, dict] = {}


def _load(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = json.loads(resources.files("process_safety").joinpath("data", name).read_text(encoding="utf-8"))
    return _CACHE[name]


def entries() -> list[dict]:
    return list(_load("standards_library.json")["entries"])


def recommendations() -> dict:
    return _load("design_recommendations.json")


def by_designation() -> dict[str, dict]:
    return {e["designation"]: e for e in entries()}


def search(text: str | None = None, category: str | None = None, body: str | None = None, region: str | None = None,
           kind: str | None = None, access: str | None = None) -> list[dict]:
    """All filters are optional and combined with AND. `text` matches every word against designation, title, body, topics and note."""
    words = (text or "").lower().split()
    out = []
    for e in entries():
        if category and e["category"] != category:
            continue
        if body and body.lower() != e["body"].lower():
            continue
        if region and e["region"].lower() != region.lower():
            continue
        if kind and e["kind"] != kind:
            continue
        if access and e["access"] != access:
            continue
        hay = " ".join([e["designation"], e["title"], e["body"], e["note"], e["category"], " ".join(e["topics"])]).lower()
        if all(w in hay for w in words):
            out.append(e)
    return out


def activity(key: str) -> dict | None:
    """One activity or material row of the reading map, with each designation resolved to its catalogue entry."""
    r = recommendations()
    idx = by_designation()
    for row in r["activities"] + r["materials"]:
        if row["id"] == key:
            return {"id": row["id"], "title": row["title"], "documents": [idx[d] for d in row["documents"]]}
    return None


TITLE_MARK = {"publisher-page": "P", "search-listing": "S", "compiler": "C"}


def _cell(s: str) -> str:
    return s.replace("|", "\\|")


def _link(e: dict) -> str:
    pdf = f" ([PDF]({e['pdf_url']}))" if e.get("pdf_check") == "pdf" and e["pdf_url"] != e["url"] else ""
    return f"[{_cell(e['designation'])}]({e['url']}){pdf}"


def markdown() -> str:
    es = entries()
    n_titles = sum(1 for e in es if e["title_source"] == "publisher-page")
    n_search = sum(1 for e in es if e["title_source"] == "search-listing")
    checks: dict[str, int] = {}
    for e in es:
        c = e.get("check", "unchecked")
        checks[c] = checks.get(c, 0) + 1
    n_pdf = len({e.get("pdf_url") for e in es if e.get("pdf_check") == "pdf"} | {e["url"] for e in es if e.get("check") == "pdf"})
    dates = sorted({e["checked"] for e in es if e.get("checked")})
    lines = ["# Standards and literature library", "",
             f"Generated from `process_safety/data/standards_library.json`: {len(es)} entries. Regenerate with "
             "`python -m process_safety library --markdown > docs/STANDARDS_LIBRARY.md`. Search with "
             "`python -m process_safety library WORDS [--category C] [--body B] [--region R] [--kind K] [--access A]`.",
             "The reading map by design activity is in [DESIGN_STANDARDS_RECOMMENDATIONS.md](DESIGN_STANDARDS_RECOMMENDATIONS.md).", "",
             "## How far to trust an entry", "",
             "* **Not a complete list of everything published.** It is a curated index; add missing documents in `scripts/build_standards_library.py`.",
             "* **Editions are not recorded.** Confirm the current edition, and the edition your regulator or contract cites.",
             f"* **Title**: {n_titles} titles were read from the publisher's page (marked `P`); {n_search} came from web-search result listings (`S`). "
             f"The other {len(es) - n_titles - n_search} were typed by the compiler (`C`) and "
             "not compared with the publisher; confirm before citing. No document text was read for this library.",
             "* **Link**: `document` links point to a page for that document. `catalogue` links point to the publisher's search or catalogue page: "
             "search there for the designation.",
             f"* **Check** (one automated request, {', '.join(dates) or 'not run'}): "
             + ", ".join(f"{k} {v}" for k, v in sorted(checks.items())) + ". `blocked` means the site refuses automated clients (not bypassed): "
             "open it in a browser. `robots` means the site's robots.txt disallows this kind of agent, so the page was not requested. A reachable catalogue page does not show that a designation or title is right.",
             "* **Access**: `free`, `free-registration`, `mixed` (some free, or free read-only), `paid`. Only publisher, regulator or "
             "rights-holder pages are linked. Paid standards are not copied into this repository.",
             f"* **PDFs**: {n_pdf} free official PDF links were confirmed to return a PDF. `python3 scripts/check_standards_library.py --pdf` rechecks them.", "", "## Contents", ""]
    for cat, label in CATEGORIES.items():
        n = sum(1 for e in es if e["category"] == cat)
        lines.append(f"* [{label}](#{_anchor(label)}) ({n})")
    lines.append("")
    for cat, label in CATEGORIES.items():
        group = [e for e in es if e["category"] == cat]
        lines += [f"## {label}", "", "| Document | Title | Body | Region | Access | Link | Title | Check | Note |", "|---|---|---|---|---|---|---|---|---|"]
        for e in group:
            lines.append(f"| {_link(e)} | {_cell(e['title'])} | {_cell(e['body'])} | {e['region']} | {e['access']} | {e['link']} | "
                         f"{TITLE_MARK[e['title_source']]} | {e.get('check', 'unchecked')} | {_cell(e['note'])} |")
        lines.append("")
    return "\n".join(lines)


def _anchor(label: str) -> str:
    return "".join(c for c in label.lower() if c.isalnum() or c in " -").replace(" ", "-")


def recommendations_markdown() -> str:
    r = recommendations()
    idx = by_designation()
    lines = ["# Design standards reading map", "",
             "Generated from `process_safety/data/design_recommendations.json`. Regenerate with "
             "`python -m process_safety library --map-markdown > docs/DESIGN_STANDARDS_RECOMMENDATIONS.md`. One row: "
             "`python -m process_safety library --activity ID`.", "", r["note"], ""]
    for key, head in (("activities", "By design activity"), ("materials", "Materials: specification families by product form and service")):
        lines += [f"## {head}", ""]
        for row in r[key]:
            lines += [f"### {row['title']} (`{row['id']}`)", "", "| Document | Title | Access |", "|---|---|---|"]
            for d in row["documents"]:
                e = idx[d]
                lines.append(f"| {_link(e)} | {_cell(e['title'])} | {e['access']} |")
            lines.append("")
    return "\n".join(lines)
