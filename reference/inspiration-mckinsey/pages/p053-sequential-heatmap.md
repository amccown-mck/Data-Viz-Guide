---
still: 28
page: 53
section: Correlation
title: Sequential heatmap
page_type: chart-type
chart_types: [sequential heatmap]
---
## Intent
A heatmap represents each value in a matrix by color intensity; it is useful for seeing variation across several variables and spotting patterns/correlations. A sequential heatmap is the variant to use when the reference value sits at one end of the data range (e.g. zero deals up to many deals).

## Guidance (paraphrased, every rule stated on the page)
- Heatmaps encode matrix values via color variation to reveal variance and correlation patterns across multiple variables.
- A sequential heatmap uses a sequential continuous color palette; choose it when the reference point is at one extreme of the range.
- Assign a neutral color to zero/null values.
- Typically the darkest shade stands for the highest value (e.g. most deals) and the lightest shade for the lowest.
- Rows (sub-industries) are ranked/ordered (margin note says ranked from highest increase to highest decrease — see Other notes about wording).
- A sequential continuous palette suits encoding a count such as number of deals by sub-industry.

## Examples marked Recommended
- Single annotated exemplar (no explicit Recommended/Avoid labels): heatmap "Photo and payments show consistently positive results across the years" — mobile quarterly financing history by sub-industry, 2012–2017; rows = 12 sub-industries, columns = quarters; color = number of deals.

## Examples marked Try to avoid / Not recommended
- None shown on this page.

## Visual specifics observed
- Color roles: light grey = 0 (neutral null value); blue ramp from very pale sky blue (low) through bright blue and teal-blue to deep navy/near black (high, 70+). Single-hue family plus grey.
- Legend: titled "No. of deals", placed top-right above the matrix; separate grey swatch labeled 0, then a stepped 7-swatch blue bar with tick labels 1, 10, 20, 30, 40, 50, 60, 70+. Although described as continuous, the legend renders as discrete steps.
- Matrix: 12 rows — Payments, Photo, Advertising, Communication, Customer mgmt, Gaming, Wellness, Navigation, Security, Social, Travel, Video (top to bottom); approx. 24 columns (4 quarters × 6 years). Square-ish cells separated by thin white gutters. No values printed in cells.
- Row header: bold "Sub-industry" label above the left-aligned row labels.
- X-axis: year labels only at the first quarter of each year: '12, '13, '14, '15, '16, '17, in small light grey; no gridlines or axis lines.
- Sort: rows ordered so that darker (higher-deal) rows sit at the top (Payments, Photo) and lighter rows at the bottom (Travel, Video).
- Layout: white sidebar at left with section label, serif title, and two explanatory paragraphs; chart in a white card with soft shadow; margin annotations left and right of the card attached with thin leader rules.
- Typography: page title large serif; chart headline bold sans; subtitle regular sans; row labels small sans; legend and axis labels smallest light grey.

## Annotation & narrative patterns
- Insight headline ("Photo and payments show consistently positive results across the years") + descriptive subtitle (measure, scope, date range).
- Footnote block under a thin rule: placeholder asterisked footnote/methodology line, then "Source: mckinsey.com/insights".
- Margin notes explain row ranking and palette choice.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | 53.

## Other notes
- The left margin note refers to ranking by "pollution levels", which does not match the chart's deal-count data — appears to be leftover placeholder copy in the source guide.
- Exact column count is estimated from cell spacing (~24); individual cell values are not legible/not labeled.
