"""Pressurised liquefied-gas leak: source term, droplet and rain-out, jet fire and pool fire in one JSON-driven study.

    python -m process_safety tool lgrelease input.json --out dir

Sources (all read; docs/SOURCE_TERM_SOURCES.md): TNO Yellow Book CPR 14E (2005) ch. 2 spray release, ch. 6 pool fire and its Annex property data
(`yb_spray`, `yb_poolfire`, `yb_annex`); Dutch Purple Book (`vulnerability`); omega discharge (`flash_release`, with ISO 4126-10 limits quoted
by Melhem 2023); Chamberlain jet flame from the DNV jet-fire theory report (`jet_flame`) with a line-source flux map (`jet_radiation`);
Webber-form pool spreading as quoted by Basha 2013 (`pool_spread`).

Fluids: propane and n-butane only, because their property correlations are transcribed from the Yellow Book Annex (add a fluid there first).
Discharge bases for a saturated liquid (mode 'saturated'): 'omega' (HEM-type, choked) and 'yellow_book_liquid' (the book's liquid-orifice route:
hole in the liquid space, exit at vessel conditions, flashing after the exit); both are always computed and the chosen one drives the fires.
Mode 'refrigerated': liquid at its atmospheric boiling point driven by head and overpressure, no flash.
Not modelled: horizontal jets, jet impingement, pool-fire flame drag, ground heat to the pool, droplet break-up at free-fall speed.
"""
from __future__ import annotations

import math

from . import droplet, flash_release, ignition_ukooa, release_frequency, fluiddata, jet_flame, jet_radiation, pool_spread, release, viewfactor, vulnerability, yb_annex, yb_poolfire, yb_spray
from .constants import R

REQUIRED = {"ambient": ["P_kPa", "T_K", "wind_m_s"], "fire": ["release_height_m", "target_height_m", "tau"], "pool": ["C_T", "r0_m", "h0_m"]}


def check(data: dict) -> list[str]:
    errs = []
    for k in ("fluid", "mode", "hole_d_m", "Cd"):
        if k not in data:
            errs.append(f"missing '{k}'")
    if data.get("fluid") not in yb_annex.DATA:
        errs.append(f"fluid must be one of {sorted(yb_annex.DATA)} (Yellow Book Annex data)")
    for sec, keys in REQUIRED.items():
        if sec not in data:
            errs.append(f"missing section '{sec}'")
            continue
        errs += [f"missing {sec}.{k}" for k in keys if k not in data[sec]]
    mode = data.get("mode")
    if mode == "saturated" and "P0_kPa" not in data:
        errs.append("mode 'saturated' needs P0_kPa")
    if mode == "refrigerated" and not all(k in data for k in ("overpressure_kPa_g", "head_m")):
        errs.append("mode 'refrigerated' needs overpressure_kPa_g and head_m")
    if mode not in ("saturated", "refrigerated"):
        errs.append("mode must be 'saturated' or 'refrigerated'")
    if data.get("discharge_basis", "omega") not in ("omega", "yellow_book_liquid"):
        errs.append("discharge_basis must be 'omega' or 'yellow_book_liquid'")
    fq = data.get("frequency")
    if fq is not None:
        if fq.get("sheet") not in release_frequency.equipment_types():
            errs.append(f"frequency.sheet must be one of {sorted(release_frequency.equipment_types())} (IOGP 434-01 datasheet number)")
        if not (fq.get("D_mm", 0) > 0 and fq.get("count", 1) > 0):
            errs.append("frequency.D_mm and frequency.count must be positive")
        if fq.get("period", "2006-2015") not in release_frequency.PERIODS:
            errs.append(f"frequency.period must be one of {release_frequency.PERIODS}")
    if data.get("fire", {}).get("probit", "hydrocarbon") not in vulnerability.PROBIT_INTERCEPT:
        errs.append("fire.probit must be 'hydrocarbon' (default), 'eisenberg' or 'lees'")
    if data.get("fire", {}).get("release_angle_deg", 90) != 90:
        errs.append("only a vertical release (release_angle_deg = 90) is implemented for the jet flux map")
    return errs


