from __future__ import annotations

import csv
import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import yaml


DEFAULT_INPUT_DIR_NAME = "migration_inputs"
STANDARD_INPUT_BUCKETS = ("raw_data", "images", "videos")
REQUEST_FILE_CANDIDATES = (
    "migration_request.yaml",
    "migration_request.yml",
    "migration_request.json",
    "migration_request.md",
    "migration_request.txt",
)
INPUT_MANIFEST_FILES = {
    "images": ("image_manifest.yaml", "image_manifest.yml", "image_manifest.json"),
    "videos": ("video_manifest.yaml", "video_manifest.yml", "video_manifest.json"),
    "raw_data": ("raw_data_manifest.yaml", "raw_data_manifest.yml", "raw_data_manifest.json"),
}
URL_RE = re.compile(r"https?://[^\s)>\]\"']+")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
TEXT_EXTENSIONS = {".txt", ".md", ".rst"}
DATA_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls"}
DOC_EXTENSIONS = {".pdf", ".docx", ".pptx"}
STRUCTURED_EXTENSIONS = {".json", ".yaml", ".yml", ".xml"}


@dataclass
class InputArtifact:
    artifact_id: str
    path: Path
    relative_path: str
    kind: str
    source_type: str
    signal: str
    summary: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    urls: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "path": str(self.path),
            "relative_path": self.relative_path,
            "kind": self.kind,
            "source_type": self.source_type,
            "signal": self.signal,
            "summary": self.summary,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "urls": self.urls,
        }


def default_input_dir(root: Path) -> Path:
    return root / DEFAULT_INPUT_DIR_NAME


def ensure_input_directory(root: Path) -> Path:
    directory = default_input_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    for bucket in STANDARD_INPUT_BUCKETS:
        bucket_dir = directory / bucket
        bucket_dir.mkdir(parents=True, exist_ok=True)
        gitkeep = bucket_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
    return directory


def load_migration_request(input_dir: Path) -> dict[str, Any]:
    for candidate in REQUEST_FILE_CANDIDATES:
        path = input_dir / candidate
        if not path.exists():
            continue
        if path.suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return data if isinstance(data, dict) else {"notes": str(data)}
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"notes": str(data)}
        text = path.read_text(encoding="utf-8", errors="ignore")
        parsed = _parse_key_value_text(text)
        parsed.setdefault("notes", text.strip())
        return parsed
    return {}


def scan_input_directory(input_dir: Path) -> list[InputArtifact]:
    artifacts: list[InputArtifact] = []
    excluded = {name.lower() for name in REQUEST_FILE_CANDIDATES} | {"readme.md"}
    for candidates in INPUT_MANIFEST_FILES.values():
        excluded.update(name.lower() for name in candidates)
    manifests = _load_input_manifests(input_dir)
    for index, path in enumerate(sorted(item for item in input_dir.rglob("*") if item.is_file()), start=1):
        lower_name = path.name.lower()
        if lower_name in excluded or lower_name.endswith((".example.yaml", ".example.yml", ".example.json")) or ".gitkeep" in lower_name:
            continue
        artifacts.append(classify_input_path(path, input_dir, index, manifests=manifests))
    return artifacts


