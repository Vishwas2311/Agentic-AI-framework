# Database Postgres Generator Prompt

Generate PostgreSQL schema and migrations from `canonical_app_spec.json`.

## Required

- tables
- constraints
- indexes
- foreign keys
- seed data
- migration files
- rollback notes

## Rules

- Do not include real sensitive data in seed data.
- Preserve source constraints when supported.
- Mark stored procedure conversions for review.

