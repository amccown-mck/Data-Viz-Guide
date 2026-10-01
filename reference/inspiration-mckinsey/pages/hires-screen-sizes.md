---
source: hires_screen-sizes
page: ? (no printed page number visible; footer reads "Data Visualization Guidelines")
section: Format — Mobile considerations
title: Screen sizes
---
## Intent
How to adapt charts built for print / large screens to mobile: reorient for portrait scrolling, re-order hierarchy (key and insight placement), reduce series complexity, and keep type legible. Four "Recommended" panels each pair a desktop/print chart with its mobile adaptation (shown in phone outlines, some with a magnifier lens to show detail).

## Full structure / taxonomy (if any)
- **Format → Screen sizes → Mobile considerations**
  1. Resizing and orientation — Recommended
  2. Adjusting hierarchy — Recommended
  3. Reducing chart complexity on mobile — Recommended options
  4. Ensure legibility — Recommended

## Guidance (paraphrased, exhaustive)
- Left rail: reducing print/large-screen charts to their essentials lets mobile users grasp the chart intuitively via a layout optimised for the device.
- Resizing and orientation: design for the phone's portrait ratio so the chart scrolls vertically (e.g., rotate vertical columns into horizontal bars).
- Adjusting hierarchy: as charts get simplified, swap direct labels for a key; the insight can move to the top of the chart instead of being anchored at its data point.
- Reducing chart complexity: cut and simplify elements to remove clutter. Instead of keying every line, show only one highlighted line, grey the others into the background, and place the insight inside the chart next to the highlighted feature.
- Ensure legibility: reduce the number/amount of type elements (headline, insights, axis labels, footnotes); simplify key text as well.

## Recommended examples — what & why
1. **Resizing and orientation**
   - Desktop: vertical stacked bar chart (Italy gambling example: 10 countries, 5 segments, y-axis 0/250/500/750/1,000 with gridlines, callout line above Italy bar).
   - Mobile (portrait phone): same data as **horizontal** stacked bars; countries as rows top→bottom (Sweden, Canada, Norway, Ireland, **Italy** bold, US, New Zealand, Finland, Singapore, Australia); value axis 0/250/500/750/1,000 across the **top**; vertical gridlines; insight call-out "The House wins in Italy" + short explanatory line at top; small marker line beside Italy row. Why: portrait fit, vertical scrolling, long labels fit.
2. **Adjusting hierarchy**
   - Magnifier view of desktop line chart top: key laid out horizontally (Natural Gas, Oil, Nuclear / Wind, Solar, Tidal), then insight "Oil ramp up" with text that oil consumption rose toward end-2017 due to US tariff policy changes, then axis "BTU", quarters Q1 '17, Q2, Q3, Q4 …
   - Mobile: compact key at top (Natural Gas, Oil, Nuclear, Coal / Wind, Solar, Tidal — 7 series), insight block moved above the plot, multi-line chart below with grey shaded band marking Q4 '17–Q1 '18. Why: direct labels don't fit; key + top-positioned insight preserves hierarchy.
3. **Reducing chart complexity on mobile** (two phone options)
   - Option A: plain title "US primary energy consumption, 2016-2018 (Quadrillion BTU)", full 7-series key, insight "Oil ramp up" above plot, all lines coloured, shaded band.
   - Option B: insight headline "While most energy sources consumption are steady, oil is more volatile" + same descriptive subtitle; only oil drawn as a dark highlighted line, other series light grey; no full key; "Oil ramp up" annotation placed inside the plot beside the shaded band. Why: one highlighted line + in-chart insight removes clutter.
4. **Ensure legibility**
   - Desktop heatmap (magnified): "Photo and payments show consist[ently…]" / "Mobile quarterly financing history by sub[-industry]"; key "No. of deals" with graduated scale 0, 1, 10, 20, 30, 40, 50, 60, 70+; rows (sub-industry): Payments, Photo, Advertising, Communication, Customer mgmt, Gaming, Wellness, Navigation, Security, Social, Travel, Video; tiny type throughout.
   - Mobile: larger headline "Photo and payments show consistently positive results across the years"; subtitle "Mobile quarterly financing history by sub-industry, 2012-2017"; key simplified to endpoints (0, 1, 70+); year columns '12–'17; row labels at readable size (Payments, Photo, Advertising, Communication, Customer mgmt, …). Why: fewer, larger text elements and a simplified key.

## Try to avoid examples — what & why
No explicit "Try to avoid" markers on this page. Implicitly: desktop layouts shown for contrast — landscape column charts, direct labelling of many series, fully keyed multi-line charts, and dense small type — are unsuitable for mobile as-is.

## Visual specifics (colors & roles, axes, labels, sort, spacing ratios, strokes, typography hierarchy)
- Page: white left rail (eyebrow "Format" small sans; title "Screen sizes" serif display; sub-head "Mobile considerations" bold sans + body), grey main area with 2×2 white panels.
- Panel headings in medium-weight sans, large; "Recommended" marker = blue filled circle with white check + bold label; thin grey rule above marker row.
- Phone devices drawn as light grey rounded-rectangle outlines, cropped at the panel's bottom rule.
- Magnifier: circular lens with drop shadow enlarging part of the desktop chart to show type detail.
- Stacked bar palette as in bar pages: Deep Blue navy, royal blue, bright cyan, pale cyan, steel teal; highlighted category label bold (Italy).
- Line charts: highlighted series black/near-black; others in blues/cyans; in simplified version non-focus lines light grey; vertical light-grey shaded band highlights a time window (Q4 '17–Q1 '18).
- Key style for lines: short coloured line segment + label, arranged horizontally in rows.
- Heatmap: sequential scale from light grey (0) through pale cyan to Deep Blue navy (70+); white gaps between cells.
- Axis for mobile bars moved to top of chart; y-axis title "BTU" placed at top-left of the line plot (horizontal, not rotated).
- Typography hierarchy on mobile: headline (bold, largest) > descriptive subtitle (regular) > key/insight title (bold small) > insight body (small regular) > axis ticks (smallest, grey).

## Numeric specs observed
- Bar axis: 0, 250, 500, 750, 1,000.
- Line chart: y 1–4 (BTU, quadrillion); quarters Q1 '17 → Q2 '18 (6 quarters); 7 energy series (Natural Gas, Oil, Nuclear, Coal, Wind, Solar, Tidal).
- Heatmap key bins: 0, 1, 10, 20, 30, 40, 50, 60, 70+ (desktop) → 0, 1, 70+ (mobile); years 2012–2017; 12 sub-industries on desktop.
- No breakpoints, pixel widths or font sizes printed; only "portrait ratio" stated qualitatively.

## Annotation & narrative patterns
- On mobile, insight moves to the top (above plot) or into the plot next to the single highlighted feature, rather than anchored via leader line.
- Descriptive title can be upgraded to an insight headline when simplifying (Option B), with the descriptive line demoted to subtitle.
- Highlight + grey-out ("one line in focus") replaces full legend.

## Other notes
- Small tick labels in desktop thumbnails and footnote text inside heatmap are illegible.
- Faint footer text beyond "Data Visualization Guidelines" illegible.
