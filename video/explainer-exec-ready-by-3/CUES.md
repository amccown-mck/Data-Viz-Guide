# Narration cues (reference = scratch voice)

Generated from `ref_cues.json` (written by `video/voice/make_scratch.py`); the final Kokoro voice is re-pinned to these by the engine.

Your scene's time `u` is seconds into the scene. Narration starts at `narrAt` (you set it in SCENES[id]; default .5).
Chunk *i* is spoken starting at **u = narrAt + cue[i]**. Put each visual beat on its chunk's start (or a beat just before/after).
With any other voice (ElevenLabs), the engine re-pins every chunk start to the same u, so author against these numbers only.
The scene lasts at least narrAt + dur + hold + 0.5 (hold = the deliberate silence after the last chunk), or data-min if longer.

## s-hook  (dur 23.92s + hold 0.30s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.04) | POV: you're Sam. |
| 1 | 2.04 (→ 5.46) | Management analyst. Fluent in Excel, PowerPoint, |
| 2 | 5.46 (→ 7.64) | and... "per my last email." |
| 3 | 7.64 (→ 10.98) | It's two-oh-seven on a Tuesday. All quiet. |
| 4 | 10.98 (→ 15.49) | And then... |
| 5 | 15.49 (→ 21.94) | Dana, the VP of Operations. Leadership wants to see where we're losing people, and if it's getting better. |
| 6 | 21.94 (→ 23.92) | Exec-ready. By three. |

## s-data  (dur 14.79s + hold 0.40s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.02) | So Sam opens the file. |
| 1 | 2.02 (→ 4.48) | And... it's a lot. |
| 2 | 4.48 (→ 6.41) | Numbers stored as text. |
| 3 | 6.41 (→ 9.45) | Percents, or decimals? Who knows. |
| 4 | 9.45 (→ 11.96) | The same team, listed twice. |
| 5 | 11.96 (→ 14.79) | And a column that's just... hashtags. |

## s-clean  (dur 11.61s + hold 0.30s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.65) | So how will Sam spend the next fifty-three minutes? |
| 1 | 3.65 (→ 8.16) | First, twelve minutes of cleanup. Fine. That's the job. |
| 2 | 8.16 (→ 9.88) | Now, the hard part: |
| 3 | 9.88 (→ 11.61) | making it say something. |

## s-pain  (dur 25.83s + hold 0.50s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 1.96) | Step one: pick a chart. |
| 1 | 1.96 (→ 4.31) | Which one actually tells this story? |
| 2 | 4.31 (→ 7.23) | Pie? Pie? A gauge? No! |
| 3 | 7.23 (→ 9.33) | Step two: make it on-brand. |
| 4 | 9.33 (→ 11.27) | Which blue is our blue? |
| 5 | 11.27 (→ 13.38) | Step three: build it in the deck. |
| 6 | 13.38 (→ 17.43) | Chart Title. Copy, paste, resize, nudge. |
| 7 | 17.43 (→ 20.73) | Final, version seven, real final. |
| 8 | 20.73 (→ 23.34) | Step four: ask a chatbot for help. |
| 9 | 23.34 (→ 24.96) | And it makes everything... |
| 10 | 24.96 (→ 25.83) | purple. |

## s-out  (dur 9.72s + hold 2.00s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 1.45) | Two fifty-two. |
| 1 | 1.45 (→ 4.92) | Eight minutes left. Charts finished: zero. |
| 2 | 4.92 (→ 7.64) | And her coffee? Cold. |
| 3 | 7.64 (→ 9.72) | Okay. Let's rewind. |

## s-turn  (dur 16.94s + hold 0.50s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.80) | Same Tuesday. Same two-oh-seven. |
| 1 | 2.80 (→ 6.06) | But this time, Sam has a secret weapon. |
| 2 | 6.06 (→ 8.52) | The Data Viz Starter Kit. |
| 3 | 8.52 (→ 11.64) | One visual language for everyone who makes charts: |
| 4 | 11.64 (→ 12.84) | business folks, |
| 5 | 12.84 (→ 14.21) | technical folks, |
| 6 | 14.21 (→ 16.94) | and the AI agents working alongside them. |

