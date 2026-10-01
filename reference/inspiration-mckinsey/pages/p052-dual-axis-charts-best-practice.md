---
still: 27
page: 52
section: Correlation
title: Dual axis charts best practice
page_type: chart-best-practice
chart_types: [dual axis line chart, small multiples (side-by-side line charts), combo bar + line chart]
---
## Intent
Best practices for dual axis charts: when to break them into two separate charts, how to treat gridlines, and when to combine a line with bars instead of two lines.

## Guidance (paraphrased, every rule stated on the page)
Panel "When to split the chart in two":
- Dual axis scales are arbitrary, so the apparent relationship between the two series (e.g. where they cross) can mislead readers.
- It can be better to separate the series into two charts placed side by side so the two scales are not confused.

Panel "Grid lines":
- Do not run horizontal gridlines across the full width of a dual axis chart; this produces a confusing mesh of lines.
- Keep it simple with minimal lines and let the tick numbers beside each of the two Y-axes do the work.

Panel "Mixing lines and bars":
- Two trend lines are not always the right choice, particularly when one measure is a discrete quantity and the other is not.
- When comparing discrete quantities (e.g. GDP) against trends, indexes or rates, consider a bar chart for the quantity combined with a line for the rate.

## Examples marked Recommended
- Split chart: two adjacent small line charts — "Global GDP" (blue line, axis 40m–70m) and "German GDP" (navy line, axis 5m–8m), x-axis '04 to '08 — each series has its own independent scale, removing the false crossing.
- Grid lines: dual axis line chart (series A blue, left axis 0–6; series B navy, right axis 0–200) with no horizontal gridlines, only tick numbers on each side — cleaner read.
- Mixing lines and bars: blue columns for Global GDP with value labels above bars (31, 70, 122, 221, 243) plus a navy line for inflation rate; top legend with a line icon ("Inflation rate") and a bar icon ("Global GDP") — distinguishes discrete quantity from rate by mark type.

## Examples marked Try to avoid / Not recommended
- Split chart: single dual axis chart overlaying Global GDP (blue, left axis 40m–70m) and German GDP (navy, right axis 5m–8m), '04–'08; lines cross, implying a relationship created only by arbitrary scale choices.
- Grid lines: same A/B dual axis chart with horizontal gridlines extended across the whole plot — gridlines only match one axis and add clutter.
- Mixing lines and bars: two lines — Global GDP (blue, left axis 0–6) and Inflation rate (navy, right axis 0–200) — treating a discrete quantity like a continuous trend.

## Visual specifics observed
- Colors: bright/sky blue and dark navy only; blue consistently = first/left series (Global GDP, A), navy = second/right series (German GDP, B, Inflation rate).
- Series keys: small zig-zag line icons in each series' color above each axis, with a tiny label beneath (e.g. "Global GDP", "German GDP", "A", "B", "Inflation rate"); in the combo chart, a small bar icon keys the bars.
- Axes: tick numbers tiny light grey on both sides; faint vertical gridlines at x ticks in line examples. Note the split-chart examples use non-zero Y ranges (40m and 5m minimum) — contrasts with the zero-baseline rule on the previous page.
- X-axis: abbreviated years ('04, '05, '06, '07, '08); in the recommended split version only endpoints ('04, '08) appear labeled (small; partially hard to read).
- Combo chart: solid blue columns, evenly spaced, gaps roughly equal to or slightly wider than bar width; bold-ish small data labels above each bar; left axis 0–6 visible, right axis not clearly shown (illegible/absent). Faint horizontal gridlines may be present in the combo chart — hard to confirm.
- Lines: thin, no markers.
- Layout: three white cards on light grey page (two top, one bottom-left, bottom-right empty); each card holds an avoid/recommended pair with icon + bold label + body caption under a thin rule.
- Typography: large two-line serif page title with small sans eyebrow "Correlation"; card headings medium sans; captions small light sans; chart labels very small.

## Annotation & narrative patterns
- Descriptive headings only; no insight headlines or sources in the mini examples.
- Direct value labels used on bars in the recommended combo chart.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | 52.

## Other notes
- Many axis tick values are very small; values listed above are best reading, some intermediate ticks (e.g. 50m/60m, 6m/7m) are faint.
