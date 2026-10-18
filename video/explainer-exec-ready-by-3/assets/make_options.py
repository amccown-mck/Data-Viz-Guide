""""Give me 5 options" story for the explainer: five rule-compliant ways to show which job families drive attrition.

Run:  .venv/bin/python out/explainer/assets/make_options.py   (from anywhere; run make_nb.py first)
Writes raw/opt1..5.png via mv.save, frames every raw/*.png onto a 1920x1080 white canvas as <name>.png, and
writes options.json with each option's computed headline, subtitle and real mv.lint findings.
"""
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from PIL import Image

import mckviz as mv

mv.use()
C = mv.colors
REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "examples/data"
ASSETS = Path(__file__).resolve().parent
RAW = ASSETS / "raw"
RAW.mkdir(exist_ok=True)
BAND = mv.TOKENS["chart"]["bar"]["band_fill"]
KPI = mv.TOKENS["typography"]["roles"]["kpi"]
SRC = "Source: Synthetic HRIS data for illustration only; FY26, all job families"
DEF = "Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months"
WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}

att = pd.read_csv(DATA / "attrition_by_job_family.csv")
ENT = att.enterprise_rate_pct.iloc[0]
TOP = att.nlargest(2, "vol_attrition_pct")
FOCUS = set(TOP.job_family)


def bold_focus(labels, focus):
    for t in labels:
        if t.get_text() in focus:
            t.set(fontweight="bold", color=C.headline)


