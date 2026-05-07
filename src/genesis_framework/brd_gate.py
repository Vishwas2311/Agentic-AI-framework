from __future__ import annotations

from typing import Any

from genesis_framework.human_patch import apply_brd_semantic_patch


BRD_GATE_OPTIONS: list[dict[str, str]] = [
    {
        "code": "A",
        "action": "approved",
        "label": "Approve BRD understanding",
        "description": "Use the extracted BRD plan as the source of truth for downstream planning.",
    },
    {
        "code": "B",
        "action": "approved_with_assumptions",
        "label": "Approve with assumptions",
        "description": "Continue with the extracted BRD plan and keep unclear items visible for review.",
    },
    {
        "code": "C",
        "action": "needs_more_evidence",
        "label": "Add missing requirements or evidence",
        "description": "Pause for more files, screenshots, examples, credentials, or business clarification.",
    },
    {
        "code": "D",
        "action": "edit_requested",
        "label": "Edit BRD before generation",
        "description": "Ask the user what to change, then apply those BRD changes before generation.",
    },
]


_DECISION_ALIASES = {
    "a": "approved",
    "approve": "approved",
    "approved": "approved",
    "yes": "approved",
    "proceed": "approved",
    "b": "approved_with_assumptions",
    "approve_with_assumptions": "approved_with_assumptions",
    "approved_with_assumptions": "approved_with_assumptions",
    "assumptions": "approved_with_assumptions",
    "c": "needs_more_evidence",
    "needs_more_evidence": "needs_more_evidence",
    "more_evidence": "needs_more_evidence",
    "add_missing": "needs_more_evidence",
    "add_missing_requirements": "needs_more_evidence",
    "stop": "needs_more_evidence",
    "pause": "needs_more_evidence",
    "d": "edit_requested",
    "edit": "edit_requested",
    "edit_brd": "edit_requested",
    "edit_requested": "edit_requested",
    "change": "edit_requested",
    "changes": "edit_requested",
}


def normalize_brd_gate_decision(value: str | None) -> str | None:
    if not value:
        return None
    key = "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")
    while "__" in key:
        key = key.replace("__", "_")
    return _DECISION_ALIASES.get(key)


def build_brd_understanding(
    request: dict[str, Any],
    brd_design_intent: dict[str, Any],
    brd_mockup_inventory: dict[str, Any],
    artifacts: list[dict[str, Any]],
    *,
    app_name: str,
) -> dict[str, Any]:
    requirements = _clean_list(brd_design_intent.get("functional_requirements"))
    acceptance = _clean_list(brd_design_intent.get("acceptance_criteria"))
    screens = _clean_list(brd_design_intent.get("screen_candidates"))
    workflows = _clean_list(brd_design_intent.get("workflow_candidates"))
    roles = _dedupe(
        _clean_list(request.get("roles"))
        + _clean_list(request.get("target_users"))
        + _clean_list(brd_design_intent.get("target_users"))
        + _clean_list(brd_design_intent.get("roles"))
        + _clean_list(brd_design_intent.get("document_roles"))
    )
    entities = _clean_list(brd_design_intent.get("document_entities"))
    summary = _clean_list(brd_design_intent.get("summary_sentences"))
    if not summary:
        summary = _clean_list(brd_design_intent.get("evidence_snippets"))[:8]
    if not summary and brd_design_intent.get("prompt_summary"):
        summary = [str(brd_design_intent["prompt_summary"])]

    document_sources = [artifact for artifact in artifacts if artifact.get("kind") == "document"]
    embedded_media_docs = [
        {
            "path": artifact.get("relative_path"),
            "entry_count": artifact.get("metadata", {}).get("entry_count", 0),
            "contains_images": bool(artifact.get("metadata", {}).get("contains_images")),
        }
        for artifact in document_sources
        if artifact.get("metadata", {}).get("contains_images")
    ]
    security_privacy = _security_privacy_notes(requirements + acceptance + summary)
    missing_questions = _missing_questions(
        requirements=requirements,
        screens=screens,
        workflows=workflows,
        roles=roles,
        entities=entities,
        mockup_inventory=brd_mockup_inventory,
    )
    confidence = _confidence(brd_design_intent, requirements, screens, workflows, acceptance)
    return {
        "schema_version": "3.1.0",
        "app_name": app_name,
        "application_intent": {
            "domain": brd_design_intent.get("domain") or request.get("domain") or "unknown",
            "goal": brd_design_intent.get("goal") or request.get("goal") or "Generate production software from provided evidence.",
            "delivery_mode_hint": brd_design_intent.get("delivery_mode") or request.get("delivery_mode"),
        },
        "summary": summary[:12],
        "roles": roles[:30],
        "pages_or_screens": [{"name": _title_from_text(screen), "source": "brd"} for screen in screens[:30]],
        "functional_requirements": requirements[:80],
        "workflows": workflows[:60],
        "entities": entities[:60],
        "acceptance_criteria": acceptance[:80],
        "security_privacy_notes": security_privacy,
        "mockup_evidence": {
            "separate_images": brd_mockup_inventory.get("images", []),
            "runtime_videos": brd_mockup_inventory.get("videos", []),
            "documents": brd_mockup_inventory.get("documents", []),
            "embedded_media_documents": embedded_media_docs,
            "mockup_count": int(brd_mockup_inventory.get("mockup_count", 0) or 0),
            "runtime_video_count": int(brd_mockup_inventory.get("runtime_video_count", 0) or 0),
            "visual_analysis_count": len(brd_mockup_inventory.get("visual_analyses", []) or []),
        },
        "source_documents": [
            {
                "path": artifact.get("relative_path"),
                "summary": artifact.get("summary"),
                "confidence": artifact.get("confidence"),
            }
            for artifact in document_sources
        ],
        "missing_questions": missing_questions,
        "confidence": confidence,
    }


