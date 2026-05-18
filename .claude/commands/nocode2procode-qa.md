# /nocode2procode-qa

Run NoCode2ProCode by TrustEngines quality, security, visual, accessibility, SBOM, and compliance gates on a generated app.

## Required Behavior

1. Read `.genesis/genesis.qa.yaml`.
2. Run available deterministic local tools before asking agents to fix anything.
3. Use Claude Code agents only after collecting concrete failures.
4. Produce `code_quality_report.json`, `test_report.json`, `security_review_report.md`, `visual_parity_score.json`, and `design_qa_report.md`.

## Compatibility

`/genesis-qa` remains supported as an older alias.