def classify_input_path(
    path: Path,
    input_dir: Path,
    index: int,
    *,
    manifests: dict[str, Any] | None = None,
) -> InputArtifact:
    lower_name = path.name.lower()
    suffix = path.suffix.lower()
    relative_path = str(path.relative_to(input_dir))
    input_bucket = _input_bucket(relative_path)
    manifest_entry = _manifest_entry_for(relative_path, manifests or {})
    metadata: dict[str, Any] = {
        "extension": suffix,
        "size_bytes": path.stat().st_size,
        "input_bucket": input_bucket,
        "input_lane": _input_lane(input_bucket),
    }
    if manifest_entry:
        metadata["manifest"] = manifest_entry
    urls: list[str] = []
    kind = "binary"
    source_type = "file"
    signal = "generic_input_present"
    confidence = 0.45
    summary = "Generic input file."

    if lower_name.endswith(".pa.yaml") or lower_name.endswith(".msapp"):
        kind = "lowcode_export"
        source_type = "powerapps"
        signal = "powerapps_export_present"
        confidence = 0.8
        metadata.update(_inspect_powerapps_like(path))
        summary = "Power Apps source artifact detected."
    elif suffix == ".zip":
        archive_info = _inspect_zip_file(path)
        metadata.update(archive_info)
        if archive_info.get("contains_powerapps_markers"):
            kind = "lowcode_export"
            source_type = "powerapps"
            signal = "powerapps_export_present"
            confidence = 0.75
            summary = "Archive appears to contain Power Platform or Power Apps source files."
        else:
            kind = "archive"
            source_type = "archive"
            signal = "archive_input_present"
            confidence = 0.55
            summary = "Archive input detected."
    elif suffix in IMAGE_EXTENSIONS:
        kind = "visual_evidence"
        source_type = "image"
        signal = "screenshot_present"
        purpose = str(manifest_entry.get("purpose") or _visual_reference_purpose(relative_path, lower_name))
        metadata["visual_reference_purpose"] = purpose
        metadata["screen_hint"] = manifest_entry.get("screen") or _screen_hint_from_path(relative_path)
        metadata["priority"] = manifest_entry.get("priority") or _reference_priority(relative_path)
        confidence = 0.78 if input_bucket == "images" else 0.72
        summary = f"Image UI/reference evidence detected ({purpose})."
    elif suffix in VIDEO_EXTENSIONS:
        kind = "video_evidence"
        source_type = "video"
        signal = "video_present"
        purpose = str(manifest_entry.get("purpose") or _video_reference_purpose(relative_path, lower_name))
        metadata["video_reference_purpose"] = purpose
        metadata["flow_hint"] = manifest_entry.get("flow") or _screen_hint_from_path(relative_path)
        metadata["priority"] = manifest_entry.get("priority") or _reference_priority(relative_path)
        confidence = 0.74 if input_bucket == "videos" else 0.68
        summary = f"Video walkthrough/runtime evidence detected ({purpose})."
    elif suffix in {".yaml", ".yml", ".json"}:
        structured = _inspect_structured_file(path)
        metadata.update(structured)
        kind = "structured"
        source_type = structured.get("source_type", "structured")
        signal = structured.get("signal", "structured_file_present")
        confidence = float(structured.get("confidence", 0.7))
        summary = structured.get("summary", "Structured file detected.")
        urls = structured.get("urls", [])
    elif suffix == ".xml":
        xml_info = _inspect_xml_file(path)
        metadata.update(xml_info)
        kind = "structured"
        source_type = xml_info.get("source_type", "xml")
        signal = xml_info.get("signal", "xml_present")
        confidence = float(xml_info.get("confidence", 0.65))
        summary = xml_info.get("summary", "XML input detected.")
    elif suffix in DATA_EXTENSIONS:
        data_info = _inspect_table_file(path)
        metadata.update(data_info)
        kind = "data"
        source_type = data_info.get("source_type", "tabular")
        signal = data_info.get("signal", "data_input_present")
        confidence = float(data_info.get("confidence", 0.7))
        summary = data_info.get("summary", "Tabular or spreadsheet input detected.")
    elif suffix == ".sql":
        sql_info = _inspect_sql_file(path)
        metadata.update(sql_info)
        kind = "database_schema"
        source_type = "database"
        signal = "db_connection_present"
        confidence = 0.78
        summary = sql_info.get("summary", "SQL schema input detected.")
    elif suffix in DOC_EXTENSIONS:
        doc_info = _inspect_document_file(path)
        metadata.update(doc_info)
        kind = "document"
        source_type = doc_info.get("source_type", "document")
        signal = doc_info.get("signal", "document_present")
        confidence = float(doc_info.get("confidence", 0.62))
        summary = doc_info.get("summary", "Document input detected.")
        urls = doc_info.get("urls", [])
    elif suffix in TEXT_EXTENSIONS or suffix == ".url":
        text_info = _inspect_text_file(path)
        metadata.update(text_info)
        urls = text_info.get("urls", [])
        if urls:
            kind = "website_reference"
            source_type = "website"
            signal = "website_url_present"
            confidence = 0.7
            summary = "Website URLs or references detected."
        else:
            kind = "document"
            source_type = "text"
            signal = "document_present"
            confidence = 0.58
            summary = text_info.get("summary", "Text input detected.")
    elif suffix == ".har":
        kind = "runtime_evidence"
        source_type = "network_trace"
        signal = "api_trace_present"
        confidence = 0.82
        summary = "Network trace input detected."
    elif suffix == ".openapi":
        kind = "api_spec"
        source_type = "api"
        signal = "openapi_present"
        confidence = 0.85
        summary = "OpenAPI input detected."

    metadata["detected_urls"] = urls
    if input_bucket == "raw_data":
        metadata.setdefault("raw_data_role", str(manifest_entry.get("purpose") or "source_evidence"))
    return InputArtifact(
        artifact_id=f"artifact-{index:03d}",
        path=path,
        relative_path=relative_path,
        kind=kind,
        source_type=source_type,
        signal=signal,
        summary=summary,
        confidence=confidence,
        metadata=metadata,
        urls=urls,
    )


