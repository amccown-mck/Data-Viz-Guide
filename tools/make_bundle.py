"""Build the release bundle: one zip for SharePoint, for people who won't use git.

    python tools/make_bundle.py              -> dist/release/DataViz-Starter-Kit-McKesson-Edition-v<version>.zip
    python tools/make_bundle.py --no-wheel   skip building the mckviz wheel (offline machines)

Run the builds first (tokens/build.py, office/build_office.py, tools/build_guide.py): the bundle packs what is in
dist/ now and says so if something is missing. Layout inside the zip:

    DataViz-Starter-Kit-McKesson-Edition-v<version>/
      START-HERE.html          what's inside and what to open first, written for non-technical readers
      CHANGELOG.md
      guide/                   the standalone guide (one HTML file, works offline) and the 16:9 PDF
      print/                   one-page chart chooser and cheat sheet (PDF)
      office/                  PowerPoint template, starter deck(s), chart workbook, theme colors and fonts XML, set-up
      powerbi/                 report theme JSON and set-up
      fonts/LibreFranklin/     the TTFs and the SIL Open Font License
      web/                     CSS variables and components, mck-viz.js helper, Plotly template, Vega-Lite config,
                               chart-card starters (online and offline, with vendor/plotly.min.js), R theme
      python/                  the mckviz wheel (pip install it offline) and how to install from GitHub
      agents/                  the one-file rules, the portable mck-chart skill (folder and Claude.ai zip)

dist/office/McKesson-DataViz-Starter-Official.pptx (built locally from the internal brand template, never committed)
is included when it exists.
"""
from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
NAME = f"DataViz-Starter-Kit-McKesson-Edition-v{VERSION}"
OUT = DIST / "release" / f"{NAME}.zip"
REPO_URL = "https://github.com/amccown-mck/Data-Viz-Guide"
sys.path[:0] = [str(ROOT / "tools")]

# bundle path -> source (relative to the repo root). Missing optional files are skipped with a note.
FILES = {
    "CHANGELOG.md": "CHANGELOG.md",
    "LICENSE": "LICENSE",
    "guide/McKesson-DataViz-Guide.html": "dist/guide/McKesson-DataViz-Guide.html",
    "guide/McKesson-DataViz-Guide.pdf": "dist/guide/McKesson-DataViz-Guide.pdf",
    "guide/McKesson-DataViz-Quick-Guide.pdf": "dist/guide/McKesson-DataViz-Quick-Guide.pdf",
    "print/chart-chooser.pdf": "dist/print/chart-chooser.pdf",
    "print/cheat-sheet.pdf": "dist/print/cheat-sheet.pdf",
    "office/McKesson-DataViz.potx": "dist/office/McKesson-DataViz.potx",
    "office/McKesson-DataViz-Starter.pptx": "dist/office/McKesson-DataViz-Starter.pptx",
    "office/McKesson-DataViz-Charts.xlsx": "dist/office/McKesson-DataViz-Charts.xlsx",
    "office/Theme Colors/McKesson Data Viz.xml": "dist/office/Theme Colors/McKesson Data Viz.xml",
    "office/Theme Fonts/McKesson Data Viz.xml": "dist/office/Theme Fonts/McKesson Data Viz.xml",
    "office/office-setup.md": "docs/office-setup.md",
    "powerbi/mckesson-dataviz-theme.json": "dist/powerbi/mckesson-dataviz-theme.json",
    "powerbi/powerbi-setup.md": "docs/powerbi-setup.md",
    "web/mck-viz.css": "dist/web/mck-viz.css",
    "web/mck-plotly-template.js": "dist/web/mck-plotly-template.js",
    "web/mck-viz.js": "dist/web/mck-viz.js",
    "web/vendor/plotly.min.js": "dist/web/vendor/plotly.min.js",
    "web/vendor/LICENSE-plotly.txt": "dist/web/vendor/LICENSE-plotly.txt",
    "web/vega-lite-config.json": "dist/web/vega-lite-config.json",
    "web/theme_mck.R": "dist/r/theme_mck.R",
    "agents/mck-viz-rules.md": "dist/agents/mck-viz-rules.md",
}
OPTIONAL = {"office/McKesson-DataViz-Starter-Official.pptx": "dist/office/McKesson-DataViz-Starter-Official.pptx"}


