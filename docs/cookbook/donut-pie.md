# Donut and pie charts

> **Question type:** Part-to-whole · Single number
> **Use for:** how **one** whole splits into ≤ 5 parts when one part is the story, or a single % against a full 100% (progress dial) · **Avoid when:** you compare the mix across several groups, or parts are close in size → use a [100% stacked bar](stacked-bar.md) or a sorted [bar chart](bar.md)

## When to use
- **One whole, few parts, one story segment.** For example, the worker-type mix of one function, or how one year's hires were sourced. The reader should see at a glance that "this part is about a third of the total".
- **Prefer a donut to a pie.** In a ring the eye follows arc length around the circle, which is easier to judge than wedge area. The empty center can also hold the headline number.
- **Variants:**
  - **Progress dial (ring):** a single percentage on a full 0–100% track, such as completion, coverage or readiness. Use a row of dials (small multiples) to compare the same % across ≤ 6 groups. Every dial uses the same size and the same 0–100% scale.
  - **Pie small multiples (pie matrix):** a grid of pies when each entity needs **two** things at once: its size (pie **area**) and a two-part split (e.g., postings per metro and the share requiring certification). Keep it to 2 segments per pie.
  - **Pie:** acceptable for a 2–3 part split read as "about half / about a quarter". Never use a pie for more than 3 parts or for precise comparison.

## When not to use
- You are comparing the mix **across groups** (functions, years, peers) → use a [100% stacked bar](stacked-bar.md). Never put a row of multi-segment donuts side by side.
- More than 5 parts, or parts within a few points of each other → use a sorted [bar chart](bar.md). People can't rank 22% vs. 25% by angle.
- The parts don't add up to a meaningful 100% (multi-select survey answers, overlapping skills) → use a [bar chart](bar.md) and say "% of respondents".
- A hierarchy or many parts (cost by org level, skills portfolio) → use a [treemap](treemap.md).
- Change in the mix over time → use a [stacked area](stacked-area.md) chart or [stacked bars](stacked-bar.md). For a bridge between two totals → use a [waterfall](waterfall.md).
- A single headline number with no part-to-whole meaning → use a [KPI / big number](kpi-big-number.md) instead of a dial.

## McKesson spec

| Element | Rule |
|---|---|
| Color | **Greys plus one story color.** The segment the headline names gets `chart.focus` `#005A8C` (or `chart.accent` navy `#143359` for a single exception next to a blue group). Never orange as the story color. Other segments alternate `chart.context` `#B4B0A5` and `chart.context_light` `#DEDBD1`, so neighbors stay distinct. "Other" is always `#DEDBD1`. Highlight at most **2** segments. Use the categorical order (`#005A8C`, `#143359`, `#66C4FF`, `#00AF9D`, `#00737A`) only when every part must be told apart, and then label every one. Separate segments with a 1.5–2 pt **white** border. **Dials:** value arc `#005A8C` for the dial(s) the headline names, `#B4B0A5` for the rest, on a light-sand track `surface.subtle` `#EFEDE7`. Mark targets with a short `chart.total` `#143359` tick. Use semantic `#00AF9D` / `#EF8200` only when good vs. bad is the message (e.g., coverage above vs. orange below target), with text in `#00737A` / `#A75B00`. Never use red vs. green. |
| Labels | For 2–3 short segments, label next to each segment, outside the ring. For 4–5 segments, use an **aligned key to the right of the ring**: marker, name, then a right-aligned value column, in wedge order. Never scatter bare values around the ring. Values are whole-number % (12 pt / 13 px Medium `#505050`). The story segment's name is bold Navy `#143359`, and its value is bold Navy `#143359`. The **center** holds one number, the story share or the total, in big-number style (Light, Navy `#143359`), plus 1–2 words in the subtitle style. Never put a legend at the bottom. |
| Axes / gridlines | None. No 3D, no shadows, no exploded wedges, no gradient fills. |
| Sort / order | Start at **12 o'clock** and run **clockwise**, largest segment first, then descending. "Other" goes last, whatever its size. A natural order (e.g., survey scale, tenure bands) overrides size. Keep the same order and colors for the same categories across the deck. In a dial row, sort the dials by value unless the groups have a fixed order. |
| Proportions | The hole is **62% of the diameter** (`chart.donut.hole`). That is Excel **Doughnut Hole Size ≈ 60–62%**, Plotly `hole=0.62`, matplotlib `wedgeprops=dict(width=0.38)`. Dials use the same ring. In a pie matrix, pie **area** (not diameter) is proportional to size: radius ∝ √value. |
| Limits | **≤ 5 segments** (`chart.donut.max_segments`, `chart.limits.pie_segments`); merge the tail into "Other". Segments must sum to **100%**. Round, then check the rounded labels still add to 100 (fix the largest segment if needed). ≤ 6 dials per row. Every whole and every segment is based on **n ≥ 10** people. Put "n = …" in the subtitle when the base is small. |

