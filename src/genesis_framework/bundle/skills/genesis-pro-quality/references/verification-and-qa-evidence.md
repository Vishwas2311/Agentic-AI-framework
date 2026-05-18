# Verification And QA Evidence Rules

Inspired by local verification-before-completion, test-engineer, and eval-harness skills.

## Core Rule

No completion, PASS, ready, approved, or fixed claim is valid unless it has fresh evidence.

## Evidence Requirements

Every required suite in `qa_evidence_manifest.json` must record:

- command or artifact source
- working directory
- start/end timestamp when command-backed
- exit code when command-backed
- stdout/stderr excerpt when command-backed
- artifact path
- pass/fail count when available
- target URL for runtime/browser/performance tests

## QAOS Mandatory Categories

- dependency validation
- database/schema/seed validation
- lint/type/build validation
- unit/component tests
- runtime launch and HTTP readiness
- Playwright functional sanity
- route/control click coverage
- console/page error scan
- API positive and negative behavior
- safe runtime security checks
- accessibility checks
- performance checks
- visual screenshots
- final approval gate

## Anti-Patterns To Block

- "should work" claims
- manually written PASS reports without command provenance
- skipped runtime checks shown as production-ready
- QA passing from static checks only
- final approval when local app did not start
