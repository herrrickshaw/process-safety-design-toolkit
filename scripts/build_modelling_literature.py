"""Build the modelling-literature data from material kept outside the repository.

Usage: python3 scripts/build_modelling_literature.py RESEARCH_DIR [--write]

RESEARCH_DIR holds records.json (merged catalogue records, with abstracts), profiles/*.json (full-text reading notes, each claim
with an exact quote), sources/ (the saved text of every work read), and optionally curation.json ({profile id: {field: value}},
reviewer corrections applied after the quote checks) and playbooks.json (cross-study synthesis, each point naming profile ids).
A profile is left out if any quote is not in its saved text. Abstracts, quotes and source texts are never written to the repository.
Standard library only.
"""
import glob
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from process_safety import modelling_literature as ml  # noqa: E402

DATA = os.path.join(ROOT, "process_safety", "data")
COMPILED = "2026-11-26"
BANNED = ("scribd.", "sci-hub", "scihub", "libgen", "pdfcoffee", "dokumen.", "idoc.pub", "slideshare.", "academia.edu", "z-lib",
          "studocu.", "coursehero.", "vdocument", "yumpu.", "researchgate.")
# Links that carry a temporary access token or session id are not stored.
TOKEN_LINK = re.compile(r"[?&;](key|token|download_token|access_token|sig|signature|jsessionid|auth)=", re.I)
REQUIRED = ("id", "title", "authors", "year", "doc_type", "institution_or_venue", "url", "saved_text", "read_scope", "study_types",
            "objective", "tools", "build_steps", "key_choices", "tool_chain", "validation", "sensitivity", "limitations", "lesson", "caveats")


