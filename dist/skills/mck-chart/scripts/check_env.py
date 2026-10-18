"""Check that this environment can build McKesson charts in Python, and set it up where it can.

    python scripts/check_env.py          # exit code 0 = ready, 1 = something to fix (what to do is printed)

In order: is mckviz importable? If not, install the wheel shipped in assets/python/ (works with no access to GitHub),
then try the GitHub install. If neither works, print the no-package fallback (colors from references/rules.md as
named constants, fonts from assets/fonts/). Then check that Libre Franklin registers with matplotlib; if not, register
the TTFs in assets/fonts/; if that fails too, name the fallback (Liberation Sans or Arimo, metric-compatible with
Arial). The last line says which install path worked, or what to do instead.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
WHEELS = sorted((SKILL / "assets" / "python").glob("mckviz-*.whl"))
FONTS = SKILL / "assets" / "fonts"
GITHUB = 'mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.2.0#subdirectory=python'
FALLBACK_FONTS = ("Liberation Sans", "Arimo", "Arial")      # the first two are metric-compatible with Arial
FONT = "Libre Franklin"

def pip_install(*args: str) -> str | None:
    """Install with this interpreter's pip, or with uv when the venv has no pip. Returns the error, or None."""
    cmds = [[sys.executable, "-m", "pip", "install", "-q", *args]]
    if shutil.which("uv"):
        cmds.append(["uv", "pip", "install", "-q", "--python", sys.executable, *args])
    err = "pip is not available"
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            importlib.invalidate_caches()
            return None
        lines = (r.stderr or r.stdout).strip().splitlines()
        err = lines[-1] if lines else f"{cmd[0]} failed"
    return err

def import_mckviz():
    try:
        return importlib.import_module("mckviz")
    except ImportError:
        return None

def register_shipped_fonts() -> bool:
    """Register assets/fonts/*.ttf with matplotlib; True if matplotlib now finds Libre Franklin."""
    from matplotlib import font_manager as fm

    for ttf in FONTS.glob("*.ttf"):
        try:
            fm.fontManager.addfont(str(ttf))
        except (OSError, RuntimeError, ValueError):
            continue
    return any(f.name == FONT for f in fm.fontManager.ttflist)

def font_report() -> bool:
    """Print which font charts will use. True when it is Libre Franklin."""
    try:
        from matplotlib import font_manager as fm
    except ImportError:
        print("font: matplotlib is not installed (pip install matplotlib), so no font check")
        return False
    found = any(f.name == FONT for f in fm.fontManager.ttflist) or register_shipped_fonts()
    if found:
        print(f"font: {FONT} ({fm.findfont(FONT)})")
        return True
    for name in FALLBACK_FONTS:
        try:
            path = fm.findfont(name, fallback_to_default=False)
        except ValueError:
            continue
        print(f"font: {FONT} is not available (no TTFs in {FONTS}); use {name} ({path}) and say so under QA "
              "exceptions in the brief")
        return False
    print(f"font: {FONT} is not available and neither are {', '.join(FALLBACK_FONTS)}; matplotlib will use DejaVu "
          "Sans, whose wider letters can make labels collide. Leave label slack and say so under QA exceptions")
    return False

def main() -> int:
    mv = import_mckviz()
    how = "already installed"
    if mv is None and WHEELS:
        wheel = WHEELS[-1]
        print(f"mckviz is not installed; installing the wheel shipped with the skill ({wheel.relative_to(SKILL)})")
        err = pip_install(str(wheel))
        if err and any(k in err for k in ("matplotlib", "numpy", "No matching distribution")):
            err = pip_install("--no-deps", str(wheel)) and err      # PyPI unreachable: the wheel alone still helps
        if err:
            print(f"  local wheel failed: {err}")
        else:
            mv, how = import_mckviz(), f"installed from {wheel.relative_to(SKILL).as_posix()}"
    if mv is None:
        print("installing mckviz from GitHub (needs access to github.com)")
        err = pip_install(GITHUB)
        if err:
            print(f"  GitHub install failed: {err}")
        else:
            mv, how = import_mckviz(), "installed from GitHub"
    if mv is None:
        print("mckviz could not be installed. Build without it: take the color roles from references/rules.md and "
              "define them once as named constants, register the fonts in assets/fonts/ with matplotlib "
              "(font_manager.addfont per TTF), and go through references/qa-checklist.md by hand in place of mv.lint.")
        font_report()
        print("not ready: no mckviz (fallback above)")
        return 1

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        mv.use()
    for w in caught:
        print(f"warning: {w.message}")
    print(f"mckviz {getattr(mv, '__version__', '(unknown version)')} ({how}) from {mv.__file__}")
    font_ok = font_report()

    def parts(v: str) -> tuple:
        return tuple(int(x) for x in v.split(".")[:3] if x.isdigit())

    if parts(getattr(mv, "__version__", "0")) < parts("1.2.0"):
        print(f"note: this skill was written for mckviz 1.2.0; upgrade with:\n  pip install \"{GITHUB}\"")
    for extra in ("plotly", "pandas"):
        try:
            __import__(extra)
        except ImportError:
            print(f"optional: {extra} is not installed (pip install {extra})")
    print("ready" if font_ok else f"not ready: {FONT} did not register (fallback above)")
    return 0 if font_ok else 1

if __name__ == "__main__":
    sys.exit(main())
