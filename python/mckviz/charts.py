"""On-brand chart builders for matplotlib: one call per chart the guide teaches.

    import mckviz as mv
    fig, ax = plt.subplots()
    mv.waterfall(ax, steps, values, focus={"Automation savings"})       # totals navy, deltas grey, focus blue

Each builder draws into an Axes (``multiples`` into a Figure) with the house rules built in: grey context, blue focus,
navy totals and accent, orange only for worse, green only for better and always with an arrow or a word, status
colors only with their symbol and word, white separators in stacks, flat shapes, direct labels and zero baselines.
Add ``mv.titles`` and ``mv.source`` and the figure passes ``mv.lint(fig, strict=True)``.

Data goes in as plain lists or arrays, or a pandas DataFrame where noted (pandas is optional). Every builder returns
a ``types.SimpleNamespace`` with the artists and positions a caller needs to annotate further. Sizes come from the
typography roles in ``mv.TOKENS``, colors from ``mv.colors`` / ``mv.STATUS``.
"""
from __future__ import annotations

import math
import textwrap
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, Sequence

import numpy as np

from . import DIVERGING, FONT, MINUS, SEQUENTIAL, STATUS, TOKENS, _SCALE, colors as C, halo, signed, text_on

_ROLES = TOKENS["typography"]["roles"]
LABEL = _ROLES["label"]["size_pt"] - 1          # 11 pt: direct labels (as mv.label_bars)
TICK = _ROLES["tick"]["size_pt"]                # 11 pt: category and axis labels
SMALL = _ROLES["footnote"]["size_pt"]           # 9 pt: keys, owners, secondary text (the house minimum)
KPI_PT = _ROLES["kpi"]["size_pt"] * _SCALE      # big numbers on a 10 in figure (54 pt on a 13.33 in slide)
KPI_WEIGHT = _ROLES["kpi"]["weight"]
BAND = TOKENS["chart"]["bar"]["band_fill"]
UP, DOWN = "▲", "▼"
STATUS_ORDER = ["off_track", "at_risk", "on_track", "not_started", "done"]   # exceptions first
_MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ------------------------------------------------------------------ shared plumbing
def _pandas():
    try:
        import pandas as pd
    except ImportError as e:                                    # pragma: no cover - depends on the environment
        raise ImportError("this mckviz helper needs pandas for a CSV path or a DataFrame: pip install pandas "
                          "(or pip install 'mckviz[pandas]'), or pass plain lists / dicts instead") from e
    return pd


def _records(data) -> list[dict]:
    """A DataFrame, a CSV path or a list of dicts -> list of dicts, with NaN turned into None."""
    if isinstance(data, (str, Path)):
        data = _pandas().read_csv(data)
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        data = data.to_dict("records")
    out = []
    for r in data:
        out.append({k: (None if isinstance(v, float) and v != v else v) for k, v in dict(r).items()})
    return out


def _floats(values, name: str) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    return arr


def _offset(transform, fig, dx: float = 0, dy: float = 0):
    from matplotlib.transforms import offset_copy

    return offset_copy(transform, fig=fig, x=dx, y=dy, units="points") if (dx or dy) else transform


def _mark(ax, x, y, marker, size, *, transform=None, offset=(0, 0), face="none", edge="none", lw=0.0, z=6,
          cap="butt"):
    """One marker of `size` points at (x, y), without touching the axes' data limits (safe in any coordinates)."""
    from matplotlib.collections import PathCollection
    from matplotlib.markers import MarkerStyle
    from matplotlib.transforms import IdentityTransform

    ms = MarkerStyle(marker, capstyle=cap, joinstyle="miter")
    path = ms.get_path().transformed(ms.get_transform())
    coll = PathCollection((path,), sizes=[size ** 2], offsets=[(x, y)],
                          offset_transform=_offset(transform or ax.transData, ax.figure, *offset),
                          facecolors=[face], edgecolors=[edge], linewidths=[lw], zorder=z)
    coll.set_transform(IdentityTransform())
    coll.set_capstyle(cap)
    coll.set_joinstyle("miter")
    coll.set_clip_on(False)
    ax.add_collection(coll, autolim=False)
    return coll


def _fam(s: str) -> dict:
    """Libre Franklin has no ▲ / ▼: let matplotlib fall back to DejaVu Sans (bundled) for those glyphs only."""
    return {"fontfamily": [FONT, "DejaVu Sans"]} if (UP in s or DOWN in s) else {}


def _text_width_pt(ax, s: str, size: float, weight=400) -> float:
    fig = ax.figure
    t = fig.text(0, 0, s, fontsize=size, fontweight=weight)
    w = t.get_window_extent(fig.canvas.get_renderer()).width * 72 / fig.dpi
    t.remove()
    return w


def _bold_ticks(labels, names, color=None):
    names = set(names)
    for t in labels:
        if t.get_text() in names:
            t.set_fontweight(600)
            t.set_color(color or C.headline)


def _plain(ax, keep=()):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)
        ax.spines[side].set_color(C.axis)
    ax.grid(False)
    ax.tick_params(length=0)


def _wrap(s: str, width: int | None) -> str:
    """Wrap on word boundaries only: a long name overflows its slot rather than breaking mid-word."""
    return textwrap.fill(str(s), width, break_long_words=False, break_on_hyphens=False) if width else str(s)


def _month(v) -> int | None:
    """'2026-03', a date or a Timestamp -> absolute month number (year * 12 + month - 1)."""
    if v is None or v == "" or (isinstance(v, float) and v != v):
        return None
    if hasattr(v, "year") and hasattr(v, "month"):
        return int(v.year) * 12 + int(v.month) - 1
    y, m = str(v)[:7].split("-")
    return int(y) * 12 + int(m) - 1


def _mon(m: int, year: bool = False) -> str:
    return _MON[m % 12] + (f" {m // 12}" if year else "")


# ------------------------------------------------------------------ comparisons (KPI deltas, gap to target)
def delta_label(change: float, *, unit: str = "", vs: str = "", better: str = "up", decimals: int = 0):
    """Text and color for a change: an arrow for the direction, a color for the judgment.

        text, color = mv.delta_label(14, unit=" pts", vs="vs. Mar 2025")   # "▲ +14 pts vs. Mar 2025", green text
        mv.delta_label(5, unit=" days", better="down")                      # up is worse here: orange text

    better: "up" (higher is better), "down" (lower is better) or None (neutral: grey text, arrow kept).
    Green (`positive_text`) is used only for a favorable change, and always with its arrow; orange
    (`negative_text`) only for an unfavorable one. A change that rounds to zero reads "No change".
    """
    if better not in ("up", "down", None):
        raise ValueError("better must be 'up', 'down' or None")
    body = signed(change, decimals)
    tail = f" {vs}" if vs else ""
    if body.lstrip("+" + MINUS) == body and float(body.replace(",", "")) == 0:
        return f"No change{tail}", C.text
    arrow = UP if change > 0 else DOWN
    good = None if better is None else (change > 0) == (better == "up")
    color = C.text if good is None else C.positive_text if good else C.negative_text
    return f"{arrow} {body}{unit}{tail}", color


