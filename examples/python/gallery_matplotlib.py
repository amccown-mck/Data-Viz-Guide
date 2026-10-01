"""Reference charts in matplotlib using the mckviz theme and synthetic workforce data.

    python examples/python/gallery_matplotlib.py      -> examples/output/*.png

Each function demonstrates one chart type AND the house rules: insight headline, neutral subtitle,
grey context vs. blue focus vs. orange accent, direct labels instead of legends/axes, source line.
"""
from pathlib import Path
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter, StrMethodFormatter

import mckviz as mv

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
SRC = "Source: Synthetic data for illustration only"
BAND = mv.TOKENS["chart"]["bar"]["band_fill"]
NEG_TEXT = mv.colors.negative_text
mv.use()
C = mv.colors


def bar_highlight():
    df = pd.read_csv(DATA / "attrition_by_job_family.csv").sort_values("vol_attrition_pct")
    ent = df.enterprise_rate_pct.iloc[0]
    focus = set(df.job_family[df.vol_attrition_pct > 20])
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.axvline(ent, ymin=0.02, ymax=0.98, color=C.annotation, lw=0.75, ls=(0, (3, 3)), zorder=0)
    bars = ax.barh(df.job_family, df.vol_attrition_pct, color=mv.highlight(df.job_family, focus=focus), height=BAND, zorder=2)
    mv.label_bars(ax, bars, fmt="{:.1f}%")
    ax.text(ent, len(df) - 0.35, f"Enterprise {ent:.1f}%", color=C.annotation, fontsize=9, ha="center", va="bottom")
    mv.clean_axes(ax, keep=(), grid=None)
    ax.set_xticks([])
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in focus:
            lbl.set_fontweight("bold")
            lbl.set_color(C.headline)
    mv.titles(fig, f"Two frontline job families lose about 1 in 4 people a year, well above the {ent:.1f}% enterprise rate",
              "Voluntary attrition by job family, FY26 (%)")
    mv.source(fig, SRC)
    return fig


def line_gap():
    df = pd.read_csv(DATA / "data_ai_supply_demand.csv")
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.fill_between(df.year, df.internal_supply_fte, df.demand_fte, color=C.accent, alpha=0.12, lw=0)
    ax.plot(df.year, df.demand_fte, color=C.navy, label="Demand")
    ax.plot(df.year, df.internal_supply_fte, color=C.focus, label="Internal supply")
    mv.label_line_ends(ax, fmt="{:,.0f}")
    gap = int(df.demand_fte.iloc[-1] - df.internal_supply_fte.iloc[-1])
    mid = (df.demand_fte.iloc[-1] + df.internal_supply_fte.iloc[-1]) / 2
    ax.annotate(f"Gap: {gap:,} FTE", (df.year.iloc[-1], mid), xytext=(-10, 0), textcoords="offset points",
                ha="right", va="center", fontsize=11, fontweight="bold", color=NEG_TEXT)
    mv.callout(ax, (2025, df.set_index("year").demand_fte[2025]), "Gen AI programs scale",
               "Demand growth accelerates to ~11% a year", xytext=(-40, 120))
    mv.clean_axes(ax)
    ax.set_ylim(800, df.demand_fte.max() * 1.03)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.set_xticks(df.year)
    ax.set_xlim(df.year.min() - 0.2, df.year.max() + 0.1)
    mv.titles(fig, f"Without action, Data & AI demand outruns internal supply by ~{round(gap, -1):,} FTE by 2030",
              "Forecast Data & AI roles, FTE, 2024\u20132030 (base scenario)")
    mv.source(fig, SRC, footnote=f"Supply = current headcount {mv.MINUS} projected attrition + planned internal moves; excludes external hiring.")
    return fig


