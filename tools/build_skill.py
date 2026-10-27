"""Build the portable agent skill (dist/skills/mck-chart/), its Microsoft 365 Copilot edition
(dist/skills/mck-chart-copilot/) and the repo's own copy (.github/skills/mck-chart/SKILL.md).

    python tools/build_skill.py            (tokens/build.py runs it too; tools/make_bundle.py zips it)
    python tools/build_skill.py --zip      also builds the mckviz wheel into assets/python/ (needs uv) and writes
                                           dist/skills/mck-chart.zip (upload to Claude.ai as a custom skill) and
                                           dist/skills/mck-chart-copilot.zip
    python tools/build_skill.py --copilot  writes only the Copilot zip (upload in Agent Builder: Configure > Skills
                                           > Add); needs no uv. See docs/copilot-agent-setup.md

Source: agents/skill/SKILL.template.md, the task guides in agents/skill/references/ (filled per edition into
references/: options.md, review.md, native-formats.md), agents/skill/scripts/ and agents/skill/copilot/ (its files
land at the same paths in the Copilot edition). A block between
<!-- portable --> and <!-- /portable --> appears only in the portable skill, <!-- repo --> only in the repo copy,
<!-- copilot --> only in the Copilot edition; <!-- portable,repo --> in both of those. Placeholders: {{version}},
{{repo_url}}, {{description}}, {{docs}} (references/ or docs/), {{refs}} (where the task guides are), {{rules}} (the
house rules page), {{web_css}}, {{web_plotly}}, {{web_vega}}, {{chart_card}}, {{themes}}, {{pptx_theme}},
{{generated_note}}.

The portable skill is self-contained, so it works dropped into ~/.claude/skills/, a repo's .claude/skills/ or
.github/skills/, or zipped and uploaded to Claude.ai as a custom skill, in a sandbox that cannot reach GitHub:
    SKILL.md                    the workflow (question -> chart type -> build -> headline -> QA), under SKILL_BUDGET
    references/options.md ...   task guides SKILL.md points to: options pages, chart reviews, native formats
    references/rules.md         the house rules on one page (dist/agents/mck-viz-rules.md)
    references/*.md             principles, chart chooser, QA checklist, color, type, formats, Office and Power BI setup
    references/cookbook/*.md    one page per chart type (spec, do/don't, code for each platform)
    assets/                     web themes and chart-card starter, R theme, Power BI theme
    assets/data/                the sample CSVs the cookbook snippets read (synthetic)
    assets/fonts/               Libre Franklin TTFs and the OFL, for a run that cannot install packages
    assets/office/              the PowerPoint template (.potx), the theme XML and the pptxgenjs theme
    assets/python/              the mckviz wheel (--zip and make_bundle only; it is not committed)
    scripts/                    check_env.py (installs mckviz from the wheel, registers the font) and a mckviz how-to
Links between included docs keep working; links to other kit files point at GitHub. In the copied cookbook pages,
repo paths become skill paths (examples/data/ -> assets/data/, dist/web/ -> assets/web/, fonts/LibreFranklin ->
assets/fonts, ...), so the snippets run with the skill folder as the working directory.

The Copilot edition has the same references/ and SKILL.md workflow, built for Agent Builder's skill rules (SKILL.md at
the zip root, a fixed list of file types, no pip and no network in the sandbox; COPILOT_* below), and fails the build
when it breaks one (Agent Builder also rejects anything but script types under scripts/). mckviz ships as source with
scripts/mck_setup.py, which assembles it in a temp folder:
    scripts/mckviz_src/         the package code (.py only)
    assets/mckviz/              the tokens and Plotly template; mckviz.mplstyle and VERSION as .txt; a README
    assets/geodata/             the map data
    assets/fonts/               the Libre Franklin weights the type roles use, base64 in .ttf.b64.txt, and the OFL
    assets/data/, assets/powerbi/   as in the portable skill (web, R and Office theme files can't ship)
The folder is gitignored; the zip is what people upload.
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "agents" / "skill"
OUT = ROOT / "dist" / "skills" / "mck-chart"
REPO_SKILL = ROOT / ".github" / "skills" / "mck-chart" / "SKILL.md"
REPO_URL = "https://github.com/amccown-mck/Data-Viz-Guide"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
ZIP_LIMIT_MB = 10                                           # Claude.ai custom skills; the zip is ~4 MB with the wheel

DOCS = ["principles.md", "choosing-a-chart.md", "chart-decision-tree.md", "qa-checklist.md", "color.md", "typography-and-layout.md",
        "formats.md", "office-setup.md", "powerbi-setup.md"]
# skill path under assets/ -> repo path. Text files get the skill's relative paths; binaries are copied as they are.
ASSETS = {"web/mck-viz.css": "dist/web/mck-viz.css", "web/mck-plotly-template.js": "dist/web/mck-plotly-template.js",
          "web/vega-lite-config.json": "dist/web/vega-lite-config.json", "r/theme_mck.R": "dist/r/theme_mck.R",
          "powerbi/mckesson-dataviz-theme.json": "dist/powerbi/mckesson-dataviz-theme.json",
          "html/chart-card.html": "templates/html/chart-card.html",
          "office/McKesson-DataViz.potx": "dist/office/McKesson-DataViz.potx",
          "office/pptxgenjs-theme.js": "dist/office/pptxgenjs-theme.js",
          "office/Theme Colors/McKesson Data Viz.xml": "dist/office/Theme Colors/McKesson Data Viz.xml",
          "office/Theme Fonts/McKesson Data Viz.xml": "dist/office/Theme Fonts/McKesson Data Viz.xml"}
BINARY = (".potx", ".pptx", ".xlsx", ".whl", ".ttf", ".png")
FONTS = ROOT / "fonts" / "LibreFranklin"
# Repo folders that ship whole in the skill (for link rewriting), besides the files in ASSETS.
SHIPPED_DIRS = {"fonts/LibreFranklin": "fonts", "examples/data": "data"}
# Repo paths in the copied cookbook pages -> where the same file is in the skill (or in the release bundle, for the
# starter deck and workbook, which the skill doesn't ship). Specific entries first. Not applied inside GitHub URLs.
COOKBOOK_PATHS = {"examples/data/": "assets/data/", "dist/web/": "assets/web/", "dist/r/": "assets/r/",
                  "dist/powerbi/": "assets/powerbi/", "fonts/LibreFranklin": "assets/fonts",
                  "dist/office/McKesson-DataViz-Starter": "office/McKesson-DataViz-Starter",
                  "dist/office/McKesson-DataViz-Charts": "office/McKesson-DataViz-Charts", "dist/office": "assets/office"}
ZIP = OUT.parent / "mck-chart.zip"

COPILOT_OUT = ROOT / "dist" / "skills" / "mck-chart-copilot"
COPILOT_ZIP = COPILOT_OUT.parent / "mck-chart-copilot.zip"
# Agent Builder skill rules (preview, 2026-09): learn.microsoft.com/microsoft-365/copilot/extensibility/declarative-agent-skills
COPILOT_SCRIPT_TYPES = {".py", ".js", ".mjs", ".cjs", ".ts", ".mts", ".sh", ".bash"}   # the only types under scripts/
COPILOT_TYPES = {".json", ".xml", ".yaml", ".yml", ".ini", ".config", ".utf8", ".docx", ".doc", ".docm", ".pdf", ".txt",
                 ".rtf", ".md", ".ppt", ".pptx", ".ppsm", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv", ".html", ".htm",
                 ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".log", *COPILOT_SCRIPT_TYPES}
# Our own budget for SKILL.md, well under the platform's 20,000: it holds only what every chart needs. Task detail goes in
# the guides in agents/skill/references/ (read on demand), and a rule a function enforces gets a line at most.
SKILL_BUDGET = 14_000
TASK_GUIDES = SRC / "references"                          # options.md, review.md, native-formats.md -> references/
COPILOT_MAX = {"instructions": 20_000, "description": 1024, "parts": 3, "files": 350, "file_mb": 25, "zip_mb": 50}
COPILOT_FONTS = ("Light", "Regular", "Medium", "SemiBold", "Bold")   # the weights the type roles use (300-700)
COPILOT_ASSETS = ("data", "powerbi")        # portable assets/ folders whose file types a Copilot skill can carry

DESCRIPTION = ("Make a McKesson-standard chart or table from data, going from question to chart type, build with mckviz "
               "(or the web, Office, Power BI or R theme), insight headline, and QA checklist. Use whenever the user asks "
               "for a chart, graph, plot, visualization, scorecard or exhibit for McKesson, or for Workforce Innovation "
               "work (people analytics, workforce intelligence or planning / SWP data).")
MODES = {
    "copilot": {"docs": "references/", "refs": "references/", "rules": "references/rules.md",
                "description": "Make or review a McKesson-standard chart or table: question, chart type, build with "
                               "mckviz in the Python sandbox, insight headline, and QA checklist, plus Excel, "
                               "PowerPoint and Power BI steps when the chart must be native. Use whenever the user asks "
                               "for a chart, graph, plot, visualization, scorecard or exhibit for McKesson, asks for "
                               "feedback on one, or works with Workforce Innovation data (people analytics, workforce "
                               "intelligence or planning / SWP).",
                "generated_note": "GENERATED by tools/build_skill.py from agents/skill/ in the data-viz-guide repo "
                                  "(Microsoft 365 Copilot edition)."},
    "portable": {"docs": "references/", "refs": "references/", "rules": "references/rules.md",
                 "description": DESCRIPTION, "web_css": "`assets/web/mck-viz.css`",
                 "web_plotly": "`assets/web/mck-plotly-template.js`", "web_vega": "`assets/web/vega-lite-config.json`",
                 "chart_card": " (starter: `assets/html/chart-card.html`)",
                 "pptx_theme": "`assets/office/pptxgenjs-theme.js`",
                 "themes": "the theme files in `assets/` (Office files: see Setup below)",
                 "generated_note": "GENERATED by tools/build_skill.py from agents/skill/ in the data-viz-guide repo."},
    "repo": {"docs": "docs/", "refs": ".github/skills/mck-chart/references/", "rules": "AGENTS.md",
             "description": DESCRIPTION, "web_css": "`dist/web/mck-viz.css`", "web_plotly": "`mck-plotly-template.js`",
             "web_vega": "`vega-lite-config.json`", "chart_card": " (starter: `templates/html/chart-card.html`)",
             "pptx_theme": "`dist/office/pptxgenjs-theme.js`", "themes": "the themes in `dist/`",
             "generated_note": "GENERATED by tools/build_skill.py from agents/skill/SKILL.template.md - edit that, then "
                               "rerun (tokens/build.py does)."},
}


def fill(text: str, mode: str) -> str:
    """Keep the <!-- mode --> blocks (or <!-- a,b --> blocks naming the mode), drop the others, fill placeholders."""
    text = re.sub(r"<!-- ([a-z]+(?:,[a-z]+)*) -->\n(.*?)<!-- /\1 -->\n?",
                  lambda m: m.group(2) if mode in m.group(1).split(",") else "", text, flags=re.S)
    values = {"version": VERSION, "repo_url": REPO_URL, **MODES[mode]}
    values["description"] = json.dumps(values["description"], ensure_ascii=False)  # quoted: valid YAML with any ':'
    text = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], text)
    return re.sub(r"\n{3,}", "\n\n", text)


def shipped_path(rel: str) -> str | None:
    """Where a repo path (posix, relative to the root) lives inside the skill's assets/, or None if it doesn't ship."""
    for skill_rel, repo_rel in ASSETS.items():
        if rel == repo_rel:
            return skill_rel
    for repo_dir, skill_dir in SHIPPED_DIRS.items():
        if rel == repo_dir or rel.startswith(repo_dir + "/"):
            return skill_dir + rel[len(repo_dir):]
    return None


def portable_links(md: str, src: Path, dest: Path) -> str:
    """Relative links: kept if the target ships in the skill (same layout as docs/), else pointed at GitHub."""
    def fix(m):
        target, anchor = m.group(1), m.group(2) or ""
        if not target or re.match(r"[a-z]+:", target):
            return m.group(0)
        resolved = (src.parent / target).resolve()
        try:
            rel_docs = resolved.relative_to(ROOT / "docs")
            shipped = OUT / "references" / rel_docs
            if shipped.exists() or shipped == dest:
                return m.group(0)
        except ValueError:
            pass
        rel = resolved.relative_to(ROOT).as_posix()
        shipped_asset = shipped_path(rel)
        if shipped_asset:                                   # a theme file, font or dataset that ships in assets/
            up = Path(*[".."] * len(dest.parent.relative_to(OUT).parts))
            return f"]({(up / 'assets' / shipped_asset).as_posix()}{anchor})"
        kind = "tree" if resolved.is_dir() else "raw" if resolved.suffix in (".png", ".svg", ".jpg") else "blob"
        return f"]({REPO_URL}/{kind}/main/{rel}{anchor})"
    return re.sub(r"\]\(([^)\s#]*)(#[^)\s]*)?\)", fix, md)


def build_wheel(dest: Path) -> Path:
    """Build the mckviz wheel (fonts and map data inside) with uv into dest/. Fails loudly: the wheel is what makes
    the skill work in a sandbox that cannot reach GitHub, so a zip without it is not a release."""
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("tools/build_skill.py: `uv` is not on PATH, so the mckviz wheel cannot be built. Install it "
                         "(https://docs.astral.sh/uv/, or `pip install uv`), or run without --zip.")
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([uv, "build", str(ROOT / "python"), "--wheel", "--out-dir", tmp],
                           capture_output=True, text=True)
        for junk in ("build", "mckviz.egg-info"):              # setuptools builds in-tree; tidy up (both gitignored)
            shutil.rmtree(ROOT / "python" / junk, ignore_errors=True)
        wheels = sorted(Path(tmp).glob("mckviz-*.whl"))
        if r.returncode or not wheels:
            raise SystemExit(f"tools/build_skill.py: uv build failed:\n{(r.stderr or r.stdout).strip()[-800:]}")
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        return Path(shutil.copy2(wheels[0], dest / wheels[0].name))


def python_readme() -> str:
    name = f"mckviz-{VERSION}-py3-none-any.whl"
    return (f"# mckviz wheel\n\n`{name}`: the kit's Python package with the Libre Franklin fonts and the map data "
            f"inside, built from `python/` in the repo. Install it with no access to GitHub:\n\n"
            f"    pip install assets/python/{name}\n\n"
            "(add `--no-deps` when PyPI is unreachable and matplotlib and numpy are already installed). "
            "`python scripts/check_env.py` does this for you and says which path worked.\n\n"
            "The wheel is built into this folder by `python tools/build_skill.py --zip` and `tools/make_bundle.py` "
            "(with uv), so it is in the skill zip and the release bundle but not in git. If it is missing here, "
            "use one of those, or install from GitHub.\n")


def build(wheel: bool = False) -> Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    ref = OUT / "references"
    (ref / "cookbook").mkdir(parents=True)
    pages = [(ROOT / "docs" / d, ref / d) for d in DOCS]
    pages += [(p, ref / "cookbook" / p.name) for p in sorted((ROOT / "docs" / "cookbook").glob("*.md"))
              if not p.name.startswith("_")]
    for src, dest in pages:                                 # copy first, so link checks see every shipped page
        shutil.copyfile(src, dest)
    data = set()
    for src, dest in pages:
        text = portable_links(src.read_text(encoding="utf-8"), src, dest)
        if dest.parent.name == "cookbook":
            data |= set(re.findall(r"(?<![\w/])examples/data/([\w.-]+\.csv)", text))
            for old, new in COOKBOOK_PATHS.items():
                text = re.sub(rf"(?<![\w/]){re.escape(old)}", new, text)
        dest.write_text(text, encoding="utf-8", newline="\n")
    (OUT / "assets" / "data").mkdir(parents=True)
    for name in sorted(data):                               # only the CSVs a snippet reads
        shutil.copyfile(ROOT / "examples" / "data" / name, OUT / "assets" / "data" / name)
    shutil.copyfile(ROOT / "dist" / "agents" / "mck-viz-rules.md", ref / "rules.md")
    (OUT / "assets" / "fonts").mkdir()
    for f in sorted(FONTS.iterdir()):                       # the font, for a run that cannot install the wheel
        if f.suffix == ".ttf" or f.name == "OFL.txt":
            shutil.copyfile(f, OUT / "assets" / "fonts" / f.name)

    for rel, src in ASSETS.items():
        dest = OUT / "assets" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.suffix in BINARY:
            shutil.copyfile(ROOT / src, dest)
            continue
        text = (ROOT / src).read_text(encoding="utf-8")
        if rel.startswith("html/"):                         # the starter links the themes next to it
            text = text.replace("../../dist/web/", "../web/").replace(
                "the two dist/ files below are linked relative to this file (templates/html/)",
                "the two theme files below are linked relative to this file (assets/html/ in the skill)")
            text = text.replace("dist/web/", "assets/web/").replace("docs/", "references/")
        dest.write_text(text, encoding="utf-8", newline="\n")

    whl = build_wheel(OUT / "assets" / "python") if wheel else None
    (OUT / "assets" / "python").mkdir(exist_ok=True)
    (OUT / "assets" / "python" / "README.md").write_text(python_readme(), encoding="utf-8", newline="\n")

    tpl = (SRC / "SKILL.template.md").read_text(encoding="utf-8")
    (OUT / "SKILL.md").write_text(fill(tpl, "portable"), encoding="utf-8", newline="\n")
    for src in sorted((SRC / "scripts").iterdir()):
        dest = OUT / "scripts" / src.name
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(fill(src.read_text(encoding="utf-8"), "portable"), encoding="utf-8", newline="\n")
    REPO_SKILL.write_text(fill(tpl, "repo"), encoding="utf-8", newline="\n")
    write_guides(OUT / "references", "portable")
    write_guides(REPO_SKILL.parent / "references", "repo")

    left = [p for p in OUT.rglob("*") if p.is_file() and p.suffix in (".md", ".py")
            and re.search(r"\{\{\w+\}\}", p.read_text(encoding="utf-8"))]
    if left:
        raise SystemExit(f"unfilled placeholders in {left}")
    n = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"  wrote dist/skills/mck-chart/ ({n} files{', with ' + whl.name if whl else ''}) "
          "and .github/skills/mck-chart/ (SKILL.md and the task guides)")
    build_copilot()
    return OUT


def write_guides(dest: Path, mode: str) -> None:
    """The task guides (agents/skill/references/*.md), filled for one edition, into its references/ folder."""
    dest.mkdir(parents=True, exist_ok=True)
    for src in sorted(TASK_GUIDES.glob("*.md")):
        (dest / src.name).write_text(fill(src.read_text(encoding="utf-8"), mode), encoding="utf-8", newline="\n")


def copilot_links(md: str, dest: Path) -> str:
    """Links into assets/ that the Copilot edition can't carry (web, R, Office themes, TTFs) point at GitHub."""
    def fix(m):
        target, anchor = m.group(1), m.group(2) or ""
        resolved = (dest.parent / target).resolve()
        if not target or re.match(r"[a-z]+:", target) or resolved.exists() or not resolved.is_relative_to(COPILOT_OUT):
            return m.group(0)
        rel = resolved.relative_to(COPILOT_OUT).as_posix().removeprefix("assets/")
        repo = ASSETS.get(rel) or next((d + rel[len(s):] for d, s in SHIPPED_DIRS.items() if rel.startswith(s + "/")),
                                       None)
        return f"]({REPO_URL}/blob/main/{repo}{anchor})" if repo else f"]({REPO_URL}/releases{anchor})"
    return re.sub(r"\]\(([^)\s#]*)(#[^)\s]*)?\)", fix, md)


def build_copilot() -> Path:
    """The Microsoft 365 Copilot edition, from the portable skill just built (see the module docstring)."""
    if COPILOT_OUT.exists():
        shutil.rmtree(COPILOT_OUT)
    COPILOT_OUT.mkdir(parents=True)
    tpl = (SRC / "SKILL.template.md").read_text(encoding="utf-8")
    (COPILOT_OUT / "SKILL.md").write_text(fill(tpl, "copilot"), encoding="utf-8", newline="\n")
    for folder in COPILOT_ASSETS:
        shutil.copytree(OUT / "assets" / folder, COPILOT_OUT / "assets" / folder)
    fonts = COPILOT_OUT / "assets" / "fonts"
    fonts.mkdir()
    for weight in COPILOT_FONTS:
        ttf = FONTS / f"LibreFranklin-{weight}.ttf"
        (fonts / f"{ttf.name}.b64.txt").write_bytes(base64.encodebytes(ttf.read_bytes()))
    shutil.copyfile(FONTS / "OFL.txt", fonts / "OFL.txt")

    for src in (SRC / "copilot").rglob("*"):                 # scripts/mck_setup.py, assets/mckviz/README.md
        if src.is_file() and "__pycache__" not in src.parts:
            dest = COPILOT_OUT / src.relative_to(SRC / "copilot")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(fill(src.read_text(encoding="utf-8"), "copilot"), encoding="utf-8", newline="\n")
    pkg = ROOT / "python" / "mckviz"
    shutil.copytree(pkg, COPILOT_OUT / "scripts" / "mckviz_src", ignore=lambda d, names: [   # the code only
        n for n in names if not n.endswith(".py")])
    for f in [*pkg.glob("*.json"), *pkg.glob("*.pptx"), pkg / "mckviz.mplstyle", pkg / "VERSION"]:   # data, by README
        name = f.name if f.suffix in COPILOT_TYPES else f"{f.name}.txt"   # mck_setup.py renames these back
        shutil.copyfile(f, COPILOT_OUT / "assets" / "mckviz" / name)
    shutil.copytree(pkg / "geodata", COPILOT_OUT / "assets" / "geodata", ignore=shutil.ignore_patterns("__pycache__"))

    shutil.copytree(OUT / "references", COPILOT_OUT / "references")  # after assets/, so links can check what ships
    for p in (COPILOT_OUT / "references").rglob("*.md"):
        p.write_text(copilot_links(p.read_text(encoding="utf-8"), p), encoding="utf-8", newline="\n")
    write_guides(COPILOT_OUT / "references", "copilot")       # replaces the portable fill of the task guides
    check_copilot()
    n = sum(1 for p in COPILOT_OUT.rglob("*") if p.is_file())
    size = len((COPILOT_OUT / "SKILL.md").read_text(encoding="utf-8"))
    print(f"  wrote dist/skills/mck-chart-copilot/ ({n} files; SKILL.md {size:,} of {SKILL_BUDGET:,} characters)")
    return COPILOT_OUT


def check_copilot() -> None:
    """Fail the build when the Copilot edition breaks an Agent Builder skill rule (COPILOT_TYPES, COPILOT_MAX)."""
    files = [p for p in COPILOT_OUT.rglob("*") if p.is_file()]
    problems = [f"{len(files)} files (max {COPILOT_MAX['files']})"] if len(files) > COPILOT_MAX["files"] else []
    for p in files:
        rel = p.relative_to(COPILOT_OUT)
        if p.suffix.lower() not in COPILOT_TYPES:
            problems.append(f"{rel.as_posix()}: {p.suffix or 'no extension'} is not a skill file type")
        elif rel.parts[0] == "scripts" and p.suffix.lower() not in COPILOT_SCRIPT_TYPES:
            problems.append(f"{rel.as_posix()}: only script types ({', '.join(sorted(COPILOT_SCRIPT_TYPES))}) may sit "
                            "under scripts/")
        if len(rel.parts) > COPILOT_MAX["parts"]:
            problems.append(f"{rel.as_posix()}: nested deeper than {COPILOT_MAX['parts']} levels")
        if p.stat().st_size > COPILOT_MAX["file_mb"] * 1e6:
            problems.append(f"{rel.as_posix()}: over {COPILOT_MAX['file_mb']} MB")
    skill = (COPILOT_OUT / "SKILL.md").read_text(encoding="utf-8")
    if len(skill) >= COPILOT_MAX["instructions"]:
        problems.append(f"SKILL.md is {len(skill):,} characters (must be under {COPILOT_MAX['instructions']:,})")
    elif len(skill) > SKILL_BUDGET:
        problems.append(f"SKILL.md is {len(skill):,} characters, over our budget of {SKILL_BUDGET:,}: move task detail "
                        "into agents/skill/references/ or into code (a builder or a lint rule), not into SKILL.md")
    # Agent Builder parses the front matter as YAML and rejects a plain value with ": " in it. No YAML parser here, so
    # hold it to a form that is always valid: a plain lowercase name and a JSON (double-quoted YAML) description.
    front = re.match(r"---\nname: ([a-z0-9-]+)\ndescription: (\".*\")\n---\n", skill)
    try:
        desc = json.loads(front.group(2)) if front else None
    except json.JSONDecodeError:
        desc = None
    if desc is None:
        problems.append('SKILL.md front matter must be exactly "name: <lowercase-name>" and "description: "<quoted>""')
    elif len(desc) > COPILOT_MAX["description"]:
        problems.append(f"description is {len(desc)} characters (max {COPILOT_MAX['description']})")
    if problems:
        raise SystemExit("tools/build_skill.py: the Copilot edition breaks Agent Builder's skill rules:\n  "
                         + "\n  ".join(problems))


def zip_copilot(dest: Path = COPILOT_ZIP) -> Path:
    """A zip with SKILL.md at its root: the layout Agent Builder expects."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(COPILOT_OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(COPILOT_OUT).as_posix())
    mb = dest.stat().st_size / 1e6
    if mb > COPILOT_MAX["zip_mb"]:
        raise SystemExit(f"{dest} is {mb:.1f} MB, over the {COPILOT_MAX['zip_mb']} MB limit for an Agent Builder skill")
    shown = dest.relative_to(ROOT).as_posix() if dest.is_relative_to(ROOT) else dest.name
    print(f"  wrote {shown} ({mb:.1f} MB)")
    return dest


def zip_skill(dest: Path = ZIP) -> Path:
    """A zip with the mck-chart/ folder at its root: the layout Claude.ai custom skills expect."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, (Path("mck-chart") / p.relative_to(OUT)).as_posix())
    mb = dest.stat().st_size / 1e6
    if mb > ZIP_LIMIT_MB:
        raise SystemExit(f"{dest} is {mb:.1f} MB, over the {ZIP_LIMIT_MB} MB limit for a Claude.ai skill")
    shown = dest.relative_to(ROOT).as_posix() if dest.is_relative_to(ROOT) else dest.name   # the bundle zips into a temp folder
    print(f"  wrote {shown} ({mb:.1f} MB)")
    return dest


if __name__ == "__main__":
    build(wheel="--zip" in sys.argv)
    if "--zip" in sys.argv:
        zip_skill()
    if "--zip" in sys.argv or "--copilot" in sys.argv:
        zip_copilot()
