# Color

All values live in [`tokens/tokens.json`](../tokens/tokens.json) — the single source of truth. Platform files in [`dist/`](../dist) are generated from it. Swatches: [`dist/palette.png`](../dist/palette.png). Accessibility checks: [`dist/palette-report.md`](../dist/palette-report.md).

## 1. The McKesson brand palette (what we draw from)

**Core palette** — use for ~80% of any piece.

| Name | Hex | Notes |
|---|---|---|
| McKesson Blue | `#005A8C` | Primary brand color. Our **focus** color in charts. |
| McKesson Navy | `#143359` | Headlines, totals, dark series. |
| McKesson Orange | `#EF8200` | Core accent — our **accent** color in charts. |
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
| Amber | Payer | `#FFE9B3` | `#FFD366` | `#FFB502` | — |

> Source: McKesson Social Media Guide (Extended Audience Palette) and FY26 Impact Report. Full swatches and ASE files: BrandHQ.

## 2. Chart color roles (how we use it)

Think in **roles**, not hex codes. Code and templates reference roles so the palette can evolve.

| Role | Token | Hex | When |
|---|---|---|---|
| Context | `chart.context` | `#B4B0A5` | Data the reader should see but not focus on |
| Context (light) | `chart.context_light` | `#DEDBD1` | De-emphasized stack segments, masked columns, dumbbell bars |
| **Focus** | `chart.focus` | `#005A8C` | What the headline is about; default single-series color |
| **Accent** | `chart.accent` | `#EF8200` | The one element that must pop (esp. against blue) |
| Total | `chart.total` | `#143359` | Totals, subtotals, benchmark / target lines |
| Axis | `chart.axis` | `#8C8C8C` | Baselines, axis lines |
| Grid | `chart.grid` | `#E6E4DE` | Gridlines — only when labels don't carry values |
| Annotation | `chart.annotation` | `#143359` | Callout text and leader lines |
| Focus on dark | `chart.focus_on_dark` | `#66C4FF` | Highlight on Deep Navy backgrounds |
| Context on dark | `chart.context_on_dark` | `#5A7194` | De-emphasis on Deep Navy backgrounds |

### The three highlight patterns
1. **Focus** (default): everything grey, headline item(s) blue.
2. **Uniform + accent**: all bars blue (a single series with no "context"), one bar orange.
3. **Focus + accent**: grey context, blue for the main group, orange for the single exception the headline calls out.

Python: `mv.highlight(labels, focus=..., accent=..., base=None)`; R: `mck_highlight()`; HTML/CSS: `var(--mck-chart-focus)` etc.

## 3. Semantic colors

| Meaning | Fill | Text on white |
|---|---|---|
| Positive / increase / favorable | Teal `#00AF9D` | `#00737A` |
| Negative / decrease / unfavorable | Orange `#EF8200` | `#A75B00` |
| Neutral / no change | `#B4B0A5` | `#505050` |

- **Blue–orange, not red–green.** Red/green is the most common color-vision conflict and red is not a brand color.
- Only use semantic color when "good vs. bad" *is* the message (variance to plan, benchmark gaps). Otherwise use focus/context.
- Headcount growth isn't automatically "good" — pick semantic colors from the audience's point of view (e.g., cost reduction = favorable).

## 4. Categorical palette (fixed order)

When categories must be distinguished (e.g., 4 business units in a line chart), use the colors **in this order**:

| # | Hex | Name | Lines/text? |
|---|---|---|---|
| 1 | `#005A8C` | McKesson Blue | yes |
| 2 | `#EF8200` | Orange | fill; label it |
| 3 | `#00AF9D` | Teal | fill; label it |
| 4 | `#143359` | Navy | yes |
| 5 | `#66C4FF` | Azure mid | fill only |
| 6 | `#FFB502` | Amber | fill only |
| 7 | `#00622C` | Green dark | (avoid if possible) |
| 8 | `#D9F14E` | Lime | (avoid if possible) |

- **≤ 6 categories.** Tested for deuteranopia/protanopia/tritanopia — the first 6 stay separable (min ΔE ≥ 14). Beyond 6, group the tail into **"Other"** in context grey.
- Keep a category's color **constant across the whole deck** (e.g., Technology is always teal).
- Business-unit colors *may* follow the audience palette (Pharmacy = green, Oncology = teal, …) when the audience expects it — check separability if you do.

## 5. Sequential and diverging scales

| Scale | Stops (light → dark) | Use |
|---|---|---|
| Sequential blue | `#E6F3FB` `#B6E2FA` `#66C4FF` `#009EFF` `#0A5FBC` `#143359` | Heatmaps, choropleths of a single measure (headcount, tenure, exposure) |
| Sequential teal | `#E6F7F5` `#B3E7E2` `#66CFC4` `#00AF9D` `#00737A` `#004B4F` | Alternate single-measure scale |
| Sequential orange | `#FFF3E0` `#FFD9A8` `#F7B25C` `#EF8200` `#A75B00` `#6B3A00` | Risk / intensity (e.g., flight risk) |
| Diverging orange–blue | `#A75B00` `#EF8200` `#F7C180` **`#EFEDE7`** `#99BDD1` `#005A8C` `#143359` | Above/below benchmark, variance to plan, change vs. prior |

- Diverging scales need a **meaningful midpoint** (0, benchmark, target) — center the scale on it and make the range symmetric.
- Prefer **5–7 binned classes** for maps and heatmaps shown on slides; continuous is fine for interactive.
- Put text on cells with `mv.text_on(fill)` (white on dark cells, navy on light).

## 6. Backgrounds and dark mode
- Default: **white**. Panels/callout boxes: Light Sand `#EFEDE7`.
- **Dark slides** (Deep Navy `#0B3266`) for dim rooms, keynotes and social cards: white text, `focus_on_dark` highlight, `context_on_dark` for the rest.
- Social / single-KPI cards use a 3-tone combination (background + 1–2 foregrounds); see `color.social` in tokens.

## 7. Accessibility rules
- Text ≥ 4.5:1 contrast. The lightest text color is `text.muted #737373`.
- Orange, teal, azure and amber are **below 3:1** on white as thin lines/text — use them as **fills** and add labels, or use their `dark` step for text.
- Never encode meaning by color alone — add labels, patterns, position or shape.
- Check new palettes with `python tokens/build.py` → `dist/palette-report.md`.
