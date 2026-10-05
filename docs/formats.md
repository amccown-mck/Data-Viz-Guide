# Formats: designing for the medium

The same finding needs different treatment in a live meeting, a PDF, a phone or a dashboard. Rules below build on [principles.md](principles.md).

## Presentations (PowerPoint)

**Clarity and simplicity.** A slide is on screen for well under a minute and the audience can't explore it.

- **One message per slide**; the slide title *is* the chart headline (don't repeat it inside the chart).
- **≤ 2 charts per slide.** Never a wall of charts; never dense text beside a chart.
- **Build-ups** (2–5 steps) for complex charts:
  1. *Set the scene* — axes, labels and a first slice of data (e.g., totals only).
  2. *Highlight the insight* — show the rest greyed out; color only the point.
  3. *Show the full picture* — all data; add legend entries only as their categories appear.
  - *Alternative:* keep all data visible but **mask** non-focus columns (lighter tints) and reveal on the next slide.
- Keep **category order and scales fixed** across the build so marks don't jump.
- **Dark backgrounds** (Deep Navy) for dim rooms, keynotes, town halls: white text, `focus_on_dark` highlight.
- Use **native, editable charts** (not pasted images) so numbers can be updated — start from the template and starter deck in [`dist/office`](../dist/office) (set-up guide: [office-setup.md](office-setup.md)).
- Put footnotes and source on every slide with data; speaker notes can carry method detail.

## Reports and print (PDF, Word, memos)

- Three chart sizes on a column grid:
  - **Featured** — full page or across a spread; the hero exhibit.
  - **Editorial** — spans 2 of 3 columns, sits with running text.
  - **Inline** — one column, next to the paragraph it supports.
- Charts **can be denser** than on slides (the reader controls pace) but still carry an insight headline.
- **Big-number callouts** (Bold, large) work well in margins or text columns.
- Number every exhibit ("Exhibit 3") and refer to it in the text.
- Export **vector** (SVG/PDF/EMF) for print; PNG at 300 dpi otherwise.

## Web and HTML (articles, microsites, internal tools)

- Use the **chart-card pattern**: headline, subtitle and source in HTML text; the chart library draws only the data. Template: [`templates/html/chart-card.html`](../templates/html/chart-card.html) (copy it; it draws after the font loads and swaps end labels for a top key on phones); CSS: [`dist/web/mck-viz.css`](../dist/web/mck-viz.css).
- Charts must be **responsive**: fixed aspect on desktop, re-flowed on mobile.
- **Tooltips** hold detail (exact values, n-size) — never the only place the key number lives.
- Provide **alt text** or a visually hidden text summary (headline + 2–3 numbers).
- Web recipes (a full HTML page each, using the files below) are in the **HTML / JavaScript** section of the cookbook pages: [waterfall](cookbook/waterfall.md), [100% stacked bar](cookbook/stacked-bar.md), [heatmap](cookbook/heatmap.md), [KPI tiles](cookbook/kpi-big-number.md), plans and status.

### Web files (`dist/web/`)

| File | What it is |
|---|---|
| `mck-viz.css` | Token variables (`--mck-*`), the chart card, tables and the dashboard components below |
| `mck-viz.js` | Helpers on `window.mck` (a plain script, no modules); also defines `window.MCK_PLOTLY_TEMPLATE` |
| `mck-plotly-template.js` | The Plotly template alone (optional when `mck-viz.js` is loaded) |
| `vega-lite-config.json` | Vega-Lite `config` |
| `vendor/plotly.min.js` | Plotly.js **4.1.1** (the version the online card loads), about **4.8 MB** (4,815,814 bytes); MIT licence in `vendor/LICENSE-plotly.txt`. Downloaded, not generated: to update, fetch `https://cdn.plot.ly/plotly-<version>.min.js` and change the version in both chart cards |

Everything except `vendor/` is generated from `tokens/tokens.json` by `tokens/build.py`; never edit it by hand.

### Dashboard components (`mck-viz.css`)
All flat (no shadows, gradients or rounded cards) and token-driven. A class reference sits at the top of the components block in the CSS.

- **`.mck-grid`**: card grid with the 16 px gutter (`--mck-gutter`): 1 column under 560 px, 2 up to 980 px, 3 above. `.mck-grid__wide` spans the row; `.mck-grid__span-2` spans two columns on wide screens.
- **`.mck-kpi` tile**: `.mck-kpi__name`, `.mck-kpi__value` (the `kpi` role: Bold, 56 px, navy), `.mck-kpi__delta` (`is-up`/`is-down` set ▲/▼ for direction; `is-good`/`is-bad` set green or orange text for favorability, judged from the audience's view), `.mck-kpi__label` (one sentence), `.mck-kpi__meter` (`style="--value: 62%; --target: 75%"`), `.mck-kpi__gap` and `.mck-kpi__source`. Add `.mck-kpi--dark` for Deep Navy. A bare `<p class="mck-kpi">` still styles just the number.
- **`.mck-status`**: color + symbol + word, never color alone: `<span class="mck-status mck-status--at-risk">At risk</span>`. The keys and symbols come from `color.status` (on track ✓, at risk !, off track ✕, not started –, complete ✓); off track and at risk are bold. `.mck-status--pill` adds a hairline outline.
- **`.mck-tracker`**: status tracker table (hairlines, top-aligned rows, `tr.is-exception`, `.owner`, `.due`, `.slip`, `.progress`). Wrap wide tables in `.mck-scroll`.
- **Heat tables**: `<table class="mck-table mck-table--heat">` with `<td class="mck-heat mck-heat-blue-1">` … `-6` (also `-orange-`, `-teal-`, and `mck-heat-div-1` … `-7`); each class sets the fill and the readable text color. `is-suppressed` marks n < 10; `is-focus-col` outlines a column.
- **Dark surfaces:** inside `.mck-chart--dark`, the KPI tile, status and tracker switch to their on-dark tokens.

### JavaScript helper (`mck-viz.js`)
Load `<script src="mck-viz.js"></script>` before your chart script. It mirrors the Python helpers, so web and Python charts format numbers alike:

| Function | Does |
|---|---|
| `mck.tok("chart-focus")` | A token color (the page's CSS variable if it overrides one) |
| `mck.highlight(labels, {focus, accent})` | Grey context, blue focus, navy accent (= `mv.highlight`) |
| `mck.fmtNum(v, {kind, decimals, sign, prefix, suffix})` | `"$4.3B"`, `"12K"`, `"19.9%"`, `"+2.5%"`, a true minus (= `mv.fmt_num`) |
| `mck.suppressSmall(rows, "n", {minN: 10, otherLabel: "Other"})` | `[rows, footnote]`: merges or drops groups under 10 (= `mv.suppress_small`) |
| `mck.textOn(hex)` | White or navy text for a fill (= `mv.text_on`) |
| `mck.status("at_risk")` | `{color, symbol, word, ink}` |
| `mck.plotlyLayout(kind, extra)` | The layout for `"bar"`, `"line"`, `"waterfall"`, `"stacked"`, `"heatmap"`, `"sankey"` or `"roadmap"` on the McKesson template (small margins, no legend, hidden value axis where bars are labelled); `extra` is deep-merged in |
| `mck.zeroLine`, `mck.alpha`, `mck.srTable`, `mck.ready`, `mck.plotConfig` | Baseline shape, rgba wash, hidden data table, draw after the font loads, Plotly config |

### Offline and locked-down intranet pages
[`templates/html/chart-card-offline.html`](../templates/html/chart-card-offline.html) loads nothing from the internet: Libre Franklin through `@font-face` from a `fonts/` folder next to the page (copy the TTFs and `OFL.txt` from `fonts/LibreFranklin/`), Plotly from `vendor/plotly.min.js`, and `mck-viz.css`/`mck-viz.js` from `dist/web/`. The comment at its top lists the folder to deploy. Expect about 5.5 MB per page folder, nearly all of it Plotly; serve it from one shared location so browsers cache it.

### SharePoint
SharePoint pages **strip inline `<script>`**, so a chart page pasted into a text or code web part will not draw. Host the page as a file instead (upload it with its `mck-viz.*`, `vendor/` and `fonts/` files to a document library and link to it, or show it in an Embed web part if your tenant allows it), use the Script Editor web part where it is still enabled (classic pages), or package the chart as an SPFx web part.

### Mobile and small screens
- Design **portrait** (4:5); readers scroll vertically.
- **Columns → horizontal bars**; long category names fit and scroll naturally.
- **Adjust hierarchy:** swap line-end labels for a compact key on top; move callouts above the plot.
- **Reduce complexity:** one highlighted series, everything else grey; drop secondary annotations.
- **Fewer text elements, larger:** headline, one insight, axis labels, source. Shorten the headline to its core claim.

### Interactivity (only with a purpose)
Useful interactions, each must earn its place:

| Interaction | Use for |
|---|---|
| Hover / tooltip | Reveal exact values and n-sizes without labelling everything |
| Cursor tracking | Reading values across multiple time series |
| Toggles / filters | Switch populations (BU, region, level) |
| Sliders | Scenario inputs (attrition rate, hiring volume) in SWP models |
| Range selection / zoom | Focus a time window |
| Play / pause / scrub | Animate change over time |

- The **default view must tell the story** without any interaction.
- Respect people-data rules in drill-downs and tooltips (**minimum group size**).

### Long-form and "scrolly-telling"
- Text scrolls; the chart stays pinned and **updates to match the paragraph** (highlight the category being discussed).
- On mobile, replace side-by-side layouts with **in-line snapshots** of the chart at each step.
- **Never hijack scrolling** (auto-snapping); it hurts accessibility.

## Dashboards (Power BI / Fabric)

Dashboards are **exploratory**, but the same visual rules apply.

- Apply the theme [`dist/powerbi/mckesson-dataviz-theme.json`](../dist/powerbi/mckesson-dataviz-theme.json) (View → Themes → Browse).
- **Top-left = most important.** A row of 3–5 KPI cards, then the primary chart, then detail.
- Each visual gets a **question-style or insight title** (dynamic titles via DAX measures where the insight changes with filters).
- Use **conditional formatting** to apply highlight logic (focus vs. context) rather than rainbow categorical colors.
- Keep **filters/slicers** in one consistent place (left rail or top bar); show active filters.
- Enforce **row-level security** and **minimum group sizes** (e.g., a measure that blanks results when n < 10).
- One dashboard page ≈ one decision. If a page needs scrolling, it's two pages.

## Social and single-asset graphics

- One point, readable at thumbnail size without zooming.
- Use a **3-tone** combination (background + 1–2 foregrounds) — see `color.social` in the tokens.
- Assets must **stand alone**: headline, key, source and McKesson logo on the image itself.
- Break complex stories into a **sequence** (carousel / thread), one simple chart per frame.
- Use the approved social templates from BrandHQ; follow the social team's process.

## Animation and motion

- **Purposeful only:** motion shows change over time, a transition or aggregation — never decoration.
- **Sequence entrances** in reading order; bring the key element in last or highlight it.
- **Easing:** natural acceleration/deceleration. No overshoot or bounce.
- **Natural movement:** lines draw left → right; bars grow from the baseline; bubbles grow from the center.
- **Say what you see:** narration and on-screen text match what the data is doing at that moment.
- **Exits mirror entrances.** Keep it simple; split complex charts into sequences.
