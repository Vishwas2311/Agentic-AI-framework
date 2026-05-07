from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_THRESHOLDS = {
    "visual_fidelity_score": 0.90,
    "ux_quality_score": 0.88,
    "accessibility_score": 0.95,
    "responsive_score": 0.92,
    "desktop_space_utilization_score": 0.85,
    "content_density_score": 0.84,
    "container_fit_score": 0.86,
    "motion_quality_score": 0.85,
    "component_reuse_score": 0.80,
}


def calculate_overall_score(scores: dict[str, float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores.values()) / len(scores), 4)


def evaluate_design_quality(
    scores: dict[str, float] | None = None,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    effective_scores = scores or {key: 0.0 for key in DEFAULT_THRESHOLDS}
    effective_thresholds = thresholds or DEFAULT_THRESHOLDS
    failures = [
        {
            "score": key,
            "actual": effective_scores.get(key, 0.0),
            "minimum": minimum,
        }
        for key, minimum in effective_thresholds.items()
        if effective_scores.get(key, 0.0) < minimum
    ]
    overall = calculate_overall_score(effective_scores)
    return {
        "schema_version": "3.1.0",
        "scores": effective_scores,
        "thresholds": effective_thresholds,
        "overall_design_quality_score": overall,
        "approved": not failures and overall >= 0.90,
        "failures": failures,
        "next_action": "approve" if not failures and overall >= 0.90 else "reject_and_run_ui_polish_loop",
    }


def write_design_quality_report(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
