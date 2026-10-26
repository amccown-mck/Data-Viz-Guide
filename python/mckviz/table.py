"""mv.table: a blended table (scorecard) in one call, to the spec in docs/cookbook/tables.md.

    cols = [mv.Col("headcount", "Headcount", "bar", agg="sum"),
            mv.Col("vol_attrition_pct", "Voluntary\\nattrition (%)", "heat", fmt="{:.1f}"),
            mv.Col("attrition_change_pts", "Change vs.\\nFY25 (pts)", "delta", worse="up"),
            mv.Col("median_days_to_fill", "Median\\ndays to fill", fmt="{:.0f}")]
    fig, ax = plt.subplots(figsize=(10, 5))
    t = mv.table(ax, df, "job_family", cols, focus={"Pharmacy Technician"}, weights="headcount",
                 total_label="All 8 job families")
    mv.titles(fig, "<headline>", "<subtitle; totals weighted by headcount>")
    mv.source(fig, "Source: ...", footnote=" ".join(t.notes))
    mv.save(fig, "out/scorecard.png", dpi=200)

Column kinds: "number" (right-aligned, one format per column), "bar" (an inline bar in context grey, focus rows in blue,
with the value after it), "heat" (cells shaded light to dark on the column's own scale; scale="orange" when darker
means worse, scale="diverging" around `center` for gaps to a benchmark), "delta" (signed with a true minus; only the
unfavorable direction, given by worse="up" or "down", is colored) and "text". At most two shaded columns and two focus
rows, as the spec says. Rows are drawn in the order given: sort the frame first. With `n=` (a count column), cells of
rows under `min_n` people show "n<10". The figure height is fitted to the rows unless fit=False.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Iterable, Sequence

import numpy as np
from matplotlib.patches import Rectangle

from . import DIVERGING, SEQUENTIAL, colors as C, signed, text_on

_PAD = 14            # points between columns
_BAR_PT = 72         # inline bar length (points)


@dataclass
class Col:
    key: str
    header: str
    kind: str = "number"             # number | bar | heat | delta | text
    fmt: str = "{:,.0f}"             # number, bar and heat cells
    decimals: int = 1                # delta cells
    worse: str | None = None         # delta: "up" or "down" is unfavorable; heat: with scale="diverging", "up" flips
    scale: str = "blue"              # heat: blue | orange | diverging
    center: float = 0.0              # heat, diverging: the benchmark
    agg: str | None = None           # total row: "sum", "mean", "weighted" (default: weighted with weights=, else mean)


def _width(ax, s: str, size: float, weight=400) -> float:
    fig = ax.figure
    t = fig.text(0, 0, s, fontsize=size, fontweight=weight)
    w = t.get_window_extent(fig.canvas.get_renderer()).width * 72 / fig.dpi
    t.remove()
    return w


def _cell(col: Col, v) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    if col.kind == "delta":
        return signed(float(v), col.decimals)
    if col.kind == "text":
        return str(v)
    return col.fmt.format(v)


def _heat_fill(col: Col, v: float, lo: float, hi: float) -> str:
    if col.scale == "diverging":
        span = max(abs(lo - col.center), abs(hi - col.center)) or 1.0
        k = min(3, int(round(abs(v - col.center) / span * 3)))
        below = v < col.center
        if col.worse == "up":
            below = not below
        return DIVERGING[3 - k] if below else DIVERGING[3 + k]
    ramp = SEQUENTIAL["orange" if col.scale == "orange" else "blue"]
    if hi <= lo:
        return ramp[len(ramp) // 2]
    return ramp[min(int((v - lo) / (hi - lo) * len(ramp)), len(ramp) - 1)]


def table(ax, df, label: str, cols: Sequence[Col], *, focus: Iterable = (), weights: str | None = None,
          total_label: str | None = None, n: str | None = None, min_n: int = 10, fontsize: float = 10,
          fit: bool = True):
    """Draw a blended table on `ax` (rows in the order of `df`). Returns SimpleNamespace(notes, rows)."""
    focus = set(focus)
    if len(focus) > 2:
        raise ValueError(f"{len(focus)} focus rows: bold at most two, the ones the headline names")
    if sum(c.kind == "heat" for c in cols) > 2:
        raise ValueError("shade at most two columns, each on its own scale")
    df = df.reset_index(drop=True)
    rows = len(df)
    fig = ax.figure
    ax.axis("off")
    suppressed = set(df.index[df[n] < min_n]) if n else set()
    total = total_label is not None

    if fit:
        heads = max(c.header.count("\n") + 1 for c in cols)
        fig.set_figheight(0.34 * (rows + total + 0.6 + 0.45 * heads) * fontsize / 10 + 1.7)
        fig.subplots_adjust(left=0, right=1)                    # full width, kept when mv.layout moves the top
    fig.canvas.draw()

    def cells(c):
        return [("n<10" if i in suppressed and c.kind != "text" else _cell(c, df.at[i, c.key])) for i in range(rows)]

    texts = {c.key: cells(c) for c in cols}
    totals = {}
    if total:
        for c in cols:
            v = df.loc[~df.index.isin(suppressed), c.key]
            agg = c.agg or ("weighted" if weights and c.key != weights else "mean")
            if c.kind == "text" or not len(v):
                totals[c.key] = ""
            elif agg == "sum":
                totals[c.key] = _cell(c, v.sum())
            elif agg == "weighted" and weights:
                w = df.loc[v.index, weights]
                totals[c.key] = _cell(c, float(np.average(v, weights=w)))
            else:
                totals[c.key] = _cell(c, float(v.mean()))

    # column widths in points: the widest header line or cell, plus padding
    labels = [str(x) for x in df[label]] + ([total_label] if total else [])
    lab_w = max(_width(ax, s, fontsize, 700) for s in labels) + _PAD
    widths = []
    for c in cols:
        head = max(_width(ax, line, fontsize * 0.9, 700) for line in c.header.split("\n"))
        body = max([_width(ax, s, fontsize, 700) for s in texts[c.key] + [totals.get(c.key, "")] if s] or [0])
        widths.append(max(head, body + (_BAR_PT + 6 if c.kind == "bar" else 0)) + _PAD)
    need = lab_w + sum(widths)
    avail = ax.get_window_extent().width * 72 / fig.dpi
    if need > avail:
        raise ValueError(f"the table needs {need:.0f} pt but the axes is {avail:.0f} pt wide: widen the figure, "
                         "drop a column or shorten the headers")
    ax.set_xlim(0, avail)                                     # compact on the left; numbers aren't stretched
    head_lines = max(c.header.count("\n") + 1 for c in cols)
    ax.set_ylim(rows + (1.15 if total else 0) + 0.15, -0.55 - 0.45 * head_lines)

    lefts = np.cumsum([lab_w, *widths[:-1]])
    notes = []
    for c, x0, w in zip(cols, lefts, widths):
        right = x0 + w - _PAD / 2
        num = c.kind in ("number", "heat", "delta")
        ax.text(right if num else x0, -0.5, c.header, ha="right" if num else "left", va="bottom",
                fontsize=fontsize * 0.9, fontweight="bold", color=C.headline, linespacing=1.15)
        vals = df.loc[~df.index.isin(suppressed), c.key].astype(float) if c.kind in ("bar", "heat") else None
        lo, hi = (float(vals.min()), float(vals.max())) if vals is not None and len(vals) else (0.0, 1.0)
        if c.kind == "heat":
            one = c.header.replace("\n", " ")
            notes.append(f"{one} shaded around {c.center:g} (orange = worse)." if c.scale == "diverging" else
                         f"{one} shaded light to dark from {_cell(c, lo)} to {_cell(c, hi)}"
                         + (" (darker = worse)." if c.scale == "orange" else "."))
        for i in range(rows):
            hi_row = df.at[i, label] in focus
            weight, color = ("bold", C.headline) if hi_row else ("normal", C.text)
            s = texts[c.key][i]
            if i in suppressed and c.kind != "text":
                ax.add_patch(Rectangle((x0 + _PAD / 2, i - 0.42), w - _PAD, 0.84, color=C.context_light, lw=0))
                ax.text(right, i, s, ha="right", va="center", fontsize=fontsize * 0.9, color=C.text_muted)
                continue
            v = df.at[i, c.key]
            if c.kind == "bar":
                length = _BAR_PT * (float(v) / hi if hi > 0 else 0)
                ax.add_patch(Rectangle((x0, i - 0.21), length, 0.42, color=C.focus if hi_row else C.context, lw=0))
                ax.text(x0 + length + 4, i, s, ha="left", va="center", fontsize=fontsize, fontweight=weight,
                        color=color)
            elif c.kind == "heat":
                fill = _heat_fill(c, float(v), lo, hi)
                ax.add_patch(Rectangle((x0 + _PAD / 2, i - 0.5), w - _PAD / 2, 1.0, color=fill, lw=0))
                ax.text(right - 4, i, s, ha="right", va="center", fontsize=fontsize, fontweight=weight,
                        color=text_on(fill))
            elif c.kind == "delta":
                bad = (c.worse == "up" and v > 0) or (c.worse == "down" and v < 0)
                ax.text(right, i, s, ha="right", va="center", fontsize=fontsize, fontweight=weight,
                        color=C.negative_text if bad else color)
            elif c.kind == "text":
                ax.text(x0, i, s, ha="left", va="center", fontsize=fontsize, fontweight=weight, color=color)
            else:
                ax.text(right, i, s, ha="right", va="center", fontsize=fontsize, fontweight=weight, color=color)
        if total:
            t = totals[c.key]
            ax.text(right if num else (x0 if c.kind == "text" else x0 + _BAR_PT + 4), rows + 0.15, t,
                    ha="right" if num else "left", va="center", fontsize=fontsize, fontweight="bold",
                    color=C.headline)

    right_edge = lab_w + sum(widths) - _PAD / 2
    ax.plot([0, right_edge], [-0.45, -0.45], color=C.axis, lw=0.75)
    for i in range(rows):
        hi_row = df.at[i, label] in focus
        ax.text(0, i, str(df.at[i, label]), ha="left", va="center", fontsize=fontsize,
                fontweight="bold" if hi_row else "normal", color=C.headline if hi_row else C.text)
        if i < rows - 1 and rows > 6:
            ax.plot([0, right_edge], [i + 0.5, i + 0.5], color=C.grid, lw=0.75, zorder=0)
    if total:
        ax.plot([0, right_edge], [rows - 0.35, rows - 0.35], color=C.total, lw=1.25)
        ax.text(0, rows + 0.15, total_label, ha="left", va="center", fontsize=fontsize, fontweight="bold",
                color=C.headline)
        if weights:
            notes.append(f"Totals weighted by {weights.replace('_', ' ')}.")
    if suppressed:
        notes.append(f"n<10: fewer than {min_n} people, not shown.")
    return SimpleNamespace(notes=notes, rows=rows)
