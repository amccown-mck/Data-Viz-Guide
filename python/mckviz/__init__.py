"""mckviz - McKesson data-visualization helpers for matplotlib and Plotly.

    import mckviz as mv
    mv.use()                                   # fonts + matplotlib style + Plotly template "mck"
    colors = mv.highlight(df.job_family, focus="Pharmacy Ops")
    fig, ax = plt.subplots(); ax.barh(df.job_family, df.attrition, color=colors)
    mv.titles(fig, "Pharmacy Ops attrition is 2x the enterprise rate", "Voluntary attrition, FY26 (%)")
    mv.source(fig, "Source: Workday HCM; McKesson Workforce Innovation")
    mv.save(fig, "out/attrition.png")

All colors, sizes and fonts come from tokens/tokens.json (copied to _tokens.json by tokens/build.py). The Libre
Franklin fonts (SIL OFL) and the map data for mckviz.geo ship inside the package, so a plain `pip install` works.
"""
from __future__ import annotations

import json
import re
import warnings
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, Sequence

_HERE = Path(__file__).resolve().parent
__version__: str = (_HERE / "VERSION").read_text(encoding="utf-8").strip()
TOKENS: dict = json.loads((_HERE / "_tokens.json").read_text(encoding="utf-8"))
_C = TOKENS["color"]
_T = TOKENS["typography"]
_K = TOKENS["chart"]

FONT = _T["family"]["primary"]
CATEGORICAL: list[str] = _C["categorical"]["values"]            # series order, at most 6
FILL_TINTS: list[str] = _C["categorical"]["fill_tints"]         # light tints for large fills only, outside the order
SEQUENTIAL: dict[str, list[str]] = _C["sequential"]
DIVERGING: list[str] = _C["diverging"]["orange_blue"]["values"]
STEPS: list[str] = _C["steps"]["values"]            # ordered process stages (blue to green), not data magnitude
STATUS: dict[str, dict] = {k: v for k, v in _C["status"].items() if not k.startswith("$")}   # RAG: status only

