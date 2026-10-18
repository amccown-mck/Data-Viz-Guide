# Eval cases for the mck-chart skill

Three small synthetic CSVs that are **not** the sample data the skill ships, with the facts a correct answer must contain (`cases.json`). The Claude.ai test on 2026-10-18 used a table identical to `attrition_by_job_family.csv`, so one headline matched the cookbook word for word; these cases measure reasoning, not copying.

| Case | What it tests |
|---|---|
| `time_to_fill_by_job_family.csv` | Ranking against a target; the 2-highlight limit; orange only as "worse"; no invented source or period |
| `engagement_by_site.csv` | Values clustered far from zero (dot plot, not truncated bars); **a site with 8 respondents that must be suppressed** |
| `internal_fill_two_periods.csv` | Two periods (slope or dumbbell, not a line); the biggest fall in orange and the biggest rise in blue; derived counts as estimates |

None of the files carries a source system, as-of date or period, on purpose: the skill should ask once or write the `[confirm source and as-of date]` placeholder, never invent one.

## Run it by hand

**Claude.ai:** upload the skill zip once (Settings › Capabilities › Skills, `dist/skills/mck-chart.zip` from `python tools/build_skill.py --zip`). Start a new chat, paste a CSV as a table, and send one of these prompts:

```
/mck-chart Can I have an exec-ready chart with a headline?
```
```
/mck-chart Give me 3 options that fit a storyline about <the case's question>.
```
Then, for one case: `Could you turn that into a PowerPoint slide?`

**Claude Code / Copilot:** with the skill in `.claude/skills/` or `.github/skills/`, run `/mck-chart` with the file path and the same prompt.

## What to record

Write one file per run under `runs/`, named `<date>-<tool>-<model>.md`, and commit it. Per case, record:

1. **Setup:** what `scripts/check_env.py` reported (installed from the local wheel, from GitHub, already installed, or the no-package fallback and which font).
2. **Chart family** chosen, and whether it is one of `chart_family` in `cases.json`.
3. **Focus rows** and their colors; whether any color broke a rule (orange as a plain highlight, green without ▲ or a word, red vs. green, more than 2 highlighted).
4. **Headline:** the sentence, and whether every number in it matches `headline_numbers` (recomputed, not eyeballed) and starts with a spelled-out number if it starts with one.
5. **Suppression** (case 2): whether Boise Clinic Support appeared anywhere, and whether the footnote says a site under 10 is not shown.
6. **Source line:** the placeholder or question, and whether a system name or period was invented.
7. **QA:** whether `mv.lint` ran, what the render-and-look step caught (label on the benchmark line, title wrapping, collisions), and the QA exceptions the brief listed.
8. **PowerPoint** (if asked): native chart or picture, title placeholder at 26 pt Bold McKesson Blue, overlays as shapes, speaker-notes caveat.
9. Anything the skill text did not cover, as a finding for `agents/skill/SKILL.template.md`.

`python -m pytest python/tests/test_eval_cases.py` checks that `cases.json` still matches the CSVs after an edit. No automated scoring yet; this is the fixture set the next test uses.
