# Genesis Stage Guide

Use this reference when deciding what to do in each stage.

## Discovery

Collect source export metadata, runtime evidence, API contracts, DB schemas, screenshots, design sources, and assets.

## Source Truth

When sources disagree, do not guess silently. Apply source truth rules. If confidence is low, require human review.

## IR

Build domain, workflow, UI, integration, security, design, and deployment IRs. Validate with schemas.

## Generation

Generate from `canonical_app_spec.json`. Do not generate from prompt vibes.

## Repair

Use small scoped patches. Run tests after patches. Keep agent ownership boundaries.

## Approval

Approval requires build, tests, security, visual, accessibility, SBOM, policy, replay, and traceability.

