# config/schemas — JSON Schemas

Validation schemas for every structured artifact the pipeline produces. Used to validate LLM outputs before they are written to disk.

## Schemas

| File | Validates | Written By Stage |
|------|-----------|-----------------|
| `canonical_app_spec.schema.json` | `canonical_app_spec.json` — the master app specification | `build_canonical_app_spec` |
| `ulc_ir.schema.json` | `ulc_ir.json` — Universal Low-Code Intermediate Representation | `build_ulc_ir` |
| `brd/brd_design_intent.schema.json` | `brd_design_intent.json` — extracted BRD requirements | `extract_brd_design_intent` |
| `brd/brd_mockup_inventory.schema.json` | `brd_mockup_inventory.json` — BRD UI mockup list | `extract_brd_mockups` |
| `confidence_report.schema.json` | `brd_confidence_report.json` — BRD extraction completeness scores | `brd_gate` |
| `source_truth_report.schema.json` | `source_truth_report.json` — multi-source conflict resolution | `resolve_source_truth` |
| `evidence_graph.schema.json` | `evidence_graph.json` — evidence links between sources | `build_semantic_graph` |
| `planning/stack_decision.schema.json` | `stack_decision_report.json` — tech stack selection | `decide_delivery_mode_and_stack` |
| `design/design_decision.schema.json` | `design_decision.json` — design strategy choices | `decide_design_strategy` |
| `design/design_quality_score.schema.json` | `design_quality_score.json` — design evaluation result | `evaluate_design_quality` |
| `visual/visual_layout_tree.schema.json` | `visual_layout_tree.json` — layout geometry from screenshots | `run_visual_design_qa` |
| `visual/visual_lock_spec.schema.json` | `visual_lock_spec.json` — locked visual spec pre-generation | `decide_design_strategy` |

## How Validation Works

After each LLM call that produces a structured output, `agent_runner.py` validates the parsed JSON against the corresponding schema:

```python
import jsonschema
schema = load_schema("canonical_app_spec.schema.json")
jsonschema.validate(instance=output_dict, schema=schema)
```

If validation fails, the output is rejected and the agent is retried (up to `max_retries` from `genesis.agents.yaml`).

## Adding a New Schema

1. Create `config/schemas/your_artifact.schema.json` using JSON Schema Draft 7
2. Reference it in `agent_runner.py`'s schema registry
3. The pipeline will automatically validate outputs against it
