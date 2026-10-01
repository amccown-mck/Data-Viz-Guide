---
still: 30
page: 55
section: Correlation
title: Heatmaps best practice
page_type: chart-best-practice
chart_types: [heatmap, sequential heatmap, diverging heatmap]
---
## Intent
- Practical rules for building heatmaps well: how to define color steps, how to order rows, and how to handle the zero/neutral step on diverging scales.

## Guidance (paraphrased, every rule stated on the page)
- Coloring steps: for a sequential heatmap, avoid arbitrary or uneven class thresholds; keep steps in sequential order with even (balanced) increments.
- Sorting: data can be ordered many ways; alphabetical order is sometimes fine but often hides patterns. Ranking rows by density/value lets the color steps reveal overall trends.
- Zero on diverging heatmaps: do not drop the zero step from a diverging scale; include a zero step as the neutral midpoint. (The recommended caption says "sequential heatmaps" work best with a zero step, although the panel is about diverging heatmaps.)

## Examples marked Recommended
- Legend "Number of steps" with a separate grey 0 swatch then 8 evenly incremented blue steps (ticks approx. 1, 2, 3, 4, 5, 6, 7, 8+) — equal intervals make color differences proportional and readable.
- Blue sequential heatmap (rows labeled A–L) sorted by density — darker cells concentrate at top, lighter at bottom, so the trend emerges.
- Diverging heatmap whose legend has a grey zero swatch between 3 blue steps and 3 warm steps (7 steps total); grid includes grey neutral cells — neutral midpoint clearly separates negative from positive.

## Examples marked Try to avoid / Not recommended
- Legend "Number of steps" with grey 0 swatch then 8 blue steps using uneven thresholds (ticks approx. 1, 2, 4, 6, 8, 10, 20, 30+) — arbitrary/unbalanced class breaks distort perception.
- Same blue heatmap unsorted (alphabetical, rows A–L) — dark and light cells scattered randomly, no pattern visible.
- Diverging heatmap whose legend has only 3 blue + 3 warm steps with a gap and no zero swatch; grid has no grey cells — missing neutral step forces every value into positive/negative.

## Visual specifics observed
- Sequential palette: single-hue blue ramp from very light sky blue to near-black navy; zero shown as light grey swatch set slightly apart from the ramp.
- Diverging palette: dark royal blue → bright blue → light blue | light grey (zero) | pale salmon → salmon-orange → pink-red.
- Legends: small horizontal stepped swatch bars with a "Number of steps" title above (sequential examples) and tiny grey numeric ticks below; diverging tick labels are tiny and partly illegible (appear to be 3, 2, 1, [0], 1, 2, 3 with signs illegible).
- Sorting example: approx. 12 rows × ~24 columns of small square cells with thin white gaps; tiny single-letter row labels A–L at left (whether the recommended version's labels are reordered is illegible at this resolution).
- Diverging example grids: ~12 rows × 12 columns rectangular cells, warm rows at top, dark blue at bottom; no axes or gridlines.
- Layout: three white panels on light grey page (2 top, 1 bottom-left; bottom-right empty). Each panel has a bold sans panel title and a pair of side-by-side examples: "Try to avoid" left, "Recommended" right.
- Verdict markers: dark navy circle with white "×" for Try to avoid; bright blue circle with white check for Recommended; bold label then short regular-weight explanatory text; thin grey rule above each verdict row.
- Typography: page title serif, two lines; section eyebrow small bold sans; panel titles medium-bold sans; captions small regular sans.

## Annotation & narrative patterns
- Avoid/Recommended paired comparisons, with the avoid example always on the left.
- Example charts have no headlines/sources; only legends and minimal labels.

## Other notes
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 55.
- Left rail has only the eyebrow and title (no body text).
