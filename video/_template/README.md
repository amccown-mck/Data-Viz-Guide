# <Video title> (template)

The smallest video that builds: one scene and an empty narration file. Copy this folder to `video/<my-video>/` and replace this file with the video's story (the table below), then follow "Start a new video" in [`../README.md`](../README.md).

Build and watch (from the repo root):
```bash
python video/engine/build_video.py video/_template
```
then open `video/_template/explainer.html` in Chrome, click once, press Space.

## The story
| # | Scene | Time | What happens |
|---|---|---|---|
| 1 | s-hello | 0:00 | A caption, a sticker, Sam waves, Spark appears. |

## Files to write
- `audio/lines.tsv`: one line per scene, `scene-id<TAB>chunk | chunk [[slnc 800]]`. Empty here, so the scene runs for its `data-min` seconds with music only. Run `python video/voice/make_scratch.py video/<my-video>` after filling it in.
- `STORY.md`: the storyboard, beat by beat (see `../explainer-exec-ready-by-3/STORY.md` for the shape).
- `CUES.md`: the cue table printed by `make_scratch.py`.
- `scenes/NN-name.html`: one per scene, following `../engine/CONTRACT.md`.
- `assets/`: real charts made with `mckviz` (see `../explainer-exec-ready-by-3/assets/make_options.py`), plus `options.json` or similar for the headlines the scenes read from `window.KIT`.
