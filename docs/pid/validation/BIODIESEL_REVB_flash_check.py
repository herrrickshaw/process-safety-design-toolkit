"""Rev B check: isothermal single-stage vacuum flash of the V-401 (ester) and V-402 (glycerol) phases at 80 C.
UNIFAC-Dortmund (thermo 0.6.1) activity coefficients, CoolProp 8.0 vapour pressures; glycerol, FAME/TG, soap, NaOH non-volatile.
Run:  /private/tmp/claude-501/venv_val/bin/python -I docs/pid/validation/BIODIESEL_REVB_flash_check.py
Reads the phase compositions (streams 11, 12) from scripts/gen_pid_biodiesel.py and prints the frozen constants FL and FLASH_TBL
to paste into it (iterate until FL is unchanged). Also asserts nothing: it is a check, not part of the toolkit."""
import sys, os, importlib.util
sys.dont_write_bytecode = True
from thermo import Chemical
from thermo.unifac import UNIFAC, DOUFSG, DOUFIP2006
import CoolProp.CoolProp as CP
from scipy.optimize import fsolve
K = 273.15
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "..", "..", "..", "scripts", "gen_pid_biodiesel.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
GR = {n: Chemical(n).UNIFAC_Dortmund_groups for n in ("methanol", "water", "methyl oleate")}
GR["glycerol"] = {2: 2, 3: 1, 14: 2, 81: 1}   # glycerol: 2 CH2, 1 CH, 2 primary OH, 1 secondary OH (Dortmund subgroup ids 2, 3, 14, 81); thermo has no assignment
MWc = {"methanol": 32.042, "water": 18.015, "glycerol": 92.094, "methyl oleate": 296.488}
ps = lambda f, T: CP.PropsSI("P", "T", T + K, "Q", 0, f) / 1e5


def flash(names, kg, vol, T, P):
    """kg: dict name -> kg of every component (non-volatile included); vol: volatile names. Returns vaporised fraction per volatile."""
    n0 = {k: v / MWc[k] for k, v in kg.items()}
    def resid(u):
        V, *nl = u
        nL = dict(n0)
        for k, x in zip(vol, nl): nL[k] = x
        tl = sum(nL.values()); xs = [nL[k] / tl for k in names]
        gam = UNIFAC.from_subgroups(T=T + K, xs=xs, chemgroups=[GR[k] for k in names], subgroups=DOUFSG, interaction_data=DOUFIP2006, version=1).gammas()
        gm = dict(zip(names, gam))
        y = {k: nL[k] / tl * gm[k] * ps({"methanol": "Methanol", "water": "Water"}[k], T) / P for k in vol}
        return [sum(y.values()) - 1] + [n0[k] - nL[k] - y[k] * V for k in vol]
    guess = [0.5 * sum(n0[k] for k in vol)] + [0.05 * n0[k] for k in vol]
    sol = fsolve(resid, guess, xtol=1e-12)
    return {k: 1 - sol[1 + i] / n0[k] for i, k in enumerate(vol)}


def run(P, T=80.0):
    e, gph = g.ST[11], g.ST[12]
    ek = {"methanol": e["MeOH"], "water": e["H2O"], "methyl oleate": e["FAME"] + e["TG"]}
    gk = {"methanol": gph["MeOH"], "water": gph["H2O"], "glycerol": gph["GLY"]}
    fe = flash(["methanol", "water", "methyl oleate"], ek, ["methanol", "water"], T, P)
    fg = flash(["methanol", "water", "glycerol"], gk, ["methanol", "water"], T, P)
    return fe["methanol"], fe["water"], fg["methanol"], fg["water"]


if __name__ == "__main__":
    rows = []
    for P in (1.0, 0.5, 0.2, 0.1, 0.05, 0.02):
        r = run(P); rows.append((P,) + tuple(round(100 * x, 1) for x in r))
        print(P, [round(100 * x, 1) for x in r])
    r = run(0.10)
    print("FL = dict(E_M=%.4f, E_W=%.4f, G_M=%.4f, G_W=%.4f)" % r)
    print("FLASH_TBL =", rows)
