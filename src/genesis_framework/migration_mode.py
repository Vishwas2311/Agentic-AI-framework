from __future__ import annotations

from typing import Any


MIGRATION_MODE_OPTIONS: dict[str, dict[str, Any]] = {
    "production_e2e_app": {
        "label": "Production E2E App",
        "short_code": "A",
        "description": "Production web architecture for full enterprise handoff.",
        "technology": "Next.js + Tailwind + FastAPI + PostgreSQL-ready database",
        "runtime_goal": "production_handoff",
        "quality_depth": "pipeline_default",
        "localhost_required": False,
        "production_upgrade_required": False,
        "primary_outputs": [
            "frontend/",
            "backend/",
            "database/",
            "tests/",
            "deploy/",
            "docs/",
            "production_readiness_scorecard.json",
        ],
    },
    "local_demo_app": {
        "label": "Local Demo App",
        "short_code": "B",
        "description": "Fast localhost web app for client demo and workflow validation.",
        "technology": "Next.js + Tailwind + FastAPI + SQLite/mock data",
        "runtime_goal": "localhost_demo",
        "quality_depth": "pipeline_default",
        "localhost_required": True,
        "production_upgrade_required": True,
        "primary_outputs": [
            "run_demo.ps1",
            "demo_credentials.json",
            "localhost_url.json",
            "demo_report.md",
            "production_gap_report.md",
        ],
    },
    "hybrid_pilot_app": {
        "label": "Hybrid Pilot App",
        "short_code": "C",
        "description": "Polished localhost pilot with production-shaped architecture.",
        "technology": "Next.js + Tailwind + FastAPI + SQLite now, PostgreSQL-ready later",
        "runtime_goal": "localhost_pilot_with_production_architecture",
        "quality_depth": "pipeline_default",
        "localhost_required": True,
        "production_upgrade_required": True,
        "primary_outputs": [
            "frontend/",
            "backend/",
            "database/",
            "tests/",
            "run_demo.ps1",
            "demo_report.md",
            "production_gap_report.md",
            "genesis_replay_dashboard.html",
        ],
    },
}


_MODE_ALIASES = {
    "a": "production_e2e_app",
    "prod": "production_e2e_app",
    "production": "production_e2e_app",
    "production_procode": "production_e2e_app",
    "production_e2e": "production_e2e_app",
    "production_e2e_app": "production_e2e_app",
    "enterprise": "production_e2e_app",
    "enterprise_migration": "production_e2e_app",
    "full": "production_e2e_app",
    "full_local": "production_e2e_app",
    "full_production": "production_e2e_app",
    "b": "local_demo_app",
    "demo": "local_demo_app",
    "local_demo": "local_demo_app",
    "local_demo_app": "local_demo_app",
    "localhost": "local_demo_app",
    "prototype": "local_demo_app",
    "prototype_demo": "local_demo_app",
    "quick_demo": "local_demo_app",
    "streamlit": "local_demo_app",
    "c": "hybrid_pilot_app",
    "hybrid": "hybrid_pilot_app",
    "hybrid_pilot": "hybrid_pilot_app",
    "hybrid_pilot_app": "hybrid_pilot_app",
    "pilot": "hybrid_pilot_app",
    "client_demo": "hybrid_pilot_app",
    "client_demo_polished": "hybrid_pilot_app",
    "polished_demo": "hybrid_pilot_app",
}


def normalize_migration_mode(value: str | None) -> str | None:
    if not value:
        return None
    key = "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")
    while "__" in key:
        key = key.replace("__", "_")
    return _MODE_ALIASES.get(key)


def resolve_migration_mode(
    request: dict[str, Any],
    stack_decision: dict[str, Any],
    *,
    app_name: str,
    primary_source_type: str | None = None,
) -> dict[str, Any]:
    explicit_raw = _first_text(
        request.get("migration_output_mode"),
        request.get("migration_mode"),
        request.get("output_mode"),
        request.get("project_mode"),
    )
    explicit_mode = normalize_migration_mode(explicit_raw)
    delivery_mode = str(stack_decision.get("selected_delivery_mode") or request.get("delivery_mode") or "")
    stack_mode = normalize_migration_mode(delivery_mode)

    selection_source = "recommended_default"
    selected_mode = "hybrid_pilot_app"
    requires_confirmation = True
    reason = "No explicit migration output mode was provided. Hybrid Pilot is the safest default because it gives a runnable localhost app while keeping production-shaped architecture."

    if explicit_mode:
        selected_mode = explicit_mode
        selection_source = "explicit_request"
        requires_confirmation = False
        reason = f"User explicitly selected {MIGRATION_MODE_OPTIONS[selected_mode]['label']}."
    elif stack_mode:
        selected_mode = stack_mode
        selection_source = "delivery_mode_mapping"
        requires_confirmation = False
        reason = f"Mapped delivery mode '{delivery_mode}' to {MIGRATION_MODE_OPTIONS[selected_mode]['label']}."
    elif stack_decision.get("human_approval_required"):
        selected_mode = "hybrid_pilot_app"
        selection_source = "policy_safe_default"
        requires_confirmation = True
        reason = "A stack or policy conflict needs human review. Hybrid Pilot keeps a demo path open while preserving production upgrade structure."

    profile = MIGRATION_MODE_OPTIONS[selected_mode]
    options = [
        {
            "code": option["short_code"],
            "mode": mode,
            "label": option["label"],
            "description": option["description"],
            "technology": option["technology"],
            "runtime_goal": option["runtime_goal"],
            "quality_depth": option["quality_depth"],
        }
        for mode, option in MIGRATION_MODE_OPTIONS.items()
    ]
    return {
        "schema_version": "3.1.0",
        "app_name": app_name,
        "primary_source_type": primary_source_type,
        "selected_mode": selected_mode,
        "selected_label": profile["label"],
        "selection_source": selection_source,
        "requires_human_confirmation": requires_confirmation,
        "recommended_default": "hybrid_pilot_app",
        "question": "Choose migration output mode: A. Production E2E App, B. Local Demo App, C. Hybrid Pilot App.",
        "options": options,
        "runtime_goal": profile["runtime_goal"],
        "technology": profile["technology"],
        "quality_depth": profile["quality_depth"],
        "localhost_required": profile["localhost_required"],
        "production_upgrade_required": profile["production_upgrade_required"],
        "primary_outputs": profile["primary_outputs"],
        "reason": reason,
        "downstream_instructions": _downstream_instructions(selected_mode),
    }


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _downstream_instructions(selected_mode: str) -> list[str]:
    if selected_mode == "production_e2e_app":
        return [
            "Use the Production E2E technology profile for generated frontend, backend, and database structure.",
            "Keep the standard Genesis pipeline unchanged after this technology choice.",
        ]
    if selected_mode == "local_demo_app":
        return [
            "Use the Local Demo technology profile for a fast localhost app with lightweight data.",
            "Keep the standard Genesis pipeline unchanged after this technology choice.",
        ]
    return [
        "Use the Hybrid Pilot technology profile for company demos with production-shaped structure.",
        "Keep the standard Genesis pipeline unchanged after this technology choice.",
    ]
