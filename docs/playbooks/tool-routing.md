# Genesis Tool Routing Playbook

## Routing Rules

```text
Figma URL present        → Figma MCP
Website URL present      → Firecrawl + Playwright
Screenshot present       → Vision + screenshot_to_ui prompt
DB connection present    → read-only DB adapter
OpenAPI present          → OpenAPI parser/generator
Low-code export present  → platform adapter
Generated app fails      → QA → specific repair agent
```

## Human Questions

Ask only for:

- missing source
- missing target stack
- credential reference
- low confidence
- source conflict
- deployment approval
- compliance decision
- protected media/license risk

