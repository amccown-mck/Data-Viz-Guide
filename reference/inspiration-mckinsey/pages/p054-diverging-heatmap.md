---
still: 29
page: 54
section: Correlation
title: Diverging heatmap
page_type: chart-type
chart_types: [heatmap, diverging heatmap]
---
## Intent
- Shows values in a matrix (rows × columns) through color, so readers can see variation across several variables and pick out patterns/correlations.
- Diverging version: use when the data has a meaningful reference value in the middle of its range (e.g., zero or an average) and you need to separate values below vs above it.

## Guidance (paraphrased, every rule stated on the page)
- A heat map encodes each cell value in a matrix through color variation.
- Heat maps suit showing variance across multiple variables and revealing correlation patterns.
- A diverging heatmap uses a diverging palette.
- When the reference value sits mid-range (zero or an average), use a diverging scheme: a neutral color for the reference, one hue for low values, and a different hue for high values.
- Callout (left of chart): rows (cities) are ranked from the largest increase in pollution to the largest decrease.
- Callout (right of chart): the diverging scale is what lets the alarming increases in particular cities stand out.

## Examples marked Recommended
- None explicitly labeled "Recommended"/"Not recommended"; single annotated exemplar is shown:
  - Heatmap of monthly urban air pollution change for 12 cities — ranked rows plus a diverging warm/cool scale make the Asian-vs-North-American contrast immediately visible.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Chart: 12 rows (cities) × 12 columns (months J–D). Row order top→bottom: Seoul, Hong Kong, London, Paris, Sao Paulo, San Francisco, New York, Seattle, Amsterdam, Montreal, Washington, Chicago.
- Color roles: 7-step diverging scale — dark/royal blue (largest decrease), medium bright blue, light sky blue, light grey (neutral ≈ 0), pale salmon/peach, salmon-orange, pink-red/crimson (largest increase). Cool = decrease (good), warm = increase (bad).
- Legend: small horizontal stepped swatch bar at top-right above the grid, with a two-line title "Decrease/increase (%) of pollution levels" and tick labels -1.5%, 0, +1.5% beneath (small, light grey).
- Cells: rectangular (wider than tall), separated by thin white gaps; no gridlines, no axis lines, no borders.
- Row labels left-aligned in a column with a bold column header "Cities"; column labels are single-letter month initials centered under each column in small light grey type.
- No per-cell value labels.
- Typography: sans-serif throughout chart; headline bold large; subtitle regular with period and unit in parentheses "(%)"; footnote/source very small light grey. Page title is serif; section eyebrow small bold sans.
- Card layout: white chart card with soft drop shadow on light grey page background; thin horizontal rule above footnote area.
- Side callouts connected to the chart by thin horizontal grey leader lines (one on each side).

## Annotation & narrative patterns
- Headline is insight-style: states the takeaway (North American cities less polluted than Asian ones).
- Subtitle is descriptive: metric, time range, unit.
- Footnote line (placeholder text for notes/methodology) followed by "Source:" line, both at bottom-left of card.
- Explanatory callouts sit outside the card in the page margin, linked by leader lines.

## Other notes
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 54.
- Left rail: two short paragraphs defining heat maps and diverging heatmaps.
