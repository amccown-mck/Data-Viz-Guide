"""Load mckviz in a sandbox that can't install packages (the Microsoft 365 Copilot edition of the mck-chart skill).

    import runpy
    setup = runpy.run_path("<skill folder>/scripts/mck_setup.py", run_name="__main__")
    mv, C, SKILL_DIR = setup["mv"], setup["C"], setup["SKILL_DIR"]

or `python scripts/mck_setup.py` in a shell, then `sys.path.insert(0, MCKVIZ_PATH)` (it prints the path) and
`import mckviz as mv; mv.use()`.

Copilot skills carry only some file types (.py, .json, .md, .txt and a few others) and the sandbox has no pip and no
network, so the package ships as source: scripts/mckviz_src/ (the code, the tokens, and mckviz.mplstyle.txt and
VERSION.txt, renamed back here), scripts/mckviz_geodata/ (the map data) and assets/fonts/*.ttf.b64.txt (Libre
Franklin, base64-encoded, decoded back here). This script puts the package together in a temp folder, puts that
folder first on sys.path, imports it and applies the style. The last line says whether the font loaded.
"""
from __future__ import annotations

import base64
import importlib
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SRC = SKILL_DIR / "scripts" / "mckviz_src"
GEO = SKILL_DIR / "scripts" / "mckviz_geodata"
FONTS = SKILL_DIR / "assets" / "fonts"
VERSION = "{{version}}"
MCKVIZ_PATH = Path(tempfile.gettempdir()) / f"mckviz-{VERSION}"
FONT = "Libre Franklin"


def assemble(root: Path = MCKVIZ_PATH) -> Path:
    """Write a working mckviz package into root/mckviz/ and return root (the folder to put on sys.path)."""
    pkg = root / "mckviz"
    shutil.rmtree(pkg, ignore_errors=True)
    pkg.mkdir(parents=True)
    for f in SRC.iterdir():                                   # mckviz.mplstyle.txt -> mckviz.mplstyle, VERSION.txt -> VERSION
        if f.is_file():
            shutil.copyfile(f, pkg / (f.name[:-4] if f.name.endswith(".txt") else f.name))
    shutil.copytree(GEO, pkg / "geodata")
    (pkg / "fonts").mkdir()
    for f in FONTS.glob("*.ttf.b64.txt"):
        (pkg / "fonts" / f.name[:-len(".b64.txt")]).write_bytes(base64.b64decode(f.read_text(encoding="ascii")))
    if (FONTS / "OFL.txt").exists():
        shutil.copyfile(FONTS / "OFL.txt", pkg / "fonts" / "OFL.txt")
    return root


def load():
    """Assemble, import and style. Returns (mv, warning messages)."""
    root = str(assemble())
    if root in sys.path:
        sys.path.remove(root)
    sys.path.insert(0, root)
    for name in [m for m in sys.modules if m == "mckviz" or m.startswith("mckviz.")]:
        del sys.modules[name]                                 # a stale copy from an earlier run or another install
    importlib.invalidate_caches()
    mv = importlib.import_module("mckviz")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        mv.use()
    return mv, [str(w.message) for w in caught]


def main():
    """Load mckviz and print what worked. Returns (mv, colors, font_ok); mv is None when it could not load."""
    try:
        mv, warns = load()
    except ImportError as e:
        print(f"mckviz could not load: {e}. Build without it: define the color roles from references/rules.md as "
              "named constants and go through references/qa-checklist.md by hand in place of mv.lint.")
        print(f"SKILL_DIR={SKILL_DIR}")
        print("not ready: no mckviz (fallback above)")
        return None, None, False
    for w in warns:
        print(f"warning: {w}")
    from matplotlib import font_manager as fm

    font_ok = any(f.name == FONT for f in fm.fontManager.ttflist)
    print(f"mckviz {mv.__version__} loaded from {Path(mv.__file__).parent}")
    print(f"font: {FONT}" if font_ok else
          f"font: {FONT} did not load; charts use {fm.findfont('sans-serif')}. Leave label slack and list the font "
          "under QA exceptions in the brief")
    for extra in ("pandas", "plotly"):
        try:
            __import__(extra)
        except ImportError:
            print(f"optional: {extra} is not available in this sandbox")
    print(f"MCKVIZ_PATH={MCKVIZ_PATH}")
    print(f"SKILL_DIR={SKILL_DIR}")
    print("ready" if font_ok else "ready, with a fallback font")
    return mv, mv.colors, font_ok


if __name__ == "__main__":
    mv, C, FONT_OK = main()
