# Positioning: what the kit is and how we describe it

This page is the source of truth for how the kit is named and described. The README, the guide's cover and overview, `START-HERE.html` in the release bundle, the agent files and the explainer video all follow it. Change the wording here first, then carry it through.

## Name

**Data Viz Starter Kit**, with **McKesson Edition** as a secondary tag after the name.

- Write "Data Viz Starter Kit · McKesson Edition" where there is room, "Data Viz Starter Kit" where there isn't. Never "McKesson Data Viz Starter Kit": the brand is an edition, not part of the name, because the kit is built to be re-branded from one file and other McKesson businesses (CoverMyMeds, Sarah Cannon, The US Oncology Network) can have their own editions.
- The parts keep their own names: **the guide** (Data Visualization Guide), **the cookbook**, **`mckviz`** (the Python package), **the themes**, **the `mck-chart` skill**.
- Don't use "Data-Viz-Guide" (the repository slug) or "the McKesson guide" as the product's name.

## One line

One visual language for everyone who makes charts: business folks, technical folks and the AI agents working alongside them.

## The problem (Sam's Tuesday)

It's 2:07 on a Tuesday. A VP asks where we're losing people and whether it's getting better, exec-ready by 3. The data takes twelve minutes to clean. The chart takes the rest: which chart tells this story, which blue is our blue, "Chart Title", `final_v7_REAL_final.pptx`, and the chatbot makes everything purple. Every tool has its own idea of good, so the same numbers look different in Excel, Python, Power BI and a chat window, and most of what gets made says nothing.

## The promise

Exec-ready by 3. Less time fiddling, more time on the story. The kit makes the right chart the easy chart in every tool we use, and the rules are checked before a chart leaves your hands, by you, a reviewer or an agent.

## Who it's for: three hats

| Hat | Lives in | Gets |
|---|---|---|
| **Business folks**: consultants, analysts, anyone with a deck due | PowerPoint, Excel | The guide and chart chooser (which chart, and why), the cheat sheet, the template, starter deck and chart workbook, all with native, editable charts |
| **Technical folks**: analysts, data scientists, engineers | Python, R, Power BI, the web | `mckviz` (one line puts a chart on-brand; helpers for headlines, labels, estimates and ranges), themes for every library, and `mv.lint` to check the result |
| **AI agents**: Copilot, Claude, coding agents | Wherever you work | The same playbook: `AGENTS.md`, the `mck-chart` skill, the one-page rules, so an assistant follows the rules and checks its own work |

Many people wear all three: consultant before lunch, analyst after lunch, agent wrangler by 3. One kit fits every hat.

**Primary users today:** Workforce Innovation. The examples are workforce data on purpose (attrition, headcount, hiring, planning), because that is who is using it first and the examples should feel real to them. The rules are the same for finance, operations or sales. All example data is synthetic.

## What's in the box

| Tile | What it is |
|---|---|
| **A guide** | Which chart to use and when, how to keep it on-brand, what to avoid: 12 chart families plus fundamentals, formats, a chart chooser and a cheat sheet, as a website, a single offline file and a 16:9 PDF |
| **A cookbook** | 23 chart types, each with a spec table, do/don't rules and tested code or click-by-click steps for every platform |
| **`mckviz`** | The Python package: style, labels, number formats, chart builders, maps and a chart lint, for matplotlib and Plotly |
| **Themes** | Generated from one brand file for HTML/CSS, Plotly, Vega-Lite, matplotlib, ggplot2, Power BI, PowerPoint and Excel, plus the template, starter deck and workbook |
| **A playbook for agents** | Rules an AI assistant reads, in three sizes: the full `AGENTS.md`, the portable skill, the one-page rules file |

## How it holds together

- **The brand lives in one file.** `tokens/tokens.json` holds every color, font and chart constant. Change a line and every theme, template and example updates.
- **The rules are written to be checked.** Each rule is testable, `mv.lint` tests the ones code can see, and the QA checklist covers the rest. The agent playbook is the same rules in a form an assistant follows.
- **A chart practice in a box.** The useful comparison is a consulting firm's chart team: a house style, a chooser that says why, worked exhibits for every chart, a review step before anything goes out, and associates (the agents) who follow the rules. The kit packages that practice so one analyst can reproduce it with ease.

## What it is not

- Not a BI or dashboard product. It styles and disciplines the tools you already use, including Power BI.
- Not a chart library of its own. It sits on matplotlib, Plotly, ggplot2, Vega-Lite and native Office charts.
- Not a data-cleaning tool. Sam still cleans the export; the kit takes over at "make it say something".
- Not only for Workforce Innovation. The examples are workforce data; the rules are for any team.
- Not yet a chart maker for non-coders. "Paste a table, ask a question, get five on-brand options" is the next build. Today, coding agents follow the rules in a repo and check their own work; business folks use the guide and the templates.

## Voice

Plain, warm, about the craft. Sentence case. Short sentences. Numbers in headlines are computed, never eyeballed. "We" means the people making charts. Playful where the video is playful (Sam, the cold coffee), never at the expense of being clear.

## Call to action

Try it on one chart this week.
