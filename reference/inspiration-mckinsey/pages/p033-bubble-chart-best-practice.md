---
still: 08
page: 33
section: Magnitude
title: Bubble chart best practice
page_type: chart-best-practice
chart_types: [bubble, vertical bar (as comparison)]
---
## Intent
When to pick bubbles versus bars, plus how to sort and color bubbles. Bubbles suit data with very large value ranges. Bars suit data where values are close together and small differences matter.

## Guidance (paraphrased, every rule stated on the page)
- When bubbles are better: if values differ enormously, a bar chart compresses the small values into near-invisible bars and becomes unhelpful for comparison. A bubble chart handles this more efficiently because it encodes value by area, not diameter.
- When bars are better: with data points of similar value, area-scaled bubbles make comparison hard. Bars show small differences better because they encode by length.
- Sorting bubbles: an arbitrary arrangement with no functional purpose can bury the key insight. Sort bubbles by size to surface the largest and smallest values and make comparisons easier.
- Coloring bubbles: don't use color for decoration or styling. Color is appropriate when it encodes categories, helping the viewer relate data points to each other.

## Examples marked Recommended
- When bubbles are better: three navy bubbles for A=10, B=110, C=2,730, labeled inside or beside with value and letter. All three values stay visible and comparable despite the roughly 270x range.
- When bars are better: three navy columns A=140, B=147, C=160 with value labels above. Length makes the small differences readable.
- Sorting bubbles: the disease-funding bubbles ($257m Breast cancer, $147m Prostate cancer, $54m Heart disease, then $23m Motor Neurone disease, $14m HIV, $7m Chronic Pulmonary disease, $4m Diabetes, $3m Suicide) are arranged in descending size across two rows, with the three largest on top and the five smallest in a row below. Rank order is immediately readable.
- Coloring bubbles: bubbles A–H in three colors tied to a small legend (Group 1, Group 2, Group 3). A and B are bright blue, C, D, F, and G are dark navy, and E and H are royal/deep blue. Color carries meaning (group membership).

## Examples marked Try to avoid / Not recommended
- When bubbles are better: bars for A=10, B=110, C=2,730. A and B are nearly flat and can't be compared.
- When bars are better: three almost identical navy bubbles for 140, 147, 160. Area differences are imperceptible.
- Sorting bubbles: the same disease bubbles scattered in a loose cluster with no size order (small bubbles top-left, large ones mixed in). The key insight is hidden.
- Coloring bubbles: bubbles A–H each in a different decorative color (textured purple/violet, bright blue, pale blue, pink, watermelon red, royal blue, navy, peach/salmon) with no legend. Color adds no meaning.

## Visual specifics observed
- Color roles: dark navy is the default. In the recommended coloring example the categorical palette is limited to three blues (navy, bright blue, royal blue) keyed by a legend. The "avoid" example uses about 8 hues, including non-blue accents (purple, pink, watermelon, peach).
- Legend: in the recommended coloring example, a small vertical legend with dot markers sits top-left. Elsewhere on the page, labels are direct.
- Labels: bubble labels are a small value over a category name, white text inside large bubbles and dark text below small bubbles. Disease values carry "$" and an "m" suffix, while the generic examples use plain integers with a thousands comma (2,730). Bar value labels sit above the bars. Many label strings in the mini charts are tiny; the values listed above are legible, and some category sub-labels are near the limit of legibility.
- Axes: the bar examples have no y-axis or gridlines, only small category letters under a baseline.
- Card structure: the same 2x2 grid of white cards as the bar best-practice page. Each card has a sans heading and two mini charts, with "Try to avoid" (dark circle X) on the left and "Recommended" (bright blue circle check) on the right, separated from the explanation by a hairline rule.
- Typography: the page title is a large serif on two lines ("Bubble chart / best practice"). The eyebrow "Magnitude" is small bold sans. Card headings are medium sans and callout text is small regular sans.
- Footer: "McKinsey & Company", "Data Visualization Guidelines", "Version 01", "19.07.18", page "33".

## Annotation & narrative patterns
- Headings frame each card as a decision ("When bubbles are better" / "When bars are better") or a technique ("Sorting bubbles", "Coloring bubbles").
- Each callout is a single short sentence stating the risk or the benefit.
- The example charts have no headlines or sources.

## Other notes
- The disease-funding data reuses the p.32 bubble example, with "$" prefixes added here.
- Chart choice depends on the spread of the data: a wide spread favors bubbles and a narrow spread favors bars.
