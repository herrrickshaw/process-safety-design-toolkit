#!/usr/bin/env python3
"""Provenance for the frozen constants in scripts/gen_pid_urea.py (Rev B).  NOT part of the stdlib toolkit: needs CoolProp, thermo, numpy.

Run:  python3 tests/crosscheck/urea_revb_constants.py [cases.json]
(venv_val: CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2, numpy, scipy; run 11 Nov 2026.)

Part 1  water-gas-shift K(T): K = exp(-dG/RT) from thermo heats of formation, S0 and Cp integrals (same method as the validator,
        val_urea/src/recompute.py thermoK), then a 4-term fit  ln K = a + b/T + c ln T + d T  over 450-2000 K that the stdlib generator can evaluate.
Part 2  K-401 specific work (3:1 H2:N2, 313.15 K, 40 -> 200 bar, isentropic, 75 %) with CoolProp HEOS mixture; K-601 is NOT computed here
        (the generator uses the UBA 126 kWh/t CO2 figure).
Part 3  water Psat 313.15 K; NH3 saturation properties at 240.15 K and 313.15 K (for relief/fire notes).
Part 4  (optional cases.json {name: {species: mol/s, "T": K, "P": bar}}) gas M, ideal-gas k and PR-EOS Z for the relief screening cases."""
import json, sys, math
import numpy as np
from thermo import Chemical
import CoolProp.CoolProp as CP

R = 8.314462618

def chem(n): return Chemical(n)
CO, H2O, CO2, H2 = chem("CO"), chem("H2O"), chem("CO2"), chem("H2")

def H(c, T): return c.Hfgm + c.HeatCapacityGas.T_dependent_property_integral(298.15, T)
def S(c, T): return c.S0gm + c.HeatCapacityGas.T_dependent_property_integral_over_T(298.15, T)

def K_wgs(T):
    """CO + H2O -> CO2 + H2"""
    dH = H(CO2, T) + H(H2, T) - H(CO, T) - H(H2O, T)
    dS = S(CO2, T) + S(H2, T) - S(CO, T) - S(H2O, T)
    return math.exp(-(dH - T * dS) / (R * T)), dH

Ts = np.arange(450.0, 2001.0, 25.0)
lnK = np.array([math.log(K_wgs(T)[0]) for T in Ts])
A = np.column_stack([np.ones_like(Ts), 1.0 / Ts, np.log(Ts), Ts])
coef, *_ = np.linalg.lstsq(A, lnK, rcond=None)
fit = A @ coef
print("WGS fit  ln K = a + b/T + c ln T + d T")
print("  a, b, c, d =", ", ".join(f"{x:.10g}" for x in coef))
print(f"  max |dlnK| over 450-2000 K = {np.max(np.abs(fit - lnK)):.4f} ({(math.exp(np.max(np.abs(fit-lnK)))-1)*100:.2f} % in K)")
for T in (1673.15, 643.15, 503.15):
    k, dh = K_wgs(T); kf = math.exp(coef[0] + coef[1] / T + coef[2] * math.log(T) + coef[3] * T)
    moe = math.exp(4577.8 / T - 4.33)
    print(f"  T={T:7.2f} K: thermo K={k:.5f}  fit K={kf:.5f}  Moe K={moe:.5f}  Moe/thermo-1={(moe/k-1)*100:+.1f} %  dH={dh/1000:.2f} kJ/mol")
print(f"  dH_WGS at 570 K (shift mean) = {K_wgs(570.0)[1]/1000:.2f} kJ/mol; at 298.15 K = {K_wgs(298.15)[1]/1000:.2f}")

# Part 2: K-401 specific work
def comp_work_mix(T1, P1, P2, eta, z):
    names = "Hydrogen&Nitrogen"
    st = CP.AbstractState("HEOS", names); st.set_mole_fractions(z)
    st.update(CP.PT_INPUTS, P1, T1); h1, s1 = st.hmolar(), st.smolar()
    st.update(CP.PSmolar_INPUTS, P2, s1); h2s = st.hmolar()
    return (h2s - h1) / eta, h2s - h1   # J/mol actual, isentropic
w, ws = comp_work_mix(313.15, 40e5, 200e5, 0.75, [0.75, 0.25])
print(f"K-401 specific work 3:1 H2:N2, 40 -> 200 bar, 313.15 K inlet, eta 0.75: {w/1000:.4f} kJ/mol actual ({ws/1000:.4f} isentropic)")
# cross-check with mole-weighted pure components
def comp_work_pure(fl, T1, P1, P2, eta):
    s1 = CP.PropsSI("S", "T", T1, "P", P1, fl); h1 = CP.PropsSI("H", "T", T1, "P", P1, fl); h2 = CP.PropsSI("H", "P", P2, "S", s1, fl)
    return (h2 - h1) * CP.PropsSI("MOLARMASS", fl) / eta
wp = 0.75 * comp_work_pure("Hydrogen", 313.15, 40e5, 200e5, 0.75) + 0.25 * comp_work_pure("Nitrogen", 313.15, 40e5, 200e5, 0.75)
print(f"  cross-check, mole-weighted pure components: {wp/1000:.4f} kJ/mol  (mixture/pure-1 = {(w/wp-1)*100:+.2f} %)")

