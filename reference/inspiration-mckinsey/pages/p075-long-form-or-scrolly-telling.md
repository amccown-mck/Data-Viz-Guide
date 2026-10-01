---
still: 49
page: 75
section: Format
title: Long-form or "scrolly-telling"
page_type: interaction
chart_types: [dot matrix / bubble grid, dot timeline, bubble cluster animation]
---
## Intent
Covers how to handle charts inside long-form, scroll-driven web stories ("scrolly-telling"). Standard chart guidelines still apply in general, but this format gives more latitude in how data is shown: content can be explained or revealed step by step as the story moves forward, much like an animation. As a result, the reader does not need to see all the information at once, as they would with a static chart. Use it for narrative web pieces. Do not use it as a reason to take over the browser's scrolling (see Avoid).

## Guidance (paraphrased, every rule stated on the page)
- Follow the standard guidelines by default. Scrolly-telling only loosens how the data display is chosen.
- Data can be explained or revealed step by step as the narrative moves forward, in the way an animation would.
- Readers don't need every piece of information up front.
- Adapt for small screens: text and chart placed side by side fails on most devices. Solve this with in-line "snapshots" of the chart, or by rearranging the visualization at key points in the story.
- Keep animations simple and purposeful. Transitions should support the content and not distract from it. The page cross-references the animation guidelines ("pg XX", a placeholder in the original).
- Avoid scrolljacking / scroll hijacking, where the browser's scroll behaviour is overridden to auto-"snap" the reader to set points on the page. It is considered bad practice because it reduces accessibility.

## Examples marked Recommended
- "Adapt for small screens": a desktop layout with body text on the left and a dark dot-matrix chart on the right, next to a phone mockup (status bar shows 9:41). On the phone, a highlighted text passage about the automotive industry's AI investment over nine years (2010–2018) sits above a single-row dot timeline ('10–'18) with one tooltip value (reads roughly "110,000"). This works because the chart is reflowed in-line instead of sitting beside the text.
- "Simple animations": two states of a bubble cluster. On the left, one large dark bubble is surrounded by four smaller ones. On the right, the smaller bubbles move inward toward the centre, with thin bright-blue arrows showing the direction. This works because it shows a single clear, purposeful transition.

## Examples marked Try to avoid / Not recommended
- "Scrolljacking" or "scroll hijacking": a paragraph of narrative text (about deep-learning potential and companies' ability to use AI) with a vertical column of five pagination dots on the right. The fourth dot is red/active and the rest are light grey. This fails because snapping scroll positions takes control away from the user and reduces accessibility.

## Visual specifics observed
- Color roles: dark navy/near-black is the background for the chart examples and the colour of the bubbles. Bright blue is used for highlighted text backgrounds, active data dots and animation arrows. Mid-grey marks secondary dots in the matrix. Red marks the active scroll-snap dot and the Avoid icon. Light grey marks inactive dots.
- Dot matrix (desktop mock): columns of grey circles of varying size, with bright-blue dots in one column. Column headers and row labels are too small to read (illegible).
- Phone dot timeline: evenly spaced dots with varying sizes and year labels '10 to '18. A small dark tooltip sits above one dot. There are no axes or gridlines.
- Bubble animation: solid dark filled circles with no strokes. Arrows are thin blue lines.
- Each example sits in its own white card with a sans-serif card title. A thin rule separates the example from its verdict row. The verdict row has a blue check-circle icon for "Recommended" or a red x-circle icon for "Avoid", followed by a short caption.
- Typography: the page title is a large serif. The eyebrow ("Format") and body text are small sans-serif. Card titles are medium sans. Captions are the smallest sans. The scrolljacking sample text is a larger sans with generous line spacing.

## Annotation & narrative patterns
- The phone example uses highlighted in-text phrases (blue background) to tie the narrative to the chart, with bold emphasis on "automotive industry".
- A tooltip callout labels a single value on the timeline.
- The phone screen ends with a teaser subheading, "Examples of where AI can be used to".
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 75.

## Other notes
- The cross-reference to the animation page is an unfilled placeholder ("pg XX").
- The right half of the bottom row is empty.
