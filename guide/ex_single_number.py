"""Single-number exhibits: big-number KPI card (HTML), progress ring, KPI rows, best practice. Registered on import."""
from __future__ import annotations

import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, Wedge

import mckviz as mv
from exhibits import ANNOT, ANTI, BAND, HTML, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px, marker

KPI = mv.TOKENS["typography"]["roles"]["kpi"]                 # Light 300, 56 px on screen
UP, DOWN, M = "▲", "▼", mv.MINUS


# ------------------------------------------------------------------ helpers
def ring(ax, cx, cy, R, value, *, w=None, color=C.focus, track=C.context_light, target=None, start=90):
    """Single-% ring: starts at 12 o'clock, runs clockwise, stroke ~18% of the radius, no caps or gaps."""
    w = w or R * 0.18
    end = start - 360 * value / 100
    ax.add_patch(Wedge((cx, cy), R, end, start, width=w, color=color, lw=0))
    ax.add_patch(Wedge((cx, cy), R, start, end + 360, width=w, color=track, lw=0))
    if target is not None:
        t = np.deg2rad(start - 360 * target / 100)
        ax.plot([cx + (R - w - R * 0.07) * np.cos(t), cx + (R + R * 0.07) * np.cos(t)],
                [cy + (R - w - R * 0.07) * np.sin(t), cy + (R + R * 0.07) * np.sin(t)], color=C.total, lw=1.8,
                solid_capstyle="butt", zorder=4)
        return t
    return None


def canvas(w=200, h=140):
    fig = fig_px(w, h)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def big(ax, x, y, s, size, *, weight=KPI["weight"], color=C.headline, ha="left", va="baseline"):
    ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va)


def small(ax, x, y, s, size=MINI - 2, *, color=C.text, weight=400, ha="left", va="baseline"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, linespacing=1.3)


# ------------------------------------------------------------------ data
SC = _csv("succession_coverage_bu")
SC_ROLES = int(SC.critical_roles.sum())
SC_NOW, SC_PRIOR = int(SC.ready_now_mar26.sum()), int(SC.ready_now_mar25.sum())
SC_PCT, SC_PCT0 = round(SC_NOW / SC_ROLES * 100), round(SC_PRIOR / SC_ROLES * 100)
SC_TGT = int(SC.target_pct.iloc[0])
SC_D, SC_GAP = SC_PCT - SC_PCT0, SC_TGT - SC_PCT
SC["pct"] = SC.ready_now_mar26 / SC.critical_roles * 100
TEXT.update(
    sc_headline=f"Succession coverage rose {SC_D} points in a year but is still {SC_GAP} short of the {SC_TGT}% target",
    sc_subtitle=f"Critical roles with at least one ready-now successor, Mar 2026 (% of {SC_ROLES} roles)",
    sc_pct=f"{SC_PCT}%", sc_tgt=f"{SC_TGT}%", sc_d=str(SC_D),
    sc_base=f"{SC_NOW} of {SC_ROLES} critical roles", sc_check=f"{SC_PCT}% × {SC_ROLES} ≈ {SC_NOW}")

SP = _csv("skills_profile_completion")
SP_EMP, SP_NOW, SP_PRIOR = int(SP.employees.sum()), int(SP.profiles_mar26.sum()), int(SP.profiles_mar25.sum())
SP_PCT, SP_PCT0 = round(SP_NOW / SP_EMP * 100), round(SP_PRIOR / SP_EMP * 100)
SP_TGT = int(SP.target_pct.iloc[0])
assert 64 <= SP_PCT <= 70                                     # "two in three" in the headline
SP["pct"] = SP.profiles_mar26 / SP.employees * 100
TEXT.update(
    sp_headline=(f"Two in three employees now have a verified skills profile, {SP_TGT - SP_PCT} points short of "
                 f"the {SP_TGT}% target"),
    sp_subtitle=f"Employees with a verified skills profile, Mar 2026 (% of {SP_EMP / 1000:.1f}K employees)",
    sp_tgt=f"{SP_TGT}%")

