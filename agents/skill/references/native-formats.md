<!-- {{generated_note}} -->
# Native formats: Excel, PowerPoint, Power BI, HTML and R

Read this when the chart has to live somewhere other than a PNG: a native, editable chart in a deck or workbook, a Power BI report, a web page or R. The workflow in `SKILL.md` (question, chart type, headline, QA) still applies; this page covers the build for each platform. Each cookbook page has a section per platform with the steps for that chart.

<!-- copilot -->
- **PowerPoint:** a slide or deck gets a real `.pptx` built with `mv.office` (python-pptx is in the sandbox) on the McKesson branded template (master, logo, footer, Libre Franklin). **Every McKesson slide goes through `mv.office`, never PptxGenJS or another slide tool** (such as Copilot's built-in slides skill): they draw their own master, which isn't McKesson's. The headline goes in the slide title at the master's 34 pt when it fits on one line (about 55 characters), else 28 or 26 pt on two; a headline over two lines (about 150 characters) raises an error: shorten it.
  - **A ranking (bar), in one call:**
    ```python
    prs = mv.office.deck()
    mv.office.bar_slide(prs, df.team, df.rate, focus={"Pharmacy Ops"}, benchmark=19.9,
                        benchmark_label="Enterprise 19.9%", fmt="{:.1f}%", headline=..., subtitle=..., source=...)
    path = mv.office.save(prs, "/tmp/<name>.pptx")   # not /mnt/data: save refuses it
    ```
    It sorts largest first from the top, leaves out gridlines and the value axis, starts the plot right after the labels, labels each bar's end (Bold for the focus), draws the benchmark as a dashed line across all bars and moves a label off it. `fmt` is a Python format string; the common ones become the chart's number format, so Edit Data updates the labels. `takeaways=[("27.4%", "caption"), ...]` (two or three) adds the card in the right third. Same `focus`/`accent` rules as `mv.highlight`; `source` takes the placeholder when the user gave none; `alt=` sets the alt text (default: the headline).
  - **A few periods or stages as columns, in one call:** `mv.office.column_slide(prs, df.fiscal_year, df.rate, focus={"FY26"}, fmt="{:.0f}%", headline=..., subtitle=..., source=...)`: the given order kept, the value on top of each column, the same `benchmark=` line (across all columns, named at its right end), `takeaways=` and `alt=`. Long category names or a ranking: `bar_slide`.
  - **Lines over time, in one call:** `mv.office.line_slide(prs, df.quarter, {"Pharmacy Technician": [...], ...}, focus={"Pharmacy Technician"}, target=20, target_label="Target 20%", forecast_from="Q4 '25", fmt="{:.1f}%", headline=..., subtitle=..., source=...)`: `mv.line`'s arguments and rules (grey context, at most two highlighted, two to four lines without a focus in the categorical colors, end labels instead of a legend, nudged apart). `mv.line`'s `event` shading and scenario `band` have no native version: use the picture slide for those.
  - **Parts of a whole, a bridge, us vs. a comparator, in one call each**, with the arguments of `mv.hstack`, `mv.waterfall` and `mv.dumbbell`:
    ```python
    mv.office.stack_slide(prs, df.function, [("Full-time", df.ft), ("Part-time", df.pt), ("Contingent", df.cont)],
                          story="Contingent", base=df.workers, base_label="Workers", headline=..., subtitle=..., source=...)
    mv.office.waterfall_slide(prs, df.step, df.value, df.kind, focus={"Automation savings"}, floor=3900, headline=..., ...)
    mv.office.dumbbell_slide(prs, df.role, df.market_k, df.ours_k, tick_fmt="${:,.0f}K", headline=..., ...)
    ```
    Each takes `takeaways=` and `alt=` too. A waterfall's `floor=` adds the break marks and the footnote that says where the axis starts.
  - **Every other chart type (Sankey, strip, treemap, heatmap, scatter, table, ...): the mckviz chart as a picture on the branded slide.** Build the figure as usual (builder, `mv.titles`, `mv.source`), save the inline preview with `mv.save` to `/tmp/`, then pass the same figure:
    ```python
    mv.office.picture_slide(prs, fig, headline=..., subtitle=..., source=...)   # takeaways=[...] works here too
    ```
    It takes the figure's own headline, subtitle and source off (the slide's title, subtitle and source line say them once), draws the chart at the chart area's size so its text keeps its point size, and sets the alt text. Say in the hand-back that the chart is a picture (native, editable versions are coming), and offer the cookbook page's PowerPoint steps if the user needs to edit the numbers in PowerPoint. Don't build native charts by hand.
  - **Check in /tmp, then deliver once.** Everything written to `/mnt/data` becomes a copy in the user's OneDrive, and deleting it there doesn't remove the copy. So: save the deck to `/tmp`; render it there for the preview (a slide renderer, such as the slides skill's `render_slides.py`, is fine on the `/tmp` copy; else use the mckviz PNG); run no validator on it, or only on the `/tmp` copy (`artifact-validator` rewrites the file it checks and leaves a `.orig` backup). Look at the preview with `mv.look(png)`, never by copying it into `/mnt/data`. Then, as the last step, `mv.deliver(deck, preview_png)`: one copy each. Never `cp`, `mv` or `rm` in `/mnt/data`; delivering the same file again does nothing, and a revision the user asks for goes under a new name.
  - Show the preview inline and say the deck is attached.
- **Excel:** give the PNG, then the cookbook page's Excel steps with the user's numbers, labels and focus filled in. The colors are the hex values in `references/rules.md`; `references/office-setup.md` covers the theme and the font.
- **Power BI:** follow the cookbook page's Power BI section. The report theme is `assets/powerbi/mckesson-dataviz-theme.json` (also in the release bundle) and `references/powerbi-setup.md` has the steps. Write the DAX for the highlight measure and the minimum-n rule (`IF([Headcount] < 10, BLANK(), ...)`) when the user needs it.
- **Not in this edition:** Copilot skills can't carry the web themes (CSS), the R theme, the PowerPoint template as a .potx or the font files as they are, so files that cookbook pages name under `assets/web/`, `assets/html/`, `assets/r/` and `assets/office/` aren't here. They're in the release bundle ({{repo_url}}/releases), which is where the user gets the font for their own machine (a deck from `mv.office` names Libre Franklin; without the font installed, PowerPoint substitutes another).
<!-- /copilot -->
<!-- portable,repo -->
- **HTML:** the chart-card pattern with {{web_css}} plus {{web_plotly}} or {{web_vega}}{{chart_card}}.
- **Excel / PowerPoint:** build a **native, editable chart**, never a pasted picture, when a pptx tool is available. With Python and python-pptx, a ranking, columns, lines over time, a 100% stack, a waterfall or a dumbbell is one call: `mckviz.office.bar_slide`, `column_slide`, `line_slide`, `stack_slide`, `waterfall_slide` or `dumbbell_slide` on `mckviz.office.deck()`, then `mckviz.office.save` (each chart's cookbook page shows its call). In Claude.ai, or any environment with a pptx skill (pptxgenjs), use it with the theme and chart options in {{pptx_theme}} (`MCK.theme`, `MCK.text.*` on the slide grid, `MCK.barChart` with `MCK.pointColors(labels, focus)`) and the recipe in `{{docs}}office-setup.md` ("A native chart from code with pptxgenjs"): the headline in the title placeholder at 26 pt Bold McKesson Blue, the subtitle and source as text, and the benchmark line and bold focus labels as shapes over the pinned plot area. Without a pptx tool, start from the starter deck (`McKesson-DataViz-Starter.pptx`, native charts on the template grid) and follow the cookbook page's Excel / PowerPoint section by hand, or render a PNG with matplotlib and place it on the slide as the last resort.
- **Power BI, R:** follow the cookbook page's section for that platform, using {{themes}}.
<!-- /portable,repo -->
