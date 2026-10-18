"""Render the two demo outputs that no gallery writes as a PNG: the KPI card and the roadmap the explainer video shows.

Both follow the cookbook recipes (docs/cookbook/kpi-big-number.md, docs/cookbook/plans-status.md) on the synthetic
example data, pass mv.lint, and land next to this file. The other demo outputs are linked from examples/output/,
dist/office/ and the video's chart assets.

Run (from the repo root):  python demo/make_demo.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

import mckviz as mv  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
mv.use()
C = mv.colors

# --- KPI card: one number, one sentence, the change and the gap to target ------------------------------------------
value, prior, target, n_roles = 62, 48, 75, 410                  # % of critical roles with a ready-now successor
delta = value - prior
fig, ax = plt.subplots(figsize=(8, 3.6))
mv.kpi_card(ax, value, f"{round(n_roles * value / 100)} of {n_roles} critical roles now have at least one "
            "ready-now successor", change=delta, vs=f"vs. Mar 2025 ({prior}%)", target=target, ring_value=value)
mv.titles(fig, f"Succession coverage rose {delta} points in a year but is still short of the {target}% target",
          f"Critical roles with at least one ready-now successor, Mar 2026 (% of {n_roles} roles)")
mv.source(fig, "Source: Synthetic data for illustration only",
          footnote="Ready-now = assessed in the FY26 talent review as able to step in within 12 months.")
mv.lint(fig, strict=True)
mv.save(fig, HERE / "kpi-card.png", dpi=150)

# --- Roadmap: workstreams, milestones, a Today line, the slip ------------------------------------------------------
plan = pd.read_csv(REPO / "examples/data/initiative_plan.csv")
ms = pd.read_csv(REPO / "examples/data/initiative_milestones.csv")
off = plan[plan.status == "off_track"]
dep = off.depends_on.iloc[0]
words = {2: "Two", 3: "Three"}
fig, ax = plt.subplots(figsize=(11, 4.5))
mv.roadmap(ax, plan, ms, start="2025-04", end="2027-03", today="2026-03", today_label="Today, 31 Mar 2026")
mv.titles(fig, f"{words[len(off)]} of {len(plan)} workstreams are off track, both waiting on the "
               f"{dep.lower().replace(' rollout', '')}'s Workday integration",
          "Workforce Innovation roadmap by workstream, FY26–FY27, with status as of 31 Mar 2026")
mv.source(fig, "Source: Workforce Innovation PMO (synthetic data for illustration only), as of 31 Mar 2026")
mv.lint(fig, strict=True)
mv.save(fig, HERE / "roadmap.png", dpi=150)
print("wrote", HERE / "kpi-card.png", "and", HERE / "roadmap.png")
