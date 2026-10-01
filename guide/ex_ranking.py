"""Ranking exhibits: slope and bump charts, dot plots and dumbbells, heat tables. Registered on import."""
from __future__ import annotations

import html as _html

import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import mckviz as mv
from exhibits import (ANNOT, ANTI, BAND, LABEL, MINI, SHORT, TICK, C, EXHIBITS, HTML, TEXT, _csv, _plain, exhibit,
                      fig_px, marker)

WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
ORD = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth"}


# ------------------------------------------------------------------ helpers
def spread(ys, gap, lo=-np.inf, hi=np.inf):
    """Nudge label positions apart (at least `gap`), keeping their order; returns positions in the input order."""
    order = np.argsort(ys)
    out = np.asarray(ys, float)[order].copy()
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + gap)
    shift = max(0, out[-1] - hi)
    out -= shift
    for i in range(len(out) - 2, -1, -1):
        out[i] = min(out[i], out[i + 1] - gap)
    out += max(0, lo - out[0])
    res = np.empty_like(out)
    res[order] = out
    return res


def lab_style(col, hot):
    if col == C.negative:
        return dict(color=C.negative_text, fontweight=600)
    return dict(color=C.headline if hot else C.text, fontweight=600 if hot else 400)


def rank_slope(ax, names, r0, r1, cols, *, hot=(), size=LABEL, lw=(2.4, 1.4), dot=34, nums=True,
               headers=("2023", "2026"), hsize=None, dx=0.05, label=None):
    """Two-point rank slope, rank 1 at the top, names at both ends. Returns {name: right-hand text artist}."""
    label = label or {}
    right = {}
    for i in sorted(range(len(names)), key=lambda i: names[i] in hot):        # context first, highlights on top
        nm, c, h = names[i], cols[i], names[i] in hot or cols[i] != C.context
        ax.plot([0, 1], [r0[i], r1[i]], color=c, lw=lw[0] if h else lw[1], zorder=3 if h else 2,
                solid_capstyle="round")
        ax.scatter([0, 1], [r0[i], r1[i]], s=dot, color=c, zorder=4 if h else 2, lw=0)
        txt = label.get(nm, nm)
        kw = dict(va="center", fontsize=size, **lab_style(c, h))
        ax.text(-dx, r0[i], f"{txt}  {r0[i]}" if nums else txt, ha="right", **kw)
        right[nm] = ax.text(1 + dx, r1[i], f"{r1[i]}  {txt}" if nums else txt, ha="left", **kw)
    if headers:
        for x, hd in zip((0, 1), headers):
            ax.text(x, 0.2, hd, ha="center", va="center", fontsize=hsize or size, fontweight=700, color=C.text)
    n = max(max(r0), max(r1))
    ax.set_ylim(n + 0.6, -0.3)
    ax.axis("off")
    return right


# ------------------------------------------------------------------ data
SK = _csv("skills_demand_rank")
SK["move"] = SK.rank_2023 - SK.rank_2026
_RISE = int(SK.move.max())
RISERS = list(SK.sort_values("rank_2026").skill[SK.move == _RISE])
assert set(RISERS) == {"Data analysis", "Gen AI / prompt design"}           # the headline names these two
SK_SHORT = {"Inventory management": "Inventory mgmt.", "Customer service": "Customer service",
            "Regulatory compliance": "Regulatory", "Data analysis": "Data analysis",
            "Automation / robotics": "Automation", "Clinical documentation": "Clinical docs.",
            "Sales & negotiation": "Sales", "Project management": "Project mgmt.",
            "Gen AI / prompt design": "Gen AI"}
TEXT["rk_slope_headline"] = ("Data analysis and gen AI are the fastest-rising skills in sector job postings, "
                             f"up {WORD[_RISE]} places each since 2023")
TEXT["rk_slope_subtitle"] = "Rank of skills in U.S. healthcare-distribution job postings, 2023 vs. 2026 (1 = most requested)"
TEXT["rk_n_skills"] = str(len(SK))

FB = _csv("internal_fill_by_bu")
FY = list(dict.fromkeys(FB.fiscal_year))
FBP = FB.pivot(index="business_unit", columns="fiscal_year", values="internal_fill_pct")[FY]
FBR = FBP.rank(ascending=False, method="first").astype(int)
BU_SHORT = {"Oncology & Multispecialty": "Oncology", "U.S. Pharmaceutical": "U.S. Pharma",
            "Medical-Surgical": "Med-Surg", "Technology": "Technology", "Corporate": "Corporate", "RxTS": "RxTS"}
_TECH, _ONC = "Technology", "Oncology & Multispecialty"
_nb = len(FBR)
TEXT["rk_bump_note"] = (f"Rank order over five years. Technology climbed from "
                        f"{'last' if FBR.loc[_TECH, FY[0]] == _nb else ORD[FBR.loc[_TECH, FY[0]]]} to "
                        f"{ORD[FBR.loc[_TECH, FY[-1]]]} in internal fill; Oncology slid from "
                        f"{ORD[FBR.loc[_ONC, FY[0]]]} to {'last' if FBR.loc[_ONC, FY[-1]] == _nb else ORD[FBR.loc[_ONC, FY[-1]]]}.")
TEXT["rk_value_note"] = (f"Values on one shared scale, when the size of the change matters: Technology went from "
                         f"{FBP.loc[_TECH, FY[0]]}% to {FBP.loc[_TECH, FY[-1]]}%, Oncology from "
                         f"{FBP.loc[_ONC, FY[0]]}% to {FBP.loc[_ONC, FY[-1]]}%.")

