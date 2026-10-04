---
applyTo: "**/*.{R,r,Rmd,qmd}"
---

> These rules are for code that **draws charts**. Skip them when you are editing the kit's own build tools and internals (`tools/`, `tokens/`, `python/mckviz/`, `guide/`, `office/`), which have their own conventions in `AGENTS.md` part B.
# R charts (ggplot2, gt)

Applies to R scripts, R Markdown and Quarto documents that draw charts or tables. The full rules are in `AGENTS.md`, and each `docs/cookbook/<chart>.md` page has an "R — ggplot2" section.

## Setup
```r
library(ggplot2)
source("dist/r/theme_mck.R")   # theme_mck(), mck_colors, mck_categorical, mck_sequential, mck_sequential_orange,
                               # mck_diverging, mck_highlight(), scale_fill_mck(), scale_fill_mck_seq(), scale_fill_mck_div(),
                               # mck_font(), mck_wrap()
ff <- mck_font()               # registers fonts/LibreFranklin under its own name (needs systemfonts)
p <- ggplot(...) + theme_mck(base_family = ff)          # and family = ff in geom_text() / annotate()
ggsave("out/chart.png", p, width = 10, height = 5.6, dpi = 200, device = ragg::agg_png, bg = "white")
```
Use `mck_font()` rather than the font name "Libre Franklin": matching the installed static fonts by name can pick the italic file for regular text. Render with `ragg` so registered fonts are used. A complete example is in `examples/r/gallery_ggplot2.R`.

## Rules
- **No hex literals.** Use `mck_colors$focus`, `$focus_light`, `$context`, `$context_light`, `$accent` (navy exception), `$negative` (orange, only for "worse"), `$total`, `$annotation`, `$headline`, `$text`, `$muted`, `$grid`, `$axis`, `$surface_subtle` and `$negative_text`, plus the palette vectors above.
- **Highlight:** `scale_fill_manual(values = mck_highlight(levels(x), focus = ..., accent = ...), guide = "none")`. Grey context and blue focus, with ≤ 2 highlighted items.
- **Titles:** `labs(title = mck_wrap(<insight sentence>), subtitle = <metric, unit, scope, period>, caption = "Footnote\nSource: ...")`. `mck_wrap()` balances long headlines over 2 lines, since ggplot2 doesn't wrap titles. `theme_mck()` left-aligns titles to the plot edge and sizes them for 13.33 in slides; for a 10 in figure use `theme_mck(base_size = 10)` with a 17 pt title. Build the numbers in the title with `sprintf()` from the data.
- **Direct labels:** use `geom_text()` at bar ends and line ends, then `guides(fill = "none")`, and when values are labelled remove the value axis and gridlines with `theme(axis.text.x = element_blank(), panel.grid = element_blank())`. To bold the focus category, draw the category labels with `geom_text()` instead of styling the axis text. A legend, if needed, goes at the top-left.
- **Bars:** `geom_col(width = 0.67)`, starting at zero (`expansion(mult = c(0, ...))`), sorted with `reorder()` unless the order is natural.
- **Numbers:** a true minus (`sub("-", "−", ...)`) and an explicit + on deltas. Units go in the subtitle.
- **Tables:** use `{gt}` with `opt_table_lines(extent = "none")` and horizontal hairlines only, and shade ≤ 2 columns with `data_color()` on a token ramp (see `docs/cookbook/tables.md`).
- **People data:** `filter(n >= 10)` before plotting. Never label or tooltip individuals.
- **Never edit `dist/r/theme_mck.R`**. It is generated from `tokens/tokens.json` by `python tokens/build.py`.
