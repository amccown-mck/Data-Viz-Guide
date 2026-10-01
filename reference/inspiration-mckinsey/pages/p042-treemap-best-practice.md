---
still: 17
page: 42
section: Part-to-whole
title: Treemap best practice
page_type: chart-best-practice
chart_types: [treemap]
---
## Intent
Best-practice rules for building treemaps that show part-to-whole composition. Covers three concerns: how rectangles are arranged, how they are labelled, and how padding/sizing is kept consistent so area comparisons stay readable.

## Guidance (paraphrased, every rule stated on the page)
- **Arranging the treemap**
  - Do not lay out rectangles according to some functional grouping or in any order that makes comparing sizes harder.
  - Lay rectangles out so they flow from the largest to the smallest.
- **Labelling the treemap**
  - Do not add separate text boxes/bands inside or on top of rectangles to hold labels; they distort the treemap and make visual size comparison hard.
  - Put labels directly inside the rectangles; if a rectangle is too small to hold its label, place the label outside it.
- **Consistent padding and sizing**
  - Do not size rectangles inconsistently or leave empty gaps / uneven padding between blocks — it distracts.
  - Keep padding consistent so the treemap reads as one cohesive, organic shape, which supports comparison and exploration.

## Examples marked Recommended
- Treemap (5 categories A–E, legend to right) with the largest rectangle at top-left and progressively smaller rectangles flowing rightward/downward — size ordering makes comparison easy.
- Treemap of car brands (Ford, Citroen, Renault, Volkswagen, Vauxhall) all in dark navy with small labels sitting in the top-left corner of each rectangle; "Vauxhall" placed below/outside its rectangle because the slice is too thin — labels don't alter the geometry.
- Monochrome dark navy treemap with thin, uniform hairline dividers and a clean rectangular outer boundary — cohesive, no gaps.

## Examples marked Try to avoid / Not recommended
- Treemap with the same A–E legend but rectangles placed in a scattered/functional arrangement (large block bottom-left, small slivers in the middle, bright blocks at top) — no size flow, hard to compare.
- Car-brand treemap where each rectangle has a bright blue label bar/strip added across its top edge — the added bars eat into areas and distort perceived size.
- Dark navy treemap with irregular white gaps, uneven padding, and blocks that misalign / protrude past the outer edge — looks broken and distracts.

## Visual specifics observed
- Color roles: dark navy is the dominant fill; bright/sky blue, royal/electric blue, a pale light blue, and a grey-blue textured/dithered fill are used as the other categorical colors (5 total in the A–E examples). Labelling and padding examples use navy only, with blue label bars appearing only in the "avoid" case.
- Legends: small square swatches with single-letter labels (A–E) stacked vertically to the right of the chart in the arrangement examples.
- Dividers: thin light hairlines between rectangles in the recommended versions; uneven white gaps in the avoid version.
- Labels: very small sans-serif text, top-left inside each tile, light-colored on navy.
- No axes or gridlines (not applicable).
- Typography: page title in large serif ("Treemap best practice"), eyebrow "Part-to-whole" in small sans-serif above it; panel titles in medium sans-serif; verdict labels ("Try to avoid" / "Recommended") in bold small sans with an icon (dark navy circle with X for avoid; bright blue circle with check for recommended); explanatory text in regular small sans.
- Layout: three white card panels on a light grey page (two top, one bottom-left, bottom-right empty); each panel holds an avoid/recommended pair side by side separated by a thin rule above the captions.

## Annotation & narrative patterns
- Descriptive panel headings (not insight headlines); each rule expressed as a paired do/don't with a one- to two-sentence rationale.
- Footer: firm name, "Data Visualization Guidelines", "Version 01", date 19.07.18, page number at bottom right.

## Other notes
- Legend-letter labels and brand labels inside tiles are tiny; exact tile values are not shown (no numeric labels).
