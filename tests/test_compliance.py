import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest

from process_safety import compliance as cp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "process_safety", "examples", "compliance.json")
D = dt.date(2026, 11, 5)


def clause(tier, status, **kw):
    return {"id": kw.pop("id", "c1"), "tier": tier, "status": status, **kw}


GOOD_MUST = {"justification": "j", "risk_assessment_ref": "R1", "compensating_measures": ["m"], "approved_by_level": "technical-authority", "expiry": "2027-01-01"}


class Tiers(unittest.TestCase):
    def test_modality_mapping(self):
        self.assertEqual([cp.tier_from_modality(m) for m in ("mandatory", "prohibition", "recommended", "permissive")], ["MUST", "MUST", "SHOULD", "CAN"])
        with self.assertRaises(ValueError):
            cp.tier_from_modality("maybe")


class Derogation(unittest.TestCase):
    def codes(self, c):
        return {i["code"] for i in cp.check_derogation(c, D)}

    def test_complete_must_derogation_is_clean(self):
        self.assertEqual(self.codes(clause("MUST", "derogated", derogation=GOOD_MUST)), set())

    def test_must_needs_each_element(self):
        for k, code in (("justification", "no-justification"), ("risk_assessment_ref", "no-risk-assessment"),
                        ("compensating_measures", "no-compensating-measures"), ("expiry", "no-expiry"), ("approved_by_level", "not-approved")):
            d = {x: v for x, v in GOOD_MUST.items() if x != k}
            self.assertIn(code, self.codes(clause("MUST", "derogated", derogation=d)))

    def test_approver_seniority(self):
        d = dict(GOOD_MUST, approved_by_level="project-manager")
        self.assertIn("approver-too-junior", self.codes(clause("MUST", "derogated", derogation=d)))
        d = dict(GOOD_MUST, approved_by_level="president")
        self.assertIn("unknown-approver-level", self.codes(clause("MUST", "derogated", derogation=d)))

    def test_expired(self):
        d = dict(GOOD_MUST, expiry="2026-11-04")
        self.assertIn("expired", self.codes(clause("MUST", "derogated", derogation=d)))
        d = dict(GOOD_MUST, expiry="2026-11-05")
        self.assertNotIn("expired", self.codes(clause("MUST", "derogated", derogation=d)))

    def test_should_is_comply_or_explain(self):
        d = {"justification": "j", "approved_by_level": "discipline-lead"}
        self.assertEqual(self.codes(clause("SHOULD", "derogated", derogation=d)), set())
        self.assertIn("no-justification", self.codes(clause("SHOULD", "derogated", derogation={"approved_by_level": "discipline-lead"})))

    def test_statutory_cannot_be_derogated_internally(self):
        c = clause("MUST", "derogated", statutory=True, derogation=GOOD_MUST)
        self.assertEqual(self.codes(c), {"statutory-no-exemption"})
        c["regulator_ref"] = "EX-123"
        self.assertEqual(self.codes(c), set())


class Evaluate(unittest.TestCase):
    def reg(self, *cs):
        return {"as_of": "2026-11-05", "clauses": list(cs)}

    def test_gate_readiness(self):
        ok = cp.evaluate(self.reg(clause("MUST", "complied", id="a"), clause("MUST", "derogated", id="b", derogation=GOOD_MUST),
                                  clause("SHOULD", "open", id="c"), clause("CAN", "not-adopted", id="d")))
        self.assertTrue(ok["ready_for_gate"])
        self.assertEqual(ok["must_compliance"], {"satisfied": 2, "applicable": 2, "pct": 100.0})
        bad = cp.evaluate(self.reg(clause("MUST", "open", id="a")))
        self.assertFalse(bad["ready_for_gate"])

    def test_open_should_does_not_block_gate_but_is_reported(self):
        r = cp.evaluate(self.reg(clause("SHOULD", "open")))
        self.assertTrue(r["ready_for_gate"])
        self.assertEqual(r["issues"][0]["code"], "open")

    def test_na_needs_reason_for_must(self):
        r = cp.evaluate(self.reg(clause("MUST", "not-applicable")))
        self.assertFalse(r["ready_for_gate"])
        r = cp.evaluate(self.reg(clause("MUST", "not-applicable", na_reason="no vessel in this scope"), clause("MUST", "complied", id="x")))
        self.assertTrue(r["ready_for_gate"])
        self.assertEqual(r["must_compliance"]["applicable"], 1)

    def test_malformed_registers_are_rejected(self):
        for reg in ({"clauses": []}, self.reg(clause("CAN", "derogated")), self.reg(clause("CAN", "complied")), self.reg(clause("MAYBE", "open")),
                    self.reg(clause("MUST", "open"), clause("MUST", "open")), self.reg({"id": "x", "tier": "MUST"})):
            with self.assertRaises(ValueError):
                cp.evaluate(reg)

    def test_bad_date(self):
        d = dict(GOOD_MUST, expiry="soon")
        r = cp.evaluate(self.reg(clause("MUST", "derogated", derogation=d)))
        self.assertIn("bad-date", {i["code"] for i in r["issues"]})

    def test_example_register(self):
        r = cp.evaluate(cp.load(EX))
        self.assertFalse(r["ready_for_gate"])
        codes = {(i["clause"], i["code"]) for i in r["issues"]}
        self.assertIn(("4.2.2", "expired"), codes)
        self.assertIn(("4.2.2", "approver-too-junior"), codes)
        self.assertIn(("9.1", "statutory-no-exemption"), codes)
        self.assertNotIn("4.1.3", {c for c, _ in codes})
        self.assertNotIn("4.1.2", {c for c, _ in codes})


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "process_safety", *args], capture_output=True, text=True, cwd=ROOT)

    def test_check_example(self):
        r = self.run_cli("compliance", EX)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(json.loads(r.stdout)["ready_for_gate"])

    def test_init_from_extract_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            csv_path = os.path.join(d, "x.csv")
            with open(csv_path, "w", encoding="utf-8") as fh:
                fh.write("file,clause,modality,recommendation_types,cost_scope,statement\n"
                         "a.pdf,4.1,mandatory,,,Vessels shall be protected.\na.pdf,4.2,recommended,,,Lines should be short.\na.pdf,4.3,prohibition,,,Vents shall not be sited near air intakes.\n")
            out = os.path.join(d, "reg.json")
            r = self.run_cli("compliance", "--init", csv_path, "--out", out, "--allow-tracked")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)["by_tier"], {"MUST": 2, "SHOULD": 1, "CAN": 0})
            r = self.run_cli("compliance", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(json.loads(r.stdout)["ready_for_gate"])

    def test_refuses_tracked_output(self):
        r = self.run_cli("compliance", "--init", EX, "--out", os.path.join(ROOT, "docs", "reg.json"))
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
