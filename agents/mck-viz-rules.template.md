# McKesson data-viz rules for coding agents

<!-- {{generated_note}} -->

Copy this single file into any repo (for example as `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` or `.cursor/rules/mck-viz.md`) so that coding agents there make charts to the McKesson standard. It is self-contained. The full guide, themes and the `mckviz` Python package live in the **data-viz-guide** repo.

## Workflow
1. **Question:** write the one question the chart answers. Default to explanatory charts (decks, reports).
2. **Chart type:** magnitude → sorted bar · part-to-whole → 100% stacked bar (waterfall for bridges) · change over time → line · ranking → sorted bar or slope · distribution → histogram, strip or box · correlation → scatter · two categories × one measure → heatmap · flows → Sankey · overlap of ≤ 3 groups → Venn · one number → KPI. Values clustered far from zero → dot plot, never truncated bars.
3. **Build:** use the colors below by **role**. If the `mckviz` package or the generated themes are available, use them instead of typing hex values.
4. **Headline:** compute the finding in code, then write it as a sentence with the number.
5. **QA:** run the checklist at the end, render the chart and look at it.

## Every chart has
- An **insight headline**: a full sentence with a verb stating the "so what", ≤ 2 lines, sentence case, no final period. Every claim is visibly true in the chart.
- A **neutral subtitle**: metric, unit, scope, period. Example: "Voluntary attrition by job family, FY26 (%)".
- **Direct labels** instead of a legend. A legend only when labels would collide, top-left. When values are labelled, remove the value axis and gridlines.
- **Grey context with one blue focus** (plus an optional single orange accent). At most {{chart:limits.highlighted_series}} highlighted items.
- At most **{{chart:limits.categorical_series}} categorical colors**, in the fixed order below. Group the tail into "Other".
- A **"Source:"** line bottom-left (system, as-of date, population), with footnotes for definitions.

## Color roles

| Role | Hex | Use |
|---|---|---|
| Context | `{{color:chart.context}}` | Everything the reader should see but not focus on |
| Context light | `{{color:chart.context_light}}` | De-emphasized fills, suppressed cells |
| **Focus** | `{{color:chart.focus}}` | What the headline is about; default single-series color |
| **Accent** | `{{color:chart.accent}}` | The one exception that must pop |
| Total / benchmark | `{{color:chart.total}}` | Totals, target and benchmark lines (dashed, labelled) |
| Axis / baseline | `{{color:chart.axis}}` | Thin zero baseline |
| Grid | `{{color:chart.grid}}` | Gridlines, only when values aren't labelled |
| Headline text | `{{color:text.headline}}` | Headline, emphasized labels |
| Body / label text | `{{color:text.primary}}` | Subtitle, data labels |
| Muted text | `{{color:text.muted}}` | Ticks, footnotes, source (the lightest allowed text) |
| Favorable | `{{color:semantic.positive}}` (text `{{color:semantic.positive_text}}`) | Only when good vs. bad is the message |
| Unfavorable | `{{color:semantic.negative}}` (text `{{color:semantic.negative_text}}`) | Never pair red with green |

- **Categorical, in order:** {{list:categorical.values}}
- **Sequential blue (light → dark):** {{list:sequential.blue}}
- **Sequential orange (risk, intensity):** {{list:sequential.orange}}
- **Diverging orange–blue (midpoint = benchmark, symmetric):** {{list:diverging.orange_blue.values}}
- Text on a filled mark: white on dark fills, `{{color:text.headline}}` on light fills.

## Type and layout
- Font: **{{font}}** (fallback: Franklin Gothic Book, Arial).
- Headline: bold {{role:headline.size_pt}} pt / {{role:headline.size_px}} px, `{{color:text.headline}}`. Subtitle: regular {{role:subtitle.size_pt}} pt / {{role:subtitle.size_px}} px. Labels: medium {{role:label.size_pt}} pt / {{role:label.size_px}} px. Footnote and source: light {{role:footnote.size_pt}} pt / {{role:footnote.size_px}} px, `{{color:text.muted}}`. Nothing smaller.
- Everything is left-aligned on one edge, with no centered titles, chart borders, 3D, shadows or gradients.
- Bar width : gap ≈ 2 : 1 (band fill {{chart:bar.band_fill}}). Lines {{chart:line.width_px}} px; context lines {{chart:line.context_width_px}} px.

## Honest scales
- Bars and columns start at **zero**. Bubble **area** (not diameter) ∝ value. Pies and donuts have ≤ {{chart:limits.pie_segments}} segments summing to 100%.
- No dual axes: use two aligned charts, or index both series to 100. Small multiples share one scale.
- Sort by value unless the order is natural (time, bands, levels). Time runs left to right.
- Numbers: round sensibly, use a true minus (−) and an explicit + on deltas, and keep units in the subtitle.

## People data
- Never show a group of **fewer than 10 people**: not in marks, labels, tooltips, filters or drill-downs. Merge into "Other" or suppress, and footnote it.
- Protected attributes only for approved, aggregated analyses. Frame findings about systems and roles, not individuals.
- Forecasts and model outputs are labelled as estimates and show a range or scenarios.

## Platform notes
- **Python:** `import mckviz as mv; mv.use()`, then `mv.highlight()`, `mv.titles()`, `mv.source()`, `mv.label_bars()`, `mv.save()`. Without `mckviz`, set the colors above as constants in one place.
- **Web:** headline, subtitle and source as HTML text around the chart (the chart-card pattern). Use the guide's `mck-viz.css` and Plotly / Vega-Lite theme files where available.
- **Excel / PowerPoint:** native, editable charts with the McKesson Data Viz theme colors and fonts. Gap width ≈ 50%.
- **Power BI:** the McKesson data-viz theme JSON. Highlight via conditional formatting on a measure, and blank any measure with n < 10.

## QA checklist (run before returning a chart)
- [ ] The headline is an insight sentence, and its numbers are computed from the data.
- [ ] The subtitle states metric, unit, scope and period. The source line has system, date and population.
- [ ] Grey context, ≤ 2 highlights matching the headline, ≤ 6 categorical colors, no red vs. green.
- [ ] Direct labels. No redundant axis, gridlines or legend. Nothing overlaps.
- [ ] Bars from zero, honest areas, no dual axes, sorted with intent.
- [ ] No group under 10 people anywhere, including tooltips.
- [ ] Text ≥ 9 pt / 11 px with ≥ 4.5:1 contrast. Alt text given (headline + 2–3 key numbers).
