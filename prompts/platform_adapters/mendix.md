# Mendix Adapter Prompt

Use this prompt during `extract_native_ast` for Mendix sources.

## Goal

Extract Mendix source into Genesis AST using Mendix Model SDK / metamodel concepts.

## Required Output

Produce `platform_ast.json` sections for:

- domain models
- entities
- associations
- pages
- snippets
- microflows
- nanoflows
- validations
- roles and access rules
- integrations
- custom Java actions
- unsupported items

## Rules

- Do not treat raw unzip/XML parsing as sufficient when SDK/metamodel access is available.
- Mark custom Java, marketplace widgets, and undocumented runtime behavior as `manual` or `partial`.
- Include confidence per artifact.

