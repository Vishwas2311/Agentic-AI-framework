# Acceptance Proof Rules

Inspired by local Antigravity acceptance and delivery patterns, adapted for Genesis.

## Purpose

Make every user-facing requirement testable before code generation and before QA approval.

## Rules

- Convert BRD requirements, workflows, roles, forms, APIs, reports, and compliance statements into acceptance criteria.
- Each acceptance criterion must map to a required proof type: route, UI interaction, API behavior, database/seed behavior, security behavior, performance behavior, accessibility behavior, or human gate.
- Missing proof is a blocker in production and FullPipeline modes.
- Keep stack selection flexible. The selected stack changes the proof method, not the business requirement.
- If evidence is unavailable, write a missing-evidence blocker instead of assuming success.

## Required Outputs

- `acceptance_evidence_matrix.json`
- `approved_brd_plan.json`
- `canonical_app_spec.json`
- `qa_evidence_manifest.json`

## Genesis Behavior

During BRD and canonical spec stages, ask:

- What user role performs this?
- What page/route/API/data model proves it?
- What negative case should fail?
- What evidence artifact will QAOS require?
