"""Pressurised liquefied-gas leak: source term, droplet and rainout screen, jet fire and pool fire in one JSON-driven study.

    python -m process_safety tool lgrelease input.json --out dir

Chain: saturated-liquid omega discharge and flash (`flash_release`) or, for a refrigerated or subcooled liquid, Bernoulli head-driven flow
(`release.liquid_release_kg_s`); droplet and rainout screen (`droplet`); Chamberlain jet flame (`jet_flame`) with a line-source flux map
(`jet_radiation`) for the airborne part; pool spreading and burn-off (`pool_spread`) and pool-fire radiation (`pool_fire`, `viewfactor`)
for the rained-out part. Sources and limits: docs/SOURCE_TERM_SOURCES.md and the docstring of each module.

Inputs the toolkit does not hold (surface tension, air viscosity and conductivity, heat of combustion, thresholds, critical Weber number,
drag constants, friction coefficient) are REQUIRED in the file, so each carries its own source note. Saturated-liquid properties come from the
bundled CoolProp-generated table (`fluiddata`); the vapour density at the boiling point is ideal-gas unless you supply `rho_vapour_Tb_kg_m3`
(about 4 % low for propane).
"""
from __future__ import annotations

import math

from . import droplet, flash_release, fluiddata, jet_flame, jet_radiation, pool_fire, pool_spread, release, viewfactor
from .constants import R

REQUIRED = {
    "ambient": ["P_kPa", "T_K", "rho_air_kg_m3", "mu_air_Pa_s", "k_air_W_mK", "wind_m_s"],
    "droplet": ["We_crit", "fall_height_m", "sigma_N_m"],
    "fire": ["Hc_J_kg", "release_height_m", "thresholds_kW_m2", "tau", "target_height_m"],
    "pool": ["C_T", "r0_m", "h0_m"],
}


def check(data: dict) -> list[str]:
    errs = []
    for k in ("fluid", "mode", "hole_d_m", "Cd"):
        if k not in data:
            errs.append(f"missing '{k}'")
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
    if data.get("fire", {}).get("release_angle_deg", 90) != 90:
        errs.append("only a vertical release (release_angle_deg = 90) is implemented for the jet flux map")
    dr = data.get("droplet", {}).get("drag", {"law": "stokes"})
    if dr.get("law") == "schiller_naumann" and not all(k in dr for k in ("c1", "c2")):
        errs.append("drag law schiller_naumann needs c1 and c2")
    return errs


def _drag(spec):
    if spec.get("law", "stokes") == "stokes":
        return droplet.stokes_drag
    return droplet.schiller_naumann(spec["c1"], spec["c2"])


