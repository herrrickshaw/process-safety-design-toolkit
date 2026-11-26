"""CBG Rev B: real-gas constants frozen into scripts/gen_pid_cbg.py. Run: python3 cbg_realgas.py"""
import CoolProp, math
from CoolProp.CoolProp import PropsSI, AbstractState
print("CoolProp", CoolProp.__version__)
def AS(x_ch4):
    a = AbstractState("HEOS", "Methane&CO2"); a.set_mass_fractions if False else None
    a.set_mole_fractions([x_ch4, 1 - x_ch4]); return a
def hs(a, T, P):
    a.update(CoolProp.PT_INPUTS, P, T); return a.hmass(), a.smass(), a.rhomass()
# K-202: 3 stages 16.01325 -> 251.01325 bara, inlet 40 C every stage, eta_s 0.75, 96/4 mol CH4/CO2
def chain(x, p1, p2, n, T1, Tcool, eta=0.75):
    a = AS(x); rs = (p2 / p1) ** (1 / n); sh = co = 0.0; Tin = T1
    for i in range(n):
        P1, P2 = p1 * rs ** i * 1e5, p1 * rs ** (i + 1) * 1e5
        h1, s1, _ = hs(a, Tin, P1)
        a.update(CoolProp.PSmass_INPUTS, P2, s1); h2s = a.hmass()
        h2 = h1 + (h2s - h1) / eta; a.update(CoolProp.HmassP_INPUTS, h2, P2); T2 = a.T()
        h3, _, _ = hs(a, Tcool, P2); sh += h2 - h1; co += h2 - h3; Tin = Tcool
    return sh, co, T2   # J/kg
x = 0.96 / (0.96 + 0.04)   # mole fractions as given
sh, co, T2 = chain(0.96, 16.01325, 251.01325, 3, 313.15, 313.15)
# ideal-gas formula of the generator for the same duty (k 1.30)
Mm = 0.96 * 16.043 + 0.04 * 44.0095; Rg = 8.314462618; k = 1.30
cp = k / (k - 1) * Rg / (Mm / 1000); rs = (251.01325 / 16.01325) ** (1 / 3)
dT = 313.15 * (rs ** ((k - 1) / k) - 1) / 0.75
id_sh = 3 * cp * dT; id_co = 3 * cp * (313.15 + dT - 313.15)
print(f"K202 real shaft {sh/1000:.1f} kJ/kg cooling {co/1000:.1f} kJ/kg T2 {T2-273.15:.1f} C | ideal shaft {id_sh/1000:.1f} cooling {id_co/1000:.1f}")
print(f"RATIO shaft real/ideal {sh/id_sh:.4f}  cooling real/ideal {co/id_co:.4f}")
# Z at 251.01325 bara, 40 C, 96/4
a = AS(0.96); a.update(CoolProp.PT_INPUTS, 251.01325e5, 313.15)
Z = a.p() / (a.rhomolar() * Rg * a.T()); print("Z 251 bara 40 C", round(Z, 4), "rho", round(a.rhomass(), 1))
# isentropic choked mass flux, real gas, from 251.01325 bara 313.15 K
h0, s0, r0 = hs(a, 313.15, 251.01325e5); best = 0
P = 251.01325e5
def flux(p):
    a.update(CoolProp.PSmass_INPUTS, p, s0); dh = h0 - a.hmass()
    return a.rhomass() * math.sqrt(2 * dh) if dh > 0 else 0.0
lo, hi = 0.40 * P, 0.99 * P      # critical pressure ratio near 0.54 for CH4; golden-section on the mass flux
g = (math.sqrt(5) - 1) / 2; c = hi - g * (hi - lo); d = lo + g * (hi - lo)
for _ in range(30):
    if flux(c) > flux(d): hi = d
    else: lo = c
    c = hi - g * (hi - lo); d = lo + g * (hi - lo)
best = flux((lo + hi) / 2); print("critical p ratio", round((lo + hi) / 2 / P, 3))
# ideal (toolkit gas_mass_flux, k 1.30, Z=1) for the same state
M = Mm / 1000; Gi = P * math.sqrt(k * M / (Rg * 313.15)) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
print(f"G real {best:.0f} kg/m2/s ideal(k1.30,Z1) {Gi:.0f}  RATIO {best/Gi:.4f}")
# Z of biogas at K-201 discharge 17.01325 bara 40 C for several CH4 fractions (dry CH4/CO2 binary)
for y in (0.50, 0.55, 0.583, 0.60, 0.641):
    a = AS(y); a.update(CoolProp.PT_INPUTS, 17.01325e5, 313.15); print("Z biogas 17 bara 40C y", y, round(a.p() / (a.rhomolar() * Rg * a.T()), 4))
# K-201 real-gas check for the new mixture (y=0.583) 2 stages 1.06325 -> 17.01325, inlet 5 C then 40 C
sh2, co2, T22 = chain(0.583, 1.06325, 17.01325, 2, 278.15, 313.15)
print(f"K201 real (y 0.583) shaft {sh2/1000:.1f} kJ/kg cooling {co2/1000:.1f} kJ/kg T2 {T22-273.15:.1f}")
# Z at the relieving conditions used for PSV sizing (PSV-501: set 275 barg x 1.10 + 1.013 = about 303.8 bara; PSV-401: 17.6 barg x 1.10 + 1.013 = about 20.4 bara)
a = AS(0.96); a.update(CoolProp.PT_INPUTS, 303.8e5, 313.15); print("Z 303.8 bara 96/4", round(a.p() / (a.rhomolar() * Rg * a.T()), 4))
a = AS(0.583); a.update(CoolProp.PT_INPUTS, 20.4e5, 313.15); print("Z 20.4 bara y0.583", round(a.p() / (a.rhomolar() * Rg * a.T()), 4))
