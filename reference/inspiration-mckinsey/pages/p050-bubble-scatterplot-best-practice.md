---
still: 25
page: 50
section: Correlation
title: Bubble scatterplot best practice
page_type: chart-best-practice
chart_types: [bubble scatterplot, scatterplot, scatterplot with trend lines]
---
## Intent
Best-practice guidance for correlation charts (bubble scatterplots / scatterplots): how to apply color, and how many trend lines to overlay when showing relationships between two variables.

## Guidance (paraphrased, every rule stated on the page)
Panel "Using color on scatterplots":
- Option 1: Color can occasionally be acceptable for highlighting particular value ranges (marked with an X icon, i.e. the less-preferred option).
- Option 2: The preferred approach is to use color to encode an extra data variable (a category), with a legend (marked with a check icon).

Panel "Trend lines":
- Trend lines help show correlation/trends between variables, but too many of them make the chart hard to read.
- Keep comparisons to just a few trend lines at most.

## Examples marked Recommended
- Option 2 (check icon): bubble scatterplot where three colors (dark navy, bright/sky blue, deep royal blue) map to categories A, B, C shown in a small legend at right — color carries a real data variable rather than decoration.
- "Recommended" trend-line chart: same scatter data, but only two trend lines (dark navy and royal blue) are drawn with their points colored; the remaining series' points are pushed to light grey with no trend line — reduces clutter and focuses comparison.

## Examples marked Try to avoid / Not recommended
- Option 1 (X icon, framed as "sometimes okay"): bubble scatterplot where colors (navy, light blue, royal blue) appear to group points by x-range/region of the chart rather than by a data variable; no legend — acceptable only occasionally.
- "Try to avoid" trend-line chart: four series each with its own colored trend line (pale/light blue at top, dark navy, royal blue, bright blue at bottom) — too many lines crossing makes interpretation difficult.

## Visual specifics observed
- Colors: dark navy (near black), bright/sky blue, deep royal/electric blue; in the recommended trend chart, non-focus points are light grey (de-emphasis). Palette limited to 3 hues + grey.
- Axes: very light, thin gridlines in both directions; small light-grey tick labels. Y-axis labels appear as "0, 2m, 4m, 6m" (m = millions, small and faint); x-axis 0, 10, 20, 30. No bold axis lines.
- Bubbles: solid filled circles of varying size, no outlines, no transparency apparent.
- Trend lines: thin straight lines, colored to match their series.
- Legend: Option 2 uses a compact vertical legend at right (dot + letter A/B/C). Other charts have no legend.
- Layout: two white cards on a light grey page, each containing a pair of side-by-side examples; a thin rule separates chart from caption; caption has icon (dark circle with X / blue circle with check) + bold label + short body text.
- Typography: large serif page title (two lines, top-left) with small sans eyebrow "Correlation" above; card headings in medium sans; captions in small light sans.

## Annotation & narrative patterns
- Descriptive page and card headings (no insight headlines).
- Status labels "Option 1 / Option 2" and "Try to avoid / Recommended" with X / check icons.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page number 50 at bottom-right.

## Other notes
- Notably, the color panel uses "Option" labels instead of avoid/recommended, softening the guidance: range-highlighting color is permissible but encoding a variable is preferred.
