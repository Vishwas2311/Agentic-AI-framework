from __future__ import annotations

from typing import Any


PRODUCTION_INTENT_SIGNALS = {
    "proper",
    "production",
    "pro",
    "code",
    "enterprise",
    "scalable",
    "deployable",
    "beyond",
    "expectation",
}
EXACT_STACK_SIGNALS = {"exact", "streamlit", "do", "not", "change", "keep", "demo", "prototype"}
UI_HEAVY_SIGNALS = {
    "ui",
    "ux",
    "portal",
    "dashboard",
    "website",
    "webapp",
    "login",
    "form",
    "consultation",
    "patient",
    "healthcare",
}
ENTERPRISE_SIGNALS = {"permissions", "roles", "integrations", "audit", "compliance", "migration"}
PROTOTYPE_STACKS = {"streamlit", "gradio", "notebook", "static_html_only"}


def _tokens(*values: str | None) -> set[str]:
    words: set[str] = set()
    for value in values:
        if not value:
            continue
        normalized = "".join(character.lower() if character.isalnum() else " " for character in value)
        words.update(part for part in normalized.split() if part)
    return words


def _contains_phrase(values: list[str], phrase: str) -> bool:
    phrase = phrase.lower()
    return any(phrase in value.lower() for value in values if value)


def infer_delivery_mode(
    user_prompt: str,
    brd_stack: str | None = None,
    domain: str | None = None,
    scope: str | None = None,
) -> str:
    values = [user_prompt or "", brd_stack or "", domain or "", scope or ""]
    words = _tokens(*values)
    if words & ENTERPRISE_SIGNALS:
        return "enterprise_migration"
    if _contains_phrase(values, "production pro-code") or _contains_phrase(values, "proper software") or words & PRODUCTION_INTENT_SIGNALS:
        return "production_procode"
    if _contains_phrase(values, "client demo") or _contains_phrase(values, "polished demo"):
        return "client_demo_polished"
    return "prototype_demo"


def infer_target_stack(
    delivery_mode: str,
    user_prompt: str,
    brd_stack: str | None = None,
    domain: str | None = None,
    scope: str | None = None,
) -> str:
    values = [user_prompt or "", brd_stack or "", domain or "", scope or ""]
    words = _tokens(*values)
    ui_heavy = bool(words & UI_HEAVY_SIGNALS)

    if delivery_mode == "prototype_demo":
        if brd_stack and brd_stack.lower() in PROTOTYPE_STACKS:
            return brd_stack.lower()
        return "streamlit"

    if delivery_mode == "client_demo_polished":
        if ui_heavy:
            return "nextjs_tailwind_shadcn_motion"
        return "react_tailwind_shadcn"

    if delivery_mode == "enterprise_migration":
        if ui_heavy:
            return "nextjs_tailwind_shadcn_motion_plus_api"
        return "spring_boot_react_postgres"

    if ui_heavy:
        return "nextjs_tailwind_shadcn_motion"
    return "react_tailwind_shadcn_plus_backend"


def resolve_stack_decision(
    user_prompt: str,
    brd_stack: str | None = None,
    domain: str | None = None,
    scope: str | None = None,
) -> dict[str, Any]:
    delivery_mode = infer_delivery_mode(user_prompt, brd_stack, domain, scope)
    selected_stack = infer_target_stack(delivery_mode, user_prompt, brd_stack, domain, scope)
    prototype_stack_selected = selected_stack in PROTOTYPE_STACKS
    conflict_detected = bool(brd_stack and brd_stack.lower() in PROTOTYPE_STACKS and delivery_mode in {"production_procode", "enterprise_migration"})
    ui_heavy_surface = bool(_tokens(user_prompt, domain, scope) & UI_HEAVY_SIGNALS)
    human_approval_required = False
    if prototype_stack_selected and delivery_mode in {"production_procode", "enterprise_migration"}:
        human_approval_required = True
    if _contains_phrase([user_prompt], "exact streamlit") or _contains_phrase([user_prompt], "keep streamlit"):
        human_approval_required = True

    quality_gates = [
        "stack_decision_report",
        "design_decision_report",
        "design_quality_score",
        "visual_rejection_report",
        "before_after_improvement_report",
    ]
    if ui_heavy_surface:
        quality_gates.extend(["layout_profile_selection", "viewport_fit_plan", "playwright_visual_qa"])

    reason_parts = [f"Delivery mode resolved to {delivery_mode}."]
    if conflict_detected:
        reason_parts.append("BRD requested a prototype stack, so the framework upgraded the implementation stack to satisfy production intent.")
    if ui_heavy_surface:
        reason_parts.append("UI-heavy surface detected, so the premium web profile was preferred.")
    if human_approval_required:
        reason_parts.append("Human approval is required because the selected or requested stack conflicts with production policy.")

    return {
        "schema_version": "3.1.0",
        "detected_brd_stack": brd_stack,
        "user_delivery_intent": user_prompt,
        "selected_delivery_mode": delivery_mode,
        "selected_target_stack": selected_stack,
        "selected_frontend_profile": selected_stack if "tailwind" in selected_stack else None,
        "selected_ui_automation_profile": "ui_ux_pro_max_magic_motion" if ui_heavy_surface else "standard_generation",
        "prototype_stack_allowed": delivery_mode == "prototype_demo",
        "conflict_detected": conflict_detected,
        "decision_reason": " ".join(reason_parts),
        "human_approval_required": human_approval_required,
        "quality_gates_required": quality_gates,
        "ui_heavy_surface_detected": ui_heavy_surface,
    }
