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
7. Load only the prompt/reference file needed for the current stage.

## Core Rule

The user prompt tells NoCode2ProCode what to migrate. The Genesis YAML files tell the agent how to migrate it.

For BRD/DOCX/PDF inputs, the BRD is source truth for features, pages, workflows, tests, data fields, user journey, and acceptance criteria. The BRD technical stack is not automatically final when it conflicts with the user's NoCode2ProCode delivery intent.

If a BRD says Streamlit but the user asks for proper software, pro-code, production, enterprise, or beyond-expectation quality, create a stack decision and ask or document the upgrade decision before generation.

For UI-heavy portals, dashboards, websites, and patient/customer-facing web apps, prefer the premium web profile: `Next.js + Tailwind + shadcn/ui + Motion`, with UI/UX Pro Max as design director and 21st.dev Magic as component/page generator.

Do not silently choose Streamlit, Gradio, notebooks, or static-only stacks for `production_procode` or `enterprise_migration`. Those stacks are prototype-only unless the user explicitly requests them and human approval is recorded.

## Stage Discipline

Use the active stage from `genesis.flow.yaml`. Use only stage-allowed tools from `genesis.tools.yaml`. Apply the policy rules from `genesis.policy.yaml`.

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
