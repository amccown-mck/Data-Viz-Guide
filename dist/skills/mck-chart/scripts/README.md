# Using mckviz from this skill

`mckviz` is the kit's Python package: house matplotlib style, Plotly template, Libre Franklin fonts, color roles, chart furniture, `mv.lint`, and real maps (`mckviz.geo`). Install it in this order, stopping at the first that works:

```
pip install assets/python/mckviz-*.whl                                       # 1. the wheel shipped in this folder (no GitHub needed)
pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"       # 2. the tagged release on GitHub
pip install plotly pandas          # if the chart uses them
python scripts/check_env.py        # does 1 then 2 for you, registers the font, and prints which path worked
```

If PyPI is unreachable too and matplotlib is already installed, add `--no-deps` to step 1.

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

## 3. Without the package
When neither install works, build the chart without `mckviz`:
- **Colors:** take the color roles from `references/rules.md` and define them once as named constants (`FOCUS`, `CONTEXT`, `ACCENT`, `NEGATIVE`, ...). Never type a hex value inline.
- **Font:** register the TTFs in `assets/fonts/` with matplotlib (`from matplotlib import font_manager as fm; [fm.fontManager.addfont(str(p)) for p in Path("assets/fonts").glob("*.ttf")]`, then `rcParams["font.family"] = "Libre Franklin"`). If that is impossible, use **Liberation Sans or Arimo** (metric-compatible with Arial), leave some label slack, and list the font under QA exceptions in the brief.
- **QA:** go through `references/qa-checklist.md` and the cookbook page's QA specifics by hand in place of `mv.lint`, and render the chart and look at it.