# ------------------------------------------------------------------ WATERFALL
def waterfall(ax, steps: Sequence[str], values: Sequence[float], kinds: Sequence[str] | None = None, *,
              focus: Iterable[str] = (), semantic: str | None = None, arrows: bool | None = None,
              floor: float | None = None, break_marks: bool = True, connectors: bool = True, labels: bool = True,
              fmt=None, horizontal: bool = False, width: float = BAND, wrap: int | None = None):
    """Waterfall (bridge) from start total to end total: totals navy, deltas grey, the headline's deltas blue.

        mv.waterfall(ax, df.step, df.value_musd, df.kind, focus={"Automation savings"}, floor=3900)
        mv.titles(fig, "Automation offsets a third of FY26 labor cost growth", "Labor cost bridge, FY25 to FY26 ($M)")
        mv.source(fig, "Source: ...", footnote=ns.note)          # ns = the return value; says where the axis starts

    kinds: "total" or "delta" per step (default: first and last are totals). A "total" in the middle is a subtotal.
    focus: delta steps to color blue (at most two; everything else stays grey).
    semantic: color deltas by judgment instead: "up" (an increase is favorable: green up, orange down) or "down"
        (an increase is unfavorable, e.g. cost). Labels then carry ▲/▼ (arrows=False drops them).
    floor: start the value axis here (a truncated waterfall). Totals get two white break marks; say so in a footnote
        (the return value's `note`). Deltas never need a zero baseline: they float.
    fmt: callable(value, kind) -> label. Default: totals "4,210", deltas with explicit + and a true minus.
    wrap: characters per line for the step names (default 13 for columns, 28 for horizontal bars).
    Returns SimpleNamespace(bars, labels, bottoms, tops, ends, colors, note).
    """
    steps, vals = [str(s) for s in steps], _floats(values, "values")
    n = len(steps)
    if len(vals) != n:
        raise ValueError("steps and values must have the same length")
    kinds = list(kinds) if kinds is not None else ["total"] + ["delta"] * (n - 2) + ["total"]
    if len(kinds) != n or set(kinds) - {"total", "delta"}:
        raise ValueError("kinds must be 'total' or 'delta', one per step")
    if semantic not in (None, "up", "down"):
        raise ValueError("semantic must be None, 'up' (increase is favorable) or 'down' (increase is unfavorable)")
    focus = set(focus)
    if len(focus) > 2:
        raise ValueError("highlight at most two steps; the rest stay grey (house rule)")
    arrows = (semantic is not None) if arrows is None else arrows
    fmt = fmt or (lambda v, k: f"{v:,.0f}" if k == "total" else signed(v))

    run, bottoms, heights, cols, ends, tone = 0.0, [], [], [], [], []
    for s, v, k in zip(steps, vals, kinds):
        if k == "total":
            bottoms.append(0.0)
            heights.append(v)
            run = v
            cols.append(C.total)
            tone.append("total")
        else:
            bottoms.append(run if v >= 0 else run + v)
            heights.append(abs(v))
            run += v
            if semantic:
                good = (v > 0) == (semantic == "up")
                cols.append(C.positive if good else C.negative)
                tone.append("good" if good else "bad")
            else:
                cols.append(C.focus if s in focus else C.context)
                tone.append("focus" if s in focus else "context")
        ends.append(run)
    bottoms, heights = np.array(bottoms), np.array(heights)
    tops = bottoms + heights
    x = np.arange(n)
    if horizontal:
        bars = ax.barh(x, heights, left=bottoms, color=cols, height=width, zorder=2)
    else:
        bars = ax.bar(x, heights, bottom=bottoms, color=cols, width=width, zorder=2)

    if connectors:                                            # thin grey line at the running level between bars
        for i in range(n - 1):
            a, b = [i + width / 2, i + 1 - width / 2], [ends[i], ends[i]]
            ax.plot(*((b, a) if horizontal else (a, b)), color=C.axis, lw=0.75, zorder=1)

    texts = []
    if labels:
        for i, (top, v, k, t) in enumerate(zip(tops, vals, kinds, tone)):
            txt = fmt(v, k)
            if arrows and k == "delta" and v != 0:
                txt = f"{UP if v > 0 else DOWN} {txt}"
            color = {"total": C.headline, "focus": C.headline, "good": C.positive_text,
                     "bad": C.negative_text}.get(t, C.text)
            weight = 700 if t in ("total", "focus") else 600 if t in ("good", "bad") else 400
            xy, off = ((top, i), (4, 0)) if horizontal else ((i, top), (0, 3))
            texts.append(ax.annotate(txt, xy, xytext=off, textcoords="offset points", fontsize=LABEL, color=color,
                                     fontweight=weight, **_fam(txt), ha="left" if horizontal else "center",
                                     va="center" if horizontal else "bottom", annotation_clip=False))

    hi = float(tops.max())
    lo = floor if floor is not None else min(0.0, float(bottoms.min()))
    span = hi - lo
    lim = (lo, hi + span * (0.14 if horizontal else 0.08))
    note = ""
    if floor is not None:
        if any(bottoms[i] < floor for i in range(n) if kinds[i] == "delta"):
            raise ValueError(f"floor={floor:g} cuts into a delta bar; lower it")
        if break_marks:                                       # two white slashes across each total near the floor
            for i in np.flatnonzero(np.array(kinds) == "total"):
                for d in (0.035, 0.065):
                    yb = floor + span * d
                    seg = ([i - width / 2 - 0.02, i + width / 2 + 0.02], [yb - span * 0.008, yb + span * 0.008])
                    ax.plot(*(seg[::-1] if horizontal else seg), color="white", lw=2.2, zorder=4,
                            solid_capstyle="butt")
        note = f"Value axis starts at {floor:,.0f} (break marks on the totals) so the steps are readable."
    tick_text = [_wrap(s, wrap or (28 if horizontal else 13)) for s in steps]
    if horizontal:
        ax.set_xlim(*lim)
        ax.set_yticks(x, tick_text)
        ax.set_xticks([])
        ax.set_ylim(n - 0.5, -0.5)
        _plain(ax, keep=("left",))
        tick_labels = ax.get_yticklabels()
    else:
        ax.set_ylim(*lim)
        ax.set_xticks(x, tick_text)
        ax.set_yticks([])
        ax.set_xlim(-0.5, n - 0.5)
        _plain(ax, keep=("bottom",))
        tick_labels = ax.get_xticklabels()
    for t, k, s in zip(tick_labels, kinds, steps):
        t.set_fontsize(TICK)
        t.set_color(C.text)
        if k == "total" or s in focus:
            t.set_fontweight(600)
            t.set_color(C.headline)
    return SimpleNamespace(bars=bars, labels=texts, bottoms=bottoms, tops=tops, ends=np.array(ends), colors=cols,
                           note=note)


# ------------------------------------------------------------------ 100% STACKED BAR
_STACK_GREYS = [C.context, C.context_light, C.axis]
_STACK_LIGHT_BLUES = [C.focus_light, SEQUENTIAL["blue"][1], SEQUENTIAL["blue"][0]]   # uniform + accent: no greys


def hstack(ax, categories: Sequence[str], parts, *, story=None, accent: str | None = None, uniform: bool = False,
           colors: Sequence[str] | None = None, focus: Iterable[str] = (), label_min: float = 8, fmt="{:.0f}%",
           names: bool = True, name_align: Sequence[str] | None = None, base: Sequence[float] | None = None,
           base_label: str = "n", height: float = BAND, sep: float = 1.5):
    """Horizontal (100%) stacked bars in the three color patterns, story segments first on the baseline.

        parts = [("Contingent", df.contingent_pct), ("Full-time", df.ft_pct), ("Part-time", df.pt_pct)]
        mv.hstack(ax, df.function, parts, focus={"Technology"}, base=df.workers, base_label="Workers")
        mv.titles(fig, "Technology uses contingent labor at 4x the rate of other functions", "Workforce mix, 2026 (%)")

    categories: one bar per category, the first drawn on top. parts: [(name, values)] or {name: values} in stack
        order, left to right. The colored segments move to the front (on the baseline, where they are easy to compare).
    Color patterns, the same three as mv.highlight:
        Focus (default): `story=` (one segment, or two as a group) in blue, the rest in context greys; with no story
            the first part is the story.
        Focus + accent: `story=` blue plus `accent=` navy for the one segment that stands out, the rest greys.
        Uniform + accent: `accent=` navy and `uniform=True`; every other segment in light blues, no greys.
    colors: per segment, overriding the patterns (categorical, or sequential steps for ordered bands). More than 4
        segments: group them.
    focus: categories whose names go bold navy. Segments are split by white lines (`sep`, points); values are
        printed inside segments of at least `label_min`; segment names sit once over the top bar (no legend);
        `base` adds the counts behind each bar at the right, under the header `base_label`.
    Returns SimpleNamespace(bars, labels, names, lefts, totals, colors).
    """
    cats = [str(c) for c in categories]
    items = list(parts.items()) if isinstance(parts, dict) else [tuple(p) for p in parts]
    items = [(str(nm), _floats(v, f"part {nm!r}")) for nm, v in items]
    story = [] if story is None else [str(story)] if isinstance(story, str) else [str(x) for x in story]
    lead = ([str(accent)] if accent is not None else []) + story          # navy exception on the baseline, then blue
    names_ = [nm for nm, _ in items]
    for nm in lead:
        if nm not in names_:
            raise ValueError(f"{nm!r} is not one of the parts")
    if len(story) > 2:
        raise ValueError("story: at most two segments; color the rest grey or use colors=mv.categorical(n)")
    if uniform and accent is None:
        raise ValueError("uniform=True needs accent=: the light-blue series only works with one navy exception")
    items = [it for nm in lead for it in items if it[0] == nm] + [it for it in items if it[0] not in lead]
    if any(len(v) != len(cats) for _, v in items):
        raise ValueError("every part needs one value per category")
    if colors is None:
        rest = len(items) - (len(lead) if lead else 1)
        fill = _STACK_LIGHT_BLUES if uniform else _STACK_GREYS
        if rest > len(fill):
            raise ValueError(f"{len(items)} segments: group the small ones into 'Other' (at most 4 read well)")
        head = ([C.accent] if accent is not None else []) + [C.focus] * len(story) if lead else [C.focus]
        colors = head + fill[:rest]
    if len(colors) != len(items):
        raise ValueError("one color per part")
    n = len(cats)
    y = np.arange(n)[::-1]                                    # first category on top
    left = np.zeros(n)
    bars, texts, lefts = [], [], []
    for (nm, vals), col in zip(items, colors):
        lefts.append(left.copy())
        bars.append(ax.barh(y, vals, left=left, color=col, height=height, edgecolor="white", linewidth=sep,
                            zorder=2, label=nm))
        story_seg = col in (C.focus, C.accent)
        for yy, l0, v in zip(y, left, vals):
            if v >= label_min:
                texts.append(ax.text(l0 + v / 2, yy, fmt.format(v) if isinstance(fmt, str) else fmt(v), ha="center",
                                     va="center", fontsize=LABEL - 1, color=text_on(col), zorder=3,
                                     fontweight=600 if story_seg else 400))
        left = left + vals
    total = float(left.max())
    name_texts = []
    if names:                                                 # each segment named once, above the top bar
        align = list(name_align or ["left"] * len(items))
        top = 0
        l0 = 0.0
        for (nm, vals), col, a in zip(items, colors, align):
            v = vals[top]
            xx = {"left": l0, "center": l0 + v / 2, "right": l0 + v}[a]
            hot = col in (C.focus, C.accent)
            name_texts.append(ax.annotate(nm, (xx, y[top] + height / 2), xytext=(0, 3), textcoords="offset points",
                                          ha=a, va="bottom", fontsize=TICK, annotation_clip=False,
                                          color=col if hot else C.text, fontweight=600 if hot else 400))
            l0 += v
    xmax = total
    if base is not None:
        base = list(base)
        bx = total * 1.03
        for yy, b in zip(y, base):
            ax.text(bx, yy, f"{b:,.0f}", va="center", ha="left", fontsize=LABEL - 1, color=C.text_muted)
        ax.annotate(base_label, (bx, y[0] + height / 2), xytext=(0, 3), textcoords="offset points", ha="left",
                    va="bottom", fontsize=TICK, color=C.text, annotation_clip=False)
        xmax = total * 1.14
    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.5, n - 0.5 + (0.45 if names or base is not None else 0))
    ax.set_yticks(y, cats)
    ax.set_xticks([])
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), focus)
    _plain(ax)
    return SimpleNamespace(bars=bars, labels=texts, names=name_texts, lefts=lefts, totals=left, colors=list(colors))


