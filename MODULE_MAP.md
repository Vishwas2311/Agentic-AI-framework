# NoCode2ProCode by TrustEngines Module Map

This project is organized as a Claude Code-native enterprise framework.

## Top-Level Areas

- `apps/`: user-facing apps and services: CLI, API, dashboard.
- `packages/`: framework runtime modules shared by apps and agents.
- `packages/visual-fidelity`: visual source to testable UI contract and polish loop.
- `packages/layout-compiler`: screenshot/Figma/DOM geometry extraction.
- `packages/design-token-engine`: token extraction and normalization.
- `packages/component-matcher`: maps visual nodes to component registry items.
- `packages/visual-lock`: exact/modernized fidelity constraints.
- `packages/ui-polish-loop`: closed-loop screenshot diff and UI patching.
- `adapters/`: source adapters for low-code platforms, design sources, data stores, and API specs.
- `generators/`: deterministic generators for backend, frontend, DB, tests, deploy, observability, and docs.
- `agents/`: Claude Code agent role definitions, prompts, and ownership rules.
- `migration_inputs/`: default intake folder where source files and `migration_request.yaml` are placed before running `nocode2procode migrate`.
- `policies/`: OPA/Rego and Cedar policy packs.
- `benchmarks/`: fixture migrations used to certify adapters and generators.
- `examples/`: example projects and demo inputs.
- `mcp/`: MCP server configuration profiles and gateway rules.
- `memory/`: vector and graph memory schemas/configs, plus verified runtime memory packets.
- `evidence/`: sample evidence graph artifacts and traceability examples.
- `runtime/`: sandbox, Playwright, Firecrawl, session, and browser-protocol helpers.
- `compliance/`: compliance packs for EU AI Act, GDPR, HIPAA, and SOC2.

## Rule

Do not put implementation directly in random folders. Every module should declare ownership in its `module.yaml`.
