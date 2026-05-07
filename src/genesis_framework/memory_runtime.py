from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from genesis_framework.intake import InputArtifact


def build_memory_retrieval_plan(
    root: Path,
    memory_config: dict[str, Any],
    request: dict[str, Any],
    artifacts: list[InputArtifact],
) -> dict[str, Any]:
    store = _memory_store_path(root)
    source_types = sorted({artifact.source_type for artifact in artifacts})
    plan = {
        "schema_version": "3.1.0",
        "stores": memory_config.get("stores", {}),
        "query": {
            "domain": request.get("domain"),
            "source_types": source_types,
            "target_stack": request.get("target_stack"),
        },
        "available_memory_packets": 0,
        "matched_memory_packets": [],
    }
    if not store.exists():
        return plan
    packets = _load_packets(store)
    matched = [
        packet
        for packet in packets
        if _matches_query(packet, request.get("domain"), source_types, request.get("target_stack"))
    ]
    plan["available_memory_packets"] = len(packets)
    plan["matched_memory_packets"] = matched[:10]
    return plan


def build_verified_memory_packet(
    memory_config: dict[str, Any],
    request: dict[str, Any],
    artifacts: list[InputArtifact],
    canonical_spec: dict[str, Any],
    approval: dict[str, Any],
    quality: dict[str, Any],
) -> dict[str, Any]:
    source_types = sorted({artifact.source_type for artifact in artifacts})
    trust_status = "human_approved" if approval.get("status") == "approved" else "generated_only"
    return {
        "schema_version": "3.1.0",
        "trust_status": trust_status,
        "trust_levels": memory_config.get("trust_levels", {}),
        "app_name": canonical_spec.get("app", {}).get("name") or request.get("app_name"),
        "domain": request.get("domain"),
        "target_stack": canonical_spec.get("target_stack") or request.get("target_stack"),
        "source_types": source_types,
        "screen_count": len(canonical_spec.get("screens", [])),
        "workflow_count": len(canonical_spec.get("workflows", [])),
        "entity_count": len(canonical_spec.get("entities", [])),
        "quality_score": quality.get("overall_design_quality_score"),
        "save_categories": memory_config.get("save", []),
        "reuse_hints": [
            "reuse canonical spec patterns for similar domains",
            "reuse data model naming when confidence is high",
            "warn on generated-only packets before automatic reuse",
        ],
    }


def append_verified_memory_packet(root: Path, packet: dict[str, Any]) -> None:
    path = _memory_store_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(packet) + "\n")


def build_memory_context_summary(retrieval_plan: dict[str, Any]) -> dict[str, Any]:
    matches = retrieval_plan.get("matched_memory_packets", [])
    return {
        "schema_version": "3.1.0",
        "match_count": len(matches),
        "top_reuse_targets": [
            {
                "app_name": item.get("app_name"),
                "domain": item.get("domain"),
                "target_stack": item.get("target_stack"),
                "trust_status": item.get("trust_status"),
            }
            for item in matches[:5]
        ],
        "reuse_policy": "Prefer human_approved and test_passed packets before generated_only packets.",
    }


def _memory_store_path(root: Path) -> Path:
    return root / "memory" / "verified_memory_packets.jsonl"


def _load_packets(path: Path) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        packets.append(json.loads(text))
    return packets


def _matches_query(packet: dict[str, Any], domain: Any, source_types: list[str], target_stack: Any) -> bool:
    packet_sources = packet.get("source_types", [])
    domain_match = not domain or packet.get("domain") == domain
    stack_match = not target_stack or packet.get("target_stack") == target_stack
    source_match = not source_types or bool(set(packet_sources) & set(source_types))
    return domain_match and stack_match and source_match
