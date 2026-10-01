---
still: 34
page: 59
section: Relationships
title: Parallel coordinates best practice
page_type: chart-best-practice
chart_types: [parallel coordinates, table]
---
## Intent
Best-practice dos and don'ts for parallel coordinates, in three panels: choosing them over a table, highlighting a group of lines, and handling axis subsets through interactivity rather than cropping.

## Guidance (paraphrased, every rule stated on the page)
- **Parallel coordinates can replace tables:** a table is not always the best way to show a dataset. In some cases a parallel coordinates chart gets certain messages across better than a table does.
- **Highlight groups of lines:** don't try to highlight several sets with different colors, and don't color every line. Use grey for the background and deep blue for the foreground so that one specific set in the story stands out.
- **Adding interactivity:** cropping the chart down to a few axes to focus on some steps is marked Try to avoid. A better way to add exploration is interactivity, for example letting users hide axes or play with the coordinate steps.

## Examples marked Recommended
- Parallel coordinates chart of the car dataset with 7 axes (Cylinders, Mpg, Displacement, Power, Weight, Acceleration, Year). Dark lines sit over grey lines. It gets across patterns that a table cannot show at a glance.
- Parallel coordinates chart with one group in dark navy/deep blue and all other lines in light grey. The focus set is clear.
- Interactive version: all 7 axis labels are kept. The active axes (Mpg, Displacement, Power) have bold dark labels and full-strength lines. The inactive axes (Cylinders, Weight, Acceleration, Year) have faded grey labels and faded lines. The full context stays visible while the user focuses on a subset.

## Examples marked Try to avoid / Not recommended
- A small data table with columns Cylinders, Mpg, Displacement, Power, Weight, Acceleration, Year and about 5 rows. The cell values are too small to read (illegible). A table does not show multivariate patterns well.
- Parallel coordinates with many groups colored in several blues (bright cyan, royal blue, light blue, navy). This makes a noisy tangle with no clear focus.
- A static crop showing only 3 axes (Mpg, Displacement, Power). The rest of the diagram is cut away, so the context is lost.

## Visual specifics observed
- Color roles: dark navy = focus set, light grey = context/background lines. In the "avoid" example, 4 or more blue tints are used together.
- Axis labels are small grey sans above each vertical axis. In the interactive example, bold dark text marks the active axes and pale grey marks the inactive ones.
- Vertical axes are thin light grey lines with no gridlines. The tick values in these small thumbnails are illegible or not shown.
- The table in the avoid example has full black cell borders (a heavy grid).
- Layout: 3 white cards on a light grey page, laid out 2 on top and 1 at bottom left. Each card has a title in medium-weight sans (top left), two thumbnails side by side, a thin rule, then the verdicts: a dark navy circle with an "x" icon for "Try to avoid" (left) and a bright blue/cyan circle with a checkmark for "Recommended" (right). Each verdict has a bold label and a regular-weight explanation.
- Typography: page title is a large serif on two lines, with a small bold sans eyebrow "Relationships" above it. Card titles are sans at medium size. Body text is small regular sans.

## Annotation & narrative patterns
- The thumbnails have no headlines. The guidance sits in the card titles and the verdict captions.
- The consistent pattern is: avoid on the left, recommended on the right, with icon-coded labels.

## Other notes
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 59.
- The axis labels read "Power" and "Mpg" here, compared with "Horsepower" and "Miles per gallon" on page 58.
