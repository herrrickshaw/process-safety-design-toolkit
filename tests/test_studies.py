"""Tests for bow-tie, buildings/OBRA, emergency zones, SIL lifecycle, F&G mapping, PHA management, thermal runaway, ATEX, RAM."""
import datetime as dt
import json
import math
import os
import tempfile
import unittest

from process_safety import atex, bowtie, fg_mapping, pha, ram, sil, sil_lifecycle, thermal_runaway as tr
from process_safety.qra import buildings, effects, emergency, study
from process_safety.tools import run_tool

EX = os.path.join(os.path.dirname(__file__), "..", "process_safety", "examples")
QEX = os.path.join(os.path.dirname(__file__), "..", "process_safety", "qra", "examples", "lpg_terminal.json")


def load(name):
    with open(os.path.join(EX, f"{name}.json"), encoding="utf-8") as fh:
        return json.load(fh)


class BowTie(unittest.TestCase):
    def setUp(self):
        self.bt = {"top_event": "LOC", "threats": [{"name": "T1", "frequency_per_yr": 0.1, "barriers": [{"name": "B1", "pfd": 0.1}, {"name": "B2", "pfd": 0.01}]},
                                                   {"name": "T2", "frequency_per_yr": 0.01, "barriers": [{"name": "B1", "pfd": 0.1}]}],
                   "consequences": [{"name": "C1", "probability": 0.3, "barriers": [{"name": "M1", "pfd": 0.1}], "severity_weight": 10},
                                    {"name": "C2", "probability": 0.7, "severity_weight": 1}]}

    def test_arithmetic(self):
        r = bowtie.evaluate(self.bt)
        self.assertAlmostEqual(r["top_per_yr"], 0.1 * 0.1 * 0.01 + 0.01 * 0.1)
        self.assertAlmostEqual(r["consequences"][0]["mitigated_per_yr"], r["top_per_yr"] * 0.3 * 0.1)
        self.assertAlmostEqual(sum(c["unmitigated_per_yr"] for c in r["consequences"]), r["top_per_yr"])

    def test_shared_barrier_counted_once_and_importance(self):
        imp = {b["name"]: b for b in bowtie.importance(self.bt)}
        base = bowtie.evaluate(self.bt)["risk"]
        self.assertAlmostEqual(imp["B1"]["RAW"], bowtie.evaluate(self.bt, {"B1": 1.0})["risk"] / base)
        self.assertEqual(imp["B1"]["legs"], "T1; T2")
        self.assertTrue(math.isinf(imp["M1"]["RRW"]) is False)

    def test_escalation_and_checks(self):
        bt = json.loads(json.dumps(self.bt))
        bt["threats"][0]["barriers"][0]["escalation"] = [{"factor": "x", "p_present": 0.5, "pfd_if_present": 1.0}]
        self.assertAlmostEqual(bowtie._pfd(bt["threats"][0]["barriers"][0], {}), 0.5 * 0.1 + 0.5 * 1.0)
        bt["consequences"][0]["probability"] = 0.9
        self.assertTrue(any("sum to" in e for e in bowtie.check(bt)))

    def test_example_runs(self):
        with tempfile.TemporaryDirectory() as d:
            s = run_tool("bowtie", load("bowtie"), d, progress=False)
            self.assertIn("Independent HH level trip (SIF)", s["SCEs"])
            self.assertTrue(all(c.startswith("PASS") for c in s["checks"]))


class SilLifecycle(unittest.TestCase):
    def test_tables(self):
        self.assertEqual([sil_lifecycle.sil_from_rrf(r) for r in (5, 50, 500, 5000, 50000)], [0, 1, 2, 3, 4])
        self.assertEqual(sil_lifecycle.HFT_TABLE6, {1: 0, 2: 0, 3: 1, 4: 2})
        self.assertEqual(sil_lifecycle.route_1h_max_sil("B", 0.5, 0), 0)
        self.assertEqual(sil_lifecycle.route_1h_max_sil("B", 0.95, 1), 3)
        self.assertEqual(sil_lifecycle.route_1h_max_sil("A", 0.5, 0), 1)
        self.assertEqual(sil_lifecycle.hft_of("2oo3"), 1)
        self.assertAlmostEqual(sil_lifecycle.sff(3, 5, 2), 0.8)

    def test_verification_sums_and_architecture_cap(self):
        v = sil_lifecycle.verify_sif(load("sif"))
        self.assertAlmostEqual(v["PFDavg"], sum(s["PFDavg"] for s in v["subsystems"]))
        self.assertEqual(v["SIL_by_architecture"], 1)  # type A SDV, SFF 40 %, HFT 0, Route 1H
        self.assertFalse(v["meets_target"])
        self.assertAlmostEqual(v["subsystems"][2]["PFDavg"], sil.pfd_avg("1oo1", 1.5e-6, 8760))

    def test_risk_graph_refuses_uncalibrated(self):
        with self.assertRaises(KeyError):
            sil_lifecycle.risk_graph({"C": 4, "F": 2, "P": 2, "W": 3}, {"C2-F1-P2-W2": "SIL 1"})


