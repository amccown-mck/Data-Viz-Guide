"""Distribution exhibits: strip and box plots, histograms, beeswarms, small-multiple histograms. Registered on import.

People data: every group plotted has n >= 10, dots are anonymous, and no label carries an individual's value."""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Rectangle

import mckviz as mv
from exhibits import (ANNOT, ANTI, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px, marker)

MIN_N = 10
WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}

# ------------------------------------------------------------------ data
CR = _csv("compa_ratio_individuals")
_g = CR.groupby("job_family").compa_ratio
ST = _g.agg(n="size", median="median", mean="mean", low=lambda s: (s < 0.9).mean() * 100,
            p10=lambda s: s.quantile(0.1), q1=lambda s: s.quantile(0.25), q3=lambda s: s.quantile(0.75),
            p90=lambda s: s.quantile(0.9))
assert (ST.n >= MIN_N).all()
ORDER = list(ST.sort_values("median").index)                       # lowest median first (top row)
FOCUS = ST.low.idxmax()
_ratio = ST.low[FOCUS] / ST.drop(FOCUS).low.max()
FAM = {"Distribution Center Associate": "DC Associate", "Pharmacy Technician": "Pharmacy Technician",
       "Customer Care Rep": "Customer Care Rep", "Pharmacist": "Pharmacist", "Software Engineer": "Software Engineer",
       "Supply Chain Planner": "Supply Chain Planner"}
FAM_T = {"Distribution Center Associate": "DC Assoc.", "Pharmacy Technician": "Pharm. Tech",
         "Customer Care Rep": "Care Rep", "Pharmacist": "Pharmacist", "Software Engineer": "Software Eng.",
         "Supply Chain Planner": "SC Planner"}
TEXT.update(
    ds_strip_headline=(f"One in {WORD[round(100 / ST.low[FOCUS])]} pharmacy technicians is paid below 0.90 of range "
                       f"midpoint, about {_ratio:.0f}× the share in any other job family"),
    ds_strip_subtitle="Compa-ratio (base pay ÷ salary-range midpoint) by job family, U.S. regular employees, Mar 2026",
    ds_n_people=f"{len(CR):,}",
    ds_focus_low=f"{ST.low[FOCUS]:.0f}%",
    ds_all_mean=f"{CR.compa_ratio.mean():.2f}",
    ds_all_low=f"{(CR.compa_ratio < 0.9).mean() * 100:.0f}%",
    ds_min_n=str(MIN_N),
)

SP = _csv("span_of_control").direct_reports
LIMIT = 15
_over = (SP > LIMIT).mean() * 100
TEXT.update(
    ds_hist_headline=f"About 1 in {round(100 / _over)} people managers runs a team wider than the {LIMIT}-report design limit",
    ds_hist_subtitle="People managers by number of direct reports, U.S., Mar 2026 (number of managers)",
    ds_over=f"{_over:.0f}%", ds_n_managers=f"{len(SP):,}", ds_span_median=f"{SP.median():.0f}",
    ds_span_mean=f"{SP.mean():.1f}", ds_span_max=str(SP.max()),
)


