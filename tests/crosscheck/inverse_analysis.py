"""Inverse (parameter-identification) analysis of the comparisons that deviate from the reference by more than 10 %.

For each large deviation it solves for the value of one uncertain parameter that would close the gap, with every other input at its baseline, and states whether that value
is inside a physically or documentarily plausible range. The solved values are FIT VALUES: they show what would have to be true, they are not validation and they are not
adopted as defaults. Standard library plus the toolkit only.
Run: PYTHONPATH=. python3 tests/crosscheck/inverse_analysis.py"""
import math

from process_safety import jet_flame as jf
from process_safety import line_flow as lf

R = 8.314462618
HC = {"propane": 46.013e6, "n-butane": 45.86e6}
MW = {"propane": 44.096, "n-butane": 58.1}


def bisect(f, lo, hi, n=80):
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if (f(mid) > 0) == (flo > 0):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- jet fire (DNV post-expansion inputs, JFSH-Cook set)
TESTS = [  # name, fuel, m, v, r, wind, angle, Ta, Tsat(1 atm) used by DNV, measured length, measured mean SEP, DNV Phast length, DNV Phast SEP
    ("AA 3026", "propane", 16.1, 152.74, 0.059, 3.7, 16.0, 286.85, 230.51, 31.1, 331.0, 38.9, 245.9),
    ("AA 3029", "propane", 18.0, 146.47, 0.062, 2.0, 9.0, 281.15, 230.51, 30.7, 294.0, 50.0, 192.5),
    ("JIVE 8051", "n-butane", 6.86, 46.22, 0.040, 0.5, 73.0, 281.85, 272.14, 18.3, None, 33.2, 234.9)]


def flame(t, m=None, v=None, ang=None, wind=None):
    nm, fl, m0, v0, r0, w0, a0, Ta, Tsat, *_ = t
    m = m0 if m is None else m
    v = v0 if v is None else v
    rho_j = m0 / (math.pi * r0 * r0 * v0)          # DNV jet density stays fixed; radius follows from continuity
    rho_a = 1.0e5 * 0.02896 / (R * Ta)
    rho_vap = 1.0e5 * MW[fl] / 1000.0 / (R * Tsat)
    return jf.chamberlain(m, rho_j, rho_a, MW[fl], HC[fl], w0 if wind is None else wind, a0 if ang is None else ang, v_j_m_s=v, fs_model="cook", rho_vap_kg_m3=rho_vap, w1_model="cook")


def jet_rows():
    out = []
    for t in TESTS:
        nm, fl, m0, v0, r0, w0, a0, Ta, Tsat, Lmeas, SEPmeas, Ldnv, SEPdnv = t
        base = flame(t)
        L0 = base["L_B_m"]
        for target, lab in ((Lmeas, "measured visible length"), (Ldnv, "DNV Phast length")):
            if abs(L0 / target - 1) < 0.10:
                continue
            # (a) flammable mass multiplier (rain-out equivalent: 3 (1 - eta) m_d = f m_d, eta = 1 - f / 3 when f < 3 ... here f applies to the flow itself)
            fm = bisect(lambda f: flame(t, m=m0 * f)["L_B_m"] - target, 0.02, 1.0)
            eta = 1.0 - fm / 3.0
            # (b) velocity (mass flow fixed, radius from continuity)
            fv = bisect(lambda f: flame(t, v=v0 * f)["L_B_m"] - target, 0.2, 3.0)
            # (c) release-to-wind angle
            try:
                ang = bisect(lambda a: flame(t, ang=a)["L_B_m"] - target, 0.0, 180.0)
            except Exception:
                ang = float("nan")
            # (d) wind speed
            try:
                wind = bisect(lambda w: flame(t, wind=w)["L_B_m"] - target, 0.0, 30.0)
            except Exception:
                wind = float("nan")
            out.append((nm, lab, L0, target, fm, eta, fv * v0, ang, a0, wind, w0))
    return out


def sep_rows():
    out = []
    for t in TESTS:
        nm, fl, m0, v0, r0, w0, a0, Ta, Tsat, Lmeas, SEPmeas, Ldnv, SEPdnv = t
        b = flame(t)
        P = b["radiated_power_kW"]
        for target, lab in ((SEPmeas, "measured mean SEP"), (SEPdnv, "DNV Phast SEP")):
            if target is None or abs(b["SEP_kW_m2"] / target - 1) < 0.10:
                continue
            out.append((nm, lab, b["SEP_kW_m2"], target, b["F_s"], b["F_s"] * target / b["SEP_kW_m2"], b["area_m2"], P / target))
    return out