class Thermal(unittest.TestCase):
    def test_stoessel_reproduces_epsc_examples(self):
        self.assertEqual(tr.stoessel_class(81, 56, 130), 3)   # Tp 40, MTSR 81, TD24 130, MTT 56 -> class 3 (TUV SUD EPSC lecture)
        self.assertEqual(tr.stoessel_class(200, 125, 90), 5)  # MTSR 200, MTT 125, TD24 90 -> class 5
        self.assertEqual([tr.stoessel_class(*c) for c in ((60, 80, 120), (60, 130, 100), (110, 130, 100))], [1, 2, 5])
        self.assertEqual(tr.stoessel_class(120, 80, 110), 4)

    def test_tmrad_definition_and_td24(self):
        args = (1800, 10, 423.15, 1e5)
        T = tr.td_hours_K(24, *args)
        self.assertAlmostEqual(tr.tmr_ad_s(T, *args) / 3600, 24, delta=1e-3)
        self.assertGreater(tr.td_hours_K(8, *args), T)

    def test_semenov_tangency(self):
        r = tr.semenov_critical_ambient_K(1000, 20, 10, 423.15, 1e5)
        T, Ta = r["T_no_return_K"], r["Ta_critical_K"]
        q = lambda t: 1000 * tr.q_W_kg(t, 10, 423.15, 1e5)
        self.assertAlmostEqual(q(T), 20 * (T - Ta), delta=1e-6 * q(T))                     # touching
        self.assertAlmostEqual((q(T + 1e-3) - q(T - 1e-3)) / 2e-3, 20, delta=0.01)           # tangent


class Atex(unittest.TestCase):
    def test_classes_and_zones(self):
        self.assertEqual([atex.kst_class(k) for k in (0, 150, 250, 400)], ["St0", "St1", "St2", "St3"])
        self.assertEqual(atex.zone("dust", "primary"), 21)
        self.assertEqual(atex.zone("gas", "secondary"), 2)
        self.assertEqual(atex.zone("gas", "primary", dilution="high"), "1 NE")
        self.assertIsNone(atex.zone("gas", "primary", dilution="low", availability="fair"))
        rows = atex.epd_register(load("atex")["areas"])
        self.assertEqual((rows[0]["zone"], rows[0]["EPL"], rows[0]["ATEX_category"]), (21, "Db", "2D"))
        self.assertTrue(rows[2]["zone"].startswith("ASSESS"))


class Ram(unittest.TestCase):
    SYS = {"stages": [{"name": "P", "n": 2, "k": 1, "mtbf_h": 2000, "mttr_h": 100}, {"name": "C", "n": 3, "k": 2, "mtbf_h": 1500, "mttr_h": 150}]}

    def test_analytic_formula(self):
        A1, A2 = 2000 / 2100, 1500 / 1650
        exp = (1 - (1 - A1) ** 2) * (A2 ** 3 + 3 * A2 ** 2 * (1 - A2))
        self.assertAlmostEqual(ram.analytic_full_capacity(self.SYS), exp)

    def test_monte_carlo_agrees_with_analytic_and_identity(self):
        r = ram.run(self.SYS, runs=300, mission_h=20000, progress=False)
        self.assertTrue(all(m.startswith("PASS") for m in ram.consistency(r)), ram.consistency(r))
        self.assertGreaterEqual(r["production_availability"], r["full_capacity_availability"] - 1e-12)

    def test_plan_runs(self):
        smp = ram.run(self.SYS, runs=30, progress=False)
        p = ram.plan_runs(smp, smp["production_ci95"] / 2)
        self.assertGreaterEqual(p["runs_needed"], 100)


class FG(unittest.TestCase):
    def test_coverage_simple_geometry(self):
        lay = {"zones": [{"name": "Z", "polygon": [[0, 0], [20, 0], [20, 20], [0, 20]], "voting": "1ooN", "target": 0.5}],
               "detectors": [{"kind": "point_gas", "x": 10, "y": 10, "radius_m": 5}]}
        z = fg_mapping.map_coverage(lay, cell=0.25)["zones"][0]
        self.assertAlmostEqual(z["coverage_1"], math.pi * 25 / 400, delta=0.01)
        self.assertEqual(z["coverage_2"], 0)

    def test_flame_shadow_and_fov(self):
        det = {"kind": "flame", "x": 0, "y": 0, "azimuth_deg": 90, "fov_deg": 90, "range_m": 30}
        obs = [[[9, -1], [11, -1], [11, 1], [9, 1]]]
        self.assertTrue(fg_mapping.sees(det, (5, 0), obs))
        self.assertFalse(fg_mapping.sees(det, (20, 0), obs))     # behind obstruction
        self.assertFalse(fg_mapping.sees(det, (0, 20), obs))     # outside the cone (north, detector faces east)

    def test_optimiser_improves(self):
        lay = {"zones": [{"name": "Z", "polygon": [[0, 0], [20, 0], [20, 10], [0, 10]], "voting": "1ooN", "target": 0.9}], "detectors": []}
        o = fg_mapping.optimise(lay, "Z", {"kind": "point_gas", "radius_m": 6}, [(x, y) for x in range(0, 21, 4) for y in range(0, 11, 4)],
                                max_add=6, cell=1.0, progress=False)
        self.assertTrue(o["met"])


