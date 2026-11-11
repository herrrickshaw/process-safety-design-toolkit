"""Release rate of a pressurised liquid through a supply line with friction: homogeneous-equilibrium (HEM) two-phase flow.

Why: a short-orifice model (`lg_release`, Leung omega or Yellow Book liquid) over-predicts line-fed experiments
(Project AA 3026: 34 against 16.1 kg/s measured; JIVE 8051: 37 against 6.86). The line itself limits the flow.

Model (constant mass flow W through pipe segments in series, adiabatic, no slip, no heat transfer):
* liquid region (P above the vapour pressure of the stagnation liquid): incompressible, dP/dz = -f G^2 v / (2 D);
* flashing region: T = Tsat(P); quality x from the energy balance h0 = h_f(T) + x h_fg(T) + (G v)^2 / 2, v = v_l + x (v_g - v_l);
  momentum: -dP = f G^2 v / (2 D) dz + G^2 dv  ->  dz/dP = -(1 + G^2 dv/dP) / (f G^2 v / (2 D)); choking where 1 + G^2 dv/dP = 0;
* area changes: ideal Bernoulli step 0.5 (G2^2 - G1^2) v plus a contraction loss K = 0.5 (1 - beta^2) on 0.5 G2^2 v (Crane, as quoted in Perry);
* fittings (valves, bends) enter only as a loss coefficient K_fittings the caller supplies, applied to 0.5 G^2 v of the last segment: the toolkit has no
  fittings data and refuses to guess;
* friction factor: Darcy-Weisbach with Colebrook; Reynolds number from the McAdams homogeneous viscosity, with the vapour viscosity from Yellow Book
  Annex formula 7 (`yb_annex.vapour_viscosity_Pa_s`).
The largest W for which the line can pass the pressure drop (choke at the exit or exit at ambient pressure) is returned.

Limits: homogeneous flow (no slip, instant flashing, no nucleation delay) usually over-predicts the flow of a subcooled liquid through a short line and
under-predicts it for long lines; vapour treated as ideal gas. Source of the HEM equations: Yellow Book 2.5.x / Fauske; Colebrook as in any pipe-flow text.
"""
from __future__ import annotations

import math

from . import props_ref, yb_annex

R_GAS = 8.314462618


def colebrook_f(Re: float, rel_rough: float) -> float:
    """Darcy friction factor; laminar 64/Re below 2300, Colebrook (fixed point) above."""
    if not Re > 0:
        raise ValueError("Reynolds number must be positive")
    if Re < 2300.0:
        return 64.0 / Re
    f = 0.02
    for _ in range(60):
        f_new = (-2.0 * math.log10(rel_rough / 3.7 + 2.51 / (Re * math.sqrt(f)))) ** -2
        if abs(f_new - f) < 1e-12:
            break
        f = f_new
    return f


