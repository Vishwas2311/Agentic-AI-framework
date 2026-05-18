# config/ — Schemas, Policies, and Prompts

All configuration that drives the Genesis pipeline lives here. No Python code — only declarative definitions that Claude and the orchestrator read at runtime.

```
config/
├── schemas/        JSON Schema definitions for every Genesis artifact
├── policies/       Cedar and Rego policy rules for compliance gates
└── prompts/        Stage-level prompt templates used by the pipeline
```

---

## schemas/ — JSON Schemas

Every artifact Genesis writes has a schema here. The orchestrator validates outputs against these before advancing stages.

| Schema | Validates |
|---|---|
| `canonical_app_spec.schema.json` | The central canonical spec (screens, entities, APIs, flows) |
| `evidence_graph.schema.json` | The semantic graph export (nodes, edges, confidence scores) |
| `ulc_ir.schema.json` | Universal Low-Code Intermediate Representation |
| `confidence_report.schema.json` | BRD confidence gate output |
| `source_truth_report.schema.json` | Source truth resolution report |
| `brd/` | BRD design intent and mockup inventory schemas |
| `design/` | Design decision and quality score schemas |
| `planning/` | Stack decision schema |
| `visual/` | Visual layout tree and visual lock spec schemas |
| `reports/` | QA and scorecard schemas |

---

## policies/ — Compliance Policies

Policy rules that the compliance gate evaluates before approving output.

| Folder | Language | Purpose |
|---|---|---|
| `cedar/` | Cedar policy language | Attribute-based access control rules |
| `rego/` | Rego (Open Policy Agent) | General-purpose compliance rules |

---

## prompts/ — Stage Prompt Templates

Markdown prompt files that the orchestrator injects into Claude at specific pipeline stages. The routing is defined in `.genesis/genesis.routing.yaml`.

| Folder | Prompts for |
|---|---|
| `platform_adapters/` | Source inventory, video runtime, XML, PowerApps, Mendix, Appian, OutSystems |
| `design/` | Figma-to-UI, website-to-UI, screenshot-to-UI, magic selector, motion director |
| `generation/` | API contracts generation |
| `planning/` | Migration planning prompts |
| `brd/` | BRD analysis and understanding |
| `qa/` | QA and repair prompts |
| `review/` | Code review prompts |

Key root-level prompts:
- `ui_ux_pro_max.md` — UI/UX Pro Max design director brief
- `generator.md` — Core code generation system prompt
- `source_truth.md` — Source truth resolution prompt
- `qa.md` / `repair.md` / `review.md` — Quality and repair prompts

---

## How These Are Used

The orchestrator loads prompts dynamically at each stage. Path resolution:
```yaml
# .genesis/genesis.routing.yaml
appian_export_present:
  prompt: config/prompts/platform_adapters/appian.md
```

Schemas are validated by the orchestrator after each artifact is written:
```python
jsonschema.validate(artifact, schema)
```
