from __future__ import annotations

import re
from collections import Counter
from typing import Any


ROLE_PATTERNS = (
    "admin",
    "manager",
    "employee",
    "approver",
    "reviewer",
    "patient",
    "doctor",
    "customer",
    "user",
    "agent",
)

SCREEN_HINT_WORDS = (
    "screen",
    "page",
    "dashboard",
    "form",
    "portal",
    "queue",
    "settings",
    "login",
)

WORKFLOW_VERBS = (
    "submit",
    "approve",
    "reject",
    "create",
    "update",
    "delete",
    "assign",
    "notify",
    "review",
    "login",
    "upload",
    "search",
)


def analyze_brd_text(text: str, source_name: str = "") -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized = "\n".join(lines)
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", normalized) if segment.strip()]
    keywords = _keywords(normalized)
    functional_requirements = _functional_requirements(lines)
    acceptance_criteria = _acceptance_criteria(lines)
    screen_candidates = _screen_candidates(lines)
    workflow_candidates = _workflow_candidates(lines)
    roles = _roles(lines)
    entities = _entities(lines)
    doc_type = _document_type(source_name, normalized)
    confidence = 0.52
    if functional_requirements:
        confidence += 0.12
    if screen_candidates:
        confidence += 0.08
    if workflow_candidates:
        confidence += 0.08
    if roles:
        confidence += 0.05
    if acceptance_criteria:
        confidence += 0.05
    confidence = round(min(confidence, 0.9), 4)
    return {
        "document_type": doc_type,
        "summary_sentences": sentences[:12],
        "functional_requirements": functional_requirements[:25],
        "acceptance_criteria": acceptance_criteria[:25],
        "screen_candidates": screen_candidates[:20],
        "workflow_candidates": workflow_candidates[:20],
        "user_roles": roles[:20],
        "entities": entities[:20],
        "keywords": keywords[:25],
        "confidence": confidence,
    }


def merge_brd_analyses(analyses: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "summary_sentences": [],
        "functional_requirements": [],
        "acceptance_criteria": [],
        "screen_candidates": [],
        "workflow_candidates": [],
        "user_roles": [],
        "entities": [],
        "keywords": [],
        "document_types": [],
    }
    for analysis in analyses:
        merged["document_types"].append(analysis.get("document_type"))
        for key in (
            "summary_sentences",
            "functional_requirements",
            "acceptance_criteria",
            "screen_candidates",
            "workflow_candidates",
            "user_roles",
            "entities",
            "keywords",
        ):
            merged[key].extend(analysis.get(key, []))
    return {
        "document_types": sorted({item for item in merged["document_types"] if item}),
        "summary_sentences": _dedupe(merged["summary_sentences"])[:20],
        "functional_requirements": _dedupe(merged["functional_requirements"])[:40],
        "acceptance_criteria": _dedupe(merged["acceptance_criteria"])[:40],
        "screen_candidates": _dedupe(merged["screen_candidates"])[:30],
        "workflow_candidates": _dedupe(merged["workflow_candidates"])[:30],
        "user_roles": _dedupe(merged["user_roles"])[:20],
        "entities": _dedupe(merged["entities"])[:30],
        "keywords": _dedupe(merged["keywords"])[:40],
        "confidence": round(
            sum(float(analysis.get("confidence", 0.0)) for analysis in analyses) / max(len(analyses), 1),
            4,
        ),
    }


def _functional_requirements(lines: list[str]) -> list[str]:
    matches = []
    for line in lines:
        lowered = line.lower()
        if lowered.startswith(("must ", "should ", "shall ", "system should", "system must", "users can", "user can")):
            matches.append(line)
        elif any(token in lowered for token in WORKFLOW_VERBS) and len(line.split()) >= 4:
            matches.append(line)
    return matches


def _acceptance_criteria(lines: list[str]) -> list[str]:
    items = []
    for line in lines:
        lowered = line.lower()
        if lowered.startswith(("acceptance", "given ", "when ", "then ", "success criteria")):
            items.append(line)
        elif lowered.startswith(("-", "*")) and any(token in lowered for token in ("must", "should", "visible", "allow", "validate")):
            items.append(line.lstrip("-* ").strip())
    return items


def _screen_candidates(lines: list[str]) -> list[str]:
    candidates = []
    for line in lines:
        lowered = line.lower()
        if any(word in lowered for word in SCREEN_HINT_WORDS):
            titleish = re.findall(r"[A-Z][A-Za-z0-9/& -]{2,}", line)
            if titleish:
                candidates.extend(item.strip() for item in titleish)
            else:
                candidates.append(line[:80])
    return candidates


def _workflow_candidates(lines: list[str]) -> list[str]:
    matches = []
    for line in lines:
        lowered = line.lower()
        if any(verb in lowered for verb in WORKFLOW_VERBS):
            matches.append(line)
    return matches


def _roles(lines: list[str]) -> list[str]:
    roles = []
    text = " ".join(lines).lower()
    for role in ROLE_PATTERNS:
        if role in text:
            roles.append(role)
    return roles


def _entities(lines: list[str]) -> list[str]:
    entities = []
    for line in lines:
        for match in re.findall(r"\b(User|Request|Approval|Attachment|Notification|Invoice|Patient|Doctor|Order|Ticket|Audit Log)\b", line):
            entities.append(match)
    return entities


def _document_type(source_name: str, text: str) -> str:
    lowered = f"{source_name}\n{text[:2000]}".lower()
    if "brd" in lowered or "business requirement" in lowered:
        return "brd"
    if "prd" in lowered or "product requirement" in lowered:
        return "prd"
    if "user story" in lowered:
        return "user_story"
    return "document"


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
    counts = Counter(words)
    return [word for word, _ in counts.most_common(25)]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output = []
    for item in items:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(cleaned)
    return output
