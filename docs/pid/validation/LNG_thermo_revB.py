#!/usr/bin/env python3
"""LNG Rev B frozen thermodynamic data (CoolProp 8.0, HEOS). Run: /private/tmp/claude-501/venv_val/bin/python thermo_lng.py [search|final]
Basis 1 kg/s of NG to the cold train.  Outputs JSON to stdout (frozen into scripts/gen_pid_lng.py)."""
import sys, json, itertools
import numpy as np
import CoolProp.CoolProp as CP
PS = CP.PropsSI
NGZ = dict(Methane=0.85, Ethane=0.08, Propane=0.04, Nitrogen=0.03)
def fl(z): return "HEOS::" + "&".join(f"{k}[{v}]" for k, v in z.items() if v > 0)
NG = fl(NGZ)
ETA = 0.75
TC = 313.15
def hNG(T): return PS("H", "T", T, "P", 50e5, NG) / 1000.0

def mr_cycle(z, Pe, Pc, Tpre=233.15, Tw=230.15, Tce=113.15, eta=ETA, mNG=1.0, detail=False):
    f = fl(z)
    h = lambda T, P: PS("H", "T", T, "P", P, f) / 1000.0
    hh_in = h(Tpre, Pc); hh_ce = h(Tce, Pc)
    hc_w = h(Tw, Pe)
    QNG = mNG * (hNG(Tpre) - hNG(114.15))
    den = hc_w - hh_in
    if den <= 0: return None
    m = QNG / den
    # JT temperature
    try: TJT = PS("T", "P", Pe, "H", hh_ce * 1000, f)
    except Exception: return None
    # pinch
    Tg = np.arange(Tce, Tpre + 0.01, 6.0)
    Tcg = np.arange(TJT - 0.5, Tw + 0.01, 3.0)
    hc = np.array([h(T, Pe) for T in Tcg])
    if np.any(np.diff(hc) <= 0): return None
    dmin = 1e9
    for T in Tg:
        Qh = mNG * (hNG(Tpre) - hNG(max(T, 114.15))) + m * (hh_in - h(T, Pc)) if T >= 114.15 else None
        if Qh is None: Qh = QNG + m * (hh_in - h(T, Pc))
        target = hc_w - Qh / m
        if target < hc[0]: dmin = min(dmin, T - Tcg[0]); continue
        Tc = float(np.interp(target, hc, Tcg))
        dmin = min(dmin, T - Tc)
    # 3-stage compression, intercool to TC, eta
    PR = (Pc / Pe) ** (1 / 3); w = 0.0; P1 = Pe; T1 = Tw; stages = []
    for i in range(3):
        h1 = h(T1, P1); s1 = PS("S", "T", T1, "P", P1, f); P2 = P1 * PR
        h2s = PS("H", "P", P2, "S", s1, f) / 1000.0
        dh = (h2s - h1) / eta; w += dh
        rho = PS("D", "T", T1, "P", P1, f)
        stages.append(dict(P_in=P1, T_in=T1, w_kJ_kg=dh, vol_m3_per_kg=1 / rho))
        T1 = TC; P1 = P2
    return dict(m_per_mNG=m / mNG, w_kJ_kg=w, W_per_mNG=m * w / mNG, TJT=TJT, dTmin=dmin, QNG=QNG, stages=stages,
                hh_in=hh_in, hh_ce=hh_ce, hc_w=hc_w, z=z, Pe=Pe, Pc=Pc)

def search():
    best = []
    for n2, c3, c1 in itertools.product([0.04], [0.03, 0.08], [0.32, 0.42]):
        c2 = 1 - n2 - c3 - c1
        if c2 < 0.2: continue
        z = dict(Nitrogen=n2, Methane=c1, Ethane=c2, Propane=c3)
        for Pe, Pc in itertools.product([3e5, 5e5], [45e5]):
            try: r = mr_cycle(z, Pe, Pc)
            except Exception as e: r = None
            if r: print('CAND', round(r['dTmin'],2), round(r['W_per_mNG'],1), round(r['TJT'],1), z, Pe/1e5, Pc/1e5, round(r['m_per_mNG'],2), flush=True)
            if r: best.append((r["dTmin"], r["W_per_mNG"], r["TJT"], z, Pe / 1e5, Pc / 1e5, r["m_per_mNG"]))
    ok = [b for b in best if b[0] >= 2.0]
    ok.sort(key=lambda b: b[1])
    print("n feasible", len(best), "ok", len(ok))
    for b in ok[:12]: print([round(x, 3) if isinstance(x, float) else x for x in b[:3]], b[3], b[4], b[5], round(b[6], 2))
    print("--- best dTmin overall")
    best.sort(key=lambda b: -b[0])
    for b in best[:6]: print([round(x, 3) if isinstance(x, float) else x for x in b[:3]], b[3], b[4], b[5], round(b[6], 2))

