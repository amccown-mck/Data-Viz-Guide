# Maps: choropleth, bubble map, dot density

> **Question type:** Geo-spatial
> **Use for:** showing where something is high or low, or where people and sites are concentrated, when location itself is part of the answer · **Avoid when:** geography is just a grouping and the reader needs to compare values precisely → use a sorted [bar](bar.md) chart or a [table](tables.md)

## When to use
- The question is **"where?"** and the pattern only makes sense on a map: regional clusters, coastal vs. inland, Sun Belt vs. Rust Belt, distance from a hub.
- **Choropleth** (shaded areas): one **normalized rate** per area, such as postings per candidate, attrition %, share of the workforce eligible to retire, or employees per 1,000 working-age residents. Area shading implies "intensity", so the value must be a rate, not a count.
- **Bubble map** (proportional symbols): **counts** at locations, such as headcount by distribution center, open requisitions by metro, or hires by campus. Bubble **area** is proportional to value. A second measure can drive the color with the focus/context rule.
- **Dot density**: the **spread and concentration** of many discrete occurrences, such as remote employees by home state or candidates by metro. One dot = one unit or a fixed quantity (e.g., 1 dot = 10 people). Small multiples (one map per group, same scale) compare spreads across groups.
- **Tile-grid map** (equal-size tiles per state): when big, sparsely populated states would otherwise dominate the picture, or when you need room for a label in every state.

## When not to use
- The reader needs to rank or compare values precisely → use a sorted [bar](bar.md) chart. A choropleth is good for the pattern, poor for "by how much".
- Only a handful of locations (≤ 5 sites) → use a [bar](bar.md) chart or a [table](tables.md). The map adds ink but no insight.
- The story is change over time in each region → use [small multiples](small-multiples.md) of lines, or two maps side by side on the same classes.
- Raw counts by state (headcount, hires) as shaded areas → use a **bubble map** instead. Shading counts just redraws the population map.
- Values span a huge range across a few locations → use [proportional bubbles](bubble-chart.md) without the map, or a log-scaled dot plot.

## McKesson spec

| Element | Rule |
|---|---|
| Color | **Choropleth:** a binned **sequential blue** ramp (`color.sequential.blue`, light → dark = low → high). For 5 classes use `#E6F3FB` `#B6E2FA` `#66C4FF` `#0A5FBC` `#143359`. This skips the mid step `#009EFF`, on which neither white nor navy text reaches 4.5:1. When a midpoint matters (1.0 = balanced market, 0 = at benchmark), use the **diverging orange–blue** ramp `#A75B00` `#EF8200` `#F7C180` `#EFEDE7` `#99BDD1` `#005A8C` `#143359`, centered on that midpoint with the unfavorable side orange. **Bubble / dot maps:** marks in `chart.context` `#B4B0A5`; the sites or group the headline names in `chart.focus` `#005A8C`; one exception in `chart.accent` navy `#143359` (orange only if the exception is worse, e.g., below benchmark). **Base map:** Light Sand `#EFEDE7` land, white 0.75 px boundaries. Areas suppressed for n < 10 get `chart.context_light` `#DEDBD1` and a footnote. No off-palette hues, no rainbow scales. |
| Labels | Label **only the focus areas or sites**, directly on or next to them: bold value + name (`**14.6%** Dallas`), 12 pt / 13 px, `#143359`. Bubble labels go outside the bubble unless it's large enough to hold them. The legend (class swatches stacked high → low, or a horizontal row top-left) uses the unit in its title. Add a **zoom inset** or a **lens callout** (bold 2–5 word title + 1 line) for small or dense areas (the Northeast, a metro) or the single outlier. |
| Axes / gridlines | None: no lat/long graticule, frame, coastline emphasis, or background fill. Boundaries stay thin and light. In **print**, darken boundaries to `chart.axis` `#8C8C8C`, because white hairlines can vanish on paper. |
| Sort / order | Legend classes run in value order (highest at top when stacked). Small-multiple maps run in the order of their totals, largest first, or in a stated natural order, with each total labelled beneath its map. |
| Proportions | Use an **equal-area projection** (Albers USA: Plotly `scope="usa"`; R `coord_sf(crs = 5070)`). Alaska and Hawaii are insets. Bubbles scale by **area** (Plotly `sizemode="area"`); the largest bubble is ~40–56 px across and bubbles may overlap lightly but never hide a focus site. Dots in a dot-density map are small (2–3 px) and all one size. |
| Limits | **3–5 classes** (5 is the default; never more than 7). Classes are **even-width with round breaks**, with no gaps and no overlaps, open-ended at both ends ("Under 0.8", "1.7+"), and every class holds at least one area. ≤ 2 highlighted sites or one highlighted class. **Every area, site and dot cluster is n ≥ 10**: merge small sites into "Other" or drop and footnote them. **Never plot employee home addresses**; aggregate to state, metro, or ZIP3 and place density dots randomly inside the area. |

