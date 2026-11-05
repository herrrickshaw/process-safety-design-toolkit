import os
import subprocess
import sys
import unittest

from process_safety import incidents, recommendation_catalog as rc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Catalog(unittest.TestCase):
    def test_entries_complete(self):
        self.assertGreaterEqual(len(rc.CATALOG), 20)
        for cid, c in rc.CATALOG.items():
            for k in ("title", "category", "trigger", "response", "scope", "keywords"):
                self.assertTrue(c[k], f"{cid}.{k}")
            self.assertIn(c["scope"], rc.SCOPE_NOTE)

    def test_classify(self):
        self.assertEqual(rc.classify("Install an independent high-high level trip to prevent overfill")[0], "HLL-SIF")
        self.assertIn("BDV", rc.classify("Add emergency depressuring valve (blowdown)"))
        self.assertIn("DUST", rc.classify("Improve housekeeping to control dust accumulation"))
        self.assertEqual(rc.classify("completely unrelated sentence about lunch"), [])

    def test_tally(self):
        t = rc.tally(["Add PSV on V-101", "Install high level alarm and trip", "Update the lunch menu"])
        self.assertEqual(t["n"], 3)
        self.assertEqual(len(t["unmatched"]), 1)
        self.assertGreaterEqual(t["counts"]["PSV-ADD"], 1)

    def test_csb_evidence_points_at_real_incidents_and_types(self):
        ids = {i["id"] for i in incidents.incidents()}
        for inc, types in rc.CSB_EVIDENCE.items():
            self.assertIn(inc, ids)
            for t in types:
                self.assertIn(t, rc.CATALOG)
        self.assertEqual(rc.csb_tally()["incidents_mapped"], len(rc.CSB_EVIDENCE))

    def test_doc_in_sync_and_cli(self):
        with open(os.path.join(ROOT, "docs", "RECOMMENDATIONS_CATALOG.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), rc.markdown(), "stale: python -m process_safety catalog --markdown > docs/RECOMMENDATIONS_CATALOG.md")
        r = subprocess.run([sys.executable, "-m", "process_safety", "catalog", "independent", "level", "trip"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("HLL-SIF", r.stdout)


if __name__ == "__main__":
    unittest.main()
