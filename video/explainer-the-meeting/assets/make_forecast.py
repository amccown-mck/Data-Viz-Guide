"""Forecast story for the explainer's notebook scene (s-notebook): a great model, a meh chart, then the kit.

Runs the exact cell strings shown on screen in one namespace (like a Jupyter kernel), on synthetic, seeded data,
captures real mv.lint output, and writes:
  fc_before.png    cell 2 as written: plain matplotlib defaults ("great model, meh chart")
  fc_one_line.png  the same cell with `import mckviz as mv; mv.use()` on top (the one-line change)
  fc_after.png     cell 3: mv.use() + the helpers (estimate, range, computed headline, source)
  fc_lint.json     the cells, the model output, the headline and mv.lint findings for before / after

Run (from the repo root):  .venv/bin/python video/explainer-exec-ready-by-3/assets/make_forecast.py
The model lives in a small module (attrition_model.py, written to a scratch folder) so the notebook cell reads like
a real team's: `from attrition_model import TrendSeasonal`. It is an honest, simple model: OLS on a linear trend plus
quarter-of-year effects, with an 80% prediction interval that widens with the horizon.
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

warnings.filterwarnings("ignore", message=".*non-interactive.*")

ASSETS = Path(__file__).resolve().parent
WORK = Path(tempfile.mkdtemp(prefix="fcwork-"))

# ---------------------------------------------------------------- synthetic, seeded data (FY22 Q1 - FY26 Q4)
rng = np.random.default_rng(2026)
t = np.arange(20)
season = np.array([-0.35, 0.65, 0.10, -0.40])          # a summer bump in Q2
rate = 22.4 - 0.27 * t + season[t % 4] + rng.normal(0, 0.45, t.size)
quarters = [f"FY{22 + i // 4} Q{i % 4 + 1}" for i in t]
pd.DataFrame({"quarter": quarters, "t": t, "rate": rate.round(1)}).to_csv(WORK / "attrition_quarterly.csv", index=False)

MODEL = '''\
"""A team's forecast model: linear trend + quarter effects (OLS), 80% interval widening with the horizon."""
import numpy as np
import pandas as pd
from statistics import NormalDist


class TrendSeasonal:
    def __init__(self, seasonal=4, drift=0.35):
        self.m, self.drift = seasonal, drift

    def _X(self, t):
        t = np.asarray(t, float)
        return np.column_stack([np.ones_like(t), t] + [(t % self.m) == k for k in range(1, self.m)]).astype(float)

    def fit(self, y):
        self.y = np.asarray(y, float)
        self.t = np.arange(self.y.size)
        X = self._X(self.t)
        self.beta, *_ = np.linalg.lstsq(X, self.y, rcond=None)
        resid = self.y - X @ self.beta
        self.s = np.sqrt(resid @ resid / (self.y.size - X.shape[1]))
        self.XtXi = np.linalg.inv(X.T @ X)
        return self

    def forecast(self, steps, interval=0.80):
        z = NormalDist().inv_cdf(0.5 + interval / 2)
        tf = self.t[-1] + np.arange(1, steps + 1)
        Xf = self._X(tf)
        mean = Xf @ self.beta
        lev = np.einsum("ij,jk,ik->i", Xf, self.XtXi, Xf)
        half = z * self.s * np.sqrt((1 + lev) * (1 + self.drift * np.arange(1, steps + 1)))
        last = self.y[-1]                                   # anchor: the estimate starts at the last actual
        q = lambda i: f"FY{22 + i // 4} Q{i % 4 + 1}"
        return pd.DataFrame({"quarter": [q(i) for i in [self.t[-1], *tf]], "t": [self.t[-1], *tf],
                             "mean": [last, *mean], "lower": [last, *(mean - half)], "upper": [last, *(mean + half)]})
'''
(WORK / "attrition_model.py").write_text(MODEL, encoding="utf-8")

# ---------------------------------------------------------------- the notebook cells, exactly as shown on screen
CELL1 = '''\
import pandas as pd
from attrition_model import TrendSeasonal          # your great model

df = pd.read_csv("attrition_quarterly.csv")       # FY22-FY26 actuals
model = TrendSeasonal(seasonal=4).fit(df.rate)
fc = model.forecast(steps=8, interval=0.80)       # FY27-FY28
fc.tail(3).round(1)'''

CELL2 = '''\
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 4.4))
plt.plot(df.quarter, df.rate, label="actual")
plt.plot(fc.quarter, fc["mean"], label="forecast")
plt.fill_between(fc.quarter, fc.lower, fc.upper, alpha=0.3, label="80% PI")
plt.xticks(rotation=90); plt.legend(); plt.title("Attrition forecast")
plt.show()'''

ONE_LINE = "import mckviz as mv; mv.use()"

CELL3 = '''\
C, GOAL, pct = mv.colors, 12, lambda v, d=1: mv.fmt_num(v, "pct", d)
now, (end, lo, hi) = df.rate.iloc[-1], fc.iloc[-1][["mean", "lower", "upper"]]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(df.t, df.rate, color=C.focus, label="_actual")                        # actuals, solid
ax.plot(fc.t, fc["mean"], color=C.focus, ls=(0, (4, 3)), label="Estimate")    # forecast, dashed
ax.fill_between(fc.t, fc.lower, fc.upper, color=C.focus, alpha=0.15, lw=0)
ax.axhline(GOAL, color=C.total, lw=0.75, ls="--")
ax.axvline(19, color=C.axis, lw=0.75, ls=":")
ax.text(19.3, 23.8, "Forecast", va="top", fontsize=10, fontweight="bold", color=C.text_muted)
ax.text(0, GOAL - 0.3, f"FY28 goal {GOAL}%", va="top", fontsize=10, color=C.total)
ax.plot(19, now, "o", ms=5, color=C.focus)

