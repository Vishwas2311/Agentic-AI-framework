from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SALES_SIGNALS = {"shop", "product", "ecommerce", "checkout", "pricing", "buy", "cart", "order", "sales"}
LEAD_SIGNALS = {"lead", "inquiry", "appointment", "booking", "contact", "demo", "quote", "consultation"}
QUIZ_SIGNALS = {"quiz", "assessment", "configurator", "recommendation", "survey", "onboarding"}
SUBSCRIPTION_SIGNALS = {"subscription", "membership", "recurring", "plan", "saas"}
ENTERPRISE_SIGNALS = {"dashboard", "admin", "workflow", "portal", "internal", "enterprise", "migration", "records"}
COMPONENT_SIGNALS = {
    "button",
    "card",
    "form",
    "table",
    "navbar",
    "sidebar",
    "modal",
    "component",
    "widget",
    "login",
    "metric",
}

DOMAIN_STYLE_PACKS: dict[str, dict[str, Any]] = {
    "healthcare": {"density": "calm_compact", "motion": "subtle", "components": ["patient_summary", "appointment_card", "forms", "alerts", "tables"]},
    "fintech": {"density": "compact_precise", "motion": "subtle", "components": ["metric_cards", "transaction_tables", "filters", "risk_badges"]},
    "saas_admin": {"density": "compact_task_focused", "motion": "subtle", "components": ["sidebar", "topbar", "metric_cards", "data_table", "filters"]},
    "ecommerce": {"density": "balanced_conversion", "motion": "standard", "components": ["product_grid", "product_card", "cart", "checkout", "reviews"]},
    "education": {"density": "balanced_guided", "motion": "standard", "components": ["course_card", "progress", "lesson_nav", "quiz"]},
    "fitness": {"density": "expressive_mobile_first", "motion": "expressive", "components": ["program_card", "progress_ring", "plan_steps", "habit_streak"]},
    "real_estate": {"density": "visual_browsing", "motion": "standard", "components": ["listing_card", "search_filters", "map_panel", "image_gallery"]},
    "crm": {"density": "compact_workflow", "motion": "subtle", "components": ["pipeline_board", "contact_card", "activity_timeline", "filters"]},
    "hrms": {"density": "compact_people_ops", "motion": "subtle", "components": ["employee_table", "profile_panel", "approval_flow", "calendar"]},
    "portfolio": {"density": "expressive_showcase", "motion": "expressive", "components": ["hero", "project_grid", "case_study", "testimonial"]},
    "marketplace": {"density": "balanced_discovery", "motion": "standard", "components": ["search", "filters", "listing_card", "compare", "reviews"]},
}

COMPONENT_PATTERNS: dict[str, dict[str, str]] = {
    "dashboard": {"pattern": "sidebar_topbar_metric_cards_filters_data_table_detail_panel", "reason": "Best fit for admin, portal, analytics, and record workflows."},
    "lead_generation": {"pattern": "hero_proof_benefits_form_faq_sticky_cta", "reason": "Best fit for inquiries, appointments, demos, and quote capture."},
    "drive_sales": {"pattern": "product_grid_pricing_cart_reviews_checkout", "reason": "Best fit for product discovery and purchase conversion."},
    "interactive_quiz": {"pattern": "stepper_progress_question_card_results_recommendation", "reason": "Best fit for guided assessment and recommendation flows."},
    "subscriptions": {"pattern": "pricing_table_plan_compare_feature_matrix_signup_billing_faq", "reason": "Best fit for plan selection and recurring signup."},
    "mobile": {"pattern": "safe_area_header_content_cards_bottom_nav_large_touch_targets", "reason": "Best fit for mobile screenshots and native-feel app surfaces."},
}

