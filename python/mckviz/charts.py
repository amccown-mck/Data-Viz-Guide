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

from . import DIVERGING, FONT, MINUS, SEQUENTIAL, STATUS, TOKENS, _SCALE, colors as C, few_highlights, halo, signed, text_on

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
    focus: the delta steps the headline names, in blue (everything else stays grey).
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
    few_highlights(focus, sum(k == "delta" for k in kinds), "steps")
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


# ------------------------------------------------------------------ BUBBLE SCATTER
def _key_values(lo: float, hi: float) -> list[float]:
    """Two or three round values for a size key: the largest 1-2-5 value at or under the biggest bubble, about half
    of it and a tenth of it (10,000 / 5,000 / 1,000), dropping a tenth smaller than every bubble."""
    if hi <= 0:
        return []
    e = 10 ** math.floor(math.log10(hi))
    m = max(k for k in (1, 2, 5) if k * e <= hi)
    top = m * e
    vals = [top / 10, top / (2.5 if m == 5 else 2), top]
    return [v for v in vals if v >= lo / 2 or v == top]


def size_key(ax, values: Sequence[float], area: float, *, title: str = "Bubble area", fmt: str = "{:,.0f}",
             side: str = "right", color: str | None = None):
    """A size key for a bubble chart, above the plot, so it can never sit on the data or pass for a data bubble.

        K = 1800 / df.headcount.max()                     # marker area (pt², scatter's s=) per person
        ax.scatter(df.x, df.y, s=df.headcount * K, ...)
        mv.size_key(ax, [1_000, 5_000, 10_000], K, title="Headcount (bubble area)")

    values: two or three round values in the data's units. area: the marker area per unit, the scale the bubbles use,
    so each key circle is the size a data bubble of that value is. side: "right" (default) or "left" end of the plot's
    top edge. The key counts as part of the plot, so mv.layout keeps the subtitle clear of it. Returns the key box.
    """
    from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea, HPacker, TextArea
    from matplotlib.patches import Circle

    if side not in ("right", "left"):
        raise ValueError('side is "right" or "left"')
    text = dict(fontsize=SMALL, color=C.text_muted)
    entries = []
    for v in values:
        d = max(math.sqrt(max(v, 0) * area), 2.0)          # scatter's s is the marker's square: a circle sqrt(s) across
        da = DrawingArea(d, d, 0, 0)
        da.add_artist(Circle((d / 2, d / 2), d / 2, fc=color or C.context_light, ec=C.axis, lw=0.75))
        entries.append(HPacker(children=[da, TextArea(fmt.format(v), textprops=text)], align="center", pad=0, sep=4))
    row = HPacker(children=[TextArea(title, textprops=text)] + entries, align="center", pad=0, sep=12)
    box = AnchoredOffsetbox(loc=f"lower {side}", child=row, pad=0, borderpad=0, frameon=False,
                            bbox_to_anchor=(1 if side == "right" else 0, 1),
                            bbox_transform=_offset(ax.transAxes, ax.figure, 0, 8))
    box.set_zorder(6)
    ax.add_artist(box)
    box.set_clip_on(False)                                    # as a legend: outside the plot, and measured there
    return box


def _overlap(bb, circles, rects, frame, own=None) -> float:
    """How badly a text box collides: pixels of bubble it covers, of other labels it covers, and of it outside the
    plot frame. For a point's name (own = its bubble), also how near another bubble sits compared with its own
    (within 4 px counts), so a name can't read as another point's. 0 means clear."""
    score = 0.0
    gaps = []
    for cx, cy, r in circles:
        dx = max(bb.x0 - cx, 0, cx - bb.x1)
        dy = max(bb.y0 - cy, 0, cy - bb.y1)
        d = math.hypot(dx, dy)
        score += max(r - d, 0)
        gaps.append(d - r)
    for o in rects:
        w = min(bb.x1, o.x1) - max(bb.x0, o.x0)
        h = min(bb.y1, o.y1) - max(bb.y0, o.y0)
        if w > 0 and h > 0:
            score += math.sqrt(w * h)
    score += max(frame.x0 - bb.x0, 0) + max(bb.x1 - frame.x1, 0) + max(frame.y0 - bb.y0, 0) + max(bb.y1 - frame.y1, 0)
    if own is not None and len(gaps) > 1:
        mine = gaps[own]
        nearest = min(g for k, g in enumerate(gaps) if k != own)
        score += 2.0 * max(mine + 4 - nearest, 0)               # as near another bubble as its own: ambiguous
    return score


def _text_box(text, renderer):
    """The box of a label's text alone: an annotation's own extent takes in its leader line, even a hidden one."""
    from matplotlib.text import Text

    if hasattr(text, "update_positions"):
        text.update_positions(renderer)
    return Text.get_window_extent(text, renderer)


def _placer(ax, points, jobs, vlines=(), hlines=()):
    """Place a chart's labels each time the figure is drawn, so they stay clear of the bubbles at the final size:
    mv.layout and picture slides resize the plot after the builder ran, and bubble sizes are in points, not data.
    jobs: (text, options, own) triples, own = the index of the label's bubble in `points` (None for a zone or line
    label); an option is (anchor, offset, ha, va) or, for a far spot drawn with its leader line, (..., True[,
    relpos]), relpos being where on the text the line starts.
    vlines / hlines: x / y values of reference lines that names should not cross. Each label first takes its earliest clear option; then each is moved, in turn, to its best option given
    where the others sit, until nothing improves (a crowded corner gets sorted out, not just the first label)."""
    from matplotlib.artist import Artist
    from matplotlib.transforms import Bbox

    def put(text, anchor, off, ha, va, leader=False, relpos=(0.5, 0.5)):
        text.xy = anchor
        text.set_position(off)
        text.set_ha(ha)
        text.set_va(va)
        if getattr(text, "arrow_patch", None) is not None:
            text.arrow_patch.set_visible(leader)                # a thin line back to the bubble, far labels only
            text._arrow_relpos = relpos                         # where on the text the line starts (read at creation
                                                                # from arrowprops, so set here)

    class Placer(Artist):
        def draw(self, renderer):
            pts = renderer.points_to_pixels(1.0)
            xy = points.get_offset_transform().transform(points.get_offsets())
            circles = [(cx, cy, math.sqrt(s) / 2 * pts) for (cx, cy), s in zip(xy, points.get_sizes())]
            frame = ax.get_window_extent(renderer)
            lines = []                                         # reference lines, 2 px wide, as obstacles for names
            for v in vlines:
                x = ax.transData.transform((v, 0))[0]
                lines.append(Bbox([[x - 1, frame.y0], [x + 1, frame.y1]]))
            for v in hlines:
                y = ax.transData.transform((0, v))[1]
                lines.append(Bbox([[frame.x0, y - 1], [frame.x1, y + 1]]))
            boxes = {}                                         # (job, option) -> text box, measured once per draw

            def box(k, m):
                if (k, m) not in boxes:
                    put(jobs[k][0], *jobs[k][1][m])
                    boxes[k, m] = _text_box(jobs[k][0], renderer).expanded(1.02, 1.04)
                return boxes[k, m]

            def score(k, m, chosen):
                others = [box(o, c) for o, c in chosen.items() if o != k]
                if jobs[k][2] is not None:                     # a point's name keeps off the reference lines
                    others += lines
                led = len(jobs[k][1][m]) > 4 and jobs[k][1][m][4]   # a leader line says whose name it is
                return _overlap(box(k, m), circles, others, frame, None if led else jobs[k][2])

            chosen = {}
            for k, (_, options, _) in enumerate(jobs):         # first pass: the earliest clear option
                best = None
                for m in range(len(options)):
                    s = score(k, m, chosen)
                    if best is None or s < best[0] - 0.5:
                        best = (s, m)
                    if s <= 0.5:
                        break
                chosen[k] = best[1]
            for _ in range(4):                                 # then improve one label at a time
                moved = False
                for k, (_, options, _) in enumerate(jobs):
                    now = score(k, chosen[k], chosen)
                    if now <= 0.5:
                        continue
                    s, m = min((score(k, m, chosen), m) for m in range(len(options)))
                    if s < now - 0.5:
                        chosen[k], moved = m, True
                if not moved:
                    break
            for k, m in chosen.items():
                put(jobs[k][0], *jobs[k][1][m])

        def get_window_extent(self, renderer=None):
            return Bbox.null()

    p = Placer()
    p.set_in_layout(False)
    p.set_zorder(-100)                                         # drawn first, so the labels draw where it put them
    ax.add_artist(p)
    return p


def _point_options(x, y, r, right_first: bool, vertical_first: bool = False):
    """Where a point's label may go, best first: beside the bubble, then above, below and the diagonals (above and
    below first on a strip, where the neighbours sit beside)."""
    d, q = r + 3, 0.72 * r + 2
    right, left = ((d, 0), "left", "center"), ((-d, 0), "right", "center")
    beside = [right, left] if right_first else [left, right]
    vertical = [((0, d), "center", "bottom"), ((0, -d), "center", "top"),   # centred, then hung from either edge
                ((r, d), "right", "bottom"), ((-r, d), "left", "bottom"), ((r, -d), "right", "top"), ((-r, -d), "left", "top")]
    sides = (vertical + beside) if vertical_first else (beside + vertical)
    sides += [((q, q), "left", "bottom"), ((-q, q), "right", "bottom"), ((q, -q), "left", "top"), ((-q, -q), "right", "top")]
    near = [((x, y), off, ha, va) for off, ha, va in sides]
    if vertical_first:                                          # a strip: steps above and below the row, each name
        out = []                                                # starting over its bubble, a vertical leader down
        for k in range(4):
            f = d + 12 + 15 * k
            out += [((x, y), (-1, f), "left", "bottom", True, (0, 0)), ((x, y), (-1, -f), "left", "top", True, (0, 1)),
                    ((x, y), (1, f), "right", "bottom", True, (1, 0)), ((x, y), (1, -f), "right", "top", True, (1, 1))]
        return near + out
    f = d + 16                                                  # then farther out, with a leader line to the bubble
    far = [((0, f), "center", "bottom"), ((0, -f), "center", "top"), ((0.7 * f, 0.7 * f), "left", "bottom"),
           ((-0.7 * f, 0.7 * f), "right", "bottom"), ((0.7 * f, -0.7 * f), "left", "top"),
           ((-0.7 * f, -0.7 * f), "right", "top")]
    return near + [((x, y), off, ha, va, True) for off, ha, va in far]