# Part 3
print(f"Psat water 313.15 K = {CP.PropsSI('P','T',313.15,'Q',0,'Water')/1000:.4f} kPa")
for T in (240.15, 313.15):
    pl = CP.PropsSI("P", "T", T, "Q", 0, "Ammonia") / 1e5
    hfg = (CP.PropsSI("H", "T", T, "Q", 1, "Ammonia") - CP.PropsSI("H", "T", T, "Q", 0, "Ammonia")) / 1000
    rho = CP.PropsSI("D", "T", T, "Q", 0, "Ammonia")
    print(f"NH3 at {T} K: Psat {pl:.4f} bar, hfg {hfg:.1f} kJ/kg, rho_liq {rho:.1f} kg/m3")

# Part 4
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    from thermo import PRMIX
    cases = json.load(open(sys.argv[1]))
    ids = {"H2": "hydrogen", "N2": "nitrogen", "CO": "carbon monoxide", "CO2": "carbon dioxide", "H2O": "water", "H2S": "hydrogen sulfide",
           "NH3": "ammonia", "O2": "oxygen", "CH4": "methane"}
    for name, c in cases.items():
        T, P = c["T"], c["P"] * 1e5
        sp = {k: v for k, v in c.items() if k in ids and v > 0}
        tot = sum(sp.values()); z = [sp[k] / tot for k in sp]
        chs = [Chemical(ids[k]) for k in sp]
        M = sum(zi * ch.MW for zi, ch in zip(z, chs))
        Cp = sum(zi * ch.HeatCapacityGas(T) for zi, ch in zip(z, chs))    # J/mol/K
        k = Cp / (Cp - R)
        eos = PRMIX(T=T, P=P, Tcs=[ch.Tc for ch in chs], Pcs=[ch.Pc for ch in chs], omegas=[ch.omega for ch in chs], zs=z)
        V = eos.V_g if getattr(eos, 'V_g', None) else eos.V_l; Zg = P * V / (R * T)
        print(f"RELIEF {name}: M={M:.3f} kg/kmol  k_ideal={k:.4f}  Z_PR={Zg:.4f}  (T={T} K, P={c['P']} bar)")

# Part 5: independent recomputation of the Rev B generator balance (python3 ... --check-json gen_dump.json)
if "--check-json" in sys.argv:
    d = json.load(open(sys.argv[sys.argv.index("--check-json") + 1]))
    coal = d["coal"]; c = dict(carbon=.42, hydrogen=.029, oxygen=.052, nitrogen=.008, sulfur=.013, ash=.35, moisture=.128)
    aw = dict(C=12.011, H=1.008, O=15.999, N=14.007, S=32.06)
    nC = coal*c["carbon"]*1000/aw["C"]*0.90
    nH2eq = (coal*c["hydrogen"]*1000/aw["H"] + 2*(coal*c["moisture"]*1000/18.015 + 0.10*coal*1000/18.015))/2
    nOt = coal*c["oxygen"]*1000/aw["O"] + (coal*c["moisture"]*1000/18.015 + 0.10*coal*1000/18.015) + 2*0.55*coal*1000/31.998
    from scipy.optimize import brentq
    A_ = 2*nC + nH2eq - nOt; K = K_wgs(1673.15)[0]
    f = lambda x: (nC - x)*(A_ - x) - K*x*(nH2eq - (A_ - x))
    nCO = brentq(f, max(1e-9, A_ - nH2eq), min(nC, A_) - 1e-9)
    s4 = d["streams"]["4"]
    print(f"CHECK gasifier (exact thermo K {K:.5f}): CO {nCO:.1f} vs generator {s4['CO']:.1f} ({(s4['CO']/nCO-1)*100:+.2f} %), H2 {A_-nCO:.1f} vs {s4['H2']:.1f} ({(s4['H2']/(A_-nCO)-1)*100:+.2f} %)")
    def shift(sp, fr, T, ap):
        tot = sum(sp.values()); st = fr*tot; Kk = K_wgs(T+ap)[0]
        nW = sp["H2O"]+st; g = lambda x: (sp["CO2"]+x)*(sp["H2"]+x) - Kk*(sp["CO"]-x)*(nW-x)
        x = brentq(g, 0, min(sp["CO"], nW)-1e-9); o = dict(sp); o["CO"] -= x; o["H2O"] = nW-x; o["CO2"] += x; o["H2"] += x
        return o, x/sp["CO"]
    g4 = {k: v for k, v in s4.items()}
    ht, cht = shift(g4, 0.30, 623.15, 20.0); lt, clt = shift(ht, 0.10, 493.15, 10.0)
    print(f"CHECK HT conversion {cht:.4f} vs {d['ht_conv']:.4f}; LT {clt:.4f} vs {d['lt_conv']:.4f}; H2 after LT {lt['H2']:.1f} vs {d['streams']['9']['H2']:.1f}")
    nh3 = d["nh3"]; urea = d["urea"]
    print(f"CHECK urea = NH3/2: {nh3/2:.3f} vs {urea:.3f}; t NH3/t urea {nh3*17.031/(urea*60.06):.4f}; t CO2/t urea {urea*44.01/(urea*60.06):.4f}")
    F, rec, purge = d["F"], d["rec"], d["purge"]; X, p = 0.19, 0.02
    inlet = F/(1-(1-p)*(1-X)); print(f"CHECK loop: NH3 = 0.5 X inlet {0.5*X*inlet:.3f} vs {nh3:.3f}; purge total {p*(1-X)*inlet:.3f} vs {purge+rec:.3f}")
    el = {"N": 0, "H": 0}
    print("CHECK N balance loop: 2*N2 in S15 =", 2*d["streams"]["15"]["N2"], " = NH3 + 2*(purge+rec)*0.25:", nh3 + 2*(purge+rec)*0.25)