LAYOUT_PROFILES: dict[str, dict[str, str]] = {
    "auth_split_screen": {
        "desktop_strategy": "split_screen_balanced",
        "reason": "Best fit for login and access-gate screens that need a focused form plus a contextual visual anchor.",
    },
    "portal_dashboard": {
        "desktop_strategy": "task_first_wide",
        "reason": "Best fit for dashboards and portal home screens that should use horizontal space efficiently on desktop.",
    },
    "operational_form": {
        "desktop_strategy": "form_plus_context",
        "reason": "Best fit for booking, intake, settings, and workflow forms that benefit from wider or multi-column layouts.",
    },
    "data_table_workspace": {
        "desktop_strategy": "dense_workspace",
        "reason": "Best fit for records, queues, and data-heavy screens that need broad scanable task surfaces.",
    },
    "landing_or_marketing": {
        "desktop_strategy": "editorial_capped",
        "reason": "Best fit for narrative or conversion pages where capped containers improve readability and rhythm.",
    },
}


def _tokens(*values: str | None) -> set[str]:
    words: set[str] = set()
    for value in values:
        if not value:
            continue
        normalized = "".join(character.lower() if character.isalnum() else " " for character in value)
        words.update(part for part in normalized.split() if part)
    return words


def infer_magic_project_type(source_type: str, scope: str | None = None) -> str:
    words = _tokens(scope, source_type)
    if "component" in words or source_type == "component" or words & COMPONENT_SIGNALS:
        return "component"
    return "website"


def infer_creation_type(reference_url: str | None, source_type: str) -> str:
    if reference_url or source_type == "website":
        return "get_inspired"
    return "from_scratch"


def infer_source_material(source_type: str, reference_url: str | None) -> dict[str, str | None]:
    if reference_url or source_type == "website_url" or source_type == "website":
        return {"kind": "url", "usage": "primary_website_evidence_or_style_reference", "reference_url": reference_url}
    if source_type in {"screenshot", "screenshot_existing_ui", "mobile_app_screenshot", "figma_export_image"}:
        return {"kind": "uploaded_image", "usage": "primary_visual_evidence", "reference_url": None}
    if source_type in {"wireframe", "sketch", "wireframe_or_sketch"}:
        return {"kind": "uploaded_image", "usage": "layout_intent", "reference_url": None}
    if source_type in {"inspiration_image", "design_inspiration_image"}:
        return {"kind": "uploaded_image", "usage": "style_dna_reference", "reference_url": None}
    if source_type in {"brand", "logo", "brand_logo_image"}:
        return {"kind": "logo", "usage": "brand_system_seed", "reference_url": None}
    if source_type in {"existing_code", "outdated_existing_ui"}:
        return {"kind": "existing_code_or_uploaded_image", "usage": "ux_audit_baseline", "reference_url": None}
    if source_type in {"lowcode", "powerapps", "mendix", "appian", "outsystems"}:
        return {"kind": "lowcode_export", "usage": "application_source_truth", "reference_url": None}
    return {"kind": "text_brief", "usage": "product_brief", "reference_url": None}


def infer_rebuild_mode(source_type: str, reference_url: str | None, fidelity_mode: str) -> str:
    if fidelity_mode == "exact_fidelity":
        return "exact_rebuild"
    if source_type in {"inspiration_image", "design_inspiration_image"}:
        return "inspired_redesign"
    if source_type in {"outdated_existing_ui", "existing_code"}:
        return "improve_and_modernize"
    if source_type in {"wireframe", "sketch", "wireframe_or_sketch"}:
        return "polished_interpretation"
    if source_type in {"brand", "logo", "brand_logo_image"}:
        return "brand_matched_design_system"
    if reference_url or source_type in {"website", "website_url"}:
        return "modernized_rebuild"
    return "from_brief_best_practice" if source_type == "text" else "modernized_rebuild"


def infer_tool_sequence(source_material: dict[str, str | None]) -> list[str]:
    kind = source_material["kind"]
    usage = source_material["usage"]
    if kind == "url":
        return ["firecrawl", "playwright", "ui_ux_pro_max", "magic_21st", "motion_after_rebuild", "playwright_qa"]
    if kind == "uploaded_image":
        return ["vision_model", "ui_ux_pro_max", "magic_21st", "motion_after_rebuild", "playwright_qa"]
    if kind == "logo":
        return ["vision_model", "ui_ux_pro_max", "magic_21st", "motion_after_rebuild", "playwright_qa"]
    if usage == "ux_audit_baseline":
        return ["ui_ux_pro_max_audit", "magic_21st", "motion_after_rebuild", "playwright_qa"]
    if kind == "lowcode_export":
        return ["platform_adapter", "ui_ux_pro_max", "magic_21st", "motion_after_rebuild", "playwright_qa"]
    return ["ui_ux_pro_max", "magic_21st", "motion_after_rebuild", "playwright_qa"]


