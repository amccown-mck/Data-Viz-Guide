# Explainer video: "Exec-ready by 3" (v4 cut)

About 4:47, 14 scenes, narrated by Kokoro (`af_heart`, via `video/voice/make_voice_kokoro.py`). The storyboard is `STORY.md`; every visual beat is pinned to its narration chunk (`CUES.md`). How the kit works as a whole: [`../README.md`](../README.md).

Build and watch (from the repo root):
```bash
python video/engine/build_video.py video/explainer-exec-ready-by-3
```
then open `video/explainer-exec-ready-by-3/explainer.html` in **Chrome**, click once, then press **Space**. Music, sound effects and the narration are built in. The finished export lives outside git (see `demo/README.md`).

## The story
| # | Scene | Time | What happens |
|---|---|---|---|
| 1 | Hook | 0:00 | Two bars of music, then "POV: you're Sam." Management analyst, fluent in Excel, PowerPoint and "per my last email". 2:07 on a Tuesday. A Teams-style ping from Dana (VP, Operations): where are we losing people, and is it getting better? Exec-ready by 3. |
| 2 | The data | 0:29 | The export, and it's a lot: numbers stored as text, percents vs decimals, the same team twice, a column of ########. |
| 3 | Cleanup | 0:45 | "How will Sam spend the next 53 minutes?" 12 minutes of cleanup. "Now, the hard part: making it say something." |
| 4 | The pain | 0:58 | Four steps: pick a chart (pie, pie, gauge), make it on-brand (which blue?), build the deck (Chart Title, v7), ask a chatbot (purple). |
| 5 | Out of time | 1:25 | 2:52, 8 minutes left, 0 charts, cold coffee. "Let's rewind." VHS rewind to 2:07. |
| 6 | Take two | 1:38 | TAKE 2. Sam has a secret weapon: the **Data Viz Starter Kit** (McKesson Edition). One visual language for business folks, technical folks and AI agents. The music turns upbeat. |
| 7 | Business folks | 1:56 | The guide's chart chooser picks the chart and says why; the PowerPoint and Excel templates make it on-brand with native, editable charts. |
| 8 | Technical folks | 2:16 | Python, R, Power BI. A forecast: great model, meh chart, then `mv.use()`, labelled estimate, range, computed headline, lint ✓. |
| 9 | AI agents | 2:42 | Your favorite assistant (Copilot, Claude) reads the same playbook. Five on-brand options from a pasted table (coming soon). Coding agents follow the rules today and check their own work. |
| 10 | Brand swap | 3:07 | One line in tokens.json: CoverMyMeds, Sarah Cannon, The US Oncology Network, dark mode. |
| 11 | Three hats | 3:25 | Consultant before lunch, analyst after lunch, agent wrangler by 3. "One kit. Every hat." |
| 12 | Sent | 3:38 | 2:35, sent, 25 minutes to spare, and the coffee is still hot. |
| 13 | Why | 3:47 | "Before AI, I never had the time, or the patience." The four parts of the kit. "So I built it, with AI as my partner." |
| 14 | Close | 4:07 | "What problem have you always wanted to solve…?" "Imagine what you could build." "Make the thing you wish existed." (`?close=a|b|d` previews the other closing lines.) |

Narration lines are in `audio/lines.tsv`, one per scene; `|` separates the chunks the visuals lock to, `[[slnc N]]` is a pause in ms. After editing a line, run `python video/voice/make_scratch.py video/explainer-exec-ready-by-3` (scratch voice, which also defines the reference cues), re-voice it with Kokoro, and rebuild.

## Voice
The final voice is Kokoro `af_heart`; its clips (`audio/*.voice.m4a`) and chunk timings (`audio/timings-voice.json`) are tracked, so the video rebuilds without a TTS setup. To re-voice (all three options are explained in `../README.md`):
- **Kokoro:** `video/voice/.tts/bin/python video/voice/make_voice_kokoro.py video/explainer-exec-ready-by-3 [--only s-why]`.
- **ElevenLabs:** `export ELEVENLABS_API_KEY=...`, then `python video/voice/make_voice_elevenlabs.py video/explainer-exec-ready-by-3 VOICE_ID`. Each chunk is voiced separately and joined with the scripted pauses (`assemble_voice.py`), so every beat stays on its words.
- **Your own voice:** press **P** to rehearse with the teleprompter, then **V** to record with your mic (use headphones).
Delete the `.voice.m4a` files to go back to the scratch voice.

## Export
- **E:** export the video with sound. Share **This tab** when Chrome asks; an `.mp4` or `.webm` downloads at the end.
- **V:** the same, recording your mic instead of the narration.
- **A:** the soundtrack alone (`.wav`), for editing in iMovie or Clipchamp.

## Controls
Space play/pause · ←/→ scene · R restart · M/S/N music/sfx/voice · P teleprompter · H hide controls.
URL options: `?scene=s-agent` (start at a scene), `?only=s-agent` (that scene alone), `?t=12` (a still at 12s), `?selftest=1` (audio check).

## How it's built
- `video/engine/shell.html` is the engine: stage, motion utilities, actors (Sam, Spark), the clock, synthesized music and sound effects, narration, and export.
- The score: instruments, sections and Sam's theme are in `SCORE` in the shell; `scenes/98-score.html` is this video's cue sheet (which section plays at each story beat, plus the hits). `python video/engine/tools/dump_audio.py video/explainer-exec-ready-by-3 music` renders the soundtrack to `stills/score-music.wav` for checking.
- `scenes/NN-*.html` holds one file per scene, in order. `video/engine/CONTRACT.md` explains how to write one.
- `python video/engine/build_video.py video/explainer-exec-ready-by-3` assembles `explainer.html`. Run it after any edit.
- `tokenwall/make_wall_scene.py` regenerates the brand-swap scene (`scenes/70-wall.html`) from `tokenwall/tokenwall.html`.
- Characters live in `video/characters/final/` (`sam.svg`, `spark.svg`). Swap Sam's look with `python video/characters/restyle.py --hair pony --outfit blue --eyewear frames` (or `--hair lob --outfit cream --eyewear none`).
- The real charts in `assets/` come from `assets/make_options.py`, `assets/make_nb.py` and `assets/make_forecast.py` (mckviz on the synthetic data); `assets/guide/` holds screenshots of the guide.
- The owner's review of the previous cut is `review-notes-v3.md` (its screenshots, the earlier cuts and the stills are in `video/archive/`, which git ignores).
