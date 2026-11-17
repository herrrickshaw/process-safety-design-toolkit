"""Step 4 - risk calculation and integration: location-specific individual risk (LSIR) on a grid, LSIR / IRPA at receptors,
societal risk (F-N events, PLL), and per-scenario contributions.

For each LOC scenario s, outcome o, weather w and wind sector d:  f = f_s x P(o|s) x P(w) x P(d)  and
    LSIR(x, y)  += f x p_o(x, y)                              (outdoor, permanently present person)
    N_event      = sum_i people_i x p_o(x_i, y_i) x v_i,o     (expected fatalities for that event; v = indoor/outdoor vulnerability)
    PLL          = sum f x N_event
Weather-independent radial outcomes (fires, fireballs) are integrated once with weight 1 because sum(P(w) P(d)) = 1.
Wind rose: probability the wind blows FROM each sector (equal sectors centred on north, clockwise); x = east, y = north.
Each sector is split into equal-weight sub-directions: at least `sector_subdivisions` (default 12) and adaptively more for thin
plumes (angular step <= a third of the narrowest footprint's angular width, max 90 per sector) so the sector is covered, not sampled by one ray.

Consistency identity checked after every run: PLL from the F-N events equals sum_i people_i x (vulnerability-weighted LSIR at i).
"""
from __future__ import annotations

import math

from .progress import Progress


def vulnerability(kind: str, pop: dict, indoor_vuln: dict) -> float:
    f_in = pop.get("indoor_fraction", 0.0)
    return (1 - f_in) + f_in * indoor_vuln.get(kind, 1.0)


class Grid:
    def __init__(self, x_min, x_max, y_min, y_max, step):
        self.step = step
        self.xs = [x_min + i * step for i in range(int(round((x_max - x_min) / step)) + 1)]
        self.ys = [y_min + j * step for j in range(int(round((y_max - y_min) / step)) + 1)]
        self.ir = [[0.0] * len(self.xs) for _ in self.ys]

    @property
    def cells(self):
        return len(self.xs) * len(self.ys)

    def index_range(self, lo, hi, axis):
        arr = self.xs if axis == 0 else self.ys
        a0, s = arr[0], self.step
        i0 = max(0, int(math.ceil((lo - a0) / s)))
        i1 = min(len(arr) - 1, int(math.floor((hi - a0) / s)))
        return i0, i1


def _local(X, Y, sin_t, cos_t):
    """World offset (X east, Y north) -> (downwind, crosswind) for a wind blowing TOWARD bearing t."""
    return X * sin_t + Y * cos_t, X * cos_t - Y * sin_t


def _aabb(e, sx, sy, sin_t, cos_t):
    if not e.directional:
        r = e.reach
        return sx - r, sx + r, sy - r, sy + r
    corners = [(-e.x_back, -e.half_width), (-e.x_back, e.half_width), (e.reach, -e.half_width), (e.reach, e.half_width)]
    pts = [(sx + dx * sin_t + dy * cos_t, sy + dx * cos_t - dy * sin_t) for dx, dy in corners]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def subdivisions(e, sector_deg: float, min_sub: int, max_sub: int = 90) -> int:
    """Sub-directions for one footprint: at least min_sub, and enough that the angular step is <= 1/3 of the narrowest directional
    part's angular width (a 50 m wide plume at 750 m spans ~4 deg, so a 45 deg sector needs ~35 rays to be sampled without gaps)."""
    parts = [p for p in getattr(e, "parts", [e]) if p.directional and p.reach > 0]
    if not parts:
        return min_sub
    ang = min(math.degrees(2 * math.atan2(max(p.half_width, 1e-6), p.reach)) for p in parts)
    return int(min(max_sub, max(min_sub, math.ceil(sector_deg / (ang / 3)))))


def enumerate_events(scenarios, weather, rose, cache_builder, sub=12):
    """Yield (scenario, outcome, weather or None, bearing_toward or None, frequency, effect). Effects are built once per
    (scenario, outcome, weather) via cache_builder; each wind sector is split into subdivisions(effect) rays of equal weight."""
    n_dir = len(rose)
    width = 360.0 / n_dir
    for s in scenarios:
        for o in s["branches"]:
            f_so = s["frequency_per_yr"] * o["prob"]
            if f_so <= 0:
                continue
            if not o["weather_dependent"]:
                e = cache_builder(s, o, None)
                if e is not None:
                    yield s, o, None, None, f_so, e
                continue
            for w in weather:
                e = cache_builder(s, o, w)
                if e is None:
                    continue
                n = subdivisions(e, width, sub)
                for d, pd in enumerate(rose):
                    if pd <= 0:
                        continue
                    for k in range(n):
                        frm = d * width - width / 2 + (k + 0.5) * width / n
                        yield s, o, w, (frm + 180.0) % 360.0, f_so * w["p"] * pd / n, e


def prebuild(scenarios, weather, cache_builder, progress=True, label="footprints"):
    keys = [(s, o, w) for s in scenarios for o in s["branches"] if s["frequency_per_yr"] * o["prob"] > 0
            for w in (weather if o["weather_dependent"] else [None])]
    prog = Progress(len(keys), label, enabled=progress)
    for s, o, w in keys:
        cache_builder(s, o, w)
        prog.update()
    prog.done()


