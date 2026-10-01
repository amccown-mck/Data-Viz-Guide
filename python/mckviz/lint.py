"""Check a finished matplotlib or Plotly figure against the house rules (docs/principles.md, docs/qa-checklist.md).

    import mckviz as mv
    findings = mv.lint(fig)                       # prints a report and returns the findings
    mv.lint(fig, strict=True)                     # raises if any rule at "error" level fails

For Plotly figures whose headline, subtitle and source live in HTML (the chart-card pattern), pass them in:
    mv.lint(fig, headline="...", subtitle="...", source="Source: ...")

Levels: error = breaks a rule; warn = probably wrong, check it; info = worth a look.
The lint can't judge whether the headline is *true* or the chart type fits the question: that is still a human check.
"""
from __future__ import annotations

import colorsys
import re
from dataclasses import dataclass
from typing import Iterable

LEVELS = ("error", "warn", "info")
MIN_FONT_PT = 7.0          # figures are drawn ~10 in wide and scaled up ~1.33x on a 13.33 in slide: 7 pt -> ~9 pt


@dataclass(frozen=True)
class Finding:
    level: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():5}  {self.rule}: {self.message}"


class LintError(AssertionError):
    pass


# ----------------------------------------------------------------------------------------------- color helpers
def _palette() -> set[str]:
    from . import TOKENS

    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", node):
            found.add(node.upper())

    walk(TOKENS)
    return found | {"#FFFFFF", "#000000"}


def _do_not_use() -> set[str]:
    """Hexes of brand families whose tokens say they are not used internally (e.g. amber)."""
    from . import TOKENS

    out: set[str] = set()
    for fam in TOKENS["brand"]["extended"].values():
        if isinstance(fam, dict) and "do not use" in str(fam.get("usage", "")).lower():
            out |= {v.upper() for k, v in fam.items() if k in ("light", "mid", "base", "dark") and v}
    return out


def _neutrals() -> set[str]:
    from . import colors as c

    return {x.upper() for x in (c.context, c.context_light, c.axis, c.grid, c.text, c.text_muted, c.surface_subtle,
                                getattr(c, "sand", c.context_light), "#FFFFFF")}


def _hex(color) -> str | None:
    """Any matplotlib/Plotly color spec -> '#RRGGBB' (alpha ignored), or None if transparent/unknown."""
    from matplotlib.colors import to_rgba

    if color is None:
        return None
    if isinstance(color, str):
        m = re.fullmatch(r"\s*rgba?\(([^)]*)\)\s*", color)
        if m:
            parts = [float(p) for p in m.group(1).split(",")]
            if len(parts) == 4 and parts[3] == 0:
                return None
            return "#{:02X}{:02X}{:02X}".format(*(int(round(p)) for p in parts[:3]))
    try:
        r, g, b, a = to_rgba(color)
    except (ValueError, TypeError):
        return None
    if a == 0:
        return None
    return "#{:02X}{:02X}{:02X}".format(*(int(round(v * 255)) for v in (r, g, b)))


