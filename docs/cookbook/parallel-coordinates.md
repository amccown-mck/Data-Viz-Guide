# Parallel coordinates

> **Question type:** Relationships & flows (multivariate profiles)
> **Use for:** showing how a few sites, roles or skill groups stand out across 4–8 measures at once, with 1–2 groups highlighted against grey · **Avoid when:** you have ≤ 3 measures or the reader needs exact values → use a [scatter](scatter-bubble.md), [dot plot](dot-plot-dumbbell.md) or [table](tables.md)

## When to use
- Each entity (a site, job family, skill cluster or employer) has **4–8 measures**, and the story is that **one group looks different on several of them at once**. For example: the three distribution centers with the most overtime also have the highest attrition, the slowest fills and the widest spans.
- You want to show a **profile**: the shape of one line across the axes, against the grey "everyone else".
- It can do a job a table does badly. A table of 18 sites × 6 measures hides the pattern. A parallel-coordinates chart shows it at a glance, as long as one group is highlighted.
- **Exploratory tools** (HTML, dashboards), where users can **brush** a range on an axis to filter lines, **drag axes to reorder** them, or hide axes. Interactivity is a better way to focus than cropping axes away.

## When not to use
- Only 2–3 measures → use a [scatter / bubble](scatter-bubble.md) (2–3 measures) or a [dot plot / dumbbell](dot-plot-dumbbell.md) (one measure, two points).
- One measure over time → use a [line](line.md) chart. The axes here are different variables, **not** time steps.
- The reader needs exact values for every cell → use a [table](tables.md) with conditional formatting, or a [heatmap](heatmap.md) (entities × measures, color = standardized score).
- Comparing many groups equally, with no single group to highlight → use [small multiples](small-multiples.md) of bars per measure. A tangle of colored lines has no message.
- The entities are **individual people**. Each line would be a person's record, which risks re-identification. Aggregate to groups of n ≥ 10 first.

## McKesson spec

| Element | Rule |
|---|---|
| Color | Grey everything, then color the group the headline names. Context lines `chart.context` `#B4B0A5` at 1 px (`chart.line.context_width_px` 1.25 max) with ~30% transparency. Focus lines `chart.focus` `#005A8C` at 2 px, drawn **on top**. One exception the headline calls out may be `chart.accent` `#EF8200`. Highlight **≤ 2 groups** (one color each). Never use one color per line, and never use several shades of blue for several groups. If two groups must be compared, use `color.categorical` positions 1–2 (`#005A8C`, `#EF8200`) and nothing else. |
| Labels | Label focus lines directly at the right end (series label role: 12 pt / 13 px, SemiBold, in the line color). No legend. Axis names go below each axis (tick role, 11 pt / 12 px, `#505050`), with the unit in parentheses. **Bold the story axis names** in Navy `#143359`. Show each axis's raw **min at the bottom and max at the top** in `#737373`, 9–11 pt. Use thousands separators and `%` where relevant. One callout (bold 2–5 word title + 1 line) sits in empty space near the axes it explains. |
| Axes / gridlines | Thin vertical axes in `chart.axis` `#8C8C8C`, 0.75 pt. No horizontal gridlines, no frame, no markers where lines cross axes. |
| Sort / order | **Order axes deliberately.** Put the story axis first (leftmost), then the measures it explains, then the context measures. Place related measures next to each other so crossings between them are meaningful. **Orient every axis so the same direction means the same thing** (e.g., up = more risk). Reverse axes like engagement or tenure and say "reversed" in the axis name and footnote. Keep the same axis order on every slide of a build-up. |
| Proportions | **Normalize each axis** (min–max per axis, or a percentile/z-score scale, stated in the subtitle). Never put raw units with different scales on one shared y-axis. Evenly spaced axes. About 16:9 for slides. |
| Limits | 4–8 axes. ≤ ~50 lines for a static chart (beyond that, show group medians or a density and keep the focus lines). ≤ 2 highlighted groups. **Every line is an aggregate with n ≥ 10.** Drop or merge smaller units into "Other" and footnote it, including in tooltips. |

## Do / don't