if __name__ == "__main__" and sys.argv[1] == "search":
    search()

def propane_cascade(Q, ETAp=ETA):
    f = "Propane"
    Te = [285.15, 268.15, 250.15, 230.15]
    P = [PS("P", "T", T, "Q", 1, f) for T in Te]
    hv = [PS("H", "T", T, "Q", 1, f) / 1000 for T in Te]
    hl = [PS("H", "T", T, "Q", 0, f) / 1000 for T in Te]
    rv = [PS("D", "T", T, "Q", 1, f) for T in Te]
    Pc = PS("P", "T", TC, "Q", 0, f); hc = PS("H", "T", TC, "Q", 0, f) / 1000; rhoc = PS("D", "T", TC, "Q", 0, f)
    hin = [hc, hl[0], hl[1], hl[2]]
    x = [(hin[i] - hl[i]) / (hv[i] - hl[i]) for i in range(4)]
    mev = [Q[i] / (hv[i] - hl[i]) for i in range(4)]
    m = [0] * 4
    m[3] = mev[3] / (1 - x[3])
    for i in (2, 1, 0): m[i] = (mev[i] + m[i + 1]) / (1 - x[i])
    F = [m[i] * x[i] + mev[i] for i in range(4)]
    assert abs(sum(F) - m[0]) < 1e-9 * m[0]
    st = []; hcur = None; mcur = 0.0; W = 0.0
    for k in (3, 2, 1, 0):  # lowest level first
        Pin = P[k]
        if hcur is None: hmix, mmix = hv[k], F[k]
        else: hmix = (mcur * hcur + F[k] * hv[k]) / (mcur + F[k]); mmix = mcur + F[k]
        Pout = P[k - 1] if k > 0 else Pc
        s = PS("S", "P", Pin, "H", hmix * 1000, f)
        hs = PS("H", "P", Pout, "S", s, f) / 1000
        ho = hmix + (hs - hmix) / ETAp
        rho_in = PS("D", "P", Pin, "H", hmix * 1000, f)
        st.append(dict(level=k + 1, P_in=Pin / 1e5, P_out=Pout / 1e5, m=mmix, w=mmix * (ho - hmix), vol_m3_h=mmix / rho_in * 3600,
                       T_in=PS("T", "P", Pin, "H", hmix * 1000, f), T_out=PS("T", "P", Pout, "H", ho * 1000, f)))
        W += mmix * (ho - hmix); hcur, mcur = ho, mmix
    Qc = mcur * (hcur - hc)
    assert abs(sum(Q) + W - Qc) < 1e-6 * Qc, (sum(Q) + W, Qc)
    return dict(Te=Te, Pe=[p / 1e5 for p in P], Pc=Pc / 1e5, hv=hv, hl=hl, rho_v=rv, hc=hc, rho_c=rhoc, m_cond=m[0], mev=mev, x=x, stages=st, W=W, Qc=Qc, Q=Q)

def final(zjson, Pe, Pc):
    z = json.loads(zjson)
    r = mr_cycle(z, Pe, Pc)
    f = fl(z)
    cuts = [313.15, 288.15, 271.15, 253.15, 233.15]
    hNGc = {T: hNG(T) for T in cuts + [333.15, 173.15, 114.15]}
    hh = {T: PS("H", "T", T, "P", Pc, f) / 1000 for T in cuts}
    rr = r["m_per_mNG"]
    Q = [(hNGc[cuts[i]] - hNGc[cuts[i + 1]]) + rr * (hh[cuts[i]] - hh[cuts[i + 1]]) for i in range(4)]
    pc = propane_cascade(Q)
    # MR stage detail with m
    # NG gamma, Z at 50 bar 298 K ; propane at 14 bar sat vapour
    g_ng = PS("CPMASS", "T", 298.15, "P", 50e5, NG) / PS("CVMASS", "T", 298.15, "P", 50e5, NG)
    z_ng = PS("Z", "T", 298.15, "P", 50e5, NG)
    pr = dict(gamma=PS("CPMASS", "T", 313.15, "P", 13.69e5, "Propane") / PS("CVMASS", "T", 313.15, "P", 13.69e5, "Propane"))
    out = dict(NG_h=hNGc, mr=r, mr_hot_h=hh, Q_levels=Q, propane=pc, gamma_NG=g_ng, Z_NG=z_ng)
    # latent heat propane at 14.9 bar ~ relieving, BOG latent
    print(json.dumps(out, indent=1, default=float))

