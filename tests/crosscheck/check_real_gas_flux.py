"""Real-gas isentropic nozzle flux (API 520-I Annex B direct integration) for saturated propane and n-butane at the relief workbook conditions, against the
ideal-gas critical-flow equation with Z = 1 and with the calculated saturated-vapour Z. Needs CoolProp (optional; skips when absent).
Run: PYTHONPATH=. python3 tests/crosscheck/check_real_gas_flux.py"""
try:
    from CoolProp.CoolProp import PropsSI as CP
except ImportError:
    print("CoolProp not installed: skipped")
    raise SystemExit(0)
import math

from process_safety import relief

CASES = (("Propane", 44.096, 1724.0, 1.115), ("n-Butane", 58.122, 690.0, 1.08))   # fluid, M, set kPag, ideal-gas k (workbook)


def real_flux(cn, P1_pa, Pb_pa=101325.0, n=600):
    h1, s1 = CP("Hmass", "P", P1_pa, "Q", 1, cn), CP("Smass", "P", P1_pa, "Q", 1, cn)
    best = 0.0
    for i in range(1, n):
        P = P1_pa - (P1_pa - Pb_pa) * i / n
        h, rho = CP("Hmass", "P", P, "S", s1, cn), CP("Dmass", "P", P, "S", s1, cn)
        best = max(best, math.sqrt(max(0.0, 2.0 * (h1 - h))) * rho)
    return best


for cn, M, pset, k in CASES:
    P1 = relief.relieving_pressure_kpa(pset, "fire")
    T, Zs = CP("T", "P", P1 * 1e3, "Q", 1, cn), CP("Z", "P", P1 * 1e3, "Q", 1, cn)
    G = real_flux(cn, P1 * 1e3)
    print("%s: P1 %.0f kPa, T %.1f K, Z calc %.3f, real-gas flux %.0f kg/m2/s" % (cn, P1, T, Zs, G))
    for Z, lab in ((1.0, "Z = 1"), (Zs, "Z calc")):
        Gi, _ = relief.gas_mass_flux(P1, 101.325, T, M, k, Z)
        print("   %-7s ideal-gas flux %.0f, area %+.1f %% against the real-gas area" % (lab, Gi, 100.0 * (G / Gi - 1.0)))
    print("   Z that reproduces the real-gas flux: %.3f" % relief.effective_Z(G, P1, T, M, k))
