from __future__ import annotations

from typing import Any


class PolicyDecision:
    def __init__(self, allowed: bool, reason: str) -> None:
        self.allowed = allowed
        self.reason = reason

    def __bool__(self) -> bool:
        return self.allowed


def is_tool_allowed(tools_config: dict[str, Any], stage: str, tool: str) -> PolicyDecision:
    stages = tools_config.get("stages", {})
    stage_config = stages.get(stage)
    if stage_config is None:
        return PolicyDecision(False, f"Unknown stage: {stage}")

    denied = set(stage_config.get("denied_tools", []))
    if tool in denied:
        return PolicyDecision(False, f"Tool {tool} is denied during {stage}")

    allowed = set(stage_config.get("allowed_tools", []))
    if tool in allowed:
        return PolicyDecision(True, f"Tool {tool} is allowed during {stage}")

    if tools_config.get("defaults", {}).get("unknown_tool") == "deny":
        return PolicyDecision(False, f"Tool {tool} is not allowlisted during {stage}")

    return PolicyDecision(True, f"Tool {tool} allowed by default")