class PHA(unittest.TestCase):
    def test_actions_and_revalidation(self):
        d = load("pha")
        a = pha.action_status(d["actions"], dt.date(2026, 11, 5))
        self.assertEqual(a["overdue"], 1)
        self.assertAlmostEqual(a["closure_pct"], 100 / 3)
        r = pha.revalidation("2021-11-20", 12, 1, today=dt.date(2026, 11, 5))
        self.assertEqual(r["due"], "2026-11-20")
        self.assertEqual(len(r["early_revalidation_triggers"]), 2)

    def test_carry_forward_and_simops(self):
        d = load("pha")
        cf = pha.carry_forward(d["previous_worksheet"], d["nodes"])
        self.assertEqual((cf["added"], cf["removed"], cf["intent_changed"]), (["Node 4 Vapour return"], ["Node 3 Old drain"], ["Node 2 Pump P-101"]))
        cl = pha.simops_clashes(d["simops"]["schedule"], d["simops"]["rules"])
        self.assertEqual([(c["activity_1"], c["activity_2"], c["level"]) for c in cl], [("Tanker loading", "Hot work", "prohibited")])
        m = pha.simops_matrix(["A", "B"], {"A|B": "X"})
        self.assertEqual(m[1][2], "X")
        self.assertEqual(m[2][1], "X")

    def test_worksheets(self):
        for k in ("chazop", "whatif", "swift", "pssr"):
            self.assertTrue(pha.worksheet(k, "N1"))


class BuildingsAndEmergency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s = study.load(QEX)
        s["grid"] = {"x_min": -400, "x_max": 400, "y_min": -400, "y_max": 400, "step": 40}
        s["conventions"]["sector_subdivisions"] = 4
        cls.s = s
        cls.out = study.run(s, progress=False, mitigate=False)

    def test_purple_book_vulnerability(self):
        pb = buildings.PURPLE_BOOK
        self.assertEqual(buildings.vulnerability({"overpressure_kpa": 35}, pb), 1.0)
        self.assertEqual(buildings.vulnerability({"overpressure_kpa": 15}, pb), 0.025)
        self.assertEqual(buildings.vulnerability({"overpressure_kpa": 5}, pb), 0.0)
        self.assertEqual(buildings.vulnerability({"flux_kW_m2": 40}, pb), 1.0)
        self.assertEqual(buildings.vulnerability({"in_cloud": True}, pb), 1.0)

    def test_building_identities(self):
        r = buildings.assess(self.out, self.s, progress=False)
        for b, spec in zip(r["buildings"], self.s["buildings"]):
            self.assertAlmostEqual(b["PLL_per_yr"], b["IR_occupant_per_yr"] * spec.get("occupancy", 1) * spec["occupants"])
            self.assertGreaterEqual(b["F(P>=3kPa)"], b["F(P>=10kPa)"])
            self.assertGreaterEqual(b["F(P>=10kPa)"], b["F(P>=30kPa)"])
            self.assertLessEqual(b["worst_overpressure_kpa"], 800.0 + 1e-9)

    def test_emergency_nesting_and_distance(self):
        e = emergency.assess(self.out, self.s)
        for d in e["rows"]:
            self.assertLessEqual(d["zone_A_m"], d["zone_B_m"])
            self.assertLessEqual(d["zone_B_m"], d["zone_C_m"])
            self.assertIn(d["emergency_level"], (1, 2, 3))
        # pool-fire distance to 4 kW/m2 must match a direct inverse-square solve of the same point source
        sc = next(x for x in self.out["scenarios"] if x["id"] == "S4-T-401-rupture")
        eff = self.out["results"]["effects"][(sc["id"], "pool_fire", None)]
        d = emergency.distance_to(eff, "flux_kW_m2", 4.0)
        self.assertAlmostEqual(eff.field(d, 0)["flux_kW_m2"], 4.0, delta=0.15)
        with tempfile.TemporaryDirectory() as td:
            files = emergency.write(e, self.s, os.path.join(td, "x"))
            self.assertTrue(all(os.path.getsize(f) > 100 for f in files))


class ToolsRunner(unittest.TestCase):
    def test_all_tools_run(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ("sif", "thermal", "atex", "pha", "ram"):
                data = load(name)
                if name == "ram":
                    data["sample_runs"], data["max_runs"] = 30, 200
                s = run_tool(name, data, d, progress=False)
                self.assertFalse(any(str(c).startswith("FAIL") for c in s["checks"]), (name, s["checks"]))


if __name__ == "__main__":
    unittest.main()
