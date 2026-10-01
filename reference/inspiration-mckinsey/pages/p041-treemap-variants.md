---
still: 16
page: 41
section: Part-to-whole
title: Treemap variants
page_type: chart-type
chart_types: [geographic treemap, marimekko chart]
---
## Intent
Presents two alternatives to the standard treemap for part-to-whole questions: a geographic treemap for when the spatial arrangement of regions should be preserved, and a Marimekko (mosaic) chart for showing composition across two dimensions at once (e.g., region size × product mix).

## Guidance (paraphrased, every rule stated on the page)
- Geographic treemap: a treemap variant that places each rectangle in a position roughly matching where that world region actually sits.
- Marimekko chart: a two-dimensional stacked chart — like a stacked bar chart, segment heights vary, but in addition each column's width varies too.
- No explicit do/don't rules beyond these descriptions.

## Examples marked Recommended
- No explicit Recommended/Avoid verdicts; both panels are reference variants.
- Geographic treemap "Vehicle Sales" — three regional blocks laid out left-to-right as North America, Europe, Asia (west-to-east order), each subdivided into sub-rectangles — preserves a mental map while showing size.
- Marimekko chart "Vehicle Sales" — three columns (North America, Europe, Asia) whose widths reflect regional totals and whose stacked segments show the split between Cars, SUVs and Trucks — shows both regional share and product mix in one view.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Color roles:
  - Geographic treemap: each region has its own hue family, with tints for sub-rectangles — North America = dark navy (large base) plus two lighter slate/grey-navy strips on top; Europe = four stacked sky/cyan blue tints, lightest at top to most saturated at bottom; Asia = large royal blue base plus a top row of three rectangles in royal blue, medium periwinkle and light lavender-blue. Sub-rectangles are unlabeled.
  - Marimekko: 3 categorical colors mapped to product — dark navy = Cars (bottom), bright cyan blue = SUVs (middle), royal blue = Trucks (top). Same colors used in every column.
- Fill texture: some fills show a stippled/dithered pattern, most likely a GIF compression artifact rather than intended texture.
- Axes / gridlines: none in either chart; no value axis, no gridlines, no numeric labels.
- Labels:
  - Geographic treemap: region names centered below each block; no labels inside rectangles; no legend.
  - Marimekko: region names centered below each column; segment category labels (Trucks, SUVs, Cars) set as a column to the left, vertically aligned with the segments of the first (North America) column; no legend, no percentages.
- Proportions: Marimekko columns are full-height (100% stacked) with widths decreasing North America > Europe > Asia. Mix differs visibly: Asia has a much larger Trucks share and a thin SUVs band; Europe has a large SUVs share. Geographic treemap block widths also decrease NA > Asia > Europe roughly (Asia wider than Europe).
- Spacing: geographic treemap blocks separated by small white gaps between regions and thin white lines between sub-rectangles; Marimekko columns separated by thin white lines only (no gaps).
- Typography: page title large bold serif ("Treemap variants", two lines); eyebrow "Part-to-whole" small bold sans. Panel titles small bold sans with regular sans descriptions beneath. Chart titles "Vehicle Sales" small bold sans, centered above each chart. Category labels small regular sans.
- Layout: two equal-width white cards side by side on light-grey page background; title block top-left.

## Annotation & narrative patterns
- Chart titles are purely descriptive ("Vehicle Sales"); no insight headline, no callouts, no source or footnote.
- Footer: "McKinsey & Company" | "Data Visualization Guidelines" | "Version 01" | "19.07.18" | page "41".

## Other notes
- Sub-rectangles in the geographic treemap carry no labels or legend, so their meaning is not identifiable from this page.
