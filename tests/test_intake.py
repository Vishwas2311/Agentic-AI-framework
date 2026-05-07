from pathlib import Path

from genesis_framework.intake import (
    ensure_input_directory,
    infer_primary_source_type,
    load_migration_request,
    scan_input_directory,
    summarize_input_artifacts,
)


def test_scan_input_directory_detects_powerapps_and_urls(tmp_path: Path) -> None:
    (tmp_path / "migration_request.yaml").write_text(
        "app_name: Intake App\ndomain: healthcare\n",
        encoding="utf-8",
    )
    (tmp_path / "app.pa.yaml").write_text("HomeScreen As screen:\n", encoding="utf-8")
    (tmp_path / "references.txt").write_text("https://example.com/app\n", encoding="utf-8")

    request = load_migration_request(tmp_path)
    artifacts = scan_input_directory(tmp_path)

    assert request["app_name"] == "Intake App"
    assert len(artifacts) == 2
    assert any(artifact.source_type == "powerapps" for artifact in artifacts)
    assert any(artifact.signal == "website_url_present" for artifact in artifacts)
    assert infer_primary_source_type(artifacts, request) == "powerapps"


def test_ensure_input_directory_creates_standard_lanes(tmp_path: Path) -> None:
    input_dir = ensure_input_directory(tmp_path)

    assert input_dir.name == "migration_inputs"
    assert (input_dir / "raw_data").is_dir()
    assert (input_dir / "images").is_dir()
    assert (input_dir / "videos").is_dir()


def test_scan_input_directory_classifies_raw_images_and_videos(tmp_path: Path) -> None:
    (tmp_path / "raw_data").mkdir()
    (tmp_path / "images").mkdir()
    (tmp_path / "videos").mkdir()
    (tmp_path / "raw_data" / "app.pa.yaml").write_text("HomeScreen As screen:\n", encoding="utf-8")
    (tmp_path / "images" / "dashboard.png").write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + (1440).to_bytes(4, "big") + (900).to_bytes(4, "big") + b"\x00" * 8
    )
    (tmp_path / "videos" / "booking-walkthrough.mp4").write_bytes(b"video")
    (tmp_path / "images" / "image_manifest.example.yaml").write_text("images: []\n", encoding="utf-8")

    artifacts = scan_input_directory(tmp_path)
    summary = summarize_input_artifacts(artifacts, {})

    assert len(artifacts) == 3
    assert summary["input_buckets"] == {"images": 1, "raw_data": 1, "videos": 1}
    image = next(artifact for artifact in artifacts if artifact.source_type == "image")
    video = next(artifact for artifact in artifacts if artifact.source_type == "video")
    raw = next(artifact for artifact in artifacts if artifact.source_type == "powerapps")
    assert image.metadata["input_lane"] == "visual_reference"
    assert image.metadata["visual_reference_purpose"] == "ui_reference"
    assert video.metadata["input_lane"] == "runtime_behavior"
    assert video.metadata["video_reference_purpose"] == "runtime_walkthrough"
    assert raw.metadata["input_lane"] == "source_evidence"


def test_image_manifest_overrides_visual_reference_metadata(tmp_path: Path) -> None:
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "dashboard.png").write_bytes(b"image")
    (tmp_path / "images" / "image_manifest.yaml").write_text(
        "\n".join(
            [
                "images:",
                "  - file: dashboard.png",
                "    screen: Executive Dashboard",
                "    purpose: exact_ui_reference",
                "    priority: high",
            ]
        ),
        encoding="utf-8",
    )

    artifacts = scan_input_directory(tmp_path)

    assert len(artifacts) == 1
    artifact = artifacts[0]
    assert artifact.metadata["screen_hint"] == "Executive Dashboard"
    assert artifact.metadata["visual_reference_purpose"] == "exact_ui_reference"
    assert artifact.metadata["priority"] == "high"