def waterfall():
    df = pd.read_csv(DATA / "labor_cost_bridge.csv")
    focus = {"Automation savings", "Contractor conversion"}
    fig, ax = plt.subplots(figsize=(10, 5.6))
    running, bottoms, heights, cols = 0, [], [], []
    for r in df.itertuples():
        if r.kind == "total":
            bottoms.append(0); heights.append(r.value_musd); cols.append(C.total); running = r.value_musd
        else:
            bottoms.append(running if r.value_musd >= 0 else running + r.value_musd)
            heights.append(abs(r.value_musd))
            cols.append(C.accent if r.step in focus else C.context)
            running += r.value_musd
    x = np.arange(len(df))
    ax.bar(x, heights, bottom=bottoms, color=cols, width=BAND)
    tops = [b + h for b, h in zip(bottoms, heights)]
    for i in range(len(df) - 1):
        level = tops[i] if (df.kind[i] == "total" or df.value_musd[i] >= 0) else bottoms[i]
        ax.plot([i + BAND / 2, i + 1 - BAND / 2], [level, level], color=C.axis, lw=0.75)
    for i, r in df.iterrows():
        total = r.kind == "total"
        txt = f"{r.value_musd:,.0f}" if total else mv.signed(r.value_musd)
        ax.text(i, tops[i] + 8, txt, ha="center", va="bottom", fontsize=10, fontweight="bold" if total or r.step in focus else "medium",
                color=C.headline if total else NEG_TEXT if r.step in focus else C.text)
    ax.set_xticks(x, [textwrap.fill(s, 13) for s in df.step], fontsize=9)
    ax.set_ylim(3900, max(tops) + 45)
    for i in (0, len(df) - 1):
        for dy in (0, 14):
            ax.plot([i - BAND / 2 - 0.02, i + BAND / 2 + 0.02], [3925 + dy, 3935 + dy], color="white", lw=2.5, solid_capstyle="butt")
    mv.clean_axes(ax, grid=None)
    ax.set_yticks([])
    mv.titles(fig, "Automation and contractor conversion offset ~40% of FY26 labor cost growth",
              "Labor cost bridge, FY25 to FY26 ($M)")
    mv.source(fig, SRC, footnote="Value axis starts at $3,900M (break marks on totals) to make the drivers readable.")
    return fig


def bubble_scatter():
    df = pd.read_csv(DATA / "automation_exposure.csv")
    focus = set(df.role[df.genai_exposure_pct >= 50])
    left_side = {"Customer Care", "HR Operations", "Software Engineering"}
    below: set = set()
    fig, ax = plt.subplots(figsize=(10, 5.6))
    sizes = df.headcount / df.headcount.max() * 1800
    ax.axhspan(50, 72, color=C.surface_subtle, lw=0, zorder=0)
    ax.axhline(50, color=C.axis, lw=0.75, ls=(0, (3, 3)), zorder=1)
    ax.text(151, 71, "High exposure: 50%+ of task hours", ha="right", va="top", fontsize=8, color=C.annotation, fontweight="bold")
    ax.scatter(df.median_pay_k, df.genai_exposure_pct, s=sizes, c=mv.highlight(df.role, focus=focus),
               alpha=0.9, edgecolors="white", linewidths=1.2, zorder=2)
    for r, s in zip(df.itertuples(), sizes):
        rad = np.sqrt(s / np.pi) + 3
        bold = r.role in focus
        if r.role in below:
            off, ha, va = (0, -rad), "center", "top"
        elif r.role in left_side:
            off, ha, va = (-rad, 0), "right", "center"
        else:
            off, ha, va = (rad, 0), "left", "center"
        ax.annotate(r.role, (r.median_pay_k, r.genai_exposure_pct), xytext=off, textcoords="offset points", ha=ha, va=va,
                    fontsize=9 if bold else 8, fontweight="bold" if bold else "normal",
                    color=C.headline if bold else C.text_muted, path_effects=mv.halo(), zorder=3)
    ax.set_xlim(28, 152)
    ax.set_ylim(0, 72)
    ax.xaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}K"))
    ax.set_xlabel("Median base pay")
    ax.set_ylabel("Task hours exposed to gen AI (%)", rotation=0, ha="left", va="bottom")
    ax.yaxis.set_label_coords(0, 1.01)
    mv.clean_axes(ax, keep=("bottom",), grid="y")
    mv.titles(fig, "Four support roles carry the highest gen AI exposure \u2013 start redesign and reskilling there",
              "Gen AI exposure vs. median pay by role; bubble size = headcount")
    mv.source(fig, SRC, footnote="Exposure = share of task hours matched to gen-AI-capable activities in an external task taxonomy.")
    return fig


