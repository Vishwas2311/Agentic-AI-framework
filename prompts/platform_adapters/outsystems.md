# OutSystems Adapter Prompt

Use this prompt during `extract_native_ast` and `record_runtime_evidence` for OutSystems sources.

## Goal

Extract what is available from OAP/OML, platform APIs, and runtime evidence.

## Required Output

Produce `platform_ast.json` sections for:

- modules
- entities
- screens
- actions
- roles
- integrations
- dependencies
- unsupported/proprietary items

## Rules

- Treat OutSystems as a high-risk proprietary adapter.
- Do not assume clean XML parsing is complete.
- Use runtime evidence heavily for screens, actions, validations, and permissions.
- Escalate low-confidence workflow semantics to human review.

