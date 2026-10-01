# Principles

The house rules. Every chart we ship — in a deck, a report, an HTML page or a Power BI page — should pass all of them. They are written to be **testable**: a reviewer (human or agent) can check each one.

> Inspiration: patterns documented from a leading consulting firm's public-facing visualization guide (see [reference/inspiration-mckinsey](../reference/inspiration-mckinsey/README.md)), adapted to McKesson brand and to people-analytics / workforce work.

---

## 1. Start with the question, not the chart
- Write the **question** the chart answers before choosing a chart ("Where is attrition concentrated?" not "show attrition").
- Decide the **mode**: *explanatory* (we know the answer; the chart proves it — decks, reports, memos) or *exploratory* (the reader finds answers — dashboards, tools). This kit defaults to explanatory.
- Pick the chart from the question using [choosing-a-chart.md](choosing-a-chart.md).

## 2. The headline is the insight; the subtitle is the measure
Every chart has a two-tier title:

| Element | Job | Example |
|---|---|---|
| **Headline** (bold, navy) | The "so what". A full sentence with a verb. States the finding, ideally with the number. ≤ 2 lines. | *Two frontline job families lose about 1 in 4 people a year, well above the 19.9% enterprise rate* |
| **Subtitle** (regular, grey) | Neutral description: **metric, unit, scope, period**. No opinions. | *Voluntary attrition by job family, FY26 (%)* |

- The headline must be **true to the chart** — every claim (counts, "all", "most", multipliers) is visibly supported. Recompute numbers; don't eyeball.
- If you can't write a headline, you don't have a finding yet — you have a chart.

## 3. One message per chart, few charts per page
- One chart makes one point. If you have two points, make two charts (or a build-up sequence).
- Slides: **≤ 2 charts** per slide; never a "chart wall" in a live presentation.
- Keep text next to a chart short; the chart should carry the message.

## 4. Highlight, don't decorate
Color is for **meaning**, never decoration.

| Role | Color | Use |
|---|---|---|
| Context | warm grey `#B4B0A5` | Everything the reader should *see but not focus on* |
| Focus | McKesson Blue `#005A8C` | The data the headline is about; default single-series color |
| Accent | McKesson Orange `#EF8200` | The *one* thing that must pop (use sparingly) |
| Total | Navy `#143359` | Totals, subtotals, benchmark lines |

- Default pattern: **grey everything, then color only what the headline mentions**.
- Max **2 highlighted** items/series. More highlights = no highlight.
- Use a categorical palette only when categories genuinely need to be told apart — and then ≤ 6 colors, in the fixed order (see [color.md](color.md)).
- Echo the highlight in text: bold the matching category label; match callout color to the mark.

## 5. Label directly; delete everything that doesn't help
- **Direct labels** beat legends: label line ends, bar ends, segments in place.
- Use a legend only when direct labels would collide (e.g., 100% stacked bars, dense scatter) — place it **top-left**, above the plot, in reading order.
- Remove: chart borders, background fills, 3D, shadows, gradients, heavy gridlines, redundant axis titles, tick marks.
- If bars carry value labels, **remove the value axis and gridlines**.
- Keep a light **baseline** (the zero line) on bar and column charts.

## 6. Honest scales
- **Bars and columns start at zero.** If the differences are too small to see from zero, use a dot plot or line instead of truncating bars.
- The only exception is a **waterfall** bridge between large totals — then mark the break visually and say so in the footnote.
- **Bubble area** (not diameter) is proportional to value.
- Pie/donut segments **sum to 100%**; ≤ 5 segments.
- Avoid **dual axes**. If you must compare two measures over time, prefer two aligned charts or index both series to 100.
- Small multiples share the **same scale** unless labelled otherwise.
- Time runs **left to right** at even intervals; show gaps in data as gaps.

## 7. Order with intent
- Sort categories **by value** (largest first for bars, or ascending toward the focus item for columns) unless there's a natural order: time, age/tenure bands, job levels, org hierarchy, survey scales.
- Keep the **same order** for the same categories across a deck/report.
- Stacks: put the segment you're talking about **on the baseline** (or at the end for 100% bars) so it's easy to compare.

## 8. Numbers people can read
- Round to the precision that matters (19.9%, not 19.874%; 4.3K, not 4,291 unless exact counts matter).
- Units go in the **subtitle** (`($M)`, `(%)`, `(FTE)`), not on every label.
- Use thousands separators, a true minus (−) for negatives, and an explicit + for deltas ("+139").
- Use `K`/`M`/`B` consistently within a chart. Dates: `FY26`, `Q3 FY26`, `Mar 2026`, or `'24` for tight axes.

## 9. Annotate the "why"
- Add **callouts** for what the reader can't infer: a bold 2–5 word title + 1–2 lines of explanation, placed next to the data, with a thin leader line if needed.
- Use **shaded bands** for periods (reorg, hiring freeze, system change) and **reference lines** for targets/benchmarks (labelled).
- Don't annotate everything — annotate the point of the headline.

## 10. Source, define, and date everything
Bottom-left, small, muted:
- **Footnotes** for definitions and caveats (e.g., *"Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months"*).
- **Source:** the system(s) and, for workforce data, the **as-of date** and **population** (e.g., *"Source: Workday HCM, as of 31 Mar 2026; U.S. regular employees"*).
- External signals name the provider and the benchmark definition.

## 11. People data is personal — protect it
Workforce charts carry extra obligations:
- **Minimum group size.** Don't show any cut with fewer than **10 people** (or your policy's threshold); combine into "Other" or suppress with a footnote.
- **No re-identification.** Avoid combinations (small team × demographic × tenure) that single out individuals, including in tooltips and drill-downs.
- **Protected attributes** (gender, ethnicity, age, disability, veteran status) — use only for approved analyses (e.g., pay equity), aggregated, with legal/HR guidance.
- **Forecasts and models** show uncertainty (ranges/scenarios) and are labelled as estimates.
- Frame people-level findings about **systems and roles**, not individuals.

## 12. Design for the medium
The same data needs different treatment for a live slide, a PDF, a phone or a dashboard. See [formats.md](formats.md).
- Live slides: simplify, build up in steps, fewer words.
- Reports: full context, footnotes, can be denser.
- Web / mobile: portrait layouts, fewer text elements, move labels to a top key, tooltips for detail.
- Dashboards: exploratory; consistent layouts and filters; still use highlight logic.

## 13. Accessible by default
- Text contrast ≥ **4.5:1** (our `text.muted` is the lightest allowed for text).
- Palettes are checked for color-vision deficiency; never use **red vs. green** as the only distinction.
- **Never rely on color alone**: pair with labels, position or shape.
- Minimum text size: **9 pt** on slides / **11 px** on screens.
- Provide **alt text** or a text summary (the headline + key numbers) for every chart that leaves the building.

---

**Before you ship:** run the [QA checklist](qa-checklist.md).
