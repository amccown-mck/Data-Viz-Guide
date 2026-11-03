"""Lint every gallery chart against the house rules with mckviz.lint (python/mckviz/lint.py).

    python tools/lint_charts.py            # matplotlib + Plotly galleries; exits 1 if any chart has an error
    python tools/lint_charts.py --all      # also print warn/info findings for charts without errors

Use mv.lint(fig) directly on your own figures before saving them.
"""
from __future__ import annotations

import argparse
import importlib
import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples" / "python"))

import mckviz as mv  # noqa: E402


def matplotlib_charts():
    g = importlib.import_module("gallery_matplotlib")
    names = [n for n in dir(g) if callable(getattr(g, n)) and not n.startswith("_")
             and getattr(getattr(g, n), "__module__", "") == g.__name__ and n != "main"]
    for name in sorted(names):
        fig = getattr(g, name)()
        yield f"matplotlib:{name}", fig, {}
        plt.close(fig)


def plotly_charts():
    g = importlib.import_module("gallery_plotly")
    captured = []
    real_card = g.card

    def capture(fig, headline, subtitle, source, footnote=None, dark=False):
        captured.append((fig, headline, subtitle, source))
        return real_card(fig, headline, subtitle, source, footnote, dark)

    g.card = capture
    for name in ("bar_highlight", "line_gap", "bubble_scatter", "sankey"):
        getattr(g, name)()
        fig, headline, subtitle, source = captured[-1]
        yield f"plotly:{name}", fig, {"headline": headline, "subtitle": subtitle, "source": source}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="show warn/info findings for every chart")
    args = ap.parse_args()
    mv.use()
    errors = 0
    for label, fig, texts in itertools.chain(matplotlib_charts(), plotly_charts()):   # each linted before it closes
        found = mv.lint(fig, quiet=True, **texts)
        n_err = sum(f.level == "error" for f in found)
        errors += n_err
        status = "FAIL" if n_err else "ok  "
        print(f"{status} {label}  ({n_err} error, {sum(f.level == 'warn' for f in found)} warn, "
              f"{sum(f.level == 'info' for f in found)} info)")
        for f in found:
            if args.all or f.level == "error":
                print("       " + str(f))
    print(f"\n{errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
