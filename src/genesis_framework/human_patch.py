from __future__ import annotations

import re
from copy import deepcopy
from typing import Any


def parse_human_patch_notes(notes: str, *, source: str) -> dict[str, Any]:
    clauses = _split_clauses(notes)
    actions = [_classify_clause(clause, source=source) for clause in clauses]
    return {
        "schema_version": "3.1.0",
        "source": source,
        "raw_notes": notes.strip(),
        "action_count": len(actions),
        "actions": actions,
    }


def apply_brd_semantic_patch(approved_plan: dict[str, Any], notes: str) -> tuple[dict[str, Any], dict[str, Any]]:
    patch = parse_human_patch_notes(notes, source="brd_gate") if notes.strip() else {
        "schema_version": "3.1.0",
        "source": "brd_gate",
        "raw_notes": "",
        "action_count": 0,
        "actions": [],
    }
    plan = deepcopy(approved_plan)
    applied: list[dict[str, Any]] = []
    needs_manual_review: list[dict[str, Any]] = []
    for action in patch["actions"]:
        target = action["target"]
        operation = action["operation"]
        text = action["text"]
        if target == "pages_or_screens":
            result = _apply_screen_action(plan, operation, text)
        elif target in {"functional_requirements", "workflows", "entities", "roles", "acceptance_criteria", "security_privacy_notes"}:
            result = _apply_list_action(plan, target, operation, text)
        else:
            result = _apply_list_action(plan, "functional_requirements", operation, text)
        if result["status"] == "manual_review_required":
            needs_manual_review.append({**action, **result})
        else:
            applied.append({**action, **result})

    report = {
        "schema_version": "3.1.0",
        "source": "brd_gate",
        "status": "not_requested" if not patch["actions"] else "applied_with_review_items" if needs_manual_review else "applied",
        "raw_notes": notes.strip(),
        "parsed_actions": patch["actions"],
        "applied_actions": applied,
        "manual_review_items": needs_manual_review,
        "patched_fields": sorted({item["target"] for item in applied if item.get("target")}),
    }
    plan["semantic_patch"] = report
    if notes.strip():
        plan["human_patch_summary"] = _summary_from_actions(patch["actions"])
    return plan, report


def build_generated_app_semantic_patch(notes: str, *, action: str) -> dict[str, Any]:
    patch = parse_human_patch_notes(notes, source="generated_app_gate") if notes.strip() else {
        "schema_version": "3.1.0",
        "source": "generated_app_gate",
        "raw_notes": "",
        "action_count": 0,
        "actions": [],
    }
    return {
        **patch,
        "gate_action": action,
        "target_stage": "run_agent_repair_loop",
        "agent_usage": "Repair/build agents should treat these semantic actions as scoped patch instructions while keeping the fixed pipeline order.",
    }


def _split_clauses(notes: str) -> list[str]:
    normalized = notes.replace("\r", "\n")
    parts = re.split(r"[\n.;]+|(?:\s+-\s+)", normalized)
    clauses: list[str] = []
    for part in parts:
        for subpart in re.split(r"\s+\band\b\s+", part, flags=re.IGNORECASE):
            cleaned = subpart.strip(" -:\t")
            if cleaned:
                clauses.append(cleaned)
    return clauses


def _classify_clause(clause: str, *, source: str) -> dict[str, Any]:
    lowered = clause.lower()
    operation = "add"
    if any(token in lowered for token in ("remove", "delete", "exclude", "drop", "without")):
        operation = "remove"
    elif any(token in lowered for token in ("rename", "replace", "change", "modify", "update")):
        operation = "update"
    elif any(token in lowered for token in ("keep only", "only keep")):
        operation = "constrain"
    target = _target_for_clause(lowered)
    return {
        "source": source,
        "operation": operation,
        "target": target,
        "text": clause,
        "confidence": _classification_confidence(lowered, target),
    }


