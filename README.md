# NoCode2ProCode by TrustEngines

Claude Code-native framework for converting no-code, low-code, screenshots, Figma, Stitch, websites, APIs, and database schemas into production pro-code applications.

Genesis is not a prompt-only system. It uses:

- Claude Code plugin/commands/skills/subagents/hooks
- YAML-defined pipeline flow
- Durable runtime sessions and stage checkpoints
- Swarm-style agent execution planning
- Stage-scoped MCP tool access
- Browser/runtime capture planning
- Source truth resolution
- ULC-IR and canonical app specs
- Deterministic generators
- E2B sandbox verification
- Security, SBOM, visual, accessibility, and compliance gates
- Evidence graph and verified memory
- Provider/model routing plans by stage

## Quick Start

```powershell
cd "C:\Users\Vishwas\Desktop\AI\1.Python Work Space\NoCode2ProCode-Genesis"
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1
Copy-Item ".\migration_inputs\migration_request.example.yaml" ".\migration_inputs\migration_request.yaml"
.\.venv\Scripts\nocode2procode.exe migrate
```

Read `PREREQUISITES.md` before connecting MCPs or production credentials.

In Claude Code, you can also type: `install Genesis E2E`. Genesis maps that intent to:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocal -AllowSystemInstall -IncludeSecurityTools
```

After installation, Genesis opens `Full User Manual - Genesis.html` automatically. For terminal-only setup, add `-NoLaunchManual`.

## Input-First Migration

Put source evidence in:

`migration_inputs/`

Then run:

```powershell
nocode2procode migrate
```

## BRD Understanding Gate

After BRD/design/mockup extraction, Genesis now writes a human-readable BRD gate before technology selection:

- `brd_understanding_summary.md`
- `brd_understanding_report.json`
- `brd_understanding_gate.json`
- `brd_edit_request.json`
- `approved_brd_plan.json`

The gate shows what Genesis understood from the raw files: app goal, users, pages, logic, workflows, entities, acceptance criteria, mockup/image counts, security notes, missing questions, and confidence. In `migration_request.yaml`, use:

```yaml
brd_gate_decision: A   # approve extracted BRD
brd_gate_decision: D   # edit BRD before generation
brd_edit_notes: "Add admin approval queue and remove billing page."
```

If no BRD decision is provided, Genesis continues the pipeline but marks human confirmation as required before final approval.

When edit notes are provided, Genesis now also writes `brd_semantic_patch_report.json` and structurally patches `approved_brd_plan.json` where the note is clear enough, such as adding/removing screens, workflows, entities, roles, requirements, acceptance criteria, or security/privacy notes. Items that cannot be safely matched remain as manual-review patch items.

## Migration Output Mode

Before planning and generation continue, Genesis now writes `migration_mode_decision.json`.

Choose the mode in `migration_inputs/migration_request.yaml`:

```yaml
migration_output_mode: production_e2e_app   # full enterprise-ready app
migration_output_mode: local_demo_app       # fastest localhost demo
migration_output_mode: hybrid_pilot_app     # polished demo with production-shaped architecture
```

If no mode is provided, Genesis defaults to `hybrid_pilot_app` and records that human confirmation is recommended.

## Generated App Approval Gate

After `generate_code`, Genesis writes a generated-output review gate. This does not change the pipeline path; it only validates the frontend/backend/database/tests/docs created so far.

```yaml
generated_app_gate_decision: A   # approve generated output
generated_app_gate_decision: B   # reject generated output
generated_app_review_notes: "Dashboard is missing the admin approval queue."
generated_app_gate_decision: C   # add extra input or missing requirement
generated_app_review_notes: "Add role-based admin view before QA."
```

The gate writes `generated_app_review_summary.md`, `generated_app_approval_gate.json`, `generated_app_human_notes.json`, and `generated_app_patch_instructions.json`. The next stage is always the existing `run_agent_repair_loop`.

Generated-app rejection/add-input notes are now parsed into `generated_app_semantic_patch_report.json` so repair/build agents can consume structured add/remove/update actions. The repair loop also writes `docs/HUMAN_PATCH_REQUESTS.md` when human patch instructions exist.

The runtime now classifies inputs, extracts structured evidence, builds migration planning artifacts, writes a canonical app spec, generates a scaffold workspace, and produces replay/approval outputs in `genesis_apps/`.

It also now writes:

- `runtime_session.json` and `session_events.jsonl`
- `provider_routing_plan.json`
- `agent_execution_plan.json` and `swarm_topology.json`
- `brd_understanding_summary.md`, `brd_understanding_gate.json`, and `approved_brd_plan.json`
- `brd_semantic_patch_report.json`
- `browser_runtime_plan.json` and `runtime_capture_contract.json`
- `memory_retrieval_plan.json`, `memory_context.json`, and `verified_memory_packet.json`
- `generated_app_review_summary.md`, `generated_app_approval_gate.json`, and `generated_app_patch_instructions.json`
- `generated_app_semantic_patch_report.json`
- `repair_loop_report.json` and `agent_patch_log.jsonl`
- `code_quality_report.json`, `test_report.json`, and `security_review.json`
- `production_readiness_scorecard.json`

## First Real QA Pass

Genesis now runs a local quality pass during `nocode2procode migrate` instead of writing QA placeholders only.

The current runtime can now:

- verify core scaffold files are present
- validate generated JSON artifacts
- validate dependency manifests
- verify frontend route files match the route manifest
- compile generated Python files for syntax errors
- run focused Ruff structural checks when Ruff is installed
- run a generated backend `/health` smoke test when FastAPI is available
- run a local secret-pattern security scan
- produce a production readiness scorecard for the migration workspace

## Better Evidence Understanding

Genesis now also does a stronger first-pass extraction for migration evidence:

- BRD and text documents now produce functional requirements, acceptance criteria, role hints, workflow candidates, and screen candidates
- `.docx` and `.pptx` documents now contribute text-based intent extraction through Office XML parsing
- screenshot inputs now produce viewport and UI-hint metadata
- local `file://` and localhost-style website references now produce real HTML structure capture in `runtime_evidence.json`

Remote runtime capture stays conservative by default. To attempt remote URL capture during a run, set `allow_remote_runtime_capture: true` in `migration_request.yaml`.

The repair loop is still intentionally conservative. It now performs deterministic preflight scaffold normalization before QA runs, and it records those actions in `repair_loop_report.json`.

## Smart UI Strategy

Genesis now decides UI tooling before generation:

- 21st.dev Magic: `component` vs `website`
- Magic website mode: `from_scratch` vs `get_inspired`
- Magic goal: `lead_generation`, `drive_sales`, `interactive_quiz`, `subscriptions`, or `custom`
- UI/UX Pro Max brief and design-system persistence
- Motion intensity, bundle policy, reduced-motion fallback, and QA checks

Rules live in `.genesis/genesis.design.yaml`. The CLI helper writes `design_decision_report.json` so Claude Code can follow the same decision path every time.
