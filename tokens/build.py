"""Build platform-specific theme files from tokens/tokens.json.

Usage:  python tokens/build.py
Writes: dist/ (CSS, Plotly, Vega-Lite, matplotlib, ggplot2, Power BI, Office theme XML, palette report + swatch image,
        portable agent rules from agents/*.template.md)
        python/mckviz/_tokens.json (runtime copy for the Python package)
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOKENS = json.loads((ROOT / "tokens" / "tokens.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist"

C = TOKENS["color"]
T = TOKENS["typography"]
K = TOKENS["chart"]
CORE = TOKENS["brand"]["core"]
EXT = {k: d for k, d in TOKENS["brand"]["extended"].items() if not k.startswith("$")}
FONT = T["family"]["primary"]
CAT = C["categorical"]["values"]


def v(path: str) -> str:
    """Resolve a dotted token path under `color`, e.g. 'text.muted'."""
    node = C
    for key in path.split("."):
        node = node[key]
    return node["value"] if isinstance(node, dict) else node


def write(rel: str, text: str) -> None:
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    print(f"  wrote dist/{rel}")


def role(name: str) -> dict:
    r = T["roles"][name]
    return {**r, "hex": v(r["color"])}


# ---------------------------------------------------------------- CSS
def build_css() -> None:
    lines = [":root {"]
    for k, t in CORE.items():
        lines.append(f"  --mck-{k}: {t['value']};")
    for k, t in TOKENS["brand"]["core_2026"].items():
        lines.append(f"  --mck-{k.replace('_', '-')}: {t['value']};")
    for fam, t in EXT.items():
        for step in ("light", "mid", "base", "dark"):
            if t.get(step):
                lines.append(f"  --mck-{fam}-{step}: {t[step]};")
    for group in ("text", "surface", "chart", "semantic"):
        for k, t in C[group].items():
            lines.append(f"  --mck-{group}-{k.replace('_', '-')}: {t['value']};")
    for i, hx in enumerate(CAT, 1):
        lines.append(f"  --mck-cat-{i}: {hx};")
    for name, ramp in C["sequential"].items():
        for i, hx in enumerate(ramp, 1):
            lines.append(f"  --mck-seq-{name}-{i}: {hx};")
    for i, hx in enumerate(C["diverging"]["orange_blue"]["values"], 1):
        lines.append(f"  --mck-div-{i}: {hx};")
    lines.append(f"  --mck-font: {T['family']['fallback_web']};")
    for name in T["roles"]:
        if name.startswith("$"):
            continue
        r = role(name)
        lines += [
            f"  --mck-{name}-size: {r['size_px']}px;",
            f"  --mck-{name}-weight: {r['weight']};",
            f"  --mck-{name}-color: {r['hex']};",
        ]
    lines.append(f"  --mck-pad: {K['spacing']['padding_px']}px;")
    lines.append("}")

    components = f"""
/* Libre Franklin: load from Google Fonts in your <head>, or @font-face from /fonts in this repo.
   <link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"> */

