from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Stage:
    name: str
    objective: str
    skill: str | None
    produces: tuple[str, ...]


def stages_for_entrypoint(flow: dict[str, Any], entrypoint: str = "genesis-migrate") -> list[Stage]:
    entrypoints = flow.get("entrypoints", {})
    if entrypoint not in entrypoints:
        raise KeyError(f"Unknown Genesis entrypoint: {entrypoint}")
    ordered_names = entrypoints[entrypoint].get("stages", [])
    stage_defs = flow.get("stages", {})
    stages: list[Stage] = []
    for name in ordered_names:
        spec = stage_defs.get(name, {})
        stages.append(
            Stage(
                name=name,
                objective=str(spec.get("objective", "")),
                skill=spec.get("skill"),
                produces=tuple(spec.get("produces", [])),
            )
        )
    return stages


def validate_flow(flow: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    entrypoints = flow.get("entrypoints")
    stages = flow.get("stages")
    if not isinstance(entrypoints, dict):
        errors.append("flow.entrypoints must be a mapping")
    if not isinstance(stages, dict):
        errors.append("flow.stages must be a mapping")
    if isinstance(entrypoints, dict) and isinstance(stages, dict):
        for entrypoint_name, entrypoint in entrypoints.items():
            for stage_name in entrypoint.get("stages", []):
                if stage_name not in stages:
                    errors.append(f"entrypoint {entrypoint_name} references missing stage {stage_name}")
    return errors

