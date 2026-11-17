#!/usr/bin/env python3
"""Rev B thermo CHECK for scripts/gen_pid_saf.py (optional libraries: thermo 0.6.1, chemicals 1.5.2, CoolProp 8.0; NOT part of the stdlib toolkit).
Run:  /private/tmp/claude-501/venv_val/bin/python tests/crosscheck/saf_revb_thermo.py
It imports the generator's balance (stdlib part), runs Peng-Robinson (kij = 0, screening) flashes, and prints the frozen constants to paste into FROZEN in the generator,
plus independent re-computations of duties for the Rev B results file. Water/H2 solubility in PR with kij = 0 is unreliable (screening only)."""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, ROOT)
src = open(os.path.join(ROOT, "scripts", "gen_pid_saf.py")).read().split("# 2. DRAWING")[0]
g = {"__file__": os.path.join(ROOT, "scripts", "gen_pid_saf.py"), "__name__": "head"}
exec(compile(src, "gen_head", "exec"), g)
from thermo import ChemicalConstantsPackage, FlashVL, CEOSGas, CEOSLiquid, PRMIX
import CoolProp.CoolProp as CP
CAS = dict(H2="1333-74-0", H2O="7732-18-5", CO="630-08-0", CO2="124-38-9", C3="74-98-6", C17="629-78-7", C2="74-84-0", C4="106-97-8", C7="142-82-5", C11="1120-21-4", C16="544-76-3")
def mk(names):
    cons, cors = ChemicalConstantsPackage.from_IDs([CAS[n] for n in names])
    eos = dict(Tcs=cons.Tcs, Pcs=cons.Pcs, omegas=cons.omegas)
    gas = CEOSGas(PRMIX, eos_kwargs=eos, HeatCapacityGases=cors.HeatCapacityGases); liq = CEOSLiquid(PRMIX, eos_kwargs=eos, HeatCapacityGases=cors.HeatCapacityGases)
    return FlashVL(cons, cors, liquid=liq, gas=gas), cons
