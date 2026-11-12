#!/usr/bin/env python3
"""Coal-to-urea, unit-by-unit P&ID package (pilot). Talcher-class basis: 3,850 t/d urea, 2,200 t/d NH3 (1.27 Mt/yr at 330 d).

Usage: python3 scripts/gen_pid_urea_detail.py <out.html> [--previews] [--registers <dir>]

Balance: the Rev B balance in gen_pid_urea.py is linear in coal feed, so every stream is scaled by K = 3850 / Rev B urea t/d (D).
Capacity basis: Talcher Fertilizers 3,850 t/d urea / 2,200 t/d NH3 (ICRA, Feb 2025, quoted in coal-to-urea-design-opensource docs/VALIDATION.md;
12.7 LMTPA urea in PIB releases of 13 Mar 2026 and 24 Jul 2026). See docs/pid/analogues/ for the verification grade.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *


def build():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID",
              "Rev B balance scaled K=%.4f; capacity per ICRA/PIB (see docs/pid/analogues)" % K)
    A = "A"
    # ---- V-203 shift condensate knock-out drum (area 400)
    wat = g.M[28] * 3.6 * K
    gas_in = stream(9, "shift gas, cooled", "twophase", T=40.0, P=45.0, drop_water=True, flow=g.M[9] * 3.6 * K)
    gas_in.rho_in = None
    v_gas = St("9V", "shift gas to AGR", "gas", g.M[9] * 3.6 * K - wat, 40.0, 44.0, mw=gas_in.mw)
    gas_in.mw = v_gas.mw; gas_in.rho_in = v_gas.rho * 1.0   # D: two-phase line at the gas density of the vapour (screening)
    cond = St(28, "process condensate", "liq", wat, 40.0, 45.0, rho=992.0)   # A: water at 40 C
    sheet_vessel(pkg, "40", 401, "Area 400  Shift and gas cooling  -  V-203 condensate knock-out drum",
                 dict(tag="V-203", name="Shift condensate KO drum", inlet=gas_in, gas=v_gas, liq=cond, res_min=5.0, pumps="P-203",
                      pump_dp_bar=8.0, spec="A1", internals="demister", svc_in="SG", svc_gas="SG", svc_liq="PC",
                      mat="A: CS, sour service (NACE type), to be set by licensor", hazard="sour syngas (H2, CO, H2S) at 45 bar",
                      notes=["Stream 9V is a Rev C split of stream 9 into vapour (to C-301) and condensate (stream 28).",
                             "Condensate goes to the sour-water stripper (area 300); H2S dissolved in it is not quantified (needs solubility data)."]))
    # ---- V-302 methanator effluent KO drum (area 30 reused as 40 for pilot)
    return pkg


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "urea_detail.html"
    pkg = build(); pkg.total = len(pkg.sheets)
    for sh in pkg.sheets: pass
    write_html(pkg.sheets, out, "Coal-to-urea unit P&IDs (pilot)", previews="--previews" in sys.argv)
    if "--registers" in sys.argv: pkg.write_registers(sys.argv[sys.argv.index("--registers") + 1])
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices")


if __name__ == "__main__":
    main()
