---
applyTo: "**/*.{html,js,jsx,ts,tsx,css}"
---

> These rules are for code that **draws charts**. Skip them when you are editing the kit's own build tools and internals (`tools/`, `tokens/`, `python/mckviz/`, `guide/`, `office/`), which have their own conventions in `AGENTS.md` part B.
# Web charts (HTML, JavaScript, TypeScript, CSS)

Applies to web pages, dashboards and components that show charts or tables. The full rules are in `AGENTS.md` and `docs/formats.md#web-and-html-articles-microsites-internal-tools`.

## Setup
```html
<link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="dist/web/mck-viz.css">
<script src="dist/web/mck-viz.js"></script>   <!-- window.mck helpers + window.MCK_PLOTLY_TEMPLATE -->
```
Vega-Lite: pass the contents of `dist/web/vega-lite-config.json` as the spec's `config`. Offline or locked-down intranet: start from `templates/html/chart-card-offline.html` (local fonts, `dist/web/vendor/plotly.min.js` = Plotly.js 4.1.1).

## Helpers (`mck-viz.js`, mirrors the Python package)
`mck.tok(name)` token color · `mck.highlight(labels, {focus, accent})` · `mck.fmtNum(v, {kind, decimals, sign, prefix})` (K/M/B, %, true minus, explicit +) · `mck.suppressSmall(rows, nKey, {minN: 10})` → `[rows, footnote]` · `mck.textOn(hex)` · `mck.status(key)` → `{color, symbol, word}` · `mck.plotlyLayout("bar" | "line" | "waterfall" | "stacked" | "heatmap" | "sankey" | "roadmap", extra)` · `mck.srTable`, `mck.ready(draw)`, `mck.plotConfig`. Web recipes: the "HTML / JavaScript" sections of `docs/cookbook/waterfall.md`, `stacked-bar.md`, `heatmap.md`, `kpi-big-number.md`.

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
The headline, subtitle and source are HTML text, and the chart library draws only the data (no in-chart title). Use `Plotly.newPlot(el, data, mck.plotlyLayout("bar", {...}), mck.plotConfig)` (or `{template: MCK_PLOTLY_TEMPLATE, ...}` and `{displayModeBar: false, responsive: true}`).

## Dashboard components (`mck-viz.css`)
- **KPI tile:** `<div class="mck-kpi">` with `.mck-kpi__name`, `__value`, `__delta` (`is-up`/`is-down` arrow + `is-good`/`is-bad` color), `__label` (one sentence), optional `__meter` + `__gap`, `__source`; `mck-kpi--dark` on Deep Navy.
- **Status:** `<span class="mck-status mck-status--off-track">Off track</span>` (also `--on-track`, `--at-risk`, `--not-started`, `--done`): color + symbol + word, never color alone. Status colors are for status only, never data series.
- **Grid:** `.mck-grid` (1 / 2 / 3 columns at < 560 / ≤ 980 / > 980 px, 16 px gutter). **Tracker:** `<table class="mck-tracker">` inside `.mck-scroll`. **Heat table:** `.mck-table--heat` with `td.mck-heat.mck-heat-blue-1`…`6` (`-div-1`…`7`), `is-suppressed`.

## Rules
- **No hex literals in CSS or JS.** Use the variables in `mck-viz.css`: `var(--mck-chart-focus)`, `--mck-chart-focus-light`, `--mck-chart-context`, `--mck-chart-accent` (navy exception), `--mck-semantic-negative` (orange, only for "worse"), `--mck-chart-total`, `--mck-seq-blue-1`…`6`, `--mck-div-1`…`7`, `--mck-cat-1`…`6`. In JS, use `mck.tok("chart-focus")` (or read the CSS variable with `getComputedStyle`), or the template's `colorway`.
- **Highlight, don't decorate:** context grey, one focus blue, optionally one navy accent; orange only for "worse". At most 6 categorical colors.
- **Direct labels** over legends. If a legend is unavoidable, use `.mck-legend` above the plot, top-left.
- **Tables** use `<table class="mck-table">` with `<th scope>`, right-aligned `.num` cells, `tr.is-focus` / `tr.is-total` rows and `td.is-muted` for suppressed cells. See `docs/cookbook/tables.md`.
- **Responsive:** max width ~960 px. Check the page at 390 px wide: columns become horizontal bars, the key moves on top, and wide tables scroll inside `overflow-x: auto`.
- **Tooltips** carry detail (exact values, n-size), never the only copy of the key number. Never show a group of fewer than 10 people or an individual's value in a tooltip, filter or drill-down.
- **Accessibility:** give each chart `role="img"` with an `aria-label` (or a visually hidden summary or data table: `class="sr-only"` in `mck-viz.css`), keep text ≥ 11 px, and never hijack scrolling.
- **Draw after the font loads:** `mck.ready(draw)` (= `document.fonts.ready.then(draw)`). Plotly caches label widths from its first render, so drawing with the fallback font leaves margins that clip long labels.
- **SharePoint strips inline `<script>`** from pages: host the chart page as a file (document library link or Embed web part), or use the Script Editor web part (classic) or an SPFx web part. Never paste a chart page into a text web part.
- **Never edit `dist/web/*`**. It is generated from `tokens/tokens.json` by `python tokens/build.py` (except `dist/web/vendor/`, a downloaded copy of Plotly.js; see `docs/formats.md`).