def run(data: dict) -> dict:
    amb, dr, fire, pool = data["ambient"], data["droplet"], data["fire"], data["pool"]
    fl = data["fluid"]
    const = fluiddata.fluid_constants(fl)
    Mw, Tb, Tc, Pc = const["M_kg_kmol"], const["Tb_K"], const["Tc_K"], const["Pc_kPa"]
    Pa = amb["P_kPa"]
    atm = fluiddata.at_pressure(fl, Pa)
    rho_L_b, hfg_b = atm["rho_liq_kg_m3"], atm["h_lg_kJ_kg"] * 1000.0
    rho_V_b = data.get("properties", {}).get("rho_vapour_Tb_kg_m3") or Pa * 1000.0 * Mw / (R * 1000.0 * Tb)
    area = math.pi * data["hole_d_m"] ** 2 / 4
    out = {"mode": data["mode"], "warnings": [], "notes": []}
    superheated = data["mode"] == "saturated"
    jet_possible = superheated

    if superheated:
        s0 = fluiddata.at_pressure(fl, data["P0_kPa"])
        T0, rho0, omega = s0["T_K"], s0["rho_liq_kg_m3"], s0["omega_saturated"]
        cp_mean = data.get("properties", {}).get("cp_mean_J_kgK") or 0.5 * (s0["cp_liq_kJ_kgK"] + atm["cp_liq_kJ_kgK"]) * 1000.0
        if "cp_mean_J_kgK" not in data.get("properties", {}):
            out["notes"].append("cp_mean is the average of the table cp at T0 and at Tb; supply properties.cp_mean_J_kgK (e.g. from enthalpies) for better accuracy")
        out["warnings"] += flash_release.iso4126_10_check(T0, Tc, data["P0_kPa"], Pc, omega)
        rel = flash_release.saturated_liquid_release(data["P0_kPa"], rho0, omega, area, data["Cd"], T0, Tb, cp_mean, hfg_b, rho_L_b, rho_V_b, Pa)
        rel.update(T0_K=T0, omega=omega, cp_mean_J_kgK=cp_mean)
        W, u_f, xH = rel["W_kg_s"], rel["u_f_m_s"], rel["x_isenthalpic"]
        v_st = 1.0 / rho0
        Ep = droplet.partial_expansion_energy_J_kg(data["P0_kPa"] * 1000.0, Pa * 1000.0, v_st, data["P0_kPa"] * 1000.0, -0.5 * u_f * u_f)
        P_for_validity = data["P0_kPa"]
    else:
        T0 = data.get("T0_K", Tb)
        dP = data["overpressure_kPa_g"] * 1000.0
        W = release.liquid_release_kg_s(data["hole_d_m"], rho_L_b, dP, data["head_m"], data["Cd"])
        u_f = math.sqrt(2.0 * (dP + rho_L_b * 9.80665 * data["head_m"]) / rho_L_b)
        rel = {"W_kg_s": W, "u_f_m_s": u_f, "T0_K": T0, "regime": "liquid Bernoulli (no flash)", "x_vapour": 0.0, "x_isenthalpic": 0.0}
        xH, Ep = 0.0, None
        P_for_validity = Pa + data["overpressure_kPa_g"]
        out["notes"].append("Refrigerated/subcooled liquid: Bernoulli head-driven flow at the vena contracta velocity; no flash, no jet fire from the liquid.")
    out["release"] = rel

    smoke_drag = _drag(dr.get("drag", {"law": "stokes"}))
    scr = droplet.screen(sigma_N_m=dr["sigma_N_m"], u_f_m_s=u_f, rho_air=amb["rho_air_kg_m3"], mu_air=amb["mu_air_Pa_s"], k_air=amb["k_air_W_mK"],
                         We_crit=dr["We_crit"], rho_L=rho_L_b, h_fg_J_kg=hfg_b, dT_K=amb["T_K"] - Tb, fall_height_m=dr["fall_height_m"],
                         superheated=superheated, x_isenthalpic=xH, Ep_J_kg=Ep, drag=smoke_drag, orifice_mm=data["hole_d_m"] * 1000.0,
                         P_kPa=P_for_validity, horizontal=dr.get("horizontal", False))
    out["droplet"] = scr
    out["warnings"] += scr.get("validity_warnings", [])
    if dr.get("drag", {"law": "stokes"}).get("law", "stokes") == "stokes":
        out["warnings"].append("Stokes drag is exact only for Re << 1; settling of droplets near 100 micrometres or larger is overestimated, so use schiller_naumann with sourced constants")

    # jet fire on the airborne part of a flashing release
    if jet_possible:
        f_ref = min(scr["kletz"], scr["lautkaski"])
        m_jet = W * (1.0 - f_ref)
        v_j = u_f
        j = jet_flame.chamberlain(m_jet, rel["rho_f_kg_m3"], amb["rho_air_kg_m3"], Mw, fire["Hc_J_kg"], amb["wind_m_s"], 90.0, v_j_m_s=v_j)
        zr, zt, tau = fire["release_height_m"], fire["target_height_m"], fire["tau"]
        reach = {thr: {d: jet_radiation.reach_m(j, zr, thr, d, zt, tau) for d in ("downwind", "upwind", "crosswind")} for thr in fire["thresholds_kW_m2"]}
        grid = []
        for xx in (-30, -20, -10, 0, 10, 20, 30, 40, 60, 80):
            grid.append({"x_m": xx, **{f"y{yy}": jet_radiation.flux_kW_m2(j, zr, xx, yy, zt, tau) for yy in (0, 10, 20, 30, 40)}})
        out["jet"] = {"m_airborne_kg_s": m_jet, "rainout_used_for_jet": f_ref, "flame": {k: j[k] for k in ("Ds_m", "L_B0_m", "L_B_m", "alpha_deg", "B_m", "R_L_m", "W1_m", "W2_m", "area_m2", "F_s", "radiated_power_kW", "SEP_kW_m2")},
                      "reach_m": {str(k): v for k, v in reach.items()}, "flux_grid_kW_m2": grid, "near_field_radius_m": jet_radiation.near_field_radius_m(j),
                      "notes": j["notes"] + ["Source state is the two-phase mixture (DNV two-phase jet source not implemented); line-source flux map, vertical release only."]}
    else:
        out["jet"] = None

    # pool fire on the rained-out part
    cases = sorted({round(c, 6) for c in (scr["kletz"], scr["lautkaski"]) if c > 0} | {round(c, 6) for c in pool.get("extra_rainout_fractions", []) if c > 0})
    mflux = pool_fire.burning_rate_kg_m2_s(fire["Hc_J_kg"] / 1000.0, hfg_b / 1000.0, atm["cp_liq_kJ_kgK"], Tb, amb["T_K"])
    out["pool_burning_flux_kg_m2_s"] = mflux
    out["pool"] = []
    for fr in cases:
        mr = fr * W
        pf = pool_fire.pool_fire(pool_spread.equilibrium_area_m2(mr, mflux), fire["Hc_J_kg"] / 1000.0, hfg_b / 1000.0, atm["cp_liq_kJ_kgK"], Tb, amb["T_K"])
        sp = pool_spread.spread(mr, rho_L_b, amb["rho_air_kg_m3"], mflux, pool["r0_m"], pool["h0_m"], pool["C_T"])
        reach = {}
        for thr in fire["thresholds_kW_m2"]:
            reach[str(thr)] = {"point_source_m": pool_fire.distance_to_flux_m(pf, thr), "solid_flame_m": _solid_flame_reach(pf, thr)}
        out["pool"].append({"rainout_fraction": fr, "feed_kg_s": mr, "D_eq_m": pf["diameter_m"], "A_eq_m2": pf["diameter_m"] ** 2 * math.pi / 4, "flame_height_m": pf["flame_height_m"],
                            "heat_release_MW": pf["heat_release_MW"], "SEP_kW_m2": pf["sep_mudan_croce_kW_m2"], "t_to_equilibrium_s": sp["t_to_equilibrium_s"],
                            "spread_samples": sp["samples"], "reach": reach})
    if not cases:
        out["notes"].append("Neither published rainout correlation gives any rainout: no pool fire evaluated. Add pool.extra_rainout_fractions to test a hypothesis (for example ground impingement).")
    out["checks"] = _checks(out, data)
    return out


