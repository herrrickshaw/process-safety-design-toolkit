"""How published studies build process-simulation and safety models, in two layers.

* **Map** (`data/modelling_map.json`): catalogue records from open bibliographic services, screened and tagged by rule from the
  title and abstract (`modelling_tags`). The records were not read. A tag says a tool or study type is mentioned.
* **Profiles** (`data/modelling_studies.json`): works whose full text, or the stated parts of it, were read by an AI research
  agent; each method claim was checked, before audit corrections, to have an exact quote in the saved text (the quotes are not
  republished). A matching quote does not prove the paraphrase is right.

Neither layer is a systematic review: the search is not exhaustive and the profiles are a purposive, open-access sample, so counts
here do not estimate how common a practice is.
"""
from __future__ import annotations

import json
from collections import Counter
from importlib import resources

from . import modelling_tags as tags

DOC_TYPES = ("phd-thesis", "masters-thesis", "bachelor-thesis", "journal", "conference", "official-report", "other-report", "guideline")
VALIDATION_KINDS = ("experiment", "plant-data", "code-to-code", "literature-values", "none-reported")
MAP_TYPES = ("thesis", "journal", "conference", "report", "book-chapter", "preprint", "other")
_CACHE: dict[str, dict] = {}


def _load(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = json.loads(resources.files("process_safety").joinpath("data", name).read_text(encoding="utf-8"))
    return _CACHE[name]


def study_labels() -> dict[str, str]:
    return {**{k: v[0] for k, v in tags.STUDIES.items()}, "method-guidance": "Method guidance and model evaluation"}


def records() -> list[dict]:
    return list(_load("modelling_map.json")["records"])


def profiles() -> list[dict]:
    return list(_load("modelling_studies.json")["profiles"])


def playbooks() -> list[dict]:
    return list(_load("modelling_studies.json")["playbooks"])


def search(text: str | None = None, tool: str | None = None, study: str | None = None, kind: str | None = None,
           since: int | None = None, open_only: bool = False) -> list[dict]:
    """Map records, newest first."""
    t = (text or "").lower()
    return [r for r in records()
            if (not t or t in f"{r['title']} {' '.join(r['authors'])} {r['venue']}".lower())
            and (not tool or tool in r["tools"]) and (not study or study in r["studies"]) and (not kind or r["type"] == kind)
            and (since is None or (r["year"] or 0) >= since) and (not open_only or r["open_url"])]


def _profile_text(p: dict) -> str:
    return json.dumps(p, ensure_ascii=False).lower()


def search_profiles(text: str | None = None, tool: str | None = None, study: str | None = None) -> list[dict]:
    t = (text or "").lower()
    out = []
    for p in profiles():
        named = " ".join(x["name"] for x in p["tools"])
        if tool and tool not in tags.tools_in(named + " simulation CFD gas release fire process dispersion pipeline transient"):
            continue
        if (study and study not in p["study_types"]) or (t and t not in _profile_text(p)):
            continue
        out.append(p)
    return out


def sheet(p: dict) -> list[str]:
    """One profile as Markdown lines."""
    where = p["institution_or_venue"]
    lines = [f"### {p['title']}", "",
             f"`{p['id']}` · {', '.join(p['authors'][:4])}{' et al.' if len(p['authors']) > 4 else ''} · {p['year']} · {p['doc_type']}"
             f"{' · ' + where if where else ''}", "",
             f"[Open copy read]({p['url']})" + (f" · [DOI](https://doi.org/{p['doi']})" if p["doi"] else "") + f" · read: {p['read_scope']}",
             "", f"**Objective.** {p['objective']}", ""]
    if p["tools"]:
        lines.append("**Tools.**")
        lines += [f"- {x['name']} (version: {x['version']}): {x['role']}" for x in p["tools"]]
        lines.append("")
    if p["build_steps"]:
        lines.append("**How the study was built.**")
        lines += [f"{n}. {x['step']}" for n, x in enumerate(p["build_steps"], 1)]
        lines.append("")
    if p["key_choices"]:
        lines.append("**Modelling choices.**")
        lines += [f"- {x['item']}: {x['value']}" for x in p["key_choices"]]
        lines.append("")
    if p["tool_chain"]:
        lines += [f"**Tool chain.** {p['tool_chain']}", ""]
    v, s = p["validation"], p["sensitivity"]
    lines += [f"**Validation ({v['kind']}).** {v.get('detail') or 'None reported in the parts read.'}", "",
              f"**Sensitivity or uncertainty.** {s.get('detail') if s.get('done') else 'None reported in the parts read.'}", ""]
    if p["limitations"]:
        lines.append("**Limitations the authors state.**")
        lines += [f"- {x['text']}" for x in p["limitations"]]
        lines.append("")
    lines += [f"**Reusable lesson (compiler's).** {p['lesson']}", ""]
    if p["caveats"]:
        lines += [f"**Caveats.** {p['caveats']}", ""]
    if p["audit_note"]:
        lines += [f"**Audit note.** {p['audit_note']}", ""]
    return lines


def matrix(rows: list[dict] | None = None, min_tool: int = 10) -> tuple[list[str], list[str], dict]:
    """(tool keys, study keys, {(tool, study): count}) over map records."""
    rows = records() if rows is None else rows
    tool_n = Counter(t for r in rows for t in r["tools"])
    tools = [t for t, n in tool_n.most_common() if n >= min_tool and tags.TOOLS[t][1] != "general"]
    studies = list(tags.STUDIES)
    cells = Counter((t, s) for r in rows for t in r["tools"] for s in r["studies"])
    return tools, studies, cells


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("[", "(").replace("]", ")")


def markdown() -> str:
    d = _load("modelling_studies.json")
    ps, rows = profiles(), records()
    labels = study_labels()
    kinds = Counter(p["validation"]["kind"] for p in ps)
    theses = sum(1 for p in ps if p["doc_type"].endswith("thesis"))
    lines = ["# How process simulation and safety studies are built: a literature map", "",
             "Generated from `process_safety/data/modelling_studies.json` and `modelling_map.json` (compiled " + d["compiled"] + "). "
             "Regenerate: `python -m process_safety modelling --markdown > docs/MODELLING_STUDIES.md`.", "",
             "## Read this first", "",
             f"* **Two layers.** A map of {len(rows)} catalogue records (titles and abstracts screened by rule, **not read**), and "
             f"{len(ps)} works ({theses} of them theses) whose full text, or the parts stated on each sheet, were read by AI research "
             "agents.",
             "* **Quote check.** Before the audit corrections, each tool, step, choice, validation, sensitivity and limitation entry had to match "
             "an exact quote in the saved text. This shows the passage exists, not that the paraphrase or the study is right. Objectives, tool chains, lessons "
             "and caveats are the reader's own. No human has checked the sheets.",
             "* **Not a systematic review.** The searches are not exhaustive, the read set is a purposive sample of openly available works "
             "(English-heavy), and several are student theses. Counts here do **not** estimate how common a practice is.",
             "* **Not design guidance.** Use a published model's choices as questions to ask about yours, not as values to copy.", "",
             "## Audit", "", d["audit"], "",
             "## What the read works did about validation", "",
             "The kind each sheet records, from the parts read. Counts describe this sample only.", "", "| Kind | Works |", "|---|---|"]
    lines += [f"| {k} | {kinds.get(k, 0)} |" for k in VALIDATION_KINDS]
    lines += ["", "## How studies of each type are built", "",
              "Synthesis across the read works. Each point is the compiler's reading and names the sheets it rests on; one or two sheets "
              "support an observation, not a rule.", ""]
    for b in d["playbooks"]:
        lines += [f"### {b['title']}", "", b["intro"], ""]
        lines += [f"- {x['text']} ({', '.join(f'`{i}`' for i in x['profiles'])})" for x in b["points"]]
        lines.append("")
    tools, studies, cells = matrix(rows)
    n_type = Counter(r["type"] for r in rows)
    lines += ["## The map", "",
              f"{len(rows)} records: " + ", ".join(f"{n_type[k]} {k}" for k in MAP_TYPES if n_type[k]) + ". "
              f"{sum(1 for r in rows if r['open_url'])} have an open link as reported by the catalogue (not checked). "
              f"{sum(1 for r in rows if r['tagged_from'] == 'title only')} were tagged from the title alone. Theses are listed in "
              "`docs/MODELLING_THESES.md`; search everything with `python -m process_safety modelling TEXT --tool T --study S`.", "",
              "Records whose title or abstract mentions both the tool and the study type. The numbers reflect the search queries as much "
              "as the literature: do not read them as popularity.", "",
              "| Tool | " + " | ".join(studies) + " |", "|---|" + "---|" * len(studies)]
    lines += [f"| {tags.TOOLS[t][0]} | " + " | ".join(str(cells[(t, s)] or "") for s in studies) + " |" for t in tools]
    lines += ["", "Column keys: " + "; ".join(f"`{k}` {tags.STUDIES[k][0].lower()}" for k in studies) + ".", "",
              "## Study sheets", "", "Grouped by the first study type each sheet lists.", ""]
    for key, label in labels.items():
        group = [p for p in ps if p["study_types"] and p["study_types"][0] == key]
        if not group:
            continue
        lines += [f"## {label}", ""]
        for p in sorted(group, key=lambda p: (p["year"] or 0, p["id"])):
            lines += sheet(p)
    return "\n".join(lines).rstrip() + "\n"


def theses_markdown() -> str:
    rows = [r for r in records() if r["type"] == "thesis"]
    lines = ["# Theses in the modelling-literature map", "",
             "Generated by `python -m process_safety modelling --theses-markdown > docs/MODELLING_THESES.md`.", "",
             f"{len(rows)} records that a catalogue marks as a thesis or dissertation, screened by rule from title and abstract. "
             "**They were not read** (those that were are in `MODELLING_STUDIES.md`). Catalogues mislabel some documents, levels are "
             "often missing, and links were not checked.", "",
             "| Year | Title | Authors | Level | Tools mentioned | Study types mentioned |", "|---|---|---|---|---|---|"]
    for r in rows:
        link = r["open_url"] or r["url"]
        lines.append(f"| {r['year'] or ''} | [{_cell(r['title'])}]({link.replace(' ', '%20').replace('(', '%28').replace(')', '%29')}) | "
                     f"{_cell(', '.join(r['authors']))} | {r['level']} | {', '.join(r['tools'])} | {', '.join(r['studies'])} |")
    return "\n".join(lines) + "\n"