## Do / don't

| Do | Don't |
|---|---|
| Use one donut for one whole, with the story segment in color and the rest grey | Put a row of five multi-color donuts side by side to compare mixes (use 100% bars) |
| Start the largest segment at 12 o'clock and go clockwise in descending order | Mix large and small wedges in arbitrary or alphabetical order |
| Merge small slivers into a grey "Other" placed last | Show 8–11 slivers with off-palette colors and hatching |
| Label outside the ring, or in an aligned name + value key in wedge order | Scatter values around the ring with no names, or use a bottom legend |
| Put the story number in the center | Leave the hole empty, or fill it with a logo or icon |
| Give every dial the same size, the same 0–100% track and the same target tick | Let dials run to different maxima, or use speedometer half-gauges with red/amber/green bands |
| Size pies in a matrix by **area** and keep 2 segments each | Scale pie diameter by value (overstates the big ones) |

## Workforce examples
- **Function, internal:** *Headline:* "Contingent workers make up 30% of Technology's workforce, more than 4x the rate in other functions". *Subtitle:* "Technology workforce by worker type, 2026 (% of workers)". *Data:* [`examples/data/workforce_mix.csv`](../../examples/data/workforce_mix.csv), HRIS plus vendor-management (contingent) records. Contingent in blue, full-time and part-time in greys, and the 6.5% average for other functions stated beside the key.
- **Individuals → functions, internal (dial row):** *Headline:* "Only Pharmacy Ops has enrolled more than half of its high-exposure employees in reskilling". *Subtitle:* "Employees in high gen-AI-exposure roles enrolled in a reskilling pathway, by function, Q2 FY26 (%)". *Data:* individual learning-system enrollments joined to role-level exposure scores from [`examples/data/automation_exposure.csv`](../../examples/data/automation_exposure.csv), aggregated to function (n ≥ 10). One dial per function, a navy 50% target tick on each, and only the dial above target in blue.
- **Sector, external (pie matrix):** *Headline:* "In our three largest hiring metros, most pharmacy technician postings now require national certification". *Subtitle:* "Pharmacy technician job postings, top 8 McKesson hiring metros, Q2 2026 (pie area = postings; blue = % requiring certification)". *Data:* external job-postings data, metros ranked by McKesson hires. Use two-segment pies sized by area: the certification share in `#005A8C`, the rest in `#DEDBD1`, with the % under each pie and the three largest metros bolded.

## Build it

### Python — matplotlib + `mckviz`
```python
# verified runnable (from the repo root)
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
C = mv.colors
HOLE = mv.TOKENS["chart"]["donut"]["hole"]                     # hole = 62% of the diameter

mix = pd.read_csv(Path("examples/data/workforce_mix.csv")).set_index("function")
tech = mix.loc["Technology"]
others = mix.drop("Technology").contingent_pct.mean()
story = "Contingent workers"
parts = pd.Series({"Full-time employees": tech.employee_ft_pct, story: tech.contingent_pct,
                   "Part-time employees": tech.employee_pt_pct}).sort_values(ascending=False)   # largest first
fills = {"Full-time employees": C.context, "Part-time employees": C.context_light, story: C.focus}

fig, ax = plt.subplots(figsize=(10, 5.6))
ax.pie(parts, colors=[fills[k] for k in parts.index], startangle=90, counterclock=False,   # 12 o'clock, clockwise
       wedgeprops=dict(width=1 - HOLE, edgecolor="white", linewidth=2))
ax.text(0, 0.08, f"{parts[story]:.0f}%", ha="center", va="center", fontsize=40, fontweight=300, color=C.headline)
ax.text(0, -0.24, "contingent", ha="center", va="center", fontsize=12, color=C.text)

for i, (name, val) in enumerate(parts.items()):                # aligned key = labels + values, in wedge order
    y, hi = 0.36 - i * 0.3, name == story
    ax.scatter(1.4, y, s=110, color=fills[name], clip_on=False)
    ax.text(1.55, y, name, va="center", fontsize=11, fontweight="bold" if hi else "normal",
            color=C.headline if hi else C.text)
    ax.text(3.0, y, f"{val:.0f}%", va="center", ha="right", fontsize=11, fontweight="bold",
            color=C.headline if hi else C.text)
ax.plot([1.35, 3.0], [-0.42, -0.42], color=C.grid, lw=0.75)
ax.text(1.35, -0.55, f"Other functions average {others:.1f}% contingent", va="top", fontsize=10, color=C.annotation)
ax.set_xlim(-1.05, 3.05)
ax.set_ylim(-1.05, 1.05)

ratio = int(parts[story] // others)
mv.titles(fig, f"Contingent workers make up {parts[story]:.0f}% of Technology's workforce, more than {ratio}x the rate "
               "in other functions", "Technology workforce by worker type, 2026 (% of workers)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Contingent = contractors and agency workers in the vendor-management system. Other functions = "
                   "Distribution, Pharmacy Ops, Customer Care, Corporate.")
mv.save(fig, "out/donut.png", dpi=200)
```