def resolve_brd_understanding_gate(
    request: dict[str, Any],
    brd_understanding: dict[str, Any],
    *,
    app_name: str,
) -> dict[str, Any]:
    explicit_raw = _first_text(
        request.get("brd_understanding_decision"),
        request.get("brd_gate_decision"),
        request.get("brd_review_decision"),
        request.get("brd_understanding_status"),
    )
    explicit_action = normalize_brd_gate_decision(explicit_raw)
    edit_notes = _first_text(
        request.get("brd_edit_notes"),
        request.get("brd_changes"),
        request.get("requirement_changes"),
        request.get("change_request"),
    )

    action = explicit_action or "review_required"
    status = "pending_review"
    requires_confirmation = True
    reason = "Genesis extracted the BRD understanding and needs the user to approve, edit, or add missing evidence before final approval."
    if action == "approved":
        status = "approved"
        requires_confirmation = False
        reason = "The BRD understanding was explicitly approved."
    elif action == "approved_with_assumptions":
        status = "approved_with_assumptions"
        requires_confirmation = False
        reason = "The BRD understanding was approved while keeping assumptions visible downstream."
    elif action == "edit_requested" and edit_notes:
        status = "edited_by_request"
        requires_confirmation = False
        reason = "The user supplied BRD edit notes in the migration request; Genesis will carry them into the approved BRD plan."
    elif action == "edit_requested":
        reason = "The user selected BRD editing. Genesis should ask what changes are needed before treating the BRD as approved."
    elif action == "needs_more_evidence":
        reason = "The user requested more evidence or missing requirements before approving the BRD."

    approved_plan = dict(brd_understanding)
    approved_plan["approval_state"] = status
    approved_plan["user_edit_notes"] = edit_notes or ""
    approved_plan["source_of_truth"] = "approved_brd_plan.json"
    if edit_notes:
        approved_plan.setdefault("manual_overrides", []).append(
            {
                "type": "brd_edit_notes",
                "text": edit_notes,
                "effect": "Downstream planning must treat these notes as higher priority than inferred BRD details.",
            }
        )
    approved_plan, semantic_patch = apply_brd_semantic_patch(approved_plan, edit_notes or "")

    return {
        "schema_version": "3.1.0",
        "app_name": app_name,
        "question": "BRD Understanding Gate: is this extracted BRD correct, or do you want to edit it before generation?",
        "options": BRD_GATE_OPTIONS,
        "selected_action": action,
        "status": status,
        "requires_human_confirmation": requires_confirmation,
        "reason": reason,
        "edit_notes": edit_notes or "",
        "how_to_edit": "Set brd_gate_decision: D and brd_edit_notes: '<your changes>' in migration_request.yaml, or tell Claude Code what to change when it shows this gate.",
        "semantic_patch": semantic_patch,
        "approved_brd_plan": approved_plan,
    }


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def _title_from_text(value: str) -> str:
    cleaned = value.strip().strip("-*#0123456789. ")
    if len(cleaned) <= 72:
        return cleaned
    return cleaned[:69].rstrip() + "..."


def _security_privacy_notes(lines: list[str]) -> list[str]:
    notes = []
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in ("password", "privacy", "security", "sensitive", "patient", "medical", "auth", "login")):
            notes.append(line)
    return _dedupe(notes)[:25]


def _missing_questions(
    *,
    requirements: list[str],
    screens: list[str],
    workflows: list[str],
    roles: list[str],
    entities: list[str],
    mockup_inventory: dict[str, Any],
) -> list[str]:
    questions = []
    if not requirements:
        questions.append("No clear functional requirements were extracted.")
    if not screens:
        questions.append("No page or screen list was confidently extracted.")
    if not workflows:
        questions.append("No workflow sequence was confidently extracted.")
    if not roles:
        questions.append("No user roles were confidently extracted.")
    if not entities:
        questions.append("No domain entities or data objects were confidently extracted.")
    if not mockup_inventory.get("images") and not mockup_inventory.get("visual_analyses"):
        questions.append("No separate screenshot/mockup image evidence was available.")
    return questions


def _confidence(
    brd_design_intent: dict[str, Any],
    requirements: list[str],
    screens: list[str],
    workflows: list[str],
    acceptance: list[str],
) -> float:
    confidence = float(brd_design_intent.get("document_confidence") or 0.45)
    if requirements:
        confidence += 0.04
    if screens:
        confidence += 0.03
    if workflows:
        confidence += 0.03
    if acceptance:
        confidence += 0.03
    return round(min(confidence, 0.95), 4)
