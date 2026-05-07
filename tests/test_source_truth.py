from genesis_framework.source_truth import decide_source_truth
from genesis_framework.visual_fidelity import bbox_delta, default_visual_lock_spec


def test_runtime_wins_before_export() -> None:
    decision = decide_source_truth(
        artifact_id="screen:home",
        artifact_type="screen",
        candidates={"export": {}, "runtime": {}},
    )
    assert decision.winning_source == "runtime"
    assert not decision.requires_human_review


def test_visual_lock_defaults_block_content_removal() -> None:
    spec = default_visual_lock_spec("login")
    screen = spec["screens"][0]
    assert screen["blocked_changes"]["remove_visible_content"] is True
    assert screen["thresholds"]["minor_spacing_tolerance_px"] == 8


def test_bbox_delta() -> None:
    delta = bbox_delta({"x": 10, "y": 10, "width": 100, "height": 50}, {"x": 14, "y": 8, "width": 110, "height": 45})
    assert delta == {"x": 4, "y": -2, "width": 10, "height": -5}
