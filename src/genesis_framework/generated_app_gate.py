from __future__ import annotations

from pathlib import Path
from typing import Any

from genesis_framework.human_patch import build_generated_app_semantic_patch


GENERATED_APP_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve generated app",
        "description": "Approve the frontend/backend/database output generated so far and continue the fixed pipeline.",
    },
    {
        "code": "B",
        "action": "rejected",
        "label": "Reject generated app",
        "description": "Explain what is wrong so the next repair-loop stage can use that feedback.",
    },
    {
        "code": "C",
        "action": "additional_input",
        "label": "Add extra input or missing requirement",
        "description": "Add a missing requirement or instruction before the repair and QA stages continue.",
    },
]


_DECISION_ALIASES = {
    "a": "approved",
    "approve": "approved",
    "approved": "approved",
    "yes": "approved",
    "ok": "approved",
    "proceed": "approved",
    "b": "rejected",
    "reject": "rejected",
    "rejected": "rejected",
    "wrong": "rejected",
    "not_approved": "rejected",
    "c": "additional_input",
    "add": "additional_input",
    "add_input": "additional_input",
    "additional_input": "additional_input",
    "missing_requirement": "additional_input",
    "extra_input": "additional_input",
}


def normalize_generated_app_gate_decision(value: str | None) -> str | None:
    if not value:
        return None
    key = "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")
    while "__" in key:
        key = key.replace("__", "_")
    return _DECISION_ALIASES.get(key)


def build_generated_app_review(
    workspace: Path,
    canonical_spec: dict[str, Any],
    generated_manifest: dict[str, Any],
) -> dict[str, Any]:
    frontend_files = _relative_files(workspace / "frontend", workspace)
    backend_files = _relative_files(workspace / "backend", workspace)
    database_files = _relative_files(workspace / "database", workspace)
    test_files = _relative_files(workspace / "tests", workspace)
    docs_files = _relative_files(workspace / "docs", workspace)
    run_files = sorted(path.name for path in workspace.glob("run*.ps1"))
    expected_files = [
        "frontend/package.json",
        "frontend/app/page.tsx",
        "backend/app/main.py",
        "database/migration.sql",
        "tests/api/test_health.py",
        "tests/playwright/smoke.spec.ts",
        "generated_file_manifest.json",
    ]
    missing = [item for item in expected_files if not (workspace / item).exists()]
    mode = canonical_spec.get("migration_mode", {})
    return {
        "schema_version": "3.1.0",
        "app_name": canonical_spec.get("app", {}).get("name"),
        "selected_migration_output_mode": canonical_spec.get("selected_migration_output_mode"),
        "migration_output_label": mode.get("selected_label"),
        "technology_profile": mode.get("technology"),
        "target_stack": canonical_spec.get("target_stack"),
        "generated_manifest_file_count": len(generated_manifest.get("files", []) or []),
        "frontend": {
            "file_count": len(frontend_files),
            "key_files": _limit(frontend_files),
            "routes": _read_routes(workspace),
        },
        "backend": {
            "file_count": len(backend_files),
            "key_files": _limit(backend_files),
            "health_endpoint_expected": "backend/app/main.py" in backend_files,
        },
        "database": {
            "file_count": len(database_files),
            "key_files": _limit(database_files),
        },
        "tests": {
            "file_count": len(test_files),
            "key_files": _limit(test_files),
        },
        "docs": {
            "file_count": len(docs_files),
            "key_files": _limit(docs_files),
        },
        "run_files": run_files,
        "canonical_alignment": {
            "screen_count": len(canonical_spec.get("screens", []) or []),
            "entity_count": len(canonical_spec.get("entities", []) or []),
            "workflow_count": len(canonical_spec.get("workflows", []) or []),
            "acceptance_criteria_count": len(canonical_spec.get("acceptance_criteria", []) or []),
        },
        "missing_expected_files": missing,
        "ready_for_repair_and_qa": not missing,
    }


