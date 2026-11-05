"""Relief, venting and flare commands."""
from __future__ import annotations

from .. import depressuring, flare, relief, release, tank_venting
from .registry import command, emit


@command("relief-gas", "API 520-I gas/vapour PSV area")
class ReliefGas:
    ranges = {"W": "mass_flow_kg_h", "T": "temperature_K", "set_g": "set_pressure_kPag", "back_g": "back_pressure_kPag",
              "M": "molar_mass_kg_kmol", "k": "heat_capacity_ratio", "Z": "compressibility", "Kb": "coefficient_0_1", "Kc": "coefficient_0_1"}

    @staticmethod
    def add_arguments(g):
        g.add_argument("--W", type=float, required=True, help="required relieving rate kg/h")
        g.add_argument("--T", type=float, required=True, help="relieving temperature K")
        g.add_argument("--set-g", type=float, required=True, help="set pressure kPag")
        g.add_argument("--back-g", type=float, default=0.0, help="total back pressure kPag")
        g.add_argument("--case", choices=list(relief.ACCUMULATION), default="single_non_fire")
        g.add_argument("--M", type=float, required=True)
        g.add_argument("--k", type=float, required=True, help="Cp/Cv")
        g.add_argument("--Z", type=float, default=1.0)
        g.add_argument("--Kb", type=float, default=1.0)
        g.add_argument("--Kc", type=float, default=1.0, help="0.9 if rupture disk upstream")

    @staticmethod
    def run(a, p):
        P1 = relief.relieving_pressure_kpa(a.set_g, a.case)
        emit(relief.gas_area(a.W, a.T, P1, a.back_g + relief.ATM, a.M, a.k, a.Z, Kb=a.Kb, Kc=a.Kc, set_g_kpa=a.set_g))


@command("relief-steam")
class ReliefSteam:
    ranges = {"W": "mass_flow_kg_h", "set_g": "set_pressure_kPag", "Ksh": "multiplier_positive"}

    @staticmethod
    def add_arguments(st):
        st.add_argument("--W", type=float, required=True)
        st.add_argument("--set-g", type=float, required=True)
        st.add_argument("--case", choices=list(relief.ACCUMULATION), default="single_non_fire")
        st.add_argument("--Ksh", type=float, default=1.0)

    @staticmethod
    def run(a, p):
        emit(relief.steam_area(a.W, relief.relieving_pressure_kpa(a.set_g, a.case), Ksh=a.Ksh))


@command("relief-liquid")
class ReliefLiquid:
    ranges = {"Q": "flow_m3_h", "rho": "density_kg_m3", "set_g": "set_pressure_kPag", "back_g": "back_pressure_kPag", "mu": "viscosity_cP"}

    @staticmethod
    def add_arguments(li):
        li.add_argument("--Q", type=float, required=True, help="m3/h")
        li.add_argument("--rho", type=float, required=True)
        li.add_argument("--set-g", type=float, required=True)
        li.add_argument("--back-g", type=float, default=0.0)
        li.add_argument("--mu", type=float, default=1.0, help="cP")

    @staticmethod
    def run(a, p):
        P1 = a.set_g * 1.10 + relief.ATM
        emit(relief.liquid_area(a.Q, a.rho, P1, a.back_g + relief.ATM, a.mu))


@command("relief-fire", "API 521 liquid-wetted fire case")
class ReliefFire:
    ranges = {"wetted_area": "area_m2", "D": "length_m", "L": "length_m", "level": "nonneg_length_m", "elevation": "nonneg_length_m",
              "latent": "latent_heat_kJ_kg", "F": "environment_factor"}

    @staticmethod
    def add_arguments(f):
        f.add_argument("--wetted-area", type=float, help="m2 (else give vessel geometry)")
        f.add_argument("--D", type=float); f.add_argument("--L", type=float); f.add_argument("--level", type=float)
        f.add_argument("--orientation", choices=["horizontal", "vertical"], default="horizontal")
        f.add_argument("--elevation", type=float, default=0.0)
        f.add_argument("--latent", type=float, required=True, help="latent heat kJ/kg at relieving conditions")
        f.add_argument("--F", type=float, default=1.0)
        f.add_argument("--no-drainage", action="store_true")

    @staticmethod
    def run(a, p):
        A = a.wetted_area or relief.wetted_area_cylinder(a.D, a.L, a.level, a.orientation, a.elevation)
        W = relief.fire_relief_rate_kg_h(A, a.latent, a.F, not a.no_drainage)
        emit({"wetted_area_m2": A, "heat_input_kW": relief.fire_heat_input_W(A, a.F, not a.no_drainage) / 1e3,
              "relief_rate_kg_h": W, "note": "relieving pressure for fire = set x 1.21 + atm; feed W to relief-gas"})


@command("tank-normal", "API 2000 normal (thermal + liquid movement) venting")
class TankNormal:
    ranges = {"volume": "volume_m3", "fill": "flow_m3_h", "empty": "flow_m3_h"}

    @staticmethod
    def add_arguments(tn):
        tn.add_argument("--volume", type=float, required=True, help="tank capacity m3")
        tn.add_argument("--fill", type=float, default=0.0, help="max filling rate m3/h")
        tn.add_argument("--empty", type=float, default=0.0, help="max emptying rate m3/h")
        tn.add_argument("--volatile", action="store_true", help="flash point < 37.8 C or boiling point < 148.9 C")

    @staticmethod
    def run(a, p):
        emit(tank_venting.normal_venting(a.volume, a.fill, a.empty, a.volatile))