colors = SimpleNamespace(
    **{k: t["value"] for k, t in TOKENS["brand"]["core"].items()},
    **{k: t["value"] for k, t in TOKENS["brand"]["core_2026"].items() if k != "text"},
    **{k: t["value"] for k, t in _C["chart"].items()},
    **{k: t["value"] for k, t in _C["semantic"].items()},
    text=_C["text"]["primary"]["value"],
    text_muted=_C["text"]["muted"]["value"],
    headline=_C["text"]["headline"]["value"],
    title=_C["text"]["title"]["value"],
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
    """The Libre Franklin folder: the copy inside the package first, then a repo-level fonts/LibreFranklin/."""
    if any((_HERE / "fonts").glob("LibreFranklin-*.ttf")):
        return _HERE / "fonts"
    for base in _HERE.parents:
        cand = base / "fonts" / "LibreFranklin"
        if any(cand.glob("LibreFranklin-*.ttf")):
            return cand
    return None


def register_fonts() -> bool:
    """Register the bundled Libre Franklin TTFs with matplotlib. Returns True if matplotlib can now find the font."""
    from matplotlib import font_manager as fm

    folder = _find_fonts()
    if not folder:
        return False
    for ttf in folder.glob("*.ttf"):
        try:
            fm.fontManager.addfont(str(ttf))
        except (OSError, RuntimeError, ValueError):
            continue
    return any(f.name == FONT for f in fm.fontManager.ttflist)


_FONT_WARNED = False


def use(plotly_default: bool = True) -> None:
    """Apply the McKesson style to matplotlib (and register/activate the Plotly template if Plotly is installed).

    Warns once if Libre Franklin can't be registered: charts then fall back to Franklin Gothic, Arial or DejaVu Sans,
    whose wider letters can make labels collide.
    """
    global _FONT_WARNED
    import matplotlib.pyplot as plt

    if not register_fonts() and not _FONT_WARNED:
        _FONT_WARNED = True
        warnings.warn(f"mckviz: could not register the {FONT} fonts (looked in {_HERE / 'fonts'}); charts will use a "
                      "fallback font. Reinstall mckviz, or install Libre Franklin on this machine.", stacklevel=2)
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
    """Color list aligned to `labels`: grey context, blue `focus`, navy `accent`.

    focus / accent may be a single label or a collection of labels. Use `base=colors.focus_light` to make
    everything light blue and only the accent navy (the 'uniform + accent' pattern).
    """
    def as_set(x):
        if x is None:
            return set()
        return {x} if isinstance(x, (str, int, float)) else set(x)

    f, a = as_set(focus), as_set(accent)
    default = base or colors.context
    return [colors.accent if lab in a else colors.focus if lab in f else default for lab in labels]


def categorical(n: int) -> list[str]:
    """First n categorical colors (blue, navy, bright blue, teal, mint, orange). Prefer <= 4; more than 6 raises:
    group the tail into 'Other' or use small multiples."""
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
_SCALES = {"K": 1e3, "M": 1e6, "B": 1e9}


def fmt_num(value, kind: str = "auto", decimals: int | None = None, sign: bool = False, prefix: str = "",
            suffix: str = "") -> str:
    """Format a number for a label, headline or table cell, house style.

    kind: "auto" (plain below 10,000, then K / M / B), "K", "M" or "B" (always that unit), "pct" (the value is
    already in percent: 19.94 -> "19.9%"; pass share * 100 for a fraction) or "plain" (thousands separators only).
    decimals: default 0 for plain numbers, 1 for percentages, and for K / M / B 1 below 10 (4.3B) and 0 above (12K).
    sign: an explicit + on positive values, for deltas. Negatives always get a true minus (U+2212), never a hyphen.
    prefix / suffix: units around the number: prefix="$" gives "$4.3B" and "\u2212$71M". None and NaN give an en dash.

        fmt_num(4_292_000_000, prefix="$")  -> "$4.3B"       fmt_num(12_480)        -> "12K"
        fmt_num(-71.4e6, "M", prefix="$")   -> "\u2212$71M"       fmt_num(19.94, "pct")  -> "19.9%"
        fmt_num(2.5, "pct", sign=True)      -> "+2.5%"       fmt_num(8_430)         -> "8,430"
    """
    if value is None or value != value:                           # None or NaN
        return "\u2013"
    v = float(value)
    kind = kind if kind in ("auto", "plain", "pct") else str(kind).upper()
    if kind not in ("auto", "plain", "pct", *_SCALES):
        raise ValueError(f"kind must be 'auto', 'plain', 'pct', 'K', 'M' or 'B', not {kind!r}")
    unit = ""
    if kind == "pct":
        d, unit = (1 if decimals is None else decimals), "%"
    elif kind == "plain" or (kind == "auto" and abs(v) < 1e4):
        d = 0 if decimals is None else decimals
    else:
        order = list(_SCALES)
        k = order.index(kind) if kind != "auto" else (2 if abs(v) >= 1e9 else 1 if abs(v) >= 1e6 else 0)
        while True:
            scaled = v / _SCALES[order[k]]
            d = (1 if abs(scaled) < 9.95 else 0) if decimals is None else decimals
            if kind == "auto" and k < 2 and round(abs(scaled), d) >= 1000:   # 999,960 -> "1.0M", not "1,000K"
                k += 1
                continue
            break
        v, unit = scaled, order[k]
    body = f"{abs(v):,.{d}f}"
    if float(body.replace(",", "")) == 0:
        return f"{prefix}{body}{unit}{suffix}"
    return ("+" if v > 0 and sign else MINUS if v < 0 else "") + f"{prefix}{body}{unit}{suffix}"


def suppress_small(df, n_col: str, min_n: int = 10, other_label: str | None = "Other", group_cols=None,
                   by=None, sum_cols=(), unit: str = "people"):
    """Keep every group under `min_n` out of a chart: merge the small groups into one `other_label` row, or drop them.

    df: one row per group, with its head count in `n_col`. Returns (frame, footnote); the footnote is "" when nothing
    was changed, else a sentence for mv.source(..., footnote=...). Run it before plotting and before computing the
    headline numbers.

    group_cols: the column(s) that name a group; they read `other_label` on the merged row. Default: every non-numeric
        column not in `by`.
    by: optional column(s) to merge within (e.g. "quarter": small job families are merged per quarter).
    sum_cols: numeric columns that are counts (leavers, hires) and are summed. Every other numeric column is treated as
        a rate or average and combined as an n-weighted mean, which is right for %, ratios and means.
    other_label=None drops the small groups. A merged row that is itself still under `min_n` is dropped too. If the data
    already has an `other_label` row, the small groups are merged into it.

    Suppressing one small group still lets a reader subtract it from a shown total; when totals are shown, merge at least
    two groups (or suppress a second one) so no single value can be backed out.
    """
    import pandas as pd

    if n_col not in df.columns:
        raise KeyError(f"suppress_small: no column {n_col!r}")
    by = [by] if isinstance(by, str) else list(by or [])
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and c not in by]
    if group_cols is None:
        group_cols = [c for c in df.columns if c not in numeric and c not in by]
    group_cols = [group_cols] if isinstance(group_cols, str) else list(group_cols)
    sums = {n_col, *([sum_cols] if isinstance(sum_cols, str) else sum_cols)}
    small = df[n_col] < min_n
    if not small.any():
        return df.reset_index(drop=True), ""

    is_other = (df[group_cols[0]] == other_label) if (group_cols and other_label is not None) else pd.Series(False, df.index)
    keep = df[~small & ~is_other]
    n_small = int((small & ~is_other).sum())
    dropped = merged = 0
    rows = []
    if other_label is not None:
        pool = df[small | is_other]
        parts = pool.groupby(by, sort=False, dropna=False) if by else [((), pool)]
        for _, part in parts:
            n = part[n_col].sum()
            k = int(((part[n_col] < min_n) & ~is_other[part.index]).sum())   # small groups, not the old Other row
            if n < min_n:
                dropped += k
                continue
            merged += k
            row = {c: part[c].iloc[0] for c in df.columns}
            for c in group_cols:
                row[c] = other_label
            for c in numeric:
                row[c] = part[c].sum() if c in sums else (part[c] * part[n_col]).sum() / n
            rows.append(row)
    else:
        dropped = n_small
    out = pd.concat([keep, pd.DataFrame(rows, columns=df.columns)], ignore_index=True) if rows else keep
    out = out.astype({c: df[c].dtype for c in sums if c in df.columns}, errors="ignore").reset_index(drop=True)

    def groups(k):
        return f"{k} group{'s' if k != 1 else ''}"
    notes = []
    if merged:
        notes.append(f"{groups(merged)} with fewer than {min_n} {unit} merged into \"{other_label}\"")
    if dropped:
        notes.append(f"{groups(dropped)} with fewer than {min_n} {unit} not shown")
    note = "; ".join(notes)
    return out, note[0].upper() + note[1:] + "."


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
                    fontweight=h["weight"], color="white" if dark else h["hex"], linespacing=1.15)
    sub = None
    if subtitle:
        sub = fig.text(0, 1, textwrap.fill(subtitle, int(max_chars * hsize / ssize)), ha="left", va="top",
                       fontsize=ssize, color="white" if dark else s["hex"], linespacing=1.2)
    fig._mck = {**getattr(fig, "_mck", {}), "head": head, "sub": sub}


