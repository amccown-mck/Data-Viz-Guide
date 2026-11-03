"""Check a finished matplotlib or Plotly figure against the house rules (docs/principles.md, docs/qa-checklist.md).

    import mckviz as mv
    findings = mv.lint(fig)                       # prints a report and returns the findings
    mv.lint(fig, strict=True)                     # raises if any rule at "error" level fails

For Plotly figures whose headline, subtitle and source live in HTML (the chart-card pattern), pass them in:
    mv.lint(fig, headline="...", subtitle="...", source="Source: ...")

Levels: error = breaks a rule; warn = probably wrong, check it; info = worth a look.
The lint can't judge whether the headline is *true* or the chart type fits the question: that is still a human check.
"""
from __future__ import annotations

import colorsys
import re
from dataclasses import dataclass
from typing import Iterable

LEVELS = ("error", "warn", "info")
MIN_FONT_PT = 7.0          # figures are drawn ~10 in wide and scaled up ~1.33x on a 13.33 in slide: 7 pt -> ~9 pt
MIN_FONT_PX = 11.0         # Plotly sizes are CSS px: the house minimum is 9 pt / 11 px (template text starts at 12 px)
RAMP_TOL = 10.0            # RGB distance from a ramp segment that still counts as "on the ramp" (8-bit LUT rounding)
PLOTLY_3D = {"scatter3d", "surface", "mesh3d", "cone", "streamtube", "volume", "isosurface"}


@dataclass(frozen=True)
class Finding:
    level: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():5}  {self.rule}: {self.message}"


class LintError(AssertionError):
    pass


# ----------------------------------------------------------------------------------------------- color helpers
def _palette() -> set[str]:
    from . import TOKENS

    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", node):
            found.add(node.upper())

    walk(TOKENS)
    return found | {"#FFFFFF", "#000000"}


def _do_not_use() -> set[str]:
    """Hexes of brand families whose tokens say they are not used internally (e.g. amber)."""
    from . import TOKENS

    out: set[str] = set()
    for fam in TOKENS["brand"]["extended"].values():
        if isinstance(fam, dict) and "do not use" in str(fam.get("usage", "")).lower():
            out |= {v.upper() for k, v in fam.items() if k in ("light", "mid", "base", "dark") and v}
    return out


def _neutrals() -> set[str]:
    from . import colors as c

    return {x.upper() for x in (c.context, c.context_light, c.axis, c.grid, c.text, c.text_muted, c.surface_subtle,
                                getattr(c, "sand", c.context_light), "#FFFFFF")}


def _hex(color) -> str | None:
    """Any matplotlib/Plotly color spec -> '#RRGGBB' (alpha ignored), or None if transparent/unknown."""
    from matplotlib.colors import to_rgba

    if color is None:
        return None
    if isinstance(color, str):
        m = re.fullmatch(r"\s*rgba?\(([^)]*)\)\s*", color)
        if m:
            parts = [float(p) for p in m.group(1).split(",")]
            if len(parts) == 4 and parts[3] == 0:
                return None
            return "#{:02X}{:02X}{:02X}".format(*(int(round(p)) for p in parts[:3]))
    try:
        r, g, b, a = to_rgba(color)
    except (ValueError, TypeError):
        return None
    if a == 0:
        return None
    return "#{:02X}{:02X}{:02X}".format(*(int(round(v * 255)) for v in (r, g, b)))


