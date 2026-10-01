# Proportional (packed) bubble charts

> **Question type:** Magnitude
> **Use for:** a quick sense of scale when values span orders of magnitude (one or two giants and a long tail) · **Avoid when:** values are close together or must be compared precisely → use a [bar chart](bar.md)

<!-- No rendered example in examples/output yet; the matplotlib snippet below produces one. -->

## When to use
- Values differ **enormously** (as a rule of thumb, largest ≥ ~20× smallest), so a bar chart would squash the small values into slivers.
- The message is about **scale**, not precise differences: "one function holds more automatable hours than all others combined"; "demand for role A is 30× demand for role B".
- Explanatory settings (exec summaries, reports, social cards) where a striking size contrast carries the point and every bubble is labelled with its value.
- Bubbles carry no axes or gridlines, so they suit **direct labelling**.

## When not to use
- Values within ~3× of each other: area differences are hard to see → use a [bar chart](bar.md). Bars encode by length, which the eye compares far more precisely.
- The reader must rank close items or read exact differences → use a [sorted bar chart](bar.md).
- Bubble **position** encodes two more measures → that's a [bubble scatter](scatter-bubble.md). Bubbles placed over time → use a [bubble timeline](bubble-timeline.md). Bubbles on a map → use a [bubble map](maps.md).
- Parts of one total, especially a hierarchy → use a [treemap](treemap.md) (rectangles pack and compare better than circles).

## McKesson spec

| Element | Rule |
|---|---|
| Color | **One color** for all bubbles, `chart.focus` `#005A8C`, **or** `chart.context` `#B4B0A5` for all with the headline bubble in `chart.focus` `#005A8C` (one exception in `chart.accent` navy `#143359`). Highlight at most 2. Use the categorical order (`#005A8C`, `#143359`, `#66C4FF`, `#00AF9D`, …) only when color **encodes a group** (≤ 3–4 groups), with a small top-left key. Never use decorative multi-color bubbles. No gradients, 3D or shadows. |
| Labels | Every bubble shows a **bold value** plus its category name in regular weight. Put the label **inside** when the bubble is big enough (white on `#005A8C`, navy `#143359` on grey; use `mv.text_on()`). Otherwise put it **below** (or beside) the bubble, aligned on one shared line. Use one unit in the subtitle ("thousand hours", "$M") and consistent K/M. |
| Axes / gridlines | None: no axes, gridlines, size legend or frame. Values are labelled, so the size key is redundant. |
| Sort / order | **Descending by size.** Largest first (left, or top-left), wrapping into a second row like text if needed; keep the order monotonic. The arrangement may adapt to the layout, but never scatter bubbles randomly. Bubbles sit on a **shared baseline** (single row) or are packed with 2–4 px white gaps and no overlap. |
| Proportions | **Area ∝ value**, never diameter: `r = √(value / π) × k`. That is matplotlib `Circle` with `r ∝ √v`, Plotly `sizemode="area"`, ggplot2 `scale_size_area()` or `packcircles(sizetype = "area")`, and Excel **Size represents: Area of bubbles**. Keep the aspect ratio equal, so circles stay circles. The smallest bubble must be ≥ ~6 px across. |
| Limits | ≤ ~12 bubbles. If max/min exceeds ~1,000×, the smallest become dots: group them into "Other", or list them in a footnote. Headcount-based bubbles follow **n ≥ 10**. |

## Do / don't

| Do | Don't |
|---|---|
| Use bubbles when values span orders of magnitude | Use bubbles for values like 140 / 147 / 160: the differences vanish |
| Scale bubble **area** to the value (a 4× value → 2× diameter) | Scale the diameter (a 4× value looks 16× bigger) |
| Sort largest to smallest so the rank reads at a glance | Scatter bubbles in a loose, arbitrary cluster that hides the insight |
| Use one color, or grey plus one highlight tied to the headline | Give each bubble its own decorative color |
| Use color only to encode a real grouping, keyed top-left | Rely on color without a key, or use more than ~4 groups |
| Label every bubble's value directly (inside or below) | Add a "size legend" and make readers estimate areas |
| Use bars when values are close together | Swap bars for bubbles just for visual variety |

