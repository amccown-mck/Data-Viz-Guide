"""mckviz - McKesson data-visualization helpers for matplotlib and Plotly.

    import mckviz as mv
    mv.use()                                   # fonts + matplotlib style + Plotly template "mck"
    colors = mv.highlight(df.job_family, focus="Pharmacy Ops")
    fig, ax = plt.subplots(); ax.barh(df.job_family, df.attrition, color=colors)
    mv.titles(fig, "Pharmacy Ops attrition is 2x the enterprise rate", "Voluntary attrition, FY26 (%)")
    mv.source(fig, "Source: Workday HCM; McKesson People Analytics")
    mv.save(fig, "out/attrition.png")

All colors, sizes and fonts come from tokens/tokens.json (copied to _tokens.json by tokens/build.py).
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, Sequence

_HERE = Path(__file__).resolve().parent
TOKENS: dict = json.loads((_HERE / "_tokens.json").read_text(encoding="utf-8"))
_C = TOKENS["color"]
_T = TOKENS["typography"]
_K = TOKENS["chart"]

FONT = _T["family"]["primary"]
CATEGORICAL: list[str] = _C["categorical"]["values"]
SEQUENTIAL: dict[str, list[str]] = _C["sequential"]
DIVERGING: list[str] = _C["diverging"]["orange_blue"]["values"]

colors = SimpleNamespace(
    **{k: t["value"] for k, t in TOKENS["brand"]["core"].items()},
    **{k: t["value"] for k, t in TOKENS["brand"]["core_2026"].items() if k != "text"},
    **{k: t["value"] for k, t in _C["chart"].items()},
    **{k: t["value"] for k, t in _C["semantic"].items()},
    text=_C["text"]["primary"]["value"],
    text_muted=_C["text"]["muted"]["value"],
    headline=_C["text"]["headline"]["value"],
    surface_subtle=_C["surface"]["subtle"]["value"],
    surface_dark=_C["surface"]["dark"]["value"],
)
extended = {fam: {k: val for k, val in d.items() if k in ("light", "mid", "base", "dark")}
            for fam, d in TOKENS["brand"]["extended"].items() if not fam.startswith("$")}


def _role(name: str) -> dict:
    r = dict(_T["roles"][name])
    node = _C
    for key in r["color"].split("."):
        node = node[key]
    r["hex"] = node["value"]
    return r


def _find_fonts() -> Path | None:
    for base in (_HERE, *_HERE.parents):
        cand = base / "fonts" / "LibreFranklin"
        if cand.exists():
            return cand
    return None


def register_fonts() -> bool:
    """Register bundled Libre Franklin TTFs with matplotlib. Returns True if found."""
    from matplotlib import font_manager as fm

    folder = _find_fonts()
    if not folder:
        return False
    for ttf in folder.glob("*.ttf"):
        fm.fontManager.addfont(str(ttf))
    return True


def use(plotly_default: bool = True) -> None:
    """Apply the McKesson style to matplotlib (and register/activate the Plotly template if Plotly is installed)."""
    import matplotlib.pyplot as plt

    register_fonts()
    plt.style.use(str(_HERE / "mckviz.mplstyle"))
    try:
        import plotly.io as pio

        pio.templates["mck"] = plotly_template()
        if plotly_default:
            pio.templates.default = "mck"
    except ImportError:
        pass


# ------------------------------------------------------------------ color logic
def highlight(labels: Iterable, focus=None, accent=None, base: str | None = None) -> list[str]:
    """Color list aligned to `labels`: grey context, blue `focus`, orange `accent`.

    focus / accent may be a single label or a collection of labels. Use `base=colors.focus` to make
    everything blue and only the accent orange (the 'uniform' pattern).
    """
    def as_set(x):
        if x is None:
            return set()
        return {x} if isinstance(x, (str, int, float)) else set(x)

    f, a = as_set(focus), as_set(accent)
    default = base or colors.context
    return [colors.accent if lab in a else colors.focus if lab in f else default for lab in labels]


def categorical(n: int) -> list[str]:
    """First n categorical colors. More than 6 series is a smell: group the tail into 'Other'."""
    if n > len(CATEGORICAL):
        raise ValueError(f"Max {len(CATEGORICAL)} categorical colors; group the long tail into 'Other'.")
    return CATEGORICAL[:n]


def sequential_cmap(name: str = "blue"):
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(f"mck_{name}", SEQUENTIAL[name])


def diverging_cmap():
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list("mck_div", DIVERGING)


# ------------------------------------------------------------------ matplotlib chart furniture
# Headline/subtitle/source are positioned at save() time by measuring rendered extents, so they never collide
# with the plot and always share one left edge with the outermost axis labels.
_SCALE = 0.75  # role sizes are specified for 13.33in slides; figures default to 10in wide


def halo(color: str = "white", width: float = 3):
    import matplotlib.patheffects as pe

    return [pe.withStroke(linewidth=width, foreground=color)]


def signed(value: float, decimals: int = 0, suffix: str = "") -> str:
    """Format with a true minus sign and explicit plus: +4, −11.5%. Zero renders without sign."""
    s = f"{abs(value):,.{decimals}f}"
    if float(s.replace(",", "")) == 0:
        return f"{s}{suffix}"
    return ("+" if value > 0 else MINUS) + s + suffix


MINUS = "\u2212"


def text_on(fill_hex: str) -> str:
    """Readable label color for text on a filled cell/bar: white or headline navy, whichever has more contrast.

    Mid-tones such as orange #EF8200 or azure #009EFF get navy (about 4.5-5:1) rather than white (under 3:1).
    """
    def lum(hex_color: str) -> float:
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return sum(w * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
                   for w, c in zip((0.2126, 0.7152, 0.0722), (r, g, b)))

    fill = lum(fill_hex)
    on_white = (1.05) / (fill + 0.05)
    on_navy = (fill + 0.05) / (lum(colors.headline) + 0.05)
    return "#FFFFFF" if on_white >= on_navy else colors.headline


def rgba(hex_color: str, alpha: float) -> str:
    """CSS/Plotly 'rgba(r, g, b, a)' string from a token hex, for translucent fills (gap washes, Sankey links)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def _balanced_wrap(text: str, max_chars: int) -> str:
    """Wrap to the fewest lines, then even out line lengths so no single word dangles on the last line."""
    import math
    import textwrap

    lines = textwrap.wrap(text, max_chars)
    if len(lines) > 1:
        target = math.ceil(len(text) / len(lines)) + 2
        while target < max_chars and len(textwrap.wrap(text, target)) > len(lines):
            target += 1
        lines = textwrap.wrap(text, target)
    return "\n".join(lines)


