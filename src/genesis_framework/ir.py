from __future__ import annotations

from typing import Any


def empty_ulc_ir(schema_version: str = "3.1.0") -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "domain_ir": {"entities": [], "relationships": [], "enums": [], "constraints": []},
        "workflow_ir": {"workflows": [], "timers": [], "approvals": [], "async_jobs": [], "business_rules": []},
        "ui_ir": {"screens": [], "ui_components": [], "navigation": [], "responsive_rules": [], "a11y_requirements": []},
        "integration_ir": {"api_contracts": [], "data_sources": [], "connectors": [], "mocks": []},
        "security_ir": {"roles": [], "permissions": [], "row_level_rules": [], "auth_flows": []},
        "design_ir": {"design_tokens": {}, "visual_layout_tree": [], "component_registry": [], "design_source_map": []},
        "deployment_ir": {"deployment_topology": {}, "container_specs": [], "env_config": {}, "infrastructure_requirements": []},
        "unsupported_items": [],
    }

