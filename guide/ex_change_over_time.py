"""Change-over-time exhibits: line, stacked area, bubble timeline, small multiples. Registered on import."""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import mckviz as mv
from exhibits import (ANNOT, ANTI, LABEL, MINI, SHORT, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px,
                      marker)

LINE, CTX_LINE, GRID_LW = 2.4, 1.4, 0.75          # data lines about twice the gridline weight


# ------------------------------------------------------------------ helpers
def end_labels(ax, x, items, *, size=LABEL, gap=None, dx=0.25):
    """Direct labels at line ends, nudged apart. items = [(y, text, color, bold)]."""
    lo, hi = ax.get_ylim()
    gap = gap or (hi - lo) * 0.055
    items = sorted(items, key=lambda t: t[0])
    ys = [t[0] for t in items]
    for i in range(1, len(ys)):                       # push up until labels clear each other
        ys[i] = max(ys[i], ys[i - 1] + gap)
    shift = max(0, ys[-1] - (hi - gap * 0.3)) if ys else 0
    ys = [y - shift for y in ys]
    for i in range(len(ys) - 2, -1, -1):
        ys[i] = min(ys[i], ys[i + 1] - gap)
    for (y0, txt, col, bold), y in zip(items, ys):
        ax.text(x + dx, y, txt, va="center", fontsize=size, color=col, fontweight=600 if bold else 400)


def quarter_axis(ax, quarters, *, size=TICK, years=True):
    x = np.arange(len(quarters))
    ax.set_xticks(x, [q.split()[0] for q in quarters])
    ax.tick_params(axis="x", labelsize=size - 1.5, length=0, colors=C.text_muted)
    if years:
        fys = [q.split()[1] for q in quarters]
        for fy in dict.fromkeys(fys):
            idx = [i for i, f in enumerate(fys) if f == fy]
            ax.text(np.mean(idx), -0.13, fy, transform=ax.get_xaxis_transform(), ha="center", va="top",
                    fontsize=size - 0.5, color=C.text)
    return x


def shade(ax, x0, x1, label=None, *, size=ANNOT, y=0.98):
    ax.axvspan(x0, x1, color=C.surface_subtle, lw=0, zorder=0)
    if label:
        ax.text(x0 + 0.12, y, label, transform=ax.get_xaxis_transform(), fontsize=size, color=C.text_muted, va="top")


def ygrid(ax, ticks, fmt="{:.0f}", size=TICK):
    ax.set_yticks(ticks, [fmt.format(t) for t in ticks])
    ax.grid(axis="y", color=C.grid, lw=GRID_LW)
    ax.tick_params(axis="y", labelsize=size - 1, length=0, colors=C.text_muted)


# ------------------------------------------------------------------ data
AQ = _csv("attrition_quarterly")
QS = list(dict.fromkeys(AQ.quarter))
PIV = AQ.pivot(index="quarter", columns="job_family", values="attrition_pct").loc[QS]
PT = PIV["Pharmacy Technician"]
RESET = QS.index("Q3 FY25")
_drop = PT.iloc[RESET - 1] - PT.iloc[-1]
TEXT["ts_drop"] = f"{_drop:.0f}"
TEXT["ts_headline"] = f"Pharmacy Technician attrition fell about {_drop:.0f} points after the pay and scheduling reset"
TEXT["ts_subtitle"] = "Annualized voluntary attrition by job family, Q1 FY24–Q4 FY26 (%)"

IDX = _csv("data_ai_index")
TIME = _csv("pharmacist_time_mix")
TEXT["area_headline"] = (f"Clinical services rose from {TIME.clinical_pct.iloc[0]}% to {TIME.clinical_pct.iloc[-1]}% "
                         "of a retail pharmacist's week as central fill absorbed dispensing")
TEXT["area_subtitle"] = "Share of a retail pharmacist's hours by activity, FY22–FY26 (%)"

WR = _csv("workforce_reductions")
WQ = [f"{y} Q{q}" for y in range(2020, 2027) for q in (1, 2, 3, 4)][:26]
_since = WR[WR.quarter >= "2023"].groupby("sub_sector").roles_affected.sum().sort_values(ascending=False)
TEXT["bt_top"] = f"{_since.iloc[0]:,}"
TEXT["bt_ratio"] = f"{_since.iloc[0] / _since.iloc[1]:.1f}"
TEXT["bt_headline"] = (f"Pharma manufacturers have announced {TEXT['bt_top']} job cuts since 2023, "
                       f"{TEXT['bt_ratio']}× the next healthcare sub-sector")
TEXT["bt_subtitle"] = "Announced workforce reductions by healthcare sub-sector, 2020–Q2 2026 (bubble area = roles affected)"

