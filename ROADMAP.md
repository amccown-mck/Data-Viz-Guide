# Roadmap and status

Last updated: 2026-09-30. Read this first when resuming work, whether you're a person or an agent.

## Done

| Area | What exists | Where |
|---|---|---|
| Inspiration capture | Paraphrased notes on each page of the McKinsey Data Viz Guidelines (pp. 26–86 plus 4 hi-res pages). No images are committed. | `reference/inspiration-mckinsey/pages/` |
| Brand extraction | Libre Franklin typeface, plus the core, 2026, and extended palettes taken from the Social Media guide and FY26 Impact Report | `tokens/tokens.json`, `tools/*.py` |
| Design tokens | Single source of truth, including chart roles (focus, accent, context, total), categorical-6, sequential, and diverging (orange-blue, CVD-safe) | `tokens/tokens.json` |
| Token build | `python tokens/build.py` generates CSS, Plotly, Vega-Lite, mplstyle, ggplot2, Power BI theme, Office theme XML, a palette report, and swatches | `dist/` |
| Python package | `mckviz`: `use()`, `highlight()`, `titles()`, `source()`, `label_bars()`, `label_line_ends()`, `callout()`, `shade_period()`, `pl_finish()` | `python/mckviz/` |
| Fonts | Static Libre Franklin TTFs (SIL OFL) | `fonts/LibreFranklin/` |
| Example data | 9 synthetic workforce / SWP datasets | `examples/data/` (`make_data.py`) |
| Galleries | 8 matplotlib PNGs that were visually QA'd, plus a Plotly HTML gallery | `examples/python/`, `examples/output/` |
| Core docs | principles, color, typography-and-layout, choosing-a-chart, formats, qa-checklist | `docs/` |
| Cookbook | 20 chart pages plus `_template.md` | `docs/cookbook/` |

## Next steps (in priority order)

1. **Finish the cookbook.** `docs/` links to three pages that don't exist yet: `distribution` (histogram, box, beeswarm), `tables` (formatted tables and heat-tables), and `venn`. Follow `docs/cookbook/_template.md`.
2. **Agent assets.** These are needed so that coding agents follow the guide automatically:
   - Expand `AGENTS.md`, which is a stub today. Add `CLAUDE.md` and `.github/copilot-instructions.md`, both pointing to `AGENTS.md`.
   - Add `.github/instructions/viz-python.instructions.md` (applyTo `**/*.py`), `viz-web.instructions.md` (`**/*.{html,js,ts,css}`), and `viz-r.instructions.md` (`**/*.{R,Rmd,qmd}`).
   - Add `.github/skills/mck-chart/SKILL.md`, a workflow skill: question → chart type → build with `mckviz` → headline → QA checklist.
   - Add a portable single-file rules prompt for use in other repos (`agents/mck-viz-rules.md`).
3. **HTML starter.** Add a self-contained `templates/html/chart-card.html` that uses `dist/web/mck-viz.css` and `mck-plotly-template.js`. Open `examples/output/gallery.html` and check it visually.
4. **Excel / PowerPoint (priority 2 audience).**
   - Add a `.pptx` / `.potx` with the theme colors and fonts applied, plus native, editable sample charts built with python-pptx (bar highlight, line, waterfall, stacked 100%).
   - Add an Excel workbook with the palette and example charts (xlsxwriter).
   - Write a how-to for installing the `dist/office/Theme Colors` and `Theme Fonts` XML into `%APPDATA%\Microsoft\Templates\Document Themes\`.
   - Write a one-page consultant cheat sheet and a chart-chooser PDF.
5. **Power BI (priority 3).** Load `dist/powerbi/mckesson-dataviz-theme.json` into Desktop and validate it. Libre Franklin isn't a Power BI Service font, so confirm how the fallback renders.
6. **R (nice-to-have).** Smoke-test `dist/r/theme_mck.R` with ggplot2 and add 2–3 examples.
7. **QA automation.** Add a lint script that checks a matplotlib or Plotly figure against the rules: more than 6 colors, a missing headline or source, legend vs. direct labels, and so on.
8. **Brand confirmation.** Confirm with Brand that the full swatch values on BrandHQ match the values extracted from the PDFs, and check the derived ramps (sequential, diverging, context grey).

## Resume commands

```powershell
cd C:\Users\exs4yig\repos\data-viz-guide
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -e .\python[examples] kaleido python-pptx openpyxl xlsxwriter pymupdf
.\.venv\Scripts\python.exe tokens\build.py                      # regenerate dist/
.\.venv\Scripts\python.exe examples\data\make_data.py           # regenerate data
.\.venv\Scripts\python.exe examples\python\gallery_matplotlib.py
.\.venv\Scripts\python.exe examples\python\gallery_plotly.py
```

## Working notes

- The source McKinsey images and brand PDFs stay **outside** the repo, in OneDrive `Desktop\McK-Data-Viz\`. Never commit them.
- Edit colors and type only in `tokens/tokens.json`, then rebuild. Never hand-edit `dist/`.
- Examples use the People Analytics, Workforce Intelligence, and SWP lens, not plain HR reporting. They mix internal and external signals at the individual, team, firm, and sector levels.
- Platform priority: HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
