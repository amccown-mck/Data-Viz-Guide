"""Tests for the packaging and helper functions: version, bundled fonts, fmt_num, suppress_small, mckviz.geo."""
from __future__ import annotations

import warnings
from pathlib import Path

import pytest

import mckviz as mv

MINUS = "−"
REPO = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------------------------------------- version and fonts
def test_version_matches_repo_version_file():
    assert mv.__version__.count(".") == 2
    repo_version = REPO / "VERSION"
    if repo_version.exists():                       # in the repo: the package copy is synced by tokens/build.py
        assert mv.__version__ == repo_version.read_text(encoding="utf-8").strip()


def test_fonts_ship_inside_the_package():
    folder = mv._find_fonts()
    assert folder == Path(mv.__file__).parent / "fonts"
    assert (folder / "LibreFranklin-Regular.ttf").exists() and (folder / "OFL.txt").exists()


def test_use_registers_libre_franklin_without_warning():
    from matplotlib import font_manager as fm

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        mv.use()
    assert "LibreFranklin" in Path(fm.findfont(mv.FONT, fallback_to_default=False)).name


def test_use_warns_once_when_fonts_are_missing(monkeypatch):
    monkeypatch.setattr(mv, "register_fonts", lambda: False)
    monkeypatch.setattr(mv, "_FONT_WARNED", False)
    with pytest.warns(UserWarning, match="Libre Franklin"):
        mv.use()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        mv.use()                                     # second call: silent


# ----------------------------------------------------------------------------------------------- fmt_num
@pytest.mark.parametrize("args, kw, expected", [
    ((4_292_000_000,), {"prefix": "$"}, "$4.3B"),
    ((-71.4e6, "M"), {"prefix": "$"}, f"{MINUS}$71M"),
    ((12_480,), {}, "12K"),
    ((8_430,), {}, "8,430"),
    ((999_960,), {}, "1.0M"),
    ((1_234.5, "K"), {}, "1.2K"),
    ((1_500_000, "K"), {}, "1,500K"),
    ((19.94, "pct"), {}, "19.9%"),
    ((2.5, "pct"), {"sign": True}, "+2.5%"),
    ((-11.46, "pct"), {}, f"{MINUS}11.5%"),
    ((-0.04, "pct"), {}, "0.0%"),
    ((42, "plain"), {"sign": True}, "+42"),
    ((0.123, "pct"), {"decimals": 0}, "0%"),
    ((3_456, "plain"), {"suffix": " people"}, "3,456 people"),
    ((None,), {}, "–"),
    ((float("nan"),), {}, "–"),
])
def test_fmt_num(args, kw, expected):
    assert mv.fmt_num(*args, **kw) == expected


def test_fmt_num_never_uses_a_hyphen_minus():
    assert "-" not in mv.fmt_num(-1234) and mv.fmt_num(-1234).startswith(MINUS)


def test_fmt_num_rejects_unknown_kind():
    with pytest.raises(ValueError):
        mv.fmt_num(1, "T")


# ----------------------------------------------------------------------------------------------- suppress_small
pd = pytest.importorskip("pandas")


def _families(small=(6, 5)):
    return pd.DataFrame({"family": ["Pharmacy Ops", "Distribution", "Finance", "Legal", "Security"],
                         "n": [240, 180, 40, *small], "leavers": [60, 30, 4, 2, 1],
                         "rate": [25.0, 16.7, 10.0, 2 / small[0] * 100, 1 / small[1] * 100]})


def test_suppress_small_merges_into_other():
    out, note = mv.suppress_small(_families(), "n", sum_cols=["leavers"])
    assert list(out.family) == ["Pharmacy Ops", "Distribution", "Finance", "Other"]
    other = out.iloc[-1]
    assert other.n == 11 and other.leavers == 3                   # counts are summed
    assert other.rate == pytest.approx(3 / 11 * 100)               # rates are n-weighted
    assert out.n.dtype == _families().n.dtype
    assert note == '2 groups with fewer than 10 people merged into "Other".'


def test_suppress_small_drops_a_merged_row_still_under_min_n():
    out, note = mv.suppress_small(_families(small=(6, 3)), "n", sum_cols=["leavers"])
    assert list(out.family) == ["Pharmacy Ops", "Distribution", "Finance"] and (out.n >= 10).all()
    assert note == "2 groups with fewer than 10 people not shown."


def test_suppress_small_can_drop_instead_of_merge():
    out, note = mv.suppress_small(_families(), "n", other_label=None)
    assert len(out) == 3 and note == "2 groups with fewer than 10 people not shown."


def test_suppress_small_leaves_clean_data_alone():
    df = _families(small=(12, 15))
    out, note = mv.suppress_small(df, "n")
    assert note == "" and out.equals(df)


def test_suppress_small_merges_into_an_existing_other_row_and_within_by():
    df = pd.DataFrame({"quarter": ["Q1"] * 4 + ["Q2"] * 4,
                       "family": ["Ops", "Finance", "Legal", "Other"] * 2,
                       "n": [200, 40, 4, 20, 210, 8, 30, 3]})
    out, note = mv.suppress_small(df, "n", by="quarter")
    q1 = out[out.quarter == "Q1"].set_index("family").n.to_dict()
    q2 = out[out.quarter == "Q2"].set_index("family").n.to_dict()
    assert q1 == {"Ops": 200, "Finance": 40, "Other": 24}
    assert q2 == {"Ops": 210, "Legal": 30, "Other": 11}
    assert (out.n >= 10).all()
    assert note == '2 groups with fewer than 10 people merged into "Other".'   # the existing Other isn't counted


# ----------------------------------------------------------------------------------------------- geo
def test_geo_reads_the_packaged_maps():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from mckviz import geo

    assert mv.geo is geo
    for name in geo.FILES:
        assert (geo.GEO / name).exists()
    fig = plt.figure(figsize=(6, 4))
    ax = geo.canvas(fig)
    m = geo.Map("states-albers-10m.json", "states", (0, 0, 432, 288), key=geo.FIPS.get)
    assert len(m.rings) == 51                                       # 50 states and DC
    m.draw(ax, {"TX": mv.colors.focus}, default=mv.colors.context_light)
    x, y = m.point(-96.80, 32.78)                                   # Dallas lies inside Texas
    assert m.path("TX").contains_point((x, y))
    world = geo.Map("countries-110m.json", "countries", (0, 0, 432, 220), project=geo.equal_earth, min_area=2)
    assert len(world.rings) > 150
    plt.close(fig)
