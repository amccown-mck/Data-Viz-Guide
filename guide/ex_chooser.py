"""Chart chooser and cheat sheet exhibits: one small icon per chart family, and the cheat sheet's mini chart.
Icons follow the house style they point to: grey context, one blue focus, no text."""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

import mckviz as mv
from exhibits import (ATTR, ENT, FOCUS, MINI, SHORT, C, EXHIBITS, bench, fig_px, hbars, marker)

W, H = 84, 54                                                  # icon size (px)


def _icon_ax():
    fig = fig_px(W, H, pad=1)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.88])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")
    return fig, ax


def _icon(kind):
    fig, ax = _icon_ax()
    G, GL, B, N = C.context, C.context_light, C.focus, C.total
    if kind == "magnitude":
        for i, (w, c) in enumerate([(86, B), (70, B), (52, G), (40, G), (30, G)]):
            ax.add_patch(Rectangle((6, 52 - i * 12), w, 8, color=c, lw=0))
        ax.plot([6, 6], [0, 64], color=C.axis, lw=0.8)
    elif kind == "part":
        for i, (a, b) in enumerate([(30, 58), (8, 80), (7, 71)]):
            y = 44 - i * 20
            ax.add_patch(Rectangle((4, y), a * 0.92, 13, color=B, lw=0))
            ax.add_patch(Rectangle((4 + a * 0.92 + 1, y), b * 0.92, 13, color=G, lw=0))
            ax.add_patch(Rectangle((4 + (a + b) * 0.92 + 2, y), (100 - a - b) * 0.92 - 2, 13, color=GL, lw=0))
    elif kind == "time":
        x = np.linspace(6, 94, 7)
        ax.plot(x, [40, 38, 41, 37, 39, 36, 38], color=G, lw=1.4)
        ax.plot(x, [22, 26, 30, 34, 42, 50, 56], color=B, lw=2.4)
        ax.scatter([94], [56], s=12, color=B, zorder=3)
        ax.plot([4, 96], [4, 4], color=C.axis, lw=0.8)
    elif kind == "ranking":
        for y1, y2, c in [(54, 30, G), (42, 54, B), (30, 18, G), (18, 42, G), (6, 6, G)]:
            ax.plot([22, 78], [y1, y2], color=c, lw=2.4 if c == B else 1.2, zorder=3 if c == B else 2)
            ax.scatter([22, 78], [y1, y2], s=10, color=c, zorder=3 if c == B else 2)
    elif kind == "distribution":
        h = [4, 9, 17, 27, 36, 31, 22, 14, 9, 6, 4]
        for i, v in enumerate(h):
            ax.add_patch(Rectangle((6 + i * 8, 6), 7, v * 1.4, color=B if i >= 7 else G, lw=0))
        ax.plot([4, 96], [6, 6], color=C.axis, lw=0.8)
    elif kind == "correlation":
        rng = np.random.default_rng(4)
        xs = rng.uniform(10, 90, 22)
        ys = 8 + xs * 0.55 + rng.normal(0, 6, 22)
        ax.scatter(xs, ys, s=10, color=[B if x > 70 else G for x in xs], lw=0, alpha=0.9)
        ax.plot([6, 6, 96], [62, 4, 4], color=C.axis, lw=0.8)
    elif kind == "flows":
        def band(y1a, y1b, y2a, y2b, c, a):
            t = np.linspace(0, 1, 30)
            s = 3 * t ** 2 - 2 * t ** 3
            top = y1a + (y2a - y1a) * s
            bot = y1b + (y2b - y1b) * s
            ax.fill_between(14 + 72 * t, bot, top, color=c, alpha=a, lw=0)
        band(62, 44, 62, 50, G, 0.5)
        band(44, 30, 28, 14, G, 0.5)
        band(28, 4, 48, 30, B, 0.6)
        for x, segs in ((8, [(44, 62, G), (30, 44, G), (4, 28, B)]), (86, [(50, 62, G), (30, 48, B), (4, 28, G)])):
            for y0, y1, c in segs:
                ax.add_patch(Rectangle((x, y0), 6, y1 - y0 - 1, color=c, lw=0))
    elif kind == "geo":
        shades = mv.SEQUENTIAL["blue"]
        grid = [[1, 2, 4, 2, 1], [2, 5, 3, 1, 0], [0, 1, 2, 4, 2]]
        for r, row in enumerate(grid):
            for c, k in enumerate(row):
                ax.add_patch(Rectangle((8 + c * 17.5, 44 - r * 20), 16.5, 18.5, color=shades[k], lw=0))
    elif kind == "single":
        ax.text(4, 34, "75%", fontsize=21, fontweight=700, color=C.headline, va="center")
        ax.add_patch(Rectangle((4, 6), 92, 6, color=GL, lw=0))
        ax.add_patch(Rectangle((4, 6), 69, 6, color=B, lw=0))
    return fig


FAMILIES = ["magnitude", "part", "time", "ranking", "distribution", "correlation", "flows", "geo", "single"]
for _k in FAMILIES:
    EXHIBITS[f"ch_icon_{_k}"] = (lambda k=_k: (_icon(k), f"Icon for the {k} chart family."))


# ================================================================== CHEAT SHEET
def cs_bars():
    d = ATTR.tail(5)
    fig = fig_px(250, 112)
    ax = fig.add_subplot()
    hbars(ax, [SHORT[f] for f in d.job_family], d.vol_attrition_pct, mv.highlight(d.job_family, focus=FOCUS),
          bold={SHORT[f] for f in FOCUS}, size=MINI - 1.5, tick=MINI - 1.5, xmax=46)
    bench(ax, ENT, f"Enterprise {ENT:.1f}%", size=MINI - 1.5)
    ax.set_ylim(-0.6, len(d) + 0.1)
    marker(ax, (float(d.vol_attrition_pct.iloc[-1]), len(d) - 1), 3, offset=(46, 0))
    return fig, (f"Five job families' voluntary attrition; Pharmacy Technician and DC Associate in blue above the "
                 f"{ENT:.1f}% enterprise rate.")


EXHIBITS["cs_bars"] = cs_bars


# ------------------------------------------------------------------ token-driven snippets for the cheat sheet
from exhibits import HTML  # noqa: E402

_ROLES = [("context", "Context", "everything else"), ("focus", "Focus", "what the headline names"),
          ("accent", "Accent (navy)", "the one exception"), ("focus_light", "Light blue", "a series, in the uniform pattern"),
          ("negative", "Orange", "worse only: below target, shrinking"), ("positive", "Green", "better only, with ▲ or words")]
HTML["cs_roles"] = "".join(
    f'<div class="cs-role"><span class="sw" style="background:{getattr(C, k)}"></span><span><b>{n}</b> {u}</span>'
    f"<code>{getattr(C, k)}</code></div>" for k, n, u in _ROLES)

_T = mv.TOKENS["typography"]["roles"]
_WN = {300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}
_TYPE = [("slide_title", "Slide title"), ("headline", "Chart headline"), ("subtitle", "Subtitle"), ("label", "Data labels"),
         ("tick", "Axis, categories"), ("footnote", "Footnote, source"), ("kpi", "Big number")]
HTML["cs_type"] = ('<table class="cs-table"><tbody>' + "".join(
    f'<tr><td>{n}</td><td>{_WN[_T[k]["weight"]]}</td><td class="num">{_T[k]["size_pt"]} pt</td></tr>' for k, n in _TYPE)
    + "</tbody></table>")