_top = 6
_in = SK[(SK.rank_2026 <= _top) & (SK.rank_2023 > _top)]
_out = SK[(SK.rank_2023 <= _top) & (SK.rank_2026 > _top)]
assert len(_in) == 1 and len(_out) == 1
TEXT["rk_topn_note"] = (f"“Top {_top}” in the subtitle, and a stub for what enters or leaves: gen AI enters "
                        f"from {ORD[int(_in.rank_2023.iloc[0])]}; clinical documentation drops to "
                        f"{ORD[int(_out.rank_2026.iloc[0])]}.")

PAY = _csv("pay_vs_market").sort_values("gap_pct", ignore_index=True)        # largest shortfall first
LAG = PAY.gap_pct <= -5
assert set(PAY.role[LAG]) == {"RN, Specialty", "Pharmacy Technician", "Pharmacist"}   # clinical and pharmacy roles
TEXT["rk_db_headline"] = f"McKesson pay trails the market by 5% or more for {WORD[int(LAG.sum())]} clinical and pharmacy roles"
TEXT["rk_db_subtitle"] = "Median base pay, McKesson vs. external market, 2026 ($K)"

SC = _csv("job_family_scorecard")
FL = _csv("hiring_flow_by_family").set_index("job_family")
_w = lambda c: float(np.average(SC[c], weights=SC.headcount))                 # weighted by headcount
SC_FOCUS = set(SC.job_family[SC.vol_attrition_pct > 20])
assert SC_FOCUS == set(SC.nsmallest(2, "engagement_index").job_family) == set(SC.nlargest(2, "headcount").job_family)
TEXT["rk_heat_headline"] = "The two largest frontline job families combine the highest attrition with the lowest engagement"
TEXT["rk_heat_subtitle"] = "Workforce scorecard by job family, FY26; totals weighted by headcount"
TEXT["rk_eng_avg"] = f"{_w('engagement_index'):.0f}"
TEXT["rk_eng_range"] = f"{SC.engagement_index.min()}–{SC.engagement_index.max()}"
TEXT["rk_n_families"] = str(len(SC))


# ================================================================== SLOPE
@exhibit
def rk_slope_anatomy():
    fig = fig_px(640, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    names = list(SK.skill)
    cols = [C.focus if s in RISERS else C.context for s in names]
    right = rank_slope(ax, names, list(SK.rank_2023), list(SK.rank_2026), cols, hot=set(RISERS), size=LABEL)
    for s in RISERS:
        ax.annotate(mv.signed(_RISE), xy=(1, 0.5), xycoords=right[s], xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=LABEL, color=C.focus, fontweight=700)
    ax.set_xlim(-0.82, 1.95)
    da = SK.set_index("skill").loc["Data analysis"]
    ga = SK.set_index("skill").loc["Gen AI / prompt design"]
    marker(ax, (0.62, da.rank_2023 - 0.62 * 3), 3, offset=(6, 13))
    marker(ax, (0.5, 7.5), 4, offset=(0, -12))
    marker(ax, (-0.05, 1), 5, offset=(-160, 0))
    marker(ax, (1, 0.2), 6, offset=(26, 0))
    marker(ax, (1.05, ga.rank_2026), 7, offset=(178, 0))
    marker(ax, (-0.7, 8), 8)
    return fig, (TEXT["rk_slope_headline"] + ". Data analysis rose from 4th to 1st and gen AI from 9th to 6th; "
                 "customer service fell from 2nd to 5th.")


@exhibit
def rk_var_bump():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    bump(ax)
    return fig, TEXT["rk_bump_note"]


def bump(ax, *, size=MINI - 2, ms=120, num=MINI - 3.5, dx=0.32, lw=(2, 1.1), header=True):
    x = np.arange(len(FY))
    for b in sorted(FBR.index, key=lambda b: b in (_TECH, _ONC)):
        col = C.focus if b == _TECH else C.negative if b == _ONC else C.context
        hi = b in (_TECH, _ONC)
        r = FBR.loc[b].values
        ax.plot(x, r, color=col, lw=lw[0] if hi else lw[1], zorder=3 if hi else 2)
        ax.scatter(x, r, s=ms, color=col, edgecolors="white", linewidths=1.1, zorder=4 if hi else 2.5)
        for xi, ri in zip(x, r):
            ax.text(xi, ri, str(ri), ha="center", va="center", fontsize=num, color=mv.text_on(col), fontweight=700,
                    zorder=5)
        kw = dict(va="center", fontsize=size, **lab_style(col, hi))
        ax.text(-dx, r[0], BU_SHORT[b], ha="right", **kw)
        ax.text(x[-1] + dx, r[-1], BU_SHORT[b], ha="left", **kw)
    if header:
        for xi, f in zip(x, FY):
            ax.text(xi, 0.15, f, ha="center", va="center", fontsize=size, fontweight=700, color=C.text)
    ax.set_ylim(_nb + 0.55, -0.35)
    ax.set_xlim(-1.75, len(FY) - 1 + 1.75)
    ax.axis("off")


def value_slope(ax, a, b, names, cols, *, hot=(), size=MINI - 1.5, ylim=(10, 45), fmt="{:.0f}%", label=None,
                headers=("FY22", "FY26"), gap=None, dx=0.06, names_left=False, lw=(2, 1.2)):
    label = label or {}
    lo, hi = ylim
    gap = gap or (hi - lo) * 0.085
    ya, yb = spread(a, gap, lo, hi), spread(b, gap, lo, hi)
    for i in sorted(range(len(names)), key=lambda i: cols[i] != C.context):
        c = cols[i]
        h = c != C.context
        ax.plot([0, 1], [a[i], b[i]], color=c, lw=lw[0] if h else lw[1], zorder=3 if h else 2, solid_capstyle="round")
        ax.scatter([0, 1], [a[i], b[i]], s=16, color=c, zorder=4 if h else 2, lw=0)
        kw = dict(va="center", fontsize=size, **lab_style(c, h))
        nm = label.get(names[i], names[i])
        ax.text(-dx, ya[i], f"{nm}  {fmt.format(a[i])}" if names_left else fmt.format(a[i]), ha="right", **kw)
        ax.text(1 + dx, yb[i], f"{fmt.format(b[i])}  {nm}", ha="left", **kw)
    if headers:
        for x, hd in zip((0, 1), headers):
            ax.text(x, hi + (hi - lo) * 0.1, hd, ha="center", va="bottom", fontsize=size, fontweight=700, color=C.text)
    ax.set_ylim(lo - (hi - lo) * 0.04, hi + (hi - lo) * 0.2)
    ax.axis("off")


@exhibit
def rk_var_value():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0.02, 1, 0.96])
    names = list(FBP.index)
    cols = [C.focus if b == _TECH else C.negative if b == _ONC else C.context for b in names]
    value_slope(ax, FBP[FY[0]].values, FBP[FY[-1]].values, names, cols, label=BU_SHORT, ylim=(12, 42),
                headers=(FY[0], FY[-1]))
    ax.set_xlim(-0.75, 2.05)
    return fig, "Value slope of internal fill rate by business unit, FY22 vs. FY26: Technology 14% to 41%, Oncology 24% to 21%."