**Progress-dial row** (the same ring, one dial per group, shared 0–100% track):
```python
# verified runnable (from the repo root)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import mckviz as mv

mv.use()
C = mv.colors
HOLE = mv.TOKENS["chart"]["donut"]["hole"]
TARGET = 50

# Share of employees in high gen-AI-exposure roles enrolled in a reskilling pathway (%), sorted
enrolled = pd.Series({"Pharmacy Ops": 58, "Customer Care": 44, "Distribution": 37, "Corporate": 21})

fig, axes = plt.subplots(1, len(enrolled), figsize=(10, 3.8))
for ax, (unit, pct) in zip(axes, enrolled.items()):
    hi = pct >= TARGET
    ax.pie([pct, 100 - pct], colors=[C.focus if hi else C.context, C.surface_subtle], startangle=90,
           counterclock=False, wedgeprops=dict(width=1 - HOLE))      # every dial shares the same 0-100% track
    ax.plot([0, 0], [-HOLE + 0.04, -1.06], color=C.total, lw=1.5)   # 50% target tick at 6 o'clock
    ax.text(0, 0, f"{pct}%", ha="center", va="center", fontsize=22, fontweight="bold" if hi else "normal",
            color=C.headline if hi else C.text)
    ax.text(0, -1.22, unit, ha="center", va="top", fontsize=11, fontweight="bold" if hi else "normal",
            color=C.headline if hi else C.text)

mv.titles(fig, "Only Pharmacy Ops has enrolled more than half of its high-exposure employees in reskilling",
          "Employees in high gen-AI-exposure roles enrolled in a reskilling pathway, by function, Q2 FY26 (%)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Navy tick = 50% enrollment target. High exposure = 50%+ of task hours exposed to gen AI.")
mv.save(fig, "out/donut-dials.png", dpi=200)
```
For a **pie matrix**, loop over a grid of axes and call `ax.pie([share, 100 - share], radius=(n / n.max()) ** 0.5, startangle=90, counterclock=False, colors=[C.focus, C.context_light], wedgeprops=dict(edgecolor="white", linewidth=1.5))`. The square root makes **area** proportional to size. Fix `ax.set_xlim(-1, 1)` and `ax.set_ylim(-1, 1)` on every axis so the pies share one scale.

### Python — Plotly / HTML
```python
# verified: builds without error
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

import mckviz as mv

mv.use()  # registers + activates the "mck" Plotly template
C = mv.colors
HOLE = mv.TOKENS["chart"]["donut"]["hole"]

mix = pd.read_csv(Path("examples/data/workforce_mix.csv")).set_index("function")
tech = mix.loc["Technology"]
others = mix.drop("Technology").contingent_pct.mean()
story = "Contingent workers"
parts = pd.Series({"Full-time employees": tech.employee_ft_pct, story: tech.contingent_pct,
                   "Part-time employees": tech.employee_pt_pct}).sort_values(ascending=False)
fills = {"Full-time employees": C.context, "Part-time employees": C.context_light, story: C.focus}

fig = go.Figure(go.Pie(
    labels=parts.index, values=parts.values, hole=HOLE, sort=False, direction="clockwise", rotation=0,  # 12 o'clock
    marker={"colors": [fills[k] for k in parts.index], "line": {"color": "white", "width": 2}},
    texttemplate="%{label}<br><b>%{value:.0f}%</b>", textposition="outside",
    hovertemplate="%{label}: %{value:.0f}%<extra></extra>"))
fig.add_annotation(text=f"<b>{parts[story]:.0f}%</b><br><span style='font-size:13px'>contingent</span>",
                   x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                   font={"size": 40, "color": C.headline})
fig.update_layout(showlegend=False, margin={"l": 80, "r": 80})
ratio = int(parts[story] // others)
mv.pl_finish(fig, f"Contingent workers make up {parts[story]:.0f}% of Technology's workforce, more than {ratio}x the "
                  "rate in other functions", "Technology workforce by worker type, 2026 (% of workers)",
             "Source: Synthetic data for illustration only",
             footnote=f"Other functions average {others:.1f}% contingent (Distribution, Pharmacy Ops, Customer Care, Corporate).")
Path("out").mkdir(exist_ok=True)
fig.write_html("out/donut.html", include_plotlyjs="cdn")
```
Plotly defaults to counter-clockwise and sorts by value, so always set `sort=False, direction="clockwise"`, and sort the data yourself (with "Other" last). For a dial row, use `make_subplots(rows=1, cols=n, specs=[[{"type": "domain"}] * n])` with one two-value `go.Pie` per cell, and the remainder colored `C.surface_subtle`. Hover may show headcounts, but only for groups with n ≥ 10.