## Do / don't

| Do | Don't |
|---|---|
| Shade **rates** (per candidate, %, per 1,000 residents) on a choropleth | Shade raw headcount or hires, which mostly shows where people live |
| Show **counts** as area-scaled bubbles on a quiet base map | Scale bubbles by radius or diameter (a 2× value looks 4× bigger) |
| Use 3–5 even, round-number classes with open-ended "+" / "Under" ends | Use uneven or overlapping ranges, or leave a gap between classes |
| Use one sequential hue, or diverging only when the midpoint means something | Use a rainbow or off-palette scale where one hue pops for no reason |
| Keep the base map light: sand fill, thin white boundaries | Use a dark or heavily outlined base map that competes with the data |
| Label the areas or sites the headline names, and add a zoom inset for tiny areas | Label every state, or make readers decode the Northeast from a legend |
| Consider a tile-grid map when large, low-value states dominate the view | Let geographic size stand in for importance |
| Aggregate locations and suppress anything under 10 people | Plot a 3-person satellite office or geocoded home addresses |

## Workforce examples
- **Sector, external:** *Headline:* "Four Sun Belt states have 1.7+ open pharmacy technician postings per candidate". *Subtitle:* "Open pharmacy technician postings per qualified candidate, by state, Q2 2026 (ratio)". *Data:* external job-postings and candidate-profile data. A choropleth on 5 even classes, the four 1.7+ states labelled, and a Northeast zoom inset (built below). Use the diverging ramp centered on 1.0 if the story is "above vs. below balanced".
- **Firm, internal:** *Headline:* "Vacancy rates top 12% at three southern distribution centers – Dallas, Memphis and Phoenix". *Subtitle:* "Distribution center associates (bubble area) and vacancy rate, Mar 2026; blue = vacancy rate 12% or higher". *Data:* Workday HCM headcount and ATS open requisitions by DC. A bubble map: bubble area = associates, focus blue = vacancy ≥ 12%, the rest context grey. One 7-person satellite site is dropped and footnoted (built below).
- **Team, internal:** *Headline:* "Six in ten remote Customer Care agents now live outside the three hub states". *Subtitle:* "Remote and hybrid Customer Care agents by home state, Mar 2026 (1 dot = 10 agents)". *Data:* Workday work-location and home-state fields, aggregated to state before plotting. A dot density map with dots placed randomly within each state, the hub states labelled, and states with fewer than 10 agents merged into "Other states" in the footnote. For a second group (e.g., onsite agents), use two small maps side by side on the same scale rather than two dot colors.

## Build it

### Python — matplotlib + `mckviz`
True state shapes need `geopandas` and a boundary file, which this kit's environment **does not install**. The route below needs no new packages: an **equal-area tile-grid map**, which also avoids the large-state bias of a choropleth. For real boundaries, install `geopandas` in your own environment, read a Census cartographic boundary file, reproject to EPSG:5070 (Albers), and call `gdf.plot(color=gdf["cls"].map(dict(enumerate(ramp))), edgecolor="white", linewidth=0.5)` with the same classes as below.