RB = _csv("regretted_attrition_bu")
RBQ = list(dict.fromkeys(RB.quarter))
RBP = RB.pivot(index="quarter", columns="business_unit", values="regretted_attrition_pct").loc[RBQ]
_onc = RBP["Oncology & Multispecialty"]
_others = RBP.drop(columns="Oncology & Multispecialty")
TEXT["sm_ratio"] = f"{_onc.iloc[-1] / _onc.iloc[0]:.1f}"
TEXT["sm_headline"] = ("Oncology regretted attrition nearly doubled in two years while every other business unit "
                       f"stayed within {np.ceil((_others.max() - _others.min()).max()):.0f} points")
TEXT["sm_subtitle"] = "Regretted attrition by business unit, Q1 FY25–Q4 FY26 (% of high performers, annualized)"


# ================================================================== LINE
@exhibit
def ts_line_anatomy():
    fig = fig_px(640, 330)
    ax = fig.add_subplot()
    x = np.arange(len(QS))
    shade(ax, RESET - 0.5, len(QS) - 0.5, "After the pay and scheduling reset", size=ANNOT)
    for fam in PIV.columns:
        if fam != "Pharmacy Technician":
            ax.plot(x, PIV[fam], color=C.context, lw=CTX_LINE, zorder=2)
    ax.plot(x, PT, color=C.focus, lw=LINE, zorder=3)
    ax.set_xlim(-0.3, len(QS) + 2.7)
    ax.set_ylim(0, 40)
    ygrid(ax, [0, 10, 20, 30, 40])
    quarter_axis(ax, QS)
    ax.set_xticks(x, [q.split()[0] for q in QS])
    _plain(ax, bottom=True)
    end_labels(ax, len(QS) - 1, [(PIV[f].iloc[-1], f"{SHORT[f]} {PIV[f].iloc[-1]:.1f}",
                                  C.focus if f == "Pharmacy Technician" else C.text, f == "Pharmacy Technician")
                                 for f in PIV.columns], size=LABEL - 1)
    ax.annotate("", xy=(len(QS) - 1.3, PT.iloc[-1] + 0.6), xytext=(len(QS) - 1.3, PT.iloc[RESET - 1]),
                arrowprops=dict(arrowstyle="-|>", color=C.annotation, lw=1, mutation_scale=9))
    ax.plot([RESET - 1, len(QS) - 1.3], [PT.iloc[RESET - 1]] * 2, color=C.annotation, lw=0.7, ls=(0, (2, 2)))
    ax.text(len(QS) - 1.45, (PT.iloc[RESET - 1] + PT.iloc[-1]) / 2, f"{mv.signed(-_drop, 1)} pts", ha="right",
            va="center", fontsize=ANNOT, color=C.annotation, fontweight=600)
    marker(ax, (4, PT.iloc[4]), 3, offset=(0, 14))
    marker(ax, (2, PIV["Customer Care"].iloc[2]), 4, offset=(0, 13))
    marker(ax, (RESET - 0.5, 38.5), 5, offset=(-14, 0))
    marker(ax, (len(QS) - 1, 25), 6, offset=(14, 22))
    marker(ax, (len(QS) - 1.3, (PT.iloc[RESET - 1] + PT.iloc[-1]) / 2), 7, offset=(-70, 0))
    marker(ax, (1.0, 30), 8)
    return fig, TEXT["ts_headline"] + f": from {PT.iloc[RESET - 1]:.1f}% in Q2 FY25 to {PT.iloc[-1]:.1f}% in Q4 FY26."


@exhibit
def ts_var_forecast():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x = np.arange(len(QS))
    fx = np.arange(len(QS) - 1, len(QS) + 4)
    base = PT.iloc[-1] - 0.75 * np.arange(5)
    spread = np.linspace(0, 3.2, 5)
    shade(ax, len(QS) - 0.5, fx[-1] + 0.4, "Forecast", size=MINI - 1.5)
    ax.fill_between(fx, base - spread, base + spread, color=C.focus, alpha=0.14, lw=0)
    ax.plot(x, PT, color=C.focus, lw=2)
    ax.plot(fx, base, color=C.focus, lw=2, ls=(0, (3, 2)))
    ax.text(fx[-1] + 0.3, base[-1], f"Base {base[-1]:.0f}%\nRange {base[-1] - spread[-1]:.0f}–{base[-1] + spread[-1]:.0f}%",
            fontsize=MINI - 2, va="center", color=C.focus)
    ax.set_xlim(-0.3, fx[-1] + 4.5)
    ax.set_ylim(15, 38)
    ygrid(ax, [20, 30], size=MINI)
    ax.set_xticks([0, 4, 8, 12], ["FY24", "FY25", "FY26", "FY27"])
    ax.tick_params(axis="x", labelsize=MINI - 1.5, length=0)
    _plain(ax, bottom=True)
    return fig, "Pharmacy Technician attrition with a dashed FY27 forecast and a widening shaded range."


