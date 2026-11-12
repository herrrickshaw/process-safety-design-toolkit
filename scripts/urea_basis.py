"""urea_basis.py - shared basis for the coal-to-urea unit-by-unit package: the Rev B balance (gen_pid_urea.py) scaled to the
Talcher-class nameplate, 3,850 t/d urea. Every flow is Rev B x K (D); the Rev B model is linear in coal feed."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_pid_urea as g
from pid_unit import St

URATE_TPD = 3850.0
K = URATE_TPD / g.UREA_TPD
assert abs(g.M[22] * 3.6 * K * 24 - URATE_TPD) < 1e-6


def stream(i, name, phase, T=None, P=None, rho=None, drop_water=False, flow=None, base=None):
    """St for sheet stream number i. base = Rev B stream whose composition/conditions/flow are used (default i);
    flow in t/h overrides the scaled Rev B flow; T (C), P (bar) override the Rev B conditions."""
    b = i if base is None else base
    t = float(g.TP[b][0][0]) if T is None else T
    p = float(g.TP[b][1][0]) if P is None else P
    sp = {k: v for k, v in g.S[b].items() if not (drop_water and k == "H2O")}
    mol = sum(sp.values())
    mw = g.mass(sp) / mol * 1000 if mol else 18.0
    f = g.M[b] * 3.6 * K if flow is None else flow
    return St(i, name, phase, f, t, p, mw=mw, rho=rho)


def simple(i, name, phase, flow_t_h, T, P, mw=None, rho=None):
    """a utility or new stream outside the Rev B balance (flow, T, P and mw/rho must be given, tag A unless the area file says otherwise)"""
    return St(i, name, phase, flow_t_h, T, P, mw=mw, rho=rho)