class _Fluid:
    def __init__(self, fluid: str, T0: float, P0: float, props: str = "reference", relax_m: float | None = None):
        if relax_m is not None and not relax_m > 0:
            raise ValueError("relaxation_length_m must be positive (or None for homogeneous equilibrium)")
        self.relax = relax_m
        self.s = 0.0  # distance travelled since the pressure fell below the vapour pressure (used only with relax_m)
        if props not in ("reference", "yb_annex"):
            raise ValueError("props must be 'reference' (NIST table, real-gas vapour volume) or 'yb_annex' (Yellow Book Annex, ideal gas)")
        self.y = props_ref if props == "reference" else yb_annex
        self.real_gas = props == "reference"
        y = self.y
        self.fl, self.T0, self.P0 = fluid, T0, P0
        self.M = y.molar_mass_kg_mol(fluid)
        self.Pv0 = y.vapour_pressure_Pa(fluid, T0)
        self.vl0 = 1.0 / y.liquid_density_kg_m3(fluid, T0)
        self.mu = y.liquid_viscosity_Pa_s(fluid, T0)

    def mixture_viscosity(self, x: float) -> float:
        """McAdams homogeneous viscosity 1/mu = x/mu_g + (1 - x)/mu_l at the temperature of the last `state` call; liquid viscosity when x = 0."""
        if x <= 0.0:
            return self.mu
        mul = self.y.liquid_viscosity_Pa_s(self.fl, self._T)
        mug = self.y.vapour_viscosity_Pa_s(self.fl, self._T)
        return 1.0 / (x / mug + (1.0 - x) / mul)

    def state(self, P: float, G: float) -> tuple[float, float]:
        """(specific volume m3/kg, quality) at pressure P and mass flux G with stagnation enthalpy conserved."""
        if P >= self.Pv0:
            self._T = self.T0
            return self.vl0, 0.0
        y = self.y
        T = y.saturation_temperature_K(self.fl, P)
        self._T = T
        vl = 1.0 / y.liquid_density_kg_m3(self.fl, T)
        vg = 1.0 / y.vapour_density_kg_m3(self.fl, T) if self.real_gas else R_GAS * T / (P * self.M)
        Lv = y.heat_of_vaporisation_J_kg(self.fl, T)
        a = -y.liquid_enthalpy_change_J_kg(self.fl, self.T0, T)  # h0 - h_f(T) > 0

        def g(x: float) -> float:
            v = vl + x * (vg - vl)
            return x * Lv + 0.5 * G * G * v * v - a

        if g(1.0) <= 0.0:
            return vg, 1.0
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if g(mid) < 0.0 else (lo, mid)
        x = 0.5 * (lo + hi)
        if self.relax is not None:
            x *= 1.0 - math.exp(-self.s / self.relax)
        return vl + x * (vg - vl), x

    def dv_ds(self, P: float, G: float) -> float:
        """d v / d s at fixed P: rate at which the delayed flashing adds vapour volume along the pipe (0 for homogeneous equilibrium)."""
        if self.relax is None or P >= self.Pv0:
            return 0.0
        s_keep = self.s
        self.s = 1e9  # equilibrium state at this P
        v_eq, x_eq = self.state(P, G)
        self.s = s_keep
        vl = 1.0 / self.y.liquid_density_kg_m3(self.fl, self._T)
        return (v_eq - vl) * math.exp(-s_keep / self.relax) / self.relax


def _dz_dP(F: _Fluid, P: float, G: float, D: float, eps: float) -> float:
    """dz/dP (negative while the flow can still accelerate); zero or positive at the choke."""
    v, x = F.state(P, G)
    mu = F.mixture_viscosity(x)
    dP = max(1.0, 1e-5 * P)
    v2, _ = F.state(P - dP, G)
    dv_dP = (v2 - v) / (-dP)
    f = colebrook_f(G * D / mu, eps / D)
    return -(1.0 + G * G * dv_dP) / (f * G * G * v / (2.0 * D) + G * G * F.dv_ds(P, G))


def _segment(F: _Fluid, P_in: float, G: float, D: float, L: float, eps: float, P_floor: float) -> float | None:
    """Pressure at the end of a straight segment of length L, or None when the segment cannot pass G (choke first, or P below the floor).

    With a relaxation length the flashing distance F.s grows only while P is below the vapour pressure of the stagnation liquid.
    """
    z, P = 0.0, P_in
    n_guard = 0
    while z < L:
        n_guard += 1
        if n_guard > 20000:
            return None
        dzdP = _dz_dP(F, P, G, D, eps)
        if dzdP >= 0.0:
            return None
        dP = min(0.002 * P_in, max(50.0, 0.01 * (P - P_floor)))
        if P - dP <= P_floor:
            dP = P - P_floor
            if dP <= 0:
                return None
        s_start = F.s
        mid = _dz_dP(F, P - 0.5 * dP, G, D, eps)
        if mid >= 0.0:
            return None
        if F.relax is not None and P - 0.5 * dP < F.Pv0:  # corrector: evaluate at the mid-step flashing distance
            F.s = s_start + 0.5 * (-mid * dP)
            mid = _dz_dP(F, P - 0.5 * dP, G, D, eps)
            F.s = s_start
            if mid >= 0.0:
                return None
        dz = -mid * dP
        if z + dz >= L:
            if P - dP < F.Pv0:
                F.s = s_start + (L - z)
            return P - dP * (L - z) / dz
        z += dz
        P -= dP
        if F.relax is not None and P < F.Pv0:
            F.s = s_start + dz
        if P <= P_floor:
            return None
    return P


