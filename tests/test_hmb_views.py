"""Simulator-style views of an HMB audit: flowsheet, stream and unit tables, run summary and fixed-width text report."""
import copy
import os
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from process_safety import hmb_audit, hmb_report, hmb_views
from process_safety.hmb_audit import FAIL, NC, PASS
from tests.test_hmb_audit import SPEC, closed


def faulty():
    return hmb_audit.audit(copy.deepcopy(SPEC))


def clean():
    return hmb_audit.audit(closed())


class StreamStatus(unittest.TestCase):
    def test_worst_status_of_the_stream_wins(self):
        r = faulty()
        self.assertEqual(hmb_views.stream_status(r, "S4"), FAIL)        # model temperature drift
        self.assertEqual(hmb_views.stream_status(r, "S6"), FAIL)        # wrong line number
        self.assertEqual(hmb_views.stream_status(r, "S1"), PASS)

    def test_a_stream_with_no_model_result_is_never_a_pass(self):
        d = closed()
        del d["model_streams"]
        r = hmb_audit.audit(d)
        self.assertEqual({hmb_views.stream_status(r, s["id"]) for s in r["streams"]}, {NC})

    def test_unit_status_is_the_worst_of_its_three_balances(self):
        r = faulty()
        by = {u["unit"]: hmb_views.unit_status(u) for u in r["units"]}
        self.assertEqual(by["V-100"], FAIL)
        self.assertEqual(by["P-100"], NC)
        self.assertEqual(by["MX-100"], PASS)


class Properties(unittest.TestCase):
    def rows(self, r, name):
        return {x["label"]: x for x in dict(hmb_views.property_lists(r))[name]}

    def test_three_lists_each_with_one_cell_per_stream_and_a_units_column(self):
        r = faulty()
        lists = hmb_views.property_lists(r)
        self.assertEqual([n for n, _ in lists], ["Summary", "Material balance", "P&ID"])
        for _, rows in lists:
            for row in rows:
                self.assertEqual(len(row["values"]), len(r["streams"]), row["label"])
                self.assertIn("unit", row)

    def test_component_mass_flows_add_up_to_the_stream_mass(self):
        r = faulty()
        flows = [x for x in self.rows(r, "Material balance").values() if x["unit"] == "kg/h" and x["label"].startswith("Component ")]
        self.assertTrue(flows)
        for i, s in enumerate(r["streams"]):
            self.assertAlmostEqual(sum(x["values"][i] or 0.0 for x in flows), s["mass_kg_h"], places=6)

    def test_unreadable_composition_gives_blank_component_flows_not_zero(self):
        d = copy.deepcopy(SPEC)
        d["streams"][0]["components"] = {"water": 0.5}                  # sums to 0.5
        rows = self.rows(hmb_audit.audit(d), "Material balance")
        self.assertIsNone(rows["Component water"]["values"][0])
        self.assertIsNone(rows["Component ethanol"]["values"][0])

    def test_a_component_absent_from_a_readable_composition_is_zero_in_both_rows(self):
        rows = self.rows(faulty(), "Material balance")
        self.assertEqual(rows["Component ethanol"]["values"][0], 0.0)
        self.assertEqual(rows["Fraction ethanol"]["values"][0], 0.0)

    def test_failed_comparison_carries_the_model_value_on_the_design_cell(self):
        r = faulty()
        row = self.rows(r, "Summary")["Temperature"]
        i = [s["id"] for s in r["streams"]].index("S4")
        self.assertEqual(row["model"], {i: 86.0})


class Flowsheet(unittest.TestCase):
    def test_is_valid_svg_with_every_unit_and_a_linked_flag_per_stream(self):
        r = faulty()
        svg = hmb_views.flowsheet_svg(r)
        ET.fromstring(svg)
        for u in r["units"]:
            self.assertIn(f'href="#unit-{r["units"].index(u)}"', svg)
            self.assertIn(u["unit"], svg)
        for i, s in enumerate(r["streams"]):
            self.assertIn(f'href="#stream-{i}"', svg)
        self.assertIn("L-199", svg)

    def test_no_unit_box_is_crossed_by_a_stream_line(self):
        d = closed()                                                     # add a bypass that skips two units
        d["streams"].append({"id": "S8", "from": "MX-100", "to": "P-100", "mass_kg_h": 0, "H_kW": 0})
        r = hmb_audit.audit(d)
        boxes, paths = hmb_views.flowsheet_layout(r)[:2]
        for p in paths:
            for (x1, y1), (x2, y2) in zip(p["points"], p["points"][1:]):
                self.assertTrue(x1 == x2 or y1 == y2, "orthogonal routing")
                for b in boxes:
                    inside_x = min(x1, x2) < b["x"] + b["w"] - 1 and max(x1, x2) > b["x"] + 1
                    inside_y = min(y1, y2) < b["y"] + b["h"] - 1 and max(y1, y2) > b["y"] + 1
                    self.assertFalse(inside_x and inside_y, f"{p['stream']} crosses {b['key']}")

    def test_hostile_names_are_escaped(self):
        d = closed()
        for key in ("streams", "model_streams"):
            d[key][0]["id"] = '<img src=x>"'
        svg = hmb_views.flowsheet_svg(hmb_audit.audit(d))
        ET.fromstring(svg)
        self.assertNotIn("<img", svg)


