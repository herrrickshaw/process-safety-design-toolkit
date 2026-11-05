"""Commands about the toolkit itself: coverage map, glossary, input ranges."""
from __future__ import annotations

from .. import compliance, glossary, incidents, literature, ranges, recommendation_catalog, requirements_extract, scenario_ingest, standards
from .registry import command, emit


@command("coverage")
class Coverage:
    @staticmethod
    def add_arguments(p):
        pass

    @staticmethod
    def run(a, p):
        for t, (stds, mod, status) in standards.TOPICS.items():
            print(f"- {t}\n    standards: {', '.join(stds)}\n    code: {mod or '-'}\n    status: {status}")


@command("glossary", "search the glossary of terms and abbreviations (no term lists everything)")
class Glossary:
    @staticmethod
    def add_arguments(g):
        g.add_argument("term", nargs="?", help="text to search in term, expansion and definition")
        g.add_argument("--markdown", action="store_true", help="print the whole glossary as Markdown (docs/GLOSSARY.md)")

    @staticmethod
    def run(a, p):
        if a.markdown:
            print(glossary.markdown(), end="")
            return 0
        hits = glossary.search(a.term) if a.term else glossary.entries()
        for e in hits:
            name = e["term"] + (f" ({e['expansion']})" if e["expansion"] else "")
            print(f"{name}\n    {e['definition']}\n    [{e['category']}; {e['applies_to']}]")
        return 0 if hits else 1


@command("ranges", "show the accepted input ranges (hard = rejected, soft = warning)")
class Ranges:
    @staticmethod
    def add_arguments(g):
        g.add_argument("name", nargs="?", help="one quantity, e.g. temperature_K")
        g.add_argument("--markdown", action="store_true", help="print the full table as Markdown (docs/RANGES.md)")

    @staticmethod
    def run(a, p):
        if a.markdown:
            print(ranges.markdown_table(), end="")
            return 0
        if a.name:
            try:
                r = ranges.get(a.name)
            except KeyError:
                print(f"unknown quantity {a.name!r}; run 'ranges' to list", file=__import__("sys").stderr)
                return 2
            emit({"name": r.name, "unit": r.unit, "description": r.description, "hard_range": r.hard_text(), "soft_range": r.soft_text(), "note": r.note})
            return 0
        for r in ranges.RANGES.values():
            print(f"{r.name:28s} {r.unit:9s} possible {r.hard_text():14s} typical {r.soft_text()}")
        return 0


@command("literature", "search the curated literature and source index (regulators, investigations, journals, tools)")
class Literature:
    @staticmethod
    def add_arguments(lp):
        lp.add_argument("text", nargs="?", help="text to search in title, publisher, note and topics")
        lp.add_argument("--topic"); lp.add_argument("--module"); lp.add_argument("--region", help="e.g. US, UK, EU, IN, SG, AU, ME, global")
        lp.add_argument("--kind", help="regulation, standard, guidance, investigation, database, association, journal, news, data-tool")
        lp.add_argument("--read-only", action="store_true", help="only sources whose content was read for the toolkit")
        lp.add_argument("--markdown", action="store_true", help="print the whole index as Markdown (docs/LITERATURE.md)")

    @staticmethod
    def run(a, p):
        if a.markdown:
            print(literature.markdown(), end="")
            return 0
        hits = literature.search(a.text, a.topic, a.module, a.region, a.kind, a.read_only)
        for e in hits:
            print(f"{e['title']}\n    {e['publisher']} [{e['region']}, {e['kind']}, {e['access']}, read: {e['read']}, HTTP {e.get('http_status', '?')}]\n    {e['url']}")
            if e["note"]:
                print(f"    {e['note']}")
        return 0 if hits else 1


@command("incidents", "search the CSB-based incident register (maps incidents to toolkit modules and design review steps)")
class Incidents:
    @staticmethod
    def add_arguments(ip):
        ip.add_argument("text", nargs="?"); ip.add_argument("--module"); ip.add_argument("--step", type=int, help="design review step 1-12 (docs/DESIGN_AWARENESS.md)")
        ip.add_argument("--sector"); ip.add_argument("--year", type=int)
        ip.add_argument("--markdown", action="store_true", help="print the whole register as Markdown (docs/INCIDENTS.md)")

    @staticmethod
    def run(a, p):
        if a.markdown:
            print(incidents.markdown(), end="")
            return 0
        hits = incidents.search(a.text, a.module, a.step, a.sector, a.year)
        for i in hits:
            d = "" if i["deaths"] is None else f", {i['deaths']} killed"
            print(f"{i['date']}  {i['name']} ({i['location']}{d})\n    {i['lesson']}\n    modules: {', '.join(i['modules'])}; steps: {', '.join(map(str, i['design_steps']))}\n    {i['source']}")
        return 0 if hits else 1