def _march(F: _Fluid, W: float, segments, k_fit: float, eps: float, Pa: float, k_entry: float) -> float | None:
    """Exit pressure for flow W, or None if the line cannot pass W."""
    F.s = 0.0
    D0 = segments[0][1]
    G = W / (math.pi / 4.0 * D0 * D0)
    v, _ = F.state(F.P0, G)
    P = F.P0 - k_entry * 0.5 * G * G * v - 0.5 * G * G * v  # entrance loss plus acceleration to the line velocity
    if P <= Pa:
        return None
    for i, (L, D) in enumerate(segments):
        if i > 0:
            Dp = segments[i - 1][1]
            G1, G2 = W / (math.pi / 4.0 * Dp * Dp), W / (math.pi / 4.0 * D * D)
            v, _ = F.state(P, G1)
            K = 0.5 * (1.0 - (D / Dp) ** 2) if D < Dp else (1.0 - (Dp / D) ** 2) ** 2
            P -= 0.5 * (G2 * G2 - G1 * G1) * v + K * 0.5 * G2 * G2 * v
            if P <= Pa:
                return None
        G = W / (math.pi / 4.0 * D * D)
        if i == len(segments) - 1 and k_fit > 0.0:
            v, _ = F.state(P, G)
            P -= k_fit * 0.5 * G * G * v
            if P <= Pa:
                return None
        P = _segment(F, P, G, D, L, eps, Pa)
        if P is None:
            return None
    return P


def line_discharge(fluid: str, T0_K: float, P0_Pa: float, Pa_Pa: float, segments: list[tuple[float, float]], *, roughness_m: float = 1.5e-6,
                   k_fittings: float = 0.0, k_entry: float = 0.5, props: str = "reference", relaxation_length_m: float | None = None) -> dict:
    """Largest mass flow (kg/s) a series of straight segments [(length m, inner diameter m), ...] passes from a vessel of liquid at (T0, P0) to ambient Pa.

    k_fittings: total loss coefficient of valves and bends, applied to 0.5 G^2 v in the last segment (caller-supplied; not defaulted from data).
    relaxation_length_m: None (default) is homogeneous equilibrium. A positive value delays flashing: the vapour quality is
    x_eq (1 - exp(-s/L_r)), s the distance travelled since the pressure fell below the vapour pressure; L_r -> 0 recovers HEM and
    L_r -> infinity a frozen liquid. This is the delayed-equilibrium idea (see docs/LITERATURE_SURVEY.md) in its simplest closure; the
    L_r is an INPUT: no value is built in because the correlations in the DEM papers have not been read. The energy balance uses the
    equilibrium state (the liquid-side superheat is not tracked), so mass-flow results are indicative only.
    The last segment's open end is the discharge plane; an orifice of the same bore adds nothing. Returns W, exit pressure and the flow regime.
    """
    if not (P0_Pa > Pa_Pa > 0) or T0_K <= 0 or roughness_m < 0 or k_fittings < 0 or k_entry < 0:
        raise ValueError("need P0 > Pa > 0, T0 > 0 and non-negative roughness and loss coefficients")
    if not segments or any(L <= 0 or D <= 0 for L, D in segments):
        raise ValueError("segments must be a non-empty list of (length, diameter) with positive values")
    F = _Fluid(fluid, T0_K, P0_Pa, props, relaxation_length_m)
    Amax = math.pi / 4.0 * max(D for _, D in segments) ** 2
    lo, hi = 1e-6, 3.0e4 * Amax
    if _march(F, lo, segments, k_fittings, roughness_m, Pa_Pa, k_entry) is None:
        raise ValueError("line cannot pass even a trickle (start pressure below ambient after entrance losses)")
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if _march(F, mid, segments, k_fittings, roughness_m, Pa_Pa, k_entry) is None:
            hi = mid
        else:
            lo = mid
    W = lo
    Pe = _march(F, W, segments, k_fittings, roughness_m, Pa_Pa, k_entry)
    regime = "choked at exit" if Pe is not None and Pe > 1.02 * Pa_Pa else "exit at ambient pressure"
    return {"W_kg_s": W, "P_exit_Pa": Pe, "regime": regime, "G_last_kg_m2_s": W / (math.pi / 4.0 * segments[-1][1] ** 2)}
