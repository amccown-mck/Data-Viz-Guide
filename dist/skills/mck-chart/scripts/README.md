# Using mckviz from this skill

`mckviz` is the kit's Python package: house matplotlib style, Plotly template, Libre Franklin fonts, color roles, chart furniture, `mv.lint`, and real maps (`mckviz.geo`). Install it from the tagged release:

```
pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"
pip install plotly pandas          # if the chart uses them
python scripts/check_env.py        # confirms the package and font are ready
```

Then, in the chart script:

```python
import mckviz as mv
mv.use()                                   # fonts + style + Plotly template "mck"
C = mv.colors                              # C.focus, C.context, C.accent, C.negative, ...
df, note = mv.suppress_small(df, "headcount")      # no group under 10 people; note -> footnote
# ... build the chart with mv.highlight(...), mv.label_bars(...), mv.fmt_num(...) ...
mv.titles(fig, headline, subtitle)
mv.source(fig, "Source: ...", footnote=note or None)
mv.lint(fig)                               # fix every error, read every warning
mv.save(fig, "out/chart.png", dpi=200)
```

For a Plotly chart whose headline, subtitle and source live in HTML (the chart-card pattern), pass them to the lint: `mv.lint(fig, headline=..., subtitle=..., source=...)`. In CI, `mv.lint(fig, strict=True)` raises on any error.

Without network access to GitHub, ask the user for the release bundle (`DataViz-Starter-Kit-McKesson-Edition-v1.1.0.zip`), or use the colors in `references/rules.md` as named constants.
