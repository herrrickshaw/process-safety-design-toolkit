import os
import subprocess
import sys
import unittest

from process_safety import literature
from process_safety.cli import REGISTRY

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Literature(unittest.TestCase):
    def test_entries_are_well_formed(self):
        es = literature.entries()
        self.assertGreaterEqual(len(es), 45)
        ids = [e["id"] for e in es]
        self.assertEqual(len(ids), len(set(ids)))
        for e in es:
            self.assertTrue(e["url"].startswith("https://"), e["id"])
            self.assertIn(e["read"], ("text", "page", "no"))
            self.assertIn(e["access"], ("free", "paywalled", "mixed"))
            self.assertTrue(e["topics"], e["id"])
            self.assertIn("http_status", e, f"{e['id']}: run scripts/check_literature_urls.py")

    def test_modules_exist(self):
        pkg = os.path.join(ROOT, "process_safety")
        for e in literature.entries():
            for m in e["modules"]:
                self.assertTrue(os.path.exists(os.path.join(pkg, m + ".py")) or os.path.isdir(os.path.join(pkg, m)), f"{e['id']}: unknown module {m}")

    def test_search_filters(self):
        self.assertTrue(literature.search(topic="incident"))
        self.assertTrue(all(e["region"] == "IN" for e in literature.search(region="IN")))
        self.assertTrue(all(e["read"] != "no" for e in literature.search(read_only=True)))
        self.assertEqual(literature.search("zzzz-not-there"), [])

    def test_blocked_source_is_not_marked_read(self):
        e = [x for x in literature.entries() if x["id"] == "ccps-beacon"][0]
        self.assertEqual(e["read"], "no")

    def test_markdown_in_sync_and_cli(self):
        with open(os.path.join(ROOT, "docs", "LITERATURE.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), literature.markdown(), "docs/LITERATURE.md is stale: python -m process_safety literature --markdown > docs/LITERATURE.md")
        self.assertIn("literature", REGISTRY)
        r = subprocess.run([sys.executable, "-m", "process_safety", "literature", "csb"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, "-m", "process_safety", "literature", "zzzz"], capture_output=True, text=True).returncode, 1)


if __name__ == "__main__":
    unittest.main()
