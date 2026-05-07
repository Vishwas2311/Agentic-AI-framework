# Backend Java Spring Generator Prompt

Generate Spring Boot backend from `canonical_app_spec.json`.

## Required

- entities
- DTOs
- repositories
- services
- controllers
- validation
- auth/roles
- health endpoint
- OpenAPI docs
- unit/API tests

## Rules

- Do not invent endpoints not in canonical spec.
- Keep business rules traceable to source evidence.
- Use Testcontainers for integration tests where possible.

