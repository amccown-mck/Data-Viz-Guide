# Typography, layout and chart anatomy

## 1. Typeface

**Libre Franklin** — the McKesson brand typeface. Open source (SIL OFL), so it can be bundled and embedded.

| Where | How |
|---|---|
| PowerPoint / Excel / Word | Install the TTFs from [`fonts/LibreFranklin`](../fonts/LibreFranklin) (or BrandHQ). Fallback: Arial. |
| HTML | Google Fonts: `family=Libre+Franklin:wght@300;400;500;600;700;800`. Stack: `'Libre Franklin', 'Franklin Gothic Book', Arial, sans-serif`. |
| Python (matplotlib) | `mckviz.use()` registers the bundled TTFs automatically. |
| R | Install the TTFs, then use `{systemfonts}` / `{showtext}`; `theme_mck(base_family = "Libre Franklin")`. |
| Power BI | Custom fonts only render where installed; theme falls back to Segoe UI in the service. |

**Brand signature for slide and page titles:** bold lead word(s) + light remainder, in McKesson Blue — e.g. **Workforce** intelligence gallery. Use it for *slide/page* titles only; **chart headlines are a single bold weight** in Navy.

## 2. Type roles

Sizes are for a 16:9 slide (13.33 × 7.5 in) and a 1× screen. Don't go below the footnote size.

| Role | Weight | Slide (pt) | Screen (px) | Color | Content |
|---|---|---|---|---|---|
| Headline | Bold 700 | 24 | 22 | Navy `#143359` | The insight. Full sentence, ≤ 2 lines, sentence case, no final period. |
| Subtitle | Regular 400 | 14 | 15 | `#505050` | Metric, unit, scope, period. |
| Data / series label | Medium 500 | 12 | 13 | `#505050` or series color | Direct labels. |
| Axis ticks, categories | Regular 400 | 11 | 12 | `#737373` | Minimal. |
| Callout | Bold title + Regular body | 12 | 13 | Navy | 2–5 word title, 1–2 line body. |
| Footnote / source | Light 300 | 9 | 11 | `#737373` | Definitions, caveats, source, as-of date. |
| Big number (KPI) | Light 300 | 54 | 56 | Navy | One number + a short sentence. |

- **Sentence case** everywhere (not Title Case).
- Bold within labels only to **echo the highlight** (e.g., the focus category name).
- Keep line length ≤ ~60 characters for headlines; balance two-line headlines (no single dangling word).

## 3. Chart anatomy

```
┌──────────────────────────────────────────────────────────────┐
│ Headline — the insight, in a full sentence (bold, navy)      │  ← 1
│ Subtitle — metric, unit, scope, period (regular, grey)       │  ← 2
│ ■ Key (only if direct labels won't work), top-left            │  ← 3
│                                                              │
│      ┌─ callout title                                        │  ← 5
│      │  1–2 lines of why                                     │
│  ████████████████████  27.4%   ← direct labels               │  ← 4
│  ██████████████  19.0%                                       │
│  ─────────────────────── baseline                            │
│                                                              │
│ *Footnote: definitions, caveats                              │  ← 6
│ Source: system, as-of date, population                       │  ← 7
└──────────────────────────────────────────────────────────────┘
```

1. **Headline** — top-left, aligned to the left edge of the outermost labels (not the plot area).
2. **Subtitle** — directly below the headline.
3. **Key/legend** — top-left above the plot, horizontal, in the same order as the data. Only when needed.
4. **Plot** — minimal axes; direct labels; light baseline; gridlines only when there are no value labels.
5. **Annotations** — next to the data they explain.
6. **Footnotes** — then **7. Source** — bottom-left, smallest text.

Everything is **left-aligned on one edge**. No centered titles. No chart borders or boxes.

## 4. Spacing and proportions

| Element | Rule |
|---|---|
| Bar width : gap | ≈ **2 : 1** (bar fills ~67% of its band) |
| Line weight | ≈ **2×** axis weight (2 px / 2.25 pt); context lines 1.25 px |
| Donut hole | ~62% of diameter |
| Outer padding | 24 px (screen) / 0.3 in (slide) |
| Headline → subtitle | tight (6 px) |
| Subtitle → plot | ~12–16 px |
| Plot → footnote | ~16 px |

## 5. Aspect ratios

| Medium | Ratio | Notes |
|---|---|---|
| Full slide chart | 16:9 | Leave the slide title zone for the headline. |
| Half-slide / report column | 4:3 | Two per slide max. |
| Web inline | 16:10 | Max width ~960 px. |
| Mobile | 4:5 portrait | Horizontal bars instead of columns; key on top. |
| Social | 1:1 or 4:5 | Single point, big type. |

## 6. Axes, gridlines and labels

- **Category axis:** labels only; no tick marks; no axis title if the subtitle says what it is.
- **Value axis:** hide it when bars/points carry value labels. Otherwise: light horizontal gridlines, no axis line, ticks at round numbers, unit in the subtitle.
- **Y-axis title** (when needed): horizontal, at the top-left of the axis — never rotated 90°.
- **Time axes:** show the year on the first tick and at year changes (`Q1 '25`, `Q2`, `Q3`, `Q4`, `Q1 '26`).
- **Long category names:** use horizontal bars rather than rotated labels.
