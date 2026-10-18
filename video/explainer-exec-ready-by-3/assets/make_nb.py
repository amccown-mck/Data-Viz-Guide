"""Notebook story for the explainer: run the exact cell strings in one namespace (like a Jupyter kernel),
capture real mv.lint output, and write nb_before.png, nb_one_line.png, nb_draft.png, nb_after.png, nb_lint.json.

Run:  .venv/bin/python out/explainer/assets/make_nb.py   (from the repo root)
The cells run in a scratch folder that holds a link to examples/data/attrition_by_job_family.csv, so the code on
screen reads the CSV by its bare name. Cell 1's figure is saved the way Jupyter's inline backend shows it
(bbox_inches="tight"); cells 2-3 save through mv.save exactly as written.
"""
import contextlib
import io
import json
import os
import shutil

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", message=".*non-interactive.*")

REPO = Path(__file__).resolve().parents[3]
ASSETS = Path(__file__).resolve().parent
RAW = ASSETS / "raw"
RAW.mkdir(exist_ok=True)
WORK = Path(os.environ.get("NB_WORKDIR", ASSETS / "_nbwork"))
WORK.mkdir(parents=True, exist_ok=True)
csv = WORK / "attrition_by_job_family.csv"
if not csv.exists():
    shutil.copy(REPO / "examples/data/attrition_by_job_family.csv", csv)
os.chdir(WORK)

CELL1 = '''\
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("attrition_by_job_family.csv")
df.plot.bar(x="job_family", y="vol_attrition_pct", figsize=(10, 5))
plt.title("Attrition by job family")
plt.show()'''

_CELL2_HEAD = '''\
import mckviz as mv; mv.use()                      # the one line: McKesson fonts, colors, style

df = df.sort_values("vol_attrition_pct")
top, ent = df.tail(2), df.enterprise_rate_pct.iloc[0]
fig, ax = plt.subplots(figsize=(10, 5.2))
bars = ax.barh(df.job_family, df.vol_attrition_pct, height=0.67,
               color=mv.highlight(df.job_family, focus=top.job_family))
mv.label_bars(ax, bars, fmt="{:.1f}%")
ax.axvline(ent, color=mv.colors.total, lw=0.75, ls="--")
ax.text(ent, len(df) - 0.4, f"Enterprise {ent}%", ha="center", fontsize=9,
        color=mv.colors.annotation, backgroundcolor="white")
mv.clean_axes(ax, keep=("left",), grid=None); ax.set_xticks([])
for t in ax.get_yticklabels():
    if t.get_text() in set(top.job_family): t.set(fontweight="bold", color=mv.colors.headline)
'''

CELL2_DRAFT = _CELL2_HEAD + '''\
mv.titles(fig, "Attrition by job family", "Voluntary attrition by job family, FY26 (%)")'''

CELL2 = _CELL2_HEAD + '''\
mv.titles(fig, f"Two frontline job families lose about 1 in {100 / top.vol_attrition_pct.mean():.0f} "
               f"people a year, well above the {ent}% enterprise rate", "Voluntary attrition by job family, FY26 (%)")
mv.source(fig, "Source: Synthetic HRIS data for illustration only; FY26, all job families",
          footnote="Voluntary attrition = voluntary exits ÷ average headcount, trailing 12 months")'''

CELL3 = '''\
mv.lint(fig)                                   # house rules: 0 errors before it ships
mv.save(fig, "nb_after.png", dpi=200)          # lays out headline, subtitle and source'''

CELL3_DRAFT = '''mv.lint(fig)'''


def run(code, ns):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<cell>", "exec"), ns)
    return buf.getvalue()


def fresh():
    plt.close("all")
    plt.rcdefaults()                     # a fresh kernel: mv.use() only changes rcParams (+ registers fonts)
    return {}


def as_list(findings):
    return [{"level": f.level, "rule": f.rule, "message": f.message, "printed": str(f)} for f in findings]


import mckviz as mv  # noqa: E402  (only for linting the "before" figure; the cells import it themselves)

# 1) Before: plain matplotlib defaults
ns = fresh()
run(CELL1, ns)
fig_before = plt.gcf()
fig_before.savefig(RAW / "nb_before.png", dpi=200, bbox_inches="tight")
before_findings = mv.lint(fig_before, quiet=True)

# 2) The literal one-line change: the same cell 1, with mv.use() on top
ns = fresh()
run("import mckviz as mv; mv.use()\n" + CELL1, ns)
plt.gcf().savefig(RAW / "nb_one_line.png", dpi=200, bbox_inches="tight")

# 3) Rushed draft: label headline, no source line
ns = fresh()
run(CELL1, ns)
run(CELL2_DRAFT, ns)
draft_out = run(CELL3_DRAFT, ns)
draft_findings = mv.lint(ns["fig"], quiet=True)
mv.save(ns["fig"], RAW / "nb_draft.png", dpi=200)

# 4) Final: cells 1, 2, 3 exactly as written
ns = fresh()
run(CELL1, ns)
run(CELL2, ns)
final_out = run(CELL3, ns)
final_findings = mv.lint(ns["fig"], quiet=True)
shutil.move(WORK / "nb_after.png", RAW / "nb_after.png")
headline = ns["fig"]._mck["head"].get_text().replace("\n", " ")

result = {
    "note": "Real mv.lint output from mckviz (repo version). Data is synthetic. Cells ran in one namespace, in "
            "order, like a Jupyter kernel; nb_before.png is cell 1's figure saved as the inline backend shows it.",
    "cells": {
        "cell1_before": CELL1,
        "cell2_kit": CELL2,
        "cell3_lint_and_save": CELL3,
    },
    "draft": {
        "what_is_missing": "Label-style headline with no finding or number, and no source line (mv.source omitted)",
        "cell2_draft": CELL2_DRAFT,
        "cell3_draft": CELL3_DRAFT,
        "lint_printed": draft_out.strip(),
        "findings": as_list(draft_findings),
        "errors": sum(f.level == "error" for f in draft_findings),
    },
    "final": {
        "headline": headline,
        "lint_printed": final_out.strip(),
        "findings": as_list(final_findings),
        "errors": sum(f.level == "error" for f in final_findings),
    },
    "before_default_chart": {
        "note": "mv.lint run on the default matplotlib figure from cell 1 (bonus)",
        "findings": as_list(before_findings),
        "errors": sum(f.level == "error" for f in before_findings),
    },
}
(ASSETS / "nb_lint.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: result[k] for k in ("draft", "final", "before_default_chart")}, indent=1, ensure_ascii=False))
