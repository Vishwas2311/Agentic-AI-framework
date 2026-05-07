from pathlib import Path

from genesis_framework.analyzers.brd import analyze_brd_text
from genesis_framework.analyzers.screenshot import analyze_visual_artifact
from genesis_framework.browser_capture import capture_runtime_targets


def test_brd_analyzer_extracts_requirements_and_roles() -> None:
    analysis = analyze_brd_text(
        """
        Business Requirements Document
        System must allow managers to approve requests.
        User can submit a request from the Request Form page.
        Dashboard page should show approval queue for admin users.
        Given a valid request, then the reviewer should see Submit and Reject actions.
        """,
        source_name="BRD-approval-flow.md",
    )

    assert analysis["document_type"] == "brd"
    assert any("approve requests" in item.lower() for item in analysis["functional_requirements"])
    assert "manager" in analysis["user_roles"]
    assert any("dashboard" in item.lower() for item in analysis["screen_candidates"])


def test_screenshot_analyzer_detects_png_dimensions(tmp_path: Path) -> None:
    image_path = tmp_path / "admin-dashboard.png"
    image_path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x04\x00"  # width 1024
        b"\x00\x00\x03\x00"  # height 768
        b"\x08\x02\x00\x00\x00"
        b"\x00\x00\x00\x00"
    )

    analysis = analyze_visual_artifact(image_path)

    assert analysis["dimensions"]["width"] == 1024
    assert analysis["dimensions"]["height"] == 768
    assert analysis["viewport_kind"] == "desktop"
    assert "dashboard" in analysis["visual_hints"]


def test_browser_capture_reads_local_file_html(tmp_path: Path) -> None:
    page_path = tmp_path / "index.html"
    page_path.write_text(
        "<html><head><title>Portal</title></head><body><form></form><a href='/x'>Go</a><button>Save</button></body></html>",
        encoding="utf-8",
    )

    capture = capture_runtime_targets([page_path.as_uri()], tmp_path / "captures")

    assert capture["captured_count"] == 1
    target = capture["targets"][0]
    assert target["status"] == "captured"
    assert target["title"] == "Portal"
    assert target["forms"] == 1