def token_colors() -> dict:
    t = json.loads((ROOT / "tokens" / "tokens.json").read_text(encoding="utf-8"))
    c = t["color"]
    return {"title": c["text"]["title"]["value"], "headline": c["text"]["headline"]["value"],
            "text": c["text"]["primary"]["value"], "muted": c["text"]["muted"]["value"],
            "panel": c["surface"]["subtle"]["value"], "rule": c["chart"]["grid"]["value"],
            "focus": c["chart"]["focus"]["value"]}


def start_here(has_official: bool, has_wheel: bool) -> str:
    k = token_colors()
    v = html.escape(VERSION)
    official = ("<li><b>McKesson-DataViz-Starter-Official.pptx</b>: the same starter slides on the official McKesson "
                "brand template. Use this one for decks that leave the team.</li>") if has_official else ""
    wheel = (f"<p>Offline: <code>pip install python/mckviz-{v}-py3-none-any.whl</code> (from this folder).</p>"
             if has_wheel else "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data Viz Starter Kit · McKesson Edition</title>
<style>
@font-face {{ font-family: "Libre Franklin"; font-weight: 400; src: url("fonts/LibreFranklin/LibreFranklin-Regular.ttf"); }}
@font-face {{ font-family: "Libre Franklin"; font-weight: 600; src: url("fonts/LibreFranklin/LibreFranklin-SemiBold.ttf"); }}
@font-face {{ font-family: "Libre Franklin"; font-weight: 700; src: url("fonts/LibreFranklin/LibreFranklin-Bold.ttf"); }}
:root {{ --title: {k['title']}; --head: {k['headline']}; --text: {k['text']}; --muted: {k['muted']};
         --panel: {k['panel']}; --rule: {k['rule']}; --focus: {k['focus']}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: white; color: var(--text); font: 16px/1.55 "Libre Franklin", "Franklin Gothic Book", Arial, sans-serif; }}
main {{ max-width: 860px; margin: 0 auto; padding: 40px 16px 64px; }}
h1 {{ color: var(--title); font-size: 32px; line-height: 1.2; margin: 0 0 6px; font-weight: 700; }}
h2 {{ color: var(--head); font-size: 20px; margin: 36px 0 8px; font-weight: 600; }}
.lead {{ font-size: 18px; color: var(--head); margin: 0 0 4px; }}
.meta {{ color: var(--muted); font-size: 14px; margin: 0 0 28px; }}
.tag {{ color: var(--muted); font-size: 12.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; margin: 0 0 6px; }}
.first {{ background: var(--panel); padding: 18px 22px; border-left: 4px solid var(--focus); }}
.first p {{ margin: 0 0 6px; }}
a {{ color: var(--focus); }}
code {{ font-family: Consolas, Menlo, "Courier New", monospace; font-size: 14px; background: var(--panel); padding: 1px 4px;
        overflow-wrap: anywhere; }}
ul {{ padding-left: 20px; }} li {{ margin: 4px 0; }}
ol li {{ margin: 6px 0; }}
.small {{ color: var(--muted); font-size: 14px; }}
hr {{ border: 0; border-top: 1px solid var(--rule); margin: 40px 0 16px; }}
</style>
</head>
<body>
<main>
<p class="tag">McKesson Edition</p>
<h1>Data Viz Starter Kit</h1>
<p class="lead">One visual language for everyone who makes charts: business folks, technical folks and the AI agents working alongside them.</p>
<p class="meta">Version {v} · {date.today():%B %Y} · All example data is synthetic</p>

<p>Every tool has its own idea of good, so the same numbers look different in Excel, Python, Power BI and a chat
window, and most charts say nothing. This kit makes the right chart the easy chart in every tool you already use, and
checks the rules before a chart leaves your hands. Which chart and why, templates and code that are already on-brand,
and a playbook so AI assistants follow the same rules you do.</p>

<div class="first">
<p><b>Start here:</b> open <a href="guide/McKesson-DataViz-Guide.html">guide/McKesson-DataViz-Guide.html</a> in your
browser. It is the whole guide in one file and works offline. The same pages are in
<a href="guide/McKesson-DataViz-Guide.pdf">McKesson-DataViz-Guide.pdf</a> to read or present. Short on time? The
<a href="guide/McKesson-DataViz-Quick-Guide.pdf">Quick guide</a> has the 19 pages to read first.</p>
<p>To keep the rules in front of you, print or pin the one-pagers in <code>print/</code>:
<a href="print/chart-chooser.pdf">chart chooser</a> and <a href="print/cheat-sheet.pdf">cheat sheet</a>.</p>
</div>

<h2>1. Install the font (once)</h2>
<p>McKesson charts use <b>Libre Franklin</b>. Open <code>fonts/LibreFranklin/</code>, select all the <code>.ttf</code>
files, right-click and choose <b>Install</b> (on a Mac: double-click each one, then <b>Install Font</b>). Restart
PowerPoint and Excel afterwards. The font is free to use and share (SIL Open Font License, in the same folder).</p>

<h2>2. PowerPoint and Excel</h2>
<ul>
<li><b>McKesson-DataViz.potx</b>: the template. Double-click it to start a new deck with the colors and fonts set up.</li>
<li><b>McKesson-DataViz-Starter.pptx</b>: example slides with real, editable charts (highlighted bar, line, waterfall,
100% stacked). Copy a slide, then right-click the chart › <b>Edit Data</b> to paste in your numbers.</li>
{official}
<li><b>McKesson-DataViz-Charts.xlsx</b>: the palette and ready-made charts to copy into your own workbook.</li>
<li><b>Theme Colors</b> and <b>Theme Fonts</b>: add the McKesson colors to any existing file. Step-by-step instructions
are in <code>office/office-setup.md</code> (opens in Notepad or any text editor).</li>
</ul>

<h2>3. Power BI</h2>
<p>In Power BI Desktop: <b>View › Themes › Browse for themes</b>, then pick
<code>powerbi/mckesson-dataviz-theme.json</code>. How to highlight one bar, write insight titles and hide groups under 10
people is in <code>powerbi/powerbi-setup.md</code>.</p>

<h2>4. The rules in one minute</h2>
<ol>
<li>The title is the finding, written as a sentence with a number: “Two job families lose 1 in 4 people a year”.</li>
<li>Grey for context, McKesson Blue for what the title is about. Orange only when something is worse.</li>
<li>Label the bars and lines directly; drop the legend and the gridlines when the values are labelled.</li>
<li>Bars start at zero. No 3D, no shadows, no dual axes.</li>
<li>Never show a group of fewer than 10 people, anywhere, including tooltips and filters.</li>
<li>Bottom-left: “Source: system, date, population”.</li>
</ol>

<h2>For analysts and developers</h2>
<ul>
<li><b>Python:</b> <code>pip install "mckviz @ git+{REPO_URL}@v{v}#subdirectory=python"</code>, then
<code>import mckviz as mv; mv.use()</code>. {wheel}</li>
<li><b>Web:</b> <code>web/mck-viz.css</code> (CSS variables, chart card, KPI tile, status pill, grid and tables), <code>web/mck-viz.js</code>
(number formats, highlight, minimum n, status, Plotly layouts), <code>web/mck-plotly-template.js</code>, <code>web/vega-lite-config.json</code>;
<code>web/chart-card-offline.html</code> works with no internet (Plotly is in <code>web/vendor/</code>). <b>R:</b> <code>source("web/theme_mck.R")</code>.</li>
<li>Code examples for every chart type, and the source of everything here: <a href="{REPO_URL}">{REPO_URL}</a>.</li>
</ul>

<h2>For AI assistants (Claude, Copilot and others)</h2>
<ul>
<li><b>Claude.ai:</b> in Settings, find <b>Skills</b> (under Capabilities) and upload <code>agents/mck-chart-skill.zip</code>. Claude then
follows the McKesson chart workflow whenever you ask for a chart.</li>
<li><b>Claude Code:</b> copy the folder <code>agents/mck-chart/</code> into <code>~/.claude/skills/</code> (every project)
or into a repo's <code>.claude/skills/</code>. <b>GitHub Copilot:</b> into the repo's <code>.github/skills/</code>.</li>
<li><b>Any other assistant:</b> paste or attach <code>agents/mck-viz-rules.md</code>, the rules on one page.</li>
</ul>

<hr>
<p class="small">What changed in this version: <code>CHANGELOG.md</code>. Questions and suggestions: Ashley McCown,
Workforce Innovation, via <a href="{REPO_URL}/issues">{REPO_URL}/issues</a>. Code: MIT (<code>LICENSE</code>).
Fonts: SIL Open Font License 1.1. Map data in the Python package: us-atlas and world-atlas (ISC), from public-domain
U.S. Census and Natural Earth boundaries.</p>
</main>
</body>
</html>
"""


def build_wheel(dest: Path) -> Path | None:
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", tmp, str(ROOT / "python")],
                           capture_output=True, text=True)
        for junk in ("build", "mckviz.egg-info"):              # setuptools builds in-tree; tidy up (both gitignored)
            shutil.rmtree(ROOT / "python" / junk, ignore_errors=True)
        wheels = list(Path(tmp).glob("mckviz-*.whl"))
        if r.returncode or not wheels:
            print(f"  note: could not build the mckviz wheel ({(r.stderr or r.stdout).strip()[-200:]}); skipped")
            return None
        dest.mkdir(parents=True, exist_ok=True)
        return Path(shutil.copy2(wheels[0], dest / wheels[0].name))


def main() -> None:
    import build_skill

    build_skill.build()
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / NAME
        missing = []
        for rel, src in {**FILES, **OPTIONAL}.items():
            s = ROOT / src
            if not s.exists():
                if rel not in OPTIONAL:
                    missing.append(src)
                continue
            (stage / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, stage / rel)
        if missing:
            sys.exit(f"missing (run the builds first): {', '.join(missing)}")
        for name in ("chart-card.html", "chart-card-offline.html"):     # offline card: fonts/ and vendor/ sit beside it
            card = (ROOT / "templates" / "html" / name).read_text(encoding="utf-8")
            card = card.replace("../../dist/web/", "").replace("../../fonts/LibreFranklin/", "../fonts/LibreFranklin/")
            (stage / "web" / name).write_text(card, encoding="utf-8")
        fonts = stage / "fonts" / "LibreFranklin"
        fonts.mkdir(parents=True)
        for f in (ROOT / "fonts" / "LibreFranklin").iterdir():
            if f.suffix == ".ttf" or f.name == "OFL.txt":
                shutil.copy2(f, fonts / f.name)
        shutil.copytree(build_skill.OUT, stage / "agents" / "mck-chart")
        build_skill.zip_skill(stage / "agents" / "mck-chart-skill.zip")
        wheel = None if "--no-wheel" in sys.argv else build_wheel(stage / "python")
        (stage / "python").mkdir(exist_ok=True)
        (stage / "python" / "INSTALL.txt").write_text(
            f"Install the mckviz Python package (matplotlib and Plotly theme, fonts, helpers, maps, chart lint):\n\n"
            f"  pip install \"mckviz @ git+{REPO_URL}@v{VERSION}#subdirectory=python\"\n\n"
            + (f"or, without access to GitHub, from this folder:\n\n  pip install {wheel.name}\n\n" if wheel else "")
            + "Then: import mckviz as mv; mv.use()\n", encoding="utf-8")
        has_official = (stage / "office" / "McKesson-DataViz-Starter-Official.pptx").exists()
        (stage / "START-HERE.html").write_text(start_here(has_official, wheel is not None), encoding="utf-8")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(stage.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(stage.parent).as_posix())
        n = sum(1 for p in stage.rglob("*") if p.is_file())
    print(f"wrote {OUT.relative_to(ROOT)} ({n} files, {OUT.stat().st_size / 1e6:.1f} MB"
          f"{', with the Official starter deck' if has_official else ''}{', with the mckviz wheel' if wheel else ''})")


if __name__ == "__main__":
    main()
