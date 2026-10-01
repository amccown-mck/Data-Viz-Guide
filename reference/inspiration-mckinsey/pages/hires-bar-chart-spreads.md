---
source: hires_bar-chart-spreads
page: 28–31 (composite of four pages: 28 Bar chart, 29 Stacked bar chart, 30 Bar chart variants, 31 Bar chart best practice)
section: Magnitude
title: Bar chart / Stacked bar chart / Bar chart variants / Bar chart best practice
---
## Intent
Four-page run covering the Magnitude family's bar charts: anatomy of a single-series bar chart (p28), anatomy of a stacked bar chart (p29), four alternative bar formats and when to use each (p30), and four do/don't pairs on bar sizing, colour, labelling and baselines (p31).

## Full structure / taxonomy (if any)
- **Magnitude** (section eyebrow on all 4 pages)
  - p28 **Bar chart** — single-category column chart
  - p29 **Stacked bar chart** — multiple datasets stacked into a total
  - p30 **Bar chart variants**
    - Horizontal bar chart — when labels are long / narrow layouts (mobile)
    - Grouped bar chart — two+ datasets side by side within each category
    - Butterfly chart — two groups sharing parameters, mirrored left/right
    - Diverging bar chart — positive and negative values around zero
  - p31 **Bar chart best practice** — 4 topics, each a "Try to avoid" vs "Recommended" pair
    - Size of bars
    - Color of bars
    - Direct labelling
    - Zero baseline

## Guidance (paraphrased, exhaustive)
**p28 Bar chart**
- Black definition box (repeats Magnitude definition): magnitude charts suit size comparison, either relative (which is bigger) or absolute (how big the gaps are).
- A bar chart uses rectangles whose length is proportional to value.
- One axis carries the categories being compared (by length); the other carries a discrete value or time.
- A single-category bar chart can be drawn entirely in McKinsey Deep Blue; a bar in the accent colour can flag a meaningful data point.
- Callout (left, upper): bars carry direct value labels and gridlines/axes are removed for legibility.
- Callout (left, lower): bars must start at zero, so the baseline carries a "0" axis label.
- Callout (right): bars of the same data category share one colour; here McKinsey Active Blue marks the insight bar (Insurance).

**p29 Stacked bar chart**
- Useful when comparing several categories of data.
- Built from multiple datasets stacked to show how a total splits into sub-categories and how each relates to the total.
- Callout (left, upper): an insight call-out frames the message and points attention at the key data point.
- Callout (left, lower): stacking makes direct labels hard; adding a gridded axis with labels gives a clear way to read segment values.
- Callout (right): legend stacked vertically in the same order as the bar segments to maximise legibility.

**p30 Bar chart variants**
- Horizontal: some advantages over vertical — labels fit more easily; works well in narrow layouts such as mobile.
- Grouped: use when 2+ data sets are placed side by side and grouped under shared categories on one axis.
- Butterfly: two series side by side, showing the difference between two groups with shared parameters; to emphasise the negative side (bars pointing left), McKinsey Watermelon may be used.
- Diverging: standard bar chart handling both negative and positive values; to emphasise negatives (bars pointing down), McKinsey Watermelon may be used.

**p31 Bar chart best practice**
- Size of bars — Avoid: bars too thin make the eye read the empty gaps, which carry no data. Recommended: bar width ≈ 2× the gap between bars.
- Color of bars — Avoid: a different colour per bar distracts needlessly. Recommended: keep all bars one colour; reserve a different shade for highlights.
- Direct labelling — Avoid: grid axes on bar charts usually add noise without value. Recommended: strip clutter; where possible label bars directly and remove grid axes to improve data visibility.
- Zero baseline — Avoid: never truncate bars; a bar not starting at zero misleads because bar height encodes a discrete quantity. Recommended: if a non-zero range is needed, switch chart type (line or scatter), which don't require a zero baseline and let readers compare position and slope.

