# Stacked area chart

> **Question type:** Part-to-whole (change over time)
> **Use for:** how a total and its 2–5 parts change over time · **Avoid when:** you need to compare the middle segments' own trends precisely (→ use a [line chart](line.md) or [small multiples](small-multiples.md))

## When to use
- The story covers the **total and its composition**: workforce by role family, labor hours by worker type, skills mix in postings.
- One segment's growth or decline is the message and you can put that segment **on the baseline**.
- There are enough periods (about 6 or more) for a continuous trend. With fewer periods, use stacked columns.
- **100% stacked area**: use it when share matters more than size, for example the share of a pharmacist's week spent on clinical services.

## When not to use
- Series that don't add up to a meaningful total (rates, scores, averages) → use a [line chart](line.md).
- Overlapping, unstacked areas → use a [line chart](line.md). Front areas hide the ones behind them.
- You need to read each segment's trend exactly. Only the bottom band sits on a flat baseline → use [small multiples](small-multiples.md) or lines.
- A few discrete periods or a single bridge between two totals → use a [100% stacked bar](stacked-bar.md) or a [waterfall](waterfall.md).
- More than 5 segments → group the tail into "Other", or use a [treemap](treemap.md) for a single point in time.

## McKesson spec

| Element | Rule |
|---|---|
| Color | **Highlight mode (default):** put the focus segment in `chart.focus` `#005A8C` on the baseline and stepped greys above it: `chart.context` `#B4B0A5`, then `chart.context_light` `#DEDBD1`, then `surface.subtle` `#EFEDE7`. An optional total line goes in `chart.total` `#143359` at 1.25 px. **Categorical mode:** use it only when every segment matters. Assign colors bottom-up in the fixed order `#005A8C`, `#143359`, `#66C4FF`, `#00AF9D`, `#00737A` and never in random order, because neighboring similar hues blur together. **Ordered categories** (tenure bands, job levels) use the sequential blue ramp `#E6F3FB` → `#143359`, darkest at the base. |
| Labels | Label each band directly at its right end, vertically centered on the band and in stack order. The focus label is bold `#005A8C` with its value and share; other labels use `text.muted` `#737373`. Label the total at the top of the stack. If bands are too thin to label, place a key at the top-left listed top-to-bottom in the same order as the stack. |
| Axes / gridlines | The y-axis **always starts at 0**. Put round ticks on the y-axis (or label values directly) and the unit in the subtitle. Gridlines are optional and stay behind the fills. Use straight segments between periods with no smoothing. Separate bands with 0.75 px white lines. Use a short `chart.annotation` `#143359` rule above the plot, with a bold 2–5 word title, to mark an insight period. Only use a shaded band if it doesn't hide the fills. |
| Sort / order | Put the focus segment on the baseline, then stack from **most stable to most volatile** going up. A volatile series at the bottom makes every band above it jagged. Keep the same stack order and colors across the deck. |
| Proportions | Use a wide 16:9 plot with about 20% of the width on the right for band labels. Don't draw outlines except the white separators. |
| Limits | ≤ 5 segments (`limits.stacked_segments`). Group the rest into "Other" in context grey. Use at least ~6 periods. Suppress any segment with n < 10 people. |

## Do / don't

| Do | Don't |
|---|---|
| Stack the segments, or switch to lines | Overlap semi-transparent areas so the front series hides the rest |
| Color stacks in the fixed palette order (or blue + greys) | Assign colors at random so similar hues end up side by side |
| Put the most stable categories at the bottom and the volatile ones on top | Put a spiky series on the baseline so every layer above it wiggles |
| Put the segment the headline is about on the baseline, in blue | Bury the focus segment in the middle of the stack |
| Label bands at their right end | Put a legend far from the data or in a different order from the stack |
| Mark insight periods with a short rule and a callout above the plot | Paint saturated bands over the fills or add callouts for every year |
| Size it for a 2-of-3 column "editorial" slot in reports | Squeeze a 5-band stacked area into a single narrow column |