@exhibit
def rk_var_topn():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0.02, 1, 0.96])
    t = MINI - 2
    stub = _top + 0.95
    for r in SK.sort_values("skill").itertuples():
        if r.rank_2023 > _top and r.rank_2026 > _top:
            continue
        hot = r.skill in RISERS
        c = C.focus if hot else C.context
        y0 = r.rank_2023 if r.rank_2023 <= _top else stub
        y1 = r.rank_2026 if r.rank_2026 <= _top else stub
        x0, x1 = (0.3 if r.rank_2023 > _top else 0), (0.7 if r.rank_2026 > _top else 1)
        ax.plot([x0, x1], [y0, y1], color=c, lw=2 if hot else 1.2, zorder=3 if hot else 2,
                ls=(0, (2, 1.6)) if (r.rank_2023 > _top or r.rank_2026 > _top) else "-")
        kw = dict(va="center", fontsize=t, **lab_style(c, hot))
        nm = SK_SHORT[r.skill]
        if r.rank_2023 <= _top:
            ax.scatter(0, y0, s=16, color=c, zorder=4, lw=0)
            ax.text(-0.06, y0, f"{nm}  {r.rank_2023}", ha="right", **kw)
        else:
            ax.text(x0 - 0.02, stub + 0.05, f"from {r.rank_2023}", ha="right", va="center", fontsize=t - 0.5,
                    color=C.text_muted)
        if r.rank_2026 <= _top:
            ax.scatter(1, y1, s=16, color=c, zorder=4, lw=0)
            ax.text(1.06, y1, f"{r.rank_2026}  {nm}" + ("  new" if r.rank_2023 > _top else ""), ha="left", **kw)
        else:
            ax.text(x1 + 0.02, stub + 0.05, f"to {r.rank_2026}", ha="left", va="center", fontsize=t - 0.5,
                    color=C.text_muted)
    ax.axhline(_top + 0.5, xmin=0.3, xmax=0.7, color=C.grid, lw=0.8)
    for x, hd in zip((0, 1), ("2023", "2026")):
        ax.text(x, 0.2, hd, ha="center", va="center", fontsize=t, fontweight=700, color=C.text)
    ax.set_ylim(stub + 0.5, -0.3)
    ax.set_xlim(-1.05, 2.05)
    ax.axis("off")
    return fig, "Top-6 slope chart of skills: gen AI enters the top 6 in 2026; clinical documentation drops out."


@exhibit
def rk_var_list():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    t = MINI - 1.5
    d = SK.sort_values("rank_2026")
    n = len(d)
    ax.text(0.04, 0, "2026", fontsize=t - 0.5, color=C.text_muted, va="center", ha="left")
    ax.text(0.97, 0, "vs. 2023", fontsize=t - 0.5, color=C.text_muted, va="center", ha="right")
    for i, r in enumerate(d.itertuples(), start=1):
        hot = r.skill in RISERS
        kw = dict(va="center", fontsize=t, color=C.headline if hot else C.text, fontweight=600 if hot else 400)
        ax.text(0.09, i, str(r.rank_2026), ha="right", **kw)
        ax.text(0.15, i, r.skill, ha="left", **kw)
        mv_ = int(r.move)
        if mv_:
            up = mv_ > 0
            ax.scatter(0.82, i, marker="^" if up else "v", s=22, lw=0,
                       color=(C.focus if hot else C.context) if up else C.context, zorder=3)
            ax.text(0.97, i, mv.signed(mv_), ha="right", **kw)
        else:
            ax.text(0.97, i, "–", ha="right", **kw)
        ax.axhline(i + 0.5, color=C.grid, lw=0.6)
    ax.axhline(0.5, color=C.axis, lw=0.7)
    ax.set_xlim(0, 1)
    ax.set_ylim(n + 0.6, -0.5)
    ax.axis("off")
    return fig, "A ranked list of nine skills with the change in rank since 2023 and an up or down triangle."


# --- slope / bump best practice minis
_S6 = SK[SK.rank_2023 <= 6].copy()
_S6["r26"] = _S6.rank_2026.rank(method="first").astype(int)                   # re-ranked within these six
_TINY_SK = {"Inventory management": "Inventory", "Customer service": "Customer", "Regulatory compliance": "Regulatory",
            "Data analysis": "Data", "Automation / robotics": "Automation", "Clinical documentation": "Clinical"}