```python
# verified runnable (from the repo root)
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

import mckviz as mv

mv.use()
C = mv.colors

# Equal-area tile grid (row, col): every state gets the same visual weight, so Texas can't dominate by size.
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

# Synthetic: open pharmacy-technician postings per qualified candidate, by state (a normalized rate, not a count).
rng = np.random.default_rng(26)
ratio = pd.Series(rng.normal(1.05, 0.15, len(GRID)).clip(0.6, 1.45).round(2), index=sorted(GRID))
ratio.update(pd.Series({"TX": 1.92, "AZ": 1.84, "NV": 1.76, "FL": 1.71, "CO": 1.58, "UT": 1.52}))

# 5 even-width classes, open-ended at both ends; 5 steps of the sequential blue ramp.
edges = [-np.inf, 0.8, 1.1, 1.4, 1.7, np.inf]
labels = ["Under 0.8", "0.8\u20131.1", "1.1\u20131.4", "1.4\u20131.7", "1.7+"]
ramp = [mv.SEQUENTIAL["blue"][i] for i in (0, 1, 2, 4, 5)]  # skip #009EFF: no text color reaches 4.5:1 on it
cls = pd.cut(ratio, edges, labels=False, right=False)
focus = set(ratio.index[cls == 4])
assert focus == {"TX", "AZ", "NV", "FL"}  # headline claim: four states at 1.7+

fig, ax = plt.subplots(figsize=(10, 6.4))
for st, (r, c) in GRID.items():
    fill = ramp[cls[st]]
    ax.add_patch(Rectangle((c, -r), 0.94, 0.94, fc=fill, ec="white", lw=1.5))
    ax.text(c + 0.47, -r + 0.47, st, ha="center", va="center", fontsize=10, color=mv.text_on(fill),
            fontweight="bold" if st in focus else "regular")
ax.set_xlim(-0.1, 11.1)
ax.set_ylim(-8.1, 1.1)
ax.set_aspect("equal")
ax.set_anchor("W")
ax.axis("off")
ax.legend(handles=[Patch(fc=col, ec="none", label=lab) for col, lab in zip(ramp, labels)],
          loc="lower left", bbox_to_anchor=(0, 1.0), ncol=5, frameon=False, handlelength=1.2, columnspacing=1.2)
mv.callout(ax, (3.47, -7.0), "Tightest market: Texas", f"{ratio['TX']:.2f} open postings per qualified candidate",
           xytext=(22, -18))

mv.titles(fig, "Four Sun Belt states have 1.7+ open pharmacy technician postings per candidate",
          "Open pharmacy technician postings per qualified candidate, by state, Q2 2026 (ratio)")
mv.source(fig, "Source: External job-postings and candidate-profile data; synthetic data for illustration only",
          footnote="Each tile is one state at equal size. Classes are even-width; the top and bottom classes are open-ended.")
mv.save(fig, Path(tempfile.gettempdir()) / "map-tile-grid.png", dpi=200)
```

### Python — Plotly / HTML
Primary route for real geography, with no extra packages: `go.Choropleth` with `locationmode="USA-states"` for rates by state, and `go.Scattergeo` with `scope="usa"` for bubbles and dots. Both use the Albers USA projection with Alaska and Hawaii inset.

**Choropleth with binned classes and a zoom inset.** Plotly has no "binned" option, so map each value to its class index and use a stepped colorscale. The inset is a second `geo` showing the same trace zoomed on the Northeast.