def _target_for_clause(lowered: str) -> str:
    if any(token in lowered for token in ("page", "screen", "view", "tab", "dashboard", "queue")):
        return "pages_or_screens"
    if any(token in lowered for token in ("workflow", "flow", "journey", "process", "approval queue")):
        return "workflows"
    if any(token in lowered for token in ("entity", "table", "schema", "model", "database", "field")):
        return "entities"
    if any(token in lowered for token in ("role", "admin", "patient", "doctor", "manager", "user")):
        return "roles"
    if any(token in lowered for token in ("test", "acceptance", "criteria", "validate", "qa")):
        return "acceptance_criteria"
    if any(token in lowered for token in ("security", "privacy", "auth", "login", "permission", "password")):
        return "security_privacy_notes"
    return "functional_requirements"


def _classification_confidence(lowered: str, target: str) -> float:
    confidence = 0.62
    if target != "functional_requirements":
        confidence += 0.12
    if any(token in lowered for token in ("add", "remove", "delete", "change", "update", "keep")):
        confidence += 0.12
    return round(min(confidence, 0.92), 4)


def _apply_screen_action(plan: dict[str, Any], operation: str, text: str) -> dict[str, Any]:
    plan.setdefault("pages_or_screens", [])
    if operation == "remove":
        return _remove_from_list(plan, "pages_or_screens", text, item_text=lambda item: str(item.get("name", "")))
    name = _title_from_patch(text)
    entry = {"name": name, "source": "human_semantic_patch", "instruction": text}
    if operation == "update":
        plan["pages_or_screens"].append(entry)
        return {"status": "applied", "target": "pages_or_screens", "detail": f"Added update instruction for screen/page: {name}"}
    plan["pages_or_screens"].append(entry)
    return {"status": "applied", "target": "pages_or_screens", "detail": f"Added screen/page candidate: {name}"}


def _apply_list_action(plan: dict[str, Any], target: str, operation: str, text: str) -> dict[str, Any]:
    plan.setdefault(target, [])
    if operation == "remove":
        return _remove_from_list(plan, target, text)
    value = _requirement_from_patch(text)
    if value not in [str(item) for item in plan[target]]:
        plan[target].append(value)
    return {"status": "applied", "target": target, "detail": f"{operation.title()} instruction applied to {target}."}


def _remove_from_list(plan: dict[str, Any], target: str, text: str, item_text=None) -> dict[str, Any]:
    needle = _clean_patch_subject(text)
    original = plan.get(target, [])
    kept = []
    removed = []
    for item in original:
        value = item_text(item) if item_text else str(item)
        if _matches_subject(value, needle):
            removed.append(item)
        else:
            kept.append(item)
    plan[target] = kept
    if removed:
        return {"status": "applied", "target": target, "detail": f"Removed {len(removed)} item(s) from {target}.", "removed_items": removed}
    return {"status": "manual_review_required", "target": target, "detail": f"No existing {target} item matched removal request: {text}"}


def _clean_patch_subject(text: str) -> str:
    cleaned = re.sub(
        r"\b(add|include|create|need|needs|remove|delete|exclude|drop|without|change|update|modify|rename|replace|the|a|an|page|screen|view|tab|workflow|flow|entity|table|role|requirement)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    return " ".join(cleaned.split()).lower()


def _matches_subject(value: str, needle: str) -> bool:
    if not needle:
        return False
    value_lower = value.lower()
    if needle in value_lower:
        return True
    needle_tokens = {token for token in re.findall(r"[a-z0-9]+", needle) if len(token) > 2}
    value_tokens = {token for token in re.findall(r"[a-z0-9]+", value_lower) if len(token) > 2}
    return bool(needle_tokens) and len(needle_tokens & value_tokens) >= max(1, min(2, len(needle_tokens)))


def _title_from_patch(text: str) -> str:
    cleaned = _clean_patch_subject(text)
    return " ".join(word.capitalize() for word in cleaned.split())[:80] or text[:80]


def _requirement_from_patch(text: str) -> str:
    return text.strip().rstrip(".")


def _summary_from_actions(actions: list[dict[str, Any]]) -> list[str]:
    return [f"{action['operation']} {action['target']}: {action['text']}" for action in actions]
