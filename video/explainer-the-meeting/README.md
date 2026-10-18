# Explainer video: "The meeting" (v2)

About 3:00, 9 scenes, narrated by Kokoro (`af_heart`). The second explainer: no named analyst this time. The hero is a leadership meeting, shown twice: once decoding a chart nobody gets, once deciding on a chart that lands at a glance. Then the kit, three ways in (PowerPoint and Excel, code, an AI assistant), the brand in one file, the leader's part ("ask for the headline") and the call to action from `docs/positioning.md`: try it on one chart this week. The storyboard is `STORY.md`; every visual beat is pinned to its narration chunk (`CUES.md`). How the kit works as a whole: [`../README.md`](../README.md).

Build and watch (from the repo root):
```bash
python video/engine/build_video.py video/explainer-the-meeting
```
then open `video/explainer-the-meeting/explainer.html` in **Chrome**, click once, then press **Space**. Music, sound effects and the narration are built in.

## The story
| # | Scene | What happens |
|---|---|---|
| 1 | s-open | A leadership meeting. A chart goes up: twelve colors, two axes, "Chart Title". The first question is "what am I looking at?" Ten minutes later the room is still decoding it. The decision waits. |
| 2 | s-flip | Same meeting, same data. The chart leads with its point: a headline with the number, grey context, one blue bar. Everyone gets it in three seconds, so the meeting spends its time on what to do. |
| 3 | s-kit | That's the standard top consulting firms hold every chart to, because a team sits behind every executive presentation. Now you have one too: the **Data Viz Starter Kit** (McKesson Edition). Your own data storytelling team, ready when you are. Three ways in. |
| 4 | s-office | PowerPoint and Excel: start with the question, the chooser names the chart and says why, the templates make it on-brand with native, editable charts, a quick checklist before you share. |
| 5 | s-code | Python, R, Power BI: one line puts a chart on-brand, the helpers label the estimate, shade the range and compute the headline, lint checks the house rules. |
| 6 | s-ai | Copilot, Claude, a coding agent read the same playbook, follow the same rules and check their own work. Same chart, same standard, whoever or whatever made it. |
| 7 | s-brand | The house style lives in one file. Change a few lines: CoverMyMeds, Sarah Cannon, The US Oncology Network. |
| 8 | s-lead | If you lead a team, here's your part: ask for the headline. One sentence, a verb and a number, that the chart visibly proves. If a chart can't give you that, it isn't ready. |
| 9 | s-close | Clear charts move decisions forward. Try it on one chart this week. |

Narration lines are in `audio/lines.tsv`, one per scene. After editing a line: `python video/voice/make_scratch.py video/explainer-the-meeting`, re-voice with Kokoro (`video/voice/.tts/bin/python video/voice/make_voice_kokoro.py video/explainer-the-meeting`), rebuild.

## Export
In Chrome, press **E**, share **This tab**; an `.mp4` or `.webm` downloads at the end. **A** renders the soundtrack alone. Controls: Space play/pause · ←/→ scene · R restart · M/S/N music/sfx/voice · H hide controls. URL options: `?scene=s-kit`, `?only=s-kit`, `?t=12`.

## How it's built
Same engine as the first video (`video/engine/`). `scenes/NN-*.html` are the scenes, `scenes/98-score.html` the music cue sheet, `tokenwall/make_wall_scene.py` regenerates `scenes/70-brand.html`. Chart assets in `assets/` are copied from the first video (made with `mckviz` on synthetic data) plus `make_meeting.py` (the deliberately bad "Chart Title" chart).
