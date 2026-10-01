"""Geo-spatial exhibits: US choropleth and bubble map, world map, county zoom-in, map variants, map best practice.
Registered on import.

Real geography from mckviz.geo (us-atlas and world-atlas TopoJSON in python/mckviz/geodata/, README there), decoded and drawn by
guide/geo_shapes.py with matplotlib only. US maps use the files' Albers USA layout (Alaska and Hawaii inset); the
world map is Equal Earth. Every map is drawn in figure px on an invisible canvas axes, so coordinates stay short.
The equal-area tile grid survives as one variant, for when small states matter as much as big ones.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, to_hex
from matplotlib.patches import Circle, Rectangle

import geo_shapes as gs
import mckviz as mv
from exhibits import ANTI, BAND, DATA, LABEL, MINI, TICK, C, EXHIBITS, TEXT, _csv, _plain, exhibit, fig_px, marker

US, WORLD, COUNTIES = "states-albers-10m.json", "countries-110m.json", "counties-north-texas.json"
BASE = C.surface_subtle                                    # quiet base map: light sand, white borders
NODATA = C.context_light                                   # suppressed or not shown: a darker sand, keyed
_words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}


# ------------------------------------------------------------------ map layers
def us_map(box, *, tol=0.45, min_area=0.0, **kw):
    """The 50 states and DC, keyed by postal code, in Albers USA with Alaska and Hawaii inset."""
    return gs.Map(US, "states", box, key=gs.FIPS.get, tol=tol, min_area=min_area, **kw)


_EE = gs.equal_earth(np.array([[180.0, 0], [0, -56.0], [0, 84.0]]))
EE_BOUNDS = (-_EE[0, 0], _EE[1, 1], _EE[0, 0], _EE[2, 1])          # Antarctica left out
_ME = gs.mercator(np.array([[180.0, -56.0], [0, 82.0]]))
MERC_BOUNDS = (-_ME[0, 0], _ME[0, 1], _ME[0, 0], _ME[1, 1])
WORLD_IDS = {k for k in gs.topo(WORLD).shapes("countries") if k != "010"}


def world_map(box, *, proj=gs.equal_earth, bounds=EE_BOUNDS, tol=0.4, min_area=0.0):
    return gs.Map(WORLD, "countries", box, project=proj, ids=WORLD_IDS, bounds=bounds, tol=tol, min_area=min_area)


# ------------------------------------------------------------------ keys (all positions in px)
def key_stack(ax, x, y, title, labels, colors, *, size=TICK - 1, sq=11, step=16, extra=()):
    """Class key stacked high -> low (pass labels low -> high); title's top-left at (x, y). extra: (label, color)."""
    ax.text(x, y, title, fontsize=size, color=C.text, va="top", fontweight=600, linespacing=1.15)
    yy = y - (title.count("\n") + 1) * size * 1.2 - 5
    items = list(zip(labels[::-1], colors[::-1]))
    for i, (lab, col) in enumerate(items + list(extra)):
        top = yy - i * step - (5 if i >= len(items) else 0)
        ax.add_patch(Rectangle((x, top - sq), sq, sq, fc=col, ec=C.grid, lw=0.6))
        ax.text(x + sq + 6, top - sq / 2, lab, fontsize=size, color=C.text, va="center")
    return yy - len(items + list(extra)) * step


def key_row(ax, x, y, labels, colors, *, w=36, h=8, size=MINI - 4, first=None):
    """Compact class key in one row: adjoining swatches (top at y) with labels beneath."""
    for i, (lab, col) in enumerate(zip(labels, colors)):
        ax.add_patch(Rectangle((x + i * w, y - h), w, h, fc=col, ec="white", lw=0.6))
        ax.text(x + i * w + w / 2, y - h - 2, lab, fontsize=size, color=C.text, ha="center", va="top")


def bubble(ax, xy, r, fc, *, ec="white", lw=1.0, z=3, alpha=1.0):
    ax.add_patch(Circle(xy, r, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha))


def classify(values: pd.Series, edges):
    return pd.Series(pd.cut(values, edges, labels=False, right=False), index=values.index).astype(int)


# ------------------------------------------------------------------ data: states
TM = _csv("talent_market_by_state").set_index("state")
R26, R24 = TM.postings_per_candidate_q2_2026, TM.postings_per_candidate_q2_2024
EDGES = [-np.inf, 0.8, 1.1, 1.4, 1.7, np.inf]
CLASS_LABELS = ["Under 0.8", "0.8–1.1", "1.1–1.4", "1.4–1.7", "1.7+"]
SHORT_LABELS = ["<0.8", "0.8", "1.1", "1.4", "1.7+"]
RAMP = [mv.SEQUENTIAL["blue"][i] for i in (0, 1, 2, 4, 5)]      # skip #009EFF: no text color reaches 4.5:1 on it
CLS26, CLS24 = classify(R26, EDGES), classify(R24, EDGES)
TIGHT = list(R26[CLS26 == 4].sort_values(ascending=False).index)
TIGHT24 = list(R24[CLS24 == 4].index)
NAMES = {"TX": "Texas", "AZ": "Arizona", "NV": "Nevada", "FL": "Florida", "OH": "Ohio", "GA": "Georgia"}
FILL26 = {s: RAMP[CLS26[s]] for s in R26.index}
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

