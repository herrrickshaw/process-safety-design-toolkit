import contextlib
import io
import os
import sys
import tempfile
import unittest

from process_safety import modelling_literature as ml
from process_safety import modelling_tags as tags
from process_safety.__main__ import main as cli_main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_modelling_literature as build  # noqa: E402

QUOTE = "the release was modelled with the tool and a mesh of cubic cells"


class Tagging(unittest.TestCase):
    def test_ambiguous_tool_names_need_their_context(self):
        self.assertEqual(tags.tools_in("A slotted ALOHA protocol for sensor networks"), [])
        self.assertIn("aloha", tags.tools_in("ALOHA estimates of a toxic chlorine release"))
        self.assertEqual(tags.tools_in("Reinforced concrete SLAB under load"), [])
        self.assertEqual(tags.tools_in("She is a fluent speaker"), [])
        self.assertIn("fluent", tags.tools_in("CFD simulation in ANSYS Fluent"))
        self.assertEqual(tags.tools_in("FDS regulations for food labelling"), [])
        self.assertIn("fds", tags.tools_in("FDS predictions of a warehouse fire"))

    def test_aspen_dynamics_is_not_counted_as_aspen_plus(self):
        self.assertEqual(tags.tools_in("Control study in Aspen Plus Dynamics"), ["aspen-dynamics"])
        self.assertEqual(tags.tools_in("Steady state in Aspen Plus"), ["aspen-plus"])

    def test_screen_keeps_process_studies_and_drops_other_fields(self):
        self.assertTrue(tags.include("CFD model of hydrogen leak dispersion in a refuelling station"))
        self.assertTrue(tags.include("Distillation column design in Aspen HYSYS"))
        self.assertFalse(tags.include("Quantitative risk assessment model for patients with cancer after gas anaesthesia"))
        self.assertFalse(tags.include("A history of the printing press"))

    def test_adding_text_never_removes_a_tag(self):
        base = "FLACS dispersion model of a gas leak"
        more = base + " followed by an explosion study validated against experiments in OpenFOAM CFD"
        self.assertLessEqual(set(tags.tools_in(base)), set(tags.tools_in(more)))
        self.assertLessEqual(set(tags.studies_in(base)), set(tags.studies_in(more)))


def profile(**change):
    p = {"id": "x-2000", "title": "X", "authors": ["A"], "year": 2000, "doc_type": "journal", "institution_or_venue": "V",
         "url": "https://example.org/x", "saved_text": "x.txt", "read_scope": "all", "study_types": ["dispersion"], "objective": "o",
         "tools": [{"name": "T", "version": "not stated", "role": "r", "quote": QUOTE}],
         "build_steps": [{"step": "s", "quote": QUOTE}], "key_choices": [], "tool_chain": "",
         "validation": {"kind": "none-reported", "detail": "", "quote": ""}, "sensitivity": {"done": False, "detail": "", "quote": ""},
         "limitations": [], "lesson": "l", "caveats": ""}
    p.update(change)
    return p


class Validator(unittest.TestCase):
    def check(self, p, text=None):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.txt"), "w", encoding="utf-8") as fh:
                fh.write(text if text is not None else "word " * 2000 + QUOTE.replace(" a mesh", "\n   a mesh"))
            return build.problems(p, d)

    def test_supported_profile_passes_across_line_breaks(self):
        self.assertEqual(self.check(profile()), ([], []))

    def test_invented_or_missing_quote_is_rejected(self):
        for quote in ("the release was validated against eleven field trials", ""):
            self.assertTrue(self.check(profile(build_steps=[{"step": "s", "quote": quote}]))[0])

    def test_short_saved_text_is_not_a_full_text(self):
        self.assertTrue(any("not a full text" in e for e in self.check(profile(), text=QUOTE)[0]))

    def test_number_absent_from_the_quote_is_flagged(self):
        bad, warn = self.check(profile(build_steps=[{"step": "used 12 cells", "quote": QUOTE}]))
        self.assertEqual(bad, [])
        self.assertTrue(warn and "12" in warn[0])

    def test_document_sharing_link_is_rejected(self):
        self.assertTrue(self.check(profile(url="https://www.scribd.com/x"))[0])

    def test_published_profile_carries_no_quotes_or_local_paths(self):
        row = build.published(profile())
        self.assertNotIn("quote", repr(row))
        self.assertNotIn("saved_text", row)

    def test_map_rows_drop_abstracts_and_shared_copies(self):
        r = {"title": "T", "year": 2000, "authors": list("abcde"), "venue": "", "type": "thesis", "level": "", "doi": "10.1/x",
             "url": "https://www.academia.edu/1", "oa_url": "https://www.researchgate.net/1", "tools": [], "studies": [],
             "text_used": "title only", "found_in": ["x"], "abstract": "SECRET"}
        row = build.map_rows([r])[0]
        self.assertEqual((row["url"], row["open_url"]), ("https://doi.org/10.1/x", ""))
        self.assertEqual(row["authors"], ["a", "b", "c", "et al."])
        self.assertNotIn("SECRET", repr(row))

    def test_links_with_access_tokens_are_not_stored(self):
        r = {"title": "T", "year": 2000, "authors": [], "venue": "", "type": "thesis", "level": "", "doi": "", "tools": [], "studies": [],
             "url": "https://example.org/get?key=abc123", "oa_url": "https://example.org/f?download_token=xyz", "text_used": "title only",
             "found_in": ["x"]}
        self.assertEqual(build.map_rows([r]), [])
        row = build.map_rows([dict(r, doi="10.1/y")])[0]
        self.assertEqual((row["url"], row["open_url"]), ("https://doi.org/10.1/y", ""))
        self.assertTrue(self.check_link("https://example.org/x?jsessionid=1"))

    def check_link(self, url):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "x.txt"), "w", encoding="utf-8") as fh:
                fh.write("word " * 2000 + QUOTE)
            return build.problems(profile(url=url), d)[0]


