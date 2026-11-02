# Agent architecture: inventory and migration map

A working document for the rework planned on 2026-11-02. It classifies every piece of the Copilot agent's always-loaded guidance (the agent repo's `appPackage/instruction.txt` and the Copilot edition's `SKILL.md`) against the six layers in `AGENTS.md`, "Where agent guidance goes", and says what to do with each. When the migration is done, what's worth keeping moves into `AGENTS.md` and this page is deleted.

**Snapshot:** `instruction.txt` at agent repo `cdb725a` (3,903 of 4,000 characters); the Copilot `SKILL.md` built from Data-Viz-Guide `213f673` (13,997 of 14,000). Line numbers are the built Copilot `SKILL.md` (`dist/skills/mck-chart-copilot/SKILL.md`), not the template.

**Actions:** **keep**; **trim** (keep the point, fewer words); **dedupe** (said in another layer that reaches the agent when it needs it, so delete here); **code** (a function takes it over in Phase 4, then the prose goes in the same change); **move** (to a task guide or reference doc, behind a pointer).

**Review:** the owner reviews only rows marked **⚑**: a cut or move of a line that came from a real failure. Everything else is done without a review.

## Where this lands

| | Snapshot | Planned | Done (Phase 5, 11-02) | Working level |
|---|---|---|---|---|
| `instruction.txt` | 3,903 | about 2,400 | 2,455 | 2,500 |
| Copilot `SKILL.md` | 13,997 | about 10,500 | 11,107 | 11,000 |

**Status:** every row's action is done (Phase 4 code on `feat/code-first`, the text on `feat/skill-restructure`), except B48's `savefig`/`show` override, which waits for a sandbox probe, so B48 and the Chart-card sentence in B79 stay. B49 changed with the owner's decision on 11-02: no fixed number of highlights. B90 moved to `native-formats.md`, "When mckviz won't load", behind a router line.

## A. `instruction.txt`

