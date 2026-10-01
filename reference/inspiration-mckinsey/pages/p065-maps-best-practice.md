---
still: 40
page: 65
section: Geo-spatial
title: Maps best practice
page_type: chart-best-practice
chart_types: [choropleth map, dot density map, base map]
---
## Intent
- This page collects map best practices in four panels: choosing the right base map, choosing colors, setting value ranges (legend bins), and considering different display options.
- It applies to the Geo-spatial chart family (choropleth, bubble, and dot density maps).

## Guidance (paraphrased, every rule stated on the page)
- **Choosing the right map**
  - Avoid base maps with heavy boundary lines, base maps that draw too much attention, and maps that distort proportions.
  - Use light grey fills with white outlines for boundaries so the data stands out on screen.
  - For print, consider darker outlines, because white outlines may not print clearly.
- **Selecting appropriate colors**
  - Avoid colors that are not in the McKinsey palette.
  - Watch out for colors that stand out more than others, because they give some data more weight than it deserves.
  - To show intensity, use a sequential continuous palette or a diverging palette.
- **Ranges**
  - When building intensity steps, do not use ranges that overlap or are uneven.
  - Choose three to five numeric ranges that split the data fairly evenly.
  - Use +/- signs to open-end the highest and lowest ranges (e.g. "56+").
- **Explore display options**
  - A map can show data in more than one effective way, and a single map is not always best.
  - Option one: plot both categories on one map, told apart by color.
  - Option two: split into two maps side by side, which can make differences in distribution easier to see.

## Examples marked Recommended
- Light grey US base map with faint white state outlines. It is quiet, so data layered on top will stand out.
- County choropleth in a sequential blue palette, from pale cyan to dark navy. The single hue ramp shows intensity clearly and stays within the brand palette.
- Legend "Age groups" with 5 bins: 56+, 49 - 56, 42 - 49, 36 - 42, 29 - 36. The bins are roughly even in width (about 6–7 years each), and the top bin is open-ended with "+".
- Option one (check mark): a single dot map with two categories, A in bright blue and B in dark navy, and a small dot legend at bottom-left. This is one valid way to compare two groups.
- Option two (check mark): two small side-by-side maps labelled A and B, each with dark dots. Splitting the maps makes each group's distribution easier to read. Both options have check marks; neither is marked as better.

## Examples marked Try to avoid / Not recommended
- **Try to avoid:** a solid dark navy filled US map with thick white state borders. The base map is too heavy and would compete with any data drawn on it.
- **Try to avoid:** a county map in off-palette colors (pale salmon/peach with scattered grey counties). The colors are not in the brand palette, and some hues pop more than others, which adds unintended emphasis.
- **Avoid** (red/pink X icon, a different icon from the dark "Try to avoid" X): legend "Age groups" with bins 60- 62, 58- 59, 42 - 58, 41 - 42, 29 - 36. The ranges are uneven: one is 16 years wide, another is 1 year. The bins also leave a gap: nothing covers 36–41. The result is misleading intensity steps.

## Visual specifics observed
- Layout is a 2×2 grid of white panels on a light grey page. Each panel has a bold sans heading at top-left and two examples side by side. Under each example is a thin grey rule, then a status icon with a bold label and a short explanation.
- Status icons:
  - Dark navy circle with a white X means "Try to avoid".
  - Bright blue circle with a white check means "Recommended", "Option one", or "Option two".
  - Red/pink circle with an X means "Avoid" (used only in the Ranges panel).
- The recommended base map uses a very light grey fill and white borders.
- The recommended color palette is sequential single-hue blue. Dark navy is used for the highest values.
- Legend style: small square swatches stacked vertically, highest value at the top. Labels are grey sans with spaced hyphens ("49 - 56"). The legend title is regular sans.
- In the dot maps, dots are very small. In Option one, category A is bright blue and category B is dark navy. The A and B legend labels are tiny and barely legible.
- Typography: the page title "Maps best practice" is a large serif set on two lines, with a small bold sans eyebrow "Geo-spatial" above it. Panel headings are medium-bold sans. Status labels are small bold sans. Explanations are small regular sans.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 65.

## Annotation & narrative patterns
- There are no chart headlines on this page. It is a rules page, so each example is paired with a short do/don't label and a one- or two-sentence rationale.
- There are no source or footnote lines on the examples.

## Other notes
- The "Avoid" label and red icon in Ranges differ from the "Try to avoid" label and dark icon used elsewhere on this page. This may signal a stronger prohibition, but the page does not explain the difference.
- The page mentions diverging palettes as acceptable but does not show one.
- The print guidance (use darker outlines) is text only; no example is shown.
