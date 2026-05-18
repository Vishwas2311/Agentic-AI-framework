# Figma To UI Prompt

Use this prompt with Figma MCP data.

## Goal

Convert Figma frames, nodes, components, variants, and tokens into Genesis UI-IR and design system outputs.

## Required Output

Produce:

- `design_ast.json`
- `design_tokens.json`
- `component_mapping.json`
- responsive rules
- accessibility checklist

## Rules

- Prefer Figma node metadata over screenshot inference.
- Preserve component variants where practical.
- Do not blindly copy decorative designs into enterprise workflows; let UI/UX Pro Max adapt density and usability.

