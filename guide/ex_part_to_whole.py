"""Part-to-whole exhibits: stacked bars, waterfalls, treemaps, donuts. Registered into exhibits.EXHIBITS on import."""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge

import mckviz as mv
from exhibits import (ANNOT, ANTI, BAND, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px,
                      marker)

GREYS = [C.context, C.context_light, C.grid]          # context shades for stacked segments that aren't the point


# ------------------------------------------------------------------ helpers
def key(ax, items, x0=0.0, y=1.04, gap=0.035, size=MINI, sq=0.018):
    """Top-left key in stack order: small squares + names, laid left to right in axes coordinates."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    x = x0
    for name, col in items:
        ax.add_patch(Rectangle((x, y), sq, 0.045, color=col, transform=ax.transAxes, clip_on=False))
        t = ax.text(x + sq + 0.008, y + 0.022, name, transform=ax.transAxes, fontsize=size, color=C.text, va="center")
        bb = t.get_window_extent(r).transformed(ax.transAxes.inverted())
        x = bb.x1 + gap


def hstack(ax, cats, parts, *, size=MINI, tick=TICK, label_min=8, fmt="{:.0f}%", height=BAND, bold=(),
           end_label=None, sep=1.5):
    """Horizontal stacked bars. parts = [(values, color, name)], drawn left to right; labels where they fit."""
    y = np.arange(len(cats))
    left = np.zeros(len(cats))
    for vals, col, _ in parts:
        vals = np.asarray(vals, float)
        ax.barh(y, vals, left=left, color=col, height=height, edgecolor="white", lw=sep, zorder=2)
        for yy, (l, v) in enumerate(zip(left, vals)):
            if v >= label_min:
                ax.text(l + v / 2, yy, fmt.format(v), ha="center", va="center", fontsize=size - 0.5,
                        color=mv.text_on(col), zorder=3)
        left += vals
    ax.set_yticks(y, cats)
    for t in ax.get_yticklabels():
        t.set_fontsize(tick)
        if t.get_text() in bold:
            t.set_fontweight(600)
            t.set_color(C.headline)
    if end_label is not None:
        for yy, (lab, b) in enumerate(end_label):
            ax.text(left[yy] + max(left) * 0.012, yy, lab, va="center", fontsize=size, zorder=3,
                    color=C.headline if b else C.text, fontweight=700 if b else 500)
    ax.set_xticks([])
    ax.set_ylim(-0.6, len(cats) - 0.4)
    _plain(ax)
    ax.tick_params(length=0)
    return left


def waterfall(ax, steps, values, kinds, *, focus=(), colors=None, lo=None, size=LABEL, tick=TICK, connectors=True,
              conn_style=None, labels=True, break_marks=True, width=BAND, fmt=None, horizontal=False):
    """Waterfall from a list of steps. kinds: 'total' or 'delta'. Returns tops (for markers)."""
    fmt = fmt or (lambda v, k: f"{v:,.0f}" if k == "total" else mv.signed(v))
    run, bottoms, heights, cols, ends = 0.0, [], [], [], []
    for s, v, k in zip(steps, values, kinds):
        if k == "total":
            bottoms.append(0)
            heights.append(v)
            run = v
            cols.append(C.total)
        else:
            bottoms.append(run if v >= 0 else run + v)
            heights.append(abs(v))
            run += v
            cols.append(C.focus if s in focus else C.context)
        ends.append(run)
    if colors is not None:
        cols = [c or d for c, d in zip(colors, cols)]
    x = np.arange(len(steps))
    if horizontal:
        ax.barh(x, heights, left=bottoms, color=cols, height=width, zorder=2)
        ax.invert_yaxis()
    else:
        ax.bar(x, heights, bottom=bottoms, color=cols, width=width, zorder=2)
    if connectors:
        style = conn_style or dict(color=C.axis, lw=0.7)
        for i in range(len(steps) - 1):
            if horizontal:
                ax.plot([ends[i], ends[i]], [i + width / 2, i + 1 - width / 2], zorder=1, **style)
            else:
                ax.plot([i + width / 2, i + 1 - width / 2], [ends[i], ends[i]], zorder=1, **style)
    if labels:
        for i, (b, h, v, k, s) in enumerate(zip(bottoms, heights, values, kinds, steps)):
            hot = k == "total" or s in focus
            txt = fmt(v, k)
            if horizontal:
                ax.text(b + h + (max(heights) * 0.012), i, txt, va="center", ha="left", fontsize=size,
                        color=C.headline if hot else C.text, fontweight=700 if hot else 400)
            else:
                ax.annotate(txt, (i, b + h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                            fontsize=size, color=C.headline if hot else C.text, fontweight=700 if hot else 400)
    if lo is not None:
        (ax.set_xlim if horizontal else ax.set_ylim)(lo, None)
        if break_marks:                                               # two white slashes on each total bar
            for i, k in enumerate(kinds):
                if k != "total":
                    continue
                span = (max(bottoms[j] + heights[j] for j in range(len(steps))) - lo)
                for d in (0.035, 0.065):
                    yb = lo + span * d
                    if horizontal:
                        ax.plot([yb - span * 0.008, yb + span * 0.008], [i + width / 2, i - width / 2],
                                color="white", lw=2.2, zorder=4, solid_capstyle="butt")
                    else:
                        ax.plot([i - width / 2, i + width / 2], [yb - span * 0.008, yb + span * 0.008],
                                color="white", lw=2.2, zorder=4, solid_capstyle="butt")
    if horizontal:
        ax.set_yticks(x, steps)
        ax.set_xticks([])
        _plain(ax, left=True)
    else:
        ax.set_xticks(x, steps)
        ax.set_yticks([])
        _plain(ax, bottom=True)
    ax.tick_params(labelsize=tick, length=0)
    return [b + h for b, h in zip(bottoms, heights)]


def squarify(values, x, y, w, h):
    """Squarified treemap layout (Bruls et al.). values sorted descending; returns [(x, y, w, h)] in input order."""
    vals = list(values)
    total = sum(vals)
    vals = [v * w * h / total for v in vals]
    rects, row = [], []

    def worst(r, side):
        s = sum(r)
        return max(max(side * side * v / (s * s), s * s / (side * side * v)) for v in r)

    def layout(r, x, y, w, h):
        s = sum(r)
        out = []
        if w >= h:                                      # column on the left
            cw = s / h
            yy = y
            for v in r:
                out.append((x, yy, cw, v / cw))
                yy += v / cw
            return out, (x + cw, y, w - cw, h)
        rh = s / w
        xx = x
        for v in r:
            out.append((xx, y, v / rh, rh))
            xx += v / rh
        return out, (x, y + rh, w, h - rh)

    i = 0
    while i < len(vals):
        side = min(w, h)
        v = vals[i]
        if not row or worst(row + [v], side) <= worst(row, side):
            row.append(v)
            i += 1
        else:
            out, (x, y, w, h) = layout(row, x, y, w, h)
            rects += out
            row = []
    if row:
        rects += layout(row, x, y, w, h)[0]
    return rects


def treemap(ax, labels, values, colors, *, pad=0.006, size=MINI, min_label=0.022, fmt="{:,.0f}", text=True):
    order = np.argsort(values)[::-1]
    rects = squarify([values[i] for i in order], 0, 0, 1, 1)
    for (x, y, w, h), i in zip(rects, order):
        ax.add_patch(Rectangle((x + pad, y + pad), w - 2 * pad, h - 2 * pad, color=colors[i], lw=0))
        if text and w * h >= min_label:                       # y runs downward: (x, y) is the top-left corner
            ax.text(x + 0.012 + pad, y + 0.016 + pad, f"{labels[i]}\n{fmt.format(values[i])}", ha="left",
                    va="top", fontsize=size, color=mv.text_on(colors[i]), linespacing=1.2)
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 0)
    ax.axis("off")
    return rects, order


def donut(ax, labels, values, colors, *, start=90, width=0.32, size=MINI, center=None, label_out=True,
          clockwise=True, pct=True):
    total = sum(values)
    ang = start
    for lab, v, col in zip(labels, values, colors):
        sweep = 360 * v / total
        a1, a2 = (ang - sweep, ang) if clockwise else (ang, ang + sweep)
        ax.add_patch(Wedge((0, 0), 1, a1, a2, width=width, color=col, lw=1.4, ec="white"))
        if label_out:
            mid = np.radians((a1 + a2) / 2)
            r = 1.13
            ha = "left" if np.cos(mid) > 0.25 else "right" if np.cos(mid) < -0.25 else "center"
            va = "bottom" if np.sin(mid) > 0.8 else "top" if np.sin(mid) < -0.8 else "center"
            txt = f"{lab}\n{v / total * 100:.0f}%" if pct else lab
            ax.text(r * np.cos(mid), r * np.sin(mid), txt, ha=ha, va=va, fontsize=size, color=C.text,
                    linespacing=1.15)
        ang = a1 if clockwise else a2
    if center:
        big, small = center
        ax.text(0, 0.08, big, ha="center", va="center", fontsize=size * 2.1, color=C.headline, fontweight=700)
        ax.text(0, -0.28, small, ha="center", va="center", fontsize=size - 0.5, color=C.text, linespacing=1.15)
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")


# ------------------------------------------------------------------ data
MIX = _csv("workforce_mix").sort_values("contingent_pct")
TECH = float(MIX.contingent_pct[MIX.function == "Technology"].iloc[0])
OTHERS = float(MIX.contingent_pct[MIX.function != "Technology"].mean())
TEXT["mix_headline"] = (f"Technology uses contingent labor at more than {int(TECH / OTHERS)}x the average rate of "
                        "other functions")
TEXT["mix_subtitle"] = "Workforce composition by function, 2026 (% of workers)"

PLAN = _csv("data_ai_gap_plan")
P30 = PLAN.iloc[-1]
TEXT.update(plan_build_share=f"{P30.build_fte / P30.gap_fte * 100:.0f}%",
            plan_buy_share=f"{P30.buy_fte / P30.gap_fte * 100:.0f}%",
            plan_gap=f"{int(P30.gap_fte):,}", plan_year=str(P30.fiscal_year))

BRIDGE = _csv("labor_cost_bridge")
_grow = BRIDGE.value_musd[(BRIDGE.kind == "delta") & (BRIDGE.value_musd > 0)].sum()
_off = -BRIDGE.value_musd[BRIDGE.step.isin(["Automation savings", "Contractor conversion"])].sum()
TEXT["wf_headline"] = f"Automation and contractor conversion offset ~{round(_off / _grow * 100, -1):.0f}% of FY26 labor cost growth"
TEXT["wf_subtitle"] = "Labor cost bridge, FY25 to FY26 ($M)"
WF_FOCUS = {"Automation savings", "Contractor conversion"}

HC = _csv("headcount_bridge")
TEXT["hc_exit_share"] = f"{-HC.people[HC.step == 'Voluntary exits'].iloc[0] / HC.people[HC.step == 'External hires'].iloc[0] * 100:.0f}%"

EXPO = _csv("automation_exposure")
EXPO["exposed"] = EXPO.headcount * EXPO.genai_exposure_pct / 100
_cust = {"Customer Care", "Claims & Billing Specialist"}
TEXT["tm_cap_share"] = f"{EXPO.exposed[EXPO.role.isin(_cust)].sum() / EXPO.exposed.sum() * 100:.0f}%"
TEXT["tm_hc_share"] = f"{EXPO.headcount[EXPO.role.isin(_cust)].sum() / EXPO.headcount.sum() * 100:.0f}%"
TEXT["tm_headline"] = (f"Two customer-facing roles hold {TEXT['tm_cap_share']} of our gen AI-exposed capacity "
                       f"with {TEXT['tm_hc_share']} of headcount")
TEXT["tm_subtitle"] = "Estimated gen AI-exposed capacity by role, FY26 (FTE-equivalent)"
TEXT["donut_headline"] = (f"Reskilling can close {TEXT['plan_build_share']} of the {TEXT['plan_year']} Data & AI gap; "
                          f"hiring still has to cover nearly half")


# ================================================================== STACKED BAR
@exhibit
def stack_anatomy():
    parts = [(MIX.employee_ft_pct, C.context, "Full-time"), (MIX.employee_pt_pct, C.context_light, "Part-time"),
             (MIX.contingent_pct, C.focus, "Contingent")]
    fig = fig_px(620, 300)
    ax = fig.add_subplot()
    ends = [(f"{v:.0f}%", f == "Technology") for f, v in zip(MIX.function, MIX.contingent_pct)]
    hstack(ax, list(MIX.function), [(p[0], p[1], p[2]) for p in parts], size=LABEL, tick=TICK, bold={"Technology"},
           end_label=None)
    for yy, (lab, b) in enumerate(ends):
        ax.text(101.2, yy, lab, va="center", fontsize=LABEL, color=C.headline if b else C.text,
                fontweight=700 if b else 500)
    ax.set_xlim(0, 113)
    ax.set_ylim(-0.6, len(MIX) + 0.15)
    key(ax, [(n, c) for _, c, n in parts], y=0.94, size=TICK - 0.5)
    n = len(MIX)
    marker(ax, (100 - TECH / 2, n - 1), 3, offset=(0, 21))
    marker(ax, (35, 0), 4, offset=(0, 0))
    marker(ax, (29, n - 1), 5, offset=(26, 0))
    marker(ax, (0, n - 0.05), 6, offset=(-12, 6))
    marker(ax, (101.2, n - 1), 7, offset=(34, 0))
    marker(ax, (101.2, 0), 8, offset=(34, 0))
    return fig, (TEXT["mix_headline"] + f". Technology {TECH:.0f}% contingent; the other four functions "
                 f"{int(MIX.contingent_pct[MIX.function != 'Technology'].min())}–"
                 f"{int(MIX.contingent_pct[MIX.function != 'Technology'].max())}%.")


@exhibit
def stack_var_absolute():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x = np.arange(len(PLAN))
    parts = [("build_fte", C.focus, "Build"), ("buy_fte", C.context, "Buy"), ("borrow_fte", C.context_light, "Borrow"),
             ("automate_fte", C.grid, "Automate")]
    bottom = np.zeros(len(PLAN))
    for col, c, name in parts:
        ax.bar(x, PLAN[col], bottom=bottom, color=c, width=0.55, edgecolor="white", lw=1)
        if col in ("build_fte", "buy_fte"):
            for xx, (b, v) in enumerate(zip(bottom, PLAN[col])):
                if v > 60:
                    ax.text(xx, b + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=MINI - 1.5, color=mv.text_on(c))
        bottom += PLAN[col].values
    for xx, t in enumerate(PLAN.gap_fte):
        ax.text(xx, t + 12, f"{t:,}", ha="center", va="bottom", fontsize=MINI - 1, color=C.headline, fontweight=700)
    for i, (name, c) in enumerate([(p[2], p[1]) for p in parts][::-1]):         # key in stack order, top first
        ax.add_patch(Rectangle((-0.42, 600 - i * 52), 0.08, 30, color=c))
        ax.text(-0.3, 615 - i * 52, name, fontsize=MINI - 1.5, color=C.text, va="center")
    ax.set_xticks(x, PLAN.fiscal_year)
    ax.set_xlim(-0.5, len(PLAN) - 0.5)
    ax.set_ylim(0, 700)
    ax.set_yticks([])
    ax.tick_params(labelsize=MINI - 1, length=0)
    _plain(ax, bottom=True)
    return fig, f"Stacked columns of how the Data & AI gap closes; build reaches {TEXT['plan_build_share']} by {TEXT['plan_year']}."


@exhibit
def stack_var_diverging():
    d = _csv("engagement_items").sort_values("favorable_pct")
    short = {"I have the tools to do my job well": "Tools to do my job", "My workload is manageable": "Manageable workload",
             "I see a path to grow here": "Path to grow", "My manager supports my development": "Manager support",
             "I feel I belong on my team": "Belonging", "I would recommend McKesson as a place to work": "Would recommend"}
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    y = np.arange(len(d))
    neg_left = -(d.unfavorable_pct + d.neutral_pct / 2)
    ax.barh(y, d.unfavorable_pct, left=neg_left, color=C.negative, height=BAND, edgecolor="white", lw=1)
    ax.barh(y, d.neutral_pct, left=-d.neutral_pct / 2, color=C.context_light, height=BAND, edgecolor="white", lw=1)
    ax.barh(y, d.favorable_pct, left=d.neutral_pct / 2, color=C.focus, height=BAND, edgecolor="white", lw=1)
    for yy, (u, n, f) in enumerate(zip(d.unfavorable_pct, d.neutral_pct, d.favorable_pct)):
        ax.text(-(u + n / 2) - 1.5, yy, f"{u}", ha="right", va="center", fontsize=MINI - 1.5, color=C.negative_text)
        ax.text(f + n / 2 + 1.5, yy, f"{f}", ha="left", va="center", fontsize=MINI - 1.5, color=C.text)
    ax.axvline(0, color=C.axis, lw=0.7)
    ax.set_yticks(y, [short[i] for i in d.item])
    ax.text(-30, len(d) - 0.25, "Unfavorable", ha="center", fontsize=MINI - 1.5, color=C.negative_text, va="bottom")
    ax.text(40, len(d) - 0.25, "Favorable", ha="center", fontsize=MINI - 1.5, color=C.focus, va="bottom", fontweight=600)
    ax.set_xlim(-58, 95)
    ax.set_ylim(-0.6, len(d) + 0.3)
    ax.set_xticks([])
    ax.tick_params(labelsize=MINI - 1.5, length=0)
    _plain(ax)
    return fig, "Diverging stacked bars of survey items: unfavorable in orange left of zero, favorable in blue right."


@exhibit
def stack_var_marimekko():
    d = MIX.sort_values("workers", ascending=False)
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    total = d.workers.sum()
    x = 0.0
    for f, w, ft, pt, ct in zip(d.function, d.workers, d.employee_ft_pct, d.employee_pt_pct, d.contingent_pct):
        ww = w / total * 100
        b = 0
        for v, c in ((ct, C.focus if f == "Technology" else C.context_light), (pt, C.grid), (ft, C.context)):
            ax.add_patch(Rectangle((x, b), ww, v, color=c, ec="white", lw=1.2))
            b += v
        name = {"Pharmacy Ops": "Pharmacy\nOps", "Customer Care": "Cust.\nCare", "Technology": "Tech",
                "Distribution": "Distribution", "Corporate": "Corp."}[f]
        ax.text(x + ww / 2, -3, name, ha="center", va="top", fontsize=MINI - 2, color=C.headline if f == "Technology" else C.text,
                fontweight=700 if f == "Technology" else 400, linespacing=1.05)
        if f == "Technology":
            ax.text(x + ww / 2, ct / 2, f"{ct}%", ha="center", va="center", fontsize=MINI - 2, color="white", fontweight=600)
        x += ww
    ax.text(100.8, 4, "Contingent", fontsize=MINI - 2, color=C.text, va="center")
    ax.text(100.8, 50, "Full-time", fontsize=MINI - 2, color=C.text, va="center")
    ax.set_xlim(0, 118)
    ax.set_ylim(-14, 100)
    ax.axis("off")
    return fig, "Marimekko: column width is each function's workforce, height its mix; Technology's contingent share in blue."


@exhibit
def stack_var_time():
    d = _csv("tech_mix_by_fy")
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    x = np.arange(len(d))
    bottom = np.zeros(len(d))
    for col, c in (("contingent_pct", C.focus), ("employee_pt_pct", C.context_light), ("employee_ft_pct", C.context)):
        ax.bar(x, d[col], bottom=bottom, color=c, width=BAND, edgecolor="white", lw=1)
        if col == "contingent_pct":
            for xx, v in enumerate(d[col]):
                ax.text(xx, v / 2, f"{v}%", ha="center", va="center", fontsize=MINI - 1.5, color="white", fontweight=600)
        bottom += d[col].values
    ax.text(len(d) - 0.55, 15, " Contingent", fontsize=MINI - 1.5, color=C.focus, va="center", fontweight=600)
    ax.text(len(d) - 0.55, 70, " Employees", fontsize=MINI - 1.5, color=C.text, va="center")
    ax.set_xticks(x, d.fiscal_year)
    ax.set_xlim(-0.5, len(d) + 0.9)
    ax.set_ylim(0, 100)
    ax.set_yticks([])
    ax.tick_params(labelsize=MINI - 1, length=0)
    _plain(ax, bottom=True)
    return fig, "100% stacked columns of Technology's mix FY22–FY26; the contingent share on the baseline rises from 18% to 30%."


def _mini_mix(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    d = MIX.tail(4)
    cats = [{"Pharmacy Ops": "Pharmacy", "Customer Care": "Care"}.get(f, f) for f in d.function]
    ft, pt, ct = d.employee_ft_pct.values, d.employee_pt_pct.values, d.contingent_pct.values
    lab = dict(size=MINI - 1, tick=MINI - 2, label_min=99)
    if kind == "base_avoid":
        hstack(ax, cats, [(ft, C.context, ""), (ct, C.focus, ""), (pt, C.context_light, "")], **lab)
    elif kind == "base_fix":
        hstack(ax, cats, [(ct, C.focus, ""), (ft, C.context, ""), (pt, C.context_light, "")], **lab)
    elif kind == "many_avoid":
        rng = np.random.default_rng(3)
        segs = [rng.integers(6, 20, 4) for _ in range(8)]
        tot = np.sum(segs, axis=0)
        hstack(ax, cats, [(s / tot * 100, c, "") for s, c in zip(segs, mv.CATEGORICAL)], **lab)
    elif kind == "many_fix":
        hstack(ax, cats, [(ct, C.focus, ""), (pt, C.context_light, ""), (ft, C.context, "")], size=MINI - 1,
               tick=MINI - 2, label_min=10)
    elif kind == "key_avoid":
        hstack(ax, cats, [(ft, C.context, ""), (pt, C.context_light, ""), (ct, C.focus, "")], **lab)
        ax.legend(handles=[Rectangle((0, 0), 1, 1, color=c) for c in (C.focus, C.context, C.context_light)],
                  labels=["Contingent", "Full-time", "Part-time"], fontsize=MINI - 3, loc="upper center",
                  bbox_to_anchor=(0.5, -0.02), ncol=3, frameon=False, handlelength=0.8, columnspacing=0.8)
    elif kind == "key_fix":
        hstack(ax, cats, [(ft, C.context, ""), (pt, C.context_light, ""), (ct, C.focus, "")], size=MINI - 1,
               tick=MINI - 2, label_min=10)
        key(ax, [("Full-time", C.context), ("Part-time", C.context_light), ("Contingent", C.focus)], y=1.0,
            size=MINI - 3, gap=0.06, sq=0.035)
        ax.set_ylim(-0.6, len(cats) - 0.2)
    elif kind in ("order_avoid", "order_fix"):
        parts = [(ft, C.context), (pt, C.context_light), (ct, C.focus)]
        y = np.arange(len(cats))
        for yy in y:
            seq = sorted(parts, key=lambda p: -p[0][yy]) if kind == "order_avoid" else parts
            left = 0
            for vals, col in seq:
                ax.barh(yy, vals[yy], left=left, color=col, height=BAND, edgecolor="white", lw=1.2)
                left += vals[yy]
        ax.set_yticks(y, cats)
        ax.set_xticks([])
        ax.tick_params(labelsize=MINI - 2, length=0)
        _plain(ax)
    return fig


for _k, _alt in {"base_avoid": "The highlighted segment floats in the middle of each bar.",
                 "base_fix": "The highlighted segment starts at the baseline, so bars compare directly.",
                 "many_avoid": "Bars cut into eight colored segments.",
                 "many_fix": "Three segments: the one that matters in blue, the rest grey.",
                 "key_avoid": "A legend below the chart in a different order from the stack.",
                 "key_fix": "Values in the segments and a key top-left in stack order.",
                 "order_avoid": "Segments change order from bar to bar.",
                 "order_fix": "Segments keep the same order in every bar."}.items():
    EXHIBITS[f"stack_bp_{_k}"] = (lambda k=_k, a=_alt: (_mini_mix(k), a))


# ================================================================== WATERFALL
@exhibit
def wf_anatomy():
    b = BRIDGE
    fig = fig_px(620, 320)
    ax = fig.add_subplot()
    steps = ["FY25 labor\ncost", "Merit &\nmarket", "Net new\nhires", "Attrition\nbackfill lag", "Automation\nsavings",
             "Contractor\nconversion", "FY26 labor\ncost"]
    names = list(b.step)
    focus = {steps[i] for i, s in enumerate(names) if s in WF_FOCUS}
    tops = waterfall(ax, steps, list(b.value_musd), list(b.kind), focus=focus, lo=3900, size=LABEL, tick=TICK)
    ax.set_ylim(3900, 4520)
    marker(ax, (0, 4100), 3, offset=(0, 0))
    marker(ax, (0, 3900 + 620 * 0.05), 4, offset=(-28, 0))
    marker(ax, (4, tops[4]), 5, offset=(30, -14))
    marker(ax, (2.5, tops[2]), 6, offset=(0, 10))
    marker(ax, (1, tops[1]), 7, offset=(-30, 10))
    marker(ax, (3, tops[3] - 30), 8, offset=(0, -14))
    return fig, TEXT["wf_headline"] + ". FY25 $4,210M to FY26 $4,292M; automation savings −71 and contractor conversion −24."


@exhibit
def wf_var_horizontal():
    b = BRIDGE
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    steps = ["FY25 labor cost", "Merit & market", "Net new hires", "Backfill lag", "Automation", "Contractors",
             "FY26 labor cost"]
    focus = {"Automation", "Contractors"}
    waterfall(ax, steps, list(b.value_musd), list(b.kind), focus=focus, lo=3900, size=MINI - 1.5, tick=MINI - 1.5,
              horizontal=True, width=0.6)
    ax.set_xlim(3900, 4560)
    return fig, "Horizontal waterfall of the labor cost bridge, totals in navy and the two offsets in blue."


@exhibit
def wf_var_direction():
    h = HC
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    steps = ["FY25", "Hires", "Moves\nin", "Vol.\nexits", "Invol.\nexits", "Moves\nout", "FY26"]
    cols = [None if k == "total" else (C.focus if v > 0 else C.negative) for v, k in zip(h.people, h.kind)]
    waterfall(ax, steps, list(h.people), list(h.kind), colors=cols, lo=12000, size=MINI - 1.5, tick=MINI - 1.5,
              fmt=lambda v, k: f"{v / 1000:,.1f}K" if k == "total" else mv.signed(v / 1000, 1, "K"))
    ax.set_ylim(12000, 24300)
    return fig, f"Headcount bridge with additions in blue and losses in orange; voluntary exits equal {TEXT['hc_exit_share']} of hires."


@exhibit
def wf_var_subtotal():
    b = BRIDGE
    steps = ["FY25", "Merit", "Hires", "Lag", "Before\nsavings", "Autom.", "Contr.", "FY26"]
    vals = list(b.value_musd[:4]) + [float(b.value_musd[:4].sum())] + list(b.value_musd[4:6]) + [float(b.value_musd.iloc[-1])]
    kinds = ["total", "delta", "delta", "delta", "total", "delta", "delta", "total"]
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    cols = [None, None, None, None, C.focus_light, None, None, None]
    waterfall(ax, steps, vals, kinds, focus={"Autom.", "Contr."}, colors=cols, lo=3900, size=MINI - 2,
              tick=MINI - 2, fmt=lambda v, k: f"{v:,.0f}" if k == "total" else mv.signed(v))
    ax.set_ylim(3900, 4560)
    return fig, "Labor cost bridge with a light-blue subtotal before the two savings steps."


@exhibit
def wf_var_distribution():
    gap = int(P30.gap_fte)
    shares = [("Data\neng.", 0.34), ("Analytics", 0.26), ("Data\nscience", 0.19), ("ML / AI\neng.", 0.155), ("Gov.", None)]
    vals, used = [], 0
    for _, s in shares[:-1]:
        v = round(gap * s)
        vals.append(v)
        used += v
    vals.append(gap - used)
    steps = [s for s, _ in shares] + ["Total\ngap"]
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    waterfall(ax, steps, vals + [gap], ["delta"] * len(vals) + ["total"], focus={"Data\neng."}, size=MINI - 1.5,
              tick=MINI - 2, fmt=lambda v, k: f"{v:,.0f}")             # contributions to a total: no +/- signs
    ax.set_ylim(0, gap * 1.15)
    TEXT["dist_wf_first"] = f"{vals[0] / gap * 100:.0f}%"
    return fig, f"Distribution waterfall: the {gap} FTE gap split by role family; data engineering is {TEXT['dist_wf_first']}."


def _wf_mini(kind):
    b = BRIDGE
    steps = ["FY25", "Merit", "Hires", "Lag", "Auto", "Contr", "FY26"]
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    common = dict(size=MINI - 3, tick=MINI - 3)
    vals, kinds = list(b.value_musd), list(b.kind)
    if kind == "conn_avoid":
        waterfall(ax, steps, vals, kinds, lo=3900, conn_style=dict(color=C.headline, lw=2.2), labels=False, **common)
    elif kind == "conn_fix":
        waterfall(ax, steps, vals, kinds, lo=3900, labels=False, **common)
    elif kind == "color_avoid":
        cols = [None if k == "total" else (ANTI["green"] if v > 0 else ANTI["red"]) for v, k in zip(vals, kinds)]
        waterfall(ax, steps, vals, kinds, lo=3900, colors=cols, labels=False, **common)
    elif kind == "color_fix":
        waterfall(ax, steps, vals, kinds, lo=3900, focus={"Auto", "Contr"}, labels=False, **common)
    elif kind == "break_avoid":
        waterfall(ax, steps, vals, kinds, lo=3900, break_marks=False, labels=False, **common)
        ax.set_yticks([3900, 4200, 4500])
        ax.tick_params(axis="y", labelsize=MINI - 3)
    elif kind == "break_fix":
        waterfall(ax, steps, vals, kinds, lo=3900, labels=False, **common)
        ax.text(0.0, 1.0, "Axis starts at $3.9B", transform=ax.transAxes, fontsize=MINI - 3, color=C.text_muted,
                va="top", ha="left")
    elif kind == "group_avoid":                      # the same bridge with every sub-driver shown
        merit, hires = vals[1], vals[2]
        detail = [vals[0], round(merit * 0.59), round(merit * 0.29), merit - round(merit * 0.59) - round(merit * 0.29),
                  round(hires * 0.73), hires - round(hires * 0.73), vals[3], vals[4], vals[5], vals[6]]
        waterfall(ax, list("ABCDEFGHIJ"), detail, ["total"] + ["delta"] * 8 + ["total"], lo=3900, size=MINI - 4,
                  tick=MINI - 3, width=0.7)
        ax.set_xticks(range(10), ["FY25", "Mer", "Mkt", "Pro", "Hir", "Con", "Lag", "Aut", "Ctr", "FY26"])
    elif kind == "group_fix":
        waterfall(ax, ["FY25", "Pay", "Hires", "Lag", "Savings", "FY26"],
                  [vals[0], vals[1], vals[2], vals[3], vals[4] + vals[5], vals[6]],
                  ["total", "delta", "delta", "delta", "delta", "total"], lo=3900, focus={"Savings"}, size=MINI - 3,
                  tick=MINI - 3)
    ax.set_ylim(3900, 4560)
    return fig


for _k, _alt in {"conn_avoid": "Heavy dark connectors compete with the bars.",
                 "conn_fix": "Thin light-grey connectors stay in the background.",
                 "color_avoid": "Increases in green and decreases in red.",
                 "color_fix": "Grey drivers, navy totals, the two the headline names in blue.",
                 "break_avoid": "A truncated axis with no sign that the totals are cut.",
                 "break_fix": "Break marks on the totals and a note that the axis starts at $3.9B.",
                 "group_avoid": "Ten narrow steps, each labelled, too many to follow.",
                 "group_fix": "Five steps: small drivers grouped, the savings combined and in blue."}.items():
    EXHIBITS[f"wf_bp_{_k}"] = (lambda k=_k, a=_alt: (_wf_mini(k), a))


# ================================================================== TREEMAP
_ROLE_SHORT = {"Claims & Billing Specialist": "Claims & Billing", "Distribution Center Associate": "DC Associate",
               "Software Engineering": "Software Eng.", "Supply Chain Planning": "Supply Chain",
               "Finance Operations": "Finance Ops"}


@exhibit
def tm_anatomy():
    d = EXPO
    labels = [_ROLE_SHORT.get(r, r) for r in d.role]
    cols = [C.focus if r in _cust else C.context for r in d.role]
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    rects, order = treemap(ax, labels, list(d.exposed.round()), cols, size=LABEL - 0.5, min_label=0.0225)
    pos = {i: r for r, i in zip(rects, order)}
    big = int(np.argmax(d.exposed))
    x, y, w, h = pos[big]
    marker(ax, (x + w - 0.035, y + 0.06), 3)
    second = [i for i in order if d.role.iloc[i] not in _cust][0]
    x, y, w, h = pos[second]
    marker(ax, (x + w - 0.03, y + 0.06), 4)
    x, y, w, h = pos[order[-1]]
    marker(ax, (x + w / 2, y + h / 2), 5)
    x, y, w, h = pos[order[0]]
    marker(ax, (x + 0.035, y + h - 0.06), 6)
    return fig, TEXT["tm_headline"] + "."


def _tm_mini(kind):
    d = EXPO.sort_values("exposed", ascending=False).head(7)
    labs = [_ROLE_SHORT.get(r, r).split()[0] for r in d.role]
    cols = [C.focus if r in _cust else C.context for r in d.role]
    fig = fig_px(200, 140)
    if kind == "bar_fix":
        ax = fig.add_subplot()
        dd = d.head(4).iloc[::-1]
        y = np.arange(len(dd))
        ax.barh(y, dd.exposed, color=[C.focus if r in _cust else C.context for r in dd.role], height=BAND)
        for yy, v in enumerate(dd.exposed):
            ax.text(v + 30, yy, f"{v:,.0f}", va="center", fontsize=MINI - 2.5, color=C.text)
        ax.set_yticks(y, [_ROLE_SHORT.get(r, r) for r in dd.role], fontsize=MINI - 2.5)
        ax.set_xticks([])
        ax.set_xlim(0, dd.exposed.max() * 1.3)
        ax.tick_params(length=0)
        _plain(ax)
        return fig
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    if kind == "order_avoid":                                       # alphabetical strips: sizes hard to compare
        dd = d.sort_values("role")
        x = 0
        tot = dd.exposed.sum()
        for r, v, c in zip(dd.role, dd.exposed, [C.focus if r in _cust else C.context for r in dd.role]):
            w = v / tot
            ax.add_patch(Rectangle((x + 0.004, 0.004), w - 0.008, 0.992, color=c))
            x += w
        ax.set_xlim(0, 1); ax.set_ylim(1, 0); ax.axis("off")
    elif kind == "order_fix":
        treemap(ax, labs, list(d.exposed), cols, size=MINI - 3, fmt="{:,.0f}", min_label=0.05)
    elif kind == "label_avoid":
        rects, order = treemap(ax, labs, list(d.exposed), cols, text=False)
        for (x, y, w, h), i in zip(rects, order):
            ax.add_patch(Rectangle((x + 0.006, y + 0.006), w - 0.012, min(0.09, h * 0.4), color="white", alpha=0.9))
            ax.text(x + 0.015, y + 0.012, labs[i], fontsize=MINI - 3.5, va="top", color=C.text)
    elif kind == "label_fix":
        treemap(ax, labs, list(d.exposed), cols, size=MINI - 3, min_label=0.05)
    elif kind == "pad_avoid":
        rects, order = treemap(ax, labs, list(d.exposed), cols, text=False, pad=0)
        rng = np.random.default_rng(1)
        for (x, y, w, h), i in zip(rects, order):
            p = rng.uniform(0.004, 0.03)
            ax.add_patch(Rectangle((x, y), w, h, color="white", lw=0))
            ax.add_patch(Rectangle((x + p, y + p * 1.6), w - 2.3 * p, h - 2.5 * p, color=cols[i], lw=0))
    elif kind == "pad_fix":
        treemap(ax, labs, list(d.exposed), cols, text=False, pad=0.006)
    elif kind == "bar_avoid":
        dd = d.head(4)
        treemap(ax, [_ROLE_SHORT.get(r, r) for r in dd.role], list(dd.exposed),
                [C.focus if r in _cust else C.context for r in dd.role], size=MINI - 3, min_label=0.05)
    return fig


for _k, _alt in {"order_avoid": "Rectangles in alphabetical strips: sizes are hard to compare.",
                 "order_fix": "Largest top-left to smallest bottom-right.",
                 "label_avoid": "White label bands laid over the rectangles.",
                 "label_fix": "Labels inside the rectangles, top-left.",
                 "pad_avoid": "Uneven gaps between rectangles.",
                 "pad_fix": "Even, thin white gutters.",
                 "bar_avoid": "A treemap of only four similar parts.",
                 "bar_fix": "The same four parts as a sorted bar chart."}.items():
    EXHIBITS[f"tm_bp_{_k}"] = (lambda k=_k, a=_alt: (_tm_mini(k), a))


# ================================================================== DONUT
_PLAN_PARTS = [("Buy (hire)", "buy_fte"), ("Build (reskill)", "build_fte"), ("Borrow", "borrow_fte"),
               ("Automate", "automate_fte")]


@exhibit
def donut_anatomy():
    vals = [float(P30[c]) for _, c in _PLAN_PARTS]
    labs = [n for n, _ in _PLAN_PARTS]
    cols = [C.focus if n.startswith("Build") else c for n, c in zip(labs, [C.context, C.focus, C.context_light, C.grid])]
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    donut(ax, labs, vals, cols, size=LABEL, center=(TEXT["plan_gap"], f"FTE gap\nby {TEXT['plan_year']}"), width=0.3)
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-1.3, 1.48)
    marker(ax, (0.38, 1.2), 3)
    marker(ax, (-0.92, 0.55), 4, offset=(-14, 10))
    marker(ax, (0, 0.08), 5, offset=(-52, 0))
    marker(ax, (1.13, 0.1), 6, offset=(-14, 30))
    marker(ax, (0.62, -0.79), 7, offset=(10, -12))
    return fig, TEXT["donut_headline"] + f". Buy {TEXT['plan_buy_share']}, build {TEXT['plan_build_share']}."


def _donut_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    vals = [float(P30[c]) for _, c in _PLAN_PARTS]
    labs = ["Buy", "Build", "Borrow", "Auto"]
    cols = [C.context, C.focus, C.context_light, C.grid]
    if kind == "pie_avoid":
        donut(ax, labs, vals, cols, width=1.0, size=MINI - 2)
    elif kind == "pie_fix":
        donut(ax, labs, vals, cols, width=0.3, size=MINI - 2)
    elif kind == "label_avoid":
        donut(ax, labs, vals, cols, width=0.3, label_out=False)
        tot = sum(vals)
        ang = 90
        for lab, v in zip(labs, vals):
            sweep = 360 * v / tot
            mid = np.radians(ang - sweep / 2)
            ax.text(0.85 * np.cos(mid), 0.85 * np.sin(mid), f"{lab} {v / tot * 100:.0f}%", ha="center", va="center",
                    fontsize=MINI - 3, color="white" if lab != "Auto" else C.text)
            ang -= sweep
    elif kind == "label_fix":
        donut(ax, labs, vals, cols, width=0.3, size=MINI - 2)
    elif kind == "many_avoid":
        rng = np.random.default_rng(4)
        v = list(rng.integers(3, 14, 9))
        donut(ax, [""] * 9, v, (mv.CATEGORICAL + [C.context] * 3)[:9], width=0.3, label_out=False)
    elif kind == "many_fix":
        donut(ax, ["Buy", "Build", "Other"], [vals[0], vals[1], vals[2] + vals[3]],
              [C.context, C.focus, C.context_light], width=0.3, size=MINI - 2)
    elif kind == "order_avoid":
        donut(ax, ["Auto", "Buy", "Borrow", "Build"], [vals[3], vals[0], vals[2], vals[1]],
              [C.grid, C.context, C.context_light, C.focus], width=0.3, size=MINI - 2, start=200)
    elif kind == "order_fix":
        donut(ax, labs, vals, cols, width=0.3, size=MINI - 2)
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-1.4, 1.75)
    return fig


for _k, _alt in {"pie_avoid": "A full pie: readers compare angles and areas.",
                 "pie_fix": "A donut: readers follow arc length around the ring.",
                 "label_avoid": "Labels squeezed onto the ring.",
                 "label_fix": "Labels and values outside the ring.",
                 "many_avoid": "A donut cut into nine colored slices.",
                 "many_fix": "Two named segments and the rest grouped as Other.",
                 "order_avoid": "Segments in no order, starting at an arbitrary angle.",
                 "order_fix": "Largest first, clockwise from 12 o'clock."}.items():
    EXHIBITS[f"donut_bp_{_k}"] = (lambda k=_k, a=_alt: (_donut_mini(k), a))
