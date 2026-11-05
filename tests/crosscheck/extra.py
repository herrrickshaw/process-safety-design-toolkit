"""Extra cross-checks (v0.11): two-phase omega method, correlations, separators, hydraulics, vessel geometry, real-gas release.

Imported by validate.py; needs fluids, thermo, CoolProp. Each check goes through the chk() recorder passed in.
Two-phase reference: homogeneous equilibrium model (HEM) integrated directly with CoolProp along the isentrope from the inlet state,
G(P) = rho(P, s0) sqrt(2 (h0 - h(P, s0))), maximised over P. The omega method is a one-parameter fit to that, so a few percent
agreement near the inlet state and more away from it is expected; tolerances are set from the observed spread and printed.
"""
import math

from CoolProp.CoolProp import PropsSI

from process_safety import depressuring, hydraulics, props, release, separator, twophase, vessel_mech

CP_NAMES = {"methane": "Methane", "ethane": "Ethane", "ethylene": "Ethylene", "propane": "Propane", "propylene": "Propylene",
            "n-butane": "n-Butane", "isobutane": "IsoButane"}


def hem_flux(fluid, P0, h0=None, s0=None, x0=0.0, n=400):
    """Critical HEM mass flux (kg/m2/s) from a saturated-liquid (x0=0) or saturated two-phase inlet at P0 (Pa)."""
    h0 = PropsSI("H", "P", P0, "Q", x0, fluid)
    s0 = PropsSI("S", "P", P0, "Q", x0, fluid)
    best = 0.0
    for i in range(1, n):
        P = P0 * (1 - 0.9 * i / n)
        try:
            rho = PropsSI("D", "P", P, "S", s0, fluid)
            h = PropsSI("H", "P", P, "S", s0, fluid)
        except ValueError:
            continue
        g = rho * math.sqrt(max(2 * (h0 - h), 0.0))
        best = max(best, g)
    return best


def omega_two_point_cp(fluid, P0, x0=0.0):
    v0 = 1.0 / PropsSI("D", "P", P0, "Q", x0, fluid)
    s0 = PropsSI("S", "P", P0, "Q", x0, fluid)
    v9 = 1.0 / PropsSI("D", "P", 0.9 * P0, "S", s0, fluid)
    return twophase.omega_two_point(v0, v9), v0


def omega_sat_cp(fluid, P0):
    cp = PropsSI("C", "P", P0, "Q", 0, fluid)
    T = PropsSI("T", "P", P0, "Q", 0, fluid)
    vl = 1.0 / PropsSI("D", "P", P0, "Q", 0, fluid)
    vg = 1.0 / PropsSI("D", "P", P0, "Q", 1, fluid)
    hlg = PropsSI("H", "P", P0, "Q", 1, fluid) - PropsSI("H", "P", P0, "Q", 0, fluid)
    return twophase.omega_saturated_liquid(cp, T, P0, vl, vg - vl, hlg)