def dumbbell():
    df = pd.read_csv(DATA / "pay_vs_market.csv").sort_values("gap_pct").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    lag = df.gap_pct <= -5
    for i, r in df.iterrows():
        col = C.accent if lag[i] else C.focus
        ax.plot([r.market_median_k, r.internal_median_k], [i, i], color=C.context_light, lw=3, solid_capstyle="round", zorder=1)
        ax.scatter(r.market_median_k, i, s=55, color=C.context, zorder=2)
        ax.scatter(r.internal_median_k, i, s=70, color=col, zorder=3)
        ax.text(max(r.market_median_k, r.internal_median_k) + 3, i, mv.signed(r.gap_pct, 1, "%"), va="center", fontsize=9,
                color=NEG_TEXT if lag[i] else C.text, fontweight="bold" if lag[i] else "normal",
                bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
    top = 0
    r0 = df.iloc[top]
    ax.annotate("Market", (r0.market_median_k, top), xytext=(0, 9), textcoords="offset points", ha="center", va="bottom",
                fontsize=8, color=C.text_muted)
    ax.annotate("McKesson", (r0.internal_median_k, top), xytext=(0, 9), textcoords="offset points", ha="center", va="bottom",
                fontsize=8, color=NEG_TEXT, fontweight="bold")
    ax.set_yticks(range(len(df)), df.role)
    ax.invert_yaxis()
    for lbl, b in zip(ax.get_yticklabels(), lag):
        if b:
            lbl.set_fontweight("bold"); lbl.set_color(C.headline)
    ax.set_xlim(35, 160)
    ax.xaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}K"))
    mv.clean_axes(ax, keep=(), grid="x")
    mv.titles(fig, "McKesson pay trails the market by 5% or more for three clinical and pharmacy roles",
              "Median base pay, McKesson vs. external market, 2026 ($K); orange = 5%+ below market")
    mv.source(fig, SRC, footnote="External market = posted-pay median for comparable roles and metros.")
    return fig


def heatmap_diverging():
    df = pd.read_csv(DATA / "engagement_vs_benchmark.csv")
    drivers = ["Growth", "Manager support", "Recognition", "Workload", "Tools & tech", "Belonging", "Pay fairness"]
    m = df.pivot(index="business_unit", columns="driver", values="delta_vs_benchmark_pts")[drivers]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    lim = 12
    cmap = mv.diverging_cmap()
    im = ax.imshow(m.values, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
    for (i, j), val in np.ndenumerate(m.values):
        fill = matplotlib.colors.to_hex(cmap((val + lim) / (2 * lim)))
        ax.text(j, i, mv.signed(val), ha="center", va="center", fontsize=9, color=mv.text_on(fill),
                fontweight="bold" if drivers[j] == "Workload" else "medium")
    ax.set_xticks(range(len(drivers)), [d.replace(" ", "\n", 1) for d in drivers])
    ax.set_yticks(range(m.shape[0]), m.index)
    ax.xaxis.tick_top()
    ax.set_xticks(np.arange(-0.5, m.shape[1]), minor=True)
    ax.set_yticks(np.arange(-0.5, m.shape[0]), minor=True)
    ax.grid(which="minor", color="white", lw=2)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="both", length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    w = drivers.index("Workload")
    ax.add_patch(Rectangle((w - 0.5, -0.5), 1, m.shape[0], fill=False, ec=C.headline, lw=1.5, zorder=3))
    ax.get_xticklabels()[w].set_fontweight("bold")
    ax.get_xticklabels()[w].set_color(C.headline)
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.035, pad=0.03, aspect=45, ticks=[-12, -6, 0, 6, 12])
    cb.outline.set_visible(False)
    cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: mv.signed(v)))
    cb.ax.tick_params(labelsize=8, length=0, colors=C.text_muted)
    cb.set_label("Points vs. benchmark", fontsize=8, color=C.text_muted)
    cb.ax.text(-0.01, 0.5, "Below benchmark", transform=cb.ax.transAxes, ha="right", va="center", fontsize=8, color=NEG_TEXT)
    cb.ax.text(1.01, 0.5, "Above benchmark", transform=cb.ax.transAxes, ha="left", va="center", fontsize=8, color=C.focus)
    mv.titles(fig, "Workload trails the benchmark in five of six business units \u2013 Oncology most of all",
              "Engagement driver score vs. external healthcare benchmark, 2026 (points)")
    mv.source(fig, SRC)
    return fig


