# config/policies — Policy Enforcement Rules

Defines what tools, actions, and outputs are permitted at each pipeline stage.

## Files

| File | Purpose |
|------|---------|
| `module.yaml` | Per-stage tool permission rules — what each stage may and may not call |

## How Policy Enforcement Works

`core/policy.py` reads `module.yaml` (and `genesis.policy.yaml` from `.genesis/`) before each stage runs:

```
orchestrator → policy.validate_stage(stage_name, tool_id)
  → if tool not in allowed list for this stage → raise PolicyViolation
  → stage proceeds only with permitted tools
```

## module.yaml Structure

```yaml
stages:
  generate_code:
    allowed_tools: [claude_code_generator, scaffold, acl_generator]
    denied_tools:  [database_write, deploy]
  run_quality_gates:
    allowed_tools: [bandit, semgrep, gitleaks, squawk, sqlfluff, pip_audit]
    denied_tools:  [code_generator]
```

## Tool Rule (from CLAUDE.md)

> Use only tools allowed for the active stage. If a tool is not listed, treat it as denied.

This means every adapter call goes through `policy.validate_stage()` first. Unapproved calls are blocked and logged to `runtime_session.json` as policy violations.

## Secret Rule

Policy also enforces the Secret Rule: no stage may write raw credentials to any output file or report. The policy module scans generated file content for credential patterns before allowing writes.

## genesis.policy.yaml (project-level)

The per-migration policy file in `.genesis/genesis.policy.yaml` can tighten (but never loosen) the global rules in `module.yaml`. This allows individual migrations to disable tools that are not appropriate for a specific client or compliance requirement.