# ---------------------------------------------------------------- line-fed release rates
def line_rows():
    cases = [("AA 3026", "propane", 278.65, 7.53e5, [(67.0, 0.152), (13.0, 0.052)], 16.1),
             ("AA 3029", "propane", 276.35, 7.34e5, [(67.0, 0.152), (13.0, 0.052)], 18.0),
             ("JIVE 8051", "n-butane", 275.05, 19.85e5, [(79.0, 0.152), (1.85, 0.040)], 6.86)]
    out = []
    for nm, fl, T0, P0, seg, meas in cases:
        W0 = lf.line_discharge(fl, T0, P0, 101300.0, seg)["W_kg_s"]
        if abs(W0 / meas - 1) < 0.10:
            continue
        # driving pressure that gives the measured rate
        hi = 40e5 if W0 < meas else P0
        lo = P0 if W0 < meas else 1.6e5
        P_need = bisect(lambda P: lf.line_discharge(fl, T0, P, 101300.0, seg)["W_kg_s"] - meas, lo, hi, 40)
        K = None
        if W0 > meas:   # fittings loss that gives the measured rate
            K = bisect(lambda k: lf.line_discharge(fl, T0, P0, 101300.0, seg, k_fittings=k)["W_kg_s"] - meas, 0.0, 400.0, 40)
        out.append((nm, W0, meas, P0 / 1e5, P_need / 1e5, K))
    return out


# ---------------------------------------------------------------- droplets (Weber branch: d = C_ds sigma / (u_f^2 rho_a))
def droplet_rows():
    # toolkit values at STEP conditions (liquid-orifice state, lgrelease example, 5 mm hole): d at C_ds = 15 and measured SMD
    pts = [("STEP 5 bar", 56.0, 44.0), ("STEP 11 bar", 20.0, 30.5)]
    return [(nm, d15, meas, 15.0 * meas / d15) for nm, d15, meas in pts]


# ---------------------------------------------------------------- DNV post-expansion state: pre-expansion pressure implied by DNV's velocity (ATEX momentum balance)
def dnv_state_rows():
    import math
    from process_safety import props_ref as P
    cases = [("AA 3026", "propane", 278.65, 16.1, 0.052, 152.74), ("AA 3029", "propane", 276.35, 18.0, 0.052, 146.47), ("JIVE 8051", "n-butane", 275.05, 6.86, 0.040, 46.22)]
    out = []
    for nm, fl, T0, m, D, uf in cases:
        A = math.pi / 4 * D * D
        rho = P.liquid_density_kg_m3(fl, T0)
        uo = m / (rho * A)
        Pe = 101300.0 + (uf - uo) * m / A      # u_f = u_o + (P_e - P_a) A / m  (momentum balance from a liquid exit state)
        out.append((nm, uo, uf, Pe / 1e5))
    return out


def main():
    print("1. Jet-fire flame length: parameter that would close the gap (others at baseline)")
    print("   %-10s %-24s %6s %7s | %9s %8s | %9s | %7s (base %5.1f) | %6s (base)" % ("test", "target", "L base", "L tgt", "mass x", "rain-out", "v needed", "angle", 0, "wind"))
    for nm, lab, L0, tg, fm, eta, vn, ang, a0, wind, w0 in jet_rows():
        print("   %-10s %-24s %6.1f %7.1f | %9.3f %8.2f | %9.1f | %7.1f (base %5.1f) | %6.1f (%.1f)" % (nm, lab, L0, tg, fm, eta, vn, ang, a0, wind, w0))
    print("2. Surface emissive power: radiant fraction or flame area that would close the gap")
    for nm, lab, S0, tg, Fs, Fs_need, A0, A_need in sep_rows():
        print("   %-10s %-20s SEP %5.0f -> %5.0f | Fs %.3f -> %.3f | area %6.0f -> %6.0f m2" % (nm, lab, S0, tg, Fs, Fs_need, A0, A_need))
    print("3. Line-fed release rate: driving pressure or fittings loss that would close the gap")
    for nm, W0, meas, P0, Pn, K in line_rows():
        print("   %-10s model %5.2f measured %5.2f kg/s | P0 %.2f -> %.2f bar abs%s" % (nm, W0, meas, P0, Pn, "" if K is None else " | or fittings K = %.0f" % K))
    print("4. Droplet SMD (Weber branch): C_ds that would close the gap")
    for nm, d15, meas, c in droplet_rows():
        print("   %-12s d(C_ds 15) %4.0f micron, measured %4.1f -> C_ds %.1f (literature 10 to 20)" % (nm, d15, meas, c))
    print("5. DNV post-expansion velocity: exit pressure that its momentum balance implies (liquid exit state)")
    for nm, uo, uf, Pe in dnv_state_rows():
        print("   %-10s liquid exit velocity %5.1f m/s, DNV final velocity %6.2f m/s -> exit pressure %.1f bar abs" % (nm, uo, uf, Pe))


if __name__ == "__main__":
    main()