def _slope_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0.02, 1, 0.96])
    t = MINI - 3
    names = list(_S6.skill)
    r0, r1 = list(_S6.rank_2023), list(_S6.r26)
    grey = [C.focus if s == "Data analysis" else C.context for s in names]
    kw = dict(size=t, lw=(1.8, 1.1), dot=10, nums=False, dx=0.07, label=_TINY_SK)
    if kind == "hl_avoid":
        rank_slope(ax, names, r0, r1, ANTI["rainbow"][:6], hot=set(names), **kw)
    elif kind == "hl_fix":
        rank_slope(ax, names, r0, r1, grey, hot={"Data analysis"}, **kw)
    elif kind == "label_avoid":
        cols = ANTI["rainbow"][:6]
        for i, s in enumerate(names):
            ax.plot([0, 1], [r0[i], r1[i]], color=cols[i], lw=1.4)
        ax.legend([Line2D([], [], color=c, lw=1.4) for c in cols],
                  [_TINY_SK[s] for s in names], fontsize=t - 1, loc="center left", bbox_to_anchor=(1.0, 0.5),
                  frameon=False, handlelength=1.2, labelspacing=0.3)
        ax.set_ylim(6.6, 0.4)
        ax.set_xlim(-0.15, 1.15)
        ax.set_position([0.08, 0.06, 0.5, 0.86])
        for x, hd in zip((0, 1), ("2023", "2026")):
            ax.text(x, 0.45, hd, ha="center", va="bottom", fontsize=t, fontweight=700, color=C.text)
        ax.axis("off")
        return fig
    elif kind == "label_fix":
        rank_slope(ax, names, r0, r1, grey, hot={"Data analysis"}, **kw)
    elif kind == "top_avoid":
        ax.set_position([0.13, 0.12, 0.8, 0.8])
        for i, s in enumerate(names):
            ax.plot([0, 1], [r0[i], r1[i]], color=grey[i], lw=1.8 if s == "Data analysis" else 1.1, marker="o", ms=3)
        ax.set_ylim(0.5, 6.5)
        ax.set_yticks(range(1, 7))
        ax.set_xticks([0, 1], ["2023", "2026"])
        ax.grid(axis="y", color=C.grid, lw=0.6)
        ax.tick_params(labelsize=t, length=0, colors=C.text_muted)
        ax.set_xlim(-0.25, 1.25)
        _plain(ax, left=True, bottom=True)
        return fig
    elif kind == "top_fix":
        rank_slope(ax, names, r0, r1, grey, hot={"Data analysis"}, **{**kw, "nums": True})
    elif kind in ("gap_avoid", "gap_fix"):
        bus = list(FBP.index)
        cols = [C.focus if b == _TECH else C.context for b in bus]
        if kind == "gap_avoid":
            rank_slope(ax, bus, list(FBR[FY[-2]]), list(FBR[FY[-1]]), cols, hot={_TECH}, label=BU_SHORT,
                       headers=(FY[-2], FY[-1]), **{k: v for k, v in kw.items() if k != "label"})
        else:
            value_slope(ax, FBP[FY[-2]].values, FBP[FY[-1]].values, bus, cols, label=BU_SHORT, size=t,
                        ylim=(16, 42), headers=(FY[-2], FY[-1]), gap=2.8, dx=0.07, lw=(1.8, 1.1))
            ax.set_xlim(-0.6, 2.3)
            return fig
    ax.set_xlim(-0.95, 1.95)
    return fig


for _k, _alt in {"hl_avoid": "Six slope lines in six colors.",
                 "hl_fix": "Five grey lines and one blue line.",
                 "label_avoid": "Colored lines decoded through a legend at the side.",
                 "label_fix": "Names at both ends of each line.",
                 "top_avoid": "Ranks plotted on a normal axis, so rank 1 sits at the bottom.",
                 "top_fix": "Rank 1 at the top, rank numbers beside the names, no axis.",
                 "gap_avoid": "A rank slope where two business units swap places, which looks like an even trade.",
                 "gap_fix": "The same change in values: Technology jumps 12 points; the others barely move."}.items():
    EXHIBITS[f"rk_bp_{_k}"] = (lambda k=_k, a=_alt: (_slope_mini(k), a))


# ================================================================== DOT PLOT AND DUMBBELL
def dumbbell(ax, d, *, size=LABEL, tick=TICK, s=(46, 60), lab=True, gaps=True, names=True, conn=True,
             cols=("context", "auto"), xlim=(35, 160), xticks=(40, 80, 120, 160), short=None, label_size=None,
             key_short=False):
    """Market (grey) vs. McKesson (blue; orange when 5%+ below) per row, top row first."""
    y = np.arange(len(d))
    lag = d.gap_pct <= -5
    for i, r in enumerate(d.itertuples()):
        if conn:
            ax.plot([r.market_median_k, r.internal_median_k], [i, i], color=C.context_light, lw=3.2,
                    solid_capstyle="round", zorder=1)
        c0 = getattr(C, cols[0]) if cols[0] in ("context", "focus") else cols[0]
        c1 = (C.negative if lag.iloc[i] else C.focus) if cols[1] == "auto" else cols[1]
        ax.scatter(r.market_median_k, i, s=s[0], color=c0, zorder=2, lw=0)
        ax.scatter(r.internal_median_k, i, s=s[1], color=c1, zorder=3, lw=0)
        if gaps:
            ax.text(max(r.market_median_k, r.internal_median_k) + (xlim[1] - xlim[0]) * 0.03, i,
                    mv.signed(r.gap_pct, 1, "%"), va="center", fontsize=label_size or size,
                    color=C.negative_text if lag.iloc[i] else C.text, fontweight=700 if lag.iloc[i] else 400)
    if lab:                                                   # name every dot type once, in a top-left key
        fig = ax.figure
        r = fig.canvas.get_renderer()
        to_pt = 72 / fig.dpi
        items = [("McKesson", C.focus, C.focus, 600),
                 ("5%+ below" if key_short else "McKesson, 5%+ below market", C.negative, C.negative_text, 600),
                 ("Market", c0, C.text_muted, 400)]
        fs = size - 0.5
        dot_r = (s[1] * 0.8) ** 0.5 / 2                         # marker radius in points
        x = dot_r
        for name, dot, txt, w in items:                         # laid out in points, so the layout can't shift it
            ax.scatter([0], [1.035], s=s[1] * 0.8, color=dot, transform=ax.transAxes + mpl.transforms.ScaledTranslation(
                x / 72, 0, fig.dpi_scale_trans), clip_on=False, lw=0)
            t = ax.annotate(name, (0, 1.035), xycoords="axes fraction", xytext=(x + dot_r + 3, 0),
                            textcoords="offset points", fontsize=fs, color=txt, fontweight=w, va="center")
            x += dot_r + 3 + t.get_window_extent(r).width * to_pt + fs * 1.1 + dot_r
    if names:
        ax.set_yticks(y, [short.get(r, r) for r in d.role] if short else d.role)
        for t, hi in zip(ax.get_yticklabels(), lag):
            t.set_fontsize(tick)
            if hi:
                t.set_fontweight(600)
                t.set_color(C.headline)
    else:
        ax.set_yticks([])
    ax.set_ylim(len(d) - 0.5, -0.9)
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks, [f"${v}K" for v in xticks])
    ax.grid(axis="x", color=C.grid, lw=0.75, zorder=0)
    ax.tick_params(labelsize=tick - 1, length=0)
    ax.tick_params(axis="x", colors=C.text_muted)
    _plain(ax)
    return lag


