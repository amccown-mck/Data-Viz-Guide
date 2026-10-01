---
still: 45
page: 70
section: Format
title: Screen sizes
page_type: responsive
chart_types: [stacked column, stacked bar, multi-line chart, heatmap]
---
## Intent
How to adapt charts built for print / large-screen presentation to mobile. Sidebar sub-heading "Mobile considerations": pare graphs down to essentials and use a mobile-optimized layout so users can read them intuitively on a phone. Four panels: Resizing and orientation; Adjusting hierarchy; Reducing chart complexity on mobile; Ensure legibility. All four are marked Recommended (no "avoid" examples on this page).

## Guidance (paraphrased, every rule stated on the page)
- Resizing and orientation: design mobile charts for the phone's portrait aspect ratio so content can be consumed by scrolling vertically.
- Adjusting hierarchy: when simplifying for mobile, consider swapping direct line labels for a key/legend; the insight text can also move to the top of the chart instead of being anchored at the data point.
- Reducing chart complexity on mobile: cut and simplify chart elements to remove clutter. Instead of keying every line, show a single highlighted line, put the insight inside the chart next to it, and push the other lines to grey in the background.
- Ensure legibility: reduce the number of type elements (primary headline, insights, axis labels, footnotes) on small screens; this may also mean simplifying the key's text.

## Examples marked Recommended
- Resizing and orientation — desktop landscape stacked column chart (~10 columns, dark navy / bright blue / mid blue / light cyan segments) re-cast as a horizontal stacked bar chart inside a phone frame (countries listed vertically: Sweden, Canada, Norway, Ireland, Italy, US, New Zealand, Finland, Singapore, Australia; Italy label bolded), titled "The House wins in Italy" with a small subhead. Works because categories stack vertically and scroll naturally in portrait.
- Adjusting hierarchy — magnified-circle callout of a desktop multi-line chart (legend row: Natural Gas, Oil, Nuclear, Wind, Solar, Tidal; insight "Oil ramp up" with short explanation; BTU axis, quarters Q1 '17–Q4) beside a phone version where the legend sits at top as a key and the insight text sits above the chart. Works because it frees the plot area from label clutter on a narrow screen.
- Reducing chart complexity on mobile ("Recommended options", two phone mockups):
  - Option 1: descriptive title "US primary energy consumption, 2016-2018 (Quadrillion BTU)", full key of six sources, insight "Oil ramp up" above chart, multiple colored lines with shaded highlight band.
  - Option 2: insight headline "While most energy sources consumption are steady, oil is more volatile" plus descriptive subtitle; one black highlighted line (oil), others grey in background, "Oil ramp up" annotation placed inside the chart next to a shaded vertical band. Works because only one series competes for attention and no key is needed.
- Ensure legibility — magnified circle over a dense desktop heatmap (tiny sub-industry labels: Payments, Photo, Advertising, Communication, Customer mgmt, Gaming, Wellness, Navigation, Security, Social, Travel, Video; key "No. of deals" 0, 1, 10–70+; tiny footnote text) vs. a phone version with larger insight headline "Photo and payments show consistently positive results across the years", subtitle "Mobile quarterly financing history by sub-industry, 2012-2017", simplified key (0, 1, …, 70+) and fewer, larger labels. Works because fewer, larger text elements remain readable.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Color roles: dark navy/near-black, bright/electric blue, royal blue, mid blue, light cyan used as categorical series; in the simplified mobile line chart the highlighted series is black and the rest are light grey; light grey vertical shaded band marks the time period of interest. Heatmap uses a sequential ramp from light grey (0) through cyan/blue to dark navy (70+).
- Axes: minimal; light tick labels, thin baselines, faint or no gridlines. Line chart y-axis labeled "BTU" at top-left; x-axis quarters (Q1 '17, Q2, Q3, Q4, Q1 '18, Q2).
- Labels: legends rendered as short line swatches + name in a row across the top (keys). Heatmap key is a horizontal color strip labelled "No. of deals".
- Mobile mockups drawn as light-grey outlined phone frames with rounded corners; magnifier circles with drop shadows used to show detail of the desktop version.
- Horizontal bar version: category labels left-aligned, value axis (0, 250, 500, 750, 1,000) across the top; a thin vertical reference line appears to the right near Italy.
- Typography: page title in a serif ("Screen sizes") with small sans eyebrow "Format"; panel titles in medium-weight sans; body copy in light sans; chart titles in bold sans with lighter subtitles. Check-mark icon (blue circle with white tick) precedes "Recommended".
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 70.

## Annotation & narrative patterns
- Mobile examples progress from descriptive title ("US primary energy consumption, 2016-2018") to insight headline ("While most energy sources consumption are steady, oil is more volatile"; "Photo and payments show consistently positive results across the years").
- Short bold insight label ("Oil ramp up") + 1–2 lines of explanatory text; placed either above the chart (hierarchy panel) or inline next to the highlighted line (complexity panel).
- Units given in the subtitle in parentheses ("(Quadrillion BTU)").
- Footnotes on desktop heatmap are tiny and illegible; mobile versions drop or reduce them.

## Other notes
- Some small in-chart text (desktop heatmap row labels beyond those listed, footnote lines, bar-chart subtitle) is illegible at this resolution.
