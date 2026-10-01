# Reference charts in ggplot2 using the generated McKesson theme (dist/r/theme_mck.R) and the synthetic data.
#
#   Rscript examples/r/gallery_ggplot2.R        (from the repo root)  ->  examples/output/r-*.png
#
# Needs: ggplot2, dplyr, readr, scales, ragg, systemfonts. Each chart shows the house rules: insight headline,
# neutral subtitle, grey context vs. blue focus, direct labels instead of a legend, a source line.

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
})
source("dist/r/theme_mck.R")

ff <- mck_font()                                     # bundled Libre Franklin, registered under its own name
src <- "Source: Synthetic data for illustration only"
minus <- function(x) gsub("-", "−", x, fixed = TRUE)   # true minus sign

# theme_mck() sizes type for 13.33 in slides (24 pt headline); scale it to the 10 in figure, as mckviz does.
theme_fig <- function() {
  theme_mck(base_size = 10, base_family = ff) +
    theme(plot.title = element_text(size = 17, lineheight = 1.1), plot.subtitle = element_text(size = 11),
          plot.caption = element_text(size = 8), axis.text = element_text(size = 9))
}
out <- function(p, name, width = 10, height = 5.6) {
  path <- file.path("examples", "output", paste0("r-", name, ".png"))
  ggsave(path, p, width = width, height = height, dpi = 200, device = ragg::agg_png, bg = "white")
  message("wrote ", path)
}


# 1. Bar highlight: grey context, the two families the headline names in blue, labelled benchmark ---------------
bar_highlight <- function() {
  df <- read_csv("examples/data/attrition_by_job_family.csv", show_col_types = FALSE) |>
    mutate(job_family = reorder(job_family, vol_attrition_pct),
           hi = vol_attrition_pct > 20,                       # only what the headline names
           face = ifelse(hi, "bold", "plain"),
           ink = ifelse(hi, mck_colors$headline, mck_colors$text))
  ent <- df$enterprise_rate_pct[1]
  top <- max(df$vol_attrition_pct)
  ggplot(df, aes(vol_attrition_pct, job_family)) +
    geom_blank() +                                            # fix the discrete y scale before numeric annotations
    geom_vline(xintercept = ent, colour = mck_colors$total, linetype = "22", linewidth = 0.35) +   # under the bars
    annotate("label", x = ent, y = nrow(df) + 0.7, label = sprintf("Enterprise %.1f%%", ent), size = 3.1,
             colour = mck_colors$annotation, family = ff, linewidth = 0, fill = "white") +
    geom_col(aes(fill = job_family), width = 0.67) +
    geom_segment(x = 0, xend = 0, y = 0.4, yend = nrow(df) + 0.4, colour = mck_colors$axis, linewidth = 0.3) +
    geom_text(aes(label = sprintf("%.1f%%", vol_attrition_pct), fontface = face, colour = ink),
              hjust = -0.15, size = 3.3, family = ff) +
    # Category labels drawn in the panel (left of zero), so they can be bolded and share the headline's left edge.
    geom_text(aes(x = -top * 0.012, label = job_family, fontface = face, colour = ink),
              hjust = 1, size = 3.3, family = ff) +
    scale_fill_manual(values = mck_highlight(levels(df$job_family), focus = df$job_family[df$hi]), guide = "none") +
    scale_colour_identity() +
    scale_x_continuous(limits = c(-top * 0.4, top * 1.1), expand = expansion(0)) +
    coord_cartesian(clip = "off") +
    labs(title = mck_wrap(sprintf("Two frontline job families lose about 1 in 4 people a year, well above the %.1f%% enterprise rate", ent)),
         subtitle = "Voluntary attrition by job family, FY26 (%)",
         caption = paste("Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months.", src, sep = "\n"),
         x = NULL, y = NULL) +
    theme_fig() +
    theme(axis.text = element_blank(), panel.grid = element_blank(), axis.line.x = element_blank())
}


