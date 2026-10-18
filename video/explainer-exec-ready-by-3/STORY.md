# v4 storyboard: "Exec-ready by 3", take two

Read this with `../engine/CONTRACT.md` (how a scene file works) and `CUES.md` (when each narration chunk is spoken).
The narration text lives in `audio/lines.tsv`; don't change it (ask the integrator). The previous cut is in
`video/archive/v2-archive/v3b-2m44/scenes/` (not in git). Reuse its markup and visuals freely where this board says so.

## What changed from the last cut (Ashley's notes, in short)
- **Slow the plot down.** Fast cuts are fine *inside* a beat, but each plot step needs a clear transition
  ("How will Sam spend the next 53 minutes?", "Now, the hard part", "Step one… Step two…") so a viewer can follow.
- **Hold long enough to read.** Whenever text appears that the viewer must read (Dana's message, the spreadsheet
  problems), keep it still and uncluttered until the narration moves on.
- **Name:** it's the **Data Viz Starter Kit**. Never "McKesson Data Viz Starter Kit". Show **"McKesson Edition"** as a
  secondary tag beside the name (it may be used by sub-brands later).
- **Audiences are three different kinds of user:** business folks (Excel and PowerPoint), technical folks (Python, R,
  Power BI), and AI agents (something else entirely, which is the fun part). Give each its own look.
- **Sam's hair is now all one dark brown.** Don't recolor it.
- Tone: playful, warm, about the craft and the fun of building. Keep it about the work itself; no references to careers,
  job changes or teams changing.

## The story clock (top-right pill; `clock: u => …` in your scene)
2:07 hook → 2:08 data → time-lapse to 2:19 (cleanup) → pain steps 2:19 / 2:27 / 2:35 / 2:45 → **2:52 out of time (alarm)** →
rewind spins back to **2:07** → take two: consult 2:09–2:16, notebook 2:17–2:24, agent 2:25–2:30 → **sent at 2:35, "25 min to spare ☕"**.

## Music (handled by the shell; you only set markers)
`intro` (soft) through hook/data/clean → `tense` (minor, ticking, heartbeat kick) through pain/out → `hush` from the rewind
(s-out sets `music: [[u, "hush"]]`) → the drop into `power` (bright, four-on-the-floor; s-turn sets `music: [[u, "power"]]`
on the title slam) → `soft` in s-why → `power` for the close.

## New sound effects
`teams` (chat ping: two knocks + chime), `rewind` {dur} (tape rewind squeal), `tapestop` (record winds down),
`ticktock` {dur} (fast clock ticking for time-lapses), `powerup` (bright rising arpeggio). All the old ones still work.

---

## 1 · s-hook (10-hook.html), bg: an office-y sand, narrAt ≈ 4.29 (two bars of music first)
- **0 → narrAt (music only):** set the stage. A big "POV:" caption builds; Sam is at her desk (laptop prop, focus mood);
  a cosy desk scene (monitor, plant, mug). Give the music room: nothing urgent yet.
- **cue 0 "POV: you're Sam."** lower-third name card: **Sam** · Management Analyst.
- **cue 1 "Management analyst. Fluent in Excel, PowerPoint, and 'per my last email.'"** three skill chips pop in one by one
  (Excel · PowerPoint · "per my last email"), the last one with a wink/sticker energy. Sam: proud.
- **cue 2 "It's two-oh-seven on a Tuesday. All quiet."** clock pill appears (2:07, "53 min to the 3:00 sync" can wait: use
  sub "Tuesday"), Sam sips coffee (pose coffee, props coffee, happy). Calm.
