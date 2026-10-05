# Small multiples

> **Question type:** Change over time (also Magnitude and Part-to-whole across many groups)
> **Use for:** the same chart repeated for each group on a shared scale, with each panel's own group highlighted against grey context · **Avoid when:** one or two series carry the whole story (→ use a single [line chart](line.md) with a highlight)

## When to use
- You'd otherwise draw **more than ~4 lines** on one chart, and readers need each group's own trend (business units, regions, job families, sites).
- The story is **"which group behaves differently?"**: one panel breaks the common pattern.
- You want each group read **in context**. Draw every other group faintly behind each panel's own series.
- **Matrix of pies, donuts or dials**: when each entity needs a share (and possibly a size), repeat one ring per entity on a common 0–100% scale. For example, ready-now successor rate by critical role.
- Dashboards and reports where the reader scans a grid of comparable panels.

## When not to use
- One focus series against context → use a single [line chart](line.md) with grey context lines.
- The groups need precise comparison at one point in time → use a [sorted bar](bar.md).
- The groups have very different magnitudes and a shared scale would flatten the small ones. Index each group to 100, or use independent scales and label that loudly.
- More than ~12 panels on a slide → use a [heatmap](heatmap.md) (groups × periods) or show only the top/bottom panels.

## McKesson spec

| Element | Rule |
|---|---|
| Color | In each panel, that panel's series is `chart.focus` `#005A8C`. All other groups are drawn behind it in `chart.context_light` `#DEDBD1`, lighter than `#B4B0A5` because there are many of them. The single panel the headline is about uses `chart.accent` navy `#143359`, or `semantic.negative` orange `#EF8200` when that panel is the one getting worse (as in the example below). A benchmark or enterprise line is `chart.total` `#143359`, thin and dashed, in **every** panel. Ring or dial matrices use `#005A8C` for the value arc, a `#EFEDE7` track and navy `#143359` for the exception (orange `#EF8200` only if it is below target). |
| Labels | Panel titles are left-aligned and sentence case at 11 pt. The accent panel's title is bold `#143359`. Label the end value of each panel's own series (start value optional) in the series color (an orange panel uses `#A75B00` text). No legend: the panel title names the series. If there's a benchmark, label it once, in the first panel only. |
| Axes / gridlines | Use the **same x and y scale in every panel** (`sharex=True, sharey=True`). Show y tick labels only on the left column and x tick labels only on the bottom row. Keep 2–3 gridlines in `chart.grid` `#E6E4DE`. Use sparse time ticks: the first period and each year change. |
| Sort / order | When explaining, put the focus panel first (top-left), then sort by the measure (latest value or change). Use a natural order (region, level) or alphabetical order for look-up grids. Keep the panel order identical across the deck. |
| Proportions | Use 2×2, 2×3, 3×3 or 3×4 grids with panels of equal size and aspect. Keep the gutters at ~15–20% of panel width and each panel at least ~1.5 in wide on slides. Line weights follow `chart.line`: own series 2.25 pt / 2 px, context 1.25 px. |
| Limits | Live slides take ≤ 6 panels; reports and dashboards ≤ 12, or ≤ 20 for look-up grids. Each panel follows its base chart's limits (≤ 2 highlights, ≤ 5 ring segments). Suppress or merge any panel with n < 10 and footnote it. |

## Do / don't

| Do | Don't |
|---|---|
| Put every panel on one scale, so differences in height mean differences in value | Let each panel autoscale. A flat line and a steep line can then mean the same change |
| Draw the other groups faintly behind each panel's own series | Show each panel in isolation, so the reader can't tell whether the group is high or low |
| Highlight the one exception panel (navy, or orange if it is worse) and say why in the headline | Use a different hue for every panel. Position already identifies the group |
| Sort panels with intent and put the focus panel first | Default to database order |
| Repeat rings or dials on a common 0–100% track, one value each | Mix pies of different totals with unlabeled slices |
| Label the end value inside each panel | Add a shared legend far below the grid |
| Drop to a heatmap when there are more than ~12 panels | Shrink 30 panels until the text falls below 9 pt |