.mck-chart {{
  font-family: var(--mck-font);
  color: var(--mck-text-primary);
  background: var(--mck-surface-default);
  padding: var(--mck-pad);
  max-width: 960px;
}}
.mck-chart--dark {{ background: var(--mck-surface-dark); color: var(--mck-text-inverse); }}
.mck-chart--dark .mck-headline, .mck-chart--dark .mck-subtitle, .mck-chart--dark .mck-footnote {{ color: var(--mck-text-inverse); }}
.mck-headline {{
  font-size: var(--mck-headline-size); font-weight: var(--mck-headline-weight);
  color: var(--mck-headline-color); line-height: 1.2; margin: 0 0 {K['spacing']['headline_gap_px']}px; max-width: 60ch;
}}
.mck-subtitle {{
  font-size: var(--mck-subtitle-size); font-weight: var(--mck-subtitle-weight);
  color: var(--mck-subtitle-color); margin: 0 0 12px;
}}
.mck-plot {{ width: 100%; }}
.mck-footnote {{
  font-size: var(--mck-footnote-size); font-weight: var(--mck-footnote-weight);
  color: var(--mck-footnote-color); margin-top: {K['spacing']['footnote_gap_px']}px; line-height: 1.4;
}}
.mck-callout {{ font-size: var(--mck-annotation-size); color: var(--mck-annotation-color); }}
.mck-callout strong {{ font-weight: 700; display: block; }}
.mck-kpi {{ font-size: var(--mck-kpi-size); font-weight: var(--mck-kpi-weight); color: var(--mck-kpi-color); line-height: 1; }}
.mck-legend {{ display: flex; gap: 16px; flex-wrap: wrap; font-size: var(--mck-label-size); margin-bottom: 8px; }}
.mck-legend span::before {{ content: ""; display: inline-block; width: 10px; height: 10px; margin-right: 6px; background: var(--swatch); }}

