"""Formats exhibits: presentations, print, mobile, dashboards, interactivity, animation, icons, social."""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge

import mckviz as mv
from exhibits import (ANNOT, ANTI, ATTR, BAND, ENT, FOCUS, FOCUS_EXIT_SHARE, LABEL, MINI, SHORT, SUPPLY, TICK, C,
                      EXHIBITS, TEXT, _csv, _plain, bench, exhibit, fig_px, hbars)

AQ = _csv("attrition_quarterly")
QS = list(dict.fromkeys(AQ.quarter))
PIV = AQ.pivot(index="quarter", columns="job_family", values="attrition_pct").loc[QS]
TINY6 = {"Pharmacy Technician": "Rx Tech", "Distribution Center Associate": "DC", "Customer Care": "Care",
         "Specialty Nursing": "Nursing", "Software Engineering": "Eng.", "Finance": "Finance", "Data & Analytics": "Data",
         "Supply Chain Planning": "Supply", "Sales": "Sales", "HR": "HR"}
SC = _csv("job_family_scorecard").set_index("job_family")
FILL = _csv("internal_fill_by_fy")
_pt_delta = float(SC.attrition_change_pts["Pharmacy Technician"])
TEXT["dash_headline"] = (f"Pharmacy Technician attrition is down {abs(_pt_delta):.1f} points, but two frontline families "
                         "still lose about 1 in 4 a year")