def infer_website_goal(goal: str | None, domain: str | None, description: str | None = None) -> str:
    words = _tokens(goal, domain, description)
    if words & SALES_SIGNALS:
        return "drive_sales"
    if words & QUIZ_SIGNALS:
        return "interactive_quiz"
    if words & SUBSCRIPTION_SIGNALS:
        return "subscriptions"
    if words & LEAD_SIGNALS:
        return "lead_generation"
    if words & ENTERPRISE_SIGNALS:
        return "custom"
    return "custom"


def infer_motion_intensity(goal: str, domain: str | None, fidelity_mode: str) -> str:
    words = _tokens(goal, domain)
    if fidelity_mode == "exact_fidelity":
        return "none"
    if words & {"healthcare", "fintech", "banking", "admin", "dashboard", "enterprise", "internal", "portal"}:
        return "subtle"
    if goal in {"lead_generation", "drive_sales"}:
        return "standard"
    if words & {"portfolio", "campaign", "fitness", "entertainment", "marketing"}:
        return "expressive"
    return "standard"


def infer_domain_style_pack(domain: str | None, source_type: str | None = None) -> dict[str, Any]:
    words = _tokens(domain, source_type)
    if words & {"healthcare", "clinic", "patient", "medical", "hospital"}:
        name = "healthcare"
    elif words & {"fintech", "banking", "finance", "payment", "loan"}:
        name = "fintech"
    elif words & {"ecommerce", "shop", "store", "product", "checkout"}:
        name = "ecommerce"
    elif words & {"education", "course", "learning", "lesson"}:
        name = "education"
    elif words & {"fitness", "gym", "workout", "wellness"}:
        name = "fitness"
    elif words & {"real", "estate", "property", "listing"}:
        name = "real_estate"
    elif words & {"crm", "pipeline", "salesforce", "lead"}:
        name = "crm"
    elif words & {"hrms", "hr", "employee", "payroll"}:
        name = "hrms"
    elif words & {"portfolio", "creator", "case", "study"}:
        name = "portfolio"
    elif words & {"marketplace", "listing", "vendor"}:
        name = "marketplace"
    else:
        name = "saas_admin"
    return {"name": name, **DOMAIN_STYLE_PACKS[name]}


def infer_component_pattern(website_goal: str, source_type: str, scope: str | None = None) -> dict[str, str]:
    words = _tokens(source_type, scope, website_goal)
    if words & {"mobile", "ios", "android", "react", "native", "flutter"}:
        key = "mobile"
    elif website_goal in COMPONENT_PATTERNS:
        key = website_goal
    elif words & {"dashboard", "admin", "portal", "records", "analytics"}:
        key = "dashboard"
    else:
        key = "dashboard" if website_goal == "custom" else website_goal
    return {"name": key, **COMPONENT_PATTERNS[key]}


def infer_layout_profile(
    source_type: str,
    website_goal: str,
    scope: str | None = None,
    domain: str | None = None,
) -> dict[str, str]:
    words = _tokens(source_type, website_goal, scope, domain)
    if words & {"login", "signin", "auth", "authentication", "onboarding"}:
        key = "auth_split_screen"
    elif words & {"table", "grid", "list", "queue", "records", "audit", "inbox"}:
        key = "data_table_workspace"
    elif words & {"form", "booking", "book", "intake", "settings", "profile", "workflow"}:
        key = "operational_form"
    elif website_goal == "custom" or words & {"dashboard", "portal", "admin", "patient", "workspace", "overview"}:
        key = "portal_dashboard"
    else:
        key = "landing_or_marketing"
    return {"name": key, **LAYOUT_PROFILES[key]}


