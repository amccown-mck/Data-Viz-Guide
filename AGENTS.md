# Agent instructions

You are working in the McKesson data-visualization starter kit. These instructions apply to every coding agent (Claude Code, GitHub Copilot, Cursor, Codex and others). `CLAUDE.md` and `.github/copilot-instructions.md` point here, and this file is the source of truth.

Two kinds of task happen here. Follow the section that matches yours:
- **A. Making a chart** (in this repo, or for McKesson anywhere): follow the workflow and rules below.
- **B. Changing the kit itself** (tokens, `mckviz`, docs, examples): see [Working on this repo](#b-working-on-this-repo).

If you are resuming unfinished work on the kit, read [`ROADMAP.md`](ROADMAP.md) first.

---

## A. Making a chart

### Workflow (do these in order)
1. **Question.** Write the question the chart answers in one sentence ("Where is attrition concentrated?"). Decide whether the chart is explanatory (deck, report: the default) or exploratory (dashboard).
2. **Chart type.** Name the question type, then pick from [`docs/choosing-a-chart.md`](docs/choosing-a-chart.md). Read [`docs/principles.md`](docs/principles.md) and the matching `docs/cookbook/<chart>.md` page **before** writing code. Each page has a spec table, do/don't rules and runnable code for each platform.
3. **Build.** Start from the cookbook snippet for your platform (see [Platform recipes](#platform-recipes)). Take every color from the tokens; never type a hex value.
4. **Headline.** Compute the finding from the data, then write it as a full sentence. Build the numbers in the headline from variables, not by eyeballing.
5. **QA.** In Python, run `mv.lint(fig)` and fix every error. Then go through [`docs/qa-checklist.md`](docs/qa-checklist.md) and the cookbook page's "QA specifics". Render the chart and look at it (open the PNG, or screenshot the HTML). Report any item you couldn't meet.

### Rules every chart must meet
| Rule | Detail |
|---|---|
| Insight headline | A full sentence with a verb that states the "so what", ideally with a number. ≤ 2 lines, sentence case, no final period. Every claim is visibly supported by the chart. |
| Neutral subtitle | Metric, unit, scope and period ("Voluntary attrition by job family, FY26 (%)"). No opinions. |
| Highlight logic | Grey context (`chart.context`), blue focus (`chart.focus`) for what the headline names, and an optional navy accent (`chart.accent`) for the single exception (against a light-blue series, `chart.focus_light`, in the uniform pattern). At most 2 highlighted items. **Orange means "worse"**: use it (`semantic.negative`) only for below target, shrinking or a shortfall, never as a plain highlight. Amber is never used. |
| Categorical colors | Only when categories must be told apart. At most 6, in the fixed token order; group the tail into "Other". |
| Direct labels | Label bar ends, line ends and segments in place. A legend only when labels would collide, placed top-left. When values are labelled, delete the value axis and gridlines. |
| Honest scales | Bars start at zero. Bubble **area** ∝ value. No dual axes. Small multiples share a scale. |
| Source line | "Source: system, as-of date, population", bottom-left. Footnotes define metrics. |
| People data | No group under **10 people**: not in marks, labels, tooltips, filters or drill-downs. Protected attributes only for approved, aggregated analyses. Forecasts are labelled as estimates and show a range. |
| Accessibility | Text ≥ 4.5:1 contrast, nothing below 9 pt / 11 px, never color alone, no red vs. green. Provide alt text (headline + key numbers). |

### Platform recipes

**Python (matplotlib or Plotly):** install with `pip install -e ./python[examples]`.
```python
import mckviz as mv
mv.use()                     # Libre Franklin + matplotlib style + Plotly template "mck"
C = mv.colors                # roles: C.focus, C.focus_light, C.context, C.context_light, C.accent (navy), C.negative (orange = worse), C.total, C.text, ...
```
| Need | Use |
|---|---|
| Bar/point colors for a highlight | `mv.highlight(labels, focus=..., accent=..., base=None)` (Plotly: `mv.pl_highlight`) |
| Series colors | `mv.categorical(n)` (raises above 6) |
| Ramps | `mv.SEQUENTIAL["blue" \| "teal" \| "orange"]`, `mv.DIVERGING`, `mv.sequential_cmap()`, `mv.diverging_cmap()` |
| Headline + subtitle | `mv.titles(fig, headline, subtitle)` |
| Footnote + source | `mv.source(fig, "Source: ...", footnote=...)` |
| Direct labels | `mv.label_bars(ax, bars, fmt=...)`, `mv.label_line_ends(ax, fmt=...)` |
| Annotations | `mv.callout(ax, xy, title, body)`, `mv.shade_period(ax, start, end, label)` |
| Clean axes | `mv.clean_axes(ax, keep=("bottom",), grid="y")` |
| Numbers | `mv.signed(v, decimals, suffix)` (true minus, explicit +), `mv.text_on(fill)` (white or navy text on a fill) |
| Translucent fills (Plotly) | `mv.rgba(C.negative, 0.12)` for a shortfall wash, `mv.rgba(C.focus, 0.4)` for Sankey links, instead of an `rgba(...)` literal |
| Save | `mv.save(fig, path, dpi=200)`, which also lays out the titles and source |
| Check | `mv.lint(fig)` (matplotlib or Plotly; pass `headline=`, `subtitle=`, `source=` when they live in HTML); `strict=True` raises on errors |
| Plotly titles | `mv.pl_finish(fig, headline, subtitle, source_text, footnote)` |
| All tokens | `mv.TOKENS` (the full `tokens.json`) |

**HTML / JavaScript:** use the chart-card pattern. Headline, subtitle and source are HTML text in `<figure class="mck-chart">`, and the chart library draws only the data. Load `dist/web/mck-viz.css` (CSS variables such as `var(--mck-chart-focus)`, plus the `.mck-chart`, `.mck-table` and `.mck-legend` components). For Plotly, add `dist/web/mck-plotly-template.js` and pass `template: MCK_PLOTLY_TEMPLATE`; for Vega-Lite, use `dist/web/vega-lite-config.json` as the `config`. Start from `templates/html/chart-card.html` (a bar and a line card, colors read from CSS variables, drawn after the font loads, mobile key swap). `examples/python/gallery_plotly.py` builds the same pattern from Python.

**Excel / PowerPoint:** set up per `docs/office-setup.md` (Libre Franklin plus the theme XML from `dist/office/`). Start from `dist/office/McKesson-DataViz.potx`, the starter deck or the chart workbook. Build **native, editable** charts. Each cookbook page has click-by-click steps. To generate Office files from Python, follow `office/build_office.py` (python-pptx / xlsxwriter, theme injected into the package).

**Power BI:** follow `docs/powerbi-setup.md` and import `dist/powerbi/mckesson-dataviz-theme.json`. Apply highlight colors with conditional formatting on a measure, and enforce minimum n in DAX (`IF([Headcount] < 10, BLANK(), ...)`). Most Service viewers see Segoe UI instead of Libre Franklin, so leave label slack. After changing tokens, run `python tools/check_powerbi_theme.py`.

**R:** `source("dist/r/theme_mck.R")` gives `theme_mck()`, `mck_colors`, `mck_highlight()`, the fill scales, `mck_font()` (registers the bundled Libre Franklin; pass the returned name as `base_family` and `family`) and `mck_wrap()` (balanced title wrapping). Render with `ragg`. See `examples/r/gallery_ggplot2.R`.

### Before you hand back a chart
- Say which cookbook page you followed, and list any QA items you couldn't meet and why.
- Give alt text: the headline plus 2–3 key numbers.
- If you used synthetic or placeholder data, say so in the source line.

---

## B. Working on this repo

### Map
| Path | What it is | Edit? |
|---|---|---|
| `tokens/tokens.json` | The only source of colors, type and chart constants | Yes, then run `python tokens/build.py` |
| `tokens/build.py` | Generates everything in `dist/` and syncs `python/mckviz/` | Yes |
| `dist/` | Generated theme files (CSS, Plotly, Vega-Lite, mplstyle, R, Power BI, Office, agent rules) | **Never by hand** |
| `python/mckviz/` | The Python helper package (`__init__.py`). `_tokens.json`, `mckviz.mplstyle` and `plotly_template.json` are synced copies | `__init__.py` only |
| `docs/` | Principles, color, typography, formats, chart chooser, QA checklist | Yes |
| `docs/cookbook/` | One page per chart type, following `_template.md` | Yes |
| `examples/data/` | Synthetic datasets, regenerated by `make_data.py` (seeded) | Edit `make_data.py`, not the CSVs |
| `examples/python/` | Gallery scripts that render `examples/output/` | Yes |
| `agents/` | Templates for portable agent rules (built into `dist/agents/`) | Yes |
| `office/` | `build_office.py`: generates the `.pptx`, `.potx` and `.xlsx` in `dist/office/` | Yes, then rerun it |
| `guide/` | The browsable guide: `pages/*.html` (spreads with `{{exhibit:…}}`, `{{text:…}}`, `{{html:…}}`, `{{folio}}` placeholders), `exhibits.py` (every chart in the guide, drawn from tokens and data), `guide.css`. Built into `dist/guide/` (plus a standalone single-file `McKesson-DataViz-Guide.html` and the one-page PDFs in `dist/print/`) by `tools/build_guide.py`. Link to another spread with `{{link:spread-id}}` and cite its PDF page with `{{page:spread-id}}` | Yes, then rerun it |
| `templates/` | Copy-and-edit starters (HTML chart card) | Yes |
| `reference/` | Paraphrased inspiration notes. No source images are ever committed | Rarely |
| `tools/` | Brand-extraction helpers, `check_snippets.py`, `build_guide.py` | Yes |

### Commands (Windows PowerShell, from the repo root)
```powershell
.\.venv\Scripts\python.exe tokens\build.py                      # after any token change
.\.venv\Scripts\python.exe examples\data\make_data.py           # after changing example data
.\.venv\Scripts\python.exe examples\python\gallery_matplotlib.py
.\.venv\Scripts\python.exe examples\python\gallery_plotly.py
.\.venv\Scripts\python.exe office\build_office.py              # after token or example-data changes (Office files)
.\.venv\Scripts\python.exe tools\build_guide.py                # the guide (pages, standalone .html, 16:9 PDF, one-page PDFs); must report "every spread fits"
.\.venv\Scripts\python.exe tools\check_snippets.py              # every "# verified" cookbook block must pass
.\.venv\Scripts\python.exe tools\lint_charts.py                 # mv.lint over the whole gallery: 0 errors
.\.venv\Scripts\python.exe -m pytest python\tests               # mckviz tests
```

### Conventions
- **Cookbook pages** follow `docs/cookbook/_template.md`. Python blocks start with `# verified runnable (from the repo root)` or `# verified: builds without error`, and must pass `tools/check_snippets.py`. Snippets write to `tempfile.gettempdir()` or `out/` (gitignored), never into the repo.
- **Examples** use the Workforce Innovation lens (workforce analytics, intelligence and planning), not plain HR reporting. Call the team "Workforce Innovation" in audience and team wording. Mix internal and external signals, and individual, team, firm and sector levels. All data is synthetic, and the source line says so.
- **Guide spreads** are 1280 × 720 px (one 16:9 PDF page each): a left rail (eyebrow, title with a bold lead, short text) and a stage (chart card, tiles or avoid/recommended pairs). Numbers in page text come from `{{text:…}}` keys computed in `exhibits.py`, never typed. After a change, render the PDF pages and look at them, and check the web page at 1280 px and 390 px.
- **Gallery charts** must be rendered and looked at after every change. Check for overlaps, clipping, and that the headline still matches the data.
- **Never commit** the McKinsey source images or the brand PDFs. They stay in OneDrive (`Desktop\McK-Data-Viz\`).
- **Platform priority:** HTML and Python first, then Excel and PowerPoint, then Power BI. R is a nice-to-have.
- Update `ROADMAP.md` when you finish a step, and commit after each step.
