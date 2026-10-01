---
still: 06
page: 31
section: Magnitude
title: Bar chart best practice
page_type: chart-best-practice
chart_types: [vertical bar, line (as alternative)]
---
## Intent
Four do/don't pairs for making bar charts readable and honest: bar width, use of color, labeling instead of gridlines, and keeping a zero baseline. Covers the case of values clustered far from zero, where a line or scatter plot is the better choice.

## Guidance (paraphrased, every rule stated on the page)
- Size of bars: bars that are too thin draw the eye to the empty space between them, which carries no information. Make each bar about twice as wide as the gap between bars.
- Color of the bars: giving each bar a different color distracts without reason. Use one color for all bars and apply a contrasting shade only to highlight.
- Direct labelling: bar charts usually do not need gridlines or a value axis, which add noise without adding information. Remove clutter, label values directly on the bars, and drop the gridlines to improve legibility.
- Zero baseline: never truncate the value axis of a bar chart. Bar length encodes quantity, so a non-zero start misleads. If the data need a non-zero range, switch to a chart type that doesn't need a zero baseline (line chart or scatter plot), so readers compare position and slope instead.

## Examples marked Recommended
- Size of bars: five wide navy columns (A–E) whose width is about 2x the gaps between them. This keeps attention on the data rather than on the white space.
- Color of the bars: five navy columns with only bar D in bright blue, and the D axis label set in bold. The single accent directs attention to the item that matters.
- Direct labelling: six navy columns (A–F) with value labels above each bar (e.g., 43, 84, 97, 83, 90; the first label is too small to read reliably, likely 85) and no gridlines or y-axis. The chart is cleaner and values are read directly.
- Zero baseline: the same data as a thin dark line chart on a non-zero y range (about 100–300, faint gridlines). A line doesn't imply length-from-zero, so a truncated range is acceptable.

## Examples marked Try to avoid / Not recommended
- Size of bars: very thin stick-like bars (A–E) with wide gaps. The eye is drawn to the empty space.
- Color of the bars: every bar a different color (royal blue, light blue, navy, watermelon/pink-red, teal/steel blue). The rainbow coloring distracts the reader.
- Direct labelling: navy columns with a y-axis (0/25/50/75/100) and horizontal gridlines. These add noise without adding value.
- Zero baseline: columns on a y-axis starting at about 100 (ticks ~100–300). Bar heights exaggerate the differences, which is misleading.

## Visual specifics observed
- Color roles: dark navy is the default bar color, bright blue is the single highlight, and the multi-color bars on the "avoid" side show misuse. Light grey is used for gridlines, rules, and axis text.
- Bar width to gap ratio: recommended about 2:1. The thin-bar counter-example shows roughly 1:8 or more.
- Axes: tick labels are very small and light grey, and gridlines are hairline light grey. The recommended bar examples have no y-axis and only a hairline baseline.
- Highlight pairing: the highlighted category's x-axis label is bolded (D) as well as the bar being recolored.
- Labels: direct value labels are small, centered above each bar, and shown as integers without units.
- Sort order: categories are in alphabetical order (A–F), not sorted by value.
- Card structure: each card has a medium-weight sans heading (e.g., "Size of bars") and two side-by-side mini charts. Under each chart, a hairline rule precedes an icon + label ("Try to avoid" with a dark circle X icon; "Recommended" with a bright blue circle check icon), followed by a one-to-three-line explanation.
- Typography: the page title is a large two-line serif ("Bar chart / best practice"). The eyebrow "Magnitude" is small bold sans. Card headings are larger sans, callout labels are small medium-weight sans, and body text is small regular sans.
- Footer: "McKinsey & Company", "Data Visualization Guidelines", "Version 01", "19.07.18", page "31".

## Annotation & narrative patterns
- Do/don't pairs always put "Try to avoid" on the left and "Recommended" on the right.
- Callout copy states the problem, then the fix, in one short sentence each.
- The example charts have no headlines or sources.

## Other notes
- Highlighting pattern: recolor one bar in the accent color and bold its category label.
- The truncated-axis guidance means changing the chart type rather than simply adding an axis-break symbol.
