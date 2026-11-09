# Roadmap

Where the kit and its Copilot agent stand, and what's next. **Last updated: 2026-11-09.** This page is rewritten at the end of every working session, not added to. What happened and why: [`docs/worklog.md`](docs/worklog.md). What shipped: [`CHANGELOG.md`](CHANGELOG.md). How to build, release and extend: [`docs/maintaining.md`](docs/maintaining.md).

**The goal:** turn the kit from a "could we do this?" experiment into something any McKesson team can use, with Workforce Innovation as the first user and workforce data in the examples. The repo is the engine (tokens, rules, lint, `mckviz`, the skill); the guide, the Office kit and the Copilot agent are the products on it.

## Now

- **The kit:** release 1.2.0 (2026-10-18); `main` has much more since (CHANGELOG, "Unreleased"): the decision tree and `mv.suggest`, one-call builders (`mv.bar`, `mv.bubble`, `mv.bubble_strip` among them), the options page, `mckviz.office` with the insights panel and annotations, highlights with no fixed cap, and the agent guidance restructured by layer.
- **The agent:** "WI Data Storytelling Agent" in Microsoft 365 Copilot ([its repo](https://github.com/amccown-mck/WI-Data-Storytelling-Agent)), version 1.0.21, shared with fourteen colleagues (the list is in the agent repo's `CLAUDE.md`), running `main` as of 2026-11-03.
- **Guidance by layer** (`AGENTS.md`, "Where agent guidance goes"): code first, then the agent's instructions (2,673 of 4,000), the Copilot `SKILL.md` (11,214 of 14,000), task guides (`options`, `review`, `native-formats`, `insights`), reference docs, evals. One skill per skill tree.
- **Shipped 2026-11-03** (each passed its eval and core on the local agent):
  - 1.0.17: bubble charts lay themselves out (`mv.bubble`, `mv.size_key`); lint warns on labels on the data.
  - 1.0.18: the bubble strip (`mv.bubble_strip` and its cookbook page); crowded labels go on steps with leaders.
  - 1.0.19: the insights panel (numbered claims with evidence, a big number only when the headline doesn't say it, "What it means" or a user-decided "Recommendation") and four annotations (`mv.mark`, `mv.bracket`, `mv.gap`, `mv.note`), with the task guide `references/insights.md`.
  - 1.0.20: insight markers on line slides.
  - 1.0.21: `savefig` and `plt.show` are safe in Copilot's sandbox (probe 4), so `SKILL.md` lost its "never savefig" line.
- **The published guide** on SharePoint is release 1.2.0; what the next rebuild must pick up is logged in [`docs/guide-refresh.md`](docs/guide-refresh.md).

## Next

One thing at a time, each checked with the one eval that covers it (the agent repo's `evals/prompts.md`). **Principle: fix with good code defaults and general tips, not rules written to pass a test.**

1. **Colleague feedback, small and light:** one place colleagues report what they asked for, how close the result came, and what got in the way, so we can see where to improve and track it over time (the one signal on real use while usage telemetry is blocked). A Microsoft Form the agent pre-fills from the chat for the colleague to check and submit, in a new `wi-agent-ops` skill (agent repo), being tested on the local agent. Invited only when someone says the work is done, once per chat at most.
2. **Pick the next big build:** the story skill or the analytical toolkit (both under Later). Each starts with a synthesis of source material, before any rules or code.
3. **The published guide, in one pass**, once those land.
4. **Small follow-ups:** a figure left open in the notebook (probe 4 ran outside it): if it can't produce a Chart card, `SKILL.md`'s recovery line goes; the insights repeat check could catch near-matches (617 vs. the headline's "~620"; the owner is fine without it).

## Later

- **Story building: from data scenes to full storylines** (the owner's idea, a longer horizon; likely a second skill alongside `mck-chart`). Today the agent makes strong single "data scenes" (one chart, one finding, its insights); some requests need a story arc and a storyboard across several slides. A guided experience draws out the story's purpose, its audience and what it must communicate, then builds to that. Vertical and horizontal cohesion: the headlines read across the slides as one argument, and each slide's content backs its own headline. Depth and supporting material tailored to the audience. Shaped by Nancy Duarte, Brent Dykes and the consulting rule that a storyline's parts are mutually exclusive and collectively exhaustive (MECE). Starts with a synthesis of those sources; builds on the insights panel and annotations.
- **An analytical toolkit** (the owner's idea, a longer horizon; likely another skill): helpers for analytical techniques the way `mckviz` has helpers for charts, such as forecasting models, clustering and survival analysis, each with a way to translate the method and result back into plain language for people who aren't analysts. First check what the sandbox can run: there are no installs, SciPy is confirmed, and statsmodels, scikit-learn and lifelines aren't yet.
- **The analytical-thinking layer** (a longer horizon, high impact): help the user find the story before the chart. Question the data before charting it (a gap that is small-n noise, a total that hides opposite trends in its subgroups, a rate vs. a count), propose the comparison that gives it meaning (a benchmark, the prior year, a peer group), and say what the data can't support. Feeds the headline and the insights. Starts with source material too: hypothesis-driven problem solving and issue trees from consulting practice, alongside the house rules.
- **More one-call builders** (every chart without one is drawn by hand, where collisions and off-brand details come from): stacked area and treemap first, then Venn, parallel coordinates. Then lint for hand-built bars, stacks and tables.
- **SharePoint for the rest** (moved down 2026-11-09: McKesson computers have Libre Franklin, and the agent carries its own copy for charts): the Office template and fonts (the guide is there; the release links point at a private GitHub repo colleagues can't open).
- **Release 1.3.0** of the kit with the unreleased work.
- **Needs a person, a machine or a decision:** usage telemetry (needs IT's admin consent; a long-term blocker, the agent repo's `docs/telemetry.md`); Power BI checks in Desktop and the Service; a visual check of the Office files on Windows; Brand to confirm the swatches and derived ramps; the R tranche (needs R); the three Claude.ai eval cases. Details: the worklog's "Open items".
- **Parked:** a McKesson AI analyst built on [ai-analyst](https://github.com/ai-analyst-lab/ai-analyst), and an MCP server (only if tools beyond Claude Code and Copilot need the kit). Details in the worklog.

## Decisions

- **Name and voice:** `docs/positioning.md`. Platform priority: HTML and Python, then Excel and PowerPoint, then Power BI; R is a nice-to-have.
- **Insights and annotations (2026-11-03):** the slide's side panel is numbered insights (a bold claim the chart doesn't show on its own, then the evidence), a big number only when one derived number is the point, and at most one implication, worded as what the finding means; recommendations only when the user asks and works one out with the agent, never volunteered. Annotations (markers, brackets, gaps, point callouts) are fit for purpose: less is more, and they must help, not compete.
- **Color:** McKesson Blue for what the headline names, grey context, a navy accent; no fixed number of highlights (2026-11-02), the builders warn when most are blue; orange only for "worse"; categorical order blue, navy, bright blue, teal, mint.
- **The agent:** one skill per skill tree (2026-11-09): charting stays one skill, `mck-chart`, and a distinct job family gets its own (agent operations now; story building and analytics likely next); "Think deeper" by default, never "Auto"; no sensitivity label; replies in plain words for colleagues who live in Excel and PowerPoint; one guide link, to the HTML on SharePoint (the PDF on request); slides on the McKesson branded template, native for bar, column, line, 100% stack, waterfall and dumbbell, a picture for the rest; options pages as HTML + PDF, with a recommended lead; files reach the user's OneDrive once (`mv.deliver`).
- **How we work:** the owner tests in Copilot and brings back screenshots and the reasoning; one change at a time; the four `core` evals before each push to the shared agent.