# ------------------------------------------------------------------ DUMBBELL
def dumbbell(ax, labels: Sequence[str], compare: Sequence[float], value: Sequence[float], *,
             compare_name: str = "Market", value_name: str = "McKesson", flag_below: float | None = -5.0,
             flag_name: str | None = None, gap: str = "pct", decimals: int = 1, tick_fmt: str = "{:,.0f}",
             xlim: tuple[float, float] | None = None, key: bool = True, dot: float = 8.0,
             focus: Iterable[str] | None = None):
    """Us vs. a comparator per row: comparator grey, us blue, orange where we are `flag_below`% or more below.

        ns = mv.dumbbell(ax, df.role, df.market_median_k, df.internal_median_k, tick_fmt="${:,.0f}K")
        mv.titles(fig, f"Pay trails the market by 5% or more for {ns.flagged.sum()} roles", "Median base pay, 2026 ($K)")
        mv.source(fig, "Source: ...")

    The first row is drawn on top; sort the rows first (largest shortfall first, say). The gap label after each pair
    is `value` vs. `compare`: in % (gap="pct") or in units (gap="abs"), with a true minus. Flagged rows get bold navy
    names and orange gap labels. `focus` names the rows the headline is about when the flag logic does not apply
    (flag_below=None): their names are bold navy too, so the headline and the highlight agree. A key names the dot
    types once, top left (key=False to label them yourself).
    Returns SimpleNamespace(flagged, gaps, compare_dots, value_dots, labels).
    """
    labels = [str(s) for s in labels]
    a, b = _floats(compare, "compare"), _floats(value, "value")
    if not (len(labels) == len(a) == len(b)):
        raise ValueError("labels, compare and value must have the same length")
    gaps = (b / a - 1) * 100 if gap == "pct" else b - a
    flagged = np.zeros(len(a), bool) if flag_below is None else gaps <= flag_below
    y = np.arange(len(labels))
    lo, hi = float(min(a.min(), b.min())), float(max(a.max(), b.max()))
    pad = (hi - lo) * 0.08 or 1
    xlim = xlim or (lo - pad, hi + pad * 2.2)
    span = xlim[1] - xlim[0]
    s = dot ** 2
    cd = ax.scatter(a, y, s=s * 0.8, color=C.context, zorder=2, lw=0)
    vd = ax.scatter(b, y, s=s, color=[C.negative if f else C.focus for f in flagged], zorder=3, lw=0)
    texts = []
    for i in y:
        ax.plot([a[i], b[i]], [i, i], color=C.context_light, lw=3, solid_capstyle="butt", zorder=1)
        suffix = "%" if gap == "pct" else ""
        texts.append(ax.text(max(a[i], b[i]) + span * 0.025, i, signed(gaps[i], decimals, suffix), va="center",
                             fontsize=LABEL - 1, color=C.negative_text if flagged[i] else C.text,
                             fontweight=700 if flagged[i] else 400))
    if key:                                                   # every dot type once, top left, in points
        items = [(value_name, C.focus, C.focus, 600)]
        if flagged.any():
            unit = "%" if gap == "pct" else ""
            items.append((flag_name or f"{value_name}, {abs(flag_below):g}{unit}+ below {compare_name.lower()}",
                          C.negative, C.negative_text, 600))
        items.append((compare_name, C.context, C.text_muted, 400))
        x = dot / 2
        for name, dc, tc, w in items:
            _mark(ax, 0, 1, "o", dot * 0.85, transform=ax.transAxes, offset=(x, 10), face=dc)
            t = ax.annotate(name, (0, 1), xycoords="axes fraction", xytext=(x + dot / 2 + 3, 10),
                            textcoords="offset points", fontsize=SMALL + 1, color=tc, fontweight=w, va="center")
            x += dot / 2 + 3 + _text_width_pt(ax, name, SMALL + 1, w) + 14 + dot / 2
    ax.set_yticks(y, labels)
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), [lab for lab, f in zip(labels, flagged) if f] + [str(f) for f in (focus or [])])
    ax.set_ylim(len(labels) - 0.5, -0.6)
    ax.set_xlim(*xlim)
    from matplotlib.ticker import FuncFormatter, MaxNLocator

    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: tick_fmt.format(v)))
    _plain(ax)
    ax.grid(axis="x", color=C.grid, lw=0.75, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=TICK - 1, colors=C.text_muted)
    return SimpleNamespace(flagged=flagged, gaps=gaps, compare_dots=cd, value_dots=vd, labels=texts)


# ------------------------------------------------------------------ DIVERGING BARS
def diverging_bars(ax, labels: Sequence[str], values: Sequence[float], *, worse: str = "above", fmt=None,
                   decimals: int = 1, suffix: str = "", zero_label: str | None = None, pad: float = 0.02):
    """Deviation from a benchmark per row: orange on the unfavorable side, focus blue on the other.

        gap = df.vol_attrition_pct - enterprise_rate
        ns = mv.diverging_bars(ax, df.job_family, gap, worse="above", suffix=" pts")
        mv.titles(fig, f"{ns.worse.sum()} of {len(df)} job families run above the enterprise rate", "...")

    `values` are already deviations (value minus benchmark), so zero is the benchmark and the bars start there.
    worse="above" paints positive bars orange (attrition, cost, time-to-fill); worse="below" paints negative bars
    orange (engagement, fill rate). Labels sit at the bar ends with a true minus and an explicit plus (`mv.signed`),
    or through `fmt` (a format string or a callable; a leading hyphen becomes a true minus). Unfavorable rows get bold
    navy category names and orange label text. The x-limits are padded for the label widths, so a label on a negative
    bar stays inside the plot and never runs into the category names. The first row is drawn on top; sort first.
    The value axis is removed (the labels carry the values); a thin zero line stays, with `zero_label` above it.
    Returns SimpleNamespace(bars, labels, worse, xlim).
    """
    if worse not in ("above", "below"):
        raise ValueError('worse must be "above" or "below"')
    labels = [str(s) for s in labels]
    v = _floats(values, "values")
    if len(labels) != len(v):
        raise ValueError("labels and values must have the same length")
    bad = v > 0 if worse == "above" else v < 0

    def text_of(x):
        if fmt is None:
            return signed(x, decimals, suffix)
        s = fmt(x) if callable(fmt) else fmt.format(x)
        return MINUS + s[1:] if s.startswith("-") else s

    y = np.arange(len(labels))
    cols = [C.negative if b else C.focus for b in bad]
    bars = ax.barh(y, v, color=cols, height=BAND, zorder=2)
    texts = []
    for i in y:
        neg = v[i] < 0
        texts.append(ax.annotate(text_of(v[i]), (v[i], i), xytext=(-3 if neg else 3, 0), textcoords="offset points",
                                 ha="right" if neg else "left", va="center", fontsize=LABEL,
                                 fontweight=700 if bad[i] else 500, color=C.negative_text if bad[i] else C.text,
                                 zorder=4))
    # Pad the limits so every label fits inside the plot: solve span from the label widths in axes fraction.
    lo_v, hi_v = min(0.0, float(v.min())), max(0.0, float(v.max()))
    ax_pt = ax.get_window_extent().width * 72 / ax.figure.dpi or 1.0
    left_pt = max([_text_width_pt(ax, t.get_text(), LABEL, 700) + 3 for t, x in zip(texts, v) if x < 0], default=0.0)
    right_pt = max([_text_width_pt(ax, t.get_text(), LABEL, 700) + 3 for t, x in zip(texts, v) if x >= 0], default=0.0)
    f_left, f_right = left_pt / ax_pt, right_pt / ax_pt
    span = (hi_v - lo_v) / max(1 - f_left - f_right - 2 * pad, 0.3) or 1.0
    xlim = (lo_v - (f_left + pad) * span, hi_v + (f_right + pad) * span)
    ax.set_xlim(*xlim)
    ax.set_yticks(y, labels)
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), [lab for lab, b in zip(labels, bad) if b])
    ax.set_ylim(len(labels) - 0.5, -0.6)
    ax.set_xticks([])
    _plain(ax)
    ax.axvline(0, color=C.axis, lw=0.75, zorder=3)
    if zero_label:
        ax.annotate(zero_label, (0, 1), xycoords=("data", "axes fraction"), xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=SMALL, color=C.annotation, annotation_clip=False)
    return SimpleNamespace(bars=bars, labels=texts, worse=bad, xlim=xlim)


# ------------------------------------------------------------------ POINT LABELS
def label_points(ax, xs: Sequence[float], ys: Sequence[float], names: Sequence[str], sizes=None, *,
                 focus: Iterable[str] = (), right_frac: float = 0.75, pad: float = 3.0, fontsize: float | None = None):
    """Name the points of a scatter or bubble chart in place, with a white halo.

        sc = ax.scatter(df.pay, df.exposure, s=sizes, c=mv.highlight(df.role, focus=focus))
        mv.label_points(ax, df.pay, df.exposure, df.role, sizes, focus=focus)

    Each label sits just outside its marker (`sizes` are the scatter's marker areas in pt², so the offset clears the
    bubble): to the right of the point, or to the left when the point lies in the right `right_frac` of the x-range
    (the default is the right 25%), so labels never run off the plot edge. Names in `focus` are bold navy, the rest
    muted. Set the x-limits before calling, because the side is decided against the current limits.
    Returns the list of Text artists.
    """
    names = [str(s) for s in names]
    x, y = _floats(xs, "xs"), _floats(ys, "ys")
    if not (len(names) == len(x) == len(y)):
        raise ValueError("xs, ys and names must have the same length")
    s = np.full(len(x), 0.0) if sizes is None else _floats(sizes, "sizes")
    if len(s) == 1 and len(x) > 1:
        s = np.full(len(x), float(s[0]))
    focus = {str(f) for f in focus}
    x0, x1 = ax.get_xlim()
    cut = x0 + right_frac * (x1 - x0)
    size = fontsize or (LABEL - 1)
    out = []
    for xi, yi, name, si in zip(x, y, names, s):
        rad = math.sqrt(max(si, 0) / math.pi) + pad
        left = xi >= cut
        bold = name in focus
        out.append(ax.annotate(name, (xi, yi), xytext=(-rad if left else rad, 0), textcoords="offset points",
                               ha="right" if left else "left", va="center", fontsize=size + (1 if bold else 0),
                               fontweight=700 if bold else 400, color=C.headline if bold else C.text_muted,
                               path_effects=halo(), zorder=5))
    return out


