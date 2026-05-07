from __future__ import annotations

from typing import Any


STATUS_SCORES = {
    "passed": 1.0,
    "passed_with_warnings": 0.82,
    "warning": 0.7,
    "skipped": 0.65,
    "failed": 0.2,
    "pending": 0.35,
    "approved": 1.0,
    "review_recommended": 0.45,
    "auto_passed": 0.85,
    "not_executed": 0.15,
    "unknown": 0.3,
}


def build_production_scorecard(
    confidence_scores: dict[str, Any],
    design_quality: dict[str, Any],
    code_quality: dict[str, Any],
    test_report: dict[str, Any],
    security_review: dict[str, Any],
    human_review: dict[str, Any],
    approval: dict[str, Any],
) -> dict[str, Any]:
    readiness_items = [
        {
            "name": "migration_confidence",
            "score": round(float(confidence_scores.get("overall_confidence", 0.0)), 4),
            "status": "passed" if float(confidence_scores.get("overall_confidence", 0.0)) >= 0.75 else "warning",
        },
        {
            "name": "design_quality",
            "score": round(float(design_quality.get("overall_design_quality_score", 0.0)), 4),
            "status": "approved" if design_quality.get("approved") else "pending",
        },
        {
            "name": "code_quality",
            "score": _status_score(code_quality.get("status")),
            "status": str(code_quality.get("status", "unknown")),
        },
        {
            "name": "test_gate",
            "score": _status_score(test_report.get("status")),
            "status": str(test_report.get("status", "unknown")),
        },
        {
            "name": "security_gate",
            "score": _status_score(security_review.get("status")),
            "status": str(security_review.get("status", "unknown")),
        },
        {
            "name": "human_review_gate",
            "score": _status_score(human_review.get("status")),
            "status": str(human_review.get("status", "unknown")),
        },
    ]

    blockers = []
    if not code_quality.get("gate_passed", False):
        blockers.append("code_quality_failed")
    if not test_report.get("gate_passed", False):
        blockers.append("test_gate_failed")
    if not security_review.get("gate_passed", False):
        blockers.append("security_gate_failed")
    if human_review.get("requires_human_review", False):
        blockers.append("human_review_required")
    if not design_quality.get("approved", False):
        blockers.append("design_quality_not_approved")

    overall_score = round(sum(item["score"] for item in readiness_items) / len(readiness_items), 4)
    if blockers:
        release_state = "blocked_pending_review"
    elif approval.get("status") == "approved":
        release_state = "approved_for_handoff"
    else:
        release_state = "ready_for_human_review"

    return {
        "schema_version": "3.1.0",
        "overall_score": overall_score,
        "release_state": release_state,
        "blockers": blockers,
        "checks": readiness_items,
        "recommended_next_steps": _recommended_next_steps(blockers),
    }


def _status_score(status: Any) -> float:
    return STATUS_SCORES.get(str(status), STATUS_SCORES["unknown"])


def _recommended_next_steps(blockers: list[str]) -> list[str]:
    if not blockers:
        return ["Proceed with human review and environment-specific deployment checks."]
    suggestions = []
    if "code_quality_failed" in blockers:
        suggestions.append("Review code_quality_report.json and fix the failing scaffold issues.")
    if "test_gate_failed" in blockers:
        suggestions.append("Review test_report.json and rerun the generated backend smoke test.")
    if "security_gate_failed" in blockers:
        suggestions.append("Remove hard-coded secrets and rerun the security gate.")
    if "human_review_required" in blockers:
        suggestions.append("Resolve source-truth conflicts or complete the requested human review.")
    if "design_quality_not_approved" in blockers:
        suggestions.append("Improve design quality signals or connect visual QA before final approval.")
    return suggestions
