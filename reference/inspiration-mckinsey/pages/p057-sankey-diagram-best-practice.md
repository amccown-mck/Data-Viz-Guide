---
still: 32
page: 57
section: Relationships
title: Sankey diagram best practice
page_type: chart-best-practice
chart_types: [sankey diagram]
---
## Intent
- Practical rules for coloring and styling Sankey diagrams so paths stay readable: when color helps, what it should encode, how to mark stage values, and using transparency for overlapping flows.

## Guidance (paraphrased, every rule stated on the page)
- Coloring: leaving a Sankey in one color misses a chance to clarify complex paths; color can help tell paths apart.
- Using color to show transfers: in a multi-step Sankey, don't spend color on separations that are already obvious (e.g., recoloring each stage); color works best when each type of transfer gets a consistent color across all steps.
- Styling: don't box the values between steps and don't straighten the organic flow shapes into straight/angular lines; keep curved flows and use simple devices like thin vertical lines to mark step volumes.
- Transparency: avoid flat opaque colors, since some flows can hide others; use transparency so dense overlapping regions can be seen through.

## Examples marked Recommended
- Two-source (A, B) to six-target (1–6) Sankey where flows from B are bright blue and flows from A are dark slate — color separates the two origins' paths through the crossings.
- Two-step Sankey with legend (Approved = dark navy, Rejected = red/coral, On hold = grey) applied consistently at both steps — color encodes transfer type, not stage.
- Three-stage A→B→C Sankey with curved bands, thin vertical node lines, and plain numeric labels (163; 121, 29, 13; 80, 21, 20; 57, 23) — clean, organic, values legible without boxes.
- Dense many-to-many flow with a bright blue highlighted band and semi-transparent dark bands — overlaps visible, nothing fully obscured.

## Examples marked Try to avoid / Not recommended
- Same A/B → 1–6 Sankey all in one dark slate color — crossing paths are hard to trace.
- Two-step Sankey where the first step is all dark navy and the second step is all bright blue — color only restates the step split, which is already obvious, and says nothing about transfer type.
- A→B→C Sankey with bright blue boxes around node values, straight angular diverted flows, and chunky arrow-like final branches — boxes add clutter and straight lines lose the flow feel.
- Same dense flow drawn with opaque flat colors — the blue band and dark bands cover one another.

## Visual specifics observed
- Palette across examples: dark navy/near-black, dark slate grey-blue, bright/azure blue (highlight/second category), coral-red (rejected), light grey (on hold/secondary).
- Node markers in recommended style: thin vertical lines; values as small plain numbers beside nodes; stage labels as tiny letters (A, B, C) above; target labels as tiny numerals 1–6 at right.
- Legend (transfer example): tiny inline horizontal legend at top with small square swatches: Approved, Rejected, On hold.
- Bands: smooth bezier curves; recommended transparency example shows dark bands semi-transparent over a bright blue band.
- No axes or gridlines anywhere.
- Layout: 2×2 grid of white panels on light grey page; each panel has a bold sans title and a Try to avoid (left) / Recommended (right) pair; thin grey rule above verdict rows.
- Verdict markers: dark navy circle with white × for Try to avoid; bright blue circle with white check for Recommended; bold label plus short regular caption.
- Typography: serif page title (two lines); small bold sans eyebrow; sans panel titles and captions; chart labels tiny (many numbers barely legible at this resolution).

## Annotation & narrative patterns
- Paired avoid/recommend comparisons with the avoid example on the left; example charts have no headlines or sources.

## Other notes
- Mini examples reuse the data from the page 56 Sankey (163 → 121/29/13 → 80/21/20 → 57/23).
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 57.
- Left rail has only eyebrow and title (no body text).