def resolve_generated_app_approval_gate(
    request: dict[str, Any],
    review: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    explicit_raw = _first_text(
        request.get("generated_app_gate_decision"),
        request.get("generated_app_review_decision"),
        request.get("generated_app_approval"),
        request.get("post_generation_approval"),
    )
    action = normalize_generated_app_gate_decision(explicit_raw)
    notes = _first_text(
        request.get("generated_app_review_notes"),
        request.get("generated_app_rejection_reason"),
        request.get("generated_app_extra_input"),
        request.get("post_generation_notes"),
    )

    status = "pending_review"
    requires_confirmation = True
    reason = "Generated app output needs human approval, rejection reason, or extra input before final approval can be granted."
    if action == "approved":
        status = "approved"
        requires_confirmation = False
        reason = "User approved generated frontend/backend/database output generated so far."
    elif action == "rejected" and notes:
        status = "rejected_with_reason"
        requires_confirmation = False
        reason = "User rejected generated output and supplied repair feedback for the next repair-loop stage."
    elif action == "rejected":
        status = "rejection_reason_required"
        reason = "User selected reject; Genesis must ask what is wrong with the generated app."
    elif action == "additional_input" and notes:
        status = "additional_input_received"
        requires_confirmation = False
        reason = "User supplied extra input or a missing requirement for the next repair-loop stage."
    elif action == "additional_input":
        status = "additional_input_required"
        reason = "User selected add input; Genesis must ask for the extra input or missing requirement."
    else:
        action = "pending_review"

    patch_instructions = _patch_instructions(action, status, notes, review)
    return {
        "schema_version": "3.1.0",
        "app_name": app_name,
        "question": "Generated App Approval Gate: approve generated output, reject with reason, or add missing input before repair and QA continue.",
        "options": GENERATED_APP_GATE_OPTIONS,
        "selected_action": action,
        "status": status,
        "requires_human_confirmation": requires_confirmation,
        "reason": reason,
        "human_notes": notes or "",
        "prompt_to_user": _prompt_to_user(action, status),
        "review_summary": review,
        "patch_instruction_status": patch_instructions["status"],
        "patch_instruction_count": len(patch_instructions["instructions"]),
    }


def build_generated_app_human_notes(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "3.1.0",
        "status": gate["status"],
        "selected_action": gate["selected_action"],
        "requires_human_confirmation": gate["requires_human_confirmation"],
        "human_notes": gate.get("human_notes", ""),
        "prompt_to_user": gate.get("prompt_to_user", ""),
    }


def build_generated_app_patch_instructions(gate: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    return _patch_instructions(gate["selected_action"], gate["status"], gate.get("human_notes"), review)


def _patch_instructions(action: str, status: str, notes: str | None, review: dict[str, Any]) -> dict[str, Any]:
    instructions: list[dict[str, Any]] = []
    semantic_patch = build_generated_app_semantic_patch(notes or "", action=action)
    if review.get("missing_expected_files"):
        instructions.append(
            {
                "type": "missing_expected_files",
                "priority": "high",
                "instruction": "Regenerate or patch missing required generated app files before QA.",
                "items": review["missing_expected_files"],
            }
        )
    if action == "rejected" and notes:
        instructions.append(
            {
                "type": "human_rejection",
                "priority": "high",
                "instruction": notes,
                "semantic_actions": semantic_patch["actions"],
                "target_stage": "run_agent_repair_loop",
            }
        )
    elif action == "additional_input" and notes:
        instructions.append(
            {
                "type": "additional_requirement",
                "priority": "high",
                "instruction": notes,
                "semantic_actions": semantic_patch["actions"],
                "target_stage": "run_agent_repair_loop",
            }
        )
    return {
        "schema_version": "3.1.0",
        "status": "ready_for_repair_loop" if instructions else "no_patch_requested",
        "source_gate_status": status,
        "semantic_patch": semantic_patch,
        "instructions": instructions,
        "next_pipeline_stage": "run_agent_repair_loop",
        "pipeline_sequence_changed": False,
    }


def _prompt_to_user(action: str, status: str) -> str:
    if status == "rejection_reason_required":
        return "What is wrong with the generated app? Please provide the rejection reason."
    if status == "additional_input_required":
        return "What extra input or missing requirement should Genesis add before repair and QA continue?"
    if action == "pending_review":
        return "Please approve, reject with reason, or add missing input for the generated app."
    return "No extra user input is required for this gate."


def _relative_files(directory: Path, workspace: Path) -> list[str]:
    if not directory.exists():
        return []
    return sorted(str(path.relative_to(workspace)).replace("\\", "/") for path in directory.rglob("*") if path.is_file())


def _limit(items: list[str], limit: int = 20) -> list[str]:
    return items[:limit]


def _read_routes(workspace: Path) -> list[dict[str, Any]]:
    routes_path = workspace / "frontend" / "routes.json"
    if not routes_path.exists():
        return []
    try:
        import json

        data = json.loads(routes_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    routes = data.get("routes", [])
    return routes if isinstance(routes, list) else []


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None