def _leader(r: float) -> dict:
    """arrowprops for a far label's leader line: hairline grey, from the text to the bubble's edge."""
    return dict(arrowstyle="-", color=C.axis, lw=0.6, shrinkA=1, shrinkB=r + 1)


def _fit(v, rad, extent, extra=()):
    """Axis limits that hold every bubble whole: the data range grown by each bubble's radius (points, on an axis
    `extent` points long), plus the `extra` values (a reference line, a zone edge) and 2% to spare."""
    vals = list(v) + [e for e in extra if e is not None]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or (abs(hi) or 1.0)
    a, b = lo, hi
    for _ in range(4):
        per = (b - a) / extent
        a = min(lo, float(np.min(v - rad * per)))
        b = max(hi, float(np.max(v + rad * per)))
    return (a - 0.02 * span, b + 0.02 * span)


def bubble(ax, x: Sequence[float], y: Sequence[float], size: Sequence[float] | None = None,
           names: Sequence[str] | None = None, *, focus: Iterable[str] = (), accent: str | None = None,
           label: Iterable[str] | None = None, detail: str | None = None, size_label: str | None = None,
           key: bool | Sequence[float] = True, key_fmt: str = "{:,.0f}", max_area: float = 1800.0,
           zone_x: tuple | None = None, zone_y: tuple | None = None, zone_label: str | None = None,
           ref_x: float | None = None, ref_x_label: str | None = None, ref_y: float | None = None,
           ref_y_label: str | None = None, xfmt: str | None = None, yfmt: str | None = None,
           xlabel: str | None = None, ylabel: str | None = None, logx: bool = False):
    """A scatter or bubble scatter, laid out from the data: grey context, the headline's points blue and named, bubble
    area in proportion to `size`, a size key above the plot, and every label placed clear of the bubbles.

        df = pd.read_csv("examples/data/automation_exposure.csv")     # role, headcount, genai_exposure_pct, median_pay_k
        avg = (df.genai_exposure_pct * df.headcount).sum() / df.headcount.sum()
        mv.bubble(ax, df.median_pay_k, df.genai_exposure_pct, df.headcount, df.role,
                  focus=set(df.role[df.genai_exposure_pct >= 50]), size_label="Headcount",
                  zone_y=(50, None), zone_label="High exposure: 50%+ of task hours",
                  ref_y=avg, ref_y_label=f"Workforce average {avg:.0f}%",
                  xfmt="${x:,.0f}K", yfmt="{x:.0f}%", xlabel="Median base pay", ylabel="Task hours exposed to gen AI")

    size: the third measure (headcount, open requisitions); None draws a plain scatter of equal dots, with no key.
        The largest bubble gets `max_area` (pt²); the rest scale by area, never diameter. Largest drawn first.
    focus / accent: the points the headline names, blue / one navy exception (as mv.highlight); with neither, every
        point is blue. label: the names to write on the chart (default: focus and accent); detail: a second line for
        each, formatted with x, y and size ("{y:.0f}%, ${x:.0f}K").
    key: True picks two or three round values; or pass them; False for none. It sits above the plot, top right,
        titled "<size_label> (bubble area)". Say what the area means in the subtitle as well.
    zone_x / zone_y: (low, high) shaded behind the data (None for the axis edge; both for one quadrant), named by
        zone_label. ref_x / ref_y: a dashed navy reference line (an average, a target, 1.0 = balanced), named by its
        label. xfmt / yfmt: tick formats ("${x:,.0f}K"). ylabel sits level at the top left, never rotated.
    logx: a log x axis, for a measure spanning orders of magnitude (write "(log scale)" in xlabel).
    The axis limits fit every bubble, and the labels are placed when the figure is drawn, so they stay clear at
    the final size. Returns SimpleNamespace(points, labels, key, area, order).
    """
    from matplotlib.ticker import StrMethodFormatter

    from . import clean_axes, highlight

    xs, ys = _floats(x, "x"), _floats(y, "y")
    n = len(xs)
    if len(ys) != n:
        raise ValueError("x and y must have the same length")
    if np.isnan(xs).any() or np.isnan(ys).any():
        raise ValueError("x and y have missing values: drop those rows first")
    if logx and (xs <= 0).any():
        raise ValueError("a log x axis needs every x above zero")
    nm = [str(s) for s in names] if names is not None else [""] * n
    if len(nm) != n:
        raise ValueError("names must have the same length as x")
    focus = {str(f) for f in focus}
    hot = focus | ({str(accent)} if accent is not None else set())
    missing = sorted(hot - set(nm))
    if missing:
        raise ValueError(f"focus / accent names not in the data: {', '.join(missing)}")
    if size is not None:
        sz = _floats(size, "size")
        if len(sz) != n or (sz < 0).any() or not sz.max() > 0:
            raise ValueError("size must have one value per point, none negative")
        area = max_area / sz.max()
        s = sz * area
    else:
        sz, area = None, None
        s = np.full(n, (TOKENS["chart"]["marker"]["size_px"] * 0.75 * 1.6) ** 2)
    colors = highlight(nm, focus=focus, accent=accent) if hot else [C.focus] * n
    order = sorted(range(n), key=lambda i: -s[i])               # largest first, so small bubbles stay on top
    pts = ax.scatter(xs[order], ys[order], s=s[order], c=[colors[i] for i in order], alpha=0.9, edgecolors="white",
                     linewidths=1, zorder=2)
    if logx:
        ax.set_xscale("log")

    # Limits that hold every bubble whole: grow each side by the bubbles' radii, in the plot's own pixels, with room
    # to spare because the headline takes height from the plot later.
    fig = ax.figure
    box = ax.get_position()
    w_pt = box.width * fig.get_figwidth() * 72
    h_pt = box.height * fig.get_figheight() * 72 * 0.8
    r = np.sqrt(s) / 2 + 4
    tx = np.log10(xs) if logx else xs

    zx, zy = zone_x or (None, None), zone_y or (None, None)
    xe = [ref_x, *zx]
    x0, x1 = _fit(tx, r, w_pt, [np.log10(e) if (logx and e is not None) else e for e in xe])
    y0, y1 = _fit(ys, r, h_pt, [ref_y, *zy])
    if logx:
        x0, x1 = 10 ** x0, 10 ** x1
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)

    jobs = []
    if zone_x is not None or zone_y is not None:
        from matplotlib.patches import Rectangle
        a = x0 if zx[0] is None else zx[0]
        b = x1 if zx[1] is None else zx[1]
        c = y0 if zy[0] is None else zy[0]
        d = y1 if zy[1] is None else zy[1]
        ax.add_patch(Rectangle((a, c), b - a, d - c, color=C.surface_subtle, lw=0, zorder=0))
        if zone_label:
            t = ax.annotate(zone_label, (b, d), xytext=(-4, -4), textcoords="offset points", fontsize=SMALL,
                            fontweight="bold", color=C.annotation, zorder=4)
            jobs.append((t, [((b, d), (-4, -4), "right", "top"), ((a, d), (4, -4), "left", "top"),
                             ((b, c), (-4, 4), "right", "bottom"), ((a, c), (4, 4), "left", "bottom"),
                             ((b, d), (-4, 3), "right", "bottom"), ((a, d), (4, 3), "left", "bottom"),
                             ((b, c), (-4, -3), "right", "top"), ((a, c), (4, -3), "left", "top")], None))
    for val, lab, horizontal in ((ref_y, ref_y_label, True), (ref_x, ref_x_label, False)):
        if val is None:
            continue
        (ax.axhline if horizontal else ax.axvline)(val, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
        if lab:
            if horizontal:
                end, start = (x1, val), (x0, val)
                opts = [(end, (-2, 3), "right", "bottom"), (end, (-2, -3), "right", "top"),
                        (start, (2, 3), "left", "bottom"), (start, (2, -3), "left", "top")]
            else:
                top, bot = (val, y1), (val, y0)
                opts = [(top, (3, -3), "left", "top"), (top, (-3, -3), "right", "top"),
                        (bot, (3, 3), "left", "bottom"), (bot, (-3, 3), "right", "bottom")]
            t = ax.annotate(lab, opts[0][0], xytext=opts[0][1], textcoords="offset points", fontsize=SMALL,
                            color=C.annotation, path_effects=halo(), zorder=4)
            jobs.append((t, opts, None))

    named = list(label) if label is not None else [v for v in nm if v in hot]
    named = {str(v) for v in named}
    lx0, lx1 = math.log10(x0) if logx else x0, math.log10(x1) if logx else x1
    texts = []
    point_jobs = []
    for i in order[::-1]:                                       # smallest first: they have fewest places to go
        if nm[i] not in named:
            continue
        bold = nm[i] in hot
        text = nm[i]
        if detail:
            text += "\n" + detail.format(x=xs[i], y=ys[i], size=sz[i] if sz is not None else None)
        right_first = (tx[i] - lx0) < 0.75 * (lx1 - lx0)
        opts = _point_options(xs[i], ys[i], math.sqrt(s[i]) / 2, right_first)
        t = ax.annotate(text, (xs[i], ys[i]), xytext=opts[0][1], textcoords="offset points", ha=opts[0][2],
                        va=opts[0][3], fontsize=LABEL - 1 + (1 if bold else 0), fontweight=700 if bold else 400,
                        color=C.headline if bold else C.text_muted, linespacing=1.1, path_effects=halo(), zorder=5,
                        arrowprops=_leader(math.sqrt(s[i]) / 2))
        texts.append(t)
        point_jobs.append((t, opts, order.index(i)))       # its bubble's index in the drawn points
    _placer(ax, pts, point_jobs + jobs, vlines=[ref_x] if ref_x is not None else [],
            hlines=[ref_y] if ref_y is not None else [])     # the names first, then the zone and line labels

    kbox = None
    if sz is not None and key is not False:
        vals = _key_values(float(sz.min()), float(sz.max())) if key is True else list(key)
        title = f"{size_label} (bubble area)" if size_label else "Bubble area"
        kbox = size_key(ax, vals, area, title=title, fmt=key_fmt)

    if xfmt or logx:
        ax.xaxis.set_major_formatter(StrMethodFormatter(xfmt or "{x:g}"))
    if yfmt:
        ax.yaxis.set_major_formatter(StrMethodFormatter(yfmt))
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel, rotation=0, ha="left", va="bottom")
        ax.yaxis.set_label_coords(0, 1.03)
    clean_axes(ax, keep=("bottom",), grid="both")
    return SimpleNamespace(points=pts, labels=texts, key=kbox, area=area, order=[nm[i] for i in order])