def _jet_state_omega(rel):
    """Jet state after the ATEX-style expansion from the omega choke state, in the keys the Yellow Book steps use."""
    return {"u_f_m_s": rel["u_f_m_s"], "Phi_f": rel["x_vapour"], "rho_f_kg_m3": rel["rho_f_kg_m3"], "A_f_m2": rel["A_f_m2"], "b_f_m": math.sqrt(rel["A_f_m2"] / math.pi),
            "u_e_m_s": rel["u_choke_m_s"], "rho_e_kg_m3": rel["rho_choke_kg_m3"]}


def _yb_liquid(fl, data, T0, P0_Pa, Pa_Pa, Tb):
    """Yellow Book route: liquid orifice at vessel conditions, then flashing (steps 1)."""
    A = math.pi * data["hole_d_m"] ** 2 / 4
    rho_L = yb_annex.liquid_density_kg_m3(fl, T0)
    q = data["Cd"] * A * math.sqrt(2.0 * rho_L * (P0_Pa - Pa_Pa))
    Ae = data["Cd"] * A
    M = yb_annex.molar_mass_kg_mol(fl)
    Lv_e, Lv_f = yb_annex.heat_of_vaporisation_J_kg(fl, T0), yb_annex.heat_of_vaporisation_J_kg(fl, Tb)
    dHv = Lv_f - Lv_e - yb_annex.liquid_enthalpy_change_J_kg(fl, Tb, T0)          # H_V,f - H_V,e from the liquid-side balance (docs)
    jet = yb_spray.jet_after_flash(q, Ae, P0_Pa, Pa_Pa, 0.0, rho_L, P0_Pa * M / (R * T0), dHv, Lv_e, Lv_f, yb_annex.liquid_density_kg_m3(fl, Tb), Pa_Pa * M / (R * Tb))
    return q, jet