## Workforce examples
- **Headline:** "Automation technicians grew from 3% to 14% of the DC workforce while total headcount held near 12K" — *Subtitle:* "Distribution-center workforce by role family, 2019–2026 (thousand FTE)" — data: firm-level workforce transformation, Workday HCM year-end snapshots by role family (snippet below).
- **Headline:** "Clinical services rose from 12% to 31% of a typical retail pharmacist's week as central fill absorbed dispensing" — *Subtitle:* "Share of pharmacist hours by activity, FY22–FY26 (%, 100% stacked)" — data: individual-level work sampling and task-time studies, aggregated to the role (≥ 10 pharmacists per period). It informs role redesign and SWP capacity.
- **Headline:** "Data and gen AI skills now make up 18% of skills requested in sector job postings, up from 6% in 2020" — *Subtitle:* "Skills requested in U.S. healthcare-distribution job postings by skill cluster, 2020–2026 (%, 100% stacked)" — data: sector-level external job-postings feed. The data and AI cluster sits on the baseline in blue; the other four clusters are grey.

## Build it

### Python — matplotlib + `mckviz`
```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import mckviz as mv

mv.use()
C = mv.colors

years = np.arange(2019, 2027)
# Distribution-center workforce by role family (thousand FTE). Stack order: focus on the baseline, most volatile on top.
stack = [
    ("Automation technicians", [0.35, 0.45, 0.60, 0.80, 1.00, 1.25, 1.45, 1.65], C.focus),
    ("Leads & supervisors",    [1.10, 1.10, 1.15, 1.15, 1.10, 1.10, 1.05, 1.05], C.context),
    ("Inventory & quality",    [1.60, 1.60, 1.65, 1.60, 1.60, 1.55, 1.55, 1.50], C.context_light),
    ("Material handlers",      [8.60, 8.90, 9.30, 8.70, 8.50, 8.30, 8.10, 7.90], C.surface_subtle),
]
values = np.array([v for _, v, _ in stack])
total = values.sum(axis=0)

fig, ax = plt.subplots(figsize=(10, 5.6))
ax.stackplot(years, values, colors=[c for *_, c in stack], edgecolor="white", linewidth=0.75)
ax.plot(years, total, color=C.total, lw=1.25)
tops = values.cumsum(axis=0)[:, -1]
for (name, v, col), top in zip(stack, tops):
    hi = col == C.focus
    ax.annotate(f"{name}  {v[-1]:.2f}K ({v[-1] / total[-1]:.0%})" if hi else name, (years[-1], top - v[-1] / 2),
                xytext=(8, 0), textcoords="offset points", va="center", fontsize=11 if hi else 10,
                fontweight="bold" if hi else "normal", color=C.focus if hi else C.text_muted, annotation_clip=False)
ax.annotate(f"Total {total[-1]:.1f}K", (years[-1], total[-1]), xytext=(8, 0), textcoords="offset points", va="center",
            fontsize=10, fontweight="bold", color=C.total, annotation_clip=False)
ax.plot([2021.5, 2024], [1.0, 1.0], color=C.annotation, lw=1.5, transform=ax.get_xaxis_transform(), clip_on=False)
ax.text(2021.5, 1.03, "Robotic picking rolls out to 14 DCs", transform=ax.get_xaxis_transform(), fontsize=10,
        fontweight="bold", color=C.annotation, va="bottom")

mv.clean_axes(ax, grid=None)
ax.set_xlim(years[0], years[-1])
ax.set_ylim(0, 13.5)
ax.set_yticks([0, 4, 8, 12])
ax.set_xticks(years, [f"'{y % 100:02d}" if y > years[0] else str(y) for y in years])
mv.titles(fig, f"Automation technicians grew from {values[0, 0] / total[0]:.0%} to {values[0, -1] / total[-1]:.0%} "
               "of the DC workforce while total headcount held near 12K",
          "Distribution-center workforce by role family, 2019\u20132026 (thousand FTE)")
mv.source(fig, "Source: Workday HCM, year-end snapshots; U.S. distribution centers. Synthetic data for illustration")
mv.save(fig, "out/stacked-area.png")
```
For a **100% stacked area**, divide each column by `total` before `stackplot`, set `ax.set_ylim(0, 1)` and label shares instead of FTE.

