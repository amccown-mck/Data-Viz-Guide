# QA checklist

Run this before any chart leaves your hands. Agents: run it on your own output and report failures before handing back.

> **Python shortcut:** `mv.lint(fig)` checks the mechanical items automatically, for matplotlib and Plotly figures: headline, subtitle and source present; ≤ 6 colors, palette only, no red–green; bars from zero; labels vs. value axis; legends; dual axes; pies ≤ 5; rotated or tiny text. Fix every `error`, then read the `warn` and `info` items. The lint can't tell whether the headline is true or the chart type fits the question, so the rest of this list still needs a human (or agent) eye. `python tools/lint_charts.py` lints the whole gallery.

## Message
- [ ] Headline is a **full-sentence insight**, ≤ 2 lines, no final period, balanced line breaks.
- [ ] Every claim in the headline is **visibly supported** (recompute counts, multipliers, "all/most/none").
- [ ] Subtitle states **metric, unit, scope and period** — and nothing opinionated.
- [ ] The chart type matches the question ([choosing-a-chart.md](choosing-a-chart.md)).
- [ ] One message per chart; ≤ 2 charts per slide.

## Color and emphasis
- [ ] Highlight follows the headline: grey context, blue focus, navy accent — **≤ 2 highlighted** items. Orange appears only where something is worse (negative, below target).
- [ ] Categorical colors (if any) come from the fixed order, ≤ 6, consistent across the deck.
- [ ] No red–green contrasts; nothing encoded by color alone.
- [ ] Focus category labels are bolded/colored to echo the highlight.

## Data integrity
- [ ] Bars/columns start at **zero** (waterfall exception is marked and footnoted).
- [ ] Bubble **area** ∝ value; pie/donut sums to 100% and has ≤ 5 segments.
- [ ] No dual axes (or justified and clearly labelled).
- [ ] Sorted by value, or in a natural order (time, bands, levels).
- [ ] Small multiples share a scale.
- [ ] Numbers rounded sensibly; units in subtitle; true minus (−); consistent K/M/B.

## Clutter
- [ ] Direct labels instead of a legend where possible; legend (if any) top-left, in data order.
- [ ] No borders, 3D, shadows, gradients, heavy gridlines, tick marks, rotated axis titles.
- [ ] Value axis removed when values are labelled.
- [ ] Nothing overlaps: labels, callouts, legend, headline, reference lines.

## Typography and layout
- [ ] Libre Franklin (or approved fallback); role sizes per [typography-and-layout.md](typography-and-layout.md); nothing below 9 pt / 11 px.
- [ ] Headline, subtitle, key, footnote and source **share one left edge**.
- [ ] Sentence case; consistent terminology (FTE vs. headcount; fiscal vs. calendar year).

## Source and ethics
- [ ] Footnotes define metrics and caveats.
- [ ] Source line names the system(s), **as-of date** and **population**.
- [ ] No group smaller than the **minimum n** (default 10) — including in tooltips, filters and drill-downs.
- [ ] Protected attributes used only for approved analyses, aggregated.
- [ ] Forecasts/estimates are labelled and show a range or scenario.

## Accessibility and delivery
- [ ] Text contrast ≥ 4.5:1; fills < 3:1 carry labels.
- [ ] Alt text / text summary provided (headline + key numbers).
- [ ] Exported at the right format: native Office chart, SVG/PDF for print, PNG @ 300 dpi, or responsive HTML.
- [ ] Mobile/dark variants checked if the chart will be shown that way.