FILL = _csv("internal_fill_by_fy")
FL_NOW, FL_PRIOR = int(FILL.internal_fill_pct.iloc[-1]), int(FILL.internal_fill_pct.iloc[-2])
FLOW = _csv("hiring_flow_by_family")
DTF_NOW = (FLOW.days_to_fill_fy26 * FLOW.hires_fy26).sum() / FLOW.hires_fy26.sum()
DTF_PRIOR = (FLOW.days_to_fill_fy25 * FLOW.hires_fy26).sum() / FLOW.hires_fy26.sum()
DTF_D = round(DTF_NOW) - round(DTF_PRIOR)
IDX = _csv("data_ai_index")
_low = SC.sort_values("pct").iloc[0]
TEXT.update(fill_now_sn=f"{FL_NOW}%", fill_d=mv.signed(FL_NOW - FL_PRIOR),
            sc_low_bu=_low.business_unit.split(" &")[0], sc_low_pct=f"{_low.pct:.0f}%",
            sc_below_n=str(int((SC.pct < SC_TGT).sum())), sc_bu_n=str(len(SC)),
            sp_low_fn=SP.sort_values("pct").function.iloc[0], sp_low_pct=f"{SP.pct.min():.0f}%",
            dtf_now=f"{round(DTF_NOW)}", dtf_d=mv.signed(DTF_D), dtf_up=f"{abs(DTF_D)} days")
assert DTF_D > 0                                              # page text: "days to fill rose"

# KPI row cards: (name, value, delta text, favorable?)
ROW = [("Internal fill rate", f"{FL_NOW}%", f"{UP} {mv.signed(FL_NOW - FL_PRIOR)} pts vs. FY25", True),
       ("Days to fill", f"{round(DTF_NOW)}", f"{UP if DTF_D > 0 else DOWN} {mv.signed(DTF_D)} days vs. FY25", DTF_D <= 0),
       ("Succession coverage", f"{SC_PCT}%", f"{UP} {mv.signed(SC_D)} pts vs. Mar 2025", True)]


# ================================================================== BIG NUMBER (HTML card body)
HTML["kpi_anatomy"] = f"""<div class="kpi-ana">
  <div class="kpi-main">
    <p class="kpi-num">{SC_PCT}%<span class="mk">3</span></p>
    <div>
      <p class="kpi-sent">{SC_NOW} of {SC_ROLES} critical roles have at least one ready-now successor<span class="mk">4</span></p>
      <p class="kpi-delta good">{UP} {mv.signed(SC_D)} pts vs. Mar 2025 ({SC_PCT0}%)<span class="mk">5</span></p>
      <p class="kpi-delta bad">{SC_GAP} pts short of the {SC_TGT}% FY27 target<span class="mk">6</span></p>
    </div>
  </div>
  <div class="kpi-track-row">
    <div class="kpi-track" role="img" aria-label="Progress bar: {SC_PCT}% of 100%, target {SC_TGT}%">
      <div class="fill" style="width:{SC_PCT}%"></div>
      <div class="tgt" style="left:{SC_TGT}%"><span>Target {SC_TGT}%</span></div>
    </div><span class="mk">7</span>
  </div>
  <div class="kpi-scale"><span>0%</span><span>100%</span></div>
</div>"""