def kmol(kg, name): return kg / g["MW_" + name] if False else kg / MWS[name]
MWS = {"H2": 2.016, "H2O": 18.015, "CO": 28.010, "CO2": 44.009, "C3": 44.096, "C17": 240.468, "C2": 30.069, "C4": 58.122, "C7": 100.202, "C11": 156.308, "C16": 226.441}
ST, B = g["ST"], g["B"]; out = {}
# ---- 1. V-201: stream 9 at 340 C, 49.5 bar ----
nm = ["H2", "H2O", "CO", "CO2", "C3", "C17"]; s9 = ST[9]
kg = dict(H2=s9["H2"], H2O=s9["H2O"], CO=s9["CO"], CO2=s9["CO2"], C3=s9["Propane"], C17=s9["HT paraffin"])
n = [kg[x] / MWS[x] for x in nm]; z = [v / sum(n) for v in n]
fl, cons = mk(nm); r = fl.flash(T=340 + 273.15, P=49.5e5, zs=z)
print("V-201 flash phases", r.phase_count, "VF", r.VF)
yv = r.gas.zs; Vmol = r.VF * sum(n)
par_vap_kg = yv[5] * Vmol * MWS["C17"]; phi = par_vap_kg / kg["C17"]
print("paraffin to vapour kg/h", par_vap_kg, "fraction of stream-9 paraffin", phi, " y_par", yv[5], " water in vapour fraction", yv[1] * Vmol * MWS["H2O"] / kg["H2O"])
out["PHI"] = round(phi, 4); out["fp_par9"] = round(kg["C17"], 1)
# H_COND: carried paraffin vapour (partial pressure y_par * 47 bar, 340 C) -> liquid 50 C 47 bar, kJ/kg (pure C17, PR enthalpy)
f1, _ = mk(["C17", "H2"]); p_par = yv[5] * 47e5
Hv = f1.flash(T=340 + 273.15, P=p_par, zs=[1 - 1e-7, 1e-7]); Hl = f1.flash(T=50 + 273.15, P=47e5, zs=[1 - 1e-7, 1e-7])
print("pure C17 at 340 C, p_par %.2f bar: phase %s" % (p_par / 1e5, Hv.phase_count), "liquid 50 C phase", Hl.phase_count)
out["H_COND"] = round((Hv.H() - Hl.H()) / MWS["C17"], 1)
# ---- 2. fractionator feed (stream 20): 45 C liquid at 47 bar -> 250 C at 1.5 bar ----
nm2 = ["C2", "C4", "C7", "C11", "C16"]; s20 = ST[20]
kg2 = dict(C2=s20["Fuel gas"], C4=s20["Crack LPG"], C7=s20["Naphtha cut"], C11=s20["SAF cut"], C16=s20["RD cut"])
n2 = [kg2[x] / MWS[x] for x in nm2]; z2 = [v / sum(n2) for v in n2]; N2 = sum(n2) * 1000   # mol/h
f2, c2 = mk(nm2)
A = f2.flash(T=45 + 273.15, P=47e5, zs=z2); TF = g["TC"]["feed_c"]; Bf = f2.flash(T=TF + 273.15, P=1.5e5, zs=z2)
print("feed 45 C/47 bar phases", A.phase_count, "VF", A.VF, "| feed 250 C/1.5 bar VF", Bf.VF)
E403 = N2 * (Bf.H() - A.H()) / 3600 / 1000
vf_mass = (Bf.VF * sum(Bf.gas.zs[i] * MWS[nm2[i]] for i in range(5))) / sum(z2[i] * MWS[nm2[i]] for i in range(5)) if Bf.VF > 0 else 0
print("E-403 kW", E403, "vapour mass fraction", vf_mass)
for T in (200, 225, 250, 275, 300):
    q = f2.flash(T=T + 273.15, P=1.5e5, zs=z2); print("  feed T", T, "VF mole", round(q.VF if q.VF is not None else 0, 3))
out["E403_KW"] = round(E403, 1); out["VF_FEED"] = round(Bf.VF, 3)
# ---- 3. column balance: Qreb = Qcond + sum H(products) - H(feed at 250 C) ----
def H_at(nm_, kgs, T, P):
    nm_ = list(nm_) + (["H2"] if len(nm_) == 1 else []); nn = [kgs.get(x, 0) / MWS[x] for x in nm_]; nn = [v if v > 0 else 1e-7 * sum(nn) for v in nn]; zz = [v / sum(nn) for v in nn]; ff, _ = mk(nm_)
    rr = ff.flash(T=T + 273.15, P=P, zs=zz); return sum(nn) * 1000 * rr.H() / 3600 / 1000, rr
ts = g["TC"]
H_nap, _ = H_at(["C7"], {"C7": kg2["C7"]}, 40, 1.3e5)
H_saf, rs = H_at(["C11"], {"C11": kg2["C11"]}, ts["saf"], 1.5e5)
H_rd, rr_ = H_at(["C16"], {"C16": kg2["C16"]}, ts["rd"], 1.5e5)
H_lt, rl = H_at(["C2", "C4"], {"C2": kg2["C2"], "C4": kg2["C4"]}, 40, 1.3e5)
Hfeed = N2 * Bf.H() / 3600 / 1000
# condenser: overhead vapour (naphtha x (1+RR) + light ends) at top T -> liquid naphtha + light-end vapour at 40 C
RRv = g["RR"]; 
Ho_top, ro = H_at(["C7"], {"C7": kg2["C7"] * (1 + RRv)}, ts["top"] + 1.0, 1.5e5)
Ho_out, _ = H_at(["C7"], {"C7": kg2["C7"] * (1 + RRv)}, 40, 1.3e5)
Hl_top, _ = H_at(["C2", "C4"], {"C2": kg2["C2"], "C4": kg2["C4"]}, ts["top"] + 1.0, 1.5e5)
Qcond = (Ho_top - Ho_out) + (Hl_top - H_lt)
print("phases: C11 at 212 C", rs.phase_count, "C16 at 303 C", rr_.phase_count, "overhead C7 at top T", ro.phase_count, "VF", ro.VF)
Qreb = Qcond + H_nap * 0 + (Ho_out - kg2["C7"] * (1 + RRv) * 0) * 0
Qreb = Qcond + (H_nap + H_saf + H_rd + H_lt) - Hfeed
for Tf in (170, 185, 200, 210, 225, 250):
    bq = f2.flash(T=Tf + 273.15, P=1.5e5, zs=z2); hq = N2 * bq.H() / 3600 / 1000
    print("  feed T", Tf, "VF mole %.3f" % bq.VF, "E-403 kW %.1f" % (N2 * (bq.H() - A.H()) / 3600 / 1000), "Qreb kW %.1f" % (Qcond + (H_nap + H_saf + H_rd + H_lt) - hq))
