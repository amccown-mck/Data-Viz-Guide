# Bubble timeline

> **Question type:** Change over time (events with magnitude)
> **Use for:** discrete events placed on a time axis, one row per category, with bubble area showing each event's size · **Avoid when:** the measure is continuous or there are dozens of events per row (→ use a [line chart](line.md), or a [heatmap](heatmap.md) of period totals)

## When to use
- Discrete **events** matter more than a continuous level: restructuring announcements, reskilling cohort launches, hiring events, site openings, system go-lives.
- You want to show both **when** events happened and **how big** they were, and compare across 3–8 categories (sub-sectors, business units, sites).
- The reader should be able to scan **across rows** (which category is most active) and **along one row** (how that category's pattern changed).
- It works well with **external signals**, such as peer layoffs and labor-market events, set alongside internal ones.

## When not to use
- A continuous measure sampled at even intervals (rates, headcount) → use a [line chart](line.md).
- Exact comparison of sizes matters. Area is hard to compare precisely → aggregate to periods and use a [bar](bar.md) or [heatmap](heatmap.md).
- Events with duration (vacancies, projects) → use a Gantt-style bar timeline.
- More than ~15 events in a row, so bubbles pile up → aggregate by month or quarter.
- Two numeric measures per item rather than time → use a [scatter / bubble scatter](scatter-bubble.md).

## McKesson spec

| Element | Rule |
|---|---|
| Color | Give every bubble **one color**, `chart.focus` `#005A8C`. Rows already separate the categories, so coloring by row is redundant. If the headline is about one row, that row is `#005A8C` and the others are `chart.context` `#B4B0A5`. Use `chart.accent` navy `#143359` for at most one single event that must pop. Mark the insight period with a `surface.subtle` `#EFEDE7` band behind the bubbles. |
| Labels | Put row labels on the left in sentence case, with the focus row bold `#143359`. Place a **size key** top-left under the subtitle: 2–3 reference circles at round values (e.g. 1,000 / 5,000 / 10,000) plus the unit. Label only the events the headline mentions (value + short name). Add a bold callout for the shaded period. |
| Axes / gridlines | Time runs on the x-axis at even intervals with year labels (`2020`, `'21`, `'22`, …) and no axis line. There's no y-axis; each row gets a thin guide line in `chart.grid` `#E6E4DE` at 0.75 px. No vertical gridlines. |
| Sort / order | Order rows naturally (org order, value chain) or by total magnitude, largest on top. Keep that order across the deck. **Draw the largest bubbles first** so the small ones sit on top, and give every bubble a 1 px white outline with 85–90% opacity so the overlapping edges stay visible. |
| Proportions | Bubble **area** is proportional to the value (matplotlib `s ∝ value`, Plotly `sizemode="area"`, R `scale_size_area()`). Keep the largest bubble's diameter at or below ~1.5× the row spacing and the smallest at ≥ ~4 px. Use a 16:9 frame with rows about 0.6–0.8 in apart. |
| Limits | 3–8 rows and ≤ ~15 events per row. Use one size scale for the whole chart and never rescale per row. For internal people events (exits, moves), don't plot any event that involves fewer than 10 people. |

## Do / don't

| Do | Don't |
|---|---|
| Use one color for all bubbles so the eye compares size and spots outliers | Give each row its own hue. It adds nothing, and pale tints fade into the background |
| Draw large bubbles behind small ones, with white outlines and slight transparency | Let a large bubble sit on top and hide the events behind it |
| Shade the period that supports the headline and add a short callout | Leave the reader to discover the pattern without a highlight |
| Scale bubble **area** to the value and show a size key | Scale diameter to the value. That exaggerates big events about 4× |
| Highlight the headline row in blue and grey the others | Color by an unrelated attribute such as region |
| Aggregate to months or quarters when events pile up | Plot hundreds of overlapping dots |

## Workforce examples
- **Headline:** "Pharma manufacturers have announced more job cuts since 2023 than any other healthcare sub-sector" — *Subtitle:* "Announced workforce reductions by healthcare sub-sector, 2020–2026; bubble area = roles affected" — data: sector-level external signal from public WARN notices and company announcements. Shows talent-market supply for SWP sourcing plans (snippet below).
- **Headline:** "Half of FY26 reskilling seats went to Customer Care, the workforce most exposed to gen AI" — *Subtitle:* "Reskilling cohort launches by business unit, FY24–FY26; bubble area = participants" — data: firm-level LMS cohort records joined to `assets/data/automation_exposure.csv`. Each bubble is one cohort and the Customer Care row is in focus blue.
- **Headline:** "Peak-season hiring now starts in August at every DC, six weeks earlier than in FY25" — *Subtitle:* "Hiring events by distribution center, FY25–FY26; bubble area = hires per event" — data: team/site-level requisitions and onboarding dates from Workday Recruiting. One row per DC, with the band shading Aug–Sep FY26.

## Build it

### Python — matplotlib + `mckviz`
```python
# verified runnable (from the repo root)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
C = mv.colors

# Announced workforce reductions by healthcare sub-sector (external signal): (row, date as decimal year, roles affected)
events = pd.DataFrame([
    ("Health systems", 2020.3, 12000), ("Health systems", 2020.6, 6000), ("Health systems", 2021.1, 2500),
    ("Health systems", 2022.8, 1500), ("Health systems", 2023.5, 3000), ("Health systems", 2024.9, 2000),
    ("Health systems", 2025.6, 1800),
    ("Payers", 2020.5, 1500), ("Payers", 2022.2, 1200), ("Payers", 2023.3, 2000), ("Payers", 2024.4, 4500),
    ("Payers", 2025.2, 1500),
    ("Pharma manufacturers", 2020.9, 1000), ("Pharma manufacturers", 2022.5, 1500), ("Pharma manufacturers", 2023.4, 5500),
    ("Pharma manufacturers", 2023.9, 4000), ("Pharma manufacturers", 2024.6, 6500), ("Pharma manufacturers", 2025.4, 3500),
    ("Pharma manufacturers", 2026.1, 2500),
    ("Distributors & PBMs", 2021.6, 800), ("Distributors & PBMs", 2023.1, 1200), ("Distributors & PBMs", 2024.2, 2200),
    ("Distributors & PBMs", 2025.7, 1000),
    ("Digital health", 2021.9, 300), ("Digital health", 2022.9, 2500), ("Digital health", 2023.2, 4200),
    ("Digital health", 2023.6, 3000), ("Digital health", 2024.1, 3800), ("Digital health", 2024.8, 1500),
    ("Digital health", 2025.5, 900),
], columns=["sector", "date", "roles"])
rows = ["Health systems", "Payers", "Pharma manufacturers", "Distributors & PBMs", "Digital health"]
focus = "Pharma manufacturers"
since_2023 = events[events.date >= 2023].groupby("sector").roles.sum()
AREA = 0.25                                               # marker area (pt^2) per role -> bubble AREA is proportional to value

fig, ax = plt.subplots(figsize=(10, 5.6))
ax.axvspan(2023, 2026.4, color=C.surface_subtle, lw=0, zorder=0)
ax.text(2023.05, -0.75, f"Since 2023: ~{since_2023[focus] / 1000:.0f}K roles in pharma vs. "
        f"~{since_2023.drop(focus).max() / 1000:.0f}K in {since_2023.drop(focus).idxmax().lower()}",
        fontsize=10, color=C.annotation, fontweight="bold", va="bottom")
for i, _ in enumerate(rows):
    ax.axhline(i, color=C.grid, lw=0.75, zorder=1)
ev = events.sort_values("roles", ascending=False)         # draw largest first so small bubbles stay visible on top
ax.scatter(ev.date, ev.sector.map(rows.index), s=ev.roles * AREA, c=mv.highlight(ev.sector, focus=focus),
           edgecolors="white", linewidths=1, alpha=0.9, zorder=2)
mv.size_key(ax, [1_000, 5_000, 10_000], AREA, title="Roles affected", side="left")   # above the plot, top left

ax.set_yticks(range(len(rows)), rows)
ax.set_ylim(len(rows) - 0.4, -0.9)
ax.set_xlim(2019.8, 2026.4)
ax.set_xticks(range(2020, 2027), ["2020"] + [f"'{y % 100}" for y in range(2021, 2027)])
mv.clean_axes(ax, keep=(), grid=None)
for lbl in ax.get_yticklabels():
    if lbl.get_text() == focus:
        lbl.set_fontweight("bold"); lbl.set_color(C.headline)
mv.titles(fig, "Pharma manufacturers have announced more job cuts since 2023 than any other healthcare sub-sector",
          "Announced workforce reductions by healthcare sub-sector, 2020\u20132026; bubble area = roles affected")
mv.source(fig, "Source: Public WARN notices and company announcements; U.S. only. Synthetic data for illustration",
          footnote="Each bubble is one announcement; multi-phase programs are counted at first announcement.")
mv.save(fig, "out/bubble-timeline.png")
```
For the plain single-color version (no focus row), replace `c=mv.highlight(...)` with `color=C.focus`.

### Python — Plotly / HTML
```python
# verified: builds without error
import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()
C = mv.colors
events = pd.DataFrame([  # abbreviated; use the full events table above
    ("Health systems", 2020.3, 12000), ("Health systems", 2020.6, 6000), ("Health systems", 2023.5, 3000),
    ("Payers", 2022.2, 1200), ("Payers", 2024.4, 4500),
    ("Pharma manufacturers", 2023.4, 5500), ("Pharma manufacturers", 2023.9, 4000), ("Pharma manufacturers", 2024.6, 6500),
    ("Digital health", 2023.2, 4200), ("Digital health", 2024.1, 3800),
], columns=["sector", "date", "roles"])
rows = ["Health systems", "Payers", "Pharma manufacturers", "Distributors & PBMs", "Digital health"]
focus = "Pharma manufacturers"
ev = events.sort_values("roles", ascending=False)          # largest first -> drawn underneath
fig = go.Figure(go.Scatter(
    x=ev.date, y=ev.sector, mode="markers",
    marker={"size": ev.roles, "sizemode": "area", "sizeref": 2 * 12000 / 56 ** 2, "opacity": 0.9,
            "color": mv.highlight(ev.sector, focus=focus), "line": {"color": "white", "width": 1}},
    hovertemplate="<b>%{y}</b><br>%{x:.1f}<br>%{marker.size:,} roles<extra></extra>"))
fig.add_vrect(x0=2023, x1=2026.4, fillcolor=C.surface_subtle, line_width=0, layer="below",
              annotation_text="<b>Since 2023: ~22K roles in pharma</b>", annotation_position="top left")
fig.update_yaxes(categoryorder="array", categoryarray=rows[::-1], showgrid=True, ticksuffix="  ")
fig.update_xaxes(range=[2019.8, 2026.4], dtick=1, showgrid=False)
fig.update_layout(showlegend=False)
mv.pl_finish(fig, "Pharma manufacturers have announced more job cuts since 2023 than any other healthcare sub-sector",
             "Announced workforce reductions by sub-sector, 2020\u20132026; bubble area = roles affected. Hover for detail.",
             source_text="Source: Public WARN notices and company announcements; U.S. only")
fig.show()
```
`sizeref = 2 * max_value / max_diameter_px**2` with `sizemode="area"` keeps area proportional to the value. The tooltip carries the exact number and the employer name when that's appropriate to share.

### Excel and PowerPoint
1. **Theme:** install the `assets/office` color and font XMLs and Libre Franklin, then apply **Page Layout → Colors / Fonts → McKesson Data Viz** in Excel, or **Design → Variants ▾ → Colors / Fonts** in PowerPoint.
2. Lay out the data as columns `Date` (Excel date or decimal year), `Row` (1 = top row, 2, 3, …) and `Size`, and **sort by Size, largest first**. Excel draws bubbles in data order, so the small ones end up on top.
3. Click **Insert → Insert Scatter (X, Y) or Bubble Chart → Bubble**. Under **Chart Design → Select Data**, set X = Date, Y = Row and bubble size = Size. Use one series for context rows and a second series for the focus row.
4. Press **Ctrl+1 → Series Options →** set **Size represents: Area of bubbles** (never Width) and **Scale bubble size to** ~50–80. Fill = **Accent 1 `#005A8C`** (context series: Hex `B4B0A5`) at **10% transparency**, **Border: Solid line, White, 0.75 pt**.
5. Vertical axis: set **Bounds** to 0.5 and n + 0.5, **Values in reverse order**, **Major unit 1** and **Labels → Label Position: None**. Set the major gridlines to `#E6E4DE` 0.75 pt; these are the row guides. Type the row names as text boxes aligned to the guides (bold `#143359` for the focus row).
6. Horizontal axis: set yearly bounds and units with **Tick Marks: None** and **Line: No line**. Delete the legend and the chart title.
7. **Size key:** add a third series with 3 points at round values in the top-left corner, filled `#B4B0A5`, and give it data labels showing the value.
8. **Shaded period:** in PowerPoint, set the chart area and plot area to **No fill** and place a `#EFEDE7` rectangle behind the chart (**Arrange → Send to Back**), with a bold callout above it.
9. Paste with **Use Destination Theme & Embed Workbook**. Put the headline in the title (Libre Franklin Bold 26 pt McKesson Blue `#005A8C`) and the source at 9 pt `#737373`.

### Power BI
- Apply the theme `assets/powerbi/mckesson-dataviz-theme.json` (**View → Themes → Browse for themes**).
- Build a **Scatter chart** with X = event date (continuous), Y = a numeric **row index** column, Size = roles and Values (Details) = event ID. Hide the Y-axis labels and name the rows in a narrow aligned table visual, or build the chart in **Deneb (Vega-Lite)** for exact control of rows, size key and draw order.
- In **Format → Markers → Color → fx**, use rules on an `IsFocus` column (focus `#005A8C`, else `#B4B0A5`). Set **Bubble size** so the largest bubble is less than 1.5 rows tall.
- Use **Analytics → X-axis constant line → Shade area** for the insight period. Put the exact value and source in the tooltip page.
- For internal events, filter out anything with fewer than 10 people: `Show Event = IF([People] >= 10, 1)` used as a visual-level filter.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr)
source("assets/r/theme_mck.R")

