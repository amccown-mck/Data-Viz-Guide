---
applyTo: "**/*.{html,js,ts,css}"
---
# Web charts (HTML, JavaScript, TypeScript, CSS)

Applies to web pages, dashboards and components that show charts or tables. The full rules are in `AGENTS.md` and `docs/formats.md#web-and-html-articles-microsites-internal-tools`.

## Setup
```html
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="dist/web/mck-viz.css">
<script src="dist/web/mck-plotly-template.js"></script>   <!-- defines window.MCK_PLOTLY_TEMPLATE -->
```
Vega-Lite: pass the contents of `dist/web/vega-lite-config.json` as the spec's `config`.

## Chart-card pattern
Start from `templates/html/chart-card.html`, which is a working page.

```html
<figure class="mck-chart">
  <h2 class="mck-headline">Insight sentence with the number</h2>
  <p class="mck-subtitle">Metric, unit, scope, period</p>
  <div class="mck-plot" id="chart" role="img" aria-label="Headline plus 2-3 key numbers"></div>
  <figcaption class="mck-footnote">Definitions and caveats<br>Source: system, as-of date, population</figcaption>
</figure>
```
The headline, subtitle and source are HTML text, and the chart library draws only the data (no in-chart title). Use `Plotly.newPlot(el, data, {template: MCK_PLOTLY_TEMPLATE, ...}, {displayModeBar: false, responsive: true})`.

## Rules
- **No hex literals in CSS or JS.** Use the variables in `mck-viz.css`: `var(--mck-chart-focus)`, `--mck-chart-focus-light`, `--mck-chart-context`, `--mck-chart-accent` (navy exception), `--mck-semantic-negative` (orange, only for "worse"), `--mck-chart-total`, `--mck-seq-blue-1`…`6`, `--mck-div-1`…`7`, `--mck-cat-1`…`6`. In JS, read them with `getComputedStyle(document.documentElement).getPropertyValue("--mck-chart-focus")`, or use the template's `colorway`.
- **Highlight, don't decorate:** context grey, one focus blue, optionally one orange accent. At most 6 categorical colors.
- **Direct labels** over legends. If a legend is unavoidable, use `.mck-legend` above the plot, top-left.
- **Tables** use `<table class="mck-table">` with `<th scope>`, right-aligned `.num` cells, `tr.is-focus` / `tr.is-total` rows and `td.is-muted` for suppressed cells. See `docs/cookbook/tables.md`.
- **Responsive:** max width ~960 px. Check the page at 390 px wide: columns become horizontal bars, the key moves on top, and wide tables scroll inside `overflow-x: auto`.
- **Tooltips** carry detail (exact values, n-size), never the only copy of the key number. Never show a group of fewer than 10 people or an individual's value in a tooltip, filter or drill-down.
- **Accessibility:** give each chart `role="img"` with an `aria-label` (or a visually hidden text summary), keep text ≥ 11 px, and never hijack scrolling.
- **Draw after the font loads:** `document.fonts.ready.then(draw)`. Plotly caches label widths from its first render, so drawing with the fallback font leaves margins that clip long labels.
- **Never edit `dist/web/*`**. It is generated from `tokens/tokens.json` by `python tokens/build.py`.