def opt1():
    df = att.sort_values("vol_attrition_pct").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.barh(df.job_family, df.vol_attrition_pct, color=mv.highlight(df.job_family, focus=FOCUS),
                   height=BAND, zorder=2)
    mv.label_bars(ax, bars, fmt="{:.1f}%")
    ax.axvline(ENT, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
    ax.text(ENT, len(df) - 0.4, f"Enterprise {ENT:.1f}%", ha="center", va="bottom", fontsize=9, color=C.annotation,
            bbox=dict(fc="white", ec="none", pad=1))
    mv.clean_axes(ax, keep=("left",), grid=None)
    ax.set_xticks([])
    bold_focus(ax.get_yticklabels(), FOCUS)
    k = round(100 / TOP.vol_attrition_pct.mean())
    head = (f"Pharmacy technicians and distribution center associates lose about 1 in {k} people a year, "
            f"well above the {ENT:.1f}% enterprise rate")
    sub = "Voluntary attrition by job family, FY26 (%)"
    mv.titles(fig, head, sub)
    mv.source(fig, SRC, footnote=DEF + ". Enterprise rate = headcount-weighted rate across all job families.")
    return fig, "Ranked bar with reference line", head, sub, \
        "The classic: ranks every family and shows the two clearly above the enterprise line, so the 'who' is instant"


def opt2():
    df = att.sort_values("vol_attrition_pct", ascending=False).reset_index(drop=True)
    df["gap"] = df.vol_attrition_pct - ENT
    above = df[df.gap > 0]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    gap_x = 33.5
    for i, r in df.iterrows():
        hi = r.job_family in FOCUS
        ax.plot([ENT, r.vol_attrition_pct], [i, i], color=C.context_light, lw=3, solid_capstyle="round", zorder=1)
        ax.scatter(r.vol_attrition_pct, i, s=80 if hi else 55, color=C.focus if hi else C.context, zorder=3)
        ax.text(gap_x, i, mv.signed(r.gap, 1), ha="right", va="center", fontsize=10,
                color=C.headline if hi else C.text, fontweight="bold" if hi else "normal")
    ax.text(gap_x, -0.85, "Gap vs. enterprise (pts)", ha="right", va="bottom", fontsize=9, color=C.text_muted,
            bbox=dict(fc="white", ec="none", pad=1))
    ax.axvline(ENT, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=2)
    ax.text(ENT, -0.85, f"Enterprise {ENT:.1f}%", ha="center", va="bottom", fontsize=9, color=C.annotation,
            bbox=dict(fc="white", ec="none", pad=1))
    ax.set_yticks(range(len(df)), df.job_family)
    ax.set_ylim(len(df) - 0.5, -1.0)
    ax.set_xlim(5, gap_x + 0.3)
    ax.set_xticks(range(5, 31, 5), [f"{v}%" for v in range(5, 31, 5)])
    mv.clean_axes(ax, keep=(), grid="x")
    ax.tick_params(length=0)
    bold_focus(ax.get_yticklabels(), FOCUS)
    g = above.gap.round(1).tolist()
    head = (f"Only {WORDS[len(above)].lower()} job families run above the {ENT:.1f}% enterprise rate, "
            f"by {g[0]:.1f} and {g[1]:.1f} points")
    sub = "Voluntary attrition by job family vs. the enterprise rate, FY26 (%; gap in percentage points)"
    mv.titles(fig, head, sub)
    mv.source(fig, SRC, footnote=DEF + ". Enterprise rate = headcount-weighted rate across all job families.")
    assert len(above) == 2 and set(above.job_family) == FOCUS
    return fig, "Deviation dot plot vs. enterprise rate", head, sub, \
        "Turns the benchmark into the axis of the story: everyone else sits below the line, only two families sit above it"


def opt3():
    q = pd.read_csv(DATA / "attrition_quarterly.csv")
    q["fy"] = q.quarter.str[-4:]
    fy = q.groupby(["job_family", "fy"]).attrition_pct.mean().unstack()[["FY25", "FY26"]].round(1)
    fy["chg"] = fy.FY26 - fy.FY25
    style = {"Pharmacy Technician": C.focus, "Distribution Center Associate": C.accent}
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for name, r in sorted(fy.iterrows(), key=lambda kv: kv[0] in style):          # context first, focus on top
        col = style.get(name, C.context)
        hi = name in style
        ax.plot([0, 1], [r.FY25, r.FY26], color=col, lw=2.25 if hi else 1.25, marker="o", ms=7 if hi else 5,
                zorder=3 if hi else 2)
        kw = dict(va="center", fontsize=10, color=C.headline if hi else C.text_muted,
                  fontweight="bold" if hi else "normal")
        ax.text(-0.05, r.FY25, f"{name}  {r.FY25:.1f}%", ha="right", **kw)
        ax.text(1.05, r.FY26, f"{r.FY26:.1f}%  {name}  ({mv.signed(r.chg, 1)} pts)", ha="left", **kw)
    for x, yr in ((0, "FY25"), (1, "FY26")):
        ax.text(x, 36.2, yr, ha="center", va="bottom", fontsize=11, fontweight="bold", color=C.text)
    ax.set_xlim(-1.15, 2.25)
    ax.set_ylim(5, 37.5)
    ax.axis("off")
    pt, dc = fy.loc["Pharmacy Technician"], fy.loc["Distribution Center Associate"]
    head = (f"Pharmacy technician attrition fell {abs(pt.chg):.1f} points in FY26, but distribution center "
            f"associates barely moved at {dc.FY26:.1f}%")
    sub = f"Voluntary attrition, FY25 vs. FY26, {len(fy)} tracked job families (%)"
    mv.titles(fig, head, sub)
    mv.source(fig, SRC.replace("all job families", "the six job families tracked quarterly"),
              footnote=DEF + ". Annual rate = mean of the four quarterly rates in the fiscal year.")
    assert abs(dc.chg) < 0.5 and pt.chg == fy.chg.min()
    return fig, "Slope chart (FY25 to FY26)", head, sub, \
        "Adds the 'so what next': one driver is improving fast, the other is stuck, which points the exec at DC associates"


def opt4():
    df = pd.read_csv(DATA / "job_family_scorecard.csv").sort_values("vol_attrition_pct", ascending=False)
    df = df.reset_index(drop=True)
    cols = [("headcount", "Headcount", "{:,.0f}"), ("vol_attrition_pct", "Voluntary\nattrition (%)", "{:.1f}"),
            ("attrition_change_pts", "Change vs.\nFY25 (pts)", None), ("median_days_to_fill", "Median\ndays to fill", "{:.0f}"),
            ("internal_fill_pct", "Internal fill\nrate (%)", "{:.0f}"), ("engagement_index", "Engagement\nindex", "{:.0f}")]
    focus = set(df.job_family[df.vol_attrition_pct > 20])
    ramp = mv.SEQUENTIAL["blue"]
    n = len(df)
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(n + 0.6, -1.3)
    ax.axis("off")
    xs = [4.75, 5.85, 6.85, 7.85, 8.9, 9.95]
    for x, (_, h, _) in zip(xs, cols):
        ax.text(x, -0.55, h, ha="right", va="bottom", fontsize=9, fontweight="bold", color=C.headline, linespacing=1.15)
    ax.plot([0, 10], [-0.45, -0.45], color=C.axis, lw=0.75)
    bar_max = df.headcount.max()
    for i, r in df.iterrows():
        hi = r.job_family in focus
        weight, color = ("bold", C.headline) if hi else ("normal", C.text)
        ax.text(0, i, r.job_family, va="center", fontsize=10, fontweight=weight, color=color)
        ax.barh(i, 1.0 * r.headcount / bar_max, left=2.75, height=0.42, color=C.focus if hi else C.context)
        for x, (key, _, fmt) in zip(xs, cols):
            v = r[key]
            txt = mv.signed(v, 1) if fmt is None else fmt.format(v)
            tc = color
            if key == "vol_attrition_pct":
                fill = ramp[min(int(v // 5), len(ramp) - 1)]
                ax.add_patch(Rectangle((x - 0.85, i - 0.42), 0.95, 0.84, color=fill, lw=0))
                tc = mv.text_on(fill)
            if key == "attrition_change_pts" and v > 0:
                tc = C.negative_text
            ax.text(x, i, txt, ha="right", va="center", fontsize=10, fontweight=weight, color=tc)
        ax.plot([0, 10], [i + 0.5, i + 0.5], color=C.grid, lw=0.75)
    ax.plot([0, 10], [n - 0.5, n - 0.5], color=C.total, lw=1.25)
    w = lambda c: np.average(df[c], weights=df.headcount)
    total = [f"{df.headcount.sum():,.0f}", f"{w('vol_attrition_pct'):.1f}", mv.signed(w("attrition_change_pts"), 1),
             f"{w('median_days_to_fill'):.0f}", f"{w('internal_fill_pct'):.0f}", f"{w('engagement_index'):.0f}"]
    ax.text(0, n + 0.15, f"All {n} job families", va="center", fontsize=10, fontweight="bold", color=C.headline)
    for x, t in zip(xs, total):
        ax.text(x, n + 0.15, t, ha="right", va="center", fontsize=10, fontweight="bold", color=C.headline)
    lowest_eng = df.nsmallest(2, "engagement_index")
    assert focus == set(lowest_eng.job_family) == set(df.nlargest(2, "headcount").job_family)
    engs = sorted(lowest_eng.engagement_index.astype(int))
    floor = math.floor(df[df.job_family.isin(focus)].vol_attrition_pct.min())
    head = (f"The two largest frontline job families combine attrition above {floor}% with the lowest "
            f"engagement scores ({engs[0]} and {engs[1]})")
    sub = "Workforce scorecard by job family, FY26; totals weighted by headcount"
    mv.titles(fig, head, sub)
    mv.source(fig, "Source: Synthetic HRIS, ATS and engagement-survey data for illustration only; FY26",
              footnote="Attrition shaded in 5-point classes. Orange change = attrition rising vs. FY25. "
                       "Internal fill rate = share of filled requisitions filled by current employees.")
    return fig, "Heat table / scorecard", head, sub, \
        "For the exec who asks 'why': shows the two attrition drivers are also the biggest populations with the weakest engagement"


def opt5():
    df = att.assign(exits=att.headcount * att.vol_attrition_pct / 100)
    top = df[df.job_family.isin(FOCUS)]
    exit_share = 100 * top.exits.sum() / df.exits.sum()
    hc_share = 100 * top.headcount.sum() / df.headcount.sum()
    fig, (num, ax) = plt.subplots(1, 2, figsize=(10, 4.6), width_ratios=[1.15, 1])
    num.axis("off")
    num.text(0, 0.98, f"{exit_share:.0f}%", transform=num.transAxes, va="top", ha="left",
             fontsize=KPI["size_pt"] * 0.75 * 1.6, fontweight=KPI["weight"], color=C.headline)
    num.text(0, 0.52, f"About {round(top.exits.sum(), -2):,.0f} of {round(df.exits.sum(), -2):,.0f} voluntary exits\n"
                      "in FY26 came from pharmacy technicians\nand distribution center associates",
             transform=num.transAxes, va="top", fontsize=13, color=C.text, linespacing=1.35)
    num.text(0, 0.12, f"{mv.signed(exit_share - hc_share)} pts above their {hc_share:.0f}% share of headcount",
             transform=num.transAxes, va="top", fontsize=12, fontweight="semibold", color=C.headline)
    rows = [("Share of headcount", hc_share, C.context), ("Share of voluntary exits", exit_share, C.focus)]
    ys = [1.6, 0.4]                                                  # headcount on top, exits below
    bars = ax.barh(ys, [v for _, v, _ in rows], color=[c for _, _, c in rows], height=0.5)
    mv.label_bars(ax, bars, fmt="{:.0f}%")
    for y, (name, _, _) in zip(ys, rows):                            # category labels directly above each bar
        hi = "exits" in name
        ax.text(0, y + 0.32, name, va="bottom", fontsize=11, color=C.headline if hi else C.text,
                fontweight="bold" if hi else "normal")
    ax.text(0, 2.45, "Pharmacy technicians + distribution center associates", fontsize=10, color=C.text_muted,
            va="bottom")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.1, 2.75)
    ax.set_xticks([])
    ax.set_yticks([])
    mv.clean_axes(ax, keep=("left",), grid=None)
    head = (f"Two job families account for {exit_share:.0f}% of voluntary exits but only "
            f"{hc_share:.0f}% of headcount")
    sub = "Share of voluntary exits and of headcount, two highest-attrition job families, FY26 (%)"
    mv.titles(fig, head, sub)
    mv.source(fig, SRC, footnote="Exits estimated as headcount × voluntary attrition rate for each job family; "
                                 "shares are of all 10 job families.")
    return fig, "Big-number KPI with supporting comparison", head, sub, \
        "One number an exec remembers: nearly three-quarters of the exit problem sits in two families"


def frame(src: Path, dst: Path, W=1920, H=1080, margin=24):
    im = Image.open(src).convert("RGB")
    scale = min((W - 2 * margin) / im.width, (H - 2 * margin) / im.height, 1.0)
    if scale < 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "white")
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    canvas.save(dst, optimize=True)


options = []
for i, build in enumerate([opt1, opt2, opt3, opt4, opt5], 1):
    fig, kind, head, sub, why = build()
    findings = mv.lint(fig, quiet=True)
    print(f"opt{i}", kind, "->", [str(f) for f in findings] or "no findings")
    mv.save(fig, RAW / f"opt{i}.png", dpi=200)
    plt.close(fig)
    options.append({"file": f"opt{i}.png", "chart_type": kind, "headline": head, "subtitle": sub, "why": why,
                    "lint": {"errors": sum(f.level == "error" for f in findings),
                             "findings": [str(f) for f in findings]}})

prompt = ("I'm trying to show which job families are driving attrition. Can you give me 5 options I could pop into "
          "this exec's deck right now to fit this storyline?")
(ASSETS / "options.json").write_text(json.dumps({"prompt": prompt, "data": "Synthetic (examples/data)",
                                                 "options": options}, indent=2, ensure_ascii=False), encoding="utf-8")
for p in sorted(RAW.glob("*.png")):
    frame(p, ASSETS / p.name)
    print(p.name, Image.open(p).size, "->", Image.open(ASSETS / p.name).size)