/* Tables: horizontal rules only, numbers right-aligned in tabular figures, navy rule above the total row. */
.mck-table {{ border-collapse: collapse; width: 100%; font-size: var(--mck-label-size); font-variant-numeric: tabular-nums lining-nums; }}
.mck-table th {{
  font-weight: 600; color: var(--mck-text-headline); text-align: left; vertical-align: bottom;
  padding: 6px 10px; border-bottom: 1px solid var(--mck-chart-axis);
}}
.mck-table td, .mck-table tbody th {{ padding: 6px 10px; border-bottom: 1px solid var(--mck-chart-grid); }}
.mck-table tbody th {{ font-weight: 400; color: var(--mck-text-primary); text-align: left; vertical-align: middle; }}
.mck-table .num {{ text-align: right; white-space: nowrap; }}
.mck-table thead .num {{ white-space: normal; }}
.mck-table tbody th {{ min-width: 9em; }}
.mck-table tr.is-focus td, .mck-table tr.is-focus th {{ font-weight: 700; color: var(--mck-text-headline); }}
.mck-table tr.is-total td, .mck-table tr.is-total th {{
  font-weight: 700; color: var(--mck-text-headline); border-top: 1.5px solid var(--mck-chart-total); border-bottom: none;
}}
.mck-table td.is-muted {{ color: var(--mck-text-muted); background: var(--mck-chart-context-light); }}
.mck-table .bar {{ display: inline-block; height: 10px; background: var(--mck-chart-context); vertical-align: middle; margin-right: 6px; }}
.mck-table tr.is-focus .bar {{ background: var(--mck-chart-focus); }}
@media (max-width: 600px) {{
  .mck-chart {{ padding: 16px; }}
  .mck-headline {{ font-size: 18px; }}
  .mck-subtitle {{ font-size: 13px; }}
  .mck-table {{ font-size: 12px; }}
  .mck-table th, .mck-table td {{ padding: 4px 6px; }}
  .mck-table th:first-child {{ position: sticky; left: 0; z-index: 1; background: var(--mck-surface-default); }}
}}
"""
    write("web/mck-viz.css", "/* GENERATED from tokens/tokens.json - do not edit by hand. */\n" + "\n".join(lines) + components)


# ---------------------------------------------------------------- Plotly
def plotly_template() -> dict:
    tick, lab, sub, head = role("tick"), role("label"), role("subtitle"), role("headline")
    axis_common = {
        "showgrid": False,
        "zeroline": False,
        "showline": True,
        "linecolor": v("chart.axis"),
        "linewidth": K["axis"]["width_px"],
        "ticks": "",
        "tickfont": {"size": tick["size_px"], "color": tick["hex"]},
        "title": {"font": {"size": tick["size_px"], "color": tick["hex"]}, "standoff": 8},
        "automargin": True,
    }
    return {
        "layout": {
            "font": {"family": T["family"]["fallback_web"].replace("'", ""), "size": lab["size_px"], "color": v("text.primary")},
            "title": {
                "font": {"size": head["size_px"], "color": head["hex"], "weight": 700},
                "x": 0, "xanchor": "left", "xref": "container", "pad": {"l": K["spacing"]["padding_px"]},
                "subtitle": {"font": {"size": sub["size_px"], "color": sub["hex"]}},
            },
            "colorway": CAT,
            "paper_bgcolor": v("surface.default"),
            "plot_bgcolor": v("surface.default"),
            "margin": {"l": 64, "r": 32, "t": 96, "b": 72},
            "bargap": round(1 - K["bar"]["band_fill"], 2),
            "bargroupgap": 0.08,
            "xaxis": {**axis_common},
            "yaxis": {**axis_common, "showline": False, "showgrid": True, "gridcolor": v("chart.grid"), "gridwidth": K["grid"]["width_px"]},
            "legend": {"orientation": "h", "x": 0, "xanchor": "left", "y": 1.02, "yanchor": "bottom",
                       "font": {"size": lab["size_px"], "color": lab["hex"]}, "title": {"text": ""}},
            "hoverlabel": {"bgcolor": v("text.headline"), "bordercolor": v("text.headline"),
                           "font": {"family": FONT, "color": "#FFFFFF", "size": lab["size_px"]}},
            "colorscale": {
                "sequential": [[i / (len(C["sequential"]["blue"]) - 1), c] for i, c in enumerate(C["sequential"]["blue"])],
                "diverging": [[i / (len(C["diverging"]["orange_blue"]["values"]) - 1), c]
                              for i, c in enumerate(C["diverging"]["orange_blue"]["values"])],
            },
            "annotationdefaults": {"font": {"size": role("annotation")["size_px"], "color": v("chart.annotation")},
                                   "showarrow": False, "align": "left"},
            "shapedefaults": {"line": {"color": v("chart.axis"), "width": 1}},
        },
        "data": {
            "scatter": [{"line": {"width": K["line"]["width_px"]}, "marker": {"size": K["marker"]["size_px"]}}],
            "bar": [{"marker": {"line": {"width": 0}}, "textfont": {"size": lab["size_px"]}, "cliponaxis": False}],
            "pie": [{"hole": K["donut"]["hole"], "sort": True, "direction": "clockwise",
                     "marker": {"line": {"color": "#FFFFFF", "width": 2}}}],
        },
    }


def build_plotly() -> None:
    tpl = plotly_template()
    write("python/plotly_template.json", json.dumps(tpl, indent=2))
    write("web/mck-plotly-template.js",
          "// GENERATED from tokens/tokens.json. Usage: Plotly.newPlot(el, data, {template: MCK_PLOTLY_TEMPLATE, ...})\n"
          f"window.MCK_PLOTLY_TEMPLATE = {json.dumps(tpl, indent=2)};\n")


# ---------------------------------------------------------------- Vega-Lite
def build_vega() -> None:
    tick, lab, head, sub = role("tick"), role("label"), role("headline"), role("subtitle")
    cfg = {
        "font": FONT,
        "background": v("surface.default"),
        "padding": K["spacing"]["padding_px"],
        "view": {"stroke": None},
        "title": {"anchor": "start", "fontSize": head["size_px"], "fontWeight": 700, "color": head["hex"],
                  "subtitleFontSize": sub["size_px"], "subtitleColor": sub["hex"], "subtitleFontWeight": 400, "offset": 16},
        "axis": {"labelColor": tick["hex"], "labelFontSize": tick["size_px"], "titleColor": tick["hex"],
                 "titleFontSize": tick["size_px"], "titleFontWeight": 400, "domainColor": v("chart.axis"),
                 "tickColor": v("chart.axis"), "gridColor": v("chart.grid"), "ticks": False},
        "axisX": {"grid": False},
        "axisY": {"domain": False, "grid": True},
        "legend": {"orient": "top", "labelFontSize": lab["size_px"], "labelColor": lab["hex"], "title": None, "symbolType": "square"},
        "range": {"category": CAT, "ordinal": C["sequential"]["blue"], "ramp": C["sequential"]["blue"],
                  "diverging": C["diverging"]["orange_blue"]["values"], "heatmap": C["sequential"]["blue"]},
        "bar": {"fill": v("chart.focus"), "continuousBandSize": 16},
        "line": {"stroke": v("chart.focus"), "strokeWidth": K["line"]["width_px"]},
        "point": {"filled": True, "size": 40},
        "text": {"font": FONT, "fontSize": lab["size_px"], "fill": lab["hex"]},
        "scale": {"bandPaddingInner": round(1 - K["bar"]["band_fill"], 2)},
    }
    write("web/vega-lite-config.json", json.dumps(cfg, indent=2))


# ---------------------------------------------------------------- matplotlib
def build_mplstyle() -> None:
    tick, lab = role("tick"), role("label")
    cyc = ", ".join(f"'{h.lstrip('#')}'" for h in CAT)
    s = f"""# GENERATED from tokens/tokens.json - McKesson data-viz matplotlib style