def titles(fig, headline: str, subtitle: str | None = None, dark: bool = False) -> None:
    """Left-aligned insight headline + neutral subtitle (metric, unit, scope, period) above the plot."""
    import textwrap

    h, s = _role("headline"), _role("subtitle")
    hsize, ssize = h["size_pt"] * _SCALE, s["size_pt"] * _SCALE * 1.05
    max_chars = max(24, int(fig.get_figwidth() * 72 * 0.94 / (0.54 * hsize)))
    head = fig.text(0, 1, _balanced_wrap(headline, max_chars), ha="left", va="top", fontsize=hsize,
                    fontweight="bold", color="white" if dark else h["hex"], linespacing=1.15)
    sub = None
    if subtitle:
        sub = fig.text(0, 1, textwrap.fill(subtitle, int(max_chars * hsize / ssize)), ha="left", va="top",
                       fontsize=ssize, color="white" if dark else s["hex"], linespacing=1.2)
    fig._mck = {**getattr(fig, "_mck", {}), "head": head, "sub": sub}


def source(fig, text: str, footnote: str | None = None, dark: bool = False) -> None:
    """Footnote (optional) and 'Source:' line, bottom-left."""
    f = _role("footnote")
    lines = ([footnote] if footnote else []) + [text]
    foot = fig.text(0, 0, "\n".join(lines), ha="left", va="top", fontsize=f["size_pt"],
                    color="white" if dark else f["hex"], fontweight=f["weight"], linespacing=1.35)
    fig._mck = {**getattr(fig, "_mck", {}), "foot": foot}


def layout(fig, gap_pt: float = 10) -> None:
    """Position headline/subtitle/source around the plot. Called automatically by save()."""
    fur = getattr(fig, "_mck", None)
    if not fur:
        return
    axes = [a for a in fig.axes if a.get_visible()]
    inv = fig.transFigure.inverted()
    gap = gap_pt / (fig.get_figheight() * 72)

    def box(artist):
        return inv.transform_bbox(artist.get_window_extent(fig.canvas.get_renderer()))

    def ax_boxes():
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        return [inv.transform_bbox(a.get_tightbbox(r)) for a in axes]

    left = min(b.x0 for b in ax_boxes())
    y = 1.0
    for key, spacing in (("head", 0.45), ("sub", 0.0)):
        t = fur.get(key)
        if t is not None:
            t.set_position((left, y))
            fig.canvas.draw()
            y -= box(t).height + gap * spacing
    header_bottom = y - gap * 1.8
    for _ in range(4):
        excess = max(b.y1 for b in ax_boxes()) - header_bottom
        if abs(excess) < 0.003:
            break
        fig.subplots_adjust(top=min(0.98, fig.subplotpars.top - excess))
    if fur.get("foot") is not None:
        fur["foot"].set_position((left, min(b.y0 for b in ax_boxes()) - gap * 1.6))


