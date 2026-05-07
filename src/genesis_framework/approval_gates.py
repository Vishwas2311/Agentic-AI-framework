from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from genesis_framework.human_patch import parse_human_patch_notes


SOURCE_TRUTH_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve source truth",
        "description": "Accept Genesis source-truth decisions and continue the fixed migration pipeline.",
    },
    {
        "code": "B",
        "action": "correct_assumption",
        "label": "Correct assumption",
        "description": "Tell Genesis which source, rule, or assumption is wrong so downstream agents use the correction.",
    },
    {
        "code": "C",
        "action": "add_evidence",
        "label": "Add more evidence",
        "description": "Add missing evidence notes before IR and canonical planning continue.",
    },
    {
        "code": "D",
        "action": "reject_decision",
        "label": "Reject truth decision",
        "description": "Reject a source-truth decision with a reason and carry that reason into downstream planning.",
    },
]


CANONICAL_SPEC_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve app spec",
        "description": "Freeze the canonical app spec and continue to design planning.",
    },
    {
        "code": "B",
        "action": "add_scope",
        "label": "Add screen, workflow, entity, or rule",
        "description": "Add missing application scope before design and generation continue.",
    },
    {
        "code": "C",
        "action": "remove_scope",
        "label": "Remove wrong item",
        "description": "Remove a wrong screen, workflow, entity, role, or requirement from the approved spec.",
    },
    {
        "code": "D",
        "action": "edit_spec",
        "label": "Reject or edit spec",
        "description": "Provide correction notes and continue with a patched approved canonical spec.",
    },
]


DESIGN_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve design system",
        "description": "Approve UX direction, tokens, components, and visual criteria before code generation.",
    },
    {
        "code": "B",
        "action": "change_style",
        "label": "Change style or theme",
        "description": "Add style, color, typography, density, or motion notes for frontend agents.",
    },
    {
        "code": "C",
        "action": "add_ux_requirement",
        "label": "Add UX requirement",
        "description": "Add missing accessibility, layout, usability, or interaction requirements.",
    },
    {
        "code": "D",
        "action": "reject_design",
        "label": "Reject design direction",
        "description": "Reject the generated design plan with correction notes before code generation.",
    },
]


QA_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve QA results",
        "description": "Accept the QA/security/visual results and continue to replay and final approval.",
    },
    {
        "code": "B",
        "action": "reject_quality",
        "label": "Reject quality result",
        "description": "Explain the quality issue so repair agents can use it in the next run or manual patch pass.",
    },
    {
        "code": "C",
        "action": "add_test_requirement",
        "label": "Add more test requirement",
        "description": "Add missing unit, API, UI, visual, accessibility, or security checks.",
    },
    {
        "code": "D",
        "action": "request_repair",
        "label": "Request repair",
        "description": "Ask repair agents to fix or polish specific QA findings while the pipeline continues.",
    },
]


FINAL_RELEASE_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve final delivery",
        "description": "Approve the final generated package for handoff and verified learning.",
    },
    {
        "code": "B",
        "action": "approve_demo_only",
        "label": "Approve demo only",
        "description": "Accept the localhost/demo output but keep production handoff blocked.",
    },
    {
        "code": "C",
        "action": "reject_final_output",
        "label": "Reject final output",
        "description": "Reject final delivery with handoff notes and keep final approval pending.",
    },
    {
        "code": "D",
        "action": "add_handoff_notes",
        "label": "Add final handoff notes",
        "description": "Attach final customer notes while preserving the pipeline sequence.",
    },
]


_COMMON_APPROVAL_ALIASES = {
    "a": "approved",
    "approve": "approved",
    "approved": "approved",
    "yes": "approved",
    "ok": "approved",
    "proceed": "approved",
}