def run(data: dict) -> dict:
    amb, fire, pool = data["ambient"], data["fire"], data["pool"]
    fl = data["fluid"]
    Pa = amb["P_kPa"] * 1000.0
    Ta = amb["T_K"]
    M = yb_annex.molar_mass_kg_mol(fl)
    Tb = yb_annex.normal_boiling_point_K(fl)
    rho_a = Pa * yb_annex.AIR["M_kg_kmol"] / 1000.0 / (R * Ta)
    nu_a = amb.get("nu_air_m2_s", yb_annex.AIR["nu_288K_m2_s"])
    Sc, Pr = amb.get("Sc", 0.7), yb_annex.AIR["Pr"]
    lam = yb_annex.air_conductivity_W_mK()
    area = math.pi * data["hole_d_m"] ** 2 / 4
    Hc = fire.get("Hc_J_kg", yb_annex.net_heat_of_combustion_J_kg(fl))
    out = {"mode": data["mode"], "warnings": [], "notes": []}
    superheated = data["mode"] == "saturated"
    basis = data.get("discharge_basis", "omega")

    if superheated:
        P0 = data["P0_kPa"] * 1000.0
        T0 = yb_annex.saturation_temperature_K(fl, P0)
        s0 = fluiddata.at_pressure(fl if fl in fluiddata.names() else "propane", data["P0_kPa"])
        omega = s0["omega_saturated"]
        const = fluiddata.fluid_constants(fl)
        out["warnings"] += flash_release.iso4126_10_check(T0, const["Tc_K"], data["P0_kPa"], const["Pc_kPa"], omega)
        cp_mean = yb_annex.liquid_enthalpy_change_J_kg(fl, Tb, T0) / (T0 - Tb)
        rho0 = yb_annex.liquid_density_kg_m3(fl, T0)
        hfg_b = yb_annex.heat_of_vaporisation_J_kg(fl, Tb)
        rel = flash_release.saturated_liquid_release(data["P0_kPa"], rho0, omega, area, data["Cd"], T0, Tb, cp_mean, hfg_b, yb_annex.liquid_density_kg_m3(fl, Tb), Pa * M / (R * Tb), amb["P_kPa"])
        q_yb, jet_yb = _yb_liquid(fl, data, T0, P0, Pa, Tb)
        jet_om = _jet_state_omega(rel)
        out["discharge"] = {"omega": {"W_kg_s": rel["W_kg_s"], "u_f_m_s": jet_om["u_f_m_s"], "Phi_f": jet_om["Phi_f"], "omega": omega, "eta_c": rel["eta_c"], "T0_K": T0},
                            "yellow_book_liquid": {"W_kg_s": q_yb, "u_f_m_s": jet_yb["u_f_m_s"], "Phi_f": jet_yb["Phi_f"]}, "basis_used": basis}
        W, jet = (rel["W_kg_s"], jet_om) if basis == "omega" else (q_yb, jet_yb)
        out["release"] = {**rel, "T0_K": T0, "basis": basis, "W_used_kg_s": W}
        out["notes"].append("The two discharge bases differ by a large factor for a saturated liquid; the Yellow Book treats a hole in the liquid space as liquid outflow, the omega method as flashing choked flow. Treat them as a bracket.")
        orifice_kPa = data["P0_kPa"]
    else:
        T0 = data.get("T0_K", Tb)
        dP = data["overpressure_kPa_g"] * 1000.0
        rho_L0 = yb_annex.liquid_density_kg_m3(fl, Tb)
        W = release.liquid_release_kg_s(data["hole_d_m"], rho_L0, dP, data["head_m"], data["Cd"])
        u = math.sqrt(2.0 * (dP + rho_L0 * 9.80665 * data["head_m"]) / rho_L0)
        Ae = data["Cd"] * area
        jet = {"u_f_m_s": u, "Phi_f": 0.0, "b_f_m": math.sqrt(Ae / math.pi), "u_e_m_s": u, "rho_f_kg_m3": rho_L0, "A_f_m2": Ae}
        out["release"] = {"W_kg_s": W, "W_used_kg_s": W, "u_f_m_s": u, "regime": "liquid Bernoulli (no flash)", "x_vapour": 0.0, "T0_K": T0}
        out["notes"].append("Refrigerated/subcooled liquid: Bernoulli head-driven flow, jet leaves at ambient pressure; no flash, no jet fire from the liquid.")
        orifice_kPa = amb["P_kPa"] + data["overpressure_kPa_g"]

    # --- Yellow Book steps 2 and 3: droplet diameter and rain-out
    rho_Lf = yb_annex.liquid_density_kg_m3(fl, Tb)
    nu_L = yb_annex.liquid_viscosity_Pa_s(fl, Tb) / rho_Lf
    sigma = yb_annex.surface_tension_N_m(fl, Tb)
    dd = yb_spray.droplet_diameter_m(jet["b_f_m"], jet["u_f_m_s"], nu_L, rho_Lf, sigma, rho_a, T0, Tb, data.get("C_ds", yb_spray.C_DS_RECOMMENDED))
    D = nu_a / Sc
    kB_func = lambda T: yb_spray.k_B_m2_s(M, D, Pa, rho_Lf, Ta, yb_annex.vapour_pressure_Pa(fl, T))
    ud = yb_spray.free_fall_velocity_m_s(dd["d_d_m"], rho_Lf, nu_a, rho_a)
    Re_d = ud * dd["d_d_m"] / nu_a
    lo_T = max(yb_annex.DATA[fl]["vp"][1][0], yb_annex.DATA[fl]["hv"][1][0]) + 1.0
    Td, kB = yb_spray.droplet_temperature_K(Ta, Re_d, Sc, Pr, lam, lambda T: yb_annex.heat_of_vaporisation_J_kg(fl, T), rho_Lf, kB_func, T_low_K=lo_T)
    hs = fire["release_height_m"]
    rain = yb_spray.rainout(jet=jet, d_d_m=dd["d_d_m"], q_kg_s=W, h_s_m=hs, kB=kB, Sc=Sc, rho_L_f=rho_Lf, rho_a=rho_a, nu_a=nu_a)
    xH = droplet.isenthalpic_flash_fraction(yb_annex.liquid_enthalpy_change_J_kg(fl, Tb, T0) / (T0 - Tb) if T0 > Tb else 1.0, T0, Tb, yb_annex.heat_of_vaporisation_J_kg(fl, Tb))
    out["droplet"] = {**dd, "T_droplet_K": Td, "k_B_m2_s": kB, **{k: rain[k] for k in ("u_d_m_s", "Re_d", "d_M_m", "formula_applicable_d_M", "d_ground_m", "rainout_kg_s", "rainout_fraction_of_release", "q_nett_air_kg_s")},
                      "Phi_f": jet["Phi_f"], "kletz_comparison": droplet.rainout_kletz(xH, not superheated), "lautkaski_comparison": droplet.rainout_lautkaski(xH),
                      "validity_warnings": droplet.validity_warnings(data["hole_d_m"] * 1000.0, orifice_kPa, hs, False),
                      "notes": [rain["breakup_flag"], "Kletz and Lautkaski (DNV report, simple correlations) are shown only for comparison with the Yellow Book method."]}
    out["warnings"] += ["Kletz/Lautkaski comparison: " + w for w in out["droplet"]["validity_warnings"]]
    f_rain = rain["rainout_fraction_of_release"]

    # --- jet fire on the airborne part
    if superheated:
        # Default: DNV JFSH-Cook liquid / two-phase jet fire (Jet Fire Theory, Dec 2023): source diameter eq 58, Cook radiant fraction eq 33, Cook base width eq 26,
        # flammable mass eq 59 m = Md min(1, 3 (1 - rain-out)). fire.model = "chamberlain_vapour" restores the pure-vapour treatment (eq 3, eq 32, eq 25, all airborne).
        fmodel = fire.get("model", "dnv_cook")
        if fmodel not in ("dnv_cook", "chamberlain_vapour"):
            raise ValueError("fire.model must be 'dnv_cook' or 'chamberlain_vapour'")
        cook = fmodel == "dnv_cook"
        m_jet = W * min(1.0, fire.get("jet_mass_parameter", 3.0) * (1.0 - f_rain)) if cook else rain["q_nett_air_kg_s"]
        use_58 = fire.get("dnv_two_phase_source_diameter", cook)
        rho_vap = Pa * M / (R * Tb) if use_58 else None
        j = jet_flame.chamberlain(m_jet, jet["rho_f_kg_m3"], rho_a, M * 1000.0, Hc, amb["wind_m_s"], 90.0, v_j_m_s=jet["u_f_m_s"],
                                  fs_model=fire.get("fs_model", "cook" if cook else "chamberlain"), rho_vap_kg_m3=rho_vap,
                                  w1_model="cook" if cook else "chamberlain")
        zr, zt, tau = fire["release_height_m"], fire["target_height_m"], fire["tau"]
        t_exp = fire.get("exposure_time_s", vulnerability.MAX_EXPOSURE_S)
        pv = fire.get("probit", "hydrocarbon")
        levels = {"P_death_1pct": vulnerability.flux_for_probability_kW_m2(0.01, t_exp, pv), "P_death_50pct": vulnerability.flux_for_probability_kW_m2(0.5, t_exp, pv),
                  "building_or_clothing_ignition": vulnerability.BUILDING_IGNITION_KW_M2}
        levels.update({f"TDU_{k}": vulnerability.flux_for_thermal_dose_kW_m2(v, t_exp) for k, v in vulnerability.THERMAL_DOSE_CRITERIA.items()})
        levels.update({f"IAEA_{x}": x for x in vulnerability.IAEA_EFFECT_LEVELS_KW_M2 if x != vulnerability.BUILDING_IGNITION_KW_M2})
        levels.update({f"user_{x}": x for x in fire.get("extra_flux_levels_kW_m2", [])})
        reach = {k: {"flux_kW_m2": v, **{d: jet_radiation.reach_m(j, zr, v, d, zt, tau) for d in ("downwind", "upwind", "crosswind")}} for k, v in levels.items()}
        grid = [{"x_m": xx, **{f"y{yy}": jet_radiation.flux_kW_m2(j, zr, xx, yy, zt, tau) for yy in (0, 10, 20, 30, 40)}} for xx in (-30, -20, -10, 0, 10, 20, 30, 40, 60, 80)]
        out["jet"] = {"m_airborne_kg_s": m_jet, "flame": {k: j[k] for k in ("Ds_m", "L_B0_m", "L_B_m", "alpha_deg", "B_m", "R_L_m", "W1_m", "W2_m", "area_m2", "F_s", "radiated_power_kW", "SEP_kW_m2")},
                      "exposure_time_s": t_exp, "reach_m": reach, "flux_grid_kW_m2": grid, "near_field_radius_m": jet_radiation.near_field_radius_m(j),
                      "model": fmodel, "notes": j["notes"] + ["Flame: " + ("DNV JFSH-Cook liquid / two-phase model (eq 58, 33, 26, 59)" if cook else "pure-vapour Chamberlain model (eq 3, 32, 25)") + "; line-source flux map, vertical release only."]}
    else:
        out["jet"] = None

    # --- pool fire on the rained-out part (Yellow Book chapter 6)
    out["pool"] = []
    m_inf, kbeta = yb_poolfire.LARGE_POOL[fl]
    cases = [f_rain] if f_rain > 1e-6 else []
    cases += [c for c in pool.get("extra_rainout_fractions", []) if c > 0]
    for fr in sorted(set(cases)):
        mr = fr * W
        Deq = yb_poolfire.equilibrium_diameter_m(mr, m_inf, kbeta)
        mflux = yb_poolfire.burning_flux_kg_m2_s(Deq, m_inf, kbeta)
        fl_len = yb_poolfire.flame_length_m(Deq, mflux, rho_a, amb["wind_m_s"])
        sep = 140.0 * math.exp(-0.12 * Deq) + 20.0 * (1.0 - math.exp(-0.12 * Deq))      # Yellow Book (6.19): c3 140, c4 20 kW/m2, c5 0.12 1/m
        sp = pool_spread.spread(mr, rho_Lf, rho_a, mflux, pool["r0_m"], pool["h0_m"], pool["C_T"])
        pf = {"diameter_m": Deq, "flame_height_m": fl_len["L_m"], "sep_mudan_croce_kW_m2": sep, "tau": fire["tau"]}
        t_exp = fire.get("exposure_time_s", vulnerability.MAX_EXPOSURE_S)
        pv = fire.get("probit", "hydrocarbon")
        reach = {k: {"flux_kW_m2": v, "solid_flame_m": _solid_flame_reach(pf, v)} for k, v in
                 {"P_death_1pct": vulnerability.flux_for_probability_kW_m2(0.01, t_exp, pv), "P_death_50pct": vulnerability.flux_for_probability_kW_m2(0.5, t_exp, pv),
                  "building_or_clothing_ignition": vulnerability.BUILDING_IGNITION_KW_M2}.items()}
        out["pool"].append({"rainout_fraction": fr, "from_yellow_book_method": abs(fr - f_rain) < 1e-12, "feed_kg_s": mr, "D_eq_m": Deq, "A_eq_m2": math.pi * Deq ** 2 / 4,
                            "burning_flux_kg_m2_s": mflux, "flame_length_m": fl_len["L_m"], "flame_tilt_deg": yb_poolfire.flame_tilt_deg(Deq, amb["wind_m_s"], nu_a),
                            "heat_release_MW": mflux * math.pi * Deq ** 2 / 4 * Hc / 1e6, "SEP_kW_m2": sep, "t_to_equilibrium_s": sp["t_to_equilibrium_s"],
                            "spread_samples": sp["samples"], "reach": reach})
    if not out["pool"]:
        out["notes"].append("Yellow Book rain-out is zero: no pool fire evaluated. Add pool.extra_rainout_fractions to test a hypothesis (for example ground impingement).")
    # --- ignition: three published models, reported side by side (they differ by more than an order of magnitude)
    from .qra import frequency as _qf
    ig = data.get("ignition", {})
    uk = {ignition_ukooa.case_names()[c]: ignition_ukooa.ignition_probability(W, c) for c in ig.get("ukooa_cases", [3, 5, 8])}
    out["ignition"] = {"purple_book_direct_ignition": vulnerability.direct_ignition_probability(W, vulnerability.REACTIVITY[fl]), "substance_class": vulnerability.REACTIVITY[fl],
                       "ukooa_total_ignition": uk, "cox_lees_ang_total_ignition": _qf.cox_ignition(W, "gas"), "immediate_ignition_probability_ukooa": ignition_ukooa.IMMEDIATE_IGNITION_PROBABILITY,
                       "note": ("Purple Book Table 4.5 is DIRECT ignition only; the UKOOA/Energy Institute curves (IChemE Hazards XXIII Table 2) and Cox, Lees and Ang are TOTAL "
                                "(immediate plus delayed). The spread between the models is part of the uncertainty of the event tree; choose the curve for the facility type.")}
    # --- release frequency (IOGP 434-01) and the frequency of the resulting jet fire
    fq = data.get("frequency")
    if fq:
        sheet, D_mm, count, period = fq["sheet"], fq["D_mm"], fq.get("count", 1.0), fq.get("period", "2006-2015")
        hole_mm = data["hole_d_m"] * 1000.0
        classes = release_frequency.leak_frequency(sheet, D_mm, count, period)
        idx = release_frequency.hole_class(hole_mm)
        f_class = next((c["frequency_per_year"] for c in classes if c["hole_range_mm"] == release_frequency.HOLE_CLASSES[idx]), 0.0)
        ign = out["ignition"]
        pmap = {**{f"UKOOA {k} (total)": v for k, v in ign["ukooa_total_ignition"].items()}, "Cox, Lees and Ang (total)": ign["cox_lees_ang_total_ignition"]}
        out["frequency"] = {"equipment": release_frequency.equipment_types()[sheet], "D_mm": D_mm, "count": count, "period": period, "study_hole_mm": hole_mm,
                            "hole_class_mm": release_frequency.HOLE_CLASSES[idx], "frequency_of_hole_class_per_year": f_class, "all_classes": classes,
                            "jet_fire_frequency_per_year": {k: f_class * v for k, v in pmap.items()},
                            "notes": ["IOGP 434-01 hole classes: the class frequency covers every hole in its range, so it is the frequency of releases of about the study hole size or the class representative size (geometric mean, "
                                      + f"{release_frequency.representative_hole_mm(idx, D_mm):.1f} mm), not of exactly {hole_mm:.0f} mm.",
                                      "Jet fire frequency = class frequency x TOTAL ignition probability (IOGP 434-06: a sustained jet fire follows whatever the time of ignition); the Purple Book direct-ignition value is not used for this.",
                                      "Leak frequency only: no catastrophic vessel failure, no zero-pressure releases, and a check against the installation's own record is advised (IOGP 434-01 section 1.3)."]}
    out["checks"] = _checks(out, data)
    return out


