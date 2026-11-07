"""MATLAB/Octave tools in matlab/: run their own identity tests and compare them with the Python models. Skipped without octave-cli
(or matlab): brew install octave / apt install octave."""
import math
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
EXE = shutil.which("octave-cli") or shutil.which("octave")


def run_octave(code: str) -> str:
    r = subprocess.run([EXE, "--no-gui", "--quiet", "--eval", f"addpath('{os.path.join(ROOT, 'matlab')}'); {code}"], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-1500:] + r.stderr[-1500:])
    return r.stdout


def numbers(out: str) -> list[float]:
    return [float(x) for x in out.split()]


@unittest.skipUnless(EXE, "needs GNU Octave: brew install octave")
class Matlab(unittest.TestCase):
    def test_own_identity_tests_pass(self):
        out = run_octave("ps_run_tests")
        self.assertIn("ALL PASSED", out, out[-1500:])

    def test_units_match_python(self):
        from process_safety import units
        cases = [(150, "psig", "kPag"), (212, "degF", "degC"), (1, "gal", "m3"), (100, "lb/h", "kg/s"), (7, "hp", "kW"), (10, "dF", "dK"), (3, "ft2", "m2")]
        code = "".join(f"printf('%.15g\\n', ps_units({v}, '{a}', '{b}'));" for v, a, b in cases)
        got = numbers(run_octave(code))
        for (v, a, b), g in zip(cases, got):
            self.assertTrue(math.isclose(g, units.convert(v, a, b), rel_tol=1e-12), (v, a, b, g))

    def test_relief_gas_matches_python(self):
        from process_safety import relief
        got = numbers(run_octave("r = ps_relief_gas(12000, 400, 1500*1.21+101.325, 101.325, 44, 1.13, 0.9); printf('%.15g\\n', r.area_mm2);"
                                 "r = ps_relief_gas(5000, 350, 600, 450, 30, 1.2, 1.0); printf('%.15g\\n', r.area_mm2);"))
        a = relief.gas_area(12000, 400, 1500 * 1.21 + 101.325, 101.325, 44, 1.13, 0.9).required_area_mm2
        b = relief.gas_area(5000, 350, 600, 450, 30, 1.2, 1.0).required_area_mm2
        self.assertTrue(math.isclose(got[0], a, rel_tol=1e-12), (got[0], a))
        self.assertTrue(math.isclose(got[1], b, rel_tol=1e-12), (got[1], b))

    def test_omega_flux_matches_python(self):
        from process_safety import twophase
        got = numbers(run_octave("r = ps_omega_flux(1500, 500, 5); printf('%.12g\\n%.12g\\n', r.G_kg_m2_s, r.eta_critical);"
                                 "r = ps_omega_flux(1500, 500, 5, 900); printf('%.12g\\n', r.G_kg_m2_s);"))
        a = twophase.mass_flux(1500, 500, 5)
        b = twophase.mass_flux(1500, 500, 5, P_back_kPa=900)
        self.assertTrue(math.isclose(got[0], a["G_kg_m2_s"], rel_tol=1e-8))
        self.assertTrue(math.isclose(got[1], a["eta_critical"], rel_tol=1e-6))
        self.assertTrue(math.isclose(got[2], b["G_kg_m2_s"], rel_tol=1e-10))

    def test_view_factor_matches_python(self):
        from process_safety import viewfactor
        face = viewfactor.vertical_flame_face(20, 31, 15)
        py = viewfactor.view_factor((-15, 0, 0), (1, 0, 0), face, n=200)
        c, u, v = face.corner, face.edge_u, face.edge_v
        got = numbers(run_octave(f"printf('%.12g\\n', ps_view_factor([-15 0 0], [1 0 0], {list(c)}, {list(u)}, {list(v)}, 200));"))
        self.assertTrue(math.isclose(got[0], py, rel_tol=1e-9), (got[0], py))

    def test_depressure_matches_python(self):
        from process_safety import depressuring
        got = numbers(run_octave("r = ps_depressure(30, 5000, 1000, 300, 20, 1.3, 800, 0.85, 'isothermal'); printf('%.12g\\n', r.t_s);"
                                 "r = ps_depressure(30, 5000, 1000, 300, 20, 1.3, 800, 0.85, 'adiabatic'); printf('%.15g\\n%.15g\\n', r.t_s, r.Tmin_K);"))
        iso = depressuring.depressuring_time_s(30, 5000, 1000, 300, 20, 1.3, 800, mode="isothermal", dt=0.01)
        adi = depressuring.depressuring_time_s(30, 5000, 1000, 300, 20, 1.3, 800, mode="adiabatic", dt=0.01)
        self.assertTrue(math.isclose(got[0], iso, rel_tol=2e-3), (got[0], iso))
        self.assertTrue(math.isclose(got[1], adi, rel_tol=2e-3), (got[1], adi))
        self.assertTrue(math.isclose(got[2], depressuring.min_gas_temperature_K(300, 5000, 1000, 1.3), rel_tol=1e-12))

    def test_egress_and_illumination_match_cli(self):
        import json
        cli = lambda *a: json.loads(subprocess.run([sys.executable, "-m", "process_safety", *a], capture_output=True, text=True, cwd=ROOT).stdout)  # noqa: E731
        e = cli("egress", "--distance", "60", "--speed", "1.2", "--people", "200", "--width", "2", "--specific-flow", "1.3", "--detect-s", "30", "--premove-s", "60", "--aset-s", "300")
        i = cli("illumination", "--area", "100", "--flux", "3000", "--uf", "0.6", "--mf", "0.8", "--target", "300")
        got = numbers(run_octave("r = ps_egress(60, 1.2, 200, 2, 1.3, 30, 60, 300); printf('%.15g\\n%.15g\\n', r.rset_s, r.margin_s);"
                                 "r = ps_illumination(100, 3000, 0.6, 0.8, 300); printf('%.15g\\n%d\\n', r.achieved_lux, r.n_luminaires);"))
        self.assertTrue(math.isclose(got[0], e["rset_s"], rel_tol=1e-12))
        self.assertTrue(math.isclose(got[1], e["margin_s"], rel_tol=1e-12))
        self.assertTrue(math.isclose(got[2], i["achieved_lux"], rel_tol=1e-12))
        self.assertEqual(int(got[3]), i["n_luminaires"])

    def test_pool_fire_matches_python(self):
        from process_safety import pool_fire
        pf = pool_fire.pool_fire(314, 44000, 350, 2.2, 400)
        got = numbers(run_octave("r = ps_pool_fire(314, 44000, 350, 2.2, 400, [], [], [], [30 60], 6.3);"
                                 "printf('%.15g\\n', r.diameter_m, r.burning_rate_kg_m2_s, r.flame_height_m, r.Q_kW, r.sep_mudan_croce_kW_m2, r.flux_kW_m2, r.distance_to_target_m);"))
        want = [pf["diameter_m"], pf["burning_rate_kg_m2_s"], pf["flame_height_m"], pf["Q_kW"], pf["sep_mudan_croce_kW_m2"],
                pool_fire.incident_kW_m2(pf, 30), pool_fire.incident_kW_m2(pf, 60), pool_fire.distance_to_flux_m(pf, 6.3)]
        for g, w in zip(got, want):
            self.assertTrue(math.isclose(g, w, rel_tol=1e-9), (g, w))

    def test_fireball_matches_python(self):
        from process_safety import fireball
        fb = fireball.fireball(10000, 46, 0.3)
        got = numbers(run_octave("r = ps_fireball(10000, 46, 0.3, 1, [100 200], 12.5);"
                                 "printf('%.15g\\n', r.diameter_m, r.duration_s, r.surface_emissive_power_kW_m2, r.flux_kW_m2, r.dose, r.distance_to_target_m);"))
        want = [fb["diameter_m"], fb["duration_s"], fb["surface_emissive_power_kW_m2"], fireball.incident_kW_m2(fb, 100), fireball.incident_kW_m2(fb, 200),
                fireball.thermal_dose(fireball.incident_kW_m2(fb, 100), fb["duration_s"]), fireball.thermal_dose(fireball.incident_kW_m2(fb, 200), fb["duration_s"]),
                fireball.distance_to_flux_m(fb, 12.5)]
        for g, w in zip(got, want):
            self.assertTrue(math.isclose(g, w, rel_tol=1e-9), (g, w))

    def test_jet_fire_matches_python(self):
        from process_safety import flare
        Q = 20 * 46 * 1e6
        F = flare.radiant_fraction(20)
        got = numbers(run_octave("r = ps_jet_fire(20, 46, 20, [], 1, [200 400], [4.73 9.46]);"
                                 "printf('%.15g\\n', r.Q_MW, r.flame_length_m, r.radiant_fraction, r.flux_kW_m2, r.safe_distance_m);"))
        want = [Q / 1e6, 0.00326 * Q ** 0.478, F, flare.radiation_kW_m2(Q, 200, F), flare.radiation_kW_m2(Q, 400, F),
                flare.safe_distance_m(Q, 4.73, F), flare.safe_distance_m(Q, 9.46, F)]
        for g, w in zip(got, want):
            self.assertTrue(math.isclose(g, w, rel_tol=1e-12), (g, w))

    def test_blast_and_bleve_match_python(self):
        from process_safety import explosion
        E = explosion.brode_burst_energy_J(2000, 101.325, 5, 1.4)
        W = explosion.burst_tnt_equivalent_kg(E)
        got = numbers(run_octave("b = ps_bleve(10000, 46, 5, 2000, 1.4, 0.3, 1, [100 200]);"
                                 "printf('%.15g\\n', b.blast.brode_energy_J, b.blast.tnt_equivalent_kg, b.blast.overpressure_kpa);"
                                 "printf('%.15g\\n', ps_blast('distance_m', 1000, 7), ps_blast('tnt_equivalent', 10000, 46, 0.05));"))
        want = [E, W, explosion.kinney_graham_kpa(W, 100), explosion.kinney_graham_kpa(W, 200),
                explosion.distance_for_overpressure_m(1000, 7), explosion.tnt_equivalent_kg(10000, 46)]
        for g, w in zip(got, want):
            self.assertTrue(math.isclose(g, w, rel_tol=1e-9), (g, w))


if __name__ == "__main__":
    unittest.main()
