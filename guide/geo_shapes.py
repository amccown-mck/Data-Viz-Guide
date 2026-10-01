"""Map geometry for the guide's geo-spatial exhibits: a small TopoJSON reader, projections and drawing helpers.

No geopandas or shapely. The files in guide/geodata/ (sources and licenses in the README there):
- states-albers-10m.json    us-atlas states, already projected to Albers USA (975 x 610, y down; AK and HI inset)
- counties-north-texas.json a subset of us-atlas counties (same projection) around Dallas-Fort Worth
- countries-110m.json       world-atlas countries in lon/lat; projected here to Equal Earth

Everything is drawn in pixel coordinates (an axes whose data units are the figure's px; see canvas()). Arcs are
projected, simplified once (shared borders stay shared) and rounded to 0.1 px, which keeps the inline SVG small.
Not named ex_*.py, so exhibits.py does not import it as an exhibit module.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

GEO = Path(__file__).resolve().parent / "geodata"
RAD = np.pi / 180

# Public city locations (lon, lat) for site markers. Reference geography, not data.
CITY = {"Memphis": (-90.05, 35.15), "Dallas": (-96.80, 32.78), "Columbus": (-82.99, 39.96),
        "Atlanta": (-84.39, 33.75), "Phoenix": (-112.07, 33.45), "Sacramento": (-121.49, 38.58),
        "Harrisburg": (-76.88, 40.27), "Chicago": (-87.63, 41.88), "Kansas City": (-94.58, 39.10),
        "Orlando": (-81.38, 28.54), "Denver": (-104.99, 39.74), "Seattle": (-122.33, 47.61),
        "Albany": (-73.76, 42.65), "Boise (satellite)": (-116.20, 43.62), "Irving": (-96.95, 32.81),
        "Fort Worth": (-97.33, 32.75)}

FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
        "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
        "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
        "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
        "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
        "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}


# ------------------------------------------------------------------ TopoJSON
class Topo:
    """Decode a quantized TopoJSON file: delta-encoded integer arcs -> absolute coordinates."""

    def __init__(self, name: str):
        t = json.loads((GEO / name).read_text(encoding="utf-8"))
        (sx, sy), (tx, ty) = t["transform"]["scale"], t["transform"]["translate"]
        self.arcs = [np.cumsum(np.asarray(a, float), axis=0) * (sx, sy) + (tx, ty) for a in t["arcs"]]
        self.objects = t["objects"]

    def shapes(self, obj: str) -> dict:
        """{id: (name, polygons)}. A polygon is a list of rings; a ring is a list of arc refs (~i means reversed)."""
        out = {}
        for g in self.objects[obj]["geometries"]:
            if g["type"] not in ("Polygon", "MultiPolygon"):
                continue
            polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
            out[g.get("id")] = ((g.get("properties") or {}).get("name", ""), polys)
        return out


@lru_cache(maxsize=None)
def topo(name: str) -> Topo:
    return Topo(name)


def ring_coords(arcs: list, refs: list) -> np.ndarray:
    parts = []
    for k, i in enumerate(refs):
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        parts.append(a if k == 0 else a[1:])
    return np.concatenate(parts)


# ------------------------------------------------------------------ projections (lon/lat degrees -> plane)
def _conic(lon, lat, rot, par):
    """d3.geoConicEqualArea raw projection, longitude rotated by rot; returns (x, y) with y up."""
    p0, p1 = par[0] * RAD, par[1] * RAD
    n = (np.sin(p0) + np.sin(p1)) / 2
    c = 1 + np.sin(p0) * (2 * n - np.sin(p0))
    r0 = np.sqrt(c) / n
    lam = (np.asarray(lon) + rot) * RAD
    r = np.sqrt(c - 2 * n * np.sin(np.asarray(lat) * RAD)) / n
    return r * np.sin(lam * n), r0 - r * np.cos(lam * n)


def albers_usa(lon, lat):
    """Lower-48 part of d3.geoAlbersUsa().scale(1300).translate([487.5, 305]): the frame of the us-atlas files."""
    k = 1300
    x, y = _conic(lon, lat, 96, (29.5, 45.5))
    cx, cy = _conic(-0.6 - 96, 38.7, 96, (29.5, 45.5))          # d3 center [-0.6, 38.7] is in the rotated frame
    return 487.5 + k * (x - cx), 305 - k * (y - cy)


def equal_earth(lonlat: np.ndarray) -> np.ndarray:
    """Equal Earth (Savric, Patterson and Jenny 2018): equal-area, for world maps. Returns (x, y) with y up."""
    a1, a2, a3, a4 = 1.340264, -0.081106, 0.000893, 0.003796
    lam, phi = lonlat[:, 0] * RAD, lonlat[:, 1] * RAD
    th = np.arcsin(np.sqrt(3) / 2 * np.sin(phi))
    t2, t6 = th ** 2, th ** 6
    x = 2 * np.sqrt(3) * lam * np.cos(th) / (3 * (9 * a4 * t6 * t2 + 7 * a3 * t6 + 3 * a2 * t2 + a1))
    y = th * (a1 + a2 * t2 + t6 * (a3 + a4 * t2))
    return np.column_stack([x, y])


def mercator(lonlat: np.ndarray) -> np.ndarray:
    """Web Mercator, clipped at 82 degrees. Only for the 'try to avoid' example: it inflates high latitudes."""
    phi = np.clip(lonlat[:, 1], -82, 82) * RAD
    return np.column_stack([lonlat[:, 0] * RAD, np.log(np.tan(np.pi / 4 + phi / 2))])


def lonlat(xy: np.ndarray) -> np.ndarray:
    return xy


# ------------------------------------------------------------------ simplification
def simplify(pts: np.ndarray, tol: float) -> np.ndarray:
    """Douglas-Peucker, endpoints kept (so arcs shared by two areas still meet)."""
    n = len(pts)
    if n < 3 or tol <= 0:
        return pts
    keep = np.zeros(n, bool)
    keep[[0, -1]] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        seg = pts[i + 1:j]
        d = b - a
        L = np.hypot(*d)
        dist = np.abs(d[0] * (seg[:, 1] - a[1]) - d[1] * (seg[:, 0] - a[0])) / L if L > 0 else \
            np.hypot(seg[:, 0] - a[0], seg[:, 1] - a[1])
        k = int(np.argmax(dist))
        if dist[k] > tol:
            m = i + 1 + k
            keep[m] = True
            stack += [(i, m), (m, j)]
    return pts[keep]


def _clip_x(r: np.ndarray, x: float, left: bool) -> np.ndarray:
    """Sutherland-Hodgman clip of a closed ring to x <= x (left) or x >= x."""
    inside = (r[:, 0] <= x) if left else (r[:, 0] >= x)
    out = []
    for i in range(len(r) - 1):
        p, q, pi, qi = r[i], r[i + 1], inside[i], inside[i + 1]
        if pi:
            out.append(p)
        if pi != qi:
            t = (x - p[0]) / (q[0] - p[0])
            out.append(p + t * (q - p))
    if len(out) < 3:
        return np.empty((0, 2))
    return np.vstack(out + [out[0]])


def _split_antimeridian(ll: np.ndarray) -> list:
    """A lon/lat ring that jumps across +/-180: unwrap to 0..360, cut at 180, shift the far piece back."""
    u = ll.copy()
    u[:, 0] = np.where(u[:, 0] < 0, u[:, 0] + 360, u[:, 0])
    east, west = _clip_x(u, 180, True), _clip_x(u, 180, False)
    if len(west):
        west[:, 0] -= 360
    return [p for p in (east, west) if len(p) >= 4]


def _area(r: np.ndarray) -> float:
    return 0.5 * abs(np.dot(r[:-1, 0], r[1:, 1]) - np.dot(r[1:, 0], r[:-1, 1]))


# ------------------------------------------------------------------ the map
class Map:
    """A layer of areas drawn into a pixel box.

    project: source coords -> plane (y up), or None when the source is already projected (us-atlas, y down).
    box: (x, y, w, h) in figure px (y up). bounds: plane bounds to fit (default: the selected areas).
    tol: simplification tolerance in px. min_area: drop rings smaller than this (px^2), except each area's largest.
    key: renames ids before ids= filters them. transform: per-arc (index, coords) -> coords after projection.
    """

    def __init__(self, file: str, obj: str, box, *, project=None, ids=None, bounds=None, tol=0.45, min_area=0.0,
                 decimals=1, transform=None, key=None):
        t = topo(file)
        shapes = t.shapes(obj)
        if key is not None:                                        # e.g. FIPS "48" -> "TX"
            shapes = {key(k): v for k, v in shapes.items()}
        if ids is not None:
            shapes = {k: v for k, v in shapes.items() if k in ids}
        self.names = {k: v[0] for k, v in shapes.items()}
        self.refs = {k: v[1] for k, v in shapes.items()}
        used = sorted({r if r >= 0 else ~r for polys in self.refs.values() for poly in polys for ring in poly
                       for r in ring})
        flip = project is None
        plane = {i: (project(t.arcs[i]) if project else t.arcs[i]) for i in used}
        if transform is not None:                                  # optional per-arc override (e.g. AK/HI to lon/lat)
            plane = {i: transform(i, p) for i, p in plane.items()}
        if bounds is None:
            allp = np.concatenate(list(plane.values()))
            bounds = (*allp.min(0), *allp.max(0))
        x0, y0, x1, y1 = bounds
        bx, by, bw, bh = box
        s = min(bw / (x1 - x0), bh / (y1 - y0))
        ox, oy = bx + (bw - s * (x1 - x0)) / 2, by + (bh - s * (y1 - y0)) / 2
        self.s, self.flip, self.bounds = s, flip, bounds
        self._o = (ox, oy)

        def to_px(p):
            x = ox + (p[:, 0] - x0) * s
            y = oy + ((y1 - p[:, 1]) if flip else (p[:, 1] - y0)) * s
            return np.column_stack([x, y])

        self.to_px = to_px
        self.arcs = {i: np.round(simplify(to_px(p), tol), decimals) for i, p in plane.items()}
        self.rings = {}
        for k, polys in self.refs.items():
            rings = []
            for poly in polys:
                for ring in poly:
                    if project is not None:                        # lon/lat source: cut rings that cross 180 deg
                        ll = ring_coords(t.arcs, ring)
                        if np.any(np.abs(np.diff(ll[:, 0])) > 180):
                            rings += [np.round(simplify(to_px(project(p)), tol), decimals)
                                      for p in _split_antimeridian(ll)]
                            continue
                    rings.append(ring_coords(self.arcs, ring))
            rings = [r for r in rings if len(r) >= 4]
            if not rings:
                continue
            big = max(range(len(rings)), key=lambda q: _area(rings[q]))
            self.rings[k] = [r for q, r in enumerate(rings) if q == big or _area(r) >= min_area]
        self.box = (ox, oy, s * (x1 - x0), s * (y1 - y0))         # the drawn extent in px

    # -- geometry
    def path(self, k) -> MPath:
        verts, codes = [], []
        for r in self.rings[k]:
            verts.append(r)
            codes.append(np.r_[MPath.MOVETO, np.full(len(r) - 2, MPath.LINETO), MPath.CLOSEPOLY])
        return MPath(np.concatenate(verts), np.concatenate(codes).astype(np.uint8))

    def centre(self, k):
        """Area-weighted centroid of the largest ring (a good label spot for compact shapes)."""
        r = max(self.rings[k], key=_area)
        x, y = r[:-1, 0], r[:-1, 1]
        x2, y2 = r[1:, 0], r[1:, 1]
        cr = x * y2 - x2 * y
        a = cr.sum() / 2
        return (float(((x + x2) * cr).sum() / (6 * a)), float(((y + y2) * cr).sum() / (6 * a)))

    def point(self, lon, lat, proj=None):
        """A lon/lat point in px. Default projection: Albers USA for us-atlas layers."""
        if proj is None:
            x, y = albers_usa(lon, lat)
            return tuple(self.to_px(np.array([[x, y]]))[0])
        return tuple(self.to_px(proj(np.array([[lon, lat]], float)))[0])

    # -- drawing
    def draw(self, ax, colors=None, *, default=None, ec="white", lw=0.5, z=1, ids=None, alpha=1.0):
        colors = colors or {}
        for k in (ids if ids is not None else self.rings):
            if k not in self.rings:
                continue
            ax.add_patch(PathPatch(self.path(k), fc=colors.get(k, default), ec=ec, lw=lw, zorder=z, alpha=alpha,
                                   joinstyle="round"))

    def borders(self, ax, group: dict, *, color="white", lw=1.2, z=2, ls="-"):
        """Draw only the arcs where the group changes (region outlines; state lines in a county map)."""
        owners: dict[int, set] = {}
        for k, polys in self.refs.items():
            for poly in polys:
                for ring in poly:
                    for r in ring:
                        owners.setdefault(r if r >= 0 else ~r, set()).add(group.get(k))
        segs = [self.arcs[i] for i, g in owners.items() if len(g) > 1 and None not in g]
        for a in segs:
            ax.plot(a[:, 0], a[:, 1], color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round",
                    solid_joinstyle="round")


def canvas(fig, rect=(0, 0, 1, 1)):
    """An invisible axes whose data units are the figure's px (y up), so map coordinates write short in the SVG."""
    W, H = fig.get_size_inches() * 72
    ax = fig.add_axes(list(rect))
    ax.set_xlim(rect[0] * W, (rect[0] + rect[2]) * W)
    ax.set_ylim(rect[1] * H, (rect[1] + rect[3]) * H)
    ax.axis("off")
    return ax


