# PowerApps Adapter Prompt

Use this prompt during `extract_native_ast` for PowerApps sources.

## Goal

Extract PowerApps canvas app source into Genesis AST from Power Platform Git / `.msapp` unpacked `Src/*.pa.yaml` and Power Fx.

## Required Output

Produce `platform_ast.json` sections for:

- screens
- controls
- formulas
- variables
- collections
- data sources
- connectors
- navigation
- validations
- unsupported items

## Rules

- Do not rely on unstable internal JSON as source of truth.
- Parse formulas as Power Fx expressions when possible.
- Mark custom connectors and complex formulas as `partial` until runtime evidence confirms behavior.

