---
still: 21
page: 46
section: Trend over time
title: Stacked area chart best practice
page_type: chart-best-practice
chart_types: [stacked area chart, overlapped area chart, line chart]
---
## Intent
Best-practice panel for stacked area charts showing change in composition over time. Covers three pitfalls: overlapping (non-stacked) area plots, arbitrary color ordering of stacks, and placing highly volatile series at the bottom of the stack.

## Guidance (paraphrased, every rule stated on the page)
- **Overlapped data plots:** Don't draw area series on top of one another (overlapping, not stacked). Front areas hide the ones behind them, so segments are hard to tell apart.
- Instead, stack the segments in a proper stacked area chart, or switch to a line chart.
- **Sorting colored stacks:** Don't assign colors to segments in random order. Adjacent colors may then look too similar, which hurts legibility.
- Order the stack colors by the recommended qualitative palette sequence. That keeps neighboring colors distinct and readable, even with ten categories.
- **High variability:** Don't put the categories with high variability at the bottom of the stack.
- Put the most volatile categories at the top and the most stable ones at the bottom.

## Examples marked Recommended
- Line chart version of the overlapped-area data: thin multi-line plot in navy/blue/light-blue tints with no fill. Every series stays visible and none is hidden.
- Stacked area with 10 categories (A–J) colored in palette order: A dark navy at the bottom, then blues, teal, light blue, lavender/purple, pinks/reds and salmon/peach at the top. Neighboring bands contrast clearly.
- Stacked area (A–F) with A (dark navy, stable) at the bottom and F (lavender, highly volatile) on top. The lower bands stay smooth and readable, and the volatility only affects the top edge.

## Examples marked Try to avoid / Not recommended
- Overlapping semi-transparent area fills in navy, blues, teal and lavender. Rear series are hidden behind front ones.
- 10-category stacked area with colors in arbitrary order: pink, red, blue, navy, textured/hatched fills and grey mixed together. Similar hues end up next to each other and the chart looks noisy.
- Stacked area (A–F) with the volatile series at the bottom. Its spikes pass up through every band above, so all the layers become jagged and hard to read. Here the top band (A, dark navy) is spiky and the lower bands (lavender, blues) wiggle.

## Visual specifics observed
- Color roles: the guide's qualitative palette runs from dark navy through bright/electric blue, cyan/sky blue, teal-grey, light blue and lavender, then pinks, coral/red and salmon/peach. Up to 10 colors are shown in the sorting example. Some avoid-example segments use hatched/speckled textures (hard to make out at this size).
- Axes / gridlines: no visible axis labels or tick values. A faint top reference line appears above some charts. Areas sit on a flat baseline.
- Labels: small square-swatch legends placed to the right of each stacked chart, with single-letter category keys (A–J or A–F). Legend order matches the stack order: in the recommended charts the top legend entry is the top band.
- Sort order: in the recommended variability example, stable categories are at the bottom and volatile ones on top. In the recommended color example, colors follow the palette sequence from bottom (A navy) to top (J peach).
- Layout: each panel is a white card with a panel title (sans, medium), two charts side by side, a thin divider rule, and then a verdict row. A dark circle with an "x" marks "Try to avoid"; a bright blue circle with a check marks "Recommended". Caption text sits under each verdict.
- Typography: page title in large black serif ("Stacked area chart best practice"). The small sans eyebrow above it reads "Trend over time". Panel titles are mid-size sans, verdict labels are small bold sans, body copy is small regular grey sans.
- Footer (small sans): McKinsey & Company · Data Visualization Guidelines · Version 01 · 19.07.18 · page number 46 at the right.

## Annotation & narrative patterns
- Headlines are descriptive panel titles naming the issue ("Overlapped data plots", "Sorting colored stacks", "High variability"). They don't state an insight.
- The example charts have no chart-level callouts, titles or sources. They are schematic.
- Each pitfall is presented as a paired avoid/recommended comparison with a short explanation.

## Other notes
- The page uses a 3-panel grid: two panels in the top row, one in the bottom-left, and empty space at the bottom-right.
- The dark bars at the top and bottom of the image are letterboxing from the GIF frame, not part of the page.