rows  <- c("Health systems", "Payers", "Pharma manufacturers", "Distributors & PBMs", "Digital health")
focus <- "Pharma manufacturers"
# Synthetic events for illustration (replace with yours): one row per announcement
events <- data.frame(
  sector = rep(rows, times = c(5, 4, 6, 4, 4)),
  date   = c(2020.4, 2021.8, 2023.5, 2024.6, 2025.9,   2020.9, 2022.3, 2024.2, 2025.5,
             2021.2, 2023.1, 2023.8, 2024.4, 2025.2, 2026.1,   2020.6, 2022.9, 2024.9, 2026.3,
             2021.5, 2022.6, 2023.4, 2024.7),
  roles  = c(1200, 800, 1500, 900, 700,   600, 2500, 1100, 1300,
             1800, 4000, 6500, 3000, 9000, 2500,   900, 1400, 2000, 600,
             500, 3200, 2200, 800))
events |>
  arrange(desc(roles)) |>                                  # largest drawn first (underneath)
  mutate(sector = factor(sector, levels = rev(rows))) |>
  ggplot(aes(date, sector)) +
  annotate("rect", xmin = 2023, xmax = Inf, ymin = -Inf, ymax = Inf, fill = "#EFEDE7") +
  geom_point(aes(size = roles, fill = sector == focus), shape = 21, colour = "white", stroke = 0.5, alpha = 0.9) +
  scale_size_area(max_size = 16, breaks = c(1000, 5000, 10000), labels = scales::comma, name = "Roles affected") +
  scale_fill_manual(values = c(`TRUE` = mck_colors$focus, `FALSE` = mck_colors$context), guide = "none") +
  theme_mck() +
  theme(panel.grid.major.y = element_line(colour = mck_colors$grid, linewidth = 0.3), legend.title = element_text()) +
  labs(x = NULL, y = NULL,
       title = "Pharma manufacturers have announced more job cuts since 2023 than any other healthcare sub-sector",
       subtitle = "Announced workforce reductions by healthcare sub-sector, 2020–2026; bubble area = roles affected",
       caption = "Source: Public WARN notices and company announcements; U.S. only")
```

## QA specifics
- [ ] Bubble **area**, not diameter, is proportional to the value. One size scale covers the whole chart and a size key with round values sits top-left.
- [ ] There's one bubble color, or blue focus row + grey rows, with no per-row hues.
- [ ] The largest bubbles are drawn first, and white outlines plus slight transparency keep every overlapping bubble visible.
- [ ] The time axis is evenly spaced. Each row has a thin guide line and there's no y-axis.
- [ ] The shaded period matches the dates in the headline, and the callout numbers recompute from the data.
- [ ] Rows have ≤ ~15 events each (otherwise aggregate), and internal events with fewer than 10 people are excluded.

## Inspiration
- [p047 — Bubble timeline](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p047-bubble-timeline.md)
- [p048 — Bubble timeline best practice](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p048-bubble-timeline-best-practice.md)
