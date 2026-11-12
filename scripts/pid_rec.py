"""pid_rec.py - optional symbol recorder for the drawing library (stdlib only; off by default).

When enabled, every pidlib symbol drawn (valve, relief valve, instrument bubble, pump, compressor, vessel, tank, reactor) and every glyph a generator reports with
rec() is stored with its bounding box in sheet units (1600 x 1130), so the sheets can be rendered and used as exactly labelled detector training images.
Classes follow the PID2Graph/OPEN100 node labels used by the detector: valve, instrumentation, tank, pump. Nothing is recorded unless install() is called."""
import sys, importlib

ENABLED = False
BOXES = {}          # id(sheet) -> list of (cls, x0, y0, x1, y1)
_ORIG = {}


def rec(sh, cls, x0, y0, x1, y1):
    if ENABLED: BOXES.setdefault(id(sh), []).append((cls, round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)))


def _valve_box(x, y, rot=0, kind="gate", act=False):
    w, h = (18, 14) if kind == "check" else (22, 14)
    ext = 24 if act else 0                              # actuator stem and diaphragm above the body (before rotation)
    if rot % 180 == 90:                                 # rotated: body h wide and w tall; SVG rotate(90) sends the actuator (up) to the right, rotate(270) to the left
        right = ext if rot % 360 == 90 else 0; left = ext if rot % 360 == 270 else 0
        return x - h / 2 - left, y - w / 2, x + h / 2 + right, y + w / 2
    return x - w / 2, y - h / 2 - ext, x + w / 2, y + h / 2


def install():
    """wrap the symbol functions in pidlib and in every module that imported them with `from pidlib import *`"""
    global ENABLED
    import pidlib
    ENABLED = True
    spec = {
        "valve": ("valve", lambda a, k: _valve_box(*a[1:6], **{kk: vv for kk, vv in k.items() if kk in ("rot", "kind", "act")})),
        "psv": ("valve", lambda a, k: (a[1] - 10, a[2] - 31, a[1] + 18, a[2] + 16)),
        "bubble": ("instrumentation", lambda a, k: (a[1] - k.get("r", a[7] if len(a) > 7 else 15), a[2] - k.get("r", a[7] if len(a) > 7 else 15),
                                                    a[1] + k.get("r", a[7] if len(a) > 7 else 15), a[2] + k.get("r", a[7] if len(a) > 7 else 15))),
        "pump": ("pump", lambda a, k: (a[1] - k.get("r", a[3] if len(a) > 3 else 14), a[2] - k.get("r", a[3] if len(a) > 3 else 14) - 2,
                                       a[1] + k.get("r", a[3] if len(a) > 3 else 14), a[2] + k.get("r", a[3] if len(a) > 3 else 14))),
        "compressor": ("pump", lambda a, k: (a[1] - k.get("r", a[3] if len(a) > 3 else 17), a[2] - k.get("r", a[3] if len(a) > 3 else 17),
                                             a[1] + k.get("r", a[3] if len(a) > 3 else 17), a[2] + k.get("r", a[3] if len(a) > 3 else 17))),
        "vvessel": ("tank", lambda a, k: (a[1] - a[3] / 2, a[2] - a[3] * 0.28, a[1] + a[3] / 2, a[2] + a[4] + a[3] * 0.28)),
        "hvessel": ("tank", lambda a, k: (a[1] - a[3] / 2 - a[4] * 0.3, a[2] - a[4] / 2, a[1] + a[3] / 2 + a[4] * 0.3, a[2] + a[4] / 2 + a[4] * 0.25)),
        "tank": ("tank", lambda a, k: (a[1] - a[3] / 2 - 6, a[2] - a[4] * 1.14, a[1] + a[3] / 2 + 6, a[2])),
        "reactor": ("tank", lambda a, k: (a[1] - a[3] / 2, a[2] - a[4] / 2 - a[3] * 0.2, a[1] + a[3] / 2, a[2] + a[4] / 2 + a[3] * 0.2)),
    }
    for name, (cls, boxf) in spec.items():
        orig = getattr(pidlib, name); _ORIG[name] = orig

        def make(orig=orig, cls=cls, boxf=boxf):
            def wrapped(*a, **k):
                try:
                    b = boxf(a, k)
                    if b: rec(a[0], cls, *b)
                except Exception: pass
                return orig(*a, **k)
            wrapped.__name__ = orig.__name__
            return wrapped
        w = make()
        setattr(pidlib, name, w)
        for mname, mod in list(sys.modules.items()):
            if mod is not None and getattr(mod, name, None) is orig: setattr(mod, name, w)
