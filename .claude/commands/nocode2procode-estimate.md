# /nocode2procode-estimate

Run a dry-run discovery and estimate. Do not generate production code.

## Required Behavior

1. Read `.genesis/genesis.flow.yaml`.
2. Execute `validate_inputs`, `dry_run_estimate`, `discover_sources`, and optionally `extract_native_ast`.
3. Do not deploy.
4. Do not write generated app code except report artifacts.
5. Produce `estimation_report.md`, `effort_matrix.json`, and `dry_run_confidence_scores.json`.

## Compatibility

`/genesis-estimate` remains supported as an older alias.
