# /nocode2procode-migrate

Run the full NoCode2ProCode by TrustEngines migration/build pipeline.

## Required Behavior

1. Read `CLAUDE.md`.
2. Locate the NoCode2ProCode framework root that contains `.genesis/genesis.flow.yaml`; do not run as a free-form build if `.genesis` is missing from the active project context.
3. Load `.genesis/genesis.flow.yaml`, `.genesis/genesis.stack.yaml`, `.genesis/genesis.tools.yaml`, `.genesis/genesis.policy.yaml`, `.genesis/genesis.design.yaml`, `.genesis/genesis.design_quality.yaml`, and `.genesis/genesis.outputs.yaml`.
4. Validate the requested source, output location, target stack, and delivery mode before generation. Default to reading inputs from `migration_inputs/` when the user does not provide an explicit path.
5. For BRD/DOCX/PDF inputs, extract BRD requirements, design intent, embedded mockups/images, and stack requirements before writing app code.
5a. After BRD extraction, show the BRD Understanding Gate from `brd_understanding_summary.md`: what Genesis understood, images/mockups, pages, roles, logic, workflows, acceptance criteria, missing questions, and confidence.
5b. Ask the user for one BRD decision before technology selection when confirmation is required: A. approve, B. approve with assumptions, C. add missing evidence, or D. edit BRD. If the user picks D, ask what changes they want and record them as BRD edit notes before generation.
5c. Treat BRD edit notes as semantic patch input. Preserve `brd_semantic_patch_report.json` and use `approved_brd_plan.json` as the downstream BRD source of truth.
6. If the BRD requests Streamlit or another prototype stack, do not silently accept it. Decide or ask whether to build exact BRD demo, polished Streamlit, or upgraded production pro-code.
6a. If delivery intent is `production_procode` or `enterprise_migration`, do not select Streamlit, Gradio, notebook, or static-only stacks unless the user explicitly overrides and human approval is recorded.
6b. For UI-heavy portals, dashboards, websites, and patient/customer-facing web apps, prefer the premium web profile: `Next.js + Tailwind + shadcn/ui + Motion`, with UI/UX Pro Max as design director and 21st.dev Magic as component/page generator.
7. Run the Migration Output Mode Gate after the BRD Understanding Gate. Ask or infer one of: Production E2E App, Local Demo App, or Hybrid Pilot App. Default to Hybrid Pilot when the user does not choose.
8. After code generation, show the Generated App Approval Gate from `generated_app_review_summary.md`. Ask only for generated-output validation: A. approve, B. reject and explain what is wrong, or C. add extra input/missing requirement. Do not ask the user to choose the next pipeline stage.
8a. If the user selects B without notes, ask: "What is wrong with the generated app?" Record the answer in generated app review notes.
8b. If the user selects C without notes, ask: "What extra input or missing requirement should be added?" Record the answer in generated app review notes.
8c. Treat generated-app rejection/add-input notes as semantic patch input. Preserve `generated_app_semantic_patch_report.json` and `generated_app_patch_instructions.json`.
8d. After the gate is recorded, continue the fixed pipeline sequence into `run_agent_repair_loop`, then quality, visual QA, replay, approval, delivery, and learning.
9. Execute stages in order from the `nocode2procode-migrate` alias or `genesis-migrate` internal entrypoint.
10. Produce all required BRD, design, stack, mode, and generated-app approval artifacts before QA: `brd_design_intent.json`, `brd_mockup_inventory.json`, `brd_understanding_report.json`, `brd_understanding_summary.md`, `brd_semantic_patch_report.json`, `approved_brd_plan.json`, `stack_decision_report.json`, `delivery_mode_decision.json`, `migration_mode_decision.json`, `design_decision_report.json`, `domain_style_pack.json`, `component_pattern_selection.json`, `layout_profile_selection.json`, `viewport_fit_plan.json`, `generated_app_approval_gate.json`, `generated_app_patch_instructions.json`, and `generated_app_semantic_patch_report.json`.
11. Use only tools allowlisted for the current stage.
12. Stop for human approval at policy gates.
13. Do not mark final output APPROVED unless `design_quality_score.json`, `visual_rejection_report.json`, and `before_after_improvement_report.md` exist and pass.
14. Produce all required outputs listed in `.genesis/genesis.outputs.yaml`.
15. For dashboard, portal, auth, form, and data-heavy screens, enforce the selected layout profile and viewport-fit plan. Reject layouts that feel zoomed out because operational content is trapped inside narrow centered containers.

## Compatibility

`/genesis-migrate` remains supported as an older alias.

## Prompt Contract

Ask the user only for missing inputs that cannot be safely inferred:

- source app/export/path/url
- target stack
- credentials or credential references
- deployment target
- compliance profile

## Stack Rule

`same software` means preserve features, workflows, data, tests, and user journey. It does not automatically mean preserve a prototype stack from the BRD.

If the user says `proper software`, `pro-code`, `production`, or `beyond expectation`, prefer a production pro-code stack unless the user explicitly locks the BRD stack.