@exhibit
def ts_var_indexed():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    ax.axhline(100, color=C.axis, lw=0.7)
    ax.plot(IDX.year, IDX.external_postings_idx, color=C.context, lw=2)
    ax.plot(IDX.year, IDX.internal_headcount_idx, color=C.focus, lw=2)
    end_labels(ax, IDX.year.iloc[-1], [(IDX.external_postings_idx.iloc[-1], f"Market postings {IDX.external_postings_idx.iloc[-1]}", C.text, False),
                                       (IDX.internal_headcount_idx.iloc[-1], f"Our headcount {IDX.internal_headcount_idx.iloc[-1]}", C.focus, True)],
               size=MINI - 1.5, dx=0.15)
    ax.set_xlim(2020.8, 2028.6)
    ax.set_ylim(80, 210)
    ygrid(ax, [100, 150, 200], size=MINI)
    ax.set_xticks([2021, 2023, 2025])
    ax.tick_params(axis="x", labelsize=MINI - 1.5, length=0)
    _plain(ax, bottom=False)
    TEXT["idx_post"] = str(IDX.external_postings_idx.iloc[-1])
    TEXT["idx_int"] = str(IDX.internal_headcount_idx.iloc[-1])
    return fig, "Indexed lines, 2021 = 100: market Data & AI postings reach 196, our Data & AI headcount 122."


@exhibit
def ts_var_points():
    d = _csv("internal_fill_by_fy")
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x = np.arange(len(d))
    ax.plot(x, d.internal_fill_pct, color=C.focus, lw=2, marker="o", ms=5, mfc=C.focus, mec="white", mew=1.2)
    for xx, v in zip(x, d.internal_fill_pct):
        ax.annotate(f"{v}%", (xx, v), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=MINI - 1,
                    color=C.headline if xx == len(d) - 1 else C.text, fontweight=700 if xx == len(d) - 1 else 400)
    ax.set_xticks(x, d.fiscal_year)
    ax.set_yticks([])
    ax.set_ylim(15, 33)
    ax.set_xlim(-0.4, len(d) - 0.6)
    ax.tick_params(axis="x", labelsize=MINI - 1, length=0)
    _plain(ax, bottom=True)
    return fig, "Five annual points of internal fill rate, each labelled; FY26 29% in bold."


@exhibit
def ts_var_spark():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    fams = list(PIV.iloc[-1].sort_values(ascending=False).index)
    n = len(fams)
    for i, f in enumerate(fams):
        y0 = 1 - (i + 1) / n
        hot = f == "Pharmacy Technician"
        fig.text(0.0, y0 + 0.5 / n, SHORT[f], fontsize=MINI - 1.5, va="center", color=C.headline if hot else C.text,
                 fontweight=600 if hot else 400)
        ax = fig.add_axes([0.36, y0 + 0.12 / n, 0.42, 0.76 / n])
        ax.plot(PIV[f].values, color=C.focus if hot else C.context, lw=1.4)
        ax.plot(len(QS) - 1, PIV[f].iloc[-1], "o", ms=3, color=C.focus if hot else C.text)
        ax.axis("off")
        d = PIV[f].iloc[-1] - PIV[f].iloc[-5]
        fig.text(0.82, y0 + 0.5 / n, f"{PIV[f].iloc[-1]:.1f}", fontsize=MINI - 1.5, va="center", color=C.text)
        fig.text(1.0, y0 + 0.5 / n, mv.signed(d, 1), fontsize=MINI - 1.5, va="center", ha="right",
                 color=C.negative_text if d > 0 else (C.headline if hot else C.text), fontweight=600 if hot else 400)
    return fig, "A table of sparklines: one small trend line per job family with the latest value and the one-year change."