# Use via: import mckviz; mckviz.use()   (also registers the bundled Libre Franklin fonts)
font.family: sans-serif
font.sans-serif: {FONT}, Arial, DejaVu Sans
font.size: {lab['size_pt']}
text.color: {v('text.primary')}

figure.facecolor: white
figure.dpi: 110
savefig.dpi: 300
savefig.bbox: tight
savefig.pad_inches: 0.25
figure.figsize: 10, 5.625

axes.facecolor: white
axes.edgecolor: {v('chart.axis')}
axes.linewidth: {K['axis']['width_pt']}
axes.spines.top: False
axes.spines.right: False
axes.spines.left: False
axes.grid: True
axes.grid.axis: y
axes.axisbelow: True
axes.labelcolor: {tick['hex']}
axes.labelsize: {tick['size_pt']}
axes.titlesize: {role('subtitle')['size_pt']}
axes.titleweight: normal
axes.titlelocation: left
axes.titlecolor: {role('subtitle')['hex']}
axes.prop_cycle: cycler('color', [{cyc}])
axes.xmargin: 0.02

grid.color: {v('chart.grid')}
grid.linewidth: {K['grid']['width_px']}

xtick.color: {tick['hex']}
ytick.color: {tick['hex']}
xtick.labelsize: {tick['size_pt']}
ytick.labelsize: {tick['size_pt']}
xtick.major.size: 0
ytick.major.size: 0
xtick.major.pad: 6
ytick.major.pad: 6

lines.linewidth: {K['line']['width_pt']}
lines.solid_capstyle: round
patch.linewidth: 0

legend.frameon: False
legend.fontsize: {lab['size_pt']}
legend.labelcolor: {lab['hex']}
"""
    # '#' starts a comment in .mplstyle files, so hex colors must be written without it.
    s = re.sub(r": #([0-9A-Fa-f]{6})\b", r": \1", s)
    write("python/mckviz.mplstyle", s)


# ---------------------------------------------------------------- ggplot2
def build_r() -> None:
    tick, lab, head, sub, foot = role("tick"), role("label"), role("headline"), role("subtitle"), role("footnote")
    cat = ", ".join(f'"{h}"' for h in CAT)
    seq = ", ".join(f'"{h}"' for h in C["sequential"]["blue"])
    div = ", ".join(f'"{h}"' for h in C["diverging"]["orange_blue"]["values"])
    r = f"""# GENERATED from tokens/tokens.json - McKesson data-viz theme for ggplot2.
# source("dist/r/theme_mck.R"); ggplot(...) + theme_mck() + scale_fill_mck()
# Fonts: ff <- mck_font() registers the bundled TTFs (needs {{systemfonts}}; render with {{ragg}}), then use
# theme_mck(base_family = ff) and family = ff in geom_text(). Long titles: labs(title = mck_wrap("...")).

