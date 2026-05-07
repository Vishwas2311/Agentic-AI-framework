from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from genesis_framework.generators.scaffold import TemplateScaffoldGenerator


REPAIR_CORE_FILES = [
    "frontend/package.json",
    "frontend/app/page.tsx",
    "backend/app/main.py",
    "database/migration.sql",
    "tests/api/test_health.py",
    "tests/playwright/smoke.spec.ts",
]

JSON_FILES_TO_VALIDATE = [
    "frontend/package.json",
    "generated_file_manifest.json",
]


@dataclass(frozen=True)
class RepairAction:
    action: str
    status: str
    details: str
    files_touched: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_preflight_repair(
    workspace: Path,
    canonical_spec: dict[str, Any],
    scaffold_generator: TemplateScaffoldGenerator,
    patch_instructions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actions: list[RepairAction] = []
    missing_files = [item for item in REPAIR_CORE_FILES if not (workspace / item).exists()]
    invalid_json = _invalid_json_files(workspace)
    human_instructions = (patch_instructions or {}).get("instructions", [])
    missing_from_gate = [
        item
        for instruction in human_instructions
        if instruction.get("type") == "missing_expected_files"
        for item in instruction.get("items", [])
    ]
    regeneration_needed = bool(missing_files or invalid_json or missing_from_gate)
    regenerated_files: list[str] = []

    if regeneration_needed:
        generated = scaffold_generator.generate(canonical_spec, workspace)
        regenerated_files = sorted(str(path.relative_to(workspace)) for path in generated)
        (workspace / "generated_file_manifest.json").write_text(
            json.dumps({"schema_version": "3.1.0", "files": regenerated_files}, indent=2),
            encoding="utf-8",
        )
        actions.append(
            RepairAction(
                action="regenerate_scaffold",
                status="applied",
                details="Regenerated baseline scaffold files because required outputs were missing or malformed.",
                files_touched=regenerated_files,
            )
        )
    else:
        actions.append(
            RepairAction(
                action="preflight_structural_check",
                status="no_change",
                details="Core generated scaffold files were already present and structurally valid.",
                files_touched=[],
            )
        )
    for instruction in human_instructions:
        if instruction.get("type") == "missing_expected_files":
            continue
        actions.append(
            RepairAction(
                action=str(instruction.get("type", "human_patch_instruction")),
                status="queued_for_scoped_repair",
                details=str(instruction.get("instruction", "Human supplied generated-app review feedback.")),
                files_touched=[],
            )
        )
    human_patch_doc = _write_human_patch_doc(workspace, patch_instructions or {}) if human_instructions else None
    if human_patch_doc:
        actions.append(
            RepairAction(
                action="write_human_patch_requests",
                status="applied",
                details="Wrote structured human generated-app feedback for downstream repair/build agents.",
                files_touched=[str(human_patch_doc.relative_to(workspace))],
            )
        )

    return {
        "schema_version": "3.1.0",
        "repair_iterations_used": 1 if regeneration_needed else 0,
        "repairs_applied": regeneration_needed or bool(human_instructions),
        "missing_files": missing_files,
        "missing_files_from_gate": missing_from_gate,
        "invalid_json_files": invalid_json,
        "generated_app_patch_instruction_status": (patch_instructions or {}).get("status", "not_provided"),
        "human_instruction_count": len(human_instructions),
        "semantic_action_count": len((patch_instructions or {}).get("semantic_patch", {}).get("actions", [])),
        "actions": [action.as_dict() for action in actions],
        "files_touched": regenerated_files + ([str(human_patch_doc.relative_to(workspace))] if human_patch_doc else []),
    }


def _invalid_json_files(workspace: Path) -> list[str]:
    invalid: list[str] = []
    for relative_path in JSON_FILES_TO_VALIDATE:
        path = workspace / relative_path
        if not path.exists():
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            invalid.append(relative_path)
    return invalid


def _write_human_patch_doc(workspace: Path, patch_instructions: dict[str, Any]) -> Path:
    docs_dir = workspace / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    path = docs_dir / "HUMAN_PATCH_REQUESTS.md"
    instructions = patch_instructions.get("instructions", [])
    semantic_actions = patch_instructions.get("semantic_patch", {}).get("actions", [])
    lines = [
        "# Human Patch Requests",
        "",
        "These instructions were captured at the Generated App Approval Gate.",
        "The pipeline order is unchanged; repair/build agents should use this file as scoped input.",
        "",
        "## Patch Instructions",
        "",
    ]
    if instructions:
        for index, instruction in enumerate(instructions, start=1):
            lines.extend(
                [
                    f"{index}. **{instruction.get('type', 'instruction')}**",
                    f"   - Priority: {instruction.get('priority', 'normal')}",
                    f"   - Instruction: {instruction.get('instruction', '')}",
                    "",
                ]
            )
    else:
        lines.append("- No human patch instructions captured.")
    lines.extend(["", "## Semantic Actions", ""])
    if semantic_actions:
        for action in semantic_actions:
            lines.append(f"- {action.get('operation')} `{action.get('target')}`: {action.get('text')}")
    else:
        lines.append("- No semantic actions parsed.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
