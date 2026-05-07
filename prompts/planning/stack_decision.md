# Stack Decision Prompt

Decide the delivery mode and target stack before generating code.

Inputs:

- user prompt
- BRD technical requirements
- BRD design intent
- target users
- compliance profile
- requested output location
- existing source stack, if any

Rules:

- The BRD is source truth for behavior, pages, data, workflows, tests, and acceptance criteria.
- The BRD technical stack is not automatically final.
- `same software` means same behavior and user journey, not necessarily the same stack.
- `same location` means output path, not stack lock.
- If the user says proper software, production, pro-code, enterprise, or beyond expectation, prefer a production pro-code stack.
- For UI-heavy web apps, dashboards, portals, and patient/customer-facing web products, prefer the premium web profile: `nextjs_tailwind_shadcn_motion`.
- If the BRD says Streamlit, decide whether this is exact BRD demo, polished Streamlit, or production pro-code upgrade.
- If delivery mode is `production_procode` or `enterprise_migration`, do not select Streamlit, Gradio, notebook, or static-only stacks unless the user explicitly overrides and human approval is recorded.
- If uncertain, ask one stack decision question before writing app code.

Produce:

- `stack_decision_report.json`
- `delivery_mode_decision.json`

Output must include:

- detected_brd_stack
- user_delivery_intent
- selected_delivery_mode
- selected_target_stack
- selected_frontend_profile
- selected_ui_automation_profile
- prototype_stack_allowed
- conflict_detected
- decision_reason
- human_approval_required
- quality_gates_required
