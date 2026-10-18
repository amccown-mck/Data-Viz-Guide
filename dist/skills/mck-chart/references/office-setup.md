# Set up Excel and PowerPoint

## The short version (most people)
You probably need to install nothing.

1. **Check the font.** In PowerPoint, type *Libre Franklin* in the font box. If it's listed, skip to step 2. If not, install it (section 1 below), or ask IT.
2. **New deck:** start from the **McKesson Standard Template** (File › New). Put charts on its *Title Only* layout.
3. **Charts:** open the **starter deck** from the kit, copy a chart slide into your deck, right-click the chart › **Edit Data**, and paste your numbers. The colors, fonts, labels and layout come with it.
4. **Excel:** start from the **chart workbook**. Its *Palette* sheet lists every color with the hex to type into **More Colors**.

The rest of this page is for people who build many charts from scratch and want the McKesson colors in every new Office file (sections 1–2, about five minutes), and for maintainers.

## The full set-up
Afterwards, **Page Layout › Colors** (Excel) and **Design › Variants › Colors** (PowerPoint) list **McKesson Data Viz**.

| File | What it is | Where it is |
|---|---|---|
| Libre Franklin fonts | The brand typeface, 9 weights (SIL Open Font License, free to install and embed) | [`fonts/LibreFranklin/`](../assets/fonts) |
| Theme colors | Accent 1–6 = the categorical palette, Text 2 = McKesson Blue (titles, as in the Standard Template), Background 2 = Light Sand | [`dist/office/Theme Colors/McKesson Data Viz.xml`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/office/Theme%20Colors/McKesson%20Data%20Viz.xml) |
| Theme fonts | Libre Franklin for headings and body | [`dist/office/Theme Fonts/McKesson Data Viz.xml`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/office/Theme%20Fonts/McKesson%20Data%20Viz.xml) |
| PowerPoint template | 16:9, theme applied (flat: solid fills, 1 pt lines, no shadows or bevels), no slides. Master and layouts on the Standard Template's grid: title Bold 26 pt McKesson Blue at 0.39 in left / 0.38 in top, body 16/14 pt without bullets from 1.32 in, footer with page number, "McKesson Proprietary and Confidential" and date | [`dist/office/McKesson-DataViz.potx`](../assets/office/McKesson-DataViz.potx) |
| Starter deck | Native, editable sample slides: bar highlight, line, waterfall, 100% stacked bar, KPI card, roadmap (Gantt), initiative tracker, two charts on a slide, column, dumbbell, slope and bubble (see [Starter deck, slide by slide](#starter-deck-slide-by-slide)). The internal release bundle also has a copy built on the McKesson Standard Template (`McKesson-DataViz-Starter-Official.pptx`) | [`dist/office/McKesson-DataViz-Starter.pptx`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/office/McKesson-DataViz-Starter.pptx) |
| Chart workbook | Palette sheet (chart roles, status colors with symbols and words, ramps including the ordered steps), the deck's charts in Excel, a heat-table scorecard, a formula-driven KPI card, roadmap (Gantt with a Today line set by the as-of date) and tracker, and named cell styles (**Home › Cell Styles**: Headline, Subtitle, Source, Focus row, Total) | [`dist/office/McKesson-DataViz-Charts.xlsx`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/office/McKesson-DataViz-Charts.xlsx) |
| One-page PDFs | Cheat sheet (anatomy, colors, checklist) and chart chooser | [`dist/print/cheat-sheet.pdf`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/print/cheat-sheet.pdf), [`dist/print/chart-chooser.pdf`](https://github.com/amccown-mck/Data-Viz-Guide/blob/main/dist/print/chart-chooser.pdf) |

## 1. Install the fonts
- **Windows:** open `fonts/LibreFranklin`, select all the `.ttf` files, right-click and choose **Install** (or **Install for all users** if you have admin rights). Restart Excel and PowerPoint.
- **Mac:** double-click each `.ttf` file and choose **Install Font** in Font Book.
- In the font list, Regular, Italic, Bold and Bold Italic appear as **Libre Franklin**. The other weights are separate entries: **Libre Franklin Light** (footnotes), **Libre Franklin Medium** (data labels) and **Libre Franklin SemiBold** (chart headlines). Big numbers use Bold.

## 2. Install the theme colors and fonts
**Windows:** copy the two XML files into your Office theme folders. Paste this into PowerShell from the repo root:
```powershell
$themes = "$env:APPDATA\Microsoft\Templates\Document Themes"
New-Item -ItemType Directory -Force "$themes\Theme Colors", "$themes\Theme Fonts" | Out-Null
Copy-Item "dist\office\Theme Colors\McKesson Data Viz.xml" "$themes\Theme Colors\"
Copy-Item "dist\office\Theme Fonts\McKesson Data Viz.xml" "$themes\Theme Fonts\"
```
Or do it in File Explorer: paste `%APPDATA%\Microsoft\Templates\Document Themes` into the address bar, then copy each file into the **Theme Colors** or **Theme Fonts** subfolder (create the folder if it doesn't exist).

**Mac:** copy the files to `~/Library/Group Containers/UBF8T346G9.Office/User Content/Themes/Theme Colors/` and `.../Themes/Theme Fonts/`.

## 3. Apply the theme
- **Excel:** **Page Layout › Themes › Colors › McKesson Data Viz**, then **Fonts › McKesson Data Viz**. The chart workbook already has both.
- **PowerPoint:** **Design › Variants › ▾ More › Colors › McKesson Data Viz**, then **Fonts › McKesson Data Viz**. Decks made from the `.potx` already have both.
- **Word:** **Design › Colors / Fonts › McKesson Data Viz**.
- To make it the default for new PowerPoint decks, open the `.potx`, go to **Design**, right-click the current theme thumbnail and choose **Set as Default Theme**.

Once the theme is applied, the color picker's top rows are the McKesson palette, in the categorical order: **Accent 1** McKesson Blue `#005A8C` (focus), **Accent 2** Navy `#143359` (the accent for the one exception), **Accent 3** bright blue `#009EFF`, **Accent 4** teal `#00AF9D`, **Accent 5** mint `#05CE90`. **Accent 6** is Orange `#EF8200`: use it only for "worse" (negatives, below target), never as a highlight. The context grey `#B4B0A5` and the light blue `#66C4FF` (the series fill when one bar gets the navy accent) aren't theme slots: pick them with **More Colors › Hex**, or copy formatting from a sample chart with **Format Painter**.

## 4. Use the starter files
- **New deck:** copy `McKesson-DataViz.potx` to `Documents\Custom Office Templates` (Mac: `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates`). It then shows up under **File › New › Personal** (or **Custom**).
- **Charts:** open `McKesson-DataViz-Starter.pptx`, copy the slide whose chart matches your question, then **right-click the chart › Edit Data**. The speaker notes on each slide say what to change: for example, the waterfall's hidden "Base" column, and the enterprise line on the bar chart, which is a drawn shape.
- **Excel:** copy a chart from `McKesson-DataViz-Charts.xlsx` into your workbook and use **Select Data** to point it at your range. Paste it into PowerPoint with **Paste › Use Destination Theme & Embed Workbook**, so it stays editable.
- **Reuse your own formatting:** right-click a finished chart › **Save as Template…**. The `.crtx` file goes to `%APPDATA%\Microsoft\Templates\Charts`, and appears under **Insert › Recommended Charts › All Charts › Templates**.

Each chart type's click-by-click recipe is in its cookbook page under **Excel and PowerPoint**, for example [bar.md](cookbook/bar.md#excel-and-powerpoint).

## A native chart from code with pptxgenjs
In Claude.ai (its pptx skill builds decks with [pptxgenjs](https://gitbrent.github.io/PptxGenJS/)) or any Node project, build the chart as a **native, editable PowerPoint chart**, never a pasted picture. The theme is generated from the tokens as [`dist/office/pptxgenjs-theme.js`](../assets/office/pptxgenjs-theme.js) (`assets/office/pptxgenjs-theme.js` in the portable skill): color roles, the Office scheme slots, text styles on the template grid, and chart options for bar, column and line that match the click-by-click recipes above.

```js
const pptxgen = require("pptxgenjs");
const MCK = require("./pptxgenjs-theme.js");
const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";                                   // 13.33 × 7.5 in, the grid in MCK.grid
pptx.theme = MCK.theme;                                        // Libre Franklin for headings and body
pptx.defineSlideMaster({ title: "Chart - title only", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", ...MCK.text.slideTitle } } }] });
const slide = pptx.addSlide({ masterName: "Chart - title only" });
slide.addText(headline, { placeholder: "title" });             // 26 pt Bold McKesson Blue, editable as the title
slide.addText(subtitle, MCK.text.subtitle);                    // 14 pt #505050 at 1.32 in
const focus = ["Pharmacy Technician", "Distribution Center Associate"];
slide.addChart(pptx.ChartType.bar, [{ name: "Voluntary attrition", labels, values }], {
  ...MCK.barChart, x: MCK.grid.left, y: MCK.grid.chart.y, w: MCK.grid.width, h: MCK.grid.chart.h,
  chartColors: MCK.pointColors(labels, focus), dataLabelFormatCode: '0.0"%"',
  valAxisMaxVal: 30, altText: headline });                     // fix the axis so overlays can be placed
slide.addText(source, MCK.text.source);                        // Light 9 pt #737373, bottom-left
pptx.writeFile({ fileName: "attrition-by-job-family.pptx" });
```

What the options do: `barDir: "bar"` with `catAxisOrientation: "maxMin"` puts the first row on top; `barGapWidthPct: 50` is the 2 : 1 bar-to-gap rule; the value axis and both gridlines are hidden because the bars carry outside-end labels in Libre Franklin Medium 12 pt; the category axis keeps a 0.75 pt `#8C8C8C` zero baseline with no tick marks; `chartArea.roundedCorners: false` keeps the chart flat; `layout` pins the plot area to a fixed fraction of the chart frame. `MCK.pointColors(labels, focus, accent)` gives context grey to every bar, focus blue to the ones the headline names (at most two) and navy to the one accent; pass `MCK.colors.negative` yourself only where a value means "worse".

**Overlays must be shapes.** PowerPoint charts cannot draw a labelled benchmark line, bold one category label or add a bracket, so draw those with `slide.addShape` and `slide.addText` on top of the chart, positioned from the pinned plot area. With `layout: { x, y, w, h }` as fractions of the chart frame `(cx, cy, cw, ch)` and the value axis fixed at `[0, max]`, a value `v` sits at `cx + cw * (layout.x + layout.w * v / max)` inches:
- **Benchmark line:** `slide.addShape(pptx.ShapeType.line, { x, y: cy + ch * layout.y, w: 0, h: ch * layout.h, ...MCK.benchmarkLine })`, then its label (`"Enterprise 19.9%"`, `MCK.benchmarkLabel`, white fill so it sits over the bars) just above the plot. When a value label sits within about 2 pt of the line, give the label a white backing rectangle or draw the line in segments that skip it.
- **Bold focus labels:** hide the chart's category labels (`catAxisHidden: true`, keeping the baseline as a drawn line) and add one text box per row, `MCK.text.labelFocus` for the focus rows and `MCK.text.tick` for the rest, right-aligned to the plot's left edge; or leave the axis labels and overlay only the focus names.
- **Callouts, brackets, a derived-count column:** text boxes and lines in `MCK.colors.annotation`, flat (no shadow, square corners).

Say in the speaker notes that the overlays are shapes and must be moved by hand when the data changes. Set `altText` on the chart to the headline. Before handing back, render the slide (LibreOffice: `soffice --headless --convert-to pdf`) and look at it: the title wraps to at most two lines without touching the subtitle, labels clear the benchmark line, and the fallback font is not in use.

**Theme colors.** pptxgenjs's `theme` option sets the fonts only, so the deck's color picker shows Office's default scheme unless the deck starts from the kit's `.potx` or its `theme1.xml` carries the McKesson scheme (`MCK.schemeColors`: `dk2` McKesson Blue for titles, `lt2` Light Sand, `accent1`–`accent6` in the categorical order). The chart and text options name every color explicitly, so the slide looks right either way; apply **Design › Variants › Colors › McKesson Data Viz** afterwards to get the palette into the picker.

## Starter deck, slide by slide
Every slide uses the *Title Only* layout: the headline goes in the title placeholder (Bold 26 pt McKesson Blue `#005A8C`, from the master), the subtitle is a 14 pt `#505050` text box at 1.32 in, and the footnote and source are Libre Franklin Light 9 pt `#737373`, bottom-left, ending at 6.95 in. Charts are native: **right-click › Edit Data** changes the numbers. Data labels are Libre Franklin Medium (Bold where the headline points). Drawn shapes are flat (no shadow, square corners). Headlines are written from the sample data, so rewrite them for yours. The speaker notes on each slide repeat the steps below. The chart workbook has the same charts, plus formulas, on the sheets named in each entry.

**1–2. Cover and rules.** The cover uses the brand signature (Bold lead word, Light rest). The rules slide is a reminder for the author: leave it out of decks you send.

**3. Bar highlight** (*Bar* sheet). Grey bars `#B4B0A5`, with the two the headline names in blue `#005A8C`. **To use your data:** Edit Data, column B. **Not obvious:** to recolor one bar, click it twice so only that bar is selected, then **Fill**. The dashed "Enterprise" line is a drawn shape placed for a 0–30 axis, so move it when the rate changes.

**4. Line with end labels** (*Line* sheet). Navy `#143359` for demand, blue for supply, end labels instead of a legend. **To use your data:** Edit Data, one column per series. **Not obvious:** the end labels are data labels on the last point (**Label Contains: Series Name, Value**). The gap note is a text box.

**5. Waterfall** (*Waterfall* sheet). A stacked column with an invisible *Base* series. **To use your data:** edit *Change* and *Total*, then recompute *Base* as the running total before each step (the sheet does this). **Not obvious:** the axis starts at $3,900M, and the white slashes on the total bars are drawn break marks.

**6. 100% stacked bar** (*Stacked 100%* sheet). The segment the headline is about sits on the baseline in blue; the rest are greys. **To use your data:** Edit Data, keeping the story column first.

**7. KPI card** (*KPI* sheet). Tokens: the number is Bold 54 pt navy `#143359`. The sentence is 16 pt `#505050`. The comparison is SemiBold 14 pt green `#007A48` with ▲ (use orange `#A75B00` with ▼ when the change is worse). The gap to target is orange text, in words. The progress bar is a light track `#DEDBD1`, a blue fill and a navy target tick, labelled. **To use your data:** type the new number and lines straight into the text boxes. In the group *Progress bar*, the track is 8.60 in wide, so set the fill's width to 8.60 in × value (62% = 5.33 in). Put the tick's left edge at 0.39 in + 8.60 in × target − 0.02 in, using **Shape Format › Size and Position**, and move its label with it. In Excel, edit the inputs (W:Z) and the target: the number, sentences, colors and the 20-cell bar all follow by formula.

**8. Roadmap (Gantt)** (*Roadmap* sheet). A native **Stacked Bar** with three series: *Start* (no fill, so each bar floats at its start), *Duration*, and *Slip*. Bars are grey `#B4B0A5`, blue `#005A8C` for off track and `#DEDBD1` for not started. The slip extension is light grey with a dashed outline and an arrow. Above the plot are phase bands, FY and quarter labels. Milestones are ◆ navy (met), ◇ hollow navy (due) and ✕ `#DA2103` (missed). A moved milestone keeps a grey ◇ at its original date, with an arrow and "Moved Mar to Jun". Status sits at the row end as a dot with its symbol, plus the word. A dashed navy *Today* line runs down the plot.
- **To use your data:** in Edit Data, *Start* = months after 1 Apr 2025 (FY26 Q1 = 0), *Duration* = months including the last one, and *Slip* = forecast months beyond the plan (0 if on plan). The axis runs 0–24 months; its gridlines are the quarters. To recolor a bar, click it twice › **Fill**.
- **Not obvious, the offset series:** the invisible *Start* series is what makes it a Gantt. Keep it first and with **No fill**. Tick **Format Axis › Categories in reverse order** so the first row is on top.
- **Not obvious, moving the Today line:** select the group *Today line*. One month is 0.358 in, and month 0 starts at 2.94 in from the slide's left edge. So set **Size and Position › Horizontal position** to 2.94 in + months × 0.358 in, minus half the group's width; the end of Mar 2026 (month 12) is at 7.24 in. Or nudge it with the arrow keys. In Excel, change *Status as of*: the line is a second, secondary-axis stacked bar driven by that date, so it moves by itself.
- **Not obvious, adding a row:** in Edit Data, insert the row *inside* the table so the chart range grows. Then type the name, Start, Duration and Slip 0. Rows get shorter (the plot height ÷ the number of rows), so drag each row's group back onto its bar. A group is named after its workstream (*Row 3: SWP model refresh*) and holds that row's milestones and status. For the new row, copy a group and change the dot's fill, its symbol and the word.
- **Milestone markers:** these are shapes (Insert › Shapes › Diamond, or Multiply for ✕). A milestone in month m sits at 2.94 in + (m + 0.5) × 0.358 in. The Excel sheet lists them with ◆ ◇ ✕ by formula, because Excel can't draw shapes on a bar chart's axis.

**9. Initiative tracker** (*Tracker* sheet). A native table (Insert › Table), style **No Style, No Grid**. It has no row fills, a 1 pt `#8C8C8C` rule under the header and `#E6E4DE` hairlines between rows. Rows run off track, then at risk, then the rest, with exception names in SemiBold navy. The status cell is a dot with its symbol (on track ✓ `#00AF68`, at risk ! `#FFB500`, off track ✕ `#DA2103`, not started – `#BFBFBF`, complete ✓ `#005A8C`) and the word. Above the table is a roll-up count per status. **To use your data:** type in the cells. **Not obvious:** the dots are shapes in the group *Status dots*, on top of the table. Change a dot's fill and symbol when its word changes. Rows are 0.54 in tall and fit two lines; longer text makes a row grow, and then the group needs moving. In Excel, pick the status from the dropdown: the ● color, the symbol, the bold and the roll-up counts follow (Conditional Formatting with a formula, not icon sets). Never color a whole row by status.

**10. Two charts.** The slide title carries the one message. Each card has its own SemiBold 18 pt navy headline, a 14 pt subtitle, and a footnote and source. Read left to right: a bar chart, then a dot plot with the same rows, order and highlight. **Not obvious:** the dot plot is an XY scatter with one series per row (the series name is the row label). Point 1 sits at the axis minimum (60) and carries the name; point 2 is the dot (X = value, Y = row number, 1 at the bottom). The grey line between them is the stem. Two charts is the limit.

**Slides 11–14 use the chart + takeaways frame** ([two standard widths](typography-and-layout.md#3-several-charts-on-one-slide)): the chart takes two-thirds of the width (8.04 in), and a *Key takeaways* card fills the right third (4.02 in) after a 0.5 in gutter, in the same place on every slide, with the plot area lined up to its top and bottom. **To use it:** retype the number and caption text boxes in the *Takeaways* group (keep 2–3 points, a number and one or two lines each); to go full width, delete the group and stretch the chart to 12.55 in. **Not obvious:** the slope's two periods sit on the plot's edges (**Format Axis › Axis Position › On tick marks**), and long data labels (the slope's unit names, the dumbbell's role names) are sized by hand (**Format Data Label › Size & Properties**), because Office otherwise wraps a label at about a fifth of the chart's width.

**11. Column highlight** (*Column* sheet). Grey columns, with the latest year in blue and labelled. The value axis is deleted, and the columns start at zero.

**12. Dumbbell** (*Dumbbell* sheet). Market is grey; McKesson is blue, or orange `#EF8200` for the gaps the headline names. **Not obvious:** in the deck, each role is an XY series of three points: the label anchor at the axis minimum, then market, then McKesson. Only the market–McKesson segment is drawn. The gap labels are typed, so update them. The workbook uses the cookbook's version instead ([dot-plot-dumbbell.md](cookbook/dot-plot-dumbbell.md#excel-and-powerpoint)): custom horizontal error bars, plus label series that take their text from cells.

**13. Slope** (*Slope* sheet). A Line with Markers chart, with two categories and one series per unit: the focus line is blue 2.25 pt, the rest grey. Labels are data labels on the end points (value on the left; name and value on the right), so Edit Data updates them. Labels that would touch are nudged apart; drag one to move it.

**14. Bubble** (*Scatter* sheet). X = Gen AI exposure, Y = median pay, bubble area = headcount (**Size represents: Area**, bubble scale 50%). The two roles the headline names are blue and labelled. In Excel the sheet is a plain scatter; for bubbles, use **Change Chart Type › Bubble** and set the size to the *Headcount* column.

No `.crtx` chart templates ship with the kit: python-pptx can't write them. Make your own with **right-click › Save as Template…** from any of these charts.

## 5. Sharing with people who don't have the font
- Office substitutes another font when Libre Franklin isn't installed, so line breaks and label fits change. For decks you send out, use **File › Options › Save › Embed fonts in the file** (**Embed only the characters used** keeps the file small). The Open Font License allows embedding.
- For PDFs, export with **File › Export › Create PDF/XPS**; fonts are embedded automatically.

## Troubleshooting
| Symptom | Fix |
|---|---|
| "McKesson Data Viz" is missing from the Colors list | Check that the file sits directly in `...\Document Themes\Theme Colors\` (not in a subfolder) and that its extension is `.xml`, then restart Office. |
| Text shows in Calibri or Arial | The theme fonts were applied before Libre Franklin was installed. Install the fonts, restart Office, and re-apply **Fonts › McKesson Data Viz**. |
| Libre Franklin Light / Medium don't appear | Only four styles group under "Libre Franklin"; pick **Libre Franklin Light** or **Libre Franklin Medium** by name. |
| A chart pasted from Excel changed colors | You pasted with **Keep Source Formatting** into a deck with another theme. Paste with **Use Destination Theme**, or apply the McKesson theme to both files. |

## For maintainers
All of these files are generated, so never edit them in `dist/` by hand. After changing `tokens/tokens.json`, run from the repo root:

**Windows (PowerShell)**
```powershell
.\.venv\Scripts\python.exe tokens\build.py           # theme XML, CSS, Plotly, ... (dist/)
.\.venv\Scripts\python.exe office\build_office.py    # .pptx, .potx, .xlsx (dist/office/)
.\.venv\Scripts\python.exe tools\build_guide.py       # the guide, plus the cheat sheet and chart chooser PDFs (dist/print/)
```

**Mac or Linux (bash/zsh)**
```bash
.venv/bin/python tokens/build.py
.venv/bin/python office/build_office.py
.venv/bin/python tools/build_guide.py
```

`office/build_office.py` needs `mckviz` (installed from `python/`), `python-pptx`, `xlsxwriter`, `lxml` and `pandas`, plus `openpyxl` to re-open the workbook when checking a build:
`pip install -e ./python python-pptx openpyxl xlsxwriter lxml pandas`. It swaps the McKesson color and font schemes and a flat format scheme into each package, puts the template's master and layouts on the Standard Template grid, sets the file properties, adds named cell styles and `roundedCorners=0` to the workbook, and removes xlsxwriter's `defaultThemeVersion` attribute, without which Excel ignores the embedded theme.

To check a build without Office, re-open the files with python-pptx and openpyxl and read the XML, then do a visual check in PowerPoint and Excel on Windows: the title and footer positions in **View › Slide Master**, no shadows on the drawn lines, square chart corners, and the cell styles under **Home › Cell Styles**. For the slides drawn over charts (roadmap, tracker, dot plot, dumbbell, slope), check that the shapes and labels line up with the bars, rows and points in Libre Franklin.