def summarize_input_artifacts(artifacts: list[InputArtifact], request: dict[str, Any]) -> dict[str, Any]:
    by_signal: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_bucket: dict[str, int] = {}
    discovered_urls: list[str] = []
    unsupported: list[str] = []
    for artifact in artifacts:
        by_signal[artifact.signal] = by_signal.get(artifact.signal, 0) + 1
        by_type[artifact.source_type] = by_type.get(artifact.source_type, 0) + 1
        bucket = str(artifact.metadata.get("input_bucket") or "root")
        by_bucket[bucket] = by_bucket.get(bucket, 0) + 1
        discovered_urls.extend(artifact.urls)
        if artifact.confidence < 0.6:
            unsupported.append(f"{artifact.relative_path}: extraction confidence {artifact.confidence:.2f}")
    return {
        "app_name": request.get("app_name"),
        "requested_target_stack": request.get("target_stack"),
        "requested_delivery_mode": request.get("delivery_mode"),
        "artifact_count": len(artifacts),
        "signals": by_signal,
        "source_types": by_type,
        "input_buckets": by_bucket,
        "input_folder_model": {
            "raw_data": "Business/source/raw migration evidence.",
            "images": "UI screenshots, mockups, brand, component, and layout references.",
            "videos": "Runtime walkthroughs, click flows, and user journey recordings.",
        },
        "visual_reference_count": by_type.get("image", 0),
        "runtime_video_count": by_type.get("video", 0),
        "raw_data_count": by_bucket.get("raw_data", 0),
        "website_urls": sorted(dict.fromkeys(discovered_urls)),
        "unsupported_or_low_confidence": unsupported,
        "artifacts": [artifact.as_dict() for artifact in artifacts],
    }


def infer_primary_source_type(artifacts: list[InputArtifact], request: dict[str, Any]) -> str:
    if request.get("source_type"):
        return str(request["source_type"])
    priority = ("powerapps", "website", "api", "database", "video", "image", "document", "text", "archive")
    scores: dict[str, float] = {}
    for artifact in artifacts:
        scores[artifact.source_type] = scores.get(artifact.source_type, 0.0) + artifact.confidence
    for source_type in priority:
        if source_type in scores:
            return source_type
    return "unknown"


