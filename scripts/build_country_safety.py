"""Merge regional research files into process_safety/data/country_safety.json.

Usage: python3 scripts/build_country_safety.py RESEARCH_DIR [ISO_TABLE_JSON]

A slot whose note says it was never searched is stored as not-searched, which is different from not-found.
ISO_TABLE_JSON ({ISO3: {name, url}}) fills standards bodies that the searches did not find.

Each RESEARCH_DIR/*.json is {ISO3: {slot: {"status": "found", "name", "url", "source", "note"} | {"status": "not-found"}}}.
The committed table is the durable record: a run adds to it. A slot absent from the research files keeps its current value, and a
later not-found or not-searched never erases a found entry. A malformed entry or a document-sharing link is reported and not added.
Standard library only.
"""
import glob
import json
import os
import re
import sys
from urllib.parse import quote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from process_safety.country_coverage import SLOTS  # noqa: E402

OUT = os.path.join(ROOT, "process_safety", "data", "country_safety.json")
BANNED = ("scribd.", "sci-hub", "libgen", "pdfcoffee", "dokumen.", "idoc.pub", "slideshare.", "academia.edu", "z-lib",
          "studocu.", "coursehero.", "pdfcookie", "vdocument", "fliphtml5", "yumpu.", "studylib.")


NOT_SEARCHED = re.compile(r"not\s+(been\s+)?(searched|researched)|search budget|budget ran out", re.I)
ISO_TABLE_NOTE = ("Acronym from Wikipedia's table of countries in ISO (page read 2026-11-25); the link is that table, not the body's "
                  "own site.")


def clean(slot_value) -> tuple[dict, str]:
    """Return (slot, reason it was downgraded or '')."""
    v = slot_value if isinstance(slot_value, dict) else {}
    note = " ".join(str(v.get("note") or "").split())[:240]
    if v.get("status") != "found":
        if NOT_SEARCHED.search(note):
            return {"status": "not-searched", "note": ""}, ""
        return ({"status": "not-found", "note": note}, "" if v.get("status") == "not-found" else "missing or malformed slot")
    name, url = " ".join(str(v.get("name") or "").split()), str(v.get("url") or "").strip()
    if url.startswith(("http://", "https://")):  # percent-encode spaces and non-ASCII; existing escapes are kept
        url = quote(url, safe=":/?#[]@!$&'*+,;=%~-._")
    parts = urlsplit(url)
    if not name or parts.scheme not in ("http", "https") or "." not in parts.netloc or any(c in url for c in " ()<>|"):
        url_ok = False
    else:
        url_ok = True
    if not url_ok:
        return {"status": "not-found", "note": ""}, f"no usable name or link: {url[:80]}"
    if any(b in url.lower() for b in BANNED):
        return {"status": "not-found", "note": ""}, f"document-sharing site: {parts.netloc}"
    source = "official" if v.get("source") == "official" else "secondary"
    return {"status": "found", "name": name[:220], "url": url, "source": source, "note": note}, ""


def main() -> None:
    src = sys.argv[1]
    iso_table = {}
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as fh:
            iso_table = json.load(fh)
    with open(os.path.join(ROOT, "process_safety", "data", "un_states.json"), encoding="utf-8") as fh:
        states = json.load(fh)["states"]
    research: dict = {}
    for path in sorted(glob.glob(os.path.join(src, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            chunk = json.load(fh)
        dup = set(chunk) & set(research)
        if dup:
            raise SystemExit(f"{path}: states already in another file: {sorted(dup)}")
        research.update(chunk)
    codes = {s["iso3"] for s in states}
    print("unknown codes ignored:", sorted(set(research) - codes))
    print("states with no research:", sorted(codes - set(research)))
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = json.load(fh)
    countries, dropped = {}, []
    for s in states:
        row = {}
        for slot in SLOTS:
            prev = old.get("countries", {}).get(s["iso3"], {}).get(slot, {})
            given = research.get(s["iso3"], {}).get(slot)
            if given is None:  # nothing new: keep what the table has; a slot nobody has looked at is not-searched
                row[slot] = prev or {"status": "not-searched", "note": ""}
                continue
            row[slot], why = clean(given)
            if why:
                dropped.append((s["iso3"], slot, why))
            if row[slot]["status"] != "found" and prev.get("status") == "found":  # a later blank never erases an entry
                row[slot] = prev
                continue
            if row[slot]["status"] == "found" and prev.get("url") == row[slot]["url"] and "check" in prev:
                row[slot]["check"] = prev["check"]
        if row["standards_body"]["status"] != "found" and s["iso3"] in iso_table:
            t = iso_table[s["iso3"]]
            row["standards_body"] = {"status": "found", "name": t["name"], "url": t["url"], "source": "secondary",
                                     "note": ISO_TABLE_NOTE}
            prev = old.get("countries", {}).get(s["iso3"], {}).get("standards_body", {})
            if prev.get("url") == t["url"] and "check" in prev:
                row["standards_body"]["check"] = prev["check"]
        countries[s["iso3"]] = row
    data = {"compiled": "2026-11-25",
            "note": ("Compiled from web-search result listings (pages not read) and, for some standards bodies, one Wikipedia "
                     "table. not-found does not mean no law exists; not-searched means nobody has looked."),
            "audit": old.get("audit", "Not yet done."),
            "countries": countries}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    for d in dropped:
        print("downgraded:", *d)
    print(len(countries), "states written;", len(dropped), "slots downgraded")


if __name__ == "__main__":
    main()
