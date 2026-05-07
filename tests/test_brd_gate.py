from genesis_framework.brd_gate import build_brd_understanding, normalize_brd_gate_decision, resolve_brd_understanding_gate


def test_brd_gate_normalizes_options() -> None:
    assert normalize_brd_gate_decision("A") == "approved"
    assert normalize_brd_gate_decision("approve with assumptions") == "approved_with_assumptions"
    assert normalize_brd_gate_decision("D") == "edit_requested"


def test_brd_gate_builds_understanding_from_design_intent() -> None:
    understanding = build_brd_understanding(
        {"roles": ["patient"]},
        {
            "domain": "healthcare",
            "goal": "Build a portal",
            "summary_sentences": ["Patients book consultations."],
            "functional_requirements": ["Patient can log in."],
            "screen_candidates": ["Login Page"],
            "workflow_candidates": ["Patient can book a consultation."],
            "document_entities": ["Patient"],
            "acceptance_criteria": ["Login succeeds."],
            "document_confidence": 0.8,
        },
        {"images": ["login.png"], "videos": []},
        [{"kind": "document", "relative_path": "portal.docx", "summary": "BRD", "confidence": 0.8, "metadata": {}}],
        app_name="Portal",
    )
    assert understanding["application_intent"]["domain"] == "healthcare"
    assert understanding["functional_requirements"] == ["Patient can log in."]
    assert understanding["pages_or_screens"][0]["name"] == "Login Page"
    assert understanding["mockup_evidence"]["separate_images"] == ["login.png"]


def test_brd_gate_edit_notes_allow_pipeline_to_continue() -> None:
    gate = resolve_brd_understanding_gate(
        {"brd_gate_decision": "D", "brd_edit_notes": "Remove billing page and add admin queue."},
        {"functional_requirements": ["Patient can log in."]},
        app_name="Portal",
    )
    assert gate["status"] == "edited_by_request"
    assert gate["requires_human_confirmation"] is False
    assert gate["approved_brd_plan"]["manual_overrides"][0]["text"] == "Remove billing page and add admin queue."
    assert gate["semantic_patch"]["status"] in {"applied", "applied_with_review_items"}


def test_brd_gate_requires_review_when_unspecified() -> None:
    gate = resolve_brd_understanding_gate({}, {"functional_requirements": []}, app_name="Portal")
    assert gate["status"] == "pending_review"
    assert gate["requires_human_confirmation"] is True
