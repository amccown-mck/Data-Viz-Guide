---
still: 31
page: 56
section: Relationships
title: Sankey diagram
page_type: chart-type
chart_types: [sankey diagram, flow diagram]
---
## Intent
- Relationship charts (section intro, black box): show logical relationships between entities, or how volumes move from one set/stage to another.
- Sankey: a flow diagram where band width is proportional to flow quantity; typical uses are energy, material, or cost transfers between processes.
- Use to emphasize the major transfers in a system and to find the dominant contributors to an overall flow.

## Guidance (paraphrased, every rule stated on the page)
- Band (line/arrow) width is drawn proportional to the quantity flowing.
- Sankeys put visual weight on the largest transfers, helping locate dominant contributions.
- Callout: line width represents the amount being shown.
- Callout: paths split into smaller flows as quantities move through the process; paths are colored with a diverging palette, with negative flows (rejected proposals/projects) treated as negative transfers.
- Callout: instead of a diverging palette, an alternative is to color the primary path in the brand deep blue and a secondary path in grey to signal background information.

## Examples marked Recommended
- None explicitly labeled; single annotated exemplar:
  - 3-stage Sankey (Proposals → Quotes → Projects → New/Existing clients) — dominant approved path in dark navy is visually heavy; rejected and on-hold leakage peel off below in red and grey.

## Examples marked Try to avoid / Not recommended
- None on this page.

## Visual specifics observed
- Data shown: Proposals 163 → Quotes 121 (approved), 29 (rejected), 13 (on hold). Quotes 121 → Projects 80 (approved), 21 (rejected), 20 (on hold). Projects 80 → 57 New clients, 23 Existing clients. Values sum consistently at each stage.
- Color roles (3 colors): very dark navy/near-black = approved (main flow); coral/pinkish red = rejected; light grey = on hold. The final split (new vs existing clients) is navy for both.
- Main flow drawn as straight rectangular block; diverted flows as smooth S-curved bands dropping downward.
- Nodes: thin vertical black bars at each stage with value labels (plain numbers, no units) placed beside the node bars; the final-stage labels stack number above category name (e.g., "57 / New clients").
- Stage headers bold small sans above each column: Proposals, Quotes, Projects.
- Legend: small square swatches with labels stacked vertically at lower right inside the card (Approved, Rejected, On hold).
- No axes or gridlines.
- Typography: sans-serif chart; bold headline, regular subtitle with year; tiny grey footnote + "Source:" line under a thin rule. Page title serif; eyebrow small bold sans.
- Card: white with soft shadow on light grey page; three external callouts attached via thin grey horizontal leader lines (two left, one right).
- Section intro text sits in a black box with white text in the left rail.

## Annotation & narrative patterns
- Headline is insight-style (share of proposals generating new clients); subtitle descriptive (what is distributed, year).
- Footnote placeholder + source line at card bottom.
- Explanatory callouts outside the card explain encoding (width) and color choice, plus an alternative color approach.

## Other notes
- Typos on page: headline uses "is" with "a third of proposals"; label reads "Exisitng clients".
- Footer: McKinsey & Company | Data Visualization Guidelines | Version 01 | 19.07.18 | page 56.
- Appears to be the first page of the Relationships section (black intro box).