- **cue 3 "And then…"** right after the words: `teams` ping. A **Teams-style chat** slides in: a desktop chat app with a
  left icon rail (Activity, Chat, Teams, Calendar as simple glyphs), purple accent (#5B5FC7 / #6264A7), a header
  "Dana R. · VP, Operations", a status dot, and her message bubble:
  > Hi Sam! 👋 Leadership wants to see where we're losing people, and if it's getting better.
  > Can you make the attrition data exec-ready for the 3:00 sync? 🙏
  plus an attachment chip `attrition_export_FINAL.xlsx`. Optionally a desktop toast first (bottom-right) that then opens
  into the chat. No Microsoft logos; it should *feel* like Teams. **Then hold still ~4 s** (the narration pauses) so
  everyone can read it. Sam: ooh → stressed.
- **cue 4 "Dana, the VP of Operations. Leadership wants to see where we're losing people, and if it's getting better."**
  highlight "where we're losing people" and "if it's getting better" in the bubble (lime marker), one then the other.
- **cue 5 "Exec-ready. By three."** clock pill flips to its normal sub ("53 min to the 3:00 sync"); "by 3" slams. Sam stressed.

## 2 · s-data (15-data.html), the spreadsheet, made real
- **cue 0 "So Sam opens the file."** an Excel-like window (green title bar or ribbon hint, formula bar, column letters,
  row numbers) fills most of the stage. Every row must be fully visible (no row cut off at the bottom).
- **cue 1 "And… it's a lot."** hold. Let people look (Sam deadpan, small, in a corner).
- Data (keep it plausible): job_family, headcount, vol_attrition, enterprise_rate. Rows include Pharmacy Technician,
  Distribution Center Assoc, Customer Care, **Cust. Care** (a duplicate), Specialty Nursing, Sales, Software Engineering,
  HR, Finance.
- **cue 2 "Numbers stored as text."** headcount cells left-aligned with the green corner triangle and the ⚠ diamond
  ("Number stored as text"). Circle + lime sticker "stored as text".
- **cue 3 "Percents, or decimals? Who knows."** the attrition column mixes `27.4`, `0.189`, `7.4%`. Circle all three;
  sticker "27.4? 0.189? 7.4%?".
- **cue 4 "The same team, listed twice."** Customer Care / Cust. Care rows linked by a bracket; sticker "same team, twice?".
- **cue 5 "And a column that's just… hashtags."** a too-narrow cell shows `########`; sticker "########?!".
- Stickers stay up once added (the build-up is the joke). Clock 2:08.

## 3 · s-clean (18-clean.html), the transition
- **cue 0 "So how will Sam spend the next fifty-three minutes?"** a full-screen question card (game-show/TikTok caption
  energy, big "53 minutes" in a marker). Clock 2:07 → 2:08.
- **cue 1 "First, twelve minutes of cleanup. Fine. That's the job."** time-lapse: the spreadsheet's problems fix themselves
  in quick cuts (triangles vanish, percents align, duplicate merges, column widens), a progress bar "Cleaning data · 12 min",
  `ticktock`, clock races 2:08 → 2:19. On "Fine. That's the job." a "✓ Data ready" stamp; Sam shrug (fair enough).
- **cue 2 "Now, the hard part:"** clean cut to a caption.
- **cue 3 "making it say something."** the caption completes with a marker on "say something". Sam: focus. Hold.

## 4 · s-pain (20-pain.html), the painful journey, as four recognizable steps
A **journey tracker** across the top: ① Pick a chart · ② Make it on-brand · ③ Build the deck · ④ Ask AI for help.
The current step lights up; done steps get a ✗ or a sad face, not a ✓. Clock jumps per step. Music is `tense`.
Reuse the old visuals (they're loved): the CHART-O-MATIC slot machine, "which blue is OUR blue?", PowerPoint "Chart Title",
copy/paste/resize/nudge, `final_v7_REAL_final.pptx`, the chatbot that makes it purple.
- **cue 0 "Step one: pick a chart."** step ① lights; clock 2:19.
- **cue 1 "Which one actually tells this story?"** the slot machine; lever pull, `slot`.
- **cue 2 "Pie, pie… gauge? No."** reels land PIE, PIE, GAUGE in time with the words; `error` buzz on "No."
- **cue 3 "Step two: make it on-brand."** step ② lights; clock 2:27.
- **cue 4 "Which blue is our blue?"** a parade of near-identical blues with hex codes; Sam squints.
- **cue 5 "Step three: build it in the deck."** step ③; clock 2:35. PowerPoint-ish editor.
- **cue 6 "Chart Title. Copy, paste, resize, nudge."** "Chart Title" placeholder, then four quick labelled actions.
- **cue 7 "Final, version seven, real final."** the file name mutates through versions to `final_v7_REAL_final.pptx`.
- **cue 8 "Step four: ask a chatbot for help."** step ④; clock 2:45; a generic chatbot window (not Claude, not Copilot).
- **cue 9 "And it makes everything…"** loading dots…
- **cue 10 "purple."** a garish purple gradient chart lands; `boing`/`trombone`-ish. Sam deadpan.

## 5 · s-out (25-out.html), out of time, then rewind
- **cue 0 "Two fifty-two."** clock pill goes alarm-red at 2:52 ("8 min to the 3:00 sync"); a big clock face too.
- **cue 1 "Eight minutes left. Charts finished: zero."** "Charts finished: 0" counter slams. Sam stressed.
- **cue 2 "And her coffee? Cold."** Sam holds a coffee with no steam; a little ❄️ / frost on the cup; sticker "Coffee: cold".
  `trombone`. (One coffee, not three.)
- **cue 3 "Okay. Let's rewind."** VHS rewind: `music: [[u, "hush"]]` right at the cue, `tapestop` then `rewind` {dur ≈ 2.2};
  a "◀◀ REWIND" on-screen display in a VHS style, scanlines and tracking jitter, the montage pieces (pie, purple chart,
  v7 file, Chart Title) fly back in reverse, the clock spins backwards 2:52 → 2:07. End on a white flash.

## 6 · s-turn (30-turn.html), take two, the drop, and who it's for
- **cue 0 "Same Tuesday. Same two-oh-seven."** a clapperboard slate "TAKE 2" claps (`stamp`); clock 2:07, Sam back at her desk, calm.
- **cue 1 "But this time, Sam has a secret weapon."** Sam smirks (proud); a glowing box/briefcase builds suspense; short `riser`.
- **cue 2 "The Data Viz Starter Kit."** the **drop**: `music: [[u, "power"]]` exactly here, `drop` + `powerup` sfx; the
  title slams in, "Data Viz Starter Kit", with a **"McKesson Edition"** tag to the side (a smaller rotated sticker or a
  badge, clearly secondary). Sunburst, sparkles. Sam ooh/cheeks.
- **cue 3 "One visual language for everyone who makes charts:"** caption.
- **cue 4 "business folks,"** card 1: a person/briefcase glyph, "Business folks", "Excel · PowerPoint". Clean, sand/white.
- **cue 5 "technical folks,"** card 2: a `</>` glyph, "Technical folks", "Python · R · Power BI". Mono font, dark editor look.
- **cue 6 "and the AI agents working alongside them."** card 3: Spark (the mascot) / ✦ glyph, "AI agents", "Copilot · Claude".
  Make it visibly *different*: a glowing gradient border, a little shimmer. Three distinct looks, one row.

## 7 · s-consult (40-consult.html), business folks: the guide + Office templates
Kick: "IF YOU LIVE IN POWERPOINT & EXCEL". Clock 2:09 → 2:16.
- **cue 0 "Live in PowerPoint and Excel? We've got you."** kick + Sam (happy) with a laptop.
- **cue 1 "Tell the guide what you want to say,"** the real guide's chart chooser ("What do you want to say?" with
  question types: compare/rank, change over time, part-to-whole…). Use real screenshots of `dist/guide/chooser.html`
  (render them headless, see CONTRACT). A cursor clicks "rank / compare".
- **cue 2 "and it shows you the chart that says it, and why."** the ranking page: the recommended chart plus its
  "why" / do-and-don't notes (screenshot of `dist/guide/ranking.html`, zoomed/cropped to the part that reads).
- **cue 3 "Then the PowerPoint and Excel templates"** a PowerPoint-like editor opens the starter template (title + chart
  layout, McKesson theme colors in the ribbon's theme swatches) and an Excel sheet beside it.
- **cue 4 "make it on-brand from the first click, with native, editable charts."** the chart is a native chart: an
  "Edit Data in Excel" handle, data changes, the bars update; the headline appears. Labels: "native", "editable", "on-brand".
- **cue 5 "So your time goes into the story, not the formatting."** the finished slide; Sam proud. Hold.

## 8 · s-notebook (50-notebook.html), technical folks: an advanced use case, a forecast
Kick: "IF YOU'RE THE TECHNICAL TYPE". Clock 2:17 → 2:24. Real outputs from mckviz (see brief).
- **cue 0 "More the technical type? Python, R, Power BI: we've got you too."** three tool tabs (Python, R, Power BI) light up in turn.
- **cue 1 "Say your forecast model is great."** a notebook: model code (fit, predict, interval) runs.
- **cue 2 "The chart? Not so much."** the default matplotlib forecast: default colors, legend box, no range or an ugly one,
  generic title. Caption "Great model. Meh chart."
- **cue 3 "One line puts it on-brand."** `mv.use()` typed; the chart re-renders on-brand.
- **cue 4 "The helpers label the estimate, show the range, and write the headline from the numbers."** the after-chart:
  actuals solid, forecast dashed, a shaded range labelled as an estimate, a headline computed from the forecast. Call out
  each part as the narration names it ("estimate", "range", "headline").
- **cue 5 "Lint checks it against the house rules."** `mv.lint(fig)` output, ✓ 0 errors.
- **cue 6 "No custom code. No fiddling. A forecast decision makers actually get."** the finished chart large, Sam proud.

## 9 · s-agent (60-agent.html), AI agents
Kick: "IF YOU WORK WITH AI". Clock 2:25 → 2:30. Background dark (bg-deep) to feel different.
- **cue 0 "Work with AI? Your favorite assistant can read the same playbook."** a playbook/book glyph labelled `mck-chart`.
- **cue 1 "Maybe that's Copilot. Maybe it's Claude."** two assistant chips, "Copilot" and "Claude" (generic glyphs, no
  official logos); Spark waves.
- **cue 2 "Paste a table, ask for five options that fit your storyline,"** the chat from the old consult scene: pasted
  table + "I'm trying to show which job families are driving attrition. Can you give me 5 options I could pop into this
  exec's deck right now to fit this storyline?" (reuse its markup).
- **cue 3 "and get five on-brand charts, each headline computed from your data."** five option cards cascade (real
  `assets/opt1-5.png`, headlines from `KIT.options`), each with "✓ lint: 0 errors".
- **cue 4 "That one's coming soon."** a "COMING SOON" stamp on the chat window. Friendly, not a disclaimer.
- **cue 5 "But coding agents already follow the same rules today,"** cut to the old agent scene: task card WI-2481, Spark
  walks to the `mck-chart` toolkit and reads the playbook.
- **cue 6 "and check their own work before handing it back."** checklist ticks (question ✓ chart type ✓ headline ✓
  lint ✓), PR "Ready for review" → "Approved". Spark thumbs up.

## 10 · s-wall (70-wall.html), one line changes the brand, across the McKesson family
- **cue 0 "And here's the magic. The brand lives in one file."** tokens.json beside the dashboard (McKesson theme).
- **cue 1 "Change one line, and every chart, slide, and dashboard updates."** a token line edits; the dashboard re-themes in a wave.
- **cue 2 "CoverMyMeds."** theme inspired by CoverMyMeds: warm orange + magenta accents, navy text, a rounded friendly sans
  for headings. Theme pill "CoverMyMeds".
- **cue 3 "Sarah Cannon."** inspired by Sarah Cannon Research Institute: royal blue + sunny yellow, clean geometric sans.
- **cue 4 "The US Oncology Network."** teal + warm orange, navy, a serif for headings.
- **cue 5 "Even dark mode."** dark theme, then (in the hold) back to McKesson.
Approximate palettes only; no logos. Each brand holds until the next name is spoken.

## 11–14 · s-hats, s-sent, s-why, s-close (the integrator's)
Hats with a stronger payoff ("one kit fits every hat"), sent at 2:35 with 25 minutes to spare and a hot coffee (callback),
the why with "before AI" and the four parts of the kit, and the close: the question, then "Imagine what you could build",
then the closing line.