mck_colors <- list(
  blue = "{CORE['blue']['value']}", navy = "{CORE['navy']['value']}", orange = "{CORE['orange']['value']}", sand = "{CORE['sand']['value']}",
  focus = "{v('chart.focus')}", accent = "{v('chart.accent')}", context = "{v('chart.context')}",
  context_light = "{v('chart.context_light')}", total = "{v('chart.total')}",
  positive = "{v('semantic.positive')}", negative = "{v('semantic.negative')}",
  text = "{v('text.primary')}", muted = "{v('text.muted')}", headline = "{v('text.headline')}",
  grid = "{v('chart.grid')}", axis = "{v('chart.axis')}", annotation = "{v('chart.annotation')}",
  surface_subtle = "{v('surface.subtle')}", negative_text = "{v('semantic.negative_text')}"
)
mck_categorical <- c({cat})
mck_sequential  <- c({seq})
mck_sequential_orange <- c({", ".join(f'"{h}"' for h in C["sequential"]["orange"])})
mck_diverging   <- c({div})

theme_mck <- function(base_size = {lab['size_pt']}, base_family = "{FONT}") {{
  ggplot2::theme_minimal(base_size = base_size, base_family = base_family) +
    ggplot2::theme(
      text = ggplot2::element_text(color = mck_colors$text),
      plot.title = ggplot2::element_text(face = "bold", size = {head['size_pt']}, color = mck_colors$headline, margin = ggplot2::margin(b = 4)),
      plot.subtitle = ggplot2::element_text(size = {sub['size_pt']}, color = mck_colors$text, margin = ggplot2::margin(b = 12)),
      plot.caption = ggplot2::element_text(size = {foot['size_pt']}, color = mck_colors$muted, hjust = 0, margin = ggplot2::margin(t = 12)),
      plot.title.position = "plot", plot.caption.position = "plot",
      axis.text = ggplot2::element_text(size = {tick['size_pt']}, color = mck_colors$muted),
      axis.title = ggplot2::element_text(size = {tick['size_pt']}, color = mck_colors$muted),
      axis.line.x = ggplot2::element_line(color = mck_colors$axis, linewidth = 0.3),
      axis.ticks = ggplot2::element_blank(),
      # Gridlines are set on the parent, so theme(panel.grid = element_blank()) removes them all.
      panel.grid = ggplot2::element_line(color = mck_colors$grid, linewidth = 0.3),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      legend.position = "top", legend.justification = "left", legend.title = ggplot2::element_blank(),
      legend.text = ggplot2::element_text(size = {lab['size_pt']}, color = mck_colors$text),
      plot.margin = ggplot2::margin(16, 16, 16, 16)
    )
}}

scale_fill_mck  <- function(...) ggplot2::scale_fill_manual(values = mck_categorical, ...)
scale_color_mck <- function(...) ggplot2::scale_color_manual(values = mck_categorical, ...)
scale_fill_mck_seq <- function(...) ggplot2::scale_fill_gradientn(colors = mck_sequential, ...)
scale_fill_mck_div <- function(...) ggplot2::scale_fill_gradientn(colors = mck_diverging, ...)

# Highlight helper: returns a named vector mapping every level to context grey except `focus` (blue) and `accent` (orange).
mck_highlight <- function(levels, focus = NULL, accent = NULL) {{
  cols <- stats::setNames(rep(mck_colors$context, length(levels)), levels)
  cols[focus] <- mck_colors$focus
  cols[accent] <- mck_colors$accent
  cols
}}

