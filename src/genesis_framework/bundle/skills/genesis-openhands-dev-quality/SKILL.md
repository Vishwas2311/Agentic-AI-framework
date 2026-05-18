---
name: genesis-openhands-dev-quality
description: Local no-MCP OpenHands-derived development quality layer for Genesis. Use with NoCode2ProCode-Genesis to strengthen repo onboarding, setup/runtime lifecycle, action-observation evidence, code review, test-fix discipline, and security confirmation without importing OpenHands runtime services.
---

# Genesis OpenHands Dev Quality

Use this skill as an additive development-agent quality layer on top of the Genesis 46-stage pipeline. Genesis remains the source of truth for stages, gates, stack choice, output contracts, QAOS, and approval.

## Non-Negotiable Rules

1. Do not replace, fork, or bypass `.genesis/genesis.flow.yaml`.
2. Do not import OpenHands app server, sandbox service, Docker runtime, enterprise content, or full repository code.
3. Do not require MCP, API keys, cloud services, GitHub, Docker, or Kubernetes unless the selected Genesis stack and delivery mode explicitly require them.
4. Treat OpenHands concepts as local patterns only: setup lifecycle, skill loading, action/observation trajectory, security confirmation, code review, and test-fix discipline.
5. Never change tests just to make them pass. If behavior changes, tie the test update to `approved_brd_plan.json`, `canonical_app_spec.json`, or a recorded human gate decision.
6. Never approve from claims. PASS requires command-backed or artifact-backed observation.

## Load Order

When `/genesis-migrate` or `/nocode2procode-migrate` starts:

1. Load `nocode2procode-genesis`.
2. Load `genesis-pro-quality`.
3. Load `.genesis/openhands_dev_skill_mapping.yaml`.
4. Load only the reference below that matches the active Genesis stage.

## Stage-To-Reference Map

| Genesis Stage Area | Reference |
|---|---|
| Input/source discovery | `references/repo-onboarding-patterns.md` |
| Canonical spec/test oracle | `references/action-observation-trajectory.md`, `references/test-fix-discipline.md` |
| Code generation/review | `references/code-review-discipline.md`, `references/security-confirmation.md` |
| Repair loop | `references/test-fix-discipline.md`, `references/action-observation-trajectory.md` |
| Runtime/local run/QAOS | `references/setup-and-runtime-lifecycle.md`, `references/action-observation-trajectory.md` |
| Risky actions/package delivery | `references/security-confirmation.md`, `references/code-review-discipline.md` |
| Skill coordination | `references/skill-loading-patterns.md` |

## Required Artifact Mindset

For production or FullPipeline runs, OpenHands-derived discipline means every meaningful action produces an observation:

- stage/tool action -> `migration_trajectory.jsonl`
- skill context -> `active_skill_context.json`
- command/result audit -> `action_observation_audit.json`
- risky action decision -> `action_risk_report.json`
- test truth from raw evidence -> `test_oracle.json`
- uncovered expectations -> `test_gap_report.json`
- repair handoff -> `fix_task.json`

## Keep Out

- OpenHands runtime server, sandbox server, browser service, enterprise code, and full dependency tree.
- Irrelevant OpenHands test/joke skills such as `flarglebargle.md`.
- Offensive security automation. Convert security content into safe local defensive checks only.
- Any cloud/API/MCP call unless credentials exist and Genesis selected-stack policy requires it.