def _swarm(xp, r, gap: float = 1.5) -> np.ndarray:
    """Pack circles along one line: each keeps its x and takes the y nearest the line where it touches nothing,
    largest first (all in points). Returns the y offsets."""
    y = np.zeros(len(xp))
    placed: list[int] = []
    for i in sorted(range(len(xp)), key=lambda k: -r[k]):
        spots = [0.0]
        for j in placed:
            d, dx = r[i] + r[j] + gap, xp[i] - xp[j]
            if abs(dx) < d:
                h = math.sqrt(d * d - dx * dx)
                spots += [y[j] + h, y[j] - h]
        for c in sorted(spots, key=abs):
            if all((xp[i] - xp[j]) ** 2 + (c - y[j]) ** 2 >= (r[i] + r[j] + gap) ** 2 - 1e-6 for j in placed):
                y[i] = c
                break
        placed.append(i)
    return y


def bubble_strip(ax, values: Sequence[float], sizes: Sequence[float], names: Sequence[str], *,
                 focus: Iterable[str] = (), accent: str | None = None, label: Iterable[str] | None = None,
                 detail: str | None = None, size_label: str | None = None, key: bool | Sequence[float] = True,
                 key_fmt: str = "{:,.0f}", max_area: float = 2200.0, zone: tuple | None = None,
                 zone_label: str | None = None, ref: float | None = None, ref_label: str | None = None,
                 xfmt: str | None = None, xlabel: str | None = None):
    """Categories on one value axis, each a bubble whose area is its count: how close the categories are on the
    measure and how many people each covers, in one row. Bubbles pack along the line without overlapping.

        df = pd.read_csv("examples/data/automation_exposure.csv")     # role, headcount, genai_exposure_pct, ...
        avg = (df.genai_exposure_pct * df.headcount).sum() / df.headcount.sum()
        mv.bubble_strip(ax, df.genai_exposure_pct, df.headcount, df.role, focus={"Pharmacy Technician"},
                        size_label="Headcount", ref=avg, ref_label=f"Workforce average {avg:.0f}%",
                        xfmt="{x:.0f}%", xlabel="Share of task hours exposed to gen AI")

    values: the measure (position); sizes: the count (area, never diameter; the largest gets `max_area` pt², less
        if the row would not fit the plot's height). names: one per bubble.
    focus / accent: the categories the headline names, blue / one navy exception (as mv.highlight); with neither,
        every bubble is blue. label: the names to write (default: focus and accent; with neither, all of up to 8
        bubbles, else the three largest and the two ends); detail: a second line, formatted with x and size.
    key, size_label, key_fmt: the size key above the plot, as mv.bubble. zone: (low, high) on the value axis, shaded
        and named by zone_label; ref: a dashed navy reference line named by ref_label. xfmt: tick format.
    Labels are placed when the figure is drawn, clear of the bubbles. Returns SimpleNamespace(points, labels, key,
    area, order).
    """
    from matplotlib.ticker import StrMethodFormatter
    from matplotlib.transforms import Affine2D, ScaledTranslation, blended_transform_factory

    from . import clean_axes, highlight

    xs, sz = _floats(values, "values"), _floats(sizes, "sizes")
    nm = [str(s) for s in names]
    n = len(xs)
    if not (len(sz) == len(nm) == n) or n == 0:
        raise ValueError("values, sizes and names must have the same length")
    if np.isnan(xs).any() or np.isnan(sz).any() or (sz < 0).any() or not sz.max() > 0:
        raise ValueError("values and sizes need a number for every bubble, sizes none negative")
    focus = {str(f) for f in focus}
    hot = focus | ({str(accent)} if accent is not None else set())
    missing = sorted(hot - set(nm))
    if missing:
        raise ValueError(f"focus / accent names not in the data: {', '.join(missing)}")
    colors = highlight(nm, focus=focus, accent=accent) if hot else [C.focus] * n

    fig = ax.figure
    box = ax.get_position()
    w_pt = box.width * fig.get_figwidth() * 72
    room = box.height * fig.get_figheight() * 72 * 0.62          # the headline takes height from the plot later
    zx = zone or (None, None)
    area = max_area / sz.max()
    for _ in range(16):                                         # shrink every bubble alike until the row fits
        r = np.sqrt(sz * area) / 2
        x0, x1 = _fit(xs, r + 4, w_pt, [ref, *zx])
        xp = (xs - x0) / (x1 - x0) * w_pt
        y = _swarm(xp, r)
        if 2 * float(np.max(np.abs(y) + r)) <= room:
            break
        area *= 0.8
    s = sz * area
    # y in points from the plot's middle, x in data: the row keeps its shape however the plot is resized
    along = blended_transform_factory(ax.transData, Affine2D().scale(1 / 72) + fig.dpi_scale_trans
                                      + ScaledTranslation(0, 0.5, ax.transAxes))
    order = sorted(range(n), key=lambda i: -s[i])               # largest first, so small bubbles stay on top
    pts = ax.scatter(xs[order], y[order], s=s[order], c=[colors[i] for i in order], alpha=0.9, edgecolors="white",
                     linewidths=1, zorder=2, transform=along)
    ax.set_xlim(x0, x1)
    ax.set_ylim(-1, 1)

    jobs = []
    top = ax.get_xaxis_transform()                              # x in data, y in the plot's height
    if zone is not None:
        a = x0 if zx[0] is None else zx[0]
        b = x1 if zx[1] is None else zx[1]
        ax.axvspan(a, b, color=C.surface_subtle, lw=0, zorder=0)
        if zone_label:
            t = ax.annotate(zone_label, (a, 1), xycoords=top, xytext=(4, -4), textcoords="offset points",
                            fontsize=SMALL, fontweight="bold", color=C.annotation, zorder=4)
            jobs.append((t, [((a, 1), (4, -4), "left", "top"), ((b, 1), (-4, -4), "right", "top"),
                             ((a, 0), (4, 4), "left", "bottom"), ((b, 0), (-4, 4), "right", "bottom")], None))
    if ref is not None:
        ax.axvline(ref, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
        if ref_label:
            opts = [((ref, 1), (3, -3), "left", "top"), ((ref, 1), (-3, -3), "right", "top"),
                    ((ref, 0), (3, 3), "left", "bottom"), ((ref, 0), (-3, 3), "right", "bottom")]
            t = ax.annotate(ref_label, opts[0][0], xycoords=top, xytext=opts[0][1], textcoords="offset points",
                            fontsize=SMALL, color=C.annotation, path_effects=halo(), zorder=4)
            jobs.append((t, opts, None))

    if label is not None:
        named = {str(v) for v in label}
    elif hot:
        named = hot
    elif n <= 8:
        named = set(nm)
    else:
        big3 = sorted(range(n), key=lambda i: -sz[i])[:3]
        named = {nm[i] for i in big3} | {nm[int(np.argmin(xs))], nm[int(np.argmax(xs))]}
    texts, point_jobs = [], []
    for i in order[::-1]:                                       # smallest first: they have fewest places to go
        if nm[i] not in named:
            continue
        bold = nm[i] in hot
        text = nm[i] + ("\n" + detail.format(x=xs[i], size=sz[i]) if detail else "")
        opts = _point_options(xs[i], y[i], math.sqrt(s[i]) / 2, xp[i] < 0.75 * w_pt, vertical_first=True)
        t = ax.annotate(text, (xs[i], y[i]), xycoords=along, xytext=opts[0][1], textcoords="offset points",
                        ha=opts[0][2], va=opts[0][3], fontsize=LABEL - 1 + (1 if bold else 0),
                        fontweight=700 if bold else 400, color=C.headline if bold else C.text_muted,
                        linespacing=1.1, path_effects=halo(), zorder=5, arrowprops=_leader(math.sqrt(s[i]) / 2))
        texts.append(t)
        point_jobs.append((t, opts, order.index(i)))
    _placer(ax, pts, point_jobs + jobs, vlines=[ref] if ref is not None else [])

    kbox = None
    if key is not False:
        vals = _key_values(float(sz.min()), float(sz.max())) if key is True else list(key)
        title = f"{size_label} (bubble area)" if size_label else "Bubble area"
        kbox = size_key(ax, vals, area, title=title, fmt=key_fmt)
    if xfmt:
        ax.xaxis.set_major_formatter(StrMethodFormatter(xfmt))
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_yticks([])
    clean_axes(ax, keep=("bottom",), grid="x")
    return SimpleNamespace(points=pts, labels=texts, key=kbox, area=area, order=[nm[i] for i in order])


# ------------------------------------------------------------------ ANNOTATIONS
# Four, each one call, used only where they help: a number marker tying a point to an insight on the slide, a bracket
# stating what a group adds up to, a gap between two values, and a short note on one point. They are placed each time
# the figure is drawn, clear of the bars, bubbles, lines and labels already there, so they hold at the final size.
MARK_PT = 9                                     # the number in a marker
NOTE_PT = SMALL + 1                             # 10 pt: notes, bracket and gap labels


def _annotations(ax):
    """The axes' annotation placer, made on first use: a draw-time artist that positions every annotation."""
    reg = getattr(ax, "_mck_notes", None)
    if reg is not None:
        return reg
    from matplotlib.artist import Artist
    from matplotlib.collections import PathCollection
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import Bbox

    reg = SimpleNamespace(jobs=[], before=[], count=0)

    def obstacles(renderer, own):
        pts = renderer.points_to_pixels(1.0)
        circles, rects = [], []
        for coll in ax.collections:                             # scatter markers and bubbles
            if isinstance(coll, PathCollection) and coll.get_visible() and len(coll.get_offsets()):
                xy = coll.get_offset_transform().transform(coll.get_offsets())
                sizes = coll.get_sizes()
                sizes = sizes if len(sizes) == len(xy) else [sizes[0]] * len(xy)
                circles += [(x, y, math.sqrt(s) / 2 * pts) for (x, y), s in zip(xy, sizes) if s > 0]
        for p in ax.patches:                                    # bars (not shaded zones, drawn under everything)
            if isinstance(p, Rectangle) and p.get_visible() and p.get_fill() and p.get_zorder() >= 1:
                rects.append(p.get_window_extent(renderer))
        for ln in ax.get_lines():                               # lines, sampled every few pixels
            if not ln.get_visible() or ln.get_linestyle() in ("None", "none", "") or ln in own:
                continue
            xy = ln.get_transform().transform(np.column_stack(ln.get_data(orig=False)))
            for (x0, y0), (x1, y1) in zip(xy[:-1], xy[1:]):
                k = max(int(math.hypot(x1 - x0, y1 - y0) / 6), 1)
                circles += [(x0 + (x1 - x0) * j / k, y0 + (y1 - y0) * j / k, 2.5) for j in range(k + 1)]
        for t in ax.texts:                                      # labels already on the chart
            if t.get_visible() and t.get_text().strip() and t not in own:
                rects.append(_text_box(t, renderer))
        return circles, rects

    class Placer(Artist):
        def draw(self, renderer):
            for step in reg.before:                             # geometry that follows the labels (brackets)
                step(renderer)
            own = {j[0] for j in reg.jobs} | {x for j in reg.jobs for x in j[2]}
            circles, rects = obstacles(renderer, own)
            frame = ax.get_window_extent(renderer)
            for text, options, _ in reg.jobs:
                best = None
                for opt in options:
                    _put(text, *opt)
                    bb = _text_box(text, renderer)
                    s = _overlap(bb.expanded(1.04, 1.1), circles, rects, frame)
                    if best is None or s < best[0] - 0.5:
                        best = (s, opt, bb)
                    if s <= 0.5:
                        break
                _put(text, *best[1])
                rects.append(best[2])

        def get_window_extent(self, renderer=None):
            return Bbox.null()

    p = Placer()
    p.set_in_layout(False)
    p.set_zorder(-99)                                           # after the builders' own label placers
    ax.add_artist(p)
    ax._mck_notes = reg
    return reg


def _put(text, anchor, off, ha, va, leader=False, relpos=(0.5, 0.5)):
    text.xy = anchor
    text.set_position(off)
    text.set_ha(ha)
    text.set_va(va)
    if getattr(text, "arrow_patch", None) is not None:
        text.arrow_patch.set_visible(leader)
        text._arrow_relpos = relpos


def _target(ax, target, chart):
    """Resolve what an annotation points at: an (x, y) in data, a Text (a label), or a name in a builder's result
    (a bar of mv.bar; a bubble of mv.bubble or mv.bubble_strip). Returns (kind, value, radius_pt)."""
    from matplotlib.text import Text

    if isinstance(target, Text):
        return "text", target, 0.0
    if isinstance(target, str):
        if chart is None or not hasattr(chart, "order"):
            raise ValueError(f"{target!r}: pass chart= (what mv.bar, mv.bubble or mv.bubble_strip returned) to find "
                             "it by name, or give the point as (x, y)")
        if target not in chart.order:
            raise ValueError(f"{target!r} is not on the chart: {', '.join(chart.order)}")
        i = chart.order.index(target)
        if hasattr(chart, "bars"):                              # mv.bar: the value label at the bar's end
            return "text", chart.labels[i], 0.0
        xy = chart.points.get_offsets()[i]
        return "point", (tuple(xy), chart.points.get_offset_transform()), math.sqrt(chart.points.get_sizes()[i]) / 2
    x, y = target
    return "point", ((float(x), float(y)), ax.transData), 0.0


def _ring(r, rings=(0, 14, 30), leader_from=1):
    """Spots around a point, nearest first: beside, above, below and the diagonals, ring by ring outwards."""
    out = []
    for k, extra in enumerate(rings):
        d, q = r + 4 + extra, 0.72 * (r + extra) + 3
        lead = k >= leader_from
        out += [((d, 0), "left", "center", lead), ((-d, 0), "right", "center", lead),
                ((0, d), "center", "bottom", lead), ((0, -d), "center", "top", lead),
                ((q, q), "left", "bottom", lead), ((-q, q), "right", "bottom", lead),
                ((q, -q), "left", "top", lead), ((-q, -q), "right", "top", lead)]
    return out


def mark(ax, n: int, target, *, chart=None):
    """A number marker on the chart, the same number as the insight it backs on the slide (office insights): a small
    navy circle with a white number.

        ns = mv.bar(ax, df.job_family, df.rate, focus=focus, fmt="{:.1f}%")
        mv.mark(ax, 1, "Pharmacy Technician", chart=ns)        # after that bar's value label
        mv.mark(ax, 2, (2023.5, 41.0))                         # or beside a point, in data coordinates

    target: a name on `chart` (what mv.bar, mv.bubble or mv.bubble_strip returned), a label (a Text), or (x, y).
    Placed clear of the data when the figure is drawn. Returns the marker's Text."""
    kind, where, r = _target(ax, target, chart)
    style = dict(fontsize=MARK_PT, fontweight=700, color="white", zorder=7,
                 bbox=dict(boxstyle="circle,pad=0.28", fc=C.headline, ec="none"))
    reg = _annotations(ax)
    if kind == "text":                                          # just after the label it belongs to
        t = ax.annotate(str(n), (1, 0.5), xycoords=where, xytext=(9, 0), textcoords="offset points", ha="center",
                        va="center", annotation_clip=False, **style)
    else:
        (xy, tr), opts = where, _ring(r + 2, rings=(0, 10), leader_from=9)
        t = ax.annotate(str(n), xy, xycoords=tr, xytext=opts[0][0], textcoords="offset points", **style)
        reg.jobs.append((t, [(xy, *o) for o in opts], ()))
    reg.count += 1
    return t


def note(ax, target, text: str, *, chart=None):
    """A short note on one bar, point or period, with a hairline leader to it ("Hiring freeze, Q3"; "New pay
    range"): for what the data can't say itself. Placed clear of the data and the labels when the figure is drawn.

        mv.note(ax, (2024.25, 18.2), "Hiring freeze announced")
        mv.note(ax, "Customer Care", "Includes the 2025 transfer", chart=ns)

    target: (x, y) in data, a name on `chart`, or a label (Text). Keep it to a few words. Returns the note's Text."""
    kind, where, r = _target(ax, target, chart)
    if kind == "text":
        lab = where
        t = ax.annotate(text, (1, 0.5), xycoords=lab, xytext=(14, 0), textcoords="offset points", ha="left",
                        va="center", fontsize=NOTE_PT, color=C.annotation, path_effects=halo(), zorder=6,
                        annotation_clip=False)
    else:
        (xy, tr) = where
        opts = _ring(r, rings=(10, 24, 40), leader_from=0)
        t = ax.annotate(text, xy, xycoords=tr, xytext=opts[0][0], textcoords="offset points", fontsize=NOTE_PT,
                        color=C.annotation, path_effects=halo(), zorder=6, linespacing=1.15,
                        arrowprops=dict(arrowstyle="-", color=C.axis, lw=0.6, shrinkA=1, shrinkB=r + 2))
        _annotations(ax).jobs.append((t, [(xy, *o) for o in opts], ()))
    _annotations(ax).count += 1
    return t


def gap(ax, a, b, text: str):
    """The difference between two values, as a thin span with end ticks and its label beside it ("+5.2 pts",
    "2.1x"): between two lines at one x, two columns, or a point and its target.

        mv.gap(ax, (x, us), (x, market), "-6.3 pts")           # same x: a vertical span, label to the side
        mv.gap(ax, (2.0, y), (5.5, y), "3.5 years")            # same y: a horizontal span, label above

    a, b: (x, y) in data. Returns SimpleNamespace(span, label)."""
    (x0, y0), (x1, y1) = (tuple(map(float, a)), tuple(map(float, b)))
    span = ax.annotate("", (x1, y1), xytext=(x0, y0), arrowprops=dict(
        arrowstyle="|-|,widthA=0.25,widthB=0.25", color=C.annotation, lw=0.75, shrinkA=0, shrinkB=0), zorder=6)
    mid = ((x0 + x1) / 2, (y0 + y1) / 2)
    if x0 == x1:                                                # a vertical span: the label to its side
        opts = [(mid, (6, 0), "left", "center"), (mid, (-6, 0), "right", "center")]
    else:
        opts = [(mid, (0, 5), "center", "bottom"), (mid, (0, -5), "center", "top")]
    t = ax.annotate(text, mid, xytext=opts[0][1], textcoords="offset points", ha=opts[0][2], va=opts[0][3],
                    fontsize=NOTE_PT, fontweight=600, color=C.headline, path_effects=halo(), zorder=6)
    reg = _annotations(ax)
    reg.jobs.append((t, opts, (span,)))
    reg.count += 1
    return SimpleNamespace(span=span, label=t)


def bracket(ax, chart, names: Iterable[str], text: str):
    """A bracket beside a group of bars, saying what they add up to ("73% of all voluntary exits"): drawn just right
    of the group's value labels, with the text beside it. The axis widens to make room.

        ns = mv.bar(ax, df.job_family, df.rate, focus=top2, fmt="{:.1f}%")
        mv.bracket(ax, ns, top2, f"{share:.0f}% of all\\nvoluntary exits")

    chart: what mv.bar returned; names: two or more of its bars, next to each other. Returns the label's Text."""
    from matplotlib.lines import Line2D
    from matplotlib.transforms import IdentityTransform

    if not hasattr(chart, "bars"):
        raise ValueError("bracket groups bars: pass what mv.bar returned")
    rows = sorted(chart.order.index(n) for n in names) if all(n in chart.order for n in names) else None
    if rows is None:
        raise ValueError(f"not all of {list(names)} are on the chart: {', '.join(chart.order)}")
    if len(rows) < 2 or rows != list(range(rows[0], rows[-1] + 1)):
        raise ValueError("a bracket spans two or more bars next to each other")
    fig = ax.figure
    width_pt = max(_text_width_pt(ax, line, NOTE_PT, 600) for line in text.split("\n")) + 22
    x0, x1 = ax.get_xlim()
    w_pt = ax.get_position().width * fig.get_figwidth() * 72
    ax.set_xlim(x0, x1 + (x1 - x0) * width_pt / max(w_pt - width_pt, 1))     # room for the bracket and its text
    line = Line2D([], [], color=C.annotation, lw=0.75, transform=IdentityTransform(), zorder=6, clip_on=False)
    line.set_gid("mck-annotation")                             # lint reads it as a mark, not a data line
    ax.add_line(line)
    t = ax.annotate(text, (0, 0), xycoords="figure pixels", xytext=(0, 0), textcoords="offset points", ha="left",
                    va="center", fontsize=NOTE_PT, fontweight=600, color=C.headline, linespacing=1.15, zorder=6,
                    annotation_clip=False)

    def place(renderer):
        px = renderer.points_to_pixels(1.0)
        bars = [chart.bars[i].get_window_extent(renderer) for i in rows]
        labels = [_text_box(chart.labels[i], renderer) for i in rows]
        x = max(b.x1 for b in bars + labels) + 5 * px
        top, bottom = max(b.y1 for b in bars), min(b.y0 for b in bars)
        tick = 4 * px
        line.set_data([x, x + tick, x + tick, x], [top, top, bottom, bottom])
        t.xy = (x + tick + 4 * px, (top + bottom) / 2)

    reg = _annotations(ax)
    reg.before.append(place)
    reg.count += 1
    return t

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
    few_highlights(focus | worse, len(names), "lines")
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


__all__ = ["bar", "story_order", "line", "share_bar", "strip", "dot_plot", "sankey", "diverging_bars", "label_points",
           "waterfall", "hstack", "dumbbell", "rank_slope", "heat", "key_strip", "big", "small", "ring", "kpi_card",
           "kpi_row", "delta_label", "sdot", "status", "status_key", "status_column", "tracker", "roadmap",
           "multiples", "STATUS_ORDER"]


# ------------------------------------------------------------------ SANKEY
def _rows(data, width: int) -> list[tuple]:
    if hasattr(data, "itertuples"):
        return [tuple(r[:width]) for r in data.itertuples(index=False, name=None)]
    return [tuple(r) for r in data]


def sankey(ax, flows, *, focus: Iterable[str] = (), worse: Iterable[str] = (), accent: str | None = None,
           stages: Sequence[str] | None = None, fmt="{:,.0f}", min_n: float = 10, gap: float = 0.05,
           alpha: float = 0.55):
    """Flows of people between stages: curved bands on one shared scale, thin navy nodes, names and totals beside
    them, grey context with the headline's flows in color.

        flows = pd.read_csv("examples/data/reskilling_pipeline.csv")    # from_stage, to_stage, people, transfer
        mv.sankey(ax, flows, focus={"progressed"}, worse={"not_placed"},
                  stages=("Nominated", "Enrolled", "Completed", "Outcome"))

    flows: rows of (source, target, value) or (source, target, value, kind), or a DataFrame whose first three or four
        columns are those. Columns come from the flows (a node sits one column right of its furthest source); within
        a column, nodes keep the order they first appear in, so list exits last to keep them at the bottom edge.
    focus / worse: kinds or node names whose flows are blue / orange (orange only when the flow is a loss: dropped,
        not placed, left). accent: one kind or node name in navy, the exception next to a blue group. With none of
        these, the first kind (or the largest flow) is the focus. Everything else is grey.
    stages: bold column headers, left to right. min_n: every flow must be at least this (merge smaller flows into
        "Other"). Returns SimpleNamespace(nodes={name: (x, y0, y1)}, sizes, columns, bands, labels).
    """
    from matplotlib.patches import Rectangle

    rows = []
    for r in _rows(flows, 4):
        if len(r) < 3:
            raise ValueError("each flow needs a source, a target and a value")
        s, t, v = str(r[0]), str(r[1]), float(r[2])
        kind = str(r[3]) if len(r) > 3 and r[3] is not None else None
        if v <= 0:
            raise ValueError(f"flow {s} -> {t} is {v:g}; drop empty flows")
        if v < min_n:
            raise ValueError(f"flow {s} -> {t} is {v:g} (n<{min_n:g}): merge it into 'Other' and footnote it")
        rows.append((s, t, v, kind))
    if not rows:
        raise ValueError("no flows")
    names = list(dict.fromkeys(n for s, t, *_ in rows for n in (s, t)))
    depth = {n: 0 for n in names}
    for _ in range(len(names) + 1):                           # longest path from a source; a cycle never settles
        changed = False
        for s, t, *_ in rows:
            if depth[t] < depth[s] + 1:
                depth[t], changed = depth[s] + 1, True
        if not changed:
            break
    else:
        raise ValueError("the flows loop back on themselves; a Sankey needs stages that run one way")
    inflow = {n: sum(v for s, t, v, _ in rows if t == n) for n in names}
    outflow = {n: sum(v for s, t, v, _ in rows if s == n) for n in names}
    size = {n: max(inflow[n], outflow[n]) for n in names}
    ncol = max(depth.values()) + 1
    columns = [[n for n in names if depth[n] == c] for c in range(ncol)]
    if stages is not None and len(stages) != ncol:
        raise ValueError(f"{len(stages)} stage names for {ncol} columns")

    focus, worse = {str(x) for x in focus}, {str(x) for x in worse}
    kinds = list(dict.fromkeys(k for *_, k in rows if k is not None))
    if not focus and not worse and accent is None:
        focus = {kinds[0]} if kinds else {max(rows, key=lambda r: r[2])[0]}
    marked = focus | worse | ({str(accent)} if accent is not None else set())

    def tone(row):
        s, t, _, k = row
        if accent is not None and str(accent) in (k, s, t):
            return "accent"
        return "worse" if {k, s, t} & worse else "focus" if {k, s, t} & focus else "context"
    fill = {"accent": C.accent, "worse": C.negative, "focus": C.focus, "context": C.context}

    # Room for the outer labels inside the axes, so nothing runs off the figure.
    fig = ax.figure
    ax_pt = ax.get_window_extent(fig.canvas.get_renderer()).width * 72 / fig.dpi
    label = {n: f"{n}  {fmt.format(size[n]) if isinstance(fmt, str) else fmt(size[n])}" for n in names}
    hot = {n for n in names if n in marked}

    def width(n):
        return _text_width_pt(ax, label[n], TICK, 600 if n in hot else 400) / ax_pt + 0.012
    node_w = 0.012
    left = max(width(n) for n in columns[0]) if ncol > 1 else 0
    right = max(width(n) for n in columns[-1])
    xs = [left + (1 - left - right - node_w) * (c / (ncol - 1) if ncol > 1 else 0) for c in range(ncol)]

    scale = min((1 - gap * (len(col) - 1)) / sum(size[n] for n in col) for col in columns)
    nodes = {}
    for c, col in enumerate(columns):
        total = scale * sum(size[n] for n in col) + gap * (len(col) - 1)
        y = 1 - (1 - total) / 2                               # each column centered on the same midline
        for n in col:
            h = scale * size[n]
            nodes[n] = (xs[c], y - h, y)
            y -= h + gap

    mid = {n: (y0 + y1) / 2 for n, (_, y0, y1) in nodes.items()}
    out_at = {n: nodes[n][2] for n in names}                  # next free y on each side of a node, top down
    in_at = {n: nodes[n][2] for n in names}
    slots: dict[int, dict[str, tuple[float, float]]] = {}
    for n in names:
        for i in sorted([i for i, r in enumerate(rows) if r[0] == n], key=lambda i: -mid[rows[i][1]]):
            h = scale * rows[i][2]
            slots.setdefault(i, {})["out"] = (out_at[n] - h, out_at[n])
            out_at[n] -= h
        for i in sorted([i for i, r in enumerate(rows) if r[1] == n], key=lambda i: -mid[rows[i][0]]):
            h = scale * rows[i][2]
            slots.setdefault(i, {})["in"] = (in_at[n] - h, in_at[n])
            in_at[n] -= h

    rank = {"context": 0, "focus": 1, "worse": 2, "accent": 3}
    bands = []
    t = np.linspace(0, 1, 64)
    e = t * t * (3 - 2 * t)                                   # smoothstep: flat at both nodes, curved between
    for i in sorted(range(len(rows)), key=lambda i: rank[tone(rows[i])]):    # highlights drawn over the grey
        s, tg, _, _ = rows[i]
        (a0, a1), (b0, b1) = slots[i]["out"], slots[i]["in"]
        x0, x1 = nodes[s][0] + node_w, nodes[tg][0]
        bands.append(ax.fill_between(x0 + (x1 - x0) * t, a0 + (b0 - a0) * e, a1 + (b1 - a1) * e,
                                     color=fill[tone(rows[i])], alpha=alpha, lw=0, zorder=2))
    texts = []
    ax_h = ax.get_window_extent(fig.canvas.get_renderer()).height * 72 / fig.dpi
    text_h = TICK * 1.25 / ax_h                               # one label line, in axes units
    top = 1.0
    for c, col in enumerate(columns):
        for n in col:
            x, y0, y1 = nodes[n]
            ax.add_patch(Rectangle((x, y0), node_w, y1 - y0, color=C.total, lw=0, zorder=3))
            kw = dict(fontsize=TICK, color=C.headline if n in hot else C.text, fontweight=600 if n in hot else 400,
                      zorder=4)
            if inflow[n] and outflow[n]:                      # pass-through: above the node, in the gap between
                texts.append(ax.text(x + node_w / 2, y1 + 0.008, label[n], ha="center", va="bottom",   # nodes, so
                                     path_effects=halo(), **kw))                         # the next column stays clear
                top = max(top, y1 + 0.008 + text_h)
            else:                                             # where flows start, left; where they end, right
                first = not inflow[n] and ncol > 1
                texts.append(ax.text(x - 0.006 if first else x + node_w + 0.006, (y0 + y1) / 2, label[n],
                                     ha="right" if first else "left", va="center", **kw))
    if stages is not None:
        for c, st in enumerate(stages):
            if c == 0:
                x, ha = 0.0, "left"                           # flush with the outer labels
            elif c == ncol - 1:
                x, ha = 1.0, "right"
            else:
                x, ha = xs[c] + node_w / 2, "center"
            texts.append(ax.text(x, top + 0.03, st, ha=ha, va="bottom", fontsize=TICK, fontweight=600,
                                 color=C.text))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, top + (0.03 + text_h if stages is not None else 0.01))
    ax.set_xticks([])
    ax.set_yticks([])
    _plain(ax)
    return SimpleNamespace(nodes=nodes, sizes=size, columns=columns, bands=bands, labels=texts)