## Recommended examples — what & why
- p28 example: "Insurance companies have exposed more personal records than any other industry" / "Personal records exposed, 2011-2016 (millions)". Vertical bars, alphabetical categories: Education 298, Government 380, Healthcare 270, **Insurance 577** (Active Blue, bold label and bold category name), Military 420, Retail 243, Services 211, Technology 239. Others Deep Blue. Why: direct labels, no gridlines, zero baseline labelled, single highlight colour tied to headline.
- p29 example: "Proportionally, Italy's gambling market relies heavily on gaming machines" / "Dollars lost per resident adult per year, 2017 (USD)". 10 countries: Sweden, Canada, Norway, Ireland, **Italy** (bold), US, New Zealand, Finland, Singapore, Australia (totals roughly ascending left→right, ~300–400 up to ~1,000 for Australia; values estimated). 5 segments: Online, Lotteries, Betting, Casino, Gaming machines. In-chart insight call-out above Italy: bold "The House wins in Italy" + note that although only legalised a few years ago, Italy's gaming machine industry is booming, with a short rule pointing to the bar. Why: gridded y-axis compensates for lack of direct segment labels; call-out focuses attention; legend order mirrors stack.
- p30 horizontal example: A 219, B 280, C 198, D 388, E 309, F 178, G 155, H 175 (unsorted, value labels at bar ends, "0" at base of axis).
- p30 grouped example: categories A–D, 3 series each (Deep Blue, bright/Active Blue, royal blue), y-axis 0/50/100 with light gridlines.
- p30 butterfly example: header labels "Disagree" (left) and "Agree" (right); categories A–G in the centre spine; x-axis 100 · 50 · 0 | 0 · 50 · 100; all bars Deep Blue in the example.
- p30 diverging example: categories A–G, C and F negative (bars below zero), "0" baseline labelled; all Deep Blue.
- p31 recommended thumbnails: wide bars (width ≈ 2× gap); uniform Deep Blue with one Active Blue highlight bar (its category label bold); direct value labels, no gridlines; line chart replacing truncated bars.

## Try to avoid examples — what & why
- Hairline-thin bars (Size of bars) — eye drawn to negative space.
- Rainbow bars: royal blue, pale cyan, navy, watermelon/pink-red, steel teal (Color of bars) — unnecessary distraction.
- Bars with y-axis and horizontal gridlines (ticks roughly 0/25/50/75/100) (Direct labelling) — noise without value.
- Truncated bars on an axis not starting at zero (Zero baseline) — misrepresents quantity.

## Visual specifics (colors & roles, axes, labels, sort, spacing ratios, strokes, typography hierarchy)
- Named palette references: **McKinsey Deep Blue** (default bar colour, very dark navy), **McKinsey Active Blue** (bright cyan-blue, highlight/insight), **McKinsey Watermelon** (pink-red, negative-value emphasis). Additional stacked/grouped colours: royal/electric blue, pale cyan, mid steel-teal.
- p29 segment colours (from legend): Online = steel/teal blue; Lotteries = pale cyan; Betting = royal blue; Casino = bright cyan; Gaming machines = Deep Blue navy. Gaming machines sits at the bottom of each stack; legend top→bottom lists Online … Gaming machines matching top→bottom stack order.
- Highlight emphasis is double-coded: colour on the bar + bold on the value label and category label (Insurance, Italy, highlighted "D" in p31 thumbnail).
- Axes: p28 no y-axis/gridlines, only baseline and "0"; p29 y-axis with light horizontal gridlines at 0/250/500/750/1,000 (comma thousands separator here).
- Sort: p28 alphabetical (not by value) — highlight carries the story; p29 roughly ascending by total; p30 horizontal unsorted (letter order).
- Chart cards: white cards with soft shadow on grey page; left white rail with eyebrow "Magnitude" (small bold sans) and page title (serif).
- Chart headline bold sans; subtitle regular sans with units + period in parentheses; footnote & source ("mckinsey.com/insights") in tiny light grey at card bottom.
- Guide callouts: small sans text with thin grey rules/leaders pointing into the chart.
- p31 do/don't markers: circled "x" icon (dark) + bold "Try to avoid"; circled check icon (blue) + bold "Recommended"; thin rule above each marker row.

## Numeric specs observed
- Bar width : gap ≈ **2 : 1** (explicit rule).
- p28 values: 298, 380, 270, 577, 420, 243, 211, 239 (millions, 2011–2016).
- p29 y-axis 0–1,000 step 250; year 2017; USD.
- p30 horizontal values: 219, 280, 198, 388, 309, 178, 155, 175; grouped y-axis 0–100 step 50; butterfly axis 0–100 each side step 50; 3 series in grouped; 7 categories in butterfly and diverging; 8 in horizontal.
- Footer on each page: "Data Visualization Guidelines" · "Version 01" · "19.07.18" · page number (28, 29, 30, 31).
- No pixel or font sizes printed.

## Annotation & narrative patterns
- Headline states the insight; bold/colour highlight in the chart matches the entity named in the headline.
- In-chart insight call-out (bold title + 1–2 line explanation + short leader rule) for stacked/complex charts.
- Guide uses left and right margin callouts with leader lines to explain each design decision.
- Footnote/source block always present on chart cards.

## Other notes
- Image is a 2×2 composite of four separate pages at reduced scale; chart body text is small but legible; p29 exact segment values and p31 thumbnail tick/label numbers are too small to read reliably (treated as approximate/illegible).