```python
# verified: builds without error
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()
C = mv.colors

STATES = sorted(("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM "
                 "NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY").split())
# Synthetic: open pharmacy-technician postings per qualified candidate (a normalized rate, so a choropleth is OK).
rng = np.random.default_rng(26)
ratio = pd.Series(rng.normal(1.05, 0.15, len(STATES)).clip(0.6, 1.45).round(2), index=STATES)
ratio.update(pd.Series({"TX": 1.92, "AZ": 1.84, "NV": 1.76, "FL": 1.71, "CO": 1.58, "UT": 1.52}))

# Binned classes: 5 even-width steps, open-ended at both ends, drawn as a stepped (not continuous) scale.
edges = [-np.inf, 0.8, 1.1, 1.4, 1.7, np.inf]
labels = ["Under 0.8", "0.8\u20131.1", "1.1\u20131.4", "1.4\u20131.7", "1.7+"]
ramp = [mv.SEQUENTIAL["blue"][i] for i in (0, 1, 2, 4, 5)]  # skip #009EFF: no text color reaches 4.5:1 on it
cls = pd.cut(ratio, edges, labels=False, right=False)
steps = [[s, ramp[i]] for i in range(5) for s in (i / 5, (i + 1) / 5)]
focus = list(ratio.index[cls == 4])
assert sorted(focus) == ["AZ", "FL", "NV", "TX"]  # headline claim

fig = go.Figure()
fig.add_trace(go.Choropleth(
    locations=ratio.index, locationmode="USA-states", z=cls + 0.5, zmin=0, zmax=5, colorscale=steps,
    marker_line_color="white", marker_line_width=0.75, customdata=ratio.values,
    hovertemplate="%{location}: %{customdata:.2f} postings per candidate<extra></extra>",
    colorbar={"tickvals": [i + 0.5 for i in range(5)], "ticktext": labels, "thickness": 12, "len": 0.45,
              "x": 1.0, "y": 0.98, "yanchor": "top", "outlinewidth": 0, "ticks": "",
              "title": {"text": "Postings per<br>candidate", "font": {"size": 12}}}))
fig.add_trace(go.Scattergeo(                                     # label only the focus states, in place
    locations=focus, locationmode="USA-states", mode="text", text=[f"<b>{s}</b>" for s in focus],
    textfont={"color": "white", "size": 12}, hoverinfo="skip", showlegend=False))
# Inset: zoom the small Northeast states so they can be read (same data, same classes, second geo).
fig.add_trace(go.Choropleth(
    locations=ratio.index, locationmode="USA-states", z=cls + 0.5, zmin=0, zmax=5, colorscale=steps,
    marker_line_color="white", marker_line_width=0.75, showscale=False, geo="geo2",
    customdata=ratio.values, hovertemplate="%{location}: %{customdata:.2f}<extra></extra>"))
geo_style = {"showlakes": False, "showland": False, "bgcolor": "rgba(0,0,0,0)",
             "showframe": False, "showcoastlines": False, "subunitcolor": "white"}
fig.update_layout(
    geo={"scope": "usa", "domain": {"x": [0, 0.84], "y": [0, 1]}, **geo_style},
    geo2={"scope": "usa", "domain": {"x": [0.84, 1.0], "y": [0.02, 0.34]}, "projection": {"scale": 4},
          "center": {"lat": 41.2, "lon": -73.6}, **geo_style},
    height=520, margin={"l": 8, "r": 8, "t": 110})
fig.add_shape(type="rect", xref="paper", yref="paper", x0=0.84, x1=1.0, y0=0.02, y1=0.34,
              line={"color": C.axis, "width": 0.75})
fig.add_annotation(x=0.84, y=0.35, xref="paper", yref="paper", xanchor="left", yanchor="bottom", showarrow=False,
                   text="<b>Northeast, zoomed</b>", font={"size": 11, "color": C.annotation})
mv.pl_finish(fig, "Four Sun Belt states have 1.7+ open pharmacy technician postings per candidate",
             "Open pharmacy technician postings per qualified candidate, by state, Q2 2026 (ratio)",
             "Source: External job-postings and candidate-profile data; synthetic data for illustration only",
             footnote="Classes are even-width; the top and bottom classes are open-ended.")
fig.write_html(Path(tempfile.gettempdir()) / "map-choropleth.html", include_plotlyjs="cdn")
```

**Bubble map of counts by site**, with sites under 10 people dropped and footnoted:

