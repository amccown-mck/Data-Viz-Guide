---
still: 46
page: 71
section: Format
title: Interactivity
page_type: other
chart_types: [bubble chart, scatter plot]
---
## Intent
Section-intro page for interactivity in data visualization. Explains why and when to add interactions (sliders, filters, toggles) and signals that the following pages survey specific interaction types and best practices. Shown via a single tablet-framed interactive bubble chart with a hover tooltip.

## Guidance (paraphrased, every rule stated on the page)
- Interactivity can give a visualization additional depth.
- Letting users explore via sliders, filters and toggles helps them absorb the data at their own speed and can surface extra details or insights.
- Interactions can be applied to nearly any chart type, but each one must have a clear purpose.
- Superfluous interactions can distract the viewer or make a simple idea overly complicated.
- The section gives an overview of usable interactions plus best practices.
- UI styling (controls etc.) is governed by a separate document: the McKinsey Interactive Elements Guidelines.

## Examples marked Recommended
- No explicit Recommended/Avoid marker. The single example (implicitly a good practice) is a dark-background bubble chart in a tablet frame: insight headline "While most European countries are well off, US shows a low life expectancy, despite better GDP per capita"; subtitle "Countries with life expectancy above 78 years old across the globe, 2017". Hovering the cursor over the large USA bubble reveals a white tooltip "USA / 326,000,000" (population). A shaded rectangular region highlights a cluster of mostly European bubbles. Shows interaction used to reveal detail on demand without cluttering the static view.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Dark mode: very dark navy chart background; white headline, light-grey subtitle and axis text.
- Color roles (categorical by region, 5 colors, legend at right with dot markers): Central, East Asia & Pacific = light grey/white; Europe & Russia = mid/bright blue; North America = electric/royal blue; Latin America & Caribbean = light cyan; Middle East & North Africa = muted teal/steel blue.
- Bubble size = population; size key at top of legend shows overlapping grey circles labelled "Population".
- Highlight: translucent lighter rectangle spanning roughly $30,000–$50,000 on x and 80–84 on y, marking the European cluster; USA bubble (large, electric blue) sits outside it at ~$57,000 / ~79.
- Axes: y "Health (life expectancy, years)" label placed top-left, horizontal above axis; ticks 78, 80, 82, 84. x "Wealth (GDP per capita)" centered below; ticks 0, $20,000, $40,000, $60,000, $80,000. Thin, subtle grid lines in both directions forming a grid of cells; plot area bordered.
- Tooltip: white box, small dark text, country name on first line, bold value on second, number with thousands separators, no unit label.
- Typography: page title serif ("Interactivity"), sans eyebrow "Format"; chart headline bold sans, two lines; subtitle light sans smaller; axis labels very small.
- Device mockup: tablet with white bezel, rounded corners, soft drop shadow on light grey page.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 71.

## Annotation & narrative patterns
- Insight-style two-line headline contrasting groups ("While most… , US shows…"), followed by a descriptive subtitle stating scope and year.
- Tooltip provides on-demand detail (exact value) rather than labelling every bubble.
- Shaded region used as a non-text annotation to group the referenced cluster.
- No source/footnote shown on the chart.

## Other notes
- Sidebar ends with a pointer to a separate UI styling guideline document.