# ------------------------------------------------------------------ STRIP / BOX (distributions)
def strip(ax, data, group: str | None = None, value: str | None = None, *, focus: Iterable[str] = (),
          order: Sequence[str] | None = None, dots: bool = True, box: bool | str = "focus", share=None,
          share_label: str | None = None, zone: tuple[float, float] | None = None, zone_label: str | None = None,
          ref: float | None = None, ref_label: str | None = None, min_n: int = 10, xfmt: str | None = None,
          jitter: float = 0.28, seed: int = 1):
    """The spread across people, one row per group: every person a dot (faint grey, the focus group blue), a navy
    box for the focus group's middle 50% and a median tick on every row, the n and an optional share at the row end.

        df = pd.read_csv("examples/data/compa_ratio_individuals.csv")     # job_family, compa_ratio, one row a person
        mv.strip(ax, df, "job_family", "compa_ratio", focus={"Pharmacy Technician"}, share=("below", 0.90),
                 zone=(None, 0.90), zone_label="Below 0.90", ref=1.0, ref_label="Range midpoint", xfmt="{x:.2f}")

    data: a DataFrame with `group` and `value` columns, or {group: values}. order: groups top to bottom; default by
        median, highest at the top. focus: the groups the headline names, in blue with bold navy names.
    dots / box: box="focus" (default) boxes the focus groups only, the calm executive view; box=True boxes every
        group, for readers comparing spreads; box=False, median ticks only. dots=False draws box plots with
        10th-90th percentile whiskers, for many groups or tens of thousands of people. Footnote the box once
        ("Box = middle 50%; line = median").
    share: ("below", x) or ("above", x) prints each group's share beyond x at the row end, under `share_label`
        (default "% below" or "% above"; name the threshold once, in zone_label or the subtitle). zone: (low, high) shaded behind the data (None for the axis edge), named by zone_label.
        ref: a dashed reference line (the midpoint, the limit), named by ref_label.
    Groups under min_n are left out and listed in `.suppressed` for the footnote. Returns SimpleNamespace(order,
    stats={group: dict(n, median, share)}, suppressed, labels).
    """
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import StrMethodFormatter

    if hasattr(data, "groupby"):
        if group is None or value is None:
            raise ValueError("pass the group and value column names with a DataFrame")
        groups = {str(k): np.asarray(v.dropna(), float) for k, v in data.groupby(group, sort=False)[value]}
    else:
        groups = {str(k): np.asarray(list(v), float) for k, v in dict(data).items()}
    suppressed = sorted(g for g, v in groups.items() if len(v) < min_n)
    groups = {g: v for g, v in groups.items() if len(v) >= min_n}
    if not groups:
        raise ValueError(f"every group has fewer than {min_n} people")
    focus = {str(f) for f in focus}
    few_highlights(focus, len(groups), "groups")
    if len(groups) > (8 if dots else 20):
        raise ValueError(f"{len(groups)} groups: at most 8 for a strip plot (dots=True), 20 for box plots")
    if share is not None:
        side, cut = share
        if side not in ("below", "above"):
            raise ValueError('share is ("below", x) or ("above", x)')
    names = list(order) if order is not None else sorted(groups, key=lambda g: -np.median(groups[g]))
    names = [g for g in names if g in groups]
    stats = {}
    for g in names:
        v = groups[g]
        sh = None if share is None else 100 * float(np.mean(v < cut if side == "below" else v > cut))
        stats[g] = {"n": len(v), "median": float(np.median(v)), "share": sh}

    lo = min(float(v.min()) for v in groups.values())
    hi = max(float(v.max()) for v in groups.values())
    extra = [x for x in ((zone or (None, None)) + (ref,)) if x is not None]
    lo, hi = min([lo] + extra), max([hi] + extra)
    pad = (hi - lo) * 0.04 or 1
    lo, hi = lo - pad, hi + pad
    n_rows = len(names)
    rng = np.random.default_rng(seed)                         # fixed jitter: the chart is reproducible
    top_y = n_rows - 0.45
    texts = []
    if zone is not None:
        z0 = lo if zone[0] is None else zone[0]
        z1 = hi if zone[1] is None else zone[1]
        ax.axvspan(z0, z1, color=C.surface_subtle, lw=0, zorder=0)
        if zone_label:
            texts.append(ax.text(z0 + (hi - lo) * 0.005, top_y, zone_label, fontsize=SMALL, color=C.annotation,
                                 fontweight=600, va="bottom"))
    if ref is not None:
        ax.axvline(ref, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
        if ref_label:
            texts.append(ax.text(ref, top_y, ref_label, fontsize=SMALL, color=C.annotation, ha="center", va="bottom",
                                 bbox=dict(fc="white", ec="none", pad=1), zorder=4))
    fig = ax.figure
    for i, g in enumerate(names):
        y = n_rows - 1 - i                                     # first group on top
        v = groups[g]
        hot = g in focus
        if dots:
            ax.scatter(v, y + rng.uniform(-jitter, jitter, len(v)), s=7, color=C.focus if hot else C.context,
                       alpha=0.5 if hot else 0.3, lw=0, zorder=2)
        boxed = box is True or (box == "focus" and hot)
        if dots and not boxed:                                 # context rows: just a median tick
            ax.plot([np.median(v)] * 2, [y - 0.3, y + 0.3], color=C.headline, lw=2, zorder=3, solid_capstyle="butt")
        if boxed or not dots:
            q1, med, q3 = np.percentile(v, [25, 50, 75])
            h = 0.34 if dots else 0.22
            face = "none" if dots else (C.focus if hot else C.context)
            ax.add_patch(Rectangle((q1, y - h), q3 - q1, 2 * h, fc=face, ec=C.headline, lw=1, zorder=3,
                                   alpha=1 if dots else 0.55))
            ax.plot([med, med], [y - h, y + h], color=C.headline, lw=2.25, zorder=3, solid_capstyle="butt")
            if not dots:                                       # whiskers: 10th to 90th percentile, never 1.5 x IQR
                p10, p90 = np.percentile(v, [10, 90])
                ax.plot([p10, q1], [y, y], color=C.headline, lw=1, zorder=3)
                ax.plot([q3, p90], [y, y], color=C.headline, lw=1, zorder=3)
        s = stats[g]
        dx = 6
        if s["share"] is not None:
            txt = f"{s['share']:.0f}%"
            texts.append(ax.annotate(txt, (1, y), xycoords=("axes fraction", "data"), xytext=(dx, 0),
                                     textcoords="offset points", va="center", ha="left", fontsize=LABEL,
                                     color=C.headline if hot else C.text, fontweight=600 if hot else 500))
            dx += _text_width_pt(ax, "100%", LABEL, 600) + 6
        texts.append(ax.annotate(f"n={s['n']:,}", (1, y), xycoords=("axes fraction", "data"), xytext=(dx, 0),
                                 textcoords="offset points", va="center", ha="left", fontsize=SMALL,
                                 color=C.text_muted))
    if share is not None:
        head = share_label or f"% {side}"
        texts.append(ax.annotate(head, (1, top_y), xycoords=("axes fraction", "data"), xytext=(6, 0),
                                 textcoords="offset points", va="bottom", ha="left", fontsize=SMALL,
                                 color=C.text_muted))
    ax.set_yticks(range(n_rows), names[::-1])
    ax.set_ylim(-0.6, n_rows - 0.1)
    ax.set_xlim(lo, hi)
    if xfmt:
        ax.xaxis.set_major_formatter(StrMethodFormatter(xfmt))
    _plain(ax, keep=("bottom",))
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), focus)
    return SimpleNamespace(order=names, stats=stats, suppressed=suppressed, labels=texts)


