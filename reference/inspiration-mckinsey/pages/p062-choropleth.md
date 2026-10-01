---
still: 37
page: 62
section: Geo-spatial
title: Choropleth
page_type: chart-type
chart_types: [choropleth map, magnifier/lens inset]
---
## Intent
- Geo-spatial charts (per the black callout box) are for cases where it matters to show exact locations or patterns across geography.
- A choropleth shades each area according to the value of a measured variable (examples given: population density, income per person).
- Use it to show how one measure changes across a geographic area.
- Caveat stated: the physical size of areas can skew how the data is perceived (large regions visually dominate regardless of value).

## Guidance (paraphrased, every rule stated on the page)
- Choropleth = regions filled in proportion to the variable's value.
- Good for an easy read of how a measure varies across geography.
- Be aware that geographic area size can distort perception of the data.
- Side annotation: when coloring regions, a sequential (continuous) palette is an efficient way to encode value differences between regions.
- Side annotation: a magnified lens can zoom in on relevant areas.

## Examples marked Recommended
- No explicit "Recommended" / "Try to avoid" label on this page; one exemplar chart is shown.
- US county choropleth of median age, 2017 — sequential single-hue blue ramp encodes value; a circular magnifier callout isolates the single most notable county with an explanatory note.

## Examples marked Try to avoid / Not recommended
- None shown on this page.

## Visual specifics observed
- Color roles: single-hue sequential blue ramp, 6 bins; lightest pale cyan = youngest (22–29), progressively deeper blues, near-black navy = oldest (56–62). The highlighted county (Harding, NM) appears in the darkest navy/black within the lens.
- Legend: title "Age groups"; small square swatches stacked vertically, ordered highest (56–62) at top to lowest (22–29) at bottom; bin labels in small grey sans: 56 - 62, 49 - 56, 42 - 49, 36 - 42, 29 - 36, 22 - 29. Legend placed top-right of map, not overlapping it.
- Bins share endpoints (e.g. 49 - 56 and 56 - 62) — boundary handling not specified on the page.
- No axes/gridlines (map). County borders drawn as thin white strokes separating fills.
- Magnifier: thin white circle outline drawn on the map at the location (New Mexico area); an enlarged circular inset placed to the right of the map, next to its annotation text.
- Annotation block beside lens: bold short heading "The oldest US County" + 3-line regular-weight explanation (Harding, New Mexico; median age above 56).
- Chart card: white panel with subtle drop shadow on a light grey page background.
- Thin grey horizontal rule separates the chart body from footnote/source.
- Typography: page title "Choropleth" in large serif; eyebrow "Geo-spatial" in small bold sans above it. Chart headline in bold sans (largest in chart), subtitle in regular/light sans slightly smaller, legend and footnote in small light grey sans. Side annotations in small sans with thin grey leader rules.
- Left description panel: black box with white text for the category definition; body text in regular sans.
- Footer: "McKinsey & Company", "Data Visualization Guidelines", "Version 01", "19.07.18", page number "62" at bottom right.

## Annotation & narrative patterns
- Headline is an insight statement ("The North and South-West are ageing quicker than the East Coast"), followed by descriptive subtitle (metric, geography, year: "Median age across US Counties, 2017").
- Callout: magnified lens + bold mini-heading + short explanatory sentence to spotlight an outlier.
- Footnote line (placeholder: footnotes/methodology details go here, expand where necessary) and "Source: mckinsey.com/insights" in small grey text at bottom-left of card.

## Other notes
- Page introduces the Geo-spatial family ("Geo-spatial charts are used when it's relevant to highlight precise locations or geographical patterns" — paraphrased in Intent).
- Workforce adaptation idea: sequential single-hue choropleth for talent supply/attrition by metro, with a lens on the outlier location.
