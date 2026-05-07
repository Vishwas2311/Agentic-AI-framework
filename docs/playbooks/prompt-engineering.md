# Genesis Prompt Engineering Playbook

## Core Pattern

Use stage prompts, not giant prompts.

```text
Governance: CLAUDE.md
Flow: .genesis/genesis.flow.yaml
Tool access: .genesis/genesis.tools.yaml
Policy: .genesis/genesis.policy.yaml
Stage prompt: prompts/<stage>.md
Output schema: schemas/*.json
```

## Required Decision Shape

Every non-trivial decision must include:

- source evidence
- assumptions
- reasoning summary
- confidence
- human review required

## Never Do This

```text
User prompt → final code
```

## Always Do This

```text
User input → AST → IR → canonical_app_spec.json → deterministic generation → evidence-backed QA
```