def squash(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", s).split())


def claims(p: dict):
    """(where, quote, statement) for every claim in a profile that must be supported by a quote."""
    for key, text in (("tools", "role"), ("build_steps", "step"), ("key_choices", "value"), ("limitations", "text")):
        for i, x in enumerate(p[key]):
            yield f"{key}[{i}]", x.get("quote", ""), x.get(text, "")
    if p["validation"].get("kind") != "none-reported":
        yield "validation", p["validation"].get("quote", ""), p["validation"].get("detail", "")
    if p["sensitivity"].get("done"):
        yield "sensitivity", p["sensitivity"].get("quote", ""), p["sensitivity"].get("detail", "")


def numbers(s: str) -> set[str]:
    return {x.replace(",", "").rstrip(".") for x in re.findall(r"\d[\d,]*(?:\.\d+)?", s)}


def problems(p: dict, sources_dir: str) -> tuple[list[str], list[str]]:
    """(errors that keep the profile out, warnings to review by hand)."""
    bad = [f"missing {k}" for k in REQUIRED if k not in p]
    if bad:
        return bad, []
    path = os.path.join(sources_dir, p["saved_text"])
    if not os.path.isfile(path):
        return [f"saved text not found: {p['saved_text']}"], []
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = squash(fh.read())
    if len(text) < 6000:
        bad.append(f"saved text is only {len(text)} characters: not a full text")
    warn = []
    for where, quote, statement in claims(p):
        q = squash(str(quote))
        if len(q.split()) < 5:
            bad.append(f"{where}: quote missing or too short")
        elif q not in text:
            bad.append(f"{where}: quote not in saved text")
        else:
            extra = numbers(statement) - numbers(q)
            if extra:
                warn.append(f"{where}: numbers {sorted(extra)} are in the statement but not in its quote")
    if not str(p["url"]).startswith("http") or any(b in p["url"].lower() for b in BANNED) or TOKEN_LINK.search(p["url"]):
        bad.append(f"unusable url {p['url']}")
    if p["doc_type"] not in ml.DOC_TYPES:
        bad.append(f"doc_type {p['doc_type']}")
    if p["validation"].get("kind") not in ml.VALIDATION_KINDS:
        bad.append(f"validation kind {p['validation'].get('kind')}")
    bad += [f"unknown study type {s}" for s in p["study_types"] if s not in ml.study_labels()]
    if not p["build_steps"] or not p["tools"]:
        if "method-guidance" not in p["study_types"]:
            bad.append("needs tools and build steps")
    return bad, warn


def published(p: dict) -> dict:
    """The part of a profile that is committed: paraphrase and bibliography, no quotes."""
    drop = lambda items: [{k: v for k, v in x.items() if k != "quote"} for x in items]  # noqa: E731
    row = {k: p[k] for k in REQUIRED if k != "saved_text"}
    row["doi"] = p.get("doi", "")
    for k in ("tools", "build_steps", "key_choices", "limitations"):
        row[k] = drop(p[k])
    for k in ("validation", "sensitivity"):
        row[k] = {a: b for a, b in p[k].items() if a != "quote"}
    row["audit_note"] = ""
    return row


def map_rows(records: list[dict]) -> list[dict]:
    out = []
    for r in records:
        url = r["url"] or (("https://doi.org/" + r["doi"]) if r["doi"] else "")
        oa = r["oa_url"]
        if not url.startswith("http") or any(b in url.lower() for b in BANNED) or TOKEN_LINK.search(url):
            url = ("https://doi.org/" + r["doi"]) if r["doi"] else ""
        if not url:
            continue
        if not oa.startswith("http") or any(b in oa.lower() for b in BANNED) or TOKEN_LINK.search(oa):
            oa = ""
        authors = [a for a in r["authors"] if a]
        out.append({"title": r["title"][:300], "year": r["year"], "authors": authors[:3] + (["et al."] if len(authors) > 3 else []),
                    "venue": r["venue"][:120], "type": r["type"], "level": r["level"], "doi": r["doi"], "url": url, "open_url": oa,
                    "tools": r["tools"], "studies": r["studies"], "tagged_from": r["text_used"], "found_in": r["found_in"]})
    return sorted(out, key=lambda r: (-(r["year"] or 0), r["title"].lower()))


def _load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def main() -> int:
    research = sys.argv[1]
    sources = os.path.join(research, "sources")
    curation = _load(os.path.join(research, "curation.json"), {})
    profiles, seen, titles, rejected = [], set(), {}, 0
    for path in sorted(glob.glob(os.path.join(research, "profiles", "*.json"))):
        for p in _load(path, []):
            pid = p.get("id")
            key = re.sub(r"[^a-z0-9]", "", str(p.get("title", "")).lower())
            if pid in seen or key in titles:
                print("SKIP duplicate", pid, "of", titles.get(key, pid))
                continue
            change = curation.get(pid, {})
            if change.get("_drop"):
                print("DROPPED by reviewer", pid, "-", change["_drop"])
                seen.add(pid)
                continue
            bad, warn = problems(p, sources)
            for w in warn:
                print("REVIEW", pid, w)
            if bad:
                rejected += 1
                print("REJECT", pid, "; ".join(bad))
                continue
            seen.add(pid)
            titles[key] = pid
            row = published(p)
            if set(change) - set(row):
                raise SystemExit(f"curation for {pid} has unknown fields {sorted(set(change) - set(row))}")
            row.update(change)
            profiles.append(row)
    if set(curation) - seen:
        print("curation entries not used:", sorted(set(curation) - seen))
    books = _load(os.path.join(research, "playbooks.json"), [])
    ids = {p["id"] for p in profiles}
    for b in books:
        for point in b["points"]:
            missing = set(point["profiles"]) - ids
            if missing or not point["profiles"]:
                raise SystemExit(f"playbook {b['key']}: point cites unknown or no profiles {sorted(missing)}: {point['text'][:60]}")
    rows = map_rows(_load(os.path.join(research, "records.json"), []))
    print(f"{len(rows)} map records; {len(profiles)} profiles accepted, {rejected} rejected; {len(books)} playbooks")
    if "--write" in sys.argv:
        old = _load(os.path.join(DATA, "modelling_studies.json"), {})
        studies = {"compiled": COMPILED, "audit": old.get("audit", "Not yet audited."), "playbooks": books,
                   "profiles": sorted(profiles, key=lambda p: p["id"])}
        for name, data, indent in (("modelling_studies.json", studies, 1), ("modelling_map.json", {"compiled": COMPILED, "records": rows}, None)):
            with open(os.path.join(DATA, name), "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=indent, ensure_ascii=False, separators=None if indent else (",", ":"))
                fh.write("\n")
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
