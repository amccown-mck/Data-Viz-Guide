# GENERATED from tokens/tokens.json - McKesson data-viz theme for ggplot2.
# source("dist/r/theme_mck.R"); ggplot(...) + theme_mck() + scale_fill_mck()
# Fonts: install Libre Franklin (repo /fonts) and, if needed, use {showtext} or {systemfonts}.

mck_colors <- list(
  blue = "#005A8C", navy = "#143359", orange = "#EF8200", sand = "#DEDBD1",
  focus = "#005A8C", accent = "#EF8200", context = "#B4B0A5",
  context_light = "#DEDBD1", total = "#143359",
  positive = "#00AF9D", negative = "#EF8200",
  text = "#505050", muted = "#737373", headline = "#143359",
  grid = "#E6E4DE", axis = "#8C8C8C", annotation = "#143359",
  surface_subtle = "#EFEDE7", negative_text = "#A75B00"
)
mck_categorical <- c("#005A8C", "#EF8200", "#00AF9D", "#143359", "#66C4FF", "#FFB502", "#00622C", "#D9F14E")
mck_sequential  <- c("#E6F3FB", "#B6E2FA", "#66C4FF", "#009EFF", "#0A5FBC", "#143359")
mck_sequential_orange <- c("#FFF3E0", "#FFD9A8", "#F7B25C", "#EF8200", "#A75B00", "#6B3A00")
mck_diverging   <- c("#A75B00", "#EF8200", "#F7C180", "#EFEDE7", "#99BDD1", "#005A8C", "#143359")

theme_mck <- function(base_size = 12, base_family = "Libre Franklin") {
  ggplot2::theme_minimal(base_size = base_size, base_family = base_family) +
    ggplot2::theme(
      text = ggplot2::element_text(color = mck_colors$text),
      plot.title = ggplot2::element_text(face = "bold", size = 24, color = mck_colors$headline, margin = ggplot2::margin(b = 4)),
      plot.subtitle = ggplot2::element_text(size = 14, color = mck_colors$text, margin = ggplot2::margin(b = 12)),
      plot.caption = ggplot2::element_text(size = 9, color = mck_colors$muted, hjust = 0, margin = ggplot2::margin(t = 12)),
      plot.title.position = "plot", plot.caption.position = "plot",
      axis.text = ggplot2::element_text(size = 11, color = mck_colors$muted),
      axis.title = ggplot2::element_text(size = 11, color = mck_colors$muted),
      axis.line.x = ggplot2::element_line(color = mck_colors$axis, linewidth = 0.3),
      axis.ticks = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_line(color = mck_colors$grid, linewidth = 0.3),
      legend.position = "top", legend.justification = "left", legend.title = ggplot2::element_blank(),
      legend.text = ggplot2::element_text(size = 12, color = mck_colors$text),
      plot.margin = ggplot2::margin(16, 16, 16, 16)
    )
}

scale_fill_mck  <- function(...) ggplot2::scale_fill_manual(values = mck_categorical, ...)
scale_color_mck <- function(...) ggplot2::scale_color_manual(values = mck_categorical, ...)
scale_fill_mck_seq <- function(...) ggplot2::scale_fill_gradientn(colors = mck_sequential, ...)
scale_fill_mck_div <- function(...) ggplot2::scale_fill_gradientn(colors = mck_diverging, ...)

# Highlight helper: returns a named vector mapping every level to context grey except `focus` (blue) and `accent` (orange).
mck_highlight <- function(levels, focus = NULL, accent = NULL) {
  cols <- stats::setNames(rep(mck_colors$context, length(levels)), levels)
  cols[focus] <- mck_colors$focus
  cols[accent] <- mck_colors$accent
  cols
}
