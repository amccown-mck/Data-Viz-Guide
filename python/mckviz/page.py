"""The options page: several charts of the same data on one self-contained HTML page, for a group deciding how to
show it. Each option states the question it answers, how to read it, its strength and its trade-off.

    mv.options_page(
        "out/automation-options.html",
        title="GenAI exposure by role: four ways to show it",
        lede="Four views of the same data. Each answers a different question; use one or combine them.",
        findings=[("About a third of the work is exposed (32%)", "weighted by headcount."), ...],
        options=[mv.Option(fig, name="Ranked by exposure", question="Which roles are most exposed?",
                           how_to_read="...", strength="...", tradeoff="..."), ...],
        notes={"GenAI exposure": "...", "Data": "..."},
        source="Source: Synthetic data for illustration only",
        label="Internal · For leadership discussion")

Everything is inside the one file (the charts as PNG, Libre Franklin, styles from the tokens), so it can be emailed
or put on SharePoint and opened offline. `mv.page_pdf(path)` writes the same page as a PDF where weasyprint is
installed (Copilot's sandbox). "Save as PDF" prints one option per landscape page, and each chart has
Download and Copy buttons for PowerPoint. Pass matplotlib figures built with mv.titles / mv.source: the page takes
each option's headline from its figure and lays the figure out the way mv.save does.
"""
from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import TOKENS, _find_fonts, colors, layout, working_path

_C = TOKENS["color"]
_FONT_WEIGHTS = {"Light": 300, "Regular": 400, "SemiBold": 600, "Bold": 700}
_DPI = 200          # about 2,000 px wide for a 10 in figure: sharp on a slide, light enough to email


@dataclass
class Option:
    """One way to show the data. `chart` is a matplotlib Figure (preferred) or a path to a PNG.

    `headline` defaults to the figure's mv.titles headline; `alt` defaults to the headline (give the key numbers).
    """
    chart: Any
    name: str
    question: str
    how_to_read: str
    strength: str
    tradeoff: str
    headline: str | None = None
    alt: str | None = None


def _png(chart: Any) -> bytes:
    if isinstance(chart, (str, Path)):
        return Path(chart).read_bytes()
    layout(chart)
    buf = io.BytesIO()
    # canvas.print_figure is what Figure.savefig calls; going to it directly skips sandboxes that patch savefig.
    chart.canvas.print_figure(buf, format="png", dpi=_DPI)
    return buf.getvalue()


def _headline(opt: Option) -> str:
    if opt.headline:
        return opt.headline
    head = getattr(opt.chart, "_mck", {}).get("head")
    if head is None:
        raise ValueError(f"option {opt.name!r}: pass headline=, or a figure with mv.titles")
    return " ".join(head.get_text().split())


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _font_faces() -> str:
    folder = _find_fonts()
    faces = []
    for name, weight in _FONT_WEIGHTS.items():
        ttf = folder / f"LibreFranklin-{name}.ttf" if folder else None
        if ttf and ttf.exists():
            data = base64.b64encode(ttf.read_bytes()).decode("ascii")
            faces.append(f"@font-face {{ font-family: 'Libre Franklin'; font-style: normal; font-weight: {weight}; "
                         f"font-display: swap; src: url(data:font/ttf;base64,{data}) format('truetype'); }}")
    return "\n".join(faces)


