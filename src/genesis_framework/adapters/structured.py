from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported
from genesis_framework.analyzers.brd import analyze_brd_text


class ApiSpecAdapter(SourceAdapter):
    source_type = "api"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        path = Path(source)
        data = _load_structured(path)
        paths = data.get("paths", {}) if isinstance(data, dict) else {}
        endpoints: list[dict[str, Any]] = []
        for route, methods in list(paths.items())[:100]:
            if isinstance(methods, dict):
                for method, operation in methods.items():
                    if isinstance(operation, dict):
                        endpoints.append(
                            {
                                "path": route,
                                "method": method.upper(),
                                "operation_id": operation.get("operationId"),
                                "summary": operation.get("summary"),
                            }
                        )
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.88 if endpoints else 0.65,
            ast={
                "source": str(path),
                "adapter": "api_spec",
                "title": data.get("info", {}).get("title") if isinstance(data, dict) else None,
                "version": data.get("info", {}).get("version") if isinstance(data, dict) else None,
                "endpoints": endpoints,
            },
            unsupported_items=[] if endpoints else [unsupported("Could not detect concrete API paths from the specification.", "api_paths")],
            evidence_refs=[str(path)],
        )


class DatabaseSchemaAdapter(SourceAdapter):
    source_type = "database"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix == ".sql":
            text = path.read_text(encoding="utf-8", errors="ignore")
            entities = _parse_sql_entities(text, path.stem)
        elif suffix in {".csv", ".tsv"}:
            headers = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0].split("," if suffix == ".csv" else "\t")
            entities = [{"name": path.stem.replace("_", " ").title(), "columns": headers, "source": str(path)}]
        else:
            entities = [{"name": path.stem.replace("_", " ").title(), "columns": [], "source": str(path)}]
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.82 if entities else 0.55,
            ast={"source": str(path), "adapter": "database_schema", "entities": entities},
            unsupported_items=[] if entities else [unsupported("No database entities were detected.", "db_entities")],
            evidence_refs=[str(path)],
        )


class XmlWorkflowAdapter(SourceAdapter):
    source_type = "xml"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        path = Path(source)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            return AdapterResult(
                source_type=self.source_type,
                confidence=0.4,
                ast={"source": str(path), "adapter": "xml_workflow", "root_tag": None, "workflow_steps": []},
                unsupported_items=[unsupported("XML parsing failed.", "xml_parse")],
                evidence_refs=[str(path)],
            )
        workflow_steps = []
        for element in list(root.iter())[:200]:
            tag = element.tag.split("}")[-1]
            text = (element.text or "").strip()
            if any(token in tag.lower() for token in ("step", "task", "activity", "action", "stage")):
                workflow_steps.append({"tag": tag, "name": text or element.attrib.get("name") or tag})
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.76 if workflow_steps else 0.62,
            ast={
                "source": str(path),
                "adapter": "xml_workflow",
                "root_tag": root.tag.split("}")[-1],
                "workflow_steps": workflow_steps[:100],
                "child_tags": [child.tag.split("}")[-1] for child in list(root)[:40]],
            },
            unsupported_items=[] if workflow_steps else [unsupported("XML structure was parsed but workflow semantics remain uncertain.", "workflow_semantics")],
            evidence_refs=[str(path)],
        )


class DocumentIntentAdapter(SourceAdapter):
    source_type = "document"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        path = Path(source)
        text = ""
        if path.suffix.lower() in {".txt", ".md", ".rst"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif path.suffix.lower() == ".docx":
            text = _extract_docx_text(path)
        elif path.suffix.lower() == ".pptx":
            text = _extract_pptx_text(path)
        analysis = analyze_brd_text(text, source_name=path.name) if text.strip() else {}
        sentences = analysis.get("summary_sentences", [])
        urls = re.findall(r"https?://[^\s)>\]\"']+", text)
        return AdapterResult(
            source_type=self.source_type,
            confidence=float(analysis.get("confidence", 0.72 if sentences else 0.55)),
            ast={
                "source": str(path),
                "adapter": "document_intent",
                "summary_sentences": sentences[:20],
                "urls": urls[:20],
                "keywords": analysis.get("keywords", _keywords_from_text(text)),
                "functional_requirements": analysis.get("functional_requirements", []),
                "acceptance_criteria": analysis.get("acceptance_criteria", []),
                "screen_candidates": analysis.get("screen_candidates", []),
                "workflow_candidates": analysis.get("workflow_candidates", []),
                "user_roles": analysis.get("user_roles", []),
                "entities": analysis.get("entities", []),
                "document_type": analysis.get("document_type", "document"),
            },
            unsupported_items=[],
            evidence_refs=[str(path)],
        )


def _load_structured(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def _parse_sql_entities(text: str, fallback_name: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    matches = list(re.finditer(r"create\s+table\s+([a-zA-Z0-9_\.]+)\s*\((.*?)\);", text, flags=re.IGNORECASE | re.DOTALL))
    for match in matches[:50]:
        table_name = match.group(1).split(".")[-1]
        body = match.group(2)
        columns = []
        for line in body.splitlines():
            stripped = line.strip().strip(",")
            if not stripped or stripped.lower().startswith(("primary key", "constraint", "foreign key")):
                continue
            column_name = stripped.split()[0]
            columns.append(column_name)
        entities.append({"name": table_name, "columns": columns, "source": fallback_name})
    if not entities:
        entities.append({"name": fallback_name.replace("_", " ").title(), "columns": [], "source": fallback_name})
    return entities


def _keywords_from_text(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _count in ranked[:20]]


def _extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    except (KeyError, zipfile.BadZipFile, OSError):
        return ""
    parts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml)
    return " ".join(part.strip() for part in parts if part.strip())


def _extract_pptx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = [name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
            chunks = []
            for name in slide_names[:20]:
                xml = archive.read(name).decode("utf-8", errors="ignore")
                chunks.extend(re.findall(r"<a:t>(.*?)</a:t>", xml))
    except (zipfile.BadZipFile, OSError):
        return ""
    return " ".join(part.strip() for part in chunks if part.strip())