## s-consult  (dur 18.63s + hold 0.40s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.19) | Live in PowerPoint and Excel? We've got you. |
| 1 | 3.19 (→ 5.17) | Tell the guide what you want to say, |
| 2 | 5.17 (→ 8.36) | and it shows you the chart that says it, and why. |
| 3 | 8.36 (→ 10.73) | Then the PowerPoint and Excel templates |
| 4 | 10.73 (→ 15.21) | make it on-brand from the first click, with native, editable charts. |
| 5 | 15.21 (→ 18.63) | So your time goes into the story, not the formatting. |

## s-notebook  (dur 24.68s + hold 0.40s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 5.53) | More the technical type? Python, R, Power BI: we've got you too. |
| 1 | 5.53 (→ 7.65) | Say your forecast model is great. |
| 2 | 7.65 (→ 9.95) | The chart? Not so much. |
| 3 | 9.95 (→ 11.95) | One line puts it on-brand. |
| 4 | 11.95 (→ 17.07) | The helpers label the estimate, show the range, and write the headline from the numbers. |
| 5 | 17.07 (→ 19.50) | Lint checks it against the house rules. |
| 6 | 19.50 (→ 24.68) | No custom code. No fiddling. A forecast decision makers actually get. |

## s-agent  (dur 23.16s + hold 0.40s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 4.03) | Work with AI? Your favorite assistant can read the same playbook. |
| 1 | 4.03 (→ 7.09) | Maybe that's Copilot. Maybe it's Claude. |
| 2 | 7.09 (→ 11.05) | Paste a table, ask for five options that fit your storyline, |
| 3 | 11.05 (→ 15.32) | and get five on-brand charts, each headline computed from your data. |
| 4 | 15.32 (→ 17.12) | That one's coming soon. |
| 5 | 17.12 (→ 20.39) | But coding agents already follow the same rules today, |
| 6 | 20.39 (→ 23.16) | and check their own work before handing it back. |

## s-wall  (dur 15.71s + hold 0.60s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.32) | And here's the magic. The brand lives in one file. |
| 1 | 3.32 (→ 8.42) | Change one line, and every chart, slide, and dashboard updates. |
| 2 | 8.42 (→ 10.16) | CoverMyMeds. |
| 3 | 10.16 (→ 11.84) | Sarah Cannon. |
| 4 | 11.84 (→ 14.34) | The US Oncology Network. |
| 5 | 14.34 (→ 15.71) | Even dark mode. |

## s-hats  (dur 11.43s + hold 0.50s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.15) | And if you're like me, and wear all three hats? |
| 1 | 3.15 (→ 4.96) | Consultant before lunch. |
| 2 | 4.96 (→ 6.62) | Analyst after lunch. |
| 3 | 6.62 (→ 8.80) | Agent wrangler by three. |
| 4 | 8.80 (→ 11.43) | Good news: one kit fits every hat. |

## s-sent  (dur 7.37s + hold 0.60s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 2.21) | Two thirty-five. Sent. |
| 1 | 2.21 (→ 4.26) | Twenty-five minutes to spare. |
| 2 | 4.26 (→ 7.37) | Dana loves it. And Sam's coffee is still hot. |

## s-why  (dur 18.30s + hold 0.60s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.26) | Honestly? I always wanted something like this. |
| 1 | 3.26 (→ 7.36) | But before AI, I never had the time, or the patience. |
| 2 | 7.36 (→ 11.77) | A guide, templates, code libraries, a playbook for agents: |
| 3 | 11.77 (→ 15.46) | things I used to rebuild from scratch, every time. |
| 4 | 15.46 (→ 18.30) | So I built it, with AI as my partner. |

## s-close  (dur 11.57s + hold 1.40s)
| # | cue | chunk |
|---|---|---|
| 0 | 0.00 (→ 3.15) | So, what problem have you always wanted to solve, |
| 1 | 3.15 (→ 7.11) | but never had the time, or the patience? |
| 2 | 7.11 (→ 9.53) | Imagine what you could build. |
| 3 | 9.53 (→ 11.57) | Make the thing you wish existed. |
