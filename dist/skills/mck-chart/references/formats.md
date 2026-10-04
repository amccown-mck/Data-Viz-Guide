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
- Use **native, editable charts** (not pasted images) so numbers can be updated — start from the template and starter deck in [`dist/office`](https://github.com/amccown-mck/Data-Viz-Guide/tree/main/dist/office) (set-up guide: [office-setup.md](office-setup.md)).
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

- Use the **chart-card pattern**: headline, subtitle and source in HTML text; the chart library draws only the data. Template: [`templates/html/chart-card.html`](../assets/html/chart-card.html) (copy it; it draws after the font loads and swaps end labels for a top key on phones); CSS: [`dist/web/mck-viz.css`](../assets/web/mck-viz.css).
- Charts must be **responsive**: fixed aspect on desktop, re-flowed on mobile.
- **Tooltips** hold detail (exact values, n-size) — never the only place the key number lives.
- Provide **alt text** or a visually hidden text summary (headline + 2–3 numbers).

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

- Apply the theme [`dist/powerbi/mckesson-dataviz-theme.json`](../assets/powerbi/mckesson-dataviz-theme.json) (View → Themes → Browse).
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