if __name__ == "__main__" and sys.argv[1] == "final":
    final(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))

def final2():
    cuts = [313.15, 288.15, 271.15, 253.15, 233.15]
    hN = {T: hNG(T) for T in cuts + [333.15, 173.15, 114.15, 298.15]}
    Q = [hN[cuts[i]] - hN[cuts[i + 1]] for i in range(4)]
    pc = propane_cascade(Q)
    # MR 3-stage compression, blend A, Pe 3.5 bar, Pc 45 bar, eta .75, intercool 313.15
    z = dict(Nitrogen=0.04, Methane=0.32, Ethane=0.61, Propane=0.03); f = fl(z); Pe, Pc = 3.5e5, 45e5
    PR = (Pc / Pe) ** (1 / 3); P1 = Pe; T1 = 230.15; st = []
    for i in range(3):
        h1 = PS("H", "T", T1, "P", P1, f) / 1000; s1 = PS("S", "T", T1, "P", P1, f); P2 = P1 * PR
        h2s = PS("H", "P", P2, "S", s1, f) / 1000; dh = (h2s - h1) / ETA; h2 = h1 + dh
        T2 = PS("T", "P", P2, "H", h2 * 1000, f); hc = PS("H", "T", min(T2, TC), "P", P2, f) / 1000
        st.append(dict(P_in=P1 / 1e5, T_in=T1, P_out=P2 / 1e5, T_out=T2, w=dh, q_cool=h2 - hc, v=1 / PS("D", "T", T1, "P", P1, f)))
        T1 = min(T2, TC); P1 = P2
    # exergy ideal work 298.15 K 50 bar gas -> sat liquid 1.1 bar, per kg
    T0 = 298.15; h0 = PS("H", "T", T0, "P", 50e5, NG) / 1000; s0 = PS("S", "T", T0, "P", 50e5, NG) / 1000
    P1b = 1.1e5; Tb = PS("T", "P", P1b, "Q", 0, NG); h1 = PS("H", "P", P1b, "Q", 0, NG) / 1000; s1 = PS("S", "P", P1b, "Q", 0, NG) / 1000
    wid = (h1 - h0) - T0 * (s1 - s0)
    # check: validator numbers at m 63.376
    out = dict(h_mr_hot_313=PS('H','T',TC,'P',Pc,f)/1000, h_mr_hot_233=PS('H','T',233.15,'P',Pc,f)/1000, h_mr_cold_230=PS('H','T',230.15,'P',Pe,f)/1000, NG_h=hN, Q_levels=Q, propane=pc, mr_blend=z, mr_Pe=Pe / 1e5, mr_Pc=Pc / 1e5, mr_stages=st, w_ideal_kJ_kg=-wid, w_ideal_kWh_t=-wid / 3.6,
               gamma_NG=PS("CPMASS", "T", 298.15, "P", 50e5, NG) / PS("CVMASS", "T", 298.15, "P", 50e5, NG), Z_NG=PS("Z", "T", 298.15, "P", 50e5, NG),
               gamma_C3=PS("CPMASS", "T", 313.15, "P", 13.69e5, "Propane") / PS("CVMASS", "T", 313.15, "P", 13.69e5, "Propane"),
               hfg_C3_14bar=(PS("H", "P", 15e5, "Q", 1, "Propane") - PS("H", "P", 15e5, "Q", 0, "Propane")) / 1000,
               T_C3_15bar=PS("T", "P", 15e5, "Q", 1, "Propane"), rho_C3_liq_40C=PS("D", "T", 313.15, "Q", 0, "Propane"),
               rho_vap_C3_15bar=PS("D", "P", 15e5, "Q", 1, "Propane"), MW_C3=PS("M", "Propane") * 1000)
    try:
        from chemicals.reaction import Hfg
        H = {k: Hfg(v) for k, v in dict(CH4="74-82-8", C2H6="74-84-0", C3H8="74-98-6", CO2="124-38-9", H2O="7732-18-5").items()}
        out["Hfg_J_mol"] = H
        hc = {"CH4": (1, 2), "C2H6": (2, 3), "C3H8": (3, 4)}
        mw = {"CH4": 16.043, "C2H6": 30.070, "C3H8": 44.097}
        out["LHV_MJ_kg"] = {k: -(H[k] - n * H["CO2"] - m * H["H2O"]) / mw[k] / 1000 for k, (n, m) in hc.items()}
    except Exception as e: out["LHV_err"] = repr(e)
    print(json.dumps(out, indent=1, default=float))

if __name__ == "__main__" and sys.argv[1] == "final2": final2()