| Do | Don't |
|---|---|
| Color one group dark blue and push every other line to light grey | Color each line or group in its own shade of blue. It's a noisy tangle with no focus |
| Put the story axis first and order the rest so neighbors relate | Leave axes in the order they came out of the database |
| Normalize each axis and print the real min and max at its ends | Plot raw values on one shared scale, so the axis with the biggest numbers flattens the rest |
| Flip axes so "up" always means the same thing, and label the flip | Mix directions and leave readers to work out whether high is good or bad |
| Offer brushing, axis reordering or hiding in interactive versions, keeping all axes visible | Crop a static chart down to 2–3 axes. The context is lost |
| Use it instead of a dense table when the message is a multi-measure profile | Show an illegible 18 × 6 table and expect readers to spot the pattern |
| Label focus lines at the end and annotate the one pattern that matters | Add a legend with 18 entries |

## Workforce examples
- **Site, internal:** *Headline:* "Three distribution centers combine the most overtime with the highest attrition and slowest fills". *Subtitle:* "Workforce profile of 18 U.S. distribution centers, FY26 (each axis scaled min–max; up = worse)". *Data:* Workday HCM (attrition, span, tenure), timekeeping (overtime hours per FTE), ATS (time to fill) and engagement survey. All sites n ≥ 180. Built below.
- **Job family, SWP / transformation:** *Headline:* "Claims and billing roles combine the highest Gen AI exposure with the thinnest adjacent-skill bench". *Subtitle:* "Profile of 14 job families on six transformation measures, FY26 (each axis scaled min–max)". *Data:* [`examples/data/automation_exposure.csv`](../../examples/data/automation_exposure.csv) (exposure, headcount, pay), plus skills-inventory adjacency, internal-mobility rate and an external task-exposure benchmark. Axis order: exposure → reskilling readiness → mobility rate → pay → headcount. Claims & Billing in blue, Customer Care in orange as the counter-example. Firm level, internal and external signals.
- **Sector, external:** *Headline:* "Our pharmacy-technician offer trails peers on pay but leads on schedule flexibility and promotion rate". *Subtitle:* "Employer value-proposition profile, pharmacy technicians, McKesson vs. 11 distribution and retail-pharmacy employers, 2026 (each axis scaled min–max)". *Data:* external pay benchmarks, job-postings data (shift patterns, benefits mentioned) and aggregated employer-review scores. McKesson in focus blue, peers grey and unnamed. Sector level, external signal.

## Build it