## Workforce examples
- **Firm, internal (SWP / automation):** *Headline:* "Distribution holds 1.6x the automatable work hours of all other functions combined". *Subtitle:* "Task hours automatable with current technology, by function, FY26 (thousand hours per year)". *Data:* the task inventory × an external automation taxonomy (inline data in the snippet below; range 45–9,800, ~218×).
- **Sector, external labor market:** *Headline:* "U.S. healthcare employers posted 34x more pharmacy-technician roles than machine-learning roles last year". *Subtitle:* "U.S. job postings by role, healthcare and pharma employers, trailing 12 months to Jun 2026 (thousand postings)". *Data:* external job-postings data. Pharmacy technician 410, pharmacist 96, data analyst 52, data engineer 21, ML engineer 12, gen AI specialist 3. The ML bubble is in focus blue; the rest are grey.
- **Team, internal (transformation pilots):** *Headline:* "The Pharmacy Ops automation pilot frees 20x more hours than any other team pilot". *Subtitle:* "Annualized hours freed by automation pilot, by team, FY26 (thousand hours)". *Data:* pilot time studies. Grey bubbles with Pharmacy Ops in `#005A8C`; footnote the measurement method.

## Build it

### Python — matplotlib + `mckviz`
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle

import mckviz as mv

mv.use()
C = mv.colors

df = pd.DataFrame({
    "function": ["Distribution", "Customer Care", "Pharmacy Ops", "Finance Ops", "HR Ops", "Sales", "Legal"],
    "hours_k": [9800, 2900, 2300, 640, 310, 120, 45],
}).sort_values("hours_k", ascending=False, ignore_index=True)   # largest first
focus = "Distribution"
ratio = df.hours_k[df.function == focus].iloc[0] / df.hours_k[df.function != focus].sum()

r = np.sqrt(df.hours_k.to_numpy() / np.pi)               # AREA proportional to value (radius ~ sqrt)
gap = 0.28 * r.max()
x = r[0] + np.r_[0, np.cumsum(r[:-1] + r[1:] + gap)]      # one row, touching a shared baseline

fig, ax = plt.subplots(figsize=(10, 4.2))
for xi, ri, row in zip(x, r, df.itertuples()):
    fill = C.focus if row.function == focus else C.context
    ax.add_patch(Circle((xi, ri), ri, color=fill, lw=0))
    value = f"{row.hours_k:,.0f}"
    if ri > 0.4 * r.max():                                # big enough: label inside
        ink = mv.text_on(fill)
        ax.text(xi, ri + 4, value, ha="center", va="bottom", fontsize=12, fontweight="bold", color=ink)
        ax.text(xi, ri, row.function, ha="center", va="top", fontsize=9, color=ink)
    else:                                                 # too small: label below the baseline
        bold = row.function == focus
        ax.text(xi, -3, value, ha="center", va="top", fontsize=10, fontweight="bold", color=C.headline)
        ax.text(xi, -15, row.function, ha="center", va="top", fontsize=9,
                color=C.headline if bold else C.text)

ax.set_xlim(-gap, x[-1] + r[-1] + gap)
ax.set_ylim(-28, 2 * r.max() + 4)
ax.set_aspect("equal")                                    # circles stay circles
ax.axis("off")

mv.titles(fig, f"Distribution holds {ratio:.1f}x the automatable work hours of all other functions combined",
          "Task hours automatable with current technology, by function, FY26 (thousand hours per year)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Automatable = task hours matched to robotics, RPA or gen AI capabilities in an external task taxonomy.")
