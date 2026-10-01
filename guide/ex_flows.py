"""Relationships and flows exhibits: Sankey, parallel coordinates, Venn. Registered on import."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, PathPatch, Polygon, Rectangle
from matplotlib.path import Path as MPath

import mckviz as mv
from exhibits import (ANNOT, ANTI, LABEL, MINI, SHORT, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px,
                      marker)

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


# ------------------------------------------------------------------ Sankey (drawn in matplotlib: filled bezier bands)
def sankey(ax, columns, flows, color_of, *, xs=None, node_w=0.014, gap=0.05, alpha=0.55, curved=True,
           labels=True, size=MINI, fmt="{:,.0f}", label_name=True, headers=None, header_size=None, z_order=None):
    """columns: [[node, ...] top to bottom] per stage; nodes are (stage, name) keys.
    flows: [(src_key, dst_key, value, kind)], only between adjacent stages. color_of(flow) -> (color, alpha).
    Returns {key: (x, y_bottom, y_top)} for markers."""
    n_col = len(columns)
    xs = xs or list(np.linspace(0, 1, n_col))
    inflow = {k: 0 for col in columns for k in col}
    outflow = dict(inflow)
    for s, t, v, _ in flows:
        outflow[s] += v
        inflow[t] += v
    size_of = {k: max(inflow[k], outflow[k]) for k in inflow}
    tallest = max(sum(size_of[k] for k in col) + gap * (len(col) - 1) * 0 for col in columns)
    max_gaps = max(len(col) - 1 for col in columns)
    scale = (1 - gap * max_gaps) / tallest
    pos = {}
    for c, col in enumerate(columns):
        h = sum(size_of[k] for k in col) * scale + gap * (len(col) - 1)
        top = 0.5 + h / 2
        for k in col:
            hh = size_of[k] * scale
            pos[k] = (xs[c], top - hh, top)
            top -= hh + gap
    rank = {k: i for col in columns for i, k in enumerate(col)}
    out_cursor = {k: pos[k][2] for k in pos}
    in_cursor = {k: pos[k][2] for k in pos}
    order = sorted(flows, key=lambda f: (rank[f[0]], rank[f[1]]))
    bands = {}
    for f in order:                                     # outgoing stacked by target order
        s, t, v, _ = f
        y1 = out_cursor[s]
        out_cursor[s] -= v * scale
        bands[f] = [y1, y1 - v * scale]
    for f in sorted(flows, key=lambda f: (rank[f[1]], rank[f[0]])):   # incoming stacked by source order
        s, t, v, _ = f
        y1 = in_cursor[t]
        in_cursor[t] -= v * scale
        bands[f] += [y1, y1 - v * scale]
    draw = sorted(flows, key=z_order) if z_order else flows
    for f in draw:
        s, t, v, _ = f
        a_top, a_bot, b_top, b_bot = bands[f]
        x0 = pos[s][0] + node_w
        x1 = pos[t][0]
        col, al = color_of(f)
        if curved:
            xm = (x0 + x1) / 2
            verts = [(x0, a_top), (xm, a_top), (xm, b_top), (x1, b_top), (x1, b_bot), (xm, b_bot), (xm, a_bot),
                     (x0, a_bot), (x0, a_top)]
            codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CURVE4, MPath.CURVE4,
                     MPath.CURVE4, MPath.CLOSEPOLY]
        else:                                           # angular "arrows": the thing not to do
            xm1, xm2 = x0 + (x1 - x0) * 0.35, x0 + (x1 - x0) * 0.65
            verts = [(x0, a_top), (xm1, a_top), (xm2, b_top), (x1, b_top), (x1, b_bot), (xm2, b_bot), (xm1, a_bot),
                     (x0, a_bot), (x0, a_top)]
            codes = [MPath.MOVETO] + [MPath.LINETO] * 7 + [MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(verts, codes), facecolor=col, alpha=al, lw=0, zorder=2))
    for k, (x, y0, y1) in pos.items():
        ax.add_patch(Rectangle((x, y0), node_w, y1 - y0, color=C.total, lw=0, zorder=3))
    if labels:
        for k, (x, y0, y1) in pos.items():
            c = k[0]
            last = c == n_col - 1
            first = c == 0
            txt = (f"{k[1]}  {fmt.format(size_of[k])}" if label_name else fmt.format(size_of[k]))
            if first:
                ax.text(x - 0.012, (y0 + y1) / 2, txt, ha="right", va="center", fontsize=size, color=C.text, zorder=4)
            else:
                ax.text(x + node_w + 0.012, (y0 + y1) / 2, txt, ha="left", va="center", fontsize=size, color=C.text,
                        zorder=4, path_effects=None if last else mv.halo(width=2.5))
    if headers:
        for x, h in zip(xs, headers):
            ax.text(x + node_w / 2, 1.0 + gap * 0.9, h, ha="center", va="bottom", fontsize=header_size or size,
                    fontweight=600, color=C.headline)
    ax.axis("off")
    return pos, bands


# ------------------------------------------------------------------ data
MOB = _csv("mobility_flows")
_src_tot = MOB.groupby("from_family").moves.sum().sort_values(ascending=False)
_dst_tot = MOB.groupby("to_family").moves.sum()
SK_FOCUS = list(_src_tot.index[:2])                                  # the two largest sources
_share = _src_tot.iloc[:2].sum() / MOB.moves.sum()
FAM = {"Pharmacy Technician": "Pharmacy Technician", "DC Associate": "DC Associate"}
TEXT["flow_sk_headline"] = (f"Two frontline job families start {round(_share * 10):.0f} in 10 internal moves: "
                            f"{_src_tot.iloc[0]} from {_src_tot.index[0]}, {_src_tot.iloc[1]} from {_src_tot.index[1]}")
TEXT["flow_sk_subtitle"] = "Internal moves between job families, trailing 24 months to Mar 2026 (number of moves)"
TEXT["flow_sk_total"] = f"{MOB.moves.sum():,}"
TEXT["flow_sk_min"] = f"{MOB.moves.min()}"
assert MOB.moves.min() >= 10


def _mob_columns():
    left = [(0, f) for f in _src_tot.index]
    # destinations ordered by their main source, so bands cross as little as possible
    main_src = MOB.sort_values("moves", ascending=False).drop_duplicates("to_family").set_index("to_family").from_family
    dst = sorted(_dst_tot.index, key=lambda d: (list(_src_tot.index).index(main_src[d]), -_dst_tot[d]))
    right = [(1, d) for d in dst]
    flows = [((0, r.from_family), (1, r.to_family), r.moves, "focus" if r.from_family in SK_FOCUS else "ctx")
             for r in MOB.itertuples()]
    return [left, right], flows


PIPE = _csv("reskilling_pipeline")
_STAGES = [["Nominated"], ["Enrolled", "Declined"], ["Completed", "Withdrew"],
           ["Redeployed to data role", "Returned to prior role", "Left McKesson"]]


def _pipe(short=False):
    nm = {"Redeployed to data role": "Redeployed", "Returned to prior role": "Returned", "Left McKesson": "Left"}
    stage_of = {n: i for i, col in enumerate(_STAGES) for n in col}
    cols = [[(i, nm.get(n, n) if short else n) for n in col] for i, col in enumerate(_STAGES)]
    flows = [((stage_of[r.from_stage], nm.get(r.from_stage, r.from_stage) if short else r.from_stage),
              (stage_of[r.to_stage], nm.get(r.to_stage, r.to_stage) if short else r.to_stage), r.people, r.transfer)
             for r in PIPE.itertuples()]
    return cols, flows


SC = _csv("job_family_scorecard")
PC_AXES = [("vol_attrition_pct", "Vol. attrition\n(%)", "{:.1f}%", False),
           ("attrition_change_pts", "Change vs. FY25\n(pts)", "signed", False),
           ("engagement_index", "Engagement\n(index, reversed)", "{:.0f}", True),
           ("internal_fill_pct", "Internal fill\n(%, reversed)", "{:.0f}%", True),
           ("median_days_to_fill", "Time to fill\n(days)", "{:.0f}", False)]
_top2 = lambda col, asc=False: set(SC.sort_values(col, ascending=asc).job_family.iloc[:2])
PC_FOCUS = _top2("vol_attrition_pct")
assert PC_FOCUS == _top2("attrition_change_pts") == _top2("engagement_index", asc=True)
_fast = SC.loc[SC.median_days_to_fill.idxmin()]
TEXT["flow_pc_headline"] = ("Pharmacy Technicians and DC Associates are the two worst job families on attrition, "
                            "its trend and engagement")
TEXT["flow_pc_subtitle"] = (f"Profile of {WORDS[len(SC)]} job families on {WORDS[len(PC_AXES)]} measures, FY26 "
                            "(each axis scaled min–max; up = worse)")
TEXT["flow_pc_min_hc"] = f"{SC.headcount.min():,}"
TEXT["flow_pc_fast"] = f"{_fast.median_days_to_fill}"

SKILLS = _csv("skills_overlap")
VKEYS = ["clinical", "data_analytics", "supply_chain"]


def vcount(*on):
    m = np.logical_and.reduce([SKILLS[k] == (k in on) for k in VKEYS])
    return int(SKILLS.employees[m].sum())


TEXT["flow_venn_headline"] = (f"Only {vcount(*VKEYS)} of {int(SKILLS.employees.sum()):,} employees with a verified skill "
                              "profile combine clinical, data and supply-chain expertise")
TEXT["flow_venn_subtitle"] = "Employees by verified skill area, U.S. regular employees, skills inventory as of Mar 2026 (headcount)"


# ================================================================== SANKEY
@exhibit
def flow_sk_anatomy():
    fig = fig_px(640, 330)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.25, 0.02, 0.49, 0.88])
    cols, flows = _mob_columns()

    def color(f):
        return (C.focus, 0.6) if f[3] == "focus" else (C.context_light, 0.85)
    pos, bands = sankey(ax, cols, flows, color, size=LABEL - 0.5, headers=["From", "To"], header_size=TICK, gap=0.035,
                        z_order=lambda f: f[3] == "focus")
    ax.set_xlim(0, 1.014)
    ax.set_ylim(0, 1)
    dcl = [f for f in flows if f[1] == (1, "DC Leadership")][0]
    a_top, a_bot, b_top, b_bot = bands[dcl]
    marker(ax, (0.5, (a_top + b_bot) / 2), 4)
    spo = [f for f in flows if f[1] == (1, "Specialty Pharmacy Ops")][0]
    a_top, a_bot, b_top, b_bot = bands[spo]
    marker(ax, (0.82, (b_top + b_bot) / 2), 3, offset=(0, 0))
    cs = [f for f in flows if f[0] == (0, "Customer Care") and f[1] == (1, "Sales")][0]
    a_top, a_bot, b_top, b_bot = bands[cs]
    marker(ax, (0.25, (a_top + a_bot) / 2 - 0.01), 5)
    x, y0, y1 = pos[(0, _src_tot.index[0])]
    marker(ax, (x, (y0 + y1) / 2), 6, offset=(-70, -18))
    marker(ax, (0.007, 1.0 + 0.035 * 0.9), 7, offset=(-34, 8))
    x, y0, y1 = pos[cols[1][-1]]
    marker(ax, (x, (y0 + y1) / 2), 8, offset=(150, 0))
    return fig, (TEXT["flow_sk_headline"] + f", of {TEXT['flow_sk_total']} moves in all. The largest single path is "
                 f"Pharmacy Technician to Specialty Pharmacy Ops, {MOB.moves.max()} moves.")


def _sk_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    t = MINI - 3
    if kind in ("color_avoid", "color_fix"):
        ax = fig.add_axes([0.06, 0.04, 0.88, 0.92])
        cols, flows = _mob_columns()
        if kind == "color_avoid":
            sankey(ax, cols, flows, lambda f: (C.accent, 0.9), labels=False, gap=0.04)
        else:
            sankey(ax, cols, flows, lambda f: (C.focus, 0.6) if f[3] == "focus" else (C.context_light, 0.85),
                   labels=False, gap=0.04, z_order=lambda f: f[3] == "focus")
    elif kind in ("stage_avoid", "stage_fix", "style_avoid", "style_fix"):
        ax = fig.add_axes([0.13, 0.04, 0.72, 0.84])
        cols, flows = _pipe(short=True)
        by_type = {"progressed": (C.focus, 0.6), "dropped": (C.context, 0.5), "not_placed": (C.negative, 0.7)}
        if kind == "stage_avoid":
            stage_col = [C.accent, C.focus, C.focus_light]
            sankey(ax, cols, flows, lambda f: (stage_col[f[0][0]], 0.8), labels=False, gap=0.05)
        elif kind == "stage_fix":
            sankey(ax, cols, flows, lambda f: by_type[f[3]], labels=False, gap=0.05)
        elif kind == "style_avoid":
            pos, _ = sankey(ax, cols, flows, lambda f: by_type[f[3]], labels=False, gap=0.05, curved=False,
                            node_w=0.05)
            size = {}
            for s, d, v, _ in flows:
                size[d] = size.get(d, 0) + v
                size[s] = max(size.get(s, 0), sum(f[2] for f in flows if f[0] == s))
            for k, (x, y0, y1) in pos.items():
                v = size[k]
                ax.text(x + 0.025, (y0 + y1) / 2, f"{v:,}", ha="center", va="center", fontsize=t - 0.5, color="white",
                        fontweight=700, zorder=5, bbox=dict(boxstyle="square,pad=0.25", fc=C.focus, ec=C.focus))
        else:
            sankey(ax, cols, flows, lambda f: by_type[f[3]], size=t, label_name=False, gap=0.05)
        ax.set_xlim(-0.02, 1.12)
        ax.set_ylim(0, 1)
    else:                                               # small flows: shown vs merged into Other
        ax = fig.add_axes([0.3, 0.04, 0.38, 0.92])
        src = [("Rx Tech", "Spec. Rx", 310), ("DC Assoc.", "DC Lead.", 260),
               ("Cust. Care", "Sales", 120)]          # schematic: three large paths plus three tiny ones
        tiny = [("Cust. Care", "HR", 6), ("DC Assoc.", "Finance", 4), ("Rx Tech", "HR", 7)]
        left = ["Rx Tech", "DC Assoc.", "Cust. Care"]
        if kind == "small_avoid":
            right = ["Spec. Rx", "DC Lead.", "Sales", "HR", "Finance"]
            fl = src + tiny
        else:
            right = ["Spec. Rx", "DC Lead.", "Sales", "Other"]
            fl = src + [(s, "Other", v) for s, _, v in tiny]
        flows = [((0, s), (1, d), v, "x") for s, d, v in fl]
        merged = {}
        for f in flows:
            merged[(f[0], f[1])] = merged.get((f[0], f[1]), 0) + f[2]
        flows = [(s, d, v, "x") for (s, d), v in merged.items()]
        sankey(ax, [[(0, n) for n in left], [(1, n) for n in right]], flows, lambda f: (C.context, 0.55), size=t,
               gap=0.06, fmt="{:,.0f}")
        ax.set_xlim(0, 1.02)
        ax.set_ylim(0, 1)
    return fig


for _k, _alt in {"color_avoid": "Every flow in one dark color: the crossing paths can't be traced.",
                 "color_fix": "The two frontline sources' flows in blue, the rest light grey.",
                 "stage_avoid": "Each stage of the pipeline in its own color, which repeats the stage split.",
                 "stage_fix": "One color per transfer type at every step: progressed blue, dropped grey, not placed orange.",
                 "style_avoid": "Straight angular bands and values in boxes.",
                 "style_fix": "Curved bands, thin node bars and plain numbers.",
                 "small_avoid": "Flows of 4, 6 and 7 people shown as their own paths and nodes.",
                 "small_fix": "Small flows merged into one Other node."}.items():
    EXHIBITS[f"flow_sk_bp_{_k}"] = (lambda k=_k, a=_alt: (_sk_mini(k), a))


# ================================================================== PARALLEL COORDINATES
def _norm(axes=PC_AXES, d=SC, normalize=True, flip=True):
    out = pd.DataFrame(index=d.index)
    for col, _, _, rev in axes:
        s = d[col].astype(float)
        out[col] = (s - s.min()) / (s.max() - s.min()) if normalize else s
        if rev and flip and normalize:
            out[col] = 1 - out[col]
    return out


def _fmt(f, v):
    return mv.signed(v, 1) if f == "signed" else f.format(v)


def parcoords(ax, *, axes=PC_AXES, focus=PC_FOCUS, size=TICK, lw=(1.2, 2.4), ends=True, names=True, label_ends=True,
              colors=None, normalize=True, flip=True, ylim=None, bold_first=3, name_size=None):
    norm = _norm(axes, normalize=normalize, flip=flip)
    x = np.arange(len(axes))
    for i, (col, name, f, rev) in enumerate(axes):
        top_lo = ylim if ylim else (0, 1)
        ax.plot([i, i], top_lo, color=C.axis, lw=0.75, zorder=1)
        if ends:
            lo, hi = SC[col].min(), SC[col].max()
            top, bot = (lo, hi) if (rev and flip) else (hi, lo)
            ax.text(i, top_lo[1] + 0.03 * (top_lo[1] - top_lo[0]), _fmt(f, top), ha="center", va="bottom",
                    fontsize=size - 2, color=C.text_muted)
            ax.text(i, top_lo[0] - 0.03 * (top_lo[1] - top_lo[0]), _fmt(f, bot), ha="center", va="top",
                    fontsize=size - 2, color=C.text_muted)
        if names:
            hot = i < bold_first
            ax.text(i, top_lo[0] - 0.13 * (top_lo[1] - top_lo[0]), name, ha="center", va="top",
                    fontsize=name_size or size - 1, linespacing=1.15, color=C.headline if hot else C.text,
                    fontweight=600 if hot else 400)
    cols = [c for c, *_ in axes]
    for idx in SC.index[~SC.job_family.isin(focus)]:
        c = colors[SC.job_family[idx]] if colors else C.context
        ax.plot(x, norm.loc[idx, cols], color=c, lw=lw[0], alpha=0.8 if not colors else 1, zorder=2)
    ys = {}
    for idx in SC.index[SC.job_family.isin(focus)]:
        c = colors[SC.job_family[idx]] if colors else C.focus
        ax.plot(x, norm.loc[idx, cols], color=c, lw=lw[1], zorder=3, solid_capstyle="round")
        ys[SC.job_family[idx]] = norm.loc[idx, cols[-1]]
    if label_ends:
        prev = 9.0
        for fam, y in sorted(ys.items(), key=lambda t: -t[1]):
            y = min(y, prev - 0.09)
            prev = y
            ax.text(x[-1] + 0.1, y, SHORT.get(fam, fam), va="center", fontsize=size - 0.5, fontweight=600,
                    color=C.focus)
    ax.set_xlim(-0.4, len(axes) - 0.4)
    ax.axis("off")
    return norm


@exhibit
def flow_pc_anatomy():
    fig = fig_px(640, 330)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.04, 0.22, 0.84, 0.68])
    norm = parcoords(ax, size=TICK)
    ax.set_xlim(-0.3, len(PC_AXES) - 0.75)
    ax.set_ylim(0, 1)
    j = len(PC_AXES) - 1
    fy = norm.loc[SC.median_days_to_fill.idxmin(), "median_days_to_fill"]
    ax.annotate("", xy=(j - 0.02, fy + 0.01), xytext=(j - 0.5, 0.16),
                arrowprops=dict(arrowstyle="-", color=C.annotation, lw=0.75))
    ax.text(j - 0.52, 0.2, "Fast to backfill", ha="right", va="bottom", fontsize=ANNOT, fontweight=600,
            color=C.annotation, path_effects=mv.halo(width=3))
    ax.text(j - 0.52, 0.19, f"DC roles fill in {_fast.median_days_to_fill} days,\nthe fastest of any family", ha="right",
            va="top", fontsize=ANNOT - 0.5, color=C.annotation, path_effects=mv.halo(width=3), linespacing=1.2)
    pt = SC.index[SC.job_family == "Pharmacy Technician"][0]
    ctx = SC.index[SC.job_family == "Sales"][0]
    marker(ax, (0, -0.13), 3, offset=(-52, -14))
    marker(ax, (0.5, 0.72), 4)
    marker(ax, (0.5, (norm.loc[ctx].iloc[0] + norm.loc[ctx].iloc[1]) / 2), 5, offset=(0, -12))
    marker(ax, (1, 1.03), 6, offset=(26, 9))
    marker(ax, (2, -0.13), 7, offset=(64, -14))
    marker(ax, (j - 0.52, 0.2), 8, offset=(-118, 10))
    return fig, (TEXT["flow_pc_headline"] + f". Pharmacy Technician attrition {SC.vol_attrition_pct.max()}%, "
                 f"engagement of the two {SC.engagement_index.nsmallest(2).min()}–{SC.engagement_index.nsmallest(2).max()}; "
                 f"DC roles fill fastest at {_fast.median_days_to_fill} days.")


def _pc_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    t = MINI - 3
    short_axes = [(c, n, f, r) for (c, _, f, r), n in zip(PC_AXES, ["Attr.", "Chg.", "Eng.", "Fill", "Days"])]
    if kind == "table_avoid":
        ax = fig.add_axes([0, 0, 1, 1])
        hdr = ["", "Attr.", "Chg", "Eng.", "Int.", "Days"]
        rows = [[SHORT[f][:9]] + [f"{v}" for v in r] for f, *r in
                SC[["job_family"] + [c for c, *_ in PC_AXES]].itertuples(index=False)]
        cw = [0.3, 0.14, 0.14, 0.14, 0.14, 0.14]
        y = 0.95
        for row in [hdr] + rows:
            x = 0.0
            for w, cell in zip(cw, row):
                ax.add_patch(Rectangle((x, y - 0.1), w, 0.1, fill=False, ec=C.text, lw=0.6))
                ax.text(x + 0.015, y - 0.05, cell, va="center", fontsize=t - 0.5, color=C.text,
                        fontweight=700 if row is hdr else 400)
                x += w
            y -= 0.1
        ax.set_xlim(-0.01, 1.01)
        ax.set_ylim(0, 1)
        ax.axis("off")
        return fig
    ax = fig.add_axes([0.03, 0.2, 0.8, 0.72])
    kw = dict(axes=short_axes, size=t + 1, ends=False, name_size=t, bold_first=0, lw=(0.9, 1.8))
    if kind == "table_fix":
        parcoords(ax, label_ends=False, **kw)
    elif kind == "color_avoid":
        blues = [C.focus, C.accent, C.focus_light, mv.SEQUENTIAL["blue"][1], mv.SEQUENTIAL["blue"][4], C.focus,
                 C.accent, C.focus_light]
        parcoords(ax, label_ends=False, colors=dict(zip(SC.job_family, blues)), focus=(), **kw)
    elif kind == "color_fix":
        parcoords(ax, label_ends=False, **kw)
    elif kind == "scale_avoid":
        parcoords(ax, label_ends=False, normalize=False, ylim=(0, 80), **kw)
        ax.set_ylim(-14, 80)
        return fig
    elif kind == "scale_fix":
        parcoords(ax, label_ends=False, **kw)
    elif kind == "dir_avoid":
        parcoords(ax, label_ends=False, flip=False, **kw)
    elif kind == "dir_fix":
        parcoords(ax, label_ends=False, **{**kw, "axes": [(c, n + ("*" if r else ""), f, r) for c, n, f, r in short_axes]})
        ax.text(len(short_axes) - 1, 1.04, "Up = worse", ha="right", va="bottom", fontsize=t, color=C.text_muted)
    ax.set_ylim(-0.17, 1.05)
    return fig


for _k, _alt in {"table_avoid": "A dense table of eight job families by five measures, with heavy borders.",
                 "table_fix": "The same data as parallel coordinates with two lines in blue.",
                 "color_avoid": "Every line in a different shade of blue: a tangle with no focus.",
                 "color_fix": "Two lines in blue, the rest light grey.",
                 "scale_avoid": "Raw values on one shared scale: the small measures flatten to the bottom.",
                 "scale_fix": "Each axis scaled min to max, so every measure uses the full height.",
                 "dir_avoid": "Axes pointing different ways: the focus lines zigzag between good and bad.",
                 "dir_fix": "Engagement and internal fill reversed and marked, so up always means worse."}.items():
    EXHIBITS[f"flow_pc_bp_{_k}"] = (lambda k=_k, a=_alt: (_pc_mini(k), a))


# ================================================================== VENN
def circle(cx, cy, r=1.0, k=240):
    t = np.linspace(0, 2 * np.pi, k, endpoint=False)
    return np.c_[cx + r * np.cos(t), cy + r * np.sin(t)]


def clip(subject, clipper):
    """Polygon ∩ convex polygon (Sutherland-Hodgman), both counter-clockwise."""
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def cross(p, q, a, b):
        d1, d2 = q - p, b - a
        t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / (d1[0] * d2[1] - d1[1] * d2[0])
        return p + t * d1

    out = subject
    for a, b in zip(clipper, np.roll(clipper, -1, axis=0)):
        pts, out = out, []
        for p, q in zip(pts, np.roll(pts, -1, axis=0)):
            if inside(q, a, b):
                if not inside(p, a, b):
                    out.append(cross(p, q, a, b))
                out.append(q)
            elif inside(p, a, b):
                out.append(cross(p, q, a, b))
        out = np.array(out)
    return out


VCENTERS = [(-0.55, 0.32), (0.55, 0.32), (0.0, -0.63)]
VTONE = {1: mv.SEQUENTIAL["blue"][1], 2: mv.SEQUENTIAL["blue"][3], 3: mv.SEQUENTIAL["blue"][5]}
VLABELS = [(-1.0, 0.62, "Clinical", ("clinical",), 1), (1.0, 0.62, "Data &\nanalytics", ("data_analytics",), 1),
           (0.0, -1.15, "Supply chain", ("supply_chain",), 1), (0.0, 0.8, None, ("clinical", "data_analytics"), 2),
           (-0.64, -0.38, None, ("clinical", "supply_chain"), 2), (0.64, -0.38, None, ("data_analytics", "supply_chain"), 2),
           (0.0, 0.0, None, tuple(VKEYS), 3)]


def venn(ax, *, tone=VTONE, size=LABEL, counts=True, names=True, centers=VCENTERS):
    circ = [circle(*c) for c in centers]
    pairs = [clip(circ[a], circ[b]) for a in range(3) for b in range(a + 1, 3)]
    trio = clip(pairs[0], circ[2])
    for polys, level in ((circ, 1), (pairs, 2), ([trio], 3)):           # paint light -> dark, exact token fills
        for p in polys:
            ax.add_patch(Polygon(p, color=tone[level], lw=0))
    for x, y, name, on, level in VLABELS:
        if not counts and not (names and name):
            continue
        n = vcount(*on)
        num = f"{n:,}" if n >= 10 else "n<10"
        txt = (f"{name}\n{num}" if counts else name) if (name and names) else num
        ax.text(x, y, txt, ha="center", va="center", fontsize=size, linespacing=1.25, color=mv.text_on(tone[level]),
                fontweight=700 if name or level == 3 else 500)
    ax.set_aspect("equal")
    ax.axis("off")
    return circ


@exhibit
def flow_venn_anatomy():
    fig = fig_px(640, 330)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    venn(ax, size=LABEL)
    note = dict(fontsize=ANNOT, color=C.annotation, va="top")
    ax.plot([0.12, 1.6], [0.0, 0.0], color=C.annotation, lw=0.75)
    ax.text(1.65, 0.1, "Clinical + data + supply chain", fontweight=600, **note)
    ax.text(1.65, -0.06, "The hybrid profile behind\nautomated specialty-pharmacy\nfulfillment", linespacing=1.3, **note)
    ax.plot([-1.6, -0.05], [1.0, 1.0], color=C.annotation, lw=0.75)
    ax.text(-1.65, 1.1, "Clinical + data", fontweight=600, ha="right", **note)
    ax.text(-1.65, 0.94, "Candidates for clinical\ninformatics roles", linespacing=1.3, ha="right", **note)
    ax.set_xlim(-3.35, 3.45)
    ax.set_ylim(-1.72, 1.42)
    marker(ax, (-1.0, 0.62), 3, offset=(-46, 0))
    marker(ax, (0.64, -0.38), 4, offset=(30, -6))
    marker(ax, (0.0, 0.0), 5, offset=(0, -22))
    marker(ax, (1.42, 0.0), 6, offset=(0, 0))
    marker(ax, (0.55 + 0.71, 0.32 + 0.71), 7, offset=(10, 10))
    return fig, (TEXT["flow_venn_headline"] + f". Two-skill overlaps: clinical and supply chain {vcount('clinical', 'supply_chain')}, "
                 f"data and supply chain {vcount('data_analytics', 'supply_chain')}, clinical and data "
                 f"{vcount('clinical', 'data_analytics')}.")


def _venn_mini(kind):
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    t = MINI - 3
    if kind == "sets_fix":                                   # combination bars (UpSet-style)
        ax = fig.add_axes([0.3, 0.36, 0.68, 0.6])
        combos = [(tuple(k for k in VKEYS if r[k]), r.employees) for _, r in SKILLS.iterrows()]
        combos.sort(key=lambda c: -c[1])
        x = np.arange(len(combos))
        ax.bar(x, [c[1] for c in combos], color=[C.focus if len(c[0]) == 3 else C.context for c in combos], width=0.67)
        for xx, (_, v) in zip(x, combos):
            ax.text(xx, v + 60, f"{v:,}", ha="center", va="bottom", fontsize=t - 1, color=C.text)
        ax.set_xlim(-0.6, len(combos) - 0.4)
        ax.set_ylim(0, 4600)
        ax.axis("off")
        dx = fig.add_axes([0.3, 0.03, 0.68, 0.3])
        for i, k in enumerate(VKEYS):
            for xx, (on, _) in zip(x, combos):
                dx.scatter(xx, 2 - i, s=14, color=C.headline if k in on else C.grid, zorder=3)
            dx.text(-0.8, 2 - i, ["Clinical", "Data", "Supply"][i], ha="right", va="center", fontsize=t, color=C.text)
        for xx, (on, _) in zip(x, combos):
            ys = [2 - VKEYS.index(k) for k in on]
            dx.plot([xx, xx], [min(ys), max(ys)], color=C.headline, lw=1, zorder=2)
        dx.set_xlim(-0.6, len(combos) - 0.4)
        dx.set_ylim(-0.5, 2.5)
        dx.axis("off")
        return fig
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    if kind == "shade_avoid":
        venn(ax, tone={1: VTONE[3], 2: VTONE[2], 3: VTONE[1]}, counts=False, names=False)
    elif kind == "shade_fix":
        venn(ax, counts=False, names=False)
    elif kind == "blend_avoid":
        for (cx, cy), col in zip(VCENTERS, [C.focus, mv.CATEGORICAL[3], C.negative]):
            ax.add_patch(plt.Circle((cx, cy), 1, color=col, alpha=0.5, lw=0))
        ax.set_aspect("equal")
        ax.axis("off")
    elif kind == "blend_fix":
        venn(ax, counts=False, names=False)
    elif kind == "sets_avoid":
        for (cx, cy, ang) in [(-0.35, 0.0, 45), (0.35, 0.0, -45), (-0.1, 0.3, 60), (0.1, 0.3, -60)]:
            ax.add_patch(Ellipse((cx, cy), 2.2, 1.1, angle=ang, color=C.focus, alpha=0.3, lw=0))
        ax.set_aspect("equal")
        ax.axis("off")
    elif kind == "text_avoid":
        venn(ax, counts=False, names=False)
        for x, y, txt in [(-0.95, 0.55, "Clinical skills\nverified by\nmanagers in\nthe inventory"),
                          (0.95, 0.55, "Data and\nanalytics skills\nfrom projects\nand courses"),
                          (0.0, -1.1, "Supply chain\nplanning and\noperations")]:
            ax.text(x, y, txt, ha="center", va="center", fontsize=t - 1, color=C.text, linespacing=1.1)
        ax.text(0, 0.05, "The rare\nhybrid profile", ha="center", va="center", fontsize=t - 1.5, color="white")
    elif kind == "text_fix":
        venn(ax, counts=False, size=t + 0.5)
        ax.plot([0.12, 1.75], [0, 0], color=C.annotation, lw=0.75)
        ax.text(1.8, 0.12, "The rare hybrid", fontsize=t, fontweight=700, color=C.annotation, va="top")
        ax.text(1.8, -0.14, "All three skills", fontsize=t, color=C.annotation, va="top")
        ax.set_xlim(-1.75, 3.6)
        ax.set_ylim(-1.75, 1.45)
        return fig
    ax.set_xlim(-2.35, 2.35)
    ax.set_ylim(-1.75, 1.45)
    return fig


for _k, _alt in {"shade_avoid": "A Venn whose overlaps are lighter than the single sets.",
                 "shade_fix": "Overlaps darker with each level: light, mid and navy.",
                 "blend_avoid": "Three translucent circles in different hues blending into muddy tones.",
                 "blend_fix": "Each region filled with an exact blue from the ramp.",
                 "sets_avoid": "Four overlapping ellipses: fifteen regions nobody can read.",
                 "sets_fix": "Combination bars with a dot matrix marking the skill areas in each combination.",
                 "text_avoid": "Long descriptions crammed inside the circles.",
                 "text_fix": "Short names inside; the description outside with a leader line."}.items():
    EXHIBITS[f"flow_venn_bp_{_k}"] = (lambda k=_k, a=_alt: (_venn_mini(k), a))