# ------------------------------------------------------------------ RANKING BAR
def story_order(names: Sequence[str], values: Sequence[float], hot: Iterable[str] = (), sort: bool | str = True):
    """The order a ranking runs from the top, as indexes into names: the story on top. True: largest first, or
    smallest first when every highlighted bar is in the bottom half (a "lagging" or "lowest" headline, which would
    otherwise put its blue bars at the bottom); "descending" / "ascending" force the order; False keeps the given
    order (a natural order). mv.bar and mv.office.bar_slide share it, so a chart and its slide agree."""
    if sort not in (True, False, "descending", "ascending"):
        raise ValueError("sort: True (the story on top), 'descending', 'ascending' or False")
    order = list(range(len(names)))
    if not sort:
        return order
    order.sort(key=lambda i: -values[i])                       # largest first
    hot = set(hot)
    rank = {names[i]: k for k, i in enumerate(order)}
    low_story = bool(hot) and all(rank[h] >= len(names) / 2 for h in hot)
    if sort == "ascending" or (sort is True and low_story):
        order.reverse()                                        # the highlighted (smallest) bars on top
    return order


def bar(ax, labels: Sequence[str], values: Sequence[float], *, focus: Iterable[str] = (), accent: str | None = None,
        uniform: bool = False, benchmark: float | None = None, benchmark_label: str | None = None, fmt="{:,.0f}",
        sort: bool | str = True):
    """A ranking as sorted horizontal bars, the start chart for categories × one measure: the story on top (as
    mv.office.bar_slide), grey context with the headline's bars in McKesson Blue (navy for one accent;
    uniform=True makes the rest light blue for the "uniform + accent" pattern), the value at each bar's
    end (bold for the highlighted bars), no value axis or gridlines, a zero baseline, and an optional benchmark as a
    dashed navy line named above the bars.

        mv.bar(ax, df.job_family, df.vol_attrition_pct, focus={"Pharmacy Technician", "Distribution Center Associate"},
               benchmark=19.9, benchmark_label="Enterprise 19.9%", fmt="{:.1f}%")

    fmt: a format string or a function for the value labels. sort: see mv.story_order. Values must be zero or more
    (bars start at zero; use mv.diverging_bars for signed changes, mv.dot_plot for values far from zero). Returns
    SimpleNamespace(order, bars, labels).
    """
    names = [str(v) for v in labels]
    vals = _floats(values, "values")
    if len(names) != len(vals):
        raise ValueError("one value per label")
    if not names:
        raise ValueError("no bars")
    if np.isnan(vals).any():
        raise ValueError("a value is missing (NaN): drop or fill it first")
    if vals.min() < 0:
        raise ValueError("bars start at zero: for signed changes use mv.diverging_bars")
    focus = {str(f) for f in focus}
    accent = str(accent) if accent is not None else None
    hot = focus | ({accent} if accent else set())
    few_highlights(hot, len(vals), "bars")
    if unknown := hot - set(names):
        raise ValueError(f"focus/accent not among the labels: {sorted(unknown)}")
    order = story_order(names, list(vals), hot, sort)
    names, vals = [names[i] for i in order], vals[order]
    y = np.arange(len(names))[::-1]                            # first in the order on top
    base = C.focus_light if uniform else C.context
    cols = [C.accent if nm == accent else C.focus if nm in focus else base for nm in names]
    bars = ax.barh(y, vals, height=BAND, color=cols, zorder=2)
    backing = dict(fc="white", ec="none", pad=0.5) if benchmark is not None else None   # a label over the line
    texts = [ax.annotate(_fmt(fmt, v), (v, yy), xytext=(4, 0), textcoords="offset points", va="center", ha="left",
                         fontsize=LABEL, color=C.headline if nm in hot else C.text,
                         fontweight=600 if nm in hot else 500, bbox=backing, zorder=4)
             for yy, nm, v in zip(y, names, vals)]
    top = max(float(vals.max()), benchmark or 0) or 1
    if benchmark is not None:
        ax.axvline(benchmark, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=3)
        if benchmark_label:
            texts.append(ax.annotate(benchmark_label, (benchmark, y[0] + BAND / 2), xytext=(0, 4),
                                     textcoords="offset points", ha="center", va="bottom", fontsize=SMALL,
                                     color=C.annotation, annotation_clip=False,
                                     bbox=dict(fc="white", ec="none", pad=1), zorder=4))
    ax.set_xlim(0, top * 1.18)
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_yticks(y, names)
    ax.set_xticks([])
    _plain(ax, keep=("left",))                                 # the zero baseline only
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), hot)
    return SimpleNamespace(order=names, bars=bars, labels=texts)


