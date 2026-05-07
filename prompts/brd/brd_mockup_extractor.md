# BRD Mockup Extractor Prompt

Extract visual evidence from BRD/DOCX/PDF sources.

For DOCX:

- inspect embedded images under the document media folder
- save extracted images under `brd_extracted_images/`
- map each image to its nearest caption or figure reference
- classify each image as screenshot, wireframe, mockup, diagram, logo, or non-ui image

Produce:

- `brd_mockup_inventory.json`
- `brd_extracted_images/`

If UI mockups are found, feed them into:

- `visual_layout_tree.json`
- `visual_lock_spec.json`
- `design_decision_report.json`

If figure captions exist but images are missing, record this as a risk in `brd_mockup_inventory.json`.
