"""Draw the BAD chart for "The meeting" (scene s-open): assets/meet_bad.png.

On purpose, this uses plain matplotlib defaults (no mckviz): 12 colors, a second
y-axis, a legend over the data, gridlines, and the title "Chart Title".
Run from the repo root: .venv/bin/python video/explainer-the-meeting/assets/make_meeting.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

q = pd.read_csv(ROOT / "examples/data/attrition_quarterly.csv")          # 6 families x 12 quarters
hc = pd.read_csv(ROOT / "examples/data/attrition_by_job_family.csv").set_index("job_family")["headcount"]

fams = list(q.job_family.unique())
quarters = list(q.quarter.unique())                                        # 12 series -> 12 colors
wide = q.pivot(index="job_family", columns="quarter", values="attrition_pct").loc[fams, quarters]

fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
x = np.arange(len(fams))
n = len(quarters)
w = 0.8 / n
colors = plt.cm.tab20(np.linspace(0, 1, n))                                # the rainbow
for i, col in enumerate(quarters):
    ax.bar(x + (i - n / 2) * w + w / 2, wide[col].values, w, label=col, color=colors[i])
ax.set_xticks(x)
ax.set_xticklabels(fams, rotation=20, ha="right")
ax.set_ylabel("Attrition %")
ax.grid(True)
ax.set_title("Chart Title")

ax2 = ax.twinx()                                                            # the second axis
ax2.plot(x, hc.loc[fams].values, "o-", color="tab:red", linewidth=2.5, label="Headcount")
ax2.set_ylabel("Headcount")
ax2.grid(True, linestyle="--")

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper center", ncol=2, fontsize=11)        # sits on the data

fig.savefig(HERE / "meet_bad.png", dpi=100)
print("wrote", HERE / "meet_bad.png")
