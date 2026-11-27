import copy
import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

from process_safety import hmb_audit, hmb_report, tools, xlsx_write
from process_safety.hmb_audit import FAIL, NC, PASS, REVIEW

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "process_safety", "examples", "hmb.json"), encoding="utf-8") as fh:
    SPEC = json.load(fh)


def closed():
    """The synthetic example with its deliberate faults repaired: V-100 closes, S6 line fixed, S7 enthalpy given, model equals design."""
    d = copy.deepcopy(SPEC)
    s = {x["id"]: x for x in d["streams"]}
    s["S5"].update(mass_kg_h=460, components={"water": (1500 * 0.666667 - 1040 * 0.814) / 460, "ethanol": (1500 * 0.333333 - 1040 * 0.186) / 460})
    s["S6"]["line_no"] = "L-106"
    s["S7"]["H_kW"] = 82.0
    d["lines"] = [x for x in d["lines"] if x["line_no"] != "L-108"]
    d["model_streams"] = copy.deepcopy(d["streams"])
    return d


def unit(r, tag):
    return next(u for u in r["units"] + [r["overall"]] if u["unit"] == tag)


def stream(d, sid, key="streams"):
    return next(x for x in d[key] if x["id"] == sid)


class Verdict(unittest.TestCase):
    def test_consistent_case_passes_everything(self):
        r = hmb_audit.audit(closed())
        self.assertEqual(r["verdict"], PASS, r["findings"])
        self.assertEqual(r["findings"], [])

    def test_shipped_example_shows_each_planted_fault(self):
        r = hmb_audit.audit(copy.deepcopy(SPEC))
        got = {(f["status"], f["area"], f["item"]) for f in r["findings"]}
        for want in [(FAIL, "mass balance", "V-100"), (FAIL, "P&ID link", "S6"), (NC, "energy balance", "P-100"),
                     (FAIL, "design vs model", "S4"), (FAIL, "design vs model", "S5"), (REVIEW, "P&ID link", "L-108")]:
            self.assertIn(want, got)
        self.assertEqual(r["verdict"], FAIL)

    def test_not_checked_alone_is_never_a_pass(self):
        d = closed()
        del d["model_streams"]
        self.assertEqual(hmb_audit.audit(d)["verdict"], NC)


class Identities(unittest.TestCase):
    def test_unit_residuals_sum_to_plant_residual(self):
        r = hmb_audit.audit(copy.deepcopy(SPEC))
        self.assertAlmostEqual(sum(u["mass"]["residual_kg_h"] for u in r["units"]), r["overall"]["mass"]["residual_kg_h"])

    def test_scaling_flows_leaves_relative_closure_unchanged(self):
        d = copy.deepcopy(SPEC)
        for x in d["streams"]:
            x["mass_kg_h"] *= 7.5
        a, b = hmb_audit.audit(copy.deepcopy(SPEC)), hmb_audit.audit(d)
        for u, v in zip(a["units"], b["units"]):
            self.assertAlmostEqual(u["mass"]["residual_rel"], v["mass"]["residual_rel"])

    def test_energy_with_duty_does_not_depend_on_enthalpy_datum(self):
        d = closed()
        for x in d["streams"]:
            x["H_kW"] += 0.05 * x["mass_kg_h"]          # same shift per kg: another datum (mass closes in this case)
        r = hmb_audit.audit(d)
        self.assertAlmostEqual(unit(r, "E-100")["energy"]["residual_kW"], unit(hmb_audit.audit(closed()), "E-100")["energy"]["residual_kW"])

    def test_mole_basis_gives_same_component_closure_as_mass_basis(self):
        mm = {"water": 18.0, "ethanol": 46.0}                # arbitrary test molar masses: only the conversion identity is tested
        d = closed()
        for x in d["streams"]:
            n = {c: w / mm[c] for c, w in x["components"].items()}
            x["components"] = {c: v / sum(n.values()) for c, v in n.items()}
        d.pop("model_streams")
        d.update(component_basis="mole", molar_masses=mm)
        got = unit(hmb_audit.audit(d), "MX-100")["component"]
        self.assertEqual(got["status"], PASS)
        self.assertAlmostEqual(sum(x["in_kg_h"] for x in got["components"]), 1500)


