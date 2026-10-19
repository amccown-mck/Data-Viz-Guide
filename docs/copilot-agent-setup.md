# A McKesson chart agent in Microsoft 365 Copilot

How to build a Copilot agent in **Agent Builder** that makes and reviews McKesson-standard charts, using the Copilot edition of the `mck-chart` skill. An Agent Builder agent is the easiest way to give the kit to colleagues: they open it from Copilot chat, with nothing to install.

## What you need
- A Microsoft 365 Copilot license, with your organization in the **Microsoft Frontier Program**. Skills in Agent Builder are in preview and only appear there ([Microsoft: add custom skills in Agent Builder](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/agent-builder-add-skills)).
- **`mck-chart-copilot.zip`**: in the release bundle (`agents/mck-chart-copilot-skill.zip`), or build it from the repo with `python tools/build_skill.py --copilot` (it lands in `dist/skills/`).

## Why a separate edition
Agent Builder accepts a skill as a `.zip` with `SKILL.md` at its root, and only certain file types. Its sandbox can't install packages or reach the internet. The Claude skill (`mck-chart.zip`) breaks all three rules: its files sit in a folder, it carries `.ttf`, `.whl`, `.potx`, `.css` and `.R` files, and its setup installs a wheel. The Copilot edition has the same workflow and references. It ships `mckviz` as Python source with a setup script (`scripts/mck_setup.py`) that assembles the package and the Libre Franklin font in the sandbox. `tools/build_skill.py` checks every Agent Builder limit (file types, at most 3 levels deep, 350 files, 25 MB a file, 50 MB a zip, instructions under 20,000 characters) and fails the build if one is broken.

What it leaves out: the web and R themes and the PowerPoint template. Copilot shows charts as images, and colleagues get the template from the release bundle.

## Set up the agent
1. In Copilot chat, open **Agents** (or **Agents & Skills**), then **New agent**, and switch to **Configure**. To add the skill to an agent you already have, open it in Agent Builder and go to **Configure**.
2. **Name and description**: for example "McKesson Chart Coach: turns your data into an executive-ready chart, or reviews one you have".
3. **Instructions**: paste the block below. The skill holds the detail, so the instructions stay short (the limit is 8,000 characters).
4. **Skills**: select **Add**, then **Upload skill**, and upload `mck-chart-copilot.zip` (the whole zip, not `SKILL.md` on its own).
5. **Capabilities**: turn on **Code interpreter** (Agent Builder may call it data analysis; the skill draws charts in Python). Turn **Image generation off**, so the agent never draws a picture *of* a chart.
6. **Knowledge**: leave the uploaded files empty for now. During the preview, an agent can't have both skills and uploaded (embedded) files.
7. Test it in the preview pane (see [Try it](#try-it)), then select **Create** and share it.

### Instructions to paste
```text
You are the McKesson Chart Coach for Workforce Innovation. You help colleagues turn data into charts an executive gets at a glance, and you review charts they already have.

For any request to make, fix or review a chart, graph, table, scorecard or exhibit, use the mck-chart skill and follow its workflow in order: question, chart type, build, headline, QA. Load mckviz with the skill's setup script before drawing.

Draw every chart in Python with mckviz and show the PNG it saves. Never use Copilot's built-in chart card: it can't follow the McKesson style. If Python can't run, say so plainly instead of drawing the chart another way.

Always:
- Compute every number in a headline from the data. Never estimate from a picture without saying so.
- Grey for context, McKesson Blue for what the headline names. Orange only for "worse", green only for "better".
- Never show a group of fewer than 10 people, in a chart, a label or a table.
- Never invent a source system, date or period. Use the placeholder the skill describes and say so.
- Hand back the chart, the chart brief and alt text. When the chart is going into a deck that leaves the team, also give the steps to build it as a native PowerPoint or Excel chart.

Keep replies short and plain. Ask one question at most when the data or the audience is unclear.
```

### Conversation starters
| Title | Prompt |
|---|---|
| Chart my data | Here's a table of my data. What's the one chart that makes the point, and can you build it? |
| Review my chart | Review this chart against the McKesson standard and tell me the three changes that matter most. |
| Three options | Give me three chart options for this storyline, and tell me which one to lead with. |
| Write the headline | Write an insight headline, subtitle and source line for this chart. |
| Build it in PowerPoint | Walk me through building this as a native, editable PowerPoint chart. |
| Which chart? | I want to show how attrition changed by job family over two years. Which chart should I use? |

## Try it
In the preview pane, check each of these before you share:
- **Setup loads.** Ask "Chart the sample attrition data in the skill (assets/data/attrition_by_job_family.csv)". The agent should run `mck_setup.py` and get back `font: Libre Franklin` and `ready`. If it says the font fell back, the chart still works, but the labels are wider.
- **The chart is in house style.** Grey bars with the two highest in blue, labels on the bar ends, a headline that is a full sentence with a number, and a source line.
- **Your own data.** Paste a small table with one group under 10 people. That group should be merged into "Other" or dropped, with a footnote saying so.
- **Review.** Paste a screenshot of an old chart and ask for a review. You should get a ranked list of fixes, then an offer to redraw it.

**If the chart comes back as an interactive "Chart" card** (a `</>` icon, rounded bars, gridlines, an axis instead of labels on the bars, a "Y" axis title, no source line), the agent used Copilot's built-in chart instead of the skill's Python. Check that Code interpreter is on and that the instructions above are pasted, then ask: *"Run scripts/mck_setup.py from the mck-chart skill and show me exactly what it prints."* The answer tells you whether Python runs and where the skill's files are; send it to whoever maintains the kit.

If the agent can't run the script at all, it falls back to building with the colors from `references/rules.md` and says so in its reply. Note what happened (the sandbox message) and open an issue on the repo.

## Keeping it current
When the kit changes, rebuild the zip (`python tools/build_skill.py --copilot`), then in Agent Builder remove the skill, upload the new zip, and select **Update**. The agent you shared then uses the new version.