print("Qcond", Qcond, "Qreb", Qreb, "(components kW) naphtha", H_nap, "saf", H_saf, "rd", H_rd, "lights", H_lt, "feed", Hfeed)
out["E402_KW"] = round(Qreb, 1); out["E401_KW"] = round(Qcond, 1)
# ---- 4. bubble / dew checks ----
for nme, kind in (("C11", 0), ("C16", 0), ("C7", 1)):
    ff, _ = mk([nme, "H2"]); T = 150
    fn = lambda t: (ff.flash(P=1.5e5, VF=kind, zs=[1.0]).T - 273.15) if False else 0
    rb = ff.flash(P=1.5e5, VF=float(kind), zs=[1 - 1e-7, 1e-7]); print("sat T at 1.5 bar", nme, "VF", kind, rb.T - 273.15)
# ---- 5. independent recomputations ----
sw = g["DUTY"]
qE202 = None
nm3 = ["H2", "H2O", "CO", "CO2", "C3", "C17"]; s12 = ST[12]
k12 = dict(H2=s12["H2"], H2O=s12["H2O"], CO=s12["CO"], CO2=s12["CO2"], C3=s12["Propane"], C17=s12["HT paraffin"])
nn = [k12[x] / MWS[x] for x in nm3]; zz = [v / sum(nn) for v in nn]; f3, _ = mk(nm3)
a = f3.flash(T=340 + 273.15, P=47e5, zs=zz); b = f3.flash(T=50 + 273.15, P=47e5, zs=zz)
print("E-202 PR check kW", sum(nn) * 1000 * (a.H() - b.H()) / 3600 / 1000, " generator", sw["E-202"], " phases cold", b.phase_count)
Tk = 50 + 273.15; h1 = CP.PropsSI("H", "T", Tk, "P", 47e5, "Hydrogen"); s1 = CP.PropsSI("S", "T", Tk, "P", 47e5, "Hydrogen"); h2 = CP.PropsSI("H", "P", 53e5, "S", s1, "Hydrogen")
mdot = (g["EXCESS"] * g["S1"] + g["G2"]) / 3600
wk = mdot * (h2 - h1) / g["ETA"] / 1000
print("K-201 CoolProp real-gas H2 shaft kW", wk, " generator", sw["K-201 shaft"])
print("CoolProp cp (kJ/kg/K) hot", g["CP_L"], "recomputed:", end=" ")
import numpy as np
Ts = np.linspace(250, 340, 25) + 273.15; hh = [CP.PropsSI("H", "T", t, "P", 50e5, "n-Dodecane") for t in Ts]; print((hh[-1] - hh[0]) / (Ts[-1] - Ts[0]) / 1000)
print("Q1 (kJ/kg) routes", g["Q1_ROUTES"], "mean", g["Q1"], "kW", g["Q1_KW"])
print("FROZEN =", json.dumps(out))
