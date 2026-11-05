"""SIL lifecycle beyond LOPA: SIL from RRF, calibrated risk graph, SIF verification (PFDavg + architectural constraints +
spurious trip rate), proof-test interval check, and a safety requirements specification (SRS) skeleton.

Verified tables (public copies, 2026-11-05):
* IEC 61511-1:2016 + COR1 Table 6, minimum HFT: SIL 1 -> 0; SIL 2 low demand -> 0; SIL 2 high/continuous -> 1; SIL 3 -> 1; SIL 4 -> 2.
* IEC 61508-2 Route 1H maximum SIL by safe failure fraction (SFF) and HFT, type A and type B elements (exida / PR electronics copies).
* RRF -> SIL bands: >10-100 SIL 1, >100-1000 SIL 2, >1000-10000 SIL 3, >10000-100000 SIL 4 (low demand).
HFT of an MooN group = N - M. SFF = (lambda_s + lambda_dd) / (lambda_s + lambda_dd + lambda_du).

Risk graph: the parameter definitions (C, F, P, W) and the SIL each path gives MUST be calibrated to the company's tolerable risk;
the toolkit only evaluates the calibrated table you supply (key "C2-F1-P2-W3" -> "a" | "-" | "SIL 1".. | "b").

Spurious trip rates use the common simplified forms (ISA TR84.00.02 style; independent channels, repair time MTTR):
    1oo1: ls   1oo2: 2 ls   2oo2: 2 ls^2 MTTR   2oo3: 6 ls^2 MTTR   (ls = lambda_s + lambda_dd: safe + detected-dangerous that trip)
"""
from __future__ import annotations

import math

from . import sil

HFT_TABLE6 = {1: 0, 2: 0, 3: 1, 4: 2}
HFT_TABLE6_HIGH_DEMAND = {1: 0, 2: 1, 3: 1, 4: 2}
# Route 1H: rows SFF band, columns HFT 0/1/2 -> max SIL (0 = not allowed)
ROUTE_1H = {"A": [(0.60, (1, 2, 3)), (0.90, (2, 3, 4)), (0.99, (3, 4, 4)), (1.01, (3, 4, 4))],
            "B": [(0.60, (0, 1, 2)), (0.90, (1, 2, 3)), (0.99, (2, 3, 4)), (1.01, (3, 4, 4))]}


def sil_from_rrf(rrf: float) -> int:
    if rrf <= 10:
        return 0
    for s, hi in ((1, 100), (2, 1000), (3, 10000), (4, 100000)):
        if rrf <= hi:
            return s
    return 5  # > SIL 4: not achievable by one SIF - redesign


def hft_of(arch: str) -> int:
    m, n = arch.lower().split("oo")
    return int(n) - int(m)


def sff(lambda_s: float, lambda_dd: float, lambda_du: float) -> float:
    tot = lambda_s + lambda_dd + lambda_du
    return (lambda_s + lambda_dd) / tot if tot > 0 else 0.0


def route_1h_max_sil(element_type: str, sff_value: float, hft: int) -> int:
    for ub, sils in ROUTE_1H[element_type.upper()]:
        if sff_value < ub:
            return sils[min(hft, 2)]
    return ROUTE_1H[element_type.upper()][-1][1][min(hft, 2)]


def spurious_trip_rate_per_h(arch: str, lambda_safe_trip_per_h: float, mttr_h: float = 8.0) -> float:
    ls = lambda_safe_trip_per_h
    return {"1oo1": ls, "1oo2": 2 * ls, "2oo2": 2 * ls * ls * mttr_h, "2oo3": 6 * ls * ls * mttr_h}[arch.lower()]


def risk_graph(path: dict, calibration: dict) -> str:
    """path = {"C": 2, "F": 1, "P": 2, "W": 3}; calibration maps 'C2-F1-P2-W3' -> outcome. Missing keys are an error, not a guess."""
    key = f"C{path['C']}-F{path.get('F', 1)}-P{path.get('P', 1)}-W{path['W']}"
    if key not in calibration:
        raise KeyError(f"risk graph path {key} not in the calibrated table - calibrate it, do not guess")
    return calibration[key]


