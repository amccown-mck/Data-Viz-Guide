---
source: hires_hierarchy-and-understanding
page: ? (no printed page number visible; footer reads "Data Visualization Guidelines")
section: Fundamentals — Step 2: Interpretation
title: Hierarchy and understanding
---
## Intent
Explains the second stage of how a reader processes a chart — interpretation — and shows, via an annotated bubble chart, which chart furniture (headline, chart title, key/legend, axis labels) supports it and what each element's job is.

## Full structure / taxonomy (if any)
Step framework (this page = Step 2; implies Step 1 = perception, referenced as "step one"):
- **Step 2: Interpretation**
  - Applying meaning to value and relationship
  - Understanding general narrative

Annotated anatomy (callouts in middle column, leader lines to the chart):
| Element | Role (paraphrased) | Where on example |
|---|---|---|
| **McKinsey insight** (headline) | Goes beyond a title: shapes/clarifies the first impression and adds insight | Bold top line: "Longer life expectancy is connected to higher GDP per capita" |
| **Chart title** | Plain, non-editorial descriptor stating units, time period and factor (e.g. millions) | Line 2: "Countries by life expectancy and GDP per capita" |
| **Key or legend** | Decodes information not carried by the axes; here gives categorical (regional) context via a map | Right-side "Population" size key + "Region" colour-coded world map |
| **Axis labels** | Value, time or category | "Life expectancy (years)" (y); "GDP per capita ($ adjusted for price differences, PPP 2011)" (x) |

## Guidance (paraphrased, exhaustive)
- Once the basics are perceived (step one), the reader turns to the surrounding information to make sense of the chart.
- The insight headline should either validate the reader's first impression or sharpen it with additional detail.
- Axis labels and the chart title establish scale and context so the reader can read both the values and what they mean.
- The key/legend supplies context alongside the title and helps the reader grasp how categories relate to each other.
- Headline ≠ title: headline is the takeaway (editorial); chart title is neutral and descriptive (units, period, factor).
- Legends are for information the axes cannot convey (e.g., bubble size, region colour).

## Recommended examples — what & why
- Example chart: bubble scatter of countries — x = GDP per capita (log scale), y = life expectancy (years), bubble size = population, colour = world region.
  - Why: demonstrates a complete interpretation hierarchy — takeaway headline, neutral descriptive title, labelled axes with units, and a legend covering both non-axis encodings (size and colour).
  - Region legend rendered as a small colour-coded world map rather than a list of swatches — lets the reader decode colour geographically at a glance.
  - Population legend uses three nested-reference outline circles (1m, 100m, 1bn).

## Try to avoid examples — what & why
None shown on this page. Implied: don't use an editorialized chart title (keep opinions in the headline); don't omit units/time period/factor.

## Visual specifics (colors & roles, axes, labels, sort, spacing ratios, strokes, typography hierarchy)
- Page layout: white left rail (section eyebrow "Fundamentals" small bold sans; title serif display; step text), grey centre column for callouts, white chart card with soft drop shadow on the right.
- Callouts: bold label + regular description, each with a thin grey horizontal rule above and a leader line running to the relevant chart element (one angled leader for the headline).
- Headline: bold sans, largest text on the card, black/near-black.
- Chart title: regular weight sans, slightly smaller, dark grey.
- Y-axis title placed horizontally at top of axis, right of the "85" tick label (not rotated).
- X-axis title centred below tick labels.
- Tick labels small grey sans. Y ticks: 50–85 in steps of 5. X ticks: $1 000, $2 000, $4 000, $8 000, $16 000, $32 000, $64 000, $128 000 (doubling = log2 scale); thousands separated with a space, not a comma.
- Gridlines: light grey, both vertical and horizontal; plotting area bounded by thin left and bottom axes.
- Colour encoding for region (sequential blue family used categorically): very dark navy, royal/deep blue, bright mid-cyan blue, pale light cyan. Map: Americas = dark navy; Europe/Russia = deep blue; Africa = mid cyan; Asia/Oceania = pale cyan (colour-to-region inferred from map).
- Bubbles: filled, with thin white outlines where overlapping; semi-opaque look for the big pale bubbles.
- Legend section titles "Population" and "Region" in regular sans, small.
- Footnote/source lines at card bottom rendered in extremely light grey — placeholder text, near-illegible: appears to read "*Footnotes, explanations or additional details of methodology go here. Expand where necessary." / "Source: mckinsey.com/insights" (low confidence).
- A grey horizontal line crosses the chart around y≈72.5 aligned with the "Key or legend" callout rule — this is the callout leader, not a data reference line.

## Numeric specs observed
- Y-axis range 50–85 years, 5-year intervals (8 ticks).
- X-axis log scale, $1 000 → $128 000, 8 ticks, each ×2.
- Population size key: 1m, 100m, 1bn.
- Data base year: PPP 2011.
- 4 region colours.
- No pixel/font size specs printed.

## Annotation & narrative patterns
- Two-tier top text: insight headline (the "so what") above a descriptive chart title (the "what").
- Guide-level callouts use label + one-sentence definition + leader line — a reusable anatomy-diagram pattern.
- Footnote + source block reserved at the bottom of every chart card.

## Other notes
- Page is part of a multi-step reader-processing sequence (Step 1 perception on another page).
- Footer faint text beyond "Data Visualization Guidelines" illegible.