## Workforce examples
- **Headline:** "Oncology is the only business unit where regretted attrition rose over the past two years, up 4 points" — *Subtitle:* "Regretted attrition by business unit, trailing 12 months, Q1 2025–Q4 2026 (%)" — data: firm/BU-level Workday HCM exits ÷ average headcount (snippet below). The Oncology panel is orange, because rising attrition is worse.
- **Headline:** "Market pay for warehouse associates grew faster than ours in 4 of 6 hub metros" — *Subtitle:* "Median hourly pay, warehouse associates, McKesson vs. external market, by metro, 2023–2026 ($/hr)" — data: sector-level external posted-pay feed vs. internal payroll. McKesson is blue, the market is navy `#143359` dashed, and the 4 lagging metros have bold titles.
- **Headline:** "New pharmacists on the mentored path reach full productivity ~5 weeks sooner in every region" — *Subtitle:* "Productivity index of new-hire pharmacists by week since start, by region (100 = tenured median)" — data: individual-level productivity ramps aggregated by onboarding path and region (n ≥ 10 per panel). The mentored path is blue and the standard path grey.

## Build it

### Python — matplotlib + `mckviz`
```python
# verified runnable (from the repo root)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mckviz as mv

mv.use()

quarters = ["Q1 '25", "Q2", "Q3", "Q4", "Q1 '26", "Q2", "Q3", "Q4"]
# Regretted attrition, trailing 12 months (%), by business unit
bu = {
    "Oncology & Multispecialty": [9.0, 9.4, 9.9, 10.6, 11.2, 11.9, 12.4, 13.1],
    "U.S. Pharmaceutical":       [12.5, 12.3, 12.6, 12.0, 11.8, 11.5, 11.6, 11.2],
    "Medical-Surgical":          [10.5, 10.2, 10.4, 9.9, 9.6, 9.4, 9.5, 9.1],
    "Technology":                [11.8, 11.2, 10.9, 10.1, 9.8, 9.6, 9.2, 9.0],
    "Corporate":                 [8.2, 8.0, 7.9, 7.7, 7.6, 7.4, 7.3, 7.1],
    "RxTS":                      [7.5, 7.4, 7.6, 7.2, 7.0, 7.1, 6.8, 6.7],
}
fig = plt.figure(figsize=(10, 6))
# One shared scale; panels ordered by the latest value; every other unit as grey context behind each panel's own
# blue line; start and end values labelled; attrition rose in Oncology, so its line is orange (worse).
sm = mv.multiples(fig, bu, x=quarters, ncols=3, worse={"Oncology & Multispecialty"},
                  ylim=(5, 15), yticks=[5, 10, 15], xticks=[0, 4])   # lines need no zero baseline
mv.titles(fig, "Oncology is the only business unit where regretted attrition rose over the past two years, up 4 points",
          "Regretted attrition by business unit, trailing 12 months, Q1 2025\u2013Q4 2026 (%)")
mv.source(fig, "Source: Workday HCM, as of 31 Dec 2026; U.S. regular employees. Synthetic data for illustration",
          footnote="Regretted = voluntary exits of high performers or critical-skill roles. Cuts with < 10 exits per quarter are suppressed.")
mv.lint(fig, strict=True)
mv.save(fig, "out/small-multiples.png")
```
`mv.titles()` and `mv.save()` align the headline and source to the left edge of the leftmost panel's labels automatically. `mv.multiples` also takes a DataFrame (one column per panel, the index as x); `sm.axes` are the panels in order, for callouts.