# ------------------------------------------------------------------ SHARE BEYOND A THRESHOLD
def share_bar(ax, data, group: str | None = None, value: str | None = None, *, below: float | None = None,
              above: float | None = None, focus: Iterable[str] = (), ref: float | str | None = None,
              ref_label: str | None = None, min_n: int = 10, decimals: int = 0):
    """The share of each group beyond a threshold, from one row per person: a sorted bar per group (grey, the focus
    group blue), the share at the bar end and each group's n beside it. The executive view of "who is paid below
    0.90?"; mv.strip shows the whole spread behind it.

        df = pd.read_csv("examples/data/compa_ratio_individuals.csv")     # job_family, compa_ratio, one row a person
        mv.share_bar(ax, df, "job_family", "compa_ratio", below=0.90, focus={"Pharmacy Technician"})

    data: a DataFrame with `group` and `value` columns, or {group: values}. Pass exactly one of below= / above=
        (strictly below or above the threshold). focus: the groups the headline names. ref: an optional reference share in
        percent, drawn as a navy dashed line and named by ref_label; ref="overall" draws the share across all the
        groups shown, labeled with that share ("All groups 12%"; ref_label replaces "All groups").
    Groups under min_n people are left out and listed in `.suppressed`. Returns SimpleNamespace(order, shares
    {group: percent}, counts {group: people beyond}, n {group: people}, overall (percent), suppressed, bars).
    """
    if (below is None) == (above is None):
        raise ValueError("pass exactly one of below= or above=")
    if hasattr(data, "groupby"):
        if group is None or value is None:
            raise ValueError("pass the group and value column names with a DataFrame")
        groups = {str(k): np.asarray(v.dropna(), float) for k, v in data.groupby(group, sort=False)[value]}
    else:
        groups = {str(k): np.asarray(list(v), float) for k, v in dict(data).items()}
    suppressed = sorted(g for g, v in groups.items() if len(v) < min_n)
    groups = {g: v for g, v in groups.items() if len(v) >= min_n}
    if not groups:
        raise ValueError(f"every group has fewer than {min_n} people")
    focus = {str(f) for f in focus}
    few_highlights(focus, len(groups), "groups")
    beyond = {g: int(np.sum(v < below if below is not None else v > above)) for g, v in groups.items()}
    n = {g: len(v) for g, v in groups.items()}
    shares = {g: 100 * beyond[g] / n[g] for g in groups}
    overall = 100 * sum(beyond.values()) / sum(n.values())
    if isinstance(ref, str):
        if ref != "overall":
            raise ValueError('ref is a share in percent or "overall"')
        ref, ref_label = overall, f"{ref_label or 'All groups'} {overall:.{decimals}f}%"   # the number, computed
    order = sorted(groups, key=lambda g: -shares[g])           # largest share on top
    y = np.arange(len(order))[::-1]
    vals = [shares[g] for g in order]
    bars = ax.barh(y, vals, height=BAND, color=[C.focus if g in focus else C.context for g in order], zorder=2)
    top = max(vals + [ref or 0]) or 1
    for yy, g, v in zip(y, order, vals):
        hot = g in focus
        t = ax.annotate(f"{v:.{decimals}f}%", (v, yy), xytext=(4, 0), textcoords="offset points", va="center",
                        ha="left", fontsize=LABEL, color=C.headline if hot else C.text, fontweight=600 if hot else 500)
        ax.annotate(f"n={n[g]:,}", (v, yy), xytext=(4 + _text_width_pt(ax, t.get_text(), LABEL, 600) + 6, 0),
                    textcoords="offset points", va="center", ha="left", fontsize=SMALL, color=C.text_muted)
    if ref is not None:
        ax.axvline(ref, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=3)
        if ref_label:
            ax.annotate(ref_label, (ref, y[0] + BAND / 2), xytext=(0, 4), textcoords="offset points", ha="center",
                        va="bottom", fontsize=SMALL, color=C.annotation, annotation_clip=False,
                        bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlim(0, top * 1.25)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_yticks(y, order)
    ax.set_xticks([])
    _plain(ax, keep=("left",))
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), focus)
    return SimpleNamespace(order=order, shares=shares, counts=beyond, n=n, overall=overall, suppressed=suppressed,
                           bars=bars)


