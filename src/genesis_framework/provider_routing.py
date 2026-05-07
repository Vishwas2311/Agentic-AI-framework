from __future__ import annotations

from typing import Any

from genesis_framework.intake import InputArtifact


STAGE_REASONING_MAP = {
    "resolve_source_truth": "high_reasoning",
    "resolve_conflicts": "high_reasoning",
    "validate_ir": "high_reasoning",
    "generate_code": "fast_generation",
    "run_agent_repair_loop": "high_reasoning",
    "run_visual_design_qa": "vision_capable",
    "evaluate_design_quality": "vision_capable",
    "learn_verified_patterns": "embedding",
}


def build_provider_routing_plan(
    routing_config: dict[str, Any],
    cost_config: dict[str, Any],
    request: dict[str, Any],
    artifacts: list[InputArtifact],
) -> dict[str, Any]:
    active_signals = sorted({artifact.signal for artifact in artifacts})
    preferred_providers = request.get("preferred_model_providers") or [
        "openai_compatible",
        "anthropic_compatible",
        "azure_openai_compatible",
        "local_openai_compatible",
    ]
    stage_model_map = []
    model_routing = routing_config.get("model_routing", {})
    for stage_name, reasoning_tier in STAGE_REASONING_MAP.items():
        use_cases = model_routing.get(reasoning_tier, {}).get("use_for", [])
        stage_model_map.append(
            {
                "stage": stage_name,
                "reasoning_tier": reasoning_tier,
                "recommended_provider_classes": preferred_providers,
                "rationale": _stage_rationale(stage_name),
                "matching_use_cases": use_cases[:6],
            }
        )
    return {
        "schema_version": "3.1.0",
        "principle": routing_config.get("principle"),
        "active_signals": active_signals,
        "preferred_provider_classes": preferred_providers,
        "budgets": cost_config.get("budgets", {}),
        "actions": cost_config.get("actions", {}),
        "stage_model_map": stage_model_map,
    }


def _stage_rationale(stage_name: str) -> str:
    if stage_name in {"resolve_source_truth", "resolve_conflicts", "validate_ir"}:
        return "Use stronger reasoning models when the framework must reconcile evidence or validate migration semantics."
    if stage_name in {"run_visual_design_qa", "evaluate_design_quality"}:
        return "Use vision-capable models when comparing screenshots, layouts, or visual acceptance rules."
    if stage_name == "learn_verified_patterns":
        return "Use embedding or retrieval-friendly models to organize reusable migration memory."
    if stage_name == "run_agent_repair_loop":
        return "Use strong coding models for repair and focused generation fixes."
    return "Use efficient generation models for deterministic expansion and reporting."
