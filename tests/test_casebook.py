import datetime
import os
import subprocess
import sys
import tempfile
import unittest

from process_safety import casebook, incidents

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_casebook  # noqa: E402


def good_case(**change):
    c = {"id": "x-1990", "name": "X", "date": "1990-01-02", "iso3": "IND", "place": "P", "sector": "chemicals",
         "event_types": ["fire"], "substance": "", "deaths": 3, "deaths_note": "", "what_happened": "w", "cause_status": "secondary-account",
         "causes": ["c"], "learnings": [{"text": "t", "basis": "compiler"}], "questions": ["a?", "b?"], "topics": ["ignition-control"],
         "regulatory_aftermath": "", "sources": [{"title": "t", "publisher": "p", "url": "https://example.org/x", "grade": "C"}],
         "evidence": [{"field": f, "file": "x.txt", "quote": "On 2 January 1990 three people died"} for f in ("date", "deaths", "cause")]}
    c.update(change)
    return c


class Validator(unittest.TestCase):
    def check(self, case):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.txt"), "w", encoding="utf-8") as fh:
                fh.write("Report.\nOn 2 January 1990 three\npeople died in a fire.\n")
            return build_casebook.problems(case, d)

    def test_supported_case_passes_across_line_breaks(self):
        self.assertEqual(self.check(good_case()), ([], []))

    def test_invented_quote_is_rejected(self):
        bad = good_case(evidence=[{"field": f, "file": "x.txt", "quote": "thirty people died"} for f in ("date", "deaths", "cause")])
        self.assertTrue(self.check(bad)[0])

    def test_death_toll_needs_a_quote_only_when_given(self):
        ev = [e for e in good_case()["evidence"] if e["field"] != "deaths"]
        self.assertIn("no verified deaths quote", self.check(good_case(evidence=ev))[0])
        self.assertEqual(self.check(good_case(evidence=ev, deaths=None))[0], [])

    def test_wrong_number_is_flagged(self):
        self.assertTrue(self.check(good_case(deaths=30))[1])

    def test_unknown_topic_and_basis_are_rejected(self):
        self.assertTrue(self.check(good_case(topics=["nonsense"]))[0])
        self.assertTrue(self.check(good_case(learnings=[{"text": "t", "basis": "me"}]))[0])


class Casebook(unittest.TestCase):
    def test_records_well_formed(self):
        cs = casebook.cases()
        self.assertEqual(len({c["id"] for c in cs}), len(cs))
        names, csb = casebook.country_names(), {i["id"] for i in incidents.incidents()}
        for c in cs:
            with self.subTest(c["id"]):
                parts = [int(x) for x in c["date"].split("-")]
                datetime.date(*(parts + [1, 1])[:3])
                self.assertIn(c["iso3"], names)
                self.assertTrue(c["topics"] and set(c["topics"]) <= set(casebook.TOPICS))
                self.assertTrue(c["event_types"] and set(c["event_types"]) <= set(casebook.EVENT_TYPES))
                self.assertIn(c["cause_status"], casebook.CAUSE_STATUS)
                self.assertTrue(c["causes"] and c["learnings"])
                self.assertTrue({x["basis"] for x in c["learnings"]} <= {"source", "compiler"})
                self.assertEqual(len(c["questions"]), 2)
                self.assertTrue(c["deaths"] is None or c["deaths"] >= 0)
                self.assertTrue(c["sources"] and all(s["url"].startswith("http") and s["grade"] in casebook.GRADES for s in c["sources"]))
                self.assertEqual(c.get("csb_id"), c["id"] if c["id"] in csb else None)
                if c["cause_status"] == "official-investigation":
                    self.assertIn(casebook.best_grade(c), ("A", "B"), "an official cause needs more than a secondary source")

    def test_topics_point_at_real_modules(self):
        pkg = os.path.join(ROOT, "process_safety")
        for key, (_, _, modules) in casebook.TOPICS.items():
            for m in modules:
                self.assertTrue(os.path.exists(os.path.join(pkg, m + ".py")) or os.path.isdir(os.path.join(pkg, m)), f"{key}: {m}")

    def test_every_case_appears_once_in_roster_country_and_sheets(self):
        text = casebook.markdown()
        for c in casebook.cases():
            self.assertEqual(text.count(f"({'`' + c['id'] + '`'}) |"), 1, c["id"])
            self.assertEqual(text.count(f"\n`{c['id']}` · "), 1, c["id"])

    def test_filters_narrow_and_unknown_country_matches_nothing(self):
        everything = {c["id"] for c in casebook.search()}
        by_country = [casebook.search(country=code) for code in {c["iso3"] for c in casebook.cases()}]
        self.assertEqual(sum(len(x) for x in by_country), len(everything))
        for topic in casebook.TOPICS:
            self.assertTrue(all(topic in c["topics"] for c in casebook.search(topic=topic)))
        self.assertEqual(casebook.search(country="Atlantis"), [])
        dates = [c["date"] for c in casebook.search()]
        self.assertEqual(dates, sorted(dates))

    def test_doc_in_sync_and_cli(self):
        with open(os.path.join(ROOT, "docs", "INCIDENT_CASEBOOK.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), casebook.markdown(), "stale: python -m process_safety casebook --markdown > docs/INCIDENT_CASEBOOK.md")
        run = lambda *a: subprocess.run([sys.executable, "-m", "process_safety", "casebook", *a], capture_output=True, text=True, cwd=ROOT)
        first = casebook.cases()[0]
        r = run("--country", first["iso3"], "--sheet")
        self.assertEqual(r.returncode, 0)
        self.assertIn(first["id"], r.stdout)
        self.assertEqual(run("zzzzqqq").returncode, 1)

    def test_data_file_is_the_normal_form(self):
        with open(casebook._PATH, encoding="utf-8") as fh:
            self.assertNotIn('"evidence"', fh.read(), "quotes from sources stay out of the repository")


if __name__ == "__main__":
    unittest.main()