def build_viewport_fit_plan(layout_profile: dict[str, str], domain_style_pack: dict[str, Any]) -> dict[str, Any]:
    profile_name = layout_profile["name"]
    if profile_name == "auth_split_screen":
        return {
            "desktop_space_strategy": "Keep the form focused, but balance it with a strong hero or support panel so the screen does not feel empty on wide desktops.",
            "whitespace_strategy": "Use whitespace to frame the form, not to miniaturize it; keep the form visually anchored within the composition.",
            "container_strategy": "Allow a form width around 480-640px and pair it with a meaningful companion panel on large screens.",
            "rejection_triggers": [
                "miniaturized_form_on_desktop",
                "unbalanced_empty_whitespace",
                "weak_visual_anchor_for_auth_screen",
            ],
        }
    if profile_name == "portal_dashboard":
        return {
            "desktop_space_strategy": "Use broad task-first sections for hero, metrics, quick actions, filters, and record previews so the page feels like a real product surface.",
            "whitespace_strategy": "Whitespace should separate sections and aid scanability, not dominate the viewport.",
            "container_strategy": "Prefer wide adaptive containers and dense grids over narrow marketing-style centered columns.",
            "rejection_triggers": [
                "dashboard_composition_feels_zoomed_out",
                "narrow_operational_layout",
                "undersized_hero_for_viewport",
            ],
        }
    if profile_name == "operational_form":
        return {
            "desktop_space_strategy": "Use desktop width to enable clearer two-column form groupings or contextual side panels when space allows.",
            "whitespace_strategy": "Reduce empty lateral margins by adding structured context, summaries, or multi-column sections.",
            "container_strategy": "Prefer medium-to-wide form containers sized for task completion, not centered card miniatures.",
            "rejection_triggers": [
                "single_column_form_wastes_desktop_space",
                "form_context_missing_on_wide_screen",
            ],
        }
    if profile_name == "data_table_workspace":
        return {
            "desktop_space_strategy": "Expand tables, filters, and detail surfaces with viewport width so the interface reads as a desktop workspace.",
            "whitespace_strategy": "Favor visible data and controls over decorative empty margins.",
            "container_strategy": "Use wide or near-full-width containers with clear panels for navigation, filters, and record detail.",
            "rejection_triggers": [
                "data_surface_too_narrow_for_desktop",
                "mobile_card_stack_pasted_into_desktop_shell",
            ],
        }
    return {
        "desktop_space_strategy": "Use section-based container widths that support readability while still making the page feel intentionally composed on large screens.",
        "whitespace_strategy": "Whitespace should create rhythm and emphasis, not accidental undersizing.",
        "container_strategy": f"Use {domain_style_pack['density']} density with capped editorial sections only where they improve the intended experience.",
        "rejection_triggers": [
            "hero_or_primary_section_feels_undersized",
            "composition_reads_like_accidental_zoom_out",
        ],
    }


def build_tool_selection_explanation(
    source_material: dict[str, str | None],
    project_type: str,
    layout_profile: dict[str, str],
    creation_type: str,
    website_goal: str,
    motion_intensity: str,
) -> dict[str, str]:
    return {
        "source_material_reason": f"Input is treated as {source_material['kind']} for {source_material['usage']}.",
        "build_scope_reason": f"Build scope is {project_type} because the detected/requested UI scope maps to that Magic project type.",
        "layout_profile_reason": f"Use the {layout_profile['name']} layout profile with {layout_profile['desktop_strategy']} desktop strategy because the selected surface and workflow need that composition pattern.",
        "magic_project_type_reason": f"Use Magic {project_type} to avoid generating the wrong UI surface.",
        "magic_creation_type_reason": f"Use {creation_type}; from_scratch means no URL flow, get_inspired means URL-derived evidence or inspiration.",
        "website_goal_reason": f"Use {website_goal} to pick the right conversion/workflow pattern.",
        "ui_ux_pro_max_mode_reason": "UI/UX Pro Max must improve the UI beyond the source while respecting fidelity and source truth.",
        "motion_intensity_reason": f"Use {motion_intensity} motion after UI rebuild only, with purpose and reduced-motion fallback.",
        "qa_gate_reason": "Design quality, visual parity, accessibility, responsiveness, and motion purpose gates must approve the output.",
    }


