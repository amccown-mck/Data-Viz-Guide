# Positioning: what the kit is and how we describe it

This page is the source of truth for how the kit is named and described. The README, the guide's cover and overview, `START-HERE.html` in the release bundle, `demo/README.md` and the agent files all follow it. Change the wording here first, then carry it through.

**Second pass, 2026-10-18.** The first pass took its language from the explainer video: Sam's Tuesday, exec-ready by 3, the three hats. That story works in the video, which has a character and a clock to carry it. Product copy is read by people who haven't seen the video, so it now says in its own words what the kit is, why it matters, why it isn't another style guide, who it's for and what you get. It leads with what good looks like, not with a pain point, so it reads well to the people making charts and to the leaders reading them. The video keeps its own script (`video/explainer-exec-ready-by-3/`). Product copy doesn't quote it.

## Name

**Data Viz Starter Kit**, with **McKesson Edition** as a secondary tag after the name.

- Write "Data Viz Starter Kit · McKesson Edition" where there is room, "Data Viz Starter Kit" where there isn't. Never "McKesson Data Viz Starter Kit": the brand is an edition, not part of the name, because the kit is built to be re-branded from one file and other McKesson businesses (CoverMyMeds, Sarah Cannon, The US Oncology Network) can have their own editions.
- The parts keep their own names: **the guide** (Data Visualization Guide), **the cookbook**, **`mckviz`** (the Python package), **the themes**, **the `mck-chart` skill**.
- Don't use "Data-Viz-Guide" (the repository slug) or "the McKesson guide" as the product's name.

## One line

Your own data storytelling team, ready when you are.

## In one breath

A kit that helps anyone at McKesson make charts that look and read like a top consulting firm made them.

## What it is

Top consulting firms have a team behind every executive presentation, people whose whole job is turning analysis into a chart a leader gets at a glance. The Data Viz Starter Kit puts that know-how in your hands. You get a guide that teaches the craft, templates and code that start you off right in PowerPoint, Excel, Power BI and Python, and a quick check before you share. Your AI assistant can use it too.

## Why it matters

Clear charts move decisions forward. When the point of a chart is obvious, a meeting spends its time on what to do, not on what the chart means. That's the standard top consulting firms hold every chart to, and it's a craft anyone can learn with the right tools. This kit makes it the easy path for every McKesson team.

## Why it isn't another style guide

A style guide describes good charts. This kit makes them the default.

- **The rules are built into the tools.** Every color, font and chart rule lives in one file, `tokens/tokens.json`, and is generated into the PowerPoint template, the Excel workbook, the Power BI theme, the web and R themes and the `mckviz` Python package. A new chart starts on-brand instead of being fixed later. Change a line and every theme, template and example updates.
- **The rules are written to be checked.** Each one is testable. A reviewer has the QA checklist, code has `mv.lint`, and an AI assistant works from the rules and runs the checks itself before you see the chart.

## What you get: the team, piece by piece

The owner's own words for it: a mini consulting firm at the ready, top-notch data viz reproduced with ease. A consulting firm's charts look the way they do because of the data storytelling team behind them, not one talented person. The kit packages that team's know-how so anyone can have it:

| What a firm's team gives you | What the kit gives you |
|---|---|
| **A data storytelling expert who knows which chart** | **The guide and chart chooser.** Name the question; the chooser names the chart and says why. Fundamentals, formats and 12 chart families, plus a cheat sheet, as a website, a single offline file and a 16:9 PDF |
| **A house style** | **Themes and templates generated from one file**, for PowerPoint, Excel, Power BI, HTML/CSS, Plotly, Vega-Lite, matplotlib and ggplot2, with native, editable Office charts |
| **Worked examples to copy** | **The cookbook.** 23 chart types, each with a spec table, do/don't rules and tested code or click-by-click steps for every platform. In Python, `mckviz` adds the builders, labels and number formats |
| **A review before it reaches an executive** | **The QA checklist and `mv.lint`** |
| **Associates who follow the house rules** | **The agent playbook**: the full `AGENTS.md`, the portable `mck-chart` skill and the one-page rules file |

Use the frame to explain the kit; don't promise a firm. The kit is the know-how and the tools; you still make the call on the story.

## Who it's for

Anyone at McKesson who needs to communicate with data: analysts, consultants, data scientists, and the leaders who present their work. People move between tools all week, so the kit is organized by where you're working, not who you are. One set of rules, three ways in:

| Way in | Tools | Start with |
|---|---|---|
| **In PowerPoint and Excel** | PowerPoint, Excel, Power BI | The guide and chart chooser, the cheat sheet, then the template, starter deck and chart workbook; the Power BI theme |
| **In code** | Python, R, the web, Power BI | `mckviz` and the themes, the cookbook's tested code, `mv.lint` to check the result |
| **With an AI assistant** | Copilot, Claude, coding agents | `AGENTS.md` in this repo; the `mck-chart` skill or the one-page rules anywhere else |

**First users:** Workforce Innovation. The examples are workforce data on purpose (attrition, headcount, hiring, planning), because that is who is using it first and the examples should feel real to them. The rules work the same for finance, operations or sales. All example data is synthetic.

## What it is not

- Not a BI or dashboard product. It styles and disciplines the tools you already use, including Power BI.
- Not a chart library of its own. It sits on matplotlib, Plotly, ggplot2, Vega-Lite and native Office charts.
- Not a data-cleaning tool. You still clean the export; the kit takes over when the numbers are ready to become a chart.
- Not only for Workforce Innovation. The examples are workforce data; the rules are for any team.
- Not yet a chart maker for non-coders. "Paste a table, ask a question, get five on-brand options" is the next build. Today, coding agents work to the rules in a repo and lint a chart before handing it over; people in PowerPoint and Excel use the guide and the templates.

## Voice

Plain, warm, positive, specific. Sentence case. Short sentences. Lead with what good looks like and what the reader can do, not with what goes wrong; the copy should read well to the person making the chart and to the executive reading it. Lean on the consulting-firm comparison and "executive-ready" to say what sets the kit apart from templates, but don't name a firm. Numbers in headlines are computed, never eyeballed. "We" means the people making charts. No hype: say what the kit does and let the charts make the case. The video can be playful in its own way; product copy doesn't borrow its characters or its clock.

## Call to action

Try it on one chart this week.