def source(fig, text: str, footnote: str | None = None, dark: bool = False) -> None:
    """Footnote (optional) and 'Source:' line, bottom-left."""
    f = _role("footnote")
    lines = ([footnote] if footnote else []) + [text]
    old = getattr(fig, "_mck", {}).get("foot")
    if old is not None:                                       # called again: replace, don't stack a second line
        old.remove()
    foot = fig.text(0, 0, "\n".join(lines), ha="left", va="top", fontsize=f["size_pt"],
                    color="white" if dark else f["hex"], fontweight=f["weight"], linespacing=1.35)
    fig._mck = {**getattr(fig, "_mck", {}), "foot": foot, "foot_lines": lines}


def _fit_lines(fig, text_artist, lines: list[str], width_px: float) -> None:
    """Wrap each line so the text block is no wider than width_px. An unwrapped footnote wider than the figure makes
    savefig's tight bounding box widen the whole image, which shrinks the chart inside it."""
    import textwrap

    r = fig.canvas.get_renderer()
    out = []
    for line in lines:
        chars = len(line)
        while True:
            text_artist.set_text("\n".join(textwrap.wrap(line, chars, break_on_hyphens=False)) or line)
            if text_artist.get_window_extent(r).width <= width_px or chars <= 20:
                break
            chars = int(chars * 0.92)
        out.append(text_artist.get_text())
    text_artist.set_text("\n".join(out))


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
        if fur.get("foot_lines"):                             # no wider than the plot and the headline
            right = max([b.x1 for b in ax_boxes()] + [box(fur[k]).x1 for k in ("head", "sub") if fur.get(k)])
            _fit_lines(fig, fur["foot"], fur["foot_lines"], 0.97 * (right - left) * fig.bbox.width)
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