def _rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _near(h: str, pool: Iterable[str], tol: float = 8.0) -> bool:
    r, g, b = _rgb(h)
    return any(((r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2) ** 0.5 <= tol for R, G, B in map(_rgb, pool))


def _is_neutral(h: str, neutrals: set[str]) -> bool:
    if _near(h, neutrals, 6):
        return True
    r, g, b = (v / 255 for v in _rgb(h))
    return colorsys.rgb_to_hsv(r, g, b)[1] < 0.12        # greys, sands, near-whites


def _color_findings(used: list[str]) -> list[Finding]:
    out: list[Finding] = []
    palette, neutrals = _palette(), _neutrals()
    off = sorted({h for h in used if not _near(h, palette)})
    if off:
        out.append(Finding("warn", "palette", f"colors not in tokens/tokens.json: {', '.join(off[:6])}"
                                              f"{' ...' if len(off) > 6 else ''} (use mv.colors / mv.CATEGORICAL)"))
    hues = sorted({h for h in used if not _is_neutral(h, neutrals)})
    # A sequential or diverging ramp is one encoding, not one category per step: count each ramp used once.
    from . import DIVERGING, SEQUENTIAL
    ramps = [set(map(str.upper, r)) for r in (*SEQUENTIAL.values(), DIVERGING)]
    in_ramp = [i for i, r in enumerate(ramps) if len({h for h in hues if h in r}) >= 3]
    ramp_colors = set().union(*(ramps[i] for i in in_ramp)) if in_ramp else set()
    categories = len([h for h in hues if h not in ramp_colors]) + len(in_ramp)
    if categories > 6:
        out.append(Finding("error", "max-6-colors", f"{categories} distinct colors; use at most 6 and grey the rest"))
    from . import STATUS
    status = {STATUS[k]["value"].upper() for k in ("on_track", "at_risk", "off_track")}
    is_status = len({h for h in hues if _near(h, status, 6)}) >= 2      # a tracker / roadmap using two RAG colors
    if is_status:
        out.append(Finding("info", "status-colors", "status (RAG) colors: only for status, never data series; pair each "
                                                    "color with a symbol and a word (mv.STATUS has both)"))
    has_red = has_green = False
    for h in hues:
        if is_status and _near(h, status, 6):
            continue
        hh, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in _rgb(h)))
        deg = hh * 360
        has_red |= (deg < 15 or deg > 345) and s > 0.4 and v > 0.3
        has_green |= 85 < deg < 150 and s > 0.35 and v > 0.3
    if has_red and has_green:
        out.append(Finding("error", "no-red-green", "red and green are both used; use blue vs. navy (orange only for negatives)"))
    banned = sorted({h for h in used if _near(h, _do_not_use(), 6) and not (is_status and _near(h, status, 6))})
    if banned:
        out.append(Finding("error", "do-not-use", f"{', '.join(banned)} is not used internally (amber family); "
                                                  "pick from mv.CATEGORICAL"))
    from . import colors as c
    if any(_near(h, {c.orange.upper()}, 6) for h in hues) and not any(i == len(ramps) - 1 for i in in_ramp):
        out.append(Finding("info", "orange-semantic", "orange appears: keep it for negatives / below target only, "
                                                      "never as a plain highlight (use navy, chart.accent)"))
    return out


def _headline_findings(headline: str | None, subtitle: str | None, source: str | None) -> list[Finding]:
    out: list[Finding] = []
    if not headline or not headline.strip():
        out.append(Finding("error", "headline", "no headline: add an insight sentence (mv.titles / mv.pl_finish)"))
    else:
        text = " ".join(headline.replace("<br>", " ").split())
        if len(text.split()) < 5:
            out.append(Finding("warn", "headline", f'"{text}" reads like a label; state the finding as a sentence'))
        if text.endswith("."):
            out.append(Finding("info", "headline", "drop the final period"))
        if not re.search(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|half|twice|double|triple|all|most|none|every)\b",
                         text, re.I):
            out.append(Finding("info", "headline", "no number in the headline; the best ones quantify the finding"))
        if len(text) > 140:
            out.append(Finding("warn", "headline", f"{len(text)} characters; keep it to about 2 lines"))
    if not subtitle or not subtitle.strip():
        out.append(Finding("error", "subtitle", "no subtitle: state metric, unit, scope and period"))
    elif not re.search(r"\(|\b(FY|Q[1-4]|20\d\d|19\d\d|month|year|weekly|annual)", subtitle, re.I):
        out.append(Finding("info", "subtitle", "subtitle has no unit in brackets or period; add metric, unit, scope, period"))
    if not source or "source:" not in source.lower():
        out.append(Finding("error", "source", 'no "Source:" line (mv.source / pl_finish(source_text=...))'))
    return out


