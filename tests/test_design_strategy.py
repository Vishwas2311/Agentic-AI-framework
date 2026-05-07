from genesis_framework.design_strategy import build_design_strategy, write_design_strategy_bundle


def test_website_reference_uses_get_inspired_and_sales_goal() -> None:
    strategy = build_design_strategy(
        source_type="website_url",
        domain="ecommerce product store",
        goal="drive sales",
        reference_url="https://example.com",
    )
    magic = strategy["magic_selection"]
    assert magic["project_type"] == "website"
    assert magic["creation_type"] == "get_inspired"
    assert magic["website_goal"] == "drive_sales"
    assert strategy["source_material"]["kind"] == "url"
    assert strategy["decision"]["improve_by_default"]
    assert strategy["tool_sequence"][:2] == ["firecrawl", "playwright"]


def test_component_request_uses_component_mode() -> None:
    strategy = build_design_strategy(source_type="component", goal="metric card", scope="component")
    assert strategy["magic_selection"]["project_type"] == "component"
    assert strategy["magic_selection"]["creation_type"] == "from_scratch"


def test_enterprise_dashboard_gets_subtle_motion() -> None:
    strategy = build_design_strategy(source_type="screenshot", domain="enterprise admin dashboard", goal="custom")
    assert strategy["motion_plan"]["intensity"] == "subtle"
    assert strategy["domain_style_pack"]["name"] == "saas_admin"
    assert strategy["component_pattern_selection"]["name"] == "dashboard"
    assert strategy["layout_profile_selection"]["name"] == "portal_dashboard"
    assert strategy["viewport_fit_plan"]["container_strategy"]


def test_uploaded_image_from_scratch_still_uses_image_evidence() -> None:
    strategy = build_design_strategy(source_type="mobile_app_screenshot", domain="fitness app", goal="mobile onboarding")
    assert strategy["magic_selection"]["creation_type"] == "from_scratch"
    assert strategy["source_material"]["kind"] == "uploaded_image"
    assert strategy["source_material"]["usage"] == "primary_visual_evidence"
    assert "vision_model" in strategy["tool_sequence"]


def test_url_can_still_build_single_component() -> None:
    strategy = build_design_strategy(
        source_type="website_url",
        scope="pricing card component",
        reference_url="https://example.com",
    )
    assert strategy["magic_selection"]["project_type"] == "component"
    assert strategy["magic_selection"]["creation_type"] == "get_inspired"
    assert strategy["source_material"]["kind"] == "url"


def test_healthcare_gets_healthcare_style_pack_and_motion_contract() -> None:
    strategy = build_design_strategy(source_type="mobile_app_screenshot", domain="healthcare patient app")
    assert strategy["domain_style_pack"]["name"] == "healthcare"
    assert strategy["motion_plan"]["purpose_contract"]["intensity"] == "subtle"
    assert "tool_selection_explanation" in strategy
    assert "layout_profile_reason" in strategy["tool_selection_explanation"]


def test_login_screen_uses_auth_layout_profile() -> None:
    strategy = build_design_strategy(source_type="component", goal="login form", scope="login screen")
    assert strategy["layout_profile_selection"]["name"] == "auth_split_screen"
    assert "miniaturized_form_on_desktop" in strategy["viewport_fit_plan"]["rejection_triggers"]


def test_design_strategy_bundle_writes_expected_files(tmp_path) -> None:
    strategy = build_design_strategy(source_type="website", goal="subscription SaaS")
    paths = write_design_strategy_bundle(tmp_path, strategy)
    assert paths["magic_selection"].exists()
    assert paths["motion_plan"].exists()
    assert paths["ui_ux_pro_max_brief"].exists()
    assert paths["layout_profile_selection"].exists()
    assert paths["viewport_fit_plan"].exists()