class Page(unittest.TestCase):
    def test_page_has_navigation_flowsheet_and_tables_with_unique_targets(self):
        page = hmb_report.html_page(faulty())
        for anchor in ("flowsheet", "streams", "units", "findings"):
            self.assertIn(f'href="#{anchor}"', page)
            self.assertIn(f'id="{anchor}"', page)
        ids = re.findall(r'\sid="([^"]+)"', page)
        self.assertEqual(len(ids), len(set(ids)), "ids must be unique")
        for target in re.findall(r'href="#([^"]+)"', page):
            self.assertIn(target, ids)
        self.assertNotIn("<script", page)

    def test_stream_table_has_streams_as_columns(self):
        r = faulty()
        table = hmb_views.stream_table_html(r)
        head = table.split("</tr>")[0]
        order = [head.index(f">{s['id']}<") for s in r["streams"]]
        self.assertEqual(order, sorted(order))
        self.assertIn("Units", head)
        self.assertIn("model 86", table)

    def test_run_summary_names_the_largest_residual(self):
        facts = dict(hmb_views.run_summary(faulty()))
        self.assertIn("V-100", facts["Largest mass residual"])
        self.assertIn("FAIL", facts["Run status"])

    def test_run_summary_does_not_report_a_residual_it_never_computed(self):
        d = closed()
        for s in d["streams"]:
            s["mass_kg_h"] = None
        facts = dict(hmb_views.run_summary(hmb_audit.audit(d)))
        self.assertEqual(facts["Largest mass residual"], "not computed: no unit mass balance could be run")
        self.assertEqual(facts["Largest component residual"], "not computed: no component balance could be run")


class TextReport(unittest.TestCase):
    def test_sections_in_order_and_lines_fit_the_page(self):
        text = hmb_views.text_report(faulty())
        heads = ["RUN SUMMARY", "MESSAGES", "STREAM SUMMARY", "UNIT SUMMARY", "P&ID LINKS", "DESIGN VS MODEL", "TOLERANCES AND LIMITS"]
        at = [text.index("\n" + h + "\n") for h in heads]
        self.assertEqual(at, sorted(at))
        self.assertLessEqual(max(len(x) for x in text.splitlines()), hmb_views.WIDTH)
        self.assertTrue(text.isascii())

    def test_every_stream_appears_once_per_property_list_across_pages(self):
        d = closed()
        for i in range(8, 20):
            d["streams"].append({"id": f"S{i}", "from": "battery_limit", "to": "battery_limit", "mass_kg_h": 1.0})
        text = hmb_views.text_report(hmb_audit.audit(d))
        body = text.split("\nSTREAM SUMMARY\n")[1].split("\nUNIT SUMMARY\n")[0]
        header_ids = [t for line in body.splitlines() if line.startswith("Stream ") for t in line.split()[2:]]
        self.assertEqual(len(header_ids), 3 * 19)

    def test_missing_value_prints_as_a_dash_not_zero(self):
        text = hmb_views.text_report(faulty())
        row = [x for x in text.splitlines() if x.startswith("Enthalpy flow")]
        self.assertTrue(any(x.rstrip().endswith("-") for x in row), row)

    def test_written_with_the_other_reports(self):
        with tempfile.TemporaryDirectory() as t:
            files = hmb_report.write(clean(), os.path.join(t, "x"))
            self.assertEqual([os.path.basename(f) for f in files],
                             ["x_report.xlsx", "x_report.html", "x_findings.csv", "x_report.txt"])
            self.assertTrue(os.path.getsize(files[3]) > 0)


class Fallbacks(unittest.TestCase):
    def test_a_reaction_that_does_not_conserve_mass_fails_the_unit_even_if_its_balances_pass(self):
        u = copy.deepcopy(clean()["units"][0])
        self.assertEqual(hmb_views.unit_status(u), PASS)
        u["generation"] = {"status": FAIL, "reason": "generation does not sum to zero"}
        self.assertEqual(hmb_views.unit_status(u), FAIL)

    def test_a_very_large_value_keeps_its_magnitude_and_fits_the_column(self):
        d = closed()
        for key in ("streams", "model_streams"):
            d[key][0]["mass_kg_h"] = 2.5e12
        r = hmb_audit.audit(d)
        self.assertIn(">2.5e+12<", hmb_views.stream_table_html(r))
        self.assertIn("2.5e+12", hmb_views.text_report(r))

    def test_run_summary_says_when_no_energy_balance_could_be_run(self):
        d = closed()
        del d["enthalpy_basis"]
        facts = dict(hmb_views.run_summary(hmb_audit.audit(d)))
        self.assertEqual(facts["Largest energy residual"], "not computed: no energy balance could be run")

    def test_an_unrecognised_equipment_type_is_a_plain_box_with_no_symbol(self):
        d = closed()
        d["units"][0]["type"] = "widget"
        r = hmb_audit.audit(d)
        root = ET.fromstring(hmb_views.flowsheet_svg(r))
        unit_link = next(a for a in root.iter("a") if a.get("href") == "#unit-0")
        self.assertEqual(unit_link.find("rect").get("rx"), "3")
        self.assertEqual(len(unit_link.find("g")), 0)

    def test_text_report_says_when_there_are_no_model_results(self):
        d = closed()
        del d["model_streams"]
        text = hmb_views.text_report(hmb_audit.audit(d))
        self.assertIn("\nNot compared: no model results.\n", text)


if __name__ == "__main__":
    unittest.main()
