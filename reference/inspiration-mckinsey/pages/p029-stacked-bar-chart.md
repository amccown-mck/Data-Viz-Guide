---
still: 04
page: 29
section: Magnitude
title: Stacked bar chart
page_type: chart-type
chart_types: [stacked bar chart, stacked column chart]
---
## Intent
Covers the stacked (vertical) bar chart in the Magnitude family. Use it to compare several categories when each total is made of sub-categories, so the reader sees both the total and how it splits. The page does not list any "when not to use" cases. It does warn that stacking makes direct labeling hard (see below).

## Guidance (paraphrased, every rule stated on the page)
Left-column body copy:
- Stacked bars help when comparing several categories of data.
- They layer several datasets on top of one another. This shows how a larger category divides into sub-categories and how each part relates to the total.

Annotations around the example chart:
- Add an insight call-out to frame the message and draw the eye to the key data point.
- Direct labeling is hard with stacked bars. Adding a gridded value axis with labels gives a clear way to read the bars. This is an exception to the bar-chart rule of removing axes.
- Stack the legend vertically, in the same order as the stacked segments, so it is easy to read.

## Examples marked Recommended
- A stacked vertical bar chart titled "Proportionally, Italy's gambling market relies heavily on gaming machines". It shows dollars lost per resident adult per year, 2017 (USD), for 10 countries, split into 5 gambling types. It is presented as the model example (not explicitly labeled "Recommended"). It works because:
  - The insight headline and the in-chart call-out both point at Italy.
  - Italy's category label is bold.
  - The gridlines and y-axis make the unlabeled segments readable.
  - The legend order matches the stack order.
  - Countries are sorted by total.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Data: countries left to right are Sweden, Canada, Norway, Ireland, Italy, US, New Zealand, Finland, Singapore, Australia. They are sorted ascending by total height (about 375 for Sweden up to about 1,000 for Australia; totals read off the gridlines, approximate). Italy's gaming-machines segment (about 250) is more than half of its total (about 440). Exact segment values are not labeled on the page.
- Color roles: 5 series, all in the blue family. Stack order from the bottom (baseline) to the top, with the matching legend order read from bottom to top:
  1. Gaming machines: very dark navy / Deep Blue (the story series, at the baseline so its length is easy to compare).
  2. Casino: bright azure / Active Blue.
  3. Betting: saturated royal/electric blue.
  4. Lotteries: pale light cyan.
  5. Online: muted steel/teal blue.
  - The legend lists top to bottom: Online, Lotteries, Betting, Casino, Gaming machines, so it mirrors the stack as it appears visually. Legend swatches are small squares with labels to their right. The legend sits in the top-right of the plot area, to the right of the last bar, aligned with the top of the bars. "Gaming machines" wraps onto two lines.
- Axes / gridlines / baseline: thin light-grey horizontal gridlines at 0, 250, 500, 750 and 1,000. Y-axis tick labels are small, grey, left of the plot, with a comma thousands separator ("1,000"). There is no vertical axis line. The baseline at 0 is the same weight as the gridlines.
- Labels: country labels are centered under the bars in regular sans. "Italy" is **bold**. There are no segment value labels. The unit (USD) is stated in the subtitle, not on the axis.
- Call-out: in the plot area above Italy's bar is a bold heading "The House wins in Italy" with 2 lines of regular text below it. The text paraphrases as: gaming machines were legalized only recently, yet the industry is booming. A short dark horizontal marker line sits under the call-out, at about the 1,000 gridline level above the Italy column. It is left-aligned with the call-out text.
- Spacing: bar width is roughly 2.5x the gap between bars. The segments stack with no visible gaps. Thin white separators between segments may be present but are unclear at this resolution.
- Card/layout: white chart card with a soft shadow on a light grey page. A thin rule separates the plot from the footnote. Grey leader rules link the guide notes (2 on the left, 1 on the right) to the card.
- Typography: same system as the bar chart page.
  - Page title: serif, with a small bold sans eyebrow "Magnitude" above it.
  - Chart headline: bold sans.
  - Subtitle: regular sans.
  - Call-out heading: bold, small (about label size); call-out body in regular weight.
  - Axis, legend and category labels: small.
  - Footnote/source: smallest, light grey.

## Annotation & narrative patterns
- The headline is insight-style and qualified ("Proportionally, ...") so the reader knows it is about share, not absolute size.
- Subtitle pattern: metric, then year, then unit in parentheses ("Dollars lost per resident adult per year, 2017 (USD)").
- An in-chart insight call-out (bold short title plus 1–2 sentences of context) is anchored near the focal bar. The bold category label reinforces the same point.
- Footnote block: a line marked with an asterisk (placeholder saying methodology details go here), then "Source: mckinsey.com/insights". Both are small and grey.

## Other notes
- Unlike the single bar chart, emphasis here does not come from a color highlight. All bars use the same 5-color scheme. Emphasis comes from the headline, the call-out and the bold axis label.
- Placing the story segment (Gaming machines) at the baseline in the darkest color makes it the easiest segment to compare across bars.