# Census divisions: when data exists only by region, dissolve the states.
DIVISIONS = {"New England": "CT ME MA NH RI VT", "Mid-Atlantic": "NJ NY PA", "East North Central": "IL IN MI OH WI",
             "West North Central": "IA KS MN MO NE ND SD", "South Atlantic": "DE DC FL GA MD NC SC VA WV",
             "East South Central": "AL KY MS TN", "West South Central": "AR LA OK TX",
             "Mountain": "AZ CO ID MT NV NM UT WY", "Pacific": "AK CA HI OR WA"}
DIV_OF = {s: d for d, sts in DIVISIONS.items() for s in sts.split()}
_cand = TM.open_postings_q2_2026 / R26                          # candidates implied by postings and the rate
DIV_RATE = (TM.open_postings_q2_2026.groupby(DIV_OF).sum() / _cand.groupby(DIV_OF).sum()).round(2)
DIV_CLS = classify(DIV_RATE, EDGES)
TEXT["geo_div_top"] = DIV_RATE.idxmax()
TEXT["geo_div_top_rate"] = f"{DIV_RATE.max():.2f}"

# ------------------------------------------------------------------ data: sites and agents
DC = _csv("dc_network")
DC_SMALL = DC[DC.associates < 10]
DCS = DC[DC.associates >= 10].copy()
DC_FOCUS = set(DCS.site[DCS.vacancy_pct >= 12])
_dc_share = DCS.associates[DCS.site.isin(DC_FOCUS)].sum() / DC.associates.sum() * 100
TEXT["dc_headline"] = (f"Vacancy tops 12% at {_words[len(DC_FOCUS)].lower()} southern distribution centers that employ "
                       f"{_dc_share:.0f}% of our DC associates")
TEXT["dc_subtitle"] = "Distribution center associates by site (bubble area) and vacancy rate, Mar 2026"
TEXT["dc_small_n"] = _words[len(DC_SMALL)].lower()
TEXT["dc_sites"] = str(len(DCS))

RC = _csv("remote_care_agents").set_index("state")
_hubs = list(RC.index[RC.hub_state])
TEXT["rc_outside"] = f"{RC.agents[~RC.hub_state].sum() / RC.agents.sum() * 100:.0f}%"
TEXT["rc_small_n"] = str(int((RC.agents < 10).sum()))

# ------------------------------------------------------------------ data: world
WD = pd.read_csv(DATA / "data_ai_talent_by_country.csv", dtype={"iso_n3": str}).set_index("iso_n3")
W_RATE = WD.candidates_per_role_2026
W_EDGES = [-np.inf, 3, 5, 7, np.inf]
W_LABELS = ["Under 3", "3–5", "5–7", "7+"]
W_RAMP = [mv.SEQUENTIAL["blue"][i] for i in (1, 2, 4, 5)]       # no palest class: it would read as "not assessed"
W_CLS = classify(W_RATE, W_EDGES)
W_FILL = {k: W_RAMP[c] for k, c in W_CLS.items()}
W_TOP = W_RATE.idxmax()
W_US = W_RATE["840"]
TEXT["world_headline"] = (f"{WD.country[W_TOP]} offers {W_RATE[W_TOP]:.1f} qualified Data & AI candidates per open "
                          f"role, more than {_words[int(W_RATE[W_TOP] // W_US)].lower()} times the U.S. rate")
TEXT["world_subtitle"] = "Qualified Data & AI candidates per open role, countries assessed for a capability center, Q2 2026 (ratio)"
TEXT["world_n"] = str(len(WD))
TEXT["world_top_n"] = _words[int((W_CLS == 3).sum())].lower()
PEOPLE = WD.our_data_ai_people
PEOPLE_SHOWN = PEOPLE[PEOPLE >= 10]
PEOPLE_SMALL = PEOPLE[(PEOPLE > 0) & (PEOPLE < 10)]
TEXT["world_people_top"] = WD.country[PEOPLE.drop("840").idxmax()]
TEXT["world_people_top_share"] = f"{PEOPLE.drop('840').max() / PEOPLE.sum() * 100:.0f}%"
TEXT["world_people_small"] = " and ".join(WD.country[PEOPLE_SMALL.index])

# ------------------------------------------------------------------ data: North Texas counties (the zoom-in)
STUDY_MILES = 70                                           # study-area radius in make_data.pharm_tech_north_texas
CT = _csv("pharm_tech_north_texas").astype({"fips": str}).set_index("fips")
CT_SHOWN = CT[CT.qualified_candidates >= 10]
CT_SMALL = CT[CT.qualified_candidates < 10]
Z_RATE = CT_SHOWN.postings_per_candidate
Z_CLS = classify(Z_RATE, EDGES)                             # the state map's classes, unchanged
Z_FILL = {k: RAMP[c] for k, c in Z_CLS.items()} | {k: NODATA for k in CT_SMALL.index}
Z_CORE = list(Z_RATE[Z_CLS == 4].sort_values(ascending=False).index)
Z_LOW = Z_RATE[Z_RATE < 1.1]
assert CLS26["TX"] == 4, "the zoom headline compares the core counties with Texas's class"
TEXT["zoom_headline"] = (f"Around Irving, {_words[len(Z_CORE)].lower()} core counties have 1.7+ postings per "
                         f"candidate, while {_words[len(Z_LOW)].lower()} outer counties are under 1.1")