@exhibit
def rk_db_anatomy():
    fig = fig_px(640, 320)
    ax = fig.add_subplot()
    dumbbell(ax, PAY)
    ds = PAY.index[PAY.role == "Data Scientist"][0]
    ph = PAY.index[PAY.role == "Pharmacist"][0]
    pt = PAY.index[PAY.role == "Pharmacy Technician"][0]
    r = PAY.loc[ds]
    marker(ax, (r.internal_median_k, ds), 3, offset=(0, -14))
    rp = PAY.loc[pt]
    marker(ax, (rp.internal_median_k, pt), 4, offset=(-15, 0))
    rph = PAY.loc[ph]
    marker(ax, ((rph.internal_median_k + rph.market_median_k) / 2, ph), 5, offset=(0, 13))
    marker(ax, (0, 1.035), 6, offset=(-14, 0), coords="axes fraction")
    marker(ax, (rp.market_median_k, pt), 7, offset=(70, 0))
    marker(ax, (80, len(PAY) - 1.5), 8)
    return fig, (TEXT["rk_db_headline"] + ". " + "; ".join(f"{r.role} {mv.signed(r.gap_pct, 1, '%')}"
                                                         for r in PAY[LAG].itertuples()) + ".")


@exhibit
def rk_dot_var_bench():
    d = SC.sort_values("engagement_index")
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    y = np.arange(len(d))
    hot = d.job_family.isin(SC_FOCUS)
    avg = _w("engagement_index")
    ax.axvline(avg, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=1)
    ax.text(avg, len(d) - 0.35, f"All {len(d)} families {avg:.0f}", ha="center", va="bottom", fontsize=MINI - 2,
            color=C.annotation, bbox=dict(fc="white", ec="none", pad=1))
    ax.scatter(d.engagement_index, y, s=34, color=[C.focus if h else C.context for h in hot], zorder=3, lw=0)
    for yy, (v, h) in enumerate(zip(d.engagement_index, hot)):
        ax.text(v + 0.7, yy, f"{v}", va="center", fontsize=MINI - 2, color=C.headline if h else C.text,
                fontweight=700 if h else 400)
    ax.set_yticks(y, [SHORT[f] for f in d.job_family])
    for t, h in zip(ax.get_yticklabels(), hot):
        t.set_fontsize(MINI - 1.5)
        if h:
            t.set_fontweight(600)
            t.set_color(C.headline)
    ax.set_xlim(60, 80)
    ax.set_xticks([60, 70, 80])
    ax.set_ylim(-0.6, len(d) + 0.3)
    ax.grid(axis="x", color=C.grid, lw=0.6, zorder=0)
    ax.tick_params(axis="x", labelsize=MINI - 2, length=0, colors=C.text_muted)
    ax.tick_params(axis="y", length=0)
    _plain(ax)
    return fig, f"Dot plot of engagement index by job family on a 60–80 scale; the two lowest are in blue, below the average of {avg:.0f}."


@exhibit
def rk_dot_var_arrow():
    d = FL.sort_values("days_to_fill_fy26").reset_index()
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    focus = "Pharmacy Technician"
    for i, r in enumerate(d.itertuples()):
        hot = r.job_family == focus
        c = C.focus if hot else C.context
        ax.scatter(r.days_to_fill_fy25, i, s=14, color=C.context_light if not hot else C.context, zorder=2, lw=0)
        ax.annotate("", xy=(r.days_to_fill_fy26, i), xytext=(r.days_to_fill_fy25, i),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.8 if hot else 1.1, mutation_scale=7,
                                    shrinkA=0, shrinkB=0), zorder=3)
        dd = r.days_to_fill_fy26 - r.days_to_fill_fy25
        ax.text(max(r.days_to_fill_fy25, r.days_to_fill_fy26) + 2, i, mv.signed(dd), va="center",
                fontsize=MINI - 2, color=C.headline if hot else C.text, fontweight=700 if hot else 400)
    ax.set_yticks(range(len(d)), [SHORT[f] for f in d.job_family])
    for t in ax.get_yticklabels():
        t.set_fontsize(MINI - 1.5)
        if t.get_text() == SHORT[focus]:
            t.set_fontweight(600)
            t.set_color(C.headline)
    ax.set_xlim(15, 85)
    ax.set_xticks([20, 40, 60, 80])
    ax.set_ylim(-0.6, len(d) - 0.4)
    ax.grid(axis="x", color=C.grid, lw=0.6, zorder=0)
    ax.tick_params(axis="x", labelsize=MINI - 2, length=0, colors=C.text_muted)
    ax.tick_params(axis="y", length=0)
    _plain(ax)
    TEXT["rk_pt_days"] = str(int(FL.loc[focus, "days_to_fill_fy26"] - FL.loc[focus, "days_to_fill_fy25"]))
    return fig, "Arrows from FY25 to FY26 median days to fill by job family; Pharmacy Technician rises 11 days."


