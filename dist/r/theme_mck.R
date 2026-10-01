# GENERATED from tokens/tokens.json - McKesson data-viz theme for ggplot2.
# source("dist/r/theme_mck.R"); ggplot(...) + theme_mck() + scale_fill_mck()
# Fonts: ff <- mck_font() registers the bundled TTFs (needs {systemfonts}; render with {ragg}), then use
# theme_mck(base_family = ff) and family = ff in geom_text(). Long titles: labs(title = mck_wrap("...")).

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
      # Gridlines are set on the parent, so theme(panel.grid = element_blank()) removes them all.
      panel.grid = ggplot2::element_line(color = mck_colors$grid, linewidth = 0.3),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
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

# Register the bundled Libre Franklin TTFs under their own family name and return that name. Matching the installed
# "Libre Franklin" by name is unreliable: the static Italic file isn't flagged as italic, so regular text can come out italic.
mck_font <- function(dir = "fonts/LibreFranklin", family = "Libre Franklin MCK") {
  if (!family %in% systemfonts::registry_fonts()$family) {
    f <- function(style) file.path(dir, paste0("LibreFranklin-", style, ".ttf"))
    systemfonts::register_font(family, plain = f("Regular"), bold = f("Bold"), italic = f("Italic"),
                               bolditalic = f("BoldItalic"))
  }
  family
}

# Headlines are full sentences and ggplot2 doesn't wrap titles: wrap to the fewest lines, then narrow the width
# while the line count holds, so lines come out balanced (no single word dangling on the last line).
mck_wrap <- function(x, width = 75) {
  n <- length(strwrap(x, width = width))
  while (n > 1 && width > 20 && length(strwrap(x, width = width - 1)) == n) width <- width - 1
  paste(strwrap(x, width = width), collapse = "\n")
}