### Python — matplotlib + `mckviz`
```python
# verified runnable (from the repo root)
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import mckviz as mv

mv.use()
C = mv.colors
rng = np.random.default_rng(7)

# Site profiles: 18 distribution centers (every site has hundreds of employees, so n >= 10 holds)
df = pd.DataFrame({
    "site": [f"DC {i:02d}" for i in range(1, 19)],
    "headcount": rng.integers(180, 900, 18),
    "overtime": rng.normal(9, 2, 18).round(1),
    "attrition": rng.normal(19, 2.5, 18).round(1),
    "time_to_fill": rng.normal(34, 5, 18).round(0),
    "span": rng.normal(17, 2, 18).round(1),
    "engagement": rng.normal(72, 3, 18).round(0),
    "tenure": rng.normal(5.6, 1.0, 18).round(1),
})
focus = ["DC 04", "DC 11", "DC 15"]
assert df.headcount.min() >= 10                                                # every line is a group of n >= 10
measures = ["overtime", "attrition", "time_to_fill", "span", "engagement", "tenure"]
df.loc[df.site.isin(focus), measures] = [[17.5, 31.2, 52, 24.5, 63, 2.9],
                                         [16.1, 29.4, 49, 23.0, 65, 3.4],
                                         [15.2, 27.8, 55, 22.1, 64, 3.2]]
assert set(df.nlargest(3, "overtime").site) == set(focus)                      # headline: the 3 highest-overtime sites...
assert (df[df.site.isin(focus)].attrition > 25).all() and (df[~df.site.isin(focus)].attrition < 25).all()
assert set(df.nlargest(3, "time_to_fill").site) == set(focus)

# Axis order is a design choice: story axis first, then the measures it drives. Reversed axes keep "worse = up".
axes = [("overtime", "Overtime\n(hrs/FTE/month)", "{:.0f}", False),
        ("attrition", "Vol. attrition\n(%)", "{:.0f}%", False),
        ("time_to_fill", "Time to fill\n(days)", "{:.0f}", False),
        ("span", "Span of control\n(reports)", "{:.0f}", False),
        ("engagement", "Engagement\n(index, reversed)", "{:.0f}", True),
        ("tenure", "Median tenure\n(years, reversed)", "{:.1f}", True)]
norm = pd.DataFrame(index=df.index)
for col, _, _, rev in axes:
    s = df[col]
    norm[col] = (s - s.min()) / (s.max() - s.min())                           # min-max per axis
    if rev:
        norm[col] = 1 - norm[col]
x = np.arange(len(axes))

fig, ax = plt.subplots(figsize=(10, 5.6))
for i, (col, name, fmt, rev) in enumerate(axes):
    ax.plot([i, i], [0, 1], color=C.axis, lw=0.75, zorder=1)
    top, bottom = (df[col].min(), df[col].max()) if rev else (df[col].max(), df[col].min())
    ax.text(i, 1.03, fmt.format(top), ha="center", va="bottom", fontsize=9, color=C.text_muted)
    ax.text(i, -0.03, fmt.format(bottom), ha="center", va="top", fontsize=9, color=C.text_muted)
    ax.text(i, -0.13, name, ha="center", va="top", fontsize=10, linespacing=1.2,
            color=C.headline if i < 2 else C.text, fontweight="bold" if i < 2 else "normal")
for idx in df.index[~df.site.isin(focus)]:                                     # context first, thin grey
    ax.plot(x, norm.loc[idx, [a[0] for a in axes]], color=C.context, lw=1.0, alpha=0.7, zorder=2)
for idx in df.index[df.site.isin(focus)]:                                      # focus on top, 2x weight
    y = norm.loc[idx, [a[0] for a in axes]].to_numpy()
    ax.plot(x, y, color=C.focus, lw=2.0, zorder=3, solid_capstyle="round")
ends = norm.loc[df.site.isin(focus), axes[-1][0]].set_axis(df.site[df.site.isin(focus)]).sort_values(ascending=False)
prev = 2.0
for site, end in ends.items():                                                 # direct labels, nudged >= 0.08 apart
    prev = min(end, prev - 0.08)
    ax.text(x[-1] + 0.12, prev, site, va="center", fontsize=10, fontweight="semibold", color=C.focus)
mv.callout(ax, (0.12, 0.66), "Overtime travels with exits",
           "The 3 sites above 15 hrs/FTE also lose >1 in 4 associates", xytext=(0, 0), arrow=False)
ax.set_xlim(-0.35, len(axes) - 1 + 0.6)
ax.set_ylim(-0.05, 1.12)
mv.clean_axes(ax, keep=(), grid=None)
ax.set_xticks([])
ax.set_yticks([])

mv.titles(fig, "Three distribution centers combine the most overtime with the highest attrition and slowest fills",
          "Workforce profile of 18 U.S. distribution centers, FY26 (each axis scaled min\u2013max; up = worse)")
mv.source(fig, "Source: Workday HCM, timekeeping, ATS and engagement survey, as of 31 Mar 2026; synthetic data for illustration",
          footnote="Engagement and tenure axes are reversed so that higher always means more risk. All sites n \u2265 180.")
out = mv.save(fig, Path(tempfile.gettempdir()) / "parallel-coordinates-dc.png", dpi=200)
print("saved", out)
```
- With more than ~50 entities, draw the context as group medians or a light band (10th–90th percentile per axis) and keep only the focus lines individual.
- Min–max scaling exaggerates small spreads. If one axis spans 71–75, say so in the footnote, or use a common percentile scale (0–100th) across all axes.

### Python — Plotly / HTML
Use `go.Parcoords` for the interactive version. Users can **brush** (drag along an axis to filter lines), **reorder** axes (drag an axis title) and clear a brush by clicking the axis. Plotly draws Parcoords lines at a fixed 1 px width, so the focus/context contrast comes from color alone. Keep the focus group to one color.

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
rng = np.random.default_rng(7)

