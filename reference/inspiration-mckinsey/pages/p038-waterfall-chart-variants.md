---
still: 13
page: 38
section: Part-to-whole
title: Waterfall chart variants
page_type: chart-type
chart_types: [distribution waterfall chart, horizontal waterfall chart]
---
## Intent
Shows two alternative forms of the standard waterfall chart for part-to-whole questions: (1) breaking a total down into its categorical contributors, and (2) showing a sequence of increases/decreases from a starting value to an ending balance in a horizontal orientation. Use the distribution variant when the X axis holds categories rather than time; use the horizontal variant when labels are long or the layout is narrow (e.g., mobile).

## Guidance (paraphrased, every rule stated on the page)
- Distribution waterfall chart: a waterfall variant whose X axis carries data categories rather than time periods.
- Horizontal waterfall chart: has advantages over the vertical form — category labels are easier to fit, and it performs better in narrow layouts such as mobile screens.
- No explicit "do/don't" rules beyond these two descriptions.

## Examples marked Recommended
- None explicitly marked Recommended/Try to avoid; both panels are presented as reference variants.
- Distribution waterfall (left panel): a total bar on the far left, followed by category segments (Ford, Citroen, Renault, Volkswagen, Vauxhall) that step down from the top of the total to the baseline — shows how a whole splits into components.
- Horizontal waterfall (right panel): "Previous" start bar, a series of floating increase/decrease bars (rows labeled A–E), and a "Balance" end bar — shows net movement from start to end value.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Color roles:
  - Distribution waterfall: bright blue = the Total bar (highlight/anchor); dark navy = each component segment. 2 colors.
  - Horizontal waterfall: dark navy = start ("Previous") and end ("Balance") bars; bright blue = increases; red/pink (coral-red) = decreases. 3 colors, with a legend "Increase" (blue square) / "Decrease" (red square) placed top-right above the plot.
- Axes / gridlines / baseline:
  - Distribution: no Y axis, no gridlines, no value labels; a thin light-grey baseline under the bars; thin light connector lines join the top/bottom of consecutive segments.
  - Horizontal: no X axis or gridlines; a thin light vertical baseline at the left origin where Previous and Balance bars start; no value labels.
- Labels:
  - Distribution: category labels centered under each bar; the "Total" label is set in bold, component labels in regular weight.
  - Horizontal: category labels left-aligned in a column to the left of the bars (Previous, A, B, C, D, E, Balance). Legend used (not direct labeling) for increase/decrease color meaning.
- Sort order: distribution segments appear in the order Ford, Citroen, Renault, Volkswagen, Vauxhall (not sorted by size — Citroen and Vauxhall are the largest). Horizontal chart follows sequential order start → changes → balance.
- Spacing: vertical bars are relatively narrow with gaps roughly equal to bar width; horizontal bars are thick with small gaps between rows.
- Observation: in the horizontal example the floating bars do not line up one-to-one with the row labels — there appear to be six change bars for five labels (A–E), and bars sit slightly offset from label baselines. Likely a mock-up artifact; do not copy.
- Typography: page title in a large bold serif ("Waterfall chart variants", two lines); eyebrow "Part-to-whole" in small bold sans above it. Panel titles in small bold sans, descriptions in small regular sans beneath. Axis/category labels in small regular sans. Footer in small sans.
- Layout: two equal-width white cards side by side on a light-grey page background; title block top-left, generous empty space above the cards.

## Annotation & narrative patterns
- Panel headlines are descriptive (the chart type name) followed by a one- or two-sentence explanation; no insight headlines.
- No callouts, sources, or footnotes on the charts.
- Footer: "McKinsey & Company" | "Data Visualization Guidelines" | "Version 01" | "19.07.18" | page number "38" at far right.

## Other notes
- Example data is generic (car manufacturers; lettered categories A–E) with no numeric values shown.
