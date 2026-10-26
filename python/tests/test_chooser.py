"""Tests for mv.suggest and the decision tree: every sample dataset lands on the right shape, the conditions fire on the
data that has them, and the tree file is consistent with the code and the cookbook."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

import mckviz as mv

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "examples" / "data"

# sample dataset -> the shape mv.suggest must rank first
FIRST = {
    "attrition_by_job_family": "cat_measure", "attrition_quarterly": "time", "automation_exposure": "cat_measures",
    "compa_ratio_individuals": "people", "dc_vacancy_overtime": "time", "engagement_items": "composition",
    "engagement_vs_benchmark": "matrix", "headcount_bridge": "bridge", "initiative_milestones": "plans",
    "initiative_plan": "plans", "initiative_status_history": "plans", "labor_cost_bridge": "bridge",
    "mobility_flows": "flows", "pay_vs_market": "pairs", "pharm_tech_north_texas": "geo",
    "pharmacist_time_mix": "time", "remote_care_agents": "geo", "reskilling_pipeline": "flows",
    "skills_demand_rank": "pairs", "skills_overlap": "sets", "span_of_control": "people",
    "succession_coverage_bu": "pairs", "talent_market_by_state": "pairs", "workforce_mix": "composition",
    "data_ai_talent_by_country": "geo", "dc_network": "geo",
}


def suggest(name, **kw):
    return mv.suggest(pd.read_csv(DATA / f"{name}.csv"), **kw)


def holds(s, shape):
    m = next(x for x in s.shapes if x.id == shape)
    return {f.when for leaf in m.leaves for f in leaf.further if f.holds}


def trig(key):
    return mv.chooser.TREE["triggers"][key]


@pytest.mark.parametrize("name,shape", sorted(FIRST.items()))
def test_sample_lands_on_its_shape(name, shape):
    s = suggest(name)
    assert s.shapes and s.shapes[0].id == shape, [x.id for x in s.shapes]


def test_size_column_offers_richer_charts_but_the_bar_stays_the_answer():
    s = suggest("automation_exposure")
    assert trig("has_size") in holds(s, "cat_measure")
    leaf = next(x for x in s.shapes if x.id == "cat_measure").leaves
    assert any(lf.type.startswith("magnitude (derived") for lf in leaf)      # rate × headcount
    assert "Option: Bubble strip" in str(s) and "Option: Treemap" in str(s)
    rank = next(lf for lf in leaf if lf.type == "magnitude / ranking")
    assert all(f.only_if for f in rank.further if f.holds)                   # no rule forces a switch here
    assert "Sorted bar  -> cookbook/bar.md  (ax.barh + mv.highlight + mv.label_bars)  <- the answer here" in str(s)


def test_benchmark_opens_the_deviation_question():
    s = suggest("attrition_by_job_family")
    types = [lf.type for lf in next(x for x in s.shapes if x.id == "cat_measure").leaves]
    assert "deviation" in types


def test_conditions_fire_on_the_data_that_has_them():
    assert trig("ranks") in holds(suggest("skills_demand_rank"), "pairs")
    assert trig("many_series") in holds(suggest("attrition_quarterly"), "time")
    assert trig("two_units") in holds(suggest("dc_vacancy_overtime"), "time")
    assert trig("parts_over_time") in holds(suggest("pharmacist_time_mix"), "time")
    assert trig("parts_ordered") in holds(suggest("engagement_items"), "composition")
    assert trig("has_groups") in holds(suggest("compa_ratio_individuals"), "people")
    assert trig("counts_not_rates") in holds(suggest("remote_care_agents"), "geo")
    assert trig("many_categories") in holds(suggest("dc_network"), "cat_measure")


def test_workforce_mix_colors_every_part():
    s = suggest("workforce_mix")
    leaf = s.shapes[0].leaves[0]
    assert leaf.color == "Categorical" and not any(f.holds for f in leaf.further)


def test_hints_override_the_guesses():
    df = pd.DataFrame({"team": list("ABCDEFGH"), "a": [3, 5, 2, 8, 6, 4, 7, 1], "b": [10, 30, 20, 50, 40, 60, 80, 70]})
    s = mv.suggest(df, measure="b", size="a")
    m = next(x for x in s.shapes if x.id == "cat_measure")
    assert "b per team, a as a count" in m.evidence[0]


def test_report_names_the_path_and_what_the_data_cannot_support():
    text = str(suggest("attrition_by_job_family"))
    assert "Path:" in text and "Start with: Sorted bar" in text
    assert "change over time: it needs two or more periods" in text


def test_tree_is_consistent_with_code_and_cookbook():
    spec = importlib.util.spec_from_file_location("build_chooser", ROOT / "tools" / "build_chooser.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    tree = json.loads((ROOT / "tokens" / "chooser.json").read_text(encoding="utf-8"))
    assert build.check(tree) == []
    assert tree == mv.chooser.TREE                                              # the package copy is current
    assert (ROOT / "docs" / "chart-decision-tree.md").read_text(encoding="utf-8") == build.markdown(tree)
