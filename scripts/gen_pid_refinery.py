#!/usr/bin/env python3
"""Generate the REFINERY conceptual P&ID set, Rev B (8 sheets): P&ID; heat and material balance (two sheets); scenario overlays (two
sheets); safety design basis (three sheets: relief schedule; ESD cause-and-effect and SIF list; detection, mitigation, hazard
identification, inherently safer design, gaps).

Process basis: the open-source design code in the repo clone refinery-design-opensource (refinery_design package,
commit 1ad5918): 15 Mt/yr crude unit (benchmarks.CDU_MTPA), CDU/VDU (distillation.distill), hydrotreating (hydrotreater.hydrotreat),
FCC (reference case from docs/VALIDATION.md section 2, NOT run on this VGO). The delayed-coker correlation of the repo (coker.py, 1.6 x CCR)
is kept only to compute the Rev A column of the change table.

Rev B changes from Rev A (sources: docs/pid/validation/GAP_CLOSURE_THERMO.md, REFINERY_VALIDATION.md):
  1. Crude slate refit. Rev A: 57 vol% Upper Zakum + 43 vol% Cold Lake Blend (2.90 wt% S). Rev B: three crudes from the repo's assays.json
     (Cold Lake Blend, Upper Zakum, Dalia) whose two free fractions are fitted to TWO targets: slate sulphur 2.264 wt% (IOCL Paradip EC
     compliance report 2020, Annexure-4, mean Dec19-Apr20; range 2.10-2.39) and vacuum-residue yield 27.33 wt% of crude (repo coker/CDU
     ratio 4.1/15). It is a fit, not Paradip's purchase list.
  2. Coker yields. Coke = 30 wt% of vacuum residue (Honeywell UOP Apr 2021: a delayed coker typically converts about 30 wt% of VR to coke;
     Tulsa JIP DOE/BC/15182-2 Table 41 pilot cokes 29.6-38.8 wt%; range 27-35) replaces 1.6 x CCR. Gas and naphtha: slopes of PTQ Q1 2020
     "Estimating delayed coker yields" Tables 1-2 at the slate CCR; gas oil by difference.
  3. Range and check tables: hydrotreater H2, naphtha end point, crude-heater duty (Peng-Robinson flash), FCC repo run.

Frozen repo runs below came from this runner (python with numpy, scipy, CoolProp: python3):

    sys.path.insert(0, REPO)
    cl, uz, da = (load_crude(k) for k in ("cold_lake_blend", "upper_zakum", "dalia"))
    mk  = lambda p: Slate([(cl, p[0]), (uz, p[1]), (da, 1 - p[0] - p[1])])
    p   = fsolve(lambda p: [mk(p).sulfur_wt - 2.264, mk(p).cut(550, INF).wt_frac - COKER_TO_CDU], [0.3, 0.35])   # 0.345 / 0.364 / 0.291 vol
    bpd = CDU_MTPA * 1e9 / 8760 / slate.density_kg_m3 / 0.158987294928 * 24
    d   = distill(slate, bpd)            # cuts, S, MCR, furnace duty, vaporised fraction
    for svc, ppm in (("naphtha", .5), ("kerosene", 10), ("diesel", 10), ("vgo", 1000)):
        hydrotreat(d.streams[svc].mass_kg_h, d.streams[svc].density_kg_m3, d.streams[svc].cut.sulfur_wt, ppm, service=svc)
    refine(slate, bpd, RefineryConfig(fcc=True, coker=True, vgo_hydrotreat=True)).fcc    # information only (FCC_REPO)
    # Rev A basket: x = brentq(VR yield == COKER_TO_CDU) = 0.4327 of Cold Lake; the same runner reproduces Rev A to 1e-9.

DUTY_CHECK (crude heater) came from thermo 0.6.1 Peng-Robinson FlashVL, n-alkane surrogates for the six cuts, 250 -> 360 C, coil outlet
2 and 3 bar abs (A), mol/s from the cut masses: command in the sheet 3 note. Anything not in the repo or a cited document is 'A'.
Screening aid, not certified design. No OISD, API, IEC or NFPA text was read: those items are recorded as gaps.

Usage (standard library only):
    python3 scripts/gen_pid_refinery.py docs/pid/REFINERY_PID_Set_RevB.html [--previews]
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pidlib import *

# ======================================================================== frozen repo outputs, Rev B basket (S)
REF = json.loads(r'''{
 "bpd": 286426.84793842066,
 "feed_kg_h": 1712328.7671232878,
 "furnace_MW": 210.558264741515,
 "vap": 0.4518368400577568,
 "slate": {
  "api": 25.138919014256402,
  "S": 2.2639999999999993,
  "rho": 902.4481328751658,
  "name": "CL/UZ/Dalia refit",
  "tan": 0.871048675697602
 },
 "vol_frac": {
  "cold_lake_blend": 0.34496480535098883,
  "upper_zakum": 0.3637166068026636,
  "dalia": 0.29131858784634757
 },
 "vr_wt": 0.2733333333333333,
 "vgo_wt": 0.30482982660890984,
 "streams": {
  "lpg": {
   "kg_h": 43771.43474371442,
   "S": null,
   "mcr": null,
   "bpd": 11110.783684246026
  },
  "naphtha": {
   "kg_h": 145758.43349546008,
   "S": 0.03571341338332326,
   "mcr": null,
   "bpd": 30537.296784735274
  },
  "kerosene": {
   "kg_h": 192105.28778789847,
   "S": 0.22478749452953,
   "mcr": null,
   "bpd": 35654.65026443672
  },
  "diesel": {
   "kg_h": 340688.2002362093,
   "S": 1.1174726191746749,
   "mcr": null,
   "bpd": 58312.12922409189
  },
  "vgo": {
   "kg_h": 521968.8811796402,
   "S": 2.269503559210046,
   "mcr": 1.1505527363033088,
   "bpd": 83279.06004919688
  },
  "vacuum_residue": {
   "kg_h": 468036.5296803654,
   "S": 4.834026055610192,
   "mcr": 24.930055206052067,
   "bpd": 67532.92793171387
  }
 },
 "ht": {
  "naphtha": {
   "feed_kg_h": 145758.43349546008,
   "s_in_ppm": 357.1341338332326,
   "s_out_ppm": 0.5,
   "lhsv_1_h": 5.256036690845192,
   "reactor_volume_m3": 38.48782596554599,
   "catalyst_t": 26.941478175882192,
   "sulfur_removed_kg_h": 51.982432678542246,
   "h2s_kg_h": 55.257682647683076,
   "h2_chemical_kg_h": 9.806292976912772,
   "h2_makeup_kg_h": 13.075057302550363,
   "recycle_gas_Nm3_h": 20229.342542577397
  },
  "kerosene": {
   "feed_kg_h": 192105.28778789847,
   "s_in_ppm": 2247.8749452953,
   "s_out_ppm": 10.0,
   "lhsv_1_h": 2.9636938577627228,
   "reactor_volume_m3": 79.69554027849105,
   "catalyst_t": 55.78687819494374,
   "sulfur_removed_kg_h": 429.90761039928117,
   "h2s_kg_h": 456.9947399378509,
   "h2_chemical_kg_h": 81.10047497488623,
   "h2_makeup_kg_h": 108.13396663318163,
   "recycle_gas_Nm3_h": 47238.63664288912
  },
  "diesel": {
   "feed_kg_h": 340688.2002362093,
   "s_in_ppm": 11174.72619174675,
   "s_out_ppm": 10.0,
   "lhsv_1_h": 1.497358547392046,
   "reactor_volume_m3": 257.9789507490118,
   "catalyst_t": 180.58526552430826,
   "sulfur_removed_kg_h": 3803.690472396267,
   "h2s_kg_h": 4043.3490735890446,
   "h2_chemical_kg_h": 717.5520891158023,
   "h2_makeup_kg_h": 956.7361188210698,
   "recycle_gas_Nm3_h": 115886.09608537935
  },
  "vgo": {
   "feed_kg_h": 521968.8811796402,
   "s_in_ppm": 22695.03559210046,
   "s_out_ppm": 1000.0,
   "lhsv_1_h": 0.9826651203004195,
   "reactor_volume_m3": 561.4116908464399,
   "catalyst_t": 392.98818359250794,
   "sulfur_removed_kg_h": 11324.13345516115,
   "h2s_kg_h": 12037.63157055184,
   "h2_chemical_kg_h": 2136.2557435063827,
   "h2_makeup_kg_h": 2848.3409913418436,
   "recycle_gas_Nm3_h": 275839.8433618394
  }
 },
 "naph_end_sens": {
  "150": 1.2768438774202304,
  "180": 1.7257166221908646,
  "200": 2.0500019371367966
 },
 "nci_unamb": 7.54831893,
 "nci_amb": 10.5053897,
 "fuel_loss_pct": 10.0,
 "fcc_repo": {
  "yields": {
   "dry_gas": 2.621427588377488,
   "lpg": 12.798734696195968,
   "gasoline": 48.48190701767344,
   "lco": 21.085244139743846,
   "slurry": 9.036533202747366,
   "coke": 5.97615335526198,
   "total": 100.0000000000001
  },
  "regen_T_C": 756.7796219956376
 }
}''')

# Rev A frozen outputs (57/43 Upper Zakum / Cold Lake basket): used only to compute the Rev A column of the change table
REF_A = json.loads(r'''{
 "bpd": 289820.195,
 "feed_kg_h": 1712328.77,
 "furnace_MW": 216.589244,
 "vap": 0.475824796,
 "slate": {
  "api": 26.9946464,
  "S": 2.90364309,
  "tan": 0.548693806,
  "rho": 891.88186,
  "name": "57% Upper Zakum + 43% Cold Lake Blend"
 },
 "heavy_vol": 0.432740253,
 "vr_wt": 0.273333333,
 "vgo_wt": 0.280841871,
 "streams": {
  "lpg": {
   "kg_h": 59905.8958,
   "S": null,
   "mcr": null,
   "bpd": 15226.8663
  },
  "naphtha": {
   "kg_h": 183870.045,
   "S": 0.0380950416,
   "mcr": null,
   "bpd": 38901.12
  },
  "kerosene": {
   "kg_h": 203595.388,
   "S": 0.274133306,
   "mcr": null,
   "bpd": 38226.645
  },
  "diesel": {
   "kg_h": 316027.295,
   "S": 1.53572547,
   "mcr": null,
   "bpd": 54356.8972
  },
  "vgo": {
   "kg_h": 480893.614,
   "S": 3.13141567,
   "mcr": 1.22748791,
   "bpd": 76397.2516
  },
  "vacuum_residue": {
   "kg_h": 468036.53,
   "S": 6.23304855,
   "mcr": 27.2521331,
   "bpd": 66711.4144
  }
 },
 "coker": {
  "feed": 468036.53,
  "ccr": 27.2521331,
  "coke": 204079.901,
  "gas": 54874.0404,
  "naph": 45998.1695,
  "go": 163084.419,
  "drum_m3": 6122.39702
 },
 "ht": {
  "naphtha": {
   "feed_kg_h": 183870.045,
   "s_in_ppm": 380.950416,
   "s_out_ppm": 0.5,
   "lhsv_1_h": 5.20490235,
   "reactor_volume_m3": 49.510886,
   "catalyst_t": 34.6576202,
   "sulfur_removed_kg_h": 69.9534351,
   "h2s_kg_h": 74.3609816,
   "h2_chemical_kg_h": 13.1964559,
   "h2_makeup_kg_h": 17.5952745,
   "recycle_gas_Nm3_h": 25769.9327
  },
  "kerosene": {
   "feed_kg_h": 203595.388,
   "s_in_ppm": 2741.33306,
   "s_out_ppm": 10.0,
   "lhsv_1_h": 2.90581257,
   "reactor_volume_m3": 87.1464627,
   "catalyst_t": 61.0025239,
   "sulfur_removed_kg_h": 556.086812,
   "h2s_kg_h": 591.124098,
   "h2_chemical_kg_h": 104.903713,
   "h2_makeup_kg_h": 139.871617,
   "recycle_gas_Nm3_h": 50646.2574
  },
  "diesel": {
   "feed_kg_h": 316027.295,
   "s_in_ppm": 15357.2547,
   "s_out_ppm": 10.0,
   "lhsv_1_h": 1.49060274,
   "reactor_volume_m3": 241.570514,
   "catalyst_t": 169.09936,
   "sulfur_removed_kg_h": 4850.15139,
   "h2s_kg_h": 5155.74421,
   "h2_chemical_kg_h": 914.963056,
   "h2_makeup_kg_h": 1219.95074,
   "recycle_gas_Nm3_h": 108025.701
  },
  "vgo": {
   "feed_kg_h": 480893.614,
   "s_in_ppm": 31314.1567,
   "s_out_ppm": 1000.0,
   "lhsv_1_h": 0.945324706,
   "reactor_volume_m3": 535.362448,
   "catalyst_t": 374.753714,
   "sulfur_removed_kg_h": 14577.8844,
   "h2s_kg_h": 15496.3911,
   "h2_chemical_kg_h": 2750.06378,
   "h2_makeup_kg_h": 3666.75171,
   "recycle_gas_Nm3_h": 253045.675
  }
 },
 "nci_unamb": 7.54831893,
 "nci_amb": 10.5053897,
 "fuel_loss_pct": 10.0
}''')

# Peng-Robinson flash check of the crude-heater duty (thermo 0.6.1; surrogate sets and P as in the docstring), MW and vapour mass fraction at 360 C
DUTY_CHECK = {"C4,C8,C12,C16,C24,C30": {"2": (198.7, 0.553), "3": (192.2, 0.429)},
              "C4,C8,C12,C18,C28,C36": {"2": (186.0, 0.421), "3": (182.6, 0.337)}}
DUTY_CHECK_REVA = {"C4,C8,C12,C16,C24,C30": {"2": (198.1, 0.612), "3": (192.9, 0.495)},
                   "C4,C8,C12,C18,C28,C36": {"2": (185.7, 0.479), "3": (183.2, 0.400)}}

MW_S, MW_H2S, MW_H2 = 32.06, 34.08, 2.016      # refinery_design/hydrotreater.py constants (atomic-mass based)
# FCC reference case, docs/VALIDATION.md section 2 (a calibration, not a plant validation), wt% of FCC feed. NOT run on this VGO.
FCC_REF = {"dry gas": 3.6, "lpg": 17.8, "gasoline": 49.4, "coke": 5.95}
LCO_FRAC_UNCONV = 0.70                         # refinery_design/fcc.py FccOperation.lco_frac_of_unconverted default
HT_SERVICES = (("naphtha", "NHT", "R-201"), ("kerosene", "KHT", "R-202"), ("diesel", "DHT", "R-203"), ("vgo", "VGO HT", "R-204"))
# Coker, Rev B (S): coke 30 wt% of VR (UOP 2021; JIP Table 41; WRI-02-R012), range 27-35. PTQ Q1 2020 Tables 1-2 (CCR 10-29 domain):
# coke 1.23 x CCR (comparison only), gas 7.8 + 0.051 x CCR, naphtha (21-140 C) 25.37 - 0.573 x CCR, gas oil by difference.
COKE_WT, COKE_LO, COKE_HI = 30.0, 27.0, 35.0
DRUM_FILL_H, COKE_RHO, DRUM_FILL_FRAC = 18.0, 800.0, 0.75      # coker.py defaults (A)
# Real-plant references read by the validator (grade A): IOCL Paradip EC report 2020 Annex-4; investor presentation Jun 2017 slide 7
REAL = dict(S_lo=2.10, S_hi=2.39, S_mean=2.264, petcoke_mean=7.77, petcoke_lo=7.2, petcoke_hi=8.2, nht_Mt=3.96, dcu_Mt=4.4, indmax_Mt=4.17)
# scf of H2 at 60 F, 1 atm (A: standard-condition definition) derived from the ideal-gas law, used only for the scf/bbl range comparison
R_GAS, T_STD, P_STD = 8.314462618, (60 - 32) / 1.8 + 273.15, 101325.0
KG_PER_SCF_H2 = MW_H2 * 1e-3 / (R_GAS * T_STD / P_STD) * 0.3048 ** 3
BBL_M3 = 0.158987294928


def f0(x): return f"{x:,.0f}"
def f1(x): return f"{x:,.1f}"
def f2(x): return f"{x:,.2f}"


def coker_yields(feed, ccr, mode):
    """mode 'A' = Rev A (repo coker.py: coke 1.6 x CCR, gas 7.8 + 0.144 x CCR, 22 % of liquids to naphtha); mode 'B' = Rev B."""
    if mode == "A":
        coke_p = 1.6 * ccr; gas_p = 7.8 + 0.144 * ccr
        naph_p = (100 - coke_p - gas_p) * 0.22
    else:
        coke_p = COKE_WT; gas_p = 7.8 + 0.051 * ccr; naph_p = 25.37 - 0.573 * ccr
    go_p = 100.0 - coke_p - gas_p - naph_p
    assert go_p > 0 and min(coke_p, gas_p, naph_p) > 0, "coker yields out of range"
    k = feed / 100.0
    return dict(feed=feed, ccr=ccr, coke=coke_p * k, gas=gas_p * k, naph=naph_p * k, go=go_p * k, pct=(coke_p, gas_p, naph_p, go_p),
                drum_m3=coke_p * k * DRUM_FILL_H / (COKE_RHO * DRUM_FILL_FRAC))


# ======================================================================== the balance (computed here, asserted closed)
def compute(R, mode="B"):
    st = R["streams"]; ht = R["ht"]
    crude = R["feed_kg_h"]
    cut = {k: st[k]["kg_h"] for k in st}
    assert abs(sum(cut.values()) - crude) / crude < 1e-3, "CDU/VDU cuts must sum to the charge"
    ck = coker_yields(st["vacuum_residue"]["kg_h"], st["vacuum_residue"]["mcr"], mode)
    tr, unit = {}, {}
    for svc, nm, tag in HT_SERVICES:
        h = ht[svc]
        tr[svc] = h["feed_kg_h"] + h["h2_chemical_kg_h"] - h["h2s_kg_h"]          # D1: feed + chemical H2 = treated product + H2S
        assert abs(h["h2s_kg_h"] - h["sulfur_removed_kg_h"] * MW_H2S / MW_S) < 1e-6 * h["h2s_kg_h"]   # D2
        unit[svc] = (h["feed_kg_h"] + h["h2_chemical_kg_h"]) - (tr[svc] + h["h2s_kg_h"])
    h2_mk = sum(ht[k]["h2_makeup_kg_h"] for k in ht)
    h2_chem = sum(ht[k]["h2_chemical_kg_h"] for k in ht)
    h2_purge = h2_mk - h2_chem
    h2s = sum(ht[k]["h2s_kg_h"] for k in ht)
    s_removed = sum(ht[k]["sulfur_removed_kg_h"] for k in ht)
    h2_in_hc = {k: ht[k]["h2_chemical_kg_h"] - ht[k]["sulfur_removed_kg_h"] * (MW_H2S - MW_S) / MW_S for k in ht}
    assert all(v > 0 for v in h2_in_hc.values())
    # element check, hydrogen: make-up = H2 in treated hydrocarbon + H2 in H2S + purge (D)
    h2_out = sum(h2_in_hc.values()) + h2s * (MW_H2S - MW_S) / MW_H2S + h2_purge
    assert abs(h2_out - h2_mk) < 1e-6 * h2_mk, "hydrogen element balance"
    F = tr["vgo"]
    unconv = 100.0 - sum(FCC_REF.values())
    fy = dict(FCC_REF); fy["lco"] = unconv * LCO_FRAC_UNCONV; fy["slurry"] = unconv * (1 - LCO_FRAC_UNCONV)
    fcc = {k: F * v / 100.0 for k, v in fy.items()}
    assert abs(sum(fcc.values()) - F) < 1e-6 * F
    coker_out = ck["coke"] + ck["gas"] + ck["naph"] + ck["go"]
    assert abs(coker_out - ck["feed"]) < 1e-6 * ck["feed"], "coker balance"
    def sw(k): return st[k]["S"]
    T_P = {1: ("40", "5"), 2: ("40", "10"), 3: ("40", "5"), 4: ("60", "5"), 5: ("80", "5"), 6: ("150", "5"), 7: ("200", "8")}
    rows = [
        (1, "Crude", "Crude slate charge", "L", crude, "in", 0, 0, R["slate"]["S"]),
        (2, "LPG", "CDU LPG / off-gas", "V", cut["lpg"], "out", 0, 0, None),
        (3, "SR naph", "Straight-run naphtha", "L", cut["naphtha"], "int", 0, 0, sw("naphtha")),
        (4, "SR kero", "Straight-run kerosene", "L", cut["kerosene"], "int", 0, 0, sw("kerosene")),
        (5, "SR dsl", "Straight-run diesel", "L", cut["diesel"], "int", 0, 0, sw("diesel")),
        (6, "VGO", "Vacuum gas oil", "L", cut["vgo"], "int", 0, 0, sw("vgo")),
        (7, "Vac res", "Vacuum residue", "L", cut["vacuum_residue"], "int", 0, 0, sw("vacuum_residue")),
        (8, "H2 mkup", "Hydrogen make-up, all HT", "V", h2_mk, "in", 100, 0, None),
        (9, "NHT out", "Treated naphtha", "L", tr["naphtha"], "out", 0, 0, 0.5e-4),
        (10, "KHT out", "Treated kerosene", "L", tr["kerosene"], "out", 0, 0, 10e-4),
        (11, "DHT out", "Treated diesel", "L", tr["diesel"], "out", 0, 0, 10e-4),
        (12, "VGOHT", "Treated VGO to FCC", "L", tr["vgo"], "int", 0, 0, 1000e-4),
        (13, "H2S", "H2S to amine / SRU, all HT", "V", h2s, "out", 0, 100, None),
        (14, "HT purge", "H2 purge + solution loss", "V", h2_purge, "out", 100, 0, None),
        (15, "FCC DG", "FCC dry gas", "V", fcc["dry gas"], "out", 0, 0, None),
        (16, "FCC LPG", "FCC LPG", "L/V", fcc["lpg"], "out", 0, 0, None),
        (17, "FCC gaso", "FCC gasoline", "L", fcc["gasoline"], "out", 0, 0, None),
        (18, "LCO", "FCC light cycle oil", "L", fcc["lco"], "out", 0, 0, None),
        (19, "Slurry", "FCC slurry oil", "L", fcc["slurry"], "out", 0, 0, None),
        (20, "FCC coke", "Coke burned in regenerator", "S", fcc["coke"], "out", 0, 0, None),
        (21, "Cok gas", "Coker gas", "V", ck["gas"], "out", 0, 0, None),
        (22, "Cok naph", "Coker naphtha", "L", ck["naph"], "out", 0, 0, None),
        (23, "Cok GO", "Coker gas oil", "L", ck["go"], "out", 0, 0, None),
        (24, "Petcoke", "Delayed-coker coke", "S", ck["coke"], "out", 0, 0, None),
    ]
    tot_in = sum(r[4] for r in rows if r[5] == "in")
    tot_out = sum(r[4] for r in rows if r[5] == "out")
    err = (tot_out - tot_in) / tot_in * 100.0
    assert abs(err) < 0.1, f"overall closure {err}"
    s_crude = crude * R["slate"]["S"] / 100.0
    s_cuts = sum(st[k]["kg_h"] * st[k]["S"] / 100.0 for k in st if st[k]["S"] is not None)
    s_err = (s_cuts - s_crude) / s_crude * 100.0
    assert abs(s_err) < 0.1, f"sulphur closure {s_err}"
    s_in_h2s = h2s * MW_S / MW_H2S
    assert abs(s_in_h2s - s_removed) < 1e-6 * s_removed
    selffuel = fcc["coke"] + fcc["dry gas"] + ck["gas"] + h2_purge
    pools = {"lpg": cut["lpg"] + fcc["lpg"], "gaso": tr["naphtha"] + fcc["gasoline"] + ck["naph"],
             "mid": tr["kerosene"] + tr["diesel"] + fcc["lco"] + ck["go"]}
    return dict(rows=rows, T_P=T_P, crude=crude, tot_in=tot_in, tot_out=tot_out, err=err, s_crude=s_crude, s_cuts=s_cuts, s_err=s_err,
                h2_mk=h2_mk, h2_chem=h2_chem, h2_purge=h2_purge, h2s=h2s, s_removed=s_removed, h2_in_hc=h2_in_hc, unit=unit, tr=tr, fcc=fcc, fy=fy,
                unconv=unconv, coker_out=coker_out, selffuel=selffuel, F=F, ck=ck, h2_out=h2_out, pools=pools, cut=cut,
                petcoke_pct=ck["coke"] / crude * 100.0, light=sum(pools.values()) / crude * 100.0)


C = compute(REF, "B")
CA = compute(REF_A, "A")
assert abs(CA["ck"]["coke"] - 204079.901) < 1.0 and abs(CA["err"]) < 0.1     # the Rev A column reproduces the Rev A coker and closure


def coker_sens():
    """petcoke vs coke fraction (S range 27-35, PTQ 1.23 x CCR as comparison, Rev A 1.6 x CCR), % of crude and kg/h"""
    vr = REF["streams"]["vacuum_residue"]["kg_h"]; ccr = REF["streams"]["vacuum_residue"]["mcr"]
    out = []
    for lab, pct in (("UOP/JIP low", COKE_LO), ("UOP central (Rev B)", COKE_WT), ("PTQ 1.23 x CCR", 1.23 * ccr), ("JIP/UOP high", COKE_HI), ("1.6 x CCR (Rev A form)", 1.6 * ccr)):
        out.append((lab, pct, vr * pct / 100.0, vr * pct / 100.0 / REF["feed_kg_h"] * 100.0))
    return out


def ht_h2_range():
    """S-only hydrotreater H2 (A3) vs the published 150-300 scf/bbl band (ENERGY STAR guide 2015 quoting Gary, secondary), per unit"""
    rows = []
    for svc, nm, tag in HT_SERVICES:
        h = REF["ht"][svc]; bpd = REF["streams"][svc]["bpd"]
        scf_bbl = h["h2_chemical_kg_h"] / KG_PER_SCF_H2 / (bpd / 24.0)
        lo = 150 * (bpd / 24.0) * KG_PER_SCF_H2; hi = 300 * (bpd / 24.0) * KG_PER_SCF_H2
        rows.append((tag + " " + nm, bpd, scf_bbl, h["h2_chemical_kg_h"], lo, hi))
    return rows

# ======================================================================== local helpers
BROWN = "#6d4c41"; VIOLET = "#6a1b9a"


def wtable(s, x, y, colw, rows, size=10, lh=12.2, pad=4, bold_first=False, head=True):
    """table with wrapped cells; returns y below"""
    import textwrap as tw
    cpl = [max(4, int((w - 2 * pad) / (0.53 * size))) for w in colw]
    heights = []
    wrapped = []
    for r in rows:
        cells = [tw.wrap(str(c), cpl[j]) or [""] for j, c in enumerate(r)]
        wrapped.append(cells)
        heights.append(max(len(c) for c in cells) * lh + 6)
    tot = sum(heights); W_ = sum(colw)
    yy = y
    for i, cells in enumerate(wrapped):
        h = heights[i]
        if head and i == 0: R(s, x, yy, W_, h, "#e8eaf0", "none")
        elif i % 2 == 0: R(s, x, yy, W_, h, "#f6f7fa", "none")
        cx = x
        for j, lines in enumerate(cells):
            wgt = 700 if (head and i == 0) or (bold_first and j == 0) else 400
            for k, t in enumerate(lines): T(s, cx + pad, yy + 11 + k * lh, t, size, wgt)
            cx += colw[j]
        yy += h
    R(s, x, y, W_, tot, "none", "#9aa", 1)
    return yy


def zone(s, x, y, w, h, title, sub=None, right=False):
    R(s, x, y, w, h, "none", "#7986cb", 1.1, "7 4")
    xx, an = (x + w - 6, "end") if right else (x + 6, "start")
    T(s, xx, y + 13, title, 10, 700, anchor=an, fill="#1a237e")
    if sub: T(s, xx, y + 25, sub, 9.5, 400, anchor=an, fill=GREY)


def rv(s, x, y, rot=0, color=INK):
    """relief valve glyph, inlet bottom / outlet top at rot=0; rot=90 gives inlet left, outlet right. size 22 x 16"""
    s.add(f'<g transform="translate({x},{y}) rotate({rot})" stroke="{color}" stroke-width="1.6" fill="#fff">'
          f'<polygon points="-7,11 7,11 0,0"/><polygon points="-7,-11 7,-11 0,0"/>'
          f'<polyline points="9,-6 13,-3 9,0 13,3 9,6" fill="none"/></g>')


def fired_heater(s, x, y, w, h, tag, sub=None, hot=False):
    """box fired heater with stack, coil and three burners; returns ports"""
    R(s, x, y, w, h, "#fffaf0" if not hot else "#ffe0b2", INK, 2.4)
    R(s, x + 10, y - 26, 14, 26, "#fff", INK, 1.8)
    pts = []
    n = 7
    for i in range(n + 1):
        pts.append((x + 10 + (w - 20) * i / n, y + h * (0.10 if i % 2 == 0 else 0.34)))
    PL(s, pts, 1.6, INK)
    for bx in (x + w * 0.25, x + w * 0.5, x + w * 0.75):
        s.add(f'<polygon points="{bx-5},{y+h} {bx+5},{y+h} {bx},{y+h-9}" fill="#ff8f00" stroke="{RED}" stroke-width="1"/>')
    T(s, x + w / 2, y + h * 0.60, tag, 11, 700, "middle")
    if sub: T(s, x + w / 2, y + h * 0.60 + 11, sub, 9, 400, "middle")
    return dict(inlet=(x + w - 9, y), left=(x, y + h * 0.5), out=(x + w, y + h * 0.5), fuel=(x + w / 2, y + h), x=x, y=y, w=w, h=h)


def hopline(s, pts, hops=(), sw=2.6, color=INK, dash=None, arrow_=True):
    """orthogonal line with small bridge arcs where a horizontal segment crosses the x values in hops"""
    d = f"M{pts[0][0]},{pts[0][1]}"
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if ya == yb:
            for hx in sorted((h for h in hops if min(xa, xb) < h < max(xa, xb)), reverse=xb < xa):
                sgn = 1 if xb > xa else -1
                d += f" L{hx - 6 * sgn},{ya} A6,6 0 0 {1 if sgn > 0 else 0} {hx + 6 * sgn},{ya}"
        d += f" L{xb},{yb}"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    s.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{da}/>')
    if arrow_:
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        if abs(xb - xa) >= abs(yb - ya): arrow(s, xb, yb, "r" if xb > xa else "l", color)
        else: arrow(s, xb, yb, "d" if yb > ya else "u", color)


SIG = dict(sw=1.3, stroke=BLUE, dash="5 4", marker="ahb")
CTL = dict(sw=1.5, stroke=RED, dash="6 4", marker="ahr")
H2C = GREEN
SOUR = VIOLET


def esd_box(s, x, y, w, h, t1, t2=None):
    R(s, x, y, w, h, "#fff3e0", RED, 1.6)
    T(s, x + w / 2, y + 13, t1, 10, 700, "middle", RED)
    if t2: T(s, x + w / 2, y + 25, t2, 9, 400, "middle", RED)




# ---------------------------------------------------------------------------------------------------- Rev B additions
class SheetB(Sheet):
    """Sheet whose header and status line say Rev B (pidlib frame() prints Rev A; pidlib is not edited)"""
    def svg(self):
        return super().svg().replace("|  Rev A<", "|  Rev B<").replace("Draft A.", "Draft B.")


NS = 8                                                   # sheets in the set
PROJ = "Oil refinery, Paradip-class basket, 15 Mt/yr"
BASIS_S = "refinery-design-opensource, Rev B, 11 Nov 2026"


def newsheet(no, title, sub):
    return SheetB(no, title, sub, code="VS-REF", project=PROJ, basis=BASIS_S)


def dtag(s, x, y, letters, num, side="r", color=BLUE, r=8):
    """small instrument circle with the function letters inside; the numeric tag is written beside it (keeps sheet 1 legible)"""
    s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{color}" stroke-width="1.4"/>')
    T(s, x, y + 2.6, letters[:2], 7.5, 700, "middle", color)
    full = f"{letters}-{num}"
    if side == "r": T(s, x + r + 3, y + 3.3, full, 9, 700, "start", color)
    elif side == "l": T(s, x - r - 3, y + 3.3, full, 9, 700, "end", color)


def tie(s, x, y, t="FL"):
    """tie to the flare / relief header"""
    s.add(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="{BROWN}" stroke-width="1.5"/>')
    T(s, x, y + 3.2, t, 8.5, 700, "middle", BROWN)


def psv_tag(s, x, y, tag, anchor="start", size=9):
    T(s, x, y, tag, size, 700, anchor, BROWN)


# ---------------------------------------------------------------------------------------------------- relief schedule data
# (tag, item, design-pressure basis (A), relief cases, device, discharge, sizing status / data needed, mark, drawn?)
# Marks: R = a named free source supports the requirement (S5 OSHA 1910.119 relief design basis; S11 CSB Kuraray discharge location;
# S13 Roberts/HSL fire case; S1 HSG176 tank fire venting); A = assumed here; gap = controlling standard not obtained.
RELIEF = [
    ("T-001", "Crude tank, floating roof", "atmospheric (A)", "fire at rim seal or full surface; overfill; roof sinking",
     "none: open rim vent and roof drain", "foam to rim seal, bund, closed roof drain (A)",
     "not sized: needs tank diameter, height, level (tank_venting.py: API 2000 5th ed. read; 7th ed. not)", "R S1 / gap API 2000 7th, OISD-STD-108/116/118", False),
    ("T-801", "Gasoline tank, floating roof", "atmospheric (A)", "fire at rim seal or full surface; overfill; roof tilt",
     "none: open rim vent and roof drain", "foam to rim seal, bund, closed roof drain (A)",
     "not sized: needs tank size and vapour pressure", "R S1 / gap OISD-STD-108", False),
    ("E-101", "Crude preheat exchanger", "higher-pressure side governs; both n/d (A)", "blocked-in thermal expansion; tube rupture; fire",
     "none while open to D-101 and C-101 path; TSV only if block valves are fitted", "C-101 PSV-101 path / closed drain (A)",
     "not sized: needs both design pressures and the tube-rupture case (API 521 not obtained)", "A / gap API 521", False),
    ("E-102", "Crude preheat exchanger", "as E-101 (A)", "as E-101", "as E-101", "as E-101", "not sized: as E-101", "A / gap API 521", False),
    ("D-101", "Desalter", "crude pump shut-in head plus margin (A)", "blocked outlet; fire; liquid-full thermal expansion; steam or water flash",
     "PSV-103", "flare header via tie FL (A)", "not sized: vessel size n/d; fire case needs wetted area (relief.wetted_area_cylinder) and crude latent heat", "R S13 fire case / A", True),
    ("H-101", "Crude heater coil (fired)", "pump shut-in (A)", "blocked outlet; tube rupture into firebox; coking",
     "no PSV on coil: relieves through the open transfer line to C-101 PSV-101; trips XV-101/102/103", "flare via PSV-101",
     "not sized: pass count, coil volume n/d. No block valve may isolate coil from PSV-101 (A)", "A", False),
    ("C-101", "Crude column", "operating plus margin (A); operating P n/d", "loss of overhead cooling (E-103); reflux failure; blocked vapour outlet; fire; power failure",
     "PSV-101", "flare header (drawn)", "not sized: needs overhead vapour rate and MW (relief.gas_area ready); the repo has no preheat or condenser design", "R S5 / A", True),
    ("E-103", "Overhead condenser", "n/d (A)", "cooling-water failure (see C-101); tube rupture if CW pressure exceeds shell; thermal",
     "none: protected by C-101 PSV-101 and D-102 PSV-104 (open path); CW-side relief if tube rupture governs", "flare / CW return (A)",
     "not sized: needs both design pressures", "A / gap API 521", False),
    ("D-102", "Reflux drum", "operating plus margin (A)", "blocked liquid or vapour outlet; fire; loss of cooling", "PSV-104", "flare header (drawn)",
     "not sized: vessel size n/d", "A", True),
    ("H-102", "Vacuum heater coil (fired)", "pump shut-in (A)", "blocked outlet; tube rupture; coking; steam injection loss",
     "no PSV on coil: relieves through C-102 PSV-102", "flare via PSV-102", "not sized: coil n/d", "A", False),
    ("C-102", "Vacuum column", "full vacuum and positive (A)", "loss of vacuum system; air ingress; steam-out; excess heat input; fire",
     "PSV-102 for positive pressure; no vacuum breaker: nitrogen admission (A)", "tie FL via vacuum-system seal drum (A)",
     "not sized: needs vapour load; vacuum collapse case needs wall thickness (gap)", "A / gap API 521, 620", True),
    ("D-201..204", "HP separators of the four HT loops", "HP loop pressure set by licensor (A)", "as the reactor of the same loop",
     "protected by PSV-201..204 (open path to reactor)", "flare header", "not sized: with R-201..204", "A", False),
    ("R-201", "Naphtha HT reactor", "HP loop (A)", "blocked outlet; loss of quench or cooling; H2 make-up valve fails open; feed/effluent exchanger tube rupture; fire",
     "PSV-201", "flare header (drawn)", "not sized: relief load needs loop inventory and make-up valve Cv (n/d); 49.5 m3 is catalyst volume from LHSV, not vessel volume", "A", True),
    ("R-202", "Kerosene HT reactor", "HP loop (A)", "as R-201", "PSV-202", "flare header (drawn)", "not sized: 87.1 m3 catalyst volume only", "A", True),
    ("R-203", "Diesel HT reactor", "HP loop (A)", "as R-201", "PSV-203", "flare header (drawn)", "not sized: 241.6 m3 catalyst volume only", "A", True),
    ("R-204", "VGO HT reactor", "HP loop (A)", "as R-201 plus temperature runaway (largest exotherm of the four); H2S release",
     "PSV-204; HV-204 emergency depressuring (TAHH-204 via ESD-2)", "flare header (drawn)", "not sized: 535.4 m3 catalyst volume only; depressuring rate needs inventory and target rate (depressuring.py needs them)", "A", True),
    ("C-501", "Amine absorber", "loop pressure (A)", "blocked gas outlet; foaming carry-over; fire", "licensor package PSV (not drawn)", "flare (A)",
     "not sized: package unit, n/d", "A", False),
    ("SRU", "Sulphur recovery unit", "low pressure, licensor (A)", "explosion in reaction furnace or sulphur pit; H2S release", "licensor package relief and explosion vents (not drawn)",
     "tail gas incinerator / flare (A)", "not sized: package unit, n/d", "A", False),
    ("R-301", "FCC reactor", "operating plus margin (A)", "hydrocarbon or air back-flow through slide valve; blocked overhead; loss of C-301 overhead cooling",
     "PSV-302 on reactor overhead line", "flare header (drawn)", "not sized: vessel and catalyst inventory n/d (fcc_operate not run for sizing)", "A", True),
    ("R-302", "FCC regenerator", "operating plus margin (A)", "afterburn; air blower surge or trip; combustion overpressure", "PSV-303", "tie FL (A); flue gas route to stack (A)",
     "not sized: needs flue-gas and air flows; fcc_operate gives 757 C only as a screen", "A", True),
    ("C-301", "FCC main fractionator", "operating plus margin (A)", "loss of overhead or pumparound cooling; blocked; fire", "PSV-301", "flare header (drawn)",
     "not sized: needs vapour load n/d", "A", True),
    ("H-401", "Coker heater coil (fired)", "pump shut-in (A)", "blocked outlet; coil coking; tube rupture; low velocity",
     "no PSV on coil: relieves through the open line to the on-line drum PSV-402A/B", "flare via PSV-402",
     "not sized: coil n/d. Switching-valve position must keep this path open (A)", "A", False),
    ("D-401A/B", "Coke drums", "operating plus margin (A)", "overfill or foam-over; steam or quench water into hot drum; blocked overhead; unheading release; fire",
     "PSV-402A/B (one per drum)", "tie FL (A); coker blowdown D-402 not drawn (A)",
     "not sized: drum dimensions n/d (6,122 m3 is the coke volume per fill cycle, not the drum)", "A", True),
    ("C-401", "Coker fractionator", "operating plus margin (A)", "loss of overhead cooling; blocked; fire", "PSV-401", "tie FL to flare header (drawn)",
     "not sized: n/d", "A", True),
    ("D-901", "Flare knock-out drum", "low pressure (A)", "blocked outlet; liquid overfill; fire", "PSV-901", "tie FL to flare stack (A)",
     "not sized: needs the governing simultaneous relief case (OISD-STD-106 walled)", "A / gap OISD-STD-106", True),
    ("FL-901", "Flare header and stack", "back-pressure limit set by lowest PSV (A)", "simultaneous relief on loss of cooling or power; liquid carry-over; radiation at grade",
     "not a relief device", "atmosphere at height", "not sized: needs simultaneous cases; process_safety.flare (API 521 point source) needs rate and geometry", "gap OISD-STD-106/109, API 521", False),
]
DRAWN_DEVICES = ["PSV-101", "PSV-102", "PSV-103", "PSV-104", "PSV-201", "PSV-202", "PSV-203", "PSV-204", "PSV-301", "PSV-302", "PSV-303",
                 "PSV-401", "PSV-402A", "PSV-402B", "PSV-901", "HV-204"]


# ======================================================================== the P&ID (common to all sheets)
HT_X, HT_W, HT_H = 540, 195, 62
HT_Y = {"naphtha": 136, "kerosene": 214, "diesel": 292, "vgo": 396}
GAP_X = {"h2": 776, "relief": 798}


def pid(s, detail=True):
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    # ---------------- flare / relief header (top) and zones
    PL(s, [(250, 88), (1112, 88), (1112, 715), (1062, 715)], 3.4, BROWN)
    arrow(s, 1062, 715, "l", BROWN)
    T(s, 436, 83, "FLARE / RELIEF HEADER (A)", 9.5, 700, fill=BROWN)
    zone(s, 22, 98, 440, 504, "CRUDE + VACUUM UNIT")
    zone(s, 532, 98, 222, 372, "HYDROPROCESSING", None, right=True)
    zone(s, 806, 98, 292, 322, "FCC UNIT")
    zone(s, 532, 480, 222, 62, "AMINE + SULPHUR RECOVERY (A)", None, right=True)
    zone(s, 478, 550, 300, 216, "DELAYED COKER")
    zone(s, 820, 534, 96, 62, "H2 UNIT (A)")

    # ---------------- crude tank, pump, preheat, desalter
    tank(s, 62, 190, 76, 54, "T-001", "crude (FR)", roof="floating", level=0.7)
    dtag(s, 112, 132, "LHD", "001")
    pump(s, 140, 179, 12, "P-101")
    PL(s, [(100, 179), (105, 179)], 2.6); PL(s, [(127, 179), (128, 179)], 2.6)
    valve(s, 116, 179, 0, "gate", act=True, color=RED); T(s, 116, 150, "XV-001", 8.5, 700, "middle", RED)
    pipe(s, [(152, 167), (152, 152), (165, 152)])
    hx(s, 190, 152, 50, 24, "E-101", None)
    PL(s, [(215, 152), (231, 152)], 2.6)
    hvessel(s, 262, 152, 44, 30, "D-101", None)
    T(s, 262, 190, "desalter", 9, 400, "middle")
    PL(s, [(262, 137), (262, 119)], 2.2, BROWN); rv(s, 262, 108, 0); PL(s, [(262, 97), (262, 88)], 2.2, BROWN)
    psv_tag(s, 274, 106, "PSV-103")
    PL(s, [(293, 152), (301, 152)], 2.6)
    hx(s, 326, 152, 50, 24, "E-102", None)
    strm(s, 152, 160, 1)
    PL(s, [(351, 152), (351, 232)], 2.6); arrow(s, 351, 232, "d")
    h1 = fired_heater(s, 282, 232, 78, 76, "H-101", "crude heater")
    pipe(s, [(360, 270), (394, 270)])
    # C-101
    c1 = vvessel(s, 420, 160, 52, 175, None, None, trays=8)
    T(s, 452, 346, "C-101", 11, 700)
    T(s, 452, 358, "crude column", 9, 400)
    # overhead
    PL(s, [(420, 145), (420, 128), (432, 128)], 2.6)
    hx(s, 450, 128, 36, 24, "E-103", None)
    hvessel(s, 500, 128, 44, 26, "D-102", None)
    PL(s, [(468, 128), (470, 128)], 2.6)
    pipe(s, [(530, 128), (600, 128)])
    strm(s, 556, 128, 2)
    T(s, 608, 125, "LPG to gas plant (A)", 9.5)
    PL(s, [(500, 115), (500, 114)], 2.2, BROWN); rv(s, 500, 103, 0); PL(s, [(500, 92), (500, 88)], 2.2, BROWN)
    psv_tag(s, 512, 101, "PSV-104")
    # side draws
    for key, nm, y_, n in (("naphtha", "", 167, 3), ("kerosene", "", 245, 4), ("diesel", "", 323, 5)):
        pipe(s, [(446, y_), (540, y_)]); strm(s, 492, y_, n)
    # residue to vacuum
    PL(s, [(420, 350), (420, 372), (356, 372), (356, 400)], 2.6); arrow(s, 356, 400, "d")
    h2h = fired_heater(s, 291, 400, 74, 56, "H-102", "vac. heater (A)")
    pipe(s, [(365, 428), (410, 428)])
    c2 = vvessel(s, 440, 395, 60, 190, None, None, trays=0, packing=True)
    T(s, 404, 590, "C-102", 11, 700, "end")
    T(s, 404, 602, "vacuum column", 9, 400, "end")
    PL(s, [(440, 378), (440, 366), (484, 366)], 2.6); arrow(s, 484, 366, "r")
    T(s, 490, 370, "vacuum system (A)", 9.5)
    pipe(s, [(470, 427), (540, 427)]); strm(s, 505, 427, 6)
    # PSV-102 on the C-102 head, tie to the relief header
    PL(s, [(403, 386), (424, 386)], 2.2, BROWN); rv(s, 392, 386, -90); PL(s, [(381, 386), (377, 386)], 2.2, BROWN); tie(s, 368, 386)
    psv_tag(s, 392, 404, "PSV-102", "middle")

    # ---------------- hydroprocessing blocks
    tags = {"naphtha": ("NHT", "R-201", 9, "D-201", "PSV-201"), "kerosene": ("KHT", "R-202", 10, "D-202", "PSV-202"),
            "diesel": ("DHT", "R-203", 11, "D-203", "PSV-203"), "vgo": ("VGO HT", "R-204", 12, "D-204", None)}
    for key, (nm, rt, sn, dn, pv) in tags.items():
        y0 = HT_Y[key]
        R(s, HT_X, y0, HT_W, HT_H, "#fff", INK, 1.6)
        T(s, HT_X + 70, y0 + 12, f"{nm}  {rt}", 10, 700)
        yc = y0 + 31
        vvessel(s, 585, y0 + 15, 22, 28, None, None)
        hvessel(s, 652, yc, 40, 18, None, None)
        T(s, 652, y0 + 56, f"{dn} HP sep", 9, 400, "middle")
        PL(s, [(HT_X, yc), (574, yc)], 2.6)
        PL(s, [(596, yc), (625, yc)], 2.2)
        if pv:
            pipe(s, [(681, yc), (770, yc)]); strm(s, 752, yc, sn)
            PL(s, [(660, y0 + 22), (660, y0 + 13), (692, y0 + 13)], 2.0, BROWN)
            rv(s, 703, y0 + 13, 90)
            hopline(s, [(714, y0 + 13), (GAP_X["relief"], y0 + 13)], hops=((GAP_X["h2"],) if key != "naphtha" else ()), sw=2.0, color=BROWN, arrow_=False)
            psv_tag(s, 692, y0 + 8, pv, "start", 9)
        else:
            pipe(s, [(681, yc), (748, yc)]); strm(s, 722, yc, sn)
        # H2 branch: header -> under the vessels -> feed line
        hopline(s, [(GAP_X["h2"], y0 + 49), (556, y0 + 49), (556, yc)], sw=2.0, color=H2C, dash="7 3")
        if key != "vgo":   # sour-gas stub to the amine unit (all four loops are stream 13)
            hopline(s, [(735, y0 + 57), (760, y0 + 57)], sw=1.8, color=SOUR, dash="5 3")
    PL(s, [(566, 458), (566, 484)], 2.0, SOUR, "5 3"); arrow(s, 566, 484, "d", SOUR)
    strm(s, 582, 470, 13, SOUR)
    # H2 header, make-up compressor and plant
    compressor(s, 868, 508, 14, None)
    T(s, 888, 504, "K-201", 10, 700)
    T(s, 888, 516, "H2 make-up", 9, 400)
    R(s, 828, 558, 80, 22, "#f1f8e9", H2C, 1.2); T(s, 868, 573, "H2 PLANT", 10, 700, "middle", H2C)
    PL(s, [(868, 558), (868, 523)], 2.4, H2C, "7 3"); arrow(s, 868, 523, "u", H2C)
    hopline(s, [(854, 508), (GAP_X["h2"], 508), (GAP_X["h2"], 185)], sw=2.4, color=H2C, dash="7 3", arrow_=False)
    T(s, GAP_X["h2"] + 5, 180, "H2", 9.5, 700, fill=H2C)
    strm(s, 815, 508, 8, H2C)
    PL(s, [(GAP_X["h2"], 508), (GAP_X["h2"], 540)], 2.0, H2C, "7 3"); arrow(s, GAP_X["h2"], 540, "d", H2C, 7)
    strm(s, GAP_X["h2"], 524, 14, H2C)
    T(s, GAP_X["h2"] + 14, 527, "purge to fuel gas", 8.5, 400, fill=H2C)
    # treated VGO to FCC
    hopline(s, [(735, 427), (836, 427), (836, 290)], hops=(GAP_X["h2"], GAP_X["relief"]), sw=2.6)
    # R-204 reliefs: PSV-204 on the right side, HV-204 emergency depressuring from the top
    PL(s, [(735, 410), (739, 410)], 2.2, BROWN)
    rv(s, 750, 410, 90)
    hopline(s, [(761, 410), (GAP_X["relief"], 410)], hops=(GAP_X["h2"],), sw=2.2, color=BROWN, arrow_=False)
    PL(s, [(718, 396), (718, 384), (721, 384)], 2.2, BROWN)
    valve(s, 732, 384, 0, "gate", act=True, color=BROWN)
    hopline(s, [(743, 384), (GAP_X["relief"], 384)], hops=(GAP_X["h2"],), sw=2.2, color=BROWN, arrow_=False)
    T(s, 746, 380, "HV-204", 8.5, 700)
    T(s, 756, 399, "PSV-204", 9, 700, "middle")
    PL(s, [(GAP_X["relief"], 410), (GAP_X["relief"], 88)], 2.4, BROWN)
    arrow(s, GAP_X["relief"], 88, "u", BROWN)
    # C-101 relief
    PL(s, [(420, 128), (420, 119)], 2.2, BROWN); rv(s, 420, 108, 0); PL(s, [(420, 97), (420, 88)], 2.2, BROWN)
    T(s, 408, 106, "PSV-101", 9.5, 700, "end")

    # ---------------- ARU / SRU
    vvessel(s, 566, 498, 20, 20, None, None, trays=2)
    T(s, 582, 508, "C-501", 9, 700); T(s, 582, 520, "amine absorber", 9, 400)
    hvessel(s, 672, 514, 40, 16, None, None)
    T(s, 700, 536, "SRU (A)", 9, 400, "middle")
    PL(s, [(698, 514), (738, 514)], 2.0, SOUR); arrow(s, 738, 514, "r", SOUR)
    T(s, 722, 508, "S", 9, 700, "middle", SOUR)
    dtag(s, 612, 468, "AT", "204A"); dtag(s, 700, 468, "AT", "204B")

    # ---------------- FCC
    r1 = vvessel(s, 836, 170, 34, 110, None, None)
    T(s, 836, 196, "R-301", 9.5, 700, "middle"); T(s, 836, 207, "reactor", 8.5, 400, "middle")
    r2 = vvessel(s, 912, 170, 60, 130, None, None)
    T(s, 912, 192, "R-302", 11, 700, "middle"); T(s, 912, 204, "regenerator", 9, 400, "middle")
    c3 = vvessel(s, 1030, 130, 52, 200, None, None, trays=8)
    T(s, 1030, 366, "C-301", 11, 700, "middle"); T(s, 1030, 378, "main fractionator", 9, 400, "middle")
    PL(s, [(836, 160), (836, 118), (990, 118), (990, 310), (1004, 310)], 2.6); arrow(s, 1004, 310, "r")
    PL(s, [(853, 240), (882, 240)], 2.4); arrow(s, 882, 240, "r")
    valve(s, 867, 240, 0, "gate", act=True); T(s, 867, 212, "SV-301", 8.5, 700, "middle")
    PL(s, [(882, 285), (836, 285)], 2.4); arrow(s, 836, 285, "l")
    valve(s, 859, 285, 0, "gate", act=True); T(s, 859, 258, "SV-302", 8.5, 700, "middle")
    compressor(s, 912, 380, 14, None)
    T(s, 936, 384, "K-301 air", 9.5, 700)
    PL(s, [(912, 366), (912, 318)], 2.4); arrow(s, 912, 318, "u")
    PL(s, [(870, 380), (898, 380)], 2.4); arrow(s, 898, 380, "r")
    PL(s, [(942, 222), (982, 222)], 2.6); arrow(s, 982, 222, "r"); strm(s, 962, 222, 20)
    T(s, 944, 206, "flue gas", 9, 400)
    for n, y_, lab in ((15, 150, "dry gas"), (16, 190, "LPG"), (17, 230, "gasoline"), (18, 270, "LCO"), (19, 310, "slurry")):
        pipe(s, [(1056, y_), (1092, y_)]); strm(s, 1074, y_ + 0, n)
        T(s, 1058, y_ - 14, lab, 9, 400)
    PL(s, [(1030, 115), (1030, 113)], 2.2, BROWN); rv(s, 1030, 102, 0)
    PL(s, [(1030, 91), (1030, 88)], 2.2, BROWN)
    T(s, 1018, 100, "PSV-301", 9.5, 700, "end")
    # PSV-302 on the reactor overhead line, PSV-303 on the regenerator wall with a tie to the header
    PL(s, [(886, 118), (886, 114)], 2.2, BROWN); rv(s, 886, 103, 0); PL(s, [(886, 92), (886, 88)], 2.2, BROWN)
    psv_tag(s, 898, 101, "PSV-302")
    PL(s, [(942, 186), (941, 186)], 2.2, BROWN); rv(s, 952, 186, 90); PL(s, [(963, 186), (965, 186)], 2.2, BROWN); tie(s, 974, 186)
    psv_tag(s, 946, 172, "PSV-303", "start")
    s.add(f'<circle cx="912" cy="139" r="8" fill="#fff" stroke="{BLUE}" stroke-width="1.4"/>'); T(s, 912, 141.6, "TA", 7.5, 700, "middle", BLUE)
    T(s, 923, 142.3, "TAHH-302", 9, 700, fill=BLUE)

    # ---------------- coker
    hc = fired_heater(s, 500, 605, 75, 70, "H-401", "coker heater")
    PL(s, [(440, 602), (440, 640), (500, 640)], 2.6); arrow(s, 500, 640, "r")
    strm(s, 440, 624, 7)
    for cx in (622, 668):
        vvessel(s, cx, 590, 38, 78, None, None)
    T(s, 645, 733, "D-401A/B  coke drums", 10, 700, "middle")
    PL(s, [(575, 640), (598, 640), (598, 710), (668, 710)], 2.4)
    for cx in (622, 668):
        PL(s, [(cx, 710), (cx, 680)], 2.4); arrow(s, cx, 680, "u")
        valve(s, cx, 696, 90, "gate", act=True)
    T(s, 604, 722, "XV-401A/B", 9, 700)
    PL(s, [(622, 579), (622, 568), (685, 568), (685, 620), (703, 620)], 2.4)
    PL(s, [(668, 579), (668, 568)], 2.4); arrow(s, 703, 620, "r")
    vvessel(s, 725, 575, 44, 125, None, None, trays=5)
    T(s, 725, 725, "C-401", 11, 700, "middle")
    for n, y_, lab in ((21, 598, "gas"), (22, 648, "naph"), (23, 690, "GO")):
        pipe(s, [(747, y_), (778, y_)]); strm(s, 762, y_, n)
        T(s, 748, y_ + 22, lab, 8.5, 400)
    PL(s, [(603, 662), (584, 662), (584, 745)], 2.6); arrow(s, 584, 745, "d"); strm(s, 584, 722, 24)
    T(s, 590, 757, "petcoke to pit", 9.5, 400)
    rv(s, 758, 563, 90); PL(s, [(748, 563), (736, 563)], 2.0, BROWN)
    T(s, 744, 553, "PSV-401", 9, 700)
    PL(s, [(769, 563), (790, 563)], 2.0, BROWN); arrow(s, 790, 563, "r", BROWN)
    tie(s, 803, 563)
    # PSV-402A/B: one glyph on the common overhead of the two drums (a PSV per drum, drawn once), tie to the header
    PL(s, [(630, 568), (630, 569)], 2.2, BROWN); rv(s, 630, 558, 0); PL(s, [(630, 547), (630, 546)], 2.2, BROWN); tie(s, 630, 537)
    psv_tag(s, 642, 554, "PSV-402A/B")
    # coker heater fuel-gas shut-off, pass-flow and drum-level SIS tags
    PL(s, [(537, 700), (537, 678)], 2.2, AMBER); arrow(s, 537, 678, "u", AMBER, 7)
    valve(s, 537, 689, 90, "gate", act=True, color=RED); T(s, 546, 692, "XV-404", 9, 700, fill=RED)
    dtag(s, 498, 696, "FSLL", "401", "l")
    dtag(s, 594, 600, "LAHH", "401A/B", "l")

    # ---------------- tank T-801, flare KO and stack
    tank(s, 840, 745, 80, 46, "T-801", "gasoline (FR)", roof="floating", level=0.65)
    dtag(s, 840, 686, "LHD", "801")
    hvessel(s, 1020, 715, 64, 30, "D-901", None)
    T(s, 1020, 755, "flare KO", 9, 400, "middle")
    PL(s, [(979, 715), (930, 715)], 3.0, BROWN)
    flare(s, 930, 745, 140, "FL-901")
    T(s, 940, 632, "flare + pilot (A)", 9, 400)
    PL(s, [(1010, 700), (1010, 697)], 2.2, BROWN); rv(s, 1010, 686, 0); PL(s, [(1010, 675), (1010, 673)], 2.2, BROWN); tie(s, 1010, 664)
    psv_tag(s, 998, 684, "PSV-901", "end")
    dtag(s, 1045, 738, "LAHH", "901")

    # ---------------- utilities
    util = [("Fuel gas (14, 15, 21) to burners", AMBER), ("Steam: stripping, ejectors, coker", GREY), ("Cooling water: condensers, coolers", BLUE),
            ("Instrument air / nitrogen / fire water", GREY)]
    R(s, 26, 614, 330, 70, "#fff", "#aab", 1)
    T(s, 32, 627, "UTILITIES (stubs, A)", 10, 700, fill="#1a237e")
    for i, (t, col) in enumerate(util):
        yy = 641 + i * 12
        PL(s, [(34, yy - 3), (56, yy - 3)], 2, col); arrow(s, 56, yy - 3, "r", col, 6)
        T(s, 62, yy, t, 9.5)
    for (px, py, tg) in ((321, 345, ""), (328, 482, "FG")):
        PL(s, [(px, py), (px, py - 22)], 2.2, AMBER); arrow(s, px, py - 22, "u", AMBER, 7)
        if tg: T(s, px + 6, py - 6, tg, 9.5, 700, fill=AMBER)
    if detail:
        loops(s)
    return dict(h1=h1)


def loops(s):
    """control and safety loops on the most hazardous units (tagged A unless noted); the same tags are used in the cause-and-effect matrix"""
    PL(s, [(321, 345), (321, 308)], 2.2, AMBER)
    valve(s, 321, 328, 90, "gate", act=True, color=RED); T(s, 335, 331, "XV-101", 9.5, 700, fill=RED)
    bubble(s, 322, 190, "FSLL", "101", True, BLUE)
    PL(s, [(337, 190), (351, 190)], **SIG)
    esd_box(s, 136, 262, 104, 40, "ESD-1", "heater BMS (A)")
    PL(s, [(307, 190), (188, 190), (188, 262)], **SIG)
    bubble(s, 264, 278, "BE", "101", True, BLUE, r=13)
    PL(s, [(251, 278), (241, 278)], **SIG)
    PL(s, [(188, 302), (188, 328), (306, 328)], **CTL)
    bubble(s, 378, 300, "TIC", "101", True, BLUE)
    PL(s, [(378, 285), (378, 270)], **SIG)
    PL(s, [(378, 315), (378, 345), (326, 345)], 1.3, BLUE, "5 4", "ahb")
    bubble(s, 150, 332, "AT", "101A", True, BLUE, r=13)
    PL(s, [(150, 319), (150, 302)], **SIG)
    valve(s, 351, 200, 90, "gate", act=True, color=RED); T(s, 366, 190, "XV-102", 9, 700, fill=RED)
    valve(s, 377, 270, 0, "gate", act=True, color=RED); T(s, 376, 256, "XV-103", 8.5, 700, "middle", RED)
    valve(s, 756, 445, 0, "gate", act=True, color=RED); T(s, 756, 462, "XV-205", 8.5, 700, "middle", RED)
    valve(s, 515, 427, 0, "gate", act=True, color=RED); T(s, 515, 449, "XV-206", 9, 700, "middle", RED)
    esd_box(s, 960, 396, 118, 34, "ESD-3 FCC SIS", "R: SAFETY.md")
    valve(s, 912, 345, 90, "gate", act=True, color=RED); T(s, 926, 349, "XV-301", 9.5, 700, fill=RED)
    PL(s, [(960, 413), (944, 413), (944, 345), (927, 345)], 1.5, RED, "6 4", "ahr")
    bubble(s, 585, 376, "TAHH", "204", True, BLUE)
    PL(s, [(585, 391), (585, 406)], **SIG)
    esd_box(s, 612, 361, 88, 30, "ESD-2", "HT (A)")
    PL(s, [(600, 376), (612, 376)], **SIG)
    PL(s, [(700, 376), (730, 376)], **CTL)
    bubble(s, 867, 352, "PDIC", "301", True, BLUE)
    PL(s, [(867, 337), (867, 254)], **SIG)
    bubble(s, 832, 352, "PDALL", "301", True, BLUE)
    PL(s, [(832, 337), (832, 292)], **SIG)
    esd_box(s, 700, 738, 70, 28, "ESD-4", "coker (A)")
    valve(s, 836, 395, 90, "gate", act=True, color=RED); T(s, 846, 398, "XV-302", 9, 700, fill=RED)


def pid_overlay_legend(s, x, y):
    legend_mini(s, x, y)


# ======================================================================== sheets 1 to 3
def Mt(kg_h): return kg_h * 8760 / 1e9


def sheet_pid():
    s = newsheet(1, "REFINERY Rev B: block-level P&ID with relief devices, detectors and SIS tags", "P&ID: units, streams, relief, key loops")
    frame(s, NS)
    pid(s, True)
    legend_mini(s, 36, 725)
    panel_box(s)
    R_ = REF; sl = R_["slate"]; vf = R_["vol_frac"]
    y = section(s, 1135, 84, 445, "BASIS (Rev B; S unless marked)")
    yy = y + 16
    for t in (f"Crude: three-crude refit, {vf['cold_lake_blend']*100:.0f} / {vf['upper_zakum']*100:.0f} / {vf['dalia']*100:.0f} vol% Cold Lake / Upper Zakum / Dalia: API {sl['api']:.1f}, {sl['S']:.2f} wt% S, TAN {sl['tan']:.2f}. Fitted to S (Paradip 2.26) and vacuum residue 27.3 % of crude. Rev A basket was 2.90 % S (sheet 2).",
              f"Charge 15.0 Mt/yr = {f0(C['crude'])} kg/h at 8,760 h/yr (A), {f0(R_['bpd'])} bpd (D).",
              f"Coker coke 30 wt% of vacuum residue (range 27-35; UOP, JIP); petcoke {C['petcoke_pct']:.1f} % of crude (Paradip 7.2-8.2). FCC yields: reference case, not run on this VGO.",
              f"CDU heater {f1(R_['furnace_MW'])} MW (S); an independent PR-flash check gives 183-199 MW (sheet 3).",
              "Not modelled and not drawn: reformer, alkylation, isomerisation, hydrocracker, gas plant, utilities."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13, bullet=True) + 3
    y = section(s, 1135, yy + 4, 445, "WHAT REV B ADDS TO THIS SHEET")
    yy = y + 16
    nd = len([d for d in DRAWN_DEVICES if d.startswith("PSV")])
    for t in (f"{nd} PSV tags and HV-204 now drawn (was 4 PSVs); the relief schedule on sheet 6 covers every pressure item, with a device or a written reason.",
              "Detectors, ESD-4 and SIS tags named in the scenarios are drawn here: AT-101A, AT-204A/B, LHD-001/801, LAHH-901, LAHH-401A/B, FSLL-401, XV-404, TAHH-302, PDALL-301.",
              "HP separators are tagged D-201..204; amine absorber C-501. Sour-gas stubs end at the amine unit (stream 13 diamond on the R-204 line)."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13, bullet=True) + 3
    y = section(s, 1135, yy + 4, 445, "LEGEND")
    yy = y + 14
    PL(s, [(1145, yy), (1180, yy)], 2.4, GREEN, "7 3"); T(s, 1186, yy + 4, "hydrogen", 9.5)
    PL(s, [(1245, yy), (1280, yy)], 2.0, VIOLET, "5 3"); T(s, 1286, yy + 4, "sour gas / H2S", 9.5)
    PL(s, [(1370, yy), (1405, yy)], 3, BROWN); T(s, 1411, yy + 4, "relief / flare", 9.5)
    yy += 22
    rv(s, 1155, yy, 90); T(s, 1172, yy + 4, "PSV / relief device", 9.5)
    tie(s, 1300, yy); T(s, 1314, yy + 4, "FL = tie to relief header", 9.5)
    yy += 22
    dtag(s, 1150, yy, "AT", "xxx"); T(s, 1196, yy + 3, "detector / switch circle, tag beside", 9.5)
    yy += 20
    strm(s, 1150, yy, 7); T(s, 1172, yy + 4, "stream number = HMB column (sheet 2)", 9.5)
    yy += 18
    yy = WRAP(s, 1141, yy + 4, "Tags: R = required or recommended in a named free source; A = assumed by this drawing. Only the stream numbers, the repo outputs and the sourced values are S/D.", 70, 10, 12.5, fill=GREY) + 2
    y = section(s, 1135, yy + 8, 445, "UNITS")
    yy = y + 14
    for t in ("CDU/VDU: T-001, P-101, E-101/102, D-101 desalter, H-101, C-101, E-103, D-102, H-102, C-102.",
              "Hydroprocessing R-201..204 with HP separators D-201..204; K-201 H2 make-up; C-501 amine absorber and SRU (A).",
              "FCC: R-301, R-302, SV-301/302, K-301, C-301. Coker: H-401, D-401A/B, C-401. Flare: D-901, FL-901. T-801 gasoline tank."):
        yy = WRAP(s, 1141, yy, t, 70, 10, 12.5, bullet=True) + 2
    # bottom tables
    hts = REF["ht"]
    y = section(s, 20, 784, 640, "EQUIPMENT LIST (S = repo output, D = derived, A = assumed)")
    rows = [("Tag", "Description", "Size / duty", "Basis"),
            ("H-101", "Crude heater, 250 to 360 C", f"{f1(REF['furnace_MW'])} MW", "S distill()"),
            ("C-101/C-102", "Crude / vacuum columns", "n/d (no tray design)", "A"),
            ("E-101..103, D-101/102", "Preheat, condenser, desalter, drum", "n/d", "A"),
            ("H-102, H-401", "Vacuum / coker heaters", "n/d", "A"),
            ("R-201 NHT", "Naphtha HT, LHSV / volume / cat.", f"{hts['naphtha']['lhsv_1_h']:.2f} /h, {hts['naphtha']['reactor_volume_m3']:.1f} m3, {hts['naphtha']['catalyst_t']:.1f} t", "S hydrotreat()"),
            ("R-202 KHT", "Kerosene HT", f"{hts['kerosene']['lhsv_1_h']:.2f} /h, {hts['kerosene']['reactor_volume_m3']:.1f} m3, {hts['kerosene']['catalyst_t']:.1f} t", "S hydrotreat()"),
            ("R-203 DHT", "Diesel HT", f"{hts['diesel']['lhsv_1_h']:.2f} /h, {hts['diesel']['reactor_volume_m3']:.1f} m3, {hts['diesel']['catalyst_t']:.1f} t", "S hydrotreat()"),
            ("R-204 VGO HT", "VGO HT (FCC feed)", f"{hts['vgo']['lhsv_1_h']:.3f} /h, {hts['vgo']['reactor_volume_m3']:.1f} m3, {hts['vgo']['catalyst_t']:.1f} t", "S hydrotreat()"),
            ("D-201..204", "HP separators", "n/d", "A"),
            ("K-201", "H2 make-up; recycle gas (all HT)", f"{f0(C['h2_mk'])} kg/h; {f0(sum(hts[k]['recycle_gas_Nm3_h'] for k in hts))} Nm3/h", "D / S"),
            ("C-501, SRU", "Amine absorber, sulphur recovery", f"H2S {f0(C['h2s'])} kg/h to ARU", "D; sizes A"),
            ("R-301/302, C-301", "FCC reactor, regenerator, fractionator", "feed = stream 12; sizes not run", "A (ref. case)"),
            ("K-301, SV-301/302", "Air blower, slide valves", "n/d", "A"),
            ("D-401A/B, C-401", "Coke drums, coker fractionator", f"coke {f0(C['ck']['drum_m3'])} m3 per fill cycle; drum size n/d", "D (A)"),
            ("T-001 / T-801", "Floating-roof tanks", "n/d: needs tankage data", "A"),
            ("D-901 / FL-901", "Flare KO drum, flare", "n/d: needs relief loads", "A")]
    table(s, 20, y, (125, 200, 215, 100), rows, 16, 10, bold_first_col=True)
    y2 = section(s, 670, 784, 450, "RELIEF DEVICES DRAWN ON THIS SHEET (schedule: sheet 6)")
    prot = {"PSV-101": "C-101", "PSV-102": "C-102 (+H-102)", "PSV-103": "D-101 desalter", "PSV-104": "D-102 reflux drum", "PSV-201": "R-201 loop", "PSV-202": "R-202 loop",
            "PSV-203": "R-203 loop", "PSV-204": "R-204 loop", "PSV-301": "C-301", "PSV-302": "R-301 reactor", "PSV-303": "R-302 regenerator", "PSV-401": "C-401",
            "PSV-402A": "D-401A (+H-401)", "PSV-402B": "D-401B (+H-401)", "PSV-901": "D-901 KO drum", "HV-204": "R-204 depressuring"}
    rows = [("Tag", "Protects", "Discharge")] + [(d, prot[d], "flare header" if d not in ("PSV-102", "PSV-303", "PSV-401", "PSV-402A", "PSV-402B", "PSV-901") else "tie FL to header") for d in DRAWN_DEVICES]
    table(s, 670, y2, (80, 200, 170), rows, 16, 10, bold_first_col=True)
    return s


def sheet_hmb():
    s = newsheet(2, "REFINERY Rev B: heat and material balance (HMB), changes and closure", "Heat and material balance")
    frame(s, NS)
    rows_ = C["rows"]
    labels = [r[0] for r in rows_]
    crude = C["crude"]
    def pct(v): return f"{v / crude * 100:.2f}"
    def swt(r):
        v = r[8]
        if v is None: return "n/d"
        return f"{v:.2f}" if v >= 0.1 else f"{v:.4f}"
    out_rows = [
        ("Name", [r[1] for r in rows_]),
        ("Boundary", [{"in": "IN", "out": "OUT", "int": "int."}[r[5]] for r in rows_]),
        ("Phase", [r[3] for r in rows_]),
        ("T (C), A", [C["T_P"].get(r[0], ("n/d", "n/d"))[0] for r in rows_]),
        ("P (barg), A", [C["T_P"].get(r[0], ("n/d", "n/d"))[1] for r in rows_]),
        ("Mass flow (kg/h)", [f0(r[4]) for r in rows_]),
        ("Mass flow (t/h)", [f1(r[4] / 1000) for r in rows_]),
        ("% of crude charge", [pct(r[4]) for r in rows_]),
        ("Composition, mass %", None),
        ("Hydrocarbon", [f"{100 - r[6] - r[7]:.0f}" for r in rows_]),
        ("H2", [f"{r[6]:.0f}" for r in rows_]),
        ("H2S", [f"{r[7]:.0f}" for r in rows_]),
        ("S in stream, wt%", [swt(r) for r in rows_]),
        ("Basis", ["S"] * 7 + ["D"] * 12 + ["S*", "S*", "S*", "S*", "D"][:5]),
    ]
    out_rows[-1] = ("Basis", ["S"] * 7 + ["D"] * 13 + ["B", "B", "B", "B"])
    y = hmb_table(s, 20, 84, labels, out_rows, first_w=182, col_w=57.5, rh=16.5, size=9.5, title="STREAM TABLE (numbers match the diamonds on sheet 1)")
    T(s, 22, y + 12, "S = repo output (basket refit, cut yields, HT stoichiometry). D = computed here. B = Rev B coker yields (sourced coke 30 wt% of VR, PTQ slopes for gas and naphtha, gas oil by difference). FCC streams 15-20 = reference case (A4), NOT run on this VGO. T, P = A.", 9, fill=GREY)
    y0 = y + 24
    # ---- left column: closure, duties, hydrotreating
    y1 = section(s, 20, y0, 540, "CLOSURE (asserted in the generator)")
    R(s, 20, y1, 540, 140, "#fff", "#889", 1)
    yy = y1 + 15
    T(s, 28, yy, "Mass: in %s kg/h, out %s kg/h, error %.4f %%  (assert < 0.1 %%)" % (f0(C['tot_in']), f0(C['tot_out']), abs(C['err'])), 10.5, 700, fill=GREEN); yy += 14
    T(s, 28, yy, "In = streams 1 + 8. Out = 2, 9, 10, 11, 13 to 24. Intermediates 3-7, 12 not counted.", 9.5); yy += 13
    T(s, 28, yy, f"CDU/VDU cuts 2-7 = {f0(sum(r[4] for r in rows_[1:7]))} kg/h vs charge {f0(crude)}.", 9.5); yy += 13
    T(s, 28, yy, f"Coker: coke+gas+naphtha+gas oil = {f0(C['coker_out'])} = feed {f0(C['ck']['feed'])} (gas oil by difference, so closure is by construction).", 9.5); yy += 13
    T(s, 28, yy, f"FCC: yields sum to 100.00 % of {f0(C['F'])} kg/h (reference case).", 9.5); yy += 13
    T(s, 28, yy, f"Sulphur: crude {f0(C['s_crude'])} vs cuts {f0(C['s_cuts'])} kg/h ({C['s_err']:+.3f} %); HT S removed {f0(C['s_removed'])} = S in H2S {f0(C['h2s']*MW_S/MW_H2S)} kg/h.", 9.5); yy += 13
    T(s, 28, yy, f"Hydrogen: make-up {f0(C['h2_mk'])} = in HC {f0(sum(C['h2_in_hc'].values()))} + in H2S {f0(C['h2s']*(MW_H2S-MW_S)/MW_H2S)} + purge {f0(C['h2_purge'])} kg/h (error {(C['h2_out']-C['h2_mk'])/C['h2_mk']*100:+.5f} %).", 9.5); yy += 13
    T(s, 28, yy, "Not checked: carbon, energy (no data). Losses: zero by construction.", 9, fill=GREY); yy += 13
    T(s, 28, yy, f"Self-fuel candidates (FCC coke, dry gas, coker gas, purge) = {C['selffuel']/crude*100:.1f} % of crude vs PPAC fuel and loss {REF['fuel_loss_pct']:.1f} %.", 9.5)
    yy = y1 + 140
    y2 = section(s, 20, yy + 10, 540, "DUTY LINES")
    rows = [("Item", "Duty", "Basis"),
            ("H-101 crude heater", f"{f1(REF['furnace_MW'])} MW", "S distill(); PR check 183-199 MW (sheet 3)"),
            ("H-102, H-401, R-201..204 heat of reaction", "n/d", "not computed by repo"),
            ("K-201 H2 make-up compressor", "n/d", "needs delivery pressure (A)"),
            ("FCC heat balance (R-301/302)", "n/d", "reference case only"),
            ("E-101/102/103 preheat and condenser", "n/d", "no preheat-train design in repo")]
    y2 = wtable(s, 20, y2, (225, 85, 230), rows, 9.5, 11.5)
    y3 = section(s, 20, y2 + 10, 540, "HYDROTREATING DETAIL (S: hydrotreat(); H2S, treated flows D)")
    rows = [("Unit", "Feed kg/h", "S in -> out (ppm)", "H2 chem kg/h", "H2 mkup kg/h", "H2S kg/h")]
    for svc, nm, tag in HT_SERVICES:
        h = REF["ht"][svc]
        rows.append((tag + " " + nm, f0(h["feed_kg_h"]), f"{f0(h['s_in_ppm'])} -> {h['s_out_ppm']:g}", f1(h["h2_chemical_kg_h"]), f1(h["h2_makeup_kg_h"]), f1(h["h2s_kg_h"])))
    rows.append(("Total", "", "", f1(C["h2_chem"]), f1(C["h2_mk"]), f1(C["h2s"])))
    y3 = wtable(s, 20, y3, (105, 85, 120, 80, 80, 70), rows, 9.5, 11.5)
    T(s, 22, y3 + 12, f"Sulphur to SRU from HT H2S only: {C['s_removed']*24/1000:.0f} t/d (D) vs 696 t/d product sulphur at Paradip (EC report): coker and FCC S routing n/d.", 9, fill=GREY)

    # ---- middle column: Rev A to Rev B changes
    xA = 575
    yA = section(s, xA, y0, 545, "REV A TO REV B CHANGES (Rev A recomputed from the frozen Rev A outputs)")
    a, b = CA, C
    vr_a, vr_b = REF_A["streams"]["vacuum_residue"], REF["streams"]["vacuum_residue"]
    def dev(x, ref): return f"{(x - ref) / ref * 100:+.0f} %"
    rowsC = [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
             ("Crude slate S, wt%", f"{REF_A['slate']['S']:.2f}", f"{REF['slate']['S']:.2f}", "IOCL EC report 2020 Annex-4 (2.10-2.39); fit", f"deviation vs 2.264: {dev(REF_A['slate']['S'], 2.264)} -> 0 (fitted). API {REF_A['slate']['api']:.1f} -> {REF['slate']['api']:.1f}; all cut masses and HT sizes change"),
             ("Coker coke, wt% of VR", f"{a['ck']['pct'][0]:.1f}", f"{b['ck']['pct'][0]:.1f}", "UOP Apr 2021; JIP T41; WRI-02-R012 (27-35)", f"petcoke {a['petcoke_pct']:.1f} -> {b['petcoke_pct']:.1f} % of crude (Paradip 7.2-8.2); stream 24 {f0(a['ck']['coke'])} -> {f0(b['ck']['coke'])} kg/h"),
             ("Coker gas, wt% of VR", f"{a['ck']['pct'][1]:.2f}", f"{b['ck']['pct'][1]:.2f}", "PTQ Q1 2020 T1-2: 7.8 + 0.051 CCR", f"stream 21 {f0(a['ck']['gas'])} -> {f0(b['ck']['gas'])} kg/h"),
             ("Coker naphtha, wt% of VR", f"{a['ck']['pct'][2]:.2f}", f"{b['ck']['pct'][2]:.2f}", "PTQ: 25.37 - 0.573 CCR (21-140 C)", f"stream 22 {f0(a['ck']['naph'])} -> {f0(b['ck']['naph'])} kg/h"),
             ("Coker gas oil, wt% of VR", f"{a['ck']['pct'][3]:.2f}", f"{b['ck']['pct'][3]:.2f}", "by difference (PTQ 47.5 at coke 33.5)", f"stream 23 {f0(a['ck']['go'])} -> {f0(b['ck']['go'])} kg/h; leaves boundary untreated (A6)"),
             ("SR naphtha to NHT, Mt/yr", f"{Mt(a['cut']['naphtha']):.2f}", f"{Mt(b['cut']['naphtha']):.2f}", "IOCL OEP sec 1.2: NHT 3.96", f"gap to nameplate {dev(Mt(a['cut']['naphtha']), 3.96)} -> {dev(Mt(b['cut']['naphtha']), 3.96)}: end-point sweep on sheet 3, not closed"),
             ("Treated VGO to FCC, Mt/yr", f"{Mt(a['F']):.2f}", f"{Mt(b['F']):.2f}", "IOCL OEP: INDMAX 4.17", f"{dev(Mt(a['F']), 4.17)} -> {dev(Mt(b['F']), 4.17)}: WORSE (cost of the S fit)"),
             ("Vacuum residue to coker, Mt/yr", f"{Mt(a['cut']['vacuum_residue']):.2f}", f"{Mt(b['cut']['vacuum_residue']):.2f}", "IOCL OEP: DCU 4.4", "unchanged: both fitted to 4.1/15"),
             ("HT S removed, t/d", f"{a['s_removed']*24/1000:.0f}", f"{b['s_removed']*24/1000:.0f}", "EC report: 696 t/d product S", f"{dev(a['s_removed']*24/1000, 696)} -> {dev(b['s_removed']*24/1000, 696)} (coker, FCC S routing n/d)"),
             ("H2 make-up, kg/h", f0(a['h2_mk']), f0(b['h2_mk']), "hydrotreat() S-only (A3)", "range 150-300 scf/bbl on sheet 3; K-201 duty n/d"),
             ("LPG + gasoline + middle dist., % crude", f"{a['light']:.1f}", f"{b['light']:.1f}", "IOCL slide 7: 81", f"{dev(a['light'], 81)} -> {dev(b['light'], 81)}"),
             ("Crude heater H-101, MW", f"{REF_A['furnace_MW']:.1f}", f"{REF['furnace_MW']:.1f}", "distill(); PR flash 183-199", "kept (S); independent check is 6 to 15 % lower"),
             ("FCC yields (A4)", "ref. case", "ref. case", "docs/VALIDATION.md s.2", "unchanged; repo run for this VGO differs (sheet 3)"),
             ("Closure", f"{abs(a['err']):.4f} %", f"{abs(b['err']):.4f} %", "asserts", f"S {a['s_err']:+.4f} % -> {b['s_err']:+.4f} %; H2 balance added")]
    yA = wtable(s, xA, yA, (108, 44, 44, 142, 207), rowsC, 9, 10.8)
    yA2 = section(s, xA, yA + 8, 545, "ASSUMED, to be confirmed by licensor or vendor (A)")
    As = ["A1  8,760 h/yr. A2  HT product S targets 0.5 / 10 / 10 / 1000 ppm (hydrotreater.SERVICES reference points).",
          "A3  H2 use = 3 mol H2 per mol S, 25 % of make-up lost (hydrotreat() defaults): a floor; N, aromatics not counted (sheet 3 range).",
          "A4  FCC yields = docs/VALIDATION.md reference case (3.6 / 17.8 / 49.4 / 5.95 wt%), a calibration to published ranges, NOT run on this VGO. LCO 70 % / slurry 30 % of unconverted (fcc.py). No open yield table found.",
          "A5  Coker coke 30 wt% of VR is the central value of 27-35; gas and naphtha follow PTQ slopes (domain CCR 10-29; this slate 24.9).",
          "A6  Coker liquids, FCC liquids and treated cuts leave the boundary or go to blending; real routing not defined.",
          "A7  T and P on streams 1-7 are round numbers; others n/d.  A8  Desalter, preheat, vacuum system, ARU/SRU, H2 plant, tankage, flare have no sizes.",
          "A9  Tags, valve types, ESD logic and relief devices on sheets 1, 4 to 8.  A10  Slate is a three-crude fit to two targets, not a purchase list."]
    yy = yA2 + 14
    for t in As: yy = WRAP(s, xA + 6, yy, t, 105, 9.5, 12, fill=INK) + 2
    # ---- right column: pools and sources
    xS = 1135
    pools = [("LPG (2, 16)", C["pools"]["lpg"], CA["pools"]["lpg"]), ("Gasoline range (9, 17, 22)", C["pools"]["gaso"], CA["pools"]["gaso"]),
             ("Middle distillate (10, 11, 18, 23)", C["pools"]["mid"], CA["pools"]["mid"]),
             ("Fuel gas (14, 15, 21)", C["rows"][13][4] + C["rows"][14][4] + C["rows"][20][4], CA["rows"][13][4] + CA["rows"][14][4] + CA["rows"][20][4]),
             ("Petcoke (24)", C["rows"][23][4], CA["rows"][23][4]), ("FCC coke burned (20)", C["rows"][19][4], CA["rows"][19][4]),
             ("Slurry (19)", C["rows"][18][4], CA["rows"][18][4]), ("H2S (13)", C["rows"][12][4], CA["rows"][12][4])]
    yP = section(s, xS, y0, 445, "PRODUCT POOLS, % of crude (Rev B bar; Rev A in grey)")
    yy = yP + 13
    for nm, v, va in pools:
        pc, pa = v / crude * 100, va / CA["crude"] * 100
        R(s, xS + 180, yy - 9, pa * 4.2, 5, "#b0b4c4", "none"); R(s, xS + 180, yy - 4, pc * 4.2, 8, "#5c6bc0", "none")
        T(s, xS + 6, yy, nm, 9.5); T(s, xS + 184 + max(pc, pa) * 4.2, yy + 1, f"{pc:.1f} ({pa:.1f})", 9.5, 700)
        yy += 17
    T(s, xS + 6, yy + 4, f"LPG + gasoline + middle distillate = {C['light']:.1f} % (Rev A {CA['light']:.1f} %); published 79-81 %.", 9, fill=GREY)
    yS = section(s, xS, yy + 14, 445, "SOURCES (S) AND FORMULAS (D)")
    S_ = ["S1  repo benchmarks.py: CDU_MTPA 15.0, COKER_TO_CDU 4.1/15; paradip_nci 7.5-10.5 vs 10.6 reported (CHT, OGJ 2025); IOCL's 12.2 is commissioning only.",
          "S2  repo distillation.distill(), hydrotreater.hydrotreat(), assay.py assays (cold_lake_blend, upper_zakum, dalia); runner in the generator docstring.",
          "S3  IOCL Paradip EC compliance report Oct19-Mar20, Annexure-4 (crude S 2.264 wt% mean, range 2.10-2.39; petcoke 7.77 % of crude; sulphur 696 t/d); IOCL investor presentation Jun 2017 slide 7; IOCL On-Site Emergency Plan sec 1.2 (unit nameplates). Read by the validator (REFINERY_VALIDATION.md).",
          "S4  Honeywell UOP Apr 2021 (digitalrefining 1002610): coker converts about 30 wt% of VR to coke. Tulsa JIP DOE/BC/15182-2 Table 41. WRI-02-R012. PTQ Q1 2020 pp.82-83 Tables 1-2 (digitalrefining 1002409). Via GAP_CLOSURE_THERMO.md.",
          "S5  ENERGY STAR Guide for Petroleum Refineries 2015 (quotes Gary 2007: 150-300 scf/bbl; secondary).",
          "S6  docs/VALIDATION.md s.2 (FCC reference case). D1 product = feed + H2 - H2S. D2 H2S = S x 34.08/32.06. D3 purge = make-up - chemical. D4 FCC stream = feed x yield. D5 petcoke = VR x coke %. D6 scf/bbl uses 60 F, 1 atm (A)."]
    yy = yS + 14
    for t in S_: yy = WRAP(s, xS + 6, yy, t, 70, 9.5, 11.8) + 3
    return s


def sheet_hmb2():
    s = newsheet(3, "REFINERY Rev B: HMB checks, ranges and what is not closed", "HMB checks and sensitivities")
    frame(s, NS)
    crude = C["crude"]
    # (a) coker sensitivity
    y = section(s, 20, 84, 760, "A  COKER COKE: SENSITIVITY OF PETCOKE (stream 24) TO THE COKE FRACTION")
    rows = [("Coke fraction of vacuum residue", "wt% of VR", "kg/h", "% of crude", "vs Paradip 7.2-8.2 % (mean 7.8)")]
    for lab, pc, kgh, pcr in coker_sens():
        rows.append((lab, f"{pc:.1f}", f0(kgh), f"{pcr:.2f}", "within" if 7.2 <= pcr <= 8.21 else f"{(pcr - 7.77) / 7.77 * 100:+.0f} % vs mean"))
    y = wtable(s, 20, y, (230, 90, 120, 90, 230), rows, 10, 12)
    y = WRAP(s, 24, y + 14, f"Derived real-plant ratio: petcoke 7.77 % of crude over a coker feed of 4.4 Mt/yr on 15 Mt/yr = 26.6 % of feed (D), which also suggests the real coker feed CCR is below this slate's {C['ck']['ccr']:.1f} wt%. Rev B keeps 30 % (central, grade A sources); 27 % reproduces the lower end. The 1.6 x CCR form is a 1975 refinery-set ratio (quoted in WRI-02-R012) and is kept only as the Rev A column.", 150, 10, 12.5)
    # (b) HT H2 range
    y = section(s, 20, y + 10, 760, "B  HYDROTREATER H2 (A3): S-ONLY FLOOR VS THE PUBLISHED 150-300 scf/bbl BAND  (unchanged, shown as a range)")
    rows = [("Unit", "feed bpd", "S-only scf/bbl", "S-only H2 kg/h", "H2 kg/h at 150", "H2 kg/h at 300")]
    tot = [0, 0, 0]
    for tag, bpd, scf, chem, lo, hi in ht_h2_range():
        rows.append((tag, f0(bpd), f"{scf:.0f}", f0(chem), f0(lo), f0(hi))); tot[0] += chem; tot[1] += lo; tot[2] += hi
    rows.append(("Total", "", "", f0(tot[0]), f0(tot[1]), f0(tot[2])))
    y = wtable(s, 20, y, (200, 100, 120, 120, 110, 110), rows, 10, 12)
    y = WRAP(s, 24, y + 14, f"The band is a generic hydrotreating figure (ENERGY STAR guide quoting Gary 2007, secondary, grade A as a document but a generic range); the VGO unit is a heavier, higher-S service and the naphtha unit is far below the band because it is a 0.04 wt% S feed. The Rev A value is a floor (no aromatics or nitrogen term). Applying the band would raise the H2 plant duty (stream 8) by up to {tot[2]/tot[0]:.1f} x; not applied because the band is not service-specific. 1 scf H2 = {KG_PER_SCF_H2*1000:.3f} g (D, 60 F, 1 atm).", 150, 10, 12.5)
    # (c) naphtha end point
    y = section(s, 20, y + 10, 760, "C  NAPHTHA CUT END POINT vs the NHT NAMEPLATE (3.96 Mt/yr, IOCL On-Site Emergency Plan sec 1.2)")
    ne = REF["naph_end_sens"]
    rows = [("TBP end point", "SR naphtha Mt/yr", "+ coker naphtha Mt/yr", "vs 3.96")]
    for e in ("150", "180", "200"):
        v = ne[e]; w = v + Mt(C["ck"]["naph"])
        rows.append((f"{e} C" + (" (repo default, used)" if e == "150" else ""), f"{v:.2f}", f"{w:.2f}", f"{(w - 3.96) / 3.96 * 100:+.0f} %"))
    y = wtable(s, 20, y, (230, 150, 190, 190), rows, 10, 12)
    y = WRAP(s, 24, y + 14, "Even a 200 C naphtha plus coker naphtha reaches about half of the nameplate. No source explains the nameplate (it may also take other feeds); the 150 C end point is kept. Not closable here.", 150, 10, 12.5)
    # (d) heater duty
    y = section(s, 20, y + 10, 760, "D  CRUDE HEATER DUTY: repo correlation vs an independent Peng-Robinson flash")
    rows = [("Case", "coil P (bar abs, A)", "PR duty MW", "PR vapour wt% at 360 C", "repo duty / vapour")]
    for lab, dd in DUTY_CHECK.items():
        for P, (mw, vf) in dd.items():
            rows.append((f"surrogates {lab}", P, f"{mw:.1f}", f"{vf*100:.0f}", f"{REF['furnace_MW']:.1f} MW / {REF['vap']*100:.0f} %"))
    y = wtable(s, 20, y, (230, 130, 110, 160, 130), rows, 10, 12)
    lo = min(v[0] for d in DUTY_CHECK.values() for v in d.values()); hi = max(v[0] for d in DUTY_CHECK.values() for v in d.values())
    y = WRAP(s, 24, y + 14, f"PR range {lo:.0f}-{hi:.0f} MW; repo {REF['furnace_MW']:.1f} MW is {(REF['furnace_MW']-hi)/hi*100:+.0f} % to {(REF['furnace_MW']-lo)/lo*100:+.0f} % above it (Rev A recomputed on the Rev A basket: 216.6 MW vs 185-198 MW, the earlier ideal-gas n-alkane check gave 202 MW). The spread comes from surrogates and coil pressure (both A), not from the EOS. No plant duty was found, so the repo value is kept and flagged high-side. Command: thermo.FlashVL with PRMIX, ChemicalConstantsPackage.from_IDs of butane, octane, dodecane, hexadecane, tetracosane, triacontane (or octadecane, octacosane, hexatriacontane), z from the cut masses, H(360 C) - H(250 C) x mol/s, thermo 0.6.1.", 150, 10, 12.5)
    # right column
    x2 = 800
    y2 = section(s, x2, 84, 780, "E  FCC YIELDS: REFERENCE CASE (used) vs REPO RUN FOR THIS VGO (information only)")
    fr = REF["fcc_repo"]["yields"]
    fy = C["fy"]
    rows = [("wt% of FCC feed", "reference case (used)", "repo fcc_operate() on this VGO", "difference")]
    for lab, k_ref, k_run in (("dry gas", "dry gas", "dry_gas"), ("LPG", "lpg", "lpg"), ("gasoline", "gasoline", "gasoline"), ("LCO", "lco", "lco"), ("slurry", "slurry", "slurry"), ("coke", "coke", "coke")):
        rows.append((lab, f"{fy[k_ref]:.2f}", f"{fr[k_run]:.2f}", f"{fr[k_run]-fy[k_ref]:+.2f}"))
    y2 = wtable(s, x2, y2, (170, 180, 260, 170), rows, 10, 12)
    y2 = WRAP(s, x2 + 4, y2 + 14, f"The balance uses the reference case (docs/VALIDATION.md section 2), which is a calibration to published ranges and was NOT run on this VGO. A repo run (CoolProp available in the check environment) with the repo's 90 % S-removal pretreat gives the column at right, 69.9 % conversion and a {REF['fcc_repo']['regen_T_C']:.0f} C regenerator, with a warning that dense-bed height is shallow. The two differ by up to 5 points on LPG and 7 points on LCO plus slurry taken together. No open INDMAX or plant yield table was found (two searches), so neither set is validated; the real INDMAX is a propylene-maximising mode and is not represented by either. Flows 15-19 are therefore indicative.", 150, 10, 12.5)
    y2 = section(s, x2, y2 + 10, 780, "F  SLATE FIT: WHAT THE TWO-TARGET REFIT COSTS")
    vf = REF["vol_frac"]
    rows = [("Quantity", "Rev A basket", "Rev B basket", "Paradip reference"),
            ("Crude blend (vol%)", "57 UZ / 43 CL", f"{vf['cold_lake_blend']*100:.0f} CL / {vf['upper_zakum']*100:.0f} UZ / {vf['dalia']*100:.0f} Dalia", "n/a (mix varies by month)"),
            ("API / S wt% / TAN", f"{REF_A['slate']['api']:.1f} / {REF_A['slate']['S']:.2f} / {REF_A['slate']['tan']:.2f}", f"{REF['slate']['api']:.1f} / {REF['slate']['S']:.2f} / {REF['slate']['tan']:.2f}", "S 2.10-2.39"),
            ("Vacuum residue, % of crude", f"{REF_A['vr_wt']*100:.1f}", f"{REF['vr_wt']*100:.1f}", "27.3 (4.1/15); 29.3 nameplate"),
            ("VGO, % of crude", f"{REF_A['vgo_wt']*100:.1f}", f"{REF['vgo_wt']*100:.1f}", "28.0 (FCC 4.2/15)"),
            ("VR CCR (MCR) wt%", f"{REF_A['streams']['vacuum_residue']['mcr']:.1f}", f"{REF['streams']['vacuum_residue']['mcr']:.1f}", "n/d (inferred below 27)")]
    y2 = wtable(s, x2, y2, (180, 150, 250, 200), rows, 10, 12)
    y2 = WRAP(s, x2 + 4, y2 + 14, f"Two targets (S and VR) with three crudes leaves a one-parameter family; the fit picks the point where both hold. VGO rises to 30.5 % of crude against the published 28.0 %, so the FCC feed is now {(Mt(C["F"])-4.17)/4.17*100:+.0f} % against the INDMAX figure (Rev A {(Mt(CA["F"])-4.17)/4.17*100:+.0f} %). TAN rises to 0.87, which raises the naphthenic-acid corrosion flag at H-101 and C-101 (scenario 1). Dalia is a plausible Atlantic-basin grade in the repo's assay file; its use is a fitting device, not evidence of Paradip's purchases.", 150, 10, 12.5)
    y2 = section(s, x2, y2 + 10, 780, "G  NOT CLOSED, AND WHY")
    for t in ("NHT feed 59 % to 68 % below nameplate: no source explains the nameplate; end-point sweep (C) reaches about half (unchanged).",
              "FCC yields: no open table; reference case kept, repo run shown (E). The 757 C regenerator is a repo screen, below its 760 C flag; Rev A basket gave 772 C.",
              "Crude heater duty: no plant value; PR check 6 to 15 % below the repo number (D). Unchanged.",
              "Hydrotreater H2 below the 150-300 scf/bbl band: floor kept, range shown (B). Sulphur routing from coker and FCC to the SRU: not modelled, so the SRU load (696 t/d real) is not reproduced.",
              "Coker CCR: the real value is likely lower than 24.9 wt% (ratio 26.6 % of feed); not testable without the assay of the actual coker feed."):
        y2 = WRAP(s, x2 + 6, y2 + 14, t, 150, 10, 12.5, bullet=True) - 6
    return s


# ======================================================================== scenarios (sheets 4 and 5)
def badge(s, x, y, t, color=RED):
    s.add(f'<circle cx="{x}" cy="{y}" r="13" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
    T(s, x, y + 4, t, 11, 700, "middle", "#fff")


def callout(s, x, y, w, lines, color=RED, size=9.5, lh=11.5, fill="#fff"):
    h = len(lines) * lh + 8
    R(s, x, y, w, h, fill, color, 1.3)
    for i, t in enumerate(lines): T(s, x + 5, y + 12 + i * lh, t, size, 700 if i == 0 else 400, fill=color)
    return h


def cloud(s, cx, cy, rx, ry, color="#7cb342", op=0.35):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" opacity="{op}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6 4"/>')


def bullets(s, x, y, items, width=70, size=10, lh=12.5):
    for t in items: y = WRAP(s, x, y, t, width, size, lh, bullet=True) + 3
    return y


def sheet_scn_a():
    s = newsheet(4, "REFINERY Rev B: scenarios 1 to 3, heater tube rupture, H2 / H2S release, FCC upset", "Scenarios 1 to 3 on the P&ID")
    frame(s, NS)
    pid(s, True)
    flame(s, 321, 233, -5, 46, 28, 0.92)
    flame(s, 360, 262, 82, 52, 24, 0.85)
    flame(s, 321, 346, 0, 38, 36, 0.8)
    star(s, 321, 270, 15)
    badge(s, 262, 226, "1")
    cloud(s, 652, 427, 118, 46, "#7cb342", 0.33)
    star(s, 652, 436, 15)
    badge(s, 528, 394, "2")
    star(s, 867, 240, 14)
    badge(s, 948, 165, "3")
    PL(s, [(882, 262), (853, 262)], 3, RED, None, "ahr")
    flame(s, 912, 175, 0, 42, 30, 0.9)
    star(s, 912, 235, 12)
    panel_box(s)
    sl = REF["slate"]; h = REF["ht"]["vgo"]
    y = section(s, 1135, 84, 445, "1  CRUDE HEATER H-101: TUBE RUPTURE")
    yy = bullets(s, 1141, y + 14, [
        f"Release: hot crude at the 360 C coil outlet (S: distill()) from a failed coil pass, inside the firebox. Charge through the heater is {f0(C['crude'])} kg/h = {C['crude']/3600:.0f} kg/s (D), an upper bound; per-pass flow and hole size are n/d.",
        f"Hazard: firebox fire and fireball, pool fire under the heater, flame on C-101 and the transfer line. Naphthenic-acid and sulphidation corrosion above about 232 C is flagged for this basket (Rev B TAN {sl['tan']:.2f}, {sl['S']:.2f} wt% S; Rev A was 0.55 and 2.9; docs/SAFETY.md, S).",
        "Not quantified: needs coil inventory, rupture size, pass flow, tube metallurgy, time to isolate."])
    y = section(s, 1135, yy + 4, 445, "2  H2 / H2S RELEASE AT VGO HYDROTREATER")
    yy = bullets(s, 1141, y + 14, [
        f"Release: recycle-gas or effluent leak at R-204 / D-204. Loop duty (S, hydrotreat()): H2S {f0(h['h2s_kg_h'])} kg/h generated, H2 make-up {f0(h['h2_makeup_kg_h'])} kg/h, recycle gas {f0(h['recycle_gas_Nm3_h'])} Nm3/h. Operating P and T are n/d.",
        "Hazard: toxic H2S cloud (green), H2 jet fire that is hard to see, flash fire or explosion in congested structure; high-temperature hydrogen and sulphide attack; temperature excursion if quench is lost.",
        "Not quantified: needs operating P and T, hole size, loop inventory, H2S fraction in recycle gas, wind and layout."])
    y = section(s, 1135, yy + 4, 445, "3  FCC UPSET: SLIDE VALVE / AFTERBURN")
    yy = bullets(s, 1141, y + 14, [
        f"Initiator: slide-valve erosion or loss of catalyst circulation lets hydrocarbon back-flow into the air-side regenerator, or air into the reactor; afterburn lifts regenerator gas temperature. Repo screen: the Rev B basket's pretreated VGO gives a {REF['fcc_repo']['regen_T_C']:.0f} C regenerator, below the repo's 760 C action flag; the Rev A basket gave 772 C, above it (docs/VALIDATION.md, S). A screen, not a prediction.",
        "Hazard: explosion or fire in R-302 / flue gas / C-301, internals damage, loss of containment of hot catalyst and hydrocarbon.",
        "Not quantified: needs vessel volumes and catalyst inventory; fcc_operate output is not a sizing basis."])
    y = section(s, 1135, yy + 6, 445, "KEY TO THE OVERLAYS")
    yy = bullets(s, 1141, y + 14, ["Yellow star = release point. Flames = fire. Green ellipse = toxic / flammable cloud. Red numbered circle = scenario. Red valves and dashed red lines = ESD outputs; blue circles and bubbles = detectors and transmitters (all drawn on sheet 1 and listed in the sheet 7 matrix). Tags A unless marked R."])
    y = section(s, 1135, yy + 6, 445, "CONSEQUENCE BASIS")
    bullets(s, 1141, y + 14, [
        "No distances, rates, radiation or toxic doses are given: inventories, hole sizes, operating P and T are not defined by the repo. process_safety consequence modules were not run.",
        "Standards named are pointers from the repo's OISD map (titles and editions only; texts not read, INR 10,500 each): OISD-STD-111, 133, 106, 112, 152, 241, 116, 118."])
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (qualitative; consequences not quantified)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown (R / A)", "Open data needs"),
            ("1  H-101 tube rupture", "Coil failure by coking hot spot, flame impingement, corrosion, or loss of pass flow", "Hot hydrocarbon into firebox: fireball, pool fire, flame on C-101", "FSLL-101, BE-101, AT-101A to ESD-1 (A); XV-101 fuel shut-off; XV-102 feed and XV-103 outlet isolation (A); fire water (OISD-STD-116 gap)", "Coil inventory, pass layout, tube material and skin T limit, time to isolate, distance, fire-water capacity"),
            ("2  H2/H2S release R-204", "Flange, seal or line failure on recycle gas or effluent", "Toxic H2S, H2 jet fire or flash fire, explosion in congested area", "AT-204A/B (A, leak detection preferred for H2: R EIGA 15/21); ESD-2 on TAHH-204; XV-205 H2 and XV-206 feed isolation; HV-204, PSV-204 to flare (A)", "Operating P and T, loop inventory, H2S fraction, hole sizes, toxic criteria, wind and layout"),
            ("3  FCC upset", "Slide valve erosion or jam; loss of circulation or air blower trip; afterburn", "Air-hydrocarbon mixture, explosion in R-302 / C-301, hot-catalyst loss of containment", "PDIC-301 and separate PDALL-301 (A); TAHH-302; SV-301/302, XV-301 air and XV-302 feed isolation via ESD-3 (A; FCC SIS R: SAFETY.md)", "Licensor SIS logic, vessel volumes, catalyst inventory")]
    wtable(s, 20, y, (120, 190, 200, 340, 250), rows, 9.5, 11.5, bold_first=True)
    return s


def sheet_scn_b():
    s = newsheet(5, "REFINERY Rev B: scenarios 4 and 5, loss of cooling or power to flare, floating-roof tank fire", "Scenarios 4 and 5 on the P&ID")
    frame(s, NS)
    pid(s, True)
    PL(s, [(250, 88), (1112, 88), (1112, 715), (1062, 715)], 4, RED, None, None, "none", 0.55)
    PL(s, [(798, 410), (798, 88)], 3, RED, None, None, "none", 0.55)
    PL(s, [(979, 715), (930, 715)], 4, RED, None, None, "none", 0.55)
    flame(s, 930, 605, 8, 60, 34, 0.95)
    badge(s, 1075, 690, "4")
    for (x, y, rot) in ((420, 108, 0), (750, 410, 90), (1030, 102, 0), (758, 563, 90), (262, 108, 0), (500, 103, 0), (886, 103, 0), (1010, 686, 0)):
        rv(s, x, y, rot, GREEN)
    for (x, y) in ((450, 128), (855, 508), (912, 380)):
        PL(s, [(x - 14, y - 14), (x + 14, y + 14)], 3, RED); PL(s, [(x - 14, y + 14), (x + 14, y - 14)], 3, RED)
    badge(s, 480, 104, "4")
    R(s, 22, 124, 86, 112, "none", BROWN, 1.6, "8 4")
    flame(s, 42, 140, -10, 26, 18, 0.95)
    star(s, 42, 142, 8)
    badge(s, 166, 120, "5", RED)
    T(s, 26, 247, "bund (A)", 9.5, 700, fill=BROWN)
    R(s, 790, 696, 100, 72, "none", BROWN, 1.6, "8 4")
    flame(s, 806, 702, -20, 40, 22, 0.95)
    star(s, 806, 704, 8)
    badge(s, 792, 684, "5", RED)
    T(s, 794, 764, "bund (A)", 8.5, 700, fill=BROWN)
    for (x, y) in ((70, 275), (905, 700)):
        s.add(f'<polygon points="{x-9},{y} {x+9},{y} {x},{y-14}" fill="#e3f2fd" stroke="{BLUE}" stroke-width="1.4"/>')
    T(s, 84, 289, "foam monitor (A)", 9, 700, "middle", BLUE)
    T(s, 905, 712, "foam (A)", 8.5, 700, "middle", BLUE)
    panel_box(s)
    y = section(s, 1135, 84, 445, "4  LOSS OF COOLING WATER OR POWER: RELIEF TO FLARE")
    yy = bullets(s, 1141, y + 14, [
        "Initiator: total cooling-water failure (E-103 and all condensers) or plant power failure (K-201, K-301, pumps stop). Columns lose condensing; reactors and furnaces keep releasing heat; the 14 drawn PSVs (green) lift to the flare header (red), X marks = utility lost.",
        "Hazard: simultaneous relief exceeds header or KO capacity; liquid carry-over from D-901 gives burning rain; flare radiation at grade; back pressure on relief valves; H2S in the relieved gas burns to SO2; furnaces and hot reactors need an orderly shutdown (fuel trips XV-101, XV-404; HV-204; FCC feed XV-302).",
        "Not quantified: relief loads per unit are not computed by the repo; the schedule (sheet 6) lists what each device needs. OISD-STD-106 pointer: not read."])
    y = section(s, 1135, yy + 4, 445, "5  FLOATING-ROOF TANK FIRE (T-001 CRUDE, T-801 GASOLINE)")
    yy = bullets(s, 1141, y + 14, [
        "Initiator: lightning or static ignition of vapour at the rim seal; roof sinking or tilt widens the fire to a full-surface fire. Crude fires can also develop boilover (qualitative; not verified against a source here).",
        f"Hazard: radiation on neighbouring tanks and the unit, escalation, large smoke plume with SO2 from a {REF['slate']['S']:.2f} wt% S crude, firefighting run-off.",
        "Not quantified: tank diameters, levels and spacing are n/d. Bund rule (R, HSG176 para 157 as recorded in the checklist) is on sheet 8. OISD-STD-108/129/116/118: titles only, not read."])
    y = section(s, 1135, yy + 6, 445, "KEY TO THE OVERLAYS")
    yy = bullets(s, 1141, y + 14, ["Red thick line = relief / flare header carrying the release; green glyphs = relief valves lifting; red X = utility lost. Flames on T-001 and T-801 = rim-seal fire; dashed brown box = bund; blue triangle = foam monitor. Tags A."])
    y = section(s, 1135, yy + 6, 445, "CONSEQUENCE BASIS")
    bullets(s, 1141, y + 14, [
        "No relief loads, radiation distances or fire-water demands are given. The process_safety flare module (API 521 point-source method) needs a relief rate and geometry this drawing does not have.",
        "Tank 'boilover' wording is general literature behaviour, not verified against a source here."])
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (qualitative; consequences not quantified)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown (R / A)", "Open data needs"),
            ("4  Loss of cooling or power", "Total cooling-water failure or electrical bus loss", "Relief overload of flare header and KO, liquid carry-over, radiation, back pressure, SO2", "PSV-101..PSV-901 (14 drawn) to common header (A); D-901 KO with LAHH-901 (A); FL-901 with pilot (A); HV-204 (A); fuel-gas trips via ESD-1, 2, 3, 4 (A); emergency power for instruments (A)", "Relief load per unit and simultaneous case, header and KO sizing, CW and power reliability, flare radiation limits (OISD-STD-106/109 not read)"),
            ("5  Tank fire T-001 / T-801", "Lightning, static or hot-work ignition at rim seal; sunk roof", "Rim-seal fire to full-surface fire, radiation to neighbours, boilover (crude), smoke", "Bund (A, rule R); LHD-001 and LHD-801 (A); foam monitors and rim-seal foam (A); cooling water to neighbouring shell (A); XV-001 tank-outlet isolation (A)", "Tank diameter, level, spacing, foam and water demand, fire-water supply, vapour pressure, wind")]
    wtable(s, 20, y, (140, 200, 220, 330, 210), rows, 9.5, 11.5, bold_first=True)
    return s


# ======================================================================== safety design basis (sheets 6 to 8)
def sheet_relief():
    s = newsheet(6, "REFINERY Rev B: safety design basis 1 of 3, relief schedule", "Safety design basis: relief schedule")
    frame(s, NS)
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE: every pressure vessel, column, reactor, tank and heat exchanger on sheet 1 has a device or a written reason (A = assumed here; R = named free source; gap = standard not obtained)")
    rows = [("Tag", "Item", "Design pressure basis (A)", "Relief cases", "Device", "Discharge", "Sizing status / data needed", "Mark")]
    rows += [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in RELIEF]
    y = wtable(s, 20, y, (62, 112, 128, 372, 200, 150, 406, 130), rows, 8.8, 10.4, bold_first=True)
    ndev = len([r for r in RELIEF if r[8]])
    y = WRAP(s, 22, y + 14, f"{len(RELIEF)} items: {ndev} with a drawn PSV, {len(RELIEF) - ndev} with a written reason (open path to a protected item, atmospheric floating-roof tank, package unit, or not a relief device). No item is sized: the repo gives no vessel dimensions or relief loads, and the toolkit constants for API 520/521 were not read from the standards.", 230, 9.5, 12, fill=GREY)
    y = WRAP(s, 22, y + 2, "Method pointers (toolkit, standard library): relief.gas_area / liquid_area (API 520-I isentropic derivation), relief.fire_relief_rate_kg_h (API 521 fire case; constants secondary, verify), tank_venting.thermal_venting (API 2000 5th ed., read), depressuring.py. Discharge location is a design item (R: CSB Kuraray). The design basis of the relief system is required process safety information (R: OSHA 1910.119).", 230, 9.5, 12, fill=GREY)
    return s


# cause-and-effect: initiator -> final elements. X = closes/trips, O = opens, A = alarm only, M = manual, "-" none (all logic is A)
CE_COLS = ["XV-101", "XV-102", "XV-103", "XV-205", "XV-206", "HV-204", "SV-301", "SV-302", "XV-301", "XV-302", "XV-401A/B", "XV-404", "XV-001", "FW / foam", "Alarm"]
CE_ROWS = [
    ("FSLL-101 pass flow low-low (ESD-1)", "X - - - - - - - - - - - - - A"),
    ("BE-101 flame failure (ESD-1)", "X - - - - - - - - - - - - - A"),
    ("AT-101A hydrocarbon in firebox, high-high (ESD-1)", "X X X - - - - - - - - - - - A"),
    ("TAHH-204 R-204 bed temperature (ESD-2)", "- - - - X O - - - - - - - - A"),
    ("AT-204A/B H2 / H2S, 2oo2 (ESD-2)", "- - - X X - - - - - - - - - A"),
    ("PDALL-301 reactor-regenerator dp low-low (ESD-3)", "- - - - - - X X X X - - - - A"),
    ("TAHH-302 regenerator temperature high-high (ESD-3)", "- - - - - - - - - X - - - - A"),
    ("LAHH-401A/B coke drum level high-high (ESD-4)", "- - - - - - - - - - X X - - A"),
    ("FSLL-401 coker heater pass flow low-low (ESD-4)", "- - - - - - - - - - - X - - A"),
    ("LHD-001 tank rim fire", "- - - - - - - - - - - - X X A"),
    ("LHD-801 tank rim fire", "- - - - - - - - - - - - - X A"),
    ("LAHH-901 flare KO level high-high", "- - - - - - - - - - - - - - A"),
    ("Total cooling-water failure (A)", "X - - - - - - - - X - X - - A"),
    ("Plant power failure (fail-safe positions)", "X X X X X - - - - X - X X - A"),
    ("Manual ESD push-button, control room (A)", "X X X X X O X X X X X X X X A"),
]
CE_FAIL = "C C C C C O ip ip C C ip C C - -"        # fail position: C close, O open, ip in place / per licensor (A)
SIFS = [
    ("SIF-1", "FSLL-101 (ESD-1)", "XV-101 fuel gas", "Trip burners on low pass flow", "2", "Coil coking, pump trip, blocked pass; no frequency data read", "TIC-101 (separate control loop); alarm, little credit alone; PSV-101 (not an IPL for coil rupture)", "S2 separation; S10 furnace SIS credited but failed"),
    ("SIF-2", "BE-101 (ESD-1)", "XV-101", "Trip burners on flame loss", "2", "Burner flame loss, fuel-gas upset (A)", "BMS permissives (A); alarm", "S2"),
    ("SIF-3", "AT-101A (ESD-1)", "XV-101, XV-102, XV-103", "Isolate heater on hydrocarbon in firebox", "1", "Tube leak or rupture (A)", "fire water (gap OISD-STD-116); operator response not credited (S10)", "S2, S10"),
    ("SIF-4", "TAHH-204 (ESD-2)", "XV-206 feed, HV-204 depressure", "Stop feed, depressure on bed temperature high-high", "2", "Loss of quench, maldistribution, exotherm (A)", "quench gas, TIC alarm, PSV-204", "S2; licensor logic gap"),
    ("SIF-5", "AT-204A/B 2oo2 (ESD-2)", "XV-205 H2, XV-206 feed", "Isolate loop on confirmed gas release", "1", "Flange or seal leak (A)", "ventilation (open structure, A); alarm", "S4 EIGA: gas leak detection preferred for H2"),
    ("SIF-6", "PDALL-301 (ESD-3)", "SV-301/302, XV-301, XV-302", "Prevent back-flow between reactor and regenerator", "2", "Slide-valve erosion, jam, air blower trip (A)", "PDIC-301 (control); operator alarm", "repo docs/SAFETY.md (R); OISD-STD-152/153 gap"),
    ("SIF-7", "TAHH-302 (ESD-3)", "XV-302 feed", "Cut feed on afterburn temperature", "2", "Air/coke imbalance (A)", "regeneration air control; alarm", "licensor logic gap"),
    ("SIF-8", "LAHH-401A/B (ESD-4)", "XV-401A/B, XV-404", "Stop feed and firing on drum high-high level", "2", "Switching error, foam-over (A)", "operator procedure (limited credit, S10); PSV-402A/B", "S5 (PSM); S10"),
    ("SIF-9", "FSLL-401 (ESD-4)", "XV-404", "Trip coker heater on low pass flow", "2", "Pump trip, coil coking (A)", "alarm; TIC (A)", "S2"),
]


def sheet_ce():
    s = newsheet(7, "REFINERY Rev B: safety design basis 2 of 3, ESD cause-and-effect matrix and SIF list", "Safety design basis: ESD matrix, SIFs")
    frame(s, NS)
    y = section(s, 20, 84, 1100, "ESD CAUSE-AND-EFFECT MATRIX (X trips/closes, O opens; all tags drawn on sheet 1; logic is A, to be set by the licensor and a LOPA)")
    x0, lw, cw, rh = 20, 322, 51.5, 17
    R(s, x0, y, lw + cw * len(CE_COLS), 30, "#e8eaf0", "none")
    T(s, x0 + 4, y + 20, "Initiator (cause)", 10, 700)
    for j, c in enumerate(CE_COLS):
        if c == "FW / foam":
            a, b = c.split("/", 1) if c != "FW / foam" else ("FW /", "foam")
            T(s, x0 + lw + cw * j + cw / 2, y + 13, a, 9, 700, "middle"); T(s, x0 + lw + cw * j + cw / 2, y + 25, b, 9, 700, "middle")
        else:
            T(s, x0 + lw + cw * j + cw / 2, y + 20, c, 9, 700, "middle")
    yy = y + 30
    for i, (lab, cells) in enumerate(CE_ROWS):
        cs = cells.split()
        assert len(cs) == len(CE_COLS), lab
        if i % 2 == 0: R(s, x0, yy, lw + cw * len(CE_COLS), rh, "#f6f7fa", "none")
        T(s, x0 + 4, yy + 12.5, lab, 9.5)
        for j, c in enumerate(cs):
            if c != "-": T(s, x0 + lw + cw * j + cw / 2, yy + 12.5, c, 10, 700, "middle", RED if c in "XO" else GREY)
        yy += rh
    # fail position row
    fs = CE_FAIL.split()
    R(s, x0, yy, lw + cw * len(CE_COLS), rh, "#fff3e0", "none")
    T(s, x0 + 4, yy + 12.5, "Fail position on loss of air or power (A): C close, O open, ip in place", 9.5, 700)
    for j, c in enumerate(fs): T(s, x0 + lw + cw * j + cw / 2, yy + 12.5, c, 9.5, 700, "middle")
    yy += rh
    R(s, x0, y, lw + cw * len(CE_COLS), yy - y, "none", "#9aa", 1)
    for j in range(len(CE_COLS) + 1): PL(s, [(x0 + lw + cw * j, y), (x0 + lw + cw * j, yy)], 0.5, "#ccd")
    yy = WRAP(s, 22, yy + 14, "Notes: ESD-1 heater BMS, ESD-2 hydroprocessing, ESD-3 FCC SIS (R: SAFETY.md), ESD-4 delayed coker (A). XV-302 (FCC feed) and XV-001 (T-001 outlet, remote operated) are new on sheet 1 in Rev B. HV-204 is not opened on gas detection alone (a large release may justify it: licensor and HAZOP decision). Closing both XV-102 and XV-103 can trap hot crude in the coil: relief path via PSV-101 must stay open (schedule, sheet 6). Fail positions are A: SV-301/302 and XV-301 move per licensor logic with backup power. LAHH-901 is alarm only, no SIF credit. Alarm flood: BP-Husky (S10) recorded 3,712 alarms in the period reviewed; an alarm philosophy and rationalisation are required, not drawn (gap).", 190, 9.5, 12)
    y2 = section(s, 20, yy + 8, 1560, "SAFETY INSTRUMENTED FUNCTIONS: SIL TARGET IS ASSUMED (A). No LOPA was done and no SIL verification is claimed (IEC 61511 and CCPS LOPA texts not obtained)")
    rows = [("SIF", "Initiator", "Final element", "Function", "SIL (A)", "Demand source", "Independent layers credited", "Free source")] + [r for r in SIFS]
    rows.append(("F&G", "LHD-001, LHD-801", "foam / water, XV-001", "Fire protection, not a SIF", "n/a", "Rim-seal fire (A)", "bund, foam; detection layer", "S1 para 128 ROSOV; foam/water: gap OISD-STD-116"))
    wtable(s, 20, y2, (48, 150, 170, 270, 52, 280, 370, 220), rows, 9, 10.6, bold_first=True)
    return s


HAZ = [
    ("N1 H-101 crude heater", "No / low flow in a pass", "Pump trip, coking, valve closed", "Tube overheating, rupture, firebox fire", "FSLL-101, BE-101, TIC-101, AT-101A, ESD-1 / XV-101, XV-102/103 (A)", "LOPA for SIL; tube skin temperature; metallurgy for TAN 0.87 and 2.26 wt% S"),
    ("N2 C-101 / E-103 / D-102", "No cooling (cooling-water or power loss)", "CW pump trip, bus loss", "Overpressure, relief to flare", "PSV-101, PSV-104, flare (A)", "Relief load for CW and power failure; CW trip independence"),
    ("N3 C-102 / H-102", "Air ingress, loss of vacuum", "Ejector failure, leak, steam loss", "Flammable mixture with hot residue; collapse", "PSV-102, nitrogen admission (A)", "Vacuum collapse check; oxygen control"),
    ("N4 R-204 loop", "More temperature", "Loss of quench or cooling, maldistribution", "Runaway, hot spot, vessel damage, release", "TAHH-204 -> ESD-2 -> HV-204, PSV-204", "Quench logic; depressuring rate; high-temperature hydrogen attack check (gap: API 941)"),
    ("N5 R-201..204 loops", "Leak of H2 / H2S", "Flange or seal failure", "Toxic cloud, jet fire (flame hard to see), explosion", "AT-204A/B, XV-205/206 (A); vent design per EIGA 15/21 (R)", "H2S exposure protection; vent location and distances"),
    ("N6 FCC R-301 / R-302", "Reverse flow, low differential pressure", "Slide-valve erosion or jam, air blower trip", "Air-hydrocarbon mixture, explosion, afterburn", "PDIC/PDALL-301, SV-301/302, XV-301/302, TAHH-302", "Licensor SIS logic; regenerator temperature screen (757 C, flag 760 C)"),
    ("N7 D-401A/B coke drums", "Wrong switch, overfill, foam-over", "Switching-valve error, early steam or quench", "Hot oil or steam release at drum top or bottom, fire", "LAHH-401A/B, XV-401A/B, XV-404, PSV-402A/B (A)", "Position interlock on switching valves; blowdown D-402; unheading and personnel exclusion"),
    ("N8 D-901 / FL-901", "Liquid carry-over, loss of power", "Simultaneous relief, KO pump trip", "Burning rain, radiation at grade, back pressure", "LAHH-901, pilot, emergency power (A)", "Simultaneous case, radiation limits, flare-tip purge"),
    ("N9 T-001 / T-801", "Ignition at seal, overfill", "Lightning, static, no independent level trip", "Rim fire to full-surface fire, boilover (crude)", "LHD-001/801, foam, bund, XV-001 (A)", "Independent high-high level (not drawn: gap); bund volume"),
]


def sheet_mitig():
    s = newsheet(8, "REFINERY Rev B: safety design basis 3 of 3, detection, hazard identification, safer design, gaps", "Safety design basis: mitigation, HAZOP, ISD, gaps")
    frame(s, NS)
    y = section(s, 20, 84, 1100, "HAZARD IDENTIFICATION: nine nodes, qualitative (no consequence numbers; PHA with facility siting required, R: OSHA 1910.119)")
    rows = [("Node", "Deviation", "Cause", "Consequence", "Safeguard (tags on sheet 1)", "Action")] + HAZ
    y = wtable(s, 20, y, (120, 120, 150, 190, 270, 250), rows, 9, 10.6, bold_first=True)
    y = section(s, 20, y + 8, 1100, "INHERENTLY SAFER DESIGN NOTES")
    isd = [("Minimise hydrogen and H2S inventory: small HP separators and short HP lines; remote isolation XV-205/206 at the loop boundary", "R S1 para 128 (ROSOV concept) / A"),
           ("Moderate conditions: liquid or gas quench between beds to hold the R-204 rise down; more heater passes and steam injection to lower coil skin temperature", "A"),
           ("Substitute procedure: remote, automated coke-drum switching with position interlock and automated unheading in place of manual valves", "A"),
           ("Simplify: avoid block valves between a heater coil and its PSV path; fewer manual bypasses on ESD valves", "A (S2: keep protection separate from control)"),
           ("Choose the slate: lower TAN and S reduce heater and column corrosion (Rev B TAN 0.87 vs 0.55 in Rev A: a check on materials)", "D from sheet 2 / A"),
           ("Layout: separate flare KO, tanks and the H2 plant from heaters and occupied buildings; address domino escalation", "R S3 HSE COMAH layout; R S4 EIGA Table 1: 5 m to ignition sources / openings, 8 m to boundary (H2 installations)")]
    y = wtable(s, 20, y, (760, 340), [("Option", "Source / mark")] + isd, 9, 10.6)
    # right column
    x2 = 1140
    y2 = section(s, x2, 84, 440, "DETECTION AND MITIGATION BASIS")
    items = ["Gas detection: hydrocarbon at the H-101 firebox and air intakes (AT-101A); H2/H2S at the R-204 loop (AT-204A/B). For hydrogen, leak (gas or acoustic) detection supplements flame detection because the flame is hard to see (R: EIGA 15/21). Placement by release height and wind needs layout: A.",
             "Flame: burner scanners (BE-101); linear heat detection on floating-roof rims (LHD-001/801), A.",
             "Isolation of large inventories: ROSOVs XV-102/103/205/206/301/302/001 are remote operated and fail safe (R: HSG176 para 128).",
             "Bund: 110 % of the largest vessel, or 25 % of total capacity (HSG176 para 157 as recorded in the checklist; which governs not re-read). Tank volumes n/d, so volume is not computed.",
             "Distances: HSG176 Table 1 covers small tanks only (1 to 15 m), so refinery tanks need a consequence-based study: gap OISD-STD-118. Hydrogen vent/equipment distances from EIGA Table 1 as above.",
             "Fire water and foam: no free source obtained; demand arithmetic exists (fire_water.py) but needs areas and densities: gap OISD-STD-116/117.",
             "Ventilation and inerting: open structure for the H2 loop (A); nitrogen blanket for C-102; steam-out of coke drums to blowdown (A)."]
    yy = y2 + 12
    for t in items: yy = WRAP(s, x2 + 4, yy, t, 78, 9.5, 11.8, bullet=True) + 3
    y3 = section(s, x2, yy + 6, 440, "GAPS: STANDARDS NOT OBTAINED (recorded, not read)")
    gaps = [("OISD-STD-106, 108, 111, 112, 116/117, 118, 129, 133, 152/153, 163, 164, 241", "INR 10,500 each plus registration: not bought"),
            ("API 520/521/526/2000/650/2510/941", "reading room needs registration"),
            ("IEC 61511 / 61508, CCPS LOPA", "paywalled; SIL stays A"),
            ("NFPA 30, 58, 59A; BIS codes; PESO SMPV(U) 2016", "not obtained / host unreachable")]
    wtable(s, x2, y3, (230, 210), [("Standard", "Status")] + gaps, 9, 10.6)
    return s


def build_all():
    return [sheet_pid(), sheet_hmb(), sheet_hmb2(), sheet_scn_a(), sheet_scn_b(), sheet_relief(), sheet_ce(), sheet_mitig()]


def lint(sheets):
    """tags vs drawing, stream diamonds vs HMB columns, relief coverage"""
    txt = {sh.no: " ".join(sh.p) for sh in sheets}
    t1 = txt[1]
    def expand(tok):
        m = re.match(r"^([A-Z]{2,6}-)(\d{3})([A-Z]?)((?:/[A-Z0-9]+)*)$", tok)
        if not m: return [tok]
        pre, n, suf, rest = m.groups()
        out = [pre + n + suf]
        for part in rest.split("/")[1:]:
            out.append(pre + part if part.isdigit() else pre + n + part)
        return out
    pat = re.compile(r"\b(?:XV|HV|PSV|TSV|ESD|AT|BE|FSLL|TAHH|PDIC|PDALL|LHD|LAHH|SV|TIC)-\d{3}[A-Z]?(?:/[A-Z0-9]+)*")
    miss = set()
    for no in (4, 5, 6, 7, 8):
        plain = re.sub(r"<[^>]+>", " ", txt[no])
        for tok in pat.findall(plain):
            for tg in expand(tok):
                base = re.sub(r"[A-Z]$", "", tg)
                p1 = re.sub(r"<[^>]+>", " ", t1); p1 = re.sub(r"\s+", " ", p1)
                if not any(x in p1 or x.replace("-", " ") in p1 for x in (tg, base + "A/B", base + "A", base)):
                    miss.add(tg)
    diam = set(int(x) for x in re.findall(r'font-weight="700" text-anchor="middle" fill="[^"]+" >(\d{1,2})</text>', t1))
    hmb = set(r[0] for r in C["rows"])
    dr = [d for d in DRAWN_DEVICES if d not in re.sub(r"<[^>]+>", " ", t1)]
    nodev = [r[0] for r in RELIEF if not r[8] and ("none" not in r[4].lower() and "no psv" not in r[4].lower() and "package" not in r[4].lower() and "not a relief" not in r[4].lower() and "protected" not in r[4].lower() and not r[4].lower().startswith("as e-"))]
    print("lint: tags named on sheets 4-8 but absent from sheet 1:", sorted(miss) or "none")
    print("lint: stream numbers in HMB:", len(hmb), "; diamonds on sheet 1 not in HMB:", sorted(diam - hmb) or "none", "; HMB without diamond:", sorted(hmb - diam) or "none")
    print("lint: relief devices not drawn on sheet 1:", dr or "none", "; items without device or written reason:", nodev or "none", "; schedule rows:", len(RELIEF))
    return miss, dr


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, "Refinery P&ID set Rev B", previews="--previews" in sys.argv)
    lint(sheets)
    print("ok", len(sheets), "closure error %.4f %%" % C["err"], "S error %.4f %%" % C["s_err"])