# ----------------------------------------------------------------------------------------------- matplotlib
def _lint_matplotlib(fig, headline, subtitle, source) -> list[Finding]:
    from matplotlib.container import BarContainer
    from matplotlib.patches import Wedge
    from matplotlib.text import Text

    fur = getattr(fig, "_mck", {}) or {}
    head = headline or (fur["head"].get_text() if fur.get("head") is not None else None) \
        or (fig._suptitle.get_text() if getattr(fig, "_suptitle", None) else None)
    sub = subtitle or (fur["sub"].get_text() if fur.get("sub") is not None else None)
    src = source or (fur["foot"].get_text() if fur.get("foot") is not None else None)
    out = _headline_findings(head, sub, src)

    axes = [a for a in fig.axes if a.get_visible()]
    colorbar_axes = {a for a in axes if a.get_label() == "<colorbar>"}
    used: list[str] = []
    for ax in axes:
        if ax in colorbar_axes:
            continue
        if getattr(ax, "name", "") == "3d":
            out.append(Finding("error", "no-3d", "3D axes distort values; use a 2D chart"))
        for p in ax.patches:
            if p.get_visible() and p.get_fill():
                h = _hex(p.get_facecolor())
                if h:
                    used.append(h)
        for coll in ax.collections:
            for fc in (coll.get_facecolor() if len(coll.get_facecolor()) else []):
                h = _hex(fc)
                if h:
                    used.append(h)
        for ln in ax.get_lines():
            if ln.get_visible() and ln.get_linestyle() not in ("None", "none", ""):
                h = _hex(ln.get_color())
                if h:
                    used.append(h)

        # Bars: zero baseline, labels vs. value axis
        bars = [c for c in ax.containers if isinstance(c, BarContainer)]
        if bars:
            horizontal = getattr(bars[0], "orientation", "vertical") == "horizontal"
            rects = [r for c in bars for r in c]
            starts = [(r.get_x() if horizontal else r.get_y()) for r in rects]
            lo = (ax.get_xlim() if horizontal else ax.get_ylim())[0]
            floating = any(abs(s) > 1e-9 for s in starts)
            if lo > 1e-9 and not floating:
                out.append(Finding("error", "bars-from-zero", f"value axis starts at {lo:g}; bars must start at zero "
                                                              "(use a dot plot for clustered values)"))
            elif lo > 1e-9 and floating:
                out.append(Finding("warn", "bars-from-zero", f"value axis starts at {lo:g} (waterfall?): mark the break "
                                                             "on the totals and say so in a footnote"))
            labels = [t for t in ax.texts if t.get_text().strip()] + \
                     [c for c in ax.get_children() if type(c).__name__ == "Annotation" and c.get_text().strip()]
            value_ticks = ax.get_xticklabels() if horizontal else ax.get_yticklabels()
            ticks_on = ax.axison and any(t.get_visible() and t.get_text() for t in value_ticks)
            if len(labels) >= len(rects) and ticks_on:
                out.append(Finding("warn", "labels-or-axis", "bars carry value labels and a value axis; remove the axis "
                                                             "and gridlines"))
        wedges = [p for p in ax.patches if isinstance(p, Wedge)]
        if len(wedges) > 5:
            out.append(Finding("error", "pie-max-5", f"{len(wedges)} pie/donut segments; use ≤ 5 or a sorted bar"))
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            n = len(leg.get_texts())
            kind = "lines" if ax.get_lines() and not bars else "series"
            out.append(Finding("info" if kind == "series" else "warn", "direct-labels",
                               f"legend with {n} entries; label the {kind} directly where labels fit"))
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            if t.get_visible() and t.get_text() and t.get_rotation() not in (0, 360):
                out.append(Finding("warn", "no-rotated-labels", "rotated tick labels; use horizontal bars or "
                                                                "shorter labels"))
                break

    # Dual axes: two visible axes sharing a position, one a twin of the other
    for i, a in enumerate(axes):
        for b in axes[i + 1:]:
            if a.get_position().bounds == b.get_position().bounds and \
                    (a.get_shared_x_axes().joined(a, b) or a.get_shared_y_axes().joined(a, b)):
                out.append(Finding("warn", "no-dual-axis", "twin axes found; prefer two aligned charts or an index to 100"))

    small = sorted({round(t.get_fontsize(), 1) for t in fig.findobj(Text)
                    if t.get_visible() and t.get_text().strip() and t.get_fontsize() < MIN_FONT_PT})
    if small:
        out.append(Finding("warn", "min-text-size", f"text at {', '.join(map(str, small))} pt; keep ≥ {MIN_FONT_PT:g} pt "
                                                    "on a 10 in figure (≈ 9 pt on a slide)"))
    return out + _color_findings(used)


