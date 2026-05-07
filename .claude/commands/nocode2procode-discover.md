# /nocode2procode-discover

Discover source metadata, runtime behavior, design evidence, assets, APIs, and database schema before generation.

## Required Behavior

1. Read `.genesis/genesis.flow.yaml`, `.genesis/genesis.routing.yaml`, and `.genesis/genesis.tools.yaml`.
2. Default to `migration_inputs/` as the source intake folder when the user does not provide an explicit input path.
3. Use only source-appropriate tools such as Firecrawl, Playwright, Figma MCP, platform adapters, or read-only DB inspection.
4. Produce `source_baseline.json`, `runtime_evidence.json`, `asset_inventory.json`, and privacy/license scan reports where applicable.