### Excel and PowerPoint
1. Install the theme once. Copy `dist/office/Theme Colors/McKesson Data Viz.xml` to `%APPDATA%\Microsoft\Templates\Document Themes\Theme Colors\` and the Theme Fonts file to `...\Theme Fonts\`. Install Libre Franklin from `fonts/LibreFranklin`. Then apply **Page Layout › Colors › McKesson Data Viz** and **Fonts › McKesson Data Viz** (in PowerPoint: **Design › Variants › Colors / Fonts**).
2. Prepare the data: one column of names, one of values. Sort it **descending**, merge anything beyond 5 parts into "Other", and put "Other" in the last row. Excel draws the rows clockwise in sheet order.
3. Select the data, then **Insert › Charts › Insert Pie or Doughnut Chart › Doughnut**.
4. Right-click the ring › **Format Data Series › Series Options**. Set **Angle of first slice 0°** (start at 12 o'clock) and **Doughnut Hole Size 62%** (≈ 60%). Under **Fill & Line › Border**, set **Solid line, white, 1.5 pt**.
5. Per-point fill: click the ring once (selects the series), then click the story slice again (selects only that point). Set **Format Data Point › Fill › Solid fill › More Colors › Hex `005A8C`** (or `143359` for a single navy exception). Make the other slices `B4B0A5` and `DEDBD1`, alternating, with "Other" always `DEDBD1`.
6. Delete the legend and the default chart title (the headline goes in the slide title or a text box).
7. Labels. Excel can't place doughnut labels **Outside End**. For 2–3 segments, use **Chart Elements (+) › Data Labels › More Options**, tick **Category Name** and **Value**, set **Separator › (New Line)**, then drag each label just outside its slice. For 4–5 segments, delete the labels and build the aligned key in cells next to the chart (● in the slice color | name | value, right-aligned), or as a 3-column table in PowerPoint. Use Libre Franklin Medium 12 pt `#505050`, and set the story row **Bold**, Navy `#143359`.
8. Center number: select the chart, choose **Insert › Text Box**, and draw it inside the hole. With the box selected, type `=Sheet1!$B$3` in the formula bar so it updates with the data. Format it Libre Franklin Light 40 pt in Navy `#143359`, with a second line at 12 pt `#505050`.
9. **Progress dials:** give each group two cells, *Value* and *Remainder* (`=1-Value`). Build one doughnut (Angle 0°, hole 62%, **Border › No line**). Fill the Value point `005A8C` (focus) or `B4B0A5` and the Remainder point `EFEDE7`. Ctrl+drag to copy the chart, then repoint each copy with **Chart Design › Select Data**. Give all dials the same **Format › Size** (e.g., 1.6 × 1.6 in) and use **Shape Format › Align › Align Top / Distribute Horizontally**. Draw the target tick with a short navy line.
10. **Pie** (2–3 parts only): use **Insert Pie or Doughnut Chart › Pie** with the same angle, fills and borders. Pies, unlike doughnuts, do support **Data Labels › Outside End**. In a pie matrix, set each chart's **Format › Size** so that diameter ∝ √(value ÷ max value), which keeps pie **area** proportional.
11. In PowerPoint, insert a native chart (**Insert › Chart › Pie › Doughnut**, or paste with **Use Destination Theme & Embed Workbook**). Put the headline in the title placeholder (24 pt Bold Navy) and the source at 9 pt Libre Franklin Light `#737373`, bottom-left. Save the formatted chart via **Right-click › Save as Template** (`.crtx`).
12. Build-up on a live slide: **Animations › Wheel › Effect Options › Sequence: By Category** reveals the slices clockwise. Alternatively, duplicate the slide: step 1, all grey with the center number hidden; step 2, the story slice in color plus the center number.

