---
applyTo: "**/*.py"
---
# Python charts (matplotlib, Plotly)

Applies to any Python file that draws a chart. The full rules are in `AGENTS.md` and `docs/principles.md`, and the per-chart recipes are in `docs/cookbook/`.

## Setup
```python
import matplotlib
matplotlib.use("Agg")            # scripts and CI; omit in notebooks
import matplotlib.pyplot as plt
import mckviz as mv

mv.use()                         # Libre Franklin, house matplotlib style, Plotly template "mck" as the default
C = mv.colors
```

## Rules
- **No hex literals and no named colors** (`"red"`, `"tab:blue"`). Use roles: `C.focus`, `C.context`, `C.context_light`, `C.accent`, `C.total`, `C.annotation`, `C.text`, `C.text_muted`, `C.headline`, `C.negative_text`, `C.positive_text`. Use ramps from `mv.SEQUENTIAL[...]` and `mv.DIVERGING`, and series colors from `mv.categorical(n)` (≤ 6).
- **Highlight with `mv.highlight(labels, focus=..., accent=...)`**: grey everything, then color only what the headline names. Bold the matching tick label in `C.headline`.
- **Titles through the helpers.** Use `mv.titles(fig, headline, subtitle)` and `mv.source(fig, "Source: ...", footnote=...)`, then `mv.save(fig, path)`, which lays them out. Don't use `ax.set_title` or `fig.suptitle`. In Plotly, use `mv.pl_finish(fig, headline, subtitle, source_text, footnote)`, or the HTML chart-card pattern from `examples/python/gallery_plotly.py`.
- **Headline numbers come from variables** (`f"... {share:.0f}% ..."`), computed from the same data the chart plots.
- **Direct labels:** `mv.label_bars`, `mv.label_line_ends`, and `ax.text` at the data. When bars are labelled, remove the value axis (`ax.set_xticks([])`) and the gridlines (`mv.clean_axes(ax, keep=(...), grid=None)`). Don't use `ax.legend()` unless labels would collide, and then put it top-left.
- **Bars:** `height`/`width = mv.TOKENS["chart"]["bar"]["band_fill"]` (0.67), starting at zero, sorted by value unless there is a natural order. No rotated tick labels: switch to horizontal bars.
- **Numbers:** `mv.signed(v, decimals, suffix)` for deltas (true minus, explicit +), and `mv.text_on(fill)` for text placed on a colored mark.
- **People data:** drop or merge any group with n < 10 before plotting, and keep individual values out of hover text.
- **Output:** PNG at `dpi=200` for slides, SVG/PDF for print, `write_html(..., include_plotlyjs="cdn")` for the web. Example scripts write to `examples/output/`; scratch output goes to `out/` (gitignored) or `tempfile.gettempdir()`.
- **Check your work:** run `mv.lint(fig)` and fix every error, then open the rendered file and look at it. In `docs/cookbook/` code blocks, start with `# verified runnable (from the repo root)` and run `python tools/check_snippets.py <page>`.