def _solid_flame_reach(pf: dict, thr: float) -> float:
    """Distance from the pool CENTRE to flux `thr` for a target at base level facing a flat vertical flame face (D wide, H high) at the Yellow Book SEP."""
    def f(r):
        face = viewfactor.vertical_flame_face(pf["diameter_m"], pf["flame_height_m"], r)
        return viewfactor.flux_from_faces((-r, 0.0, 0.0), (1.0, 0.0, 0.0), [face], pf["sep_mudan_croce_kW_m2"], pf["tau"], 40)["incident_kW_m2"]
    lo, hi = 0.2, 500.0
    if f(lo) < thr:
        return 0.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > thr else (lo, mid)
    return 0.5 * (lo + hi) + pf["diameter_m"] / 2


def _checks(out: dict, data: dict) -> list[str]:
    c = []
    r = out["release"]
    if "A_f_m2" in r:
        err = abs(r["A_f_m2"] * r["rho_f_kg_m3"] * r["u_f_m_s"] - r["W_kg_s"]) / r["W_kg_s"]
        c.append(("PASS" if err < 1e-9 else "FAIL") + ": mass continuity A_f rho_f u_f = W (omega basis)")
    d = out["droplet"]
    err = abs(d["rainout_kg_s"] + d["q_nett_air_kg_s"] - r["W_used_kg_s"]) / r["W_used_kg_s"]
    c.append(("PASS" if err < 1e-9 else "FAIL") + ": rain-out plus airborne equals the release rate")
    for p in out["pool"]:
        err = abs(p["feed_kg_s"] - p["burning_flux_kg_m2_s"] * p["A_eq_m2"]) / p["feed_kg_s"]
        c.append(("PASS" if err < 1e-9 else "FAIL") + f": burn-off balance for rainout {p['rainout_fraction']:.3g}")
    if out["jet"]:
        lvl = next(iter(out["jet"]["reach_m"].values()))
        dist = lvl["downwind"]
        if dist > 0:
            q = jet_radiation.flux_kW_m2(out["jet"]["flame"], data["fire"]["release_height_m"], dist, 0.0, data["fire"]["target_height_m"], data["fire"]["tau"])
            c.append(("PASS" if abs(q - lvl["flux_kW_m2"]) < 1e-6 * lvl["flux_kW_m2"] else "FAIL") + ": flux at the reported downwind reach equals its level")
    c += ["WARN: " + w for w in out["warnings"]]
    c.append("INFO: C_ds = 15 (Yellow Book recommendation), Sc = 0.7 (Yellow Book default), pool-spreading C_T = input; Cd, hole size, wind are study inputs")
    return c