TEXT["zoom_subtitle"] = "Open pharmacy technician postings per qualified candidate, by county, North Texas, Q2 2026 (ratio)"
TEXT["zoom_n"] = str(len(CT))
TEXT["zoom_small_n"] = _words[len(CT_SMALL)].lower()
TEXT["zoom_miles"] = str(STUDY_MILES)
TEXT["zoom_core"] = ", ".join(CT.county[k] for k in Z_CORE)
TEXT["tx_rate"] = f"{R26['TX']:.2f}"
# the zoom frame, in the us-atlas Albers units (y down), around our Irving campus
_IX, _IY = gs.albers_usa(*gs.CITY["Irving"])
Z_BOUNDS = (_IX - 24, _IY - 30, _IX + 31, _IY + 20)
ZB_MINI = (_IX - 22, _IY - 25, _IX + 29, _IY + 18)                  # a little tighter for the 200 px minis
CMAP = LinearSegmentedColormap.from_list("blue", mv.SEQUENTIAL["blue"])   # only for the auto-range anti-example


def zoom_map(box, *, tol=0.3, bounds=Z_BOUNDS):
    return gs.Map(COUNTIES, "counties", box, bounds=bounds, tol=tol)


def draw_zoom(ax, z, *, lw=0.7, state_lw=1.0, study=True):
    """Counties: study area by class, small counties keyed grey, the rest base sand; state line; study outline."""
    z.draw(ax, Z_FILL, default=BASE, ec="white", lw=lw)
    z.borders(ax, {k: k[:2] for k in z.rings}, color=C.text_muted, lw=state_lw * 0.8, z=3, ls=(0, (3, 2)))
    if study:
        z.borders(ax, {k: k in CT.index for k in z.rings}, color=C.text_muted, lw=state_lw * 1.2, z=2)


def locator(ax, box, bounds=Z_BOUNDS, *, lw=1.1):
    """A small US map with the zoom frame outlined in navy."""
    m = us_map(box, tol=0.9, min_area=4)
    m.draw(ax, {"TX": C.context_light}, default=BASE, ec="white", lw=0.3)
    (x0, y0), (x1, y1) = m.to_px(np.array([[bounds[0], bounds[1]], [bounds[2], bounds[3]]]))
    pad = 1.5
    ax.add_patch(Rectangle((min(x0, x1) - pad, min(y0, y1) - pad), abs(x1 - x0) + 2 * pad, abs(y1 - y0) + 2 * pad,
                           fc="none", ec=C.accent, lw=lw, zorder=4))
    return m, (min(x0, x1) - pad, max(y0, y1) + pad)


def state_labels(ax, m, states, text, *, size, bold=True, nudge=None):
    nudge = nudge or {}
    for s in states:
        if s in LABEL_OUT:                                  # too thin to hold its label: set it beside, in navy
            x, y = m.point(*LABEL_OUT[s])
            ax.text(x, y, text(s), ha="right", va="center", fontsize=size, linespacing=1.05, zorder=5,
                    color=C.headline, fontweight=700 if bold else 400)
            continue
        x, y = m.centre(s)
        dx, dy = nudge.get(s, (0, 0))
        ax.text(x + dx, y + dy, text(s), ha="center", va="center", fontsize=size, linespacing=1.05, zorder=5,
                color=mv.text_on(FILL26.get(s, BASE)), fontweight=700 if bold else 400)


LABEL_OUT = {"FL": (-82.9, 26.6)}                                          # lon/lat: label in the Gulf, right-aligned
NUDGE = {"NV": (-2, 6), "TX": (4, -6)}                                     # px at anatomy scale (s ~ 0.48)


# ================================================================== CHOROPLETH
@exhibit
def geo_anatomy():
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 8, 478, 306))
    m.draw(ax, FILL26, ec="white", lw=0.6)
    state_labels(ax, m, TIGHT, lambda s: f"{s}\n{R26[s]:.2f}", size=TICK - 2, nudge=NUDGE)
    key_stack(ax, 494, 300, "Postings per\ncandidate", CLASS_LABELS, RAMP, size=TICK - 1)
    marker(ax, m.centre("MT"), 3)
    ak = m.centre("AK")
    marker(ax, (ak[0] + 30, ak[1] + 22), 4)
    marker(ax, (494, 300), 5, offset=(-14, -8))
    nv = m.centre("NV")
    marker(ax, (nv[0] - 30, nv[1] + 10), 6)
    marker(ax, m.centre("IA"), 7)
    return fig, (TEXT["geo_headline"] + ": " + ", ".join(f"{NAMES.get(s, s)} {R26[s]:.2f}" for s in TIGHT) + ".")


# ================================================================== BUBBLE MAP
DC_R = 24                                                   # px radius of the largest site (48 px across)


def dc_bubbles(ax, m, *, rmax=DC_R, area=True, cols=None, lw=1.0):
    vmax = DCS.associates.max()
    out = {}
    for _, s in DCS.sort_values("associates", ascending=False).iterrows():      # largest drawn first
        r = rmax * (np.sqrt(s.associates / vmax) if area else s.associates / vmax)
        xy = m.point(*gs.CITY[s.site])
        col = (cols or {}).get(s.site, C.focus if s.site in DC_FOCUS else C.context)
        bubble(ax, xy, r, col, lw=lw)
        out[s.site] = (xy, r)
    return out