def build_motion_purpose_contract(motion_intensity: str, component_pattern: dict[str, str]) -> dict[str, Any]:
    if motion_intensity == "none":
        animations: list[dict[str, Any]] = []
    elif motion_intensity == "subtle":
        animations = [
            {
                "component": "interactive_controls",
                "trigger": "hover_focus_tap",
                "purpose": "Give immediate feedback without distracting from task completion.",
                "duration_ms": 120,
                "easing_or_spring": "easeOut",
                "reduced_motion_fallback": "color_or_opacity_change_only",
                "qa_assertion": "No layout shift and reduced-motion mode disables transforms.",
            }
        ]
    else:
        animations = [
            {
                "component": component_pattern["pattern"],
                "trigger": "enter_or_state_change",
                "purpose": "Improve orientation and perceived polish for the selected pattern.",
                "duration_ms": 180 if motion_intensity == "standard" else 260,
                "easing_or_spring": "easeOut_or_light_spring",
                "reduced_motion_fallback": "opacity_or_instant_state_change",
                "qa_assertion": "Animation does not delay primary task or hide content.",
            }
        ]
    return {"enabled": bool(animations), "intensity": motion_intensity, "animations": animations}


def build_design_strategy(
    source_type: str,
    domain: str | None = None,
    goal: str | None = None,
    scope: str | None = None,
    reference_url: str | None = None,
    fidelity_mode: str = "modernized_fidelity",
) -> dict[str, Any]:
    website_goal = infer_website_goal(goal, domain)
    project_type = infer_magic_project_type(source_type, scope)
    creation_type = infer_creation_type(reference_url, source_type)
    motion_intensity = infer_motion_intensity(website_goal, domain, fidelity_mode)
    source_material = infer_source_material(source_type, reference_url)
    rebuild_mode = infer_rebuild_mode(source_type, reference_url, fidelity_mode)
    tool_sequence = infer_tool_sequence(source_material)
    domain_style_pack = infer_domain_style_pack(domain, source_type)
    component_pattern = infer_component_pattern(website_goal, source_type, scope)
    layout_profile = infer_layout_profile(source_type, website_goal, scope, domain)
    viewport_fit_plan = build_viewport_fit_plan(layout_profile, domain_style_pack)
    tool_selection_explanation = build_tool_selection_explanation(
        source_material, project_type, layout_profile, creation_type, website_goal, motion_intensity
    )
    motion_purpose_contract = build_motion_purpose_contract(motion_intensity, component_pattern)

    return {
        "schema_version": "3.1.0",
        "source_type": source_type,
        "domain": domain or "unspecified",
        "fidelity_mode": fidelity_mode,
        "source_material": source_material,
        "decision": {
            "build_scope": project_type,
            "rebuild_mode": rebuild_mode,
            "improve_by_default": True,
            "improvement_guardrail": "Preserve source truth and requested fidelity while improving UX, accessibility, responsiveness, states, and polish.",
        },
        "tool_sequence": tool_sequence,
        "tool_selection_explanation": tool_selection_explanation,
        "domain_style_pack": domain_style_pack,
        "component_pattern_selection": component_pattern,
        "layout_profile_selection": layout_profile,
        "viewport_fit_plan": viewport_fit_plan,
        "magic_selection": {
            "project_type": project_type,
            "creation_type": creation_type,
            "website_goal": website_goal,
            "reference_url": reference_url,
        },
        "ui_ux_pro_max": {
            "mode": "visual_fidelity_director" if fidelity_mode == "exact_fidelity" else "design_director",
            "must_create": [
                "DESIGN.md",
                "design_tokens.json",
                "component_registry.json",
                "visual_acceptance_criteria.md",
            ],
            "must_persist": ["design-system/MASTER.md", "design-system/pages/{page_id}.md"],
        },
        "motion_plan": {
            "intensity": motion_intensity,
            "library": "motion",
            "accessibility": ["MotionConfig reducedMotion=user", "useReducedMotion for bespoke motion"],
            "bundle_policy": "Prefer LazyMotion and motion/react-m; load domMax only when layout/drag is required.",
            "purpose_contract": motion_purpose_contract,
        },
        "quality_gates": [
            "desktop_screenshot",
            "mobile_screenshot",
            "visual_diff",
            "axe_accessibility",
            "motion_reduced_mode_check",
            "no_text_overlap",
            "no_content_clipping",
            "desktop_space_usage_review",
            "layout_profile_match_check",
            "design_quality_score",
            "visual_rejection_gate",
        ],
    }


