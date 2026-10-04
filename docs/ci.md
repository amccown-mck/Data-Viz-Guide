# Checking charts in CI

`mv.lint(fig, strict=True)` raises `mckviz.LintError` when a matplotlib or Plotly figure breaks a house rule at "error" level: a missing headline, subtitle or source, more than 6 colors, off-palette or red–green colors, bars not starting at zero. Dual axes, legends and text under the minimum size are reported at "warn" level, so they show in the log but don't fail the build. Any repo that builds charts in Python can run it on every push, so a broken chart fails the build instead of reaching a deck.

The lint checks the mechanics. It can't tell whether the headline is true or the chart type fits the question, so a person (or agent) still runs [qa-checklist.md](qa-checklist.md).

## 1. Make the chart code testable

Put each chart in a function that returns the figure, and save it in a separate step:

```python
# charts/attrition.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mckviz as mv


def attrition_chart(df):
    mv.use()
    fig, ax = plt.subplots(figsize=(10, 5))
    ...                                         # the cookbook recipe
    mv.titles(fig, headline, subtitle)
    mv.source(fig, "Source: Workday HCM, as of 31 Mar 2026; US employees")
    return fig
```

## 2. A test that lints every chart

```python
# tests/test_charts.py
import pandas as pd
import pytest
import mckviz as mv

from charts.attrition import attrition_chart

CHARTS = [attrition_chart]                      # add every chart function here


@pytest.mark.parametrize("make", CHARTS, ids=lambda f: f.__name__)
def test_chart_meets_house_rules(make):
    df = pd.read_csv("tests/data/attrition_sample.csv")   # small synthetic fixture, no real people data
    fig = make(df)
    mv.layout(fig)                              # place headline, subtitle and source as mv.save() would
    mv.lint(fig, strict=True)                   # raises on any error; warnings print but don't fail
```

For a Plotly chart whose headline, subtitle and source live in the page's HTML (the chart-card pattern), pass them in: `mv.lint(fig, headline=..., subtitle=..., source=..., strict=True)`.

## 3. The GitHub Actions workflow

Pin `mckviz` to a release tag so a new kit version never changes your build without a commit. The tag's fonts come with the package, so text is measured in Libre Franklin as it will be drawn.

```yaml
# .github/workflows/charts.yml
name: Chart lint
on: [push, pull_request]

jobs:
  lint-charts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install
        run: |
          pip install "mckviz @ git+https://github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"
          pip install pandas plotly pytest
      - name: Lint every chart
        run: pytest tests/test_charts.py -q
```

If the kit repo is private, give the job read access: create a fine-grained token with read access to the kit repo, store it as a secret (for example `KIT_TOKEN`), and install with `pip install "mckviz @ git+https://x-access-token:${{ secrets.KIT_TOKEN }}@github.com/amccown-mck/Data-Viz-Guide@v1.1.0#subdirectory=python"`. Without network access to GitHub, commit the wheel from the release bundle (`python/mckviz-<version>-py3-none-any.whl`) and `pip install` that file instead.

## Upgrading

Read [CHANGELOG.md](../CHANGELOG.md), change the tag in the workflow (and in `requirements.txt` if you pin it there too), and run the tests locally first: a palette or rule change in a new version can turn a passing chart into a failing one, which is the point.
