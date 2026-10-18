# How to make an explainer video with this kit

The explainer video ("Exec-ready by 3", 4:47, 14 scenes) was built with a hand-made HTML animation engine: one page, pure functions of time, synthesized music and sound effects, a narration track, and an export that records the tab in Chrome. This folder is that engine plus the finished video's source, arranged so the next video starts from a copy of a folder, not from scratch.

The finished video itself (`data-viz-kit-explainer-video.mp4`, 147 MB) is not in git: see [`../demo/README.md`](../demo/README.md) for where it lives.

## The pipeline, in order

| Step | What you do | Where it lands |
|---|---|---|
| 1. Story | Decide the question the video answers, the audience and the length. Write the beats as a table (scene, time, what happens). | `<video>/README.md` ("The story") |
| 2. Storyboard | One section per scene: background, actors, what appears on which narration chunk, holds, sound effects, the story clock. | `<video>/STORY.md` |
| 3. Narration lines | One line per scene; `\|` splits a line into chunks the visuals lock to, `[[slnc N]]` is a pause in ms after a chunk, `[[rate 0.8]]` slows one chunk. | `<video>/audio/lines.tsv` |
| 4. Scratch voice | `python video/voice/make_scratch.py <video>` speaks every chunk with the macOS `say` voice, records each chunk's start time and bundles the clips. This fixes the **reference cues** the scenes are authored against. | `<video>/audio/*.m4a`, `<video>/ref_cues.json`, `<video>/narration.js` |
| 5. Cue sheet | Copy the cue table out of the timings so scene authors know when each chunk is spoken (`u = narrAt + cue[i]`). | `<video>/CUES.md` |
| 6. Scenes | One HTML file per scene, in filename order, following [`engine/CONTRACT.md`](engine/CONTRACT.md). Real charts are made with `mckviz` and dropped in `assets/`. | `<video>/scenes/NN-name.html`, `<video>/assets/` |
| 7. Build | `python video/engine/build_video.py <video>` assembles the one-page video. | `<video>/explainer.html` |
| 8. Review | Open it in Chrome, click once, press Space. Render stills (`?only=<scene>&t=<s>`) and look at every one. Fix, rebuild, repeat. | `<video>/stills/` (ignored) |
| 9. Real voice | Kokoro (local, free) or ElevenLabs (API key) speaks the same chunks; `assemble_voice.py` joins them with the scripted pauses. The engine re-pins every visual beat to the new chunk starts, so the scenes don't change. | `<video>/audio/*.voice.m4a`, `<video>/audio/timings-voice.json` |
| 10. Export | In Chrome, press **E**, share **This tab**; an `.mp4` or `.webm` downloads at the end. | your Downloads folder (never git) |

## What each folder holds

```
video/
  README.md                       this file
  engine/                         the animation engine (shared by every video)
    shell.html                    stage, motion utilities, actors, clock, music, sfx, narration, export
    build_video.py                python video/engine/build_video.py <video folder> [--out name.html]
    CONTRACT.md                   how to write a scene file
    frames/                       UI components (frames.css, frames.js: windows, chat, notebook, slide editor, terminal)
                                  and the style frames f01–f05 that show them in use; render.sh renders them to PNG
    tools/                        contact.py (contact sheet of PNGs), dump_audio.py + score_plot.py (check the score)
  characters/                     Sam and Spark: build.py (three art directions), restyle.py (the final rigs),
                                  board.py (design board), final/{sam.svg, spark.svg, README.md}
  voice/                          make_scratch.py, make_voice_kokoro.py, make_voice_elevenlabs.py,
                                  assemble_voice.py, pack_audio.py; .tts/ (the Kokoro virtualenv, ignored)
  explainer-the-meeting/          the second video ("The meeting", about 3:00, no Sam; see its README)
  explainer-exec-ready-by-3/      the finished video's source (see its README for the story)
    README.md, STORY.md, CUES.md, ref_cues.json
    scenes/                       14 scene files plus 98-score.html (the music cue sheet)
    audio/                        lines.tsv (the narration), *.voice.m4a + timings-voice.json (the final Kokoro voice)
    assets/                       make_options.py, make_nb.py, make_forecast.py and the PNG/JSON they write; guide/ screenshots
    tokenwall/                    tokenwall.html (the brand-swap scene source) + make_wall_scene.py (turns it into scenes/70-wall.html)
    review-notes-v3.md            the owner's review of the previous cut (its screenshots are in the archive)
  _template/                      the smallest video that builds: one scene, an empty lines.tsv
  archive/                        (ignored) earlier cuts, stills, the review screenshots, voice samples, and
                                  out-explainer-original/ (the whole pre-move folder, kept until the owner deletes it)
```

Generated files never go in git: `<video>/explainer.html`, `<video>/narration.js`, `<video>/stills/`, `audio/chunks/`, the scratch `audio/*.m4a`, `assets/raw/`, `frames/png/`, the character boards, exports (`*.mp4`, `*.webm`, `*.wav`) and `voice/.tts/`. The rules are in the repo's `.gitignore`.

### Inventory: what came from `out/explainer/` and where it went

