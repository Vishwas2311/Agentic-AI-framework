# Repo Onboarding Patterns

Use this reference during `validate_inputs`, `discover_sources`, `extract_native_ast`, and `build_application_understanding`.

OpenHands onboarding patterns help agents understand an unknown repo before changing it. In Genesis, apply them to source truth:

- Identify app roots, package managers, lockfiles, route folders, API folders, DB schema, environment examples, and test folders.
- Read repo instructions when present, but do not execute arbitrary setup commands without Genesis policy permission.
- Distinguish source truth from generated artifacts, screenshots, demos, and stale files.
- Record missing evidence as blockers rather than assumptions.
- Preserve user-provided BRD, screenshots, mockups, exports, and raw data as higher-priority migration evidence.
- Feed findings into `source_baseline.json`, `asset_inventory.json`, `application_architecture.json`, and `test_oracle.json`.
