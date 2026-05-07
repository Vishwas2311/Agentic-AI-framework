from genesis_framework.stack_resolver import resolve_stack_decision


def test_production_prompt_upgrades_streamlit_brd_to_premium_web_profile() -> None:
    decision = resolve_stack_decision(
        'Use "Hospital_Online_Consultation_Portal_BRD.docx" and build the same software as production pro-code.',
        brd_stack="streamlit",
        domain="healthcare patient portal",
        scope="dashboard portal",
    )
    assert decision["selected_delivery_mode"] == "production_procode"
    assert decision["selected_target_stack"] == "nextjs_tailwind_shadcn_motion"
    assert decision["conflict_detected"]
    assert not decision["prototype_stack_allowed"]


def test_exact_streamlit_request_requires_human_approval() -> None:
    decision = resolve_stack_decision(
        "Keep Streamlit exactly and build the exact streamlit demo only.",
        brd_stack="streamlit",
        domain="healthcare",
        scope="portal",
    )
    assert decision["selected_delivery_mode"] == "prototype_demo"
    assert decision["selected_target_stack"] == "streamlit"
    assert decision["human_approval_required"]


def test_enterprise_ui_heavy_run_prefers_api_profile() -> None:
    decision = resolve_stack_decision(
        "Migrate this enterprise portal with audit, permissions, integrations, and production quality.",
        brd_stack="powerapps",
        domain="healthcare portal",
        scope="dashboard portal",
    )
    assert decision["selected_delivery_mode"] == "enterprise_migration"
    assert decision["selected_target_stack"] == "nextjs_tailwind_shadcn_motion_plus_api"
    assert decision["selected_ui_automation_profile"] == "ui_ux_pro_max_magic_motion"
