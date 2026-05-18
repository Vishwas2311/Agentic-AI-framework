# .genesis/ — Pipeline Governance YAML Files

The 48-stage Genesis pipeline is entirely defined by YAML files in this folder. These are read by the orchestrator (`src/genesis_framework/core/orchestrator.py`) at runtime. No changes to Python code are needed to adjust pipeline behavior — only these files.

```
.genesis/
├── genesis.flow.yaml           48 pipeline stage definitions
├── genesis.stack.yaml          Stack selection rules (Next.js vs React vs Vue etc.)
├── genesis.agents.yaml         Agent roles, responsibilities, and stage assignments
├── genesis.design.yaml         Design strategy decision rules (Magic, Stitch, Motion)
├── genesis.policy.yaml         Compliance and secret policy gates
├── genesis.tools.yaml          Tool access control per stage (which MCP tools allowed)
├── genesis.capabilities.yaml   Framework capability inventory
├── genesis.routing.yaml        Source-to-prompt routing (updated to config/prompts/)
├── genesis.cost.yaml           Cost estimation rules per stage
├── genesis.deploy.yaml         Deployment configuration rules
├── genesis.outputs.yaml        Expected output artifacts per stage
├── genesis.memory.yaml         Memory retention and retrieval rules
└── genesis.qa.yaml             QA gate thresholds and repair loop config
```

---

## Key Files

### genesis.flow.yaml — The Pipeline

Defines all 48 stages with objectives, inputs, outputs, and gate conditions. Each stage has:
- `objective` — what this stage accomplishes
- `tools` — which tools are allowed
- `inputs` — required artifacts from prior stages
- `outputs` — artifacts written by this stage
- `gate` — approval or confidence condition before proceeding

**Stage groups:**
1. `validate_inputs` → `discover_sources` → `scan_input_directory`
2. `extract_native_ast` → `build_ulc_ir` → `resolve_source_truth`
3. `build_brd_understanding` → (BRD gate) → `build_semantic_graph`
4. `decide_design_strategy` → `build_visual_fidelity_contract` → `generate_design_system`
5. `build_agent_execution_plan` → `generate_code` → `run_agent_repair_loop`
6. `run_qa_tests` → (QA gate) → `build_sbom` → `run_compliance_check`
7. `save_verified_memory` → (final gate) → `deploy`

### genesis.routing.yaml — Tool and Prompt Routing

Routes each source input type to the correct tools and prompt template:
```yaml
appian_export_present:
  tools: [local_workspace, context7]
  stages: [extract_native_ast]
  prompt: config/prompts/platform_adapters/appian.md
```

### genesis.design.yaml — Design Strategy Rules

Defines when to use 21st.dev Magic vs Stitch vs custom components, and how to configure Motion.

### genesis.policy.yaml — Secret and Compliance Policy

Governs what can appear in prompts, logs, and generated files. PII/PHI masking rules live here.

---

## Modifying the Pipeline

To add a new stage:
1. Add it to `genesis.flow.yaml` with objective, inputs, outputs
2. Implement the stage method in `src/genesis_framework/core/orchestrator.py`
3. Add tool access rules to `genesis.tools.yaml`
4. Add expected outputs to `genesis.outputs.yaml`
