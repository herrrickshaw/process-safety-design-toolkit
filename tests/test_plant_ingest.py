import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

from process_safety import depressuring, hmb, overfill, pid_review, plant_model, relief, scenario_ingest, scenarios

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "process_safety", "examples", "plant.json"), encoding="utf-8") as fh:
    SPEC = json.load(fh)


def model():
    return plant_model.load(copy.deepcopy(SPEC))


PROTEUS = """<?xml version="1.0" encoding="UTF-8"?>
<PlantModel>
  <PlantInformation Application="test" Date="2026-01-01"/>
  <Equipment ID="E1" TagName="V-900" ComponentClass="Vessel">
    <MaximumDesignPressure Value="1700" Units="kPa"/>
    <MaximumDesignTemperature Value="80" Units="degC"/>
    <MinimumDesignTemperature Value="-20" Units="degC"/>
    <Nozzle ID="N1" TagName="N1"><NominalDiameter Value="150" Units="mm"/></Nozzle>
  </Equipment>
  <Equipment ID="E2" TagName="V-901" ComponentClass="Vessel"><MaximumDesignPressure Value="7" Units="bar"/></Equipment>
  <PipingNetworkSystem ID="PS1" TagName="PS-1">
    <PipingNetworkSegment ID="SEG1" TagName="L-9001">
      <NominalDiameter Value="150" Units="mm"/><InsideDiameter Value="154.1" Units="mm"/><MaximumDesignPressure Value="1700" Units="kPa"/>
      <Connection FromID="E1" ToID="E2"/>
      <PipingComponent ID="PC1" TagName="PSV-900" ComponentClass="SafetyValve"/>
      <PipingComponent ID="PC2" TagName="CV-900" ComponentClass="CheckValve"/>
    </PipingNetworkSegment>
  </PipingNetworkSystem>
  <ProcessInstrumentationFunction ID="I1" TagName="LAHH-900" ComponentClass="ProcessInstrumentationFunction"/>
</PlantModel>"""


class Ingest(unittest.TestCase):
    def test_csv_and_inline_sections_and_orifice_area(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "u.csv"), "w", encoding="utf-8") as fh:
                fh.write("tag,type,design_P_kpag,volume_m3\nV-1,vessel,1000,5.5\nV-2,drum,,\n")
            m = plant_model.load({"units": "u.csv", "relief_devices": [{"tag": "PSV-1", "unit": "V-1", "orifice": "J"}],
                                  "lines": [{"line_no": "L1", "from": "V-1", "to": "V-2", "nps": 6}]}, base_dir=d)
        self.assertEqual(m["units"][0]["design_P_kpag"], 1000)
        self.assertIsNone(m["units"][1]["design_P_kpag"])
        self.assertAlmostEqual(m["relief_devices"][0]["area_mm2"], relief.API526_ORIFICES_MM2["J"])
        self.assertEqual(m["lines"][0]["id_mm"], 154.1)

    def test_validate_flags_unknown_references(self):
        bad = copy.deepcopy(SPEC)
        bad["streams"][0]["to"] = "V-999"
        bad["instruments"][0]["unit"] = "V-998"
        e = plant_model.validate(plant_model.load(bad))
        self.assertTrue(any("V-999" in x for x in e) and any("V-998" in x for x in e))
        self.assertEqual(plant_model.validate(model()), [])

    def test_proteus_xml(self):
        px = plant_model.from_proteus_xml(PROTEUS)
        u = {x["tag"]: x for x in px["units"]}
        self.assertEqual(u["V-900"]["design_P_kpag"], 1700.0)
        self.assertEqual(u["V-900"]["mdmt_C"], -20.0)
        self.assertAlmostEqual(u["V-901"]["design_P_kpag"], 700.0)          # 7 bar -> kPa
        self.assertEqual(px["lines"][0]["line_no"], "L-9001")
        self.assertEqual((px["lines"][0]["from"], px["lines"][0]["to"]), ("V-900", "V-901"))
        self.assertEqual(px["lines"][0]["id_mm"], 154.1)
        self.assertEqual([d["tag"] for d in px["relief_devices"]], ["PSV-900"])
        self.assertEqual([v["type"] for v in px["valves"]], ["check"])
        self.assertEqual(px["instruments"][0]["type"], "LAHH")
        self.assertTrue(any("gauge" in n for n in px["notes"]))
        m = plant_model.load({"units": [{"tag": "V-900", "type": "vessel", "design_P_kpag": 9999}], "proteus_xml": PROTEUS})
        self.assertEqual({x["tag"]: x["design_P_kpag"] for x in m["units"]}["V-900"], 9999)     # explicit data wins over the file
        self.assertIn("V-901", {x["tag"] for x in m["units"]})
        self.assertEqual(len(m["relief_devices"]), 1)