# ------------------------------------------------------------------ helpers
def strip(ax, fams=None, *, jitter=0.28, s=6, alpha=0.45, box=True, zone=True, ref=True, size=LABEL, tick=TICK,
          right=True, xlim=(0.68, 1.30), xticks=(0.7, 0.8, 0.9, 1.0, 1.1, 1.2), focus=FOCUS, seed=1, notes=True,
          box_h=0.34, whis=None, names=None, labels=True):
    """Compa-ratio strip plot (+ box) by job family, first family at the top. Returns the row positions."""
    fams = fams or ORDER
    rng = np.random.default_rng(seed)                                  # fixed jitter: reproducible
    n = len(fams)
    top = -0.62
    if zone:
        ax.axvspan(xlim[0], 0.90, color=C.surface_subtle, lw=0, zorder=0)
        if notes:
            ax.text(xlim[0] + 0.006, top, "Below 0.90", fontsize=size - 1.5, color=C.annotation, fontweight=600,
                    va="bottom")
    if ref:
        ax.axvline(1.0, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
        if notes:
            ax.text(1.0, top, "Range midpoint", fontsize=size - 1.5, color=C.annotation, ha="center", va="bottom",
                    bbox=dict(fc="white", ec="none", pad=1), zorder=4)
    for y, fam in enumerate(fams):
        x = CR.compa_ratio[CR.job_family == fam].values
        col = C.focus if fam == focus else C.context
        if jitter:
            ax.scatter(x, y + rng.uniform(-jitter, jitter, len(x)), s=s, color=col, alpha=alpha, lw=0, zorder=2)
        else:
            ax.scatter(x, np.full(len(x), y), s=s, color=col, alpha=alpha, lw=0, zorder=2)
        if box:
            q1, med, q3 = np.quantile(x, [0.25, 0.5, 0.75])
            ax.add_patch(Rectangle((q1, y - box_h), q3 - q1, 2 * box_h, fill=False, ec=C.headline, lw=1, zorder=3))
            ax.plot([med, med], [y - box_h, y + box_h], color=C.headline, lw=2.2, zorder=3)
            if whis:
                lo, hi = np.quantile(x, whis)
                ax.plot([lo, q1], [y, y], color=C.headline, lw=0.9, zorder=3)
                ax.plot([q3, hi], [y, y], color=C.headline, lw=0.9, zorder=3)
        if right:
            st = ST.loc[fam]
            hot = fam == focus
            ax.text(xlim[1] - 0.075, y, f"{st.low:.0f}%", va="center", ha="right", fontsize=size,
                    color=C.headline if hot else C.text, fontweight=700 if hot else 500)
            ax.text(xlim[1] - 0.065, y, f"n={int(st.n):,}", va="center", ha="left", fontsize=size - 2.5,
                    color=C.text_muted)
    if right and notes:
        ax.text(xlim[1] - 0.075, top, "Below 0.90", fontsize=size - 2, ha="right", va="bottom", color=C.text_muted)
    if labels:
        ax.set_yticks(range(n), [(names or FAM).get(f, f) for f in fams])
        for t in ax.get_yticklabels():
            t.set_fontsize(tick)
            if t.get_text() == (names or FAM).get(focus, focus):
                t.set_fontweight(600)
                t.set_color(C.headline)
    else:
        ax.set_yticks([])
    ax.set_ylim(n - 0.45, top - (0.5 if notes else 0.05))
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks, [f"{v:.2f}" for v in xticks])
    ax.tick_params(length=0)
    ax.tick_params(axis="x", labelsize=tick - 1, colors=C.text_muted)
    _plain(ax)
    return range(n)


def histogram(ax, *, size=LABEL, tick=TICK, focus=True, grid=True, callout=True, limit_label=True, seam=1.0):
    edges = np.arange(0.5, 41, 1)                                       # whole numbers: one bin per value
    counts, _ = np.histogram(SP, bins=edges)
    mids = (edges[:-1] + edges[1:]) / 2
    cols = [C.focus if (focus and m > LIMIT) else C.context for m in mids]
    ax.bar(mids, counts, width=1, color=cols, edgecolor="white", lw=seam, zorder=2)
    ax.axvline(LIMIT + 0.5, color=C.total, lw=0.9, ls=(0, (2.5, 2.5)), zorder=3)
    top = counts.max() * 1.12
    if limit_label:
        ax.text(LIMIT + 0.5, top, f"Design limit: {LIMIT}", ha="center", va="bottom", fontsize=size - 1,
                color=C.annotation, bbox=dict(fc="white", ec="none", pad=1), zorder=4)
    if callout:
        ax.text(LIMIT + 2.2, counts.max() * 0.62, f"{_over:.0f}% of managers", fontsize=size, color=C.focus,
                fontweight=700, va="bottom")
        ax.text(LIMIT + 2.2, counts.max() * 0.6, f"have more than {LIMIT} direct reports", fontsize=size - 1,
                color=C.text, va="top")
    ax.set_xlim(0, 41)
    ax.set_ylim(0, top)
    ax.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
    if grid:
        ax.set_yticks([0, 50, 100, 150])
        ax.grid(axis="y", color=C.grid, lw=0.75, zorder=0)
    else:
        ax.set_yticks([])
    ax.tick_params(length=0, labelsize=tick - 1, colors=C.text_muted)
    _plain(ax, bottom=True)
    return counts, mids


