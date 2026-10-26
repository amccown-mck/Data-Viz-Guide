"""An options page: four ways to show the same data, on one self-contained HTML page (mv.options_page).

    python examples/python/options_page.py          -> out/options-page/genai-exposure-options.html

The scenario: a leadership group wants to discuss gen AI exposure by role, and people see the data differently. The
page shows four views, each answering its own question, with how to read it, its strength and its trade-off. The
data is synthetic (examples/data/automation_exposure.csv).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import StrMethodFormatter  # noqa: E402

import mckviz as mv  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "options-page"
SOURCE = "Source: Synthetic data for illustration only"
DEF = "Exposure = share of task hours matched to gen-AI-capable activities in an external task taxonomy."

mv.use()
C = mv.colors

df = pd.read_csv(ROOT / "examples" / "data" / "automation_exposure.csv")
df = df[df.headcount >= 10]
people = df.headcount.sum()
avg = (df.genai_exposure_pct * df.headcount).sum() / people                    # headcount-weighted
df["exposed_fte"] = df.headcount * df.genai_exposure_pct / 100                  # derived: an estimate
df["exposed_share"] = df.exposed_fte / df.exposed_fte.sum() * 100
df["band"] = pd.cut(df.genai_exposure_pct, [0, 25, 50, 101], right=False,
                    labels=["Under 25%", "25–49%", "50% or more"])


def bold_focus(ax, focus):
    for lbl in ax.get_yticklabels():
        if lbl.get_text() in focus:
            lbl.set_fontweight("bold")
            lbl.set_color(C.headline)


def benchmark(ax, value, text, top):
    ax.axvline(value, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
    ax.text(value, top, text, ha="center", va="bottom", fontsize=9, color=C.annotation,
            bbox=dict(fc="white", ec="none", pad=1))


# 1. The whole workforce in three bands -------------------------------------------------------------------------
bands = df.groupby("band", observed=False).headcount.sum() / people * 100
high = bands["50% or more"]
fig1, ax = plt.subplots(figsize=(10, 2.4))
mv.hstack(ax, ["All employees"], [(b, [bands[b]]) for b in ["50% or more", "25–49%", "Under 25%"]],
          story="50% or more", base=[people], base_label="Employees")
mv.titles(fig1, f"About 1 in 5 employees ({high:.0f}%) work in roles with half or more of their task hours exposed",
          "Employees by their role's gen AI exposure, 2026 (% of employees)")
mv.source(fig1, SOURCE, footnote=DEF)

# 2. Ranked by exposure ---------------------------------------------------------------------------------------------
r = df.sort_values("genai_exposure_pct")
top2 = r.tail(2)
focus2 = set(top2.role)
fig2, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.barh(r.role, r.genai_exposure_pct, color=mv.highlight(r.role, focus=focus2),
               height=mv.TOKENS["chart"]["bar"]["band_fill"], zorder=2)
mv.label_bars(ax, bars, fmt="{:.0f}%")
benchmark(ax, avg, f"Workforce {avg:.0f}%", len(r) - 0.4)
mv.clean_axes(ax, keep=("left",), grid=None)
ax.set_xticks([])
bold_focus(ax, focus2)
lo, hi = top2.genai_exposure_pct.min(), top2.genai_exposure_pct.max()
mv.titles(fig2, f"Claims and Customer Care work is the most exposed: {lo:.0f}–{hi:.0f}% of task hours, more than "
                f"double the {avg:.0f}% workforce average",
          "Share of task hours exposed to gen AI, by role, 2026 (%)")
mv.source(fig2, SOURCE, footnote=DEF + " Workforce average weighted by headcount.")

# 3. Where the exposed work sits ------------------------------------------------------------------------------------
s = df.sort_values("exposed_share")
top = s.tail(2)
focus3 = set(top.role)
fig3, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.barh(s.role, s.exposed_share, color=mv.highlight(s.role, focus=focus3),
               height=mv.TOKENS["chart"]["bar"]["band_fill"], zorder=2)
mv.label_bars(ax, bars, fmt="{:.0f}%")
mv.clean_axes(ax, keep=("left",), grid=None)
ax.set_xticks([])
bold_focus(ax, focus3)
pt = df.set_index("role").loc["Pharmacy Technician"]
assert list(top.role) == ["Pharmacy Technician", "Customer Care"], "the headline's names no longer hold"
mv.titles(fig3, f"Customer Care and Pharmacy Technicians hold {top.exposed_share.sum():.0f}% of exposed work, the "
                "second through sheer size",
          "Share of all exposed task hours, by role, 2026 (%)")
mv.source(fig3, SOURCE, footnote="Exposed work (an estimate) = headcount × share of task hours exposed; it assumes "
                                 "every role works the same hours.\n" + DEF)

# 4. Exposure vs. pay, sized by people (the scatter-bubble cookbook page) ---------------------------------------------
b = df.sort_values("headcount", ascending=False)
focus4 = set(top2.role)                                                         # the two most exposed
least = b.loc[b.genai_exposure_pct.idxmin()]                                    # the one exception: navy accent
named = df[df.role.isin(focus4 | {least.role})]
pay_cap = 55
assert (named.median_pay_k < pay_cap).all(), "the headline's pay claim no longer holds"
K = 1800 / b.headcount.max()                                                     # marker area per person
fig4, ax = plt.subplots(figsize=(10, 5.8))
ax.axhspan(50, 72, color=C.surface_subtle, lw=0, zorder=0)
ax.text(151, 70.5, "High exposure: 50%+ of task hours", ha="right", va="top", fontsize=9, fontweight="bold",
        color=C.annotation)
ax.axhline(avg, color=C.total, lw=0.75, ls=(0, (3, 3)), zorder=1)
ax.text(151, avg + 1, f"Workforce average {avg:.0f}%", ha="right", va="bottom", fontsize=9, color=C.annotation)
ax.scatter(b.median_pay_k, b.genai_exposure_pct, s=b.headcount * K,
           c=mv.highlight(b.role, focus=focus4, accent=least.role), alpha=0.9, edgecolors="white", linewidths=1,
           zorder=2)
for row in named.itertuples():
    pad = (row.headcount * K) ** 0.5 / 2 + 3
    left = row.role == "Customer Care"
    ax.annotate(f"{row.role}\n{row.genai_exposure_pct:.0f}%, ${row.median_pay_k:.0f}K",
                (row.median_pay_k, row.genai_exposure_pct), xytext=(-pad if left else pad, 0),
                textcoords="offset points", ha="right" if left else "left", va="center", fontsize=10,
                fontweight="bold", color=C.headline, path_effects=mv.halo(), zorder=3)
key = {1_000: 119, 5_000: 130, 10_000: 144}
ax.text(115, 21, "Headcount (bubble area)", fontsize=9, color=C.text_muted)
for v, x in key.items():
    ax.scatter(x, 10, s=v * K, color=C.context_light, edgecolors=C.axis, linewidths=0.75, zorder=2)
    ax.annotate(f"{v:,}", (x, 10), xytext=(0, -((v * K) ** 0.5 / 2 + 2)), textcoords="offset points",
                ha="center", va="top", fontsize=9, color=C.text_muted)
ax.set_xlim(28, 152)
ax.set_ylim(0, 72)
ax.xaxis.set_major_formatter(StrMethodFormatter("${x:,.0f}K"))
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}%"))
ax.set_xlabel("Median base pay")
ax.set_ylabel("Task hours exposed to gen AI", rotation=0, ha="left", va="bottom")
ax.yaxis.set_label_coords(0, 1.03)
mv.clean_axes(ax, keep=("bottom",), grid="both")
mv.titles(fig4, f"Pay doesn't predict exposure: the two most exposed roles and the least exposed are all paid under "
                f"${pay_cap}K",
          "Share of task hours exposed to gen AI vs. median base pay, by role, 2026; bubble area = headcount")
mv.source(fig4, SOURCE, footnote=DEF + " Average weighted by headcount.")

# The page ----------------------------------------------------------------------------------------------------------
cc = df.set_index("role").loc["Customer Care"]
options = [
    mv.Option(fig1, name="The workforce in three bands", question="How much of our workforce is highly exposed?",
              how_to_read="One bar for all employees, split by how exposed their role's work is.",
              strength="One number to remember, with no role singled out.",
              tradeoff="It doesn't show which roles are exposed or how much work that is.",
              alt=f"One bar: {high:.0f}% of {people:,} employees are in roles with 50% or more of task hours "
                  f"exposed, {bands['25–49%']:.0f}% in 25–49% and {bands['Under 25%']:.0f}% under 25%."),
    mv.Option(fig2, name="Roles ranked by exposure", question="Which roles have the most exposed work?",
              how_to_read="One bar per role, sorted by the share of its task hours exposed, against the workforce "
                          "average.",
              strength="Every role is visible, and the most exposed stand out at once.",
              tradeoff="It treats a role of 450 people the same as one of 11,800.",
              alt=f"Ranked bars for {len(df)} roles. Claims & Billing Specialist {hi:.0f}% and Customer Care "
                  f"{lo:.0f}% are the most exposed, against a {avg:.0f}% workforce average."),
    mv.Option(fig3, name="Where the exposed work sits", question="Where would support reach the most exposed work?",
              how_to_read="Each role's share of all exposed task hours: headcount times exposure.",
              strength="It points to where reskilling or redesign would reach the most work.",
              tradeoff="It mostly reflects headcount, it's an estimate, and it assumes every role works the same "
                       "hours.",
              alt=f"Bars of each role's share of exposed work. Customer Care {cc.exposed_share:.0f}% and Pharmacy "
                  f"Technician {pt.exposed_share:.0f}% hold {top.exposed_share.sum():.0f}% between them."),
    mv.Option(fig4, name="Exposure, pay and size in one picture",
              question="How do exposure, pay and role size relate?",
              how_to_read="Each bubble is a role: across is median pay, up is exposure, and bubble area is "
                          "headcount.",
              strength="It answers a common assumption (that lower-paid work is more exposed) with all three "
                       "measures at once.",
              tradeoff="The most technical view; it takes a moment to read, and only three roles are named.",
              alt=f"Bubble chart of {len(df)} roles. Claims & Billing Specialist ({hi:.0f}%) and Customer Care "
                  f"({lo:.0f}%) are the most exposed and {least.role} ({least.genai_exposure_pct:.0f}%) the least; "
                  f"all three are paid under ${pay_cap}K."),
]
path = mv.options_page(
    OUT / "genai-exposure-options.html",
    title="Gen AI exposure by role: four ways to show it",
    lede="Four views of the same data. Each answers a different question; use one or combine them.",
    findings=[(f"About 1 in 5 employees ({high:.0f}%) are in highly exposed roles",
               "half or more of their task hours could be done with gen AI."),
              (f"Exposure is concentrated in support roles", f"Claims and Customer Care are at {lo:.0f}–{hi:.0f}%, "
               f"against {avg:.0f}% for the workforce."),
              ("Size matters as much as exposure", f"Pharmacy Technicians hold {pt.exposed_share:.0f}% of exposed "
               f"work at only {pt.genai_exposure_pct:.0f}% exposure, because there are {pt.headcount:,.0f} of them.")],
    options=options,
    notes={"Gen AI exposure": DEF,
           "Exposed work": "Headcount × share of task hours exposed, an estimate. It assumes every role works the "
                           "same hours.",
           "Data": f"{people:,} employees in {len(df)} roles. Workforce average weighted by headcount ({avg:.1f}%)."},
    source=SOURCE,
    label="Synthetic data · For illustration")
for i, f in enumerate([fig1, fig2, fig3, fig4], 1):
    mv.save(f, OUT / f"option-{i}.png", dpi=150)                                  # to look at each chart
    for finding in mv.lint(f, quiet=True):
        print(f"option {i}: {finding}")
print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size / 1e6:.1f} MB)")