df = pd.DataFrame({
    "site": [f"DC {i:02d}" for i in range(1, 19)],
    "headcount": rng.integers(180, 900, 18),
    "overtime": rng.normal(9, 2, 18).round(1),
    "attrition": rng.normal(19, 2.5, 18).round(1),
    "time_to_fill": rng.normal(34, 5, 18).round(0),
    "span": rng.normal(17, 2, 18).round(1),
    "engagement": rng.normal(72, 3, 18).round(0),
    "tenure": rng.normal(5.6, 1.0, 18).round(1),
})
focus = ["DC 04", "DC 11", "DC 15"]
assert df.headcount.min() >= 10                                    # every line is a group of n >= 10
measures = ["overtime", "attrition", "time_to_fill", "span", "engagement", "tenure"]
df.loc[df.site.isin(focus), measures] = [[17.5, 31.2, 52, 24.5, 63, 2.9],
                                         [16.1, 29.4, 49, 23.0, 65, 3.4],
                                         [15.2, 27.8, 55, 22.1, 64, 3.2]]
df["is_focus"] = df.site.isin(focus).astype(int)
df = df.sort_values("is_focus")                                    # focus rows last = drawn on top

axes = [("overtime", "<b>Overtime (hrs/FTE/mo)</b>", ".0f", False),
        ("attrition", "<b>Vol. attrition (%)</b>", ".0f", False),
        ("time_to_fill", "Time to fill (days)", ".0f", False),
        ("span", "Span of control", ".0f", False),
        ("engagement", "Engagement (reversed)", ".0f", True),
        ("tenure", "Tenure, yrs (reversed)", ".1f", True)]
dims = []
for col, label, fmt, rev in axes:
    lo, hi = df[col].min(), df[col].max()
    dims.append(dict(label=label, values=df[col], tickformat=fmt,
                     range=[hi, lo] if rev else [lo, hi],             # reversed range keeps "up = worse"
                     tickvals=[lo, hi]))                              # min/max only, like the static version

fig = go.Figure(go.Parcoords(
    line=dict(color=df.is_focus, colorscale=[[0, C.context], [1, C.focus]], cmin=0, cmax=1),
    unselected=dict(line=dict(color=C.context_light, opacity=0.6)),     # lines outside a brush fade, not vanish
    dimensions=dims, domain=dict(x=[0.04, 0.96], y=[0.14, 1]),
    labelangle=0, labelside="bottom",
    labelfont=dict(size=12, color=C.text), tickfont=dict(size=11, color=C.text_muted),
    rangefont=dict(size=1, color="rgba(0,0,0,0)"),
))
mv.pl_finish(fig, "Three distribution centers combine the most overtime with the highest attrition and slowest fills",
             "Workforce profile of 18 U.S. distribution centers, FY26 (each axis scaled min\u2013max; up = worse)",
             source_text="Source: Workday HCM, timekeeping, ATS and engagement survey, as of 31 Mar 2026; synthetic data",
             footnote="Drag along an axis to brush; drag an axis title to reorder. Engagement and tenure axes are reversed.")
