# Dual-axis charts (and what to use instead)

> **Question type:** Change over time · Correlation
> **Use for:** almost never. To compare two measures with different units over the same period, use indexed lines, two aligned panels or a connected scatter instead · **Avoid when:** in nearly every case → use [indexed lines](line.md), aligned panels ([small multiples](small-multiples.md)) or a connected [scatter](scatter-bubble.md)

<!-- No rendered example in examples/output; the matplotlib snippet below renders the recommended alternative (two aligned panels). -->

## When to use
A dual-axis chart puts two measures with different units on one plot, one on each y-axis. Because both scales are chosen arbitrarily, the reader sees crossings, gaps and "tracking" that the designer created by picking ranges. **Default to an alternative**, chosen by the question:

- **"Which grew faster?" → indexed lines.** Divide each series by its value in a base period and multiply by 100, so both start at 100 on one honest axis. Show raw values in labels or tooltips. Example: order volume vs. DC headcount since FY22.
- **"Did B move when A moved?" (timing and shape) → two vertically aligned panels sharing the x-axis.** Each measure gets its own correctly labelled scale, and the shared time axis makes the timing comparison exact. Example: vacancy rate above, overtime hours below.
- **"As A changed, how did B respond?" → connected scatter.** X = the driver, Y = the outcome, with points joined in time order and the start, end and turning points labelled. Example: market wage growth vs. our attrition by quarter.
- **Only if a dual axis is truly unavoidable** (a mandated template, or a stakeholder standard you can't change yet): use **one quantity as columns and one rate as a line**, and follow every rule in the spec below.

## When not to use
- Both measures share a unit (two attrition rates, two headcounts) → put them on one axis in a single [line chart](line.md).
- The point is the ratio between the two (revenue per FTE, spans of control, cost per hire) → chart the **ratio itself** as one [line](line.md) or [bar](bar.md).
- More than two measures → use aligned panels / [small multiples](small-multiples.md) with one measure each.
- Live slides and mobile: two y-axes are too much to decode at a glance → use aligned panels or indexed lines.
- Never overlap two column series on two axes, and never stack a series against the secondary axis.
- To suggest cause and effect from where two lines cross: the crossing point is an artifact of the chosen ranges.

## McKesson spec

| Element | Rule |
|---|---|
| Color | **Indexed lines:** the series the headline is about in `chart.focus` `#005A8C`, the comparison series in `chart.context` `#B4B0A5` (label in `text.muted` `#737373`), and the 100 baseline in `chart.axis` `#8C8C8C`. **Aligned panels:** the same `#005A8C` line in each panel (the panel titles identify the measures), and any shaded period in `surface.subtle` `#EFEDE7`, identical in both panels. **Connected scatter:** path and dots in `#005A8C`, the start point in `#B4B0A5`. **Dual axis (if unavoidable):** columns for the quantity in `chart.context` `#B4B0A5` (or `#005A8C` if they're the focus), and the rate line in `chart.total` `#143359` at 2.25 pt. Each axis's tick labels and title match their series: navy text for the line axis and `#737373` for a grey column axis (grey `#B4B0A5` text fails 4.5:1 contrast). |
| Labels | **Indexed:** state the base ("FY22 = 100") in the subtitle and on the baseline. Label line ends with the index and the raw latest value ("134 · 552M lines"). **Panels:** each panel gets a bold, left-aligned title with measure and unit. Label only the peak and latest values. **Connected scatter:** label the first, last and turning-point periods ("Q1 '24", "Q4 '26") and show the direction of time with an arrow or the labels. **Dual axis:** put a horizontal title above each y-axis with a small line or bar icon in the series color, and label column values directly. No legend if the axis titles carry the key. |
| Axes / gridlines | **Indexed:** one y-axis; light horizontal gridlines in `chart.grid` `#E6E4DE`; the 100 line drawn solid in `#8C8C8C`. **Panels:** identical x range and width, x tick labels on the bottom panel only, each y-axis starting at 0 when magnitude matters, unit in the panel title. **Dual axis:** **both y-axes start at 0**, round tick values on each side, and **no horizontal gridlines** (they can only align to one axis). Vertical gridlines are optional. |
| Sort / order | Time runs left to right at even intervals in every panel. Stack panels in reading order: driver (cause candidate) above outcome. In a connected scatter, put the driver on X and the outcome on Y. In a dual axis, the quantity goes on the left axis and the rate on the right. |
| Proportions | Panels are equal height, with ~0.5 × panel height between them; the whole figure is 16:9 (full slide) or 4:3. A connected scatter is near-square. Line weights follow `chart.line` (focus 2.25 pt / 2 px, context 1.25 px). Columns in a dual axis use Gap Width 50% (bar : gap ≈ 2 : 1). |
| Limits | **2 measures, maximum.** At least ~5 time points. The index base period must be a normal period (not a strike month or a reorg spike), and the footnote states it. Suppress any period or group with **n < 10**. Describe association, not cause, and never build a headline on a crossing point. |

## Do / don't

| Do | Don't |
|---|---|
| Index both series to 100 at a stated base period when the question is relative growth | Put two growth series on two axes and let the reader guess which grew faster |
| Stack two panels on one shared time axis when the question is timing | Overlay two lines on two scales so they "track" because of the ranges you chose |
| Use a connected scatter when the question is how one measure responded to the other | Read meaning into where two dual-axis lines cross |
| If forced to use a dual axis: columns for the quantity, a line for the rate, both axes from zero | Draw two lines on a dual axis, or start one axis at zero and the other above it |
| Drop horizontal gridlines on a dual axis and key each axis title to its series | Run gridlines across both scales, creating a confusing mesh |
| Show raw values in labels or tooltips next to the index | Show the index alone, so no one can recover the actual numbers |
| Chart the ratio directly when the ratio is the point (lines picked per FTE) | Make the reader compute a ratio across two axes in their head |

## Workforce examples
- **Site level, internal (operations workforce):** *Headline:* "DC overtime rose in step with vacancies, peaking at 6.8 hours per FTE a week when 1 in 8 roles sat open". *Subtitle:* "U.S. distribution centers, monthly, Jan 2025–Dec 2026; panels share one time axis". *Data:* HRIS open budgeted positions and timekeeping overtime hours. Two aligned panels, with the hiring sprint shaded in both (matplotlib snippet below).
- **Firm level, internal (transformation / productivity):** *Headline:* "Order volume is up 34% since FY22 on just 4% more DC headcount, lifting lines picked per FTE by 29%". *Subtitle:* "Order lines picked and DC headcount, indexed FY22 = 100, FY22–FY26". *Data:* operations volume data and HRIS FTE. Indexed lines, with raw values in the tooltips (Plotly snippet below).
- **Sector vs. internal (external pay signal):** *Headline:* "Pharmacy Technician attrition tracked market wage growth down: as posted-pay growth cooled from 7% to 3%, attrition fell 9 points". *Subtitle:* "Pharmacy Technician voluntary attrition, annualized (%) vs. year-over-year growth in posted pay for U.S. pharmacy technician roles (%), quarterly, Q1 2024–Q4 2026". *Data:* an external job-postings pay feed for X and HRIS terminations for Y. A connected scatter, with the first and last quarters and the pay-reset quarter labelled.

## Build it

### Python — matplotlib + `mckviz`
The recommended alternative: two vertically aligned panels sharing one time axis.
```python
# verified runnable (from the repo root)
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import StrMethodFormatter

import mckviz as mv

mv.use()
C = mv.colors

# U.S. distribution centers, monthly, Jan 2025 - Dec 2026
vacancy = [7.2, 7.5, 7.9, 8.4, 9.1, 9.8, 10.6, 11.4, 12.1, 12.6, 12.3, 11.8,
           11.0, 10.2, 9.5, 8.9, 8.4, 8.1, 7.9, 7.7, 7.6, 7.4, 7.3, 7.2]
overtime = [3.9, 4.0, 4.3, 4.6, 5.0, 5.5, 5.9, 6.3, 6.6, 6.8, 6.7, 6.4,
            6.0, 5.6, 5.2, 4.9, 4.7, 4.5, 4.4, 4.3, 4.3, 4.2, 4.1, 4.1]
x = np.arange(24)
peak = int(np.argmax(vacancy))
ticks = [f"{m} '{y}" if m == "Jan" else m for y in (25, 26) for m in ("Jan", "Apr", "Jul", "Oct")]

fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10, 6.4), gridspec_kw={"hspace": 0.5})
panels = ((vacancy, "Vacancy rate (% of budgeted DC roles)", "{:.1f}%"),
          (overtime, "Overtime (hours per FTE per week)", "{:.1f}"))
for ax, (y, title, fmt) in zip(axes, panels):
    mv.shade_period(ax, 9.5, 13.5)                                       # same period shaded in both panels
    ax.plot(x, y, color=C.focus)
    ax.scatter([peak, x[-1]], [y[peak], y[-1]], s=22, color=C.focus, zorder=3)
    ax.annotate(fmt.format(y[peak]), (peak, y[peak]), xytext=(-6, 4), textcoords="offset points", ha="right",
                va="bottom", fontsize=11, fontweight="bold", color=C.focus, path_effects=mv.halo())
    ax.annotate(fmt.format(y[-1]), (x[-1], y[-1]), xytext=(6, 0), textcoords="offset points", va="center",
                fontsize=10, color=C.text, annotation_clip=False)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold", color=C.text, pad=8)
    ax.set_ylim(0, max(y) * 1.35)                                        # each panel has its own honest scale from 0
    mv.clean_axes(ax)

axes[0].yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}%"))
axes[0].text(9.65, axes[0].get_ylim()[1] * 0.97, "Hiring sprint +\nreferral bonus", va="top", fontsize=9,
             fontweight="bold", color=C.annotation)
axes[1].set_xticks(range(0, 24, 3), ticks)
axes[1].set_xlim(-0.3, 23.3)

mv.titles(fig, "DC overtime rose in step with vacancies, peaking at 6.8 hours per FTE a week when 1 in 8 roles sat open",
          "U.S. distribution centers, monthly, Jan 2025\u2013Dec 2026; panels share one time axis")
mv.source(fig, "Source: Workday HCM and timekeeping data, as of 31 Dec 2026; synthetic data for illustration",
          footnote="Vacancy rate = open budgeted positions \u00f7 budgeted positions at month end. "
                   "Overtime = paid overtime hours \u00f7 worked FTE, weekly average.")
mv.save(fig, Path(tempfile.gettempdir()) / "ck_scatdual_dual-axis-panels.png", dpi=200)
```
For a **connected scatter**, use `ax.plot(driver, outcome, color=C.focus, marker="o", ms=4)`, then annotate the first, last and turning-point periods. Add `ax.annotate("", xy=end, xytext=prev, arrowprops=dict(arrowstyle="->", color=C.focus))` to show the direction of time. If a dual axis is truly unavoidable, use `ax2 = ax.twinx()` with `ax.bar(...)` (quantity, `C.context`) and `ax2.plot(...)` (rate, `C.total`). Then set `ax.set_ylim(0, …)` **and** `ax2.set_ylim(0, …)`, call `ax.grid(False)`, and color each axis's tick labels to match its series.

### Python — Plotly / HTML
Indexed lines (base period = 100), with raw values kept in the labels and tooltips.
```python
# verified: builds without error
import tempfile
from pathlib import Path

import plotly.graph_objects as go

import mckviz as mv

mv.use()  # registers + activates the "mck" Plotly template
C = mv.colors

fy = ["FY22", "FY23", "FY24", "FY25", "FY26"]
series = {  # name: (raw values, unit, line color, label color)
    "Order lines picked": ([412, 445, 482, 519, 552], "M lines", C.focus, C.focus),
    "DC headcount": ([14_800, 15_100, 15_250, 15_350, 15_400], "FTE", C.context, C.text_muted),
}

fig = go.Figure()
fig.add_hline(y=100, line={"color": C.axis, "width": 1})
fig.add_annotation(x=fy[0], y=100, text="FY22 = 100", showarrow=False, yshift=-12, xanchor="left",
                   font={"size": 11, "color": C.text_muted})
for name, (raw, unit, line_col, text_col) in series.items():
    idx = [v / raw[0] * 100 for v in raw]
    fig.add_scatter(x=fy, y=idx, name=name, mode="lines", line={"color": line_col, "width": 3 if line_col == C.focus else 2},
                    customdata=raw, hovertemplate="Index %{y:.0f}<br>%{customdata:,} " + unit + "<extra>" + name + "</extra>")
    fig.add_annotation(x=fy[-1], y=idx[-1], text=f"<b>{name}</b><br>{idx[-1]:.0f} \u00b7 {raw[-1]:,} {unit}",
                       xanchor="left", xshift=8, showarrow=False, align="left", font={"color": text_col, "size": 13})

per_fte = (series["Order lines picked"][0][-1] / series["DC headcount"][0][-1]) / \
          (series["Order lines picked"][0][0] / series["DC headcount"][0][0]) - 1
fig.update_layout(showlegend=False, hovermode="x unified", margin={"r": 200})
fig.update_yaxes(range=[90, 140])
mv.pl_finish(fig, f"Order volume is up 34% since FY22 on just 4% more DC headcount, lifting lines picked per FTE by {per_fte:.0%}",
             "Order lines picked and DC headcount, indexed FY22 = 100, FY22\u2013FY26",
             source_text="Source: Operations volume data and Workday HCM; synthetic data for illustration",
             footnote="Index = value \u00f7 FY22 value \u00d7 100. Headcount = average DC FTE for the fiscal year.")
fig.write_html(Path(tempfile.gettempdir()) / "ck_scatdual_dual-axis-indexed.html", include_plotlyjs="cdn")
```
For **aligned panels** in Plotly, use `make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12)` with one trace per row, and put each measure and unit in a top-left annotation per panel. For the chart-card HTML pattern, see [`gallery_plotly.py`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/examples/python/gallery_plotly.py). Avoid `secondary_y=True`. If you're forced to use it, set `rangemode="tozero"` on both y-axes and `showgrid=False`.

### Excel and PowerPoint
1. Install the theme once. Copy `assets/office/Theme Colors/McKesson Data Viz.xml` to `%APPDATA%\Microsoft\Templates\Document Themes\Theme Colors\` and `assets/office/Theme Fonts/McKesson Data Viz.xml` to `...\Theme Fonts\`. Install Libre Franklin from `assets/fonts`. Then apply **Page Layout › Colors / Fonts › McKesson Data Viz** (in PowerPoint: **Design › Variants › Colors / Fonts**).
2. **Indexed lines (preferred).** Next to each raw column, add a helper column `=B2/B$2*100` (lock the base row) and fill down. Select the period column plus the index columns, then **Insert › Insert Line or Area Chart › 2-D Line**.
3. On the vertical axis, set **Format Axis › Axis Options › Horizontal axis crosses › Axis value: 100**. The category axis now sits on the 100 line and acts as the baseline (`#8C8C8C`, 0.75 pt). Format the lines (focus `#005A8C` 2.25 pt, comparison `#B4B0A5` 1 pt, no markers), delete the legend, and label the last points: **Format Data Labels › Value From Cells** pointing at a column like `134 · 552M lines`.
4. **Aligned panels.** Build one line chart per measure from the same period column. Select both charts (Ctrl+click) › **Shape Format › Size**: identical **Width**, then **Align › Align Left**. Give both the same horizontal axis settings. On the top chart, set **Format Axis › Labels › Label Position: None**, keeping its axis line. Add the measure and unit as a bold, left-aligned text box above each chart, and in PowerPoint **Group** the two charts.
5. **Connected scatter.** Put the driver in one column and the outcome in the next, rows in time order. **Insert › Insert Scatter (X, Y) › Scatter with Straight Lines and Markers**. Set the line `#005A8C` 1.5 pt with 5 pt markers, and **Line › End Arrow type** to show direction. Label the first, last and turning-point rows with **Value From Cells** (the quarter).
6. **Only if a dual axis is unavoidable:** **Insert › Insert Combo Chart › Clustered Column – Line on Secondary Axis**. In **Change Chart Type › Combo**, check **Secondary Axis** only for the rate (line) series.
7. Set **both** vertical axes to **Format Axis › Bounds › Minimum 0** (typed, so it's fixed). Select the gridlines and press **Delete**. Columns: **Gap Width 50%**, fill `#B4B0A5`, with data labels. Line: `#143359`, 2.25 pt, no markers.
8. Color each axis to its series: **Format Axis › Text Options › Text Fill**, `#737373` for the column axis and `#143359` for the line axis. Add **Axis Titles**, set **Text direction: Horizontal**, and drag each one above its axis ("Open requisitions" left, "Overtime hours per FTE" right). Delete the legend.
9. In PowerPoint, paste with **Home › Paste › Use Destination Theme & Embed Workbook**. The headline goes in the title placeholder (26 pt Bold McKesson Blue `#005A8C`), the subtitle at 14 pt `#505050`, and the footnote (index base, definitions) and source at 9 pt Libre Franklin Light `#737373`, bottom-left.

### Power BI
- Apply [`assets/powerbi/mckesson-dataviz-theme.json`](../../assets/powerbi/mckesson-dataviz-theme.json) (**View › Themes › Browse for themes**).
- **Indexed lines:** write index measures and plot them in one **Line chart**: `Volume index = DIVIDE([Order lines], CALCULATE([Order lines], REMOVEFILTERS('Date'), 'Date'[Fiscal Year] = "FY22")) * 100`. Add an **Analytics pane › Y-axis constant line** at 100 (`#8C8C8C`), and put the raw measures in **Tooltips**.
- **Aligned panels:** use two **Line charts** with the same X field and identical **Format › General › Properties › Size and position** width and X position, stacked vertically. Turn the X-axis **Values** off on the top visual.
- **If unavoidable:** use the **Line and clustered column chart**. Set **Format › Y-axis › Range › Minimum 0** and **Secondary y-axis › Range › Minimum 0**, turn **Gridlines** off, and turn on **Secondary y-axis › Title**, colored to match the line. Never put three or more measures on it.
- Enforce minimum n in the measures: `Overtime per FTE (safe) = IF([Worked FTE] < 10, BLANK(), [Overtime per FTE])`.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr); library(tidyr)
source("assets/r/theme_mck.R")

# Synthetic data for illustration (replace with yours): DC vacancy rate (%) and overtime (hours per FTE per week)
df <- data.frame(
  month = seq(as.Date("2025-01-01"), as.Date("2026-12-01"), by = "month"),
  vacancy_pct  = c(7.2, 7.5, 8.1, 8.8, 9.6, 10.4, 11.2, 12.0, 12.5, 12.1, 10.9, 9.4,
                   8.2, 7.6, 7.3, 7.1, 7.0, 7.2, 7.4, 7.3, 7.1, 6.9, 6.8, 6.9),
  overtime_hrs = c(3.9, 4.0, 4.4, 4.8, 5.3, 5.8, 6.3, 6.6, 6.8, 6.5, 5.8, 5.0,
                   4.4, 4.1, 3.9, 3.8, 3.8, 3.9, 4.0, 3.9, 3.8, 3.7, 3.7, 3.7))
long <- df |>
  pivot_longer(c(vacancy_pct, overtime_hrs), names_to = "measure") |>
  mutate(measure = factor(measure, levels = c("vacancy_pct", "overtime_hrs"),
                          labels = c("Vacancy rate (% of budgeted DC roles)", "Overtime (hours per FTE per week)")))

ggplot(long, aes(month, value)) +
  annotate("rect", xmin = as.Date("2025-10-16"), xmax = as.Date("2026-02-15"), ymin = -Inf, ymax = Inf,
           fill = "#EFEDE7") +                                     # same period shaded in both panels
  geom_line(colour = mck_colors$focus, linewidth = 1) +
  facet_wrap(~ measure, ncol = 1, scales = "free_y") +             # aligned panels, shared time axis
  scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.15))) +
  scale_x_date(date_breaks = "3 months", date_labels = "%b '%y") +
  labs(title = "DC overtime rose in step with vacancies, peaking at 6.8 hours per FTE a week when 1 in 8 roles sat open",
       subtitle = "U.S. distribution centers, monthly, Jan 2025–Dec 2026; panels share one time axis",
       caption = "Source: Workday HCM and timekeeping data, as of 31 Dec 2026", x = NULL, y = NULL) +
  theme_mck() +
  theme(strip.text = element_text(hjust = 0, face = "bold", size = 11, colour = mck_colors$text),
        panel.spacing = unit(18, "pt"))

# Indexed alternative: mutate(across(c(order_lines, dc_fte), ~ .x / first(.x) * 100)) and plot one line per measure.
```

## QA specifics
- [ ] An alternative (indexed lines, aligned panels or connected scatter) was tried first. If a dual axis remains, the reason is noted and it shows only 2 measures: columns for the quantity, a line for the rate.
- [ ] Indexed charts state the base period in the subtitle and on the 100 line, the base period is a normal period, and the raw values are available in labels or tooltips.
- [ ] Aligned panels share an identical x range, width and left edge. Each panel is titled with its measure and unit, and shaded periods match across panels.
- [ ] Dual axis (if any): **both** y-axes start at 0, there are no horizontal gridlines, and each axis title and its tick labels are colored or keyed to their series.
- [ ] Connected scatter: the driver is on X and the outcome on Y, and the start, end and direction of time are labelled.
- [ ] The headline describes co-movement, not cause, and makes no claim based on where two lines cross.

## Inspiration
- [p051 — Dual axis charts](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p051-dual-axis-charts.md)
- [p052 — Dual axis charts best practice](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/reference/inspiration-mckinsey/pages/p052-dual-axis-charts-best-practice.md)