def _rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _near(h: str, pool: Iterable[str], tol: float = 8.0) -> bool:
    r, g, b = _rgb(h)
    return any(((r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2) ** 0.5 <= tol for R, G, B in map(_rgb, pool))


def _ramps() -> dict[str, list[str]]:
    """Every token ramp a colormap may interpolate along: sequential blue/teal/orange, diverging, process steps."""
    from . import DIVERGING, SEQUENTIAL, STEPS

    out = {f"sequential-{k}": [h.upper() for h in v] for k, v in SEQUENTIAL.items()}
    out["diverging"] = [h.upper() for h in DIVERGING]
    out["steps"] = [h.upper() for h in STEPS]
    return out


def _segment_distance(h: str, ramp: list[str]) -> float:
    """RGB distance from `h` to the polyline through the ramp's stops (what mv.sequential_cmap() interpolates)."""
    p = _rgb(h)
    best = float("inf")
    stops = [_rgb(x) for x in ramp]
    for a, b in zip(stops, stops[1:]):
        ab = [bb - aa for aa, bb in zip(a, b)]
        ap = [pp - aa for aa, pp in zip(a, p)]
        denom = sum(v * v for v in ab) or 1.0
        t = max(0.0, min(1.0, sum(x * y for x, y in zip(ap, ab)) / denom))
        best = min(best, sum((pp - (aa + t * v)) ** 2 for pp, aa, v in zip(p, a, ab)) ** 0.5)
    return best


def _ramp_of(h: str, ramps: dict[str, list[str]], tol: float = RAMP_TOL) -> str | None:
    """Name of the closest token ramp `h` lies on (within tol), or None."""
    dists = {name: _segment_distance(h, r) for name, r in ramps.items()}
    name = min(dists, key=dists.get)
    return name if dists[name] <= tol else None


def _is_neutral(h: str, neutrals: set[str]) -> bool:
    if _near(h, neutrals, 6):
        return True
    r, g, b = (v / 255 for v in _rgb(h))
    return colorsys.rgb_to_hsv(r, g, b)[1] < 0.12        # greys, sands, near-whites


def _color_findings(used: list[str]) -> list[Finding]:
    out: list[Finding] = []
    palette, neutrals, ramps = _palette(), _neutrals(), _ramps()
    off = sorted({h for h in used if not _near(h, palette) and _ramp_of(h, ramps) is None})
    if off:
        out.append(Finding("warn", "palette", f"colors not in tokens/tokens.json: {', '.join(off[:6])}"
                                              f"{' ...' if len(off) > 6 else ''} (use mv.colors / mv.CATEGORICAL)"))
    hues = sorted({h for h in used if not _is_neutral(h, neutrals)})
    # A sequential or diverging ramp is one encoding, not one category per step: count each ramp used once. A ramp is
    # "used" when 3+ distinct hues lie on it (exact stops or colors a colormap interpolated between them) and at least
    # one of them is not a categorical color, so plain blue + navy + orange series are still three categories.
    from . import CATEGORICAL
    cats = {h.upper() for h in CATEGORICAL}
    members = {name: {h for h in hues if _segment_distance(h, r) <= RAMP_TOL} for name, r in ramps.items()}
    used_ramps: list[str] = []
    ramp_colors: set[str] = set()
    while True:
        left = {n: m - ramp_colors for n, m in members.items() if n not in used_ramps}
        best = max(left, key=lambda n: len(left[n]), default=None)
        if best is None or len(left[best]) < 3 or not (left[best] - cats):
            break
        used_ramps.append(best)
        ramp_colors |= left[best]
    categories = len([h for h in hues if h not in ramp_colors]) + len(used_ramps)
    if categories > 6:
        out.append(Finding("error", "max-6-colors", f"{categories} distinct colors; use at most 6 and grey the rest"))
    from . import STATUS
    status = {STATUS[k]["value"].upper() for k in ("on_track", "at_risk", "off_track")}
    is_status = len({h for h in hues if _near(h, status, 6)}) >= 2      # a tracker / roadmap using two RAG colors
    if is_status:
        out.append(Finding("info", "status-colors", "status (RAG) colors: only for status, never data series; pair each "
                                                    "color with a symbol and a word (mv.STATUS has both)"))
    has_red = has_green = False
    for h in hues:
        if is_status and _near(h, status, 6):
            continue
        hh, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in _rgb(h)))
        deg = hh * 360
        has_red |= (deg < 15 or deg > 345) and s > 0.4 and v > 0.3
        has_green |= 85 < deg < 150 and s > 0.35 and v > 0.3
    if has_red and has_green:
        out.append(Finding("error", "no-red-green", "red and green are both used; use blue vs. navy (orange only for negatives)"))
    banned = sorted({h for h in used if _near(h, _do_not_use(), 6) and not (is_status and _near(h, status, 6))})
    if banned:
        out.append(Finding("error", "do-not-use", f"{', '.join(banned)} is not used internally (amber family); "
                                                  "pick from mv.CATEGORICAL"))
    from . import colors as c
    if any(_near(h, {c.orange.upper()}, 6) and h not in ramp_colors for h in hues):
        out.append(Finding("info", "orange-semantic", "orange appears: keep it for negatives / below target only, "
                                                      "never as a plain highlight (use navy, chart.accent)"))
    return out


