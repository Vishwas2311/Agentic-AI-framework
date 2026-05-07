from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_DIR_NAME = ".genesis_runtime"


def initialize_runtime_session(
    root: Path,
    workspace: Path,
    input_dir: Path,
    app_name: str,
    command: str,
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = dict(existing or {})
    created_at = session.get("created_at", _utc_now())
    session_id = session.get("session_id") or _build_session_id(workspace, input_dir, app_name)
    session.update(
        {
            "schema_version": "3.1.0",
            "framework": "NoCode2ProCode by TrustEngines",
            "session_id": session_id,
            "app_name": app_name,
            "workspace": str(workspace),
            "input_dir": str(input_dir),
            "status": "running",
            "created_at": created_at,
            "updated_at": _utc_now(),
            "last_command": command,
            "commands_run": sorted({*session.get("commands_run", []), command}),
            "completed_stages": session.get("completed_stages", []),
            "last_completed_stage": session.get("last_completed_stage"),
        }
    )
    write_runtime_session(root, workspace, session)
    append_session_event(workspace, {"type": "session_started", "command": command, "status": "running"})
    return session


def update_runtime_session(
    root: Path,
    workspace: Path,
    session: dict[str, Any],
    stage_name: str,
    stage_result: dict[str, Any],
) -> dict[str, Any]:
    completed = list(session.get("completed_stages", []))
    if stage_name not in completed:
        completed.append(stage_name)
    session.update(
        {
            "updated_at": _utc_now(),
            "last_completed_stage": stage_name,
            "completed_stages": completed,
            "completed_stage_count": len(completed),
        }
    )
    write_runtime_session(root, workspace, session)
    append_session_event(
        workspace,
        {
            "type": "stage_completed",
            "stage": stage_name,
            "status": "completed",
            "result": stage_result,
        },
    )
    return session


def finalize_runtime_session(
    root: Path,
    workspace: Path,
    session: dict[str, Any],
    approval_status: str,
    approval_required: bool,
) -> dict[str, Any]:
    session.update(
        {
            "updated_at": _utc_now(),
            "status": "awaiting_human_review" if approval_required else "completed",
            "approval_status": approval_status,
            "approval_required": approval_required,
        }
    )
    write_runtime_session(root, workspace, session)
    append_session_event(
        workspace,
        {
            "type": "session_finished",
            "status": session["status"],
            "approval_status": approval_status,
            "approval_required": approval_required,
        },
    )
    return session


def write_runtime_session(root: Path, workspace: Path, session: dict[str, Any]) -> None:
    path = workspace / "runtime_session.json"
    path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    registry = _load_registry(root)
    records = [item for item in registry.get("sessions", []) if item.get("session_id") != session.get("session_id")]
    records.append(
        {
            "session_id": session.get("session_id"),
            "app_name": session.get("app_name"),
            "workspace": session.get("workspace"),
            "input_dir": session.get("input_dir"),
            "status": session.get("status"),
            "approval_status": session.get("approval_status"),
            "last_completed_stage": session.get("last_completed_stage"),
            "updated_at": session.get("updated_at"),
        }
    )
    registry["sessions"] = sorted(records, key=lambda item: item.get("updated_at", ""), reverse=True)
    _write_registry(root, registry)


def list_runtime_sessions(root: Path) -> list[dict[str, Any]]:
    return _load_registry(root).get("sessions", [])


def read_runtime_session(workspace: Path) -> dict[str, Any]:
    path = workspace / "runtime_session.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def append_session_event(workspace: Path, event: dict[str, Any]) -> None:
    payload = {"timestamp": _utc_now(), **event}
    path = workspace / "session_events.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _load_registry(root: Path) -> dict[str, Any]:
    path = _registry_path(root)
    if not path.exists():
        return {"schema_version": "3.1.0", "sessions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_registry(root: Path, registry: dict[str, Any]) -> None:
    path = _registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def _registry_path(root: Path) -> Path:
    return root / RUNTIME_DIR_NAME / "session_registry.json"


def _build_session_id(workspace: Path, input_dir: Path, app_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", app_name.lower()).strip("-") or "migration"
    fingerprint = hashlib.sha1(f"{workspace}|{input_dir}|{app_name}".encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{fingerprint}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
