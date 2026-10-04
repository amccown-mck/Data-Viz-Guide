"""Exhibits for the browsable guide (guide/pages/*.html), drawn with mckviz and returned as inline SVG.

Each exhibit is a function registered with @exhibit. It returns (figure, alt_text). tools/build_guide.py renders
every one to SVG with real text (so the page's Libre Franklin applies) and swaps it into the page wherever
{{exhibit:<name>}} appears. Numbers quoted in page text come from TEXT, filled from the same data, via {{text:<key>}}.

Sizes are in px: a figure drawn W px wide renders 1:1 when the page shows it W px wide, so font sizes here are
the on-screen sizes at the design width.
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_hex, to_rgb

import mckviz as mv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "data"

mv.use(plotly_default=False)
C = mv.colors
K = mv.TOKENS["chart"]
BAND = K["bar"]["band_fill"]  # bar : gap ~ 2 : 1

# On-screen sizes (px) at the design width. Quieter than slide sizes: the data should outweigh the type.
TICK, LABEL, ANNOT, MINI = 11.5, 11.5, 11, 10.5

plt.rcParams.update({
    "svg.fonttype": "none", "svg.hashsalt": "mck-guide", "savefig.bbox": "standard", "savefig.pad_inches": 0,
    "axes.grid": False, "xtick.labelsize": TICK, "ytick.labelsize": TICK, "font.size": LABEL,
    "xtick.major.pad": 5, "ytick.major.pad": 6, "lines.linewidth": 2,
})

# Off-brand colors that exist only to show what NOT to do (red vs. green, rainbow defaults). Never use elsewhere.
ANTI = {"red": "#D62728", "green": "#2CA02C", "rainbow": ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
                                                         "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"]}

EXHIBITS: dict = {}
TEXT: dict[str, str] = {}

# Phone versions. render_all() renders the exhibits a page marks {{exhibit:name|phone}} a second time with PHONE set:
# fig_px() narrows the figure to PHONE_W and gives it more height, marker() scales its offsets, and an exhibit can
# branch on ph(desktop, phone) for anything else (shorter labels, fewer ticks). guide.css shows that copy on phones.
PHONE = False
PHONE_W = 340                   # fits a 375-430 px phone inside the card and stage padding
_SCALE = [1.0]                      # PHONE_W / design width of the figure being drawn


def ph(desktop, phone):
    """Pick a value by medium: ph(620, 380), ph(SHORT, TINY)."""
    return phone if PHONE else desktop


def exhibit(fn):
    EXHIBITS[fn.__name__] = fn
    return fn


# ------------------------------------------------------------------ data
def _csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv")


ATTR = _csv("attrition_by_job_family").sort_values("vol_attrition_pct")          # ascending: largest bar on top
ENT = float(ATTR.enterprise_rate_pct.iloc[0])
FOCUS = set(ATTR.job_family[ATTR.vol_attrition_pct > 20])
ATTR["exits"] = (ATTR.headcount * ATTR.vol_attrition_pct / 100).round()
FOCUS_EXIT_SHARE = ATTR.exits[ATTR.job_family.isin(FOCUS)].sum() / ATTR.exits.sum() * 100
FOCUS_HEADCOUNT_SHARE = ATTR.headcount[ATTR.job_family.isin(FOCUS)].sum() / ATTR.headcount.sum() * 100
SHORT = {"Pharmacy Technician": "Pharmacy Tech", "Distribution Center Associate": "DC Associate",
         "Customer Care": "Customer Care", "Specialty Nursing": "Specialty Nursing", "Data & Analytics": "Data & Analytics",
         "Supply Chain Planning": "Supply Chain", "Sales": "Sales", "Software Engineering": "Software Eng.",
         "HR": "HR", "Finance": "Finance"}

TINY = {"Pharmacy Technician": "Rx Tech", "Distribution Center Associate": "DC", "Customer Care": "Care",
        "Specialty Nursing": "Nursing", "Data & Analytics": "Data", "Supply Chain Planning": "Supply",
        "Sales": "Sales", "Software Engineering": "Eng.", "HR": "HR", "Finance": "Finance"}

SUPPLY = _csv("data_ai_supply_demand")
FLOW = _csv("hiring_flow_by_family")
FILL = _csv("internal_fill_by_fy")

TEXT.update({
    "ent_rate": f"{ENT:.1f}%",
    "bar_headline": f"Two frontline job families lose about 1 in 4 people a year, well above the {ENT:.1f}% enterprise rate",
    "bar_subtitle": "Voluntary attrition by job family, FY26 (%)",
    "focus_exit_share": f"{FOCUS_EXIT_SHARE:.0f}%",
    "focus_headcount_share": f"{FOCUS_HEADCOUNT_SHARE:.0f}%",
    "attrition_def": "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.",
    "focus_rates": "; ".join(f"{f} {v:.1f}%" for f, v in
                             ATTR[ATTR.job_family.isin(FOCUS)].sort_values("vol_attrition_pct", ascending=False)
                             [["job_family", "vol_attrition_pct"]].itertuples(index=False)),
    "src_synthetic": "Source: Workday HCM (synthetic data for illustration), as of 31 Mar 2026; U.S. regular employees",
})


# ------------------------------------------------------------------ helpers
def fig_px(w: float, h: float, pad: float = 2):
    if PHONE:
        _SCALE[0] = PHONE_W / w
        w, h = PHONE_W, min(h * _SCALE[0] * 1.35, 480)       # narrower, and taller than a plain shrink
    else:
        _SCALE[0] = 1.0
    fig = plt.figure(figsize=(w / 72, h / 72), layout="constrained")
    fig.get_layout_engine().set(w_pad=pad / 72, h_pad=pad / 72, wspace=0.02, hspace=0.02)
    return fig


def _plain(ax, left: bool = False, bottom: bool = False) -> None:
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side == "left" and left or side == "bottom" and bottom)
    ax.spines["left"].set_color(C.axis)
    ax.spines["bottom"].set_color(C.axis)
    ax.tick_params(length=0)


def hbars(ax, labels, values, colors, *, fmt="{:.1f}%", bold=(), size=LABEL, tick=TICK, values_on=True,
          xmax=None, height=BAND, baseline=True):
    """Horizontal bars, largest at the top (pass ascending data), direct labels, no value axis."""
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, height=height, zorder=2)
    ax.set_yticks(y, labels)
    for t in ax.get_yticklabels():
        t.set_fontsize(tick)
        if t.get_text() in bold:
            t.set_fontweight(600)
            t.set_color(C.headline)
    if values_on:
        for b, v in zip(bars, values):
            ax.annotate(fmt.format(v), (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=size, color=C.text, fontweight=500,
                        zorder=5, bbox=dict(fc="white", ec="none", pad=0.6))      # keeps reference lines off labels
    ax.set_xticks([])
    ax.set_xlim(0, xmax or max(values) * 1.16)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    _plain(ax, left=baseline)
    return bars


def vbars(ax, labels, values, colors, *, fmt="{:.0f}", size=MINI, tick=MINI, values_on=True, width=BAND,
          ymax=None, bold=()):
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, width=width, zorder=2)
    ax.set_xticks(x, labels)
    for t in ax.get_xticklabels():
        t.set_fontsize(tick)
        if t.get_text() in bold:
            t.set_fontweight(600)
            t.set_color(C.headline)
    if values_on:
        for b, v in zip(bars, values):
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=size, color=C.text,
                        fontweight=500)
    ax.set_yticks([])
    ax.set_ylim(0, ymax or max(values) * 1.18)
    _plain(ax, bottom=True)
    return bars


def marker(ax, xy, n: int, *, offset=(0, 0), coords="data") -> None:
    """Numbered anatomy marker: white disc, navy ring. Reads as guide furniture, not as data."""
    offset = (offset[0] * _SCALE[0], offset[1] * _SCALE[0])
    ax.annotate(str(n), xy, xycoords=coords, xytext=offset, textcoords="offset points", ha="center", va="center",
                fontsize=10, fontweight=700, color=C.headline, zorder=10, annotation_clip=False,
                bbox=dict(boxstyle="circle,pad=0.32", fc="white", ec=C.headline, lw=1.3))


def bench(ax, x, label, *, y_text=None, size=ANNOT, vertical=True) -> None:
    if vertical:
        ax.axvline(x, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=3)
        top = ax.get_ylim()[1] if y_text is None else y_text
        ax.text(x, top, label, ha="center", va="bottom", fontsize=size, color=C.annotation,
                bbox=dict(fc="white", ec="none", pad=1.5), zorder=4)
    else:
        ax.axhline(x, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=3)
        ax.text(ax.get_xlim()[1], x, " " + label, ha="left", va="center", fontsize=size, color=C.annotation)


def _mini_attr(n: int = 5):
    d = ATTR.tail(n)
    ranked = ATTR.sort_values("vol_attrition_pct", ascending=False).job_family      # focus in value order (FOCUS is a set)
    return [SHORT[f] for f in d.job_family], d.vol_attrition_pct.tolist(), [SHORT[f] for f in ranked if f in FOCUS]


# ------------------------------------------------------------------ SVG output
def to_svg(fig, alt: str, name: str, cls: str = "ex") -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", metadata={"Date": None, "Creator": None})
    plt.close(fig)
    svg = buf.getvalue()
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.S)
    w = re.search(r'width="([\d.]+)pt"', svg).group(1)
    svg = re.sub(r'\swidth="[\d.]+pt" height="[\d.]+pt"', "", svg, count=1)
    svg = svg.replace("<svg ", f'<svg class="{cls}" style="--w:{float(w):.0f}px" role="img" aria-label="{_esc(alt)}" ', 1)
    # matplotlib ids repeat across figures (figure_1, patch_2 ...); prefix them so inline SVGs don't collide
    svg = re.sub(r'id="([^"]+)"', rf'id="{name}-\1"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', rf'url(#{name}-\1)', svg)
    svg = re.sub(r'xlink:href="#([^"]+)"', rf'xlink:href="#{name}-\1"', svg)
    return svg.strip()


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def render_all(phone: set[str] = frozenset()) -> dict[str, str]:
    """Every exhibit as inline SVG, plus a '<name>@phone' copy for the names in `phone`."""
    global PHONE
    out = {name: to_svg(*fn(), name) for name, fn in EXHIBITS.items()}
    PHONE = True
    try:
        for name in sorted(phone):
            out[name + "@phone"] = to_svg(*EXHIBITS[name](), name + "-ph", cls="ex phone")
    finally:
        PHONE = False
    return out


# ================================================================== FUNDAMENTALS
@exhibit
def shown_not_explained():
    """The same data as a 'data dump': alphabetical, one color, gridded value axis, no benchmark."""
    d = ATTR.sort_values("job_family", ascending=False)
    fig = fig_px(470, 300)
    ax = fig.add_subplot()
    ax.barh([SHORT[f] for f in d.job_family], d.vol_attrition_pct, color=C.focus, height=BAND, zorder=2)
    ax.grid(axis="x", color=C.grid, lw=0.75)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.tick_params(labelsize=TICK - 1, length=0)
    _plain(ax, left=True)
    return fig, "Bar chart of attrition by job family, sorted alphabetically, every bar the same blue, with a gridded axis."


@exhibit
def explained():
    labels = [SHORT[f] for f in ATTR.job_family]
    fig = fig_px(470, 300)
    ax = fig.add_subplot()
    hbars(ax, labels, ATTR.vol_attrition_pct, mv.highlight(ATTR.job_family, focus=FOCUS),
          bold={SHORT[f] for f in FOCUS}, size=LABEL - 1, tick=TICK - 1)
    bench(ax, ENT, f"Enterprise {ENT:.1f}%", size=ANNOT - 1)
    return fig, TEXT["bar_headline"] + ". " + TEXT["focus_rates"] + "."


def _steps_base(stage: int):
    labels = [SHORT[f] for f in ATTR.job_family]
    fig = fig_px(300, 230)
    ax = fig.add_subplot()
    show = stage >= 2
    hbars(ax, labels, ATTR.vol_attrition_pct, mv.highlight(ATTR.job_family, focus=FOCUS),
          bold={SHORT[f] for f in FOCUS} if show else (), size=MINI, tick=MINI, values_on=show, xmax=52)
    if not show:
        ax.set_yticklabels([""] * len(labels))
    if show:
        bench(ax, ENT, f"Enterprise {ENT:.1f}%", size=MINI)
    if stage == 3:
        n = len(labels)
        x = 37.5
        ax.plot([x - 0.8, x, x, x - 0.8], [n - 0.7, n - 0.7, n - 2.3, n - 2.3], color=C.annotation, lw=1)
        ax.text(x + 1.0, n - 1.5, f"{FOCUS_EXIT_SHARE:.0f}% of all\nvoluntary\nexits", ha="left", va="center",
                fontsize=MINI, color=C.annotation, fontweight=600, linespacing=1.15)
    return fig


@exhibit
def step_perceive():
    return _steps_base(1), "The same bar chart with no text: two blue bars stand out against grey bars."


@exhibit
def step_interpret():
    return _steps_base(2), "Now with labels, values and the enterprise benchmark line."


@exhibit
def step_act():
    return _steps_base(3), f"A bracket on the two blue bars notes they account for {FOCUS_EXIT_SHARE:.0f}% of all voluntary exits."


@exhibit
def line_anatomy():
    s = SUPPLY
    yr, dem, sup = s.year.values, s.demand_fte.values, s.internal_supply_fte.values
    now = 2026
    gap = int(dem[-1] - sup[-1])
    cover = sup[-1] / dem[-1] * 100
    TEXT.update(line_gap=f"{gap:,}", line_cover=f"{cover:.0f}%", line_year=str(yr[-1]),
                line_headline=f"Internal supply covers only {cover:.0f}% of Data & AI demand by {yr[-1]}, "
                              f"a gap of about {round(gap, -1):,} FTE")
    fig = fig_px(640, 330)
    ax = fig.add_subplot()
    act, fc = yr <= now, yr >= now
    spread = np.clip((yr - now) / (yr[-1] - now), 0, 1) * 0.08          # range opens from the last actual year
    lo, hi = dem * (1 - spread), dem * (1 + spread)
    ax.fill_between(yr[fc], lo[fc], hi[fc], color=C.focus, alpha=0.12, lw=0, zorder=1)
    ax.fill_between(yr[fc], sup[fc], lo[fc], color=C.negative, alpha=0.10, lw=0, zorder=1)   # shortfall = negative
    ax.plot(yr[act], dem[act], color=C.focus, lw=2.4, zorder=3)
    ax.plot(yr[fc], dem[fc], color=C.focus, lw=2.4, ls=(0, (4, 2.5)), zorder=3)
    ax.plot(yr[act], sup[act], color=C.context, lw=2.4, zorder=3)
    ax.plot(yr[fc], sup[fc], color=C.context, lw=2.4, ls=(0, (4, 2.5)), zorder=3)
    ax.axvspan(now, yr[-1] + 0.45, color=C.surface_subtle, lw=0, zorder=0)
    ax.text(now + 0.08, 1700, "Forecast", fontsize=ANNOT, color=C.text_muted, va="top")
    ax.annotate(f"Demand {dem[-1]:,}", (yr[-1], dem[-1]), xytext=(8, 0), textcoords="offset points", va="center",
                fontsize=LABEL, color=C.focus, fontweight=600)
    ax.annotate(f"Internal supply {sup[-1]:,}", (yr[-1], sup[-1]), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=LABEL, color=C.text, fontweight=500)
    mid = (dem[-1] + sup[-1]) / 2
    ax.text(yr[-1] - 0.12, mid, f"Gap {gap:,}", ha="right", va="center", fontsize=ANNOT,
            color=C.negative_text, fontweight=600)
    ax.set_xlim(2023.8, 2030.45)
    ax.set_ylim(0, 1800)
    ax.set_xticks(yr, [str(y) if not PHONE or y % 2 == 0 else "" for y in yr])
    ax.set_yticks([0, 500, 1000, 1500], ["0", "500", "1,000", "1,500"])
    ax.grid(axis="y", color=C.grid, lw=0.75)
    _plain(ax, bottom=True)
    ax.set_clip_on(False)
    marker(ax, (yr[-1], dem[-1]), 3, offset=(ph(96, 185), 14))
    marker(ax, (2025, dem[1]), 4, offset=(-10, 16))
    marker(ax, (now, 1700), 5, offset=(-12, -6))
    marker(ax, (2029, hi[5]), 6, offset=(-4, 14))
    marker(ax, (yr[-1] - 0.12, mid), 7, offset=(ph(-62, -110), 0))
    marker(ax, (2024.55, 1500), 8)
    return fig, (TEXT["line_headline"] + f". Demand reaches {dem[-1]:,} FTE and internal supply {sup[-1]:,} FTE "
                 f"in {yr[-1]}.")


@exhibit
def ladder_plain():
    labels, vals, _ = _mini_attr(6)
    fig = fig_px(300, 150)
    ax = fig.add_subplot()
    hbars(ax, labels, vals, [C.context] * len(vals), size=MINI, tick=MINI)
    return fig, "Six grey bars of attrition by job family."


@exhibit
def ladder_focus():
    labels, vals, focus = _mini_attr(6)
    fig = fig_px(300, 150)
    ax = fig.add_subplot()
    hbars(ax, labels, vals, mv.highlight(labels, focus=focus), bold=set(focus), size=MINI, tick=MINI)
    return fig, "The same six bars with the top two in blue."


def _pattern(colors, bold=()):
    labels, vals, _ = _mini_attr(6)
    fig = fig_px(280, 150)
    ax = fig.add_subplot()
    hbars(ax, labels, vals, colors(labels), bold=bold, size=MINI, tick=MINI)
    return fig


@exhibit
def pattern_focus():
    _, _, focus = _mini_attr(6)
    return _pattern(lambda l: mv.highlight(l, focus=focus), set(focus)), "Grey bars with the two highest in blue."


@exhibit
def pattern_uniform_accent():
    return (_pattern(lambda l: mv.highlight(l, accent=["Pharmacy Tech"], base=C.focus_light), {"Pharmacy Tech"}),
            "All bars light blue except the highest in navy.")


@exhibit
def pattern_focus_accent():
    return (_pattern(lambda l: mv.highlight(l, focus=["DC Associate", "Customer Care"], accent=["Pharmacy Tech"]),
                     {"Pharmacy Tech", "DC Associate", "Customer Care"}),
            "Grey bars, two in blue and the highest in navy.")


@exhibit
def palette_categorical():
    mix = _csv("workforce_mix").sort_values("employee_ft_pct")
    cols = ["employee_ft_pct", "employee_pt_pct", "contingent_pct"]
    names = ["Full-time", "Part-time", "Contingent"]
    pal = mv.categorical(3)
    fig = fig_px(300, 170)
    ax = fig.add_subplot()
    left = np.zeros(len(mix))
    for c, n, col in zip(cols, names, pal):
        ax.barh(mix.function, mix[c], left=left, color=col, height=BAND, edgecolor="white", lw=0.8)
        for i, (l, v) in enumerate(zip(left, mix[c])):
            if v >= 8:
                ax.text(l + v / 2, i, f"{v}", ha="center", va="center", fontsize=MINI - 0.5, color=mv.text_on(col))
        left += mix[c].values
    for i, (n, col) in enumerate(zip(names, pal)):                 # top-left key, in stack order
        x0 = [0, 30, 60][i]
        ax.add_patch(plt.Rectangle((x0, len(mix) - 0.28), 3.4, 0.42, color=col, clip_on=False))
        ax.text(x0 + 5, len(mix) - 0.07, n, fontsize=MINI - 0.5, color=C.text, va="center")
    ax.set_ylim(-0.55, len(mix) + 0.3)
    ax.set_xlim(-0.5, 100)
    ax.set_xticks([])
    ax.tick_params(labelsize=MINI, length=0)
    _plain(ax)
    return fig, "100% stacked bars of workforce mix by function in blue, navy and light blue."


@exhibit
def palette_sequential():
    sc = _csv("job_family_scorecard").set_index("job_family")
    v = sc[["vol_attrition_pct"]].sort_values("vol_attrition_pct", ascending=False)
    seq = mv.SEQUENTIAL["blue"]
    fig = fig_px(300, 170)
    ax = fig.add_subplot()
    cmap = mv.sequential_cmap("blue")
    lo, hi = v.values.min(), v.values.max()
    for i, (fam, val) in enumerate(v.vol_attrition_pct.items()):
        col = to_hex(cmap(0.12 + 0.8 * (val - lo) / (hi - lo)))
        ax.add_patch(plt.Rectangle((0, -i - 0.45), 1, 0.9, color=col))
        ax.text(0.5, -i, f"{val:.1f}", ha="center", va="center", fontsize=MINI - 0.5, color=mv.text_on(col))
        ax.text(-0.08, -i, SHORT.get(fam, fam), ha="right", va="center", fontsize=MINI - 0.5, color=C.text)
    ax.set_xlim(-1.6, 1.05)
    ax.set_ylim(-len(v) + 0.4, 0.6)
    ax.axis("off")
    return fig, "A heat column of attrition by job family shaded from light to dark blue."


@exhibit
def palette_diverging():
    eng = _csv("engagement_vs_benchmark")
    m = eng.pivot(index="business_unit", columns="driver", values="delta_vs_benchmark_pts")
    m = m[["Workload", "Tools & tech", "Pay fairness", "Belonging"]].iloc[:5]
    m.columns = ["Workload", "Tools", "Pay", "Belonging"]
    cmap = mv.diverging_cmap()
    fig = fig_px(300, 170)
    ax = fig.add_subplot()
    lim = 10
    for i, (bu, row) in enumerate(m.iterrows()):
        for j, val in enumerate(row):
            col = to_hex(cmap((val + lim) / (2 * lim)))
            ax.add_patch(plt.Rectangle((j, -i - 0.5), 0.96, 0.92, color=col))
            ax.text(j + 0.48, -i - 0.04, mv.signed(val), ha="center", va="center", fontsize=MINI - 1,
                    color=mv.text_on(col))
        ax.text(-0.1, -i - 0.04, bu.replace(" & Multispecialty", "").replace("U.S. ", ""), ha="right", va="center",
                fontsize=MINI - 1, color=C.text)
    for j, d in enumerate(m.columns):
        ax.text(j + 0.48, 0.55, d, ha="center", va="bottom", fontsize=MINI - 1,
                color=C.text_muted)
    ax.set_xlim(-2.1, 4)
    ax.set_ylim(-len(m) + 0.4, 1.1)
    ax.axis("off")
    return fig, "A heatmap of engagement versus benchmark, orange below and blue above, centered on zero."


@exhibit
def clutter_before():
    d = ATTR.sort_values("job_family")
    fig = fig_px(360, 230)
    ax = fig.add_subplot()
    ax.bar(range(len(d)), d.vol_attrition_pct, color=ANTI["rainbow"][:len(d)], width=0.45, edgecolor="black", lw=0.6)
    ax.set_xticks(range(len(d)), [SHORT[f] for f in d.job_family], rotation=45, ha="right", fontsize=MINI - 1)
    ax.set_ylabel("Attrition (%)", fontsize=MINI)
    ax.grid(axis="both", color="#BBBBBB", lw=0.6)
    ax.tick_params(labelsize=MINI - 1, length=4)
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color("#333333")
    ax.set_title("Attrition by Job Family", fontsize=MINI + 1, color="#333333", loc="center")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in ANTI["rainbow"][:4]], labels=["", "", "", ""],
              fontsize=MINI - 2, frameon=True, loc="upper right", ncol=2, handlelength=1)
    ax.set_facecolor("#F4F4F4")
    return fig, "A cluttered column chart: rainbow colors, borders, rotated labels, gridlines, legend and a label-style title."


@exhibit
def clutter_after():
    labels = [SHORT[f] for f in ATTR.job_family]
    fig = fig_px(360, 230)
    ax = fig.add_subplot()
    hbars(ax, labels, ATTR.vol_attrition_pct, mv.highlight(ATTR.job_family, focus=FOCUS),
          bold={SHORT[f] for f in FOCUS}, size=MINI, tick=MINI)
    bench(ax, ENT, f"Enterprise {ENT:.1f}%", size=MINI)
    return fig, "The same data as sorted horizontal bars, grey with two blue, direct labels and a labelled benchmark."


# --- honest scales minis
ENG = _csv("job_family_scorecard").sort_values("engagement_index")


@exhibit
def scale_truncated_avoid():
    d = ENG.tail(5)
    lo, hi, base = d.engagement_index.min(), d.engagement_index.max(), 65
    TEXT["trunc_real"] = f"{(hi / lo - 1) * 100:.0f}%"
    TEXT["trunc_seen"] = f"{((hi - base) / (lo - base) - 1) * 100:.0f}%"
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    ax.bar([TINY[f] for f in d.job_family], d.engagement_index, color=C.focus, width=BAND)
    ax.set_ylim(65, 78)
    ax.set_yticks([65, 70, 75])
    ax.tick_params(labelsize=MINI - 1.5, length=0)
    ax.grid(axis="y", color=C.grid)
    _plain(ax, bottom=True)
    return fig, "Columns on an axis that starts at 65, exaggerating small differences."


@exhibit
def scale_truncated_fix():
    d = ENG.tail(5)
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    y = np.arange(len(d))
    ax.hlines(y, 60, d.engagement_index, color=C.grid, lw=1.2)
    ax.scatter(d.engagement_index, y, color=C.focus, s=34, zorder=3)
    for yy, v in zip(y, d.engagement_index):
        ax.text(v + 0.6, yy, f"{v}", va="center", fontsize=MINI - 1, color=C.text)
    ax.set_yticks(y, [TINY[f] for f in d.job_family], fontsize=MINI - 1.5)
    ax.set_xlim(60, 80)
    ax.set_xticks([60, 70, 80])
    ax.tick_params(labelsize=MINI - 1.5, length=0)
    _plain(ax)
    return fig, "A dot plot of the same engagement scores on a 60 to 80 scale."


@exhibit
def scale_dual_avoid():
    s = SUPPLY
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    ax.plot(s.year, s.demand_fte, color=C.focus)
    ax2 = ax.twinx()
    ax2.plot(s.year, s.internal_supply_fte / s.demand_fte * 100, color=C.focus_light)
    for a in (ax, ax2):
        a.tick_params(labelsize=MINI - 2, length=0)
        for side in ("top",):
            a.spines[side].set_visible(False)
    ax.set_xticks([2024, 2027, 2030])
    return fig, "A dual-axis line chart where two unrelated scales make the lines appear to cross."


@exhibit
def scale_dual_fix():
    s = SUPPLY
    fig = fig_px(200, 140)
    a1, a2 = fig.subplots(2, 1, sharex=True)
    a1.plot(s.year, s.demand_fte, color=C.focus)
    a2.plot(s.year, s.internal_supply_fte / s.demand_fte * 100, color=C.focus)
    a1.text(2024, s.demand_fte.max(), "Demand (FTE)", fontsize=MINI - 2, va="top", color=C.text_muted)
    a2.text(2030, 95, "Coverage (%)", fontsize=MINI - 2, va="top", ha="right", color=C.text_muted)
    for a in (a1, a2):
        a.tick_params(labelsize=MINI - 2, length=0)
        _plain(a, bottom=True)
        a.set_yticks([])
    a2.set_xticks([2024, 2027, 2030])
    return fig, "Two aligned line charts, one per measure, sharing the time axis."


def _bubbles(area: bool):
    vals = np.array([100, 400, 900])
    r = np.sqrt(vals) if area else vals / 10
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    x = 0
    for v, rr in zip(vals, r):
        x += rr
        ax.add_patch(plt.Circle((x, 0), rr, color=C.focus if v == 900 else C.context, lw=0))
        ax.text(x, -max(r) - 6, f"{v}", ha="center", va="top", fontsize=MINI - 1, color=C.text)
        x += rr + 6
    ax.set_xlim(-4, x)
    ax.set_ylim(-max(r) - 22, max(r) + 4)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


@exhibit
def scale_bubble_avoid():
    return _bubbles(False), "Bubbles sized by diameter: the 900 bubble looks 81 times bigger than the 100 bubble."


@exhibit
def scale_bubble_fix():
    return _bubbles(True), "Bubbles sized by area: the 900 bubble is 9 times the area of the 100 bubble."


@exhibit
def scale_pie_avoid():
    d = ATTR.sort_values("headcount", ascending=False).head(8)
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    ax.pie(d.headcount, colors=ANTI["rainbow"][:8], startangle=90, wedgeprops=dict(lw=0.6, edgecolor="white"))
    ax.set_aspect("equal")
    return fig, "A pie chart with eight similar-sized slices in eight colors."


@exhibit
def scale_pie_fix():
    d = ATTR.sort_values("headcount").tail(8)
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    hbars(ax, [SHORT[f] for f in d.job_family], d.headcount / 1000,
          mv.highlight(d.job_family, focus={d.job_family.iloc[-1]}), fmt="{:.1f}K", size=MINI - 2, tick=MINI - 2)
    return fig, "The same headcounts as a sorted bar chart."


# --- accessibility minis
def _deutan(hex_color: str) -> str:
    """Simulate deuteranopia (Machado et al. 2009, severity 1) for a single color."""
    m = np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]])
    rgb = np.array(to_rgb(hex_color))
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    out = np.clip(m @ lin, 0, 1)
    srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    return to_hex(np.clip(srgb, 0, 1))


def _two_series(c1, c2, simulate=False, labels=True):
    s = _csv("hiring_flow_by_family").sort_values("hires_fy26").tail(5)
    if simulate:
        c1, c2 = _deutan(c1), _deutan(c2)
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    y = np.arange(len(s))
    ax.barh(y + 0.21, s.hires_fy26, height=0.4, color=c1)
    ax.barh(y - 0.21, s.exits_fy26, height=0.4, color=c2)
    ax.set_yticks(y, [TINY[f] for f in s.job_family], fontsize=MINI - 1.5)
    ax.set_xticks([])
    ax.tick_params(length=0)
    _plain(ax, left=True)
    if labels:
        top = len(s) - 1
        ax.text(s.hires_fy26.iloc[-1] + 60, top + 0.25, "Hires", va="center", fontsize=MINI - 2, color=C.text,
                fontweight=600)
        ax.text(s.exits_fy26.iloc[-1] + 60, top - 0.25, "Exits", va="center", fontsize=MINI - 2, color=C.text,
                fontweight=600)
    ax.set_xlim(0, 3900)
    return fig


@exhibit
def a11y_redgreen_avoid():
    return (_two_series(ANTI["green"], ANTI["red"], simulate=True),
            "Green and red bars as seen with deuteranopia: the two series look almost the same.")


@exhibit
def a11y_redgreen_fix():
    return (_two_series(C.focus, C.focus_light, simulate=True),
            "Blue and light-blue bars as seen with deuteranopia: the two series stay distinct.")


@exhibit
def a11y_legend_avoid():
    s = SUPPLY
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    ax.plot(s.year, s.demand_fte, color=C.focus, label="Demand")
    ax.plot(s.year, s.internal_supply_fte, color=mv.categorical(3)[2], label="Supply")
    ax.legend(fontsize=MINI - 2.5, loc="lower right", frameon=True)
    ax.set_xticks([2024, 2027, 2030])
    ax.tick_params(labelsize=MINI - 2, length=0)
    _plain(ax, bottom=True)
    ax.set_yticks([])
    return fig, "Two lines identified only by a color legend in the corner."


@exhibit
def a11y_legend_fix():
    s = SUPPLY
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    ax.plot(s.year, s.demand_fte, color=C.focus)
    ax.plot(s.year, s.internal_supply_fte, color=C.context)
    ax.text(2030.15, s.demand_fte.iloc[-1], "Demand", va="center", fontsize=MINI - 1.5, color=C.focus, fontweight=600)
    ax.text(2030.15, s.internal_supply_fte.iloc[-1], "Supply", va="center", fontsize=MINI - 1.5, color=C.text)
    ax.set_xlim(2023.8, 2032.2)
    ax.set_xticks([2024, 2027, 2030])
    ax.tick_params(labelsize=MINI - 2, length=0)
    _plain(ax, bottom=True)
    ax.set_yticks([])
    return fig, "The same two lines labelled directly at their ends."


def _text_on_fills(good: bool):
    fills = [C.context_light, C.focus_light, C.context, C.focus, C.total]
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    for i, f in enumerate(fills):
        ax.add_patch(plt.Rectangle((i, 0), 0.92, 1, color=f))
        col = mv.text_on(f) if good else "#FFFFFF"
        ax.text(i + 0.46, 0.5, "24%", ha="center", va="center", fontsize=MINI, color=col, fontweight=600)
    ax.set_xlim(-0.05, 5)
    ax.set_ylim(-0.1, 1.1)
    ax.axis("off")
    return fig


@exhibit
def a11y_contrast_avoid():
    return _text_on_fills(False), "White labels on every fill, unreadable on the light fills."


@exhibit
def a11y_contrast_fix():
    return _text_on_fills(True), "Navy labels on light fills and white on dark fills, all readable."


# ================================================================== MAGNITUDE: BAR
@exhibit
def bar_anatomy():
    cut = ph(22, 12)                                   # phones: short names for everything but the shortest
    labels = [SHORT[f] if len(f) > cut else f for f in ATTR.job_family]
    bold = {SHORT[f] if len(f) > cut else f for f in FOCUS}
    fig = fig_px(620, 330)
    ax = fig.add_subplot()
    bars = hbars(ax, labels, ATTR.vol_attrition_pct, mv.highlight(ATTR.job_family, focus=FOCUS), bold=bold,
                 xmax=ph(33, 39))
    bench(ax, ENT, f"Enterprise {ENT:.1f}%")
    ax.set_ylim(-1.3, len(labels) - 0.4)
    n = len(labels)
    top = bars[-1]
    after = ph(52, 95)                                 # past the value label (offsets scale down on phones)
    marker(ax, (top.get_width(), n - 1), 3, offset=(after, 0))
    marker(ax, (0, n - 2), 4, offset=(ph(-98, -175), 0))
    marker(ax, (bars[-2].get_width(), n - 2), 5, offset=(after, 0))
    marker(ax, (ENT, n - 0.35), 6, offset=(ph(-58, -120), 9))
    marker(ax, (0, -0.6), 7, offset=(0, -11))
    marker(ax, (bars[4].get_width(), 4), 8, offset=(after, 0))
    return fig, TEXT["bar_headline"] + ". " + TEXT["focus_rates"] + "; all other families are below the enterprise rate."


@exhibit
def var_column():
    d = FILL
    fig = fig_px(300, 180)
    ax = fig.add_subplot()
    vbars(ax, d.fiscal_year, d.internal_fill_pct, mv.highlight(d.fiscal_year, focus=["FY26"]), fmt="{:.0f}%",
          bold={"FY26"})
    TEXT["fill_now"], TEXT["fill_first"] = f"{d.internal_fill_pct.iloc[-1]}%", f"{d.internal_fill_pct.iloc[0]}%"
    return fig, f"Columns of internal fill rate, FY22 {d.internal_fill_pct.iloc[0]}% to FY26 {d.internal_fill_pct.iloc[-1]}%."


@exhibit
def var_grouped():
    d = FLOW.sort_values("days_to_fill_fy26", ascending=False).head(5)
    fig = fig_px(300, 180)
    ax = fig.add_subplot()
    x = np.arange(len(d))
    w = BAND / 2
    ax.bar(x - w / 2, d.days_to_fill_fy25, width=w, color=C.context_light, edgecolor="white", lw=0.8)
    b = ax.bar(x + w / 2, d.days_to_fill_fy26, width=w, color=C.focus, edgecolor="white", lw=0.8)
    for r, v in zip(b, d.days_to_fill_fy26):
        ax.text(r.get_x() + r.get_width() / 2, v + 1.5, f"{v}", ha="center", va="bottom", fontsize=MINI - 1,
                color=C.text, fontweight=500)
    ax.set_xticks(x, [SHORT[f].replace(" ", "\n", 1) if len(SHORT[f]) > 11 else SHORT[f] for f in d.job_family],
                  fontsize=MINI - 1.5)
    for x0, (lab, col) in zip((-0.45, 0.45), (("FY25", C.context_light), ("FY26", C.focus))):   # top-left key
        ax.add_patch(plt.Rectangle((x0, 83), 0.16, 4.5, color=col))
        ax.text(x0 + 0.24, 85.2, lab, fontsize=MINI - 1, color=C.text, va="center")
    ax.set_ylim(0, 90)
    ax.set_yticks([])
    ax.tick_params(length=0)
    _plain(ax, bottom=True)
    return fig, "Grouped columns of median days to fill, FY25 in light grey and FY26 in blue, for five job families."


@exhibit
def var_diverging():
    d = FLOW.sort_values("net_change_fy26")
    fig = fig_px(300, 180)
    ax = fig.add_subplot()
    y = np.arange(len(d))
    cols = [C.negative if v < 0 else C.context for v in d.net_change_fy26]          # shrinking = negative: orange
    ax.barh(y, d.net_change_fy26, color=cols, height=BAND)
    for yy, v in zip(y, d.net_change_fy26):
        ax.text(v + (8 if v >= 0 else -8), yy, mv.signed(v), va="center", ha="left" if v >= 0 else "right",
                fontsize=MINI - 1.5, color=C.negative_text if v < 0 else C.text, fontweight=500)
        ax.text(-8 if v >= 0 else 8, yy, SHORT[d.job_family.iloc[yy]], va="center",
                ha="right" if v >= 0 else "left", fontsize=MINI - 1.5, color=C.text)
    ax.axvline(0, color=C.axis, lw=0.8)
    ax.set_xlim(-330, 420)
    ax.axis("off")
    neg = d[d.net_change_fy26 < 0]
    TEXT["shrank_n"] = {1: "One", 2: "Two", 3: "Three", 4: "Four"}.get(len(neg), str(len(neg)))
    return fig, f"Diverging bars of net headcount change; {len(neg)} job families shrank, shown in orange."


@exhibit
def var_butterfly():
    d = FLOW.sort_values("hires_fy26").tail(6)
    fig = fig_px(300, 180)
    a1, a2 = fig.subplots(1, 2, sharey=True, gridspec_kw={"wspace": 0})
    y = np.arange(len(d))
    a1.barh(y, d.exits_fy26, color=C.context, height=BAND)
    a2.barh(y, d.hires_fy26, color=C.focus, height=BAND)
    a1.set_xlim(4300, 0)
    a2.set_xlim(0, 4300)
    for a in (a1, a2):
        a.set_xticks([])
        a.tick_params(length=0)
        _plain(a)
    a1.set_yticks(y, [SHORT[f] for f in d.job_family], fontsize=MINI - 1.5)
    a2.tick_params(labelleft=False)
    a1.set_title("Exits  ", fontsize=MINI - 1, color=C.text, loc="right", fontweight=600)
    a2.set_title("  Hires", fontsize=MINI - 1, color=C.focus, loc="left", fontweight=600)
    for yy, (e, h) in enumerate(zip(d.exits_fy26, d.hires_fy26)):
        a1.text(e + 60, yy, f"{e:,}", ha="right", va="center", fontsize=MINI - 2, color=C.text)
        a2.text(h + 60, yy, f"{h:,}", ha="left", va="center", fontsize=MINI - 2, color=C.text)
    return fig, "Butterfly chart of FY26 exits (left, grey) and hires (right, blue) by job family."


# --- bar best practice minis (200 x 140)
def _bp(kind: str):
    labels, vals, focus = _mini_attr(5)
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    x = np.arange(len(vals))
    tick = MINI - 2
    full = {v: k for k, v in SHORT.items()}
    short = [TINY[full[l]] for l in labels]
    if kind == "size_avoid":
        ax.bar(x, vals, width=0.12, color=C.focus)
    elif kind == "size_fix":
        ax.bar(x, vals, width=BAND, color=C.focus)
    elif kind == "color_avoid":
        ax.bar(x, vals, width=BAND, color=mv.categorical(5))
    elif kind == "color_fix":
        ax.bar(x, vals, width=BAND, color=mv.highlight(labels, focus=focus[:1]))
    elif kind == "labels_avoid":
        ax.bar(x, vals, width=BAND, color=C.focus)
        ax.grid(axis="y", color=C.grid)
        ax.set_yticks([0, 10, 20, 30])
        ax.tick_params(axis="y", labelsize=tick)
    elif kind == "labels_fix":
        vbars(ax, short, vals, [C.focus] * 5, fmt="{:.0f}%", size=tick, tick=tick)
    elif kind in ("zero_avoid", "zero_fix"):                 # engagement scores: values far from zero
        short, vals = [TINY[f] for f in _ZERO.index], _ZERO.tolist()
        ax.bar(x, vals, width=BAND, color=C.focus)
        for xx, v in zip(x, vals):
            ax.text(xx, v, f"{v:.0f}", ha="center", va="bottom", fontsize=tick, color=C.text, fontweight=500)
        if kind == "zero_avoid":
            ax.set_ylim(_ZERO_CUT, max(vals) * 1.03)
            ax.set_yticks([_ZERO_CUT])
            ax.tick_params(axis="y", labelsize=tick, colors=C.text_muted)
        else:
            ax.set_ylim(0, max(vals) * 1.16)
    if kind != "labels_fix":
        ax.set_xticks(x, short)
        if not kind.startswith(("labels_avoid", "zero_avoid")):
            ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=tick, length=0)
    ax.tick_params(axis="y", length=0)
    _plain(ax, bottom=True)
    return fig


# Zero-baseline pair: engagement index for five job families (scores sit far from zero, so a cut axis distorts most).
_ZERO = (_csv("job_family_scorecard").set_index("job_family").engagement_index
         .loc[["Data & Analytics", "Specialty Nursing", "Customer Care", "Pharmacy Technician",
               "Distribution Center Associate"]])
_ZERO_CUT = int(_ZERO.min()) - 2
TEXT["zero_cut"] = str(_ZERO_CUT)
TEXT["zero_hi"], TEXT["zero_lo"] = f"{_ZERO.max():.0f}", f"{_ZERO.min():.0f}"
TEXT["zero_fake_ratio"] = f"{(_ZERO.max() - _ZERO_CUT) / (_ZERO.min() - _ZERO_CUT):.1f}"
TEXT["zero_true_pct"] = f"{(_ZERO.max() / _ZERO.min() - 1) * 100:.0f}"


for _k, _alt in {
    "size_avoid": "Thin, stick-like bars with wide gaps.",
    "size_fix": "Bars about twice as wide as the gaps.",
    "color_avoid": "Each bar a different color.",
    "color_fix": "All bars grey except one in blue.",
    "labels_avoid": "Bars with a gridded value axis and no labels.",
    "labels_fix": "Bars labelled directly, no axis or gridlines.",
    "zero_avoid": "Engagement scores as bars on an axis cut just below the lowest score: the top bar looks several times the bottom one.",
    "zero_fix": "The same scores as bars from zero: the difference is visible at its true size.",
}.items():
    EXHIBITS[f"bp_{_k}"] = (lambda k=_k, a=_alt: (_bp(k), a))


def _bp2(kind: str):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    tick = MINI - 2
    if kind in ("sort_avoid", "sort_fix"):
        d = ATTR.tail(6)
        d = d.sort_values("job_family", ascending=False) if kind == "sort_avoid" else d
        hbars(ax, [SHORT[f] for f in d.job_family], d.vol_attrition_pct,
              [C.focus] * len(d) if kind == "sort_avoid" else mv.highlight(d.job_family, focus=FOCUS),
              size=tick, tick=tick, fmt="{:.0f}%", bold={SHORT[f] for f in FOCUS} if kind == "sort_fix" else ())
    elif kind == "rotate_avoid":
        d = ATTR.tail(6).iloc[::-1]
        ax.bar(range(6), d.vol_attrition_pct, color=C.focus, width=BAND)
        ax.set_xticks(range(6), [f for f in d.job_family], rotation=55, ha="right", fontsize=tick - 1)
        ax.set_yticks([])
        ax.tick_params(length=0)
        _plain(ax, bottom=True)
    elif kind == "rotate_fix":
        d = ATTR.tail(6)
        hbars(ax, [SHORT[f] for f in d.job_family], d.vol_attrition_pct, [C.focus] * 6, size=tick, tick=tick,
              fmt="{:.0f}%")
    elif kind in ("bench_avoid", "bench_fix"):
        d = ATTR.tail(6)
        labels = [SHORT[f] for f in d.job_family]
        hbars(ax, labels, d.vol_attrition_pct, mv.highlight(d.job_family, focus=FOCUS), size=tick, tick=tick,
              fmt="{:.0f}%", xmax=42 if kind == "bench_avoid" else 34)
        if kind == "bench_avoid":
            ax.axvline(ENT, color=C.focus_light, lw=1.2)
            ax.legend(handles=[plt.Line2D([], [], color=C.focus_light)], labels=["Benchmark"], fontsize=tick - 1,
                      loc="lower right", frameon=True)
        else:
            bench(ax, ENT, f"Enterprise {ENT:.0f}%", size=tick)
    elif kind in ("many_avoid", "many_fix"):
        d = ATTR.tail(7)
        if kind == "many_avoid":
            cols = [C.focus, C.accent, C.focus, C.accent, C.focus, C.context, C.accent]
        else:
            cols = mv.highlight(d.job_family, focus=FOCUS)
        hbars(ax, [SHORT[f] for f in d.job_family], d.vol_attrition_pct, cols, size=tick, tick=tick, fmt="{:.0f}%")
    return fig


for _k, _alt in {
    "sort_avoid": "Bars sorted alphabetically.",
    "sort_fix": "Bars sorted by value, largest on top.",
    "rotate_avoid": "Columns with long names rotated at an angle.",
    "rotate_fix": "Horizontal bars with names that read left to right.",
    "bench_avoid": "A benchmark line explained only in a legend.",
    "bench_fix": "A benchmark line labelled where it sits.",
    "many_avoid": "Five bars highlighted in two colors.",
    "many_fix": "Two bars highlighted; the rest grey.",
}.items():
    EXHIBITS[f"bp_{_k}"] = (lambda k=_k, a=_alt: (_bp2(k), a))


# ================================================================== token-driven HTML snippets ({{html:key}})
HTML: dict[str, str] = {}


def _swatch_row(values: list[str]) -> str:
    cells = "".join(f'<div style="background:{v}"></div>' for v in values)
    hexes = "".join(f"<span>{v.lstrip('#')}</span>" for v in values)
    cols = f"grid-template-columns:repeat({len(values)},1fr)"
    return f'<div class="swatches" style="{cols}">{cells}</div><div class="hexes" style="{cols}">{hexes}</div>'


HTML["swatch_categorical"] = _swatch_row(mv.CATEGORICAL[:6])
HTML["swatch_sequential"] = _swatch_row(mv.SEQUENTIAL["blue"])
HTML["swatch_diverging"] = _swatch_row(mv.DIVERGING)

_ROLES = [("context", "Context", "everything the reader should see but not focus on"),
          ("focus", "Focus", "what the headline names"),
          ("accent", "Accent", "the one exception that must pop (navy, not orange)"),
          ("focus_light", "Light blue", "the series when navy marks the exception"),
          ("negative", "Orange", "only when it means worse: below target, shrinking, a shortfall"),
          ("positive", "Green", "only when it means better, with ▲ or words"),
          ("total", "Total and benchmark", "totals, targets, reference lines"),
          ("context_light", "Context light", "de-emphasized fills in stacks and areas")]
HTML["swatch_steps"] = _swatch_row(mv.STEPS)
HTML["swatch_status"] = _swatch_row([v["value"] for k, v in mv.STATUS.items() if k != "done"])
HTML["roles"] = "".join(
    f'<div class="role"><span class="sw" style="background:{getattr(C, k)}"></span><span><strong>{n}</strong> · {d}</span>'
    f"<code>{getattr(C, k)}</code></div>" for k, n, d in _ROLES)

_TYPE = mv.TOKENS["typography"]["roles"]
_TYPE_NAMES = {"slide_title": "Slide title", "headline": "Chart headline", "subtitle": "Subtitle", "label": "Data labels", "tick": "Axis and category labels",
               "annotation": "Callouts", "footnote": "Footnote and source", "kpi": "Big number"}
_W = {300: "Light", 400: "Regular", 500: "Medium", 600: "Semibold", 700: "Bold", 800: "Extra bold"}


def _type_row(key: str) -> str:
    r = _TYPE[key]
    node = mv.TOKENS["color"]
    for part in r["color"].split("."):
        node = node[part]
    size = min(r["size_px"], 30)
    sample = {"slide_title": "Attrition is concentrated in two families",
              "headline": "Pharmacy Technicians leave at the highest rate", "subtitle": "Voluntary attrition, FY26 (%)",
              "label": "27.4%", "tick": "Pharmacy Technician", "annotation": "Hiring freeze, Q2",
              "footnote": "Source: Workday HCM, as of 31 Mar 2026", "kpi": "75%"}[key]
    return (f'<tr><td>{_TYPE_NAMES[key]}</td><td><span style="font-size:{size}px;font-weight:{r["weight"]};'
            f'color:{node["value"]};line-height:1.2">{sample}</span></td><td>{_W[r["weight"]]}</td>'
            f'<td class="num" style="white-space:nowrap">{r["size_pt"]} pt</td><td class="num" style="white-space:nowrap">{r["size_px"]} px</td></tr>')


HTML["type_specimen"] = ('<table class="spec"><thead><tr><th>Role</th><th>Sample</th><th>Weight</th><th class="num">Slide</th>'
                         '<th class="num">Screen</th></tr></thead><tbody>'
                         + "".join(_type_row(k) for k in _TYPE_NAMES) + "</tbody></table>")

# Illustrative team-level engagement results for the people-data spread (synthetic; small n on purpose).
_TEAMS = [("Inbound", 46, 71), ("Outbound", 38, 68), ("Returns", 7, 52), ("Quality", 4, 88), ("Site leadership", 9, 81)]
MIN_N = 10


def _people_table(suppress: bool) -> str:
    rows = []
    small = [t for t in _TEAMS if t[1] < MIN_N]
    big = [t for t in _TEAMS if t[1] >= MIN_N]
    shown = big + ([("Other teams (3 combined)", sum(t[1] for t in small),
                     round(sum(t[1] * t[2] for t in small) / sum(t[1] for t in small)))] if suppress else small)
    for name, n, score in shown:
        flag = (not suppress) and n < MIN_N
        style = ' style="color:var(--mck-semantic-negative-text);font-weight:600"' if flag else ""
        rows.append(f"<tr><td>{name}</td><td class=\"num\"{style}>{n}</td><td class=\"num\">{score}</td></tr>")
    return ('<table class="spec"><thead><tr><th>Team</th><th class="num">Respondents</th><th class="num">Engagement</th>'
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


HTML["people_before"] = _people_table(False)
HTML["people_after"] = _people_table(True)
TEXT["min_n"] = str(MIN_N)


# ================================================================== section modules (guide/ex_*.py)
# Each section's exhibits live in their own module and register into EXHIBITS / TEXT / HTML on import.
import importlib as _importlib  # noqa: E402

for _mod in sorted(Path(__file__).parent.glob("ex_*.py")):
    _importlib.import_module(_mod.stem)
