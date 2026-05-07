from __future__ import annotations

from typing import Any

from genesis_framework.intake import InputArtifact


def build_agent_execution_plan(
    agents_config: dict[str, Any],
    stage_names: list[str],
    artifacts: list[InputArtifact],
) -> dict[str, Any]:
    agents = agents_config.get("agents", {})
    source_types = sorted({artifact.source_type for artifact in artifacts})
    stage_assignments: list[dict[str, Any]] = []
    active_agents: list[str] = []
    for stage_name in stage_names:
        assigned = []
        for agent_name, spec in agents.items():
            allowed = spec.get("allowed_stages", [])
            if stage_name in allowed:
                assigned.append(
                    {
                        "agent": agent_name,
                        "role": spec.get("role"),
                        "owns": spec.get("owns", []),
                        "mission": spec.get("mission"),
                    }
                )
                active_agents.append(agent_name)
        stage_assignments.append({"stage": stage_name, "agents": assigned})
    return {
        "schema_version": "3.1.0",
        "strategy": "parallel_by_stage_with_owned_outputs",
        "source_types": source_types,
        "active_agents": sorted(dict.fromkeys(active_agents)),
        "stage_assignments": stage_assignments,
        "coordination_rules": [
            "Extractors run before planners; planners run before generators.",
            "Agents own only their declared outputs and should not overwrite peer-owned areas without conflict reporting.",
            "Generation and repair agents consume canonical_app_spec.json rather than raw source files whenever possible.",
        ],
    }


def build_swarm_topology(plan: dict[str, Any]) -> dict[str, Any]:
    stage_assignments = plan.get("stage_assignments", [])
    edges: list[dict[str, str]] = []
    previous_agents: list[str] = []
    for stage in stage_assignments:
        current_agents = [item["agent"] for item in stage.get("agents", [])]
        for previous in previous_agents:
            for current in current_agents:
                edges.append({"from": previous, "to": current, "reason": "downstream_stage_dependency"})
        if current_agents:
            previous_agents = current_agents
    return {
        "schema_version": "3.1.0",
        "nodes": [
            {
                "agent": assignment["agent"],
                "role": assignment.get("role"),
            }
            for stage in stage_assignments
            for assignment in stage.get("agents", [])
        ],
        "edges": edges,
        "broadcast_channels": [
            "source_intake",
            "migration_planning",
            "generation",
            "qa_and_delivery",
        ],
    }
