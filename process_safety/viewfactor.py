"""Solid-flame radiation: view factor from a planar rectangular flame face to a small target, by numerical integration.

The view factor of a differential target element dA1 to an emitting area A2 is F = (1/pi) * integral of cos(t1) cos(t2) / r^2 dA2.
It is integrated here with a midpoint rule over the emitter, so no tabulated closed form is needed; the tests compare it with the
exact result for a differential element parallel to a rectangle (Howell) and with the coaxial disc result F = R^2 / (R^2 + h^2).

Incident flux on the target = transmissivity * SEP * F. This replaces the point-source model when the target is close to the
flame (inside ~2-3 flame diameters), where point-source results are unreliable. A real flame is a tilted cylinder or cone; a tilted
flame is approximated here by supplying the flame face you want (one or more rectangles, summed with `flux_from_faces`).
SEP and transmissivity are inputs. Blocked line of sight (other equipment) is not checked.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

Vec = tuple[float, float, float]


def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a: Vec) -> Vec:
    n = math.sqrt(_dot(a, a))
    if n == 0:
        raise ValueError("zero-length vector")
    return (a[0] / n, a[1] / n, a[2] / n)


@dataclass(frozen=True)
class Face:
    """A flat rectangular emitting face: a corner, two edge vectors, radiating toward `normal` (set automatically from the edges)."""
    corner: Vec
    edge_u: Vec
    edge_v: Vec

    @property
    def normal(self) -> Vec:
        return _unit(_cross(self.edge_u, self.edge_v))

    def area(self) -> float:
        n = _cross(self.edge_u, self.edge_v)
        return math.sqrt(_dot(n, n))


def view_factor(target: Vec, target_normal: Vec, face: Face, n: int = 200, two_sided: bool = False) -> float:
    """F from a differential target (position, outward normal) to `face`. The face emits toward its +normal side only unless two_sided.

    Midpoint integration over n x n cells; the error falls roughly with 1/n^2 (n=200 is about 1e-4 absolute for ordinary geometry,
    worse when the target sits within a cell width of the face).
    """
    tn = _unit(target_normal)
    fn = face.normal
    area = face.area()
    cell = area / (n * n)
    total = 0.0
    for i in range(n):
        su = (i + 0.5) / n
        for j in range(n):
            sv = (j + 0.5) / n
            p = (face.corner[0] + su * face.edge_u[0] + sv * face.edge_v[0],
                 face.corner[1] + su * face.edge_u[1] + sv * face.edge_v[1],
                 face.corner[2] + su * face.edge_u[2] + sv * face.edge_v[2])
            d = _sub(p, target)                       # target -> emitter point
            r2 = _dot(d, d)
            if r2 == 0:
                continue
            r = math.sqrt(r2)
            c1 = _dot(tn, d) / r                       # cosine at the target
            c2 = -_dot(fn, d) / r                      # cosine at the emitter (positive if the face looks at the target)
            if two_sided:
                c2 = abs(c2)
            if c1 > 0 and c2 > 0:
                total += c1 * c2 / r2 * cell
    return total / math.pi


def flux_from_faces(target: Vec, target_normal: Vec, faces: list[Face], sep_kW_m2: float, tau: float = 1.0, n: int = 200) -> dict:
    """Incident flux (kW/m2) = tau * SEP * sum of view factors of the faces."""
    if sep_kW_m2 <= 0 or not 0 < tau <= 1:
        raise ValueError("SEP must be positive and tau in (0, 1]")
    fs = [view_factor(target, target_normal, f, n) for f in faces]
    F = sum(fs)
    return {"view_factor": F, "view_factors": fs, "incident_kW_m2": tau * sep_kW_m2 * F, "tau": tau, "sep_kW_m2": sep_kW_m2}


def vertical_flame_face(width_m: float, height_m: float, distance_m: float, lateral_offset_m: float = 0.0, base_height_m: float = 0.0) -> Face:
    """A vertical rectangular flame face in the plane x = 0 facing -x, seen by a target at x = -distance, y = 0, z = 0.

    The face spans y in [-w/2 + offset, w/2 + offset] and z in [base, base + height]. Use target = (-distance, 0, 0) with normal
    (+1, 0, 0) for a vertical target facing the flame. The edge order makes the face normal point toward -x.
    """
    if min(width_m, height_m, distance_m) <= 0:
        raise ValueError("width, height and distance must be positive")
    return Face(corner=(0.0, lateral_offset_m + width_m / 2, base_height_m), edge_u=(0.0, -width_m, 0.0), edge_v=(0.0, 0.0, height_m))
