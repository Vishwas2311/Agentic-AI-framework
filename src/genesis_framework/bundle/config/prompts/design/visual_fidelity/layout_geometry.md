# Layout Geometry Prompt

Extract layout geometry before UI generation.

## Required Output

Produce `visual_layout_tree.json` with:

- screen_id
- viewport width/height
- node id
- node kind
- visible text
- bounding box
- parent/child relationship when available
- confidence

## Rules

- Split complex screenshots into sections.
- Identify repeated components.
- Preserve relative spacing and alignment.
- Mark ambiguous areas for human review.

