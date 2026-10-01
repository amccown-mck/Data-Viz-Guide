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
| Libre Franklin fonts | The brand typeface, 9 weights (SIL Open Font License, free to install and embed) | [`fonts/LibreFranklin/`](../fonts/LibreFranklin) |
| Theme colors | Accent 1–6 = the categorical palette, Text 2 = McKesson Blue (titles, as in the Standard Template), Background 2 = Light Sand | [`dist/office/Theme Colors/McKesson Data Viz.xml`](../dist/office/Theme%20Colors/McKesson%20Data%20Viz.xml) |
| Theme fonts | Libre Franklin for headings and body | [`dist/office/Theme Fonts/McKesson Data Viz.xml`](../dist/office/Theme%20Fonts/McKesson%20Data%20Viz.xml) |
| PowerPoint template | 16:9, theme applied, the Standard Template's grid, left-aligned Bold McKesson Blue titles, no slides | [`dist/office/McKesson-DataViz.potx`](../dist/office/McKesson-DataViz.potx) |
| Starter deck | Native, editable sample charts: bar highlight, line, waterfall, 100% stacked bar. The internal release bundle also has a copy built on the McKesson Standard Template (`McKesson-DataViz-Starter-Official.pptx`) | [`dist/office/McKesson-DataViz-Starter.pptx`](../dist/office/McKesson-DataViz-Starter.pptx) |
| Chart workbook | Palette sheet, the same four charts in Excel, and a heat-table scorecard | [`dist/office/McKesson-DataViz-Charts.xlsx`](../dist/office/McKesson-DataViz-Charts.xlsx) |
| One-page PDFs | Cheat sheet (anatomy, colors, checklist) and chart chooser | [`dist/print/cheat-sheet.pdf`](../dist/print/cheat-sheet.pdf), [`dist/print/chart-chooser.pdf`](../dist/print/chart-chooser.pdf) |

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

Once the theme is applied, the color picker's top rows are the McKesson palette. **Accent 1** is McKesson Blue `#005A8C` (focus), **Accent 2** is Navy `#143359` (the accent for the one exception) and **Accent 3** is light blue `#66C4FF` (the series fill when one bar gets the navy accent). **Accent 6** is Orange `#EF8200`: use it only for "worse" (negatives, below target), never as a highlight. The context grey `#B4B0A5` isn't a theme slot: pick it with **More Colors › Hex**, or copy formatting from a sample chart with **Format Painter**.

## 4. Use the starter files
- **New deck:** copy `McKesson-DataViz.potx` to `Documents\Custom Office Templates` (Mac: `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates`). It then shows up under **File › New › Personal** (or **Custom**).
- **Charts:** open `McKesson-DataViz-Starter.pptx`, copy the slide whose chart matches your question, then **right-click the chart › Edit Data**. The speaker notes on each slide say what to change: for example, the waterfall's hidden "Base" column, and the enterprise line on the bar chart, which is a drawn shape.
- **Excel:** copy a chart from `McKesson-DataViz-Charts.xlsx` into your workbook and use **Select Data** to point it at your range. Paste it into PowerPoint with **Paste › Use Destination Theme & Embed Workbook**, so it stays editable.
- **Reuse your own formatting:** right-click a finished chart › **Save as Template…**. The `.crtx` file goes to `%APPDATA%\Microsoft\Templates\Charts`, and appears under **Insert › Recommended Charts › All Charts › Templates**.

Each chart type's click-by-click recipe is in its cookbook page under **Excel and PowerPoint**, for example [bar.md](cookbook/bar.md#excel-and-powerpoint).

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
All of these files are generated, so never edit them in `dist/` by hand. After changing `tokens/tokens.json`:
```powershell
.\.venv\Scripts\python.exe tokens\build.py           # theme XML, CSS, Plotly, ... (dist/)
.\.venv\Scripts\python.exe office\build_office.py    # .pptx, .potx, .xlsx (dist/office/)
.\.venv\Scripts\python.exe tools\build_guide.py       # the guide, plus the cheat sheet and chart chooser PDFs (dist/print/)
```
`office/build_office.py` needs `python-pptx`, `xlsxwriter` and `pandas`. It swaps the McKesson theme into each package itself, and removes xlsxwriter's `defaultThemeVersion` attribute, without which Excel ignores the embedded theme.