@exhibit
def rk_dot_var_lollipop():
    e = _csv("engagement_vs_benchmark")
    d = e[e.business_unit == _ONC].sort_values("delta_vs_benchmark_pts", ascending=False).reset_index(drop=True)
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    for i, r in enumerate(d.itertuples()):
        v = r.delta_vs_benchmark_pts
        c = C.negative if v < 0 else C.focus
        ax.plot([0, v], [i, i], color=C.context_light, lw=1.6, zorder=1)
        ax.scatter(v, i, s=30, color=c, zorder=3, lw=0)
        ax.text(v + (0.8 if v >= 0 else -0.8), i, mv.signed(v), va="center", ha="left" if v >= 0 else "right",
                fontsize=MINI - 2, color=C.negative_text if v < 0 else C.text, fontweight=600 if v == d.delta_vs_benchmark_pts.min() else 400)
        ax.text(7.2, i, r.driver, va="center", ha="left", fontsize=MINI - 1.5, color=C.text)
    ax.axvline(0, color=C.axis, lw=0.8)
    ax.text(0, -0.85, "Benchmark", ha="center", va="bottom", fontsize=MINI - 2, color=C.text_muted,
            bbox=dict(fc="white", ec="none", pad=1), zorder=4)
    ax.set_xlim(-14, 15.5)
    ax.set_ylim(len(d) - 0.4, -1.1)
    ax.axis("off")
    TEXT["rk_onc_workload"] = mv.signed(int(d.delta_vs_benchmark_pts.min()))
    return fig, "Dots on stems from a zero benchmark: Oncology's engagement drivers, workload 11 points below in orange."


@exhibit
def rk_dot_var_panels():
    d = SC.sort_values("vol_attrition_pct")
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    a1 = fig.add_axes([0.36, 0.1, 0.3, 0.76])
    a2 = fig.add_axes([0.69, 0.1, 0.3, 0.76], sharey=a1)
    y = np.arange(len(d))
    hot = d.job_family.isin(SC_FOCUS)
    cols = [C.focus if h else C.context for h in hot]
    for ax, col, lim, ticks, title in ((a1, "vol_attrition_pct", (0, 30), [0, 10, 20], "Attrition (%)"),
                                       (a2, "engagement_index", (60, 80), [65, 75], "Engagement")):
        for yy in y:
            ax.axhline(yy, color=C.grid, lw=0.5, zorder=0)
        ax.scatter(d[col], y, s=24, color=cols, zorder=3, lw=0)
        ax.set_xlim(*lim)
        ax.set_xticks(ticks)
        ax.tick_params(axis="x", labelsize=MINI - 2.5, length=0, colors=C.text_muted)
        ax.tick_params(axis="y", length=0, labelleft=False)
        ax.set_title(title, fontsize=MINI - 2, color=C.text, loc="left", pad=3, fontweight=600)
        _plain(ax)
    a1.set_ylim(-0.6, len(d) - 0.4)
    for yy, (f, h) in enumerate(zip(d.job_family, hot)):
        fig.text(0.34, a1.transData.transform((0, yy))[1] / fig.bbox.height, SHORT[f], ha="right", va="center",
                 fontsize=MINI - 2, color=C.headline if h else C.text, fontweight=600 if h else 400)
    a1.set_ylim(-0.6, len(d) - 0.4)
    return fig, "Two dot panels sharing one row order: attrition and engagement by job family; the two frontline families in blue."


