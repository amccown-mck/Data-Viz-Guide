"""The eval fixtures stay honest: the expected facts in eval_cases/cases.json match the CSVs they describe."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

CASES = Path(__file__).parent / "eval_cases"
FACTS = json.loads((CASES / "cases.json").read_text(encoding="utf-8"))
SAMPLES = Path(__file__).resolve().parents[2] / "examples" / "data"


def case(name: str) -> tuple[dict, pd.DataFrame]:
    facts = FACTS[name]
    return facts, pd.read_csv(CASES / facts["file"])


@pytest.mark.parametrize("name", [k for k in FACTS if not k.startswith("$")])
def test_case_file_exists_and_differs_from_the_samples(name):
    facts, df = case(name)
    assert len(df) >= 6
    sample_names = {p.name for p in SAMPLES.glob("*.csv")}
    assert facts["file"] not in sample_names, "an eval case must not reuse a shipped sample file"
    for p in SAMPLES.glob("*.csv"):                              # nor its values
        s = pd.read_csv(p)
        if list(s.columns) == list(df.columns):
            assert not s.equals(df)


def test_time_to_fill_facts():
    facts, df = case("time_to_fill_by_job_family")
    n = facts["headline_numbers"]
    t = df.target_days.iloc[0]
    top = df.sort_values("median_days_to_fill", ascending=False)
    assert top.job_family.head(2).tolist() == facts["focus_rows"]
    assert top.median_days_to_fill.head(2).tolist() == [n["slowest_days"], n["second_days"]]
    assert t == n["target_days"] and len(df) == n["families"]
    assert int((df.median_days_to_fill > t).sum()) == n["over_target_count"]
    assert round(n["slowest_days"] / t, 1) == n["slowest_vs_target"]
    assert int(df.open_reqs.min()) >= 10 and str(int(df.open_reqs.sum())) in facts["source_expected"].replace(",", "")


def test_engagement_facts_and_suppression():
    facts, df = case("engagement_by_site")
    n = facts["headline_numbers"]
    ent = df.enterprise_favorable_pct.iloc[0]
    assert df[df.respondents < 10].site.tolist() == facts["suppressed_rows"]
    shown = df[df.respondents >= 10]
    below = shown[shown.favorable_pct < ent].sort_values("favorable_pct")
    assert below.site.tolist() == facts["focus_rows"], "exactly the two focus sites sit below the rate"
    assert below.favorable_pct.tolist() == [n["lowest_pct"], n["second_pct"]] and ent == n["enterprise_pct"]
    assert (ent - below.favorable_pct).tolist() == [n["gap_lowest_pts"], n["gap_second_pts"]]
    assert len(shown) == n["sites_shown"] and (shown.favorable_pct.min(), shown.favorable_pct.max()) == (n["shown_min"], n["shown_max"])
    assert n["shown_min"] > 40, "values must sit far from zero so a truncated bar chart is the trap"
    assert str(int(shown.respondents.sum())) in facts["source_expected"].replace(",", "")


def test_internal_fill_facts():
    facts, df = case("internal_fill_two_periods")
    n = facts["headline_numbers"]
    assert sorted(df.fiscal_year.unique()) == ["FY25", "FY26"]
    w = df.pivot(index="business_unit", columns="fiscal_year", values="internal_fill_pct")
    change = (w.FY26 - w.FY25).sort_values()
    fall, rise = change.index[0], change.index[-1]
    assert [fall, rise] == facts["focus_rows"]
    assert change.iloc[0] == n["biggest_fall_pts"] and change.iloc[-1] == n["biggest_rise_pts"]
    assert change.iloc[1] == n["second_fall_pts"] and change.iloc[-1] > change.iloc[-2], "the biggest rise is unique"
    assert (w.loc[fall, "FY25"], w.loc[fall, "FY26"]) == (n["biggest_fall_from"], n["biggest_fall_to"])
    assert (w.loc[rise, "FY25"], w.loc[rise, "FY26"]) == (n["biggest_rise_from"], n["biggest_rise_to"])
    assert int((change > 0).sum()) == n["units_up"] and len(change) == n["units"]
    assert int(df.hires.min()) >= 10 and str(int(df.hires.sum())) in facts["source_expected"].replace(",", "")


def test_overtime_facts_and_suppression():
    facts, df = case("overtime_by_dc")
    n = facts["headline_numbers"]
    net = df.network_avg_hrs.iloc[0]
    assert df[df.associates < 10].site.tolist() == facts["suppressed_rows"]
    shown = df[df.associates >= 10].sort_values("avg_overtime_hrs_per_week", ascending=False)
    assert shown.site.head(2).tolist() == facts["focus_rows"]
    assert shown.avg_overtime_hrs_per_week.head(2).tolist() == [n["top_hrs"], n["second_hrs"]] and net == n["network_avg_hrs"]
    assert [round(v - net, 1) for v in shown.avg_overtime_hrs_per_week.head(2)] == [n["top_gap_hrs"], n["second_gap_hrs"]]
    assert int((shown.avg_overtime_hrs_per_week > net).sum()) == n["above_count"] and len(shown) == n["sites_shown"]
    assert str(int(shown.associates.sum())) in facts["source_expected"].replace(",", "")
    assert abs((shown.associates * shown.avg_overtime_hrs_per_week).sum() / shown.associates.sum() - net) < 0.1
