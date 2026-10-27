# Roadmap

Where the kit and its Copilot agent stand, and what's next. **Last updated: 2026-10-27.** This page is rewritten at the end of every working session, not added to. What happened and why: [`docs/worklog.md`](docs/worklog.md). What shipped: [`CHANGELOG.md`](CHANGELOG.md). How to build, release and extend: [`docs/maintaining.md`](docs/maintaining.md).

**The goal:** turn the kit from a "could we do this?" experiment into something any McKesson team can use, with Workforce Innovation as the first user and workforce data in the examples. The repo is the engine (tokens, rules, lint, `mckviz`, the skill); the guide, the Office kit and the Copilot agent are the products on it.

## Now

- **The kit:** Data Viz Starter Kit · McKesson Edition, release 1.2.0 (2026-10-18). `main` has more since then, not yet released (CHANGELOG, "Unreleased"): the chart decision tree and `mv.suggest`, one-call builders (`mv.line`, `mv.sankey`, `mv.strip`, `mv.table`, ...), the options page, and `mckviz.office`.
- **The agent:** "WI Data Storytelling Agent" in Microsoft 365 Copilot ([its repo](https://github.com/amccown-mck/WI-Data-Storytelling-Agent)), version 1.0.11, shared with eight Workforce Innovation colleagues, running `main` as of 2026-10-27. It makes charts, options pages (PDF + HTML) and native PowerPoint slides on the McKesson branded template, and reviews charts.
- **Known issues** (from the 2026-10-27 core regression run):
  - A ranking PNG can put the highlighted bars at the bottom; the slide puts them on top.
  - An options page's HTML and PDF can come back as numbered copies in Copilot > Created.
  - A Sankey picture slide sits small beside the takeaways card.

## Next (2026-10-28)

One thing at a time, each checked with the one eval that covers it (the agent repo's `evals/prompts.md`). **Principle: fix with good code defaults and general tips, not rules written to pass a test.**

1. **Bar order in the PNG** (core-1): a one-call `mv.bar` that shares `bar_slide`'s "story on top" order, so the chart and the slide agree.
2. **Options page copies** (core-2): read the run's reasoning first; then route `options_page` / `page_pdf` through `mv.deliver`, like decks.
3. **Sankey picture slide height** (core-3): check how the agent built the figure; make the default fill the chart area at true point sizes.
4. **Trim the prescriptive lines** added on 2026-10-27 where code now enforces the behavior. SKILL.md is at 13,964 of 14,000 characters; the agent's `instruction.txt` at 3,706 of 4,000.
5. **Before pushing to the shared agent:** the four `core` chats on the local agent.

## Later

- **The takeaways card on slides:** redesign it; the owner isn't a fan of it as built (it tends to repeat the chart's numbers).
- **More one-call builders:** bubble strip, stacked area, treemap, Venn, parallel coordinates. Then lint for hand-built bars, stacks and tables.
- **A SharePoint site** for the Office template, fonts and guide, linked from the agent (the release links point at a private GitHub repo colleagues can't open).
- **Colleague feedback:** probably a Microsoft Loop page; design its structure with the owner.
- **Release 1.3.0** of the kit with the unreleased work.
- **Needs a person, a machine or a decision:** Power BI checks in Desktop and the Service; a visual check of the Office files on Windows; Brand to confirm the swatches and derived ramps; the R tranche (needs R); the three Claude.ai eval cases. Details: the worklog's "Open items".
- **Parked:** a McKesson AI analyst built on [ai-analyst](https://github.com/ai-analyst-lab/ai-analyst), and an MCP server (only if tools beyond Claude Code and Copilot need the kit). Details in the worklog.

## Decisions

- **Name and voice:** `docs/positioning.md`. Platform priority: HTML and Python, then Excel and PowerPoint, then Power BI; R is a nice-to-have.
- **Color:** McKesson Blue for the headline's items, grey context, a navy accent; orange only for "worse"; categorical order blue, navy, bright blue, teal, mint (`docs/maintaining.md`, working notes).
- **The agent:** "Think deeper" by default, never "Auto"; no sensitivity label; slides on the McKesson branded template, native for bar, column, line, 100% stack, waterfall and dumbbell, a picture for the rest; options pages as HTML + PDF, with a recommended lead; files reach the user's OneDrive once (`mv.deliver`).
- **How we work:** the owner tests in Copilot and brings back screenshots and the reasoning; one change at a time; the four `core` evals before each push to the shared agent.
