# Appian Adapter Prompt

Use this prompt during `extract_native_ast` for Appian sources.

## Goal

Extract Appian deployment package data into Genesis AST.

## Required Output

Produce `platform_ast.json` sections for:

- records
- interfaces
- expression rules
- process models
- integrations
- data types
- groups and permissions
- unsupported items

## Rules

- Treat process models as workflow graphs.
- Mark expression rules that cannot be safely translated as `manual`.
- Runtime evidence is required for approval flows and role-specific behavior.

