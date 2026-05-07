# Database Adapter Prompt

Use this prompt when a DB connection/schema is provided.

## Goal

Extract database structure and sample-safe behavior into DB AST and domain hints.

## Required Output

Produce:

- `db_ast.json`
- entity candidates
- relationship candidates
- constraints
- indexes
- views
- stored procedure inventory
- sample data profile with sensitive fields masked

## Rules

- Use read-only access during discovery.
- Never export raw sensitive data.
- Stored procedures are not auto-converted without review.

