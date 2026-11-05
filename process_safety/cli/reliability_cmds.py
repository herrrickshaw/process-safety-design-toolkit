"""Functional-safety commands."""
from __future__ import annotations

from .. import sil
from .registry import command, emit


@command("lopa")
class Lopa:
    ranges = {"ie": "frequency_per_yr", "ipl": "pfd", "target": "frequency_per_yr", "modifier": "fraction_0_1"}

    @staticmethod
    def add_arguments(lo):
        lo.add_argument("--ie", type=float, required=True, help="initiating event freq /yr")
        lo.add_argument("--ipl", type=float, nargs="*", default=[], help="PFD of each independent protection layer")
        lo.add_argument("--target", type=float, required=True, help="tolerable frequency /yr")
        lo.add_argument("--modifier", type=float, default=1.0)

    @staticmethod
    def run(a, p):
        emit(sil.lopa(a.ie, a.ipl, a.target, a.modifier))


@command("pfd")
class Pfd:
    ranges = {"lambda_du": "failure_rate_per_h", "ti_years": "proof_test_years", "beta": "beta_factor"}

    @staticmethod
    def add_arguments(pf):
        pf.add_argument("--arch", choices=["1oo1", "1oo2", "2oo2", "2oo3"], required=True)
        pf.add_argument("--lambda-du", type=float, required=True, help="per hour")
        pf.add_argument("--ti-years", type=float, required=True)
        pf.add_argument("--beta", type=float, default=0.0)

    @staticmethod
    def run(a, p):
        v = sil.pfd_avg(a.arch, a.lambda_du, a.ti_years * 8760, a.beta)
        emit({"pfd_avg": v, "rrf": 1 / v, "achieves": sil.sil_for_pfd(v)})