### Python — Plotly / HTML
```python
import plotly.graph_objects as go

import mckviz as mv

mv.use()
C = mv.colors
years = list(range(2019, 2027))
stack = [  # bottom -> top
    ("Automation technicians", [0.35, 0.45, 0.60, 0.80, 1.00, 1.25, 1.45, 1.65], C.focus),
    ("Leads & supervisors",    [1.10, 1.10, 1.15, 1.15, 1.10, 1.10, 1.05, 1.05], C.context),
    ("Inventory & quality",    [1.60, 1.60, 1.65, 1.60, 1.60, 1.55, 1.55, 1.50], C.context_light),
    ("Material handlers",      [8.60, 8.90, 9.30, 8.70, 8.50, 8.30, 8.10, 7.90], C.surface_subtle),
]
fig = go.Figure()
running = 0
for name, v, col in stack:
    fig.add_scatter(x=years, y=v, name=name, stackgroup="dc", mode="lines", fillcolor=col,
                    line={"color": "white", "width": 0.75}, hovertemplate="%{y:.2f}K FTE<extra>" + name + "</extra>")
    running += v[-1]
    fig.add_annotation(x=years[-1], y=running - v[-1] / 2, text=f"<b>{name}</b>" if col == C.focus else name,
                       xanchor="left", xshift=8, showarrow=False, font={"color": C.focus if col == C.focus else C.text_muted})
fig.add_vrect(x0=2021.5, x1=2024, fillcolor="white", opacity=0, line_width=0,
              annotation_text="<b>Robotic picking rolls out to 14 DCs</b>", annotation_position="top left")
fig.update_layout(showlegend=False, hovermode="x unified", margin={"r": 190})
fig.update_yaxes(range=[0, 13.5], dtick=4)
fig.update_xaxes(dtick=1)
mv.pl_finish(fig, "Automation technicians grew from 3% to 14% of the DC workforce while total headcount held near 12K",
             "Distribution-center workforce by role family, 2019\u20132026 (thousand FTE)",
             source_text="Source: Workday HCM, year-end snapshots; U.S. distribution centers")
fig.show()
```
Plotly stacks traces in the order you add them, so add the focus trace first to put it on the baseline. Add `groupnorm="percent"` on the first trace for the 100% variant.

### Excel and PowerPoint
1. **Theme:** copy the `dist/office` color and font XMLs into `%APPDATA%\Microsoft\Templates\Document Themes\Theme Colors\` and `...\Theme Fonts\`. Then apply **Page Layout → Colors / Fonts → McKesson Data Viz** in Excel, or **Design → Variants ▾ → Colors / Fonts** in PowerPoint. Install Libre Franklin.
2. Put years in the first column and one column per segment, with the **focus segment first** and the most volatile last. Click **Insert → Insert Line or Area Chart → 2-D Area → Stacked Area** (or **100% Stacked Area**).
3. If the order is wrong, use **Chart Design → Select Data → Legend Entries** and the ▲/▼ arrows so the focus series is first, which puts it on the bottom.
4. Fill each series with **Ctrl+1 → Fill & Line → Fill → Solid fill**. The focus series gets **Accent 1 `#005A8C`**; the others get **More Colors → Hex** `B4B0A5`, `DEDBD1`, `EFEDE7`. For every series set **Border → Solid line, White, 0.75 pt**.
5. **Total line:** add a `Total` column → **Change Chart Type → Combo →** Total = **Line**, `#143359`, 1.25 pt, **Marker: None**.
6. Delete the legend and the chart title. Excel can't place area labels at the band end, so in PowerPoint add text boxes aligned to the right edge of each band: Libre Franklin 11 pt, bold `#005A8C` for the focus band and `#737373` for the others.
7. Axes: set **Vertical axis → Bounds Minimum = 0** (fixed). Set gridlines to `#E6E4DE` 0.75 pt or remove them, and set the horizontal axis to **Tick Marks: None** with **Axis position: On tick marks**, so the area runs to the plot edges.
8. Mark an insight period with a short `#143359` line shape above the plot and a bold 2–5 word label.
9. Paste with **Use Destination Theme & Embed Workbook**. Put the headline in the slide title, the subtitle at 14 pt `#505050` and the source at 9 pt `#737373`, bottom-left.