def _css() -> str:
    tokens = {
        "headline": colors.headline, "text": colors.text, "muted": colors.text_muted,
        "inverse": _C["text"]["inverse"]["value"], "surface": _C["surface"]["default"]["value"],
        "subtle": colors.surface_subtle, "grid": colors.grid, "focus": colors.focus, "accent": colors.accent,
    }
    root = "\n".join(f"  --{k}: {v};" for k, v in tokens.items())
    return f""":root {{
{root}
  --font: 'Libre Franklin', 'Franklin Gothic Book', Arial, Helvetica, sans-serif;
}}
body {{ font-family: var(--font); color: var(--text); background: var(--surface); max-width: 1180px; margin: 0 auto;
       padding: 32px 16px 64px; line-height: 1.5; }}
h1 {{ color: var(--headline); font-weight: 700; margin: 0 0 8px; line-height: 1.2; }}
h2 {{ color: var(--headline); font-size: 20px; font-weight: 700; margin: 0 0 4px; }}
h3 {{ color: var(--headline); font-size: 15px; font-weight: 700; margin: 0 0 8px; }}
a {{ color: var(--focus); }}
.label {{ font-size: 12px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
          margin: 0 0 12px; }}
.lede {{ max-width: 820px; font-size: 17px; }}
.box {{ background: var(--subtle); padding: 20px 24px; margin: 24px 0; }}
.box dl {{ display: grid; grid-template-columns: 200px 1fr; gap: 8px 20px; margin: 0; }}
.box dt {{ font-weight: 700; color: var(--headline); }}
.box dd {{ margin: 0; }}
.box p {{ margin: 0; font-size: 17px; }}
.key ol {{ margin: 0; padding-left: 22px; font-size: 17px; }}
.key li {{ margin: 6px 0; }}
.key b, .box p b {{ color: var(--headline); }}
table.glance {{ border-collapse: collapse; width: 100%; font-size: 15px; margin: 8px 0; }}
.glance td {{ border-bottom: 1px solid var(--grid); padding: 8px 12px 8px 0; vertical-align: top; }}
.glance td:nth-child(2) {{ white-space: nowrap; }}
.glance .num {{ width: 24px; color: var(--muted); }}
.option {{ border-top: 1px solid var(--grid); padding: 32px 0 12px; }}
.answers {{ color: var(--muted); margin: 0 0 14px; }}
.badge {{ display: inline-block; margin-left: 10px; padding: 2px 8px; font-size: 12px; font-weight: 700;
          letter-spacing: .04em; text-transform: uppercase; vertical-align: middle; color: var(--inverse);
          background: var(--focus); }}
img {{ width: 100%; height: auto; border: 1px solid var(--grid); }}
.notes {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px 28px; margin: 14px 0 0; font-size: 14px; }}
.notes dt {{ color: var(--headline); font-size: 12px; font-weight: 700; text-transform: uppercase;
             letter-spacing: .04em; margin-bottom: 2px; }}
.notes dd {{ margin: 0; }}
footer {{ border-top: 1px solid var(--grid); margin-top: 24px; padding-top: 12px; font-size: 13px; color: var(--muted); }}
.toolbar {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 4px 0 8px; }}
.toolbar .hint {{ font-size: 13px; color: var(--muted); }}
button {{ font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; padding: 8px 14px;
          border: 1px solid var(--focus); background: var(--surface); color: var(--focus); }}
button:hover {{ background: var(--subtle); }}
button.primary {{ background: var(--focus); color: var(--inverse); }}
button.primary:hover {{ background: var(--accent); }}
button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.actions {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0 0; }}
.status {{ font-size: 13px; color: var(--muted); }}
@media print {{
  @page {{ size: letter landscape; margin: 0.45in; }}
  body {{ max-width: none; padding: 0; font-size: 12px; }}
  .toolbar, .actions {{ display: none; }}
  .box, .glance td, .badge {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  a {{ color: inherit; text-decoration: none; }}
  .option {{ break-before: page; break-inside: avoid; border-top: 0; padding-top: 0; }}
  .option img {{ max-height: 6.1in; width: auto; max-width: 100%; display: block; margin: 0 auto; }}
  .notes {{ margin-top: 8px; font-size: 11px; }}
  .definitions {{ break-before: page; }}
}}
@media (max-width: 700px) {{
  .notes {{ grid-template-columns: 1fr; }}
  .box dl {{ grid-template-columns: 1fr; gap: 2px; }}
  .box dd {{ margin-bottom: 10px; }}
  .glance td:nth-child(2) {{ white-space: normal; }}
}}"""


_SCRIPT = """function chartImage(btn) { return btn.closest("section").querySelector("img"); }
function say(btn, text) {
  var s = btn.parentNode.querySelector(".status");
  s.textContent = text;
  clearTimeout(s._t);
  s._t = setTimeout(function () { s.textContent = ""; }, 4000);
}
function downloadChart(btn) {
  var a = document.createElement("a");
  a.href = chartImage(btn).src;
  a.download = btn.dataset.name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  say(btn, "Downloaded " + btn.dataset.name);
}
async function copyChart(btn) {
  try {
    var blob = await (await fetch(chartImage(btn).src)).blob();
    await navigator.clipboard.write([new ClipboardItem({"image/png": blob})]);
    say(btn, "Copied. Paste into PowerPoint with Ctrl+V.");
  } catch (err) {
    say(btn, "Copying isn't available in this browser. Use Download instead.");
  }
}"""


def _finding(item) -> str:
    if isinstance(item, str):
        return f"<li>{escape(item)}</li>"
    lead, rest = item
    return f"<li><b>{escape(lead)}:</b> {escape(rest)}</li>"


