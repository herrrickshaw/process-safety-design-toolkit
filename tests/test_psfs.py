"""Tests for the PSFS linter (scripts/psfs_lint.py), the PSFS model and the template: the clean package must lint clean, and every rule must fire
on a seeded mistake and (for drawing-level rules) be corrected by the redraw fix."""
import os, sys, re, importlib, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import gen_pid_urea_package as G
import psfs_lint as L, psfs_model as M, urea_psfs as P, psfs_template as TPL
from pid_unit import T


def fresh():
    importlib.reload(P)          # defaults of the layout globals, independent of any variants run
    return G.build_package()[0]


def codes(F, sev="E"): return {f.code for f in F if f.sev == sev}


def psfs_sheet_with(pkg, tag):
    for s in pkg.sheets:
        if getattr(s, "psfs", False) and any(re.match(rf"{re.escape(tag)}\b", t[4]) for t in L._text_boxes(s)): return s
    raise AssertionError(tag)


def drop_text(sh, tag): sh.p[:] = [e for e in sh.p if not re.search(rf">{re.escape(tag)}\b", e)]


class PsfsLint(unittest.TestCase):
    def test_clean_package_has_no_errors(self):
        pkg = fresh()
        self.assertEqual(codes(L.lint(pkg)), set())


    def test_every_unit_sheet_has_a_box_and_all_safeguards(self):
        pkg = fresh()
        U = M.build(M.Regs.from_pkg(pkg)); boxes = {b["sheet"] for s in pkg.sheets if getattr(s, "psfs", False) for b in s.psfs_boxes}
        assert set(U) == boxes and len(U) >= 100
        assert sum(len(u.A_relief) for u in U.values()) == len(pkg.relief) and sum(len(u.C_esd) for u in U.values()) >= 140


    def test_P01_missing_relief_device_and_fix(self):
        pkg = fresh()
        r = next(x for x in pkg.relief if x[0].startswith("PSV")); sh = psfs_sheet_with(pkg, r[0]); drop_text(sh, r[0])
        self.assertIn("P01", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P02_missing_esd_valve_and_fix(self):
        pkg = fresh()
        v = next(x for x in pkg.valves if "ESD" in str(x[5])); sh = psfs_sheet_with(pkg, v[0]); drop_text(sh, v[0])
        self.assertIn("P02", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P03_missing_trip_and_fix(self):
        pkg = fresh()
        i = next(x for x in pkg.inst if x[3] == "LAHH"); sh = psfs_sheet_with(pkg, i[0]); drop_text(sh, i[0])
        self.assertIn("P03", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P04_blank_destination(self):
        pkg = fresh()
        pkg.relief[3][5] = ""; F = L.lint(pkg)
        self.assertIn("P04", codes(F)); self.assertTrue(any(f.fix.startswith("scripts/urea_area_") for f in F if f.code == "P04"))


    def test_P05_phantom_tag_and_fix(self):
        pkg = fresh()
        r = next(x for x in pkg.relief if x[0].startswith("PSV")); sh = psfs_sheet_with(pkg, r[0])
        sh.p[:] = [e.replace(f">{r[0]}", ">PSV-99999", 1) for e in sh.p]
        assert {"P05", "P01"} <= codes(L.lint(pkg)); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P06_duplicate_drawn_tag_and_fix(self):
        pkg = fresh()
        r = next(x for x in pkg.relief if x[0].startswith("PSV")); sh = psfs_sheet_with(pkg, r[0]); b = next(b for b in sh.psfs_boxes if b["sheet"] == int(r[7]))
        T(sh, b["x"] + 34, b["y"] + b["h"] - 14, f"{r[0]}  duplicate", 8.6)
        self.assertIn("P06", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P07_control_valve_without_fail_action(self):
        pkg = fresh()
        v = next(x for x in pkg.valves if x[1] == "control" and any(int(r[7]) == int(x[6]) for r in pkg.relief)); v[5] = "-"
        self.assertIn("P07", codes(L.lint(pkg)))


    def test_P08_truncation_text_and_fix(self):
        pkg = fresh()
        sh = next(s for s in pkg.sheets if getattr(s, "psfs", False)); b = sh.psfs_boxes[0]
        T(sh, b["x"] + 12, b["y"] + b["h"] - 6, "+ 3 more relief device(s)", 8.6)
        self.assertIn("P08", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P09_esd_valve_bad_fail_action(self):
        pkg = fresh()
        v = next(x for x in pkg.valves if "ESD" in str(x[5])); v[5] = "XX (ESD)"
        self.assertIn("P09", codes(L.lint(pkg)))


    def test_P10_relief_set_above_design(self):
        pkg = fresh()
        for x in pkg.relief:
            if x[3] != "per vendor": x[3] = "999"
        self.assertIn("P10", codes(L.lint(pkg)))


    def test_P11_unit_without_box(self):
        pkg = fresh()
        sh = next(s for s in pkg.sheets if getattr(s, "psfs", False))
        sh.psfs_boxes[:] = sh.psfs_boxes[1:]
        self.assertIn("P11", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P12_text_overflowing_box_and_fix(self):
        pkg = fresh()
        sh = next(s for s in pkg.sheets if getattr(s, "psfs", False)); b = sh.psfs_boxes[0]
        T(sh, b["x"] + 100, b["y"] + 60, "overflowing text that is far longer than the box and leaves it on the right " * 2, 8.6)
        self.assertIn("P12", codes(L.lint(pkg))); self.assertEqual(codes(L.fix(pkg)), set())


    def test_P13_title_and_legend(self):
        pkg = fresh()
        sh = next(s for s in pkg.sheets if getattr(s, "psfs", False)); sh.title = "Safeguarding sheet"
        self.assertIn("P13", codes(L.lint(pkg)))


    def test_P14_duplicate_relief_tag(self):
        pkg = fresh()
        pkg.relief.append(list(pkg.relief[0])); self.assertIn("P14", codes(L.lint(pkg)))


    def test_P30_trip_above_design(self):
        pkg = fresh()
        for i in pkg.inst:
            if i[3] == "PAHH": i[5] = "HH 9999 bar (A)"
        self.assertIn("P30", codes(L.lint(pkg)))


    def test_fix_is_idempotent_and_keeps_sheet_numbers(self):
        pkg = fresh()
        n0 = sorted(s.no for s in pkg.sheets); L.fix(pkg); L.fix(pkg)
        assert sorted(s.no for s in pkg.sheets) == n0 and codes(L.lint(pkg)) == set()


    def test_advisories_report_open_gaps(self):
        pkg = fresh()
        adv = codes(L.lint(pkg), "A"); assert {"P20", "P22"} <= adv


    def test_template_draws_and_has_four_sections(self):
        tmp_path = __import__('pathlib').Path(tempfile.mkdtemp())
        pkg2, sh = TPL.build(str(tmp_path / "t.html")); txt = " ".join(t[4] for t in L._text_boxes(sh))
        for k in ("A  Final safeguards", "B  Capacity-determining", "C  Mitigating systems", "D  Interfaces", "Review checklist", "Sign-off"): assert k in txt
        assert getattr(sh, "psfs_template", False) and len(sh.psfs_boxes) == 2
        ov, out = G.overlaps(sh); assert not ov and not out


    def test_model_dest_class_and_numbers(self):
        assert M.dest_class("flare header via KO-101") == "flare" and M.dest_class("") == "" and M.dest_class("steam vent (A)") == "vent"
        assert M.first_number("HH 47 bar") == 47.0 and M.design_bar_g(dict(design="27.5 bar g / 250 C (D)")) == 27.5


    def test_no_text_overlaps_or_frame_overruns(self):
        pkg = fresh(); bad = [(sh.no, G.overlaps(sh)) for sh in pkg.sheets if any(G.overlaps(sh))]
        self.assertEqual(bad, [])

    def test_title_block_rows_fit(self):
        pkg = fresh(); self.assertLessEqual(len(pkg.project), 58); self.assertLessEqual(len(pkg.basis), 58)
        self.assertTrue(all(len(s.sub) <= 58 for s in pkg.sheets), [s.sub for s in pkg.sheets if len(s.sub) > 58][:3])

    def test_esd_exemptions_have_reasons_and_real_sheets(self):
        pkg = fresh(); nos = {sh.no for sh in pkg.sheets}
        self.assertTrue(set(G.ESD_EXEMPT) <= nos and all(len(r) > 20 for r in G.ESD_EXEMPT.values()))

    def test_readme_numbers_match_the_build(self):
        pkg = fresh()
        with open(os.path.join(os.path.dirname(__file__), "..", "docs", "pid", "urea_detail", "PACKAGE_README.md")) as f: txt = f.read()
        m = re.search(r"Total (\d+) sheets .*?, (\d+) lines, (\d+) instruments, (\d+) equipment items, (\d+) relief devices, ([\d,]+) valves, (\d+) streams", txt)
        got = (len(pkg.sheets), len(pkg.lines), len(pkg.inst), len(pkg.equip), len(pkg.relief), len(pkg.valves), len(G.STREAMS))
        self.assertEqual(tuple(int(x.replace(",", "")) for x in m.groups()), got)
        n = re.search(r"Lint \((\d+) errors, (\d+) advisories\)", txt); pr, adv = G.lint(pkg)
        self.assertEqual((int(n.group(1)), int(n.group(2))), (len(pr), len(adv)))


if __name__ == "__main__":
    unittest.main()