fig.update_layout(height=540, margin=dict(l=40, r=40, t=120, b=110))
out = Path(tempfile.gettempdir()) / "parallel-coordinates-dc.html"
fig.write_html(out, include_plotlyjs="cdn")
print("saved", out)
```
- To open the page pre-filtered on the story, set `constraintrange=[15, 18]` on the first dimension. Lines outside the brush switch to the `unselected` style.
- Parcoords has no hover tooltips. If readers need site names on hover, use a `go.Scatter` line-per-entity build (like the matplotlib version) instead. Tooltips must never expose units with n < 10.
- For web pages, use the chart-card pattern in [`examples/python/gallery_plotly.py`](../../examples/python/gallery_plotly.py), with the headline, subtitle and source in HTML.

### Excel and PowerPoint
1. Install the theme once (see [bar.md](bar.md#excel-and-powerpoint)): **Page Layout › Colors › McKesson Data Viz** and **Fonts › McKesson Data Viz** (PowerPoint: **Design › Variants › Colors / Fonts**), from `dist/office/`. Fonts are Libre Franklin.
2. **Normalize first.** Build a helper table with one row per site and one column per measure, **in your chosen axis order**. Use `=(B2-MIN(B$2:B$19))/(MAX(B$2:B$19)-MIN(B$2:B$19))`; for reversed axes, `=1-(…)`. Put each axis's real range in the header, e.g. `Overtime (hrs/FTE/mo)` + `Alt+Enter` + `4–18`.
3. Select the helper table, then **Insert › Charts › Insert Line or Area Chart › 2-D Line › Line**. If the measures appear as series, use **Chart Design › Switch Row/Column** so the **measures are the categories** (x-axis) and each site is a series.
4. Double-click the vertical axis: **Format Axis › Axis Options › Bounds › Minimum 0, Maximum 1**. Then select it and press **Delete**. Delete the horizontal gridlines, the legend and the chart title.
5. Double-click the horizontal axis: **Axis Options › Axis position › On tick marks** (lines start and end on the first and last axes), **Tick Marks › None**, **Line › No line**. Then **Chart Elements (+) › Gridlines › Primary Major Vertical** and format them **Solid line, `#8C8C8C`, 0.75 pt**. These are your axes.
6. Format one context series: **Format Data Series › Fill & Line › Line › Solid line, `#B4B0A5`, Width 1 pt, Transparency 30%**, **Marker › None**. Pick the next series from **Format › Current Selection** and press **F4** to repeat the formatting.
7. Format the focus series: **`#005A8C`, 2.25 pt**. To draw it on top, open **Chart Design › Select Data**, select the focus series and click **Move Down** until it's last.
8. Label the focus lines at the right: click the last point of a focus series twice, then **Add Data Label › Format Data Label › Series Name** only, **Label Position › Right**. Use Libre Franklin SemiBold 12 pt in `#005A8C`.
9. Bold the story axis names: Excel can't bold one category label, so overlay text boxes (Libre Franklin Bold 11 pt, `#143359`) or hide the axis labels and type all axis names in text boxes.
10. In PowerPoint, **Home › Paste › Use Destination Theme & Embed Workbook**. Headline in the title placeholder (24 pt Bold Navy), subtitle 14 pt `#505050`, source 9 pt Light `#737373`, bottom-left. Build up by duplicating the slide: all lines grey → focus lines blue → callout. Slides can't brush, so link to the HTML version for exploration.

### Power BI
- Apply the theme: **View › Themes › Browse for themes ›** `dist/powerbi/mckesson-dataviz-theme.json`.
- **Native route (recommended):** unpivot in Power Query to `Site | Measure | AxisOrder | Value | Reverse`. Sort `Measure` by `AxisOrder` (**Column tools › Sort by column**). Use a **Line chart** with X-axis = `Measure` (categorical), Y-axis = a normalized measure, and Legend = `Site`. Turn off the Y-axis and the legend. Under **Format › Lines › Colors**, set every series to `#B4B0A5` and the focus series to `#005A8C`.
  ```DAX
  Norm value =
  VAR v  = AVERAGE ( Profile[Value] )
  VAR lo = CALCULATE ( MIN ( Profile[Value] ), ALLEXCEPT ( Profile, Profile[Measure] ) )
  VAR hi = CALCULATE ( MAX ( Profile[Value] ), ALLEXCEPT ( Profile, Profile[Measure] ) )
  VAR s  = DIVIDE ( v - lo, hi - lo )
  RETURN IF ( MAX ( Profile[Reverse] ), 1 - s, s )
  ```
- A bar chart of sites next to it works as a **brush**: clicking a site cross-highlights its line. Enforce n ≥ 10 before the visual: filter out units below the threshold in Power Query and footnote it.
- AppSource has parallel-coordinates **custom visuals**. Most are not Microsoft-certified. Route them through your tenant's custom-visual security review (uncertified visuals may be blocked from PPT/PDF export or may call external services), and expect limited theme support.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr); library(tidyr)
source("dist/r/theme_mck.R")