# ------------------------------------------------------------------ RANK SLOPE
def rank_slope(ax, names: Sequence[str], before: Sequence[int], after: Sequence[int], *, focus: Iterable[str] = (),
               worse: Iterable[str] = (), headers: tuple[str, str] = ("Before", "After"), nums: bool = True,
               short: dict | None = None):
    """Two-point rank slope, rank 1 at the top, names at both ends: grey context, blue focus, orange for a fall.

        mv.rank_slope(ax, df.skill, df.rank_2023, df.rank_2026, focus={"Data analysis"}, headers=("2023", "2026"))
        mv.titles(fig, "Data analysis rose four places in three years", "Rank of skills in job postings, 2023 vs. 2026")
        mv.source(fig, "Source: ...")

    Returns SimpleNamespace(lines, left, right) where left / right map each name to its label artist.
    """
    names = [str(n) for n in names]
    r0, r1 = [int(v) for v in before], [int(v) for v in after]
    focus, worse, short = set(focus), set(worse), short or {}
    if len(focus | worse) > 2:
        raise ValueError("highlight at most two lines; the rest stay grey (house rule)")
    lines, left, right = {}, {}, {}
    for i in sorted(range(len(names)), key=lambda i: names[i] in focus | worse):   # highlights drawn last
        nm = names[i]
        col = C.negative if nm in worse else C.focus if nm in focus else C.context
        hot = col != C.context
        lines[nm] = ax.plot([0, 1], [r0[i], r1[i]], color=col, lw=2.4 if hot else 1.4, zorder=3 if hot else 2,
                            solid_capstyle="butt")[0]
        _mark(ax, 0, r0[i], "o", 6, face=col, z=4 if hot else 2)
        _mark(ax, 1, r1[i], "o", 6, face=col, z=4 if hot else 2)
        kw = dict(va="center", fontsize=LABEL, color=C.negative_text if nm in worse else C.headline if hot else C.text,
                  fontweight=600 if hot else 400)
        lab = short.get(nm, nm)
        left[nm] = ax.text(-0.05, r0[i], f"{lab}  {r0[i]}" if nums else lab, ha="right", **kw)
        right[nm] = ax.text(1.05, r1[i], f"{r1[i]}  {lab}" if nums else lab, ha="left", **kw)
    for x, hd in zip((0, 1), headers):
        ax.text(x, 0.15, hd, ha="center", va="center", fontsize=TICK, fontweight=700, color=C.text)
    n = max(max(r0), max(r1))
    ax.set_ylim(n + 0.6, -0.4)
    ax.set_xlim(-0.9, 1.9)
    ax.axis("off")
    return SimpleNamespace(lines=lines, left=left, right=right)


# ------------------------------------------------------------------ HEAT TABLE
def _nice(x: float) -> float:
    if x <= 0:
        return 1.0
    k = 10 ** math.floor(math.log10(x))
    return next(m * k for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10) if m * k >= x - 1e-12)


def _stepped(bounds, ramp):
    b = np.asarray(bounds, float)

    def f(v):
        if v is None or v != v:
            return None
        k = int(np.clip(np.searchsorted(b, v, side="right") - 1, 0, len(ramp) - 1))
        return ramp[k]
    return f


def key_strip(ax, ramp: Sequence[str], labels: Sequence[str] | None = None, *, xy=(0.0, -1.0), width: float = 3.0,
              height: float = 0.28, ends: tuple[str, str] | None = None, tick_at: str = "edges"):
    """Stepped color key in the data coordinates of `ax`: equal swatches, labels under the class breaks.

        b = mv.heat(ax, m, key=False).bounds
        mv.key_strip(ax, mv.DIVERGING, [mv.signed(v) for v in b], xy=(0, -1.2), ends=("Below", "Above"))
        mv.titles(fig, "...", "..."); mv.source(fig, "Source: ...")

    labels: one per class edge (len(ramp) + 1, tick_at="edges") or per class (tick_at="centers"); "" skips one.
    ends: words over the two ends of the strip, e.g. ("Below benchmark", "Above benchmark"): the low end in the
        orange text color when the ramp is the diverging one, the high end in blue.
    Returns SimpleNamespace(swatches, labels, ends).
    """
    from matplotlib.patches import Rectangle

    x0, y0 = xy
    n = len(ramp)
    sw = width / n
    sws = [ax.add_patch(Rectangle((x0 + k * sw, y0), sw, height, color=c, lw=0, clip_on=False))
           for k, c in enumerate(ramp)]
    labs = []
    if labels is not None:
        xs = [x0 + k * sw for k in range(n + 1)] if tick_at == "edges" else [x0 + (k + 0.5) * sw for k in range(n)]
        for xx, lab in zip(xs, labels):
            if lab != "":
                labs.append(ax.annotate(lab, (xx, y0), xytext=(0, -2), textcoords="offset points", ha="center",
                                        va="top", fontsize=SMALL, color=C.text_muted, annotation_clip=False))
    end_t = []
    if ends:
        lo_col = C.negative_text if list(ramp) == list(DIVERGING) else C.text
        for xx, txt, ha, col in ((x0, ends[0], "left", lo_col), (x0 + width, ends[1], "right", C.focus)):
            end_t.append(ax.annotate(txt, (xx, y0 + height), xytext=(0, 2), textcoords="offset points", ha=ha,
                                     va="bottom", fontsize=SMALL, color=col, annotation_clip=False))
    return SimpleNamespace(swatches=sws, labels=labs, ends=end_t)