def collect_reference_urls(artifacts: list[InputArtifact], request: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    request_urls = request.get("reference_urls") or request.get("urls") or []
    if isinstance(request_urls, str):
        urls.append(request_urls)
    elif isinstance(request_urls, list):
        urls.extend(str(item) for item in request_urls)
    for artifact in artifacts:
        urls.extend(artifact.urls)
    return sorted(dict.fromkeys(urls))


def _inspect_powerapps_like(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".msapp":
        return {"subtype": "canvas_app_package", "contains_powerapps_markers": True}
    if path.name.lower().endswith(".pa.yaml"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        screens = _extract_screen_names(content)
        return {
            "subtype": "powerapps_yaml",
            "contains_powerapps_markers": True,
            "screen_names": screens,
            "screen_count": len(screens),
        }
    return {"contains_powerapps_markers": True}


def _load_input_manifests(input_dir: Path) -> dict[str, Any]:
    manifests: dict[str, Any] = {}
    for bucket, candidates in INPUT_MANIFEST_FILES.items():
        for candidate in candidates:
            path = input_dir / bucket / candidate
            if not path.exists():
                continue
            try:
                if path.suffix.lower() == ".json":
                    data = json.loads(path.read_text(encoding="utf-8"))
                else:
                    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                data = {}
            manifests[bucket] = data if isinstance(data, dict) else {"items": data}
            break
    return manifests


def _manifest_entry_for(relative_path: str, manifests: dict[str, Any]) -> dict[str, Any]:
    bucket = _input_bucket(relative_path)
    manifest = manifests.get(bucket, {})
    if not isinstance(manifest, dict):
        return {}
    items = manifest.get("items")
    if items is None:
        if bucket == "images":
            items = manifest.get("images")
        elif bucket == "videos":
            items = manifest.get("videos")
        elif bucket == "raw_data":
            items = manifest.get("raw_data") or manifest.get("files")
    if not isinstance(items, list):
        return {}
    normalized_relative = _normalize_relative_path(relative_path)
    bucket_relative = "/".join(normalized_relative.split("/")[1:])
    for item in items:
        if not isinstance(item, dict):
            continue
        file_value = _normalize_relative_path(str(item.get("file") or item.get("path") or ""))
        if file_value in {normalized_relative, bucket_relative}:
            return item
    return {}


def _input_bucket(relative_path: str) -> str:
    parts = [part.lower() for part in re.split(r"[\\/]+", relative_path) if part]
    if not parts:
        return "root"
    first = parts[0]
    if first in {"raw", "raw_data", "source", "sources", "data", "documents", "docs", "exports"}:
        return "raw_data"
    if first in {"image", "images", "visual", "visuals", "screenshots", "screenshot", "mockups", "ui"}:
        return "images"
    if first in {"video", "videos", "recordings", "runtime", "walkthroughs"}:
        return "videos"
    return "root"


def _input_lane(input_bucket: str) -> str:
    return {
        "raw_data": "source_evidence",
        "images": "visual_reference",
        "videos": "runtime_behavior",
    }.get(input_bucket, "general_input")


def _visual_reference_purpose(relative_path: str, lower_name: str) -> str:
    text = f"{relative_path.lower()} {lower_name}"
    if any(token in text for token in ("brand", "logo", "color", "palette", "font", "typography")):
        return "brand_reference"
    if any(token in text for token in ("component", "card", "table", "grid", "form", "button", "navbar", "sidebar")):
        return "component_reference"
    if any(token in text for token in ("mockup", "wireframe", "figma", "design")):
        return "ui_mockup_reference"
    if any(token in text for token in ("exact", "target", "must-match", "match")):
        return "exact_ui_reference"
    if any(token in text for token in ("screenshot", "current", "source", "legacy", "runtime")):
        return "screenshot_evidence"
    if _input_bucket(relative_path) == "images":
        return "ui_reference"
    return "visual_evidence"


def _video_reference_purpose(relative_path: str, lower_name: str) -> str:
    text = f"{relative_path.lower()} {lower_name}"
    if any(token in text for token in ("click", "flow", "journey", "walkthrough", "runtime", "recording")):
        return "runtime_walkthrough"
    if any(token in text for token in ("bug", "issue", "error", "failure")):
        return "defect_evidence"
    if any(token in text for token in ("demo", "happy", "success")):
        return "happy_path_demo"
    return "video_reference"


def _screen_hint_from_path(relative_path: str) -> str:
    stem = Path(relative_path).stem
    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    return " ".join(word.capitalize() for word in cleaned.split()) if cleaned else ""


def _reference_priority(relative_path: str) -> str:
    lowered = relative_path.lower()
    if any(token in lowered for token in ("high", "exact", "target", "must")):
        return "high"
    if any(token in lowered for token in ("low", "optional", "nice")):
        return "low"
    return "medium"


def _normalize_relative_path(path: str) -> str:
    return "/".join(part for part in re.split(r"[\\/]+", path.strip()) if part)


def _inspect_zip_file(path: Path) -> dict[str, Any]:
    details: dict[str, Any] = {
        "entry_count": 0,
        "sample_entries": [],
        "contains_powerapps_markers": False,
        "contains_office_package_markers": False,
        "contains_images": False,
    }
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.namelist()
    except zipfile.BadZipFile:
        return details
    lowered = [entry.lower() for entry in entries]
    details["entry_count"] = len(entries)
    details["sample_entries"] = entries[:15]
    details["contains_powerapps_markers"] = any(
        marker in entry for entry in lowered for marker in ("src/", ".pa.yaml", "canvasmanifest", "controls/", "powerapps")
    )
    details["contains_office_package_markers"] = any(entry.startswith("word/") or entry.startswith("ppt/") or entry.startswith("xl/") for entry in lowered)
    details["contains_images"] = any(Path(entry).suffix.lower() in IMAGE_EXTENSIONS for entry in entries)
    details["managed_solution_hint"] = any("solution.xml" in entry for entry in lowered)
    return details


def _inspect_structured_file(path: Path) -> dict[str, Any]:
    raw_text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(raw_text)
        else:
            data = yaml.safe_load(raw_text)
    except Exception:
        return {
            "source_type": "structured",
            "signal": "structured_file_present",
            "confidence": 0.5,
            "summary": "Structured file detected but parsing failed.",
        }
    summary = "Structured file detected."
    source_type = "structured"
    signal = "structured_file_present"
    confidence = 0.7
    urls = _find_urls_in_object(data)
    top_level_keys: list[str] = []
    if isinstance(data, dict):
        top_level_keys = [str(key) for key in list(data.keys())[:20]]
        lowered = {key.lower() for key in top_level_keys}
        if {"openapi", "paths"} & lowered or "swagger" in lowered:
            source_type = "api"
            signal = "openapi_present"
            confidence = 0.9
            summary = "OpenAPI or Swagger specification detected."
        elif {"screens", "app", "formulas"} & lowered:
            source_type = "powerapps"
            signal = "powerapps_export_present"
            confidence = 0.72
            summary = "Power Apps-like structured metadata detected."
        elif {"entities", "tables", "columns"} & lowered:
            source_type = "database"
            signal = "data_input_present"
            confidence = 0.76
            summary = "Data model metadata detected."
    return {
        "source_type": source_type,
        "signal": signal,
        "confidence": confidence,
        "summary": summary,
        "top_level_keys": top_level_keys,
        "urls": urls,
    }


def _inspect_xml_file(path: Path) -> dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
        root_tag = root.tag
        child_tags = [child.tag for child in list(root)[:20]]
    except ET.ParseError:
        return {
            "source_type": "xml",
            "signal": "xml_present",
            "confidence": 0.5,
            "summary": "XML file detected but parsing failed.",
        }
    lowered = root_tag.lower()
    if "workflow" in lowered or "process" in lowered:
        source_type = "workflow_xml"
        signal = "workflow_xml_present"
        summary = "Workflow XML detected."
        confidence = 0.78
    elif "solution" in lowered or "powerapps" in lowered:
        source_type = "powerapps"
        signal = "powerapps_export_present"
        summary = "Power Platform XML metadata detected."
        confidence = 0.74
    else:
        source_type = "xml"
        signal = "xml_present"
        summary = "XML input detected."
        confidence = 0.65
    return {
        "source_type": source_type,
        "signal": signal,
        "confidence": confidence,
        "summary": summary,
        "root_tag": root_tag,
        "child_tags": child_tags,
    }


def _inspect_table_file(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".csv", ".tsv"}:
        delimiter = "," if path.suffix.lower() == ".csv" else "\t"
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            rows = list(reader)
        headers = rows[0] if rows else []
        return {
            "source_type": "tabular",
            "signal": "data_input_present",
            "confidence": 0.74,
            "summary": "Delimited data file detected.",
            "column_count": len(headers),
            "columns": headers[:25],
            "row_count_estimate": max(len(rows) - 1, 0),
        }
    return {
        "source_type": "spreadsheet",
        "signal": "data_input_present",
        "confidence": 0.6,
        "summary": "Spreadsheet input detected.",
    }


def _inspect_sql_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    tables = re.findall(r"create\s+table\s+([a-zA-Z0-9_\.]+)", text, flags=re.IGNORECASE)
    return {
        "table_names": tables[:50],
        "table_count": len(tables),
        "summary": "SQL schema or migration script detected.",
    }


def _inspect_document_file(path: Path) -> dict[str, Any]:
    details: dict[str, Any] = {
        "source_type": "document",
        "signal": "document_present",
        "confidence": 0.62,
        "summary": "Business or design document detected.",
        "urls": [],
    }
    if path.suffix.lower() in {".docx", ".pptx"}:
        zip_details = _inspect_zip_file(path)
        details.update(zip_details)
        if zip_details.get("contains_images"):
            details["summary"] = "Office document detected with embedded media."
    return details


def _inspect_text_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    urls = sorted(dict.fromkeys(URL_RE.findall(text)))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    preview = " ".join(lines[:3])[:240]
    return {
        "line_count": len(lines),
        "preview": preview,
        "urls": urls,
        "summary": "Text notes or requirements detected." if lines else "Text input detected.",
    }


def _extract_screen_names(text: str) -> list[str]:
    names = re.findall(r"([A-Za-z0-9_ -]+)\s+As\s+screen", text, flags=re.IGNORECASE)
    if not names:
        names = re.findall(r"screen[_ -]?([A-Za-z0-9_ -]+)", text, flags=re.IGNORECASE)
    return [name.strip() for name in names[:50]]


def _parse_key_value_text(text: str) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key:
            parsed[key] = value
    return parsed


def _find_urls_in_object(value: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(value, dict):
        for item in value.values():
            urls.extend(_find_urls_in_object(item))
    elif isinstance(value, list):
        for item in value:
            urls.extend(_find_urls_in_object(item))
    elif isinstance(value, str):
        urls.extend(URL_RE.findall(value))
    return sorted(dict.fromkeys(urls))


def domain_from_urls(urls: list[str]) -> list[str]:
    domains: list[str] = []
    for url in urls:
        parsed = urlparse(url)
        if parsed.netloc:
            domains.append(parsed.netloc)
    return sorted(dict.fromkeys(domains))