class Hmb(unittest.TestCase):
    def test_balance_closes_and_detects_mismatch(self):
        self.assertTrue(all(b["status"] == "ok" for b in hmb.balance(model())))
        bad = copy.deepcopy(SPEC)
        bad["streams"][1]["mass_kg_h"] = 20000
        r = {b["unit"]: b for b in hmb.balance(plant_model.load(bad))}
        self.assertNotEqual(r["V-101"]["status"], "ok")

    def test_hazard_flags_from_rmp_lists(self):
        h = hmb.unit_hazards(model())
        self.assertTrue(h["V-101"]["flammable"])
        self.assertTrue(h["T-201"]["flammable"])
        self.assertFalse(h["E-301"]["flammable"])

    def scn(self, unit, name):
        return [s for s in hmb.scenarios_for(model()) if s["unit"] == unit and s["scenario"] == name]

    def test_blocked_outlet_matches_relief_module(self):
        s = self.scn("V-101", "blocked_outlet")[0]
        r = relief.gas_area(50000, 313.15, relief.relieving_pressure_kpa(1500, "single_non_fire"), relief.ATM, 20, 1.3, 1.0, set_g_kpa=1500)
        self.assertAlmostEqual(s["numbers"]["required_area_mm2"], r.required_area_mm2)
        self.assertEqual(s["status"], "gap")
        self.assertIn("PSV-UPSIZE", s["rec_ids"])
        self.assertEqual(self.scn("V-102", "blocked_outlet")[0]["rec_ids"], ["PSV-ADD"])

    def test_overfill_arithmetic_and_registered_trip(self):
        s = self.scn("T-201", "overfill")[0]
        t = overfill.time_to_overfill_s(100 * 0.10, 20000 / 500)
        self.assertAlmostEqual(s["numbers"]["time_to_overfill_min"], t / 60)
        self.assertAlmostEqual(s["numbers"]["needed_min"], (600 + 60) * 2 / 60)
        self.assertEqual(s["status"], "gap")
        ok = copy.deepcopy(SPEC)
        ok["units"][2]["level_pct"] = 50
        self.assertEqual([x for x in hmb.scenarios_for(plant_model.load(ok)) if x["scenario"] == "overfill"][0]["status"], "adequate")
        trip = copy.deepcopy(SPEC)
        trip["instruments"].append({"tag": "LSHH-201", "type": "LSHH", "unit": "T-201", "loop": "SIS", "function": "trip"})
        self.assertEqual([x for x in hmb.scenarios_for(plant_model.load(trip)) if x["scenario"] == "overfill"][0]["status"], "review")

    def test_interface_mdmt_and_tube_rupture(self):
        i = self.scn("V-102", "interface")[0]
        self.assertEqual((i["numbers"]["stream_P_kpag"], i["numbers"]["design_P_kpag"]), (1400, 700))
        m = self.scn("V-101", "mdmt")[0]
        self.assertAlmostEqual(m["numbers"]["min_gas_temp_C"], depressuring.min_gas_temperature_K(313.15, 1400 + relief.ATM, relief.ATM, 1.3) - 273.15)
        self.assertEqual(m["status"], "gap")
        t = [s for s in hmb.scenarios_for(model()) if s["scenario"] == "tube_rupture"][0]
        self.assertFalse(scenarios.tube_rupture_exempt(9000, 5000))
        flow = scenarios.tube_rupture_flow_kg_s(0.019, 8000 + relief.ATM, 2500 + relief.ATM, "vapour", T_K=350, M=20, k=1.3)
        self.assertAlmostEqual(t["numbers"]["rupture_flow_kg_s"], flow)
        ex = copy.deepcopy(SPEC)
        ex["exchangers"][0]["lp_design_kpag"] = 7000
        self.assertEqual([s for s in hmb.scenarios_for(plant_model.load(ex)) if s["scenario"] == "tube_rupture"][0]["status"], "adequate")

    def test_missing_inputs_are_reported_not_guessed(self):
        bad = copy.deepcopy(SPEC)
        del bad["streams"][0]["k"]
        s = [x for x in hmb.scenarios_for(plant_model.load(bad)) if x["unit"] == "V-101" and x["scenario"] == "blocked_outlet"][0]
        self.assertEqual(s["status"], "cannot_assess")
        self.assertIn("k", s["missing"])


