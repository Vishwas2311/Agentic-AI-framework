from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported


class PowerAppsAdapter(SourceAdapter):
    source_type = "powerapps"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        path = Path(source)
        output_dir.mkdir(parents=True, exist_ok=True)
        inventory = inspect_powerapps_source(path)
        confidence = 0.45
        unsupported_items: list[dict[str, Any]] = []

        if inventory["source_mode"] == "directory_src":
            confidence = 0.78
        elif inventory["contains_powerapps_markers"]:
            confidence = 0.68
        else:
            unsupported_items.append(unsupported("No recognizable Power Apps markers were found.", "powerapps"))

        if inventory["managed_solution_hint"]:
            unsupported_items.append(
                unsupported("Managed-solution fidelity may be limited; runtime evidence is recommended.", "managed_solution")
            )

        if not inventory["screen_names"]:
            unsupported_items.append(unsupported("No screen names were extracted from source files yet.", "screen_inventory"))

        return AdapterResult(
            source_type=self.source_type,
            confidence=confidence,
            ast={
                "source": str(path),
                "adapter": "powerapps",
                "mode": inventory["source_mode"],
                "screen_names": inventory["screen_names"],
                "screen_count": len(inventory["screen_names"]),
                "source_files": inventory["source_files"],
                "formula_file_count": inventory["formula_file_count"],
                "connector_hints": inventory["connector_hints"],
                "data_source_hints": inventory["data_source_hints"],
                "entry_count": inventory["entry_count"],
                "managed_solution_hint": inventory["managed_solution_hint"],
            },
            unsupported_items=unsupported_items,
            evidence_refs=[str(path)],
        )


def inspect_powerapps_source(path: Path) -> dict[str, Any]:
    details = {
        "source_mode": "unknown",
        "entry_count": 0,
        "source_files": [],
        "screen_names": [],
        "formula_file_count": 0,
        "connector_hints": [],
        "data_source_hints": [],
        "contains_powerapps_markers": False,
        "managed_solution_hint": False,
    }
    if not path.exists():
        return details
    if path.is_dir():
        src_files = list(path.rglob("*.pa.yaml"))
        details["source_mode"] = "directory_src"
        details["entry_count"] = len(list(path.rglob("*")))
        details["source_files"] = [str(item.relative_to(path)) for item in src_files[:100]]
        details["formula_file_count"] = len(src_files)
        details["screen_names"] = _screen_names_from_files(src_files)
        details["connector_hints"] = _search_directory(path, ("connector", "customconnector", "connectionreference"))
        details["data_source_hints"] = _search_directory(path, ("sharepoint", "dataverse", "sql", "excel", "onedrive"))
        details["contains_powerapps_markers"] = bool(src_files)
        return details

    suffix = path.suffix.lower()
    if suffix == ".msapp" or suffix == ".zip" or path.name.lower().endswith(".app.zip"):
        try:
            with zipfile.ZipFile(path) as archive:
                entries = archive.namelist()
                lowered = [entry.lower() for entry in entries]
                details["entry_count"] = len(entries)
                details["source_mode"] = "archive"
                details["contains_powerapps_markers"] = any(
                    marker in entry for entry in lowered for marker in ("src/", ".pa.yaml", "canvasmanifest", "controltemplates")
                )
                details["managed_solution_hint"] = _managed_hint_from_archive(archive, entries)
                details["source_files"] = [entry for entry in entries if entry.lower().endswith(".pa.yaml")][:100]
                details["formula_file_count"] = len(details["source_files"])
                details["screen_names"] = _screen_names_from_archive(archive, details["source_files"])
                details["connector_hints"] = sorted(
                    {Path(entry).name for entry in entries if "connector" in entry.lower() or "connectionreference" in entry.lower()}
                )[:50]
                details["data_source_hints"] = sorted(
                    {
                        Path(entry).name
                        for entry in entries
                        if any(hint in entry.lower() for hint in ("sharepoint", "dataverse", "sql", "excel", "onedrive"))
                    }
                )[:50]
                return details
        except zipfile.BadZipFile:
            details["source_mode"] = "unreadable_archive"
            return details

    if path.name.lower().endswith(".pa.yaml"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        details["source_mode"] = "pa_yaml"
        details["entry_count"] = 1
        details["source_files"] = [path.name]
        details["formula_file_count"] = 1
        details["screen_names"] = _extract_screen_names(text)
        details["contains_powerapps_markers"] = True
        details["connector_hints"] = _extract_token_hints(text, ("Connector", "ConnectionReference"))
        details["data_source_hints"] = _extract_token_hints(text, ("Dataverse", "SharePoint", "SQL", "Excel", "OneDrive"))
        return details

    return details


def _managed_hint_from_archive(archive: zipfile.ZipFile, entries: list[str]) -> bool:
    solution_files = [entry for entry in entries if entry.lower().endswith("solution.xml")]
    for entry in solution_files[:2]:
        try:
            xml_text = archive.read(entry).decode("utf-8", errors="ignore")
        except KeyError:
            continue
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            continue
        markers = [element.text or "" for element in root.iter() if element.tag.lower().endswith("managed")]
        if any(marker.strip().lower() in {"1", "true", "yes"} for marker in markers):
            return True
    return False


def _screen_names_from_files(files: list[Path]) -> list[str]:
    names: list[str] = []
    for file_path in files[:100]:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        names.extend(_extract_screen_names(text))
    return sorted(dict.fromkeys(names))[:100]


def _screen_names_from_archive(archive: zipfile.ZipFile, files: list[str]) -> list[str]:
    names: list[str] = []
    for entry in files[:100]:
        try:
            text = archive.read(entry).decode("utf-8", errors="ignore")
        except KeyError:
            continue
        names.extend(_extract_screen_names(text))
    return sorted(dict.fromkeys(names))[:100]


def _extract_screen_names(text: str) -> list[str]:
    matches = re.findall(r"([A-Za-z0-9_ -]+)\s+As\s+screen", text, flags=re.IGNORECASE)
    if not matches:
        try:
            data = yaml.safe_load(text) or {}
        except Exception:
            data = {}
        if isinstance(data, dict):
            candidates = data.get("Screens") or data.get("screens") or []
            if isinstance(candidates, list):
                matches = [str(item.get("Name") or item.get("name")) for item in candidates if isinstance(item, dict)]
    return [match.strip() for match in matches if str(match).strip()]


def _search_directory(root: Path, hints: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        lower_name = file_path.name.lower()
        if any(hint in lower_name for hint in hints):
            matches.append(str(file_path.relative_to(root)))
    return matches[:50]


def _extract_token_hints(text: str, tokens: tuple[str, ...]) -> list[str]:
    hints: list[str] = []
    for token in tokens:
        if token.lower() in text.lower():
            hints.append(token)
    return hints
