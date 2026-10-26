<!-- {{generated_note}} -->
# Native formats: Excel, PowerPoint, Power BI, HTML and R

Read this when the chart has to live somewhere other than a PNG: a native, editable chart in a deck or workbook, a Power BI report, a web page or R. The workflow in `SKILL.md` (question, chart type, headline, QA) still applies; this page covers the build for each platform. Each cookbook page has a section per platform with the steps for that chart.

<!-- copilot -->
- **Excel / PowerPoint:** a deck that leaves the team needs a **native, editable chart**, not a picture. Give the PNG for a draft or a quick look, then the cookbook page's Excel / PowerPoint steps with the user's numbers, labels and focus filled in, and the headline, subtitle and source written out ready to paste. The colors for those steps are the hex values in `references/rules.md`. The PowerPoint template, the starter deck (native charts on the template grid) and the chart workbook are in the release bundle ({{repo_url}}/releases); `references/office-setup.md` covers the theme and the font.
- **Power BI:** follow the cookbook page's Power BI section. The report theme is `assets/powerbi/mckesson-dataviz-theme.json` (also in the release bundle) and `references/powerbi-setup.md` has the steps. Write the DAX for the highlight measure and the minimum-n rule (`IF([Headcount] < 10, BLANK(), ...)`) when the user needs it.
- **Not in this edition:** Copilot skills can't carry the web themes (CSS), the R theme, the PowerPoint template (.potx) or the font files as they are, so files that cookbook pages name under `assets/web/`, `assets/html/`, `assets/r/` and `assets/office/` aren't here. They're in the release bundle ({{repo_url}}/releases), which is where the user gets the Office template and the font.
<!-- /copilot -->
<!-- portable,repo -->
- **HTML:** the chart-card pattern with {{web_css}} plus {{web_plotly}} or {{web_vega}}{{chart_card}}.
- **Excel / PowerPoint:** build a **native, editable chart**, never a pasted picture, when a pptx tool is available. In Claude.ai, or any environment with a pptx skill (pptxgenjs), use it with the theme and chart options in {{pptx_theme}} (`MCK.theme`, `MCK.text.*` on the slide grid, `MCK.barChart` with `MCK.pointColors(labels, focus)`) and the recipe in `{{docs}}office-setup.md` ("A native chart from code with pptxgenjs"): the headline in the title placeholder at 26 pt Bold McKesson Blue, the subtitle and source as text, and the benchmark line and bold focus labels as shapes over the pinned plot area. Without a pptx tool, start from the starter deck (`McKesson-DataViz-Starter.pptx`, native charts on the template grid) and follow the cookbook page's Excel / PowerPoint section by hand, or render a PNG with matplotlib and place it on the slide as the last resort.
- **Power BI, R:** follow the cookbook page's section for that platform, using {{themes}}.
<!-- /portable,repo -->