# --- dot plot best practice minis
def _dot_mini(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    t = MINI - 2.5
    short = {"RN, Specialty": "RN, Specialty", "Pharmacy Technician": "Pharm. Tech", "Pharmacist": "Pharmacist",
             "Software Engineer": "Software Eng.", "Account Executive": "Account Exec.",
             "Customer Care Rep": "Care Rep", "Data Scientist": "Data Scientist",
             "Supply Chain Planner": "SC Planner"}
    d = PAY.head(6)
    kw = dict(size=t, tick=t, s=(16, 22), short=short, label_size=t)
    if kind in ("zero_avoid", "zero_fix"):
        e = SC.sort_values("engagement_index").tail(6)
        y = np.arange(len(e))
        labels = [SHORT[f] for f in e.job_family]
        if kind == "zero_avoid":
            ax.barh(y, e.engagement_index, color=C.focus, height=BAND)
            ax.set_xlim(70, 78)
            ax.set_xticks([70, 74, 78])
        else:
            ax.hlines(y, 60, e.engagement_index, color=C.grid, lw=1)
            ax.scatter(e.engagement_index, y, s=20, color=C.focus, zorder=3, lw=0)
            ax.set_xlim(60, 80)
            ax.set_xticks([60, 70, 80])
        ax.set_yticks(y, labels)
        ax.tick_params(labelsize=t, length=0)
        ax.tick_params(axis="x", colors=C.text_muted)
        _plain(ax, left=kind == "zero_avoid")
    elif kind == "connect_avoid":
        dumbbell(ax, d, conn=False, lab=False, gaps=False, **kw)
        ax.legend(handles=[Line2D([], [], ls="", marker="o", ms=3.5, color=c)
                           for c in (C.context, C.focus)], labels=["Market", "McKesson"], fontsize=t - 0.5,
                  loc="lower right", frameon=True, handletextpad=0.2, borderpad=0.3)
    elif kind == "connect_fix":
        dumbbell(ax, d, gaps=False, key_short=True, **kw)
    elif kind == "color_avoid":
        dumbbell(ax, d, cols=(mv.CATEGORICAL[3], mv.CATEGORICAL[0]), lab=False, gaps=False, **kw)
    elif kind == "color_fix":
        dumbbell(ax, d, lab=False, gaps=False, **kw)
    elif kind == "sort_avoid":
        dumbbell(ax, PAY.sort_values("role").head(6).reset_index(drop=True), lab=False, gaps=False, **kw)
    elif kind == "sort_fix":
        dumbbell(ax, d, lab=False, **kw)
        ax.set_xlim(35, 175)
    if kind not in ("zero_avoid", "zero_fix"):
        ax.set_xticks([50, 100, 150], ["$50K", "$100K", "$150K"])
        ax.tick_params(axis="x", labelsize=t - 0.5)
    return fig


for _k, _alt in {"zero_avoid": "Bars on an axis cut at 70, exaggerating small differences.",
                 "zero_fix": "A dot plot of the same scores on a 60–80 scale.",
                 "connect_avoid": "Two unconnected dot series decoded through a legend.",
                 "connect_fix": "A light connector per row and a small key naming each dot type once.",
                 "color_avoid": "Market and McKesson dots in two equally strong colors.",
                 "color_fix": "Market dots grey, McKesson dots blue, orange only where pay is 5% or more below.",
                 "sort_avoid": "Rows in alphabetical order.",
                 "sort_fix": "Rows sorted by the gap, with signed gap labels."}.items():
    EXHIBITS[f"rk_dbp_{_k}"] = (lambda k=_k, a=_alt: (_dot_mini(k), a))


# ================================================================== HEAT TABLE (HTML, uses .mck-table from mck-viz.css)
_RAMP = mv.SEQUENTIAL["blue"]                                     # 6 even 5-point classes: 0–5, 5–10 … 25+


def _cls(v):
    return _RAMP[min(int(v // 5), len(_RAMP) - 1)]


def _mk(n):
    return f'<span class="mk" style="margin-left:5px">{n}</span>'


def _heat_table() -> str:
    d = SC.sort_values("vol_attrition_pct", ascending=False).reset_index(drop=True)
    pad = "padding:5px 7px"
    bar_max = d.headcount.max()
    heads = [("Job family", "", ""), ("Headcount", "num", _mk(5)), ("Voluntary attrition (%)", "num", _mk(4)),
             ("Engagement index", "num", ""), ("Median days to fill", "num", _mk(7)),
             ("Change vs. FY25 (days)", "num", _mk(6))]
    th = "".join(f'<th scope="col"{f" class={c}" if c else ""} style="{pad}">{h}{m}</th>' for h, c, m in heads)
    rows = []
    for i, r in d.iterrows():
        hot = r.job_family in SC_FOCUS
        fill = _cls(r.vol_attrition_pct)
        dd = int(FL.loc[r.job_family, "days_to_fill_fy26"] - FL.loc[r.job_family, "days_to_fill_fy25"])
        assert FL.loc[r.job_family, "days_to_fill_fy26"] == r.median_days_to_fill
        dstyle = f";color:{C.negative_text}" if dd > 0 else ""          # a rise in days to fill is worse
        name = SHORT.get(r.job_family, r.job_family)
        rows.append(
            f'<tr{" class=is-focus" if hot else ""}><th scope="row" style="{pad};white-space:nowrap">{_html.escape(name)}'
            f'{_mk(3) if i == 0 else ""}</th>'
            f'<td class="num" style="{pad}">{r.headcount:,.0f}<span class="bars"><span class="bar" '
            f'style="width:{r.headcount / bar_max * 100:.0f}%"></span></span></td>'
            f'<td class="num" style="{pad};background:{fill};color:{mv.text_on(fill)}">{r.vol_attrition_pct:.1f}</td>'
            f'<td class="num" style="{pad}">{r.engagement_index:.0f}</td>'
            f'<td class="num" style="{pad}">{r.median_days_to_fill:.0f}</td>'
            f'<td class="num" style="{pad}{dstyle}">{mv.signed(dd)}</td></tr>')
    days25 = np.average([FL.loc[f, "days_to_fill_fy25"] for f in d.job_family], weights=d.headcount)
    tot_dd = _w("median_days_to_fill") - days25
    rows.append(f'<tr class="is-total"><th scope="row" style="{pad};white-space:nowrap">All {len(d)} job families{_mk(8)}</th>'
                f'<td class="num" style="{pad}">{d.headcount.sum():,.0f}<span class="bars"></span></td>'
                f'<td class="num" style="{pad}">{_w("vol_attrition_pct"):.1f}</td>'
                f'<td class="num" style="{pad}">{_w("engagement_index"):.0f}</td>'
                f'<td class="num" style="{pad}">{_w("median_days_to_fill"):.0f}</td>'
                f'<td class="num" style="{pad}">{mv.signed(tot_dd)}</td></tr>')
    TEXT["rk_total_attr"] = f"{_w('vol_attrition_pct'):.1f}"
    return (f'<div class="ex-wrap"><table class="mck-table" style="font-size:12.5px;margin:2px 0 0">'
            f"<thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")


HTML["rk_heat_table"] = _heat_table()
HTML["rk_heat_key"] = ("".join(f'<span style="display:inline-block;width:14px;height:9px;background:{c};'
                               f'vertical-align:-1px"></span>' for c in _RAMP))


# --- heat table best practice minis (drawn tables, 200 x 140)
_HT = SC.sort_values("vol_attrition_pct", ascending=False).head(5).reset_index(drop=True)
_TINYF = {"Pharmacy Technician": "Pharm. Tech", "Distribution Center Associate": "DC Associate",
          "Customer Care": "Customer Care", "Specialty Nursing": "Spec. Nursing", "Data & Analytics": "Data & Analytics"}


def _mini_table(ax, *, shade="one", rules="hair", total=None, bold=True, t=MINI - 2.5):
    cols = [("vol_attrition_pct", "Attrition\n(%)", "{:.1f}"), ("engagement_index", "Engage-\nment", "{:.0f}"),
            ("median_days_to_fill", "Days to\nfill", "{:.0f}")]
    xs = [0.6, 0.8, 0.99]
    n = len(_HT)
    nrows = n + (1 if total else 0)
    ax.set_xlim(0, 1)
    ax.set_ylim(nrows + 0.1, -1.55)
    ax.axis("off")
    for x, (_, h, _) in zip(xs, cols):
        ax.text(x, -0.62, h, ha="right", va="bottom", fontsize=t, fontweight=700, color=C.headline, linespacing=1.05)
    ramps = {"vol_attrition_pct": mv.SEQUENTIAL["blue"], "engagement_index": mv.SEQUENTIAL["teal"],
             "median_days_to_fill": mv.SEQUENTIAL["orange"]}
    for i, r in _HT.iterrows():
        hot = bold and r.job_family in SC_FOCUS
        if rules == "box" and i % 2 == 1:
            ax.add_patch(Rectangle((0, i - 0.5), 1, 1, color=C.context_light, lw=0, zorder=0))
        tc, fw = (C.headline, 700) if hot else (C.text, 400)
        ax.text(0.01, i, _TINYF[r.job_family], va="center", fontsize=t, color=tc, fontweight=fw)
        for x, (k, _, fmt) in zip(xs, cols):
            v, col = r[k], tc
            fill = None
            if shade == "all" or (shade in ("one", "rag") and k == "vol_attrition_pct"):
                if shade == "rag":
                    fill = ANTI["red"] if v >= 20 else (ANTI["rainbow"][1] if v >= 15 else ANTI["green"])
                    col = "#FFFFFF"
                else:
                    ramp = ramps[k]
                    lo, hi = _HT[k].min(), _HT[k].max()
                    fill = _cls(v) if k == "vol_attrition_pct" else ramp[1 + int(round((v - lo) / (hi - lo) * 4))]
                    col = mv.text_on(fill)
            if fill:
                ax.add_patch(Rectangle((x - 0.165, i - 0.5), 0.175, 1, color=fill, lw=0, zorder=1))
            ax.text(x, i, fmt.format(v), ha="right", va="center", fontsize=t, color=col, fontweight=fw, zorder=2)
        if rules == "hair":
            ax.plot([0, 1], [i + 0.5, i + 0.5], color=C.grid, lw=0.6)
    if total:
        lab, val = total
        ax.plot([0, 1], [n - 0.5, n - 0.5], color=C.total, lw=1.1)
        ax.text(0.01, n, lab, va="center", fontsize=t, color=C.headline, fontweight=700)
        ax.text(xs[0], n, val, ha="right", va="center", fontsize=t, color=C.headline, fontweight=700)
    if rules == "box":
        for yy in np.arange(-0.5, nrows + 0.5):
            ax.plot([0, 1], [yy, yy], color=C.text, lw=0.6)
        for xx in (0, 0.445, 0.635, 0.825, 1):
            ax.plot([xx, xx], [-1.72, nrows - 0.5], color=C.text, lw=0.6)
        ax.plot([0, 1], [-1.72, -1.72], color=C.text, lw=0.6)
        ax.set_ylim(nrows + 0.1, -1.78)
    else:
        ax.plot([0, 1], [-0.52, -0.52], color=C.axis, lw=0.7)


def _heat_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    if kind == "shade_avoid":
        _mini_table(ax, shade="all", bold=False)
    elif kind == "shade_fix":
        _mini_table(ax)
    elif kind == "rag_avoid":
        _mini_table(ax, shade="rag", bold=False)
    elif kind == "rag_fix":
        _mini_table(ax)
    elif kind == "rules_avoid":
        _mini_table(ax, shade="none", rules="box", bold=False)
    elif kind == "rules_fix":
        _mini_table(ax, shade="none")
    elif kind == "total_avoid":
        _mini_table(ax, shade="none", total=("Average", f"{_HT.vol_attrition_pct.mean():.1f}"))
    elif kind == "total_fix":
        wavg = np.average(_HT.vol_attrition_pct, weights=_HT.headcount)
        _mini_table(ax, shade="none", total=(f"All {len(_HT)} families", f"{wavg:.1f}"))
    return fig


TEXT["rk_avg_simple"] = f"{_HT.vol_attrition_pct.mean():.1f}"
TEXT["rk_avg_weighted"] = f"{np.average(_HT.vol_attrition_pct, weights=_HT.headcount):.1f}"

for _k, _alt in {"shade_avoid": "Every column shaded on its own color scale.",
                 "shade_fix": "Only the attrition column shaded, the two focus rows bold.",
                 "rag_avoid": "Attrition cells in red, amber and green.",
                 "rag_fix": "Attrition cells in blue classes, light to dark.",
                 "rules_avoid": "A cell grid with boxes and zebra stripes.",
                 "rules_fix": "A rule under the header and hairlines between rows only.",
                 "total_avoid": "A total row that averages the five rates.",
                 "total_fix": "A total row weighted by headcount."}.items():
    EXHIBITS[f"rk_hbp_{_k}"] = (lambda k=_k, a=_alt: (_heat_mini(k), a))