set.seed(7)
sites <- data.frame(
  site = sprintf("DC %02d", 1:18),
  overtime = round(rnorm(18, 9, 2), 1), attrition = round(rnorm(18, 19, 2.5), 1),
  time_to_fill = round(rnorm(18, 34, 5)), span = round(rnorm(18, 17, 2), 1),
  engagement = round(rnorm(18, 72, 3)), tenure = round(rnorm(18, 5.6, 1), 1)
)
focus <- c("DC 04", "DC 11", "DC 15")
sites[sites$site %in% focus, -1] <- matrix(c(17.5, 31.2, 52, 24.5, 63, 2.9,
                                              16.1, 29.4, 49, 23.0, 65, 3.4,
                                              15.2, 27.8, 55, 22.1, 64, 3.2), nrow = 3, byrow = TRUE)
axis_names <- c(overtime = "Overtime\n(hrs/FTE/mo)", attrition = "Vol. attrition\n(%)",
                time_to_fill = "Time to fill\n(days)", span = "Span of control",
                engagement = "Engagement\n(reversed)", tenure = "Median tenure\n(reversed)")

long <- sites |>
  pivot_longer(-site, names_to = "measure") |>
  group_by(measure) |>
  mutate(scaled = (value - min(value)) / (max(value) - min(value)),
         scaled = if_else(measure %in% c("engagement", "tenure"), 1 - scaled, scaled)) |>
  ungroup() |>
  mutate(axis = factor(axis_names[measure], levels = axis_names), is_focus = site %in% focus)

ggplot(long, aes(axis, scaled, group = site)) +
  geom_vline(xintercept = seq_along(axis_names), color = mck_colors$axis, linewidth = 0.3) +
  geom_line(data = filter(long, !is_focus), color = mck_colors$context, linewidth = 0.4, alpha = 0.7) +
  geom_line(data = filter(long, is_focus), color = mck_colors$focus, linewidth = 0.9) +   # drawn last = on top
  geom_text(data = filter(long, is_focus, measure == "tenure"), aes(label = site),
            hjust = -0.2, size = 3.4, fontface = "bold", color = mck_colors$focus) +
  scale_y_continuous(breaks = NULL) +
  scale_x_discrete(expand = expansion(add = c(0.3, 0.7))) +
  labs(title = "Three distribution centers combine the most overtime with the highest attrition and slowest fills",
       subtitle = "Workforce profile of 18 U.S. distribution centers, FY26 (each axis scaled min–max; up = worse)",
       caption = "Source: Workday HCM, timekeeping, ATS and engagement survey; synthetic data", x = NULL, y = NULL) +
  theme_mck() +
  theme(panel.grid = element_blank(), axis.line.x = element_blank())

# Quick exploratory look (optional package): GGally::ggparcoord(sites, columns = 2:7, scale = "uniminmax")
# Its automatic axis ordering is for exploration; for explanatory charts, order axes by the story as above.
```

## QA specifics
- [ ] Every axis is normalized (method stated in the subtitle), and the raw min/max is printed at each axis end with units.
- [ ] Axis order is deliberate: story axis first, related measures adjacent, and the same order on every slide.
- [ ] Every axis points the same way ("up = worse" or "up = better"). Reversed axes are labelled and footnoted.
- [ ] ≤ 2 highlighted groups, drawn on top, matching the headline. All other lines are grey with no per-line colors or legend.
- [ ] Every line is an aggregate of **n ≥ 10**, including in tooltips, brushes and drill-downs. No individual-person lines.
- [ ] The headline claim is recomputed from the data (e.g., the three focus sites really are the top 3 on overtime and time to fill, and the only sites above 25% attrition).

## Inspiration
- [p058 — Parallel coordinates](../../reference/inspiration-mckinsey/pages/p058-parallel-coordinates.md)
- [p059 — Parallel coordinates best practice](../../reference/inspiration-mckinsey/pages/p059-parallel-coordinates-best-practice.md)
- [p072 — Interactivity](../../reference/inspiration-mckinsey/pages/p072-interactivity.md)