@exhibit
def dc_anatomy():
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 8, 478, 306))
    m.draw(ax, default=BASE, ec="white", lw=0.8)
    pos = dc_bubbles(ax, m)
    side = {"Memphis": 0, "Dallas": -1, "Phoenix": -1}
    for site in sorted(DC_FOCUS):
        (x, y), r = pos[site]
        d = side.get(site, 1)
        v = DCS.set_index("site").vacancy_pct[site]
        if d == 0:                                          # above the bubble
            ax.text(x, y + r + 17, f"{v:.1f}%", ha="center", va="center", fontsize=LABEL - 1, color=C.headline,
                    fontweight=700, zorder=6)
            ax.text(x, y + r + 5, site, ha="center", va="center", fontsize=LABEL - 1, color=C.headline, zorder=6)
            continue
        ha = "left" if d > 0 else "right"
        ax.text(x + d * (r + 4), y + 6, f"{v:.1f}%", ha=ha, va="center", fontsize=LABEL - 1, color=C.headline,
                fontweight=700, zorder=6)
        ax.text(x + d * (r + 4), y - 7, site, ha=ha, va="center", fontsize=LABEL - 1, color=C.headline, zorder=6)
    kx = 494
    ax.text(kx, 300, "DC associates", fontsize=TICK - 1, color=C.text, fontweight=600, va="top")
    vmax = DCS.associates.max()
    for i, v in enumerate((1500, 500)):
        r = DC_R * np.sqrt(v / vmax)
        cy = 258 - i * 44
        ax.add_patch(Circle((kx + 23, cy), r, fc="none", ec=C.text_muted, lw=0.8))
        ax.text(kx + 52, cy, f"{v:,}", fontsize=TICK - 1.5, color=C.text_muted, va="center")
    for i, (lab, col) in enumerate((("Vacancy 12%+", C.focus), ("Under 12%", C.context))):
        ax.add_patch(Circle((kx + 6, 176 - i * 17), 5.5, fc=col, ec="none"))
        ax.text(kx + 17, 176 - i * 17, lab, fontsize=TICK - 1.5, color=C.text, va="center")
    (mx, my), mr = pos["Memphis"]
    marker(ax, (mx + mr, my - mr), 3, offset=(4, -2))
    (px, py), pr = pos["Phoenix"]
    marker(ax, (px, py - pr), 4, offset=(0, -10))
    (dx, dy), dr = pos["Dallas"]
    marker(ax, (dx - dr - 52, dy), 5, offset=(-12, 0))
    (cx, cy), cr = pos["Columbus"]
    marker(ax, (cx, cy + cr), 6, offset=(0, 9))
    marker(ax, (kx, 300), 7, offset=(-14, -8))
    marker(ax, m.centre("MT"), 8)
    return fig, (TEXT["dc_headline"] + ": " + ", ".join(f"{s.site} {s.vacancy_pct:.1f}%" for _, s in
                                                       DCS[DCS.site.isin(DC_FOCUS)].iterrows()) + ".")


# ================================================================== WORLD
@exhibit
def geo_world_anatomy():
    fig = fig_px(620, 300)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    w = world_map((0, 6, 620, 290))
    w.draw(ax, W_FILL, default=BASE, ec="white", lw=0.45)
    for k, lab in ((W_TOP, f"{WD.country[W_TOP]}\n{W_RATE[W_TOP]:.1f}"), ("840", f"U.S.\n{W_US:.1f}")):
        x, y = w.centre(k)
        if k == "840":
            x, y = x + 6, y - 6
        ax.text(x, y, lab, ha="center", va="center", fontsize=TICK - 2, fontweight=700, linespacing=1.05, zorder=5,
                color=mv.text_on(W_FILL[k]))
    key_stack(ax, 14, 118, "Candidates per role", W_LABELS, W_RAMP, size=TICK - 1.5, sq=10, step=14,
                       extra=[("Not assessed", BASE)])
    marker(ax, w.point(-170, 20, gs.equal_earth), 3)
    marker(ax, w.centre("156"), 4)
    marker(ax, (14, 118), 5, offset=(116, -6))
    ix, iy = w.centre(W_TOP)
    marker(ax, (ix + 26, iy - 16), 6)
    ux, uy = w.centre("840")
    marker(ax, (ux - 34, uy - 4), 7)
    return fig, (TEXT["world_headline"] + ". " + ", ".join(f"{WD.country[k]} {v:.1f}" for k, v in
                                                          W_RATE.sort_values(ascending=False).head(4).items()) + ".")


# ================================================================== ZOOM-IN
@exhibit
def geo_zoom_anatomy():
    fig = fig_px(620, 320)
    fig.set_layout_engine("none")
    W = 372
    zax = gs.canvas(fig, (0, 0, W / 620, 1))
    z = zoom_map((0, 0, W, 320))
    draw_zoom(zax, z)
    for k in Z_CORE:
        x, y = z.centre(k)
        dx, dy = {"48113": (10, -9), "48439": (2, -8)}.get(k, (0, 0))
        zax.text(x + dx, y + dy, f"{CT.county[k]}\n{Z_RATE[k]:.2f}", ha="center", va="center", fontsize=TICK - 2,
                 fontweight=700, linespacing=1.05, color=mv.text_on(Z_FILL[k]), zorder=5)
    ix, iy = z.point(*gs.CITY["Irving"])
    zax.add_patch(Circle((ix, iy), 4.5, fc="white", ec=C.accent, lw=1.8, zorder=6))
    zax.text(ix + 6, iy + 9, "Irving", fontsize=TICK - 2, color=C.headline, fontweight=700, zorder=6,
             bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.85))
    tx, ty = z.point(-96.25, 33.86)
    zax.text(tx, ty + 7, "OKLAHOMA", fontsize=MINI - 3, color=C.text_muted, ha="left", va="bottom", zorder=5)
    zax.text(tx + 14, ty - 12, "TEXAS", fontsize=MINI - 3, color=C.text_muted, ha="left", va="top", zorder=5)
    ax = gs.canvas(fig)
    loc, (lx, ly) = locator(ax, (392, 214, 190, 102))
    ax.add_patch(Rectangle((0.6, 0.6), W - 1.2, 318.8, fc="none", ec=C.accent, lw=1.1, zorder=7))  # the frame
    key_stack(ax, 392, 196, "Postings per candidate", CLASS_LABELS, RAMP, size=TICK - 1.5, sq=10, step=14,
              extra=[("Under 10 candidates", NODATA), ("Outside study area", BASE)])
    marker(ax, (lx, ly), 3, offset=(10, 10))
    marker(ax, (392, 196), 4, offset=(-12, -6))
    marker(ax, (ix, iy), 5, offset=(0, -15))
    sx, sy = z.centre(CT_SMALL.index[0])
    marker(ax, (sx, sy), 7, offset=(-14, 0))
    marker(ax, z.centre("48121"), 6, offset=(-30, 0))
    marker(ax, z.centre("48237"), 8)
    return fig, (TEXT["zoom_headline"] + ": " + ", ".join(f"{CT.county[k]} {Z_RATE[k]:.2f}" for k in Z_CORE) + ".")


