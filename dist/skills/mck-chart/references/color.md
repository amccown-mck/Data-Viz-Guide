# Color

All values live in [`tokens/tokens.json`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/tokens/tokens.json) — the single source of truth. Platform files in [`dist/`](https://github.com/amccown-mck/Data-Viz-Guide/tree/main/dist) are generated from it. Swatches: [`dist/palette.png`](https://github.com/amccown-mck/Data-Viz-Guide/raw/main/dist/palette.png). Accessibility checks: [`dist/palette-report.md`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/palette-report.md).

## 1. The McKesson brand palette (what we draw from)

**Core palette** — use for ~80% of any piece.

| Name | Hex | Notes |
|---|---|---|
| McKesson Blue | `#005A8C` | Primary brand color. Our **focus** color in charts. |
| McKesson Navy | `#143359` | Chart headlines, totals, benchmarks. Our **accent** color in charts. Slide titles are McKesson Blue. |
| McKesson Orange | `#EF8200` | A brand color, but in charts it means **worse**. Never decoration, never the accent (see [Orange means worse](#orange-means-worse)). |
| Sand (warm grey) | `#DEDBD1` | Backgrounds, de-emphasized fills. |
| Deep Navy (FY26) | `#0B3266` | Dark slides / cards. |
| Light Sand (FY26) | `#EFEDE7` | Panels, callout boxes, shaded periods. |
| Body text (FY26) | `#505050` | Body copy and chart labels. |

**Extended audience palette** — the ~20%. Each family *loosely* maps to a business area, but **any color can be used in data viz** when a chart needs more distinct hues. Steps are light / mid / base / dark.

| Family | Business association | Light | Mid | Base | Dark |
|---|---|---|---|---|---|
| Lime | Culture / People / Patients | `#F7FCDC` | `#E8F795` | `#D9F14E` | — |
| Green | Pharmacy | `#B3E7D2` | `#66CFA4` | `#00AF68` | `#00622C` |
| Mint | Biopharma | `#B4F0DE` | `#69E2BC` | `#05CE90` | `#008264` |
| Teal | Oncology / Specialty | `#B3E7E2` | `#66CFC4` | `#00AF9D` | `#00737A` |
| Sky | Providers | `#B3ECFF` | `#66D8FF` | `#00BEFF` | `#0074D0` |
| Azure | Health Systems | `#B6E2FA` | `#66C4FF` | `#009EFF` | `#0A5FBC` |

> Source: McKesson Standard Template (Jan 2026), McKesson Social Media Guide and FY26 Impact Report. Full swatches and ASE files: BrandHQ.

**The 80/20 rule, and our audience color.** The McKesson Standard Template says: core palette for about 80% of any piece, plus **one audience color**. Workforce Innovation uses the **teal family**, which is how the template's own infographic slides use color: McKesson Blue and its bright blues, with teal and mint as the supporting hue. Green (`#00AF68`) is reserved for meaning (better, on track), not decoration.

**Amber (the Payer family) is not used in charts.** Its base `#FFB500` appears in one place only: the *at risk* status color (section 4). Never as a data series, bar, line or fill.

## 2. Chart color roles (how we use it)

Think in **roles**, not hex codes. Code and templates reference roles so the palette can evolve.

| Role | Token | Hex | When |
|---|---|---|---|
| Context | `chart.context` | `#B4B0A5` | Data the reader should see but not focus on |
| Context (light) | `chart.context_light` | `#DEDBD1` | De-emphasized stack segments, masked columns, dumbbell bars |
| **Focus** | `chart.focus` | `#005A8C` | What the headline is about; default single-series color. The color used most |
| Focus (light) | `chart.focus_light` | `#66C4FF` | The series fill in the "uniform + accent" pattern; a secondary series |
| **Accent** | `chart.accent` | `#143359` | The one exception that must pop (navy, against light blue or next to a blue group). Never orange |
| Total | `chart.total` | `#143359` | Totals, subtotals, benchmark / target lines |
| Axis | `chart.axis` | `#8C8C8C` | Baselines, axis lines |
| Grid | `chart.grid` | `#E6E4DE` | Gridlines — only when labels don't carry values |
| Annotation | `chart.annotation` | `#143359` | Callout text and leader lines |
| Focus on dark | `chart.focus_on_dark` | `#66C4FF` | Highlight on Deep Navy backgrounds |
| Context on dark | `chart.context_on_dark` | `#5A7194` | De-emphasis on Deep Navy backgrounds |

### The three highlight patterns
1. **Focus** (default): everything grey `#B4B0A5`, headline item(s) blue `#005A8C`.
2. **Uniform + accent**: all bars light blue `#66C4FF` (a single series with no "context"), the one exception navy `#143359`.
3. **Focus + accent**: grey context, blue for the main group, navy for the single exception the headline calls out.

Python: `mv.highlight(labels, focus=..., accent=..., base=None)`; for pattern 2 pass `base=C.focus_light`: `mv.highlight(labels, accent=X, base=C.focus_light)`. R: `mck_highlight(levels, accent = x, base = mck_colors$focus_light)`. HTML/CSS: `var(--mck-chart-focus)` etc.

### Orange means worse
Orange `#EF8200` has one job in our charts: it marks something **worse**. Negatives, decreases and losses, below target or benchmark, shortfalls, and the low end of the orange–blue diverging scale. Executives read orange as a warning, so a decorative orange bar sends the wrong message.

- Use it through `semantic.negative` (text: `semantic.negative_text` `#A75B00`), never through the accent role.
- Don't use orange to highlight, to decorate, or to make one item "pop". Use navy for that.
- If nothing in the chart is worse, the chart has no orange.

## 3. Semantic colors: better and worse

| Meaning | Fill | Text on white |
|---|---|---|
| Better / favorable | Green `#00AF68` | `#007A48` |
| Worse / below target / unfavorable | Orange `#EF8200` | `#A75B00` |
| Neutral / no change | `#B4B0A5` | `#505050` |

- **Always pair the color with a symbol or words** (▲ ▼, "+6 pts", "13 pts short"). Green vs. orange separates well in lightness but less well in hue for color-blind readers, so color never carries the meaning alone.
- Only use semantic color when "good vs. bad" *is* the message (variance to plan, benchmark gaps, KPI deltas, waterfalls). Otherwise use focus and context.
- Judge "better" from the audience's point of view: a cost reduction is favorable; days to fill going up is worse; headcount growth isn't automatically good.
- **No red vs. green in data.** Red appears only as a status color (section 4).

## 4. Status colors (red, amber, green)

For **status only**: initiative trackers, roadmaps, milestone plans, the status column of a scorecard. These are the McKesson Standard Template's Initiative Tracker colors.

| Status | Color | Symbol and word |
|---|---|---|
| On track | `#00AF68` | ✓ On track |
| At risk | `#FFB500` | ! At risk |
| Off track | `#DA2103` | ✕ Off track |
| Not started | `#BFBFBF` | – Not started |
| Complete | `#005A8C` | ✓ Complete |

- **Never for data series.** A bar, line or map is never colored red/amber/green; status describes a workstream, not a measure.
- **Always the symbol and the word**, not color alone: red and green are the most common color-vision conflict.
- Use them as small dots, chips or a thin status column, not large fills. `mv.STATUS` (Python), `mck_status` (R) and `--mck-status-*` (CSS) hold them.

## 5. Categorical palette (fixed order)

When categories must be distinguished (e.g., 4 business units in a line chart), use the colors **in this order**. They come from the template's infographic slides: blues with teal and mint.

| # | Hex | Name | Lines/text? |
|---|---|---|---|
| 1 | `#005A8C` | McKesson Blue | yes |
| 2 | `#00AF9D` | Teal | fill; label it (text: `#00737A`) |
| 3 | `#143359` | Navy | yes |
| 4 | `#009DFF` | Bright blue | fill; label it |
| 5 | `#05CE90` | Mint | fill only; label it |
| 6 | `#EF8200` | Orange | last resort only; fill, label it |
| 7 | `#B3ECFF` | Light sky | fills only |
| 8 | `#B3E7E2` | Light teal | fills only |

**Ordered steps** (stages of a pipeline, a journey, a timeline) use the template's blue-to-green sequence: `#005A8C` `#009DFF` `#00BEFF` `#00AF9D` `#05CE90` `#00AF68` (`color.steps`, `mv.STEPS`). Not for data magnitude (use a sequential scale) or unordered categories.

- **Prefer ≤ 5 categories.** Orange is the last-resort 6th: reach for it only when you truly need six hues, because readers will still read it as "worse". Beyond 6, group the tail into **"Other"** in context grey. Check separability with `python tokens/build.py` → `dist/palette-report.md`.
- Blue and navy sit next to each other in stacks: keep the white separators between segments.
- Green and amber are not category colors: green means better or on track, amber means at risk.
- Keep a category's color **constant across the whole deck** (e.g., Technology is always teal).

## 6. Sequential and diverging scales

| Scale | Stops (light → dark) | Use |
|---|---|---|
| Sequential blue | `#E6F3FB` `#B6E2FA` `#66C4FF` `#009EFF` `#0A5FBC` `#143359` | **Default** for one measure, light to dark: heat tables, heatmaps, choropleths (headcount, tenure, exposure) |
| Sequential teal | `#E6F7F5` `#B3E7E2` `#66CFC4` `#00AF9D` `#00737A` `#004B4F` | Alternate single-measure scale |
| Sequential orange | `#FFF3E0` `#FFD9A8` `#F7B25C` `#EF8200` `#A75B00` `#6B3A00` | Only when darker explicitly means **worse** (risk, e.g., flight risk). Say so in the subtitle or key |
| Diverging orange–blue | `#A75B00` `#EF8200` `#F7C180` **`#EFEDE7`** `#99BDD1` `#005A8C` `#143359` | Above/below benchmark, variance to plan, change vs. prior. Orange = below (worse), blue = above |

- Diverging scales need a **meaningful midpoint** (0, benchmark, target) — center the scale on it and make the range symmetric.
- Prefer **5–7 binned classes** for maps and heatmaps shown on slides; continuous is fine for interactive.
- Put text on cells with `mv.text_on(fill)` (white on dark cells, navy on light).

## 7. Backgrounds and dark mode
- Default: **white**. Panels/callout boxes: Light Sand `#EFEDE7`.
- **Dark slides** (Deep Navy `#0B3266`) for dim rooms, keynotes and social cards: white text, `focus_on_dark` highlight, `context_on_dark` for the rest.
- Social / single-KPI cards use a 3-tone combination (background + 1–2 foregrounds); see `color.social` in tokens.

## 8. Accessibility rules
- Text ≥ 4.5:1 contrast. The lightest text color is `text.muted #737373`.
- Orange, green, teal, bright blue, mint and light blue are **below 3:1** on white as thin lines/text: use them as **fills** and add labels, or use their text step (`#A75B00`, `#007A48`, `#00737A`) for text.
- Never encode meaning by color alone — add labels, patterns, position or shape.
- Check new palettes with `python tokens/build.py` → `dist/palette-report.md`.
