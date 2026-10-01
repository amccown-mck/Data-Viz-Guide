---
still: 19
page: 44
section: Trend over time
title: Line chart best practice
page_type: chart-best-practice
chart_types: [line chart, multi-series line chart, stacked bar chart, area chart]
---
## Intent
Do/don't rules for line charts: how to surface one insight among many series, when to prefer a line over a stacked bar for trends, when not to fill beneath a line, and where to place the legend/labels.

## Guidance (paraphrased, every rule stated on the page)
- **Highlights**
  - Showing many data series each in its own color does not help readers see trends, even if the volume of data matters.
  - Push background series to grey and apply a single highlight color to the series that carries the message.
- **Showing trends**
  - Stacked bars don't convey incremental change well (e.g., how sales grow over time).
  - When the trend matters more than discrete quantities, a line chart is the better choice than a stacked bar chart.
- **Shading lines**
  - Don't shade/fill under a line unless the y-axis has a zero baseline — filling turns it into an area chart.
  - When the y-axis range doesn't start at zero, use a plain line chart, not an area chart (area charts suit discrete quantities).
- **Stacked legends**
  - Don't put the legend/key above the chart — it breaks the category reading order and makes lookup awkward while reading lines.
  - Stack the legend vertically, positioned close to the ends of the lines.

## Examples marked Recommended
- Same many-series line chart with all but one line rendered in very light grey and one line in dark navy — the highlight line pops, background becomes context.
- Multi-series line chart (one dark navy line prominently higher, bright blue line, royal blue line, grey lines lower) replacing the stacked bars — the trajectory of each series is readable.
- Single dark navy line on a y-axis from ~60 to 100 with no fill — honest for a non-zero baseline.
- Four-series line chart (A–D) with labels A, B, C, D stacked vertically at the right end of the lines — each label sits beside its line.

## Examples marked Try to avoid / Not recommended
- Tangled line chart with ~10+ series in many hues (orange, pink, red, teal, blue, navy, grey) — rainbow categorical coloring hides any pattern. (Try to avoid)
- Stacked bar chart over ~8 periods with 4–5 segments (navy, bright blue, royal blue, grey, textured blue-grey) on a 0–100 scale — segment growth can't be compared across bars. (Try to avoid)
- Solid dark navy filled area under a line on a y-axis starting at ~60 — implies magnitude from a non-zero base; becomes an area chart. (Marked "Avoid" — note the stronger label and a red/pink X icon instead of the navy X used for "Try to avoid".)
- Four-series line chart with a horizontal dot legend (A, B, C, D) placed above the plot — reader must bounce between key and lines. (Try to avoid)

## Visual specifics observed
- Color roles: dark navy = primary/highlight series; bright sky blue, royal/electric blue, pale light blue = secondary series; light grey = de-emphasised background series; multi-hue palette (orange, pink, red, teal) appears only in the avoid example.
- Axes: small grey tick labels; x-axis appears to use decade labels (e.g. '60, '70, '80, '90, '00 — partly illegible at this size); y-axis ticks 0/25/50/75/100 in the trends panel and ~60–100 in steps of 10 in the shading panel. Light horizontal gridlines faintly visible; baseline hairline at bottom.
- Legend treatments: avoid = horizontal row of colored dots + letters above chart; recommended = letters only, vertically stacked, right of line ends, aligned to each line's end value.
- Lines are thin, uniform weight; no markers on points.
- Verdict icons: navy circle with white X ("Try to avoid"); red/pink circle with X ("Avoid"); bright blue circle with white check ("Recommended").
- Typography: page title large serif ("Line chart best practice") with small sans eyebrow "Trend over time"; panel headings medium sans; verdict labels small bold sans; captions small regular sans.
- Layout: 2×2 grid of white cards on light grey background; each card has an avoid (left) vs recommended (right) pair, separated from captions by thin rules.

## Annotation & narrative patterns
- Panel headings are descriptive topic labels (Highlights, Showing trends, Shading lines, Stacked legends); each rule is a paired do/don't with 1–3 sentence rationale.
- No insight headlines or source lines in the mini-examples.
- Page footer: firm name, "Data Visualization Guidelines", "Version 01", 19.07.18, page number.

## Other notes
- Two severity levels of negative verdict exist: "Try to avoid" (softer) and "Avoid" (stronger, red icon).
- Tick label values in the miniature charts are very small; exact values partly illegible.