# ================================================================== VARIANTS
@exhibit
def geo_var_diverging():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 38, 300, 170), tol=0.6, min_area=2)
    m.draw(ax, {s: PAY_RAMP[PAY_CLS[s]] for s in PAY.index}, ec="white", lw=0.4)
    for s in PAY_LOW:
        x, y = m.centre(s)
        dx, dy = {"FL": (5, -4)}.get(s, (0, 0))
        ax.text(x + dx, y + dy, s, ha="center", va="center", fontsize=MINI - 3, fontweight=700, zorder=5,
                color=mv.text_on(PAY_RAMP[0]))
    key_row(ax, 4, 26, PAY_LABELS, PAY_RAMP, w=58, h=9, size=MINI - 3.5)
    return fig, (f"Map of technician pay vs. local market: {len(PAY_LOW)} states more than 6% below market in "
                 "orange, above market in blue.")


@exhibit
def geo_var_dots():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 22, 300, 186), tol=0.6, min_area=2)
    m.draw(ax, default=BASE, ec="white", lw=0.5)
    rng = np.random.default_rng(11)                           # dots placed at random inside each state, never at addresses
    for st, n in RC.agents.items():
        if n < 10 or st not in m.rings:
            continue
        k = int(round(n / 10))
        p = m.path(st)
        (x0, y0), (x1, y1) = p.vertices.min(0), p.vertices.max(0)
        pts = np.empty((0, 2))
        while len(pts) < k:
            c = np.column_stack([rng.uniform(x0, x1, 4 * k), rng.uniform(y0, y1, 4 * k)])
            pts = np.vstack([pts, c[p.contains_points(c, radius=-1.0)]])
        ax.scatter(pts[:k, 0], pts[:k, 1], s=7, color=C.context if st in _hubs else C.focus, lw=0, zorder=3)
    ax.text(2, 4, f"1 dot = 10 agents. Grey: the three hub states ({', '.join(sorted(_hubs))}).",
            fontsize=MINI - 2.5, color=C.text_muted, va="bottom")
    return fig, f"Dot density map of remote Customer Care agents: {TEXT['rc_outside']} live outside the three grey hub states."


@exhibit
def geo_var_multiples():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    for i, (cls, yr, tight) in enumerate(((CLS24, "Q2 2024", TIGHT24), (CLS26, "Q2 2026", TIGHT))):
        x0 = i * 152
        m = us_map((x0, 50, 148, 110), tol=0.7, min_area=2)
        m.draw(ax, {s: RAMP[cls[s]] for s in cls.index}, ec="white", lw=0.3)
        ax.text(x0, 176, yr, fontsize=MINI - 1, color=C.headline, fontweight=600, va="bottom")
        ax.text(x0, 162, f"{len(tight)} state{'s' if len(tight) != 1 else ''} at 1.7+", fontsize=MINI - 2.5,
                color=C.text, va="bottom")
    key_row(ax, 8, 30, CLASS_LABELS, RAMP, w=56, h=9, size=MINI - 3.5)
    return fig, (f"Two maps on the same classes: {len(TIGHT24)} state at 1.7+ postings per candidate in Q2 2024, "
                 f"{len(TIGHT)} in Q2 2026.")


@exhibit
def geo_var_bar():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 40, 176, 150), tol=0.6, min_area=2)
    m.draw(ax, FILL26, ec="white", lw=0.35)
    bx = fig.add_axes([0.70, 0.08, 0.28, 0.84])
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
    return fig, "A map paired with a sorted bar of the seven tightest states; the four at 1.7+ in blue."


# ---- tile grid (kept as the variant for when small states matter as much as big ones)
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


@exhibit
def geo_var_tiles():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    t, gap, x0, y0 = 21.5, 1.8, 32, 206                      # tile size, gutter, top-left of the grid (px)
    for st, (r, c) in GRID.items():
        f = FILL26[st]
        x, y = x0 + c * t, y0 - (r + 1) * t
        ax.add_patch(Rectangle((x + gap / 2, y + gap / 2), t - gap, t - gap, fc=f, ec="none"))
        ax.text(x + t / 2, y + t / 2, st, ha="center", va="center", fontsize=MINI - 3.5,
                color=mv.text_on(f), fontweight=700 if st in TIGHT else 400)
    key_row(ax, 4, 2 + 9 + 11, CLASS_LABELS, RAMP, w=58, h=9, size=MINI - 3.5)
    return fig, "Tile grid map: one equal square per state in roughly its place, shaded by the same five classes."


