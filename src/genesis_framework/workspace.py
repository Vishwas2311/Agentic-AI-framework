from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DIRS = [
    "generated_app",
    "backend",
    "frontend",
    "database",
    "tests",
    "assets",
    "docs",
    "deploy",
    "observability",
    "sbom",
    "ulc_ir",
    "design_ir",
    "evidence",
    "runtime",
    "runtime_recording",
    "integration_contracts",
]


def create_migration_workspace(root: Path, app_name: str) -> Path:
    slug = app_name.lower().replace(" ", "_").replace("-", "_")
    workspace = root / "genesis_apps" / f"{slug}_migrated"
    ensure_workspace_layout(workspace, app_name)
    return workspace


def ensure_workspace_layout(workspace: Path, app_name: str) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    for directory in DEFAULT_DIRS:
        (workspace / directory).mkdir(parents=True, exist_ok=True)

    manifest = {
        "app_name": app_name,
        "workspace": str(workspace),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "framework": "NoCode2ProCode by TrustEngines",
        "schema_version": "3.1.0",
        "status": "initialized",
    }
    (workspace / "migration_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return workspace
