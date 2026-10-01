"""Check that this environment can build McKesson charts in Python: mckviz installed, Libre Franklin registered.

    python scripts/check_env.py          # exit code 0 = ready, 1 = something to fix (the fix is printed)
"""
from __future__ import annotations

import sys
import warnings

INSTALL = 'pip install "mckviz @ git+{{repo_url}}@v{{version}}#subdirectory=python"'


def main() -> int:
    try:
        import mckviz as mv
    except ImportError:
        print(f"mckviz is not installed. Install it with:\n  {INSTALL}")
        return 1
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        mv.use()
    from matplotlib import font_manager as fm

    font = fm.findfont(mv.FONT)
    ok = "LibreFranklin" in font.replace(" ", "") and not caught
    print(f"mckviz {getattr(mv, '__version__', '(unknown version)')} from {mv.__file__}")
    print(f"font: {font}")
    for w in caught:
        print(f"warning: {w.message}")
    def parts(v: str) -> tuple:
        return tuple(int(x) for x in v.split(".")[:3] if x.isdigit())

    if parts(getattr(mv, "__version__", "0")) < parts("{{version}}"):
        print(f"note: this skill was written for mckviz {{version}}; upgrade with:\n  {INSTALL}")
    for extra in ("plotly", "pandas"):
        try:
            __import__(extra)
        except ImportError:
            print(f"optional: {extra} is not installed (pip install {extra})")
    print("ready" if ok else "not ready: Libre Franklin did not register; reinstall mckviz")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