mv.save(fig, "out/bubble.png", dpi=200)
```
For more than ~8 bubbles, wrap into two rows: start a new row when `x` exceeds the plot width, keeping the descending order.

### Python — Plotly / HTML
```python
# verified: builds without error
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()  # registers + activates the "mck" Plotly template
C = mv.colors

df = pd.DataFrame({
    "function": ["Distribution", "Customer Care", "Pharmacy Ops", "Finance Ops", "HR Ops", "Sales", "Legal"],
    "hours_k": [9800, 2900, 2300, 640, 310, 120, 45],
}).sort_values("hours_k", ascending=False, ignore_index=True)
focus = "Distribution"
r = np.sqrt(df.hours_k.to_numpy() / np.pi)               # area-true circles drawn in data units
gap = 0.28 * r.max()
x = r[0] + np.r_[0, np.cumsum(r[:-1] + r[1:] + gap)]
fig = go.Figure()
for xi, ri, row in zip(x, r, df.itertuples()):
    fill = C.focus if row.function == focus else C.context
    fig.add_shape(type="circle", x0=xi - ri, x1=xi + ri, y0=0, y1=2 * ri, fillcolor=fill, line_width=0)
    inside = ri > 0.4 * r.max()
    fig.add_annotation(x=xi, y=ri if inside else -3, yanchor="middle" if inside else "top", showarrow=False,
                       text=f"<b>{row.hours_k:,}</b><br>{row.function}",
                       font={"color": mv.text_on(fill) if inside else C.headline})
fig.add_scatter(x=x, y=r, mode="markers", marker={"size": 1, "opacity": 0}, showlegend=False,   # hover targets
                customdata=df[["function", "hours_k"]],
                hovertemplate="%{customdata[0]}: %{customdata[1]:,}K hours<extra></extra>")
fig.update_xaxes(visible=False, range=[-gap, x[-1] + r[-1] + gap])
fig.update_yaxes(visible=False, range=[-30, 2 * r.max() + 4], scaleanchor="x", scaleratio=1)   # equal aspect
fig.update_layout(showlegend=False)
mv.pl_finish(fig, "Distribution holds 1.6x the automatable work hours of all other functions combined",
             "Task hours automatable with current technology, by function, FY26 (thousand hours per year)",
             "Source: Synthetic data for illustration only")
