"""Liquid pool spreading on flat ground and burn-off equilibrium for a continuous release.

Momentum balance (Webber et al. 2010 "improved integral model" as quoted by Basha et al., Chemical Engineering Transactions 31 (2013)
43-48, eq. 1; the original paper was NOT read):

    d2r/dt2 = 4 g' h / r  -  C_T (1/h) (dr/dt)^2,        h = V / (pi r^2),   g' = g (rho_L - rho_a) / rho_L

The first term is the gravity-inertia regime (the factor 4 comes from the shallow-water equations according to that source); the second is
turbulent skin friction at the base with C_T of order 1e-3 depending on ground roughness (an INPUT here; 0 gives the frictionless limit).
Volume balance with burning:  dV/dt = (m_feed - m'' pi r^2) / rho_L.   Burn-off equilibrium (exact mass balance):  A_eq = m_feed / m''.

Exact check built in the tests: without friction, feed or burning, V is constant and r'' = k / r^3 with k = 4 g' V / pi, whose first integral is
r'^2 - r0'^2 = k (1/r0^2 - 1/r^2).

Limits: flat horizontal impermeable ground, circular pool, no heat transfer from the ground, no evaporation without burning, no bund,
no gravity-viscous or surface-tension regimes (negligible for a rapidly boiling or burning LPG pool by the cited authors' argument).
The pool is stopped at the first time its radius reaches the burn-off radius; inertia overshoot after that is not modelled.
Screening aid, not certified design.
"""
from __future__ import annotations

import math

from .constants import G as g_acc


def equilibrium_area_m2(m_feed_kg_s: float, burn_flux_kg_m2_s: float) -> float:
    """Area at which burning removes the feed: A = m_feed / m''."""
    if not (m_feed_kg_s > 0 and burn_flux_kg_m2_s > 0):
        raise ValueError("feed rate and burning flux must be positive")
    return m_feed_kg_s / burn_flux_kg_m2_s


def reduced_gravity(rho_L: float, rho_a: float) -> float:
    if not rho_L > rho_a > 0:
        raise ValueError("need rho_L > rho_a > 0")
    return g_acc * (rho_L - rho_a) / rho_L


def spread(m_feed_kg_s: float, rho_L: float, rho_a: float, burn_flux_kg_m2_s: float, r0_m: float, h0_m: float, C_T: float,
           t_end_s: float = 120.0, dt_s: float = 0.002, stop_at_equilibrium: bool = True, sample_times_s: tuple = (1, 2, 5, 10, 20, 30, 60)) -> dict:
    """Integrate the pool radius with RK4. Initial state: radius r0, depth h0, at rest. Returns samples and the time to burn-off radius."""
    for k, v in dict(r0=r0_m, h0=h0_m, t_end=t_end_s, dt=dt_s).items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")
    if m_feed_kg_s < 0 or burn_flux_kg_m2_s < 0 or C_T < 0:
        raise ValueError("feed, burning flux and C_T must not be negative")
    gp = reduced_gravity(rho_L, rho_a)
    r_eq = math.sqrt(equilibrium_area_m2(m_feed_kg_s, burn_flux_kg_m2_s) / math.pi) if m_feed_kg_s > 0 and burn_flux_kg_m2_s > 0 else None

    def deriv(y):
        r, u, V = y
        h = max(V / (math.pi * r * r), 1e-9)
        return (u, 4.0 * gp * h / r - C_T * u * u / h, (m_feed_kg_s - burn_flux_kg_m2_s * math.pi * r * r) / rho_L)

    y = (r0_m, 0.0, math.pi * r0_m ** 2 * h0_m)
    t = 0.0
    t_eq = None
    samples = {}
    marks = sorted(sample_times_s)
    mi = 0
    while t < t_end_s:
        k1 = deriv(y)
        k2 = deriv(tuple(a + 0.5 * dt_s * b for a, b in zip(y, k1)))
        k3 = deriv(tuple(a + 0.5 * dt_s * b for a, b in zip(y, k2)))
        k4 = deriv(tuple(a + dt_s * b for a, b in zip(y, k3)))
        y = tuple(a + dt_s / 6.0 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4))
        y = (y[0], y[1], max(y[2], 1e-12))
        t += dt_s
        while mi < len(marks) and t >= marks[mi] - 1e-12:
            samples[marks[mi]] = {"diameter_m": 2 * y[0], "mean_depth_mm": 1000 * y[2] / (math.pi * y[0] ** 2), "front_speed_m_s": y[1]}
            mi += 1
        if r_eq is not None and t_eq is None and y[0] >= r_eq:
            t_eq = t
            if stop_at_equilibrium:
                break
    return {"g_prime_m_s2": gp, "r_equilibrium_m": r_eq, "D_equilibrium_m": None if r_eq is None else 2 * r_eq, "t_to_equilibrium_s": t_eq,
            "samples": samples, "final": {"t_s": t, "radius_m": y[0], "front_speed_m_s": y[1], "volume_m3": y[2]},
            "notes": ["Webber integral model as quoted by Basha et al. (2013); C_T is an input.",
                      "Flat impermeable ground, no ground heat, no bund; stopped at the first time the radius reaches the burn-off radius."]}