# ================================================================== RING
@exhibit
def sn_ring_anatomy():
    fig = fig_px(620, 290)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1.75, 4.6)
    ax.set_ylim(-1.45, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    t = ring(ax, 0, 0, 1.25, SP_PCT, target=SP_TGT)
    ax.text((1.25 + 0.14) * np.cos(t), (1.25 + 0.14) * np.sin(t), f"Target\n{SP_TGT}%", ha="right", va="center",
            fontsize=ANNOT, color=C.annotation, linespacing=1.15)
    big(ax, 0, 0.02, f"{SP_PCT}%", KPI["size_px"] - 4, ha="center", va="center")
    x = 1.75
    small(ax, x, 0.62, f"{SP_NOW / 1000:.1f}K of {SP_EMP / 1000:.1f}K employees have a verified\nprofile in the "
                       "skills inventory", size=LABEL + 2.5, va="top")
    small(ax, x, -0.25, f"{UP} {mv.signed(SP_PCT - SP_PCT0)} pts vs. Mar 2025 ({SP_PCT0}%)", size=LABEL + 1,
          color=C.positive_text, weight=600, va="center")
    small(ax, x, -0.62, f"{SP_TGT - SP_PCT} pts short of the {SP_TGT}% FY27 target", size=LABEL + 1,
          color=C.negative_text, weight=600, va="center")
    marker(ax, (0, 1.25), 3, offset=(0, 14))
    marker(ax, (1.25, 0), 4, offset=(14, 0))
    marker(ax, (0, -0.52), 5)
    marker(ax, ((1.25 + 0.14) * np.cos(t), (1.25 + 0.14) * np.sin(t)), 6, offset=(-62, 0))
    marker(ax, (0, -1.25), 7, offset=(0, -13))
    marker(ax, (x, 0.45), 8, offset=(-16, 0))
    return fig, (TEXT["sp_headline"] + f": {SP_PCT}% of {SP_EMP:,} employees, up {SP_PCT - SP_PCT0} points from "
                 f"{SP_PCT0}% in Mar 2025.")


# ================================================================== VARIANTS (300 x 190)
@exhibit
def sn_var_spark():
    fig, ax = canvas(300, 190)
    small(ax, 0, 160, "Internal fill rate, FY26", size=MINI - 1)
    big(ax, 0, 98, f"{FL_NOW}%", 44)
    small(ax, 0, 70, f"{UP} {mv.signed(FL_NOW - FL_PRIOR)} pts vs. FY25 ({FL_PRIOR}%)", size=MINI - 1,
          color=C.positive_text, weight=600)
    small(ax, 0, 34, "of open roles were filled by\ninternal candidates", size=MINI - 1.5, va="baseline")
    sx = fig.add_axes([0.58, 0.4, 0.34, 0.36])
    v = FILL.internal_fill_pct.values
    sx.plot(range(len(v)), v, color=C.focus, lw=1.6)
    sx.plot(len(v) - 1, v[-1], "o", ms=4, color=C.focus)
    sx.set_ylim(min(v) - 4, max(v) + 3)
    sx.set_xticks([0, len(v) - 1], [FILL.fiscal_year.iloc[0], FILL.fiscal_year.iloc[-1]])
    sx.set_yticks([])
    sx.tick_params(labelsize=MINI - 2.5, length=0, colors=C.text_muted)
    _plain(sx)
    return fig, f"Big number {FL_NOW}% internal fill rate with a sparkline FY22–FY26 and +{FL_NOW - FL_PRIOR} pts vs. FY25."


@exhibit
def sn_var_bars():
    d = SC.sort_values("pct")
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.3, 0.04, 0.6, 0.8])
    y = np.arange(len(d))
    ax.barh(y, [100] * len(d), color=C.grid, height=0.5, lw=0)
    cols = [C.focus if b == _low.business_unit else C.context for b in d.business_unit]
    ax.barh(y, d.pct, color=cols, height=0.5, lw=0)
    for yy, v in zip(y, d.pct):
        ax.text(101.5, yy, f"{v:.0f}%", va="center", fontsize=MINI - 2, color=C.text)
    ax.vlines(SC_TGT, -0.45, len(d) - 0.55, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)))
    ax.text(SC_TGT, len(d) - 0.45, f"Target {SC_TGT}%", ha="center", va="bottom", fontsize=MINI - 2.5,
            color=C.annotation)
    names = [b.replace(" & Multispecialty", "").replace("U.S. Pharmaceutical", "U.S. Pharma")
             .replace("Medical-Surgical", "Med-Surg") for b in d.business_unit]
    ax.set_yticks(y, names)
    for tl, b in zip(ax.get_yticklabels(), d.business_unit):
        tl.set_fontsize(MINI - 2)
        if b == _low.business_unit:
            tl.set_fontweight(700)
            tl.set_color(C.headline)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(d) + 0.1)
    ax.set_xticks([])
    _plain(ax)
    return fig, (f"Progress bars of succession coverage by business unit on a 0–100% track with the {SC_TGT}% target; "
                 f"{TEXT['sc_low_bu']} lowest at {TEXT['sc_low_pct']}.")