def label_line_ends(ax, lines=None, fmt: str | None = None, dx: float = 6, min_gap: float | None = None) -> None:
    """Direct labels at the right end of each line, colored like the line (replaces the legend).

    Labels that would collide are nudged apart vertically (at least `min_gap` points between centers; default
    1.25 x the label size). Call it after setting the axis limits.
    """
    lab = _role("label")
    size = lab["size_pt"] - 1
    items = []
    for ln in lines or ax.get_lines():
        if ln.get_label().startswith("_"):
            continue
        x, y = ln.get_xdata()[-1], ln.get_ydata()[-1]
        text = ln.get_label() if not fmt else f"{ln.get_label()} {fmt.format(y)}"
        items.append((x, y, text, ln.get_color()))
    if not items:
        return
    ax.autoscale_view()                       # apply pending autoscaling so data -> display is final
    to_pt = 72 / ax.figure.dpi
    ys = [ax.transData.transform((x, y))[1] * to_pt for x, y, _, _ in items]
    order = sorted(range(len(items)), key=lambda i: ys[i])
    placed = [ys[i] for i in order]
    gap = min_gap or size * 1.25
    for k in range(1, len(placed)):
        placed[k] = max(placed[k], placed[k - 1] + gap)
    excess = placed[-1] - (ax.get_window_extent().y1 * to_pt + gap / 2)      # don't push past the top
    if excess > 0:
        placed = [p - excess for p in placed]
        for k in range(len(placed) - 2, -1, -1):
            placed[k] = min(placed[k], placed[k + 1] - gap)
    limit = gap * len(items)                  # a label never moves more than the stack it belongs to
    for k, i in enumerate(order):
        x, y, text, color = items[i]
        ax.annotate(text, (x, y), xytext=(dx, max(-limit, min(limit, placed[k] - ys[i]))), textcoords="offset points", va="center",
                    fontsize=size, color=color, fontweight="semibold", annotation_clip=False, path_effects=halo())


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


def working_path(path: str | Path, what: str = "the file") -> Path:
    """`path`, checked: outside the delivery folder. Where /mnt/data exists (Copilot, whose working directory it is,
    so a bare "chart.png" lands there too), writing into it is refused with what to do instead: every write there,
    even after a delete, becomes another copy in the user's OneDrive (Copilot > Created)."""
    path = Path(path)
    if DELIVER_DIR.is_dir() and (path.resolve() == DELIVER_DIR.resolve() or
                                 DELIVER_DIR.resolve() in path.resolve().parents):
        raise ValueError(f"save {what} to /tmp first (/tmp/{path.name}), check it there (mv.look), then "
                         f"mv.deliver('/tmp/{path.name}') hands it to the user once: every write to {DELIVER_DIR} "
                         "becomes another copy in their OneDrive")
    return path


def save(fig, path: str | Path, **kw) -> Path:
    """Lay out headline/subtitle/source, then save (PNG for slides, SVG/PDF for print). In Copilot, save to /tmp and
    hand the file over with deliver(); a path in /mnt/data is refused (working_path)."""
    path = working_path(path, "the chart")
    layout(fig)
    path.parent.mkdir(parents=True, exist_ok=True)
    if kw.get("transparent"):
        fig.savefig(path, **kw)
    else:
        # What Figure.savefig calls. Going to it directly skips sandboxes that patch savefig, such as Copilot's, which
        # writes a JSON chart spec beside the PNG and then shows a bare interactive re-plot instead of this image.
        fig.canvas.print_figure(path, **kw)
    return path


DELIVER_DIR = Path("/mnt/data")       # Copilot: every file written here syncs to the user's OneDrive as a new copy


