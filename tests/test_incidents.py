import datetime
import os
import subprocess
import sys
import unittest

from process_safety import incidents

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Incidents(unittest.TestCase):
    def test_records_well_formed(self):
        inc = incidents.incidents()
        self.assertGreaterEqual(len(inc), 15)
        self.assertEqual(len({i["id"] for i in inc}), len(inc))
        pkg = os.path.join(ROOT, "process_safety")
        for i in inc:
            datetime.date.fromisoformat(i["date"])
            datetime.date.fromisoformat(i["final_report"])
            self.assertTrue(i["source"].startswith("https://www.csb.gov/"), i["id"])
            self.assertTrue(all(1 <= s <= 12 for s in i["design_steps"]), i["id"])
            for m in i["modules"]:
                self.assertTrue(os.path.exists(os.path.join(pkg, m + ".py")) or os.path.isdir(os.path.join(pkg, m)), f"{i['id']}: {m}")
            for k in ("deaths", "injured"):
                self.assertTrue(i[k] is None or i[k] >= 0)

    def test_stated_counts(self):
        by = {i["id"]: i for i in incidents.incidents()}
        self.assertEqual((by["texas-city-2005"]["deaths"], by["texas-city-2005"]["injured"]), (15, 180))
        self.assertEqual(by["imperial-sugar-2008"]["deaths"], 14)
        self.assertIsNone(by["arkema-2017"]["deaths"])   # not stated on the page: must stay blank

    def test_search(self):
        self.assertTrue(all("overfill" in i["modules"] for i in incidents.search(module="overfill")))
        self.assertTrue(incidents.search(step=7))
        self.assertEqual(incidents.search("zzzz"), [])
        years = [i["date"] for i in incidents.search()]
        self.assertEqual(years, sorted(years))

    def test_doc_in_sync_and_cli(self):
        with open(os.path.join(ROOT, "docs", "INCIDENTS.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), incidents.markdown(), "docs/INCIDENTS.md is stale: python -m process_safety incidents --markdown > docs/INCIDENTS.md")
        r = subprocess.run([sys.executable, "-m", "process_safety", "incidents", "--module", "relief"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, "-m", "process_safety", "incidents", "zzzz"], capture_output=True, text=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