# ================================================================== STRIP + BOX
@exhibit
def ds_strip_anatomy():
    fig = fig_px(640, 330)
    ax = fig.add_subplot()
    strip(ax, s=10, alpha=0.5)
    yf = ORDER.index(FOCUS)
    fx = CR.compa_ratio[CR.job_family == FOCUS]
    marker(ax, (fx.quantile(0.05), yf), 3, offset=(-6, 17))
    oth = ORDER[-1]
    ox = CR.compa_ratio[CR.job_family == oth]
    marker(ax, (1.155, 1), 4)
    q3 = fx.quantile(0.75)
    marker(ax, (q3, yf), 5, offset=(12, 15))
    marker(ax, (0.78, -0.62), 6, offset=(14, 8))
    marker(ax, (1.30 - 0.065, yf), 7, offset=(46, 0))
    marker(ax, (0.75, len(ORDER) - 0.45), 8, offset=(0, -14))
    return fig, (TEXT["ds_strip_headline"] + f". {ST.low[FOCUS]:.0f}% of {int(ST.n[FOCUS])} pharmacy technicians are "
                 f"below 0.90; no other family exceeds {ST.drop(FOCUS).low.max():.0f}%.")


# ================================================================== HISTOGRAM
@exhibit
def ds_hist_anatomy():
    fig = fig_px(640, 320)
    ax = fig.add_subplot()
    counts, mids = histogram(ax)
    ax.set_xlabel("Direct reports per manager", fontsize=TICK - 1, color=C.text_muted, labelpad=4)
    marker(ax, (19, counts[18]), 3, offset=(0, 14))
    marker(ax, (7, counts[6]), 4, offset=(0, 14))
    marker(ax, (LIMIT + 0.5, counts.max() * 1.12), 5, offset=(-56, 8))
    marker(ax, (LIMIT + 2.2, counts.max() * 0.62), 6, offset=(-24, 7))
    marker(ax, (30, 0), 7, offset=(0, 14))
    marker(ax, (38, 100), 8, offset=(0, 9))
    return fig, (TEXT["ds_hist_headline"] + f". {_over:.0f}% of {len(SP):,} managers have more than {LIMIT} direct "
                 f"reports; the median is {SP.median():.0f}.")


