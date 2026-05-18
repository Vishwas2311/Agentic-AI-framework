# Skill Loading Patterns

Use this reference at migration startup and stage execution.

OpenHands is useful because it merges skills from multiple sources while keeping context stage-specific. Genesis should use the same principle locally:

- Load Genesis core first.
- Load `genesis-pro-quality` second.
- Load `genesis-openhands-dev-quality` third.
- Load only the reference file needed for the active stage.
- Record loaded skills in `active_skill_context.json`.
- Do not let a skill override Genesis flow, gate policy, stack selection, QAOS, or installer behavior.
- If a skill asks for a cloud/MCP/API tool, verify selected-stack need and credentials first; otherwise record `not_required_for_selected_stack` or `not_used_credentials_missing`.

Skill loading must remain deterministic and no-MCP by default.
