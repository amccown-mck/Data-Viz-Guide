---
still: 47
page: 72
section: Format
title: Interactivity
page_type: other
chart_types: [bubble chart, line chart, scatter/bubble plot, stacked area chart, parallel coordinates, treemap-style diamonds]
---
## Intent
Catalogue of interaction patterns for data visualizations. Sidebar: there are many ways to interact with charts; they can be used alone or combined into systems that let users explore the story more deeply. Eight tiles, each naming an interaction, describing its purpose and showing a small illustration with a cursor. No Recommended/Avoid markers.

## Guidance (paraphrased, every rule stated on the page)
- Hover-state: triggers an active state that highlights specific information (e.g., relationships between points) or reveals more detail through direct labeling.
- Cursor tracking: labels follow the cursor and attach directly to the data; good for inspecting time-based charts such as line charts where reading exact values off the axis is hard.
- Toggles and filters: switch individual variables on/off to tailor what's shown; helps simplify complex or cluttered visuals.
- Sliders: raise or lower a variable that directly changes the displayed data (e.g., population, time, investment).
- Range selection: can be part of a filter list or sit directly on an axis; filters data to show only the chosen value range.
- Zoomable axis: sliders pick a range on an axis and the chart zooms into it, enabling finer-grained analysis.
- Handles: let users rearrange/manipulate datasets to their preference; useful for comparing multiple datasets.
- Play, pause and scrubbing: controls for animating time-based visualizations.

## Examples marked Recommended
- No explicit markers. Illustrations:
  - Hover-state — cluster of light grey circles; hovered circle turns dark navy; dark-grey tooltip "New York / 115,000".
  - Cursor tracking — two lines (bright blue and dark navy) with a vertical grey cursor line at "2008"; dot markers where the cursor crosses each line with value labels "£8.8m" (blue) and "£7.6m" (navy).
  - Toggles and filters — "Show data for:" with switches for London (off, dark knob, being clicked), Berlin (on, bright blue knob), Paris (on).
  - Sliders — cluster of rotated squares/diamonds in navy, royal blue, bright blue, light cyan, lavender, teal; large value "730" above a slider from 500 to 1,000.
  - Range selection — scatter/bubble plot with dark navy dots (selected range) and grey bubbles (outside); dual-handle slider below with labels 2000 and 2005.
  - Zoomable axis — stacked area chart (dark navy base, bright blue, royal blue, light cyan, teal, lavender bands) with x-axis Q1–Q4; dual-handle slider set between Q3 and Q4.
  - Handles — parallel coordinates plot with many thin dark lines across 4 vertical axes; grab-hand cursor on an axis handle with a blue arrow indicating dragging to reorder.
  - Play, pause and scrubbing — rewind, pause (active: dark navy fill, white icon), fast-forward buttons; timeline scrubber slider with handle near the right end.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Color roles: dark navy = active/selected state (hovered bubble, selected dots, active pause button, slider handles); light grey = inactive/unselected; bright blue = "on" state for toggles and secondary series; royal blue, cyan, teal, lavender used as categorical fills.
- Controls: thin light-grey slider tracks, dark navy filled segment between selected handles, round dark handles; toggle switches as rounded pills with circular knobs; buttons as light rounded squares with soft shadow.
- Tooltip styles: dark grey box with white text (hover tile); cursor-tracking uses inline value labels without boxes.
- Axes minimal: faint gridlines in range-selection tile; category ticks under zoomable area chart; no y-axis labels shown.
- Currency formatted with £ and "m" suffix, one decimal.
- Typography: page title serif; tile titles bold sans small; tile descriptions light sans; toggle labels large medium-weight sans; slider value large bold numeral.
- Layout: 2 rows x 4 equal white cards on light grey background.
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 72.

## Annotation & narrative patterns
- Each tile follows: bold name → 1–3 sentence purpose → minimal illustration with cursor showing the gesture.
- No headlines/insights on the example charts; focus is on interaction mechanics.

## Other notes
- Illustrations are schematic; axis values for most charts are absent.