# ================================================================== VARIANTS
@exhibit
def ds_var_box():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    for y, fam in enumerate(ORDER):
        x = CR.compa_ratio[CR.job_family == fam]
        p10, q1, med, q3, p90 = np.quantile(x, [0.1, 0.25, 0.5, 0.75, 0.9])
        hot = fam == FOCUS
        ax.add_patch(Rectangle((q1, y - 0.3), q3 - q1, 0.6, fc=C.focus if hot else C.context_light,
                               ec=C.focus if hot else C.headline, lw=0.9, zorder=3))
        ax.plot([med, med], [y - 0.3, y + 0.3], color="white" if hot else C.headline, lw=2, zorder=4)
        for a, b in ((p10, q1), (q3, p90)):
            ax.plot([a, b], [y, y], color=C.headline, lw=0.9, zorder=2)
    ax.axvline(1.0, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
    ax.set_yticks(range(len(ORDER)), [FAM_T[f] for f in ORDER])
    for t in ax.get_yticklabels():
        t.set_fontsize(MINI - 1.5)
        if t.get_text() == FAM_T[FOCUS]:
            t.set_fontweight(600)
            t.set_color(C.headline)
    ax.set_ylim(len(ORDER) - 0.5, -0.6)
    ax.set_xlim(0.78, 1.14)
    ax.set_xticks([0.8, 0.9, 1.0, 1.1], ["0.80", "0.90", "1.00", "1.10"])
    ax.tick_params(length=0, labelsize=MINI - 2, colors=C.text_muted)
    ax.tick_params(axis="y", colors=C.text)
    _plain(ax)
    return fig, "Box plots of compa-ratio by job family; whiskers at the 10th and 90th percentiles; Pharmacy Technician filled blue."


@exhibit
def ds_var_range():
    fig = fig_px(300, 190)
    ax = fig.add_subplot()
    for y, fam in enumerate(ORDER):
        st = ST.loc[fam]
        hot = fam == FOCUS
        ax.plot([st.p10, st.p90], [y, y], color=C.focus if hot else C.context, lw=7, solid_capstyle="butt", zorder=2)
        ax.plot([st["median"]] * 2, [y - 0.3, y + 0.3], color=C.headline, lw=2, zorder=3)
        ax.text(st.p90 + 0.008, y, f"{st.p10:.2f}–{st.p90:.2f}", va="center", fontsize=MINI - 2.5,
                color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    ax.axvline(1.0, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
    ax.set_yticks(range(len(ORDER)), [FAM_T[f] for f in ORDER])
    for t in ax.get_yticklabels():
        t.set_fontsize(MINI - 1.5)
        if t.get_text() == FAM_T[FOCUS]:
            t.set_fontweight(600)
            t.set_color(C.headline)
    ax.set_ylim(len(ORDER) - 0.5, -0.6)
    ax.set_xlim(0.8, 1.2)
    ax.set_xticks([0.8, 0.9, 1.0, 1.1], ["0.80", "0.90", "1.00", "1.10"])
    ax.tick_params(length=0, labelsize=MINI - 2, colors=C.text_muted)
    ax.tick_params(axis="y", colors=C.text)
    _plain(ax)
    TEXT["ds_focus_p10"] = f"{ST.p10[FOCUS]:.2f}"
    return fig, "Range bars from the 10th to the 90th percentile with a median tick; Pharmacy Technician in blue."


def _swarm(x, px_per_unit, d_px):
    """Beeswarm offsets (in px): each dot takes the free slot closest to the center line."""
    xs = np.asarray(x) * px_per_unit
    order = np.argsort(xs)
    placed, out = [], np.zeros(len(xs))
    for i in order:
        cands = [0.0]
        for (px, py) in placed:
            dx = xs[i] - px
            if abs(dx) < d_px:
                dy = np.sqrt(d_px ** 2 - dx ** 2)
                cands += [py + dy, py - dy]
        for c in sorted(cands, key=abs):
            if all((xs[i] - px) ** 2 + (c - py) ** 2 >= d_px ** 2 - 1e-6 for px, py in placed if abs(xs[i] - px) < d_px):
                out[i] = c
                placed.append((xs[i], c))
                break
    return out


@exhibit
def ds_var_swarm():
    fams = ["Supply Chain Planner", "Pharmacist", "Software Engineer"]
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0.24, 0.13, 0.74, 0.85])
    xlim = (0.84, 1.20)
    ppu = 300 * 0.74 / (xlim[1] - xlim[0])
    row_px = 190 * 0.85 / 3
    d = 3.4
    for y, fam in enumerate(fams):
        x = CR.compa_ratio[CR.job_family == fam].values
        off = _swarm(x, ppu, d)
        ax.scatter(x, y + off / row_px, s=(d * 0.72) ** 2, c=[C.focus if v < 0.9 else C.context for v in x], lw=0,
                   zorder=3)
        ax.text(xlim[0] - 0.006, y, f"{FAM_T[fam]}\nn={int(ST.n[fam])}", ha="right", va="center", fontsize=MINI - 2,
                color=C.text, linespacing=1.15)
    ax.axvline(0.9, color=C.total, lw=0.8, ls=(0, (2.5, 2.5)), zorder=1)
    ax.text(0.897, -0.5, "0.90", ha="right", va="center", fontsize=MINI - 2.5, color=C.annotation)
    ax.set_xlim(*xlim)
    ax.set_ylim(2.55, -0.62)
    ax.set_yticks([])
    ax.set_xticks([0.9, 1.0, 1.1], ["0.90", "1.00", "1.10"])
    ax.tick_params(length=0, labelsize=MINI - 2, colors=C.text_muted)
    _plain(ax)
    return fig, "Beeswarm of compa-ratio for three smaller job families; each dot one person, the few below 0.90 in blue."


@exhibit
def ds_var_ridge():
    fig = fig_px(300, 190)
    fig.set_layout_engine("none")
    edges = np.arange(0.70, 1.2201, 0.02)
    n = len(ORDER)
    h = 0.84 / n
    shares = {f: np.histogram(CR.compa_ratio[CR.job_family == f], bins=edges)[0] / ST.n[f] * 100 for f in ORDER}
    ymax = max(s.max() for s in shares.values())
    for i, fam in enumerate(ORDER):
        ax = fig.add_axes([0.3, 0.92 - (i + 1) * h, 0.68, h * 0.92])
        hot = fam == FOCUS
        ax.bar(edges[:-1], shares[fam], width=0.02, align="edge", color=C.focus if hot else C.context,
               edgecolor="white", lw=0.4)
        ax.axvline(1.0, color=C.total, lw=0.7, ls=(0, (2, 2)))
        ax.set_xlim(edges[0], edges[-1])
        ax.set_ylim(0, ymax)
        ax.set_yticks([])
        if i < n - 1:
            ax.set_xticks([])
        else:
            ax.set_xticks([0.8, 0.9, 1.0, 1.1, 1.2], ["0.80", "0.90", "1.00", "1.10", "1.20"])
            ax.tick_params(length=0, labelsize=MINI - 2.5, colors=C.text_muted)
        _plain(ax, bottom=True)
        fig.text(0.28, 0.92 - (i + 0.55) * h, FAM_T[fam], ha="right", va="center", fontsize=MINI - 2,
                 color=C.headline if hot else C.text, fontweight=600 if hot else 400)
    return fig, "Six small histograms of compa-ratio, one per job family, on the same bins and the same scale."


# ================================================================== BEST PRACTICE MINIS
def _bp(kind):
    fig = fig_px(200, 140)
    ax = fig.add_subplot()
    t = MINI - 2.5
    kw = dict(size=t + 1, tick=t, s=2.2, right=False, notes=False, names=FAM_T, box_h=0.3)
    four = ORDER[:4]
    if kind == "spread_avoid":
        y = np.arange(len(four))
        ax.barh(y, [ST["mean"][f] for f in four], color=C.focus, height=0.6)
        for yy, f in zip(y, four):
            ax.text(ST["mean"][f] + 0.02, yy, f"{ST['mean'][f]:.2f}", va="center", fontsize=t, color=C.text)
        ax.set_yticks(y, [FAM_T[f] for f in four])
        ax.set_ylim(len(four) - 0.5, -0.6)
        ax.set_xlim(0, 1.25)
        ax.set_xticks([])
        ax.tick_params(labelsize=t, length=0)
        ax.set_title("Average compa-ratio", fontsize=t, color=C.text_muted, loc="left", pad=2)
        _plain(ax, left=True)
    elif kind == "spread_fix":
        strip(ax, four, xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2), **kw)
    elif kind in ("bins_avoid", "bins_fix"):
        x = CR.compa_ratio[CR.job_family == FOCUS]
        edges = np.arange(0.675, 1.2, 0.05) if kind == "bins_avoid" else np.arange(0.70, 1.2001, 0.02)
        c, _ = np.histogram(x, bins=edges)
        mids = (edges[:-1] + edges[1:]) / 2
        blue = mids < 0.9
        share = c[blue].sum() / len(x) * 100
        ax.bar(edges[:-1], c, width=np.diff(edges), align="edge", color=[C.focus if b else C.context for b in blue],
               edgecolor="white", lw=0.6)
        ax.axvline(0.9, color=C.total, lw=0.8, ls=(0, (2, 2)))
        ax.text(0.885, c.max() * 1.02, f"{share:.0f}% below\n0.90", ha="right", va="top", fontsize=t,
                color=C.focus, fontweight=700, linespacing=1.1)
        ax.set_xlim(0.68, 1.16)
        ax.set_xticks([0.8, 0.9, 1.0, 1.1], ["0.8", "0.9", "1.0", "1.1"])
        ax.set_yticks([])
        ax.tick_params(labelsize=t, length=0, colors=C.text_muted)
        _plain(ax, bottom=True)
        TEXT[f"ds_{kind}_share"] = f"{share:.0f}%"
    elif kind in ("scale_avoid", "scale_fix"):
        fig.set_layout_engine("none")
        ax.remove()
        fams = [FOCUS, "Pharmacist", "Software Engineer"]
        for i, fam in enumerate(fams):
            x = CR.compa_ratio[CR.job_family == fam]
            a = fig.add_axes([0.05, 0.69 - i * 0.29, 0.92, 0.2])
            edges = (np.arange(0.70, 1.2001, 0.02) if kind == "scale_fix"
                     else np.linspace(x.min(), x.max(), 16))
            sh = np.histogram(x, bins=edges)[0] / len(x) * 100
            a.bar(edges[:-1], sh, width=np.diff(edges), align="edge", edgecolor="white", lw=0.4,
                  color=C.focus if fam == FOCUS else C.context)
            if kind == "scale_fix":
                a.set_xlim(0.70, 1.20)
                a.set_ylim(0, 16)
                a.axvline(1.0, color=C.total, lw=0.7, ls=(0, (2, 2)))
            a.set_yticks([])
            a.set_xticks([0.8, 1.0, 1.2] if (kind == "scale_fix" and i == 2) else [])
            a.tick_params(labelsize=t - 0.5, length=0, colors=C.text_muted)
            a.set_title(FAM_T[fam], fontsize=t, loc="left", pad=1, color=C.text)
            _plain(a, bottom=True)
        return fig
    elif kind in ("minn_avoid", "minn_fix"):
        rng = np.random.default_rng(8)                      # schematic: four DC teams, two with fewer than 10 people
        teams = [("Inbound", 46), ("Outbound", 38), ("Returns", 7), ("Quality", 4)]
        vals = {nm: np.round(rng.normal(0.97, 0.05, n), 2) for nm, n in teams}
        if kind == "minn_fix":
            small = [nm for nm, n in teams if n < MIN_N]
            rows = [(nm, vals[nm]) for nm, n in teams if n >= MIN_N] + [
                (f"Other ({len(small)} teams)", np.concatenate([vals[s] for s in small]))]
        else:
            rows = [(nm, vals[nm]) for nm, _ in teams]
        for y, (nm, v) in enumerate(rows):
            ax.scatter(v, y + rng.uniform(-0.22, 0.22, len(v)), s=4, color=C.context, alpha=0.6, lw=0)
            ax.text(1.17, y, f"n={len(v)}", va="center", fontsize=t - 0.5, color=C.text_muted)
            if kind == "minn_avoid" and len(v) < MIN_N:
                for xv, yy in zip(sorted(v)[:2], (y - 0.32, y + 0.36)):
                    ax.text(xv, yy, f"{xv:.2f}", ha="center", va="center", fontsize=t - 1.5, color=C.negative_text)
        ax.set_yticks(range(len(rows)), [r[0] for r in rows])
        ax.set_ylim(len(rows) - 0.5, -0.6)
        ax.set_xlim(0.82, 1.24)
        ax.set_xticks([0.9, 1.0, 1.1], ["0.90", "1.00", "1.10"])
        ax.tick_params(labelsize=t, length=0)
        ax.tick_params(axis="x", colors=C.text_muted)
        _plain(ax)
    elif kind == "jitter_avoid":
        strip(ax, ORDER[:3], jitter=0, alpha=1, s=6, box=False, xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2),
              **{k: v for k, v in kw.items() if k not in ("s",)})
    elif kind == "jitter_fix":
        strip(ax, ORDER[:3], box=False, xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2), **kw)
    elif kind == "box_avoid":
        data = [CR.compa_ratio[CR.job_family == f].values for f in ORDER[:4]]
        ax.boxplot(data, vert=False, positions=range(4), widths=0.55, flierprops=dict(ms=2.5, mec=C.text),
                   medianprops=dict(color=ANTI_LINE), boxprops=dict(color=C.text), whiskerprops=dict(color=C.text),
                   capprops=dict(color=C.text))
        ax.set_yticks(range(4), [FAM_T[f] for f in ORDER[:4]])
        ax.set_ylim(3.5, -0.6)
        ax.set_xlim(0.68, 1.22)
        ax.set_xticks([0.8, 1.0, 1.2], ["0.80", "1.00", "1.20"])
        ax.tick_params(labelsize=t, length=0)
        _plain(ax, left=True, bottom=True)
    elif kind == "box_fix":
        strip(ax, ORDER[:4], jitter=0, alpha=0, box=True, whis=(0.1, 0.9), xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2),
              zone=False, **kw)
        ax.set_ylim(4.55, -0.6)
        ax.text(0.69, 4.05, "Box = middle 50%\nWhiskers = 10th–90th percentile", fontsize=t - 0.8,
                color=C.text_muted, va="center", linespacing=1.15, bbox=dict(fc="white", ec="none", pad=0.5),
                zorder=5)
    elif kind in ("clip_avoid", "clip_fix"):
        lim = (0.84, 1.10) if kind == "clip_avoid" else (0.66, 1.22)
        strip(ax, ORDER[:4], xlim=lim, xticks=(0.9, 1.0, 1.1) if kind == "clip_avoid" else (0.7, 0.9, 1.1), **kw)
        sub = CR[CR.job_family.isin(ORDER[:4])].compa_ratio
        TEXT["ds_clipped"] = f"{int(((sub < 0.84) | (sub > 1.10)).sum()):,}"
    elif kind == "sort_avoid":
        strip(ax, sorted(ORDER), xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2), **kw)
    elif kind == "sort_fix":
        strip(ax, ORDER, xlim=(0.68, 1.22), xticks=(0.8, 1.0, 1.2), **kw)
    return fig