```python
# verified: builds without error
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()
C = mv.colors

# Synthetic DC network: associates (a count -> bubble area) and vacancy rate (the headline's focus rule).
sites = pd.DataFrame([
    ("Memphis, TN", 35.15, -90.05, 1650, 13.8), ("Dallas, TX", 32.78, -96.80, 1420, 14.6),
    ("Phoenix, AZ", 33.45, -112.07, 980, 12.9), ("Columbus, OH", 39.96, -83.00, 1310, 7.2),
    ("Atlanta, GA", 33.75, -84.39, 1180, 8.4), ("Sacramento, CA", 38.58, -121.49, 890, 6.9),
    ("Harrisburg, PA", 40.27, -76.88, 860, 5.8), ("Chicago, IL", 41.88, -87.63, 820, 7.7),
    ("Kansas City, MO", 39.10, -94.58, 640, 6.1), ("Denver, CO", 39.74, -104.99, 560, 9.6),
    ("Orlando, FL", 28.54, -81.38, 610, 10.4), ("Seattle, WA", 47.61, -122.33, 430, 6.3),
    ("Albany, NY", 42.65, -73.75, 380, 5.1), ("Boise, ID (satellite)", 43.62, -116.20, 7, 0.0),
], columns=["site", "lat", "lon", "associates", "vacancy_pct"])

small = sites[sites.associates < 10]                          # n < 10: never plotted, only footnoted
sites = sites[sites.associates >= 10].sort_values("associates", ascending=False)
focus = sites.vacancy_pct >= 12
assert focus.sum() == 3                                       # headline claim: three DCs

max_px = 40                                                   # diameter of the largest bubble
pos = {"Memphis, TN": "top center", "Dallas, TX": "bottom center", "Phoenix, AZ": "middle right"}
fig = go.Figure(go.Scattergeo(
    lat=sites.lat, lon=sites.lon, mode="markers+text",
    marker={"size": sites.associates, "sizemode": "area", "sizeref": 2 * sites.associates.max() / max_px ** 2,
            "color": [C.focus if f else C.context for f in focus], "opacity": 0.9,
            "line": {"color": "white", "width": 1}},
    text=[f"<b>{s.split(',')[0]}</b> {v:.1f}%" if f else "" for s, v, f in zip(sites.site, sites.vacancy_pct, focus)],
    textposition=[pos.get(s, "middle right") for s in sites.site], textfont={"color": C.headline, "size": 12},
    customdata=sites[["site", "associates", "vacancy_pct"]],
    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,} associates<br>%{customdata[2]:.1f}% vacant<extra></extra>"))
fig.update_geos(scope="usa", showland=True, landcolor=C.surface_subtle, subunitcolor="white", subunitwidth=1,
                showlakes=False, showcoastlines=False, showframe=False, bgcolor="rgba(0,0,0,0)")
fig.update_layout(height=500, margin={"l": 8, "r": 8, "t": 110}, showlegend=False)
mv.pl_finish(fig, "Vacancy rates top 12% at three southern distribution centers \u2013 Dallas, Memphis and Phoenix",
             "Distribution center associates (bubble area) and vacancy rate, Mar 2026; blue = vacancy rate 12% or higher",
             "Source: Workday HCM and ATS open requisitions, as of 31 Mar 2026; synthetic data for illustration only",
             footnote=f"Vacancy rate = open associate requisitions \u00f7 budgeted positions. {len(small)} site with fewer than "
                      "10 associates not shown.")
fig.write_html(Path(tempfile.gettempdir()) / "map-bubbles.html", include_plotlyjs="cdn")
```

- **Dot density:** use the same `go.Scattergeo` with `mode="markers"`, `marker.size` 3 and one color. Generate one point per *k* people at random positions inside each state or ZIP3 polygon (or jittered around its centroid), never at real addresses. For small multiples, use `plotly.subplots.make_subplots(rows=1, cols=n, specs=[[{"type": "scattergeo"}] * n])`, the same scope on every map, and each group's total under its map.
- **HTML pages:** use the chart-card pattern (`card()` in [`examples/python/gallery_plotly.py`](../../examples/python/gallery_plotly.py)): the headline, subtitle and source go in HTML, which also lets long headlines wrap. Tooltips may show n, but never for an area or site with n < 10.
- **Static export:** `fig.write_image("map.svg")` (needs `kaleido`) gives a vector file for PowerPoint or print.