def label_bars(ax, bars, fmt: str = "{:,.0f}", inside: bool = False, color: str | None = None, pad: float = 3) -> None:
    """Direct value labels at bar ends (replaces value axis + gridlines)."""
    lab = _role("label")
    horizontal = bars.orientation == "horizontal" if hasattr(bars, "orientation") else False
    for b in bars:
        val = b.get_width() if horizontal else b.get_height()
        text = fmt(val) if callable(fmt) else fmt.format(val)
        kw = dict(textcoords="offset points", fontsize=lab["size_pt"] - 1, fontweight="medium",
                  color=color or ("white" if inside else lab["hex"]),
                  bbox=None if inside else dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
        if horizontal:
            ax.annotate(text, (b.get_x() + val, b.get_y() + b.get_height() / 2), xytext=(-pad if inside else pad, 0),
                        ha="right" if inside else "left", va="center", **kw)
        else:
            ax.annotate(text, (b.get_x() + b.get_width() / 2, b.get_y() + val), xytext=(0, -pad if inside else pad),
                        ha="center", va="top" if inside else "bottom", **kw)


def label_line_ends(ax, lines=None, fmt: str | None = None, dx: float = 6) -> None:
    """Direct labels at the right end of each line, colored like the line (replaces the legend)."""
    lab = _role("label")
    for ln in lines or ax.get_lines():
        if ln.get_label().startswith("_"):
            continue
        x, y = ln.get_xdata()[-1], ln.get_ydata()[-1]
        text = ln.get_label() if not fmt else f"{ln.get_label()} {fmt.format(y)}"
        ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", va="center",
                    fontsize=lab["size_pt"] - 1, color=ln.get_color(), fontweight="semibold",
                    annotation_clip=False, path_effects=halo())


def callout(ax, xy, title: str, body: str | None = None, xytext=(20, 20), arrow: bool = True) -> None:
    """Bold short title + 1-2 lines of explanation, next to the data it explains."""
    a = _role("annotation")
    size = a["size_pt"] - 1
    head = ax.annotate(title, xy, xytext=xytext, textcoords="offset points", fontsize=size, color=a["hex"],
                       fontweight="bold", ha="left", va="bottom", path_effects=halo(width=4))
    anchor = head
    if body:
        anchor = ax.annotate(body, (0, 0), xycoords=head, xytext=(0, -2), textcoords="offset points", fontsize=size,
                             color=a["hex"], ha="left", va="top", path_effects=halo(width=4))
    if arrow:
        ax.annotate("", xy=xy, xytext=(0, 0), textcoords=anchor,
                    arrowprops=dict(arrowstyle="-", color=a["hex"], lw=0.75, shrinkA=2, shrinkB=3))


def shade_period(ax, start, end, label: str | None = None) -> None:
    """Light band marking a period of interest (e.g., reorg, hiring freeze)."""
    ax.axvspan(start, end, color=colors.surface_subtle, zorder=0, lw=0)
    if label:
        ax.text(start, 1.0, " " + label, transform=ax.get_xaxis_transform(), va="bottom", ha="left",
                fontsize=_role("annotation")["size_pt"] - 2, color=colors.annotation, fontweight="bold")


def clean_axes(ax, keep: Sequence[str] = ("bottom",), grid: str | None = "y") -> None:
    """Strip spines/grid to the minimum; call after plotting."""
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)
    ax.grid(False)
    if grid:
        ax.grid(True, axis=grid, color=colors.grid, lw=_K["grid"]["width_px"])
    ax.set_axisbelow(True)


def save(fig, path: str | Path, **kw) -> Path:
    """Lay out headline/subtitle/source, then save (PNG for slides, SVG/PDF for print)."""
    layout(fig)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, **kw)
    return path


# ------------------------------------------------------------------ Plotly
def plotly_template():
    import plotly.graph_objects as go

    tpl_path = _HERE / "plotly_template.json"
    if not tpl_path.exists():
        tpl_path = next((p / "dist" / "python" / "plotly_template.json" for p in _HERE.parents
                         if (p / "dist" / "python" / "plotly_template.json").exists()), None)
    return go.layout.Template(json.loads(Path(tpl_path).read_text(encoding="utf-8")))


def pl_finish(fig, headline: str, subtitle: str | None = None, source_text: str | None = None,
              footnote: str | None = None):
    """Apply headline/subtitle/source to a Plotly figure in the house layout."""
    fig.update_layout(title={"text": headline, "subtitle": {"text": subtitle or ""}})
    notes = "<br>".join(x for x in (footnote, source_text) if x)
    if notes:
        f = _role("footnote")
        fig.add_annotation(text=notes, xref="paper", yref="paper", x=0, y=-0.12, xanchor="left", yanchor="top",
                           showarrow=False, align="left", font={"size": f["size_px"], "color": f["hex"]})
        fig.update_layout(margin={"b": 96})
    return fig


def pl_highlight(labels: Iterable, focus=None, accent=None, base: str | None = None) -> list[str]:
    return highlight(labels, focus, accent, base)


from .lint import Finding, LintError, lint  # noqa: E402  (needs the names above)

__all__ = [
    "TOKENS", "FONT", "CATEGORICAL", "SEQUENTIAL", "DIVERGING", "colors", "extended",
    "use", "register_fonts", "highlight", "categorical", "sequential_cmap", "diverging_cmap", "text_on", "signed", "rgba",
    "MINUS", "halo", "titles", "source", "layout", "label_bars", "label_line_ends", "callout", "shade_period", "clean_axes", "save",
    "plotly_template", "pl_finish", "pl_highlight", "lint", "Finding", "LintError",
]