class MissingData(unittest.TestCase):
    def check(self, mutate, tag, kind):
        d = closed()
        mutate(d)
        c = unit(hmb_audit.audit(d), tag)[kind]
        self.assertEqual(c["status"], NC, c)
        self.assertTrue(c["reason"])

    def test_missing_mass_is_not_zero(self):
        for tag in ("MX-100", "WHOLE PLANT"):
            self.check(lambda d: stream(d, "S2").pop("mass_kg_h"), tag, "mass")

    def test_unit_with_both_flows_missing_is_reported(self):
        def f(d):
            for i in ("S3", "S4"):
                stream(d, i)["mass_kg_h"] = None
        self.check(f, "E-100", "mass")

    def test_unit_without_outlet(self):
        self.check(lambda d: d["units"].append({"tag": "TK-9"}), "TK-9", "mass")

    def test_composition_problems(self):
        self.check(lambda d: d.pop("component_basis"), "MX-100", "component")
        self.check(lambda d: stream(d, "S1").update(components={"water": 100.0}), "MX-100", "component")   # percent, not guessed
        self.check(lambda d: d.update(component_basis="mole"), "MX-100", "component")                      # no molar masses
        self.check(lambda d: stream(d, "S1").pop("components"), "MX-100", "component")

    def test_energy_needs_basis_and_duty(self):
        self.check(lambda d: d.pop("enthalpy_basis"), "MX-100", "energy")
        self.check(lambda d: d["units"][0].pop("duty_kW"), "MX-100", "energy")

    def test_dangling_stream_end_blocks_plant_balance(self):
        self.check(lambda d: stream(d, "S5").update(to="X-999"), "WHOLE PLANT", "mass")

    def test_unit_typed_into_a_cell_and_unread_column(self):
        d = closed()
        stream(d, "S2").update(mass_kg_h="500 kg/h", mass_t_h=0.5)
        r = hmb_audit.audit(d)
        msgs = " | ".join(f["message"] for f in r["findings"] if f["area"] == "input")
        self.assertIn("not a plain number", msgs)
        self.assertIn("mass_t_h", msgs)
        self.assertEqual(r["verdict"], FAIL)


class Reactions(unittest.TestCase):
    def spec(self, **unit_extra):
        s = lambda i, f, t, c, H: {"id": i, "from": f, "to": t, "mass_kg_h": 100, "components": c, "H_kW": H}
        return {"component_basis": "mass", "enthalpy_basis": "formation",
                "units": [{"tag": "R-1", "reactive": True, "duty_kW": -10, **unit_extra}],
                "streams": [s("A", "feed", "R-1", {"a": 1.0}, -500), s("B", "R-1", "product", {"b": 1.0}, -510)]}

    def test_without_generation_component_balance_is_not_checked(self):
        r = hmb_audit.audit(self.spec())
        self.assertEqual(unit(r, "R-1")["mass"]["status"], PASS)
        self.assertEqual(unit(r, "R-1")["component"]["status"], NC)
        self.assertEqual(r["overall"]["component"]["status"], NC)

    def test_declared_generation_closes(self):
        r = hmb_audit.audit(self.spec(generation_kg_h={"a": -100, "b": 100}))
        for k in ("mass", "component", "energy"):
            self.assertEqual(unit(r, "R-1")[k]["status"], PASS)
            self.assertEqual(r["overall"][k]["status"], PASS)

    def test_generation_that_creates_mass_fails(self):
        r = hmb_audit.audit(self.spec(generation_kg_h={"a": -80, "b": 100}))
        self.assertIn((FAIL, "reaction"), {(f["status"], f["area"]) for f in r["findings"]})

    def test_energy_needs_formation_basis(self):
        d = self.spec(generation_kg_h={"a": -100, "b": 100})
        d["enthalpy_basis"] = "elements at 25 C sensible only"
        self.assertEqual(unit(hmb_audit.audit(d), "R-1")["energy"]["status"], NC)


class PidLinks(unittest.TestCase):
    def link(self, d, sid):
        return next(x for x in hmb_audit.audit(d)["links"] if x["stream"] == sid)

    def test_end_point_match_and_ambiguity(self):
        d = closed()
        stream(d, "S3").pop("line_no")
        self.assertEqual((self.link(d, "S3")["status"], self.link(d, "S3")["line_no"]), (PASS, "L-103"))
        d["lines"].append({"line_no": "L-103B", "from": "MX-100", "to": "E-100"})
        self.assertEqual(self.link(d, "S3")["status"], NC)

    def test_reversed_line_is_a_conflict(self):
        d = closed()
        next(x for x in d["lines"] if x["line_no"] == "L-103").update({"from": "E-100", "to": "MX-100"})
        self.assertEqual(self.link(d, "S3")["status"], FAIL)

    def test_no_line_list(self):
        d = closed()
        d["lines"] = []
        self.assertEqual(hmb_audit.audit(d)["verdict"], NC)


