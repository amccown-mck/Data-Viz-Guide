"""Correlation exhibits: scatter and bubble scatter, dual axis (and what to use instead), heatmaps. Registered on import."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.patches import Rectangle

import mckviz as mv
import exhibits as _ex
from exhibits import (ANNOT, ANTI, ENT, LABEL, MINI, SHORT, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px,
                      marker, ph)

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
GRID_LW = 0.75


def word(n: int, cap: bool = False) -> str:
    w = WORDS.get(n, str(n))
    return w.capitalize() if cap else w


# ------------------------------------------------------------------ helpers
def sc_axes(ax, xticks, yticks, xfmt="{:.0f}", yfmt="{:.0f}", size=TICK, grid=True):
    """Light scaffolding for a scatter: thin grid both ways, a baseline, muted ticks, no tick marks."""
    ax.set_xticks(xticks, [xfmt.format(t) for t in xticks])
    ax.set_yticks(yticks, [yfmt.format(t) for t in yticks])
    if grid:
        ax.grid(axis="both", color=C.grid, lw=GRID_LW, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=size - 1, length=0, colors=C.text_muted)
    _plain(ax, bottom=True)


def ytitle(ax, text, size=TICK, y=1.03):
    """Y-axis title horizontal at the top-left, never rotated."""
    ax.text(0, y, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=size - 1, color=C.text)


def xtitle(ax, text, size=TICK):
    ax.set_xlabel(text, fontsize=size - 1, color=C.text, labelpad=4)


def heat(ax, m, colors_of, *, values=True, fmt=mv.signed, size=MINI, gap=0.06, bold_cols=(), bold_rows=(),
         row_labels=True, col_labels=True, tick=None, wrap=True, na_text="n<10"):
    """Draw a matrix as square-ish cells with white gutters. m: DataFrame; colors_of(value) -> hex (None = n<10)."""
    tick = tick or size
    nr, nc = m.shape
    for i, (row, vals) in enumerate(m.iterrows()):
        for j, v in enumerate(vals):
            col = colors_of(v)
            y = nr - 1 - i
            ax.add_patch(Rectangle((j + gap / 2, y + gap / 2), 1 - gap, 1 - gap, color=col or C.context_light, lw=0))
            if values:
                if col is None:
                    ax.text(j + 0.5, y + 0.5, na_text, ha="center", va="center", fontsize=size - 1, color=C.text_muted)
                elif v == v:
                    bold = m.columns[j] in bold_cols or row in bold_rows
                    ax.text(j + 0.5, y + 0.48, fmt(v), ha="center", va="center", fontsize=size,
                            color=mv.text_on(col), fontweight=700 if bold else 500)
    if row_labels:
        for i, row in enumerate(m.index):
            hot = row in bold_rows
            ax.text(-0.12, nr - 1 - i + 0.5, row, ha="right", va="center", fontsize=tick,
                    color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    if col_labels:
        for j, c in enumerate(m.columns):
            hot = c in bold_cols
            lab = c.replace(" ", "\n", 1) if wrap and " " in c and len(c) > 8 else c
            ax.text(j + 0.5, nr + 0.12, lab, ha="center", va="bottom", fontsize=tick, linespacing=1.1,
                    color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    ax.set_xlim(-0.02, nc + 0.02)
    ax.set_ylim(-0.02, nr + 0.02)
    ax.axis("off")


def stepped(bounds, ramp):
    """Value -> class color for even class breaks (len(bounds) == len(ramp) + 1)."""
    def f(v):
        if v != v:
            return None
        k = int(np.clip(np.searchsorted(bounds, v, side="right") - 1, 0, len(ramp) - 1))
        return ramp[k]
    return f


def key_strip(ax, x0, y0, w, h, ramp, labels=None, *, size=MINI, ends=None, gap=0.0, tick_at="edges", bounds=None):
    """Stepped color key drawn in data coordinates of ax: equal swatches, labels under the class breaks."""
    n = len(ramp)
    sw = w / n
    for k, c in enumerate(ramp):
        ax.add_patch(Rectangle((x0 + k * sw + gap / 2, y0), sw - gap, h, color=c, lw=0, clip_on=False))
    if labels is not None:
        xs = ([x0 + k * sw for k in range(n + 1)] if tick_at == "edges" else [x0 + (k + 0.5) * sw for k in range(n)])
        for x, lab in zip(xs, labels):
            if lab != "":
                ax.text(x, y0 - h * 0.35, lab, ha="center", va="top", fontsize=size - 1, color=C.text_muted)
    if ends:
        lo, hi = ends
        ax.text(x0 - sw * 0.25, y0 + h / 2, lo, ha="right", va="center", fontsize=size - 1, color=C.negative_text)
        ax.text(x0 + w + sw * 0.25, y0 + h / 2, hi, ha="left", va="center", fontsize=size - 1, color=C.focus)


# ------------------------------------------------------------------ data
EXPO = _csv("automation_exposure").sort_values("headcount", ascending=False)       # big bubbles drawn first
EXPO_FOCUS = list(EXPO.sort_values("genai_exposure_pct", ascending=False).role[EXPO.genai_exposure_pct >= 50])
EXPO_AVG = float((EXPO.genai_exposure_pct * EXPO.headcount).sum() / EXPO.headcount.sum())
_f = EXPO[EXPO.role.isin(EXPO_FOCUS)]
EXPO_FOCUS_AVG = float((_f.genai_exposure_pct * _f.headcount).sum() / _f.headcount.sum())
ROLE_SHORT = {"Claims & Billing Specialist": "Claims & Billing", "Distribution Center Associate": "DC Associate",
              "Software Engineering": "Software Eng.", "Supply Chain Planning": "Supply Chain",
              "Finance Operations": "Finance Ops", "Pharmacy Technician": "Pharmacy Tech",
              "Specialty Nursing": "Specialty Nursing", "Data & Analytics": "Data & Analytics"}
TEXT["corr_sc_headline"] = (f"{word(len(EXPO_FOCUS), True)} support roles have half or more of their task hours exposed to "
                            f"gen AI, {EXPO_FOCUS_AVG / EXPO_AVG:.0f}× the {EXPO_AVG:.0f}% workforce average")
TEXT["corr_sc_subtitle"] = "Share of task hours exposed to gen AI vs. median base pay, by role, FY26; bubble area = headcount"
TEXT["corr_sc_avg"] = f"{EXPO_AVG:.0f}%"

SC = _csv("job_family_scorecard")
SC_R = float(np.corrcoef(SC.engagement_index, SC.vol_attrition_pct)[0, 1])
TEXT["corr_sc_r"] = mv.signed(SC_R, 2)
ENG_AVG = float(np.average(SC.engagement_index, weights=SC.headcount))      # headcount-weighted, like the scorecard total
_hr = SC[(SC.vol_attrition_pct > ENT) & (SC.engagement_index < ENG_AVG)]  # the quadrant the headline would name
TEXT["corr_sc_quadrant_n"] = word(len(_hr), True)

IDX = _csv("data_ai_index")
TEXT.update(corr_idx_post=str(IDX.external_postings_idx.iloc[-1]), corr_idx_int=str(IDX.internal_headcount_idx.iloc[-1]))
DUAL = _csv("dc_vacancy_overtime")
_pk = int(DUAL.vacancy_pct.idxmax())
TEXT.update(corr_dual_vac_peak=f"{DUAL.vacancy_pct.max():.1f}%", corr_dual_ot_peak=f"{DUAL.overtime_hrs_per_fte_wk.max():.1f}",
            corr_dual_peak_month=DUAL.month[_pk],
            corr_dual_vac_idx=f"{(DUAL.vacancy_pct[_pk] / DUAL.vacancy_pct[0] - 1) * 100:.0f}%",
            corr_dual_ot_idx=f"{(DUAL.overtime_hrs_per_fte_wk[_pk] / DUAL.overtime_hrs_per_fte_wk[0] - 1) * 100:.0f}%",
            corr_dual_one_in=f"{round(100 / DUAL.vacancy_pct.max()):.0f}")

ENG = _csv("engagement_vs_benchmark")
DRIVERS = ["Growth", "Manager support", "Recognition", "Workload", "Tools & tech", "Belonging", "Pay fairness"]
HM = ENG.pivot(index="business_unit", columns="driver", values="delta_vs_benchmark_pts")[DRIVERS]
HM = HM.loc[HM.mean(axis=1).sort_values(ascending=False).index]                  # ranked rows, not alphabetical
HM_FOCUS = "Workload"
_below = int((HM[HM_FOCUS] < 0).sum())
_worst = HM[HM_FOCUS].idxmin()
TEXT["corr_hm_headline"] = (f"Workload trails the benchmark in {word(_below)} of {word(len(HM))} business units, "
                            f"{_worst.split(' &')[0]} most of all")
TEXT["corr_hm_subtitle"] = "Engagement driver score vs. external healthcare benchmark, by business unit, 2026 (points)"
TEXT["corr_hm_worst"] = mv.signed(HM.loc[_worst, HM_FOCUS])
DIV_BOUNDS = np.arange(-10.5, 10.6, 3)                                            # 7 even 3-point classes, 0 in the middle
div_color = stepped(DIV_BOUNDS, mv.DIVERGING)
BU_SHORT = {"Oncology & Multispecialty": "Oncology", "U.S. Pharmaceutical": "U.S. Pharma"}

AQ = _csv("attrition_quarterly")
QS = list(dict.fromkeys(AQ.quarter))
AQP = AQ.pivot(index="job_family", columns="quarter", values="attrition_pct")[QS]
AQP = AQP.loc[AQP[QS[-1]].sort_values(ascending=False).index]
TEXT["corr_hm_seq_top"] = SHORT[AQP.idxmax().mode()[0]] if (AQP.idxmax() == AQP.idxmax().iloc[0]).all() else ""
RB = _csv("regretted_attrition_bu")
RBP = RB.pivot(index="business_unit", columns="quarter", values="regretted_attrition_pct")[QS[-4:]]
RBP = RBP.loc[RBP[QS[-1]].sort_values(ascending=False).index]
TEXT["corr_hm_table_top"] = f"{RBP.iloc[0, -1]:.1f}%"
MOB = _csv("mobility_flows")
_top = MOB.loc[MOB.moves.idxmax()]
TEXT["corr_hm_od_top"] = f"{_top.from_family} to {_top.to_family}, {_top.moves} moves"


# ================================================================== SCATTER / BUBBLE
def bubbles(ax, d, *, k, focus=(), colors=None, outline=True, big_first=True, alpha=0.9, z=3):
    d = d.sort_values("headcount", ascending=not big_first)
    cols = colors or [C.focus if r in focus else C.context for r in d.role]
    if colors is not None and not isinstance(colors, list):
        cols = [colors(r) for r in d.role]
    ax.scatter(d.median_pay_k, d.genai_exposure_pct, s=d.headcount * k, c=cols, alpha=alpha,
               edgecolors="white" if outline else "none", linewidths=1 if outline else 0, zorder=z)
    return d


@exhibit
def corr_sc_anatomy():
    fig = fig_px(640, 330)
    ax = fig.add_subplot()
    k = 46 ** 2 / EXPO.headcount.max()                                       # largest bubble ~46 px across; area ∝ value
    ax.axhspan(50, 72, color=C.surface_subtle, lw=0, zorder=0)
    ax.text(31, 70.5, "High exposure: 50%+ of task hours", ha="left", va="top", fontsize=ANNOT, fontweight=600,
            color=C.annotation, zorder=4)
    ax.axhline(EXPO_AVG, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=1)
    ax.text(151, EXPO_AVG + 1.2, f"Workforce average {EXPO_AVG:.0f}%", ha="right", va="bottom", fontsize=ANNOT,
            color=C.annotation, zorder=4)
    bubbles(ax, EXPO, k=k, focus=EXPO_FOCUS)
    place = {"Customer Care": ph((-1, 0), (1, -1.6)), "Claims & Billing Specialist": (1, 0), "Finance Operations": (1, 0),
             "HR Operations": (-1, -0.2)}
    for r in EXPO[EXPO.role.isin(EXPO_FOCUS)].itertuples():
        side, dy = place.get(r.role, (1, 0))
        pad = (r.headcount * k) ** 0.5 / 2 + 3
        ax.annotate(ROLE_SHORT.get(r.role, r.role), (r.median_pay_k, r.genai_exposure_pct), xytext=(side * pad, dy * 20),
                    textcoords="offset points", ha="left" if side > 0 else "right", va="center",
                    fontsize=ph(LABEL, LABEL - 2), fontweight=600, color=C.headline, path_effects=mv.halo(), zorder=5)
    keyv = [(1000, 121), (5000, 132), (10000, 146)]                            # size key on the same scale
    ax.text(116, 20, "Headcount", fontsize=TICK - 1.5, color=C.text_muted, va="bottom")
    for v, x in keyv:
        ax.scatter(x, 10, s=v * k, facecolors="none", edgecolors=C.text_muted, linewidths=0.8, zorder=2)
        ax.annotate(f"{v:,}", (x, 10), xytext=(0, -((v * k) ** 0.5 / 2 + 2)), textcoords="offset points", ha="center",
                    va="top", fontsize=TICK - 1.5, color=C.text_muted)
    ax.set_xlim(28, 152)
    ax.set_ylim(0, 72)
    sc_axes(ax, [40, 60, 80, 100, 120, 140], [0, 20, 40, 60], xfmt="${:.0f}K", yfmt="{:.0f}%")
    ytitle(ax, "Task hours exposed to gen AI")
    xtitle(ax, "Median base pay")
    marker(ax, (147, 61), 3)
    cc = EXPO[EXPO.role == "Finance Operations"].iloc[0]
    marker(ax, (cc.median_pay_k, cc.genai_exposure_pct), 4, offset=(0, -17))
    dc = EXPO[EXPO.role == "Distribution Center Associate"].iloc[0]
    marker(ax, (dc.median_pay_k, dc.genai_exposure_pct), 5, offset=(30, 6))
    marker(ax, (151, EXPO_AVG), 6, offset=(ph(-146, -270), 9))
    marker(ax, (146, 10), 7, offset=(0, 26))
    marker(ax, (0, 1.06), 8, coords="axes fraction", offset=(ph(160, 330), 0))
    return fig, (TEXT["corr_sc_headline"] + ". " + "; ".join(f"{ROLE_SHORT.get(r, r)} {v}%" for r, v in
                 EXPO.set_index("role").genai_exposure_pct[EXPO_FOCUS].items()) + ".")


@exhibit
def corr_sc_var_plain():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    d = SC
    focus = set(d.nlargest(2, "vol_attrition_pct").job_family)
    b, a = np.polyfit(d.engagement_index, d.vol_attrition_pct, 1)
    xs = np.array([64, 79])
    ax.plot(xs, a + b * xs, color=C.axis, lw=1, ls=(0, (3, 2)), zorder=1)
    ax.scatter(d.engagement_index, d.vol_attrition_pct, s=40, zorder=3,
               c=[C.focus if f in focus else C.context for f in d.job_family], edgecolors="white", linewidths=0.8)
    for r in d[d.job_family.isin(focus)].itertuples():
        ax.annotate(SHORT[r.job_family], (r.engagement_index, r.vol_attrition_pct), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=MINI - 1.5, fontweight=600, color=C.headline)
    ax.set_xlim(63, 80)
    ax.set_ylim(0, 32)
    sc_axes(ax, [65, 70, 75, 80], [0, 10, 20, 30], yfmt="{:.0f}%", size=MINI)
    ytitle(ax, "Voluntary attrition", size=MINI - 0.5)
    xtitle(ax, "Engagement index", size=MINI - 0.5)
    return fig, f"Plain scatter of eight job families: lower engagement goes with higher attrition (r = {TEXT['corr_sc_r']})."


@exhibit
def corr_sc_var_quadrant():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    d = SC
    hot = set(_hr.job_family)
    ax.add_patch(Rectangle((63, ENT), ENG_AVG - 63, 32 - ENT, color=C.surface_subtle, lw=0, zorder=0))
    ax.axhline(ENT, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
    ax.axvline(ENG_AVG, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
    ax.text(63.3, 31.5, "Low engagement,\nhigh attrition", ha="left", va="top", fontsize=MINI - 1.5, fontweight=600,
            color=C.annotation, linespacing=1.1)
    ax.text(79.8, ENT + 0.4, f"Enterprise {ENT:.1f}%", ha="right", va="bottom", fontsize=MINI - 2, color=C.annotation)
    ax.text(ENG_AVG + 0.2, 1.0, f"Average {ENG_AVG:.0f}", ha="left", va="bottom", fontsize=MINI - 2, color=C.annotation)
    ax.scatter(d.engagement_index, d.vol_attrition_pct, s=40, zorder=3, edgecolors="white", linewidths=0.8,
               c=[C.focus if f in hot else C.context for f in d.job_family])
    for r in d[d.job_family.isin(hot)].itertuples():
        left = r.engagement_index < ENG_AVG - 2.5                    # keep labels off the reference line
        ax.annotate(SHORT[r.job_family], (r.engagement_index, r.vol_attrition_pct), xytext=(-7 if left else 7, 0),
                    textcoords="offset points", ha="right" if left else "left", va="center", fontsize=MINI - 1.5,
                    fontweight=600, color=C.headline)
    ax.set_xlim(63, 80)
    ax.set_ylim(0, 32)
    sc_axes(ax, [65, 70, 75, 80], [0, 10, 20, 30], yfmt="{:.0f}%", size=MINI)
    ytitle(ax, "Voluntary attrition, FY26", size=MINI - 0.5)
    xtitle(ax, "Engagement index", size=MINI - 0.5)
    return fig, (f"Quadrant scatter of engagement vs. attrition: {TEXT['corr_sc_quadrant_n'].lower()} job families sit in "
                 "the low-engagement, high-attrition corner.")


@exhibit
def corr_sc_var_connected():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x, y = IDX.external_postings_idx.values, IDX.internal_headcount_idx.values
    ax.plot(x, y, color=C.focus, lw=1.6, zorder=2)
    ax.scatter(x[1:], y[1:], s=18, color=C.focus, zorder=3)
    ax.scatter(x[:1], y[:1], s=18, color=C.context, zorder=3)
    ax.annotate("", xy=(x[-1], y[-1]), xytext=(x[-2], y[-2]),
                arrowprops=dict(arrowstyle="-|>", color=C.focus, lw=1.6, mutation_scale=9, shrinkA=0, shrinkB=3))
    for i, (dx, ha) in {0: (6, "left"), 2: (0, "center"), len(x) - 1: (-6, "right")}.items():
        dx, dy = (-6, 0) if i == 2 else (dx, 4)
        ax.annotate(str(IDX.year[i]), (x[i], y[i]), xytext=(dx, dy), textcoords="offset points", ha="right" if i == 2 else ha,
                    va="center" if i == 2 else "bottom", fontsize=MINI - 1.5, color=C.headline if i else C.text_muted,
                    fontweight=600 if i == len(x) - 1 else 400)
    ax.set_xlim(90, 205)
    ax.set_ylim(95, 127)
    sc_axes(ax, [100, 150, 200], [100, 110, 120], size=MINI)
    ytitle(ax, "Our Data & AI headcount (2021 = 100)", size=MINI - 0.5)
    xtitle(ax, "Market Data & AI postings (2021 = 100)", size=MINI - 0.5)
    return fig, "Connected scatter, 2021 to 2026: market postings on X, our headcount on Y, joined in time order."


_GROUP = {"Customer Care": 1, "Claims & Billing Specialist": 1, "Finance Operations": 1, "HR Operations": 1,
          "Pharmacy Technician": 0, "Distribution Center Associate": 0, "Specialty Nursing": 0, "Supply Chain Planning": 0,
          "Software Engineering": 2, "Data & Analytics": 2, "Sales": 2, "Marketing": 2}
_GROUP_NAMES = ["Frontline operations", "Service and support", "Technology and commercial"]


@exhibit
def corr_sc_var_groups():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    pal = mv.categorical(3)
    k = 22 ** 2 / EXPO.headcount.max()
    bubbles(ax, EXPO, k=k, colors=lambda r: pal[_GROUP[r]])
    ax.set_xlim(28, 152)
    ax.set_ylim(0, 80)
    sc_axes(ax, [40, 80, 120], [0, 20, 40, 60], xfmt="${:.0f}K", yfmt="{:.0f}%", size=MINI)
    ax.set_ylim(0, 96)
    for i, (name, c) in enumerate(zip(_GROUP_NAMES, pal)):                     # key top-left, palette order
        y = 91 - i * 6.5
        ax.scatter(31.5, y, s=26, color=c, zorder=4)
        ax.text(34.5, y, name, va="center", fontsize=MINI - 2, color=C.text, zorder=4)
    xtitle(ax, "Median base pay", size=MINI - 0.5)
    return fig, "Bubble scatter colored by function group, three groups in blue, navy and light blue, with a key."


# --- scatter best practice minis (200 x 140)
def _sc_mini(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    t = MINI - 2.5
    k = 20 ** 2 / EXPO.headcount.max()
    if kind == "color_avoid":
        ramp = [C.focus_light, C.focus, C.accent]
        bubbles(ax, EXPO, k=k, colors=lambda r: ramp[min(2, int((EXPO.set_index("role").median_pay_k[r] - 30) // 37))])
    elif kind == "color_fix":
        bubbles(ax, EXPO, k=k, focus=EXPO_FOCUS)
    elif kind in ("trend_avoid", "trend_fix"):
        rng = np.random.default_rng(11)                      # schematic: four groups, each with its own slope
        slopes = [0.9, 0.6, 0.35, 0.15]
        for g, sl in enumerate(slopes):
            x = rng.uniform(0, 10, 9)
            y = 1 + sl * x + rng.normal(0, 0.45, 9) + g * 0.4
            if kind == "trend_avoid":
                col = [C.focus, C.accent, C.focus_light, mv.CATEGORICAL[3]][g]
                ax.scatter(x, y, s=12, color=col, zorder=3)
                ax.plot([0, 10], np.polyval(np.polyfit(x, y, 1), [0, 10]), color=col, lw=1.4)
            else:
                hot = g == 0
                ax.scatter(x, y, s=12, color=C.focus if hot else C.context_light, zorder=3 if hot else 2)
                if hot:
                    ax.plot([0, 10], np.polyval(np.polyfit(x, y, 1), [0, 10]), color=C.focus, lw=1.6)
        ax.set_xlim(-0.5, 10.5)
    elif kind in ("label_avoid", "label_fix"):
        bubbles(ax, EXPO, k=k, focus=EXPO_FOCUS if kind == "label_fix" else ())
        labs = EXPO if kind == "label_avoid" else EXPO[EXPO.role.isin(EXPO_FOCUS[:2])]
        for r in labs.itertuples():
            name = ROLE_SHORT.get(r.role, r.role) if kind == "label_fix" else r.role
            ax.annotate(name, (r.median_pay_k, r.genai_exposure_pct), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=t - (1 if kind == "label_avoid" else 0), color=C.headline,
                        fontweight=600 if kind == "label_fix" else 400, zorder=5)
    elif kind in ("overlap_avoid", "overlap_fix"):
        kk = 52 ** 2 / EXPO.headcount.max()
        fix = kind == "overlap_fix"
        bubbles(ax, EXPO, k=kk, focus=["Pharmacy Technician"], outline=fix, big_first=fix, alpha=1)
    if kind.startswith(("color", "label", "overlap")):
        ax.set_xlim(28, 152)
        ax.set_ylim(0, 72)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(axis="both", color=C.grid, lw=0.6)
    ax.set_axisbelow(True)
    _plain(ax, bottom=True)
    return fig


for _k, _alt in {"color_avoid": "Bubbles colored by pay range: the color repeats the x position and encodes nothing.",
                 "color_fix": "Grey bubbles; the four high-exposure roles in blue.",
                 "trend_avoid": "Four groups, four colored trend lines crossing each other.",
                 "trend_fix": "One group in blue with its trend line; the others grey, no lines.",
                 "label_avoid": "Every bubble labelled; the names collide.",
                 "label_fix": "Only the two bubbles the headline names are labelled.",
                 "overlap_avoid": "Small bubbles drawn underneath and hidden by big ones.",
                 "overlap_fix": "Big bubbles drawn first, small ones on top with white outlines."}.items():
    EXHIBITS[f"corr_sc_bp_{_k}"] = (lambda k=_k, a=_alt: (_sc_mini(k), a))


# ================================================================== DUAL AXIS
def _dual(kind):
    fig = fig_px(300, 160)
    t = MINI - 1.5
    x = np.arange(len(DUAL))
    v, o = DUAL.vacancy_pct.values, DUAL.overtime_hrs_per_fte_wk.values
    ticks = ([0, 12, 23], ["Jan '25", "Jan '26", "Dec '26"])
    if kind in ("avoid_a", "avoid_b"):
        ax = fig.add_subplot()
        ax2 = ax.twinx()
        ax.plot(x, v, color=C.focus, lw=2)
        ax2.plot(x, o, color=C.accent, lw=2)
        if kind == "avoid_a":
            ax.set_ylim(6.5, 13)
            ax2.set_ylim(3.6, 7.0)
        else:
            ax.set_ylim(0, 13)
            ax2.set_ylim(3.5, 16)
        ax.grid(axis="y", color=C.grid, lw=0.6)
        for a, col, lab, ha, xx in ((ax, C.focus, "Vacancy (%)", "left", 0), (ax2, C.accent, "Overtime (hrs)", "right", 1)):
            a.tick_params(labelsize=t - 1, length=0, colors=col)
            for s in a.spines.values():
                s.set_visible(False)
            a.text(xx, 1.04, lab, transform=a.transAxes, ha=ha, va="bottom", fontsize=t - 0.5, color=col,
                   fontweight=600)
        ax.set_xticks(*ticks)
        ax.tick_params(axis="x", colors=C.text_muted)
        ax.set_xlim(-0.5, 23.5)
        return fig
    if kind == "panels":
        fig.set_layout_engine("none")
        rows = ((v, "Vacancy rate (% of budgeted roles)", "{:.1f}%"), (o, "Overtime (hours per FTE a week)", "{:.1f}"))
        for i, (y, title, fmt) in enumerate(rows):
            ax = fig.add_axes([0.08, 0.56 - i * 0.43, 0.8, 0.27])
            ax.plot(x, y, color=C.focus, lw=2, zorder=2)
            ax.scatter([_pk], [y[_pk]], s=16, color=C.focus, zorder=3)
            ax.annotate(fmt.format(y[_pk]), (_pk, y[_pk]), xytext=(5, 3), textcoords="offset points", fontsize=t - 0.5,
                        fontweight=700, color=C.focus, va="bottom")
            ax.set_ylim(0, max(y) * 1.45)
            ax.set_xlim(-0.5, 23.5)
            ax.set_yticks([0, round(max(y) / 2), round(max(y))] if max(y) > 8 else [0, 4, 8][:2] + [round(max(y))])
            ax.set_yticks([0, round(max(y))])
            ax.tick_params(labelsize=t - 1.5, length=0, colors=C.text_muted)
            ax.grid(axis="y", color=C.grid, lw=0.6)
            ax.text(-0.5, max(y) * 1.5, title, fontsize=t - 0.5, color=C.headline, fontweight=600, va="bottom")
            _plain(ax, bottom=True)
            if i == 0:
                ax.set_xticks(ticks[0], ["", "", ""])
            else:
                ax.set_xticks(*ticks)
        return fig
    ax = fig.add_subplot()                                    # indexed: one honest axis
    vi, oi = v / v[0] * 100, o / o[0] * 100
    ax.axhline(100, color=C.axis, lw=0.8)
    ax.plot(x, oi, color=C.context, lw=1.6)
    ax.plot(x, vi, color=C.focus, lw=2)
    ax.text(23.6, vi[-1] - 9, f"Vacancy {vi[-1]:.0f}", fontsize=t - 1, color=C.focus, fontweight=600, va="center")
    ax.text(23.6, oi[-1] + 9, f"Overtime {oi[-1]:.0f}", fontsize=t - 1, color=C.text, va="center")
    ax.text(0, 97, "Jan 2025 = 100", fontsize=t - 1.5, color=C.text_muted, va="top")
    ax.set_xlim(-0.5, 33)
    ax.set_ylim(80, 190)
    ax.set_yticks([100, 150], ["100", "150"])
    ax.grid(axis="y", color=C.grid, lw=0.6)
    ax.set_xticks(*ticks)
    ax.tick_params(labelsize=t - 1, length=0, colors=C.text_muted)
    _plain(ax)
    return fig


for _k, _alt in {"avoid_a": "Dual-axis chart with ranges chosen so vacancy and overtime lines lie on top of each other.",
                 "avoid_b": "The same data with different ranges: overtime now looks flat while vacancies soar.",
                 "panels": "Two aligned panels sharing one time axis: vacancy above, overtime below, each from zero.",
                 "indexed": "Both measures indexed to January 2025 = 100 on one axis."}.items():
    EXHIBITS[f"corr_dual_{_k}"] = (lambda k=_k, a=_alt: (_dual(k), a))


# ================================================================== HEATMAP
@exhibit
def corr_hm_anatomy():
    fig = fig_px(640, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes(ph([0.2, 0.2, 0.79, 0.66], [0.27, 0.2, 0.72, 0.64]))
    m = HM.rename(index=lambda b: BU_SHORT.get(b, b))
    short_cols = {"Manager support": "Manager", "Recognition": "Recog.", "Tools & tech": "Tools", "Belonging": "Belong.",
                  "Pay fairness": "Pay"}                                               # phones: one word per column
    m = m.rename(columns=lambda c: short_cols.get(c, c) if _ex.PHONE else c)
    heat(ax, m, div_color, size=ph(LABEL, LABEL - 2), tick=ph(TICK, TICK - 3), bold_cols={HM_FOCUS}, gap=0.07)
    j = DRIVERS.index(HM_FOCUS)
    nr = len(m)
    ax.add_patch(Rectangle((j + 0.01, 0.01), 0.98, nr - 0.02, fill=False, ec=C.headline, lw=1.6, zorder=4, clip_on=False))
    kx = fig.add_axes([0.2, 0.0, 0.79, 0.16])                       # stepped key under the grid, right-aligned
    kx.set_xlim(0, 7)
    kx.set_ylim(0, 1)
    kx.axis("off")
    key_strip(kx, 2.9, 0.55, 2.4, 0.26, mv.DIVERGING, None, size=TICK, ends=("Below benchmark", "Above benchmark"))
    sw = 2.4 / 7
    for kk, c in enumerate([-9, -6, -3, 0, 3, 6, 9]):
        kx.text(2.9 + (kk + 0.5) * sw, 0.42, mv.signed(c), ha="center", va="top", fontsize=TICK - 2, color=C.text_muted)
    marker(kx, (2.9 + 3.5 * sw, 0.68), 3, offset=(0, 20))
    o = m.index.get_loc(BU_SHORT.get(_worst, _worst))
    marker(ax, (j + 0.5, nr), 4, offset=(0, 36))
    marker(ax, (0, nr - 1), 5, offset=(-116, 0))
    marker(ax, (j + 0.5, nr - 1 - o + 0.5), 6, offset=(-36, 0))
    marker(ax, (DRIVERS.index("Belonging") + 0.5, 1.5), 7, offset=(31, 0))
    return fig, (TEXT["corr_hm_headline"] + f": Workload gap {TEXT['corr_hm_worst']} points in Oncology; "
                 f"Corporate is the only unit above the benchmark on workload.")


def _seq_map(lo, hi, ramp=None):
    ramp = ramp or mv.SEQUENTIAL["blue"]
    return stepped(np.linspace(lo, hi, len(ramp) + 1), ramp), np.linspace(lo, hi, len(ramp) + 1)


@exhibit
def corr_hm_var_seq():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.3, 0.26, 0.69, 0.68])
    m = AQP.rename(index=SHORT)
    col, b = _seq_map(5, 35)
    heat(ax, m, col, values=False, size=MINI - 1.5, col_labels=False, gap=0.1)
    for i, q in enumerate(QS):
        if q.startswith("Q1"):
            ax.text(i, -0.25, q.split()[1], ha="left", va="top", fontsize=MINI - 2, color=C.text_muted)
    kx = fig.add_axes([0.3, 0.05, 0.69, 0.1])
    kx.set_xlim(0, 1); kx.set_ylim(0, 1); kx.axis("off")
    key_strip(kx, 0.25, 0.45, 0.6, 0.45, mv.SEQUENTIAL["blue"], [f"{v:.0f}" for v in b], size=MINI - 1.5)
    kx.text(0.22, 0.67, "Attrition (%)", ha="right", va="center", fontsize=MINI - 2.5, color=C.text_muted)
    return fig, "Sequential heatmap of quarterly attrition by job family: Pharmacy Technician is darkest throughout."


@exhibit
def corr_hm_var_table():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.3, 0.02, 0.69, 0.8])
    m = RBP.rename(index=lambda b: BU_SHORT.get(b, b), columns=lambda q: q.split()[0])
    col, _ = _seq_map(3, 12)
    heat(ax, m, col, fmt=lambda v: f"{v:.1f}", size=MINI - 1.5, bold_rows={"Oncology"}, gap=0.08)
    ax.add_patch(Rectangle((0.01, len(m) - 1 + 0.01), len(m.columns) - 0.02, 0.98, fill=False, ec=C.headline, lw=1.3,
                           clip_on=False, zorder=4))
    return fig, "Heat table of FY26 regretted attrition by business unit and quarter, values printed, Oncology outlined."


@exhibit
def corr_hm_var_od():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.31, 0.02, 0.68, 0.72])
    rows = {"Pharmacy Technician": "Pharmacy Tech", "Customer Care": "Customer Care", "Supply Chain Planning": "Supply Chain"}
    cols = {"Specialty Pharmacy Ops": "Spec.\nRx", "Customer Care": "Cust.\ncare", "Supply Chain Planning": "Supply\nchain",
            "DC Leadership": "DC\nlead.", "Data & Analytics": "Data", "Customer Success": "Cust.\nsucc."}
    m = MOB.pivot_table(index="from_family", columns="to_family", values="moves", aggfunc="sum")
    m = m.loc[MOB.groupby("from_family").moves.sum().sort_values(ascending=False).index,
              MOB.groupby("to_family").moves.sum().sort_values(ascending=False).index]
    m = m.rename(index=rows, columns=cols)
    col, _ = _seq_map(0, 330)

    def c(v):
        return C.surface_subtle if v != v else col(v)
    heat(ax, m, c, fmt=lambda v: f"{v:.0f}" if v == v else "", size=MINI - 2.5, tick=MINI - 2.5, gap=0.08, wrap=False)
    ax.text(-0.12, len(m) + 0.12, "From (rows)\nto (columns)", ha="right", va="bottom", fontsize=MINI - 2.5,
            color=C.text_muted, linespacing=1.1)
    return fig, f"Origin-by-destination matrix of internal moves; the largest path is {TEXT['corr_hm_od_top']}."


@exhibit
def corr_hm_var_binned():
    rng = np.random.default_rng(21)                          # schematic: 2,400 synthetic people, tenure vs compa-ratio
    n = 2400
    ten = np.clip(rng.gamma(2.0, 2.6, n), 0, 19.9)
    cr = np.clip(0.86 + 0.012 * ten + rng.normal(0, 0.06, n), 0.70, 1.199)
    H, xe, ye = np.histogram2d(ten, cr, bins=[np.arange(0, 21, 2), np.arange(0.70, 1.21, 0.05)])
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    col, b = _seq_map(10, 250)
    for i in range(H.shape[0]):
        for j in range(H.shape[1]):
            v = H[i, j]
            if v == 0:
                continue
            fill = col(v) if v >= 10 else C.context_light
            ax.add_patch(Rectangle((xe[i] + 0.08, ye[j] + 0.003), 2 - 0.16, 0.05 - 0.006, color=fill, lw=0))
    ax.set_xlim(0, 20)
    ax.set_ylim(0.70, 1.20)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_yticks([0.8, 1.0, 1.2], ["0.8", "1.0", "1.2"])
    ax.tick_params(labelsize=MINI - 2, length=0, colors=C.text_muted)
    _plain(ax)
    ytitle(ax, "Compa-ratio", size=MINI - 0.5)
    xtitle(ax, "Tenure (years)", size=MINI - 0.5)
    ax.text(19.8, 0.715, "Grey = fewer than 10 people", ha="right", va="bottom", fontsize=MINI - 2.5,
            color=C.text_muted)
    return fig, "Binned density of tenure vs. compa-ratio: counts per cell in blue; cells under 10 people grey."


# --- heatmap best practice minis (200 x 140)
def _hm_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    t = MINI - 3
    rng = np.random.default_rng(8)                           # schematic matrix: 8 rows with row-level effects
    base = np.array([24, 6, 15, 30, 10, 19, 3, 27])
    mat = np.clip(base[:, None] + rng.normal(0, 3, (8, 10)) + np.linspace(-2, 2, 10), 0, 34)
    letters = list("ABCDEFGH")
    if kind in ("steps_avoid", "steps_fix", "sort_avoid", "sort_fix"):
        ax = fig.add_axes([0.08, 0.24, 0.9, 0.74])
        if kind.startswith("steps"):
            bounds = [0, 1, 2, 4, 10, 25, 35] if kind == "steps_avoid" else list(np.linspace(0, 36, 7))
            order = np.argsort(-mat.mean(axis=1))
        else:
            bounds = list(np.linspace(0, 36, 7))
            order = np.arange(8) if kind == "sort_avoid" else np.argsort(-mat.mean(axis=1))
        m = pd.DataFrame(mat[order], index=[letters[i] for i in order])
        heat(ax, m, stepped(np.array(bounds), mv.SEQUENTIAL["blue"]), values=False, col_labels=False, size=t, gap=0.1)
        kx = fig.add_axes([0.08, 0.0, 0.9, 0.18])
        kx.set_xlim(0, 1); kx.set_ylim(0, 1); kx.axis("off")
        key_strip(kx, 0.12, 0.55, 0.76, 0.32, mv.SEQUENTIAL["blue"], [f"{b:.0f}" for b in bounds], size=t + 0.5)
        return fig
    if kind in ("zero_avoid", "zero_fix"):
        ax = fig.add_axes([0.02, 0.24, 0.96, 0.74])
        m = HM.copy()
        m.index = [chr(65 + i) for i in range(len(m))]
        if kind == "zero_avoid":
            ramp = mv.DIVERGING[:3] + mv.DIVERGING[4:]
            bounds = np.array([-10.5, -7, -3.5, 0, 3.5, 7, 10.5])
        else:
            ramp, bounds = mv.DIVERGING, DIV_BOUNDS
        heat(ax, m, stepped(bounds, ramp), values=False, col_labels=False, row_labels=False, size=t, gap=0.08)
        kx = fig.add_axes([0.08, 0.0, 0.9, 0.18])
        kx.set_xlim(0, 1); kx.set_ylim(0, 1); kx.axis("off")
        key_strip(kx, 0.12, 0.55, 0.76, 0.32, ramp, None, size=t + 0.5, gap=0.004 if kind == "zero_avoid" else 0)
        sw = 0.76 / len(ramp)
        if kind == "zero_fix":
            kx.text(0.12 + 3.5 * sw, 0.42, "0", ha="center", va="top", fontsize=t + 0.5, color=C.text_muted)
        else:
            kx.text(0.12 + 3 * sw, 0.42, "0", ha="center", va="top", fontsize=t + 0.5, color=C.text_muted)
        kx.text(0.1, 0.71, "−", ha="right", va="center", fontsize=t + 1, color=C.negative_text)
        kx.text(0.9, 0.71, "+", ha="left", va="center", fontsize=t + 1, color=C.focus)
        return fig
    # small groups: team x driver scores, one team with 6 respondents
    ax = fig.add_axes([0.3, 0.04, 0.68, 0.74])
    teams = {"Inbound (46)": [4, 2, -3, 1], "Outbound (38)": [-2, 1, -6, 0], "Returns (6)": [-9, -11, -4, -8],
             "Quality (21)": [3, 5, 1, 2]}
    m = pd.DataFrame(teams, index=["Growth", "Mgr", "Load", "Tools"]).T
    if kind == "small_fix":
        m.loc["Returns (6)"] = np.nan
    heat(ax, m, div_color, size=t + 0.5, tick=t + 0.5, gap=0.08, wrap=False)
    return fig


for _k, _alt in {"steps_avoid": "A heatmap with uneven class breaks: 1, 2, 4, 10, 25.",
                 "steps_fix": "The same heatmap with six equal classes.",
                 "sort_avoid": "Rows in alphabetical order: dark and light cells scattered.",
                 "sort_fix": "Rows ranked by average: the pattern emerges from dark to light.",
                 "zero_avoid": "A diverging scale with no neutral step: every cell is forced above or below.",
                 "zero_fix": "A diverging scale with a neutral step around zero.",
                 "small_avoid": "A six-person team's scores shown in color and numbers.",
                 "small_fix": "The six-person team greyed out and marked n<10."}.items():
    EXHIBITS[f"corr_hm_bp_{_k}"] = (lambda k=_k, a=_alt: (_hm_mini(k), a))