# Register the bundled Libre Franklin TTFs under their own family name and return that name. Matching the installed
# "{FONT}" by name is unreliable: the static Italic file isn't flagged as italic, so regular text can come out italic.
mck_font <- function(dir = "fonts/LibreFranklin", family = "{FONT} MCK") {{
  if (!family %in% systemfonts::registry_fonts()$family) {{
    f <- function(style) file.path(dir, paste0("LibreFranklin-", style, ".ttf"))
    systemfonts::register_font(family, plain = f("Regular"), bold = f("Bold"), italic = f("Italic"),
                               bolditalic = f("BoldItalic"))
  }}
  family
}}

# Headlines are full sentences and ggplot2 doesn't wrap titles: wrap to the fewest lines, then narrow the width
# while the line count holds, so lines come out balanced (no single word dangling on the last line).
mck_wrap <- function(x, width = 75) {{
  n <- length(strwrap(x, width = width))
  while (n > 1 && width > 20 && length(strwrap(x, width = width - 1)) == n) width <- width - 1
  paste(strwrap(x, width = width), collapse = "\\n")
}}
"""
    write("r/theme_mck.R", r)


# ---------------------------------------------------------------- Power BI
def build_powerbi() -> None:
    head, sub, lab, tick = role("headline"), role("subtitle"), role("label"), role("tick")
    font = f"{FONT}, Segoe UI, wf_segoe-ui_normal, helvetica, arial, sans-serif"
    theme = {
        "name": "McKesson Data Viz",
        # Categorical order first; tints only extend the cycle for 9+ series. No repeats, so no two series share a color.
        "dataColors": list(dict.fromkeys(CAT + C["sequential"]["blue"][1:4] + C["sequential"]["orange"][1:4])),
        "foreground": v("text.primary"),
        "foregroundNeutralSecondary": v("text.muted"),
        "foregroundNeutralTertiary": v("chart.context"),
        "background": v("surface.default"),
        "backgroundLight": v("surface.subtle"),
        "backgroundNeutral": v("chart.context_light"),
        "tableAccent": CORE["blue"]["value"],
        "good": v("semantic.positive"),
        "neutral": v("semantic.neutral"),
        "bad": v("semantic.negative"),
        "maximum": C["sequential"]["blue"][-1],
        "center": C["diverging"]["orange_blue"]["values"][3],
        "minimum": C["sequential"]["blue"][0],
        "hyperlink": EXT["azure"]["dark"],
        "visitedHyperlink": v("chart.context_on_dark"),
        "textClasses": {
            "title": {"fontSize": head["size_pt"] - 8, "fontFace": font, "color": head["hex"]},
            "header": {"fontSize": sub["size_pt"], "fontFace": font, "color": head["hex"]},
            "callout": {"fontSize": 32, "fontFace": font, "color": head["hex"]},
            "label": {"fontSize": tick["size_pt"] - 1, "fontFace": font, "color": v("text.primary")},
        },
        "visualStyles": {
            "*": {"*": {
                "title": [{"show": True, "fontFamily": font, "fontColor": {"solid": {"color": head["hex"]}},
                           "fontSize": 14, "bold": True, "alignment": "left"}],
                "subTitle": [{"show": True, "fontFamily": font, "fontColor": {"solid": {"color": sub["hex"]}}, "fontSize": 11}],
                "background": [{"show": True, "color": {"solid": {"color": v("surface.default")}}, "transparency": 0}],
                "border": [{"show": False}],
                "dropShadow": [{"show": False}],
                "valueAxis": [{"gridlineColor": {"solid": {"color": v("chart.grid")}}, "gridlineThickness": 1,
                               "labelColor": {"solid": {"color": tick["hex"]}}, "fontSize": 9, "showAxisTitle": False}],
                "categoryAxis": [{"labelColor": {"solid": {"color": tick["hex"]}}, "fontSize": 9, "showAxisTitle": False,
                                  "gridlineShow": False}],
                "legend": [{"position": "TopLeft", "labelColor": {"solid": {"color": lab["hex"]}}, "fontSize": 9, "showTitle": False}],
                "labels": [{"color": {"solid": {"color": lab["hex"]}}, "fontSize": 9}],
            }},
            "page": {"*": {"background": [{"color": {"solid": {"color": v("surface.subtle")}}, "transparency": 0}]}},
        },
    }
    write("powerbi/mckesson-dataviz-theme.json", json.dumps(theme, indent=2))


# ---------------------------------------------------------------- Office (PowerPoint / Excel / Word)
def build_office() -> None:
    slots = {
        "dk1": v("text.primary"), "lt1": "FFFFFF", "dk2": CORE["navy"]["value"], "lt2": v("surface.subtle"),
        "accent1": CAT[0], "accent2": CAT[1], "accent3": CAT[2], "accent4": CAT[3], "accent5": CAT[4], "accent6": CAT[5],
        "hlink": EXT["azure"]["dark"], "folHlink": v("chart.context_on_dark"),
    }
    body = "\n".join(f"  <a:{k}><a:srgbClr val=\"{h.lstrip('#').upper()}\"/></a:{k}>" for k, h in slots.items())
    colors = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<a:clrScheme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="McKesson Data Viz">\n'
              f"{body}\n</a:clrScheme>\n")
    fonts = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<a:fontScheme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="McKesson Data Viz">\n'
             f'  <a:majorFont><a:latin typeface="{FONT}"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>\n'
             f'  <a:minorFont><a:latin typeface="{FONT}"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>\n'
             "</a:fontScheme>\n")
    write("office/Theme Colors/McKesson Data Viz.xml", colors)
    write("office/Theme Fonts/McKesson Data Viz.xml", fonts)


# ---------------------------------------------------------------- accessibility report
def _rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


def _lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def contrast(a, b):
    la, lb = (float(np.dot(_lin(_rgb(x)), [0.2126, 0.7152, 0.0722])) for x in (a, b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


_CVD = {  # Machado et al. 2009, severity 1.0
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "protanopia": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "tritanopia": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def _lab(h, cvd=None):
    c = _lin(_rgb(h))
    if cvd:
        c = np.clip(_CVD[cvd] @ c, 0, 1)
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ c
    xyz = xyz / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def min_delta(pal, cvd=None):
    best = (1e9, None)
    for i in range(len(pal)):
        for j in range(i + 1, len(pal)):
            d = float(np.linalg.norm(_lab(pal[i], cvd) - _lab(pal[j], cvd)))
            best = min(best, (d, (pal[i], pal[j])))
    return best


def build_report() -> None:
    rows = ["# Palette accessibility report", "", "_Generated by `tokens/build.py`. Do not edit by hand._", "",
            "## Text contrast on white (WCAG 2.x: 4.5:1 body, 3:1 large text / graphics)", "",
            "| Token | Hex | Ratio | Body text | Graphics |", "|---|---|---|---|---|"]
    checks = [("text.headline", v("text.headline")), ("text.primary", v("text.primary")), ("text.muted", v("text.muted")),
              ("chart.axis", v("chart.axis")), ("chart.context", v("chart.context")), ("chart.focus", v("chart.focus")),
              ("chart.accent", v("chart.accent")), ("semantic.positive_text", v("semantic.positive_text")),
              ("semantic.negative_text", v("semantic.negative_text"))]
    for name, hx in checks:
        r = contrast(hx, "#FFFFFF")
        rows.append(f"| `{name}` | `{hx}` | {r:.2f} | {'pass' if r >= 4.5 else '-'} | {'pass' if r >= 3 else 'fill/label needed'} |")
    rows += ["", "## Categorical palette - fills vs white and pairwise separability", "",
             "| # | Hex | Contrast vs white | Use as line/text? |", "|---|---|---|---|"]
    for i, hx in enumerate(CAT, 1):
        r = contrast(hx, "#FFFFFF")
        rows.append(f"| {i} | `{hx}` | {r:.2f} | {'yes' if r >= 3 else 'fill only (add label/outline)'} |")
    rows += ["", "Minimum pairwise CIELAB distance (dE76; > ~10 is comfortably distinct):", ""]
    for n in (4, 6, 8):
        rows.append(f"- **First {n} colors**: " + "; ".join(
            f"{cvd or 'normal vision'} {min_delta(CAT[:n], cvd)[0]:.1f}" for cvd in (None, *_CVD)))
    rows += ["", "Rule of thumb: stay within the first 6 categorical colors; always pair color with direct labels.", ""]
    write("palette-report.md", "\n".join(rows))


def build_swatches() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = [("Core", [CORE[k]["value"] for k in ("blue", "navy", "orange", "sand")]),
              ("Chart roles: focus / accent / context / total", [v("chart.focus"), v("chart.accent"), v("chart.context"), v("chart.total")]),
              ("Categorical (ordered)", CAT),
              ("Sequential blue", C["sequential"]["blue"]),
              ("Sequential teal", C["sequential"]["teal"]),
              ("Diverging orange-blue", C["diverging"]["orange_blue"]["values"])]
    fig, axes = plt.subplots(len(groups), 1, figsize=(10, 1.1 * len(groups)))
    for ax, (title, cols) in zip(axes, groups):
        for i, hx in enumerate(cols):
            ax.add_patch(plt.Rectangle((i, 0), 0.95, 1, color=hx))
            ax.text(i + 0.475, -0.25, hx, ha="center", va="top", fontsize=7, color="#505050")
        ax.set_xlim(0, 8)
        ax.set_ylim(-0.6, 1)
        ax.axis("off")
        ax.set_title(title, loc="left", fontsize=9, color="#143359")
    fig.tight_layout()
    out = DIST / "palette.png"
    fig.savefig(out, dpi=160)
    print("  wrote dist/palette.png")


# ---------------------------------------------------------------- portable agent rules
def build_agent_rules() -> None:
    """Fill agents/*.template.md placeholders from tokens, so the rules never drift from the palette.

    {{color:chart.focus}} -> hex · {{list:sequential.blue}} -> `#..`, `#..` · {{chart:bar.band_fill}} -> value
    {{role:headline.size_pt}} -> type role value · {{font}} · {{generated_note}}
    """
    def lookup(node, path):
        for key in path.split("."):
            node = node[key]
        return node

    def fill(m: re.Match) -> str:
        kind, _, path = m.group(1).partition(":")
        if kind == "color":
            return v(path)
        if kind == "list":
            return ", ".join(f"`{h}`" for h in lookup(C, path))
        if kind == "chart":
            return str(lookup(K, path))
        if kind == "role":
            return str(lookup(T["roles"], path))
        if kind == "font":
            return FONT
        if kind == "generated_note":
            return "GENERATED from tokens/tokens.json by tokens/build.py - edit agents/*.template.md, not this file."
        raise KeyError(f"unknown placeholder {{{{{m.group(1)}}}}}")

    for tpl in sorted((ROOT / "agents").glob("*.template.md")):
        text = re.sub(r"\{\{([a-z_]+(?::[\w.]+)?)\}\}", fill, tpl.read_text(encoding="utf-8"))
        write(f"agents/{tpl.name.replace('.template', '')}", text)


def main() -> None:
    print("Building tokens ->", DIST)
    build_css()
    build_plotly()
    build_vega()
    build_mplstyle()
    build_r()
    build_powerbi()
    build_office()
    build_report()
    build_swatches()
    build_agent_rules()
    pkg = ROOT / "python" / "mckviz"
    if pkg.exists():
        shutil.copyfile(ROOT / "tokens" / "tokens.json", pkg / "_tokens.json")
        shutil.copyfile(DIST / "python" / "mckviz.mplstyle", pkg / "mckviz.mplstyle")
        shutil.copyfile(DIST / "python" / "plotly_template.json", pkg / "plotly_template.json")
        print("  synced python/mckviz/ (_tokens.json, mckviz.mplstyle, plotly_template.json)")


if __name__ == "__main__":
    main()
