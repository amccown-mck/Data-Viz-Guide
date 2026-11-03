# Roadmap

Where the kit and its Copilot agent stand, and what's next. **Last updated: 2026-11-03.** This page is rewritten at the end of every working session, not added to. What happened and why: [`docs/worklog.md`](docs/worklog.md). What shipped: [`CHANGELOG.md`](CHANGELOG.md). How to build, release and extend: [`docs/maintaining.md`](docs/maintaining.md).

**The goal:** turn the kit from a "could we do this?" experiment into something any McKesson team can use, with Workforce Innovation as the first user and workforce data in the examples. The repo is the engine (tokens, rules, lint, `mckviz`, the skill); the guide, the Office kit and the Copilot agent are the products on it.

## Now

- **The kit:** release 1.2.0 (2026-10-18); `main` has much more since (CHANGELOG, "Unreleased"): the decision tree and `mv.suggest`, one-call builders (now including `mv.bar`, `mv.bubble` and `mv.bubble_strip`), the options page, `mckviz.office`, highlights with no fixed cap, and the agent guidance restructured by layer.
- **The agent:** "WI Data Storytelling Agent" in Microsoft 365 Copilot ([its repo](https://github.com/amccown-mck/WI-Data-Storytelling-Agent)), version 1.0.20, shared with twelve Workforce Innovation colleagues, running `main` as of 2026-11-03. Plain-words replies and an onboarding starter (demo chart, then a numbered menu); the guide linked on SharePoint.
- **Guidance by layer** (`AGENTS.md`, "Where agent guidance goes"): code first, then the agent's instructions (2,516 of 4,000: only what must hold with no skill loaded), the Copilot `SKILL.md` (11,107 of 14,000: the workflow plus a router to task guides), task guides, reference docs, evals. One skill (decided 2026-11-02).
- **Last core run** (local agent, 2026-11-02): core-1 to core-4 and journey-1 passed. The three known issues of 10-27 (bar order, options-page copies, small Sankey slide) are fixed in code.
- **Bubble charts** (2026-11-03): `mv.bubble` lays them out from the data (key above the plot, labels clear of the bubbles, PNG and slide alike) and lint warns on labels on the data; builders-4 and core-1 to core-4 passed on the local agent; on the shared agent as 1.0.17. `mv.bubble_strip` and its cookbook page followed (builders-5 and core passed on the local agent); on the shared agent as 1.0.18.
- **Insights and annotations** (2026-11-03, shared agent 1.0.19): the slides' insights panel (numbered claims with evidence, a big number only when the headline doesn't already say it, "What it means" or a user-decided "Recommendation"), four annotations (`mv.mark`, `mv.bracket`, `mv.gap`, `mv.note`) and the task guide `references/insights.md`. slides-5 and core passed on the local agent, including a recommendation worked out with the owner.

## Next

One thing at a time, each checked with the one eval that covers it (the agent repo's `evals/prompts.md`). **Principle: fix with good code defaults and general tips, not rules written to pass a test.**

1. **Further agent refinements** (the owner's list): chart fundamentals and the analytical thinking behind them.
2. **The published guide, in one pass** once those land: everything it must pick up is logged in [`docs/guide-refresh.md`](docs/guide-refresh.md).
3. **A figure left open in the notebook** (probe 4's second message ran outside the notebook, so it is untested): if it can't produce a Chart card, `SKILL.md`'s Chart-card recovery line can go too. Low priority: the habit of closing figures covers it.

## Later

- **Story building: from data scenes to multi-slide stories** (a longer horizon). Today the agent makes strong single "data scenes" (one chart, one finding, its insights); some requests need a full storyline and a storyboard across several slides. Shaped by Nancy Duarte's principles, the consulting rule that a storyline's parts are mutually exclusive and collectively exhaustive (MECE), and vertical and horizontal logic: the headlines read across the slides as one argument, and each slide's content backs its own headline. Starts with a synthesis of the source material (Duarte and other experts) before any rules or code; builds on the insights panel and annotations.
- **The analytical-thinking layer** (a longer horizon, high impact): help the user find the story before the chart. Question the data before charting it (a gap that is small-n noise, a total that hides opposite trends in its subgroups, a rate vs. a count), propose the comparison that gives it meaning (a benchmark, the prior year, a peer group), and say what the data can't support. Feeds the headline and the insights. Starts with source material too: hypothesis-driven problem solving and issue trees from consulting practice, alongside the house rules.
- **More one-call builders** (every chart without one is drawn by hand, where collisions and off-brand details come from): stacked area and treemap first, then Venn, parallel coordinates. Then lint for hand-built bars, stacks and tables.
- **SharePoint for the rest:** the Office template and fonts (the guide is there; the release links point at a private GitHub repo colleagues can't open).
- **Colleague feedback** (high impact while usage telemetry is blocked): the one signal on what fails in real use, not in our tests. Probably a Microsoft Loop page (what they asked, what they got, a screenshot, a rating); design its structure with the owner, then let each round of feedback set the next fix.
- **Release 1.3.0** of the kit with the unreleased work.
- **Needs a person, a machine or a decision:** usage telemetry (needs IT's admin consent; a long-term blocker, the agent repo's `docs/telemetry.md`); Power BI checks in Desktop and the Service; a visual check of the Office files on Windows; Brand to confirm the swatches and derived ramps; the R tranche (needs R); the three Claude.ai eval cases. Details: the worklog's "Open items".
- **Parked:** a McKesson AI analyst built on [ai-analyst](https://github.com/ai-analyst-lab/ai-analyst), and an MCP server (only if tools beyond Claude Code and Copilot need the kit). Details in the worklog.

## Decisions

- **Name and voice:** `docs/positioning.md`. Platform priority: HTML and Python, then Excel and PowerPoint, then Power BI; R is a nice-to-have.
- **Insights and annotations (2026-11-03):** the slide's side panel is numbered insights (a bold claim the chart doesn't show on its own, then the evidence), a big number only when one derived number is the point, and at most one implication, worded as what the finding means; recommendations only when the user asks and works one out with the agent, never volunteered. Annotations (markers, brackets, gaps, point callouts) are fit for purpose: less is more, and they must help, not compete.
- **Color:** McKesson Blue for what the headline names, grey context, a navy accent; no fixed number of highlights (2026-11-02), the builders warn when most are blue; orange only for "worse"; categorical order blue, navy, bright blue, teal, mint.
- **The agent:** one skill, `mck-chart`, a second only for a substantial reason; "Think deeper" by default, never "Auto"; no sensitivity label; replies in plain words for colleagues who live in Excel and PowerPoint; one guide link, to the HTML on SharePoint (the PDF on request); slides on the McKesson branded template, native for bar, column, line, 100% stack, waterfall and dumbbell, a picture for the rest; options pages as HTML + PDF, with a recommended lead; files reach the user's OneDrive once (`mv.deliver`).
- **How we work:** the owner tests in Copilot and brings back screenshots and the reasoning; one change at a time; the four `core` evals before each push to the shared agent.