@exhibit
def sn_var_dials():
    d = SP.sort_values("pct", ascending=False)
    fig, ax = canvas(300, 190)
    ax.set_aspect("equal")
    n = len(d)
    low = d.function.iloc[-1]
    for i, (fn, v) in enumerate(zip(d.function, d.pct)):
        cx = 30 + i * 60
        hot = fn == low
        ring(ax, cx, 105, 25, v, color=C.focus if hot else C.context, track=C.grid, w=4.5)
        ax.text(cx, 105, f"{v:.0f}%", ha="center", va="center", fontsize=MINI + (1.5 if hot else 0.5),
                color=C.headline, fontweight=600 if hot else 400)
        ax.text(cx, 72, fn.replace(" ", "\n", 1), ha="center", va="top", fontsize=MINI - 1.5, linespacing=1.1,
                color=C.headline if hot else C.text, fontweight=700 if hot else 400)
    return fig, (f"Five rings of skills-profile completion by function, highest to lowest; {low} lowest at "
                 f"{d.pct.iloc[-1]:.0f}% in blue.")


def kpi_row(ax, x0, y0, w, cards, *, num=28, name=MINI - 2, delta=MINI - 2.5, mixed=False, sep=True):
    for i, (nm, val, dl, good) in enumerate(cards):
        x = x0 + i * w
        if sep and i:
            ax.plot([x - 8, x - 8], [y0 - 52, y0 + 18], color=C.grid, lw=0.8)
        if mixed and i == 1:                                    # anti-example: a different order and look
            ax.text(x + w / 2 - 8, y0 - 18, val, fontsize=num - 4, fontweight=700, color=C.focus, ha="center")
            ax.text(x + w / 2 - 8, y0 + 8, nm.upper(), fontsize=name - 1.5, color=C.text_muted, ha="center")
            continue
        if mixed and i == 2:
            ax.add_patch(Rectangle((x - 2, y0 - 50), w - 12, 66, fc=C.surface_subtle, ec=C.axis, lw=0.8))
            ax.text(x + 3, y0 + 4, nm, fontsize=name - 1, color=C.text, fontstyle="italic")
            ax.text(x + 3, y0 - 30, val, fontsize=num - 8, fontweight=400, color=C.text)
            continue
        ax.text(x, y0 + 4, nm, fontsize=name, color=C.text)
        ax.text(x, y0 - 28, val, fontsize=num, fontweight=KPI["weight"], color=C.headline)
        ax.text(x, y0 - 48, dl, fontsize=delta, fontweight=600, color=C.positive_text if good else C.negative_text)


@exhibit
def sn_var_row():
    fig, ax = canvas(300, 190)
    kpi_row(ax, 4, 138, 102, ROW, num=30)
    small(ax, 4, 40, "Teal = favorable, orange = unfavorable; the arrow\ngives the direction, the color the judgment.",
          size=MINI - 3, color=C.text_muted)
    return fig, ("A row of three KPI cards with identical anatomy: internal fill rate, days to fill, succession "
                 "coverage; favorable deltas teal, the unfavorable one orange.")