def _headline_findings(headline: str | None, subtitle: str | None, source: str | None) -> list[Finding]:
    out: list[Finding] = []
    if not headline or not headline.strip():
        out.append(Finding("error", "headline", "no headline: add an insight sentence with mv.titles(fig, headline, "
                                                "subtitle) (Plotly: mv.pl_finish); a headline drawn with fig.text "
                                                "isn't one, so mv.save can't lay it out"))
    else:
        text = " ".join(headline.replace("<br>", " ").split())
        if len(text.split()) < 5:
            out.append(Finding("warn", "headline", f'"{text}" reads like a label; state the finding as a sentence'))
        if text[0].isdigit():
            out.append(Finding("warn", "headline", f'starts with a digit ("{text.split()[0]}"); spell out a number that '
                                                   'opens a sentence ("Two", not "2")'))
        if text.endswith("."):
            out.append(Finding("info", "headline", "drop the final period"))
        if not re.search(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|half|twice|double|triple|all|most|none|every)\b",
                         text, re.I):
            out.append(Finding("info", "headline", "no number in the headline; the best ones quantify the finding"))
        if len(text) > 140:
            out.append(Finding("warn", "headline", f"{len(text)} characters; keep it to about 2 lines"))
    if not subtitle or not subtitle.strip():
        out.append(Finding("error", "subtitle", "no subtitle: state metric, unit, scope and period"))
    elif not re.search(r"\(|\b(FY|Q[1-4]|20\d\d|19\d\d|month|year|weekly|annual)", subtitle, re.I):
        out.append(Finding("info", "subtitle", "subtitle has no unit in brackets or period; add metric, unit, scope, period"))
    if not source or "source:" not in source.lower():
        out.append(Finding("error", "source", 'no "Source:" line (mv.source / pl_finish(source_text=...))'))
    return out