@exhibit
def geo_var_regions():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m = us_map((0, 38, 300, 170), tol=0.6, min_area=2)
    fills = {s: RAMP[DIV_CLS[DIV_OF[s]]] for s in m.rings}
    for s in m.rings:                                       # each state edged in its own color: the lines vanish
        m.draw(ax, {s: fills[s]}, ids=[s], ec=fills[s], lw=0.5)
    m.borders(ax, DIV_OF, color="white", lw=1.4)
    spots = {"Pacific": "OR", "Mountain": "UT", "West North Central": "NE", "West South Central": "TX",
             "East North Central": "IN", "East South Central": "AL", "South Atlantic": "SC", "Mid-Atlantic": "PA",
             "New England": "ME"}
    for d, st in spots.items():
        x, y = m.centre(st)
        dx, dy = {"Pacific": (-4, 0), "South Atlantic": (-6, 6), "Mid-Atlantic": (-2, 0)}.get(d, (0, 0))
        f = RAMP[DIV_CLS[d]]
        ax.text(x + dx, y + dy, f"{DIV_RATE[d]:.2f}", ha="center", va="center", fontsize=MINI - 3.5,
                color=mv.text_on(f), fontweight=700 if DIV_CLS[d] == 4 else 400, zorder=5)
    key_row(ax, 4, 26, CLASS_LABELS, RAMP, w=58, h=9, size=MINI - 3.5)
    return fig, (f"Region map: states dissolved into nine Census divisions; {DIV_RATE.idxmax()} is tightest at "
                 f"{DIV_RATE.max():.2f} postings per candidate.")


NE_SMALL = ["VT", "NH", "MA", "RI", "CT", "NJ", "DE", "MD", "DC"]
NE_RECT = (210, 18, 88, 120)                                    # inset box, px


def _inset_maps():
    m = us_map((0, 34, 216, 170), tol=0.6, min_area=2)
    x0, y0, x1, y1 = us_map((0, 0, 100, 100), tol=0, ids=NE_SMALL).bounds
    b = (x0 - 4, y0 - 4, x1 + 4, y1 + 4)
    return m, us_map(NE_RECT, tol=0.4, bounds=b), b


_m, _i, _ = _inset_maps()
TEXT["geo_inset_zoom"] = f"{_i.s / _m.s:.0f}"
TEXT["geo_inset_n"] = str(len(NE_SMALL) - 1)                    # states, not counting DC


@exhibit
def geo_var_inset():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    m, inset, b = _inset_maps()
    m.draw(ax, FILL26, ec="white", lw=0.35)
    rect = NE_RECT
    iax = gs.canvas(fig, (rect[0] / 300, rect[1] / 210, rect[2] / 300, rect[3] / 210))
    inset.draw(iax, FILL26, ec="white", lw=0.6)
    for s in NE_SMALL:
        x, y = inset.centre(s)
        dx, dy = {"MD": (-14, 6), "DC": (-12, -5), "DE": (5, -3), "NJ": (2, 0), "VT": (-1, 3),
                  "MA": (-6, -1), "RI": (4, 0)}.get(s, (0, 0))
        iax.text(x + dx, y + dy, s, ha="center", va="center", fontsize=MINI - 4, zorder=5,
                 color=mv.text_on(FILL26[s]))
    ax.add_patch(Rectangle(rect[:2], rect[2], rect[3], fc="none", ec=C.context, lw=0.8, zorder=6))
    (a0, a1), (c0, c1) = m.to_px(np.array([[b[0], b[1]], [b[2], b[3]]]))
    ax.add_patch(Rectangle((a0, c1), c0 - a0, a1 - c1, fc="none", ec=C.accent, lw=0.9, zorder=6))
    key_row(ax, 4, 26, CLASS_LABELS, RAMP, w=40, h=9, size=MINI - 4.5)
    return fig, (f"US map with the Northeast enlarged {TEXT['geo_inset_zoom']} times in an inset, so the nine small "
                 "states and DC can be read.")


BUBBLE_AT = {"840": (-98.5, 39.0), "124": (-100.0, 62.0)}               # lon/lat; country centroids drift


@exhibit
def geo_var_world():
    fig = fig_px(300, 210)
    fig.set_layout_engine("none")
    ax = gs.canvas(fig)
    w = world_map((0, 30, 300, 170), tol=0.5, min_area=3)
    w.draw(ax, default=BASE, ec="white", lw=0.3)
    vmax = PEOPLE_SHOWN.max()
    top = PEOPLE.drop("840").idxmax()
    def at(k):
        return w.point(*BUBBLE_AT[k], gs.equal_earth) if k in BUBBLE_AT else w.centre(k)
    for k, v in PEOPLE_SHOWN.sort_values(ascending=False).items():
        x, y = at(k)
        r = 20 * np.sqrt(v / vmax)
        bubble(ax, (x, y), r, C.focus if k == top else C.context, lw=0.8)
    lab = {"840": (0, -1, "center"), top: (1, 0, "left"), "124": (1, 0, "left"), "372": (-1, 0, "right"),
           "376": (1, 0, "left")}
    for k, (dx, dy, ha) in lab.items():
        x, y = at(k)
        r = 20 * np.sqrt(PEOPLE[k] / vmax)
        ax.text(x + dx * (r + 3), y + dy * (r + 2), f"{PEOPLE[k]:,}", ha=ha, va={1: "bottom", -1: "top"}.get(dy, "center"),
                fontsize=MINI - 3, fontweight=700, color=C.headline, zorder=6)
    ax.text(2, 4, f"Bubble area = people. {TEXT['world_people_small']} (under 10 each) not shown.",
            fontsize=MINI - 2.5, color=C.text_muted, va="bottom")
    return fig, (f"World bubble map of our Data & AI people by work country: {TEXT['world_people_top']} holds "
                 f"{TEXT['world_people_top_share']}, the most outside the U.S.")