def _checks(out: dict, data: dict) -> list[str]:
    c = []
    r = out["release"]
    if "A_f_m2" in r:
        err = abs(r["A_f_m2"] * r["rho_f_kg_m3"] * r["u_f_m_s"] - r["W_kg_s"]) / r["W_kg_s"]
        c.append(("PASS" if err < 1e-9 else "FAIL") + ": mass continuity A_f rho_f u_f = W")
        err = abs(r["G_kg_m2_s"] * (r["u_f_m_s"] - r["u_choke_m_s"]) - (r["P_choke_kPa"] - data["ambient"]["P_kPa"]) * 1000.0) / (r["G_kg_m2_s"] * r["u_f_m_s"])
        c.append(("PASS" if err < 1e-9 else "FAIL") + ": momentum balance across the expansion")
    for p in out["pool"]:
        err = abs(p["feed_kg_s"] - out["pool_burning_flux_kg_m2_s"] * p["A_eq_m2"]) / p["feed_kg_s"]
        c.append(("PASS" if err < 1e-9 else "FAIL") + f": burn-off balance for rainout {p['rainout_fraction']}")
    if out["jet"]:
        thr = data["fire"]["thresholds_kW_m2"][0]
        d = out["jet"]["reach_m"][str(thr)]["downwind"]
        q = jet_radiation.flux_kW_m2(_rebuild_flame(out), data["fire"]["release_height_m"], d, 0.0, data["fire"]["target_height_m"], data["fire"]["tau"]) if d > 0 else thr
        c.append(("PASS" if abs(q - thr) < 1e-6 * thr else "FAIL") + ": flux at the reported downwind reach equals the threshold")
    c += ["WARN: " + w for w in out["warnings"]]
    c.append("INFO: inputs without a primary-text source (see docs/SOURCE_TERM_SOURCES.md): We_crit, Hc, thresholds, drag constants, C_T")
    return c


def _solid_flame_reach(pf: dict, thr: float) -> float:
    """Distance from the pool CENTRE to the flux `thr` for a target at base level facing a flat vertical flame face (D wide, H high), at SEP of Mudan-Croce."""
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


def _rebuild_flame(out: dict) -> dict:
    return out["jet"]["flame"]
