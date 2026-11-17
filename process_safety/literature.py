"""Curated literature and source index (`data/literature.json`): regulations, regulators, investigation bodies, databases, journals,
associations and the reference tools used to test this toolkit, each linked to topics and toolkit modules.

Every entry records how it was used: read = "text" or "page" (content read for the toolkit) or "no" (URL checked only). `http_status`
is the result of a polite automated request on the `checked` date; 403 usually means the site blocks automated access (open it in a
browser), 0 a timeout. Nothing here is a substitute for the standard or rule itself.
"""
from __future__ import annotations

import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "data", "literature.json")
_CACHE: dict | None = None


def _data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def entries() -> list[dict]:
    return list(_data()["entries"])


def search(text: str | None = None, topic: str | None = None, module: str | None = None, region: str | None = None,
           kind: str | None = None, read_only: bool = False) -> list[dict]:
    out = []
    for e in entries():
        if topic and topic.lower() not in e["topics"]:
            continue
        if module and module not in e["modules"]:
            continue
        if region and e["region"].lower() != region.lower():
            continue
        if kind and e["kind"] != kind:
            continue
        if read_only and e["read"] == "no":
            continue
        if text and text.lower() not in " ".join([e["title"], e["publisher"], e["note"], " ".join(e["topics"])]).lower():
            continue
        out.append(e)
    return out


def topics() -> list[str]:
    return sorted({t for e in entries() for t in e["topics"]})


def markdown() -> str:
    d = _data()
    es = d["entries"]
    n_read = sum(1 for e in es if e["read"] != "no")
    lines = ["# Literature and source index", "",
             f"Generated from `process_safety/data/literature.json` (compiled {d['compiled']}). {len(es)} sources, {n_read} read for the toolkit, the rest URL-checked only.",
             "Regenerate: `python -m process_safety literature --markdown > docs/LITERATURE.md`. Search: `python -m process_safety literature TEXT [--topic T] [--module M]`.",
             "",
             "* **read**: `text` = document text read for the toolkit; `page` = the page or article read; `no` = listed, URL checked, content not read.",
             "* **HTTP**: status of an automated request on the checked date. 403 usually means the site blocks automated clients (open in a browser); 0 a timeout; 202/302 are redirects or challenges that still resolve in a browser.",
             "* Paywalled standards and books are listed so you know they exist; their content is not reproduced here.", ""]
    kinds = ["regulation", "standard", "guidance", "investigation", "database", "association", "journal", "news", "data-tool"]
    for k in kinds:
        group = sorted((e for e in es if e["kind"] == k), key=lambda e: (e["region"], e["title"]))
        if not group:
            continue
        lines += [f"## {k.replace('-', ' ').capitalize()}", "", "| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |", "|---|---|---|---|---|---|---|---|---|"]
        for e in group:
            lines.append(f"| [{e['title']}]({e['url']}) | {e['publisher']} | {e['region']} | {e['access']} | {e['read']} | {e.get('http_status', '')} | {', '.join(e['topics'])} | {', '.join(e['modules'])} | {e['note']} |")
        lines.append("")
    return "\n".join(lines)