# ------------------------------------------------------------------ US in plain lon/lat (only for the anti-example)
def _conic_inv(x, y, rot, par):
    p0, p1 = par[0] * RAD, par[1] * RAD
    n = (np.sin(p0) + np.sin(p1)) / 2
    c = 1 + np.sin(p0) * (2 * n - np.sin(p0))
    r0 = np.sqrt(c) / n
    r0y = r0 - y
    lam = np.arctan2(x, np.abs(r0y)) * np.sign(r0y)
    phi = np.arcsin(np.clip((c - (x * x + r0y * r0y) * n * n) / (2 * n), -1, 1))
    return lam / n / RAD - rot, phi / RAD


def us_lonlat():
    """Per-arc transform for Map(transform=...) on the states file: undo d3.geoAlbersUsa (lower 48, AK, HI)."""
    arc_owner = {}
    shapes = topo("states-albers-10m.json").shapes("states")
    for fips, ab in (("02", "AK"), ("15", "HI")):
        for poly in shapes[fips][1]:
            for ring in poly:
                arc_owner.update({(r if r >= 0 else ~r): ab for r in ring})
    k, tx, ty = 1300, 487.5, 305
    parts = {"AK": (154, (55, 65), (-2, 58.5), k * 0.35, (tx - 0.307 * k, ty + 0.201 * k)),
             "HI": (157, (8, 18), (-3, 19.9), k, (tx - 0.205 * k, ty + 0.212 * k)),
             None: (96, (29.5, 45.5), (-0.6, 38.7), k, (tx, ty))}

    def tf(i, p):
        rot, par, ctr, sc, (ox, oy) = parts[arc_owner.get(i) if arc_owner.get(i) in ("AK", "HI") else None]
        cx, cy = _conic(ctr[0] - rot, ctr[1], rot, par)
        lon, lat = _conic_inv((p[:, 0] - ox) / sc + cx, -(p[:, 1] - oy) / sc + cy, rot, par)
        lon = np.where(lon > 0, lon - 360, lon)                      # western Aleutians
        return np.column_stack([lon, -lat])                           # y down, like the albers source
    return tf