def _signature(path: Path) -> str:
    """What a file holds, ignoring when it was built: for Office files (zips), the parts other than the document
    properties (created / modified times); for PDFs, the bytes without the creation and modification dates and the
    file ID; else the bytes. Rebuilding a file the same way gives the same signature."""
    import hashlib
    import io
    import zipfile

    def digest(data: bytes, h) -> None:
        if data[:2] == b"PK" and zipfile.is_zipfile(io.BytesIO(data)):
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for n in sorted(n for n in z.namelist() if not n.startswith("docProps/")):
                    h.update(n.encode() + b"\0")
                    digest(z.read(n), h)                       # a chart's embedded workbook has its own dates
        elif data.startswith(b"%PDF"):
            h.update(re.sub(rb"/(CreationDate|ModDate)\s*\([^)]*\)|/ID\s*\[[^\]]*\]", b"", data))
        else:
            h.update(data)

    h = hashlib.sha1()
    digest(path.read_bytes(), h)
    return h.hexdigest()


_VERSION_TAIL = re.compile(r"([ _.-]*(v\d+|rev\d*|final|draft|copy|new|fixed|updated|\(\d+\)|\d))+$", re.I)
_RUN = __import__("uuid").uuid4().hex    # this load of mckviz: mck_setup.py reloads it at the start of every script


def _deliverable(name: str) -> str:
    """What a file is, whatever version it says it is: "Attrition_Slide_v3.pptx" -> "attrition_slide.pptx"."""
    p = Path(name)
    return f"{_VERSION_TAIL.sub('', p.stem).lower()}{p.suffix.lower()}"


def _ledger(dest_dir: Path) -> Path:
    """Where deliver() records what it handed over in this chat: beside the working files, not in the delivery
    folder (a file written there would sync to the user's OneDrive)."""
    import hashlib
    import tempfile

    key = hashlib.sha1(str(dest_dir.resolve()).encode()).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / f".mckviz-delivered-{key}.json"