def heat(ax, data, *, rows: Sequence[str] | None = None, cols: Sequence[str] | None = None, kind: str = "diverging",
         bounds: Sequence[float] | None = None, ramp: Sequence[str] | None = None, fmt=None, decimals: int = 0,
         focus_cols: Iterable[str] = (), focus_rows: Iterable[str] = (), n=None, min_n: int = 10,
         na_text: str = "n<10", gap: float = 0.06, wrap: bool = True, outline: bool = True, key: bool = True,
         key_ends: tuple[str, str] | None = None):
    """Heat table: a matrix of cells in stepped classes, values printed in each cell, white gutters.

        m = df.pivot(index="business_unit", columns="driver", values="delta_pts")
        mv.heat(ax, m, focus_cols={"Workload"}, key_ends=("Below benchmark", "Above benchmark"))
        mv.titles(fig, "Workload trails the benchmark in 5 of 6 units", "Driver score vs. benchmark (points)")

    data: a DataFrame (rows = index, columns = columns) or a 2-D array with `rows` and `cols`.
    kind: "diverging" (around zero, orange below, blue above: mv.DIVERGING) or "sequential" (light to dark blue).
    bounds: class edges (len(ramp) + 1). Default: even, "nice" steps, symmetric about zero when diverging.
    n: counts with the same shape; cells under `min_n` are suppressed (light grey, `na_text`, no value). NaN cells
        show an en dash. focus_cols / focus_rows: what the headline names, outlined in a 1.5 pt navy box
        (outline=False drops it) with bold values and bold navy headers; the cells keep their class colors.
    key: a stepped key with the class edges under the table (`key_ends` labels its two ends).
    Returns SimpleNamespace(cells, texts, bounds, ramp, color_of, key, outlines).
    """
    from matplotlib.patches import Rectangle

    if hasattr(data, "values") and hasattr(data, "index") and hasattr(data, "columns"):
        rows = [str(r) for r in (rows or data.index)]
        cols = [str(c) for c in (cols or data.columns)]
        m = np.asarray(data.values, float)
    else:
        m = np.asarray(data, float)
        if rows is None or cols is None:
            raise ValueError("pass rows= and cols= with a plain 2-D array")
        rows, cols = [str(r) for r in rows], [str(c) for c in cols]
    if m.shape != (len(rows), len(cols)):
        raise ValueError(f"data is {m.shape}, but {len(rows)} rows x {len(cols)} cols were named")
    if kind not in ("diverging", "sequential"):
        raise ValueError("kind must be 'diverging' or 'sequential'")
    ramp = list(ramp or (DIVERGING if kind == "diverging" else SEQUENTIAL["blue"]))
    k = len(ramp)
    finite = m[np.isfinite(m)]
    if bounds is None:
        if kind == "diverging":
            step = _nice(2 * float(np.abs(finite).max() if finite.size else 1) / k)
            bounds = step * (np.arange(k + 1) - k / 2)
        else:
            lo, hi = (float(finite.min()), float(finite.max())) if finite.size else (0.0, 1.0)
            step = _nice((hi - lo) / k)
            lo = math.floor(lo / step) * step
            if lo + step * k < hi:
                step = _nice((hi - lo) / k * 1.0001)
            bounds = lo + step * np.arange(k + 1)
    bounds = np.asarray(bounds, float)
    if len(bounds) != k + 1:
        raise ValueError(f"{k} colors need {k + 1} class bounds")
    color_of = _stepped(bounds, ramp)
    if fmt is None:
        fmt = (lambda v: signed(v, decimals)) if kind == "diverging" else (lambda v: f"{v:,.{decimals}f}")
    supp = np.zeros(m.shape, bool) if n is None else np.asarray(n, float) < min_n
    focus_cols, focus_rows = set(focus_cols), set(focus_rows)
    nr, nc = m.shape
    cells, texts = [], []
    for i in range(nr):
        for j in range(nc):
            v = m[i, j]
            yy = nr - 1 - i
            col = None if supp[i, j] else color_of(v)
            cells.append(ax.add_patch(Rectangle((j + gap / 2, yy + gap / 2), 1 - gap, 1 - gap,
                                                color=col or C.context_light, lw=0)))
            if supp[i, j]:
                txt, tc, w = na_text, C.text_muted, 400
            elif col is None:
                txt, tc, w = "–", C.text_muted, 400
            else:
                bold = cols[j] in focus_cols or rows[i] in focus_rows
                txt, tc, w = fmt(v), text_on(col), 700 if bold else 500
            texts.append(ax.text(j + 0.5, yy + 0.48, txt, ha="center", va="center", fontsize=LABEL - 1, color=tc,
                                 fontweight=w))
    for i, r in enumerate(rows):
        hot = r in focus_rows
        ax.text(-0.1, nr - 1 - i + 0.5, r, ha="right", va="center", fontsize=TICK,
                color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    for j, c in enumerate(cols):
        hot = c in focus_cols
        lab = c.replace(" ", "\n", 1) if wrap and " " in c and len(c) > 8 else c
        ax.text(j + 0.5, nr + 0.1, lab, ha="center", va="bottom", fontsize=TICK, linespacing=1.1,
                color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    outlines = []
    if outline:                                               # 1.5 pt navy box around a focus row / column
        for j, c in enumerate(cols):
            if c in focus_cols:
                outlines.append(ax.add_patch(Rectangle((j + gap / 4, gap / 4), 1 - gap / 2, nr - gap / 2, fill=False,
                                                       ec=C.headline, lw=1.5, zorder=3)))
        for i, r in enumerate(rows):
            if r in focus_rows:
                outlines.append(ax.add_patch(Rectangle((gap / 4, nr - 1 - i + gap / 4), nc - gap / 2, 1 - gap / 2,
                                                       fill=False, ec=C.headline, lw=1.5, zorder=3)))
    ks = None
    bottom = -0.02
    if key:
        w = min(float(nc), 0.5 * k)
        labs = [fmt(b) if kind == "diverging" else f"{b:,.{decimals}f}" for b in bounds]
        if kind == "diverging" and k % 2 == 1:                 # label the outer edges and the middle class only
            labs = [lab if i in (0, k) else "" for i, lab in enumerate(labs)]
        ks = key_strip(ax, ramp, labs, xy=(0, -0.95), width=w, height=0.28, ends=key_ends)
        bottom = -1.45
    ax.set_xlim(-0.02, nc + 0.02)
    ax.set_ylim(bottom, nr + 0.02)
    ax.axis("off")
    return SimpleNamespace(cells=cells, texts=texts, bounds=bounds, ramp=ramp, color_of=color_of, key=ks,
                           outlines=outlines)


# ------------------------------------------------------------------ SINGLE NUMBER
def big(ax, x, y, text: str, *, size: float | None = None, color: str | None = None, dark: bool = False, **kw):
    """A KPI numeral: Bold, navy (white on dark), KPI role size unless `size` is given. Returns the Text.

        mv.big(ax, 0, 1, "62%", transform=ax.transAxes, va="top")
    """
    kw.setdefault("ha", "left")
    kw.setdefault("va", "baseline")
    return ax.text(x, y, text, fontsize=size or KPI_PT, fontweight=KPI_WEIGHT,
                   color=color or ("white" if dark else C.headline), **kw)


def small(ax, x, y, text: str, *, size: float | None = None, color: str | None = None, weight=400, dark: bool = False,
          **kw):
    """Supporting text for a KPI: the label role size, body text color (white on dark). Returns the Text.

        mv.small(ax, 0, 0.4, "254 of 410 critical roles", transform=ax.transAxes, va="top")
    """
    kw.setdefault("ha", "left")
    kw.setdefault("va", "baseline")
    kw.setdefault("linespacing", 1.3)
    return ax.text(x, y, text, fontsize=size or LABEL + 1, fontweight=weight,
                   color=color or ("white" if dark else C.text), **{**_fam(text), **kw})


def ring(ax, value: float, *, xy=(0.0, 0.0), radius: float = 1.0, width: float | None = None,
         target: float | None = None, target_label: bool = True, color: str | None = None, track: str | None = None,
         dark: bool = False):
    """Progress ring for one percentage (0-100): starts at 12 o'clock, clockwise, thin, flat ends, no gap.

        ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4)
        mv.ring(ax, 67, target=80)
        mv.big(ax, 0, 0, "67%", ha="center", va="center")

    target: draws a navy tick across the ring (white on dark) and, with target_label, "Target 80%" beside it.
    Returns SimpleNamespace(arc, track, tick, angle, label).
    """
    from matplotlib.patches import Wedge

    if not 0 <= value <= 100:
        raise ValueError("a ring shows one share of 0-100%; use a big number with a comparison for other values")
    cx, cy = xy
    w = width or radius * 0.18
    start = 90
    end = start - 360 * value / 100
    arc = ax.add_patch(Wedge((cx, cy), radius, end, start, width=w, lw=0,
                             color=color or (C.focus_on_dark if dark else C.focus)))
    trk = ax.add_patch(Wedge((cx, cy), radius, start, end + 360, width=w, lw=0,
                             color=track or (C.context_on_dark if dark else C.context_light)))
    tick = lab = angle = None
    if target is not None:
        angle = np.deg2rad(start - 360 * target / 100)
        r0, r1 = radius - w - radius * 0.07, radius + radius * 0.07
        tick = ax.plot([cx + r0 * np.cos(angle), cx + r1 * np.cos(angle)],
                       [cy + r0 * np.sin(angle), cy + r1 * np.sin(angle)], color="white" if dark else C.total,
                       lw=1.8, solid_capstyle="butt", zorder=4)[0]
        if target_label:
            rr = radius * 1.12
            ca = np.cos(angle)
            lab = ax.text(cx + rr * ca, cy + rr * np.sin(angle), f"Target\n{target:g}%",
                          ha="right" if ca < -0.2 else "left" if ca > 0.2 else "center",
                          va="center", fontsize=SMALL + 1, color="white" if dark else C.annotation, linespacing=1.1)
    return SimpleNamespace(arc=arc, track=trk, tick=tick, angle=angle, label=lab)


def _chain(ax, first, lines, gap=6):
    """Stack texts under `first`, left-aligned, each `gap` points below the one before."""
    out, prev = [], first
    for text, size, color, weight in lines:
        prev = ax.annotate(text, (0, 0), xycoords=prev, xytext=(0, -gap), textcoords="offset points", ha="left",
                           va="top", fontsize=size, color=color, fontweight=weight, linespacing=1.25,
                           annotation_clip=False, **_fam(text))
        out.append(prev)
    return out


def kpi_card(ax, value: str | float, sentence: str, *, change: float | None = None, unit: str = " pts",
             vs: str = "", better: str | None = "up", target: float | None = None, target_text: str | None = None,
             ring_value: float | None = None, suffix: str = "%", decimals: int = 0, dark: bool = False,
             wrap: int = 38):
    """Big-number KPI card in one Axes: the number, one sentence, the change (▲/▼ + color) and the gap to target.

        fig, ax = plt.subplots(figsize=(8, 3.6))
        mv.kpi_card(ax, 62, "254 of 410 critical roles have a ready-now successor", change=14, vs="vs. Mar 2025",
                    target=75, ring_value=62)

    value: a number (formatted with `decimals` and `suffix`) or a ready string.
    change: the delta behind `delta_label` (green only when favorable per `better`, always with its arrow).
    target: adds "N pts short of the 75% target" in orange text (a shortfall is worse) or "▲ N pts above ..." green.
    ring_value: 0-100 draws a progress ring on the left with the number inside it (plus the target tick).
    dark: white text on the dark surface (also pass facecolor=mv.colors.surface_dark to mv.save).
    Returns SimpleNamespace(number, sentence, change, target, ring).
    """
    ax.axis("off")
    num = value if isinstance(value, str) else f"{value:,.{decimals}f}{suffix}"
    body = "white" if dark else C.text
    lines = [(_wrap(sentence, wrap), LABEL + 2, body, 400)]
    chg = tgt = None
    if change is not None:
        t, col = delta_label(change, unit=unit, vs=vs, better=better, decimals=decimals)
        if dark:
            col = {C.positive_text: C.positive, C.negative_text: C.negative}.get(col, "white")
        lines.append((t, LABEL + 1, col, 600))
    if target is not None:
        if target_text is None:
            cur = float(ring_value if ring_value is not None else value if not isinstance(value, str) else np.nan)
            if cur != cur:
                raise ValueError("pass target_text= when value is a string")
            gap = target - cur
            unit_t = unit if suffix == "%" else f" {suffix}".rstrip() if suffix else ""
            if gap > 0:
                target_text = f"{gap:,.{decimals}f}{unit_t} short of the {target:g}{suffix} target"
                tcol = C.negative if dark else C.negative_text
            else:
                target_text = f"{UP} {-gap:,.{decimals}f}{unit_t} above the {target:g}{suffix} target" if gap else \
                    f"Target of {target:g}{suffix} met"
                tcol = C.positive if dark else C.positive_text
        else:
            tcol = "white" if dark else C.text
        lines.append((target_text, LABEL + 1, tcol, 600))
    rg = None
    if ring_value is not None:
        fig = ax.figure
        bb = ax.get_position()
        w_in, h_in = bb.width * fig.get_figwidth(), bb.height * fig.get_figheight()
        frac = min(0.5, h_in / w_in)
        rax = ax.inset_axes([0, 0, frac, 1])
        rax.set_xlim(-1.45, 1.45)
        rax.set_ylim(-1.45, 1.45)
        rax.set_aspect("equal", anchor="W")
        rax.axis("off")
        rg = ring(rax, ring_value, target=target, dark=dark)
        inner_pt = min(h_in, frac * w_in) * 72 * 0.8 * (2 * 0.82) / 2.9    # hole of the ring, after mv.layout
        size = min(KPI_PT, 0.66 * inner_pt / (_text_width_pt(ax, num, 10, KPI_WEIGHT) / 10))
        number = big(rax, 0, 0, num, size=size, ha="center", va="center", dark=dark)
        anchor = ax.annotate("", (frac + 0.02, 0.8), xycoords="axes fraction")
        texts = _chain(ax, anchor, lines, gap=0)
    else:
        number = big(ax, 0, 1, num, ha="left", va="top", transform=ax.transAxes, dark=dark)
        texts = _chain(ax, number, lines, gap=8)
    sent = texts[0]
    rest = texts[1:]
    if change is not None:
        chg = rest.pop(0)
    if target is not None:
        tgt = rest.pop(0)
    return SimpleNamespace(number=number, sentence=sent, change=chg, target=tgt, ring=rg)


def kpi_row(ax, cards: Sequence[dict], *, size: float | None = None, dark: bool = False, separators: bool = True):
    """A row of KPI cards with identical anatomy: name, number, change. One Axes, equal columns.

        cards = [dict(name="Internal fill rate", value="34%", change=3, vs="vs. FY25"),
                 dict(name="Days to fill", value="47", change=4, unit=" days", better="down", vs="vs. FY25")]
        mv.kpi_row(ax, cards)

    Each card: name, value (string), and optionally change, unit (default " pts"), vs, better ("up" / "down" /
    None), decimals. Thin grey rules separate the cards (flat, no boxes or shadows).
    Returns a list of SimpleNamespace(name, number, change), one per card.
    """
    ax.axis("off")
    n = len(cards)
    if not n:
        raise ValueError("kpi_row needs at least one card")
    size = size or KPI_PT * 0.75
    out = []
    for i, c in enumerate(cards):
        x = i / n
        if separators and i:
            ax.plot([x - 0.02, x - 0.02], [0.02, 0.98], transform=ax.transAxes, color=C.grid, lw=0.8)
        name = ax.text(x, 1, c["name"], transform=ax.transAxes, ha="left", va="top", fontsize=LABEL + 1,
                       color="white" if dark else C.text)
        number = ax.annotate(c["value"], (0, 0), xycoords=name, xytext=(0, -4), textcoords="offset points",
                             ha="left", va="top", fontsize=size, fontweight=KPI_WEIGHT,
                             color="white" if dark else C.headline)
        chg = None
        if c.get("change") is not None:
            t, col = delta_label(c["change"], unit=c.get("unit", " pts"), vs=c.get("vs", ""),
                                 better=c.get("better", "up"), decimals=c.get("decimals", 0))
            if dark:
                col = {C.positive_text: C.positive, C.negative_text: C.negative}.get(col, "white")
            chg = ax.annotate(t, (0, 0), xycoords=number, xytext=(0, -4), textcoords="offset points", ha="left",
                              va="top", fontsize=LABEL, fontweight=600, color=col, **_fam(t))
        out.append(SimpleNamespace(name=name, number=number, change=chg))
    return out


# ------------------------------------------------------------------ STATUS (RAG + symbol + word)
_SYM = None


def _symbols():
    """Symbol shapes drawn as stroked paths, so they never depend on a font having ✓ or ✕."""
    global _SYM
    if _SYM is None:
        from matplotlib.path import Path as P

        check = P([(-0.8, 0.05), (-0.2, -0.6), (0.8, 0.65)], [P.MOVETO, P.LINETO, P.LINETO])
        cross = P([(-0.7, -0.7), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7)], [P.MOVETO, P.LINETO, P.MOVETO, P.LINETO])
        bang = P([(0, -0.1), (0, 1.0), (0, -0.62), (0, -0.92)], [P.MOVETO, P.LINETO, P.MOVETO, P.LINETO])
        dash = P([(-0.75, 0), (0.75, 0), (0, 1.0), (0, -1.0)], [P.MOVETO, P.LINETO, P.MOVETO, P.MOVETO])
        _SYM = {"on_track": check, "done": check, "off_track": cross, "at_risk": bang, "not_started": dash}
    return _SYM


def status_key(key: str) -> str:
    """Normalize a status name: 'On track', 'on-track' and 'on_track' -> 'on_track'; 'complete' -> 'done'."""
    k = str(key).strip().lower().replace("-", "_").replace(" ", "_")
    k = {"complete": "done", "completed": "done", "off": "off_track", "risk": "at_risk"}.get(k, k)
    if k not in STATUS:
        raise ValueError(f"unknown status {key!r}; use one of {', '.join(STATUS)} (status colors only mark status)")
    return k


def sdot(ax, x, y, key: str, *, size: float = 12.0, transform=None, offset=(0.0, 0.0), z: int = 6):
    """Status dot: the status color with its symbol drawn inside (✓ ! ✕ –), white or navy ink by contrast.

        mv.sdot(ax, 3, 0, "at_risk")                                       # one cell of a status-history grid
        mv.titles(fig, "...", "..."); mv.source(fig, "Source: ...")

    size: diameter in points. transform / offset (points): place it in any coordinates without moving the limits.
    A dot alone suits a dense grid whose words appear elsewhere (a key or a "now" column); otherwise use `status`.
    Returns SimpleNamespace(dot, symbol, key).
    """
    k = status_key(key)
    col = STATUS[k]["value"]
    dot = _mark(ax, x, y, "o", size, transform=transform, offset=offset, face=col, z=z)
    sym = _mark(ax, x, y, _symbols()[k], size * 0.5, transform=transform, offset=offset, edge=text_on(col),
                lw=max(1.0, size * 0.13), z=z + 1)
    return SimpleNamespace(dot=dot, symbol=sym, key=k)


def status(ax, x, y, key: str, *, size: float = 12.0, fontsize: float | None = None, transform=None,
           offset=(0.0, 0.0), bold: bool | None = None, z: int = 6):
    """Status pill: color + symbol + word, never color alone. Off track and At risk are bold navy by default.

        mv.status(ax, 0.02, 0.5, "off_track", transform=ax.transAxes)       # ● ✕ Off track
        mv.titles(fig, "...", "..."); mv.source(fig, "Source: ...")

    Returns SimpleNamespace(dot, symbol, text, key).
    """
    d = sdot(ax, x, y, key, size=size, transform=transform, offset=(offset[0] + size / 2, offset[1]), z=z)
    b = d.key in ("off_track", "at_risk") if bold is None else bold
    t = ax.annotate(STATUS[d.key]["label"], (x, y), xycoords=transform or ax.transData,
                    xytext=(offset[0] + size + 4, offset[1]), textcoords="offset points", ha="left", va="center",
                    fontsize=fontsize or LABEL, color=C.headline if b else C.text, fontweight=600 if b else 400,
                    annotation_clip=False, zorder=z)
    return SimpleNamespace(dot=d.dot, symbol=d.symbol, text=t, key=d.key)


def status_column(ax, statuses: Sequence[str], y: Sequence[float] | None = None, *, x: float = 1.0,
                  offset: float = 14.0, header: str | None = "Status", size: float = 11.0):
    """A status column beside a chart's rows: pills at axes-fraction `x`, `offset` points to the right.

        bars = ax.barh(df.workstream, df.budget_used_pct)
        mv.status_column(ax, df.status)                                     # y defaults to 0..n-1 (barh rows)
        mv.titles(fig, "...", "..."); mv.source(fig, "Source: ...")

    Returns a list of the `status` namespaces.
    """
    y = list(range(len(statuses))) if y is None else list(y)
    tr = ax.get_yaxis_transform()                              # x in axes fraction, y in data
    out = [status(ax, x, yy, s, size=size, transform=tr, offset=(offset, 0)) for s, yy in zip(statuses, y)]
    if header:
        ax.annotate(header, (x, 1), xycoords="axes fraction", xytext=(offset, 4), textcoords="offset points",
                    ha="left", va="bottom", fontsize=SMALL + 1, color=C.text_muted, annotation_clip=False)
    return out


def _sort_exceptions(recs, field):
    return sorted(recs, key=lambda r: STATUS_ORDER.index(status_key(r[field])))


def _next_milestone(ms, name):
    left = [m for m in ms if m["workstream"] == name and m.get("state") != "met"]
    if not left:
        return "All milestones met", False
    m = left[0]
    due = _month(m["due"])
    if m.get("state") == "missed":
        return f"{m['milestone']}\nMissed {_mon(due)}; no new date", True
    if m.get("state") == "moved":
        fc = _month(m.get("forecast"))
        return f"{m['milestone']}\n{_mon(fc, True)} (was {_mon(due)})", True
    return f"{m['milestone']}\n{_mon(due, True)}", False


def tracker(ax, plan, *, milestones=None, columns: Sequence[tuple[str, str]] | None = None, name: str = "workstream",
            status_field: str = "status", owner: str | None = "owner", order: bool = True, rollup: bool = True,
            widths: Sequence[float] | None = None, fit: bool = True):
    """Initiative tracker table: status pill, workstream and owner, next milestone, what changed. Exceptions first.

        plan = pd.read_csv("examples/data/initiative_plan.csv")
        mv.tracker(ax, plan, milestones=pd.read_csv("examples/data/initiative_milestones.csv"))
        mv.titles(fig, "Three of seven workstreams need a decision", f"Status as of 31 Mar 2026")

    plan: DataFrame, CSV path or list of dicts with `name`, `status_field` and (optionally) `owner` columns.
    milestones: adds "Next milestone" (first not met: missed and moved ones say so in bold navy).
    columns: extra (header, field) columns; default [("What changed", "what_changed")] when that field exists.
    rollup: a line over the table counting workstreams per status, each with its dot.
    fit: resize the figure height so every row has room (call before mv.titles / mv.save).
    Returns SimpleNamespace(rows, statuses, texts, row_y).
    """
    recs = _records(plan)
    if not recs:
        raise ValueError("tracker needs at least one row")
    ms = _records(milestones) if milestones is not None else None
    if order:
        recs = _sort_exceptions(recs, status_field)
    if columns is None:
        columns = [("What changed", "what_changed")] if "what_changed" in recs[0] else []
    heads = ["Status", "Workstream" + (", owner" if owner else "")] + (["Next milestone"] if ms else []) + \
        [h for h, _ in columns]
    widths = list(widths or ([0.17, 0.28] + ([0.26] if ms else []) + [0.0] * len(columns)))
    rest = max(0.0, 1 - sum(widths))
    free = [i for i, w in enumerate(widths) if not w]
    for i in free:
        widths[i] = rest / len(free)
    xs = np.concatenate([[0], np.cumsum(widths)])[:-1]
    fig = ax.figure
    ax_w_pt = ax.get_position().width * fig.get_figwidth() * 72
    size = LABEL - 1

    def chars(col):
        return max(8, int(widths[col] * ax_w_pt / (0.5 * size)) - 1)

    cells = []
    for r in recs:
        exc = status_key(r[status_field]) in ("off_track", "at_risk")
        row = [None, (str(r[name]), exc, str(r[owner]) if owner and r.get(owner) else None)]
        if ms:
            row.append(_next_milestone(ms, r[name]))
        for _, field in columns:
            row.append(str(r.get(field) or ""))
        cells.append(row)

    def lines_of(row):
        n = 2 if row[1][2] else len(textwrap.wrap(row[1][0], chars(1)))
        k = 2
        if ms:
            first, second = row[2][0].split("\n", 1) if "\n" in row[2][0] else (row[2][0], "")
            n = max(n, len(textwrap.wrap(first, chars(2))) + (1 if second else 0))
            k = 3
        for j in range(k, len(row)):
            n = max(n, len(textwrap.wrap(row[j], chars(j))) or 1)
        return max(n, 1)

    nlines = [lines_of(r) for r in cells]
    line = 1.0                                                # one text line = 1 data unit
    pad = 0.7
    heights = [n * line + pad for n in nlines]
    head_h = 1.6
    total = head_h + sum(heights)
    if fit:
        line_in = size * 1.3 / 72
        need = total * line_in
        frac = ax.get_position().height
        fig.set_figheight(max(fig.get_figheight() * 0.5, need / frac + (1.4 if rollup else 1.1)))
    ax.set_xlim(0, 1)
    ax.set_ylim(total, -0.2)
    ax.axis("off")
    for j, h in enumerate(heads):
        ax.text(xs[j], head_h - 0.45, h, ha="left", va="bottom", fontsize=size, color=C.headline, fontweight=700)
    ax.plot([0, 1], [head_h - 0.2] * 2, color=C.axis, lw=0.75)
    y = head_h
    statuses, texts, row_y = [], [], []
    for r, row, h in zip(recs, cells, heights):
        top = y + pad / 2
        row_y.append(top)
        statuses.append(status(ax, xs[0], top + 0.55, r[status_field], size=11, fontsize=size))
        nm, exc, own = row[1]
        texts.append(ax.text(xs[1], top, _wrap(nm, chars(1)), ha="left", va="top", fontsize=size,
                             color=C.headline if exc else C.text, fontweight=600 if exc else 400))
        if own:
            texts.append(ax.text(xs[1], top + line, own, ha="left", va="top", fontsize=SMALL, color=C.text_muted))
        j0 = 2
        if ms:
            txt, hot = row[2]
            first, second = txt.split("\n", 1) if "\n" in txt else (txt, "")
            w1 = _wrap(first, chars(2))
            texts.append(ax.text(xs[2], top, w1, ha="left", va="top", fontsize=size, color=C.text))
            if second:
                texts.append(ax.text(xs[2], top + line * (w1.count("\n") + 1), second, ha="left", va="top",
                                     fontsize=size, color=C.headline if hot else C.text_muted,
                                     fontweight=600 if hot else 400))
            j0 = 3
        for j in range(j0, len(row)):
            texts.append(ax.text(xs[j], top, _wrap(row[j], chars(j)), ha="left", va="top", fontsize=size,
                                 color=C.text, linespacing=1.15))
        y += h
        ax.plot([0, 1], [y, y], color=C.grid, lw=0.6, zorder=0)
    if rollup:
        counts = {}
        for r in recs:
            k = status_key(r[status_field])
            counts[k] = counts.get(k, 0) + 1
        x = 0.0
        lead = f"{len(recs)} workstreams"
        ax.annotate(lead, (0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points", ha="left",
                    va="bottom", fontsize=size + 1, color=C.headline, fontweight=600, annotation_clip=False)
        x = _text_width_pt(ax, lead, size + 1, 600) + 14
        for k in STATUS_ORDER:
            if k not in counts:
                continue
            sdot(ax, 0, 1, k, size=10, transform=ax.transAxes, offset=(x + 5, 8 + 0.36 * (size + 1)))
            t = f"{counts[k]} {STATUS[k]['label'].lower()}"
            ax.annotate(t, (0, 1), xycoords="axes fraction", xytext=(x + 13, 8), textcoords="offset points",
                        ha="left", va="bottom", fontsize=size, color=C.text, annotation_clip=False)
            x += 13 + _text_width_pt(ax, t, size) + 12
    return SimpleNamespace(rows=recs, statuses=statuses, texts=texts, row_y=row_y)


def _milestone_mark(ax, x, y, kind, size=8.0, *, transform=None, offset=(0, 0), z=7):
    if kind == "met":
        return _mark(ax, x, y, "D", size, transform=transform, offset=offset, face=C.total, edge="white", lw=1, z=z)
    if kind in ("upcoming", "due", "moved"):
        return _mark(ax, x, y, "D", size, transform=transform, offset=offset, face="white", edge=C.total, lw=1.3, z=z)
    if kind == "was":
        return _mark(ax, x, y, "D", size, transform=transform, offset=offset, face="white", edge=C.text_muted, lw=1,
                     z=z)
    if kind == "missed":
        return _mark(ax, x, y, "X", size * 1.15, transform=transform, offset=offset, face=STATUS["off_track"]["value"],
                     edge="white", lw=0.8, z=z)
    raise ValueError(f"unknown milestone state {kind!r}: use met, upcoming, moved or missed")


def roadmap(ax, plan, milestones=None, *, start=None, end=None, today=None, today_label: str | None = None,
            fy_start: int = 4, name: str = "workstream", status_field: str = "status", owner: str | None = "owner",
            begin: str = "start", finish: str = "end", focus: Iterable[str] | None = None, phases=None,
            key: bool = True, fit: bool = True):
    """Roadmap (Gantt): one row per workstream with its status pill, a bar per plan, milestones, a today line.

        plan = pd.read_csv("examples/data/initiative_plan.csv")
        ms = pd.read_csv("examples/data/initiative_milestones.csv")
        mv.roadmap(ax, plan, ms, today="2026-03", today_label="Today, 31 Mar 2026")

    plan: rows with `name`, `begin`, `finish` (months as "YYYY-MM" or dates), `status_field` and optional `owner`.
    milestones: rows with workstream, milestone, due, forecast, state: met (navy ◆), upcoming (hollow ◇), missed
        (red ✕) or moved (the original date hollow grey, an arrow to the forecast, "Moved Mar to Jun").
    start / end: the window (default: the plan's first and last month). fy_start: the month the fiscal year starts
        (4 = April, McKesson; 1 = calendar years); quarters and fiscal years label the top.
    focus: workstreams whose bars are blue (default: the off-track ones); the rest stay grey, not-started light grey.
    today: the as-of month; the dashed navy line sits at the end of that month.
    phases: [(name, start, end)] months for a band over the header.
    Returns SimpleNamespace(bars, statuses, names, months, x_of).
    """
    recs = _records(plan)
    ms = _records(milestones) if milestones is not None else []
    n = len(recs)
    if not n:
        raise ValueError("roadmap needs at least one row")
    m0 = _month(start) if start is not None else min(_month(r[begin]) for r in recs)
    m1 = _month(end) if end is not None else max(_month(r[finish]) for r in recs)
    span = m1 - m0 + 1

    def X(m):
        return m - m0

    if focus is None:
        focus = {r[name] for r in recs if status_key(r[status_field]) == "off_track"}
    focus = set(focus)
    fig = ax.figure
    if fit:
        frac = ax.get_position().height
        fig.set_figheight(max(fig.get_figheight() * 0.5, (n * 0.42 + 0.2) / frac + 1.6))
    ys = np.arange(n)
    cols = []
    for r in recs:
        k = status_key(r[status_field])
        cols.append(C.focus if r[name] in focus else C.context_light if k == "not_started" else C.context)
    lefts = [X(_month(r[begin])) for r in recs]
    widths = [X(_month(r[finish])) + 1 - l0 for r, l0 in zip(recs, lefts)]
    bars = ax.barh(ys, widths, left=lefts, height=0.34, color=cols, lw=0, zorder=3)
    ax.set_xlim(0, span)
    ax.set_ylim(n - 0.5, -0.65)
    ax.set_yticks([])
    ax.set_xticks([])
    _plain(ax)
    # quarter rules and header: quarters, fiscal years, optional phases (all in points above the axes)
    xtr = ax.get_xaxis_transform()                            # x in data, y in axes fraction
    for m in range(m0, m1 + 1):
        c = m % 12 + 1
        if (c - fy_start) % 3 == 0 and m != m0:
            ax.axvline(X(m), color=C.grid, lw=0.7, zorder=0)
    for m in range(m0, m1 + 1):
        c = m % 12 + 1
        q_first = (c - fy_start) % 3 == 0
        if q_first or m == m0:
            q = ((c - fy_start) % 12) // 3 + 1
            q_end = min(m1 + 1, m + 3 - (c - fy_start) % 3)
            ax.annotate(f"Q{q}", ((X(m) + X(q_end)) / 2, 1), xycoords=xtr, xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=SMALL + 1, color=C.text_muted, annotation_clip=False)
        if c == fy_start or m == m0:
            fy = m // 12 + (1 if fy_start > 1 and c >= fy_start else 0)
            y_end = min(m1 + 1, m + 12 - (c - fy_start) % 12)
            label = f"FY{fy % 100:02d}" if fy_start > 1 else str(fy)
            if y_end - m >= 3:
                ax.annotate(label, ((X(m) + X(y_end)) / 2, 1), xycoords=xtr, xytext=(0, 20),
                            textcoords="offset points", ha="center", va="bottom", fontsize=TICK,
                            color=C.headline, fontweight=600, annotation_clip=False)
    if phases:
        for i, (pn, a, b) in enumerate(phases):
            a = X(_month(a))
            ax.annotate(pn, (a, 1), xycoords=xtr, xytext=(4, 40), textcoords="offset points", ha="left", va="bottom",
                        fontsize=SMALL + 1, color=C.headline, annotation_clip=False,
                        bbox=dict(boxstyle="square,pad=0.3", fc=C.context_light if i % 2 == 0 else C.grid, ec="none"))
    ax.plot([0, 1], [1, 1], transform=ax.transAxes, color=C.axis, lw=0.75, clip_on=False)
    # left columns: name (+ owner) and status, laid out in points left of the axes
    size = LABEL
    stat_w = 12 + 4 + max(_text_width_pt(ax, STATUS[status_key(r[status_field])]["label"], size, 600) for r in recs)
    name_w = max(_text_width_pt(ax, str(r[name]), size, 600) for r in recs)
    status_x = -(stat_w + 12)
    name_x = status_x - 14 - name_w
    ytr = ax.get_yaxis_transform()                            # x in axes fraction, y in data
    names, statuses = [], []
    for i, r in enumerate(recs):
        hot = r[name] in focus
        own = owner and r.get(owner)
        names.append(ax.annotate(str(r[name]), (0, i), xycoords=ytr, xytext=(name_x, 5 if own else 0),
                                 textcoords="offset points", ha="left", va="center", fontsize=size,
                                 color=C.headline if hot else C.text, fontweight=600 if hot else 400,
                                 annotation_clip=False))
        if own:
            ax.annotate(str(r[owner]), (0, i), xycoords=ytr, xytext=(name_x, -7), textcoords="offset points",
                        ha="left", va="center", fontsize=SMALL, color=C.text_muted, annotation_clip=False)
        statuses.append(status(ax, 0, i, r[status_field], size=12, fontsize=size, transform=ytr,
                               offset=(status_x, 0)))
    for txt, x in (("Workstream" + (" and owner" if owner else ""), name_x), ("Status", status_x)):
        ax.annotate(txt, (0, 1), xycoords="axes fraction", xytext=(x, 5), textcoords="offset points", ha="left",
                    va="bottom", fontsize=SMALL + 1, color=C.text_muted, annotation_clip=False)
    # milestones
    row_of = {r[name]: i for i, r in enumerate(recs)}
    for m in ms:
        if m.get("workstream") not in row_of:
            continue
        i = row_of[m["workstream"]]
        state = m.get("state") or "upcoming"
        due = _month(m["due"])
        if state == "moved" and m.get("forecast"):
            fc = _month(m["forecast"])
            xa, xb = X(due) + 0.5, X(fc) + 0.5
            _milestone_mark(ax, xa, i, "was")
            ax.annotate("", (xb, i), (xa, i), arrowprops=dict(arrowstyle="-|>,head_length=0.4,head_width=0.22",
                                                             color=C.annotation, lw=1.1, shrinkA=5, shrinkB=6),
                        zorder=6)
            _milestone_mark(ax, xb, i, "moved")
            ax.annotate(f"Moved {_mon(due)} to {_mon(fc)}", ((xa + xb) / 2, i), xytext=(0, 9),
                        textcoords="offset points", ha="center", va="bottom", fontsize=SMALL, color=C.annotation,
                        fontweight=600, zorder=9, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
        else:
            _milestone_mark(ax, X(due) + 0.5, i, state)
    if today is not None:
        tx = X(_month(today)) + 1
        ax.axvline(tx, color=C.total, lw=1.1, ls=(0, (3, 2.5)), zorder=8)
        ax.annotate(today_label or f"Today, {_mon(_month(today), True)}", (tx, 0), xycoords=xtr, xytext=(0, -4),
                    textcoords="offset points", ha="center", va="top", fontsize=SMALL, color=C.annotation,
                    fontweight=600, annotation_clip=False)
    if key:
        x = name_x
        for kind, lab in (("met", "Met"), ("upcoming", "Due"), ("missed", "Missed"), ("was", "Original date")):
            _milestone_mark(ax, 0, 0, kind, 7, transform=ax.transAxes, offset=(x + 4, -26))
            ax.annotate(lab, (0, 0), xycoords="axes fraction", xytext=(x + 11, -26), textcoords="offset points",
                        ha="left", va="center", fontsize=SMALL, color=C.text, annotation_clip=False)
            x += 11 + _text_width_pt(ax, lab, SMALL) + 14
    return SimpleNamespace(bars=bars, statuses=statuses, names=names, months=(m0, m1), x_of=lambda v: X(_month(v)))


# ------------------------------------------------------------------ SMALL MULTIPLES
def multiples(fig, data, *, x: Sequence | None = None, ncols: int = 3, order: str | Sequence[str] = "last",
              worse: Iterable[str] = (), focus: Iterable[str] | None = None, context: bool = True,
              fmt: str = "{:.1f}", ylim: tuple[float, float] | None = None, yticks: Sequence[float] | None = None,
              xticks: Sequence[int] | None = None):
    """Small multiples on one shared scale: each panel's series in blue over the others in light grey.

        bu = {"Oncology": [9.0, 9.9, 11.2, 13.1], "Technology": [11.8, 10.9, 9.8, 9.0], ...}
        axes = mv.multiples(fig, bu, x=["Q1", "Q2", "Q3", "Q4"], worse={"Oncology"})
        mv.titles(fig, "Oncology is the only unit where attrition rose", "Regretted attrition, T12M (%)")

    data: {name: values} or a DataFrame (one column per panel, the index as x).
    order: "last" (latest value, highest first), "name", or an explicit list of names.
    worse: panels drawn orange (a rise in a bad measure, a fall in a good one); focus: panels in blue with a bold
        title (default: every panel's own line is blue). Start and end values are labelled; y ticks only on the left
        column, x ticks only on the bottom row (the first and last x).
    Returns SimpleNamespace(axes, order) with axes as a flat list in panel order (extra grid cells removed).
    """
    if hasattr(data, "columns") and hasattr(data, "index"):
        if x is None:
            x = [str(i) for i in data.index]
        series = {str(c): _floats(data[c], str(c)) for c in data.columns}
    else:
        series = {str(k): _floats(v, str(k)) for k, v in dict(data).items()}
    if not series:
        raise ValueError("multiples needs at least one series")
    lens = {len(v) for v in series.values()}
    if len(lens) != 1:
        raise ValueError("every series needs the same number of points")
    npts = lens.pop()
    x = list(x) if x is not None else list(range(npts))
    if isinstance(order, str):
        names = (sorted(series, key=lambda k: -series[k][-1]) if order == "last" else sorted(series)
                 if order == "name" else None)
        if names is None:
            raise ValueError("order must be 'last', 'name' or a list of names")
    else:
        names = [str(o) for o in order]
    worse = set(worse)
    focus = set(series) if focus is None else set(focus)
    nrows = math.ceil(len(names) / ncols)
    grid = fig.subplots(nrows, ncols, sharex=True, sharey=True, squeeze=False)
    allv = np.concatenate(list(series.values()))
    if ylim is None:
        lo = 0.0 if allv.min() >= 0 else float(allv.min()) * 1.1
        ylim = (lo, float(allv.max()) * 1.12)
    ctx_lw = TOKENS["chart"]["line"]["context_width_px"]
    xi = np.arange(npts)
    axes = []
    for idx, ax in enumerate(grid.flat):
        if idx >= len(names):
            ax.remove()
            continue
        nm = names[idx]
        r, c = divmod(idx, ncols)
        if context:
            for other, ov in series.items():
                if other != nm:
                    ax.plot(xi, ov, color=C.context_light, lw=ctx_lw, zorder=1)
        bad, hot = nm in worse, nm in focus or nm in worse
        col = C.negative if bad else C.focus if hot else C.context
        v = series[nm]
        ax.plot(xi, v, color=col, lw=2.25, zorder=3, solid_capstyle="butt")
        tc = C.negative_text if bad else C.focus if hot else C.text
        for k, ha, w in ((0, "right", 400), (npts - 1, "left", 700)):
            ax.annotate(fmt.format(v[k]), (xi[k], v[k]), xytext=(-4 if ha == "right" else 4, 0),
                        textcoords="offset points", ha=ha, va="center", fontsize=SMALL + 1, fontweight=w, color=tc,
                        path_effects=halo(), annotation_clip=False)
        ax.set_title(nm, loc="left", fontsize=TICK, pad=6, color=C.headline if (bad or (hot and focus != set(series)))
                     else C.text, fontweight=600 if (bad or (hot and focus != set(series))) else 400)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(C.axis)
        ax.grid(axis="y", color=C.grid, lw=0.6)
        ax.grid(axis="x", visible=False)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, labelsize=SMALL + 1, colors=C.text_muted)
        axes.append(ax)
    ax0 = axes[0]
    ax0.set_ylim(*ylim)
    if yticks is not None:
        ax0.set_yticks(yticks)
    else:
        from matplotlib.ticker import MaxNLocator

        ax0.yaxis.set_major_locator(MaxNLocator(3))
    ticks = list(xticks) if xticks is not None else [0, npts - 1]
    ax0.set_xticks(ticks, [str(x[t]) for t in ticks])
    ax0.set_xlim(-0.8, npts - 0.2)
    last_row = {divmod(i, ncols)[1]: i for i in range(len(names))}       # lowest panel per column gets x labels
    for i, ax in enumerate(axes):
        ax.tick_params(axis="x", labelbottom=i == last_row[i % ncols])
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
    return SimpleNamespace(axes=axes, order=names)


__all__ = ["waterfall", "hstack", "dumbbell", "rank_slope", "heat", "key_strip", "big", "small", "ring", "kpi_card",
           "kpi_row", "delta_label", "sdot", "status", "status_key", "status_column", "tracker", "roadmap",
           "multiples", "STATUS_ORDER"]