class ModelConnectivity(unittest.TestCase):
    def conflicts(self, d):
        return [f for f in hmb_audit.audit(d)["findings"] if f["area"] == "design vs model" and "in the model" in f["message"]]

    def test_model_end_moved_to_the_boundary_is_a_conflict(self):
        d = closed()
        stream(d, "S3", "model_streams")["to"] = None          # blank end = plant boundary, as the bridge records it
        self.assertEqual([f["item"] for f in self.conflicts(d)], ["S3"])

    def test_model_without_connectivity_is_not_compared(self):
        d = closed()
        for x in d["model_streams"]:
            x.pop("from")
            x.pop("to")
        self.assertEqual(self.conflicts(d), [])


class Inputs(unittest.TestCase):
    def test_refuses_bad_specs(self):
        for mutate in (lambda d: d.update(streams=[]), lambda d: d["streams"].append(dict(d["streams"][0])),
                       lambda d: d.update(audit={"mass_tolerance": 0.1}), lambda d: d.update(audit={"mass_tol": -1})):
            d = closed()
            mutate(d)
            with self.assertRaises(ValueError):
                hmb_audit.audit(d)

    def test_csv_rows_are_cited_as_sources(self):
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, "s.csv"), "w", encoding="utf-8") as fh:
                fh.write("id,from,to,mass_kg_h\nA,feed,U,5\nB,U,product,5\n")
            r = hmb_audit.audit({"units": [{"tag": "U"}], "streams": "s.csv"}, base_dir=t)
        self.assertEqual(r["streams"][1]["source"], "s.csv row 3")


class Outputs(unittest.TestCase):
    def test_tool_writes_parseable_workbook_page_and_csv(self):
        with tempfile.TemporaryDirectory() as t:
            summ = tools.run_tool("hmb", copy.deepcopy(SPEC), t)
            self.assertTrue(summ["checks"][0].startswith("FAIL"))
            xlsx = os.path.join(t, "hmb_report.xlsx")
            with zipfile.ZipFile(xlsx) as z:
                for n in z.namelist():
                    ET.fromstring(z.read(n))
                book = z.read("xl/workbook.xml").decode()
            for name in ("Summary", "HMB", "Balances", "P&amp;ID links", "Design vs model", "Findings"):
                self.assertIn(name, book)
            with open(os.path.join(t, "hmb_report.html"), encoding="utf-8") as fh:
                page = fh.read()
            ET.fromstring(page[page.index("<svg"):page.index("</svg>") + 6])
            self.assertNotIn("<script", page)

    def test_hostile_text_is_escaped_and_never_a_formula(self):
        d = closed()
        d["name"] = "<script>alert(1)</script>"
        stream(d, "S1")["source"] = "=HYPERLINK(\"x\")\x01"
        r = hmb_audit.audit(d)
        self.assertNotIn("<script", hmb_report.html_page(r))
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "a.xlsx")
            xlsx_write.write_xlsx(p, hmb_report.sheets(r))
            with zipfile.ZipFile(p) as z:
                xml = z.read("xl/worksheets/sheet2.xml").decode()
            ET.fromstring(xml)
            self.assertNotIn("<f>", xml)

    def test_recycle_loop_draws(self):
        s = lambda i, f, t, m: {"id": i, "from": f, "to": t, "mass_kg_h": m}
        r = hmb_audit.audit({"units": [{"tag": "A"}, {"tag": "B"}],
                             "streams": [s("F", "feed", "A", 10), s("AB", "A", "B", 15), s("R", "B", "A", 5), s("P", "B", "product", 10)]})
        self.assertIn("recycle", hmb_report.sankey_svg(r))
        self.assertEqual(r["overall"]["mass"]["status"], PASS)

    def test_column_names(self):
        self.assertEqual([xlsx_write.column_name(i) for i in (0, 25, 26, 701, 702)], ["A", "Z", "AA", "ZZ", "AAA"])


if __name__ == "__main__":
    unittest.main()
