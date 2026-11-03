"""LOPA and SIL: required risk reduction (CCPS LOPA / IEC 61511) and PFDavg of a safety instrumented function.

PFDavg uses the simplified IEC 61508-6 low-demand equations (dangerous undetected failures only, no diagnostics or repair time,
beta common-cause factor). They are the usual hand-calc screening forms; a SIL verification report must also check
architectural constraints (hardware fault tolerance / SFF, IEC 61511-1 cl.11.4), systematic capability and proof-test coverage -
NOT implemented here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# Typical generic IPL PFDs (CCPS LOPA book values commonly quoted). Replace with site data; independence must be demonstrated.
GENERIC_IPL_PFD = {
    "bpcs_loop": 1e-1, "operator_response_alarm": 1e-1, "relief_valve": 1e-2, "rupture_disk": 1e-2,
    "dike": 1e-2, "check_valve": 1e-1, "flame_arrestor": 1e-2,
}

SIL_BANDS = [(4, 1e-5, 1e-4), (3, 1e-4, 1e-3), (2, 1e-3, 1e-2), (1, 1e-2, 1e-1)]  # (SIL, PFD lo, PFD hi), low demand


def sil_for_pfd(pfd: float) -> str:
    """SIL achieved by a PFDavg (low demand mode)."""
    if pfd >= 1e-1:
        return "below SIL 1"
    for sil, lo, hi in SIL_BANDS:
        if lo * (1 - 1e-9) <= pfd < hi * (1 - 1e-9):
            return f"SIL {sil}"
    return "SIL 4 or better (>SIL 4 not claimable)"


@dataclass
class LopaResult:
    unmitigated_per_yr: float
    mitigated_per_yr: float
    tolerable_per_yr: float
    required_pfd: float
    required_rrf: float
    sil_needed: str
    meets_target_without_sif: bool


def lopa(initiating_freq_per_yr: float, ipl_pfds: list[float], tolerable_per_yr: float,
         conditional_modifiers: float = 1.0) -> LopaResult:
    """Scenario frequency = IE x prod(IPL PFDs) x conditional modifiers (ignition, occupancy, fatality...).
    Required SIF PFD = tolerable / mitigated-without-SIF."""
    unmit = initiating_freq_per_yr * conditional_modifiers
    mit = unmit * math.prod(ipl_pfds)
    req = tolerable_per_yr / mit
    return LopaResult(unmit, mit, tolerable_per_yr, min(req, 1.0), max(1.0, 1 / req),
                      "no SIF needed" if req >= 1 else sil_for_pfd(req), req >= 1)


def pfd_avg(arch: str, lambda_du_per_h: float, proof_test_h: float, beta: float = 0.0) -> float:
    """Simplified IEC 61508-6 PFDavg. arch in 1oo1, 1oo2, 2oo2, 2oo3. beta = common-cause fraction (0-1)."""
    x = lambda_du_per_h * proof_test_h
    ind = (1 - beta) * x
    ccf = beta * x / 2
    if arch == "1oo1":
        return x / 2
    if arch == "2oo2":
        return x
    if arch == "1oo2":
        return ind ** 2 / 3 + ccf
    if arch == "2oo3":
        return ind ** 2 + ccf
    raise ValueError(f"unsupported architecture {arch!r}")


def sif_pfd(subsystems: dict[str, float]) -> tuple[float, str]:
    """Sensor + logic solver + final element PFDs add (IEC 61511 series reliability)."""
    total = sum(subsystems.values())
    return total, sil_for_pfd(total)


def max_proof_test_interval_h(arch: str, lambda_du_per_h: float, target_pfd: float, beta: float = 0.0) -> float:
    """Longest proof-test interval that still meets target_pfd (bisection; PFDavg is monotone in TI)."""
    lo, hi = 1.0, 1e7
    if pfd_avg(arch, lambda_du_per_h, hi, beta) <= target_pfd:
        return hi
    for _ in range(100):
        mid = (lo + hi) / 2
        if pfd_avg(arch, lambda_du_per_h, mid, beta) > target_pfd:
            hi = mid
        else:
            lo = mid
    return lo