mv.clean_axes(ax)
ax.set_ylim(8, 24); ax.set_xlim(-0.4, 27.6)
ax.set_yticks([10, 15, 20], ["10%", "15%", "20%"])
ax.set_xticks([1.5 + 4 * k for k in range(7)], [f"FY{22 + k}" for k in range(7)])
ax.tick_params(axis="x", length=0)

mv.label_line_ends(ax, fmt="{:.1f}%")                                          # the estimate
mv.callout(ax, (27, hi), "80% range", f"{pct(lo)}–{pct(hi)}", xytext=(6, 14), arrow=False)
mv.callout(ax, (19, now), f"{pct(now)} now", xytext=(-70, -24), arrow=False)
mv.titles(fig, f"Attrition should keep falling, to about {pct(end, 0)} by FY28, "
               f"but even the best case misses the {GOAL}% goal",
          "Voluntary attrition, enterprise, annualized, FY22–FY26 actual, FY27–FY28 forecast (%)")
mv.source(fig, "Source: synthetic data for illustration only; quarterly, all U.S. regular employees",
          footnote="Estimate = trend + seasonal model; shaded range = 80% prediction interval.")'''

CELL4 = '''\
mv.lint(fig)                                   # house rules: 0 errors before it ships
mv.save(fig, "fc_after.png", dpi=250)'''

# the lines shown unfolded in cell 3 (the helpers), in the order the narration names them
SHOWN = {
    "estimate": 'mv.label_line_ends(ax, fmt="{:.1f}%")',
    "range": 'mv.callout(ax, (27, hi), "80% range", f"{pct(lo)}–{pct(hi)}", xytext=(6, 14), arrow=False)',
    "headline": 'mv.titles(fig, f"Attrition should keep falling, to about {pct(end, 0)} by FY28, "',
}


def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = None
        lines = code.rstrip().split("\n")
        body, last = "\n".join(lines[:-1]), lines[-1]
        if last and not last.startswith((" ", "plt.", "mv.", "import", "from")) and "=" not in last.split("(")[0]:
            exec(compile(body, "<cell>", "exec"), ns)       # Jupyter shows the value of a trailing expression
            res = eval(compile(last, "<cell>", "eval"), ns)
        else:
            exec(compile(code, "<cell>", "exec"), ns)
    return buf.getvalue(), res


def fresh():
    plt.close("all")
    plt.rcdefaults()
    return {}


def as_list(findings):
    return [{"level": f.level, "rule": f.rule, "message": f.message, "printed": str(f)} for f in findings]


os.chdir(WORK)
import sys  # noqa: E402

sys.path.insert(0, str(WORK))
import mckviz as mv  # noqa: E402  (to lint the before figure; the cells import it themselves)

# 1) The model + the default chart
ns = fresh()
_, table = run(CELL1, ns)
run(CELL2, ns)
fig_before = plt.gcf()
fig_before.savefig(ASSETS / "fc_before.png", dpi=200, bbox_inches="tight")
before_findings = mv.lint(fig_before, quiet=True)

# 2) The one-line change: the same cell 2 with mv.use() on top
ns = fresh()
run(CELL1, ns)
run(ONE_LINE + "\n" + CELL2, ns)
plt.gcf().savefig(ASSETS / "fc_one_line.png", dpi=200, bbox_inches="tight")

# 3) The helpers, then lint and save, exactly as written
ns = fresh()
run(CELL1, ns)
run(ONE_LINE + "\n" + CELL2, ns)
run(CELL3, ns)
lint_out, _ = run(CELL4, ns)
fig = ns["fig"]
after_findings = mv.lint(fig, quiet=True)
shutil.move(WORK / "fc_after.png", ASSETS / "fc_after.png")
fc = ns["fc"]
end, lo, hi = fc.iloc[-1][["mean", "lower", "upper"]]
headline = fig._mck["head"].get_text().replace("\n", " ")

result = {
    "note": "Real mv.lint output from mckviz (repo version). Data is synthetic and seeded. Cells ran in one namespace, "
            "in order, like a Jupyter kernel; fc_before.png is cell 2's figure as the inline backend shows it.",
    "cells": {"cell1_model": CELL1, "cell2_before": CELL2, "one_line": ONE_LINE, "cell3_helpers": CELL3,
              "cell4_lint_and_save": CELL4, "cell3_shown": SHOWN, "cell3_lines": len(CELL3.split("\n"))},
    "model_output": table.to_string(),
    "forecast": {"last_actual": float(ns["df"].rate.iloc[-1]), "estimate": round(float(end), 1),
                 "low": round(float(lo), 1), "high": round(float(hi), 1), "goal": 12, "interval": 0.80},
    "headline": headline,
    "after": {"lint_printed": lint_out.strip(), "findings": as_list(after_findings),
              "errors": sum(f.level == "error" for f in after_findings)},
    "before": {"findings": as_list(before_findings), "errors": sum(f.level == "error" for f in before_findings)},
}
(ASSETS / "fc_lint.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
shutil.rmtree(WORK, ignore_errors=True)
print(json.dumps({k: result[k] for k in ("model_output", "forecast", "headline", "after", "before")}, indent=1,
                 ensure_ascii=False))
