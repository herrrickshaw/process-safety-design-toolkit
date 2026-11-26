"""Merge incident research files into process_safety/data/incident_casebook.json.

Usage: python3 scripts/build_casebook.py RESEARCH_DIR [--curation FILE] [--write]

RESEARCH_DIR holds one JSON file per research pass ({"cases": [...], "dropped": [...]}) and a sources/ folder with the text of
every page read. Each case carries "evidence": exact quotes for its date, cause and death toll. A quote that is not in the
saved text, or a missing one, is reported and the case is not written. The quotes and page texts stay out of the repository.
--curation is the reviewer's {case id: {field: value}} overlay (corrections and support notes), applied after the quote checks.
Without --write the script only reports. Standard library only.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from process_safety import casebook, incidents  # noqa: E402

OUT = os.path.join(ROOT, "process_safety", "data", "incident_casebook.json")
KEYS = ("id", "name", "date", "iso3", "place", "sector", "event_types", "substance", "deaths", "deaths_note",
        "what_happened", "cause_status", "causes", "learnings", "questions", "topics", "regulatory_aftermath", "sources")
BANNED = ("scribd.", "sci-hub", "libgen", "pdfcoffee", "dokumen.", "idoc.pub", "slideshare.", "academia.edu", "z-lib",
          "studocu.", "coursehero.", "vdocument", "yumpu.")
WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
         "eighteen nineteen twenty").split()


def squash(s: str) -> str:
    return " ".join(s.split())


def states_number(quote: str, n: int) -> bool:
    digits = {int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", quote) if x.replace(",", "")}
    return n in digits or (n < len(WORDS) and re.search(rf"\b{WORDS[n]}\b", quote, re.I) is not None)


def problems(c: dict, sources_dir: str) -> tuple[list[str], list[str]]:
    """(errors that keep the case out, warnings to review by hand)."""
    bad = [f"missing {k}" for k in KEYS if k not in c]
    if bad:
        return bad, []
    warn: list[str] = []
    quoted = {}
    for e in c.get("evidence", []):
        path = os.path.join(sources_dir, os.path.basename(str(e.get("file", ""))))
        q = squash(str(e.get("quote", "")))
        if not q or not os.path.isfile(path):
            bad.append(f"evidence {e.get('field')}: no quote or file")
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            if q not in squash(fh.read()):
                bad.append(f"evidence {e.get('field')}: quote not in {os.path.basename(path)}")
                continue
        quoted.setdefault(e.get("field"), []).append(q)
    need = ["date", "cause"] + (["deaths"] if c["deaths"] is not None else [])
    bad += [f"no verified {f} quote" for f in need if f not in quoted]
    if c["deaths"] is not None and "deaths" in quoted and not any(states_number(q, c["deaths"]) for q in quoted["deaths"]):
        warn.append(f"deaths {c['deaths']} not literally in: {quoted['deaths']}")
    year = c["date"][:4]
    if "date" in quoted and not any(year in q for q in quoted["date"]):
        warn.append(f"year {year} not in date quote: {quoted['date']}")
    if c["iso3"] not in casebook.country_names():
        bad.append(f"unknown country {c['iso3']}")
    bad += [f"unknown topic {t}" for t in c["topics"] if t not in casebook.TOPICS]
    bad += [f"unknown event type {t}" for t in c["event_types"] if t not in casebook.EVENT_TYPES]
    if c["cause_status"] not in casebook.CAUSE_STATUS:
        bad.append(f"cause_status {c['cause_status']}")
    if not c["sources"]:
        bad.append("no source")
    for s in c["sources"]:
        if s.get("grade") not in casebook.GRADES or not str(s.get("url", "")).startswith("http"):
            bad.append(f"bad source {s}")
        elif any(b in s["url"].lower() for b in BANNED):
            bad.append(f"document-sharing site {s['url']}")
    if any(x.get("basis") not in ("source", "compiler") or not x.get("text") for x in c["learnings"]) or not c["learnings"]:
        bad.append("learnings need text and basis")
    if len(c["questions"]) != 2:
        bad.append("need exactly 2 questions")
    return bad, warn


def main() -> int:
    research = sys.argv[1]
    sources_dir = os.path.join(research, "sources")
    cases, seen, rejected = [], set(), 0
    curation = {}
    if "--curation" in sys.argv:
        with open(sys.argv[sys.argv.index("--curation") + 1], encoding="utf-8") as fh:
            curation = json.load(fh)
    for path in sorted(glob.glob(os.path.join(research, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            chunk = json.load(fh)
        for d in chunk.get("dropped", []):
            print("researcher dropped:", d.get("name"), "-", d.get("reason"))
        for c in chunk["cases"]:
            if c.get("id") in seen:
                raise SystemExit(f"duplicate id {c['id']} in {path}")
            seen.add(c.get("id"))
            bad, warn = problems(c, sources_dir)
            for w in warn:
                print("REVIEW", c.get("id"), w)
            if bad:
                rejected += 1
                print("REJECT", c.get("id"), "; ".join(bad))
                continue
            row = {k: c[k] for k in KEYS}
            row["support_note"] = ""
            row["sources"] = [{k: s.get(k, "") for k in ("title", "publisher", "url", "grade")} for s in c["sources"]]
            change = curation.get(c["id"], {})
            if set(change) - set(row):
                raise SystemExit(f"curation for {c['id']} has unknown fields {sorted(set(change) - set(row))}")
            row.update(change)
            if c["id"] in {i["id"] for i in incidents.incidents()}:
                row["csb_id"] = c["id"]
            cases.append(row)
    if set(curation) - seen:
        raise SystemExit(f"curation names unknown cases {sorted(set(curation) - seen)}")
    print(f"{len(cases)} accepted, {rejected} rejected")
    if "--write" in sys.argv:
        old = {}
        if os.path.exists(OUT):
            with open(OUT, encoding="utf-8") as fh:
                old = json.load(fh)
        data = {"compiled": "2026-11-26", "audit": old.get("audit", "Not yet audited."),
                "cases": sorted(cases, key=lambda c: (c["date"], c["id"]))}
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