def verify_sif(sif: dict) -> dict:
    """sif = {"name", "target_sil" or "target_rrf", "demand": "low"|"high", "proof_test_h", "mttr_h",
              "subsystems": [{"name", "arch", "type": "A"|"B", "lambda_du", "lambda_dd", "lambda_s" (per h), "beta", "proof_test_h"?,
                              "route": "1H"|"2H" (default 2H = IEC 61511 Table 6)}]}"""
    target = sif.get("target_sil") or sil_from_rrf(sif["target_rrf"])
    high = sif.get("demand", "low") == "high"
    rows, pfd_tot, str_tot = [], 0.0, 0.0
    arch_sil = 4
    for ss in sif["subsystems"]:
        ti = ss.get("proof_test_h", sif["proof_test_h"])
        pfd = sil.pfd_avg(ss["arch"], ss["lambda_du"], ti, ss.get("beta", 0.0))
        h = hft_of(ss["arch"])
        f = sff(ss.get("lambda_s", 0.0), ss.get("lambda_dd", 0.0), ss["lambda_du"])
        if ss.get("route", "2H") == "1H":
            cap = route_1h_max_sil(ss.get("type", "B"), f, h)
        else:
            table = HFT_TABLE6_HIGH_DEMAND if high else HFT_TABLE6
            cap = max([s for s, need in table.items() if h >= need], default=0)
        arch_sil = min(arch_sil, cap)
        st = spurious_trip_rate_per_h(ss["arch"], ss.get("lambda_s", 0.0) + ss.get("lambda_dd", 0.0), sif.get("mttr_h", 8.0)) if ss["arch"].lower() in ("1oo1", "1oo2", "2oo2", "2oo3") else float("nan")
        str_tot += 0 if math.isnan(st) else st
        pfd_tot += pfd
        rows.append({"subsystem": ss["name"], "arch": ss["arch"], "HFT": h, "SFF": f, "PFDavg": pfd, "route": ss.get("route", "2H"),
                     "max_SIL_by_architecture": cap, "spurious_trip_per_yr": st * 8760})
    pfd_sil = int(sil.sil_for_pfd(pfd_tot).split()[1]) if sil.sil_for_pfd(pfd_tot).startswith("SIL") and sil.sil_for_pfd(pfd_tot)[4].isdigit() else 0
    achieved = min(pfd_sil, arch_sil)
    return {"name": sif["name"], "target_SIL": target, "PFDavg": pfd_tot, "RRF": 1 / pfd_tot if pfd_tot else math.inf,
            "SIL_by_PFD": pfd_sil, "SIL_by_architecture": arch_sil, "SIL_achieved": achieved, "meets_target": achieved >= target,
            "spurious_trips_per_yr": str_tot * 8760, "MTTF_spurious_yr": 1 / (str_tot * 8760) if str_tot else math.inf, "subsystems": rows,
            "notes": "Systematic capability (SC), proof-test coverage, diagnostics and common cause beyond beta are not assessed."}


SRS_ITEMS = [
    "SIF tag and description", "Hazardous event / LOPA scenario reference", "Safe state of the process", "Initiating sensors, trip set points, ranges",
    "Logic (voting, permissives, timers)", "Final elements and their safe positions", "Process safety time and required response time",
    "Target SIL / PFDavg / RRF and demand mode", "Proof-test interval and test procedure reference", "Bypass / override requirements and alarms",
    "Manual shutdown and reset requirements", "Behaviour on loss of utilities (power, air) and on detected faults", "Maximum spurious trip rate allowed",
    "Interfaces with BPCS / operator (alarms, HMI)", "Environmental and hazardous-area requirements", "Common-cause and independence considerations",
    "Application program requirements", "Requirements for start-up, restart and maintenance", "Verification and validation requirements",
]


def srs_skeleton(sif: dict, verification: dict | None = None) -> list[dict]:
    """Row-per-item SRS skeleton (a checklist in the spirit of IEC 61511-1 cl. 10.3; the clause text was not read - complete per it)."""
    known = {"SIF tag and description": sif.get("name", ""), "Target SIL / PFDavg / RRF and demand mode":
             f"SIL {verification['target_SIL']} target, achieved SIL {verification['SIL_achieved']}, PFDavg {verification['PFDavg']:.2e}, {sif.get('demand', 'low')} demand" if verification else "",
             "Proof-test interval and test procedure reference": f"{sif.get('proof_test_h', '')} h" if sif.get("proof_test_h") else ""}
    return [{"item": i, "requirement": known.get(i, sif.get("srs", {}).get(i, "")), "status": "draft" if known.get(i) or sif.get("srs", {}).get(i) else "TO COMPLETE"}
            for i in SRS_ITEMS]