@command("catalog", "common safety-study recommendation types; classify free text; --markdown prints docs/RECOMMENDATIONS_CATALOG.md")
class Catalog:
    @staticmethod
    def add_arguments(cp):
        cp.add_argument("text", nargs="*", help="recommendation text to classify (omit to list the catalogue)")
        cp.add_argument("--markdown", action="store_true")

    @staticmethod
    def run(a, p):
        if a.markdown:
            print(recommendation_catalog.markdown(), end="")
            return 0
        if a.text:
            ids = recommendation_catalog.classify(" ".join(a.text))
            for cid in ids[:3]:
                c = recommendation_catalog.CATALOG[cid]
                print(f"{cid}: {c['title']} [{c['category']}; scope {c['scope']}]\n    trigger: {c['trigger']}\n    response: {c['response']}")
            return 0 if ids else 1
        for cid, c in recommendation_catalog.CATALOG.items():
            print(f"{cid:14} {c['title']}  [{c['category']}; {c['scope']}]")
        return 0


@command("requirements", "extract shall/should statements from standards you hold, classify them, write them to a private file (counts only on screen)")
class Requirements:
    @staticmethod
    def add_arguments(rp):
        rp.add_argument("files", nargs="+", help=".txt .md .docx (or .pdf if pdftotext is installed)")
        rp.add_argument("--out", required=True, help="CSV to write the statements to; must be outside version control or git-ignored")
        rp.add_argument("--register", help="PHA register CSV to compare requirement types against")
        rp.add_argument("--show", type=int, default=0, help="print this many statements to the screen (default 0: counts only)")
        rp.add_argument("--allow-tracked", action="store_true", help="write even if the output path is inside a git repository and not ignored")

    @staticmethod
    def run(a, p):
        ign = requirements_extract.git_ignored(a.out)
        if ign is False and not a.allow_tracked:
            p.error(f"{a.out} is inside a git repository and not ignored: extracted statements from proprietary documents must not be committed. "
                    "Choose a path outside the repository or add it to .gitignore (or pass --allow-tracked for documents you may publish).")
        try:
            rows = requirements_extract.extract(a.files)
        except (OSError, ValueError, RuntimeError) as e:
            p.error(str(e))
        requirements_extract.write_csv(rows, a.out)
        out = {"statements": len(rows), "written_to": a.out, **requirements_extract.summarize(rows)}
        if a.register:
            out["register_comparison"] = requirements_extract.compare_register(rows, scenario_ingest.read_register(a.register))
        emit(out)
        for r in rows[: a.show]:
            print(f"[{r['file']} {r['clause']}] ({r['modality']}) {r['text']}")
        return 0


@command("compliance", "tiered compliance (must / should / can) and derogations: check a register, or start one from a requirements extract")
class Compliance:
    @staticmethod
    def add_arguments(cp):
        cp.add_argument("register", nargs="?", help="register JSON ({'as_of': date, 'clauses': [...]}); see process_safety/examples/compliance.json")
        cp.add_argument("--as-of", help="date for expiry checks, YYYY-MM-DD (default: the register's as_of, else today)")
        cp.add_argument("--init", metavar="EXTRACT_CSV", help="start a register (every clause open) from a CSV written by the requirements command")
        cp.add_argument("--out", help="with --init: register JSON to write; must be outside version control or git-ignored")
        cp.add_argument("--allow-tracked", action="store_true", help="write even if --out is inside a git repository and not ignored")

    @staticmethod
    def run(a, p):
        import datetime as dt
        try:
            if a.init:
                if not a.out:
                    p.error("--init needs --out")
                if requirements_extract.git_ignored(a.out) is False and not a.allow_tracked:
                    p.error(f"{a.out} is inside a git repository and not ignored: a register built from extracted statements must not be committed.")
                import json
                reg = compliance.init_register(a.init)
                with open(a.out, "w", encoding="utf-8") as fh:
                    json.dump(reg, fh, indent=1)
                emit({"clauses": len(reg["clauses"]), "by_tier": {t: sum(c["tier"] == t for c in reg["clauses"]) for t in compliance.TIERS}, "written_to": a.out})
                return 0
            if not a.register:
                p.error("give a register JSON, or --init EXTRACT_CSV --out FILE")
            emit(compliance.evaluate(compliance.load(a.register), dt.date.fromisoformat(a.as_of) if a.as_of else None))
        except (OSError, ValueError) as e:
            p.error(str(e))
        return 0
