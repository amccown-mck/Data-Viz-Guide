"""Build the browsable guide and its 16:9 PDF from guide/pages/*.html.

    python tools/build_guide.py            -> dist/guide/*.html + dist/guide/McKesson-DataViz-Guide.pdf
    python tools/build_guide.py --no-pdf   -> HTML only (no browser needed)

Pages are HTML fragments made of <section class="spread"> blocks. Placeholders:
    {{exhibit:name}}       inline SVG from guide/exhibits.py (add |min to keep it readable on phones: scrolls sideways)
    {{text:key}}           a number or sentence computed from the example data (exhibits.TEXT)
    {{html:key}}           a token-driven snippet: swatches, role tables, type specimen (exhibits.HTML)
    {{folio}}              the running footer with the page number
Run tokens/build.py first after a token change; the guide reads colors from dist/web/mck-viz.css.
"""
from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "guide"
OUT = ROOT / "dist" / "guide"
PDF = OUT / "McKesson-DataViz-Guide.pdf"
sys.path[:0] = [str(SRC), str(ROOT / "tools")]

# (file stem, nav label, folio section). Order = reading order = PDF order.
PAGES = [
    ("index", "Overview", "Overview"),
    ("fundamentals", "Fundamentals", "Fundamentals"),
    ("magnitude", "Magnitude", "Magnitude"),
    ("part-to-whole", "Part-to-whole", "Part-to-whole"),
    ("change-over-time", "Change over time", "Change over time"),
    ("geo", "Geo-spatial", "Geo-spatial"),
    ("single-number", "Single number", "Single number"),
    ("formats", "Formats", "Formats"),
    ("toolkit", "Toolkit", "Toolkit"),
]
# Sections planned but not written yet: shown in the nav, greyed out.
COMING = ["Ranking", "Distribution", "Correlation", "Flows"]

LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="mck-viz.css">
<link rel="stylesheet" href="guide.css">
</head>
<body>
{topbar}<main>
{body}
</main>
</body>
</html>
"""


def topbar(active: str | None) -> str:
    links = "".join(
        f'<a href="{stem}.html"{" aria-current=page" if stem == active else ""}>{label}</a>' for stem, label, _ in PAGES)
    soon = "".join(f'<span title="Coming next">{s}</span>' for s in COMING)
    return (f'<header class="topbar"><a class="brand" href="index.html"><b>McKesson</b> <span>Data Visualization Guide</span></a>'
            f'<nav aria-label="Sections">{links}{soon}</nav><a class="pdf" href="{PDF.name}">PDF</a></header>\n')


def render(stem: str, section: str, svgs: dict, text: dict, snippets: dict, used: set, page_no: list[int]) -> str:
    src = (SRC / "pages" / f"{stem}.html").read_text(encoding="utf-8")

    def exhibit(m):
        name, opt = m.group(1), m.group(2)
        if name not in svgs:
            sys.exit(f"{stem}.html: unknown exhibit '{name}'")
        used.add(name)
        return f'<div class="ex-wrap{" min" if opt == "min" else ""}">{svgs[name]}</div>'

    def txt(m):
        if m.group(1) not in text:
            sys.exit(f"{stem}.html: unknown text key '{m.group(1)}'")
        return html.escape(text[m.group(1)], quote=False)

    def folio(_):
        page_no[0] += 1
        return (f'<div class="folio" aria-hidden="true"><span>McKesson Data Visualization Guide</span><span>{section}</span>'
                f'<span class="n">{page_no[0]}</span></div>')

    out = re.sub(r"\{\{exhibit:([\w-]+)(?:\|(\w+))?\}\}", exhibit, src)
    out = re.sub(r"\{\{text:(\w+)\}\}", txt, out)
    out = re.sub(r"\{\{html:(\w+)\}\}", lambda m: snippets[m.group(1)], out)
    out = re.sub(r"\{\{folio\}\}", folio, out)
    left = re.findall(r"\{\{[^}]*\}\}", out)
    if left:
        sys.exit(f"{stem}.html: unknown placeholder(s) {left}")
    return out


def main() -> None:
    import exhibits

    OUT.mkdir(parents=True, exist_ok=True)
    svgs = exhibits.render_all()
    used: set[str] = set()
    page_no = [0]
    bodies = []
    for stem, label, section in PAGES:
        body = render(stem, section, svgs, exhibits.TEXT, exhibits.HTML, used, page_no)
        bodies.append(body)
        title = "McKesson Data Visualization Guide" + ("" if stem == "index" else f": {label}")
        (OUT / f"{stem}.html").write_text(LAYOUT.format(title=title, topbar=topbar(stem), body=body), encoding="utf-8")
        print(f"wrote {(OUT / f'{stem}.html').relative_to(ROOT)}")
    (OUT / "print.html").write_text(
        LAYOUT.format(title="McKesson Data Visualization Guide", topbar="", body="\n".join(bodies)), encoding="utf-8")

    shutil.copy2(SRC / "guide.css", OUT / "guide.css")
    shutil.copy2(ROOT / "dist" / "web" / "mck-viz.css", OUT / "mck-viz.css")
    (OUT / "fonts").mkdir(exist_ok=True)
    for w in ("Light", "Regular", "Medium", "SemiBold", "Bold", "Italic"):
        shutil.copy2(ROOT / "fonts" / "LibreFranklin" / f"LibreFranklin-{w}.ttf", OUT / "fonts")
    shutil.copy2(ROOT / "fonts" / "LibreFranklin" / "OFL.txt", OUT / "fonts")

    (OUT / "img").mkdir(exist_ok=True)                     # thumbnails of the one-page PDFs for the Toolkit page
    try:
        import pymupdf
        for pdf in sorted((ROOT / "dist" / "print").glob("*.pdf")):
            pymupdf.open(pdf)[0].get_pixmap(dpi=72).save(OUT / "img" / f"{pdf.stem}.png")
    except ImportError:
        print("  note: pymupdf not installed; Toolkit thumbnails not refreshed")

    unused = sorted(set(svgs) - used)
    if unused:
        print(f"  note: exhibits not used on any page: {', '.join(unused)}")
    print(f"{page_no[0]} spreads, {len(used)} exhibits")
    if "--no-pdf" not in sys.argv:
        print_pdf(page_no[0])


OVERFLOW_JS = """<script>
document.fonts.ready.then(() => {
  const bad = [];
  document.querySelectorAll('.spread').forEach((s, i) => {
    s.style.height = '720px'; s.style.overflow = 'hidden';
    const top = s.getBoundingClientRect().top, limit = top + 720 - 34;   // keep clear of the folio
    for (const el of s.querySelectorAll('.rail > *, .stage > *, .inner > *')) {
      const r = el.getBoundingClientRect();
      if (r.bottom > limit + 0.5 || r.top < top - 0.5)
        bad.push((i + 1) + ':' + (el.parentElement.className.split(' ')[0]) + '>' + el.tagName.toLowerCase() +
                 ':' + Math.round(Math.max(r.bottom - limit, top - r.top)) + 'px');
    }
  });
  document.body.setAttribute('data-overflow', bad.join(' '));
});
</script>"""


def check_overflow(exe: str) -> None:
    """Load print.html at 1280 px and list any spread whose rail or stage is taller than 720 px."""
    probe = OUT / "_overflow.html"
    probe.write_text((OUT / "print.html").read_text(encoding="utf-8").replace("</body>", OVERFLOW_JS + "</body>"),
                     encoding="utf-8")
    dom = subprocess.run([exe, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--window-size=1280,900",
                          "--virtual-time-budget=8000", "--dump-dom", probe.as_uri()],
                         check=True, capture_output=True, text=True, encoding="utf-8").stdout
    probe.unlink()
    m = re.search(r'data-overflow="([^"]*)"', dom)
    if m is None:
        print("  warning: overflow check did not run")
    elif m.group(1):
        print(f"  warning: content taller than the 16:9 page (spread:element:excess): {m.group(1)}")
    else:
        print("  every spread fits its 16:9 page")


def print_pdf(expected: int) -> None:
    from build_print import _page_count, browser

    check_overflow(browser())
    subprocess.run([browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=8000", f"--print-to-pdf={PDF}", (OUT / "print.html").as_uri()],
                   check=True, capture_output=True)
    pages = _page_count(PDF)
    print(f"wrote {PDF.relative_to(ROOT)} ({pages} pages)")
    if pages != expected:
        print(f"  warning: expected {expected} pages (one per spread); a spread is overflowing")


if __name__ == "__main__":
    main()