def _line_mini(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    x = np.arange(len(QS))
    t = MINI - 2.5
    if kind in ("hl_avoid", "hl_fix", "legend_avoid", "legend_fix"):
        fams = list(PIV.columns)[:5]
        for i, f in enumerate(fams):
            if kind == "hl_avoid":
                col, lw = ANTI["rainbow"][i], 1.5
            else:
                col, lw = (C.focus, 2) if f == "Pharmacy Technician" else (C.context, 1.2)
            ax.plot(x, PIV[f], color=col, lw=lw, label=SHORT[f])
        ax.set_ylim(5, 37)
        if kind == "legend_avoid":
            ax.legend(fontsize=t - 1, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False,
                      handlelength=1, columnspacing=0.6)
        if kind == "legend_fix":
            end_labels(ax, len(QS) - 1, [(PIV[f].iloc[-1], SHORT[f].split()[0],
                                          C.focus if f == "Pharmacy Technician" else C.text_muted,
                                          f == "Pharmacy Technician") for f in fams], size=t, dx=0.4, gap=3.4)
            ax.set_xlim(-0.3, len(QS) + 3.4)
    elif kind == "trend_avoid":
        bottom = np.zeros(len(TIME))
        for col, c in zip(["clinical_pct", "dispensing_pct", "inventory_pct", "admin_pct"],
                          [C.focus, C.context, C.context_light, C.grid]):
            ax.bar(range(len(TIME)), TIME[col], bottom=bottom, color=c, width=0.67, edgecolor="white", lw=0.8)
            bottom += TIME[col].values
        ax.set_xticks(range(len(TIME)), TIME.fiscal_year)
    elif kind == "trend_fix":
        xx = np.arange(len(TIME))
        ax.plot(xx, TIME.dispensing_pct, color=C.context, lw=1.6)
        ax.plot(xx, TIME.clinical_pct, color=C.focus, lw=2)
        ax.text(len(TIME) - 0.9, TIME.dispensing_pct.iloc[-1] + 4, "Dispensing", fontsize=t, color=C.text)
        ax.text(len(TIME) - 0.9, TIME.clinical_pct.iloc[-1] - 8, "Clinical", fontsize=t, color=C.focus, fontweight=600)
        ax.set_xticks(xx, TIME.fiscal_year)
        ax.set_ylim(0, 65)
    elif kind == "shade_avoid":
        ax.fill_between(x, 20, PT, color=C.focus, alpha=0.35, lw=0)
        ax.plot(x, PT, color=C.focus, lw=1.6)
        ax.set_ylim(20, 36)
        ax.set_yticks([20, 28, 36])
        ax.tick_params(axis="y", labelsize=t, length=0)
    elif kind == "shade_fix":
        ax.plot(x, PT, color=C.focus, lw=2)
        ax.set_ylim(20, 36)
        ygrid(ax, [20, 28, 36], size=t + 1)
    if kind not in ("trend_avoid", "trend_fix"):
        ax.set_xticks([0, 4, 8], ["FY24", "FY25", "FY26"])
    ax.tick_params(axis="x", labelsize=t, length=0)
    if kind not in ("shade_avoid", "shade_fix"):
        ax.set_yticks([])
    _plain(ax, bottom=True, left=kind == "shade_avoid")
    return fig


for _k, _alt in {"hl_avoid": "Five lines in five bright colors.",
                 "hl_fix": "Four grey lines and one blue line.",
                 "trend_avoid": "Stacked columns of four activities over five years.",
                 "trend_fix": "Two lines: clinical rising, dispensing falling.",
                 "shade_avoid": "A shaded area under a line on an axis that starts at 20.",
                 "shade_fix": "A plain line on the same axis.",
                 "legend_avoid": "A legend above the chart, far from the lines.",
                 "legend_fix": "Names at the line ends."}.items():
    EXHIBITS[f"ts_bp_{_k}"] = (lambda k=_k, a=_alt: (_line_mini(k), a))


def _line_mini2(kind):
    fig = fig_px(200, 140)
    t = MINI - 2.5
    if kind in ("many_fix",):
        fig.set_layout_engine("none")
        fams = list(PIV.columns)
        for i, f in enumerate(fams):
            ax = fig.add_axes([0.02 + (i % 3) * 0.33, 0.52 - (i // 3) * 0.47, 0.29, 0.32])
            for g in fams:
                ax.plot(PIV[g].values, color=C.context_light, lw=0.7)
            ax.plot(PIV[f].values, color=C.focus, lw=1.4)
            ax.set_ylim(5, 37)
            ax.axis("off")
            ax.set_title(SHORT[f].split()[0], fontsize=t - 0.5, loc="left", color=C.text, pad=2)
        return fig
    ax = fig.add_subplot()
    years = [2019, 2020, 2022, 2025, 2026]
    vals = [18, 20, 23, 26, 29]
    if kind == "even_avoid":
        ax.plot(range(5), vals, color=C.focus, lw=2, marker="o", ms=3.5)
        ax.set_xticks(range(5), [str(y) for y in years])
    elif kind == "even_fix":
        ax.plot(years, vals, color=C.focus, lw=2, marker="o", ms=3.5)
        ax.set_xticks(years, [str(y) for y in years])
    elif kind in ("gap_avoid", "gap_fix"):
        y = PT.to_numpy(dtype=float, copy=True)
        if kind == "gap_avoid":
            xs = [i for i in range(len(y)) if i not in (5, 6)]
            ax.plot(xs, y[xs], color=C.focus, lw=2)
        else:
            y[5:7] = np.nan
            ax.plot(range(len(y)), y, color=C.focus, lw=2)
            ax.axvspan(4.6, 6.4, color=C.surface_subtle, lw=0)
            ax.text(5.5, 0.95, "No data", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=t,
                    color=C.text_muted)
        ax.set_xticks([0, 4, 8], ["FY24", "FY25", "FY26"])
        ax.set_ylim(20, 38)
    elif kind in ("weight_avoid", "weight_fix"):
        heavy = kind == "weight_avoid"
        for f in list(PIV.columns)[:3]:
            ax.plot(PIV[f].values, color=C.focus if f == "Pharmacy Technician" else C.context,
                    lw=0.8 if heavy else (2 if f == "Pharmacy Technician" else 1.3))
        ax.set_yticks([15, 20, 25, 30, 35])
        ax.grid(axis="y", color=C.axis if heavy else C.grid, lw=1.2 if heavy else 0.6)
        ax.tick_params(axis="y", labelsize=t, length=0, colors=C.text_muted)
        ax.set_xticks([0, 4, 8], ["FY24", "FY25", "FY26"])
    elif kind == "many_avoid":
        for i, f in enumerate(PIV.columns):
            ax.plot(PIV[f].values + np.sin(np.arange(len(QS)) * (i + 1)) * 2.5, color=mv.CATEGORICAL[i], lw=1.3)
        ax.set_xticks([0, 4, 8], ["FY24", "FY25", "FY26"])
    ax.tick_params(axis="x", labelsize=t, length=0)
    if kind not in ("weight_avoid", "weight_fix"):
        ax.set_yticks([])
    _plain(ax, bottom=True)
    return fig


for _k, _alt in {"even_avoid": "Years spaced evenly although 2021, 2023 and 2024 are missing.",
                 "even_fix": "Years placed at their true positions.",
                 "gap_avoid": "A line drawn straight across two missing quarters.",
                 "gap_fix": "A gap and a 'No data' band where quarters are missing.",
                 "weight_avoid": "Data lines as thin as heavy gridlines.",
                 "weight_fix": "Data lines about twice the weight of light gridlines.",
                 "many_avoid": "Six crossing lines in six colors.",
                 "many_fix": "Six small panels, one highlighted line each."}.items():
    EXHIBITS[f"ts_bp2_{_k}"] = (lambda k=_k, a=_alt: (_line_mini2(k), a))


# ================================================================== STACKED AREA
_ACT = [("clinical_pct", "Clinical services", C.focus), ("dispensing_pct", "Dispensing", C.context),
        ("inventory_pct", "Inventory", C.context_light), ("admin_pct", "Admin", C.grid)]


@exhibit
def area_anatomy():
    fig = fig_px(640, 320)
    ax = fig.add_subplot()
    x = np.arange(len(TIME))
    ys = [TIME[c].values for c, _, _ in _ACT]
    ax.axvline(2, color=C.annotation, lw=0.9, ls=(0, (2.5, 2.5)), zorder=4)
    ax.text(2, 101.5, "Central fill rollout", ha="center", va="bottom", fontsize=ANNOT, color=C.annotation)
    ax.stackplot(x, *ys, colors=[c for _, _, c in _ACT], edgecolor="white", lw=1.2, zorder=2)
    cum = np.zeros(len(TIME))
    for (col, name, c), y in zip(_ACT, ys):
        mid = cum[-1] + y[-1] / 2
        ax.text(x[-1] + 0.08, mid, f"{name} {y[-1]}%", va="center", fontsize=LABEL - 1,
                color=C.focus if col == "clinical_pct" else C.text, fontweight=600 if col == "clinical_pct" else 400)
        cum += y
    ax.text(0.05, ys[0][0] / 2, f"{ys[0][0]}%", va="center", fontsize=LABEL - 1, color="white", fontweight=600)
    ax.set_xticks(x, TIME.fiscal_year)
    ax.set_xlim(0, len(TIME) + 0.25)
    ax.set_ylim(0, 109)
    ygrid(ax, [0, 25, 50, 75, 100], fmt="{:.0f}%")
    ax.grid(False)
    ax.tick_params(axis="x", labelsize=TICK, length=0)
    _plain(ax, bottom=True)
    marker(ax, (2.6, 10), 3)
    marker(ax, (1.0, 55), 4)
    marker(ax, (x[-1] + 0.08, ys[0][-1] / 2), 5, offset=(122, 0))
    marker(ax, (2, 104), 6, offset=(-66, 0))
    marker(ax, (0.05, ys[0][0] / 2), 7, offset=(30, 0))
    return fig, TEXT["area_headline"] + "."


def _area_mini(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    x = np.arange(len(TIME))
    ys = [TIME[c].values for c, _, _ in _ACT]
    if kind == "overlap_avoid":
        for (c, n, col), y in zip(_ACT, ys):
            ax.fill_between(x, 0, y, color=mv.CATEGORICAL[_ACT.index((c, n, col))], alpha=0.55, lw=0)
    elif kind == "overlap_fix":
        ax.stackplot(x, *ys, colors=[c for _, _, c in _ACT], edgecolor="white", lw=0.8)
    elif kind == "color_avoid":
        ax.stackplot(x, *ys, colors=[ANTI["rainbow"][i] for i in (3, 2, 1, 4)], edgecolor="white", lw=0.8)
    elif kind == "color_fix":
        ax.stackplot(x, *ys, colors=[c for _, _, c in _ACT], edgecolor="white", lw=0.8)
    elif kind in ("vol_avoid", "vol_fix"):
        rng = np.random.default_rng(5)                      # schematic: one volatile series, two steady ones
        xx = np.arange(16)
        steady1 = 30 + xx * 0.4
        steady2 = 20 + xx * 0.2
        vol = 12 + 9 * np.abs(np.sin(xx * 1.3)) + rng.normal(0, 1.5, 16)
        order = [vol, steady1, steady2] if kind == "vol_avoid" else [steady1, steady2, vol]
        cols = [C.focus, C.context, C.context_light] if kind == "vol_avoid" else [C.focus, C.context, C.context_light]
        ax.stackplot(xx, *order, colors=cols, edgecolor="white", lw=0.8)
        x = xx
    elif kind == "many_avoid":
        rng = np.random.default_rng(9)
        layers = [rng.uniform(4, 14, len(TIME)) for _ in range(9)]
        ax.stackplot(x, *layers, colors=(mv.CATEGORICAL + [C.context])[:9], edgecolor="white", lw=0.6)
    elif kind == "many_fix":
        ax.stackplot(x, ys[0], ys[1], ys[2] + ys[3], colors=[C.focus, C.context, C.context_light], edgecolor="white",
                     lw=0.8)
    ax.set_xlim(x[0], x[-1])
    ax.set_xticks([])
    ax.set_yticks([])
    _plain(ax, bottom=True)
    return fig


for _k, _alt in {"overlap_avoid": "Four translucent areas drawn over each other.",
                 "overlap_fix": "The same four series stacked.",
                 "color_avoid": "Stack layers in four unrelated bright colors.",
                 "color_fix": "The story layer blue on the baseline, the others in ordered greys.",
                 "vol_avoid": "A volatile layer at the bottom makes every layer above it wobble.",
                 "vol_fix": "Steady layers at the bottom, the volatile one on top.",
                 "many_avoid": "Nine thin layers.",
                 "many_fix": "Three layers: the story, the main comparison, and the rest."}.items():
    EXHIBITS[f"area_bp_{_k}"] = (lambda k=_k, a=_alt: (_area_mini(k), a))


# ================================================================== BUBBLE TIMELINE
def bubble_rows(ax, *, focus="Pharma manufacturers", single=True, big_behind=True, scale=1.0, size_key=True,
                sort=True, band=True, label_size=TICK, outline=True):
    totals = WR.groupby("sub_sector").roles_affected.sum()
    rows = list(_since.index) if sort else sorted(totals.index)
    if band:
        ax.axvspan(WQ.index("2023 Q1") - 0.5, len(WQ) - 0.5, color=C.surface_subtle, lw=0, zorder=0)
    k = 0.11 * scale                                            # marker area (pt^2) per role
    d = WR.copy()
    d["x"] = d.quarter.map(WQ.index)
    d["y"] = d.sub_sector.map({r: len(rows) - 1 - i for i, r in enumerate(rows)})
    d = d.sort_values("roles_affected", ascending=not big_behind)
    for i, r in enumerate(rows):
        ax.hlines(len(rows) - 1 - i, -1, len(WQ) - 0.5, color=C.grid, lw=0.6, zorder=1)   # stop before any key
    cols = [(C.focus if s == focus else C.context) if single else mv.CATEGORICAL[rows.index(s) % 6] for s in d.sub_sector]
    ax.scatter(d.x, d.y, s=d.roles_affected * k, c=cols, alpha=0.9, edgecolors="white" if outline else "none",
               linewidths=1 if outline else 0, zorder=3)
    ax.set_yticks(range(len(rows)), rows[::-1])
    for t in ax.get_yticklabels():
        t.set_fontsize(label_size)
        if t.get_text() == focus:
            t.set_fontweight(600)
            t.set_color(C.headline)
    ax.set_xticks([WQ.index(f"{y} Q1") for y in range(2020, 2027)], [str(y) for y in range(2020, 2027)])
    ax.tick_params(length=0, labelsize=label_size - 1)
    ax.set_xlim(-1, len(WQ) + 0.8)                              # room for the largest last-quarter bubble
    ax.set_ylim(-0.7, len(rows) - 0.3)
    _plain(ax)
    return rows, k


@exhibit
def bt_anatomy():
    fig = fig_px(640, 320)
    ax = fig.add_subplot()
    rows, k = bubble_rows(ax)
    ax.set_xlim(-1, len(WQ) + 6)
    kx = len(WQ) + 1.9                                          # size key, top-right, clear of the data and the edge
    for i, v in enumerate([500, 2000, 5000]):
        ax.scatter(kx, 4.75 - i * 0.9, s=v * k, facecolors="none", edgecolors=C.text_muted, lw=0.8, clip_on=False)
        ax.text(kx + 1.3, 4.75 - i * 0.9, f"{v:,}", va="center", fontsize=TICK - 1.5, color=C.text_muted)
    ax.text(kx, 5.45, "Roles", ha="center", fontsize=TICK - 1.5, color=C.text_muted)
    ax.text(WQ.index("2023 Q1") - 0.3, len(rows) - 0.35, "Since 2023", fontsize=ANNOT, color=C.text_muted, va="bottom")
    ax.set_ylim(-0.7, len(rows) - 0.05)
    marker(ax, (-1, 0), 3, offset=(-6, 12))
    marker(ax, (len(WQ) - 0.5, -0.45), 4, offset=(14, 0))
    marker(ax, (kx, 3.85), 5, offset=(-26, 0))
    big = WR[WR.sub_sector == "Pharma manufacturers"].roles_affected.idxmax()
    marker(ax, (WQ.index(WR.quarter[big]), len(rows) - 1), 6, offset=(-30, 12))
    marker(ax, (WQ.index("2023 Q1") - 0.5, 2.5), 7, offset=(-10, 0))
    return fig, TEXT["bt_headline"] + "."


def _bt_mini(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    kw = dict(scale=0.42, label_size=MINI - 4, band=False)
    if kind == "color_avoid":
        bubble_rows(ax, single=False, **kw)
    elif kind == "color_fix":
        bubble_rows(ax, **kw)
    elif kind == "hide_avoid":
        bubble_rows(ax, big_behind=False, outline=False, **{**kw, "scale": 0.8})
    elif kind == "hide_fix":
        bubble_rows(ax, **{**kw, "scale": 0.8})
    elif kind == "sort_avoid":
        bubble_rows(ax, sort=False, **kw)
    elif kind == "sort_fix":
        bubble_rows(ax, **kw)
    elif kind == "key_avoid":
        bubble_rows(ax, **kw)
    elif kind == "key_fix":
        rows, k = bubble_rows(ax, **kw)
        ax.set_xlim(-1, len(WQ) + 6)
        for i, v in enumerate([1000, 4000]):
            ax.scatter(len(WQ) + 4.4, 4.6 - i * 1.3, s=v * k, facecolors="none", edgecolors=C.text_muted, lw=0.6)
            ax.text(len(WQ) + 4.4, 3.95 - i * 1.3, f"{v // 1000}K", ha="center", va="top", fontsize=MINI - 4,
                    color=C.text_muted)
    ax.set_xticks([])
    return fig


for _k, _alt in {"color_avoid": "Each row's bubbles in a different color.",
                 "color_fix": "One grey for all rows, the headline's row in blue.",
                 "hide_avoid": "Big bubbles drawn over small ones.",
                 "hide_fix": "Big bubbles behind, with white outlines.",
                 "sort_avoid": "Rows in alphabetical order.",
                 "sort_fix": "Rows sorted by total, largest on top.",
                 "key_avoid": "Bubbles with no size key.",
                 "key_fix": "A size key with two reference circles."}.items():
    EXHIBITS[f"bt_bp_{_k}"] = (lambda k=_k, a=_alt: (_bt_mini(k), a))


# ================================================================== SMALL MULTIPLES
_BU_SHORT = {"Oncology & Multispecialty": "Oncology", "U.S. Pharmaceutical": "U.S. Pharma"}


def multiples(fig, *, shared=True, context=True, order=None, exception=True, size=TICK, rect=(0, 0, 1, 1), rows=2,
              axes_all=False, lw=2, mini=False):
    bus = order or list(RBP.iloc[-1].sort_values(ascending=False).index)
    cols = int(np.ceil(len(bus) / rows))
    x0, y0, w, h = rect
    axes = []
    for i, bu in enumerate(bus):
        r, c = divmod(i, cols)
        ax = fig.add_axes([x0 + c * w / cols + 0.02 * w, y0 + h - (r + 1) * h / rows + 0.05 * h,
                           w / cols - 0.05 * w, h / rows - 0.22 * h / rows * (2 / rows)])
        if context:
            for other in RBP.columns:
                ax.plot(RBP[other].values, color=C.context_light, lw=1, zorder=1)
        hot = exception and bu == "Oncology & Multispecialty"
        ax.plot(RBP[bu].values, color=C.negative if hot else C.focus, lw=lw, zorder=3)
        ax.plot(len(RBQ) - 1, RBP[bu].iloc[-1], "o", ms=3.5, color=C.negative if hot else C.focus, zorder=4)
        name = _BU_SHORT.get(bu, bu)
        if mini:
            name = {"Medical-Surgical": "Med-Surg", "Technology": "Tech", "U.S. Pharma": "Pharma"}.get(name, name)
        ax.set_title(name if mini else f"{name}  {RBP[bu].iloc[-1]:.1f}%", loc="left", fontsize=size - 1,
                     color=C.negative_text if hot else C.headline, fontweight=600, pad=3)
        if shared:
            ax.set_ylim(0, 12)
        ax.set_xlim(-0.3, len(RBQ) - 0.7)
        show_y = axes_all or c == 0
        ax.set_yticks([0, 6, 12] if shared else ax.get_yticks()[::2])
        ax.tick_params(axis="y", labelleft=show_y, labelsize=size - 2.5, length=0, colors=C.text_muted)
        ax.grid(axis="y", color=C.grid, lw=0.6)
        ax.set_xticks([0, 4], ["FY25", "FY26"] if (axes_all or r == rows - 1) else ["", ""])
        ax.tick_params(axis="x", labelsize=size - 2.5, length=0, colors=C.text_muted)
        _plain(ax, bottom=True)
        axes.append(ax)
    return axes


@exhibit
def sm_anatomy():
    fig = fig_px(640, 330)
    fig.set_layout_engine("none")
    axes = multiples(fig, rect=(0.03, 0.05, 0.97, 0.93), size=TICK)
    marker(axes[0], (len(RBQ) - 1, RBP["Oncology & Multispecialty"].iloc[-1]), 3, offset=(-30, 4))
    marker(axes[1], (2, 9), 4)
    marker(axes[2], (5, RBP[list(RBP.iloc[-1].sort_values(ascending=False).index)[2]].iloc[5]), 5, offset=(0, 14))
    marker(axes[3], (len(RBQ) - 1, 12), 6, offset=(4, -2))
    marker(axes[1], (0.66, 1.07), 7, coords="axes fraction")
    marker(axes[4], (2, 0), 8, offset=(0, -11))
    return fig, TEXT["sm_headline"] + f": Oncology {_onc.iloc[0]:.1f}% to {_onc.iloc[-1]:.1f}%."


def _sm_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    kw = dict(size=MINI - 1.5, rect=(0.04, 0.08, 0.96, 0.89), lw=1.5, mini=True)
    if kind == "scale_avoid":
        axes = multiples(fig, shared=False, context=False, **kw)
        for ax in axes:
            ax.autoscale(axis="y")
            ax.set_yticks([])
    elif kind == "scale_fix":
        multiples(fig, **kw)
    elif kind == "ctx_avoid":
        multiples(fig, context=False, **kw)
    elif kind == "ctx_fix":
        multiples(fig, **kw)
    elif kind == "order_avoid":
        multiples(fig, order=sorted(RBP.columns), **kw)
    elif kind == "order_fix":
        multiples(fig, **kw)
    elif kind == "axes_avoid":
        multiples(fig, axes_all=True, **kw)
    elif kind == "axes_fix":
        multiples(fig, **kw)
    return fig


for _k, _alt in {"scale_avoid": "Each panel on its own scale, so small wobbles look like big swings.",
                 "scale_fix": "All panels on one shared scale.",
                 "ctx_avoid": "Each panel shows only its own line.",
                 "ctx_fix": "Each panel shows the other units faintly behind its own line.",
                 "order_avoid": "Panels in alphabetical order.",
                 "order_fix": "Panels ordered by the latest value, highest first.",
                 "axes_avoid": "Axis labels repeated on every panel.",
                 "axes_fix": "Axis labels only on the outer edge."}.items():
    EXHIBITS[f"sm_bp_{_k}"] = (lambda k=_k, a=_alt: (_sm_mini(k), a))
