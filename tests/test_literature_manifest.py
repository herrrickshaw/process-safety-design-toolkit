"""The literature manifest and its fetch script: structure only, no network."""
import importlib.util
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fetch_open_sources", os.path.join(HERE, "..", "scripts", "fetch_open_sources.py"))
fos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fos)

COLS = ["id", "topic", "title", "authors_or_owner", "year", "url", "access", "http_check_2026-11-10", "size_bytes", "applies_to", "priority", "read_status"]


class Manifest(unittest.TestCase):
    def setUp(self):
        self.rows = fos.load()

    def test_columns_and_unique_ids(self):
        self.assertTrue(self.rows)
        for r in self.rows:
            self.assertEqual(list(r.keys()), COLS)
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_urls_are_https_or_blank_and_priority_valid(self):
        for r in self.rows:
            self.assertTrue(r["url"] == "" or r["url"].startswith("https://"), r["id"])
            self.assertIn(r["priority"], ("0", "1", "2", "3"), r["id"])

    def test_selection_never_includes_paid_blocked_or_already_read_items(self):
        for r in self.rows:
            if fos.selectable(r):
                self.assertTrue(r["access"].lower().startswith("free"))
                self.assertTrue(r["http_check_2026-11-10"].startswith("200 PDF"))
                self.assertNotEqual(r["read_status"].lower(), "read")
        paid = [r for r in self.rows if r["access"].lower().startswith("paid")]
        self.assertTrue(paid)
        self.assertFalse(any(fos.selectable(r) for r in paid))


if __name__ == "__main__":
    unittest.main()
