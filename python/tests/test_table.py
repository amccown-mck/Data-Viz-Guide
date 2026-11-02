"""Tests for mv.table: the tables.md spec in one call."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
from matplotlib.colors import to_hex  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import mckviz as mv  # noqa: E402

C = mv.colors
DATA = Path(__file__).resolve().parents[2] / "examples" / "data"


@pytest.fixture(autouse=True)
def _style():
    mv.use(plotly_default=False)
    yield
    plt.close("all")


@pytest.fixture
def scorecard():
    return pd.read_csv(DATA / "job_family_scorecard.csv").sort_values("vol_attrition_pct", ascending=False)


COLS = [mv.Col("headcount", "Headcount", "bar", agg="sum"),
        mv.Col("vol_attrition_pct", "Voluntary\nattrition (%)", "heat", fmt="{:.1f}"),
        mv.Col("attrition_change_pts", "Change vs.\nFY25 (pts)", "delta", worse="up")]


def texts(ax):
    return {t.get_text(): t for t in ax.texts}


def test_scorecard_follows_the_spec(scorecard):
    fig, ax = plt.subplots(figsize=(10, 5))
    focus = {"Pharmacy Technician", "Distribution Center Associate"}
    t = mv.table(ax, scorecard, "job_family", COLS, focus=focus, weights="headcount", total_label="All 8 job families")
    mv.titles(fig, "Two frontline job families combine the highest attrition with falling engagement", "Scorecard, FY26")
    mv.source(fig, "Source: Synthetic data for illustration only", footnote=" ".join(t.notes))
    mv.layout(fig)
    assert not [f for f in mv.lint(fig, quiet=True) if f.level == "error"]
    tx = texts(ax)
    assert tx["Pharmacy Technician"].get_fontweight() == "bold" and tx["Sales"].get_fontweight() == "normal"
    assert tx["+0.4"].get_color() == C.negative_text                           # a rise is worse: orange text
    assert tx["−5.6"].get_color() != C.negative_text                            # true minus, not colored
    assert tx[f"{scorecard.headcount.sum():,.0f}"].get_fontweight() == "bold"   # total row sums the counts
    w = (scorecard.vol_attrition_pct * scorecard.headcount).sum() / scorecard.headcount.sum()
    assert f"{w:.1f}" in tx                                                     # and weights the rate
    fills = {to_hex(p.get_facecolor()).upper() for p in ax.patches if isinstance(p, Rectangle)}
    assert mv.SEQUENTIAL["blue"][-1].upper() in fills and mv.SEQUENTIAL["blue"][0].upper() in fills
    assert any("shaded light to dark" in n for n in t.notes) and any("weighted" in n for n in t.notes)


def test_diverging_column_and_suppression():
    df = pd.DataFrame({"team": ["A", "B", "C", "D"], "n": [40, 25, 6, 30], "gap": [-6.0, -1.0, 2.0, 4.0]})
    fig, ax = plt.subplots(figsize=(8, 3))
    t = mv.table(ax, df, "team", [mv.Col("gap", "Gap (pts)", "heat", fmt="{:+.1f}", scale="diverging")], n="n")
    tx = texts(ax)
    assert "n<10" in tx and "+2.0" not in tx                                    # team C (6 people) is suppressed
    fills = [to_hex(p.get_facecolor()).upper() for p in ax.patches]
    assert mv.DIVERGING[0].upper() in fills                                     # the largest shortfall, darkest orange
    assert any("n<10" in n for n in t.notes)


def test_limits_are_enforced(scorecard):
    fig, ax = plt.subplots(figsize=(10, 5))
    heat3 = [mv.Col(c, c, "heat") for c in ("vol_attrition_pct", "internal_fill_pct", "engagement_index")]
    with pytest.raises(ValueError, match="at most two columns"):
        mv.table(ax, scorecard, "job_family", heat3)
    fig, ax = plt.subplots(figsize=(3, 3))
    wide = COLS + [mv.Col("median_days_to_fill", "Median days to fill a requisition")]
    with pytest.raises(ValueError, match="widen the figure"):
        mv.table(ax, scorecard, "job_family", wide)
