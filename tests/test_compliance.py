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


PESTLE = {f: {"rating": 1, "note": "n"} for f in cp.PESTLE_FACTORS}
CONS = {"scenario": "s", "safety_severity": 3, "pestle": PESTLE}      # medium class
GOOD_MUST = {"justification": "j", "risk_assessment_ref": "R1", "compensating_measures": ["m"], "expiry": "2027-01-01",
             "consequence": CONS, "approvals": [{"level": "TA2", "name": "x"}]}


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
                        ("compensating_measures", "no-compensating-measures"), ("expiry", "no-expiry"),
                        ("approvals", "not-approved"), ("consequence", "no-consequence-assessment")):
            d = {x: v for x, v in GOOD_MUST.items() if x != k}
            self.assertIn(code, self.codes(clause("MUST", "derogated", derogation=d)))

    def test_missing_consequence_is_treated_as_severe(self):
        d = {x: v for x, v in GOOD_MUST.items() if x != "consequence"}
        self.assertIn("approval-insufficient", self.codes(clause("MUST", "derogated", derogation=d)))   # TA2 alone is not enough for severe

    def test_expired(self):
        d = dict(GOOD_MUST, expiry="2026-11-04")
        self.assertIn("expired", self.codes(clause("MUST", "derogated", derogation=d)))
        d = dict(GOOD_MUST, expiry="2026-11-05")
        self.assertNotIn("expired", self.codes(clause("MUST", "derogated", derogation=d)))

    def test_should_is_comply_or_explain(self):
        d = {"justification": "j", "consequence": {"safety_severity": 1}, "approvals": [{"level": "TA3"}]}
        self.assertEqual(self.codes(clause("SHOULD", "derogated", derogation=d)), set())
        self.assertIn("no-justification", self.codes(clause("SHOULD", "derogated", derogation={"approvals": [{"level": "TA3"}], "consequence": {"safety_severity": 1}})))

    def test_statutory_cannot_be_derogated_internally(self):
        c = clause("MUST", "derogated", statutory=True, derogation=GOOD_MUST)
        self.assertEqual(self.codes(c), {"statutory-no-exemption"})
        c["regulator_ref"] = "EX-123"
        self.assertEqual(self.codes(c), set())


class Matrix(unittest.TestCase):
    def test_class_from_highest_rating(self):
        self.assertEqual(cp.consequence_class({"safety_severity": 1})[0], "low")
        self.assertEqual(cp.consequence_class({"safety_severity": 3})[0], "medium")
        self.assertEqual(cp.consequence_class({"safety_severity": 1, "pestle": {"legal": {"rating": 4}}}), ("high", ["legal"]))
        self.assertEqual(cp.consequence_class({"pestle": {"social": {"rating": 5}, "legal": {"rating": 5}}}), ("severe", ["legal", "social"]))
        self.assertEqual(cp.consequence_class(None), ("severe", []))

    def test_bad_ratings_and_factors(self):
        for c in ({"safety_severity": 6}, {"pestle": {"legal": {"rating": -1}}}, {"pestle": {"military": {"rating": 1}}}):
            with self.assertRaises(ValueError):
                cp.consequence_class(c)

    def test_matrix_cells(self):
        m = cp.APPROVAL_MATRIX
        self.assertEqual(m["MUST"]["severe"], ("TA1", "TA2"))
        self.assertEqual(m["SHOULD"]["low"], ("TA3",))
        for t in m:                                   # authority never falls as consequence rises
            top = [max(cp._level(x) for x in m[t][c]) for _, c in cp.CLASS_THRESHOLDS]
            self.assertEqual(top, sorted(top))

    def test_higher_level_can_stand_in_but_not_twice(self):
        self.assertEqual(cp._signoffs_met(("TA2",), [{"level": "TA1"}]), [])
        self.assertEqual(cp._signoffs_met(("TA1",), [{"level": "TA2"}]), ["TA1"])
        self.assertEqual(cp._signoffs_met(("TA1", "TA2"), [{"level": "TA1"}]), ["TA2"])      # one person cannot fill both
        self.assertEqual(cp._signoffs_met(("TA1", "TA2"), [{"level": "TA1"}, {"level": "TA2"}]), [])

    def test_pestle_rules(self):
        def codes(cons):
            d = dict(GOOD_MUST, consequence=cons, approvals=[{"level": "TA1"}, {"level": "TA2"}])
            return {i["code"] for i in cp.check_derogation(clause("MUST", "derogated", derogation=d), D)}
        self.assertIn("pestle-incomplete", codes({"scenario": "s", "pestle": {"legal": {"rating": 1}}}))
        hot = dict(PESTLE, economic={"rating": 3, "note": "n"})
        self.assertIn("pestle-no-action", codes({"scenario": "s", "pestle": hot}))
        self.assertNotIn("pestle-no-action", codes({"scenario": "s", "pestle": hot, "management_actions": {"economic": "spare on site"}}))

    def test_review_reports_the_pestle_map(self):
        d = dict(GOOD_MUST, consequence=dict(CONS, pestle=dict(PESTLE, legal={"rating": 4, "note": "notice"}), management_actions={"legal": "talk to regulator"}),
                 approvals=[{"level": "TA1"}])
        r = cp.review(clause("MUST", "derogated", derogation=d))
        self.assertEqual((r["consequence_class"], r["required_signoffs"], r["unmet"]), ("high", ["TA1"], []))
        self.assertEqual(r["driven_by"], ["legal"])
        self.assertEqual(r["pestle"]["legal"]["management_action"], "talk to regulator")
        self.assertEqual(set(r["pestle"]), set(cp.PESTLE_FACTORS))


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
        self.assertIn(("4.2.2", "approval-insufficient"), codes)
        self.assertIn(("4.2.2", "pestle-incomplete"), codes)
        rv = {x["clause"]: x for x in r["derogation_reviews"]}
        self.assertEqual((rv["4.1.3"]["consequence_class"], rv["4.1.3"]["unmet"]), ("high", []))
        self.assertEqual(rv["4.2.2"]["unmet"], ["TA2"])
        self.assertNotIn("9.1", rv)
        self.assertIn(("9.1", "statutory-no-exemption"), codes)
        self.assertEqual({k for c, k in codes if c == "4.1.3"}, {"seveso-documents-not-updated"})
        self.assertNotIn("4.1.2", {c for c, _ in codes})


