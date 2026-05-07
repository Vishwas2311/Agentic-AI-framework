# BRD Design Intent Extractor Prompt

Extract design intent from BRD/DOCX/PDF sources before UI generation.

Capture:

- domain and target users
- tone and trust requirements
- page-specific design expectations
- mockup/figure references
- accessibility requirements
- privacy/security UI requirements
- visual hierarchy requirements
- words like modern, premium, clean, professional, client-ready, patient-friendly
- exact stack requirements and whether they are mandatory

Produce `brd_design_intent.json`.

Do not collapse design requirements into a single sentence like "modern UI." Convert them into measurable acceptance criteria.

Example acceptance criteria:

- login page has centered secure access card
- dashboard has clear metric cards and quick actions
- booking form is easy for non-technical patients
- labels remain visible with 4.5:1 contrast
- status values use text and color
- demo/privacy disclaimer is visible
