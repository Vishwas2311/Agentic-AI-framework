---
name: nocode2procode-genesis
description: Use this skill when Codex or Claude Code needs to run or extend NoCode2ProCode by TrustEngines: a Claude Code-native framework for converting no-code, low-code, screenshots, Figma, Stitch, websites, APIs, and database schemas into production pro-code apps with source truth resolution, ULC-IR, deterministic generators, E2B sandboxing, MCP gateway governance, visual QA, security, SBOM, compliance, replay dashboard, and evidence graph. Internal engine codename: Genesis.
---

# NoCode2ProCode by TrustEngines

Use the Genesis Engine inside NoCode2ProCode by TrustEngines as a flow-driven framework, not as a free-form prompt.

## Startup

1. Read the project `CLAUDE.md`.
2. Load `.genesis/genesis.flow.yaml`.
3. Load `.genesis/genesis.stack.yaml`.
4. Load `.genesis/genesis.tools.yaml`.
5. Load `.genesis/genesis.policy.yaml`.
6. Load `.genesis/genesis.design.yaml` and `.genesis/genesis.design_quality.yaml`.
7. Load `.genesis/quality_skill_sources.yaml` and `skills/genesis-pro-quality/SKILL.md` when present.
8. Load `.genesis/openhands_dev_skill_mapping.yaml` and `skills/genesis-openhands-dev-quality/SKILL.md` when present.
9. Load only the prompt/reference file needed for the current stage.

## Core Rule

The user prompt tells NoCode2ProCode what to migrate. The Genesis YAML files tell the agent how to migrate it.

For BRD/DOCX/PDF inputs, the BRD is source truth for features, pages, workflows, tests, data fields, user journey, and acceptance criteria. The BRD technical stack is not automatically final when it conflicts with the user's NoCode2ProCode delivery intent.

If a BRD says Streamlit but the user asks for proper software, pro-code, production, enterprise, or beyond-expectation quality, create a stack decision and ask or document the upgrade decision before generation.

For UI-heavy portals, dashboards, websites, and patient/customer-facing web apps, prefer the premium web profile: `Next.js + Tailwind + shadcn/ui + Motion`, with UI/UX Pro Max as design director and 21st.dev Magic as component/page generator.

Do not silently choose Streamlit, Gradio, notebooks, or static-only stacks for `production_procode` or `enterprise_migration`. Those stacks are prototype-only unless the user explicitly requests them and human approval is recorded.

## Stage Discipline

Use the active stage from `genesis.flow.yaml`. Use only stage-allowed tools from `genesis.tools.yaml`. Apply the policy rules from `genesis.policy.yaml`.

## Local Pro Quality Layer

Use `genesis-pro-quality` as an additive local skill layer. It improves acceptance proof, evidence honesty, browser QA, API/security negative tests, accessibility, motion performance, repair discipline, and package hygiene without requiring MCP or API keys.

The local quality layer must never replace the Genesis flow, gates, stack selection, QAOS, or installer. If an MCP or paid tool is missing, report it as `not_used_credentials_missing` or `not_required_for_selected_stack`; do not block local migration unless the selected source, stack, or delivery mode explicitly requires that external tool.

## Local OpenHands Dev Quality Layer

Use `genesis-openhands-dev-quality` as an additive local development-agent pattern layer. It improves repo onboarding, setup/runtime lifecycle states, action-observation evidence, code review discipline, test-fix discipline, and security confirmation without importing OpenHands runtime services, Docker sandboxing, enterprise content, MCP, or API-key tools.

This layer must never replace Genesis stages, gates, QAOS, stack selection, or approval. It must write or strengthen `migration_trajectory.jsonl`, `migration_trajectory.zip`, `active_skill_context.json`, `action_observation_audit.json`, `action_risk_report.json`, and `test_gap_report.json` when QAOS runs.

Apply the stage-specific references from `skills/genesis-pro-quality/references/`:

- Stages 1-9: acceptance proof and stack/tool-risk evidence.
- Stages 10-21: runtime/source evidence and missing-evidence blockers.
- Stages 22-28: testability and canonical proof targets.
- Stages 29-32: UI/UX Pro Max local design rules, accessibility, and motion quality.
- Stages 33-35: forbidden-pattern checks and focused repair handoff.
- Stages 36-40: QAOS evidence, browser click coverage, API negative tests, security abuse checks, screenshots, and console logs.
- Stages 41-46: final evidence, package hygiene, and evidence-backed learning.

Apply the stage-specific references from `skills/genesis-openhands-dev-quality/references/`:

- Source stages: repo/source onboarding patterns.
- Canonical/test stages: action-observation and testability discipline.
- Code generation/review: code review and security confirmation.
- Repair/QA/local run: exact failing observation repair, runtime lifecycle, and action-risk classification.
- Final/PR/learning: trajectory-backed approval and evidence-backed learning.

## Required Gates

Stop for human approval when:

- credentials are missing or unsafe
- confidence is below threshold
- protected media is found
- sensitive data is unmasked
- critical source truth conflicts remain
- deployment or destructive infrastructure action is requested

## Design Direction

Use UI/UX Pro Max as the design director. It owns `DESIGN.md`, `design_tokens.json`, `component_registry.json`, and `visual_acceptance_criteria.md`.

Use 21st.dev Magic for shadcn/Tailwind component generation. Use Framer Motion only for purposeful animation.

Do not approve UI from functional tests alone. Final approval requires `design_decision_report.json`, `domain_style_pack.json`, `design_quality_score.json`, `visual_rejection_report.json`, and `before_after_improvement_report.md`.

For dashboard, portal, auth, form, and data-heavy screens, always create and honor `layout_profile_selection.json` and `viewport_fit_plan.json`. Reject UIs that technically respond to screen size but still feel zoomed out, miniaturized, or trapped inside the wrong container strategy for the screen type.

## Verification

Do not call a migration complete until generated output is tied to evidence:

source artifact → AST → IR → canonical spec → generated file → test → screenshot/API/DB evidence → human approval.