# ================================================================== BEST PRACTICE (minis 200 x 140)
MINI_BOX = (0, 24, 200, 114)


def _mini():
    fig = fig_px(200, 140)
    fig.set_layout_engine("none")
    return fig, gs.canvas(fig)


def _mini_us(ax, fills=None, *, box=MINI_BOX, lw=0.3, default=BASE, ec="white", **kw):
    m = us_map(box, tol=0.75, min_area=2.5, **kw)
    m.draw(ax, fills, default=default, ec=ec, lw=lw)
    return m


def _key(ax, labels, colors):
    key_row(ax, 10, 20, labels, colors, w=180 / len(colors), h=8, size=MINI - 4)


def _geo_bp(kind):
    fig, ax = _mini()
    if kind == "rates_avoid":                                   # raw counts: the population map again
        cnt = TM.open_postings_q2_2026
        cls = classify(cnt, [-np.inf, 150, 300, 600, 1200, np.inf])
        _mini_us(ax, {s: RAMP[cls[s]] for s in cls.index})
        _key(ax, ["<150", "150", "300", "600", "1,200+"], RAMP)
    elif kind == "classes_avoid":                               # uneven, gappy, overlapping breaks
        cls = classify(R26, [-np.inf, 0.75, 0.95, 1.05, 1.9, np.inf])
        _mini_us(ax, {s: RAMP[cls[s]] for s in cls.index})
        _key(ax, ["0.6–0.7", "0.7–1.0", "0.95–1.1", "1.2–1.9", "1.9+"], RAMP)
    elif kind == "hue_avoid":                                   # continuous rainbow, off palette
        v = (R26 - R26.min()) / (R26.max() - R26.min())
        pal = ANTI["rainbow"][:6]
        _mini_us(ax, {s: pal[min(int(v[s] * 6), 5)] for s in v.index})
        _key(ax, [""] * 6, pal)
    elif kind in ("rates_fix", "hue_fix", "classes_fix"):
        _mini_us(ax, FILL26)
        _key(ax, CLASS_LABELS if kind == "classes_fix" else SHORT_LABELS, RAMP)
    elif kind == "label_avoid":
        m = _mini_us(ax, FILL26, box=(0, 4, 200, 132))
        for s in R26.index.intersection(list(m.rings)):
            x, y = m.centre(s)
            ax.text(x, y, f"{R26[s]:.1f}", ha="center", va="center", fontsize=MINI - 5.5, color=mv.text_on(FILL26[s]))
    elif kind == "label_fix":
        m = _mini_us(ax, FILL26, box=(0, 4, 200, 132))
        state_labels(ax, m, TIGHT, lambda s: f"{R26[s]:.2f}", size=MINI - 4,
                     nudge={k: (v[0] * 0.45, v[1] * 0.45) for k, v in NUDGE.items()})
    elif kind in ("base_avoid", "base_fix", "area_avoid", "area_fix", "privacy_fix"):
        box = (2, 2, 196, 112) if kind == "privacy_fix" else (2, 4, 196, 132)
        if kind == "base_avoid":
            m = _mini_us(ax, box=box, default=C.surface_dark, ec="white", lw=1.4)
            dc_bubbles(ax, m, rmax=11, cols={s: C.focus_light for s in DC_FOCUS}, lw=0)
        else:
            m = _mini_us(ax, box=box)
            dc_bubbles(ax, m, rmax=13 if kind.startswith("area") else 11, area=kind != "area_avoid", lw=0.7)
        if kind == "privacy_fix":
            ax.text(198, 139, f"{len(DC_SMALL)} site under 10 people not shown", fontsize=MINI - 3.5,
                    color=C.text_muted, va="top", ha="right")
    elif kind == "few_avoid":
        m = _mini_us(ax, box=(2, 4, 196, 132))
        hubs = RC[RC.hub_state].agents
        for s, v in hubs.items():
            bubble(ax, m.centre(s), 13 * np.sqrt(v / hubs.max()), C.focus, lw=0.7)
    elif kind == "few_fix":
        fig.clf()
        bx = fig.add_axes([0.28, 0.2, 0.62, 0.6])
        hubs = RC[RC.hub_state].agents.sort_values()
        y = np.arange(len(hubs))
        bx.barh(y, hubs.values, color=[C.focus if i == len(hubs) - 1 else C.context for i in y], height=BAND)
        for yy, v in zip(y, hubs.values):
            bx.text(v + 6, yy, f"{v}", va="center", fontsize=MINI - 2, color=C.text)
        bx.set_yticks(y, [NAMES[s] for s in hubs.index], fontsize=MINI - 2)
        bx.set_xticks([])
        bx.set_xlim(0, hubs.max() * 1.25)
        _plain(bx, left=True)
    elif kind == "privacy_avoid":
        m = _mini_us(ax, box=(2, 4, 196, 132))
        rng = np.random.default_rng(4)                              # schematic: one dot per person, exact spots
        for site in list(gs.CITY)[:13]:
            x, y = m.point(*gs.CITY[site])
            k = int(rng.integers(25, 70))
            ax.scatter(x + rng.normal(0, 3, k), y + rng.normal(0, 3, k), s=0.8, color=C.headline, lw=0)
        bx, by = m.point(*gs.CITY["Boise (satellite)"])
        bubble(ax, (bx, by), 3.5, C.focus, lw=0.6, z=4)
        ax.text(bx + 5, by + 6, "Boise: 7", fontsize=MINI - 3.5, color=C.headline, fontweight=700, zorder=5)
    elif kind == "proj_world_avoid":                            # Mercator: high latitudes inflated
        w = world_map((0, 4, 200, 132), proj=gs.mercator, bounds=MERC_BOUNDS, tol=0.6, min_area=2)
        w.draw(ax, W_FILL, default=BASE, ec="white", lw=0.25)
    elif kind == "proj_world_fix":
        w = world_map((0, 20, 200, 100), tol=0.6, min_area=2)
        w.draw(ax, W_FILL, default=BASE, ec="white", lw=0.25)
    elif kind == "proj_us_avoid":                               # plain lon/lat, Alaska where it really is
        m = us_map((2, 4, 196, 132), tol=0.75, min_area=2.5, transform=gs.us_lonlat(),
                   bounds=(-180, -72, -65, -18))
        m.draw(ax, FILL26, default=BASE, ec="white", lw=0.3)
    elif kind == "proj_us_fix":
        _mini_us(ax, FILL26, box=(2, 4, 196, 132))
    elif kind == "zoom_avoid":                                  # county detail at national scale
        box = (2, 4, 196, 132)
        m = _mini_us(ax, {"TX": C.context_light}, box=box)
        z = gs.Map(COUNTIES, "counties", box, ids=set(CT.index), bounds=m.bounds, tol=0.2)   # same Albers frame
        z.draw(ax, Z_FILL, default=BASE, ec="white", lw=0.1)
    elif kind == "zoom_fix":                                    # the zoom, with a locator beside it
        zax = gs.canvas(fig, (0, 0, 128 / 200, 1))
        z = zoom_map((0, 0, 128, 140), bounds=ZB_MINI)
        draw_zoom(zax, z, lw=0.5, state_lw=0.7)
        locator(ax, (132, 78, 66, 44), bounds=ZB_MINI, lw=0.8)
    elif kind in ("scale_avoid", "scale_fix"):
        zax = gs.canvas(fig, (0, 24 / 140, 1, 116 / 140))
        z = zoom_map((0, 24, 200, 116), bounds=ZB_MINI)
        if kind == "scale_fix":
            draw_zoom(zax, z, lw=0.5, state_lw=0.7)
            _key(ax, SHORT_LABELS, RAMP)
        else:                                                   # auto range: this map's min to max, continuous
            lo, hi = Z_RATE.min(), Z_RATE.max()
            fills = {k: to_hex(CMAP((v - lo) / (hi - lo))) for k, v in Z_RATE.items()}
            fills |= {k: NODATA for k in CT_SMALL.index}
            z.draw(zax, fills, default=BASE, ec="white", lw=0.5)
            z.borders(zax, {k: k[:2] for k in z.rings}, color=C.text_muted, lw=0.7, z=3)
            n = 36
            for i in range(n):
                ax.add_patch(Rectangle((10 + i * 180 / n, 12), 180 / n + 0.3, 8, fc=to_hex(CMAP(i / (n - 1))),
                                       ec="none"))
            for x, v, ha in ((10, lo, "left"), (190, hi, "right")):
                ax.text(x, 10, f"{v:.2f}", fontsize=MINI - 4, color=C.text, ha=ha, va="top")
    return fig