# ================================================================== BEST PRACTICE (200 x 140)
def _sn_bp(kind):
    fig, ax = canvas()
    if kind == "weight_avoid":
        ax.add_patch(FancyBboxPatch((28, 26), 150, 88, boxstyle="round,pad=2,rounding_size=8", fc="#9A9A9A", ec="none"))
        ax.add_patch(FancyBboxPatch((22, 32), 150, 88, boxstyle="round,pad=2,rounding_size=8", fc=C.surface_subtle,
                                    ec=C.headline, lw=2.2))
        big(ax, 97, 72, f"{SC_PCT}%", 38, weight=800, color=C.focus, ha="center", va="center")
        small(ax, 97, 42, "SUCCESSION", size=MINI - 1, weight=700, ha="center", color=C.headline)
    elif kind == "weight_fix":
        big(ax, 14, 62, f"{SC_PCT}%", 42)
        small(ax, 14, 36, f"{SC_NOW} of {SC_ROLES} critical roles have\na ready-now successor", size=MINI - 1,
              va="top")
    elif kind == "context_avoid":
        big(ax, 100, 64, f"{SC_PCT}%", 46, ha="center", va="center")
    elif kind == "context_fix":
        big(ax, 14, 70, f"{SC_PCT}%", 42)
        small(ax, 14, 50, f"{SC_NOW} of {SC_ROLES} critical roles have\nat least one ready-now successor",
              size=MINI - 1, va="top")
    elif kind == "compare_avoid":
        big(ax, 14, 62, f"{SC_PCT}%", 42)
        small(ax, 14, 36, f"+{SC_D}%", size=MINI, weight=600, color=C.text)
    elif kind == "compare_fix":
        big(ax, 14, 62, f"{SC_PCT}%", 42)
        small(ax, 14, 36, f"{UP} {mv.signed(SC_D)} pts vs. Mar 2025 ({SC_PCT0}%)", size=MINI - 1, weight=600,
              color=C.positive_text)
        small(ax, 14, 20, f"{SC_GAP} pts short of the {SC_TGT}% target", size=MINI - 1, weight=600,
              color=C.negative_text)
    elif kind == "gauge_avoid":                               # speedometer with traffic-light zones and a needle
        ax.set_aspect("equal")
        for a0, a1, col in ((120, 180, ANTI["red"]), (60, 120, ANTI["rainbow"][1]), (0, 60, ANTI["green"])):
            ax.add_patch(Wedge((100, 38), 72, a0, a1, width=24, color=col, lw=0))
        th = np.deg2rad(180 - 180 * SC_PCT / 100)
        ax.plot([100, 100 + 62 * np.cos(th)], [38, 38 + 62 * np.sin(th)], color="#222222", lw=2.5)
        ax.add_patch(Wedge((100, 38), 8, 0, 360, color="#222222"))
        small(ax, 100, 12, f"{SC_PCT}%", size=MINI + 1, weight=700, ha="center", color="#222222")
    elif kind == "gauge_fix":
        ax.set_aspect("equal")
        t = ring(ax, 118, 70, 52, SC_PCT, target=SC_TGT, w=9.5)
        big(ax, 118, 70, f"{SC_PCT}%", 22, ha="center", va="center")
        ax.text(118 + 60 * np.cos(t), 70 + 60 * np.sin(t), f"Target\n{SC_TGT}%", ha="right", va="center",
                fontsize=MINI - 1, color=C.annotation, linespacing=1.1)
    elif kind in ("favor_avoid", "favor_fix"):
        rows = [("Internal fill rate", f"{FL_NOW}%", f"{UP} {mv.signed(FL_NOW - FL_PRIOR)} pts", True),
                ("Days to fill", f"{round(DTF_NOW)}", f"{UP} {mv.signed(DTF_D)} days", DTF_D <= 0)]
        for i, (nm, val, dl, good) in enumerate(rows):
            y = 100 - i * 62
            small(ax, 14, y + 16, nm, size=MINI - 1.5)
            big(ax, 14, y - 14, val, 28)
            if kind == "favor_avoid":                          # colored by direction: up = green
                col = ANTI["green"]
            else:
                col = C.positive_text if good else C.negative_text
            small(ax, 88, y - 12, dl, size=MINI - 0.5, weight=600, color=col)
    elif kind == "round_avoid":
        big(ax, 14, 66, f"{SC_NOW / SC_ROLES * 100:.4f}%", 30)
        small(ax, 14, 38, f"+{SC_NOW / SC_ROLES * 100 - SC_PRIOR / SC_ROLES * 100:.5f} vs. prior", size=MINI - 1,
              weight=600, color=C.text)
    elif kind == "round_fix":
        big(ax, 14, 66, f"{SC_PCT}%", 42)
        small(ax, 14, 38, f"{UP} {mv.signed(SC_D)} pts vs. Mar 2025", size=MINI - 1, weight=600, color=C.positive_text)
    elif kind == "ring_avoid":                                 # an index of 122 forced into a ring: it laps itself
        ax.set_aspect("equal")
        v = int(IDX.internal_headcount_idx.iloc[-1])
        ring(ax, 70, 70, 50, 100, w=9, color=C.focus)
        ring(ax, 70, 70, 41, v - 100, w=9, color=C.focus_light, track="white")
        big(ax, 70, 70, f"{v}%", 20, ha="center", va="center")
        small(ax, 130, 74, "Data & AI\nheadcount", size=MINI - 1, va="center")
    elif kind == "ring_fix":
        v, m = int(IDX.internal_headcount_idx.iloc[-1]) - 100, int(IDX.external_postings_idx.iloc[-1]) - 100
        small(ax, 14, 112, "Data & AI headcount since 2021", size=MINI - 1)
        big(ax, 14, 68, mv.signed(v) + "%", 40)
        small(ax, 14, 42, f"vs. {mv.signed(m)}% for market\nData & AI postings", size=MINI - 1, va="top")
    elif kind == "row_avoid":
        kpi_row(ax, 6, 92, 66, ROW, num=19, name=MINI - 3.5, delta=MINI - 3.5, mixed=True, sep=False)
    elif kind == "row_fix":
        kpi_row(ax, 6, 92, 66, [(n.replace("Succession coverage", "Succession"), v, d.split(" vs.")[0], g)
                                for n, v, d, g in ROW], num=19, name=MINI - 3.5, delta=MINI - 3)
    return fig