# ------------------------------------------------------------------ LINE
def _fmt(fmt, v) -> str:
    return fmt.format(v) if isinstance(fmt, str) else fmt(v)


def line(ax, x, series, *, focus: Iterable[str] = (), accent: str | None = None, target: float | None = None,
         target_label: str | None = None, event: tuple | None = None, forecast_from=None, band=None,
         fmt="{:,.1f}", ylim: tuple[float, float] | None = None):
    """Lines over time with the house rules: grey context, the headline's series blue (one navy accent at most),
    direct labels at the line ends in end-value order (no legend), light horizontal gridlines, straight segments.

        q = ["Q1 '24", "Q2", "Q3", "Q4", "Q1 '25", ...]
        mv.line(ax, q, {"Pharmacy Technician": [...], "DC Associate": [...], ...}, focus={"Pharmacy Technician"},
                target=20, target_label="Target 20%", event=("Q3 '25", "Q4", "Pay-band reset"),
                forecast_from="Q4 '26", band={"Pharmacy Technician": (low, high)})

    x: the period labels, evenly spaced (put the year on the first tick and at each year change). series:
        {name: values} or a DataFrame whose columns are the series; NaN leaves a gap (never interpolated).
    focus: the series the headline names, in blue (accent= one in navy). With none: one series is the focus; two to four
        series each get a categorical color; more than four raises (name the focus, or use mv.multiples).
    target: a navy dashed line, named by target_label. event: (first, last, text) shades that span.
    forecast_from: the last actual period; every line is dashed after it, with a dotted divider. Periods are a
        label that appears once in x, or a 0-based position (repeated quarter labels need the position). band:
        {name: (low, high)} scenario bounds aligned to x (NaN before the forecast), shaded in the line's color; the
        end label then reads "base (low-high)". fmt: format for end values. ylim: fixed limits (a line may start
        above zero, but never fill under it). Returns SimpleNamespace(lines={name: Line2D}, labels, colors).
    """
    from matplotlib.transforms import offset_copy

    from . import CATEGORICAL, clean_axes, shade_period

    if hasattr(series, "columns"):
        data = {str(c): np.asarray(series[c], float) for c in series.columns}
    else:
        data = {str(k): np.asarray(list(v), float) for k, v in dict(series).items()}
    labels_x = [str(v) for v in x]
    n = len(labels_x)
    if any(len(v) != n for v in data.values()):
        raise ValueError("every series needs one value per period in x")
    focus = {str(f) for f in focus}
    accent = str(accent) if accent is not None else None
    hot = focus | ({accent} if accent else set())
    if hot - set(data):
        raise ValueError(f"not a series: {sorted(hot - set(data))}")
    few_highlights(hot, len(data), "lines")
    categorical = False
    if not hot:
        if len(data) == 1:
            focus = hot = set(data)
        elif len(data) <= 4:
            categorical = True
        else:
            raise ValueError(f"{len(data)} lines: name the focus (the rest go grey) or use mv.multiples")
    names = list(data)
    color = {nm: (CATEGORICAL[i] if categorical else C.accent if nm == accent else C.focus if nm in focus
                  else C.context) for i, nm in enumerate(names)}
    strong = set(names) if categorical else hot
    lw = TOKENS["chart"]["line"]
    xs = np.arange(n)
    def at(lab):                                              # a 0-based position, or a label that appears once
        if isinstance(lab, (int, np.integer)):
            if not 0 <= lab < n:
                raise ValueError(f"position {lab} is outside x (0 to {n - 1})")
            return int(lab)
        hits = [i for i, v in enumerate(labels_x) if v == str(lab)]
        if len(hits) != 1:
            raise ValueError(f"{lab!r} appears {len(hits)} times in x; pass its 0-based position instead")
        return hits[0]

    if event is not None:
        a, b, text = event
        shade_period(ax, max(at(a) - 0.5, -0.2), min(at(b) + 0.5, n - 0.8), text)
    cut = None if forecast_from is None else at(forecast_from)
    band = {str(k): (np.asarray(lo, float), np.asarray(hi, float)) for k, (lo, hi) in (band or {}).items()}
    for nm, (lo, hi) in band.items():
        if nm not in data or len(lo) != n or len(hi) != n:
            raise ValueError(f"band {nm!r}: a series name and two lists aligned to x")
        ax.fill_between(xs, lo, hi, color=color[nm], alpha=0.15, lw=0, zorder=1)
    lines = {}
    for nm in sorted(names, key=lambda nm: nm in strong):    # context first, highlights on top
        y = data[nm]
        kw = dict(color=color[nm], lw=lw["width_pt"] if nm in strong else lw["context_width_px"],
                  zorder=3 if nm in strong else 2, solid_capstyle="round")
        if cut is None:
            lines[nm], = ax.plot(xs, y, label=nm, **kw)
        else:
            lines[nm], = ax.plot(xs[:cut + 1], y[:cut + 1], label=nm, **kw)
            ax.plot(xs[cut:], y[cut:], ls=(0, (4, 3)), label="_forecast", **kw)
    if cut is not None:
        ax.axvline(cut, color=C.axis, lw=0.75, ls=":", zorder=1)
        ax.annotate("Forecast", (cut, 1), xycoords=("data", "axes fraction"), xytext=(4, -2),
                    textcoords="offset points", va="top", fontsize=SMALL, color=C.text_muted)
    if target is not None:
        ax.axhline(target, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=2)
    clean_axes(ax)
    step = max(1, math.ceil(n / 20))                          # thin only long runs (monthly over years)
    ax.set_xticks(xs[::step], labels_x[::step])
    if ylim is not None:
        ax.set_ylim(*ylim)
    elif target is not None:
        lo_, hi_ = ax.get_ylim()
        ax.set_ylim(min(lo_, target), max(hi_, target))

    # End labels: text first, so their width can be reserved inside the plot on the right.
    ends = []
    for nm in names:
        y = data[nm]
        idx = [i for i in range(n) if np.isfinite(y[i])]
        if not idx:
            continue
        i = idx[-1]
        if nm in band and np.isfinite(band[nm][0][i]):
            text = f"{nm}\n{_fmt(fmt, y[i])} ({_fmt(fmt, band[nm][0][i])}–{_fmt(fmt, band[nm][1][i])})"
        elif nm in strong:
            text = f"{nm}  {_fmt(fmt, y[i])}"
        else:
            text = nm
        ends.append((nm, i, float(y[i]), text))
    fig = ax.figure
    ax_pt = ax.get_window_extent(fig.canvas.get_renderer()).width * 72 / fig.dpi
    width = max(max(_text_width_pt(ax, ln, LABEL, 600 if nm in strong else 400) for ln in t.split("\n"))
                for nm, _, _, t in ends) / ax_pt + 0.02
    left = -0.2
    ax.set_xlim(left, left + (n - 1 - left + 0.1) / (1 - width))
    ax.autoscale_view(scalex=False)
    to_pt = 72 / fig.dpi
    yp = {nm: ax.transData.transform((i, v))[1] * to_pt for nm, i, v, _ in ends}
    placed = {}
    prev = None
    for nm, i, v, t in sorted(ends, key=lambda e: yp[e[0]]):  # bottom up, nudged apart
        h = LABEL * 1.3 * t.count("\n") / 2 + LABEL * 0.65
        y = yp[nm] if prev is None else max(yp[nm], prev + h + 1)
        placed[nm] = y
        prev = y + h - LABEL * 0.65
    texts = []
    inv = ax.transData.inverted()
    for nm, i, v, t in ends:
        y = inv.transform((0, placed[nm] / to_pt))[1]
        texts.append(ax.text(i, y, t, transform=offset_copy(ax.transData, fig, x=6, units="points"),
                             va="center", ha="left", fontsize=LABEL, linespacing=1.15,
                             color=color[nm] if nm in strong else C.text_muted,
                             fontweight=600 if nm in strong else 400, path_effects=halo(), zorder=4))
    if target is not None and target_label:                   # at the end and side of the line furthest from data
        ty = ax.transData.transform((0, target))[1] * to_pt
        th = SMALL * 1.2
        best = None
        for side, near in (("left", (0, 1)), ("right", (n - 2, n - 1))):
            pts = [ax.transData.transform((i, data[nm][i]))[1] * to_pt for nm in names for i in near
                   if 0 <= i < n and np.isfinite(data[nm][i])]
            for up in (True, False):
                lo_, hi_ = (ty + 3, ty + 3 + th) if up else (ty - 3 - th, ty - 3)
                clear = min((0.0 if lo_ <= p <= hi_ else min(abs(p - lo_), abs(p - hi_)) for p in pts), default=99)
                if best is None or clear > best[0]:
                    best = (clear, side, up)
        _, side, up = best
        texts.append(ax.annotate(target_label, (0 if side == "left" else n - 1, target),
                                 xytext=(2 if side == "left" else -2, 3 if up else -3), textcoords="offset points",
                                 ha=side, va="bottom" if up else "top", fontsize=SMALL, color=C.annotation,
                                 path_effects=halo(), zorder=4))
    return SimpleNamespace(lines=lines, labels=texts, colors=color)