### Python — Plotly / HTML
```python
# verified: builds without error
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import mckviz as mv

mv.use()
C = mv.colors
quarters = ["Q1 '25", "Q2 '25", "Q3 '25", "Q4 '25", "Q1 '26", "Q2 '26", "Q3 '26", "Q4 '26"]
bu = {
    "Oncology & Multispecialty": [9.0, 9.4, 9.9, 10.6, 11.2, 11.9, 12.4, 13.1],
    "U.S. Pharmaceutical":       [12.5, 12.3, 12.6, 12.0, 11.8, 11.5, 11.6, 11.2],
    "Medical-Surgical":          [10.5, 10.2, 10.4, 9.9, 9.6, 9.4, 9.5, 9.1],
    "Technology":                [11.8, 11.2, 10.9, 10.1, 9.8, 9.6, 9.2, 9.0],
    "Corporate":                 [8.2, 8.0, 7.9, 7.7, 7.6, 7.4, 7.3, 7.1],
    "RxTS":                      [7.5, 7.4, 7.6, 7.2, 7.0, 7.1, 6.8, 6.7],
}
accent = "Oncology & Multispecialty"
fig = make_subplots(rows=2, cols=3, shared_xaxes=True, shared_yaxes=True, subplot_titles=list(bu),
                    horizontal_spacing=0.05, vertical_spacing=0.16)
for i, (name, y) in enumerate(bu.items()):
    row, col = i // 3 + 1, i % 3 + 1
    for other, oy in bu.items():
        if other != name:
            fig.add_scatter(x=quarters, y=oy, mode="lines", line={"color": C.context_light, "width": 1.25},
                            hoverinfo="skip", row=row, col=col)
    color = C.negative if name == accent else C.focus        # attrition rose: orange means worse
    fig.add_scatter(x=quarters, y=y, mode="lines", line={"color": color, "width": 2.5},
                    hovertemplate=name + "<br>%{x}: %{y:.1f}%<extra></extra>", row=row, col=col)
for ann in fig.layout.annotations:                         # left-align panel titles; bold the exception panel
    ann.update(x=ann.x - 0.145, xanchor="left", font={"size": 13, "color": C.headline if ann.text == accent else C.text},
               text=f"<b>{ann.text}</b>" if ann.text == accent else ann.text)
fig.update_yaxes(range=[5, 15], dtick=5)
fig.update_xaxes(tickvals=["Q1 '25", "Q1 '26"])
fig.update_layout(showlegend=False, height=520)
mv.pl_finish(fig, "Oncology is the only business unit where regretted attrition rose over the past two years",
             "Regretted attrition by business unit, trailing 12 months, Q1 2025\u2013Q4 2026 (%)",
             source_text="Source: Workday HCM, as of 31 Dec 2026; U.S. regular employees",
             footnote="Cuts with < 10 exits per quarter are suppressed.")
fig.show()
```
`px.line(..., facet_col="bu", facet_col_wrap=3)` is quicker for exploration, but it can't draw the grey context of the other groups in each panel. Use the loop above for explanatory charts. On mobile, re-flow the grid to one column.

### Excel and PowerPoint
1. **Theme:** install the `office` color and font XMLs and Libre Franklin, then apply **Page Layout → Colors / Fonts → McKesson Data Viz** in Excel, or **Design → Variants ▾ → Colors / Fonts** in PowerPoint.
2. Build **one** panel completely first: **Insert → Insert Line or Area Chart → 2-D Line → Line**, with all groups as series. Set every series to **Hex `DEDBD1`, 1 pt** and the panel's own group to **Accent 1 `#005A8C`, 2.25 pt**. Set **Marker: None**, delete the legend, and replace the chart title with the group name (Libre Franklin 11 pt, left-aligned).
3. **Fix the scale:** **Vertical axis → Format Axis → Bounds Minimum / Maximum** to fixed values (e.g. 5 and 15) and **Major unit** to 5. Never leave the bounds on Auto. This is what makes the panels comparable.
4. Add an end-value data label to the own series' **last point** (**Add Data Label → Value, Position: Right**, bold, in the series color).
5. Copy the chart (**Ctrl+C / Ctrl+V**) for each group. In each copy, recolor the panel's own series to blue and set the previous one back to grey (**Ctrl+1**, or **F4** to repeat), then change the title. The exception panel uses **Accent 6 `#EF8200`** here, because its attrition rose (use **Accent 2 `#143359`** navy for an exception that isn't worse), with a bold `#143359` title.
6. Remove the y tick labels from inner columns (**Format Axis → Labels → Label Position: None**) and the x labels from upper rows.
7. Paste all panels into PowerPoint (**Use Destination Theme & Embed Workbook**), select them and use **Shape Format → Align → Align Top / Distribute Horizontally**, then **Group**. Give every panel the same size under **Shape Format → Size**.
8. Put the headline in the slide title. Add one subtitle (metric, unit, period) and one source line for the whole grid.

