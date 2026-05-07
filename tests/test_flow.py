from pathlib import Path

from genesis_framework.config import load_yaml
from genesis_framework.flow import stages_for_entrypoint, validate_flow
from genesis_framework.policy import is_tool_allowed


ROOT = Path(__file__).resolve().parents[1]


def test_flow_is_valid() -> None:
    flow = load_yaml(ROOT / ".genesis" / "genesis.flow.yaml")
    assert validate_flow(flow) == []
    assert len(stages_for_entrypoint(flow)) >= 10


def test_policy_denies_unknown_tool() -> None:
    tools = load_yaml(ROOT / ".genesis" / "genesis.tools.yaml")
    decision = is_tool_allowed(tools, "generate_code", "terraform")
    assert not decision.allowed


def test_policy_allows_context7_for_generation() -> None:
    tools = load_yaml(ROOT / ".genesis" / "genesis.tools.yaml")
    decision = is_tool_allowed(tools, "generate_code", "context7")
    assert decision.allowed


def test_routing_has_figma_signal() -> None:
    routing = load_yaml(ROOT / ".genesis" / "genesis.routing.yaml")
    assert "figma_url_present" in routing["source_routing"]
    assert "figma_mcp" in routing["source_routing"]["figma_url_present"]["tools"]


def test_install_plan_marks_kubernetes_manual() -> None:
    install = load_yaml(ROOT / ".genesis" / "genesis.install.yaml")
    assert install["tools"]["kubernetes"]["install_mode"] == "manual_setup_required"
    assert "kubernetes" in install["policy"]["never_auto_install"]


def test_design_strategy_config_has_magic_goals() -> None:
    design = load_yaml(ROOT / ".genesis" / "genesis.design.yaml")
    goals = design["magic_selection"]["website_goals"]
    assert "lead_generation" in goals
    assert "drive_sales" in goals
    assert "interactive_quiz" in goals
    assert "subscriptions" in goals
    assert "custom" in goals


def test_design_quality_config_has_rejection_gate() -> None:
    quality = load_yaml(ROOT / ".genesis" / "genesis.design_quality.yaml")
    assert "visual_rejection_gate" in quality
    assert "domain_style_packs" in quality
    assert "healthcare" in quality["domain_style_packs"]


def test_stack_governance_config_exists() -> None:
    stack = load_yaml(ROOT / ".genesis" / "genesis.stack.yaml")
    assert stack["default_decision"]["if_user_says_same_software"] == "preserve_features_not_stack"
    assert "streamlit" in stack["stack_categories"]["prototype_or_demo"]


def test_flow_requires_stack_and_brd_design_stages() -> None:
    flow = load_yaml(ROOT / ".genesis" / "genesis.flow.yaml")
    stages = [stage.name for stage in stages_for_entrypoint(flow)]
    assert stages.index("decide_delivery_mode_and_stack") < stages.index("generate_code")
    assert (
        stages.index("extract_brd_mockups")
        < stages.index("brd_understanding_gate")
        < stages.index("decide_delivery_mode_and_stack")
        < stages.index("migration_mode_gate")
        < stages.index("dry_run_estimate")
    )
    assert stages.index("resolve_source_truth") < stages.index("source_truth_approval_gate") < stages.index("build_ulc_ir")
    assert stages.index("build_canonical_app_spec") < stages.index("canonical_spec_approval_gate") < stages.index("human_review_gate")
    assert stages.index("generate_design_system") < stages.index("design_system_approval_gate") < stages.index("generate_code")
    assert stages.index("generate_code") < stages.index("generated_app_approval_gate") < stages.index("run_agent_repair_loop")
    assert stages.index("evaluate_design_quality") < stages.index("qa_result_approval_gate") < stages.index("build_replay_dashboard")
    assert "extract_brd_design_intent" in stages
    assert "extract_brd_mockups" in stages
    assert "brd_understanding_gate" in stages
    assert "generated_app_approval_gate" in stages
