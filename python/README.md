# mckviz

The McKesson data-visualization theme and helpers for matplotlib and Plotly: Libre Franklin, the token colors, insight
headlines, direct labels, number formats, maps and a chart lint. Part of the
[Data-Viz-Guide](https://github.com/amccown-mck/Data-Viz-Guide) kit; the rules are in its `docs/` and `AGENTS.md`.

## Install

From a release tag (fonts and map data are included):

```bash
pip install "mckviz[plotly] @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"
```

Drop `[plotly]` for matplotlib only. If the repo is private, see `docs/ci.md` for a token, or install the wheel from the
release bundle. Working on the kit itself: `pip install -e "./python[examples]"` from the repo root.

## Example

```python
import matplotlib.pyplot as plt
import mckviz as mv

mv.use()                                             # fonts, matplotlib style, Plotly template "mck"
cats, vals = ["Pharmacy Technician", "DC Associate", "Customer Care", "Sales"], [27.4, 24.1, 18.9, 10.6]
fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.barh(cats[::-1], vals[::-1], color=mv.highlight(cats[::-1], focus=cats[:2]))
mv.label_bars(ax, bars, fmt="{:.1f}%"); mv.clean_axes(ax, keep=("left",), grid=None); ax.set_xticks([])
mv.titles(fig, "Two frontline job families lose about 1 in 4 people a year", "Voluntary attrition by job family, FY26 (%)")
mv.source(fig, "Source: Synthetic data for illustration only")
mv.lint(fig); mv.save(fig, "attrition.png")
```

## API

| Need | Use |
|---|---|
| Bar/point colors for a highlight | `mv.highlight(labels, focus=..., accent=..., base=None)` (Plotly: `mv.pl_highlight`) |
| Series colors | `mv.categorical(n)` (blue, navy, bright blue, teal, mint, orange; raises above 6); `mv.FILL_TINTS` for large light fills only |
| Ramps | `mv.SEQUENTIAL["blue" \| "teal" \| "orange"]`, `mv.DIVERGING`, `mv.STEPS`, `mv.sequential_cmap()`, `mv.diverging_cmap()` |
| Headline + subtitle | `mv.titles(fig, headline, subtitle)` |
| Footnote + source | `mv.source(fig, "Source: ...", footnote=...)` |
| Direct labels | `mv.label_bars(ax, bars, fmt=...)`, `mv.label_line_ends(ax, fmt=...)` |
| Annotations | `mv.callout(ax, xy, title, body)`, `mv.shade_period(ax, start, end, label)` |
| Clean axes | `mv.clean_axes(ax, keep=("bottom",), grid="y")` |
| Numbers | `mv.fmt_num(v, kind="auto" \| "K" \| "M" \| "B" \| "pct" \| "plain", decimals=None, sign=False, prefix="")` (`"$4.3B"`, `"−$71M"`, `"+2.5%"`), `mv.signed(v, decimals, suffix)`, `mv.text_on(fill)` |
| Minimum n (people data) | `df, note = mv.suppress_small(df, "headcount", min_n=10, other_label="Other")`, then `mv.source(..., footnote=note)` |
| Real maps | `from mckviz import geo`: `geo.canvas(fig)`, `geo.Map(...)`, `geo.equal_earth`; US states, world countries and a county subset ship with the package |
| Translucent fills (Plotly) | `mv.rgba(C.negative, 0.12)`, `mv.rgba(C.focus, 0.4)` |
| Waterfall | `mv.waterfall(ax, steps, values, kinds, focus=..., semantic=None \| "up" \| "down", floor=None, horizontal=False)` |
| 100% stacked bar | `mv.hstack(ax, categories, [(name, values), ...], story=..., focus=..., base=counts, base_label="n")` |
| Dumbbell, rank slope | `mv.dumbbell(ax, labels, compare, value, flag_below=-5, tick_fmt="{:,.0f}")`, `mv.rank_slope(ax, names, before, after, focus=..., worse=...)` |
| Heat table | `mv.heat(ax, matrix, kind="diverging", bounds=None, focus_cols=..., n=None, key_ends=...)`, `mv.key_strip(ax, ramp, labels, xy=..., width=...)` |
| KPI | `mv.kpi_card(ax, value, sentence, change=..., vs=..., better="up", target=..., ring_value=..., dark=False)`, `mv.kpi_row(ax, cards)`, `mv.delta_label(change, unit=, vs=, better=)`, `mv.ring`, `mv.big`, `mv.small` |
| Plans and status | `mv.roadmap(ax, plan, milestones, today=...)`, `mv.tracker(ax, plan, milestones=...)`, `mv.status_column(ax, statuses)`, `mv.status(ax, x, y, key)`, `mv.sdot(...)`, `mv.status_key(name)` |
| Small multiples | `mv.multiples(fig, data, x=..., worse=..., ncols=3, ylim=None)` |
| Save | `mv.save(fig, path, dpi=200)`, which also lays out the titles and source |
| Check | `mv.lint(fig)` (matplotlib or Plotly; pass `headline=`, `subtitle=`, `source=` when they live in HTML); `strict=True` raises on errors |
| Plotly titles | `mv.pl_finish(fig, headline, subtitle, source_text, footnote)` |
| Color roles / all tokens | `mv.colors` (`focus`, `focus_light`, `context`, `accent`, `negative`, ...), `mv.TOKENS` |

The chart builders (`mckviz/charts.py`) draw into a matplotlib Axes (`multiples` into a Figure) with the house rules
built in, take plain lists or a pandas DataFrame (pandas stays optional), and return a namespace with the artists and
positions for further annotation. Add `mv.titles` and `mv.source`, and the figure passes `mv.lint(fig, strict=True)`.

`mv.lint` checks headline, subtitle and source, at most 6 colors (a colormap or ramp counts once), off-palette and
red-green colors, bars from zero, labels plus a value axis, legends, dual axes, pies over 5, rotated or tiny text and
3D. It cannot judge whether the headline is true or the chart type fits the question.

## Licenses

- **Code:** proprietary, McKesson internal (owner to confirm; no LICENSE file yet).
- **Fonts** (`mckviz/fonts/`): Libre Franklin, SIL Open Font License 1.1 (`mckviz/fonts/OFL.txt`).
- **Map data** (`mckviz/geodata/`): us-atlas and world-atlas TopoJSON (ISC), built from U.S. Census Bureau and Natural
  Earth boundaries, both in the public domain. Details in `mckviz/geodata/README.md`.

Colors and type come from `tokens/tokens.json` in the kit; `_tokens.json`, `mckviz.mplstyle`, `plotly_template.json`,
`VERSION` and `fonts/` in this package are copies synced by `tokens/build.py`. Do not edit them here.
