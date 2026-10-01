---
applyTo: "**/*.{R,Rmd,qmd}"
---
# R charts (ggplot2, gt)

Applies to R scripts, R Markdown and Quarto documents that draw charts or tables. The full rules are in `AGENTS.md`, and each `docs/cookbook/<chart>.md` page has an "R — ggplot2" section.

## Setup
```r
library(ggplot2)
source("dist/r/theme_mck.R")   # theme_mck(), mck_colors, mck_categorical, mck_sequential, mck_sequential_orange,
                               # mck_diverging, mck_highlight(), scale_fill_mck(), scale_fill_mck_seq(), scale_fill_mck_div()
```
Install Libre Franklin from `fonts/LibreFranklin` and register it with `{systemfonts}` or `{showtext}` if it doesn't render.

## Rules
- **No hex literals.** Use `mck_colors$focus`, `$context`, `$context_light`, `$accent`, `$total`, `$annotation`, `$headline`, `$text`, `$muted`, `$grid`, `$axis`, `$surface_subtle` and `$negative_text`, plus the palette vectors above.
- **Highlight:** `scale_fill_manual(values = mck_highlight(levels(x), focus = ..., accent = ...), guide = "none")`. Grey context and blue focus, with ≤ 2 highlighted items.
- **Titles:** `labs(title = <insight sentence>, subtitle = <metric, unit, scope, period>, caption = "Footnote\nSource: ...")`. Use `theme_mck()`, which left-aligns the titles to the plot edge. Build the numbers in the title with `sprintf()` from the data.
- **Direct labels:** use `geom_text()` at bar ends and line ends, then `guides(fill = "none")` and remove the value axis and gridlines when values are labelled. A legend, if needed, goes at the top-left.
- **Bars:** `geom_col(width = 0.67)`, starting at zero (`expansion(mult = c(0, ...))`), sorted with `reorder()` unless the order is natural.
- **Numbers:** a true minus (`sub("-", "−", ...)`) and an explicit + on deltas. Units go in the subtitle.
- **Tables:** use `{gt}` with `opt_table_lines(extent = "none")` and horizontal hairlines only, and shade ≤ 2 columns with `data_color()` on a token ramp (see `docs/cookbook/tables.md`).
- **People data:** `filter(n >= 10)` before plotting. Never label or tooltip individuals.
- **Never edit `dist/r/theme_mck.R`**. It is generated from `tokens/tokens.json` by `python tokens/build.py`.
