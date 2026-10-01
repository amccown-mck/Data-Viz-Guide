---
still: 14
page: 39
section: Part-to-whole
title: Waterfall chart best practice
page_type: chart-best-practice
chart_types: [waterfall chart]
---
## Intent
Formatting best practices for waterfall charts (part-to-whole / bridge from a starting value to an ending value). Covers three topics: styling of connector lines, coloring of increase/decrease bars, and labeling when segment sizes vary greatly.

## Guidance (paraphrased, every rule stated on the page)
- Connecting line
  - Do not draw the connectors between bars with a heavy, dark stroke — they visually compete with the bars and make comparison harder.
  - Use a thin, light-grey connector so the bars remain the dominant element.
- Coloring the waterfall bars
  - Do not encode increases and decreases with red and green: the pair is not accessible to people with color-vision deficiency and those colors are not part of the brand palette.
  - When you want to draw attention to decreases, use colors from the brand's diverging palette to shade negative values (example uses blue for increases and a pink/red for decreases).
- Large difference in values
  - When segment sizes differ enormously and exact figures are not the point, direct value labels can be a poor fit because the scale makes the small numbers hard to read.
  - In that situation, drop direct labels and label the value axis instead.

## Examples marked Recommended
- Connecting line — waterfall with dark navy step bars, a bright blue intermediate subtotal bar and a bright blue final total; connectors are hairline light grey, almost invisible — bars stand out.
- Coloring the waterfall bars — dark navy "Previous" start and "Balance" end bars; bright blue increase bars; muted pink/red decrease bars; small legend "Increase / Decrease" top-right — accessible, on-palette, and emphasizes the negative steps.
- Large difference in values — same many-small-steps-then-one-big-step waterfall, now with a light Y axis (ticks 0, 25, 50, 75, 100) and faint horizontal gridlines; no direct labels — values remain readable via the axis.

## Examples marked Try to avoid / Not recommended
- Connecting line ("Try to avoid") — same waterfall with thick black connector lines linking bar tops; the lines overpower the bars and blur comparison.
- Coloring the waterfall bars ("Avoid") — bright green for increases and for the Previous/Balance bars, bright red for decreases, with a green/red legend — not colorblind-safe and off-brand.
- Large difference in values ("Try to avoid") — waterfall with many tiny steps and one tall step, no axis; per the text, direct labels in this situation become hard to read (no value labels are actually legible in the thumbnail).

## Visual specifics observed
- Color roles: dark navy = component/step bars and start/end anchors; bright blue = totals/subtotals (connector & large-difference examples) or increases (coloring example); pink/red = decreases (diverging palette); light grey = connectors, baseline, gridlines. Red/green only in the negative example.
- Axes / gridlines / baseline: default examples have no axis and no gridlines, just a light baseline. Recommended large-difference version adds a small, light-grey Y axis with 25-unit ticks (0–100) and faint horizontal gridlines.
- Labels: coloring examples use tiny X-axis category labels (Previous, A, B, C, D, E, F, Balance) and a legend top-right with small square swatches; other examples have no category labels.
- Stroke weights: heavy black connector (avoid) vs hairline light-grey connector (recommended).
- Bar widths: bars moderately narrow with gaps about equal to or larger than bar width; final total bar is the same width as step bars.
- Icons: "Try to avoid" = dark navy circle with white X; "Avoid" (coloring panel) = pink/red circle with X; "Recommended" = bright blue circle with white check mark. A thin grey rule separates each chart from its verdict text.
- Typography: page title large bold serif (two lines); eyebrow "Part-to-whole" small bold sans. Panel titles ("Connecting line", "Coloring the waterfall bars", "Large difference in values") medium sans. Verdict labels small bold sans; explanation small regular grey sans. Axis tick labels very small light grey.
- Layout: 2×2 grid of white cards on light-grey background (bottom-right cell empty); each card pairs a negative (left) and positive (right) example.

## Annotation & narrative patterns
- No chart headlines; charts are unlabeled mockups. Explanatory text sits beneath each chart with a verdict label (Try to avoid / Avoid / Recommended).
- No sources or footnotes on charts.
- Footer: "McKinsey & Company" | "Data Visualization Guidelines" | "Version 01" | "19.07.18" | page "39".

## Other notes
- Two different negative labels are used on the same page: "Try to avoid" (styling issues) and the stronger "Avoid" (accessibility/palette violation), with a distinct red icon for the latter.
