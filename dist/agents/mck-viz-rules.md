# McKesson data-viz rules for coding agents

<!-- GENERATED from tokens/tokens.json by tokens/build.py - edit agents/*.template.md, not this file. -->

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
- **Grey context with one blue focus** (plus an optional single navy accent). At most 2 highlighted items. For one series with one exception: all light blue, the exception navy.
- **Orange means worse.** Use orange only for negatives, decreases, below target or benchmark, and the low end of the diverging scale. Never as a highlight or decoration.
- At most **6 categorical colors**, in the fixed order below. Group the tail into "Other".
- A **"Source:"** line bottom-left (system, as-of date, population), with footnotes for definitions.

## Color roles

| Role | Hex | Use |
|---|---|---|
| Context | `#B4B0A5` | Everything the reader should see but not focus on |
| Context light | `#DEDBD1` | De-emphasized fills, suppressed cells |
| **Focus** | `#005A8C` | What the headline is about; default single-series color. The color used most |
| Focus light | `#66C4FF` | The series fill when every bar is one series and one exception gets the accent |
| **Accent** | `#143359` | The one exception that must pop (navy, never orange) |
| Total / benchmark | `#143359` | Totals, target and benchmark lines (dashed, labelled) |
| Axis / baseline | `#8C8C8C` | Thin zero baseline |
| Grid | `#E6E4DE` | Gridlines, only when values aren't labelled |
| Headline text | `#143359` | Headline, emphasized labels |
| Body / label text | `#505050` | Subtitle, data labels |
| Muted text | `#737373` | Ticks, footnotes, source (the lightest allowed text) |
| Favorable | `#00AF9D` (text `#00737A`) | Only when good vs. bad is the message |
| Unfavorable | `#EF8200` (text `#A75B00`) | Negatives, below target. The only job orange has. Never pair red with green |

- **Categorical, in order:** `#005A8C`, `#143359`, `#66C4FF`, `#00AF9D`, `#00737A`, `#EF8200`, `#B6E2FA`, `#66CFC4`. Prefer ≤ 5; orange (6th) is a last resort. Amber is not used.
- **Sequential blue (light → dark, the default for one measure):** `#E6F3FB`, `#B6E2FA`, `#66C4FF`, `#009EFF`, `#0A5FBC`, `#143359`
- **Sequential orange (only when darker means worse, e.g., risk; say so):** `#FFF3E0`, `#FFD9A8`, `#F7B25C`, `#EF8200`, `#A75B00`, `#6B3A00`
- **Diverging orange–blue (midpoint = benchmark, symmetric):** `#A75B00`, `#EF8200`, `#F7C180`, `#EFEDE7`, `#99BDD1`, `#005A8C`, `#143359`
- Text on a filled mark: white on dark fills, `#143359` on light fills.

## Type and layout
- Font: **Libre Franklin** (fallback: Franklin Gothic Book, Arial).
- Slide title: bold 24 pt, `#143359` (with one chart on a slide, its headline is the slide title). Chart headline (a chart with its own title): semibold 18 pt / 20 px, still an insight sentence. Two charts on a slide: a bold slide title for the shared message, a semibold insight headline per chart. Big KPI numbers: bold. Subtitle: regular 14 pt / 15 px. Labels: medium 12 pt / 13 px. Footnote and source: light 9 pt / 11 px, `#737373`. Nothing smaller.
- Everything is left-aligned on one edge, with no centered titles, chart borders, 3D, shadows or gradients.
- Bar width : gap ≈ 2 : 1 (band fill 0.67). Lines 2.0 px; context lines 1.25 px.

## Honest scales
- Bars and columns start at **zero**. Bubble **area** (not diameter) ∝ value. Pies and donuts have ≤ 5 segments summing to 100%.
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
- [ ] Grey context, ≤ 2 highlights matching the headline, ≤ 6 categorical colors, no red vs. green. Orange only where something is worse.
- [ ] Direct labels. No redundant axis, gridlines or legend. Nothing overlaps.
- [ ] Bars from zero, honest areas, no dual axes, sorted with intent.
- [ ] No group under 10 people anywhere, including tooltips.
- [ ] Text ≥ 9 pt / 11 px with ≥ 4.5:1 contrast. Alt text given (headline + 2–3 key numbers).