### Power BI
- Import [`dist/powerbi/mckesson-dataviz-theme.json`](../../dist/powerbi/mckesson-dataviz-theme.json) via **View › Themes › Browse for themes**.
- Use the native **Donut chart** (Legend = category, Values = measure). Use **⋯ › Sort by › [measure] › Sort descending**. Under **Format visual › Rotation**, set the start angle to **0**. Where your Desktop version offers **Slices › Spacing › Inner radius**, set it to ~62%.
- Set each slice under **Slices › Colors**: story `#005A8C` (or `#143359` for a navy exception), the rest `#B4B0A5` / `#DEDBD1`. If **fx** (field-value color) isn't offered for slices in your version, drive the color with a measure on a bar chart instead.
- **Detail labels:** Position *Outside*, Label contents *Category, percent of total*. Turn the **Legend** off. Put the story number in a **Card** layered over the hole.
- Dials: a donut with two measures, `[Enrolled %]` and `Remainder = 1 - [Enrolled %]`, with the remainder colored `#EFEDE7`. Copy one visual per group, filter each one, and keep identical sizes. Avoid the native **Gauge**, which uses a half-circle with a different scale per visual.
- Enforce minimum n in the measures, so tooltips and drill-throughs inherit it: `Share (safe) = IF([Headcount] < 10, BLANK(), [Share])`.

### R — ggplot2 (optional)
```r
library(ggplot2); library(dplyr); library(readr)
source("dist/r/theme_mck.R")

tech <- read_csv("examples/data/workforce_mix.csv") |> filter(`function` == "Technology")
parts <- tibble(type = c("Full-time employees", "Contingent workers", "Part-time employees"),
                pct  = c(tech$employee_ft_pct, tech$contingent_pct, tech$employee_pt_pct)) |>
  arrange(desc(pct)) |>
  mutate(type = factor(type, levels = type), key = sprintf("%s   %d%%", type, pct))
fills <- mck_highlight(levels(parts$type), focus = "Contingent workers")
fills["Part-time employees"] <- mck_colors$context_light

ggplot(parts, aes(x = 2, y = pct, fill = type)) +
  geom_col(width = 1, color = "white", linewidth = 0.8, position = position_stack(reverse = TRUE)) +
  annotate("text", x = -0.13, y = 0, label = sprintf("%d%%\ncontingent", parts$pct[parts$type == "Contingent workers"]),
           size = 7, lineheight = 0.9, color = mck_colors$headline) +
  scale_fill_manual(values = fills, labels = parts$key, name = NULL) +
  coord_polar(theta = "y", start = 0, direction = 1) +   # 12 o'clock, clockwise
  xlim(c(-0.13, 2.5)) +                                   # hole = (1.5 + 0.13) / (2.5 + 0.13) = 62% of the diameter
  labs(title = "Contingent workers make up 30% of Technology's workforce, more than 4x the rate in other functions",
       subtitle = "Technology workforce by worker type, 2026 (% of workers)",
       caption = "Source: Synthetic data for illustration only") +
  theme_mck() +
  theme(axis.text = element_blank(), axis.title = element_blank(), axis.line.x = element_blank(),
        panel.grid = element_blank(), legend.position = "right")
```

## QA specifics
- [ ] There is one whole with ≤ 5 segments, "Other" is grey and last, and the shares add to 100% after rounding.
- [ ] The largest segment starts at 12 o'clock and runs clockwise in descending order (or in a stated natural order).
- [ ] Only the segment(s) the headline names are in color (≤ 2), and their name is bolded in the key. No rainbow, 3D, shadows or exploded slices.
- [ ] The hole is ≈ 62% of the diameter, and the center carries the story number, not a logo or an empty hole.
- [ ] Labels sit outside the ring or in an aligned name + value key in wedge order. There is no bottom legend and no scattered bare values.
- [ ] Dials share one size, one 0–100% track and one target marker. Pie-matrix sizes scale by area. Every whole and segment has n ≥ 10.

## Inspiration
- [p034 — Donut and pie chart](../../reference/inspiration-mckinsey/pages/p034-donut-and-pie-chart.md)
- [p035 — Donut and pie chart variants](../../reference/inspiration-mckinsey/pages/p035-donut-and-pie-chart-variants.md)
- [p036 — Donut and pie chart best practice](../../reference/inspiration-mckinsey/pages/p036-donut-and-pie-chart-best-practice.md)
