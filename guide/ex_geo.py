"""Geo-spatial exhibits: tile-grid choropleth, bubble map, dot density, map best practice. Registered on import.

No state boundary files ship with the kit (geopandas isn't installed), so every map here is an equal-area tile grid:
one square per state in an approximate geographic layout. That is also the honest choice for state-level rates,
because a big, empty state gets no more ink than a small, dense one.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Circle, Rectangle

import mckviz as mv
from exhibits import ANNOT, ANTI, BAND, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px, marker

# Equal-area tile grid (row, col), the same layout as docs/cookbook/maps.md.
GRID = {"AK": (0, 0), "ME": (0, 10), "VT": (1, 9), "NH": (1, 10),
        "WA": (2, 0), "ID": (2, 1), "MT": (2, 2), "ND": (2, 3), "MN": (2, 4), "IL": (2, 5), "WI": (2, 6),
        "MI": (2, 7), "NY": (2, 8), "RI": (2, 9), "MA": (2, 10),
        "OR": (3, 0), "NV": (3, 1), "WY": (3, 2), "SD": (3, 3), "IA": (3, 4), "IN": (3, 5), "OH": (3, 6),
        "PA": (3, 7), "NJ": (3, 8), "CT": (3, 9),
        "CA": (4, 0), "UT": (4, 1), "CO": (4, 2), "NE": (4, 3), "MO": (4, 4), "KY": (4, 5), "WV": (4, 6),
        "VA": (4, 7), "MD": (4, 8), "DE": (4, 9),
        "AZ": (5, 1), "NM": (5, 2), "KS": (5, 3), "AR": (5, 4), "TN": (5, 5), "NC": (5, 6), "SC": (5, 7), "DC": (5, 8),
        "OK": (6, 3), "LA": (6, 4), "MS": (6, 5), "AL": (6, 6), "GA": (6, 7),
        "HI": (7, 0), "TX": (7, 3), "FL": (7, 8)}
GAP = 0.07                                                 # white gutter between tiles (tile units)
BASE = C.surface_subtle                                    # quiet base map: light sand


def centre(st):
    r, c = GRID[st]
    return c + 0.5, -r + 0.5


# ------------------------------------------------------------------ helpers
def tiles(ax, fills=None, *, text=None, size=MINI - 3, bold=(), abbr=True, edge="white", lw=0.0, gap=GAP,
          color=None, xmax=11.05, ymin=-7.08, only=None, hide=()):
    """Draw the tile grid. fills: {state: color} (default sand). text: {state: label} overrides the abbreviation."""
    fills = fills or {}
    for st, (r, c) in GRID.items():
        f = fills.get(st, BASE)
        ax.add_patch(Rectangle((c + gap / 2, -r + gap / 2), 1 - gap, 1 - gap, fc=f, ec=edge, lw=lw, zorder=1))
        if abbr and st not in hide and (only is None or st in only):
            lab = text.get(st, st) if text else st
            hot = st in bold
            ax.text(c + 0.5, -r + 0.5, lab, ha="center", va="center", fontsize=size, linespacing=1.05, zorder=2,
                    color=color or (mv.text_on(f) if (hot or f != BASE) else C.text_muted),
                    fontweight=700 if hot else 400)
    ax.set_xlim(-0.05, xmax)
    ax.set_ylim(ymin, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")


def classify(values: pd.Series, edges):
    return pd.Series(pd.cut(values, edges, labels=False, right=False), index=values.index).astype(int)


def legend_stack(ax, x, y, title, labels, colors, *, size=TICK - 1, step=0.52, sq=0.42):
    """Class key stacked high -> low (pass labels low -> high)."""
    ax.text(x, y, title, fontsize=size, color=C.text, va="bottom", fontweight=600)
    for i, (lab, col) in enumerate(zip(labels[::-1], colors[::-1])):
        yy = y - 0.18 - (i + 1) * step
        ax.add_patch(Rectangle((x, yy), sq, sq, fc=col, ec="none"))
        ax.text(x + sq + 0.18, yy + sq / 2, lab, fontsize=size, color=C.text, va="center")


def legend_row(ax, x, y, labels, colors, *, size=MINI - 3.5, w=0.9, h=0.32):
    """Compact class key in one row (for minis): adjoining swatches with labels beneath."""
    for i, (lab, col) in enumerate(zip(labels, colors)):
        ax.add_patch(Rectangle((x + i * w, y), w, h, fc=col, ec="white", lw=0.6))
        ax.text(x + i * w + w / 2, y - 0.1, lab, fontsize=size, color=C.text, ha="center", va="top")


def bubbles(ax, sites, sizes, colors, *, rmax=0.72, vmax=None, area=True, edge="white", lw=1.0, alpha=1.0):
    vmax = vmax or max(sizes)
    rs = []
    for st, v, col in sorted(zip(sites, sizes, colors), key=lambda t: -t[1]):     # largest drawn first
        r = rmax * (np.sqrt(v / vmax) if area else v / vmax)
        x, y = centre(st)
        ax.add_patch(Circle((x, y), r, fc=col, ec=edge, lw=lw, alpha=alpha, zorder=3))
        rs.append((st, r))
    return dict(rs)


# ------------------------------------------------------------------ data
TM = _csv("talent_market_by_state").set_index("state")
R26, R24 = TM.postings_per_candidate_q2_2026, TM.postings_per_candidate_q2_2024
EDGES = [-np.inf, 0.8, 1.1, 1.4, 1.7, np.inf]
CLASS_LABELS = ["Under 0.8", "0.8–1.1", "1.1–1.4", "1.4–1.7", "1.7+"]
RAMP = [mv.SEQUENTIAL["blue"][i] for i in (0, 1, 2, 4, 5)]      # skip #009EFF: no text color reaches 4.5:1 on it
CLS26, CLS24 = classify(R26, EDGES), classify(R24, EDGES)
TIGHT = list(R26[CLS26 == 4].sort_values(ascending=False).index)
TIGHT24 = list(R24[CLS24 == 4].index)
NAMES = {"TX": "Texas", "AZ": "Arizona", "NV": "Nevada", "FL": "Florida"}
_words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}
TEXT["geo_headline"] = f"{_words[len(TIGHT)]} Sun Belt states have 1.7+ open pharmacy technician postings per candidate"
TEXT["geo_subtitle"] = "Open pharmacy technician postings per qualified candidate, by state, Q2 2026 (ratio)"
TEXT["geo_tight_n"] = str(len(TIGHT))
TEXT["geo_tight24_n"] = str(len(TIGHT24))
TEXT["geo_top"] = f"{R26[TIGHT[0]]:.2f}"

PAY = TM.tech_pay_vs_market_pct
PAY_EDGES = [-np.inf, -6, -2, 2, 6, np.inf]
PAY_LABELS = ["Under −6", "−6 to −2", "−2 to +2", "+2 to +6", "Over +6"]
PAY_RAMP = [mv.DIVERGING[i] for i in (1, 2, 3, 4, 5)]          # orange (worse) -> sand (neutral) -> blue
PAY_CLS = classify(PAY, PAY_EDGES)
PAY_LOW = list(PAY[PAY_CLS == 0].index)
TEXT["geo_pay_low_n"] = _words[len(PAY_LOW)].lower()
TEXT["geo_pay_low_all_tight"] = "all of them" if set(PAY_LOW) <= set(TIGHT) else "most of them"

DC = _csv("dc_network")
DC_SMALL = DC[DC.associates < 10]
DCS = DC[DC.associates >= 10].copy()
DC_FOCUS = set(DCS.state[DCS.vacancy_pct >= 12])
_dc_share = DCS.associates[DCS.state.isin(DC_FOCUS)].sum() / DC.associates.sum() * 100
TEXT["dc_headline"] = (f"Vacancy tops 12% at {_words[len(DC_FOCUS)].lower()} southern distribution centers that employ "
                       f"{_dc_share:.0f}% of our DC associates")
TEXT["dc_subtitle"] = "Distribution center associates by site (bubble area) and vacancy rate, Mar 2026"
TEXT["dc_small_n"] = _words[len(DC_SMALL)].lower()
TEXT["dc_sites"] = str(len(DCS))

RC = _csv("remote_care_agents").set_index("state")
_hubs = list(RC.index[RC.hub_state])
TEXT["rc_outside"] = f"{RC.agents[~RC.hub_state].sum() / RC.agents.sum() * 100:.0f}%"
TEXT["rc_small_n"] = str(int((RC.agents < 10).sum()))


# ================================================================== CHOROPLETH
@exhibit
def geo_anatomy():
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    fills = {st: RAMP[CLS26[st]] for st in GRID}
    text = {st: f"{st}\n{R26[st]:.2f}" for st in TIGHT}
    tiles(ax, fills, text=text, size=TICK - 2.5, bold=set(TIGHT), xmax=15.6, ymin=-7.25)
    legend_stack(ax, 12.0, 0.45, "Postings per candidate", CLASS_LABELS, RAMP, size=TICK - 1)
    tx, ty = centre(TIGHT[0])
    ax.add_patch(Circle((tx, ty), 0.68, fc="none", ec=C.annotation, lw=1.2, zorder=4))
    ax.plot([tx + 0.68, 4.25], [ty, ty], color=C.annotation, lw=0.8, zorder=4)
    ax.text(4.32, ty + 0.2, f"Tightest: {NAMES.get(TIGHT[0], TIGHT[0])}", fontsize=ANNOT, color=C.annotation,
            fontweight=700, va="center")
    ax.text(4.32, ty - 0.22, f"{R26[TIGHT[0]]:.2f} per candidate", fontsize=ANNOT - 0.5, color=C.text, va="center")
    marker(ax, (2.5, -0.6), 3)
    marker(ax, (12.0, 0.75), 4, offset=(-16, 0))
    marker(ax, (0.5, -4.5), 5)
    marker(ax, (tx - 0.68, ty), 6, offset=(-14, 0))
    marker(ax, (9.5, -5.5), 7)
    return fig, (TEXT["geo_headline"] + ": " + ", ".join(f"{NAMES.get(s, s)} {R26[s]:.2f}" for s in TIGHT) + ".")


# ================================================================== BUBBLE MAP
@exhibit
def dc_anatomy():
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    tiles(ax, size=MINI - 2.5, xmax=15.6, ymin=-7.25, hide=set(DCS.state) | {"NC", "SC"})
    cols = [C.focus if s in DC_FOCUS else C.context for s in DCS.state]
    rs = bubbles(ax, DCS.state, DCS.associates, cols, rmax=0.74)
    pos = {"TN": (1, 0), "TX": (1, 0), "AZ": (-1, 0)}       # label side per focus site: right, left or above
    for _, s in DCS[DCS.state.isin(DC_FOCUS)].iterrows():
        x, y = centre(s.state)
        dx, dy = pos.get(s.state, (1, 0))
        r = rs[s.state]
        if dy:
            ax.text(x, y + r + 0.08, f"{s.site} ", ha="center", va="bottom", fontsize=LABEL - 1, color=C.headline,
                    zorder=5)
            ax.text(x, y + r + 0.52, f"{s.vacancy_pct:.1f}%", ha="center", va="bottom", fontsize=LABEL - 1,
                    color=C.headline, fontweight=700, zorder=5)
        else:
            ha = "left" if dx > 0 else "right"
            ax.text(x + dx * (r + 0.1), y + 0.2, f"{s.vacancy_pct:.1f}%", ha=ha, va="center", fontsize=LABEL - 1,
                    color=C.headline, fontweight=700, zorder=5)
            ax.text(x + dx * (r + 0.1), y - 0.22, s.site, ha=ha, va="center", fontsize=LABEL - 1, color=C.headline,
                    zorder=5)
    # size key: area, top-right
    ax.text(12.0, 0.45, "DC associates", fontsize=TICK - 1, color=C.text, fontweight=600, va="bottom")
    vmax = DCS.associates.max()
    for i, v in enumerate((1500, 500)):
        r = 0.74 * np.sqrt(v / vmax)
        ax.add_patch(Circle((12.75, -0.85 - i * 1.25), r, fc="none", ec=C.text_muted, lw=0.8))
        ax.text(13.75, -0.85 - i * 1.25, f"{v:,}", fontsize=TICK - 1.5, color=C.text_muted, va="center")
    ax.add_patch(Circle((12.25, -3.55), 0.17, fc=C.focus, ec="none"))
    ax.text(12.6, -3.55, "Vacancy 12%+", fontsize=TICK - 1.5, color=C.text, va="center")
    ax.add_patch(Circle((12.25, -4.1), 0.17, fc=C.context, ec="none"))
    ax.text(12.6, -4.1, "Under 12%", fontsize=TICK - 1.5, color=C.text, va="center")
    tn = centre("TN")
    marker(ax, (tn[0] - rs["TN"], tn[1]), 3, offset=(-12, 0))
    az = centre("AZ")
    marker(ax, (az[0], az[1] - rs["AZ"]), 4, offset=(0, -12))
    tx = centre("TX")
    marker(ax, (tx[0] + rs["TX"] + 2.3, tx[1]), 5)
    oh = centre("OH")
    marker(ax, (oh[0], oh[1] + rs["OH"]), 6, offset=(0, 10))
    marker(ax, (12.0, 0.75), 7, offset=(-16, 0))
    marker(ax, (2.5, -0.6), 8)
    return fig, (TEXT["dc_headline"] + ": " + ", ".join(f"{s.site} {s.vacancy_pct:.1f}%" for _, s in
                                                       DCS[DCS.state.isin(DC_FOCUS)].iterrows()) + ".")


# ================================================================== VARIANTS
@exhibit
def geo_var_diverging():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0, 1, 1])
    fills = {st: PAY_RAMP[PAY_CLS[st]] for st in GRID}
    tiles(ax, fills, size=MINI - 3, bold=set(PAY_LOW), only=set(PAY_LOW), xmax=11.05, ymin=-8.3)
    legend_row(ax, 0.6, -7.75, PAY_LABELS, PAY_RAMP, w=1.95, size=MINI - 3.5)
    return fig, (f"Tile map of technician pay vs. local market: {len(PAY_LOW)} states more than 6% below market in "
                 "orange, above market in blue.")


@exhibit
def geo_var_dots():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0.13, 1, 0.87])
    tiles(ax, abbr=False)
    rng = np.random.default_rng(11)                            # dots placed at random inside each state's tile
    for st, n in RC.agents.items():
        if n < 10:
            continue
        k = int(round(n / 10))
        r, c = GRID[st]
        xs = c + 0.14 + rng.random(k) * 0.72
        ys = -r + 0.14 + rng.random(k) * 0.72
        ax.scatter(xs, ys, s=6, color=C.context if st in _hubs else C.focus, lw=0, zorder=3)
    fig.text(0.0, 0.02, f"1 dot = 10 agents. Grey: the three hub states ({', '.join(sorted(_hubs))}).",
             fontsize=MINI - 2.5, color=C.text_muted, va="bottom")
    return fig, f"Dot density tile map of remote Customer Care agents: {TEXT['rc_outside']} live outside the three grey hub states."


@exhibit
def geo_var_multiples():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    for i, (cls, vals, yr, tight) in enumerate(((CLS24, R24, "Q2 2024", TIGHT24), (CLS26, R26, "Q2 2026", TIGHT))):
        ax = fig.add_axes([0.005 + i * 0.505, 0.2, 0.49, 0.64])
        tiles(ax, {st: RAMP[cls[st]] for st in GRID}, abbr=False, gap=0.1)
        ax.text(0, 2.45, yr, fontsize=MINI - 1, color=C.headline, fontweight=600, va="bottom")
        ax.text(0, 1.3, f"{len(tight)} state{'s' if len(tight) != 1 else ''} at 1.7+", fontsize=MINI - 2.5,
                color=C.text, va="bottom")
    lax = fig.add_axes([0, 0, 1, 0.16])
    lax.set_xlim(0, 10)
    lax.set_ylim(-1, 0.6)
    lax.axis("off")
    legend_row(lax, 0.35, 0.05, CLASS_LABELS, RAMP, w=1.85, h=0.42, size=MINI - 3.5)
    return fig, (f"Two tile maps on the same classes: {len(TIGHT24)} state at 1.7+ postings per candidate in Q2 2024, "
                 f"{len(TIGHT)} in Q2 2026.")


@exhibit
def geo_var_bar():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = fig.add_axes([0, 0.06, 0.5, 0.88])
    fills = {st: RAMP[CLS26[st]] for st in GRID}
    tiles(ax, fills, abbr=False, gap=0.1)
    bx = fig.add_axes([0.66, 0.08, 0.32, 0.84])
    d = R26.sort_values().tail(7)
    cols = [C.focus if s in TIGHT else C.context for s in d.index]
    y = np.arange(len(d))
    bx.barh(y, d.values, color=cols, height=BAND)
    for yy, v in zip(y, d.values):
        bx.text(v + 0.05, yy, f"{v:.2f}", va="center", fontsize=MINI - 2.5, color=C.text)
    bx.set_yticks(y, d.index)
    for t in bx.get_yticklabels():
        t.set_fontsize(MINI - 2.5)
        if t.get_text() in TIGHT:
            t.set_fontweight(700)
            t.set_color(C.headline)
    bx.set_xticks([])
    bx.set_xlim(0, 2.6)
    _plain(bx, left=True)
    return fig, "A tile map paired with a sorted bar of the seven tightest states; the four at 1.7+ in blue."


# ================================================================== BEST PRACTICE (minis 200 x 140)
def _mini_map(fig, rect=(0.0, 0.17, 1.0, 0.83)):
    fig.set_layout_engine("none")
    return fig.add_axes(list(rect))


def _geo_bp(kind):
    fig = fig_px(200, 140)
    lab = MINI - 4
    if kind in ("rates_avoid", "rates_fix", "classes_avoid", "classes_fix", "hue_avoid", "hue_fix", "label_avoid",
                "label_fix"):
        ax = _mini_map(fig)
        if kind == "rates_avoid":                                   # raw counts: the population map again
            cnt = TM.open_postings_q2_2026
            cls = classify(cnt, [-np.inf, 150, 300, 600, 1200, np.inf])
            tiles(ax, {s: RAMP[cls[s]] for s in GRID}, abbr=False)
            labels = ["<150", "150", "300", "600", "1,200+"]
            colors = RAMP
        elif kind == "classes_avoid":                               # uneven, gappy, overlapping breaks
            edges = [-np.inf, 0.75, 0.95, 1.05, 1.9, np.inf]
            cls = classify(R26, edges)
            tiles(ax, {s: RAMP[cls[s]] for s in GRID}, abbr=False)
            labels, colors = ["0.6–0.7", "0.7–1.0", "0.95–1.1", "1.2–1.9", "1.9+"], RAMP
        elif kind == "hue_avoid":                                   # continuous rainbow, off palette
            v = (R26 - R26.min()) / (R26.max() - R26.min())
            pal = ANTI["rainbow"][:6]
            tiles(ax, {s: pal[min(int(v[s] * 6), 5)] for s in GRID}, abbr=False)
            labels, colors = ["", "", "", "", "", ""], pal
        elif kind == "label_avoid":
            tiles(ax, {s: RAMP[CLS26[s]] for s in GRID}, text={s: f"{R26[s]:.1f}" for s in GRID}, size=MINI - 5.5,
                  gap=0.05)
            labels, colors = None, None
        elif kind == "label_fix":
            tiles(ax, {s: RAMP[CLS26[s]] for s in GRID}, text={s: f"{R26[s]:.1f}" for s in TIGHT}, only=set(TIGHT),
                  size=MINI - 5, bold=set(TIGHT))
            labels, colors = None, None
        else:                                                       # rates_fix / classes_fix / hue_fix
            tiles(ax, {s: RAMP[CLS26[s]] for s in GRID}, abbr=False)
            labels, colors = ["<0.8", "0.8", "1.1", "1.4", "1.7+"], RAMP
            if kind == "classes_fix":
                labels = CLASS_LABELS
        if labels is not None:
            lax = fig.add_axes([0, 0, 1, 0.17])
            lax.set_xlim(0, 10)
            lax.set_ylim(-1, 0.6)
            lax.axis("off")
            w = 10 / len(colors) * 0.9
            legend_row(lax, 0.45, 0.08, labels, colors, w=w, h=0.42, size=lab)
        return fig
    ax = _mini_map(fig, (0.03, 0.02, 0.94, 0.96))
    sites, sizes = list(DCS.state), list(DCS.associates)
    cols = [C.focus if s in DC_FOCUS else C.context for s in sites]
    if kind == "base_avoid":
        tiles(ax, {s: C.surface_dark for s in GRID}, abbr=False, edge="white", lw=1.6, gap=0.0)
        bubbles(ax, sites, sizes, [C.focus_light if s in DC_FOCUS else C.context for s in sites], rmax=0.85, lw=0)
    elif kind == "base_fix":
        tiles(ax, abbr=False)
        bubbles(ax, sites, sizes, cols, rmax=0.85)
    elif kind == "area_avoid":
        tiles(ax, abbr=False)
        bubbles(ax, sites, sizes, cols, rmax=0.95, area=False)
    elif kind == "area_fix":
        tiles(ax, abbr=False)
        bubbles(ax, sites, sizes, cols, rmax=0.95)
    elif kind == "few_avoid":
        tiles(ax, abbr=False)
        hubs = RC[RC.hub_state].agents
        bubbles(ax, hubs.index, hubs.values, [C.focus] * len(hubs), rmax=0.9)
    elif kind == "few_fix":
        fig.clf()
        bx = fig.add_axes([0.28, 0.2, 0.62, 0.6])
        hubs = RC[RC.hub_state].agents.sort_values()
        names = {"TX": "Texas", "OH": "Ohio", "GA": "Georgia"}
        y = np.arange(len(hubs))
        bx.barh(y, hubs.values, color=[C.focus if i == len(hubs) - 1 else C.context for i in y], height=BAND)
        for yy, v in zip(y, hubs.values):
            bx.text(v + 6, yy, f"{v}", va="center", fontsize=MINI - 2, color=C.text)
        bx.set_yticks(y, [names[s] for s in hubs.index], fontsize=MINI - 2)
        bx.set_xticks([])
        bx.set_xlim(0, hubs.max() * 1.25)
        _plain(bx, left=True)
    elif kind == "privacy_avoid":
        tiles(ax, abbr=False)
        rng = np.random.default_rng(4)                              # schematic: one dot per person, exact spots
        for st, n in RC.agents.items():
            k = max(1, int(n / 6))
            r, c = GRID[st]
            px, py = c + 0.2 + rng.random() * 0.6, -r + 0.2 + rng.random() * 0.6
            ax.scatter(px + rng.normal(0, 0.05, k), py + rng.normal(0, 0.05, k), s=0.8, color=C.headline, lw=0)
        bx, by = centre("ID")
        ax.add_patch(Circle((bx, by), 0.2, fc=C.focus, ec="white", lw=0.6, zorder=4))
        ax.text(bx + 0.3, by + 0.55, "Boise: 7", fontsize=MINI - 3.5, color=C.headline, fontweight=700, zorder=5)
    elif kind == "privacy_fix":
        tiles(ax, abbr=False)
        bubbles(ax, sites, sizes, cols, rmax=0.85)
        ax.text(1.25, 0.5, f"{len(DC_SMALL)} site under 10 people\nnot shown", fontsize=MINI - 3.5,
                color=C.text_muted, va="center")
    if kind != "few_fix":
        ax.set_ylim(-7.75, 1.05)
    return fig


for _k, _alt in {"rates_avoid": "Tile map shaded by raw counts of postings: the big-population states are darkest.",
                 "rates_fix": "Tile map shaded by postings per candidate, a rate.",
                 "classes_avoid": "A key with uneven, gappy and overlapping class breaks.",
                 "classes_fix": "Five even classes with round breaks, open-ended at both ends.",
                 "hue_avoid": "A rainbow color scale where some hues pop for no reason.",
                 "hue_fix": "One sequential blue ramp, light to dark.",
                 "base_avoid": "Bubbles on a dark navy base map with heavy white borders.",
                 "base_fix": "Bubbles on a light sand base map with thin white gutters.",
                 "area_avoid": "Bubbles scaled by radius: the largest site looks far bigger than it is.",
                 "area_fix": "Bubbles scaled by area.",
                 "label_avoid": "A value printed in every state.",
                 "label_fix": "Values only on the four states the headline names.",
                 "few_avoid": "A whole US map for three contact-center hubs.",
                 "few_fix": "The three hubs as a sorted bar chart.",
                 "privacy_avoid": "Dots at individual locations and a labelled site of seven people.",
                 "privacy_fix": "Sites aggregated; the site under 10 people dropped and footnoted."}.items():
    EXHIBITS[f"geo_bp_{_k}"] = (lambda k=_k, a=_alt: (_geo_bp(k), a))