# 2. Line with end labels and a shaded gap (no legend) ----------------------------------------------------------
line_gap <- function() {
  df <- read_csv("examples/data/data_ai_supply_demand.csv", show_col_types = FALSE)
  last <- df[nrow(df), ]
  gap <- last$demand_fte - last$internal_supply_fte
  lab <- function(y, text, colour) annotate("text", x = last$year + 0.12, y = y, hjust = 0, size = 3.4,
                                            family = ff, fontface = "bold", colour = colour, label = text)
  ggplot(df, aes(year)) +
    geom_ribbon(aes(ymin = internal_supply_fte, ymax = demand_fte), fill = mck_colors$negative, alpha = 0.12) +
    geom_line(aes(y = demand_fte), colour = mck_colors$total, linewidth = 1) +
    geom_line(aes(y = internal_supply_fte), colour = mck_colors$focus, linewidth = 1) +
    lab(last$demand_fte, paste("Demand", scales::comma(last$demand_fte)), mck_colors$total) +
    lab(last$internal_supply_fte, paste("Internal supply", scales::comma(last$internal_supply_fte)), mck_colors$focus) +
    lab((last$demand_fte + last$internal_supply_fte) / 2, paste("Gap", scales::comma(gap), "FTE"), mck_colors$negative_text) +
    scale_x_continuous(breaks = df$year, expand = expansion(mult = c(0.02, 0.2))) +
    scale_y_continuous(labels = scales::label_comma(), limits = c(800, NA)) +
    labs(title = mck_wrap(sprintf("Without action, Data & AI demand outruns internal supply by about %s FTE by 2030",
                                  scales::comma(round(gap, -1)))),
         subtitle = "Forecast Data & AI roles, 2024–2030, base scenario (FTE)",
         caption = paste("Supply = current headcount − projected attrition + planned internal moves. Forecast, not actuals.",
                         src, sep = "\n"),
         x = NULL, y = NULL) +
    theme_fig()
}


# 3. Diverging heatmap: midpoint = benchmark, symmetric, ranked rows, outlined focus column -----------------------
heatmap_diverging <- function() {
  drivers <- c("Growth", "Manager support", "Recognition", "Workload", "Tools & tech", "Belonging", "Pay fairness")
  df <- read_csv("examples/data/engagement_vs_benchmark.csv", show_col_types = FALSE) |>
    mutate(driver = factor(driver, levels = drivers),
           business_unit = reorder(business_unit, delta_vs_benchmark_pts, mean),   # highest average on top
           lab = ifelse(delta_vs_benchmark_pts == 0, "0", minus(sprintf("%+d", as.integer(delta_vs_benchmark_pts)))),
           txt = ifelse(delta_vs_benchmark_pts <= -8 | delta_vs_benchmark_pts >= 5, "white", mck_colors$headline),
           face = ifelse(driver == "Workload", "bold", "plain"))
  below <- sum(df$delta_vs_benchmark_pts[df$driver == "Workload"] < 0)
  worst <- as.character(df$business_unit[df$driver == "Workload"][which.min(df$delta_vs_benchmark_pts[df$driver == "Workload"])])
  w <- which(drivers == "Workload")
  ggplot(df, aes(driver, business_unit, fill = delta_vs_benchmark_pts)) +
    geom_tile(colour = "white", linewidth = 1.2) +
    geom_text(aes(label = lab, colour = txt, fontface = face), size = 3.2, family = ff) +
    annotate("rect", xmin = w - 0.5, xmax = w + 0.5, ymin = 0.5, ymax = nlevels(df$business_unit) + 0.5,
             fill = NA, colour = mck_colors$headline, linewidth = 0.7) +
    scale_colour_identity() +
    scale_fill_stepsn(colours = mck_diverging, breaks = seq(-7.5, 7.5, 3), limits = c(-10.5, 10.5),
                      labels = function(b) minus(sprintf("%+.1f", b)), name = NULL,
                      guide = guide_coloursteps(show.limits = FALSE)) +
    scale_x_discrete(position = "top", labels = function(x) sub(" ", "\n", x)) +
    labs(title = mck_wrap(sprintf("Workload trails the benchmark in %d of %d business units – %s most of all",
                                  below, nlevels(df$business_unit), sub(" &.*", "", worst))),
         subtitle = "Engagement driver score vs. external healthcare benchmark, by business unit, 2026 (points)",
         caption = paste("Rows ranked by average gap. Cells with fewer than 10 respondents are suppressed.", src, sep = "\n"),
         x = NULL, y = NULL) +
    theme_fig() +
    theme(panel.grid = element_blank(), axis.line.x = element_blank(), legend.position = "bottom",
          legend.justification = "right", legend.key.height = unit(6, "pt"), legend.key.width = unit(52, "pt"),
          legend.text = element_text(size = 8, colour = mck_colors$muted))
}

out(bar_highlight(), "bar-highlight")
out(line_gap(), "line-gap")
out(heatmap_diverging(), "heatmap-diverging", height = 5.4)