Path("out").mkdir(exist_ok=True)
fig.write_html("out/bubble.html", include_plotlyjs="cdn")
```
If you use `go.Scatter` markers instead of shapes, set `marker.sizemode="area"` and `sizeref = 2 * max(values) / max_px**2`. Marker sizes are in pixels, so leave generous spacing to avoid overlaps.

### Excel and PowerPoint
**PowerPoint shapes (most precise for ≤ 12 bubbles):**
1. Apply the **McKesson Data Viz** theme colors and fonts (Libre Franklin) from `dist/office/` (see [bar.md](bar.md#excel-and-powerpoint)).
2. In Excel, compute each diameter from the **area** rule: `=ROUND(3 * SQRT(B2 / MAX($B$2:$B$8)), 2)`. That gives inches, with the largest bubble 3 in across. A 4× value gets a 2× diameter.
3. In PowerPoint, **Insert › Shapes › Oval**. In **Format Shape › Size**, type the computed value into both **Height** and **Width**. Set **Fill: Solid** `B4B0A5` (headline bubble `005A8C`), **Line: No line**, and no shadow or 3D effects.
4. Select all the bubbles, then use **Shape Format › Align › Align Bottom** (shared baseline) and **Distribute Horizontally**. Order them largest to smallest.
5. Type the label into big bubbles: value **Bold** 14 pt and name Regular 11 pt, white on blue and navy on grey. For small bubbles, put a text box below and **Align Top** all the below-labels.
6. **Group** (Ctrl+G) and tick **Size › Lock aspect ratio** so any resize keeps the areas proportional. Headline in the title placeholder; footnote and source at 9 pt Libre Franklin Light, bottom-left.

**Excel bubble chart (data-driven):**
1. Set up the columns X (position), Y (0) and Size (value). Then use **Insert › Charts › Scatter › Bubble**.
2. **Format Data Series › Series Options › Size represents: Area of bubbles** (not Width). Adjust **Scale bubble size to** (e.g., 60–120%) until no bubbles overlap.
3. Fix the axis bounds, then delete both axes, the gridlines and the legend. Set individual point fills (grey, plus `005A8C` for the focus).
4. **Data Labels › Value From Cells** (names) + **Bubble Size**, **Position: Center** for big bubbles and **Below** for small ones.

### Power BI
- Apply [`dist/powerbi/mckesson-dataviz-theme.json`](../../dist/powerbi/mckesson-dataviz-theme.json).
- There is no native packed-bubble visual. Use the certified **Deneb** visual: a Vega-Lite `circle` mark, where the `size` channel is area-scaled, laid out on a single row with `x` from a running-position calculation. Or use a Vega spec with the `pack` transform for a packed cluster.
- If you use the native **Scatter chart** with a *Size* field, verify the area scaling with a known pair: a 4:1 value pair should show a 2:1 diameter. Hide both axes and gridlines, and turn on **Category labels**.
- Highlight with conditional color (**fx**) on a color measure. Keep data labels on; there is no size legend.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr); library(packcircles)
source("dist/r/theme_mck.R")

df <- tibble(fn = c("Distribution", "Customer Care", "Pharmacy Ops", "Finance Ops", "HR Ops", "Sales", "Legal"),
             hours_k = c(9800, 2900, 2300, 640, 310, 120, 45)) |>
  arrange(desc(hours_k))
layout <- circleProgressiveLayout(df$hours_k, sizetype = "area")      # area-true packing
df <- bind_cols(df, layout) |>
  mutate(fill = ifelse(fn == "Distribution", mck_colors$focus, mck_colors$context),
         ink  = ifelse(fn == "Distribution", "white", mck_colors$headline))
verts <- circleLayoutVertices(layout, npoints = 80)
verts$fill <- df$fill[verts$id]

ggplot() +
  geom_polygon(data = verts, aes(x, y, group = id, fill = fill), color = "white", linewidth = 0.6) +
  geom_text(data = filter(df, radius > 0.35 * max(radius)),
            aes(x, y, label = paste0(scales::comma(hours_k), "\n", fn), color = ink), size = 3.4, lineheight = 0.9) +
  scale_fill_identity() + scale_color_identity() +
  coord_equal() +
  labs(title = "Distribution holds 1.6x the automatable work hours of all other functions combined",
       subtitle = "Task hours automatable with current technology, by function, FY26 (thousand hours per year)",
       caption = "Small bubbles: Finance Ops 640, HR Ops 310, Sales 120, Legal 45.\nSource: Synthetic data for illustration only") +
  theme_mck() +
  theme(axis.text = element_blank(), axis.title = element_blank(), axis.line.x = element_blank(),
        panel.grid = element_blank())
```

## QA specifics
- [ ] **Area**, not diameter, is proportional to value. Check one pair: a 4:1 value ratio shows a 2:1 diameter ratio.
- [ ] The range justifies bubbles (max/min ≥ ~20×); otherwise the chart is redrawn as bars.
- [ ] Bubbles are sorted largest → smallest, don't overlap, and stay circular (equal aspect ratio).
- [ ] Every bubble has a value label (inside if it fits, otherwise below on one aligned line); there are no axes, gridlines or size legend.
- [ ] Color is one hue, or grey plus ≤ 2 highlights tied to the headline. Multiple colors only encode a keyed grouping.
- [ ] The headline's comparison ("more than all others combined", "34x") is recomputed from the data.

## Inspiration
- [p032 — Bubble chart](../../reference/inspiration-mckinsey/pages/p032-bubble-chart.md)
- [p033 — Bubble chart best practice](../../reference/inspiration-mckinsey/pages/p033-bubble-chart-best-practice.md)
