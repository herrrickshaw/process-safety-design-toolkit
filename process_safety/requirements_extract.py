"""Extract normative statements ("shall", "must", "should" ...) from design standards and practices, classify them against the
recommendation catalogue, and compare them with a PHA register. Built to be run LOCALLY on documents you are licensed to hold (company
design and engineering practices, client specifications, standards you have bought).

Nothing from any proprietary document ships with the toolkit. The statements are written only to an output file you name, which must be
outside version control or git-ignored (the CLI refuses a tracked location), and the console shows counts, never statement text, unless you
ask with --show. Do not publish extracted statements from documents you do not own.

Readers: .txt, .md, .csv (text); .docx (stdlib zip + XML); .pdf only through `pdftotext` if it is installed. Statement detection is by
modal words in sentences; a clause number is taken from the start of the line if there is one. It will miss requirements written without a
modal verb and will include sentences that only quote a requirement: read the output as a worklist, not a complete requirement register.
"""
from __future__ import annotations

import csv
import os
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET

from . import recommendation_catalog as rc

_MANDATORY = re.compile(r"\b(shall|must|is required to|are required to|is to be|are to be)\b", re.I)
_RECOMMENDED = re.compile(r"\b(should|is recommended|are recommended|ought to)\b", re.I)
_PROHIBIT = re.compile(r"\b(shall not|must not|may not|is not permitted|are not permitted|is prohibited|are prohibited)\b", re.I)
_CLAUSE = re.compile(r"^\s*((?:\d+(?:\.\d+)*|[A-Z]\.\d+(?:\.\d+)*|\(\w\))\.?)\s+")
_SPLIT = re.compile(r"(?<=[.;:])\s+(?=[A-Z0-9(])")


def read_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".csv"):
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    if ext == ".docx":
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paras = []
        for p in root.iter(ns + "p"):
            paras.append("".join(t.text or "" for t in p.iter(ns + "t")))
        return "\n".join(paras)
    if ext == ".pdf":
        exe = shutil.which("pdftotext")
        if not exe:
            raise RuntimeError("PDF input needs the pdftotext program (poppler); convert the PDF to text or .docx first")
        return subprocess.run([exe, "-layout", path, "-"], capture_output=True, text=True, check=True).stdout
    raise ValueError(f"unsupported file type {ext}")


def modality(s: str) -> str | None:
    if _PROHIBIT.search(s):
        return "prohibition"
    if _MANDATORY.search(s):
        return "mandatory"
    if _RECOMMENDED.search(s):
        return "recommended"
    return None


def statements(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _CLAUSE.match(line)
        clause = m.group(1).rstrip(".") if m else ""
        for sent in _SPLIT.split(line):
            sent = sent.strip()
            md = modality(sent)
            if md and len(sent) > 15:
                out.append({"clause": clause, "modality": md, "text": sent})
    return out


def extract(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        for s in statements(read_text(p)):
            ids = rc.classify(s["text"])[:2]
            rows.append({"file": os.path.basename(p), **s, "rec_ids": ids, "scope": rc.CATALOG[ids[0]]["scope"] if ids else ""})
    return rows


def summarize(rows: list[dict]) -> dict:
    by_mod: dict[str, int] = {}
    by_id: dict[str, int] = {}
    by_file: dict[str, int] = {}
    for r in rows:
        by_mod[r["modality"]] = by_mod.get(r["modality"], 0) + 1
        by_file[r["file"]] = by_file.get(r["file"], 0) + 1
        for i in r["rec_ids"]:
            by_id[i] = by_id.get(i, 0) + 1
    return {"n": len(rows), "by_modality": by_mod, "by_recommendation_type": dict(sorted(by_id.items(), key=lambda kv: -kv[1])), "by_file": by_file,
            "unclassified": sum(1 for r in rows if not r["rec_ids"])}


def compare_register(rows: list[dict], register: list[dict]) -> dict:
    """Requirement types versus the types the PHA register touches: which requirement areas the register never mentions."""
    req = summarize(rows)["by_recommendation_type"]
    reg_ids: dict[str, int] = {}
    for rec in register:
        for i in rc.classify(" ".join(str(rec.get(k) or "") for k in ("deviation", "cause", "consequence", "safeguards", "recommendation")))[:2]:
            reg_ids[i] = reg_ids.get(i, 0) + 1
    return {"requirement_types_not_in_register": {k: v for k, v in req.items() if k not in reg_ids}, "register_types": reg_ids,
            "note": "keyword matching: a type missing from the register is a prompt to check coverage, not proof of a gap"}


def git_ignored(path: str) -> bool | None:
    """True if git ignores the path, False if it is inside a repository and not ignored, None if not in a repository (or git is missing)."""
    d = os.path.dirname(os.path.abspath(path)) or "."
    while not os.path.isdir(d):
        d = os.path.dirname(d)
    git = shutil.which("git")
    if not git:
        return None
    inside = subprocess.run([git, "-C", d, "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if inside.returncode != 0:
        return None
    r = subprocess.run([git, "-C", d, "check-ignore", "-q", os.path.abspath(path)], capture_output=True)
    return r.returncode == 0


def write_csv(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "clause", "modality", "recommendation_types", "cost_scope", "statement"])
        for r in rows:
            w.writerow([r["file"], r["clause"], r["modality"], ";".join(r["rec_ids"]), r["scope"], r["text"]])
