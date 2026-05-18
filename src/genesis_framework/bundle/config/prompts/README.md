# config/prompts — LLM System Prompts

Every prompt template used by Genesis agents. Prompts are plain Markdown files — the agent dispatcher injects workspace context (spec, graph, evidence) before sending to the LLM.

## Directory Structure

```
prompts/
├── brd/                        # BRD extraction prompts
│   ├── brd_design_extractor.md      # Extract screens, fields, workflows from BRD text
│   └── brd_mockup_extractor.md      # Extract UI mockup descriptions from BRD
├── design/                     # Design system and visual prompts
│   ├── design_decision_engine.md    # Drives design_strategy.py decisions
│   ├── figma_to_ui.md               # Translates Figma frames to component specs
│   ├── magic_selector.md            # Selects 21st.dev Magic component type
│   ├── motion_director.md           # Motion plan: purpose, pattern, fallback, QA
│   ├── screenshot_to_ui.md          # Vision: extracts UI structure from screenshots
│   ├── visual_fidelity/
│   │   ├── layout_geometry.md       # Layout region detection and sizing
│   │   ├── ui_polish_loop.md        # Iterative polish instructions
│   │   └── visual_lock_spec.md      # Locks visual spec before generation starts
│   └── website_to_ui.md             # Crawls live URL, extracts UI patterns
├── generation/                 # Code generation prompts
│   ├── frontend_react.md            # Next.js + Tailwind + shadcn/ui page generation
│   ├── backend_java_spring.md       # Java Spring Boot backend (alternate stack)
│   ├── api_contracts.md             # OpenAPI spec generation from canonical app spec
│   └── database_postgres.md         # PostgreSQL schema + migration SQL generation
├── planning/
│   └── stack_decision.md            # Prompt for stack_resolver.py LLM call
├── platform_adapters/          # Platform-specific extraction prompts
│   ├── powerapps.md                 # Power Apps screen/formula extraction
│   ├── mendix.md                    # Mendix page/microflow extraction
│   ├── appian.md                    # Appian SAIL/process model extraction
│   ├── outsystems.md                # OutSystems screen/action extraction
│   ├── structured.md                # DOCX/XLSX field and workflow extraction
│   ├── video_runtime.md             # Video frame analysis for UI evidence
│   ├── xml.md                       # Generic XML/config extraction
│   ├── archive.md                   # ZIP/archive unpacking and routing
│   ├── database.md                  # Database schema reverse-engineering
│   └── source_inventory.md          # Initial source type detection and routing
├── qa/                         # Quality assurance prompts
│   ├── accessibility_qa.md          # WCAG check instructions for the QA agent
│   ├── security_qa.md               # Security review instructions
│   ├── design_quality_gate.md       # Design quality evaluation criteria
│   └── visual_qa.md                 # Visual parity check instructions
├── review/
│   └── human_review.md              # Human gate presentation format
├── generator.md                # Top-level code generation meta-prompt
├── qa.md                       # Top-level QA agent meta-prompt
├── repair.md                   # Repair loop agent meta-prompt
├── source_truth.md             # Source truth resolution agent prompt
└── ui_ux_pro_max.md            # UI/UX Pro Max design director master prompt
```

## How Prompts Are Used

1. `agent_dispatcher.py` selects the prompt file for the current stage
2. Injects structured context (JSON from workspace) into the prompt template
3. Sends to LLM via `llm_client.py`
4. Response is parsed as structured JSON and written to the workspace output

## Key Prompts

| Prompt | Purpose | Called By |
|--------|---------|-----------|
| `ui_ux_pro_max.md` | Master design director — drives all UI decisions | `decide_design_strategy` |
| `generator.md` | Meta-prompt for all code generation | `generate_code` |
| `repair.md` | Self-repair instructions — sees failing check + code, proposes diff | `run_agent_repair_loop` |
| `source_truth.md` | Resolves conflicts between multiple source signals | `resolve_source_truth` |
