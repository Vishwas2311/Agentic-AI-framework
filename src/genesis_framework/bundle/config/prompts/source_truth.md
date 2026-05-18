# Source Truth Resolver Prompt

Resolve conflicts between:

- source export
- runtime behavior
- DB schema
- API docs
- screenshots
- Figma/Stitch
- website crawl
- human input

Output `source_truth_report.json` with one decision per artifact:

- artifact_id
- artifact_type
- candidate_sources
- winning_source
- reason
- confidence
- requires_human_review

Do not silently resolve critical conflicts with confidence below 0.75.