def _read_ledger(dest_dir: Path) -> dict:
    try:
        return json.loads(_ledger(dest_dir).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def deliver(*paths, to: str | Path | None = None, revision: str | None = None) -> Path | list[Path]:
    """Hand finished files to the user, as the last step: copy each one from the working folder (/tmp) into the
    delivery folder, /mnt/data in Copilot (it syncs to the user's OneDrive, Copilot > Created) or `to`. Every write
    there, even after a delete, becomes another copy in the user's OneDrive, so each deliverable goes there once:

    - Delivering the same file again does nothing (rebuilding it the same way isn't a change: build dates are
      ignored), so a rerun leaves no extra copy.
    - A second version of a deliverable already handed over in this chat ("deck.pptx", then "deck_v2.pptx", or a
      changed "deck.pptx") is refused: finish the checks in /tmp (mv.look) before delivering. When the user asks
      for a change, deliver it under a new name with `revision=` saying what they asked for.
    - Never cp, mv or rm in the delivery folder: use this.

        mv.save(fig, "/tmp/attrition.png"); mv.deliver("/tmp/attrition.png")      # then link sandbox:/mnt/data/...
        mv.deliver("/tmp/options.html", "/tmp/options.pdf")
        mv.deliver("/tmp/attrition_v2.pptx", revision="user asked for the enterprise rate as a line")

    Returns the delivered path (a list for several)."""
    import shutil

    dest_dir = Path(to) if to is not None else DELIVER_DIR
    if not dest_dir.is_dir():
        raise FileNotFoundError(f"no delivery folder {dest_dir}; pass to=")
    done = _read_ledger(dest_dir)
    out = []
    for p in paths:
        src = Path(p)
        if not src.is_file():
            raise FileNotFoundError(src)
        dest = dest_dir / src.name
        if src.resolve() == dest.resolve():
            raise ValueError(f"{src} is already in the delivery folder: build and check in /tmp, then deliver from "
                             "there")
        sig = _signature(src)
        what = _deliverable(src.name)
        earlier = done.get(what)
        if earlier and earlier["sig"] == sig or dest.exists() and _signature(dest) == sig:
            out.append(dest_dir / (earlier["name"] if earlier else dest.name))      # already delivered: a no-op
            continue
        if (earlier or dest.exists()) and not revision:
            raise FileExistsError(
                f"{earlier['name'] if earlier else dest.name} was already delivered in this chat, and every new file "
                f"in {dest_dir} is another copy in the user's OneDrive. Deliver each deliverable once: make every fix "
                "and check in /tmp (mv.look) first. If the user asked for a change, deliver it under a new name with "
                "revision='<what the user asked for>'.")
        if dest.exists():
            raise FileExistsError(f"{dest.name} is taken: deliver the revision under a new name (e.g. "
                                  f"{src.stem}-v2{src.suffix}); never delete or overwrite it there")
        shutil.copyfile(src, dest)
        done[what] = {"name": src.name, "sig": sig, "run": _RUN}
        out.append(dest)
    try:
        _ledger(dest_dir).write_text(json.dumps(done), encoding="utf-8")
    except OSError:
        pass
    return out[0] if len(out) == 1 else out


def clear_delivered(to: str | Path | None = None) -> list[Path]:
    """Take the files that deliver() handed over in an earlier run out of the delivery folder; scripts/mck_setup.py
    calls this at the start of every script. In Copilot they are already in the user's OneDrive by then, and stay
    there (with their links); but a file left in /mnt/data is uploaded again as "name 1.pptx", "name 2.pdf", ... after
    later code runs (decks, PDFs and HTML pages all came back). Files delivered in this run, and files deliver()
    didn't write, are left alone. Returns what it took out."""
    dest_dir = Path(to) if to is not None else DELIVER_DIR
    if not dest_dir.is_dir():
        return []
    cleared = []
    for entry in _read_ledger(dest_dir).values():
        f = dest_dir / entry["name"]
        if entry.get("run") != _RUN and f.is_file():
            f.unlink()
            cleared.append(f)
    return cleared


def look(path: str | Path, width: int = 900):
    """Show a render (a PNG in /tmp) in the notebook output so you can check it, without writing it to the
    delivery folder: copying a check image into /mnt/data to see it leaves a copy in the user's OneDrive."""
    from IPython.display import Image, display

    display(Image(filename=str(path), width=width))


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
from .charts import (STATUS_ORDER, bar, big, delta_label, diverging_bars, dot_plot, dumbbell, heat, hstack,  # noqa: E402
                     key_strip, kpi_card, kpi_row, label_points, line, multiples, rank_slope, ring, roadmap, sdot, small,
                     status, sankey, share_bar, status_column, status_key, story_order, strip, tracker, waterfall)
from .page import Option, options_page, page_pdf  # noqa: E402
from .chooser import suggest  # noqa: E402
from .table import Col, table  # noqa: E402


def __getattr__(name: str):
    """`mv.geo` and `mv.office` (native PowerPoint, needs python-pptx) import on first use (import mckviz.geo works
    too)."""
    if name in ("geo", "office"):
        import importlib

        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module 'mckviz' has no attribute {name!r}")


__all__ = [
    "__version__", "TOKENS", "FONT", "CATEGORICAL", "FILL_TINTS", "SEQUENTIAL", "DIVERGING", "STEPS", "STATUS", "colors", "extended",
    "use", "register_fonts", "highlight", "categorical", "sequential_cmap", "diverging_cmap", "text_on", "signed", "rgba",
    "fmt_num", "suppress_small",
    "MINUS", "halo", "titles", "source", "layout", "label_bars", "label_line_ends", "callout", "shade_period", "clean_axes", "save",
    "working_path", "deliver", "clear_delivered", "look", "plotly_template", "pl_finish", "pl_highlight", "lint", "Finding", "LintError",
    # chart builders (mckviz/charts.py)
    "bar", "story_order", "line", "share_bar", "strip", "dot_plot", "sankey",
    "waterfall", "hstack", "diverging_bars", "label_points", "dumbbell", "rank_slope", "heat", "key_strip", "big", "small", "ring", "kpi_card",
    "kpi_row", "delta_label", "sdot", "status", "status_key", "status_column", "tracker", "roadmap", "multiples",
    "STATUS_ORDER",
    # tables, the decision tree, options pages
    "table", "Col", "suggest", "Option", "options_page", "page_pdf",
]
