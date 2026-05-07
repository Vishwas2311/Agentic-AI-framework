from pathlib import Path

import json

from genesis_framework.approval_gates import (
    collect_human_gate_context,
    resolve_canonical_spec_gate,
    resolve_design_system_gate,
    resolve_final_release_gate,
    resolve_qa_result_gate,
    resolve_source_truth_gate,
)


def test_source_truth_gate_requires_review_when_conflicts_exist() -> None:
    bundle = resolve_source_truth_gate(
        {},
        {"decisions": [{"artifact_id": "ui_surface", "requires_human_review": True}]},
        {"conflicts": [{"artifact_id": "ui_surface"}]},
        app_name="Demo",
    )

    assert bundle["gate"]["status"] == "review_recommended"
    assert bundle["gate"]["requires_human_confirmation"] is True
    assert bundle["approved_report"]["approval_gate"]["pipeline_sequence_changed"] is False


def test_canonical_spec_gate_adds_human_scope_to_approved_spec() -> None:
    bundle = resolve_canonical_spec_gate(
        {"canonical_spec_gate_decision": "B", "canonical_spec_notes": "Add admin approval queue page."},
        {"screens": [], "ui_spec": {"screens": []}, "workflow_spec": {"workflows": []}},
        app_name="Demo",
    )

    assert bundle["gate"]["requires_human_confirmation"] is False
    assert bundle["approved_spec"]["screens"][0]["name"] == "Admin Approval Queue"
    assert bundle["patch_instructions"]["next_pipeline_stage"] == "decide_design_strategy"


def test_design_system_gate_carries_style_notes() -> None:
    bundle = resolve_design_system_gate(
        {"design_gate_decision": "B", "design_gate_notes": "Change theme to healthcare blue and white."},
        {"design_tokens": {}, "visual_acceptance_criteria": []},
        app_name="Demo",
    )

    assert bundle["gate"]["status"] == "change_style_received"
    assert bundle["approved_plan"]["design_tokens"]["human_overrides"]
    assert bundle["patch_instructions"]["pipeline_sequence_changed"] is False


def test_qa_result_gate_flags_quality_blockers() -> None:
    bundle = resolve_qa_result_gate(
        {},
        {
            "code_quality_report": {"gate_passed": False, "status": "failed"},
            "test_report": {"gate_passed": True, "status": "passed"},
            "security_review": {"gate_passed": True, "status": "passed"},
            "design_quality_score": {"approved": True},
        },
        app_name="Demo",
    )

    assert bundle["gate"]["status"] == "review_recommended"
    assert bundle["gate"]["requires_human_confirmation"] is True
    assert bundle["qa_summary"]["blockers"] == ["code_quality_report:failed"]


def test_final_release_gate_supports_demo_only_approval() -> None:
    bundle = resolve_final_release_gate(
        {"final_approval_decision": "B"},
        {"blockers": ["deployment_not_configured"]},
        app_name="Demo",
    )

    assert bundle["gate"]["selected_action"] == "approve_demo_only"
    assert bundle["gate"]["status"] == "approved_demo_only"
    assert bundle["gate"]["requires_human_confirmation"] is False


def test_collect_human_gate_context_lists_pending_gates(tmp_path: Path) -> None:
    (tmp_path / "source_truth_approval_gate.json").write_text(
        json.dumps({"requires_human_confirmation": True, "status": "review_recommended"}),
        encoding="utf-8",
    )
    (tmp_path / "generated_app_approval_gate.json").write_text(
        json.dumps({"requires_human_confirmation": False, "status": "approved"}),
        encoding="utf-8",
    )

    context = collect_human_gate_context(tmp_path)

    assert context["pipeline_sequence_changed"] is False
    assert context["pending_confirmation_gates"] == ["source_truth_approval_gate"]
