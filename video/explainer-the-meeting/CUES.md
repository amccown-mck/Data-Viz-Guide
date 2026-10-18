# Narration cues (reference = scratch voice)

Generated from `ref_cues.json` (written by `video/voice/make_scratch.py`); the final Kokoro voice is re-pinned to these by the engine.

Your scene's time `u` is seconds into the scene. Narration starts at `narrAt` (you set it in SCENES[id]; default .5). Chunk *i* is spoken starting at **u = narrAt + cue[i]**. Put each visual beat on its chunk's start. The scene lasts at least narrAt + dur + hold + 0.5, or data-min if longer.

## s-open  (dur 20.82s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.05) | Picture a leadership meeting. |
| 1 | 2.05 (→ 4.12) | A chart goes up. |
| 2 | 4.12 (→ 9.59) | Twelve colors. Two axes. And a title that says... "Chart Title." |
| 3 | 9.59 (→ 12.56) | So the first question isn't "what should we do?" |
| 4 | 12.56 (→ 15.26) | It's "what am I looking at?" |
| 5 | 15.26 (→ 18.93) | Ten minutes later, the room is still decoding the chart. |
| 6 | 18.93 (→ 20.82) | And the decision waits. |

## s-flip  (dur 19.83s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.48) | Same meeting. Same data. |
| 1 | 2.48 (→ 5.39) | This time, the chart leads with its point: |
| 2 | 5.39 (→ 10.08) | a headline that says the finding, in one sentence, with the number. |
| 3 | 10.08 (→ 13.97) | Grey for context. One blue bar for what matters. |
| 4 | 13.97 (→ 16.50) | Everyone gets it in three seconds. |
| 5 | 16.50 (→ 19.83) | So the meeting spends its time on what to do about it. |

## s-kit  (dur 22.68s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.94) | That's the standard top consulting firms hold every chart to. |
| 1 | 3.94 (→ 9.06) | They can, because there's a whole team behind every executive presentation. |
| 2 | 9.06 (→ 11.10) | Now you have one too. |
| 3 | 11.10 (→ 13.63) | The Data Viz Starter Kit. |
| 4 | 13.63 (→ 17.52) | Your own data storytelling team, ready when you are. |
| 5 | 17.52 (→ 21.26) | It's organized by where you work, not by your job title. |
| 6 | 21.26 (→ 22.68) | Three ways in. |

## s-office  (dur 18.29s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.38) | Live in PowerPoint and Excel? |
| 1 | 2.38 (→ 5.06) | Start with the question you need to answer. |
| 2 | 5.06 (→ 8.73) | The chart chooser names the chart, and says why. |
| 3 | 8.73 (→ 11.75) | Then the templates make it on-brand from the first click, |
| 4 | 11.75 (→ 14.42) | with native charts you can still edit. |
| 5 | 14.42 (→ 18.29) | A quick checklist before you share, and it's ready for the room. |

## s-code  (dur 15.89s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.96) | Work in code? Python, R, Power BI. |
| 1 | 3.96 (→ 6.53) | One line puts a chart on-brand. |
| 2 | 6.53 (→ 11.96) | The helpers label the estimate, shade the range, and compute the headline from the data. |
| 3 | 11.96 (→ 15.89) | And lint checks it against the house rules before anyone else sees it. |

## s-ai  (dur 16.91s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 4.97) | Work with an AI assistant? Copilot, Claude, a coding agent. |
| 1 | 4.97 (→ 7.13) | They read the same playbook you do, |
| 2 | 7.13 (→ 8.97) | follow the same rules, |
| 3 | 8.97 (→ 12.21) | and check their own work before handing it back. |
| 4 | 12.21 (→ 16.91) | Same chart. Same standard. Whoever, or whatever, made it. |

## s-brand  (dur 13.03s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.83) | And the whole house style lives in one file. |
| 1 | 2.83 (→ 6.99) | Change a few lines, and every template and theme updates. |
| 2 | 6.99 (→ 8.90) | CoverMyMeds. |
| 3 | 8.90 (→ 10.75) | Sarah Cannon. |
| 4 | 10.75 (→ 13.03) | The US Oncology Network. |

## s-lead  (dur 16.30s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.91) | If you lead a team, here's your part. |
| 1 | 2.91 (→ 4.93) | Ask for the headline. |
| 2 | 4.93 (→ 9.93) | One sentence, with a verb and a number, that the chart visibly proves. |
| 3 | 9.93 (→ 13.23) | If a chart can't give you that, it isn't ready. |
| 4 | 13.23 (→ 16.30) | Say that once, and watch what comes back. |

## s-close  (dur 13.95s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.76) | Clear charts move decisions forward. |
| 1 | 2.76 (→ 7.31) | This kit makes them the easy path, for every team at McKesson. |
| 2 | 7.31 (→ 10.68) | Try it on one chart this week. |
| 3 | 10.68 (→ 13.95) | The Data Viz Starter Kit. McKesson Edition. |

Total narration: 157.7s (plus narrAt and holds).