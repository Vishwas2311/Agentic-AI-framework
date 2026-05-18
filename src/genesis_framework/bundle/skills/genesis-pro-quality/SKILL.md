---
name: genesis-pro-quality
description: Local no-MCP quality layer for Genesis migrations. Use with NoCode2ProCode-Genesis to strengthen acceptance proof, design quality, runtime QA, browser testing, API/security negative tests, motion performance, repair loops, and package hygiene without requiring API keys.
---

# Genesis Pro Quality

Use this skill as an additive quality layer on top of the normal Genesis 46-stage pipeline. Genesis remains the source of truth for stages, gates, stack selection, policies, and output contracts.

## Non-Negotiable Rules

1. Do not replace or bypass `.genesis/genesis.flow.yaml`.
2. Do not call MCP, paid APIs, cloud tools, remote databases, GitHub, Figma, Firecrawl, E2B, 21st.dev Magic, Context7, Percy, or Chromatic unless the selected source/stack requires it and credentials are present.
3. Treat this skill as local knowledge only: prompts, checklists, invariants, and evidence discipline.
4. Never claim PASS or APPROVED from a skill recommendation. PASS requires real command-backed or artifact-backed evidence.
5. Keep stack choice user-driven at the Stack Gate. Use this skill to assess risks and required evidence for the selected stack.

## Load Order

When `/genesis-migrate` or `/nocode2procode-migrate` starts:

1. Load `nocode2procode-genesis`.
2. Load `.genesis/quality_skill_sources.yaml`.
3. Load `.genesis/openhands_dev_skill_mapping.yaml` and `skills/genesis-openhands-dev-quality/SKILL.md` when present.
4. Load the reference file below that matches the current stage area.
5. Apply only the checks relevant to the selected source, stack, and delivery mode.

## Stage-To-Reference Map

| Stage Area | Reference |
|---|---|
| 1-4 Input and BRD understanding | `references/acceptance-proof.md` |
| 5-9 Stack and estimate gates | `references/acceptance-proof.md` |
| 10-21 Source/runtime/source truth | `references/browser-ui-dogfooding.md` |
| 22-28 IR and canonical spec | `references/verification-and-qa-evidence.md` |
| 29-32 Design strategy/system | `references/accessibility-and-design-quality.md`, `references/motion-performance.md` |
| 33-35 Code generation/repair | `references/repair-and-package-hygiene.md` |
| 36-40 QAOS/visual/replay | `references/verification-and-qa-evidence.md`, `references/browser-ui-dogfooding.md`, `references/api-security-negative-tests.md` |
| 41-46 local run/final/PR/learning | `references/repair-and-package-hygiene.md` |

## Required Artifact Mindset

For production or FullPipeline runs, every important claim must end in at least one artifact:

- BRD requirement -> `acceptance_evidence_matrix.json`
- UI route/control -> `ui_click_coverage_report.json`
- API route -> `api_negative_test_report.json`
- Security-sensitive flow -> `security_abuse_case_report.json`
- Motion/animation -> `motion_runtime_invariant_report.json`
- QA claim -> `qa_evidence_manifest.json`
- Repair -> `fix_task.json`
- Installer/package -> `package_cleanliness_report.json`
- Development action -> `migration_trajectory.jsonl`
- Runtime/repair lifecycle -> `action_observation_audit.json`, `action_risk_report.json`

## Source Package Policy

This bundle is curated from local packages under `C:\Users\Vishwas\Desktop\AI\Backup\Inventions`. It intentionally stores compact Genesis-specific rules instead of vendoring entire ZIPs.

See `.genesis/quality_skill_sources.yaml` for the source map.
