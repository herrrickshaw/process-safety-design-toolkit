import os
import subprocess
import sys
import unittest

from process_safety import standards_library as lib
from process_safety.cli import REGISTRY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as fh:
        return fh.read()


def _cli(*args):
    return subprocess.run([sys.executable, "-m", "process_safety", "library", *args], capture_output=True, text=True, cwd=ROOT)


class StandardsLibrary(unittest.TestCase):
    def test_entries_are_well_formed(self):
        es = lib.entries()
        self.assertGreaterEqual(len(es), 1300)
        self.assertEqual(len({e["id"] for e in es}), len(es))
        self.assertEqual(len({e["designation"] for e in es}), len(es), "the reading map resolves by designation")
        for e in es:
            self.assertTrue(e["url"].startswith("https://"), e["id"])
            self.assertIn(e["category"], lib.CATEGORIES, e["id"])
            self.assertIn(e["kind"], lib.KINDS, e["id"])
            self.assertIn(e["access"], ("free", "free-registration", "mixed", "paid"), e["id"])
            self.assertIn(e["link"], ("document", "catalogue"), e["id"])
            self.assertIn(e["title_source"], ("publisher-page", "search-listing", "compiler"), e["id"])
            self.assertTrue(e["title"], f"{e['id']}: no title (run scripts/check_standards_library.py)")
            self.assertIn(e.get("check"), ("ok", "pdf", "missing", "blocked", "error", "robots"), f"{e['id']}: run scripts/check_standards_library.py")

    def test_no_missing_pages_and_astm_titles_come_from_astm(self):
        for e in lib.entries():
            self.assertNotEqual(e["check"], "missing", f"{e['id']}: dead link {e['url']}")
            if e["body"] == "ASTM":
                self.assertEqual(e["title_source"], "publisher-page", e["id"])

    def test_digital_refining_rows_claim_nothing(self):
        rows = [e for e in lib.entries() if e["body"] == "Digital Refining"]
        self.assertGreaterEqual(len(rows), 80)
        self.assertTrue(all(e["check"] == "robots" and e["title_source"] == "search-listing" for e in rows))

    def test_no_unofficial_copy_hosts(self):
        banned = ("scribd.", "sci-hub", "libgen", "pdfcoffee", "dokumen.", "idoc.pub", "slideshare.", "academia.edu", "z-lib")
        for e in lib.entries():
            self.assertFalse(any(b in e["url"].lower() for b in banned), e["url"])

    def test_reading_map_resolves(self):
        idx = lib.by_designation()
        r = lib.recommendations()
        rows = r["activities"] + r["materials"]
        self.assertEqual(len({x["id"] for x in rows}), len(rows))
        for row in rows:
            self.assertTrue(row["documents"], row["id"])
            self.assertEqual([d for d in row["documents"] if d not in idx], [], row["id"])
            self.assertEqual(len(set(row["documents"])), len(row["documents"]), row["id"])

    def test_search(self):
        self.assertIn("API STD 521", [e["designation"] for e in lib.search("relief", body="API")])
        self.assertTrue(all(e["region"] == "IN" for e in lib.search(region="IN")))
        self.assertTrue(lib.search("combustible dust", category="explosion-dust"))
        self.assertEqual(lib.search("zzzz-not-there"), [])

    def test_generated_docs_in_sync(self):
        self.assertEqual(_read("STANDARDS_LIBRARY.md"), lib.markdown())
        self.assertEqual(_read("DESIGN_STANDARDS_RECOMMENDATIONS.md"), lib.recommendations_markdown())

    def test_cli(self):
        self.assertIn("library", REGISTRY)
        self.assertEqual(_cli("A106").returncode, 0)
        self.assertEqual(_cli("zzzz-not-there").returncode, 1)
        self.assertEqual(_cli().returncode, 2)
        self.assertEqual(_cli("--activity", "list").returncode, 0)
        self.assertEqual(_cli("--activity", "low-temperature").returncode, 0)
        self.assertEqual(_cli("--activity", "nope").returncode, 2)


if __name__ == "__main__":
    unittest.main()
