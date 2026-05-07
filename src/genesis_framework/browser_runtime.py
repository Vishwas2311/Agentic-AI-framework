from __future__ import annotations

from typing import Any

from genesis_framework.intake import InputArtifact, collect_reference_urls


def build_browser_runtime_plan(
    artifacts: list[InputArtifact],
    request: dict[str, Any],
    routing_config: dict[str, Any],
) -> dict[str, Any]:
    urls = collect_reference_urls(artifacts, request)
    source_routing = routing_config.get("source_routing", {})
    website_route = source_routing.get("website_url_present", {})
    preferred_tools = website_route.get("tools", ["playwright", "firecrawl"])
    roles = _coerce_list(request.get("roles")) or ["default_user"]
    operations = [
        "map entry pages",
        "capture DOM snapshots",
        "record navigation paths",
        "capture screenshots at key states",
        "save network traces for important flows",
    ]
    if request.get("requires_authenticated_runtime"):
        operations.insert(0, "establish authenticated browser session")
    return {
        "schema_version": "3.1.0",
        "status": "planned" if urls else "not_applicable",
        "target_urls": urls,
        "preferred_tools": preferred_tools,
        "roles_to_capture": roles,
        "operations": operations,
        "browser_protocol": {
            "provider_contract": [
                "session_start",
                "page_open",
                "page_snapshot",
                "network_trace",
                "form_interaction",
                "screenshot_capture",
            ],
            "notes": [
                "This normalizes runtime capture so Playwright, Firecrawl, or future providers can plug into the same pipeline stage.",
                "Use runtime capture to close gaps that export files cannot reveal.",
            ],
        },
    }


def build_runtime_capture_contract(
    artifacts: list[InputArtifact],
    request: dict[str, Any],
    source_truth: dict[str, Any],
) -> dict[str, Any]:
    urls = collect_reference_urls(artifacts, request)
    decisions = source_truth.get("decisions", [])
    review_items = [item for item in decisions if item.get("requires_human_review")]
    return {
        "schema_version": "3.1.0",
        "capture_priority": "high" if urls or review_items else "medium",
        "critical_flows": _coerce_list(request.get("critical_flows"))
        or ["login", "primary navigation", "core create/update workflow"],
        "required_artifacts": [
            "screenshots",
            "navigation map",
            "network trace",
            "role-aware capture",
        ],
        "review_sensitive_areas": [item.get("artifact_id") for item in review_items],
        "runtime_roles": _coerce_list(request.get("roles")) or ["default_user"],
    }


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]