class Data(unittest.TestCase):
    def test_map_records_well_formed(self):
        rows = ml.records()
        self.assertTrue(rows)
        for r in rows:
            self.assertTrue(r["title"] and r["url"].startswith("http"), r["title"])
            self.assertIn(r["type"], ml.MAP_TYPES)
            self.assertTrue(set(r["tools"]) <= set(tags.TOOLS) and set(r["studies"]) <= set(tags.STUDIES))
            self.assertNotIn("abstract", r)
            self.assertIsNone(build.TOKEN_LINK.search(r["url"] + " " + r["open_url"]), r["title"])
        dois = [r["doi"] for r in rows if r["doi"]]
        self.assertEqual(len(dois), len(set(dois)), "one record per DOI")

    def test_profiles_and_playbooks_well_formed(self):
        ps = ml.profiles()
        ids = [p["id"] for p in ps]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for p in ps:
            with self.subTest(p["id"]):
                self.assertTrue(p["url"].startswith("http") and p["read_scope"] and p["lesson"])
                self.assertIn(p["doc_type"], ml.DOC_TYPES)
                self.assertIn(p["validation"]["kind"], ml.VALIDATION_KINDS)
                self.assertTrue(set(p["study_types"]) <= set(ml.study_labels()))
                self.assertNotIn('"quote"', repr(p))
        self.assertTrue(ml.playbooks())
        for b in ml.playbooks():
            for point in b["points"]:
                self.assertTrue(point["profiles"] and set(point["profiles"]) <= set(ids), point["text"])

    def test_documents_are_in_sync(self):
        for name, make, flag in (("MODELLING_STUDIES.md", ml.markdown, "--markdown"),
                                 ("MODELLING_THESES.md", ml.theses_markdown, "--theses-markdown")):
            with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as fh:
                self.assertEqual(fh.read(), make(), f"stale: python -m process_safety modelling {flag} > docs/{name}")
        text = ml.markdown()
        for p in ml.profiles():
            self.assertIn(p["id"], text)


class Search(unittest.TestCase):
    def test_filters_return_exactly_the_matching_records(self):
        rows = ml.records()
        got = ml.search(study="relief-blowdown", kind="thesis", since=2015, open_only=True)
        want = [r for r in rows if "relief-blowdown" in r["studies"] and r["type"] == "thesis" and (r["year"] or 0) >= 2015 and r["open_url"]]
        self.assertEqual(got, want)
        self.assertEqual(ml.search(), rows)
        self.assertTrue(all("flacs" in r["tools"] for r in ml.search(tool="flacs")))
        self.assertEqual(ml.search("zzzz-no-such-work"), [])
        first = rows[0]["title"]
        self.assertIn(rows[0], ml.search(first.upper()))

    def test_profile_filters(self):
        for p in ml.profiles():
            self.assertIn(p, ml.search_profiles(p["title"]))
            self.assertIn(p, ml.search_profiles(study=p["study_types"][0]))
        self.assertEqual(ml.search_profiles("zzzz-no-such-work"), [])
        self.assertLess(len(ml.search_profiles(tool="flacs")), len(ml.profiles()))

    def test_command_output_paths(self):
        def run(*args):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = cli_main(["modelling", *args])
                except SystemExit as exc:
                    code = exc.code
            return code, out.getvalue(), err.getvalue()

        self.assertEqual(run("--markdown")[1], ml.markdown())
        self.assertEqual(run("--theses-markdown")[1], ml.theses_markdown())
        code, out, _ = run("--tool", "aspen-hysys", "--limit", "3")
        self.assertEqual(code, 0)
        self.assertIn("showing 3 of", out)
        first = ml.profiles()[0]
        self.assertIn(first["id"], run(first["title"], "--read")[1])
        self.assertIn("How the study was built", run(first["title"], "--sheet")[1])
        code, out, err = run("zzzz-no-such-work")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("not exhaustive", err)


if __name__ == "__main__":
    unittest.main()