### Excel and PowerPoint
1. Install the theme and Libre Franklin once (see [bar.md](bar.md#excel-and-powerpoint), step 1).
2. **Filled map (choropleth):** put full state names (or 2-letter codes) in column A and the **rate** in column B. Select both, then **Insert › Charts › Maps › Filled Map**. Excel geocodes the names through Bing, so you need to be online. Fix any "?" flags it raises.
3. Right-click a state › **Format Data Series › Series Options**: **Map projection › Albers**, **Map area › Only regions with data**, **Map labels › None** (you'll label the focus states yourself).
4. **Series Color › Sequential (2-color)**: Minimum `#E6F3FB`, Maximum `#143359`. Excel only draws continuous scales. To get **binned classes**, add a column with the class number (1–5, from `=MATCH(B2,{0,0.8,1.1,1.4,1.7})`) and map *that*: five distinct values give five distinct shades. Then build the legend yourself as five small squares with labels ("Under 0.8" … "1.7+"). For a diverging story, choose **Diverging (3-color)** with Minimum `#EF8200`, Midpoint **Number** = your midpoint in `#EFEDE7`, and Maximum `#005A8C`.
5. **Format Chart Area › Border › No line** and **Fill › No fill**. Delete the chart title and the default legend. Put the headline in the slide title or a text box.
6. **Label the focus states** with text boxes (Libre Franklin 12 pt, bold value + name, `#143359`). For an **inset**, copy the chart, filter its data to the Northeast states (with **Only regions with data** on, Excel zooms in), shrink it, and give it a 0.75 pt `#8C8C8C` outline and a bold "Northeast, zoomed" label. For a lens callout, draw a circle (**Insert › Shapes › Oval**, no fill, 1 pt white or navy outline) over the outlier and a leader line to the callout text.
7. **Bubble maps and dot density:** Excel's Map chart can't do proportional symbols (3D Maps is not suitable for slides). Build these in Python above, export SVG, and in PowerPoint use **Insert › Pictures › This Device**. **Graphics Format › Convert to Shape** makes the labels editable.
8. PowerPoint has the same **Insert › Chart › Map › Filled Map** chart (it opens an embedded worksheet), so steps 3–6 also work directly on a slide. Add the source (9 pt Light, `#737373`) and the n < 10 footnote bottom-left.
9. **For print:** set the state outline (**Format Data Series › Border**) to `#8C8C8C`, 0.5 pt, because white boundaries can disappear on paper.

### Power BI
- Apply the theme: **View › Themes › Browse for themes ›** [`dist/powerbi/mckesson-dataviz-theme.json`](../../dist/powerbi/mckesson-dataviz-theme.json).
- Use the **Azure Maps** visual (the older Map and Filled map visuals are being retired; your tenant admin must enable Azure Maps). For a choropleth, add a **Filled map** layer on the state field. For bubbles, use the **Bubble layer** with **Size** = a count measure and **Range scaling** = *Magnitude* (area-proportional).
- Bin with a color measure, then set **Fill color › fx › Field value**: `State Fill = SWITCH(TRUE(), [Ratio] >= 1.7, "#143359", [Ratio] >= 1.4, "#0A5FBC", [Ratio] >= 1.1, "#009EFF", [Ratio] >= 0.8, "#66C4FF", "#B6E2FA")`. Do the same for focus/context bubbles (`"#005A8C"` / `"#B4B0A5"`).
- **Privacy:** map visuals send location values to an Azure service for geocoding, so check this against your data-handling rules. Map only aggregated locations (state, metro, site); never latitude/longitude of employees' homes. Remove precise-location fields from tooltips, and apply row-level security before the map.
- **Minimum n:** `Ratio (safe) = IF([Headcount] < 10, BLANK(), [Ratio])` and `Site Headcount (safe) = IF([Headcount] < 10, BLANK(), [Headcount])`. Use the safe measures in the visual, the tooltips and drill-through, and footnote what's suppressed.
- For an equal-area tile map, the **Shape map** visual (preview) accepts a custom TopoJSON. Otherwise pair the map with a sorted bar chart for exact comparisons.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr)
source("dist/r/theme_mck.R")
# maps::map_data() needs {maps}; the Albers projection needs {mapproj}. Lower 48 only.
# For AK/HI insets use {sf} + tigris::states(cb = TRUE) |> tigris::shift_geometry() and coord_sf(crs = 5070).

rates <- tibble(abb = c(state.abb, "DC"), ratio = runif(51, 0.7, 1.4)) |>
  mutate(ratio = case_when(abb == "TX" ~ 1.92, abb == "AZ" ~ 1.84, abb == "NV" ~ 1.76, abb == "FL" ~ 1.71,
                           TRUE ~ ratio),
         region = tolower(c(state.name, "district of columbia")),
         cls = cut(ratio, c(-Inf, 0.8, 1.1, 1.4, 1.7, Inf), right = FALSE,
                   labels = c("Under 0.8", "0.8–1.1", "1.1–1.4", "1.4–1.7", "1.7+")))
shapes <- map_data("state") |> left_join(rates, by = "region")

ggplot(shapes, aes(long, lat, group = group, fill = cls)) +
  geom_polygon(color = "white", linewidth = 0.25) +
  coord_map("albers", lat0 = 29.5, lat1 = 45.5) +
  scale_fill_manual(values = mck_sequential[c(1, 2, 3, 5, 6)], drop = FALSE, name = "Postings per candidate") +
  labs(title = "Four Sun Belt states have 1.7+ open pharmacy technician postings per candidate",
       subtitle = "Open pharmacy technician postings per qualified candidate, by state, Q2 2026 (ratio)",
       caption = "Source: External job-postings data; synthetic data for illustration only") +
  theme_mck() + theme(axis.text = element_blank(), axis.title = element_blank(),
                      panel.grid = element_blank(), axis.line.x = element_blank())

# Bubble map: counts at sites, area-proportional.
# + geom_point(data = sites, aes(lon, lat, size = associates, color = vacancy_pct >= 12), inherit.aes = FALSE) +
#   scale_size_area(max_size = 14, guide = "none") +
#   scale_color_manual(values = c(`TRUE` = mck_colors$focus, `FALSE` = mck_colors$context), guide = "none")
```

## QA specifics
- [ ] Choropleth values are **rates** (per candidate, %, per 1,000), not raw counts. Counts are shown as **area-scaled** bubbles.
- [ ] 3–5 binned classes with round, even-width breaks, no gaps or overlaps, open-ended ends, and a legend that names the unit. A diverging scale is centered on a stated, meaningful midpoint.
- [ ] Only brand ramps are used (sequential blue, or diverging orange–blue). The base map is light sand with thin white boundaries (darker boundaries for print), with no graticule or frame.
- [ ] The areas or sites the headline names are labelled directly. Small or dense areas have a zoom inset or a lens callout. At most 2 highlighted sites or one highlighted class.
- [ ] Every area, site and dot cluster is **n ≥ 10**. Smaller ones are merged or suppressed and footnoted, including in tooltips. No individual or home-level locations are plotted.
- [ ] The headline claim is recomputed from the data (e.g., exactly four states are in the 1.7+ class), and the projection is equal-area (Albers USA).

## Inspiration
- [p062 — Choropleth](../../reference/inspiration-mckinsey/pages/p062-choropleth.md)
- [p063 — Bubble map](../../reference/inspiration-mckinsey/pages/p063-bubble-map.md)
- [p064 — Dot density map](../../reference/inspiration-mckinsey/pages/p064-dot-density-map.md)
- [p065 — Maps best practice](../../reference/inspiration-mckinsey/pages/p065-maps-best-practice.md)
- [p084 — Print](../../reference/inspiration-mckinsey/pages/p084-print.md)
