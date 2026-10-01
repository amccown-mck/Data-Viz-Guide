---
still: 33
page: 58
section: Relationships
title: Parallel coordinates
page_type: chart-type
chart_types: [parallel coordinates]
---
## Intent
Shows how records behave across many variables at the same time, for high-dimensional or multivariate analysis. Use it to follow one category or cluster across several measures. It works like a multi-axis line chart, but the axes are separate variables, not points in time, so the axis order is a design choice rather than a given.

## Guidance (paraphrased, every rule stated on the page)
- Parallel coordinates are a standard way to show high-dimensional geometry and analyze multivariate data.
- The chart is closely related to a time-series line chart. The difference is that each axis is a different variable, not a moment in time, so the axes have no natural order.
- Side annotation 1: the first axis (leftmost) should carry the story. In the example that is Cylinders, and the eight-cylinder cars are the focus.
- Side annotation 2: color only one cluster in the brand dark blue and leave everything else in light grey. This highlights one category (eight-cylinder cars) and lets the reader follow how it performs across the other axes.

## Examples marked Recommended
- A single example chart, not explicitly labeled Recommended but shown as the model. It is a parallel coordinates plot of cars across 7 axes: Cylinders, Miles per gallon, Displacement, Horsepower, Weight (lb), Acceleration (sec), Year. Eight-cylinder cars are drawn in dark navy and all other cars are faint light grey. This works because one highlighted cluster cuts through the dense overplotting and makes the story readable.

## Examples marked Try to avoid / Not recommended
- None shown on this page.

## Visual specifics observed
- Color roles: dark navy/near-black blue (brand dark blue) = highlighted cluster. Very light grey = all other records, pushed into the background. The navy lines vary in opacity/shade (darker to mid grey-blue), which suggests transparency where lines overlap. Effectively 1 hue plus grey.
- Axes: 7 thin vertical light-grey axes spaced evenly. The min value sits in small grey type below each axis and the max value above it. Examples: Cylinders 3–8, with extra ticks at 4, 5 and 6 on the left; MPG 0–45; Displacement 50–450; Horsepower 0–220; Weight 1,500–5,000; Acceleration 8–25; Year 1970–1982. No horizontal gridlines.
- Axis names sit centered below each axis in regular sans type, darker than the tick values.
- Thin lines (roughly 1px), with no markers at the axis crossings.
- Two annotation callouts sit above the plot: a bold short heading, a regular-weight explanation underneath, and a thin dark horizontal rule under the text marking which axes it refers to. Left callout "Heavy beasts" spans Cylinders→MPG (paraphrase: eight-cylinder cars average low MPG). Right callout "They don't make'em like they used to" spans Acceleration→Year and is right-aligned (paraphrase: eight-cylinder cars were more popular until 1979).
- Number formats: thousands separator with comma (1,500; 5,000). Units go in parentheses in the axis names (lib [sic, likely lb], sec).
- Chart card: white panel with a soft drop shadow on a light grey page background. A thin horizontal rule separates the chart from the footnote area.
- Typography: the page title is in a large serif. The eyebrow "Relationships" is small bold sans. Page body text is regular sans. The chart headline is bold sans, the subtitle is regular sans at a lighter weight and slightly smaller, and the footnotes are very small grey sans.

## Annotation & narrative patterns
- Headline states the insight: "Eight-cylinder cars are disappearing from the market". The subtitle describes what is plotted and the year (2017).
- The in-chart callouts use a short, casual bold hook with a plain-language finding underneath, placed directly above the relevant axes.
- Footnote placeholder with an asterisk for methodology notes, then a "Source:" line (mckinsey.com/insights) in small grey text below the rule.
- Page-level side notes connect to the chart with thin horizontal leader lines that point toward it.

## Other notes
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 58.
- The weight axis label reads "Weight (lib)" as printed. This is likely a typo for lb.