for _k, _alt in {"rates_avoid": "Map shaded by raw counts of postings: the big-population states are darkest.",
                 "rates_fix": "Map shaded by postings per candidate, a rate.",
                 "classes_avoid": "A key with uneven, gappy and overlapping class breaks.",
                 "classes_fix": "Five even classes with round breaks, open-ended at both ends.",
                 "hue_avoid": "A rainbow color scale where some hues pop for no reason.",
                 "hue_fix": "One sequential blue ramp, light to dark.",
                 "base_avoid": "Bubbles on a dark navy base map with heavy white borders.",
                 "base_fix": "Bubbles on a light sand base map with thin white borders.",
                 "area_avoid": "Bubbles scaled by radius: the largest site looks far bigger than it is.",
                 "area_fix": "Bubbles scaled by area.",
                 "label_avoid": "A value printed in every state; the small eastern states pile up.",
                 "label_fix": "Values only on the four states the headline names.",
                 "few_avoid": "A whole US map for three contact-center hubs.",
                 "few_fix": "The three hubs as a sorted bar chart.",
                 "privacy_avoid": "Dots at individual locations and a labelled site of seven people.",
                 "privacy_fix": "Sites aggregated; the site under 10 people dropped and footnoted.",
                 "proj_world_avoid": "World map in Mercator: Canada, Greenland and Russia swell; India looks small.",
                 "proj_world_fix": "The same world map in Equal Earth: every country at its true relative area.",
                 "proj_us_avoid": "US states in plain longitude and latitude: Alaska dwarfs the rest and the lower 48 "
                                  "are squashed into a corner.",
                 "proj_us_fix": "US states in Albers, with Alaska and Hawaii moved into insets.",
                 "zoom_avoid": "North Texas counties drawn at national scale: a smudge inside Texas.",
                 "zoom_fix": "The same counties zoomed in, with a small US locator and the frame outlined.",
                 "scale_avoid": "The county zoom on a continuous ramp stretched to its own minimum and maximum.",
                 "scale_fix": "The county zoom on the state map's five classes."}.items():
    EXHIBITS[f"geo_bp_{_k}"] = (lambda k=_k, a=_alt: (_geo_bp(k), a))
