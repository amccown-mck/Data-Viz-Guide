---
still: 11
page: 36
section: Part-to-whole
title: Donut and pie chart best practice
page_type: chart-best-practice
chart_types: [donut, pie]
---
## Intent
- A set of do/don't pairs for building donut and pie charts. The page is organized as 4 cards, each with a "Try to avoid"/"Avoid" example on the left and a "Recommended" example on the right. The card topics are:
  1. When donuts are better than pies
  2. Labelling donut charts
  3. Dealing with many small wedges
  4. Order of wedges

## Guidance (paraphrased, every rule stated on the page)
- **When donuts are better than pies**
  - People perceive differences in length more quickly than differences in area, so pies can be hard to interpret.
  - With a donut, the reader follows the ring around the circle and can judge each segment's "length" relative to the one before.
- **Labelling donut charts**
  - When there are more than a few values, don't put the value labels directly on the chart.
  - Consider labeling small segments outside the chart, particularly when the labels are long.
- **Dealing with many small wedges**
  - Avoid donuts with many sections, because they become hard to read.
  - Try combining the smallest segments into a new category called "Other".
- **Order of wedges**
  - Don't mix small and large segments arbitrarily unless there is a functional reason.
  - Begin with the largest value and continue clockwise toward smaller values.

## Examples marked Recommended
- **Donuts vs pies**: a thin-ring donut with the same data as the pie. There is a large dark navy segment (about half) from 12 o'clock clockwise, then bright blue, royal blue, and small light blue and teal segments. It works because readers can compare arc lengths around the ring.
- **Labelling**: a donut with a legend to the right. Labels and values are in two aligned columns, with small, near-illegible text that appears to read:

  | Label | Value |
  |---|---|
  | Ford | 49% |
  | Citroen | 20% |
  | Renault | 17% |
  | Volkswagen | 7% |
  | Vauxhall | 5% |
  | Other | 2% |

  It works because the labels sit outside the ring in one aligned list with room for long names.
- **Many small wedges**: a donut with 7 legend entries (A–F plus "Other"), where the smallest categories are merged into a grey "Other" segment. It works because the number of segments drops and every remaining segment is readable.
- **Order of wedges**: a donut with legend A–E. The largest dark navy segment starts at 12 o'clock and the segments get smaller clockwise, in the same order as the legend. It works because the order is predictable and easy to scan.

## Examples marked Try to avoid / Not recommended
- **Donuts vs pies ("Try to avoid")**: a filled pie with a dark navy half, then bright blue, royal blue, light blue, teal and a pale lavender sliver. It fails because readers must compare areas, which is harder than comparing lengths.
- **Labelling ("Try to avoid")**: a donut with percentage values scattered around the outside of the ring next to each segment (49%, 20%, 17%, 7%, 5%, 2%) and no category names. It fails because the labels are cluttered and inconsistently placed once there are more than a few values.
- **Many small wedges ("Try to avoid")**: a donut with 11 legend entries (A–K). Several tiny slivers near 12 o'clock use extra colors, including purple, pink, red, tan and a patterned/hatched swatch. It fails because it has too many sections, the slivers can't be read, and the palette sprawls.
- **Order of wedges ("Avoid")**: a donut whose legend reads D, E, B, C, A. A small bright blue segment sits between the large dark navy and teal segments, and grey and blue segments follow in no size order. It fails because the arbitrary mix of large and small segments has no purpose.

## Visual specifics observed
- **Colors (recommended examples)**: up to about 6.
  - Dark navy is always the largest segment.
  - Bright sky blue, royal/electric blue, light cyan and teal/steel blue follow.
  - Mid grey is used for "Other".
- **Colors (bad example)**: the many-wedges example adds off-palette purple, pink, red, tan and pattern swatches.
- **Donut rings**: thin rings with large holes. Small white gaps separate the segments.
- **Starting position**: the largest segment starts at 12 o'clock and runs clockwise in the recommended versions.
- **Legends**: small filled circle markers in a vertical list to the right of the ring, with values right-aligned in a separate column where shown.
- **"Other" placement**: grey "Other" is the last item, in both the legend and the ring.
- **Axes and gridlines**: none.
- **Verdict markers**:
  - A thin rule above each verdict.
  - A dark navy circle with a white "×" marks "Try to avoid".
  - A bright blue circle with a white check marks "Recommended".
  - The "Order of wedges" bad example uses a **red/pink circle with a dark ×** and the label "Avoid", not "Try to avoid". This may mean a stronger prohibition, but the page does not state it.
  - Verdict labels are a bold small sans serif. The explanation beneath is a regular small sans serif.
- **Typography**:
  - Card titles are a medium-bold sans serif, larger than the verdict text.
  - The page title is a large 2-line serif ("Donut and pie chart best practice"), with a small bold sans-serif eyebrow above it.
- **Layout**: a 2×2 grid of white cards on a light grey background. Each card is split into two equal columns (bad on the left, good on the right).

## Annotation & narrative patterns
- The cards are titled by topic, not by insight. There are no data headlines or sources in the examples.
- Page footer: "McKinsey & Company", "Data Visualization Guidelines", "Version 01", "19.07.18", and the page number 36.

## Other notes
- The text in the labelling legend and in the value labels around the rings is very small. Brand names and percentages are read as best possible; exact characters are partially illegible.
- The left-rail body area is empty apart from the eyebrow and title.
