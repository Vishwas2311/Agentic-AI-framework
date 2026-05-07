from genesis_framework.design_quality import evaluate_design_quality


def test_design_quality_rejects_empty_scores() -> None:
    report = evaluate_design_quality()
    assert not report["approved"]
    assert report["next_action"] == "reject_and_run_ui_polish_loop"
    assert report["failures"]


def test_design_quality_approves_good_scores() -> None:
    report = evaluate_design_quality(
        {
            "visual_fidelity_score": 0.95,
            "ux_quality_score": 0.94,
            "accessibility_score": 0.98,
            "responsive_score": 0.96,
            "desktop_space_utilization_score": 0.90,
            "content_density_score": 0.88,
            "container_fit_score": 0.89,
            "motion_quality_score": 0.91,
            "component_reuse_score": 0.90,
        }
    )
    assert report["approved"]
    assert report["next_action"] == "approve"


def test_design_quality_rejects_poor_viewport_fit_scores() -> None:
    report = evaluate_design_quality(
        {
            "visual_fidelity_score": 0.95,
            "ux_quality_score": 0.94,
            "accessibility_score": 0.98,
            "responsive_score": 0.96,
            "desktop_space_utilization_score": 0.60,
            "content_density_score": 0.90,
            "container_fit_score": 0.90,
            "motion_quality_score": 0.91,
            "component_reuse_score": 0.90,
        }
    )
    assert not report["approved"]
    assert any(failure["score"] == "desktop_space_utilization_score" for failure in report["failures"])