def write_design_strategy(path: Path, strategy: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(strategy, indent=2), encoding="utf-8")
    return path


def write_design_strategy_bundle(directory: Path, strategy: dict[str, Any]) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = {
        "design_decision_report": directory / "design_decision_report.json",
        "magic_selection": directory / "magic_selection.json",
        "motion_plan": directory / "motion_plan.json",
        "ui_ux_pro_max_brief": directory / "ui_ux_pro_max_brief.md",
        "tool_selection_explanation": directory / "tool_selection_explanation.md",
        "domain_style_pack": directory / "domain_style_pack.json",
        "component_pattern_selection": directory / "component_pattern_selection.json",
        "layout_profile_selection": directory / "layout_profile_selection.json",
        "viewport_fit_plan": directory / "viewport_fit_plan.json",
        "motion_purpose_contract": directory / "motion_purpose_contract.json",
    }
    paths["design_decision_report"].write_text(json.dumps(strategy, indent=2), encoding="utf-8")
    paths["magic_selection"].write_text(json.dumps(strategy["magic_selection"], indent=2), encoding="utf-8")
    paths["motion_plan"].write_text(json.dumps(strategy["motion_plan"], indent=2), encoding="utf-8")
    paths["domain_style_pack"].write_text(json.dumps(strategy["domain_style_pack"], indent=2), encoding="utf-8")
    paths["component_pattern_selection"].write_text(
        json.dumps(strategy["component_pattern_selection"], indent=2), encoding="utf-8"
    )
    paths["layout_profile_selection"].write_text(
        json.dumps(strategy["layout_profile_selection"], indent=2), encoding="utf-8"
    )
    paths["viewport_fit_plan"].write_text(
        json.dumps(strategy["viewport_fit_plan"], indent=2), encoding="utf-8"
    )
    paths["motion_purpose_contract"].write_text(
        json.dumps(strategy["motion_plan"]["purpose_contract"], indent=2), encoding="utf-8"
    )
    paths["ui_ux_pro_max_brief"].write_text(
        "# UI/UX Pro Max Brief\n\n"
        f"- Domain: {strategy['domain']}\n"
        f"- Source type: {strategy['source_type']}\n"
        f"- Source material: {strategy['source_material']['kind']} ({strategy['source_material']['usage']})\n"
        f"- Fidelity mode: {strategy['fidelity_mode']}\n"
        f"- Rebuild mode: {strategy['decision']['rebuild_mode']}\n"
        f"- Magic project type: {strategy['magic_selection']['project_type']}\n"
        f"- Magic creation type: {strategy['magic_selection']['creation_type']}\n"
        f"- Website goal: {strategy['magic_selection']['website_goal']}\n"
        f"- Layout profile: {strategy['layout_profile_selection']['name']}\n"
        f"- Desktop strategy: {strategy['layout_profile_selection']['desktop_strategy']}\n"
        f"- Motion intensity: {strategy['motion_plan']['intensity']}\n\n"
        "Create DESIGN.md, design_tokens.json, component_registry.json, and "
        "visual_acceptance_criteria.md from this decision. Preserve visual lock constraints, "
        "define measurable QA checks for every design and motion choice, and make viewport-fit "
        "decisions explicit for desktop, tablet, and mobile.\n",
        encoding="utf-8",
    )
    explanation = strategy["tool_selection_explanation"]
    paths["tool_selection_explanation"].write_text(
        "# Tool Selection Explanation\n\n"
        + "\n".join(f"- {key}: {value}" for key, value in explanation.items())
        + "\n",
        encoding="utf-8",
    )
    return paths