for _k, _alt in {"weight_avoid": "A bold blue numeral in a bordered box with a drop shadow.",
                 "weight_fix": "A light-weight navy numeral with one line of context.",
                 "context_avoid": "A bare 62% with no explanation.",
                 "context_fix": "62% with a sentence saying 254 of 410 critical roles are covered.",
                 "compare_avoid": "A delta of '+14%' with no reference period.",
                 "compare_fix": "+14 pts vs. Mar 2025 in teal, and the gap to target in orange.",
                 "gauge_avoid": "A speedometer gauge with red, orange and green zones and a needle.",
                 "gauge_fix": "A thin progress ring with a labelled target tick.",
                 "favor_avoid": "Two deltas colored green because both went up.",
                 "favor_fix": "Fill rate up in teal (good), days to fill up in orange (worse).",
                 "round_avoid": "A number shown to four decimal places.",
                 "round_fix": "The same number rounded to 62%.",
                 "ring_avoid": "An index of 122 forced into a ring that laps itself.",
                 "ring_fix": "The growth as a big number with a market comparison.",
                 "row_avoid": "Three KPI cards, each with a different order, weight and box.",
                 "row_fix": "Three KPI cards with identical anatomy."}.items():
    EXHIBITS[f"sn_bp_{_k}"] = (lambda k=_k, a=_alt: (_sn_bp(k), a))
