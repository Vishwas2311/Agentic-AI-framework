from pathlib import Path

from genesis_framework.generated_app_gate import (
    build_generated_app_patch_instructions,
    build_generated_app_review,
    normalize_generated_app_gate_decision,
    resolve_generated_app_approval_gate,
)


def test_generated_app_gate_normalizes_options() -> None:
    assert normalize_generated_app_gate_decision("A") == "approved"
    assert normalize_generated_app_gate_decision("reject") == "rejected"
    assert normalize_generated_app_gate_decision("extra input") == "additional_input"


def test_generated_app_review_detects_expected_outputs(tmp_path: Path) -> None:
    for relative_path in (
        "frontend/package.json",
        "frontend/app/page.tsx",
        "backend/app/main.py",
        "database/migration.sql",
        "tests/api/test_health.py",
        "tests/playwright/smoke.spec.ts",
    ):
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")
    review = build_generated_app_review(
        tmp_path,
        {"app": {"name": "Demo"}, "screens": [{"name": "Home"}], "entities": [], "workflows": []},
        {"files": []},
    )
    assert review["ready_for_repair_and_qa"] is False
    assert review["missing_expected_files"] == ["generated_file_manifest.json"]


def test_generated_app_gate_rejection_requires_reason() -> None:
    gate = resolve_generated_app_approval_gate(
        {"generated_app_gate_decision": "B"},
        {"missing_expected_files": []},
        app_name="Demo",
    )
    assert gate["status"] == "rejection_reason_required"
    assert gate["requires_human_confirmation"] is True
    assert "What is wrong" in gate["prompt_to_user"]


def test_generated_app_gate_additional_input_creates_patch_instruction() -> None:
    gate = resolve_generated_app_approval_gate(
        {"generated_app_gate_decision": "C", "generated_app_review_notes": "Add admin dashboard."},
        {"missing_expected_files": []},
        app_name="Demo",
    )
    instructions = build_generated_app_patch_instructions(gate, {"missing_expected_files": []})
    assert gate["status"] == "additional_input_received"
    assert gate["requires_human_confirmation"] is False
    assert instructions["instructions"][0]["type"] == "additional_requirement"
    assert instructions["semantic_patch"]["actions"][0]["target"] == "pages_or_screens"