### Power BI
- Apply the theme `assets/powerbi/mckesson-dataviz-theme.json`.
- In a line, column or area chart, drag the group to the **Small multiples** well. Set **Format → Small multiples → Layout** (rows × columns) and keep the **Y-axis shared**: leave "Independent" scale off.
- Small multiples show only each panel's own data. To add context, add a measure that ignores the panel filter and format it grey (`#DEDBD1`) or as the navy benchmark: `Enterprise rate = CALCULATE([Regretted attrition %], REMOVEFILTERS(BU[BU]))`.
- Color the exception panel with a field-value rule (**Format → Lines → Color → fx**) driven by an `IsFocus` measure.
- Suppress small panels: `Regretted % (safe) = IF([Exits] < 10, BLANK(), [Regretted attrition %])`, and footnote the suppression in a text box.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr)
source("assets/r/theme_mck.R")

# Synthetic data for illustration (replace with yours): regretted attrition by BU, Q1 2025 (1) to Q4 2026 (8)
start <- c("Corporate" = 9, "Medical-Surgical" = 11, "Oncology & Multispecialty" = 8, "RxTS" = 10,
           "Technology" = 12, "U.S. Pharmaceutical" = 10)
df <- expand.grid(quarter = 1:8, bu = names(start), stringsAsFactors = FALSE) |>
  mutate(rate = ifelse(bu == "Oncology & Multispecialty", start[bu] + (quarter - 1) * 4 / 7,   # up 4 points
                       start[bu] - (quarter - 1) * 0.15))

# A copy without the facet column draws in every panel as context.
bg <- rename(df, other = bu)
accent <- "Oncology & Multispecialty"
df$bu <- factor(df$bu, levels = df |> filter(quarter == max(quarter)) |> arrange(desc(rate)) |> pull(bu))
ggplot(df, aes(quarter, rate)) +
  geom_line(data = bg, aes(group = other), colour = mck_colors$context_light, linewidth = 0.45) +
  geom_line(aes(colour = bu == accent), linewidth = 1.05) +
  scale_colour_manual(values = c(`TRUE` = mck_colors$negative, `FALSE` = mck_colors$focus), guide = "none") +
  facet_wrap(~bu, ncol = 3) +                              # fixed scales by default: keep it that way
  coord_cartesian(ylim = c(5, 15)) +
  theme_mck() + theme(strip.text = element_text(hjust = 0, size = 11, colour = mck_colors$text)) +
  labs(x = NULL, y = NULL,
       title = "Oncology is the only business unit where regretted attrition rose over the past two years, up 4 points",
       subtitle = "Regretted attrition by business unit, trailing 12 months, Q1 2025–Q4 2026 (%)",
       caption = "Source: Workday HCM, as of 31 Dec 2026; U.S. regular employees")
```

## QA specifics
- [ ] Every panel uses the same x and y scale. If not, the subtitle says "independent scales" and explains why.
- [ ] Each panel's own series is blue and the other groups are faint `#DEDBD1` context. At most one exception panel is highlighted (navy, or orange only if it is worse), and the headline names it.
- [ ] Panel titles are left-aligned and in a deliberate order (focus first, then by value or natural order), consistent across the deck.
- [ ] Tick labels appear only on the outer panels, with no per-panel legends and no text below 9 pt.
- [ ] The grid has ≤ 6 panels for live slides and ≤ 12 for reports, and every panel meets the minimum n (suppressed panels are footnoted).
- [ ] Ring and dial matrices share a 0–100% track, and each ring shows one value.

## Inspiration
- [p035 — Donut and pie chart variants (pie matrix, dials)](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p035-donut-and-pie-chart-variants.md)
- [p044 — Line chart best practice](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p044-line-chart-best-practice.md)