# ----------------------------------------------------------------------------------------------- matplotlib
def _image_colors(im, samples: int = 9) -> list[str]:
    """Colors an AxesImage shows: its colormap over the plotted value range, or the distinct pixels of an RGB image."""
    import numpy as np

    arr = im.get_array()
    if arr is None:
        return []
    arr = np.ma.asarray(arr)
    if arr.ndim == 2:
        vals = arr.compressed() if np.ma.isMaskedArray(arr) else np.ravel(arr)
        if not vals.size:
            return []
        lo, hi = im.norm.vmin, im.norm.vmax
        if lo is None or hi is None:
            lo, hi = float(np.nanmin(vals)), float(np.nanmax(vals))
        dmin, dmax = max(float(np.nanmin(vals)), lo), min(float(np.nanmax(vals)), hi)
        a, b = (float(im.norm(dmin)), float(im.norm(dmax))) if hi > lo else (0.0, 1.0)
        rgba = im.cmap(np.linspace(a, b, samples))
    else:
        px = np.asarray(arr).reshape(-1, arr.shape[-1])
        if px.dtype.kind in "ui":
            px = px / 255.0
        rgba = np.unique(np.round(px[:: max(1, len(px) // 2000)], 3), axis=0)[:64]
    return [h for h in (_hex(tuple(c)) for c in rgba) if h]


_GLYPHS: dict[str, frozenset[int]] = {}


def _glyphs(path: str) -> frozenset[int]:
    """The code points a font file covers (cached per file)."""
    if path not in _GLYPHS:
        try:
            from fontTools.ttLib import TTFont

            with TTFont(path, lazy=True) as f:
                _GLYPHS[path] = frozenset(f.getBestCmap() or {})
        except Exception:                                   # unreadable font: assume it has everything
            _GLYPHS[path] = frozenset()
    return _GLYPHS[path]


def _missing_glyphs(text_artist) -> set[str]:
    """Characters of a Text artist that none of its font families can draw (matplotlib falls back to a box)."""
    from matplotlib import font_manager as fm

    chars = {c for c in text_artist.get_text() if ord(c) > 0x7F and not c.isspace()}
    if not chars:
        return set()
    props = text_artist.get_fontproperties()
    families = props.get_family()
    if isinstance(families, str):
        families = [families]
    covered: set[int] = set()
    found_any = False
    for fam in families:
        try:
            path = fm.findfont(fm.FontProperties(family=fam, weight=props.get_weight(), style=props.get_style()),
                               fallback_to_default=False)
        except ValueError:
            continue
        glyphs = _glyphs(path)
        if not glyphs:                                      # could not read the font: don't guess
            return set()
        found_any = True
        covered |= glyphs
    if not found_any:
        return set()
    return {c for c in chars if ord(c) not in covered}


def _x_repeats(xdata) -> bool:
    """True when a line of 3+ points goes back to an earlier x: the signature of repeated period labels used as x."""
    try:
        import numpy as np
        x = np.asarray(xdata, dtype=float)
    except (TypeError, ValueError):
        return False
    if x.ndim != 1 or len(x) < 3 or np.isnan(x).any():
        return False
    d = np.diff(x)
    return bool((d < 0).any() and (d > 0).any() and len(np.unique(x)) < len(x))


def _undrawn_ticks(axes) -> set[int]:
    """Tick labels outside the axis range: matplotlib keeps them as visible Text but never draws them."""
    out = set()
    for ax in axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                loc = tick.get_loc()
                if loc is None or not lo - 1e-9 * (abs(lo) + abs(hi) + 1) <= loc <= hi + 1e-9 * (abs(lo) + abs(hi) + 1):
                    out.update((id(tick.label1), id(tick.label2)))
    return out


def _short(t) -> str:
    return " ".join(t.get_text().split())[:40]


def _overlap_findings(axes, renderer) -> list[Finding]:
    """Labels, keys and legends that sit on scatter markers or on each other. A label wholly inside one bubble (a
    value printed in it) is deliberate; one that straddles a bubble's edge, or covers another label, is a collision."""
    from matplotlib.collections import PathCollection
    from matplotlib.text import Annotation, Text

    on_marks, on_text = [], []
    for ax in axes:
        px = renderer.points_to_pixels(1.0)
        circles = []
        for coll in ax.collections:
            if not (isinstance(coll, PathCollection) and coll.get_visible()) or not len(coll.get_offsets()):
                continue
            sizes = coll.get_sizes()
            if not len(sizes):
                continue
            xy = coll.get_offset_transform().transform(coll.get_offsets())
            sizes = sizes if len(sizes) == len(xy) else [sizes[0]] * len(xy)
            circles += [(x, y, (s ** 0.5) / 2 * px) for (x, y), s in zip(xy, sizes) if s > 0]
        boxes = []
        for t in ax.texts + [c for c in ax.get_children() if isinstance(c, Annotation) and c not in ax.texts]:
            if isinstance(t, Text) and t.get_visible() and t.get_text().strip():
                if isinstance(t, Annotation):                 # the text alone, not its leader line
                    t.update_positions(renderer)
                bb = Text.get_window_extent(t, renderer)
                if bb.width > 0 and bb.height > 0:
                    boxes.append((f'"{_short(t)}"', bb))
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            boxes.append(("the legend", leg.get_window_extent(renderer)))
        for name, bb in boxes:
            for cx, cy, rad in circles:
                corners = [(bb.x0, bb.y0), (bb.x0, bb.y1), (bb.x1, bb.y0), (bb.x1, bb.y1)]
                if all((x - cx) ** 2 + (y - cy) ** 2 <= rad ** 2 for x, y in corners):
                    continue                                  # a label printed inside its bubble
                dx = max(bb.x0 - cx, 0, cx - bb.x1)
                dy = max(bb.y0 - cy, 0, cy - bb.y1)
                if rad - (dx * dx + dy * dy) ** 0.5 > max(2.0, 0.2 * rad):
                    on_marks.append(name)
                    break
        for i, (a, ba) in enumerate(boxes):
            for b, bb in boxes[i + 1:]:
                w = min(ba.x1, bb.x1) - max(ba.x0, bb.x0)
                h = min(ba.y1, bb.y1) - max(ba.y0, bb.y0)
                if w > 2 and h > 2:
                    on_text.append(f"{a} and {b}")
    out = []
    if on_marks:
        out.append(Finding("warn", "label-on-data", f"{'; '.join(list(dict.fromkeys(on_marks))[:3])} "
                                                    "sits on the data markers: move it beside its point or into "
                                                    "empty space (mv.bubble and mv.label_points place labels clear "
                                                    "of the bubbles; a size key goes above the plot, mv.size_key)"))
    if on_text:
        out.append(Finding("warn", "label-overlap", f"{'; '.join(on_text[:3])} overlap: move one of them"))
    return out


def _lint_matplotlib(fig, headline, subtitle, source) -> list[Finding]:
    import numpy as np
    from matplotlib.container import BarContainer
    from matplotlib.patches import Wedge
    from matplotlib.text import Text

    from . import colors

    fur = getattr(fig, "_mck", {}) or {}
    head = headline or (fur["head"].get_text() if fur.get("head") is not None else None) \
        or (fig._suptitle.get_text() if getattr(fig, "_suptitle", None) else None)
    sub = subtitle or (fur["sub"].get_text() if fur.get("sub") is not None else None)
    src = source or (fur["foot"].get_text() if fur.get("foot") is not None else None)
    out = _headline_findings(head, sub, src)

    axes = [a for a in fig.axes if a.get_visible()]
    colorbar_axes = {a for a in axes if a.get_label() == "<colorbar>"}
    used: list[str] = []
    for ax in axes:
        if ax in colorbar_axes:
            continue
        if getattr(ax, "name", "") == "3d":
            out.append(Finding("error", "no-3d", "3D axes distort values; use a 2D chart"))
        for p in ax.patches:
            if p.get_visible() and p.get_fill():
                h = _hex(p.get_facecolor())
                if h:
                    used.append(h)
        for coll in ax.collections:
            for fc in (coll.get_facecolor() if len(coll.get_facecolor()) else []):
                h = _hex(fc)
                if h:
                    used.append(h)
        for im in ax.images:                              # imshow: sample the colormap (or the RGB pixels)
            if im.get_visible():
                used.extend(_image_colors(im))
        for ln in ax.get_lines():
            if ln.get_gid() == "mck-annotation":               # a bracket: drawn by mv.bracket, not data
                continue
            if ln.get_visible() and ln.get_linestyle() not in ("None", "none", ""):
                h = _hex(ln.get_color())
                if h:
                    used.append(h)
                if _x_repeats(ln.get_xdata(orig=False)):
                    out.append(Finding("warn", "x-repeats", "a line revisits earlier x positions: repeated period "
                                                            "labels (\"Q2\", \"Q2\") used as x? give each period its "
                                                            "own value and abbreviate in the tick text"))
                    break

        # Lines drawn by hand: the habits mv.line avoids (markers on every point, an off-palette reference line,
        # a y-axis title where the subtitle carries the unit)
        data_lines = [ln for ln in ax.get_lines() if ln.get_visible() and len(ln.get_xdata(orig=False)) >= 5
                      and ln.get_linestyle() not in ("None", "none", "")]
        if any(str(ln.get_marker()) not in ("None", "none", "", " ") for ln in data_lines):
            out.append(Finding("warn", "line-markers", "markers on every point of a line make it heavy; drop them "
                                                       "(a dot only on a labelled point). mv.line draws the house line"))
        for ln in ax.get_lines():
            y = np.asarray(ln.get_ydata(orig=False), float)
            ref = (len(y) == 2 and y[0] == y[1] and ln.get_linestyle() not in ("-", "solid")
                   and tuple(ln.get_xdata(orig=False)) == (0, 1))          # an axhline, dashed: target or benchmark
            h = _hex(ln.get_color())
            if ref and h and not _near(h, {colors.total.upper()}):
                out.append(Finding("warn", "reference-line", "a dashed reference line that isn't navy: draw targets and "
                                                             "benchmarks in C.total, 0.75 pt (mv.line(target=...))"))
                break
        if data_lines and ax.get_ylabel().strip():
            out.append(Finding("warn", "axis-title", "a y-axis title on a line chart: put the unit in the subtitle "
                                                     "and drop the title (mv.line does)"))

        # Bars: zero baseline, labels vs. value axis
        bars = [c for c in ax.containers if isinstance(c, BarContainer)]
        if bars:
            horizontal = getattr(bars[0], "orientation", "vertical") == "horizontal"
            rects = [r for c in bars for r in c]
            starts = [(r.get_x() if horizontal else r.get_y()) for r in rects]
            lo = (ax.get_xlim() if horizontal else ax.get_ylim())[0]
            floating = any(abs(s) > 1e-9 for s in starts)
            if lo > 1e-9 and not floating:
                out.append(Finding("error", "bars-from-zero", f"value axis starts at {lo:g}; bars must start at zero "
                                                              "(use a dot plot for clustered values)"))
            elif lo > 1e-9 and floating:                    # a waterfall on a floor: fine once the footnote says so
                noted = any("break" in t.get_text().lower() or "axis starts" in t.get_text().lower() for t in fig.texts)
                out.append(Finding("info" if noted else "warn", "bars-from-zero",
                                   f"value axis starts at {lo:g} (waterfall?): " +
                                   ("break marks noted in the footnote" if noted else
                                    "mark the break on the totals and say so in a footnote")))
            labels = [t for t in ax.texts if t.get_text().strip()] + \
                     [c for c in ax.get_children() if type(c).__name__ == "Annotation" and c.get_text().strip()]
            value_ticks = ax.get_xticklabels() if horizontal else ax.get_yticklabels()
            ticks_on = ax.axison and any(t.get_visible() and t.get_text() for t in value_ticks)
            if len(labels) >= len(rects) and ticks_on:
                out.append(Finding("warn", "labels-or-axis", "bars carry value labels and a value axis; remove the axis "
                                                             "and gridlines"))
        wedges = [p for p in ax.patches if isinstance(p, Wedge)]
        if len(wedges) > 5:
            out.append(Finding("error", "pie-max-5", f"{len(wedges)} pie/donut segments; use ≤ 5 or a sorted bar"))
        notes = getattr(getattr(ax, "_mck_notes", None), "count", 0)
        if notes > 3:
            out.append(Finding("warn", "annotations", f"{notes} annotations on one chart compete for the eye: keep the "
                                                      "one or two that carry the headline (less is more)"))
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            n = len(leg.get_texts())
            kind = "lines" if ax.get_lines() and not bars else "series"
            out.append(Finding("info" if kind == "series" else "warn", "direct-labels",
                               f"legend with {n} entries; label the {kind} directly where labels fit"))
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            if t.get_visible() and t.get_text() and t.get_rotation() not in (0, 360):
                out.append(Finding("warn", "no-rotated-labels", "rotated tick labels; use horizontal bars or "
                                                                "shorter labels"))
                break

    # Dual axes: two visible axes sharing a position, one a twin of the other
    for i, a in enumerate(axes):
        for b in axes[i + 1:]:
            if a.get_position().bounds == b.get_position().bounds and \
                    (a.get_shared_x_axes().joined(a, b) or a.get_shared_y_axes().joined(a, b)):
                out.append(Finding("warn", "no-dual-axis", "twin axes found; prefer two aligned charts or an index to 100"))

    pale = sorted({" ".join(t.get_text().split())[:30] for t in fig.findobj(Text)
                   if t.get_visible() and t.get_text().strip() and (_hex(t.get_color()) or "").upper() in
                   {colors.context.upper(), colors.context_light.upper()}})
    if pale:
        out.append(Finding("warn", "text-contrast", f"text in context grey ({'; '.join(pale[:3])}) fails 4.5:1 "
                                                    "contrast; use C.text_muted for context labels"))
    small = sorted({round(t.get_fontsize(), 1) for t in fig.findobj(Text)
                    if t.get_visible() and t.get_text().strip() and t.get_fontsize() < MIN_FONT_PT})
    if small:
        out.append(Finding("warn", "min-text-size", f"text at {', '.join(map(str, small))} pt; keep ≥ {MIN_FONT_PT:g} pt "
                                                    "on a 10 in figure (≈ 9 pt on a slide)"))
    # Text past the figure edge: the tight bounding box widens the saved image to fit it, shrinking the chart inside.
    # mv.layout wraps the footnote and source line, so they are skipped here.
    fig.canvas.draw()
    r, width = fig.canvas.get_renderer(), fig.bbox.width
    hidden = _undrawn_ticks(axes)
    off = []
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip() and t is not fur.get("foot") and id(t) not in hidden:
            e = t.get_window_extent(r)
            if e.x1 > width * 1.1 or e.x0 < -width * 0.1:      # a little is normal: long tick labels
                off.append(" ".join(t.get_text().split())[:40])
    if off:
        out.append(Finding("warn", "off-canvas", f"text runs past the figure edge ({'; '.join(off[:3])}); the saved "
                                                 "image widens to fit it and the chart shrinks: wrap or shorten it"))
    out += _overlap_findings(axes, r)
    missing: dict[str, str] = {}
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip():
            for c in _missing_glyphs(t):
                missing.setdefault(c, " ".join(t.get_text().split())[:40])
    if missing:
        where = "; ".join(f"{c!r} in \"{s}\"" for c, s in sorted(missing.items())[:4])
        out.append(Finding("warn", "missing-glyph", f"{where}: the font has no glyph for it, so it renders as a box; "
                                                    "use a word or a drawn marker, or give the text a fallback family "
                                                    "(fontfamily=[mv.FONT, \"DejaVu Sans\"])"))
    return out + _color_findings(used)


# ----------------------------------------------------------------------------------------------- Plotly
def _overlaid(lay, axis_id: str) -> bool:
    """True if a y axis like 'y2' / 'y3' shares the plot area of the main y axis (a dual axis) rather than being a
    separate subplot panel (make_subplots gives each panel its own domain)."""
    name = "yaxis" + axis_id[1:]
    ax = lay[name] if name in lay else None
    if ax is None or ax.overlaying:
        return True
    main = list(lay.yaxis.domain) if lay.yaxis and lay.yaxis.domain else [0, 1]
    return ax.domain is None or list(ax.domain) == main and ax.anchor in (None, "x", "free")


def _plotly_font_sizes(fig) -> list[float]:
    """Every explicitly set font size in a Plotly figure: layout, titles, axes, legend, annotations, trace text."""
    sizes: list = []

    def add(font):
        if font is not None and font.size is not None:
            v = font.size
            sizes.extend(v if isinstance(v, (list, tuple)) else (v.tolist() if hasattr(v, "tolist") else [v]))

    lay = fig.layout
    add(lay.font)
    if lay.title:
        add(lay.title.font)
        if lay.title.subtitle:
            add(lay.title.subtitle.font)
    if lay.legend:
        add(lay.legend.font)
    for key in lay:
        if re.fullmatch(r"[xy]axis\d*", key) and lay[key] is not None:
            add(lay[key].tickfont)
            if lay[key].title:
                add(lay[key].title.font)
    for a in lay.annotations or []:
        if a.text:
            add(a.font)
    for tr in fig.data:
        for attr in ("textfont", "insidetextfont", "outsidetextfont"):
            if attr in tr:
                add(getattr(tr, attr))
    return [float(v) for v in sizes if isinstance(v, (int, float))]


def _lint_plotly(fig, headline, subtitle, source) -> list[Finding]:
    lay = fig.layout
    head = headline or (lay.title.text if lay.title and lay.title.text else None)
    sub = subtitle or (lay.title.subtitle.text if lay.title and lay.title.subtitle and lay.title.subtitle.text else None)
    src = source or next((a.text for a in (lay.annotations or []) if a.text and "source:" in a.text.lower()), None)
    out = _headline_findings(head, sub, src)

    used: list[str] = []

    def collect(value):
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for v in value:
                collect(v)
        elif hasattr(value, "tolist"):
            collect(value.tolist())
        elif isinstance(value, str):
            h = _hex(value)
            if h:
                used.append(h)

    for tr in fig.data:
        for attr in ("marker", "line"):
            obj = getattr(tr, attr, None)
            if obj is not None and "color" in obj:
                collect(obj.color)
        if "fillcolor" in tr:
            collect(tr.fillcolor)
        if tr.type == "sankey":
            collect(tr.node.color)
            collect(tr.link.color)
    unset = [tr for tr in fig.data if tr.type in ("bar", "scatter") and not (tr.marker and tr.marker.color)
             and not (getattr(tr, "line", None) and tr.line.color)]
    if unset:
        cw = list(lay.colorway or (lay.template.layout.colorway if lay.template and lay.template.layout else []) or [])
        collect(cw[:len(unset)])

    bars = [tr for tr in fig.data if tr.type == "bar"]
    for tr in bars:
        horizontal = tr.orientation == "h"
        axis = lay.xaxis if horizontal else lay.yaxis
        rng = axis.range if axis is not None else None
        if rng and rng[0] is not None and rng[0] > 0 and not tr.base:
            out.append(Finding("error", "bars-from-zero", f"bar axis range starts at {rng[0]}; start at zero"))
    def has_labels(tr):
        return tr.text is not None or bool(getattr(tr, "texttemplate", None))

    if bars and all(has_labels(tr) for tr in bars):
        axis = lay.xaxis if bars[0].orientation == "h" else lay.yaxis
        if axis is None or axis.visible is not False:
            out.append(Finding("warn", "labels-or-axis", "bars carry text labels and a visible value axis; hide the axis"))
    y_axes = {getattr(tr, "yaxis", None) or "y" for tr in fig.data if "yaxis" in tr}
    extra = sorted(a for a in y_axes if a != "y" and _overlaid(lay, a))
    if len(extra) >= 2:
        out.append(Finding("error", "no-dual-axis", f"{len(extra) + 1} y axes share one plot; split into aligned "
                                                    "charts or index to 100"))
    elif extra:
        out.append(Finding("warn", "no-dual-axis", f"a trace uses a second y axis ({extra[0]}); prefer two aligned "
                                                   "charts"))
    three_d = sorted({tr.type for tr in fig.data if tr.type in PLOTLY_3D})
    if three_d:
        out.append(Finding("error", "no-3d", f"3D trace ({', '.join(three_d)}) distorts values; use a 2D chart"))
    small = sorted({round(float(v), 1) for v in _plotly_font_sizes(fig) if v < MIN_FONT_PX})
    if small:
        out.append(Finding("warn", "min-text-size", f"text at {', '.join(f'{v:g}' for v in small)} px; keep ≥ "
                                                    f"{MIN_FONT_PX:g} px"))
    for tr in fig.data:
        if tr.type == "pie" and tr.labels is not None and len(tr.labels) > 5:
            out.append(Finding("error", "pie-max-5", f"{len(tr.labels)} pie/donut segments; use ≤ 5 or a sorted bar"))
    for tr in fig.data:                                   # a line through "Q1 '24, Q2, Q3, Q4, Q1 '25, Q2, ..." folds back
        if tr.type == "scatter" and "lines" in (tr.mode or "lines") and not tr.fill and tr.x is not None:
            xs = list(tr.x)
            if len(xs) >= 3 and len(set(map(str, xs))) < len(xs):
                out.append(Finding("warn", "x-repeats", f'trace "{tr.name or ""}" has repeated x values: on a category '
                                                        "axis every \"Q2\" shares one position; use unique periods "
                                                        "(\"Q2 '25\") as x and abbreviate in ticktext"))
                break
    shown = [tr for tr in fig.data if tr.type not in ("pie", "sankey", "heatmap", "treemap")
             and getattr(tr, "showlegend", None) is not False]
    if len(shown) > 1 and lay.showlegend is not False:
        out.append(Finding("info", "direct-labels", f"legend with {len(shown)} series; label them directly where labels fit"))
    for ax_name in ("xaxis", "yaxis"):
        ax = getattr(lay, ax_name, None)
        if ax is not None and ax.tickangle not in (None, 0):
            out.append(Finding("warn", "no-rotated-labels", f"{ax_name} tick labels are rotated"))
    return out + _color_findings(used)


# ----------------------------------------------------------------------------------------------- entry point
def _print_safe(text: str) -> None:
    """Print findings even where stdout can't encode ≤, −, × (a Windows console or a pipe in CI)."""
    import sys
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(enc, errors="replace").decode(enc, errors="replace"))


def lint(fig, *, headline: str | None = None, subtitle: str | None = None, source: str | None = None,
         strict: bool = False, quiet: bool = False) -> list[Finding]:
    """Lint a matplotlib Figure or a Plotly Figure against the house rules. Returns the findings (errors first)."""
    if type(fig).__module__.startswith("plotly"):
        findings = _lint_plotly(fig, headline, subtitle, source)
    else:
        fig.canvas.draw()                                   # resolve limits, tick labels and layout first
        findings = _lint_matplotlib(fig, headline, subtitle, source)
    findings = sorted(dict.fromkeys(findings), key=lambda f: LEVELS.index(f.level))
    if not quiet:
        _print_safe("\n".join(map(str, findings)) if findings else "lint: no findings")
    if strict and any(f.level == "error" for f in findings):
        raise LintError("; ".join(str(f) for f in findings if f.level == "error"))
    return findings