### Power BI
- Apply the theme: **View → Themes → Browse for themes →** `dist/powerbi/mckesson-dataviz-theme.json`.
- Build a **Stacked area chart** with X = year (continuous), Y = FTE measure and Legend = role family. Control the stack order with a sort column (**Column tools → Sort by column**) so the focus segment comes first.
- In **Format → Colors**, set the focus segment to `#005A8C` and the rest to the greys `#B4B0A5`, `#DEDBD1`, `#EFEDE7`. Turn the legend off, turn **Series labels** on, and set **Total labels** to show the stack total. Use the **100% stacked area chart** visual for shares.
- Use **Analytics → X-axis constant line → Shade area** for a period of interest, kept light.
- Blank segments below the minimum n: `FTE (safe) = IF([Headcount] < 10, BLANK(), [FTE])`.

### R — ggplot2 (optional)
```r
library(ggplot2)
source("dist/r/theme_mck.R")

# Synthetic data for illustration (replace with yours): DC workforce by role family, thousand FTE
total <- c(11.9, 12.1, 12.0, 12.2, 12.1, 11.9, 12.0, 12.1)                     # 2019-2026, held near 12K
auto  <- total * seq(0.03, 0.14, length.out = 8)                                # automation share 3% -> 14%
rest  <- total - auto
df <- data.frame(year = rep(2019:2026, 4),
                 role = rep(c("Material handlers", "Inventory & quality", "Leads & supervisors", "Automation technicians"),
                            each = 8),
                 fte = c(rest * 0.60, rest * 0.22, rest * 0.18, auto))

# ggplot stacks the FIRST factor level on top, so list the focus segment last.
df$role <- factor(df$role, levels = c("Material handlers", "Inventory & quality", "Leads & supervisors", "Automation technicians"))
ggplot(df, aes(year, fte, fill = role)) +
  geom_area(colour = "white", linewidth = 0.3) +
  scale_fill_manual(values = c("Material handlers" = "#EFEDE7", "Inventory & quality" = mck_colors$context_light,
                               "Leads & supervisors" = mck_colors$context, "Automation technicians" = mck_colors$focus),
                    guide = "none") +
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.05))) +
  scale_x_continuous(expand = c(0, 0)) +
  theme_mck() +
  labs(x = NULL, y = NULL,
       title = "Automation technicians grew from 3% to 14% of the DC workforce while total headcount held near 12K",
       subtitle = "Distribution-center workforce by role family, 2019–2026 (thousand FTE)",
       caption = "Source: Workday HCM, year-end snapshots; U.S. distribution centers")
```

## QA specifics
- [ ] The y-axis starts at 0 and the segments add up to a real total (or to 100% in the 100% variant).
- [ ] The segment the headline is about sits on the baseline. Stable segments sit below volatile ones.
- [ ] There are ≤ 5 segments, colored blue + greys or in the fixed categorical order bottom-up (never random), with white separators.
- [ ] Each band is labelled at its right end (or the key matches the stack order top-to-bottom), and the focus label shows the value and share.
- [ ] Areas are stacked, never overlapping. There's no smoothing and the periods are evenly spaced.
- [ ] Any insight-period marker spans the correct dates and doesn't hide the fills.

## Inspiration
- [p045 — Stacked area chart](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p045-stacked-area-chart.md)
- [p046 — Stacked area chart best practice](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p046-stacked-area-chart-best-practice.md)
- [p085 — Print](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p085-print.md)
