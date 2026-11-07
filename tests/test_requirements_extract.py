import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

from process_safety import requirements_extract as rx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = """4.1 General
4.1.1 Every pressure vessel shall be protected by a pressure relief device sized for the governing case.
4.1.2 The relief valve inlet line should be as short as practicable.
4.1.3 Relief devices shall not discharge flammable vapour to atmosphere.
Some background sentence without any modal verb in it at all.
5.2 A high level trip must be independent of the control system. Operators are required to test the trip every year.
"""


def make_docx(path, paragraphs):
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    xml = f'<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}</w:body></w:document>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", xml)


class Extract(unittest.TestCase):
    def test_modality_and_clause(self):
        st = {s["clause"] + "|" + s["modality"] for s in rx.statements(SAMPLE)}
        self.assertIn("4.1.1|mandatory", st)
        self.assertIn("4.1.2|recommended", st)
        self.assertIn("4.1.3|prohibition", st)           # 'shall not' is a prohibition, not a plain mandatory
        self.assertIn("5.2|mandatory", st)
        texts = [s["text"] for s in rx.statements(SAMPLE)]
        self.assertFalse(any("background sentence" in t for t in texts))
        self.assertTrue(any(t.startswith("Operators are required to test") for t in texts))     # second sentence on the same line

    def test_docx_and_text_readers_agree(self):
        with tempfile.TemporaryDirectory() as d:
            t = os.path.join(d, "a.txt")
            x = os.path.join(d, "a.docx")
            with open(t, "w", encoding="utf-8") as fh:
                fh.write(SAMPLE)
            make_docx(x, SAMPLE.splitlines())
            a = [s["text"] for s in rx.statements(rx.read_text(t))]
            b = [s["text"] for s in rx.statements(rx.read_text(x))]
            self.assertEqual(a, b)
            with self.assertRaises(ValueError):
                rx.read_text(os.path.join(d, "a.xyz"))

    def test_classification_and_summary(self):
        with tempfile.TemporaryDirectory() as d:
            t = os.path.join(d, "std.txt")
            with open(t, "w", encoding="utf-8") as fh:
                fh.write(SAMPLE)
            rows = rx.extract([t])
        s = rx.summarize(rows)
        self.assertEqual(s["n"], len(rows))
        self.assertEqual(s["by_modality"]["prohibition"], 1)
        self.assertIn("PSV-ADD", s["by_recommendation_type"])
        self.assertIn("HLL-SIF", s["by_recommendation_type"])
        self.assertEqual(s["by_file"], {"std.txt": len(rows)})

    def test_compare_with_register(self):
        rows = [{"file": "f", "clause": "", "modality": "mandatory", "text": "x", "rec_ids": ["HLL-SIF"], "scope": "sensors"},
                {"file": "f", "clause": "", "modality": "mandatory", "text": "y", "rec_ids": ["DUST"], "scope": "mechanical"}]
        reg = [{"recommendation": "Add independent high level trip", "consequence": "overfill"}]
        c = rx.compare_register(rows, reg)
        self.assertIn("DUST", c["requirement_types_not_in_register"])
        self.assertNotIn("HLL-SIF", c["requirement_types_not_in_register"])


class Cli(unittest.TestCase):
    def run_cli(self, *a):
        return subprocess.run([sys.executable, "-m", "process_safety", *a], capture_output=True, text=True, cwd=ROOT)

    def test_writes_privately_and_prints_counts_only(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "std.txt")
            out = os.path.join(d, "out.csv")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(SAMPLE)
            r = self.run_cli("requirements", src, "--out", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn("pressure relief device sized", r.stdout)       # statement text is not echoed by default
            with open(out, encoding="utf-8") as fh:
                self.assertIn("pressure relief device sized", fh.read())
            shown = self.run_cli("requirements", src, "--out", out, "--show", "1")
            self.assertIn("(mandatory)", shown.stdout)

    def test_refuses_to_write_into_the_tracked_repository(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "std.txt")
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(SAMPLE)
            bad = os.path.join(ROOT, "docs", "_should_not_exist.csv")
            r = self.run_cli("requirements", src, "--out", bad)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(os.path.exists(bad))
            ok = self.run_cli("requirements", src, "--out", os.path.join(ROOT, "requirements_out", "t.csv"))     # git-ignored path
            self.assertEqual(ok.returncode, 0, ok.stderr)
            os.remove(os.path.join(ROOT, "requirements_out", "t.csv"))
            os.rmdir(os.path.join(ROOT, "requirements_out"))

    def test_git_ignored_helper(self):
        self.assertIs(rx.git_ignored(os.path.join(ROOT, "docs", "x.csv")), False)
        self.assertIs(rx.git_ignored(os.path.join(ROOT, "requirements_out", "x.csv")), True)
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(rx.git_ignored(os.path.join(d, "x.csv")))


if __name__ == "__main__":
    unittest.main()
