import os
import subprocess
import sys
import unittest

from process_safety import country_coverage as cc
from process_safety.cli import REGISTRY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(*args):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)


class CountryCoverage(unittest.TestCase):
    def test_table_shape_structure_and_links(self):
        for cmd in ("shape", "structure", "links"):  # completeness (slots, floors) is not a repository invariant yet
            r = _run(os.path.join("scripts", "check_country_coverage.py"), cmd)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_no_document_sharing_hosts(self):
        banned = ("scribd.", "sci-hub", "libgen", "pdfcoffee", "dokumen.", "slideshare.", "academia.edu", "studocu.")
        for row in cc.table().values():
            for v in row.values():
                self.assertFalse(any(b in v.get("url", "").lower() for b in banned), v.get("url"))

    def test_unsearched_is_never_shown_as_not_found(self):
        pending = [(iso, slot) for iso, row in cc.table().items() for slot, v in row.items() if v["status"] == "not-searched"]
        self.assertEqual(cc.counts()["not_searched"], len(pending))
        if pending:
            self.assertIn("not searched yet", cc.markdown())
            self.assertIn("not searched yet", _run("-m", "process_safety", "countries", pending[0][0]).stdout)

    def test_find(self):
        self.assertEqual(cc.find("IND")["name"], "India")
        self.assertEqual(cc.find("in")["iso3"], "IND")
        self.assertIsNone(cc.find("guinea-nowhere"))
        self.assertIsNone(cc.find("land"), "an ambiguous fragment must not pick one")

    def test_eu_layer(self):
        self.assertEqual(len(cc.EU), 27)
        self.assertIn("major_hazard", cc.regional("DEU"))
        self.assertIn("major_hazard", cc.regional("NOR"))
        self.assertEqual(cc.regional("CHE"), {})
        self.assertEqual(cc.regional("GBR"), {})

    def test_generated_doc_in_sync_and_cli(self):
        with open(os.path.join(ROOT, "docs", "COUNTRY_SAFETY_COVERAGE.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), cc.markdown())
        self.assertIn("countries", REGISTRY)
        self.assertEqual(_run("-m", "process_safety", "countries").returncode, 0)
        self.assertIn("does not mean no law exists", _run("-m", "process_safety", "countries", "India").stdout)
        self.assertEqual(_run("-m", "process_safety", "countries", "zzzz").returncode, 1)


if __name__ == "__main__":
    unittest.main()