def run_extra(chk):
    # --- two-phase omega method against a direct HEM integration with CoolProp
    for fluid, P0 in (("Propane", 1.0e6), ("Propane", 1.9e6), ("n-Butane", 1.0e6), ("Ammonia", 1.5e6)):
        ref = hem_flux(fluid, P0)
        w2, v0 = omega_two_point_cp(fluid, P0)
        g2 = twophase.mass_flux(P0 / 1e3, 1 / v0, w2)["G_kg_m2_s"]
        chk(f"twophase flux, two-point omega ({fluid} sat. liquid, {P0/1e3:.0f} kPa)", g2, ref, 0.20,
            "CoolProp isentropic HEM, maximum of rho*sqrt(2 dh) over P", "kg/m2/s")
        ws = omega_sat_cp(fluid, P0)
        gs = twophase.mass_flux(P0 / 1e3, 1 / v0, ws)["G_kg_m2_s"]
        chk(f"twophase flux, saturated omega ({fluid}, {P0/1e3:.0f} kPa)", gs, ref, 0.05,
            "CoolProp isentropic HEM (single-point omega)", "kg/m2/s")
    # --- Lee-Kesler vapour pressure and Rackett density against CoolProp reference EOS
    for comp, name in CP_NAMES.items():
        Tc = props.COMPONENTS[comp][0]
        for Tr in (0.6, 0.7, 0.8):
            T = Tr * Tc
            chk(f"props.vapour_pressure_bar {comp} Tr={Tr}", props.vapour_pressure_bar(comp, T),
                PropsSI("P", "T", T, "Q", 0, name) / 1e5, 0.04, "CoolProp (Helmholtz EOS)", "bar")
            chk(f"props.liquid_density_kg_m3 {comp} Tr={Tr}", props.liquid_density_kg_m3(comp, T),
                PropsSI("D", "T", T, "Q", 0, name), 0.04, "CoolProp (Helmholtz EOS)", "kg/m3")
    # --- depressuring: ideal-gas isentropic end temperature against the real-gas isentrope
    for name, P0, Pt, T0 in (("Methane", 5.0e6, 1.0e6, 300.0), ("Nitrogen", 5.0e6, 1.0e6, 300.0)):
        k = PropsSI("Cpmass", "P", P0, "T", T0, name) / PropsSI("Cvmass", "P", P0, "T", T0, name)
        s0 = PropsSI("S", "P", P0, "T", T0, name)
        ref = PropsSI("T", "P", Pt, "S", s0, name)
        chk(f"depressuring.min_gas_temperature_K {name} 50->10 bar", depressuring.min_gas_temperature_K(T0, P0 / 1e3, Pt / 1e3, k), ref, 0.10,
            "KNOWN DIFFERENCE: ideal-gas isentrope with inlet-state k is 5-9% (10-20 K) colder than the real-gas isentrope at 50 bar; conservative for MDMT", "K")
    # --- choked gas release with real-gas k and Z
    for name, M, P, T in (("Methane", 16.043, 2.0e6, 300.0), ("Nitrogen", 28.013, 2.0e6, 300.0)):
        Z = PropsSI("Z", "P", P, "T", T, name)
        k = PropsSI("Cpmass", "P", P, "T", T, name) / PropsSI("Cvmass", "P", P, "T", T, name)
        s0 = PropsSI("S", "P", P, "T", T, name)
        best = 0.0
        for i in range(1, 400):
            Pp = P * (1 - 0.95 * i / 400)
            rho = PropsSI("D", "P", Pp, "S", s0, name)
            h = PropsSI("H", "P", Pp, "S", s0, name) - PropsSI("H", "P", P, "T", T, name)
            best = max(best, rho * math.sqrt(max(-2 * h, 0)))
        d = 0.01
        ours = release.gas_release_kg_s(d, P / 1e3, T, M, k, Cd=1.0, Z=Z)
        chk(f"release.gas_release_kg_s {name} 20 bar 10 mm hole", ours, best * math.pi * d * d / 4, 0.05,
            "CoolProp real-gas isentropic choked flux", "kg/s")
    # --- fluids: separators, drag, hydraulics, valve units, vessel geometry
    try:
        import fluids
        from fluids import control_valve, friction, geometry
        from fluids import separator as fsep
        rhoL, rhoG = 700.0, 20.0
        chk("separator.souders_brown_velocity", separator.souders_brown_velocity(rhoL, rhoG, 0.107),
            fsep.v_Sounders_Brown(K=0.107, rhol=rhoL, rhog=rhoG), 0.001,
            "fluids.separator.v_Sounders_Brown", "m/s")
        from fluids import drag
        for d_um in (100, 300):
            ours = separator.droplet_terminal_velocity(d_um, rhoL, rhoG, 1.2e-5)
            ref = drag.v_terminal(d_um * 1e-6, rhoL, rhoG, 1.2e-5)
            chk(f"separator.droplet_terminal_velocity {d_um} um", ours, ref, 0.15, "fluids.drag.v_terminal (default drag correlation)", "m/s")
        Q, D, L, rho, mu = 0.02, 0.1, 100.0, 800.0, 1.0e-3
        ours = hydraulics.incompressible_dp_kpa(Q, D, L, rho, mu)["dp_friction_kPa"]
        ref = friction.one_phase_dP(m=Q * rho, rho=rho, mu=mu, D=D, roughness=4.6e-5, L=L) / 1e3
        chk("hydraulics.incompressible_dp_kpa 100 m, 100 mm", ours, ref, 0.01, "fluids.friction.one_phase_dP", "kPa")
        chk("hydraulics.cv_from_kv", hydraulics.cv_from_kv(100.0), control_valve.Kv_to_Cv(100.0), 0.001, "fluids.control_valve.Kv_to_Cv", "")
        for frac in (0.25, 0.5, 0.8):
            chk(f"vessel_mech.liquid_inventory_m3 horizontal fill {frac}", vessel_mech.liquid_inventory_m3(2.0, 6.0, frac, "horizontal"),
                _cyl_segment(fluids, 2.0, 6.0, frac), 0.001,
                "fluids.geometry.TANK (plain cylinder, flat ends excluded)", "m3")
    except ImportError:
        pass


def _cyl_segment(fluids, D, L, frac):
    from fluids.geometry import TANK
    t = TANK(D=D, L=L, horizontal=True, sideA=None, sideB=None)
    return t.V_from_h(frac * D, method="full") if hasattr(t, "V_from_h") else float("nan")