def resolve_source_truth_gate(
    request: dict[str, Any],
    source_truth_report: dict[str, Any],
    source_conflict_report: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    action = _normalize_decision(
        _first_text(
            request.get("source_truth_gate_decision"),
            request.get("source_truth_decision"),
            request.get("truth_gate_decision"),
        ),
        {
            **_COMMON_APPROVAL_ALIASES,
            "b": "correct_assumption",
            "correct": "correct_assumption",
            "correct_assumption": "correct_assumption",
            "c": "add_evidence",
            "add_evidence": "add_evidence",
            "more_evidence": "add_evidence",
            "d": "reject_decision",
            "reject": "reject_decision",
            "reject_decision": "reject_decision",
        },
    )
    notes = _first_text(
        request.get("source_truth_notes"),
        request.get("source_truth_correction"),
        request.get("source_truth_extra_evidence"),
        request.get("truth_gate_notes"),
    )
    conflict_count = len(source_conflict_report.get("conflicts", []) or [])
    default_status = "review_recommended" if conflict_count else "auto_ready"
    gate = _resolve_gate(
        gate_id="source_truth_approval_gate",
        app_name=app_name,
        question="Source Truth Gate: approve Genesis truth decisions or provide correction/evidence before IR planning continues.",
        options=SOURCE_TRUTH_GATE_OPTIONS,
        action=action,
        notes=notes,
        default_status=default_status,
        default_requires_confirmation=bool(conflict_count),
        note_required_actions={"correct_assumption", "add_evidence", "reject_decision"},
        next_stage="build_ulc_ir",
    )
    patch = _semantic_patch(notes or "", source="source_truth_gate")
    approved_report = deepcopy(source_truth_report)
    approved_report["approval_gate"] = _gate_summary(gate)
    approved_report["human_truth_patch"] = patch
    approved_report["source_conflict_count"] = conflict_count
    return {
        "gate": gate,
        "approved_report": approved_report,
        "human_notes": _human_notes(gate),
        "patch_instructions": _patch_instruction_bundle(gate, patch, "build_ulc_ir"),
    }


def resolve_canonical_spec_gate(
    request: dict[str, Any],
    canonical_spec: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    action = _normalize_decision(
        _first_text(
            request.get("canonical_spec_gate_decision"),
            request.get("canonical_gate_decision"),
            request.get("app_spec_gate_decision"),
            request.get("spec_gate_decision"),
        ),
        {
            **_COMMON_APPROVAL_ALIASES,
            "b": "add_scope",
            "add": "add_scope",
            "add_scope": "add_scope",
            "add_screen": "add_scope",
            "add_workflow": "add_scope",
            "c": "remove_scope",
            "remove": "remove_scope",
            "remove_scope": "remove_scope",
            "d": "edit_spec",
            "edit": "edit_spec",
            "reject": "edit_spec",
            "edit_spec": "edit_spec",
        },
    )
    notes = _first_text(
        request.get("canonical_spec_notes"),
        request.get("canonical_spec_changes"),
        request.get("app_spec_notes"),
        request.get("spec_gate_notes"),
    )
    gate = _resolve_gate(
        gate_id="canonical_spec_approval_gate",
        app_name=app_name,
        question="Canonical Spec Gate: approve the app blueprint or provide scope changes before design planning continues.",
        options=CANONICAL_SPEC_GATE_OPTIONS,
        action=action,
        notes=notes,
        default_status="pending_review",
        default_requires_confirmation=True,
        note_required_actions={"add_scope", "remove_scope", "edit_spec"},
        next_stage="human_review_gate",
    )
    patched_spec, patch = _apply_spec_patch(canonical_spec, notes or "", source="canonical_spec_gate")
    patched_spec["canonical_spec_approval_gate"] = _gate_summary(gate)
    return {
        "gate": gate,
        "approved_spec": patched_spec,
        "human_notes": _human_notes(gate),
        "patch_instructions": _patch_instruction_bundle(gate, patch, "decide_design_strategy"),
        "semantic_patch": patch,
    }


def resolve_design_system_gate(
    request: dict[str, Any],
    design_bundle: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    action = _normalize_decision(
        _first_text(
            request.get("design_system_gate_decision"),
            request.get("design_gate_decision"),
            request.get("ux_gate_decision"),
        ),
        {
            **_COMMON_APPROVAL_ALIASES,
            "b": "change_style",
            "style": "change_style",
            "change_style": "change_style",
            "theme": "change_style",
            "c": "add_ux_requirement",
            "ux": "add_ux_requirement",
            "add_ux": "add_ux_requirement",
            "add_ux_requirement": "add_ux_requirement",
            "d": "reject_design",
            "reject": "reject_design",
            "reject_design": "reject_design",
        },
    )
    notes = _first_text(
        request.get("design_system_notes"),
        request.get("design_gate_notes"),
        request.get("ux_notes"),
        request.get("visual_design_changes"),
    )
    gate = _resolve_gate(
        gate_id="design_system_approval_gate",
        app_name=app_name,
        question="Design System Gate: approve UX direction or provide visual/UX changes before code generation.",
        options=DESIGN_GATE_OPTIONS,
        action=action,
        notes=notes,
        default_status="pending_review",
        default_requires_confirmation=True,
        note_required_actions={"change_style", "add_ux_requirement", "reject_design"},
        next_stage="generate_code",
    )
    patch = _semantic_patch(notes or "", source="design_system_gate")
    approved_plan = deepcopy(design_bundle)
    approved_plan["approval_gate"] = _gate_summary(gate)
    approved_plan["human_design_patch"] = patch
    if notes:
        approved_plan.setdefault("design_tokens", {}).setdefault("human_overrides", []).append(notes)
        approved_plan.setdefault("visual_acceptance_criteria", []).append(
            f"Human design gate note: {notes}"
        )
    return {
        "gate": gate,
        "approved_plan": approved_plan,
        "human_notes": _human_notes(gate),
        "patch_instructions": _patch_instruction_bundle(gate, patch, "generate_code"),
        "semantic_patch": patch,
    }


def resolve_qa_result_gate(
    request: dict[str, Any],
    qa_bundle: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    action = _normalize_decision(
        _first_text(
            request.get("qa_result_gate_decision"),
            request.get("qa_gate_decision"),
            request.get("quality_gate_decision"),
        ),
        {
            **_COMMON_APPROVAL_ALIASES,
            "b": "reject_quality",
            "reject": "reject_quality",
            "reject_quality": "reject_quality",
            "c": "add_test_requirement",
            "add_test": "add_test_requirement",
            "add_test_requirement": "add_test_requirement",
            "d": "request_repair",
            "repair": "request_repair",
            "request_repair": "request_repair",
        },
    )
    notes = _first_text(
        request.get("qa_result_notes"),
        request.get("qa_gate_notes"),
        request.get("quality_gate_notes"),
        request.get("test_requirement_notes"),
    )
    blocker_count = len(_qa_blockers(qa_bundle))
    gate = _resolve_gate(
        gate_id="qa_result_approval_gate",
        app_name=app_name,
        question="QA Result Gate: approve quality results or provide repair/test notes before replay and final approval.",
        options=QA_GATE_OPTIONS,
        action=action,
        notes=notes,
        default_status="review_recommended" if blocker_count else "auto_ready",
        default_requires_confirmation=bool(blocker_count),
        note_required_actions={"reject_quality", "add_test_requirement", "request_repair"},
        next_stage="build_replay_dashboard",
    )
    patch = _semantic_patch(notes or "", source="qa_result_gate")
    return {
        "gate": gate,
        "qa_summary": {
            "schema_version": "3.1.0",
            "app_name": app_name,
            "blockers": _qa_blockers(qa_bundle),
            "reports": qa_bundle,
            "approval_gate": _gate_summary(gate),
        },
        "human_notes": _human_notes(gate),
        "repair_instructions": _patch_instruction_bundle(gate, patch, "run_agent_repair_loop"),
        "semantic_patch": patch,
    }


def resolve_final_release_gate(
    request: dict[str, Any],
    final_context: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    action = _normalize_decision(
        _first_text(
            request.get("final_release_gate_decision"),
            request.get("final_approval_decision"),
            request.get("release_gate_decision"),
        ),
        {
            **_COMMON_APPROVAL_ALIASES,
            "b": "approve_demo_only",
            "demo": "approve_demo_only",
            "approve_demo_only": "approve_demo_only",
            "c": "reject_final_output",
            "reject": "reject_final_output",
            "reject_final_output": "reject_final_output",
            "d": "add_handoff_notes",
            "notes": "add_handoff_notes",
            "add_handoff_notes": "add_handoff_notes",
        },
    )
    notes = _first_text(
        request.get("final_release_notes"),
        request.get("final_approval_notes"),
        request.get("handoff_notes"),
    )
    has_blockers = bool(final_context.get("blockers"))
    gate = _resolve_gate(
        gate_id="final_release_approval_gate",
        app_name=app_name,
        question="Final Release Gate: approve final delivery, approve demo only, reject, or add handoff notes.",
        options=FINAL_RELEASE_GATE_OPTIONS,
        action=action,
        notes=notes,
        default_status="review_recommended" if has_blockers else "pending_review",
        default_requires_confirmation=True,
        note_required_actions={"reject_final_output", "add_handoff_notes"},
        next_stage="deliver_github_pr",
    )
    if gate["selected_action"] == "approve_demo_only":
        gate["status"] = "approved_demo_only"
        gate["requires_human_confirmation"] = False
    return {
        "gate": gate,
        "human_notes": _human_notes(gate),
        "release_context": {**final_context, "approval_gate": _gate_summary(gate)},
    }


def collect_human_gate_context(workspace: Path) -> dict[str, Any]:
    files = [
        "brd_understanding_gate.json",
        "migration_mode_decision.json",
        "source_truth_approval_gate.json",
        "canonical_spec_approval_gate.json",
        "human_review_decisions.json",
        "design_system_approval_gate.json",
        "generated_app_approval_gate.json",
        "qa_result_approval_gate.json",
        "final_release_approval_gate.json",
    ]
    gates = {}
    pending = []
    for file_name in files:
        path = workspace / file_name
        if not path.exists():
            continue
        try:
            data = _read_json(path)
        except Exception:
            continue
        gates[file_name.removesuffix(".json")] = data
        if data.get("requires_human_confirmation"):
            pending.append(file_name.removesuffix(".json"))
    return {
        "schema_version": "3.1.0",
        "pipeline_sequence_changed": False,
        "purpose": "Human gate decisions are structured input for downstream agents. They do not skip or reorder stages.",
        "pending_confirmation_gates": pending,
        "gates": gates,
    }


def _resolve_gate(
    *,
    gate_id: str,
    app_name: str,
    question: str,
    options: list[dict[str, str]],
    action: str | None,
    notes: str | None,
    default_status: str,
    default_requires_confirmation: bool,
    note_required_actions: set[str],
    next_stage: str,
) -> dict[str, Any]:
    selected = action or "pending_review"
    status = default_status if action is None else selected
    requires_confirmation = default_requires_confirmation if action is None else False
    reason = "Gate has no explicit user decision yet; Genesis will keep the decision visible and continue only as a reviewable pipeline artifact."
    if selected == "approved":
        status = "approved"
        requires_confirmation = False
        reason = "User approved this gate."
    elif selected in note_required_actions and notes:
        status = f"{selected}_received"
        requires_confirmation = False
        reason = "User supplied gate notes; downstream agents must treat them as structured migration context."
    elif selected in note_required_actions:
        status = f"{selected}_notes_required"
        requires_confirmation = True
        reason = "User selected this option but did not provide notes yet."
    return {
        "schema_version": "3.1.0",
        "gate_id": gate_id,
        "app_name": app_name,
        "question": question,
        "options": options,
        "selected_action": selected,
        "status": status,
        "requires_human_confirmation": requires_confirmation,
        "reason": reason,
        "human_notes": notes or "",
        "next_pipeline_stage": next_stage,
        "pipeline_sequence_changed": False,
        "agent_instruction": "Read this gate artifact before planning, generating, repairing, testing, or approving. Use the human notes as scoped context while preserving the configured pipeline order.",
    }


def _patch_instruction_bundle(gate: dict[str, Any], patch: dict[str, Any], next_stage: str) -> dict[str, Any]:
    instructions = []
    if gate.get("human_notes"):
        instructions.append(
            {
                "type": gate["selected_action"],
                "priority": "high",
                "instruction": gate["human_notes"],
                "semantic_actions": patch.get("actions", []),
                "target_stage": next_stage,
            }
        )
    return {
        "schema_version": "3.1.0",
        "status": "ready_for_downstream_agents" if instructions else "no_human_patch_requested",
        "source_gate": gate["gate_id"],
        "source_gate_status": gate["status"],
        "instructions": instructions,
        "semantic_patch": patch,
        "next_pipeline_stage": next_stage,
        "pipeline_sequence_changed": False,
    }


def _apply_spec_patch(spec: dict[str, Any], notes: str, *, source: str) -> tuple[dict[str, Any], dict[str, Any]]:
    patch = _semantic_patch(notes, source=source)
    patched = deepcopy(spec)
    applied = []
    manual_review = []
    for action in patch.get("actions", []):
        result = _apply_spec_action(patched, action)
        if result["status"] == "manual_review_required":
            manual_review.append({**action, **result})
        else:
            applied.append({**action, **result})
    report = {
        **patch,
        "status": "not_requested" if not patch.get("actions") else "applied_with_review_items" if manual_review else "applied",
        "applied_actions": applied,
        "manual_review_items": manual_review,
    }
    patched["human_gate_semantic_patch"] = report
    return patched, report


def _apply_spec_action(spec: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    target = action.get("target", "functional_requirements")
    operation = action.get("operation", "add")
    text = action.get("text", "")
    if target == "pages_or_screens":
        item = {"name": _title_from_patch(text), "source": "human_gate", "instruction": text}
        return _apply_to_spec_lists(spec, ["screens", "ui_spec.screens"], item, operation, text)
    if target == "workflows":
        item = {"name": _title_from_patch(text), "source": "human_gate", "description": text}
        return _apply_to_spec_lists(spec, ["workflows", "workflow_spec.workflows"], item, operation, text)
    if target == "entities":
        item = {"name": _title_from_patch(text), "columns": [], "source": "human_gate", "instruction": text}
        return _apply_to_spec_lists(spec, ["entities", "domain_spec.entities"], item, operation, text)
    if target == "roles":
        return _apply_to_spec_lists(spec, ["roles", "security_spec.roles"], _title_from_patch(text), operation, text)
    if target == "acceptance_criteria":
        return _apply_to_spec_lists(spec, ["acceptance_criteria"], text, operation, text)
    return _apply_to_spec_lists(spec, ["domain_spec.requirements", "acceptance_criteria"], text, operation, text)


def _apply_to_spec_lists(spec: dict[str, Any], paths: list[str], item: Any, operation: str, text: str) -> dict[str, Any]:
    changed = 0
    for dotted in paths:
        parent, key = _ensure_parent(spec, dotted)
        current = parent.setdefault(key, [])
        if not isinstance(current, list):
            continue
        if operation == "remove":
            before = len(current)
            parent[key] = [existing for existing in current if not _matches(existing, text)]
            changed += before - len(parent[key])
        else:
            if not any(_items_equal(existing, item) for existing in current):
                current.append(deepcopy(item))
                changed += 1
    if changed:
        return {"status": "applied", "target": ",".join(paths), "detail": f"{operation} changed {changed} list item(s)."}
    return {"status": "manual_review_required", "target": ",".join(paths), "detail": "No matching item changed automatically."}


def _ensure_parent(data: dict[str, Any], dotted: str) -> tuple[dict[str, Any], str]:
    parts = dotted.split(".")
    parent = data
    for part in parts[:-1]:
        value = parent.setdefault(part, {})
        if not isinstance(value, dict):
            value = {}
            parent[part] = value
        parent = value
    return parent, parts[-1]


def _semantic_patch(notes: str, *, source: str) -> dict[str, Any]:
    if not notes.strip():
        return {"schema_version": "3.1.0", "source": source, "raw_notes": "", "action_count": 0, "actions": []}
    return parse_human_patch_notes(notes, source=source)


def _qa_blockers(qa_bundle: dict[str, Any]) -> list[str]:
    blockers = []
    for key in ("code_quality_report", "test_report", "security_review"):
        report = qa_bundle.get(key, {})
        if report and not report.get("gate_passed", False):
            blockers.append(f"{key}:{report.get('status', 'unknown')}")
    design = qa_bundle.get("design_quality_score", {})
    if design and not design.get("approved", False):
        blockers.append("design_quality_score:not_approved")
    visual = qa_bundle.get("visual_parity_score", {})
    if visual.get("status") == "failed":
        blockers.append("visual_parity_score:failed")
    return blockers


def _human_notes(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "3.1.0",
        "gate_id": gate["gate_id"],
        "status": gate["status"],
        "selected_action": gate["selected_action"],
        "requires_human_confirmation": gate["requires_human_confirmation"],
        "human_notes": gate.get("human_notes", ""),
        "next_pipeline_stage": gate.get("next_pipeline_stage"),
        "pipeline_sequence_changed": False,
    }


def _gate_summary(gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_id": gate["gate_id"],
        "status": gate["status"],
        "selected_action": gate["selected_action"],
        "requires_human_confirmation": gate["requires_human_confirmation"],
        "human_notes": gate.get("human_notes", ""),
        "pipeline_sequence_changed": False,
    }


def _normalize_decision(value: str | None, aliases: dict[str, str]) -> str | None:
    if not value:
        return None
    key = "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")
    while "__" in key:
        key = key.replace("__", "_")
    return aliases.get(key)


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _title_from_patch(text: str) -> str:
    cleaned = re.sub(
        r"\b(add|include|create|need|needs|remove|delete|exclude|drop|without|change|update|modify|rename|replace|the|a|an|page|screen|view|tab|workflow|flow|entity|table|role|requirement)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = " ".join(cleaned.split())
    return " ".join(word.capitalize() for word in cleaned.split())[:80] or text[:80]


def _matches(item: Any, text: str) -> bool:
    value = item.get("name", "") if isinstance(item, dict) else str(item)
    needle = _title_from_patch(text).lower()
    value_lower = value.lower()
    if needle and needle in value_lower:
        return True
    needle_tokens = {token for token in re.findall(r"[a-z0-9]+", needle) if len(token) > 2}
    value_tokens = {token for token in re.findall(r"[a-z0-9]+", value_lower) if len(token) > 2}
    return bool(needle_tokens) and len(needle_tokens & value_tokens) >= max(1, min(2, len(needle_tokens)))


def _items_equal(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return str(left.get("name", "")).lower() == str(right.get("name", "")).lower()
    return str(left).lower() == str(right).lower()


def _read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
