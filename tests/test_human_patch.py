from genesis_framework.human_patch import apply_brd_semantic_patch, build_generated_app_semantic_patch, parse_human_patch_notes


def test_parse_human_patch_notes_classifies_add_remove_targets() -> None:
    patch = parse_human_patch_notes("Add admin approval queue and remove billing page.", source="test")
    assert patch["action_count"] == 2
    assert patch["actions"][0]["operation"] == "add"
    assert patch["actions"][0]["target"] == "pages_or_screens"
    assert patch["actions"][1]["operation"] == "remove"
    assert patch["actions"][1]["target"] == "pages_or_screens"


def test_apply_brd_semantic_patch_structurally_updates_plan() -> None:
    plan = {
        "pages_or_screens": [{"name": "Billing Page", "source": "brd"}],
        "functional_requirements": [],
        "workflows": [],
        "entities": [],
        "roles": [],
        "acceptance_criteria": [],
    }
    patched, report = apply_brd_semantic_patch(plan, "Add admin approval queue and remove billing page.")
    names = [screen["name"] for screen in patched["pages_or_screens"]]
    assert "Billing Page" not in names
    assert "Admin Approval" in names[0]
    assert report["status"] == "applied"
    assert "pages_or_screens" in report["patched_fields"]


def test_generated_app_semantic_patch_targets_repair_loop() -> None:
    patch = build_generated_app_semantic_patch("Add admin dashboard before QA.", action="additional_input")
    assert patch["source"] == "generated_app_gate"
    assert patch["target_stage"] == "run_agent_repair_loop"
    assert patch["actions"][0]["target"] == "pages_or_screens"