def nudge(values, gap):
    """Spread label positions (sorted) so neighbours are at least `gap` apart; returns positions in input order."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    pos = [values[i] for i in order]
    for k in range(1, len(pos)):
        pos[k] = max(pos[k], pos[k - 1] + gap)
    out = [0.0] * len(values)
    for k, i in enumerate(order):
        out[i] = pos[k]
    return out


# ------------------------------------------------------------------ helpers
def canvas(fig):
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return ax


def text_lines(ax, x, y, w, n, gap=0.035, h=0.012, color=None, last=0.6):
    for i in range(n):
        ax.add_patch(Rectangle((x, y - i * gap), w * (last if i == n - 1 else 1), h, color=color or C.grid, lw=0))


def mini_bars(ax, rect, focus=True, labels=False, colors=None, n=6, fig=None):
    inner = fig.add_axes(rect)
    d = ATTR.tail(n)
    cols = colors or (mv.highlight(d.job_family, focus=FOCUS) if focus else [C.context] * n)
    inner.barh(range(n), d.vol_attrition_pct, color=cols, height=BAND)
    inner.set_xlim(0, 32)
    inner.axis("off")
    if labels:
        for y, v in enumerate(d.vol_attrition_pct):
            inner.text(v + 0.6, y, f"{v:.0f}", va="center", fontsize=5.5, color=C.text)
    return inner


# ================================================================== PRESENTATIONS
def _build(step):
    labels = [SHORT[f] for f in ATTR.job_family]
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    cols = mv.highlight(ATTR.job_family, focus=FOCUS) if step >= 2 else [C.context] * len(ATTR)
    hbars(ax, labels, ATTR.vol_attrition_pct, cols, bold={SHORT[f] for f in FOCUS} if step >= 2 else (),
          size=MINI - 1, tick=MINI - 1, xmax=54)
    if step == 3:
        bench(ax, ENT, f"Enterprise {ENT:.1f}%", size=MINI - 1)
        n = len(labels)
        ax.plot([36.2, 37.0, 37.0, 36.2], [n - 0.7, n - 0.7, n - 2.3, n - 2.3], color=C.annotation, lw=0.9)
        ax.text(37.8, n - 1.5, f"{FOCUS_EXIT_SHARE:.0f}% of all\nvoluntary exits", va="center", fontsize=MINI - 1.5,
                color=C.annotation, fontweight=600, linespacing=1.1)
    return fig


for _s, _alt in {1: "Step 1: every bar grey, labelled, so the audience learns the chart.",
                 2: "Step 2: the two families the headline names turn blue.",
                 3: "Step 3: the benchmark and a callout complete the picture."}.items():
    EXHIBITS[f"fmt_build_{_s}"] = (lambda s=_s, a=_alt: (_build(s), a))


def _slide(kind):
    fig = fig_px(300, 169)
    ax = canvas(fig)
    dark = kind == "dark"
    bg = C.surface_dark if dark else "white"
    ax.add_patch(Rectangle((0.005, 0.01), 0.99, 0.98, facecolor=bg, edgecolor=C.grid, lw=1))
    if kind == "avoid":
        ax.text(0.05, 0.9, "Attrition analysis", fontsize=MINI, color=C.headline, fontweight=700, va="top")
        for i, (x, y) in enumerate([(0.05, 0.47), (0.36, 0.47), (0.05, 0.08), (0.36, 0.08)]):
            sub = fig.add_axes([x, y, 0.27, 0.3])
            if i == 0:
                sub.pie([5, 4, 3, 2, 2, 1], colors=ANTI["rainbow"][:6], startangle=90)
            elif i == 1:
                sub.bar(range(6), [5, 3, 6, 2, 4, 3], color=ANTI["rainbow"][:6])
                sub.grid(True, color="#BBBBBB", lw=0.4)
                sub.tick_params(labelsize=3, length=1.5)
            elif i == 2:
                for k in range(4):
                    sub.plot(np.cumsum(np.random.default_rng(k).normal(0, 1, 12)), color=ANTI["rainbow"][k], lw=0.8)
                sub.tick_params(labelsize=3, length=1.5)
            else:
                text_lines(sub, 0.02, 0.85, 0.95, 7, gap=0.13, h=0.06)
                sub.set_xlim(0, 1); sub.set_ylim(0, 1); sub.axis("off")
            if i < 3:
                sub.set_xticks([]); sub.set_yticks([])
        for k in range(9):
            ax.add_patch(Rectangle((0.69, 0.78 - k * 0.075), 0.25 if k % 3 else 0.2, 0.025, color=C.context_light, lw=0))
        return fig
    ax.text(0.05, 0.92, "Two frontline job families lose about 1 in 4\npeople a year, well above the enterprise rate",
            fontsize=MINI - 1, color="white" if dark else C.headline, fontweight=700, va="top", linespacing=1.2)
    inner = fig.add_axes([0.2, 0.14, 0.62, 0.52])
    d = ATTR.tail(6)
    if dark:
        cols = [C.focus_on_dark if f in FOCUS else C.context_on_dark for f in d.job_family]
    else:
        cols = mv.highlight(d.job_family, focus=FOCUS)
    inner.barh(range(6), d.vol_attrition_pct, color=cols, height=BAND)
    for y, (f, v) in enumerate(zip(d.job_family, d.vol_attrition_pct)):
        inner.text(-0.6, y, SHORT[f], ha="right", va="center", fontsize=5.5,
                   color=("white" if dark else C.headline) if f in FOCUS else (C.context_light if dark else C.text_muted),
                   fontweight=700 if f in FOCUS else 400)
        inner.text(v + 0.6, y, f"{v:.0f}%", va="center", fontsize=5.5, color="white" if dark else C.text)
    inner.set_xlim(0, 32)
    inner.axis("off")
    ax.text(0.05, 0.05, "Source: Workday HCM, FY26", fontsize=5, color=C.context_light if dark else C.text_muted)
    return fig


for _k, _alt in {"avoid": "A slide with a label title, four small charts and a column of bullet text.",
                 "fix": "A slide whose title is the headline, with one large chart and a source line.",
                 "dark": "The same slide on a dark navy background for a dimmed room."}.items():
    EXHIBITS[f"fmt_slide_{_k}"] = (lambda k=_k, a=_alt: (_slide(k), a))


# ================================================================== PRINT
def _page(kind):
    fig = fig_px(170, 220)
    ax = canvas(fig)
    ax.add_patch(Rectangle((0.02, 0.01), 0.96, 0.98, facecolor="white", edgecolor=C.grid, lw=1))
    if kind == "featured":
        ax.add_patch(Rectangle((0.1, 0.84), 0.6, 0.035, color=C.headline, lw=0))
        ax.add_patch(Rectangle((0.1, 0.79), 0.45, 0.02, color=C.context, lw=0))
        mini_bars(ax, [0.1, 0.18, 0.8, 0.56], fig=fig, labels=True)
        text_lines(ax, 0.1, 0.1, 0.5, 2, gap=0.03, h=0.012)
    elif kind == "editorial":
        ax.add_patch(Rectangle((0.1, 0.9), 0.55, 0.03, color=C.headline, lw=0))
        text_lines(ax, 0.1, 0.84, 0.37, 20, gap=0.034)
        ax.add_patch(Rectangle((0.53, 0.84), 0.37, 0.022, color=C.headline, lw=0))
        mini_bars(ax, [0.53, 0.52, 0.37, 0.28], fig=fig)
        text_lines(ax, 0.53, 0.46, 0.37, 11, gap=0.034)
    else:                                                           # inline
        ax.add_patch(Rectangle((0.1, 0.9), 0.55, 0.03, color=C.headline, lw=0))
        text_lines(ax, 0.1, 0.84, 0.8, 7, gap=0.034)
        ax.add_patch(Rectangle((0.1, 0.57), 0.37, 0.018, color=C.headline, lw=0))
        mini_bars(ax, [0.1, 0.36, 0.37, 0.19], fig=fig)
        text_lines(ax, 0.53, 0.58, 0.37, 7, gap=0.034)
        text_lines(ax, 0.1, 0.3, 0.8, 6, gap=0.034)
    return fig


for _k, _alt in {"featured": "A page where one chart fills most of the space.",
                 "editorial": "A two-column page with a chart in one column.",
                 "inline": "A small chart inside one text column, next to the paragraph it supports."}.items():
    EXHIBITS[f"fmt_print_{_k}"] = (lambda k=_k, a=_alt: (_page(k), a))


# ================================================================== WEB AND MOBILE
def _desk(kind):
    fig = fig_px(250, 140)
    ax = fig.add_subplot()
    if kind == "bars":
        d = ATTR.tail(6).iloc[::-1]
        ax.bar(range(6), d.vol_attrition_pct, color=mv.highlight(d.job_family, focus=FOCUS), width=BAND)
        ax.set_xticks(range(6), [TINY6.get(f, f) for f in d.job_family], fontsize=MINI - 2.5)
        for x, v in enumerate(d.vol_attrition_pct):
            ax.text(x, v + 0.6, f"{v:.0f}", ha="center", fontsize=MINI - 2.5, color=C.text)
        ax.set_yticks([])
        ax.tick_params(length=0)
        _plain(ax, bottom=True)
    else:
        fams = list(PIV.iloc[-1].sort_values(ascending=False).index)[:5]
        ys = nudge([PIV[f].iloc[-1] for f in fams], 2.6)
        for f, yl in zip(fams, ys):
            hot = f == "Pharmacy Technician"
            ax.plot(PIV[f].values, color=(C.focus if hot else C.context) if kind == "simple" else
                    mv.CATEGORICAL[fams.index(f)], lw=1.8 if hot else 1.2)
            ax.text(len(QS) - 0.6, yl, TINY6[f], fontsize=MINI - 3, va="center", color=C.focus if hot else C.text_muted)
        if kind == "key":
            ax.annotate("Reset", (6, PIV["Pharmacy Technician"].iloc[6]), xytext=(4, 36), fontsize=MINI - 3,
                        color=C.annotation, arrowprops=dict(arrowstyle="-", color=C.annotation, lw=0.6))
        ax.set_xlim(0, len(QS) + 1.8)
        ax.set_ylim(5, 38)
        ax.set_xticks([])
        ax.set_yticks([])
        _plain(ax, bottom=True)
    return fig


def _phone(kind):
    fig = fig_px(130, 205)
    ax = canvas(fig)
    ax.add_patch(FancyBboxPatch((0.04, 0.02), 0.92, 0.96, boxstyle="round,pad=0,rounding_size=0.06",
                                facecolor="white", edgecolor=C.axis, lw=1.2))
    if kind == "bars":
        ax.text(0.12, 0.9, "Two families lose\n1 in 4 a year", fontsize=MINI - 3, color=C.headline, fontweight=700,
                va="top", linespacing=1.15)
        inner = fig.add_axes([0.36, 0.12, 0.5, 0.62])
        d = ATTR.tail(6)
        inner.barh(range(6), d.vol_attrition_pct, color=mv.highlight(d.job_family, focus=FOCUS), height=BAND)
        for y, (f, v) in enumerate(zip(d.job_family, d.vol_attrition_pct)):
            inner.text(-0.8, y, TINY6.get(f, f), ha="right", va="center", fontsize=MINI - 4,
                       color=C.headline if f in FOCUS else C.text_muted, fontweight=700 if f in FOCUS else 400)
            inner.text(v + 0.8, y, f"{v:.0f}", va="center", fontsize=MINI - 4, color=C.text)
        inner.set_xlim(0, 34)
        inner.axis("off")
        return fig
    ax.text(0.12, 0.9, "Rx Tech attrition\nfell 9 points", fontsize=MINI - 3, color=C.headline, fontweight=700,
            va="top", linespacing=1.15)
    fams = list(PIV.iloc[-1].sort_values(ascending=False).index)[:5]
    if kind == "key":
        ax.text(0.12, 0.74, "After the pay reset in Q3 FY25", fontsize=MINI - 4.5, color=C.annotation, va="top")
        for i, f in enumerate(fams[:4]):
            y = 0.67 - (i // 2) * 0.05
            x = 0.12 + (i % 2) * 0.4
            ax.add_patch(Rectangle((x, y - 0.006), 0.05, 0.012, color=mv.CATEGORICAL[i], lw=0))
            ax.text(x + 0.07, y, TINY6[f], fontsize=MINI - 4.5, va="center", color=C.text)
    inner = fig.add_axes([0.12, 0.1, 0.78, 0.48 if kind == "key" else 0.58])
    for i, f in enumerate(fams if kind == "key" else fams):
        hot = f == "Pharmacy Technician"
        col = mv.CATEGORICAL[i] if kind == "key" else (C.focus if hot else C.context_light)
        inner.plot(PIV[f].values, color=col, lw=1.6 if hot else 1)
    if kind == "simple":
        inner.text(len(QS) - 1, PIV["Pharmacy Technician"].iloc[-1] + 3, "Rx Tech", ha="right", fontsize=MINI - 4,
                   color=C.focus, fontweight=700)
    inner.set_ylim(5, 38)
    inner.axis("off")
    return fig


for _k, _alt in {"bars": ("Desktop: columns of attrition by job family.", "Phone: the same data as horizontal bars, headline shortened."),
                 "key": ("Desktop: lines labelled at their ends with a callout at the data.", "Phone: a compact key and the insight moved above the chart."),
                 "simple": ("Desktop: five lines, labelled.", "Phone: one highlighted line, the rest faint, the insight on top.")}.items():
    EXHIBITS[f"fmt_desk_{_k}"] = (lambda k=_k, a=_alt[0]: (_desk(k), a))
    EXHIBITS[f"fmt_phone_{_k}"] = (lambda k=_k, a=_alt[1]: (_phone(k), a))


# ================================================================== DASHBOARDS
def _card(fig, rect, value, label, delta=None, bad=False, gauge=False):
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=C.grid, lw=0.8))
    if gauge:
        ax.add_patch(Wedge((0.5, 0.18), 0.38, 0, 180, width=0.12, color=ANTI["green"]))
        ax.add_patch(Wedge((0.5, 0.18), 0.38, 120, 180, width=0.12, color=ANTI["red"]))
        ax.add_patch(Wedge((0.5, 0.18), 0.38, 60, 120, width=0.12, color="#FFD700"))
        ax.plot([0.5, 0.3], [0.18, 0.42], color="black", lw=1.2)
        ax.text(0.5, 0.04, value, ha="center", fontsize=MINI - 3, color="black")
        return
    ax.text(0.08, 0.86, label, fontsize=MINI - 3.5, color=C.text, va="top")
    ax.text(0.08, 0.42, value, fontsize=MINI + 3, color=C.headline, fontweight=300, va="center")
    if delta:
        ax.text(0.08, 0.14, delta, fontsize=MINI - 3.5, color=C.negative_text if bad else C.text, va="center")


def _dashboard(kind):
    fig = fig_px(470, 290)
    fig.set_layout_engine("none")
    bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off")
    bg.add_patch(Rectangle((0, 0), 1, 1, color=C.surface_subtle, transform=bg.transAxes))
    if kind == "fix":
        bg.text(0.03, 0.95, TEXT["dash_headline"], fontsize=MINI - 1.5,
                color=C.headline, fontweight=700, va="top", transform=bg.transAxes)
        fill_now, fill_prev = int(FILL.internal_fill_pct.iloc[-1]), int(FILL.internal_fill_pct.iloc[-2])
        cards = [(f"{ENT:.1f}%", "Enterprise attrition, FY26", "All job families", False),
                 (f"{SC.vol_attrition_pct['Pharmacy Technician']:.1f}%", "Pharmacy Technician attrition",
                  f"{mv.signed(_pt_delta, 1)} pts vs. FY25", _pt_delta > 0),
                 (f"{fill_now}%", "Internal fill rate, FY26", f"{mv.signed(fill_now - fill_prev)} pts vs. FY25", False)]
        for i, (v, l, d, bad) in enumerate(cards):
            _card(fig, [0.03 + i * 0.32, 0.66, 0.3, 0.2], v, l, d, bad)
        a1 = fig.add_axes([0.05, 0.08, 0.42, 0.5])
        d = ATTR.tail(7)
        a1.barh(range(len(d)), d.vol_attrition_pct, color=mv.highlight(d.job_family, focus=FOCUS), height=BAND)
        for y, (f, v) in enumerate(zip(d.job_family, d.vol_attrition_pct)):
            a1.text(-0.5, y, SHORT[f], ha="right", va="center", fontsize=MINI - 4, color=C.text)
            a1.text(v + 0.5, y, f"{v:.0f}%", va="center", fontsize=MINI - 4, color=C.text)
        a1.set_xlim(-11, 32); a1.axis("off")
        a2 = fig.add_axes([0.55, 0.1, 0.42, 0.42])
        for f in PIV.columns:
            a2.plot(PIV[f].values, color=C.focus if f == "Pharmacy Technician" else C.context_light,
                    lw=1.6 if f == "Pharmacy Technician" else 0.9)
        a2.set_ylim(0, 38)
        a2.set_yticks([0, 20], ["0", "20"])
        a2.tick_params(labelsize=MINI - 4, length=0, colors=C.text_muted)
        a2.set_xticks([])
        a2.grid(axis="y", color=C.grid, lw=0.5)
        _plain(a2, bottom=True)
        a2.text(0, 1.06, "Attrition by quarter (%)", transform=a2.transAxes, fontsize=MINI - 3.5, color=C.text)
        return fig
    bg.text(0.03, 0.95, "HR DASHBOARD", fontsize=MINI - 1, color="black", fontweight=700, va="top", transform=bg.transAxes)
    for i in range(3):
        _card(fig, [0.03 + i * 0.32, 0.64, 0.3, 0.24], f"{[19.9, 27.4, 29][i]}", "", gauge=True)
    a1 = fig.add_axes([0.05, 0.08, 0.28, 0.45])
    a1.pie(ATTR.headcount, colors=ANTI["rainbow"][:len(ATTR)], startangle=90)
    a2 = fig.add_axes([0.4, 0.1, 0.56, 0.42])
    d = ATTR.sort_values("job_family")
    a2.bar(range(len(d)), d.vol_attrition_pct, color=ANTI["rainbow"][:len(d)], edgecolor="black", lw=0.4)
    a2.set_xticks(range(len(d)), [SHORT[f][:6] for f in d.job_family], rotation=60, fontsize=MINI - 4.5)
    a2.grid(True, color="#BBBBBB", lw=0.4)
    a2.tick_params(labelsize=MINI - 4.5, length=2)
    a2.legend(handles=[Rectangle((0, 0), 1, 1, color=c) for c in ANTI["rainbow"][:4]], labels=["", "", "", ""],
              fontsize=4, loc="upper right", ncol=2)
    return fig


for _k, _alt in {"avoid": "A dashboard of gauges, a rainbow pie and rainbow columns with a label-style title.",
                 "fix": "A dashboard with an insight title, three KPI cards, a highlighted bar chart and a trend."}.items():
    EXHIBITS[f"fmt_dash_{_k}"] = (lambda k=_k, a=_alt: (_dashboard(k), a))


# ================================================================== INTERACTIVITY
@exhibit
def fmt_tooltip():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x = np.arange(len(QS))
    for f in PIV.columns:
        hot = f == "Pharmacy Technician"
        ax.plot(x, PIV[f], color=C.focus if hot else C.context, lw=2 if hot else 1.1)
    k = 8
    ax.axvline(k, color=C.axis, lw=0.8)
    ax.plot(k, PIV["Pharmacy Technician"].iloc[k], "o", color=C.focus, ms=5, mec="white", mew=1)
    box = f"{QS[k]}\nPharmacy Tech  {PIV['Pharmacy Technician'].iloc[k]:.1f}%\nHeadcount 6,200"
    ax.text(k - 0.4, 37, box, fontsize=MINI - 2, va="top", ha="right", color=C.text, linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.2", fc="white", ec=C.grid, lw=0.8))
    ax.set_ylim(0, 40)
    ax.set_xticks([0, 4, 8], ["FY24", "FY25", "FY26"])
    ax.set_yticks([])
    ax.tick_params(labelsize=MINI - 1.5, length=0)
    _plain(ax, bottom=True)
    return fig, "Cursor tracking on a line chart: a vertical rule and a tooltip with the quarter, the value and the headcount."


# ================================================================== ANIMATION
def _frame(step):
    s = SUPPLY
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    n = {1: 0, 2: 4, 3: len(s)}[step]
    if n:
        ax.plot(s.year[:n], s.demand_fte[:n], color=C.focus, lw=2)
        ax.plot(s.year[:n], s.internal_supply_fte[:n], color=C.context, lw=1.6)
    if step == 3:
        ax.fill_between(s.year, s.internal_supply_fte, s.demand_fte, color=C.negative, alpha=0.12, lw=0)
        ax.text(2029.6, (s.demand_fte.iloc[-1] + s.internal_supply_fte.iloc[-1]) / 2, "Gap", ha="right", va="center",
                fontsize=MINI - 2, color=C.negative_text, fontweight=600)
    ax.set_xlim(2023.8, 2030.3)
    ax.set_ylim(700, 1700)
    ax.set_xticks([2024, 2027, 2030])
    ax.set_yticks([1000, 1500])
    ax.grid(axis="y", color=C.grid, lw=0.5)
    ax.tick_params(labelsize=MINI - 2.5, length=0, colors=C.text_muted)
    _plain(ax, bottom=True)
    return fig


for _s, _alt in {1: "Frame 1: axes and labels only.", 2: "Frame 2: the lines draw in from the left.",
                 3: "Frame 3: the gap shades in once both lines are complete."}.items():
    EXHIBITS[f"fmt_anim_{_s}"] = (lambda s=_s, a=_alt: (_frame(s), a))


# ================================================================== ICONS AND SOCIAL
def person(ax, x, y, s, color):
    """A simple person glyph: head and rounded shoulders, s units tall (axes must have equal aspect)."""
    ax.add_patch(Circle((x, y + 0.78 * s), 0.19 * s, color=color, lw=0))
    ax.add_patch(FancyBboxPatch((x - 0.3 * s, y), 0.6 * s, 0.5 * s,
                                boxstyle=f"round,pad=0,rounding_size={0.22 * s}", color=color, lw=0))


def _icons(kind):
    fig = fig_px(200, 140)
    ax = canvas(fig)
    ax.set_xlim(0, 200 / 140)
    ax.set_aspect("equal")
    if kind == "avoid":                                   # value doubled -> icon scaled in both dimensions (4x area)
        person(ax, 0.38, 0.22, 0.3, C.context)
        person(ax, 0.98, 0.16, 0.6, C.focus)
        ax.text(0.38, 0.1, "1,000", ha="center", fontsize=MINI - 2, color=C.text)
        ax.text(0.98, 0.04, "2,000", ha="center", fontsize=MINI - 2, color=C.text)
        return fig
    for row, (n, col, lab) in enumerate([(10, C.context, "1,000"), (20, C.focus, "2,000")]):
        y = 0.66 - row * 0.36
        for i in range(n):
            person(ax, 0.08 + (i % 10) * 0.1, y - (i // 10) * 0.16, 0.12, col)
        ax.text(1.1, y + 0.06 - (0.08 if n > 10 else 0), lab, fontsize=MINI - 2, color=C.text, va="center")
    ax.text(0.04, 0.96, "Each icon = 100 people", fontsize=MINI - 3, color=C.text_muted, va="top")
    return fig


for _k, _alt in {"avoid": "A person icon scaled up in height and width to show double the value: it looks four times bigger.",
                 "fix": "A pictogram where each icon is 100 people: 10 icons versus 20."}.items():
    EXHIBITS[f"fmt_icon_{_k}"] = (lambda k=_k, a=_alt: (_icons(k), a))


@exhibit
def fmt_social():
    combo = mv.TOKENS["color"]["social"]["combos"][0]
    bgc, fg = combo["background"], combo["foreground"]
    fig = fig_px(240, 240)
    ax = canvas(fig)
    ax.add_patch(Rectangle((0, 0), 1, 1, color=bgc, lw=0))
    ax.text(0.08, 0.9, f"{FOCUS_EXIT_SHARE:.0f}%", fontsize=44, color=fg[1], fontweight=300, va="top")
    ax.text(0.08, 0.6, "of voluntary exits come from\njust two frontline job families", fontsize=MINI, color=fg[0],
            va="top", linespacing=1.25)
    ax.add_patch(Rectangle((0.08, 0.3), 0.84, 0.06, color=C.context_on_dark, lw=0))
    ax.add_patch(Rectangle((0.08, 0.3), 0.84 * FOCUS_EXIT_SHARE / 100, 0.06, color=fg[1], lw=0))
    ax.text(0.08, 0.13, "Source: Workday HCM, FY26 (synthetic)", fontsize=MINI - 3, color=fg[0], alpha=0.75)
    ax.text(0.92, 0.13, "McKesson", fontsize=MINI - 1.5, color=fg[0], fontweight=700, ha="right")
    return fig, f"A square social card: {FOCUS_EXIT_SHARE:.0f}% of voluntary exits come from two frontline job families."