def count_events(scenarios, weather, rose, sub=12, cache_builder=None):
    """Exact event count when footprints are available (cache_builder), else the minimum (sub rays per sector)."""
    n = 0
    nd = sum(1 for p in rose if p > 0)
    width = 360.0 / len(rose)
    for s in scenarios:
        for o in s["branches"]:
            if s["frequency_per_yr"] * o["prob"] <= 0:
                continue
            if not o["weather_dependent"]:
                n += 1 if (cache_builder is None or cache_builder(s, o, None) is not None) else 0
                continue
            for w in weather:
                if cache_builder is None:
                    n += nd * sub
                else:
                    e = cache_builder(s, o, w)
                    n += 0 if e is None else nd * subdivisions(e, width, sub)
    return n


def integrate(scenarios, weather, rose, grid: Grid, receptors, population, indoor_vuln, build_effect, progress=True,
              label="risk integration", sub=12) -> dict:
    cache = {}

    def cached(s, o, w):
        key = (s["id"], o["outcome"], w["name"] if w else None)
        if key not in cache:
            cache[key] = build_effect(s, o, w)
        return cache[key]

    prebuild(scenarios, weather, cached, progress, (label + ": footprints")[:22])
    total = count_events(scenarios, weather, rose, sub, cached)
    prog = Progress(total, label, enabled=progress)

    rec_ir = {r["name"]: 0.0 for r in receptors}
    pop_irv = {p["name"]: 0.0 for p in population}
    fn_events = []
    contrib = {}
    by_outcome = {}
    n_events = 0
    for s, o, w, toward, f, e in enumerate_events(scenarios, weather, rose, cached, sub):
        n_events += 1
        kind = o["outcome"].split("+")[0]
        t = math.radians(toward) if toward is not None else 0.0
        sin_t, cos_t = math.sin(t), math.cos(t)
        sx, sy = s["x"], s["y"]
        # grid
        x0, x1, y0, y1 = _aabb(e, sx, sy, sin_t, cos_t)
        i0, i1 = grid.index_range(x0, x1, 0)
        j0, j1 = grid.index_range(y0, y1, 1)
        for j in range(j0, j1 + 1):
            Y = grid.ys[j] - sy
            row = grid.ir[j]
            for i in range(i0, i1 + 1):
                X = grid.xs[i] - sx
                dx, dy = _local(X, Y, sin_t, cos_t)
                p = e.p(dx, dy)
                if p > 0:
                    row[i] += f * p
        # receptors (LSIR at the point)
        c = contrib.setdefault(s["id"], {"pll": 0.0, "receptor_ir": {r["name"]: 0.0 for r in receptors}})
        for r in receptors:
            dx, dy = _local(r["x"] - sx, r["y"] - sy, sin_t, cos_t)
            p = e.p(dx, dy)
            if p > 0:
                rec_ir[r["name"]] += f * p
                c["receptor_ir"][r["name"]] += f * p
        # societal
        N = 0.0
        for pp in population:
            dx, dy = _local(pp["x"] - sx, pp["y"] - sy, sin_t, cos_t)
            p = e.p(dx, dy)
            if p > 0:
                v = vulnerability(kind, pp, indoor_vuln)
                N += pp["people"] * p * v
                pop_irv[pp["name"]] += f * p * v
        if N > 0:
            fn_events.append((f, N, s["id"], o["outcome"]))
            c["pll"] += f * N
        bo = by_outcome.setdefault(o["outcome"].split("+")[0], {"frequency_per_yr": 0.0, "pll": 0.0})
        bo["frequency_per_yr"] += f
        bo["pll"] += f * N
        prog.update()
    elapsed = prog.done()
    pll = sum(f * N for f, N, *_ in fn_events)
    pll_alt = sum(pp["people"] * pop_irv[pp["name"]] for pp in population)
    return {"grid": grid, "receptor_lsir": rec_ir, "population_weighted_ir": pop_irv, "fn_events": fn_events, "pll": pll,
            "pll_check": pll_alt, "contributions": contrib, "by_outcome": by_outcome, "events": n_events, "elapsed_s": elapsed,
            "effects_built": len(cache), "effects": cache}


def fn_curve(fn_events, n_points=None) -> list[tuple[float, float]]:
    """Cumulative F(N >= n) evaluated at n = 1, 2, 3, ... up to the largest event N (log-spaced above 10)."""
    if not fn_events:
        return []
    nmax = max(N for _, N, *_ in fn_events)
    ns, n = [], 1.0
    while n <= nmax:
        ns.append(n)
        n = n + 1 if n < 10 else n * 1.25
    ev = sorted(fn_events, key=lambda e: -e[1])
    out = []
    for n in ns:
        out.append((n, sum(f for f, N, *_ in ev if N >= n)))
    return out


def max_ir(grid: Grid) -> tuple[float, float, float]:
    best = (0.0, 0.0, 0.0)
    for j, row in enumerate(grid.ir):
        for i, v in enumerate(row):
            if v > best[0]:
                best = (v, grid.xs[i], grid.ys[j])
    return best


def contour_distance(grid: Grid, level: float, sx: float = 0.0, sy: float = 0.0) -> float:
    """Largest distance from (sx, sy) of any grid cell with LSIR >= level (0 if none) - a simple contour-extent metric."""
    d = 0.0
    for j, row in enumerate(grid.ir):
        for i, v in enumerate(row):
            if v >= level:
                d = max(d, math.hypot(grid.xs[i] - sx, grid.ys[j] - sy))
    return d