def options_page(path: str | Path, title: str, options: Sequence[Option], *, lede: str | None = None,
                 findings: Sequence[str | tuple[str, str]] = (), recommendation: str | None = None,
                 lead: int | None = None, notes: Mapping[str, str] | None = None, source: str | None = None,
                 label: str | None = None) -> Path:
    """Write the options page to `path` (.html) and return the path. In Copilot, write it to /tmp, make its PDF
    (page_pdf) and hand both over with mv.deliver; a path in /mnt/data is refused (mv.working_path).

    title           the page title, e.g. "GenAI exposure by role: four ways to show it"
    options         the Option list, in the order to read them (2 to 8)
    lede            one or two sentences under the title
    findings        "What the data shows": short strings or (bold lead, rest) pairs, computed from the data
    recommendation  optional "Where to start" text, for when the user asked which option to lead with
    lead            optional 1-based number of the option to badge "Suggested lead" (goes with recommendation)
    notes           "Definitions and data notes": term -> text (definitions, exclusions, suppressed groups)
    source          the source line for the footer ("Source: system, as of date; population")
    label           optional line above the title, e.g. "Confidential · McKesson workforce data · Internal use"
    """
    if not 2 <= len(options) <= 8:
        raise ValueError(f"an options page needs 2 to 8 options, got {len(options)}")
    if lead is not None and not 1 <= lead <= len(options):
        raise ValueError(f"lead={lead} is not an option number (1 to {len(options)})")
    path = working_path(path, "the options page")
    stem = _slug(path.stem) or "chart"
    heads = [_headline(o) for o in options]

    parts = []
    if label:
        parts.append(f'<p class="label">{escape(label)}</p>')
    parts.append(f"<h1>{escape(title)}</h1>")
    if lede:
        parts.append(f'<p class="lede">{escape(lede)}</p>')
    parts.append('<div class="toolbar"><button type="button" class="primary" onclick="window.print()">Save as PDF'
                 '</button><span class="hint">In the print window, choose "Save as PDF" as the printer. Each chart '
                 'also has its own download and copy buttons for PowerPoint.</span></div>')
    if findings:
        parts.append('<div class="box key"><h3>What the data shows</h3><ol>'
                     + "".join(_finding(f) for f in findings) + "</ol></div>")
    if recommendation:
        parts.append(f'<div class="box"><h3>Where to start</h3><p>{escape(recommendation)}</p></div>')
    rows = "".join(f'<tr><td class="num">{i}</td><td><a href="#opt{i}">{escape(o.name)}</a></td>'
                   f"<td>{escape(h)}</td></tr>" for i, (o, h) in enumerate(zip(options, heads), 1))
    parts.append(f'<h3>At a glance</h3><table class="glance"><tbody>{rows}</tbody></table>')

    for i, (o, head) in enumerate(zip(options, heads), 1):
        png = base64.b64encode(_png(o.chart)).decode("ascii")
        badge = '<span class="badge">Suggested lead</span>' if lead == i else ""
        name = f"{stem}-{i}-{_slug(o.name)}.png"
        parts.append(
            f'<section class="option" id="opt{i}"><h2>{i} · {escape(o.name)}{badge}</h2>'
            f'<p class="answers">{escape(o.question)}</p>'
            f'<img src="data:image/png;base64,{png}" alt="{escape(o.alt or head)}">'
            f'<div class="actions"><button type="button" onclick="downloadChart(this)" data-name="{escape(name)}">'
            f'Download image (PNG)</button><button type="button" onclick="copyChart(this)">Copy image</button>'
            f'<span class="status" role="status"></span></div>'
            f'<dl class="notes"><div><dt>How to read it</dt><dd>{escape(o.how_to_read)}</dd></div>'
            f"<div><dt>Strength</dt><dd>{escape(o.strength)}</dd></div>"
            f"<div><dt>Trade-off</dt><dd>{escape(o.tradeoff)}</dd></div></dl></section>")

    if notes:
        items = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in notes.items())
        parts.append(f'<div class="box definitions"><h3>Definitions and data notes</h3><dl>{items}</dl></div>')
    if source:
        parts.append(f"<footer>{escape(source)}</footer>")

    html = (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{escape(title)}</title>\n'
            f"<style>\n{_font_faces()}\n{_css()}\n</style>\n</head>\n<body>\n" + "\n".join(parts)
            + f"\n<script>\n{_SCRIPT}\n</script>\n</body>\n</html>\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8", newline="\n")
    return path


def page_pdf(path: str | Path) -> Path | None:
    """Print an options page to a PDF beside it (one option per landscape page) and return its path.

    Copilot opens a linked .html in the OneDrive viewer, where "Open in app" fails until the file is downloaded; a PDF
    opens there directly and can be forwarded as it is. Hand back the PDF to read and share, and the .html for the
    Download and Copy buttons. Uses weasyprint (in Copilot's sandbox); returns None where it isn't installed or its
    native libraries are missing (most Windows machines), so callers can fall back to the page's Save as PDF button.
    """
    path = working_path(path, "the options page")             # its PDF goes beside it: both in /tmp, then deliver
    try:
        from weasyprint import HTML
    except Exception:  # noqa: BLE001  (ImportError, or OSError when Pango/GTK is missing)
        return None
    pdf = path.with_suffix(".pdf")
    try:
        HTML(filename=str(path)).write_pdf(str(pdf))
    except Exception as exc:  # noqa: BLE001  (the .html still works: hand it back with its Save as PDF button)
        import warnings

        warnings.warn(f"page_pdf: weasyprint could not print {path.name}: {exc}", stacklevel=2)
        return None
    return pdf
