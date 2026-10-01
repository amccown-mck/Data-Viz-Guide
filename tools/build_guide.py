"""Build the browsable guide, its 16:9 PDF, a standalone single-file HTML and the one-page PDFs from guide/pages/*.html.

    python tools/build_guide.py            -> dist/guide/*.html                      one page per section (in the repo)
                                              dist/guide/McKesson-DataViz-Guide.html  standalone: one file, works offline,
                                                                                      fonts and images inside; send it
                                              dist/guide/McKesson-DataViz-Guide.pdf   every spread, one 16:9 page each
                                              dist/print/chart-chooser.pdf, cheat-sheet.pdf   the one-pagers
    python tools/build_guide.py --no-pdf   -> HTML only (no browser needed)

Pages are HTML fragments made of <section class="spread" id="..."> blocks. Placeholders:
    {{exhibit:name}}       inline SVG from guide/exhibits.py (add |min to keep it readable on phones: scrolls sideways)
    {{text:key}}           a number or sentence computed from the example data (exhibits.TEXT)
    {{html:key}}           a token-driven snippet: swatches, role tables, type specimen (exhibits.HTML)
    {{link:spread-id}}     a link to any spread, resolved for each output (page.html#id, or #id in a single file)
    {{page:spread-id}}     that spread's page number in the PDF
    {{folio}}              the running footer with the page number
Run tokens/build.py first after a token change; the guide reads colors from dist/web/mck-viz.css.
Set CHROME=<path> if Chrome or Edge isn't found automatically.
"""
from __future__ import annotations

import base64
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "guide"
OUT = ROOT / "dist" / "guide"
PDF = OUT / "McKesson-DataViz-Guide.pdf"
STANDALONE = OUT / "McKesson-DataViz-Guide.html"
PRINT_OUT = ROOT / "dist" / "print"
REPO_URL = "https://github.com/amccown-mck/Data-Viz-Guide"   # kit files are linked here from the PDF and standalone file
sys.path[:0] = [str(SRC)]

# (file stem, nav label, folio section, kind). Order = reading order = PDF order.
# kind "section" appears in the section nav; "tool" pages get their own buttons in the top bar.
PAGES = [
    ("index", "Overview", "Overview", "section"),
    ("chooser", "Chart chooser", "Chart chooser", "tool"),
    ("fundamentals", "Fundamentals", "Fundamentals", "section"),
    ("formats", "Formats", "Formats", "section"),
    ("magnitude", "Magnitude", "Magnitude", "section"),
    ("part-to-whole", "Part-to-whole", "Part-to-whole", "section"),
    ("change-over-time", "Change over time", "Change over time", "section"),
    ("ranking", "Ranking", "Ranking", "section"),
    ("distribution", "Distribution", "Distribution", "section"),
    ("correlation", "Correlation", "Correlation", "section"),
    ("flows", "Flows", "Relationships and flows", "section"),
    ("geo", "Geo-spatial", "Geo-spatial", "section"),
    ("single-number", "Single number", "Single number", "section"),
    ("plans", "Plans and status", "Plans and status", "section"),
    ("cheat-sheet", "Cheat sheet", "Cheat sheet", "tool"),
    ("toolkit", "Toolkit", "Toolkit", "section"),
]
# Progressive disclosure on screen: these spreads fold behind a one-line "More" bar (the PDF shows everything).
FOLD = re.compile(r"(variants|build|best-practice-2|geographies|projection-zoom)$")
# The Quick guide PDF: the pages to read first, in this order.
QUICK = ["cover", "quick-start", "chooser", "chooser-traps", "question-first", "anatomy", "headline", "color",
         "honest-scales", "people-data", "mck-slide", "slides", "two-charts", "flat", "bar", "bar-best-practice",
         "line", "cheat-sheet", "setup"]
QUICK_PDF = OUT / "McKesson-DataViz-Quick-Guide.pdf"
# One-page PDFs printed from guide spreads: file name -> spread ids.
ONE_PAGERS = {"chart-chooser": ["chooser", "chooser-traps"], "cheat-sheet": ["cheat-sheet"]}

LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{head}
</head>
<body>
{topbar}<main>
{body}
</main>
{script}</body>
</html>
"""
LINKED_CSS = '<link rel="stylesheet" href="mck-viz.css">\n<link rel="stylesheet" href="guide.css">'
SPREAD_RE = re.compile(r'<section class="spread[^"]*" id="([\w-]+)"')

CANDIDATES = [
    os.environ.get("CHROME", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("msedge") or "",
]


def browser() -> str:
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("No Chrome/Edge found; set CHROME to the browser executable.")


def page_count(pdf: Path) -> int:
    try:
        import pymupdf
        return len(pymupdf.open(pdf))
    except ImportError:
        return pdf.read_bytes().count(b"/Type /Page") - pdf.read_bytes().count(b"/Type /Pages")


# ------------------------------------------------------------------ spread index: id -> page stem, PDF page number
def index_spreads() -> tuple[dict[str, str], dict[str, int], dict[str, str]]:
    stem_of, page_of, first_of = {}, {}, {}
    n = 0
    for stem, *_ in PAGES:
        src = (SRC / "pages" / f"{stem}.html").read_text(encoding="utf-8")
        if src.count('<section class="spread') != len(SPREAD_RE.findall(src)):
            sys.exit(f"{stem}.html: every <section class=\"spread\"> needs an id")
        for sid in SPREAD_RE.findall(src):
            n += 1
            if sid in stem_of:
                sys.exit(f"duplicate spread id '{sid}' in {stem}.html and {stem_of[sid]}.html")
            stem_of[sid], page_of[sid] = stem, n
            first_of.setdefault(stem, sid)
    return stem_of, page_of, first_of


def topbar(active: str | None, href) -> str:
    """href(stem) -> the link target for a page in this output."""
    links = "".join(f'<a href="{href(stem)}"{" aria-current=page" if stem == active else ""}>{label}</a>'
                    for stem, label, _, kind in PAGES if kind == "section")
    tools = "".join(f'<a class="tool" href="{href(stem)}"{" aria-current=page" if stem == active else ""}>{label}</a>'
                    for stem, label, _, kind in PAGES if kind == "tool")
    pdf = f'<a class="pdf" href="{PDF.name}">PDF</a>' if active != "__standalone__" else ""
    return (f'<header class="topbar"><a class="brand" href="{href("index")}"><b>McKesson</b> <span>Data Visualization '
            f'Guide</span></a><nav aria-label="Sections">{links}</nav><div class="tools">{tools}{pdf}</div></header>\n')


def render(stem: str, section: str, svgs: dict, text: dict, snippets: dict, used: set, idx, link) -> str:
    stem_of, page_of, _ = idx
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

    def lnk(m):
        if m.group(1) not in stem_of:
            sys.exit(f"{stem}.html: link to unknown spread '{m.group(1)}'")
        return link(m.group(1), stem)

    def pg(m):
        if m.group(1) not in page_of:
            sys.exit(f"{stem}.html: page number of unknown spread '{m.group(1)}'")
        return str(page_of[m.group(1)])

    def folio(m):
        sid = SPREAD_RE.findall(src[:m.start()])[-1]
        return (f'<div class="folio" aria-hidden="true"><span>McKesson Data Visualization Guide</span><span>{section}</span>'
                f'<span class="n">{page_of[sid]}</span></div>')

    out = re.sub(r"\{\{folio\}\}", folio, src)
    out = re.sub(r"\{\{exhibit:([\w-]+)(?:\|(\w+))?\}\}", exhibit, out)
    out = re.sub(r"\{\{text:(\w+)\}\}", txt, out)
    out = re.sub(r"\{\{html:(\w+)\}\}", lambda m: snippets[m.group(1)], out)
    out = re.sub(r"\{\{link:([\w-]+)\}\}", lnk, out)
    out = re.sub(r"\{\{page:([\w-]+)\}\}", pg, out)
    left = re.findall(r"\{\{[^}]*\}\}", out)
    if left:
        sys.exit(f"{stem}.html: unknown placeholder(s) {left}")
    return out


FOLD_JS = """<script>
// Folded spreads open when a link (or the address bar) points at them.
(() => {
  const open = () => {
    const t = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const d = t && t.closest('details.fold');
    if (d && !d.open) { d.open = true; t.scrollIntoView(); }
  };
  addEventListener('hashchange', open); addEventListener('DOMContentLoaded', open); open();
})();
</script>
"""


def fold(body: str) -> str:
    """Wrap the spreads named by FOLD in <details>: readers see one line ("More: Bar chart variants") until they ask."""
    def wrap(m):
        sec = m.group(0)
        title = re.sub(r"<[^>]+>", "", re.search(r'<h2 class="title">(.*?)</h2>', sec, re.S).group(1))
        title = " ".join(title.split())
        return (f'<details class="fold"><summary><span class="more">More</span> {html.escape(title)}'
                f'<span class="hint">Show</span></summary>\n{sec}\n</details>')
    return re.sub(r'<section class="spread[^"]*" id="([\w-]+)".*?</section>',
                  lambda m: wrap(m) if FOLD.search(m.group(1)) else m.group(0), body, flags=re.S)


def single_doc_links(body: str, first_of: dict[str, str], present: set[str]) -> str:
    """In a one-file document, page links (magnitude.html, magnitude.html#bar) become in-document anchors. Links to
    spreads that aren't in this document lose their href (the text stays)."""
    stems = "|".join(re.escape(s) for s in first_of)

    def fix(m):
        target = m.group(2)[1:] if m.group(2) else first_of[m.group(1)]
        return f'href="#{target}"'
    body = re.sub(rf'href="({stems})\.html(#[\w-]+)?"', fix, body)
    return re.sub(r'<a ([^>]*?)href="#([\w-]+)"([^>]*)>', lambda m: m.group(0) if m.group(2) in present
                  else f'<a {m.group(1)}{m.group(3)}>', body)


def repo_links(body: str) -> str:
    """Links to kit files (../office/..., ../../docs/...) are relative to dist/guide/, which only works inside the repo
    or the release bundle. In files that travel on their own (the PDFs, the standalone HTML), point them at GitHub."""
    def fix(m):
        target = (OUT / m.group(1)).resolve()
        rel = target.relative_to(ROOT).as_posix()
        kind = "tree" if target.is_dir() else "blob"
        return f'href="{REPO_URL}/{kind}/main/{rel}{m.group(2) or ""}"'
    return re.sub(r'href="((?:\.\./)+[^"#]*)(#[^"]*)?"', fix, body)


def main() -> None:
    import exhibits

    OUT.mkdir(parents=True, exist_ok=True)
    idx = index_spreads()
    stem_of, page_of, first_of = idx
    svgs = exhibits.render_all()
    used: set[str] = set()

    def multi_link(sid, here):
        return f"#{sid}" if stem_of[sid] == here else f"{stem_of[sid]}.html#{sid}"

    def single_link(sid, here):
        return f"#{sid}"

    pages = {}                                            # stem -> body for the multi-page site
    singles = {}                                          # stem -> body with in-document links
    for stem, label, section, _ in PAGES:
        pages[stem] = render(stem, section, svgs, exhibits.TEXT, exhibits.HTML, used, idx, multi_link)
        singles[stem] = render(stem, section, svgs, exhibits.TEXT, exhibits.HTML, set(), idx, single_link)
        title = "McKesson Data Visualization Guide" + ("" if stem == "index" else f": {label}")
        (OUT / f"{stem}.html").write_text(
            LAYOUT.format(title=title, head=LINKED_CSS, topbar=topbar(stem, lambda s: f"{s}.html"),
                          body=fold(pages[stem]), script=FOLD_JS), encoding="utf-8")
        print(f"wrote {(OUT / f'{stem}.html').relative_to(ROOT)}")

    every = set(stem_of)
    all_single = repo_links(single_doc_links("\n".join(singles[s] for s, *_ in PAGES), first_of, every))
    (OUT / "print.html").write_text(LAYOUT.format(title="McKesson Data Visualization Guide", head=LINKED_CSS, topbar="",
                                                  body=all_single, script=""), encoding="utf-8")
    for name, ids in ONE_PAGERS.items():                     # print sources for the one-page PDFs
        body = "\n".join(re.search(rf'<section class="spread[^"]*" id="{i}".*?</section>', all_single, re.S).group(0)
                         for i in ids)
        (OUT / f"_print-{name}.html").write_text(
            LAYOUT.format(title=name, head=LINKED_CSS, topbar="", body=single_doc_links(body, first_of, set(ids)),
                          script=""), encoding="utf-8")

    quick = "\n".join(re.search(rf'<section class="spread[^"]*" id="{i}".*?</section>', all_single, re.S).group(0)
                      for i in QUICK)                      # the Quick guide: same spreads, its own page order
    (OUT / "_print-quick.html").write_text(
        LAYOUT.format(title="Quick guide", head=LINKED_CSS + "\n<style>.folio .n { display: none; }</style>",
                      topbar="", body=single_doc_links(quick, first_of, set(QUICK)), script=""), encoding="utf-8")

    shutil.copy2(SRC / "guide.css", OUT / "guide.css")
    shutil.copy2(ROOT / "dist" / "web" / "mck-viz.css", OUT / "mck-viz.css")
    (OUT / "fonts").mkdir(exist_ok=True)
    for w in ("Light", "Regular", "Medium", "SemiBold", "Bold", "Italic"):
        shutil.copy2(ROOT / "fonts" / "LibreFranklin" / f"LibreFranklin-{w}.ttf", OUT / "fonts")
    shutil.copy2(ROOT / "fonts" / "LibreFranklin" / "OFL.txt", OUT / "fonts")

    unused = sorted(set(svgs) - used)
    if unused:
        print(f"  note: exhibits not used on any page: {', '.join(unused)}")
    print(f"{len(page_of)} spreads, {len(used)} exhibits")
    if "--no-pdf" not in sys.argv:
        exe = browser()
        check_overflow(exe)
        print_pdf(exe, OUT / "print.html", PDF, expected=len(page_of))
        PRINT_OUT.mkdir(parents=True, exist_ok=True)
        for name, ids in ONE_PAGERS.items():
            src = OUT / f"_print-{name}.html"
            print_pdf(exe, src, PRINT_OUT / f"{name}.pdf", expected=len(ids))
            src.unlink()
        print_pdf(exe, OUT / "_print-quick.html", QUICK_PDF, expected=len(QUICK))
        (OUT / "_print-quick.html").unlink()
        thumbnails()
    else:
        for name in ONE_PAGERS:
            (OUT / f"_print-{name}.html").unlink()
        (OUT / "_print-quick.html").unlink()
    write_standalone(all_single)       # last: it inlines the thumbnails


# ------------------------------------------------------------------ standalone single file
STANDALONE_JS = """<script>
// Highlight the section in the top bar as the reader scrolls (the file works without it).
(() => {
  const links = new Map([...document.querySelectorAll('.topbar a[data-page]')].map(a => [a.dataset.page, a]));
  const seen = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    links.forEach(a => a.removeAttribute('aria-current'));
    const a = links.get(e.target.dataset.page);
    if (a) { a.setAttribute('aria-current', 'page'); a.scrollIntoView({block: 'nearest', inline: 'nearest'}); }
  }), {rootMargin: '-45% 0px -50% 0px'});
  document.querySelectorAll('[data-page]').forEach(p => { if (p.tagName === 'DIV') seen.observe(p); });
})();
</script>
"""


def _data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def write_standalone(all_single: str) -> None:
    """One HTML file with everything inside (styles, fonts, images, every page), for sending to someone who has
    neither the repo nor, necessarily, a network connection."""
    _, _, first_of = index_spreads()
    css = (OUT / "mck-viz.css").read_text(encoding="utf-8") + "\n" + (OUT / "guide.css").read_text(encoding="utf-8")
    css = re.sub(r'url\("fonts/([\w-]+\.ttf)"\)',
                 lambda m: f'url("{_data_uri(OUT / "fonts" / m.group(1), "font/ttf")}")', css)
    css += "\n.ext { color: var(--g-ink); font-weight: inherit; }\n"
    body = all_single
    # Wrap each page so the top bar can follow the reader; a page starts at the first spread of its stem.
    parts = []
    starts = sorted((body.index(f'id="{first_of[s]}"'), s) for s, *_ in PAGES)
    starts = [(body.rfind("<section", 0, i), s) for i, s in starts]
    for k, (i, stem) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(body)
        parts.append(f'<div class="page" data-page="{stem}">\n{body[i:end]}</div>\n')
    body = fold("".join(parts))
    body = re.sub(r'src="img/([\w-]+\.png)"', lambda m: f'src="{_data_uri(OUT / "img" / m.group(1), "image/png")}"', body)
    bar = topbar("__standalone__", lambda s: f"#{first_of[s]}")
    bar = re.sub(r'<a (class="tool" )?href="#([\w-]+)"',
                 lambda m: f'<a {m.group(1) or ""}data-page="{next(s for s in first_of if first_of[s] == m.group(2))}" '
                           f'href="#{m.group(2)}"', bar)
    note = ('<p class="standalone-note">This is the standalone copy of the guide: one file that works offline. Links to '
            'templates, themes and code open the starter kit on GitHub; the release bundle has them as files.</p>')
    body = body.replace('<p class="small">Inspired by the structure', note + '\n    <p class="small">Inspired by the structure', 1)
    STANDALONE.write_text(LAYOUT.format(title="McKesson Data Visualization Guide", head=f"<style>\n{css}\n</style>",
                                        topbar=bar, body=body, script=STANDALONE_JS + FOLD_JS), encoding="utf-8")
    left = re.findall(r'(?:src|href)="(?!#|data:|https?:)[^"]+"', STANDALONE.read_text(encoding="utf-8"))
    mb = STANDALONE.stat().st_size / 1e6
    print(f"wrote {STANDALONE.relative_to(ROOT)} ({mb:.1f} MB, self-contained"
          + (f"; WARNING {len(left)} external reference(s): {left[:3]}" if left else "") + ")")


def thumbnails() -> None:
    """Thumbnails of the one-page PDFs for the Toolkit page."""
    (OUT / "img").mkdir(exist_ok=True)
    try:
        import pymupdf
        for pdf in sorted(PRINT_OUT.glob("*.pdf")):
            pymupdf.open(pdf)[0].get_pixmap(dpi=40).save(OUT / "img" / f"{pdf.stem}.png")
    except ImportError:
        print("  note: pymupdf not installed; Toolkit thumbnails not refreshed")


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
    for (const el of s.querySelectorAll('.ex-wrap, pre.snip, .panel, .card'))      // sideways: scrollbars in the PDF
      if (el.scrollWidth > el.clientWidth + 1)
        bad.push((i + 1) + ':' + el.className.split(' ')[0] + ':' + (el.scrollWidth - el.clientWidth) + 'px wide');
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


def print_pdf(exe: str, src: Path, pdf: Path, expected: int) -> None:
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf}", src.as_uri()],
                   check=True, capture_output=True)
    pages = page_count(pdf)
    print(f"wrote {pdf.relative_to(ROOT)} ({pages} page{'s' if pages != 1 else ''})")
    if pages != expected:
        print(f"  warning: expected {expected} pages (one per spread); a spread is overflowing")


if __name__ == "__main__":
    main()