@command("tank-fire", "API 2000 emergency venting for fire exposure")
class TankFire:
    ranges = {"D": "length_m", "L": "nonneg_length_m", "elevation": "nonneg_length_m", "wetted_area": "area_m2",
              "design_barg": "design_pressure_barg", "normal_capacity": "flow_m3_h", "L_kj_kg": "latent_heat_kJ_kg",
              "T": "temperature_K", "M": "molar_mass_kg_kmol"}

    @staticmethod
    def add_arguments(tf):
        tf.add_argument("--shape", choices=["sphere", "horizontal", "vertical"])
        tf.add_argument("--D", type=float); tf.add_argument("--L", type=float, default=0.0)
        tf.add_argument("--elevation", type=float, default=0.0)
        tf.add_argument("--wetted-area", type=float)
        tf.add_argument("--F", default="1.0", help=f"number or one of: {', '.join(tank_venting.F_FACTORS)}")
        tf.add_argument("--design-barg", type=float, default=0.07)
        tf.add_argument("--normal-capacity", type=float, default=0.0, help="outbreathing capacity of installed normal vents, Nm3/h")
        tf.add_argument("--L-kj-kg", type=float, help="latent heat (default hexane basis)")
        tf.add_argument("--T", type=float, help="relieving vapour temperature K")
        tf.add_argument("--M", type=float, help="vapour molecular weight")

    @staticmethod
    def run(a, p):
        A = a.wetted_area or tank_venting.wetted_area_m2(a.shape, a.D, a.L, a.elevation)
        F = tank_venting.F_FACTORS.get(a.F) if a.F in tank_venting.F_FACTORS else float(a.F)
        kw = {k: v for k, v in (("L_kJ_kg", a.L_kj_kg), ("T_K", a.T), ("M", a.M)) if v}
        req = tank_venting.fire_venting_Nm3h(A, F, design_barg=a.design_barg, **kw)
        emit({"wetted_area_m2": A, "F": F, "required_Nm3h_eq1B": req,
              "required_Nm3h_simplified": tank_venting.fire_venting_simplified(A, F, a.design_barg),
              "additional_emergency_vent_Nm3h": tank_venting.emergency_vent_shortfall_Nm3h(req, a.normal_capacity),
              "note": "API 2000 5th ed. (1998); a frangible roof-to-shell joint may replace emergency vents (4.3.3.1)"})


@command("blowdown", "adiabatic vessel blowdown through a hole")
class Blowdown:
    ranges = {"volume": "volume_m3", "p0": "pressure_abs_kPa", "T0": "temperature_K", "M": "molar_mass_kg_kmol",
              "k": "heat_capacity_ratio", "hole_d": "length_m", "t_end": "time_s"}

    @staticmethod
    def add_arguments(bd):
        for n in ("volume", "p0", "T0", "M", "k", "hole-d"):
            bd.add_argument("--" + n, type=float, required=True)
        bd.add_argument("--t-end", type=float, default=600.0)

    @staticmethod
    def run(a, p):
        r = release.blowdown_adiabatic(a.volume, a.p0, a.T0, a.M, a.k, a.hole_d, t_end_s=a.t_end)
        r.pop("series"); emit(r)


@command("depressure", "time to target pressure through an orifice (isothermal and adiabatic) + min gas temperature")
class Depressure:
    ranges = {"volume": "volume_m3", "p0": "pressure_abs_kPa", "pt": "pressure_abs_kPa", "T0": "temperature_K",
              "M": "molar_mass_kg_kmol", "k": "heat_capacity_ratio", "area": "area_m2"}

    @staticmethod
    def add_arguments(dp):
        for n in ("volume", "p0", "pt", "T0", "M", "k", "area"):
            dp.add_argument("--" + n, type=float, required=True)

    @staticmethod
    def run(a, p):
        k = a.k
        emit({"isothermal_s": depressuring.depressuring_time_s(a.volume, a.p0, a.pt, a.T0, a.M, k, a.area, mode="isothermal"),
              "adiabatic_s": depressuring.depressuring_time_s(a.volume, a.p0, a.pt, a.T0, a.M, k, a.area, mode="adiabatic"),
              "min_gas_temperature_K_isentropic": depressuring.min_gas_temperature_K(a.T0, a.p0, a.pt, k),
              "note": "gas phase only; the isentropic temperature is a screening lower bound for MDMT, not metal temperature"})


@command("flare", "API 521 point-source radiation")
class Flare:
    ranges = {"mass": "mass_flow_kg_s", "lhv": "heat_of_combustion_MJ_kg", "mw": "molar_mass_kg_kmol", "flame_length": "length_m", "tau": "coefficient_0_1"}

    @staticmethod
    def add_arguments(fl):
        fl.add_argument("--mass", type=float, required=True, help="kg/s")
        fl.add_argument("--lhv", type=float, required=True, help="MJ/kg")
        fl.add_argument("--mw", type=float, required=True)
        fl.add_argument("--flame-length", type=float)
        fl.add_argument("--tau", type=float, default=1.0)

    @staticmethod
    def run(a, p):
        F = flare.radiant_fraction(a.mw); Q = flare.heat_release_W(a.mass, a.lhv)
        emit({"heat_release_MW": Q / 1e6, "radiant_fraction": F, **flare.radiation_checks(Q, F, a.flame_length, a.tau)})