LB_IMPL = {"regime": "EU", "instrument": "Directive 2012/18/EU", "article": "10(1)(c)", "relation": "implements"}
LB_IS = dict(LB_IMPL, relation="is")
SEV_OK = {"significant": True, "rationale": "r", "authority_informed": "2026-10-01",
          "documents_updated": ["notification", "MAPP", "safety management system", "safety report"]}


class EuCompliance(unittest.TestCase):
    def codes(self, c, seveso="upper"):
        return {i["code"] for i in cp.check_derogation(c, D, seveso)}

    def must(self, **extra):
        return clause("MUST", "derogated", derogation=dict(GOOD_MUST, approvals=[{"level": "TA1"}, {"level": "TA2"}], **extra))

    def test_clause_that_is_the_eu_text_cannot_be_derogated_internally(self):
        c = self.must(); c["legal_basis"] = LB_IS
        self.assertEqual(self.codes(c), {"statutory-no-exemption"})
        c["regulator_ref"] = "CA-1"
        self.assertEqual(self.codes(c), set())

    def test_implementing_clause_needs_equivalence_and_is_floored_to_high(self):
        c = self.must(seveso_assessment=SEV_OK); c["legal_basis"] = LB_IMPL
        self.assertIn("eu-equivalence-not-shown", self.codes(c))
        c["derogation"]["eu_equivalence"] = "how"
        self.assertEqual(self.codes(c), set())
        s = clause("SHOULD", "derogated", legal_basis=LB_IMPL, derogation={"justification": "j", "eu_equivalence": "e", "consequence": {"safety_severity": 1},
                                                                           "approvals": [{"level": "TA3"}], "seveso_assessment": SEV_OK})
        self.assertEqual(cp.effective_class(s)[0], "high")
        self.assertIn("approval-insufficient", self.codes(s))               # SHOULD / high needs TA2, TA3 is not enough
        s["derogation"]["approvals"] = [{"level": "TA2"}]
        self.assertEqual(self.codes(s), set())

    def test_seveso_article_11_screening(self):
        c = self.must()
        self.assertIn("seveso-not-assessed", self.codes(c))
        self.assertNotIn("seveso-not-assessed", self.codes(c, seveso=None))
        c["derogation"]["seveso_assessment"] = {"significant": False, "rationale": "cosmetic"}
        self.assertEqual(self.codes(c), set())
        c["derogation"]["seveso_assessment"] = {"significant": True, "rationale": "r"}
        self.assertEqual(self.codes(c), {"seveso-authority-not-informed", "seveso-documents-not-updated"})
        c["derogation"]["seveso_assessment"] = SEV_OK
        self.assertEqual(self.codes(c), set())

    def test_lower_tier_has_no_safety_report(self):
        c = self.must(seveso_assessment=dict(SEV_OK, documents_updated=["notification", "MAPP", "safety management system"]))
        self.assertEqual(self.codes(c, "lower"), set())
        self.assertIn("seveso-documents-not-updated", self.codes(c, "upper"))

    def test_low_should_departure_is_not_screened(self):
        s = clause("SHOULD", "derogated", derogation={"justification": "j", "consequence": {"safety_severity": 1}, "approvals": [{"level": "TA3"}]})
        self.assertEqual(self.codes(s), set())

    def test_summary_and_validation(self):
        r = cp.evaluate(cp.load(EX))
        eu = r["eu_compliance"]
        self.assertEqual((eu["seveso_tier"], eu["non_derogable_eu_clauses"], eu["art11_significant"], eu["art11_unassessed"]), ("upper", ["9.1"], ["4.1.3"], ["4.2.2"]))
        self.assertIn(("4.1.3", "seveso-documents-not-updated"), {(i["clause"], i["code"]) for i in r["issues"]})
        self.assertIsNone(cp.evaluate({"as_of": "2026-11-05", "clauses": [clause("MUST", "complied")]})["eu_compliance"])
        with self.assertRaises(ValueError):
            cp.evaluate({"seveso": "medium", "clauses": [clause("MUST", "complied")]})
        with self.assertRaises(ValueError):
            cp.check_derogation(clause("MUST", "derogated", legal_basis=dict(LB_IMPL, relation="maybe"), derogation=GOOD_MUST), D)


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

    def test_matrix_flag(self):
        r = self.run_cli("compliance", "--matrix")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, cp.matrix_markdown())

    def test_refuses_tracked_output(self):
        r = self.run_cli("compliance", "--init", EX, "--out", os.path.join(ROOT, "docs", "reg.json"))
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
