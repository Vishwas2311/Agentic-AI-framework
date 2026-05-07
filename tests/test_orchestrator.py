from pathlib import Path

import json

from genesis_framework.orchestrator import run_pipeline


ROOT = Path(__file__).resolve().parents[1]


def test_migrate_pipeline_writes_core_outputs(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    workspace = tmp_path / "workspace"
    input_dir.mkdir()
    html_reference = tmp_path / "portal.html"
    html_reference.write_text(
        "<html><head><title>Demo Portal</title></head><body><form></form><button>Submit</button></body></html>",
        encoding="utf-8",
    )
    (input_dir / "migration_request.yaml").write_text(
        "\n".join(
            [
                "app_name: Demo Portal",
                "delivery_mode: production_procode",
                "domain: healthcare",
                "goal: Rebuild the app as production software",
                "reference_urls:",
                f"  - {html_reference.as_uri()}",
            ]
        ),
        encoding="utf-8",
    )
    (input_dir / "portal.pa.yaml").write_text("DashboardScreen As screen:\n", encoding="utf-8")
    (input_dir / "notes.txt").write_text(
        "System must allow managers to approve requests.\nUser can submit a request from the dashboard page.\n",
        encoding="utf-8",
    )

    result = run_pipeline(
        "migrate",
        project=ROOT,
        input_dir=input_dir,
        app_name="Demo Portal",
        workspace=workspace,
    )

    assert result.workspace == workspace
    assert (workspace / "canonical_app_spec.json").exists()
    assert (workspace / "checkpoint_manifest.json").exists()
    assert (workspace / "genesis_replay_dashboard.html").exists()
    assert (workspace / "generated_file_manifest.json").exists()
    assert (workspace / "runtime_session.json").exists()
    assert (workspace / "provider_routing_plan.json").exists()
    assert (workspace / "agent_execution_plan.json").exists()
    assert (workspace / "browser_runtime_plan.json").exists()
    assert (workspace / "memory_context.json").exists()
    assert (workspace / "verified_memory_packet.json").exists()
    assert (workspace / "repair_loop_report.json").exists()
    assert (workspace / "code_quality_report.json").exists()
    assert (workspace / "test_report.json").exists()
    assert (workspace / "security_review.json").exists()
    assert (workspace / "production_readiness_scorecard.json").exists()
    assert (workspace / "migration_mode_decision.json").exists()
    assert (workspace / "migration_mode_options.md").exists()
    assert (workspace / "brd_understanding_report.json").exists()
    assert (workspace / "brd_understanding_summary.md").exists()
    assert (workspace / "brd_understanding_gate.json").exists()
    assert (workspace / "brd_semantic_patch_report.json").exists()
    assert (workspace / "approved_brd_plan.json").exists()
    assert (workspace / "visual_reference_inventory.json").exists()
    assert (workspace / "generated_app_review_report.json").exists()
    assert (workspace / "generated_app_review_summary.md").exists()
    assert (workspace / "generated_app_approval_gate.json").exists()
    assert (workspace / "generated_app_human_notes.json").exists()
    assert (workspace / "generated_app_patch_instructions.json").exists()
    assert (workspace / "generated_app_semantic_patch_report.json").exists()
    assert (workspace / "source_truth_approval_gate.json").exists()
    assert (workspace / "approved_source_truth_report.json").exists()
    assert (workspace / "canonical_spec_approval_gate.json").exists()
    assert (workspace / "approved_canonical_app_spec.json").exists()
    assert (workspace / "design_system_approval_gate.json").exists()
    assert (workspace / "approved_design_system_plan.json").exists()
    assert (workspace / "qa_result_approval_gate.json").exists()
    assert (workspace / "qa_result_review_summary.json").exists()
    assert (workspace / "final_release_approval_gate.json").exists()
    assert (workspace / "human_gate_context.json").exists()
    assert (workspace / "run_demo.ps1").exists()
    assert (workspace / "demo_report.md").exists()
    assert (workspace / "production_gap_report.md").exists()
    assert (workspace / "frontend" / "package.json").exists()
    assert (workspace / "backend" / "app" / "main.py").exists()
    assert (workspace / "database" / "migration.sql").exists()
    spec = json.loads((workspace / "canonical_app_spec.json").read_text(encoding="utf-8"))
    assert spec["app"]["name"] == "Demo Portal"
    assert "ui_spec" in spec
    assert "api_spec" in spec
    runtime_session = json.loads((workspace / "runtime_session.json").read_text(encoding="utf-8"))
    runtime_evidence = json.loads((workspace / "runtime_evidence.json").read_text(encoding="utf-8"))
    brd_design_intent = json.loads((workspace / "brd_design_intent.json").read_text(encoding="utf-8"))
    brd_gate = json.loads((workspace / "brd_understanding_gate.json").read_text(encoding="utf-8"))
    generated_app_gate = json.loads((workspace / "generated_app_approval_gate.json").read_text(encoding="utf-8"))
    human_gate_context = json.loads((workspace / "human_gate_context.json").read_text(encoding="utf-8"))
    agent_execution_plan = json.loads((workspace / "agent_execution_plan.json").read_text(encoding="utf-8"))
    assert runtime_session["last_command"] == "migrate"
    assert runtime_evidence["captured_targets"][0]["status"] == "captured"
    assert brd_design_intent["functional_requirements"]
    assert brd_gate["requires_human_confirmation"] is True
    assert generated_app_gate["status"] == "pending_review"
    assert generated_app_gate["requires_human_confirmation"] is True
    assert human_gate_context["pipeline_sequence_changed"] is False
    assert "source_truth_approval_gate" in human_gate_context["gates"]
    assert agent_execution_plan["human_gate_context_file"] == "human_gate_context.json"
    assert agent_execution_plan["pipeline_sequence_changed_by_gates"] is False
    code_quality = json.loads((workspace / "code_quality_report.json").read_text(encoding="utf-8"))
    test_report = json.loads((workspace / "test_report.json").read_text(encoding="utf-8"))
    scorecard = json.loads((workspace / "production_readiness_scorecard.json").read_text(encoding="utf-8"))
    mode_decision = json.loads((workspace / "migration_mode_decision.json").read_text(encoding="utf-8"))
    generated_manifest = json.loads((workspace / "generated_file_manifest.json").read_text(encoding="utf-8"))
    assert code_quality["status"] in {"passed", "passed_with_warnings"}
    assert code_quality["gate_passed"] is True
    assert test_report["status"] in {"passed", "passed_with_warnings"}
    assert scorecard["release_state"] in {"blocked_pending_review", "ready_for_human_review", "approved_for_handoff"}
    assert mode_decision["selected_mode"] == "production_e2e_app"
    assert "brd_understanding" in spec
    assert "human_semantic_patch_spec" in spec
    assert generated_manifest["migration_output_mode"] == "production_e2e_app"