| Role | Files | Size | Kept as source? |
|---|---|---|---|
| Engine | `v3/shell.html` (64 KB), `v3/build_video.py`, `v3/CONTRACT.md` | 80 KB | Yes → `engine/` |
| UI components | `frames/frames.css`, `frames.js`, `f01–f05.html`, `render.sh`; `frames/png/` (3 MB of renders) | 70 KB + 3 MB | Yes → `engine/frames/`; the PNGs are ignored |
| Engine tools | `v3/contact.py`, `dump_audio.py`, `score_plot.py` | 12 KB | Yes → `engine/tools/` |
| Scenes | `v3/scenes/*.html` (15 files incl. the score cue sheet) | 270 KB | Yes → `<video>/scenes/` |
| Storyboard and cues | `v3/STORY.md`, `v3/CUES.md`, `v3/ref_cues.json`, `script.md` | 40 KB | Yes → `<video>/` (`script.md` became the video's README) |
| Narration | `audio/lines.tsv`, `audio/timings-voice.json` | 16 KB | Yes |
| Final voice (Kokoro) | `audio/*.voice.m4a` (14 clips) | 3.8 MB | **Yes**, so the video rebuilds without a TTS setup |
| Voice intermediates | `audio/chunks/*.wav` (14 MB), scratch `audio/*.m4a` (1.1 MB), `timings-scratch.json`, `audio/samples/` (2.2 MB) | 17 MB | No: regenerated by the voice scripts; samples archived |
| `narration.js` | the clips base64-packed for file:// playback | 4.9 MB | No: `pack_audio.py` rebuilds it (the build runs it when missing) |
| Voice pipeline | `make_scratch.py`, `make_voice_kokoro.py`, `make_voice_elevenlabs.py`, `assemble_voice.py`, `pack_audio.py` | 20 KB | Yes → `voice/` |
| TTS virtualenv | `.tts/` | 1.0 GB | No: moved to `voice/.tts/`, ignored; recreate with the command in `make_voice_kokoro.py` |
| Characters | `design/character/{build,restyle,board}.py`, `final/{sam,spark}.svg` + README, 6 exploration SVGs | 230 KB | Yes → `characters/` |
| Character boards | `design/character/board-*.{html,png}` | 5.6 MB | No: `board.py` regenerates them; ignored |
| Chart assets | `assets/make_{options,nb,forecast}.py`, `opt1–5.png`, `nb_*.png`, `fc_*.png`, `guide/*.png`, `*.json` | 3.4 MB | Yes → `<video>/assets/`, so the video builds without rerunning mckviz or Chrome |
| Asset intermediates | `assets/raw/` | 1.2 MB | No: ignored |
| Brand-swap scene | `frames/tokenwall/tokenwall.html`, `v3/make_wall_scene.py`; `still-*.png` (4.2 MB) | 50 KB | Yes → `<video>/tokenwall/`; stills ignored |
| Build output | `explainer.html` (372 KB) | | No: rebuilt by `build_video.py` |
| Review | `explainer-video-feedback/` (md + 19 screenshots) | 14 MB | The notes, yes (`review-notes-v3.md`); the screenshots → `archive/` |
| Design board | `board.html`, `board-data.js`, `make_board.py` | 24 KB | No → `archive/` (it indexed the generated PNGs of the old layout) |
| Stills and contact sheets | `stills/` (5 MB), `v3/stills/` (26 MB) | 31 MB | No → `archive/` |
| Previous cuts | `v2-archive/` (the 2:44 cut and older lines) | 4.5 MB | No → `archive/` |
| The export | `data-viz-kit-explainer-video.mp4` (in Downloads) | 147 MB | No: over GitHub's 100 MB limit; see `demo/README.md` |

Tracked source: about 8 MB. Everything else (about 107 MB plus the 1 GB virtualenv) is ignored or archived. The moved copy was checked against the original in Chrome before the original folder went to `archive/out-explainer-original/`: 14 scenes, 14 narration clips, 287.4 s, identical scene start times and a byte-identical `narration.js`.

## Start a new video

1. Copy the template: `cp -r video/_template video/<my-video>` (or copy `video/explainer-exec-ready-by-3` to reuse its scenes). A video folder sits directly under `video/`.
2. Write `README.md` (the story table) and `STORY.md` (beat by beat).
3. Write `audio/lines.tsv`: `scene-id<TAB>chunk | chunk [[slnc 800]] | chunk`. Scene ids start with `s-`.
4. `python video/voice/make_scratch.py video/<my-video>` (macOS). Copy the printed cues into `CUES.md`.
5. Write `scenes/NN-<name>.html`, one per scene, following `engine/CONTRACT.md`. The minimum a scene needs: a `<section class="scene" id="s-…" data-min="N">` and a `SCENES["s-…"] = {narrAt: .5}` entry.
6. `python video/engine/build_video.py video/<my-video>`, then open `video/<my-video>/explainer.html` in Chrome (click once, Space).
7. Real voice, then export (below).

The minimum files to change for a new video: `audio/lines.tsv`, `STORY.md`, the scene files, and the chart assets. The engine, the characters and the voice scripts stay as they are. If you edit the music (the `SCORE` object in `shell.html`) or add a sound effect, you are editing the engine for every video; keep it backward compatible.

## Restyle or add a character

Sam and Spark are inline SVGs generated by `characters/restyle.py` (the rig, moods, poses, props and hats are documented in [`characters/final/README.md`](characters/final/README.md)). The build inlines `characters/final/sam.svg` and `spark.svg` into every video.

- **Swap Sam's look:** `python video/characters/restyle.py --hair pony --outfit blue --eyewear frames` (or `--hair lob --outfit cream --eyewear none`). Hair, outfit and eyewear are separate groups; the rig and class names stay the same, so no scene changes.
- **Add a mood or pose:** edit the mood and pose tables in `restyle.py` (arm angles are the CSS variables `--lu --lf --ru --rf`), rerun it, and add the name to the actor keys in `engine/CONTRACT.md`.
- **Add a character:** draw it as a function in `restyle.py` that returns one inline SVG with class-switched states (look at `spark()`), write it to `final/<name>.svg`, give it an actor track in `shell.html` (search for `spark` to see the two places: the actor element and the per-frame state merge), and document its keys in the contract.
- **Explore first:** `python video/characters/build.py` writes the three art directions for Sam and two mascot variants, plus `board-characters.html` and a PNG per page (needs Chrome).

## Make the chart assets with mckviz

Real charts in the video are real `mckviz` output on the synthetic example data, not drawings. Each is a script in `<video>/assets/` that writes PNGs and a JSON with the computed headlines and the `mv.lint` output, which the build inlines as `window.KIT`:

- `make_options.py`: the five options from one pasted table (`examples/data/attrition_by_job_family.csv`), each saved with `mv.save`, framed onto a 1920×1080 canvas, plus `options.json` (prompt, headlines, lint results).
- `make_nb.py`: the notebook scene's before / one-line / after figures and `nb_lint.json` (the cells run in one namespace and the real lint output is recorded).
- `make_forecast.py`: the forecast before / one-line / after and `fc_lint.json`.

Run them with the repo's venv from the repo root, e.g. `.venv/bin/python video/explainer-exec-ready-by-3/assets/make_options.py`. The guide screenshots in `assets/guide/` are headless-Chrome renders of `dist/guide/chooser.html` and the bar page (the command pattern is in `engine/CONTRACT.md`, "Previewing your scene").

## The three voice options

All three speak the same `lines.tsv`, chunk by chunk, so every visual beat stays on its words.

1. **Scratch voice (macOS `say`):** `python video/voice/make_scratch.py <video> [scene-id …] [--reref]`. Free, instant, and it defines the reference cues. `--reref` replaces the reference cues for the scenes you name (only after you re-author those scenes).
2. **Kokoro (local, open source):** once, `cd video/voice && uv venv .tts --python 3.12 && VIRTUAL_ENV=.tts uv pip install "kokoro>=0.9.4" "transformers>=4.44" torch soundfile en_core_web_sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl`. Then `video/voice/.tts/bin/python video/voice/make_voice_kokoro.py <video> [--voice af_heart] [--speed 1.0] [--only s-why]`. The finished video uses `af_heart`.
3. **ElevenLabs:** `export ELEVENLABS_API_KEY=…` (never in a file), then `python video/voice/make_voice_elevenlabs.py <video> VOICE_ID [--only s-why]`.

Kokoro and ElevenLabs write `audio/chunks/`, then `assemble_voice.py` joins the chunks with the scripted pauses into `audio/<scene>.voice.m4a` and `timings-voice.json`, and `pack_audio.py` bundles whatever is present into `narration.js` (final voice first, then scratch). Delete the `.voice.m4a` files to go back to the scratch voice. Rebuild after any voice change.

## Export (manual, Chrome)

1. Build, then open `<video>/explainer.html` in **Google Chrome** (the export needs Chrome's `MediaRecorder` with `getDisplayMedia`). Click once on the page so audio is allowed.
2. Press **H** to hide the controls if you want a clean frame.
3. Press **E**. Chrome asks what to share: choose **This tab** (the "Chrome Tab" option, the current tab). Playback starts from the top and the recording runs in real time (about 5 minutes for this video).
4. When it reaches the end, an `.mp4` (or `.webm`, depending on what Chrome supports) downloads. Rename it, e.g. `data-viz-kit-explainer-video.mp4`.
5. Other keys: **V** records your own voice from the mic instead of the narration (press **P** first to rehearse with the teleprompter); **A** downloads the soundtrack alone as a `.wav` for editing in iMovie or Clipchamp.

Controls while reviewing: Space play/pause · ←/→ scene · R restart · M/S/N music/sfx/voice · P teleprompter · H hide controls. URL options: `?scene=s-agent` (start there), `?only=s-agent` (one scene), `?t=12` (a still at 12 s), `?selftest=1` (audio levels per scene), `?pace=1.2`.

Exports are never committed (`*.mp4`, `*.webm`, `*.wav` are ignored). The finished video is published as a GitHub Release asset and on SharePoint; `demo/README.md` has the links.
