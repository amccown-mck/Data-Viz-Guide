---
still: 12
page: 37
section: Part-to-whole
title: Waterfall chart
page_type: chart-type
chart_types: [waterfall]
---
## Intent
- Shows how a series of positive or negative values, added one after another, builds up to a running total.
- Use it to break a total into sequential contributing steps, including intermediate subtotals.

## Guidance (paraphrased, every rule stated on the page)
- A waterfall chart helps readers understand the combined effect of values added in sequence, whether positive or negative.
- Underneath, a waterfall is a stacked bar chart with two series:
  - The visible series is the data being shown.
  - The invisible series is a spacer that "floats" each bar above the previous cumulative amount, so readers can see how the total changes.
- Annotation: incremental bars use the brand's "Deep Blue", and bars showing the full amount required (totals) use the brand's "Active Blue".
- Annotation: thin connecting lines between bars help readers follow the increments. Keep them light so they don't distract or add clutter.
- Annotation (right): place insight text next to the tallest bars.

## Examples marked Recommended
- There are no explicit "Recommended" or "Not recommended" tags. The single example is presented as the model to follow.
- The chart is titled "Saving for retirement", subtitle "Breakdown of financial needs in the future, 2017 (GBP)". It has 8 columns, left to right:

  | Column | Bar type | Value |
  |---|---|---|
  | Child education | Increment | +3,000 |
  | House purchase | Increment | +6,000 |
  | Car purchase | Increment | +1,000 |
  | **Required by age 50** | Total | 10,000 |
  | Child marriage | Increment | +1,000 |
  | After retirement | Increment | +10,000 |
  | Emergency | Increment | +3,000 |
  | **Required by age 80** | Total | 24,000 |

  An insight block beside the final bar reads **"Saved away"**, with a short note that an additional £14,000 is needed over the last 30 years, which makes planning harder after age 50.
- It works because:
  - There are two clear color roles.
  - The subtotal checkpoint appears partway through the sequence.
  - Values are labeled directly on every bar.
  - The insight is placed right where the peak is.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- **Colors**: 2 in total.
  - Near-black dark navy ("Deep Blue"): increment bars.
  - Bright cyan/sky blue ("Active Blue"): total/subtotal bars.
- **Legend**: at top left of the plot, with small square markers labeled "Increment" (dark) and "Total" (blue). It is stacked vertically.
- **Axes and gridlines**:
  - There is no y-axis line, no y-axis tick values except a single "0" at the baseline, and no gridlines.
  - A thin grey horizontal baseline runs at zero.
- **Connectors**: thin light-grey horizontal lines run from the top of each bar to the start of the next bar.
- **Bars**: equal widths. The gaps between bars are roughly equal to or slightly smaller than the bar width. Every value is positive, so the chart steps upward.
- **Value labels**:
  - They sit directly above each bar.
  - Increments show a "+" prefix and a thousands separator, in regular weight (e.g., "+6,000").
  - Totals are **bold** with no sign (e.g., "10,000", "24,000").
- **Category labels**:
  - Centered under each bar and wrapped to 2 lines where needed.
  - The labels for the total columns are **bold** ("Required by age 50", "Required by age 80"). The rest are regular.
- **Units**: GBP appears in the subtitle only. There is no currency symbol on the bar labels, although the insight text uses "£".
- **Insight block**: a bold short heading ("Saved away") with a small regular-weight paragraph beneath. It sits to the right of the final total bar, aligned with its top.
- **Typography**:
  - Chart title: bold sans serif, descriptive.
  - Subtitle: regular, lighter and smaller.
  - Page title: large serif ("Waterfall chart"); eyebrow: small bold sans serif ("Part-to-whole").
  - Footnote/source: smallest size, grey.
- **Layout**: the chart sits on a white card with a soft shadow over a light grey page. Side annotations are attached to the card with thin horizontal leader lines.

## Annotation & narrative patterns
- The headline is descriptive (a topic), not an insight. The insight is carried by the "Saved away" callout next to the tallest bar.
- Footnote placeholder text: "*Footnotes, explanations or additional details of methodology go here. Expand where necessary." The next line is "Source: mckinsey.com/insights". Both sit below a hairline rule.
- Page footer: "McKinsey & Company", "Data Visualization Guidelines", "Version 01", "19.07.18", and the page number 37.

## Other notes
- The page names two brand colors: "Deep Blue" (dark navy) and "Active Blue" (bright cyan). This page gives no hex values.
- The example includes only increases. The page does not show how to treat negative or decrease bars.