def slope():
    df = pd.read_csv(DATA / "skills_demand_rank.csv")
    style = {"Data analysis": C.focus, "Gen AI / prompt design": C.focus}
    fig, ax = plt.subplots(figsize=(8, 6))
    for r in df.itertuples():
        col = style.get(r.skill, C.context)
        hi = r.skill in style
        ax.plot([0, 1], [r.rank_2023, r.rank_2026], color=col, lw=2.5 if hi else 1.25, marker="o", ms=7 if hi else 5,
                zorder=3 if hi else 2)
        kw = dict(va="center", fontsize=9, color=C.headline if hi else C.text_muted, fontweight="bold" if hi else "normal")
        ax.text(-0.06, r.rank_2023, f"{r.skill}  {r.rank_2023}", ha="right", **kw)
        ax.text(1.06, r.rank_2026, f"{r.rank_2026}  {r.skill}", ha="left", **kw)
    ax.set_ylim(len(df) + 0.35, 0.2)
    ax.set_xlim(-1.0, 2.0)
    ax.axis("off")
    for x, yr in ((0, "2023"), (1, "2026")):
        ax.text(x, 0.3, yr, ha="center", fontsize=10, fontweight="bold", color=C.text)
    mv.titles(fig, "Data analysis and gen AI are the fastest-rising skills in sector job postings",
              "Rank of skills in U.S. healthcare-distribution job postings, 2023 vs. 2026")
    mv.source(fig, SRC)
    return fig


def stacked_100():
    df = pd.read_csv(DATA / "workforce_mix.csv").sort_values("contingent_pct").reset_index(drop=True)
    parts = [("employee_ft_pct", "Full-time", C.context), ("employee_pt_pct", "Part-time", C.context_light),
             ("contingent_pct", "Contingent", C.accent)]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    left = np.zeros(len(df))
    for col, name, color in parts:
        ax.barh(df.function, df[col], left=left, color=color, height=0.62, edgecolor="white", linewidth=1.5)
        for y, (l, w) in enumerate(zip(left, df[col])):
            if col == "contingent_pct":
                hi = df.function[y] == "Technology"
                ax.text(101, y, f"{w:.0f}%", ha="left", va="center", fontsize=10 if hi else 9,
                        color=NEG_TEXT, fontweight="bold" if hi else "medium")
            elif w >= 4:
                ax.text(l + w / 2, y, f"{w:.0f}%", ha="center", va="center", fontsize=9 if w >= 8 else 8, color=mv.text_on(color))
        left += df[col].values
    handles = [Rectangle((0, 0), 1, 1, color=c) for _, _, c in parts]
    ax.legend(handles, [n for _, n, _ in parts], loc="lower left", bbox_to_anchor=(0, 1.0), ncols=3, fontsize=9,
              handlelength=1, handleheight=1, borderaxespad=0.2)
    mv.clean_axes(ax, keep=(), grid=None)
    ax.set_xticks([])
    ax.set_xlim(0, 112)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() == "Technology":
            lbl.set_fontweight("bold"); lbl.set_color(C.headline)
    mv.titles(fig, "Technology uses contingent labor at ~4x the average rate of other functions",
              "Workforce composition by function, 2026 (% of workers)")
    mv.source(fig, SRC)
    return fig


def main():
    charts = {"bar-highlight": bar_highlight, "line-gap": line_gap, "waterfall": waterfall, "bubble-scatter": bubble_scatter,
              "dumbbell": dumbbell, "heatmap-diverging": heatmap_diverging, "slope": slope, "stacked-100": stacked_100}
    for name, fn in charts.items():
        fig = fn()
        print("wrote", mv.save(fig, OUT / f"{name}.png").name)
        plt.close(fig)


if __name__ == "__main__":
    main()