class Review(unittest.TestCase):
    def test_rules(self):
        f = pid_review.review(model(), isolation_inventory_kg=20000)
        rules = {(x["rule"], x["unit"]) for x in f}
        self.assertIn(("R1", "V-102"), rules)
        self.assertIn(("R2", "T-201"), rules)        # atmospheric discharge in flammable service
        self.assertIn(("R3", "T-201"), rules)        # level only in the control system
        self.assertIn(("R5", "V-102"), rules)        # no detector
        self.assertNotIn(("R5", "V-101"), rules)     # GD-101 registered
        self.assertIn(("R6", "V-102"), rules)
        self.assertIn(("R7", "T-201"), rules)
        self.assertNotIn(("R7", "V-101"), rules)     # XV-101 registered / below limit

    def test_r4_needs_required_sil(self):
        d = copy.deepcopy(SPEC)
        d["units"][2]["sil_required"] = 2
        self.assertIn(("R4", "T-201"), {(x["rule"], x["unit"]) for x in pid_review.review(plant_model.load(d))})
        self.assertNotIn("R4", {x["rule"] for x in pid_review.review(model())})


class Register(unittest.TestCase):
    def test_classification_and_crosscheck(self):
        reg = scenario_ingest.read_register(SPEC["register"])
        c = scenario_ingest.classify_register(reg)
        self.assertGreaterEqual(c["n_with_recommendation"], 6)
        by = {r["id"]: r for r in reg}
        self.assertIn("HLL-SIF", by["H3"]["rec_ids"])
        self.assertIn("PSV-ADD", by["H2"]["rec_ids"])
        rat = scenario_ingest.rationale(model(), None, reg, 20000)
        key = {(r["unit"], r["rec_id"]): r for r in rat["rationale"]}
        self.assertTrue(key[("V-102", "PSV-ADD")]["in_register"])            # H2 covers it
        self.assertTrue(key[("T-201", "HLL-SIF")]["in_register"])            # H3 covers it
        self.assertFalse(key[("V-101", "MATERIAL")]["in_register"])          # nobody mentioned MDMT
        self.assertFalse(key[("T-201", "DETECT")]["in_register"])
        self.assertIn("pid_review", key[("V-102", "PSV-ADD")]["sources"])
        self.assertIn("hmb", key[("V-102", "PSV-ADD")]["sources"])           # both routes reach the same recommendation
        self.assertEqual(len(key[("V-102", "PSV-ADD")]["reasons"]), 2)
        self.assertTrue(all(g["in_register"] is False for g in rat["gaps_not_in_register"]))

    def test_without_register_the_flag_is_none(self):
        rat = scenario_ingest.rationale(model(), None, None)
        self.assertTrue(all(r["in_register"] is None for r in rat["rationale"]))
        self.assertEqual(rat["gaps_not_in_register"], [])

    def test_workflow_skeleton_lists_what_is_missing(self):
        rat = scenario_ingest.rationale(model(), None, None)
        sk = scenario_ingest.workflow_skeleton(model(), rat)
        tags = {u["tag"] for u in sk["units"]}
        self.assertIn("V-101", tags)
        v101 = [u for u in sk["units"] if u["tag"] == "V-101"][0]
        self.assertEqual(v101["existing"]["psv_area_mm2"], relief.API526_ORIFICES_MM2["J"])
        self.assertEqual(v101["fluid"]["M"], 20)
        self.assertTrue(any(t.startswith("V-101: install") for t in sk["todo"]))


class Tool(unittest.TestCase):
    def test_tool_end_to_end(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "plant", "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            s = json.loads(r.stdout)
            self.assertIn("HLL-SIF", s["triggered_recommendation_types"])
            self.assertTrue(s["gaps_not_in_register"])
            self.assertEqual(len(s["files"]), 3)
            for f in s["files"]:
                self.assertTrue(os.path.getsize(f) > 0, f)


if __name__ == "__main__":
    unittest.main()
