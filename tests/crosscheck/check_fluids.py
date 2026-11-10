"""Cross-check toolkit formulae against CalebBell/fluids (MIT; optional, not a toolkit dependency): API 520 vapour relief area, Colebrook friction,
contraction and entrance loss coefficients, and typical valve K values for the JIVE implied loss.
Run: PYTHONPATH=. python3 tests/crosscheck/check_fluids.py   (skips cleanly when fluids is not installed)"""
try:
    import fluids
except ImportError:
    print("fluids not installed: skipped")
    raise SystemExit(0)

from process_safety import line_flow as lf

# 1. API 520 critical-flow vapour area: workbook Propane_Vessel_Relief_Sizing.xlsx inputs (relieving 2187.365 kPa(a), T 334.75 K, Z 0.673, k 1.115)
WORKBOOK = (("V1", 5731.32, 243.64), ("V2", 14578.65, 619.74), ("V3", 28863.47, 1226.99), ("V4", 48922.88, 2079.72), ("V5", 7359.14, 312.84))
print("API 520 vapour area, toolkit workbook against fluids.API520_A_g")
for nm, kg_h, mm2 in WORKBOOK:
    A = fluids.API520_A_g(kg_h / 3600.0, 334.75, 0.673, 44.096, 1.115, 2187365.0, 101325.0, 0.975, 1.0, 1.0) * 1e6
    print("  %s workbook %8.1f mm2  fluids %8.1f mm2  %+.2f %%" % (nm, mm2, A, 100 * (mm2 / A - 1)))

# 2. friction factor
print("Colebrook, toolkit against fluids.friction_factor (smooth and eD 1e-4)")
for Re in (5e3, 1e5, 1e6, 1e7):
    for eD in (0.0, 1e-4):
        a, b = lf.colebrook_f(Re, eD), fluids.friction_factor(Re=Re, eD=eD)
        print("  Re %.0e eD %.0e  toolkit %.5f  fluids %.5f  %+.2f %%" % (Re, eD, a, b, 100 * (a / b - 1)))

# 3. loss coefficients
print("Loss coefficients: toolkit contraction 0.5 (1 - beta^2) against fluids.contraction_sharp; entrance 0.5 against sharp-edged")
for D1, D2 in ((0.152, 0.052), (0.152, 0.040)):
    beta = D2 / D1
    print("  %.3f to %.3f m: toolkit %.3f  fluids contraction_sharp %.3f" % (D1, D2, 0.5 * (1 - beta ** 2), fluids.contraction_sharp(D1, D2)))
print("  entrance: toolkit 0.5, fluids entrance_sharp %.3f" % fluids.entrance_sharp())

# 4. valve K values for the JIVE implied loss (about 73, from the HEM line model)
print("Typical fully open valve K (Crane method) for a 6 inch line, fT from fluids.ft_Crane")
D = 0.1541
ft = fluids.ft_Crane(D)
print("  Crane fT %.4f" % ft)
for nm, fn in (("gate valve", lambda: fluids.K_gate_valve_Crane(D, D, 0.0, fd=ft)), ("globe valve", lambda: fluids.K_globe_valve_Crane(D, D, fd=ft)),
               ("ball valve", lambda: fluids.K_ball_valve_Crane(D, D, 0.0, fd=ft)), ("swing check", lambda: fluids.K_swing_check_valve_Crane(fd=ft))):
    try:
        print("  %s K %.2f" % (nm, fn()))
    except Exception as e:  # signature differences between versions
        print("  %s: %s" % (nm, str(e)[:70]))