# ------------------------------------------------------------------ DOT PLOT
def dot_plot(ax, labels: Sequence[str], values: Sequence[float], *, focus: Iterable[str] = (),
             accent: str | None = None, benchmark: float | None = None, benchmark_label: str | None = None,
             fmt="{:,.1f}", sort: bool = True, xlim: tuple[float, float] | None = None, tick_fmt: str | None = None):
    """One value per category as a dot on a common scale: the alternative to bars when the values sit far from zero
    and the differences are small (engagement scores, compa-ratios, rates around 80-90%). Grey dots, the headline's
    in blue (navy for one accent), the value beside each dot, a named dashed benchmark line, light row guides.

        mv.dot_plot(ax, df.team, df.engagement, focus={"Pharmacy Ops"}, benchmark=78, benchmark_label="Company 78")

    sort: largest value on top (False keeps the given order, for a natural order). xlim: the value range; by default
    the data and the benchmark with a margin (the axis may start above zero, because position carries the value, not
    length). tick_fmt: axis tick format, e.g. "{x:.0f}". Returns SimpleNamespace(order, dots, labels).
    """
    from matplotlib.ticker import StrMethodFormatter

    from . import clean_axes

    names = [str(v) for v in labels]
    vals = _floats(values, "values")
    if len(names) != len(vals):
        raise ValueError("one value per label")
    focus = {str(f) for f in focus}
    accent = str(accent) if accent is not None else None
    hot = focus | ({accent} if accent else set())
    few_highlights(hot, len(vals), "rows")
    order = sorted(range(len(names)), key=lambda i: -vals[i]) if sort else list(range(len(names)))
    names, vals = [names[i] for i in order], vals[order]
    y = np.arange(len(names))[::-1]                            # first row on top
    for yy in y:                                               # light guides, so each dot reads back to its name
        ax.axhline(yy, color=C.grid, lw=0.75, zorder=0)
    cols = [C.accent if nm == accent else C.focus if nm in focus else C.context for nm in names]
    dots = ax.scatter(vals, y, s=90, color=cols, lw=0, zorder=3)
    texts = []
    for yy, nm, v in zip(y, names, vals):
        texts.append(ax.annotate(_fmt(fmt, v), (v, yy), xytext=(8, 0), textcoords="offset points", va="center",
                                 ha="left", fontsize=LABEL, color=C.headline if nm in hot else C.text,
                                 fontweight=600 if nm in hot else 400, zorder=4))
    span = [float(np.nanmin(vals)), float(np.nanmax(vals))] + ([benchmark] if benchmark is not None else [])
    lo, hi = min(span), max(span)
    pad = (hi - lo) * 0.08 or abs(hi) * 0.05 or 1
    ax.set_xlim(*(xlim or (lo - pad, hi + pad * 1.6)))         # extra room on the right for the value labels
    ax.set_ylim(-0.6, len(names) - 0.4 + (0.35 if benchmark_label else 0))
    if benchmark is not None:
        ax.axvline(benchmark, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=2)
        if benchmark_label:
            texts.append(ax.annotate(benchmark_label, (benchmark, y[0]), xytext=(0, 12), textcoords="offset points",
                                     ha="center", va="bottom", fontsize=SMALL, color=C.annotation,
                                     bbox=dict(fc="white", ec="none", pad=1), zorder=4))
    ax.set_yticks(y, names)
    clean_axes(ax, keep=(), grid=None)
    ax.tick_params(length=0)
    if tick_fmt:
        ax.xaxis.set_major_formatter(StrMethodFormatter(tick_fmt))
    for t in ax.get_yticklabels():
        t.set_fontsize(TICK)
        t.set_color(C.text)
    _bold_ticks(ax.get_yticklabels(), hot)
    return SimpleNamespace(order=names, dots=dots, labels=texts)
