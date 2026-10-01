---
still: 15
page: 40
section: Part-to-whole
title: Treemap
page_type: chart-type
chart_types: [treemap]
---
## Intent
Introduces the treemap for part-to-whole questions involving hierarchical (tree-structured) data — e.g., how a total splits across groups and sub-groups (regions → countries). Suitable when showing relative size of many parts nested within categories; exact comparison of similar-sized parts is not its strength (not stated on page, but implied by area encoding).

## Guidance (paraphrased, every rule stated on the page)
- A treemap shows hierarchical data as nested rectangles; each branch gets a rectangle, which can in turn be subdivided into smaller rectangles for its sub-branches.
- Each rectangle's area is proportional to a chosen data value.
- Rectangles are typically colored to indicate a separate value or a category.
- Callout (left of chart): arrange rectangles from largest at the top-left to smallest at the bottom-right.
- Callout (left of chart): area encodes value; labels are placed directly inside each rectangle.
- Callout (right of chart): fill color reflects the category each rectangle belongs to.

## Examples marked Recommended
- No explicit Recommended/Avoid verdicts; the single annotated example serves as the reference.
- Treemap "US is leading the investment market" — investment by country grouped into three regions (Americas, Europe, Asia); largest block (US) at top-left, direct labels inside rectangles, region shown by color — makes the dominant part and regional grouping obvious at a glance.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Data shown (as labeled): Americas — US 3,332m; Brazil 644m; Canada 511m. Europe — Germany 1,084m; Russia 668m; UK 618m; France 520m; Italy 519m. Asia — Japan 1,269m; India 528m.
- Layout: Americas block on the left (US large on top, Brazil and Canada beneath); Europe block top-right (Germany tall on left, Russia/UK stacked, France/Italy stacked); Asia block bottom-right (Japan wide, India narrow).
- Color roles: 3 categorical colors from the blue family — dark navy = Americas, bright sky/cyan blue = Europe, electric/royal blue = Asia. Thin white gutters separate rectangles.
- Axes / gridlines: none (not applicable).
- Labels: direct labels in white inside each rectangle, top-left aligned; value on the first line in bold (e.g., "3,332m"), country name below in regular weight. Numbers use thousands separator and lowercase "m" suffix; currency unit stated once in the subtitle "(USD)".
- Legend: vertical list with small square swatches (Americas, Europe, Asia) placed to the right of the treemap, aligned with its top.
- Sort order: largest to smallest from top-left toward bottom-right (per callout); within groups, larger countries placed first.
- Typography: page title "Treemap" large bold serif; eyebrow "Part-to-whole" small bold sans. Chart headline bold sans, larger; subtitle regular sans, somewhat smaller ("Investments globally, 2017 (USD)"). Labels small sans. Footnote and source very small light grey sans.
- Page structure: left white sidebar holds the explanatory text; main light-grey area holds a white chart card with a subtle drop shadow; annotation callouts sit outside the card, each topped by a thin grey horizontal leader line pointing toward the chart.

## Annotation & narrative patterns
- Headline is an insight statement ("US is leading the investment market"), followed by a descriptive subtitle giving measure, scope, year and unit.
- Footnote block below a thin grey rule at the card bottom: an asterisked placeholder line for footnotes/methodology, then "Source: mckinsey.com/insights".
- Designer callouts in the page margins explain encoding choices (ordering, area/labeling, color).
- Footer: "McKinsey & Company" | "Data Visualization Guidelines" | "Version 01" | "19.07.18" | page "40".

## Other notes
- Colors distinguish categories rather than a quantitative value in this example, even though the text notes color can also encode a separate value.
