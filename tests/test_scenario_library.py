import importlib
import unittest

from process_safety import scenario_library as sl


class Library(unittest.TestCase):
    def test_entries_are_well_formed(self):
        ids = set()
        for e in sl.entries():
            for k in ("id", "title", "family", "status", "grade", "hazards", "initiating_events", "outcomes", "barriers", "hazid_prompts", "modules",
                      "gaps", "sources"):
                self.assertIn(k, e, e.get("id"))
            self.assertNotIn(e["id"], ids)
            ids.add(e["id"])
            self.assertIn(e["status"], sl.STATUSES)
            self.assertIn(e["grade"], sl.GRADES)
            self.assertTrue(e["hazid_prompts"], e["id"])
            self.assertTrue(e["gaps"], f"{e['id']}: every scenario records what is missing")

    def test_modules_exist(self):
        for e in sl.entries():
            for m in e["modules"]:
                importlib.import_module(f"process_safety.{m}")

    def test_grade_matches_sources(self):
        for e in sl.entries():
            reads = {s["read"] for s in e["sources"]}
            if e["grade"] == "none":
                self.assertFalse(e["sources"], e["id"])
                self.assertFalse(e["hazards"] or e["initiating_events"] or e["barriers"], f"{e['id']}: unsourced fields must stay blank")
            if e["grade"] == "read":
                self.assertIn("text", reads, e["id"])
            if e["grade"] == "search-summary":
                self.assertNotIn("text", reads, e["id"])
                self.assertTrue(e["sources"], e["id"])

    def test_sources_have_urls(self):
        for e in sl.entries():
            for s in e["sources"]:
                self.assertTrue(s["url"].startswith("http"), e["id"])

    def test_search_and_worksheet(self):
        self.assertTrue(sl.search(text="H2S"))
        self.assertTrue(sl.search(module="expansion"))
        self.assertEqual({e["status"] for e in sl.search(status="blocked")}, {"blocked"})
        rows = sl.worksheet("biogas-cbg")
        self.assertEqual(len(rows), len(sl.get("biogas-cbg")["hazid_prompts"]) + len(sl.get("biogas-cbg")["hazards"]))
        with self.assertRaises(KeyError):
            sl.get("nope")

    def test_blocked_entries_say_why(self):
        for e in sl.search(status="blocked"):
            self.assertTrue(any(w in " ".join(e["gaps"]).lower() for w in ("paywalled", "no open", "unofficial", "gpl", "not copied")), e["id"])

    def test_markdown_is_current(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "docs", "SCENARIO_LIBRARY.md")
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(fh.read().rstrip("\n"), sl.markdown().rstrip("\n"))


if __name__ == "__main__":
    unittest.main()