| # | What it says (short) | Chars | Belongs in | Action | Origin |
|---|---|---|---|---|---|
| A1 | Identity: built by WI on McKesson's Data Viz Guide; consulting-firm charts without becoming an expert | 373 | Instructions | keep | ecdf2c8 (positioning, 11-02) |
| A2 | For any chart, graph, table, slide…: use the mck-chart skill and follow its workflow (question, chart type, build, headline, QA) | 193 | Instructions (when to use the skill) | trim: drop the step list, which is the skill's | bad0c7d (first port) |
| A3 | A question asked of data is a chart request: answer in one sentence, then the chart | 179 | Instructions (when to use the skill) | keep | 757420d (a "who is paid below 0.90?" run answered in text) |
| A4 | Build every chart in Python with mckviz; start each script with `mck_setup.py` | 156 | `SKILL.md` Setup (line 82) | dedupe | bad0c7d |
| A5 ⚑ | Choose with the decision tree (`mv.suggest` on the data as given) and build with the builder it names, also when the user names the chart; the start chart is right most of the time | 245 | `SKILL.md` step 2 (lines 36-38) | dedupe | aaaa16a, 757420d, bb9c0a3 (a bubble strip and a navy/blue pair where a sorted bar was right; a strip drawn by hand) |
| A6 ⚑ | Show the chart as mckviz's PNG inline with a download link; never Copilot's built-in interactive chart; if Python can't run, say so | 263 | Instructions, shorter: "every chart goes through the skill, never Copilot's own chart or a picture of one; if Python can't run, say so". The PNG-inline detail is in `SKILL.md` line 79 | trim | 2f64ab3 (first Copilot run drew Copilot's chart card) |
| A7 | Lead with what the user asked for; for a chart, reply as the skill's Hand-back says | 180 | Instructions (the journey) | trim: "the skill's Hand-back sets a chart reply" | a80d08e (11-02) |
| A8 ⚑ | Every write to `/mnt/data` adds a OneDrive copy; build in `/tmp`, `mv.look`, deliver only with `mv.deliver`, never `cp`/`mv`/`rm` | 233 | Code (Phase 4: `mv.save`, `options_page` and `page_pdf` refuse `/mnt/data` like `office.save` does) and `SKILL.md` line 78 | code, then delete | 00bd97d, 14254e7 (numbered copies; a deck replaced with `rm` and `cp`) |
| A9 | Compute every number in a headline from the data; never estimate from a picture without saying so | 144 | Instructions (holds in any answer with numbers) | keep | bad0c7d |
| A10 ⚑ | Color from what it encodes: grey context, McKesson Blue for what the headline names, at most two; categorical, sequential, diverging; orange only "worse", green only "better" | 356 | `SKILL.md` step 2 (line 39) and `rules.md`; the builders cap highlights at two | dedupe | aaaa16a, bb9c0a3 (the navy/blue pair) |
| A11 | Never show a group under 10 people, anywhere | 92 | Instructions (privacy; holds in text too) | keep | bad0c7d |
| A12 | Never invent a source system, date or period; use the placeholder, tell the user what to confirm | 122 | Instructions | keep | bad0c7d |
| A13 | Say a chart passed QA only when lint ran and you looked | 89 | Instructions | keep | 2f64ab3 ("QA: Pass" with no lint) |
| A14 ⚑ | Slides: a real .pptx on the branded template with `mv.office` (`native-formats.md`), the six native slide functions, `picture_slide` for the rest, never PptxGenJS, headline once as the title | 394 | Instructions keep one line: "slides and decks only through the skill (`mv.office`, the McKesson template), never PptxGenJS or another slides tool". The function names live in `native-formats.md` | trim | 571a851, 9adb697, 30154e4, 258e6d6 (a Sankey slide built with PptxGenJS; `.orig` copies; slide types the agent didn't know) |
| A15 | Short, plain replies for busy colleagues; one question at most | 162 | Instructions (voice) | keep | 0b01a42, ecdf2c8 |
| A16 | When a request needs more from the user, ask for all of it in one short message with an example, then wait | 210 | Instructions (journey) | keep | 0b01a42 (starters send as they are) |
| A17 | Use only the data the user gives; don't search mail, chats or files unless asked | 101 | Instructions | keep | bad0c7d |
| A18 | The Data Viz Guide's two links, pasted exactly | 327 | Instructions (holds with no skill) | keep | ecdf2c8 (the agent retyped the URL with one wrong character) |

## B. Copilot `SKILL.md`

| Lines | What it says (short) | Chars | Belongs in | Action | Origin |
|---|---|---|---|---|---|
| 1-5 | Front matter (the description decides when Copilot loads the skill), generated note | 610 | `SKILL.md` | keep | — |
| 8 | Intro: what the skill is, what's in it, load mckviz first | 516 | `SKILL.md` | trim: the file list and the load step are in Setup | 0a247a5 |
| 10-23 | The chart brief (working notes, in the reasoning) and its template | 790 | `SKILL.md` (the workflow's scaffold) | keep | a158c57, 52da57e, a80d08e |
| 25-28 | Task guides: options, review, native formats | 631 | `SKILL.md`: **the router** | keep; rename "When the request is…", one line per guide (the build checks one exists) | 0a247a5, 2127b00, f161c51 |
| 31-33 | Step 1: one question, mode and medium, look at the data | 495 | `SKILL.md` | keep | a158c57 |
| 36 | `print(mv.suggest(df))` on the rows as given; one row per person stays that way | 484 | `SKILL.md` | trim (keep the "as given" reason) | 707a852 (counts totaled first hid the spread) |
| 37 | The start chart is right most of the time; Go further, Option; status pills | 368 | `SKILL.md`; status pills to `rules.md` (lint has `status-colors`) | trim | 707a852, 52823ba |
| 38 ⚑ | Builder index: fifteen builders and six slide functions by name | 662 | Code: `mv.suggest` names the builder for every common leaf once `mv.bar` exists (Phase 4). Line becomes "build with the builder `mv.suggest` names, also when the user names the chart; its cookbook page shows the call" | code, then trim | 707a852 (the agent didn't know `mv.strip` existed), e184b9e |
| 39 ⚑ | Color patterns: Focus, Focus + accent, Uniform + accent, Categorical, Sequential, Diverging, stacks | 512 | Code and reference: `mv.suggest` prints the pattern by name; `chart-decision-tree.md` section 4 explains each. Line becomes "use the color pattern `mv.suggest` names (decision tree, section 4); Focus by default" | dedupe | 707a852, 204c936 (Focus + accent was never chosen) |
| 40 | Write Path and Color in the brief; read `principles.md` and the cookbook page | 182 | `SKILL.md` | keep | 52da57e |
| 41 | Common traps: clustered far from zero, two units over time, more than 6 categories, a spread across people | 259 | Code: `mv.suggest`'s Go-further rules and lint's `no-dual-axis` | dedupe | a158c57 |
| 44 | Start from the cookbook snippet; non-PNG outputs read `native-formats.md` | 146 | `SKILL.md` | keep | 0a247a5 |
| 45 | `import mckviz as mv; mv.use()`; `fmt_num`, `signed` decimals, `suppress_small`, maps | 514 | `SKILL.md`, trimmed: in Copilot `mck_setup.py` imports and styles already; `mv.signed`'s decimals tip and the maps pointer go to the cookbook | trim | 5975372 (Claude.ai friction points) |
| 46-47 ⚑ | Copy the snippet, change only data, labels and focus; don't build the frame with `fig.text`; the real color role names, "there is no `C.grey`" | 751 | Code: `mv.colors` raises an error that lists the roles; lint's "headline missing" error names `mv.titles` (Phase 4). Keep "copy the snippet, change only data, labels and focus" | code, then trim | 76331dc (`fig.text` frame; guessed `C.grey` and `C.muted`) |
| 48 ⚑ | Save only with `mv.save`; never `savefig`/`show` (the sandbox turns them into its Chart card) | 279 | Code, candidate: `mck_setup.py` makes `plt.savefig`/`plt.show` safe in the sandbox (render through `print_figure`), so a slip can't produce the card. Then "save with `mv.save`" | code, then trim | 2f64ab3 (the first Copilot run's chart card) |
| 49 ⚑ | At most two highlighted items, the ones the headline names | 231 | `SKILL.md`, rewritten: the owner decided (11-02) there is no fixed cap; highlight what the headline names. Code: `mv.few_highlights` warns when most are blue | trim (done) | 2f64ab3 (three highlighted) |
| 50 | No hex literals; color roles; orange only "worse", green only "better"; RAG only as status | 395 | `rules.md` and lint (`palette`, `orange-semantic`, `status-colors`) | trim to one line | a158c57 |
| 51 | Direct labels, zero baseline, sorting, units in the subtitle | 106 | `SKILL.md` (cheap) | keep | a158c57 |
| 52 | A derived measure is footnoted as an estimate | 307 | `SKILL.md` (no code can tell) | keep | a7d6400 (agent-door dry run) |
| 53 | Drop groups under 10 before plotting (`mv.suppress_small`) | 186 | `SKILL.md` | keep | a158c57 |
| 56, 58-60 | Headline: computed, a sentence with a verb and a number; words literally true; names what the focus shows; neutral subtitle; source line | 626 | `SKILL.md` | keep | a158c57 |
| 57 | Spell out a number that starts the headline | 190 | Code: lint warns already (`headline`) | dedupe | a7d6400 |
| 61 | Missing metadata: ask once or write the placeholder; never invent a system or period | 408 | `SKILL.md` (and A12 in the instructions) | keep | e9d1637 ("Workday HRIS, FY26" invented) |
| 64-68 | QA: lint, look at the render, checklist, honest QA line, alt text | 646 | `SKILL.md` | keep | a158c57, 2f64ab3 |
| 71-76 | Hand-back in plain words: why this chart, before you share, alt text, next steps | 780 | `SKILL.md` | keep | a80d08e (11-02) |
| 78 ⚑ | Files land in OneDrive from `/mnt/data`; build in `/tmp`; `mv.deliver` once; never `cp`/`mv`/`rm`; revisions under a new name | 498 | Code (the output guard, Phase 4) with errors that teach. Line becomes "build and check in `/tmp` (`mv.look`); `mv.deliver` hands each finished file over once" | code, then trim | 382ef56, 05d4dba (check renders copied into `/mnt/data`; `rm` and `cp`; `_v2` and `_v3` decks) |
| 79 | Show the PNG inline (`sandbox:/mnt/data/…`) with a download link; Chart card recovery; code only if asked | 335 | `SKILL.md`; the recovery sentence goes with line 48's code change | trim after line 48 | 2f64ab3 |
| 82-89 | Setup: load mckviz at the top of every script, the snippet, the `find` fallback, check the font line | 1,200 | `SKILL.md` | trim the prose around the snippet | 58339b7 (fresh process per command; skill path under `appCatalog/<id>/`) |
| 90 | If mckviz won't load: constants from `rules.md`, the checklist by hand, or the chart spec plus Excel steps | 483 | A task guide (a rare path) behind a router line, or `native-formats.md` | move | b46082f |
| 91 | Data: read the upload with pandas; sample paths relative to `SKILL_DIR`; what this edition lacks | 386 | `SKILL.md` | trim | 0a247a5 |

## C. For the owner's review (⚑)

Each of these removes or shortens a line that exists because of a real failure. The proposal keeps the failure covered by the layer named; say "keep" for any where you'd rather the line stays.

1. **A5:** the decision-tree line in the instructions. Covered by `SKILL.md` step 2, which loads with every chart request.
2. **A6:** "never Copilot's built-in chart", shortened to one line; the PNG details live in the skill.
3. **A8:** the `/mnt/data` paragraph in the instructions, after the output guard makes writing there an error that says what to do.
4. **A10:** the color paragraph in the instructions. Covered by `SKILL.md` step 2, `rules.md` and the builders' two-highlight cap.
5. **A14:** the PowerPoint paragraph, shortened to "slides only through the skill, never PptxGenJS"; the six function names live in `native-formats.md`.
6. **B38:** the builder index, after `mv.suggest` names a builder for every common chart.
7. **B39:** the color patterns, which `mv.suggest` already names and the decision tree explains.
8. **B46-47:** the color-role list and the `fig.text` warning, after `mv.colors` and lint teach through their errors.
9. **B48:** "never savefig/show", after `mck_setup.py` makes them safe in the sandbox (a new idea: worth it only if it's simple and reliable).
10. **B49:** the two-highlight rule in `SKILL.md`, after `mv.highlight` enforces it like the builders do.
11. **B78:** the OneDrive paragraph, after the output guard.

## D. The code this asks for (Phase 4)

| Change | Lets us cut | ROADMAP |
|---|---|---|
| `mv.bar`, sharing `bar_slide`'s story-on-top order; the tree names it for the sorted bar | B38 (and core-1's bar order) | #1 |
| `mv.save`, `mv.options_page`, `mv.page_pdf` refuse `/mnt/data` in Copilot, like `office.save` | A8, B78 (and core-2's copies) | #2 |
| `picture_slide` fills the chart area | nothing in prose (core-3's small Sankey) | #3 |
| `mv.colors` raises an error listing the roles | B47's list | — |
| Lint's "headline missing" names `mv.titles` | B47's `fig.text` sentence | — |
| `mv.highlight` caps highlights at two | B49 | — |
| `mck_setup.py` makes `plt.savefig`/`plt.show` safe in the sandbox (candidate) | B48, half of B79 | — |
| `__all__` lists every builder | — | — |