ANTI_LINE = ANTI["rainbow"][1]      # matplotlib's default median orange: anti-example only

for _k, _alt in {"spread_avoid": "Bars of average compa-ratio that all look the same.",
                 "spread_fix": "Every person as a dot, with the box: the low tail is visible.",
                 "bins_avoid": "Wide bins that straddle 0.90, so the colored share is wrong.",
                 "bins_fix": "Narrow bins with an edge exactly on 0.90.",
                 "scale_avoid": "Three histograms, each on its own bins and range.",
                 "scale_fix": "The same three on shared bins and one scale.",
                 "minn_avoid": "Teams of 7 and 4 plotted, with individual values labelled.",
                 "minn_fix": "Teams under 10 merged into one group; n shown for every row.",
                 "jitter_avoid": "Opaque dots on one line per group: overlaps hide the density.",
                 "jitter_fix": "Jittered, translucent dots: dense areas read darker.",
                 "box_avoid": "Default box plots with 1.5 × IQR whiskers and outlier points, unexplained.",
                 "box_fix": "Boxes with 10th–90th percentile whiskers, explained in a note.",
                 "clip_avoid": "An axis that silently cuts off the people in the tails.",
                 "clip_fix": "An axis wide enough for everyone.",
                 "sort_avoid": "Groups in alphabetical order.",
                 "sort_fix": "Groups sorted by median, the focus group beside the zone."}.items():
    EXHIBITS[f"ds_bp_{_k}"] = (lambda k=_k, a=_alt: (_bp(k), a))
