# Scene contract: how to write a scene file

A video is one page, `video/<video>/explainer.html`, assembled by `python video/engine/build_video.py video/<video>` (from the repo root) from:
- `video/engine/shell.html`: the engine (stage, motion utilities, actors, clock, audio, export), shared by every video. Don't edit it for one scene. Ask the integrator instead.
- `video/<video>/scenes/NN-name.html`: one file per scene, in filename order. You own only your scene files.
- `video/<video>/STORY.md`: the storyboard (what each scene shows, beat by beat). `video/<video>/CUES.md`: when each narration chunk starts.

The examples below are from the first video, `video/explainer-exec-ready-by-3/` ("Exec-ready by 3"); its scene list is at the end.

Stage: 1920×1080, absolute positioning. Everything is a pure function of time, so the video can be paused, scrubbed and screenshotted at any time.

## A scene file
```html
<section class="scene bg-sand" id="s-consult" data-min="17">
  <h2 class="cap a" data-sfx="whoosh" style="--k:slam;--t:.2s;left:80px;top:60px">Ask for <span class="m">5 options</span>.</h2>
  <div class="a x" style="--k:whipR;--t:1s;--t2:6s;--k2:xwhipL;left:200px;top:200px;width:900px">…</div>
</section>
<style>
  #s-consult .thing{…}         /* ALWAYS scope your CSS under #<scene-id> */
</style>
<script>
SCENES["s-consult"] = {
  sam:   [[0, {x: 1500, y: 560, s: .9, mood: "focus", pose: "type", props: ["laptop"]}], [6.2, {mood: "ooh", pose: "cheeks", props: []}]],
  spark: [[0, {x: 1300, y: 700, s: 1, pose: "stand"}]],
  clock: u => H(14, 12),                 // minutes after midnight, or {m, sub, alarm, left}, or null to hide
  sfx:   [[2.0, "pop"], [3.1, "slot", {dur: 1.2}]],
  narrAt: .5,                            // when this scene's voiceover starts (seconds into the scene)
  music: [[7.2, "power"]],               // optional: switch the music section at u (the cue sheet in 98-score.html sets these)
  trim: [[.25, 2, .25]],                 // optional: squeeze reference seconds a..b (before the narration) into `keep` s
  frame(u, local) {},                    // optional: called every frame. MUST be a pure function of u.
  reset() {},                            // optional: called when the scene is entered
};
</script>
```
- `id` is fixed per scene (see the scene list below). `data-min` is the scene's minimum length in seconds. The engine stretches it if the narration is longer.
- **Time `u`** is seconds into the scene, timed against the scratch narration. Narration chunk *i* starts at `u = narrAt + cue[i]` (table in the video's `CUES.md`). Put each visual beat on the chunk that names it. If a different voice is used later, the engine re-pins every chunk start to the same `u` and warps everything between (all `--t`, `--t2`, typing `--d`, sfx, actor, clock and `frame(u)` times), so write times against the scratch cues only.
- **Holds:** the narration has deliberate pauses (e.g. 4 s after "And then…" in s-hook so people can read Dana's message). Don't fill them with new motion; let the viewer read.
- Keep the scene pure-CSS-animated where you can. Use `frame(u)` only for things CSS can't do (counters, the clock, swapping text, driving an embedded sub-timeline), and make it a pure function of `u` (seekable: setting the same `u` must give the same picture).

## Motion utilities (from the shell)
- `.a`: animates in when the scene is on: `--k` (keyframe), `--t` (delay, seconds), `--d` (duration, default .6s), `--e` (easing).
  Keyframes available: `up`, `pop`, `fade`, `cut` (instant), `left`, `right`, `whipL`, `whipR` (slides in from off-stage), `drop`, `slam` (big in, overshoot), `stamp`, `zoom`, `wipe` (left-to-right reveal).
- `.a.x`: also animates OUT at `--t2` with `--k2` (`xout` default, `xfade`, `xcut` = instant, `xwhipL`, `xwhipR`) over `--d2` (default .3s). **Use this for fast TikTok cuts inside one scene.**
- `.bar` (scaleX grow) and `.vbar` (scaleY grow) at `--t`. `.type` (typewriter, needs a monospace font, `--t`, `--d`) plus `.caret`.
- `shake` is a keyframe you can use in your own CSS, e.g. `animation: shake .4s 2 var(--t)` inside `#s-x .on …`. Remember `.on` is on the section: write your own animations as `#s-x.on .foo{animation:…}` so they restart when the scene is entered.
- Custom properties inherit: an `.a` nested inside an `.a.x` picks up the parent's `--k2`, `--t2`, `--d`… unless you set its own.
- `data-sfx-semi="4"` pitches a `pop` up 4 semitones (rising cascades).
- Never use CSS transitions for timed content (they don't seek). Use animations with delays.

## Captions and components (from the shell)
- `.cap` (96px bold navy), `.cap.xl` (120), `.cap.md` (80), `.cap.sm` (64), `.cap.inv` (white). `<span class="m">` is the lime marker highlight. `.kick` (pill, `.kick.lime`), `.sticker`, `.sticker.navy`.
- Backgrounds on the section: `bg-sand`, `bg-white`, `bg-deep`, `bg-navy`, plus `bg-dots`.
- Every component from `video/engine/frames/frames.css` (the style frames) is available, scoped under `.scene`: `.win`/`.tb`, chat (`.chat-hd`, `.msgs`, `.row`, `.bub.me/.them`, `.composer`, `.toast`, `.file`, `.av.claude`), `.dt`, `.grid`, `.opt`, the slide editor (`.ribbon`, `.editor`, `.rail`, `.canvas`, `.slide`), the notebook (`.nb-tb`, `.nb`, `.cell`), the terminal (`.term`), `.card`, `.chip`, `.ph`. Look at `video/engine/frames/f0*.html` to see them in use, and lift markup from there.
- JS helpers: `esc()`, `pyHL(code)` (notebook syntax colouring), `H(h, m)`, `SPARK_GLYPH` (svg string), `tok("--mck-blue")`.
- `window.KIT.options` (from `assets/options.json`) and `window.KIT.nb` (from `assets/nb_lint.json`) hold the real chart headlines, notebook code and lint output.
- Images: reference real files relative to the video folder, e.g. `assets/opt1.png`, `assets/nb_before.png`, `assets/nb_one_line.png`, `assets/nb_after.png`, `assets/nb_draft.png`, or the repo's `../../examples/output/bar-highlight.png` (a video folder sits directly under `video/`).
- Fonts: LF (Libre Franklin) is the page font; `font-family: Mono` is Inconsolata.

## Actors (live above all scenes; glide between scenes)
State is `[[u, {...}], …]`, merged in order. Omit the track to hide the actor in your scene.
- **Sam** (300×420 viewBox, full body, standing; feet at about y = 405 of 420). Keys:
  - Position and display: `x`, `y` (top-left of the 300×420 box, in stage px), `s` (scale), `show`, `dark: true` (on dark backgrounds), `fx: -1` (mirror), `snap: true` (jump without gliding).
  - `mood`: neutral, happy, stressed, ooh, proud, focus, shrug, deadpan.
  - `pose`: rest, type, coffee, wave, shrug, cheeks, phone, point, cheer.
  - `props`: ["laptop"], ["coffee"].
  - `hats`: 0–3.
  Sam's hair is one dark brown (no highlights), so her arms read clearly against it.
- **Spark** (the mascot, 220×240 viewBox, feet at y = 203). Keys: `x`, `y`, `s`, `pose` (stand, walk, read, thumbs, think, wave), `walking: true` (leg-cycle animation; animate `x` across time for travel by adding more keyframes, since gliding uses a .7s transition between states), `fx: -1` (face left), `dark`.
- Actors sit at z-index 5 (Spark 7). Elements with class `front` (z 6) render in front of Sam (desks, laptops).

## Sound
- `data-sfx="name"` on an element fires at that element's `--t`, or use the `sfx` list. Several names can be space-separated.
- Names: pop, ding, stamp, whoosh, zoom, send, riser {dur}, drop, sparkle, check, blip, error, boing, tick, step, thunk, snap, slot {dur}, scratch, trombone, type {dur} (a `.type` element with `data-sfx="type"` uses its `--d`), and new: teams (chat ping), rewind {dur}, tapestop, ticktock {dur}, powerup.
- The music is handled by the shell, by section: intro (s-hook…s-clean), tense (s-pain, s-out), hush, power (from the drop in s-turn), soft (s-why), power (s-close). Only s-out (`[[u, "hush"]]` at the rewind) and s-turn (`[[u, "power"]]` at the title) set markers.

## Scenes and owners (the first video)
| file | id | owner |
|---|---|---|
| 10-hook, 15-data, 18-clean | s-hook, s-data, s-clean | opening agent |
| 20-pain, 25-out | s-pain, s-out | pain agent |
| 30-turn, 40-consult | s-turn, s-consult | turn + business agent |
| 50-notebook | s-notebook | technical agent |
| 60-agent | s-agent | AI-agents agent |
| 70-wall | s-wall | brand agent |
| 80-hats, 85-sent, 90-why, 95-close | s-hats, s-sent, s-why, s-close | integrator |

Narration text is in the video's `audio/lines.tsv` and the cue table in its `CUES.md`. Don't edit either; ask the integrator.
The story clock is in `STORY.md`. Character rigs (moods, poses, props): `video/characters/final/README.md`.

## Previewing your scene
```bash
cd <repo root> && python video/engine/build_video.py video/<video> --out preview-consult.html
cd video/<video> && mkdir -p stills
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --hide-scrollbars --window-size=1920,1080 --virtual-time-budget=20000 \
  --screenshot="$PWD/stills/s-consult-04.0.png" "file://$PWD/preview-consult.html?only=s-consult&t=4&hud=0"
```
Several agents preview at once, so **always build to your own `--out preview-<you>.html`** (never `explainer.html`, which is the integrator's) and delete your preview file when you finish. `?only=<id>` keeps just your scene, and `?t=` is seconds into it, frozen there (stills). Render a still every 0.5–1s through your scene and **look at every one** with the Read tool. To watch it live: `open -a "Google Chrome" "explainer.html?only=s-consult"`, then press Space. Write stills to the video's `stills/` folder (ignored by git) with your scene id in the file name. `python video/engine/tools/contact.py stills out.png 4` makes a contact sheet.