# ----------------------------------------------------------------------------------------------- Plotly
def _lint_plotly(fig, headline, subtitle, source) -> list[Finding]:
    lay = fig.layout
    head = headline or (lay.title.text if lay.title and lay.title.text else None)
    sub = subtitle or (lay.title.subtitle.text if lay.title and lay.title.subtitle and lay.title.subtitle.text else None)
    src = source or next((a.text for a in (lay.annotations or []) if a.text and "source:" in a.text.lower()), None)
    out = _headline_findings(head, sub, src)

    used: list[str] = []

    def collect(value):
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for v in value:
                collect(v)
        elif hasattr(value, "tolist"):
            collect(value.tolist())
        elif isinstance(value, str):
            h = _hex(value)
            if h:
                used.append(h)

    for tr in fig.data:
        for attr in ("marker", "line"):
            obj = getattr(tr, attr, None)
            if obj is not None and "color" in obj:
                collect(obj.color)
        if "fillcolor" in tr:
            collect(tr.fillcolor)
        if tr.type == "sankey":
            collect(tr.node.color)
            collect(tr.link.color)
    unset = [tr for tr in fig.data if tr.type in ("bar", "scatter") and not (tr.marker and tr.marker.color)
             and not (getattr(tr, "line", None) and tr.line.color)]
    if unset:
        cw = list(lay.colorway or (lay.template.layout.colorway if lay.template and lay.template.layout else []) or [])
        collect(cw[:len(unset)])

    bars = [tr for tr in fig.data if tr.type == "bar"]
    for tr in bars:
        horizontal = tr.orientation == "h"
        axis = lay.xaxis if horizontal else lay.yaxis
        rng = axis.range if axis is not None else None
        if rng and rng[0] is not None and rng[0] > 0 and not tr.base:
            out.append(Finding("error", "bars-from-zero", f"bar axis range starts at {rng[0]}; start at zero"))
    if bars and all(tr.text is not None for tr in bars):
        axis = lay.xaxis if bars[0].orientation == "h" else lay.yaxis
        if axis is None or axis.visible is not False:
            out.append(Finding("warn", "labels-or-axis", "bars carry text labels and a visible value axis; hide the axis"))
    if any(getattr(tr, "yaxis", None) == "y2" for tr in fig.data):
        out.append(Finding("warn", "no-dual-axis", "a trace uses a second y axis; prefer two aligned charts"))
    for tr in fig.data:
        if tr.type == "pie" and tr.labels is not None and len(tr.labels) > 5:
            out.append(Finding("error", "pie-max-5", f"{len(tr.labels)} pie/donut segments; use ≤ 5 or a sorted bar"))
    shown = [tr for tr in fig.data if tr.type not in ("pie", "sankey", "heatmap", "treemap")
             and getattr(tr, "showlegend", None) is not False]
    if len(shown) > 1 and lay.showlegend is not False:
        out.append(Finding("info", "direct-labels", f"legend with {len(shown)} series; label them directly where labels fit"))
    for ax_name in ("xaxis", "yaxis"):
        ax = getattr(lay, ax_name, None)
        if ax is not None and ax.tickangle not in (None, 0):
            out.append(Finding("warn", "no-rotated-labels", f"{ax_name} tick labels are rotated"))
    return out + _color_findings(used)


# ----------------------------------------------------------------------------------------------- entry point
def _print_safe(text: str) -> None:
    """Print findings even where stdout can't encode ≤, −, × (a Windows console or a pipe in CI)."""
    import sys
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(text.encode(enc, errors="replace").decode(enc, errors="replace"))


def lint(fig, *, headline: str | None = None, subtitle: str | None = None, source: str | None = None,
         strict: bool = False, quiet: bool = False) -> list[Finding]:
    """Lint a matplotlib Figure or a Plotly Figure against the house rules. Returns the findings (errors first)."""
    if type(fig).__module__.startswith("plotly"):
        findings = _lint_plotly(fig, headline, subtitle, source)
    else:
        fig.canvas.draw()                                   # resolve limits, tick labels and layout first
        findings = _lint_matplotlib(fig, headline, subtitle, source)
    findings = sorted(dict.fromkeys(findings), key=lambda f: LEVELS.index(f.level))
    if not quiet:
        _print_safe("\n".join(map(str, findings)) if findings else "lint: no findings")
    if strict and any(f.level == "error" for f in findings):
        raise LintError("; ".join(str(f) for f in findings if f.level == "error"))
    return findings
