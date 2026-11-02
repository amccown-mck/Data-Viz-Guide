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
2. **Name and description**: the name is what colleagues see in Copilot chat (ours is "Data Storytelling Studio"). The description is shown to users and helps Copilot decide when the agent fits (1,000 characters at most):
   ```text
   Your own data storytelling team, ready when you are: charts that look like they came from a top consulting firm, without having to become a data viz expert. Paste a table or attach a spreadsheet and get an executive-ready chart in the McKesson style: the right chart type, an insight headline with numbers computed from your data, house colors and fonts, and a quality check. It also reviews charts you already have, offers options for a storyline, and turns a chart into an editable PowerPoint slide. Groups under 10 people are never shown. Built on the Data Viz Starter Kit, McKesson Edition, by Workforce Innovation.
   ```
3. **Instructions**: paste the block below. The skill holds the detail, so the instructions stay short (the limit is 8,000 characters). They repeat the few rules that matter most, because the instructions are always in context and the skill is loaded only when a request matches it.
4. **Skills**: select **Add**, then **Upload skill**, and upload `mck-chart-copilot.zip` (the whole zip, not `SKILL.md` on its own).
5. **Knowledge settings** (the gear next to Knowledge): turn on **Create documents, charts, and code** (the Python sandbox the skill draws in, and how it writes PowerPoint files). Turn **Create images off**, so the agent never draws a picture *of* a chart. Leave **People data** off.
6. **Knowledge**: leave the uploaded files empty for now. During the preview, an agent can't have both skills and uploaded (embedded) files. Under **Work content**, keep **Cloud files** on (so people can point the agent at a spreadsheet in OneDrive or SharePoint) and turn **Outlook**, **Teams** and **Web search** off: the agent should chart the data the user gives it, not search mail and chats, and web results invite sources nobody checked. Turn Web search back on only if you want external benchmarks, and then ask the agent to cite them in the source line.
7. Test it in the preview pane (see [Try it](#try-it)), then select **Create** (or **Update**) and share it.

### Instructions to paste
```text
You are Data Storytelling Studio, built by Workforce Innovation on McKesson's Data Viz Guide. You help colleagues make charts that look like they came from a top consulting firm, without having to become data viz experts: you pick the right chart, write the headline and build it, all the way to an editable PowerPoint slide, and you review charts they already have.

How you work
- For any request to make, fix or review a chart, graph, table, scorecard, slide or exhibit, use the mck-chart skill and follow its workflow in order: question, chart type, build, headline, QA.
- Build every chart in Python with mckviz. Start each script by running the skill's setup script (scripts/mck_setup.py), as the skill's Setup section shows.
- Show the finished chart as the PNG that mckviz saved, inline in your reply, with a download link. Never use Copilot's built-in interactive chart instead: it drops the McKesson style. If Python can't run, say so plainly rather than drawing the chart another way.
- Lead with what the user asked for. For a chart, reply as the skill's Hand-back says: the headline, the chart, then in plain words why this chart and what to check before sharing.

Rules you never break
- Compute every number in a headline from the data (shares, gaps, headcount-weighted averages). Never estimate from a picture without saying so.
- Grey for context and McKesson Blue for what the headline names. Orange only for "worse", green only for "better".
- Never show a group of fewer than 10 people: not in a chart, a label, a table or your text.
- Never invent a source system, date or period. Use the placeholder the skill describes and tell the user what to confirm.
- Say a chart passed QA only when the skill's lint ran clean and you looked at the image.

PowerPoint and Excel
- When the user asks for a slide or a deck, build a real .pptx with a native, editable chart, not a pasted picture: the headline as the slide title, the subtitle, direct labels, the source line at 9 pt or larger, Libre Franklin as the font, and no label sitting on a line or on another label.
Style
- Keep replies short and plain, for busy business readers. Ask one question at most, and only when the data or the audience is unclear.
- Use the data the user gives you. Don't search their email, chats or files for data unless they ask.
```

### Suggested prompts
Starters show on the agent's first screen. Each one works when clicked with nothing attached: the first runs on sample data built into the skill (a quick demo for someone new), and the others ask for the user's data.

| Title | Message |
|---|---|
| Try it on sample data | Show me what you can do: build an executive chart from the sample attrition data in your skill, then explain the choices you made. |
| Chart my data | I'll paste a table or attach a spreadsheet. Find the one chart that makes the point for an executive audience, and build it. |
| Review my chart | I'll share a chart. Review it against the McKesson standard, give me the three changes that matter most, then offer to redraw it. |
| Options for my story | I'll paste my data and the point I want to make. Give me three chart options, each with its own headline, and tell me which one to lead with. |
| Make it a slide | Turn the chart we just made into a PowerPoint slide with a native, editable chart I can share in a leadership meeting. |
| Which chart should I use? | Help me pick a chart. I'll tell you what I want to show and who will see it. |

## Try it
In the preview pane, check each of these before you share:
- **Setup loads.** Ask "Chart the sample attrition data in the skill (assets/data/attrition_by_job_family.csv)". The agent should run `mck_setup.py` and get back `font: Libre Franklin` and `ready`. If it says the font fell back, the chart still works, but the labels are wider.
- **The chart is in house style.** Grey bars with the two highest in blue, labels on the bar ends, a headline that is a full sentence with a number, and a source line.
- **Your own data.** Paste a small table with one group under 10 people. That group should be merged into "Other" or dropped, with a footnote saying so.
- **Review.** Paste a screenshot of an old chart and ask for a review. You should get a ranked list of fixes, then an offer to redraw it.

**If the chart comes back as an interactive "Chart" card** (a `</>` icon, rounded bars, gridlines, an axis instead of labels on the bars, a "Y" axis title, no source line), the agent used Copilot's built-in chart instead of the skill's Python. Check that **Create documents, charts, and code** is on and that the instructions above are pasted, then ask: *"Run scripts/mck_setup.py from the mck-chart skill and show me exactly what it prints."* The answer tells you whether Python runs and where the skill's files are; send it to whoever maintains the kit.

If the agent can't run the script at all, it falls back to building with the colors from `references/rules.md` and says so in its reply. Note what happened (the sandbox message) and open an issue on the repo.

## Keeping it current
When the kit changes, rebuild the zip (`python tools/build_skill.py --copilot`), then in Agent Builder remove the skill, upload the new zip, and select **Update**. The agent you shared then uses the new version.
