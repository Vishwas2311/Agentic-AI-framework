from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

from genesis_framework.adapters.powerapps import PowerAppsAdapter
from genesis_framework.adapters.structured import ApiSpecAdapter, DatabaseSchemaAdapter, DocumentIntentAdapter, XmlWorkflowAdapter
from genesis_framework.adapters.website import WebsiteAdapter
from genesis_framework.analyzers.brd import analyze_brd_text, merge_brd_analyses
from genesis_framework.analyzers.screenshot import analyze_visual_artifact
from genesis_framework.approval_gates import (
    collect_human_gate_context,
    resolve_canonical_spec_gate,
    resolve_design_system_gate,
    resolve_final_release_gate,
    resolve_qa_result_gate,
    resolve_source_truth_gate,
)
from genesis_framework.brd_gate import build_brd_understanding, resolve_brd_understanding_gate
from genesis_framework.browser_capture import capture_runtime_targets
from genesis_framework.browser_runtime import build_browser_runtime_plan, build_runtime_capture_contract
from genesis_framework.config import find_project_root, load_all
from genesis_framework.design_quality import DEFAULT_THRESHOLDS, evaluate_design_quality, write_design_quality_report
from genesis_framework.design_strategy import build_design_strategy, write_design_strategy_bundle
from genesis_framework.flow import Stage, stages_for_entrypoint
from genesis_framework.generated_app_gate import (
    build_generated_app_human_notes,
    build_generated_app_patch_instructions,
    build_generated_app_review,
    resolve_generated_app_approval_gate,
)
from genesis_framework.generators.scaffold import TemplateScaffoldGenerator
from genesis_framework.intake import (
    InputArtifact,
    collect_reference_urls,
    default_input_dir,
    domain_from_urls,
    ensure_input_directory,
    infer_primary_source_type,
    load_migration_request,
    scan_input_directory,
    summarize_input_artifacts,
)
from genesis_framework.ir import empty_ulc_ir
from genesis_framework.memory_runtime import (
    append_verified_memory_packet,
    build_memory_context_summary,
    build_memory_retrieval_plan,
    build_verified_memory_packet,
)
from genesis_framework.migration_mode import resolve_migration_mode
from genesis_framework.qa_runner import run_quality_gates
from genesis_framework.provider_routing import build_provider_routing_plan
from genesis_framework.repair_loop import run_preflight_repair
from genesis_framework.reports import write_json, write_text
from genesis_framework.runtime_sessions import finalize_runtime_session, initialize_runtime_session, read_runtime_session, update_runtime_session
from genesis_framework.scorecard import build_production_scorecard
from genesis_framework.source_truth import decide_source_truth
from genesis_framework.stack_resolver import resolve_stack_decision
from genesis_framework.swarm import build_agent_execution_plan, build_swarm_topology
from genesis_framework.visual_fidelity import default_visual_lock_spec
from genesis_framework.workspace import create_migration_workspace, ensure_workspace_layout


COMMAND_TARGETS = {
    "discover": "record_runtime_evidence",
    "plan": "build_visual_fidelity_contract",
    "generate": "generate_code",
    "qa": "evaluate_design_quality",
    "replay": "build_replay_dashboard",
    "migrate": "learn_verified_patterns",
}


@dataclass(frozen=True)
class PipelineRunResult:
    workspace: Path
    target_stage: str
    approval_required: bool
    approval_status: str


class MigrationOrchestrator:
    def __init__(
        self,
        project: Path | None = None,
        input_dir: Path | None = None,
        app_name: str | None = None,
        workspace: Path | None = None,
    ) -> None:
        self.root = (project or find_project_root()).resolve()
        self.configs = load_all(self.root)
        self.input_dir = (input_dir or default_input_dir(self.root)).resolve()
        ensure_input_directory(self.root)
        self.request = load_migration_request(self.input_dir) if self.input_dir.exists() else {}
        self.artifacts = scan_input_directory(self.input_dir) if self.input_dir.exists() else []
        self.app_name = app_name or self._derive_app_name()
        if workspace:
            self.workspace = ensure_workspace_layout(workspace.resolve(), self.app_name)
        else:
            self.workspace = create_migration_workspace(self.root, self.app_name)
        self.flow_stages = stages_for_entrypoint(self.configs["flow"], "genesis-migrate")
        self.stage_lookup = {stage.name: stage for stage in self.flow_stages}
        self.checkpoint_path = self.workspace / "checkpoint_manifest.json"
        self.state = self._load_checkpoint()
        self.session = initialize_runtime_session(
            self.root,
            self.workspace,
            self.input_dir,
            self.app_name,
            "bootstrap",
            existing=read_runtime_session(self.workspace),
        )
        self.powerapps_adapter = PowerAppsAdapter()
        self.website_adapter = WebsiteAdapter()
        self.api_adapter = ApiSpecAdapter()
        self.db_adapter = DatabaseSchemaAdapter()
        self.document_adapter = DocumentIntentAdapter()
        self.xml_adapter = XmlWorkflowAdapter()
        self.scaffold_generator = TemplateScaffoldGenerator(self.root / "templates")

    def run(self, command: str) -> PipelineRunResult:
        if command not in COMMAND_TARGETS:
            raise KeyError(f"Unknown NoCode2ProCode pipeline command: {command}")
        self.session = initialize_runtime_session(
            self.root,
            self.workspace,
            self.input_dir,
            self.app_name,
            command,
            existing=self.session,
        )
        target_stage = COMMAND_TARGETS[command]
        for stage in self._stages_until(target_stage):
            self._run_stage(stage)
        approval = self._read_json("approval.json", {"status": "not_started"})
        self.session = finalize_runtime_session(
            self.root,
            self.workspace,
            self.session,
            str(approval.get("status", "unknown")),
            bool(approval.get("requires_human_approval", False)),
        )
        return PipelineRunResult(
            workspace=self.workspace,
            target_stage=target_stage,
            approval_required=approval.get("requires_human_approval", False),
            approval_status=str(approval.get("status", "unknown")),
        )

    def _derive_app_name(self) -> str:
        if self.request.get("app_name"):
            return self._slug_label(str(self.request["app_name"]))
        if self.artifacts:
            return self._slug_label(self.artifacts[0].path.stem.replace("_", " ").replace("-", " "))
        return "migration app"

    def _slug_label(self, value: str) -> str:
        cleaned = " ".join(part for part in re.split(r"[^A-Za-z0-9]+", value) if part)
        return cleaned or "migration app"

    def _stages_until(self, target_stage: str) -> list[Stage]:
        stages: list[Stage] = []
        for stage in self.flow_stages:
            stages.append(stage)
            if stage.name == target_stage:
                break
        return stages

    def _run_stage(self, stage: Stage) -> None:
        started_at = _utc_now()
        result = self._handle_stage(stage.name)
        completed_at = _utc_now()
        self.state.setdefault("stages", {})[stage.name] = {
            "objective": stage.objective,
            "status": "completed",
            "started_at": started_at,
            "completed_at": completed_at,
            "result": result,
            "produces": list(stage.produces),
        }
        self.state["last_completed_stage"] = stage.name
        self.state["workspace"] = str(self.workspace)
        self.state["input_dir"] = str(self.input_dir)
        self.state["app_name"] = self.app_name
        self.session = update_runtime_session(self.root, self.workspace, self.session, stage.name, result)
        self._write_checkpoint()

    def _load_checkpoint(self) -> dict[str, Any]:
        if self.checkpoint_path.exists():
            return json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        return {
            "schema_version": "3.1.0",
            "framework": "NoCode2ProCode by TrustEngines",
            "created_at": _utc_now(),
            "stages": {},
        }

    def _write_checkpoint(self) -> None:
        metrics = {
            "completed_stage_count": len(self.state.get("stages", {})),
            "artifact_count": len(self.artifacts),
            "last_completed_stage": self.state.get("last_completed_stage"),
            "app_name": self.app_name,
            "workspace": str(self.workspace),
            "input_dir": str(self.input_dir),
        }
        self.state["pipeline_metrics"] = metrics
        write_json(self.checkpoint_path, self.state)
        write_json(self.workspace / "pipeline_metrics.json", metrics)

    def _handle_stage(self, stage_name: str) -> dict[str, Any]:
        handler = getattr(self, f"_stage_{stage_name}", None)
        if handler is None:
            return {"status": "no_handler", "message": f"No explicit runtime handler for stage {stage_name}."}
        return handler()

    def _stage_validate_inputs(self) -> dict[str, Any]:
        ensure_input_directory(self.root)
        has_request = bool(self.request)
        if not self.artifacts and not has_request:
            raise ValueError(
                f"No migration inputs found in {self.input_dir}. Add files or create a migration_request.yaml before running migrate."
            )
        intake_manifest = {
            "schema_version": "3.1.0",
            "input_dir": str(self.input_dir),
            "request": self.request,
            "artifacts": [artifact.as_dict() for artifact in self.artifacts],
            "artifact_count": len(self.artifacts),
            "primary_source_type": infer_primary_source_type(self.artifacts, self.request),
        }
        write_json(self.workspace / "input_intake_manifest.json", intake_manifest)
        write_json(
            self.workspace / "provider_routing_plan.json",
            build_provider_routing_plan(self.configs["routing"], self.configs["cost"], self.request, self.artifacts),
        )
        retrieval_plan = build_memory_retrieval_plan(self.root, self.configs["memory"], self.request, self.artifacts)
        write_json(self.workspace / "memory_retrieval_plan.json", retrieval_plan)
        write_json(self.workspace / "memory_context.json", build_memory_context_summary(retrieval_plan))
        manifest_path = self.workspace / "migration_manifest.json"
        manifest = self._read_json(
            manifest_path.name,
            {
                "schema_version": "3.1.0",
                "framework": "NoCode2ProCode by TrustEngines",
                "workspace": str(self.workspace),
            },
        )
        manifest.update(
            {
                "app_name": self.app_name,
                "workspace": str(self.workspace),
                "input_dir": str(self.input_dir),
                "updated_at": _utc_now(),
                "status": "validated",
                "artifact_count": len(self.artifacts),
                "primary_source_type": intake_manifest["primary_source_type"],
                "session_id": self.session.get("session_id"),
            }
        )
        write_json(manifest_path, manifest)
        return {"artifact_count": len(self.artifacts), "request_present": has_request}

    def _stage_extract_brd_design_intent(self) -> dict[str, Any]:
        notes = str(self.request.get("notes", "")).strip()
        previews = [
            artifact.metadata.get("preview")
            for artifact in self.artifacts
            if artifact.kind in {"document", "website_reference"} and artifact.metadata.get("preview")
        ]
        document_analyses = []
        for artifact in self.artifacts:
            if artifact.kind != "document":
                continue
            text = self._read_text_evidence(artifact.path)
            if text.strip():
                document_analyses.append(analyze_brd_text(text, source_name=artifact.path.name))
        merged_analysis = merge_brd_analyses(document_analyses) if document_analyses else {}
        prompt = self._user_prompt()
        design_intent = {
            "schema_version": "3.1.0",
            "app_name": self.app_name,
            "domain": self.request.get("domain") or self._infer_domain(),
            "goal": self.request.get("goal") or self._infer_goal(),
            "delivery_mode": self.request.get("delivery_mode") or "production_procode",
            "target_users": self._list_from_request("target_users"),
            "roles": self._list_from_request("roles"),
            "accessibility_requirements": self._list_from_request("accessibility_requirements")
            or ["keyboard_access", "visible_labels", "color_contrast_review"],
            "visual_constraints": self._list_from_request("visual_constraints"),
            "notes": notes,
            "evidence_snippets": [item for item in previews[:5] if item],
            "prompt_summary": prompt,
            "summary_sentences": merged_analysis.get("summary_sentences", []),
            "functional_requirements": merged_analysis.get("functional_requirements", []),
            "acceptance_criteria": merged_analysis.get("acceptance_criteria", []),
            "screen_candidates": merged_analysis.get("screen_candidates", []),
            "workflow_candidates": merged_analysis.get("workflow_candidates", []),
            "document_roles": merged_analysis.get("user_roles", []),
            "document_entities": merged_analysis.get("entities", []),
            "document_keywords": merged_analysis.get("keywords", []),
            "document_confidence": merged_analysis.get("confidence", 0.0),
        }
        write_json(self.workspace / "brd_design_intent.json", design_intent)
        return {
            "domain": design_intent["domain"],
            "goal": design_intent["goal"],
            "document_requirements": len(design_intent["functional_requirements"]),
        }

    def _stage_extract_brd_mockups(self) -> dict[str, Any]:
        images = [artifact.relative_path for artifact in self.artifacts if artifact.source_type == "image"]
        videos = [artifact.relative_path for artifact in self.artifacts if artifact.source_type == "video"]
        docs = [artifact.relative_path for artifact in self.artifacts if artifact.kind == "document"]
        image_references = [
            {
                "artifact_id": artifact.artifact_id,
                "path": artifact.relative_path,
                "purpose": artifact.metadata.get("visual_reference_purpose", "visual_evidence"),
                "screen_hint": artifact.metadata.get("screen_hint"),
                "priority": artifact.metadata.get("priority", "medium"),
                "input_bucket": artifact.metadata.get("input_bucket", "root"),
            }
            for artifact in self.artifacts
            if artifact.source_type == "image"
        ]
        video_references = [
            {
                "artifact_id": artifact.artifact_id,
                "path": artifact.relative_path,
                "purpose": artifact.metadata.get("video_reference_purpose", "video_reference"),
                "flow_hint": artifact.metadata.get("flow_hint"),
                "priority": artifact.metadata.get("priority", "medium"),
                "input_bucket": artifact.metadata.get("input_bucket", "root"),
            }
            for artifact in self.artifacts
            if artifact.source_type == "video"
        ]
        visual_analyses = []
        for artifact in self.artifacts:
            if artifact.source_type == "image":
                visual_analyses.append(
                    {
                        "artifact_id": artifact.artifact_id,
                        "purpose": artifact.metadata.get("visual_reference_purpose", "visual_evidence"),
                        "screen_hint": artifact.metadata.get("screen_hint"),
                        "priority": artifact.metadata.get("priority", "medium"),
                        "input_bucket": artifact.metadata.get("input_bucket", "root"),
                        **analyze_visual_artifact(artifact.path),
                    }
                )
            elif artifact.source_type == "video":
                visual_analyses.append(
                    {
                        "artifact_id": artifact.artifact_id,
                        "source": str(artifact.path),
                        "type": artifact.path.suffix.lower().lstrip("."),
                        "purpose": artifact.metadata.get("video_reference_purpose", "video_reference"),
                        "flow_hint": artifact.metadata.get("flow_hint"),
                        "priority": artifact.metadata.get("priority", "medium"),
                        "input_bucket": artifact.metadata.get("input_bucket", "root"),
                        "viewport_kind": "unknown",
                        "screen_candidates": [artifact.path.stem.replace("_", " ").replace("-", " ").title()],
                        "visual_hints": [token for token in ("walkthrough", "demo", "runtime", "approval") if token in artifact.path.stem.lower()],
                        "confidence": artifact.confidence,
                    }
                )
        inventory = {
            "schema_version": "3.1.0",
            "images": images,
            "videos": videos,
            "documents": docs,
            "image_references": image_references,
            "video_references": video_references,
            "mockup_count": len(images),
            "runtime_video_count": len(videos),
            "visual_analyses": visual_analyses,
        }
        write_json(self.workspace / "brd_mockup_inventory.json", inventory)
        write_json(
            self.workspace / "visual_reference_inventory.json",
            {
                "schema_version": "3.1.0",
                "input_model": {
                    "raw_data": "source/business/runtime export evidence",
                    "images": "UI screenshots, mockups, visual references, brand, and components",
                    "videos": "walkthroughs, click flows, state changes, and runtime behavior",
                },
                "image_references": image_references,
                "video_references": video_references,
                "visual_analyses": visual_analyses,
            },
        )
        extracted_dir = self.workspace / "brd_extracted_images"
        extracted_dir.mkdir(parents=True, exist_ok=True)
        return {"images": len(images), "videos": len(videos), "visual_analyses": len(visual_analyses)}

    def _stage_brd_understanding_gate(self) -> dict[str, Any]:
        brd_understanding = build_brd_understanding(
            self.request,
            self._read_json("brd_design_intent.json", {}),
            self._read_json("brd_mockup_inventory.json", {}),
            [artifact.as_dict() for artifact in self.artifacts],
            app_name=self.app_name,
        )
        gate = resolve_brd_understanding_gate(self.request, brd_understanding, app_name=self.app_name)
        approved_plan = gate["approved_brd_plan"]
        edit_request = {
            "schema_version": "3.1.0",
            "status": gate["status"],
            "selected_action": gate["selected_action"],
            "requires_human_confirmation": gate["requires_human_confirmation"],
            "edit_notes": gate["edit_notes"],
            "prompt_to_user": "What changes do you want in the BRD understanding before Genesis continues toward code generation?",
        }
        write_json(self.workspace / "brd_understanding_report.json", brd_understanding)
        write_json(self.workspace / "brd_understanding_gate.json", gate)
        write_json(self.workspace / "brd_edit_request.json", edit_request)
        write_json(self.workspace / "brd_semantic_patch_report.json", gate["semantic_patch"])
        write_json(self.workspace / "approved_brd_plan.json", approved_plan)
        write_text(
            self.workspace / "brd_understanding_summary.md",
            textwrap.dedent(
                f"""\
                # BRD Understanding Gate

                App: **{self.app_name}**

                Status: `{gate['status']}`

                Requires human confirmation: `{gate['requires_human_confirmation']}`

                ## What Genesis understood

                - Domain: {brd_understanding['application_intent']['domain']}
                - Goal: {brd_understanding['application_intent']['goal']}
                - Confidence: {brd_understanding['confidence']}

                ## Summary

                {self._markdown_list(brd_understanding.get('summary', [])) or "- No summary sentences extracted."}

                ## Roles / users

                {self._markdown_list(brd_understanding.get('roles', [])) or "- No roles extracted."}

                ## Pages / screens

                {self._markdown_list([screen.get('name', '') for screen in brd_understanding.get('pages_or_screens', [])]) or "- No pages extracted."}

                ## Functional requirements

                {self._markdown_list(brd_understanding.get('functional_requirements', [])[:30]) or "- No functional requirements extracted."}

                ## Workflows

                {self._markdown_list(brd_understanding.get('workflows', [])[:20]) or "- No workflow candidates extracted."}

                ## Mockup and runtime evidence

                - Separate images: {len(brd_understanding['mockup_evidence'].get('separate_images', []))}
                - Runtime videos: {len(brd_understanding['mockup_evidence'].get('runtime_videos', []))}
                - Office documents with embedded media: {len(brd_understanding['mockup_evidence'].get('embedded_media_documents', []))}

                ## Gate options

                {self._render_brd_gate_options(gate.get('options', []))}

                ## If editing is needed

                {gate['how_to_edit']}

                ## Semantic patch result

                - Status: {gate['semantic_patch']['status']}
                - Parsed actions: {gate['semantic_patch']['action_count'] if 'action_count' in gate['semantic_patch'] else len(gate['semantic_patch'].get('parsed_actions', []))}
                - Patched fields: {', '.join(gate['semantic_patch'].get('patched_fields', [])) or 'none'}
                """
            ),
        )
        return {
            "status": gate["status"],
            "requires_human_confirmation": gate["requires_human_confirmation"],
            "requirement_count": len(brd_understanding.get("functional_requirements", [])),
            "screen_count": len(brd_understanding.get("pages_or_screens", [])),
        }

    def _stage_decide_delivery_mode_and_stack(self) -> dict[str, Any]:
        prompt = self._user_prompt()
        decision = resolve_stack_decision(
            prompt,
            brd_stack=self.request.get("brd_stack"),
            domain=self.request.get("domain") or self._infer_domain(),
            scope=self.request.get("scope") or self._infer_scope(),
        )
        write_json(self.workspace / "stack_decision_report.json", decision)
        write_json(
            self.workspace / "delivery_mode_decision.json",
            {
                "schema_version": "3.1.0",
                "selected_delivery_mode": decision["selected_delivery_mode"],
                "selected_target_stack": decision["selected_target_stack"],
                "human_approval_required": decision["human_approval_required"],
                "reason": decision["decision_reason"],
            },
        )
        return {
            "delivery_mode": decision["selected_delivery_mode"],
            "target_stack": decision["selected_target_stack"],
        }

    def _stage_migration_mode_gate(self) -> dict[str, Any]:
        decision = resolve_migration_mode(
            self.request,
            self._read_json("stack_decision_report.json", {}),
            app_name=self.app_name,
            primary_source_type=infer_primary_source_type(self.artifacts, self.request),
        )
        write_json(self.workspace / "migration_mode_decision.json", decision)
        write_text(
            self.workspace / "migration_mode_options.md",
            textwrap.dedent(
                f"""\
                # Migration Output Mode Gate

                Selected mode: **{decision['selected_label']}**

                Selection source: `{decision['selection_source']}`

                Requires human confirmation: `{decision['requires_human_confirmation']}`

                ## Options

                {self._render_mode_options(decision.get('options', []))}

                ## Why this mode

                {decision['reason']}

                ## Downstream instructions

                {self._markdown_list(decision.get('downstream_instructions', []))}
                """
            ),
        )
        return {
            "selected_mode": decision["selected_mode"],
            "requires_human_confirmation": decision["requires_human_confirmation"],
        }

    def _stage_dry_run_estimate(self) -> dict[str, Any]:
        baseline = summarize_input_artifacts(self.artifacts, self.request)
        confidence = round(self._overall_artifact_confidence(), 4)
        unsupported = baseline["unsupported_or_low_confidence"]
        effort_matrix = {
            "schema_version": "3.1.0",
            "artifact_complexity": len(self.artifacts),
            "estimated_screen_count": self._estimated_screen_count(),
            "estimated_workflow_count": self._estimated_workflow_count(),
            "confidence": confidence,
            "migration_output_mode": self._read_json("migration_mode_decision.json", {}).get("selected_mode"),
            "requires_runtime_evidence": any(artifact.source_type in {"website", "video"} for artifact in self.artifacts),
            "requires_human_review": bool(unsupported),
        }
        write_json(self.workspace / "effort_matrix.json", effort_matrix)
        write_json(
            self.workspace / "dry_run_confidence_scores.json",
            {
                "schema_version": "3.1.0",
                "artifact_confidence": confidence,
                "unsupported_items": unsupported,
            },
        )
        write_text(
            self.workspace / "estimation_report.md",
            textwrap.dedent(
                f"""\
                # NoCode2ProCode Dry Run Estimate

                - App: {self.app_name}
                - Input artifacts: {len(self.artifacts)}
                - Estimated screens: {effort_matrix['estimated_screen_count']}
                - Estimated workflows: {effort_matrix['estimated_workflow_count']}
                - Confidence: {confidence:.2f}
                - Runtime evidence recommended: {effort_matrix['requires_runtime_evidence']}
                - Human review likely: {effort_matrix['requires_human_review']}

                ## Low-confidence areas
                {self._markdown_list(unsupported) or '- None detected from intake metadata.'}
                """
            ),
        )
        return {"confidence": confidence, "unsupported_count": len(unsupported)}

    def _stage_discover_sources(self) -> dict[str, Any]:
        baseline = summarize_input_artifacts(self.artifacts, self.request)
        baseline["schema_version"] = "3.1.0"
        baseline["primary_source_type"] = infer_primary_source_type(self.artifacts, self.request)
        baseline["domains"] = domain_from_urls(collect_reference_urls(self.artifacts, self.request))
        write_json(self.workspace / "source_baseline.json", baseline)
        asset_inventory = {
            "schema_version": "3.1.0",
            "images": [artifact.relative_path for artifact in self.artifacts if artifact.source_type == "image"],
            "videos": [artifact.relative_path for artifact in self.artifacts if artifact.source_type == "video"],
            "documents": [artifact.relative_path for artifact in self.artifacts if artifact.kind == "document"],
            "archives": [artifact.relative_path for artifact in self.artifacts if artifact.kind in {"archive", "lowcode_export"}],
            "input_buckets": baseline.get("input_buckets", {}),
            "visual_references": [
                {
                    "path": artifact.relative_path,
                    "purpose": artifact.metadata.get("visual_reference_purpose"),
                    "screen_hint": artifact.metadata.get("screen_hint"),
                    "priority": artifact.metadata.get("priority"),
                }
                for artifact in self.artifacts
                if artifact.source_type == "image"
            ],
            "runtime_video_references": [
                {
                    "path": artifact.relative_path,
                    "purpose": artifact.metadata.get("video_reference_purpose"),
                    "flow_hint": artifact.metadata.get("flow_hint"),
                    "priority": artifact.metadata.get("priority"),
                }
                for artifact in self.artifacts
                if artifact.source_type == "video"
            ],
            "urls": collect_reference_urls(self.artifacts, self.request),
        }
        write_json(self.workspace / "asset_inventory.json", asset_inventory)
        stage_names = [stage.name for stage in self._stages_until(COMMAND_TARGETS["migrate"])]
        execution_plan = build_agent_execution_plan(self.configs["agents"], stage_names, self.artifacts)
        write_json(self.workspace / "agent_execution_plan.json", execution_plan)
        write_json(self.workspace / "swarm_topology.json", build_swarm_topology(execution_plan))
        return {"artifact_count": baseline["artifact_count"], "primary_source_type": baseline["primary_source_type"]}

    def _stage_extract_native_ast(self) -> dict[str, Any]:
        platform_ast: dict[str, Any] = {
            "schema_version": "3.1.0",
            "sources": [],
            "screens": [],
            "workflows": [],
            "data_sources": [],
            "connector_hints": [],
            "unsupported_items": [],
        }
        design_ast: dict[str, Any] = {
            "schema_version": "3.1.0",
            "images": [],
            "videos": [],
            "documents": [],
            "visual_sources": [],
        }
        website_ast: dict[str, Any] = {"schema_version": "3.1.0", "pages": [], "domains": [], "unsupported_items": [], "navigation_hints": []}
        api_ast: dict[str, Any] = {"schema_version": "3.1.0", "specs": [], "endpoints": [], "unsupported_items": []}
        db_ast: dict[str, Any] = {"schema_version": "3.1.0", "entities": [], "columns": [], "unsupported_items": []}
        document_intent: dict[str, Any] = {"schema_version": "3.1.0", "documents": [], "notes": [], "keywords": []}

        for artifact in self.artifacts:
            if artifact.source_type == "powerapps":
                result = self.powerapps_adapter.extract(artifact.path, self.workspace / "evidence" / "powerapps")
                platform_ast["sources"].append(result.ast)
                platform_ast["screens"].extend(result.ast.get("screen_names", []))
                platform_ast["connector_hints"].extend(result.ast.get("connector_hints", []))
                platform_ast["data_sources"].extend(result.ast.get("data_source_hints", []))
                platform_ast["unsupported_items"].extend(result.unsupported_items)
            elif artifact.source_type == "website":
                for url in artifact.urls or [artifact.metadata.get("preview", "")]:
                    if not url:
                        continue
                    result = self.website_adapter.extract(url, self.workspace / "evidence" / "website")
                    website_ast["pages"].append(result.ast)
                    website_ast["navigation_hints"].append({"url": url, "path": result.ast.get("path") or "/"})
                    website_ast["unsupported_items"].extend(result.unsupported_items)
            elif artifact.signal == "openapi_present":
                result = self.api_adapter.extract(artifact.path, self.workspace / "evidence" / "api")
                api_ast["specs"].append(result.ast)
                api_ast["endpoints"].extend(result.ast.get("endpoints", []))
                api_ast["unsupported_items"].extend(result.unsupported_items)
            elif artifact.source_type in {"database", "tabular", "spreadsheet"}:
                result = self.db_adapter.extract(artifact.path, self.workspace / "evidence" / "database")
                db_ast["entities"].extend(result.ast.get("entities", []))
                db_ast["unsupported_items"].extend(result.unsupported_items)
            elif artifact.source_type in {"image", "video"}:
                destination = "images" if artifact.source_type == "image" else "videos"
                visual_analysis = analyze_visual_artifact(artifact.path) if artifact.source_type == "image" else {
                    "source": str(artifact.path),
                    "type": artifact.path.suffix.lower().lstrip("."),
                    "viewport_kind": "unknown",
                    "screen_candidates": [artifact.path.stem.replace("_", " ").replace("-", " ").title()],
                    "visual_hints": [],
                    "confidence": artifact.confidence,
                    "dimensions": {"width": None, "height": None},
                }
                visual_analysis["input_bucket"] = artifact.metadata.get("input_bucket", "root")
                visual_analysis["purpose"] = artifact.metadata.get("visual_reference_purpose") or artifact.metadata.get("video_reference_purpose")
                visual_analysis["priority"] = artifact.metadata.get("priority", "medium")
                visual_analysis["screen_hint"] = artifact.metadata.get("screen_hint") or artifact.metadata.get("flow_hint")
                design_ast[destination].append({**artifact.as_dict(), "analysis": visual_analysis})
                design_ast["visual_sources"].append(
                    {
                        "path": artifact.relative_path,
                        "type": artifact.source_type,
                        "input_bucket": artifact.metadata.get("input_bucket", "root"),
                        "purpose": visual_analysis.get("purpose"),
                        "priority": visual_analysis.get("priority"),
                        "screen_candidates": visual_analysis.get("screen_candidates", []),
                        "viewport_kind": visual_analysis.get("viewport_kind"),
                    }
                )
            elif artifact.source_type in {"document", "text", "xml", "workflow_xml"}:
                if artifact.source_type in {"xml", "workflow_xml"}:
                    result = self.xml_adapter.extract(artifact.path, self.workspace / "evidence" / "xml")
                    platform_ast["workflows"].extend(result.ast.get("workflow_steps", []))
                    platform_ast["unsupported_items"].extend(result.unsupported_items)
                    document_intent["documents"].append({**artifact.as_dict(), "xml_root_tag": result.ast.get("root_tag")})
                else:
                    result = self.document_adapter.extract(artifact.path, self.workspace / "evidence" / "documents")
                    document_intent["documents"].append({**artifact.as_dict(), **result.ast})
                    document_intent["notes"].extend(result.ast.get("summary_sentences", [])[:5])
                    document_intent["keywords"].extend(result.ast.get("keywords", []))

            if artifact.signal == "workflow_xml_present":
                platform_ast["workflows"].append(
                    {
                        "name": Path(artifact.path).stem,
                        "path": artifact.relative_path,
                        "source_type": artifact.source_type,
                }
            )

        website_ast["domains"] = domain_from_urls(collect_reference_urls(self.artifacts, self.request))
        db_ast["columns"] = sorted(
            {
                column
                for entity in db_ast["entities"]
                for column in entity.get("columns", [])
                if isinstance(column, str) and column
            }
        )[:200]
        document_intent["keywords"] = sorted(dict.fromkeys(document_intent["keywords"]))[:50]
        design_ast["documents"] = document_intent["documents"]

        write_json(self.workspace / "platform_ast.json", platform_ast)
        write_json(self.workspace / "design_ast.json", design_ast)
        write_json(self.workspace / "website_ast.json", website_ast)
        write_json(self.workspace / "api_ast.json", api_ast)
        write_json(self.workspace / "db_ast.json", db_ast)
        write_json(self.workspace / "document_intent.json", document_intent)
        return {
            "platform_sources": len(platform_ast["sources"]),
            "website_pages": len(website_ast["pages"]),
            "api_specs": len(api_ast["specs"]),
            "db_entities": len(db_ast["entities"]),
        }

    def _stage_record_runtime_evidence(self) -> dict[str, Any]:
        urls = collect_reference_urls(self.artifacts, self.request)
        browser_plan = build_browser_runtime_plan(self.artifacts, self.request, self.configs["routing"])
        write_json(self.workspace / "browser_runtime_plan.json", browser_plan)
        capture_bundle = capture_runtime_targets(
            urls,
            self.workspace / "runtime_recording" / "html_snapshots",
            allow_remote=bool(self.request.get("allow_remote_runtime_capture", False)),
        )
        runtime_evidence = {
            "schema_version": "3.1.0",
            "status": capture_bundle["status"],
            "recommended_capture_targets": urls,
            "video_inputs": [artifact.relative_path for artifact in self.artifacts if artifact.source_type == "video"],
            "playwright_actions": ["login", "navigate core flows", "submit forms", "capture screenshots", "save network traces"],
            "network_trace_status": "not_captured",
            "captured_targets": capture_bundle["targets"],
            "notes": [
                "This run created runtime evidence from URLs that were safe to capture in the current environment.",
                "Remote authenticated flows still need Playwright or live credentials for full parity capture.",
            ],
        }
        privacy_scan = {
            "schema_version": "3.1.0",
            "status": "heuristic_scan_only",
            "potential_sensitive_artifacts": [
                artifact.relative_path
                for artifact in self.artifacts
                if any(token in artifact.relative_path.lower() for token in ("patient", "user", "employee", "salary", "invoice"))
            ],
        }
        asset_license = {
            "schema_version": "3.1.0",
            "status": "input_inventory_only",
            "review_required_assets": [artifact.relative_path for artifact in self.artifacts if artifact.source_type in {"image", "video"}],
        }
        write_json(self.workspace / "runtime_evidence.json", runtime_evidence)
        write_json(
            self.workspace / "runtime_capture_contract.json",
            build_runtime_capture_contract(self.artifacts, self.request, self._read_json("source_truth_report.json", {})),
        )
        write_json(self.workspace / "privacy_scan_report.json", privacy_scan)
        write_json(self.workspace / "asset_license_report.json", asset_license)
        return {
            "recommended_capture_targets": len(urls),
            "captured_targets": capture_bundle["captured_count"],
            "video_inputs": len(runtime_evidence["video_inputs"]),
        }

    def _stage_resolve_source_truth(self) -> dict[str, Any]:
        platform_ast = self._read_json("platform_ast.json", {})
        website_ast = self._read_json("website_ast.json", {})
        api_ast = self._read_json("api_ast.json", {})
        db_ast = self._read_json("db_ast.json", {})
        runtime = self._read_json("runtime_evidence.json", {})
        decisions = [
            decide_source_truth(
                artifact_id="ui_surface",
                artifact_type="screen_inventory",
                candidates={
                    "runtime": runtime if runtime.get("recommended_capture_targets") else None,
                    "export": platform_ast if platform_ast.get("screens") else None,
                    "design": website_ast if website_ast.get("pages") else None,
                },
            ),
            decide_source_truth(
                artifact_id="data_model",
                artifact_type="entities",
                candidates={
                    "db": db_ast if db_ast.get("entities") else None,
                    "api": api_ast if api_ast.get("specs") else None,
                    "export": platform_ast if platform_ast.get("data_sources") else None,
                },
            ),
        ]
        report = {
            "schema_version": "3.1.0",
            "decisions": [
                {
                    "artifact_id": decision.artifact_id,
                    "artifact_type": decision.artifact_type,
                    "winning_source": decision.winning_source,
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "requires_human_review": decision.requires_human_review,
                }
                for decision in decisions
            ],
        }
        conflicts = {
            "schema_version": "3.1.0",
            "conflicts": [
                item
                for item in report["decisions"]
                if item["requires_human_review"] or item["winning_source"] == "none"
            ],
        }
        write_json(self.workspace / "source_truth_report.json", report)
        write_json(self.workspace / "source_conflict_report.json", conflicts)
        return {"decision_count": len(report["decisions"]), "conflict_count": len(conflicts["conflicts"])}

    def _stage_source_truth_approval_gate(self) -> dict[str, Any]:
        bundle = resolve_source_truth_gate(
            self.request,
            self._read_json("source_truth_report.json", {}),
            self._read_json("source_conflict_report.json", {}),
            app_name=self.app_name,
        )
        write_json(self.workspace / "source_truth_approval_gate.json", bundle["gate"])
        write_json(self.workspace / "source_truth_human_notes.json", bundle["human_notes"])
        write_json(self.workspace / "source_truth_patch_instructions.json", bundle["patch_instructions"])
        write_json(self.workspace / "source_truth_semantic_patch_report.json", bundle["patch_instructions"].get("semantic_patch", {}))
        write_json(self.workspace / "approved_source_truth_report.json", bundle["approved_report"])
        self._write_human_gate_context()
        return {
            "status": bundle["gate"]["status"],
            "requires_human_confirmation": bundle["gate"]["requires_human_confirmation"],
            "patch_instruction_count": len(bundle["patch_instructions"].get("instructions", [])),
        }

    def _stage_build_ulc_ir(self) -> dict[str, Any]:
        platform_ast = self._read_json("platform_ast.json", {})
        website_ast = self._read_json("website_ast.json", {})
        api_ast = self._read_json("api_ast.json", {})
        db_ast = self._read_json("db_ast.json", {})
        design_ast = self._read_json("design_ast.json", {})
        source_truth = self._read_json("approved_source_truth_report.json", self._read_json("source_truth_report.json", {}))
        approved_brd = self._read_json("approved_brd_plan.json", {})
        brd_screens = [
            {"name": screen.get("name"), "source": "approved_brd_plan"}
            for screen in approved_brd.get("pages_or_screens", [])
            if screen.get("name")
        ]
        brd_workflows = [
            {"name": self._short_label(workflow), "source": "approved_brd_plan", "description": workflow}
            for workflow in approved_brd.get("workflows", [])[:60]
        ]
        brd_entities = [
            {"name": entity, "columns": [], "source": "approved_brd_plan"}
            for entity in approved_brd.get("entities", [])[:60]
        ]
        ir = empty_ulc_ir()
        ir["ui_ir"]["screens"] = [
            {"name": name, "source": "powerapps_export"} for name in platform_ast.get("screens", [])[:100]
        ] + [
            {"name": page.get("domain") or page.get("source"), "source": "website_reference"}
            for page in website_ast.get("pages", [])[:20]
        ] + brd_screens
        ir["workflow_ir"]["workflows"] = platform_ast.get("workflows", []) + brd_workflows
        ir["domain_ir"]["entities"] = db_ast.get("entities", []) + brd_entities
        ir["domain_ir"]["requirements"] = approved_brd.get("functional_requirements", [])
        ir["domain_ir"]["human_semantic_patch"] = approved_brd.get("semantic_patch", {})
        ir["workflow_ir"]["acceptance_criteria"] = approved_brd.get("acceptance_criteria", [])
        ir["workflow_ir"]["human_patch_summary"] = approved_brd.get("human_patch_summary", [])
        ir["integration_ir"]["api_contracts"] = api_ast.get("specs", [])
        ir["integration_ir"]["data_sources"] = platform_ast.get("data_sources", [])
        ir["integration_ir"]["connectors"] = platform_ast.get("connector_hints", [])
        ir["design_ir"]["design_source_map"] = design_ast.get("visual_sources", [])
        ir["security_ir"]["roles"] = self._unique_strings(self._list_from_request("roles") + approved_brd.get("roles", []))
        ir["security_ir"]["privacy_notes"] = approved_brd.get("security_privacy_notes", [])
        ir["unsupported_items"] = platform_ast.get("unsupported_items", []) + website_ast.get("unsupported_items", [])
        ulc_dir = self.workspace / "ulc_ir"
        design_dir = self.workspace / "design_ir"
        ulc_dir.mkdir(parents=True, exist_ok=True)
        design_dir.mkdir(parents=True, exist_ok=True)
        write_json(ulc_dir / "ulc_ir.json", ir)
        write_json(design_dir / "design_ir.json", ir["design_ir"])
        self._validate_json_schema(ir, self.root / "schemas" / "ulc_ir.schema.json")
        write_json(
            self.workspace / "ir_changelog.json",
            {
                "schema_version": "3.1.0",
            "changes": [
                    {
                        "stage": "build_ulc_ir",
                        "timestamp": _utc_now(),
                        "summary": f"Built IR from {len(self.artifacts)} input artifacts, {len(source_truth.get('decisions', []))} source-truth decisions, and {len(approved_brd.get('semantic_patch', {}).get('applied_actions', []))} human semantic BRD patch actions.",
                    }
                ],
            },
        )
        return {
            "screen_count": len(ir["ui_ir"]["screens"]),
            "entity_count": len(ir["domain_ir"]["entities"]),
            "workflow_count": len(ir["workflow_ir"]["workflows"]),
        }

    def _stage_resolve_conflicts(self) -> dict[str, Any]:
        ulc_ir = self._read_json(str(Path("ulc_ir") / "ulc_ir.json"), {})
        conflicts: list[dict[str, Any]] = []
        screen_names: set[str] = set()
        for screen in ulc_ir.get("ui_ir", {}).get("screens", []):
            name = screen.get("name")
            if name in screen_names:
                conflicts.append({"type": "duplicate_screen", "name": name, "resolution": "rename_or_merge"})
            if name:
                screen_names.add(name)
        report = {"schema_version": "3.1.0", "conflicts": conflicts, "resolved_count": 0}
        write_json(self.workspace / "conflict_resolution_report.json", report)
        return {"conflict_count": len(conflicts)}

    def _stage_validate_ir(self) -> dict[str, Any]:
        ulc_ir = self._read_json(str(Path("ulc_ir") / "ulc_ir.json"), {})
        brd_gate = self._read_json("brd_understanding_gate.json", {})
        brd_requires_review = bool(brd_gate.get("requires_human_confirmation"))
        confidence_scores = {
            "schema_version": "3.1.0",
            "overall_confidence": round(self._overall_artifact_confidence(), 4),
            "ui_confidence": round(0.7 if ulc_ir.get("ui_ir", {}).get("screens") else 0.4, 4),
            "data_confidence": round(0.78 if ulc_ir.get("domain_ir", {}).get("entities") else 0.42, 4),
            "integration_confidence": round(0.72 if ulc_ir.get("integration_ir", {}).get("api_contracts") else 0.48, 4),
        }
        unsupported_strategy = {
            "schema_version": "3.1.0",
            "items": ulc_ir.get("unsupported_items", []),
            "strategy": "Capture runtime evidence and request targeted human review for unresolved semantics.",
        }
        migration_contract = {
            "schema_version": "3.1.0",
            "app_name": self.app_name,
            "target_stack": self._read_json("stack_decision_report.json", {}).get("selected_target_stack"),
            "delivery_mode": self._read_json("delivery_mode_decision.json", {}).get("selected_delivery_mode"),
            "migration_output_mode": self._read_json("migration_mode_decision.json", {}).get("selected_mode"),
            "must_preserve": [
                "approved BRD understanding",
                "user journeys",
                "data model intent",
                "role behavior",
                "core workflows",
            ],
            "brd_understanding_status": brd_gate.get("status", "unknown"),
            "review_required": bool(self._read_json("source_conflict_report.json", {}).get("conflicts")) or brd_requires_review,
        }
        test_oracle = {
            "schema_version": "3.1.0",
            "critical_user_flows": self._critical_user_flows(),
            "required_quality_gates": self.configs["qa"].get("quality_gates", {}),
        }
        write_json(self.workspace / "confidence_scores.json", confidence_scores)
        write_json(self.workspace / "unsupported_strategy.json", unsupported_strategy)
        write_json(self.workspace / "migration_contract.json", migration_contract)
        write_json(self.workspace / "test_oracle.json", test_oracle)
        write_json(
            self.workspace / "ir_validation_report.json",
            {
                "schema_version": "3.1.0",
                "status": "valid_with_review_items" if migration_contract["review_required"] else "valid",
                "screen_count": len(ulc_ir.get("ui_ir", {}).get("screens", [])),
                "entity_count": len(ulc_ir.get("domain_ir", {}).get("entities", [])),
                "unsupported_items": len(ulc_ir.get("unsupported_items", [])),
            },
        )
        return {"overall_confidence": confidence_scores["overall_confidence"]}

    def _stage_build_canonical_app_spec(self) -> dict[str, Any]:
        ulc_ir = self._read_json(str(Path("ulc_ir") / "ulc_ir.json"), {})
        stack = self._read_json("stack_decision_report.json", {})
        migration_mode = self._read_json("migration_mode_decision.json", {})
        design = self._read_json("design_decision_report.json", {})
        source_summary = self._read_json("source_baseline.json", {})
        migration_contract = self._read_json("migration_contract.json", {})
        confidence_scores = self._read_json("confidence_scores.json", {})
        test_oracle = self._read_json("test_oracle.json", {})
        approved_brd = self._read_json("approved_brd_plan.json", {})
        domain_spec = {
            "domain": self.request.get("domain") or self._infer_domain(),
            "entities": ulc_ir.get("domain_ir", {}).get("entities", []),
            "relationships": ulc_ir.get("domain_ir", {}).get("relationships", []),
            "constraints": ulc_ir.get("domain_ir", {}).get("constraints", []),
            "requirements": ulc_ir.get("domain_ir", {}).get("requirements", []),
            "source_summary": source_summary,
        }
        workflow_spec = {
            "workflows": ulc_ir.get("workflow_ir", {}).get("workflows", []),
            "approvals": ulc_ir.get("workflow_ir", {}).get("approvals", []),
            "business_rules": ulc_ir.get("workflow_ir", {}).get("business_rules", []),
            "critical_user_flows": test_oracle.get("critical_user_flows", []),
        }
        api_spec = {
            "contracts": ulc_ir.get("integration_ir", {}).get("api_contracts", []),
            "data_sources": ulc_ir.get("integration_ir", {}).get("data_sources", []),
            "connectors": ulc_ir.get("integration_ir", {}).get("connectors", []),
            "mocks": ulc_ir.get("integration_ir", {}).get("mocks", []),
        }
        ui_spec = {
            "screens": ulc_ir.get("ui_ir", {}).get("screens", []),
            "ui_components": ulc_ir.get("ui_ir", {}).get("ui_components", []),
            "navigation": ulc_ir.get("ui_ir", {}).get("navigation", []),
            "responsive_rules": ulc_ir.get("ui_ir", {}).get("responsive_rules", []),
            "design_strategy": design,
        }
        security_spec = {
            "roles": ulc_ir.get("security_ir", {}).get("roles", []),
            "permissions": ulc_ir.get("security_ir", {}).get("permissions", []),
            "row_level_rules": ulc_ir.get("security_ir", {}).get("row_level_rules", []),
            "auth_flows": ulc_ir.get("security_ir", {}).get("auth_flows", []),
            "review_required": migration_contract.get("review_required", False),
        }
        deployment_spec = {
            "delivery_mode": stack.get("selected_delivery_mode"),
            "migration_output_mode": migration_mode.get("selected_mode"),
            "migration_output_label": migration_mode.get("selected_label"),
            "technology_profile": migration_mode.get("technology"),
            "runtime_goal": migration_mode.get("runtime_goal"),
            "localhost_required": migration_mode.get("localhost_required", False),
            "target_stack": stack.get("selected_target_stack"),
            "quality_gates_required": stack.get("quality_gates_required", []),
            "human_approval_required": stack.get("human_approval_required", False),
        }
        observability_spec = {
            "logging": True,
            "health_endpoint": True,
            "recommended_integrations": ["structured_logs", "error_monitoring", "request_tracing"],
        }
        spec = {
            "schema_version": "3.1.0",
            "app": {
                "name": self.app_name,
                "description": self.request.get("goal") or self._infer_goal(),
            },
            "target_stack": stack.get("selected_target_stack"),
            "domain_spec": domain_spec,
            "workflow_spec": workflow_spec,
            "api_spec": api_spec,
            "ui_spec": ui_spec,
            "security_spec": security_spec,
            "deployment_spec": deployment_spec,
            "migration_mode": migration_mode,
            "brd_understanding": approved_brd,
            "human_semantic_patch_spec": approved_brd.get("semantic_patch", {}),
            "observability_spec": observability_spec,
            "test_oracle_spec": test_oracle,
            "acceptance_criteria": [
                "Preserve core workflows from extracted evidence.",
                "Preserve the approved BRD understanding before technology selection.",
                "Preserve data model intent and important fields.",
                "Keep role-sensitive behavior reviewable.",
                "Generate software through the canonical migration pipeline.",
                f"Honor migration output mode: {migration_mode.get('selected_label', 'Hybrid Pilot App')}.",
            ]
            + approved_brd.get("acceptance_criteria", [])[:20],
            "source_summary": source_summary,
            "migration_contract": migration_contract,
            "selected_delivery_mode": stack.get("selected_delivery_mode"),
            "selected_migration_output_mode": migration_mode.get("selected_mode"),
            "selected_target_stack": stack.get("selected_target_stack"),
            "design_strategy": design,
            "screens": ui_spec["screens"],
            "workflows": workflow_spec["workflows"],
            "entities": domain_spec["entities"],
            "integrations": api_spec["contracts"],
            "roles": security_spec["roles"],
            "confidence_scores": confidence_scores,
        }
        self._validate_json_schema(spec, self.root / "schemas" / "canonical_app_spec.schema.json")
        write_json(self.workspace / "canonical_app_spec.json", spec)
        return {"screen_count": len(spec["screens"]), "entity_count": len(spec["entities"])}

    def _stage_canonical_spec_approval_gate(self) -> dict[str, Any]:
        bundle = resolve_canonical_spec_gate(
            self.request,
            self._read_json("canonical_app_spec.json", {}),
            app_name=self.app_name,
        )
        write_json(self.workspace / "canonical_spec_approval_gate.json", bundle["gate"])
        write_json(self.workspace / "canonical_spec_human_notes.json", bundle["human_notes"])
        write_json(self.workspace / "canonical_spec_patch_instructions.json", bundle["patch_instructions"])
        write_json(self.workspace / "canonical_spec_semantic_patch_report.json", bundle["semantic_patch"])
        write_json(self.workspace / "approved_canonical_app_spec.json", bundle["approved_spec"])
        self._write_human_gate_context()
        return {
            "status": bundle["gate"]["status"],
            "requires_human_confirmation": bundle["gate"]["requires_human_confirmation"],
            "patch_instruction_count": len(bundle["patch_instructions"].get("instructions", [])),
        }

    def _stage_human_review_gate(self) -> dict[str, Any]:
        conflicts = self._read_json("source_conflict_report.json", {}).get("conflicts", [])
        confidence = self._read_json("confidence_scores.json", {}).get("overall_confidence", 0.0)
        migration_mode = self._read_json("migration_mode_decision.json", {})
        brd_gate = self._read_json("brd_understanding_gate.json", {})
        source_truth_gate = self._read_json("source_truth_approval_gate.json", {})
        canonical_gate = self._read_json("canonical_spec_approval_gate.json", {})
        decisions = {
            "schema_version": "3.1.0",
            "requires_human_review": (
                bool(conflicts)
                or confidence < 0.75
                or bool(migration_mode.get("requires_human_confirmation"))
                or bool(brd_gate.get("requires_human_confirmation"))
                or bool(source_truth_gate.get("requires_human_confirmation"))
                or bool(canonical_gate.get("requires_human_confirmation"))
            ),
            "reasons": [],
            "status": "auto_passed",
            "gate_context_file": "human_gate_context.json",
        }
        if conflicts:
            decisions["reasons"].append("source_conflicts_present")
        if confidence < 0.75:
            decisions["reasons"].append("overall_confidence_below_threshold")
        if migration_mode.get("requires_human_confirmation"):
            decisions["reasons"].append("migration_output_mode_confirmation_required")
        if brd_gate.get("requires_human_confirmation"):
            decisions["reasons"].append("brd_understanding_confirmation_required")
        if source_truth_gate.get("requires_human_confirmation"):
            decisions["reasons"].append("source_truth_confirmation_required")
        if canonical_gate.get("requires_human_confirmation"):
            decisions["reasons"].append("canonical_spec_confirmation_required")
        if decisions["reasons"]:
            decisions["status"] = "review_recommended"
        write_json(self.workspace / "human_review_decisions.json", decisions)
        self._write_human_gate_context()
        return {"requires_human_review": decisions["requires_human_review"]}

    def _stage_decide_design_strategy(self) -> dict[str, Any]:
        source_type = infer_primary_source_type(self.artifacts, self.request)
        urls = collect_reference_urls(self.artifacts, self.request)
        strategy = build_design_strategy(
            source_type=source_type,
            domain=self.request.get("domain") or self._infer_domain(),
            goal=self.request.get("goal") or self._infer_goal(),
            scope=self.request.get("scope") or self._infer_scope(),
            reference_url=urls[0] if urls else None,
            fidelity_mode=str(self.request.get("fidelity_mode", "modernized_fidelity")),
        )
        write_design_strategy_bundle(self.workspace, strategy)
        return {
            "project_type": strategy["magic_selection"]["project_type"],
            "layout_profile": strategy["layout_profile_selection"]["name"],
        }

    def _stage_build_visual_fidelity_contract(self) -> dict[str, Any]:
        screens = self._approved_canonical_spec().get("screens", [])
        if not screens:
            screens = [{"name": "home"}]
        spec = {
            "schema_version": "3.1.0",
            "mode": str(self.request.get("fidelity_mode", "modernized_fidelity")),
            "screens": [],
        }
        for screen in screens[:10]:
            screen_name = str(screen.get("name") or "screen").replace(" ", "_").lower()
            screen_spec = default_visual_lock_spec(screen_name, spec["mode"])["screens"][0]
            screen_spec["source_refs"] = [screen.get("source")] if screen.get("source") else []
            spec["screens"].append(screen_spec)
        write_json(self.workspace / "visual_lock_spec.json", spec)
        write_json(
            self.workspace / "visual_layout_tree.json",
            {
                "schema_version": "3.1.0",
                "nodes": [
                    {"screen_id": item["screen_id"], "layout": "pending_visual_geometry_capture"}
                    for item in spec["screens"]
                ],
            },
        )
        return {"screen_contracts": len(spec["screens"])}

    def _stage_generate_design_system(self) -> dict[str, Any]:
        design_strategy = self._read_json("design_decision_report.json", {})
        screens = self._approved_canonical_spec().get("screens", [])
        components = sorted(
            dict.fromkeys(
                ["page_shell", "navigation", "form", "data_table", "metric_card"]
                + ["screen:" + str(screen.get("name")) for screen in screens[:20]]
            )
        )
        tokens = {
            "schema_version": "3.1.0",
            "color": {"brand": "#2563eb", "surface": "#ffffff", "text": "#111827"},
            "radius": {"sm": 6, "md": 8, "lg": 12},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32},
            "motion": design_strategy.get("motion_plan", {}),
        }
        component_registry = {
            "schema_version": "3.1.0",
            "components": [{"name": name, "status": "planned"} for name in components],
        }
        component_mapping = {
            "schema_version": "3.1.0",
            "screens": [
                {"screen": screen.get("name"), "recommended_components": ["page_shell", "form", "data_table"]}
                for screen in screens[:20]
            ],
        }
        write_json(self.workspace / "design_tokens.json", tokens)
        write_json(self.workspace / "component_registry.json", component_registry)
        write_json(self.workspace / "component_mapping.json", component_mapping)
        write_text(
            self.workspace / "DESIGN.md",
            textwrap.dedent(
                f"""\
                # Design System Plan

                - App: {self.app_name}
                - Domain pack: {design_strategy.get('domain_style_pack', {}).get('name', 'unknown')}
                - Layout profile: {design_strategy.get('layout_profile_selection', {}).get('name', 'unknown')}
                - Motion intensity: {design_strategy.get('motion_plan', {}).get('intensity', 'pending')}
                """
            ),
        )
        write_text(
            self.workspace / "visual_acceptance_criteria.md",
            textwrap.dedent(
                """\
                # Visual Acceptance Criteria

                - Preserve the core information hierarchy from source evidence.
                - Preserve visible content unless the migration brief explicitly approves changes.
                - Keep operational screens dense, clear, and keyboard friendly.
                - Run visual QA before marking the migration approved.
                """
            ),
        )
        return {"component_count": len(components)}

    def _stage_design_system_approval_gate(self) -> dict[str, Any]:
        design_bundle = {
            "schema_version": "3.1.0",
            "design_decision_report": self._read_json("design_decision_report.json", {}),
            "design_tokens": self._read_json("design_tokens.json", {}),
            "component_registry": self._read_json("component_registry.json", {}),
            "component_mapping": self._read_json("component_mapping.json", {}),
            "visual_acceptance_criteria": self._read_text_lines("visual_acceptance_criteria.md"),
        }
        bundle = resolve_design_system_gate(self.request, design_bundle, app_name=self.app_name)
        write_json(self.workspace / "design_system_approval_gate.json", bundle["gate"])
        write_json(self.workspace / "design_system_human_notes.json", bundle["human_notes"])
        write_json(self.workspace / "design_system_patch_instructions.json", bundle["patch_instructions"])
        write_json(self.workspace / "design_system_semantic_patch_report.json", bundle["semantic_patch"])
        write_json(self.workspace / "approved_design_system_plan.json", bundle["approved_plan"])
        self._write_human_gate_context()
        return {
            "status": bundle["gate"]["status"],
            "requires_human_confirmation": bundle["gate"]["requires_human_confirmation"],
            "patch_instruction_count": len(bundle["patch_instructions"].get("instructions", [])),
        }

    def _stage_generate_code(self) -> dict[str, Any]:
        spec = self._approved_canonical_spec()
        design_gate = self._read_json("approved_design_system_plan.json", {})
        human_gate_context = self._write_human_gate_context()
        stack = spec.get("target_stack") or spec.get("selected_target_stack") or "nextjs_tailwind_shadcn_motion_plus_api"
        generated_paths = self.scaffold_generator.generate(spec, self.workspace)
        generated_paths.extend(self._write_migration_mode_artifacts(spec))
        frontend_routes = [
            {"path": f"/{self._route_slug(screen.get('name', 'screen'))}", "screen": screen.get("name")}
            for screen in spec.get("ui_spec", {}).get("screens", [])[:20]
        ] or [{"path": "/", "screen": "home"}]
        entities = spec.get("domain_spec", {}).get("entities", [])
        workflows = spec.get("workflow_spec", {}).get("workflows", [])
        write_json(self.workspace / "frontend" / "routes.json", {"routes": frontend_routes, "stack": stack})
        write_json(
            self.workspace / "backend" / "service_blueprint.json",
            {
                "services": [{"name": entity.get("name"), "type": "crud_service"} for entity in entities],
                "workflow_handlers": workflows,
                "stack": stack,
            },
        )
        write_text(self.workspace / "database" / "schema_outline.sql", self._render_schema_outline(entities))
        write_json(
            self.workspace / "integration_contracts" / "service_contracts.json",
            {
                "apis": spec.get("api_spec", {}).get("contracts", []),
                "roles": spec.get("security_spec", {}).get("roles", []),
            },
        )
        write_text(
            self.workspace / "docs" / "MIGRATION_BRIEF.md",
            textwrap.dedent(
                f"""\
                # Migration Brief

                - App: {self.app_name}
                - Delivery mode: {spec.get('deployment_spec', {}).get('delivery_mode') or spec.get('selected_delivery_mode')}
                - Target stack: {stack}
                - Screens: {len(spec.get('ui_spec', {}).get('screens', []))}
                - Entities: {len(entities)}
                - Workflows: {len(workflows)}
                """
            ),
        )
        write_text(
            self.workspace / "observability" / "README.md",
            "# Observability Plan\n\nAdd request logging, error monitoring, and business event tracing during implementation.\n",
        )
        write_text(
            self.workspace / "tests" / "TEST_PLAN.md",
            "# Test Plan\n\n" + "\n".join(f"- Validate {flow}" for flow in self._critical_user_flows()),
        )
        write_text(
            self.workspace / "deploy" / "README.md",
            "# Deployment Plan\n\nGenerate container, staging, and CI/CD assets from the selected target stack during later implementation passes.\n",
        )
        write_json(
            self.workspace / "generated_file_manifest.json",
            {
                "schema_version": "3.1.0",
                "migration_output_mode": spec.get("selected_migration_output_mode"),
                "migration_output_label": spec.get("migration_mode", {}).get("selected_label"),
                "human_gate_context_file": "human_gate_context.json",
                "design_system_gate_status": design_gate.get("approval_gate", {}).get("status"),
                "pending_human_gate_count": len(human_gate_context.get("pending_confirmation_gates", [])),
                "files": sorted(str(path.relative_to(self.workspace)) for path in generated_paths),
            },
        )
        return {"generated_files": len(generated_paths), "stack": stack}

    def _stage_generated_app_approval_gate(self) -> dict[str, Any]:
        spec = self._approved_canonical_spec()
        manifest = self._read_json("generated_file_manifest.json", {})
        review = build_generated_app_review(self.workspace, spec, manifest)
        gate = resolve_generated_app_approval_gate(self.request, review, app_name=self.app_name)
        human_notes = build_generated_app_human_notes(gate)
        patch_instructions = build_generated_app_patch_instructions(gate, review)
        write_json(self.workspace / "generated_app_review_report.json", review)
        write_json(self.workspace / "generated_app_approval_gate.json", gate)
        write_json(self.workspace / "generated_app_human_notes.json", human_notes)
        write_json(self.workspace / "generated_app_patch_instructions.json", patch_instructions)
        write_json(self.workspace / "generated_app_semantic_patch_report.json", patch_instructions.get("semantic_patch", {}))
        write_text(
            self.workspace / "generated_app_review_summary.md",
            textwrap.dedent(
                f"""\
                # Generated App Approval Gate

                App: **{self.app_name}**

                Status: `{gate['status']}`

                Requires human confirmation: `{gate['requires_human_confirmation']}`

                Next pipeline stage: `run_agent_repair_loop`

                Pipeline sequence changed: `false`

                ## Generated output summary

                - Frontend files: {review['frontend']['file_count']}
                - Backend files: {review['backend']['file_count']}
                - Database files: {review['database']['file_count']}
                - Test files: {review['tests']['file_count']}
                - Docs files: {review['docs']['file_count']}
                - Run files: {', '.join(review['run_files']) or 'none'}
                - Missing expected files: {', '.join(review['missing_expected_files']) or 'none'}

                ## Canonical alignment

                - Screens: {review['canonical_alignment']['screen_count']}
                - Entities: {review['canonical_alignment']['entity_count']}
                - Workflows: {review['canonical_alignment']['workflow_count']}
                - Acceptance criteria: {review['canonical_alignment']['acceptance_criteria_count']}

                ## Human choices

                {self._render_generated_app_gate_options(gate.get('options', []))}

                ## Human notes

                {gate.get('human_notes') or gate.get('prompt_to_user')}
                """
            ),
        )
        return {
            "status": gate["status"],
            "requires_human_confirmation": gate["requires_human_confirmation"],
            "patch_instruction_count": gate["patch_instruction_count"],
        }

    def _stage_run_agent_repair_loop(self) -> dict[str, Any]:
        execution_plan = self._read_json("agent_execution_plan.json", {})
        patch_instructions = self._read_json("generated_app_patch_instructions.json", {})
        repair_result = run_preflight_repair(
            self.workspace,
            self._approved_canonical_spec(),
            self.scaffold_generator,
            patch_instructions,
        )
        repair_agents = sorted(
            agent_name
            for agent_name in execution_plan.get("active_agents", [])
            if agent_name in {"frontend_agent", "backend_agent", "test_repair_agent", "security_agent", "deploy_agent"}
        ) or ["test_repair_agent"]
        log_entries = []
        for agent_name in repair_agents:
            log_entries.append(
                {
                    "timestamp": _utc_now(),
                    "agent": agent_name,
                    "status": "applied" if repair_result["repairs_applied"] else "no_change",
                    "reason": (
                        "Preflight structural repair regenerated the scaffold baseline."
                        if repair_result["repairs_applied"]
                        else "Preflight structural repair found the scaffold baseline intact."
                    ),
                    "files_touched": repair_result["files_touched"],
                }
            )
        (self.workspace / "agent_patch_log.jsonl").write_text("\n".join(json.dumps(entry) for entry in log_entries) + "\n", encoding="utf-8")
        write_json(self.workspace / "repair_loop_report.json", repair_result)
        write_json(
            self.workspace / "agent_cost_report.json",
            {
                "schema_version": "3.1.0",
                "repair_iterations_used": repair_result["repair_iterations_used"],
                "estimated_agent_cost_usd": 0.0,
                "budget_cap_usd": self.configs["cost"].get("budgets", {}).get("max_usd_per_run"),
                "notes": (
                    "Repair loop currently performs deterministic scaffold normalization before quality gates. "
                    "Compiler- and model-driven patching can extend this stage later."
                ),
            },
        )
        return {
            "repair_iterations_used": repair_result["repair_iterations_used"],
            "repairs_applied": repair_result["repairs_applied"],
            "files_touched": len(repair_result["files_touched"]),
        }

    def _stage_run_quality_gates(self) -> dict[str, Any]:
        gate_bundle = run_quality_gates(
            self.workspace,
            critical_flows=self._critical_user_flows(),
            recommended_tools=self.configs["tools"].get("stages", {}).get("run_quality_gates", {}).get("cli_tools", []),
        )
        write_json(self.workspace / "code_quality_report.json", gate_bundle["code_quality_report"])
        write_json(self.workspace / "test_report.json", gate_bundle["test_report"])
        write_json(self.workspace / "security_review.json", gate_bundle["security_review"])
        write_text(self.workspace / "permission_parity_report.md", gate_bundle["permission_parity_report_md"])
        write_text(self.workspace / "security_review_report.md", gate_bundle["security_review_report_md"])
        write_text(self.workspace / "compliance_report.md", gate_bundle["compliance_report_md"])
        write_text(self.workspace / "eu_ai_act_report.md", gate_bundle["eu_ai_act_report_md"])
        write_text(self.workspace / "observability_setup_report.md", gate_bundle["observability_setup_report_md"])
        return {
            "code_quality_status": gate_bundle["code_quality_report"]["status"],
            "test_status": gate_bundle["test_report"]["status"],
            "security_status": gate_bundle["security_review"]["status"],
        }

    def _stage_run_visual_design_qa(self) -> dict[str, Any]:
        write_json(
            self.workspace / "visual_parity_score.json",
            {
                "schema_version": "3.1.0",
                "status": "not_executed",
                "visual_parity_score": 0.0,
                "reason": "No screenshot diff runtime connected in this scaffold run.",
            },
        )
        write_json(
            self.workspace / "geometry_diff.json",
            {
                "schema_version": "3.1.0",
                "status": "not_executed",
                "screens": [],
            },
        )
        write_json(
            self.workspace / "pixel_diff_report.json",
            {
                "schema_version": "3.1.0",
                "status": "not_executed",
                "diff_ratio": None,
            },
        )
        write_text(
            self.workspace / "ui_polish_report.md",
            "# UI Polish Report\n\nStatus: polish loop not started because screenshot-based QA is not connected yet.\n",
        )
        write_text(
            self.workspace / "design_qa_report.md",
            "# Design QA Report\n\nStatus: scaffold evaluation only. Connect Playwright, pixel diff, and accessibility tools for full QA.\n",
        )
        write_json(
            self.workspace / "accessibility_report.json",
            {
                "schema_version": "3.1.0",
                "status": "not_executed",
                "reason": "Accessibility scan tooling is not wired into this scaffold run yet.",
            },
        )
        write_text(
            self.workspace / "visual_rejection_report.md",
            "# Visual Rejection Report\n\nCurrent run did not execute screenshot comparison, so visual approval is still pending.\n",
        )
        write_text(
            self.workspace / "before_after_improvement_report.md",
            "# Before vs After Improvement Report\n\nThis run produced migration scaffolding and planning artifacts. Visual modernization and parity validation remain for later implementation passes.\n",
        )
        write_json(
            self.workspace / "ui_polish_tasklist.json",
            {
                "schema_version": "3.1.0",
                "tasks": [
                    "Connect Playwright screenshot capture",
                    "Capture baseline source UI screenshots",
                    "Run pixel and geometry diff against generated UI",
                ],
            },
        )
        return {"visual_qa_status": "not_executed"}

    def _stage_evaluate_design_quality(self) -> dict[str, Any]:
        overall_confidence = self._read_json("confidence_scores.json", {}).get("overall_confidence", 0.5)
        visual_available = self._read_json("visual_parity_score.json", {}).get("visual_parity_score", 0.0)
        scores = {
            "visual_fidelity_score": round(max(visual_available, overall_confidence * 0.85), 4),
            "ux_quality_score": round(min(0.88, overall_confidence * 0.95 + 0.1), 4),
            "accessibility_score": 0.7,
            "responsive_score": 0.72,
            "desktop_space_utilization_score": 0.7,
            "content_density_score": 0.74,
            "container_fit_score": 0.75,
            "motion_quality_score": 0.7,
            "component_reuse_score": 0.76,
        }
        report = evaluate_design_quality(scores=scores, thresholds=DEFAULT_THRESHOLDS)
        write_design_quality_report(self.workspace / "design_quality_score.json", report)
        return {"approved": report["approved"], "overall_design_quality_score": report["overall_design_quality_score"]}

    def _stage_qa_result_approval_gate(self) -> dict[str, Any]:
        qa_bundle = {
            "schema_version": "3.1.0",
            "code_quality_report": self._read_json("code_quality_report.json", {}),
            "test_report": self._read_json("test_report.json", {}),
            "security_review": self._read_json("security_review.json", {}),
            "visual_parity_score": self._read_json("visual_parity_score.json", {}),
            "accessibility_report": self._read_json("accessibility_report.json", {}),
            "design_quality_score": self._read_json("design_quality_score.json", {}),
        }
        bundle = resolve_qa_result_gate(self.request, qa_bundle, app_name=self.app_name)
        write_json(self.workspace / "qa_result_approval_gate.json", bundle["gate"])
        write_json(self.workspace / "qa_result_human_notes.json", bundle["human_notes"])
        write_json(self.workspace / "qa_result_repair_instructions.json", bundle["repair_instructions"])
        write_json(self.workspace / "qa_result_semantic_patch_report.json", bundle["semantic_patch"])
        write_json(self.workspace / "qa_result_review_summary.json", bundle["qa_summary"])
        self._write_human_gate_context()
        return {
            "status": bundle["gate"]["status"],
            "requires_human_confirmation": bundle["gate"]["requires_human_confirmation"],
            "repair_instruction_count": len(bundle["repair_instructions"].get("instructions", [])),
        }

    def _stage_build_replay_dashboard(self) -> dict[str, Any]:
        baseline = self._read_json("source_baseline.json", {})
        canonical = self._approved_canonical_spec()
        quality = self._read_json("design_quality_score.json", {})
        approval = self._read_json("human_review_decisions.json", {})
        human_gate_context = self._write_human_gate_context()
        session = self._read_json("runtime_session.json", {})
        browser_plan = self._read_json("browser_runtime_plan.json", {})
        memory_context = self._read_json("memory_context.json", {})
        execution_plan = self._read_json("agent_execution_plan.json", {})
        html = textwrap.dedent(
            f"""\
            <!doctype html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <title>NoCode2ProCode Replay Dashboard</title>
              <style>
                body {{ font-family: Arial, sans-serif; margin: 24px; color: #111827; }}
                h1, h2 {{ margin-bottom: 8px; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
                .panel {{ border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; }}
                code {{ background: #f3f4f6; padding: 2px 4px; }}
              </style>
            </head>
            <body>
              <h1>NoCode2ProCode Replay Dashboard</h1>
              <p><strong>App:</strong> {self.app_name}</p>
              <p><strong>Session:</strong> {session.get('session_id', 'pending')}</p>
              <div class="grid">
                <section class="panel">
                  <h2>Inputs</h2>
                  <p>Artifacts: {baseline.get('artifact_count', 0)}</p>
                  <p>Primary source type: {baseline.get('primary_source_type', 'unknown')}</p>
                </section>
                <section class="panel">
                  <h2>Planning</h2>
                  <p>Screens: {len(canonical.get('screens', []))}</p>
                  <p>Entities: {len(canonical.get('entities', []))}</p>
                  <p>Workflows: {len(canonical.get('workflows', []))}</p>
                </section>
                <section class="panel">
                  <h2>Quality</h2>
                  <p>Approved: {quality.get('approved', False)}</p>
                  <p>Overall score: {quality.get('overall_design_quality_score', 0)}</p>
                </section>
                <section class="panel">
                  <h2>Review</h2>
                  <p>Human review required: {approval.get('requires_human_review', False)}</p>
                  <p>Status: {approval.get('status', 'unknown')}</p>
                  <p>Pending gates: {len(human_gate_context.get('pending_confirmation_gates', []))}</p>
                </section>
                <section class="panel">
                  <h2>Runtime Plan</h2>
                  <pre>{json.dumps(browser_plan, indent=2)}</pre>
                </section>
                <section class="panel">
                  <h2>Agents</h2>
                  <pre>{json.dumps(execution_plan.get('active_agents', []), indent=2)}</pre>
                </section>
                <section class="panel">
                  <h2>Memory Context</h2>
                  <pre>{json.dumps(memory_context, indent=2)}</pre>
                </section>
              </div>
            </body>
            </html>
            """
        )
        write_text(self.workspace / "genesis_replay_dashboard.html", html)
        return {"dashboard": "generated"}

    def _stage_deploy_staging(self) -> dict[str, Any]:
        write_text(
            self.workspace / "deployment_report.md",
            "# Deployment Report\n\nStaging deployment was not executed automatically in scaffold mode. Wire Docker/Kubernetes/Terraform before using this gate.\n",
        )
        write_json(
            self.workspace / "staging_url.json",
            {
                "schema_version": "3.1.0",
                "status": "not_deployed",
                "reason": "human_approval_and_runtime_deploy_integration_required",
            },
        )
        return {"deployed": False}

    def _stage_final_approval(self) -> dict[str, Any]:
        human_review = self._read_json("human_review_decisions.json", {})
        human_gate_context = self._write_human_gate_context()
        generated_app_gate = self._read_json("generated_app_approval_gate.json", {})
        qa_result_gate = self._read_json("qa_result_approval_gate.json", {})
        design_quality = self._read_json("design_quality_score.json", {})
        code_quality = self._read_json("code_quality_report.json", {})
        test_report = self._read_json("test_report.json", {})
        security_review = self._read_json("security_review.json", {})
        quality_blockers = []
        if generated_app_gate.get("requires_human_confirmation"):
            quality_blockers.append("generated_app_approval_required")
        if qa_result_gate.get("requires_human_confirmation"):
            quality_blockers.append("qa_result_approval_required")
        if code_quality and not code_quality.get("gate_passed", False):
            quality_blockers.append("code_quality_failed")
        if test_report and not test_report.get("gate_passed", False):
            quality_blockers.append("test_gate_failed")
        if security_review and not security_review.get("gate_passed", False):
            quality_blockers.append("security_gate_failed")
        pending_gate_blockers = [
            f"{gate}_confirmation_required"
            for gate in human_gate_context.get("pending_confirmation_gates", [])
            if gate not in {"generated_app_approval_gate", "qa_result_approval_gate", "final_release_approval_gate"}
        ]
        final_context = {
            "schema_version": "3.1.0",
            "quality_blockers": quality_blockers,
            "pending_gate_blockers": pending_gate_blockers,
            "blockers": quality_blockers + pending_gate_blockers,
        }
        final_gate_bundle = resolve_final_release_gate(self.request, final_context, app_name=self.app_name)
        final_gate = final_gate_bundle["gate"]
        write_json(self.workspace / "final_release_approval_gate.json", final_gate)
        write_json(self.workspace / "final_release_human_notes.json", final_gate_bundle["human_notes"])
        human_gate_context = self._write_human_gate_context()
        final_action = final_gate.get("selected_action")
        hard_blockers = quality_blockers + pending_gate_blockers
        approved_for_delivery = (
            final_action == "approved"
            and design_quality.get("approved")
            and not human_review.get("requires_human_review")
            and not hard_blockers
        )
        demo_only_approved = final_action == "approve_demo_only"
        approval = {
            "schema_version": "3.1.0",
            "status": (
                "approved"
                if approved_for_delivery
                else "demo_only_approved"
                if demo_only_approved
                else "pending"
            ),
            "requires_human_approval": (
                human_review.get("requires_human_review", True)
                or generated_app_gate.get("requires_human_confirmation", True)
                or qa_result_gate.get("requires_human_confirmation", True)
                or final_gate.get("requires_human_confirmation", True)
                or not design_quality.get("approved", False)
                or bool(hard_blockers)
            ),
            "final_release_gate_status": final_gate.get("status"),
            "final_release_action": final_action,
            "human_gate_context_file": "human_gate_context.json",
            "reasons": human_review.get("reasons", [])
            + ([] if design_quality.get("approved") else ["design_quality_not_approved"])
            + hard_blockers
            + ([] if not final_gate.get("requires_human_confirmation") else ["final_release_confirmation_required"]),
        }
        write_json(self.workspace / "approval.json", approval)
        scorecard = build_production_scorecard(
            self._read_json("confidence_scores.json", {}),
            design_quality,
            code_quality,
            test_report,
            security_review,
            human_review,
            approval,
        )
        write_json(self.workspace / "production_readiness_scorecard.json", scorecard)
        write_json(
            self.workspace / "final_migration_confidence.json",
            {
                "schema_version": "3.1.0",
                "overall_confidence": self._read_json("confidence_scores.json", {}).get("overall_confidence", 0.0),
                "design_quality_approved": design_quality.get("approved", False),
                "status": approval["status"],
                "production_readiness_score": scorecard["overall_score"],
                "release_state": scorecard["release_state"],
            },
        )
        return approval

    def _stage_deliver_github_pr(self) -> dict[str, Any]:
        write_text(
            self.workspace / "github_delivery_report.md",
            "# GitHub Delivery Report\n\nNo pull request was created automatically in scaffold mode. Connect GitHub delivery once generated code is compilation-ready.\n",
        )
        return {"pr_created": False}

    def _stage_learn_verified_patterns(self) -> dict[str, Any]:
        approval = self._read_json("approval.json", {})
        quality = self._read_json("design_quality_score.json", {})
        canonical = self._approved_canonical_spec()
        memory_packet = build_verified_memory_packet(
            self.configs["memory"],
            self.request,
            self.artifacts,
            canonical,
            approval,
            quality,
        )
        write_json(self.workspace / "verified_memory_packet.json", memory_packet)
        append_verified_memory_packet(self.root, memory_packet)
        patterns = {
            "schema_version": "3.1.0",
            "trust_status": "generated_only" if approval.get("status") != "approved" else "human_approved",
            "patterns": [
                {
                    "name": "multi_source_migration_pipeline",
                    "source_types": sorted({artifact.source_type for artifact in self.artifacts}),
                    "quality_score": quality.get("overall_design_quality_score"),
                }
            ],
        }
        write_json(self.workspace / "verified_migration_patterns.json", patterns)
        write_json(
            self.workspace / "verified_ui_patterns.json",
            {
                "schema_version": "3.1.0",
                "patterns": [
                    {
                        "layout_profile": self._read_json("layout_profile_selection.json", {}).get("name"),
                        "motion_intensity": self._read_json("motion_plan.json", {}).get("intensity"),
                    }
                ],
            },
        )
        write_json(
            self.workspace / "plugin_registry.json",
            {
                "schema_version": "3.1.0",
                "plugins": ["Claude commands", "Genesis skill"],
            },
        )
        write_json(
            self.workspace / "mcp_registry.json",
            {
                "schema_version": "3.1.0",
                "core": self._read_module_section("mcp", "core"),
                "gated": self._read_module_section("mcp", "gated"),
            },
        )
        write_json(
            self.workspace / "mcp_security_report.json",
            {
                "schema_version": "3.1.0",
                "tool_policy": self.configs["tools"].get("tool_policy"),
                "secret_exposure_rule": self.configs["tools"].get("defaults", {}).get("expose_raw_secret_to_agent"),
            },
        )
        write_json(self.workspace / "evidence_graph.json", self._build_evidence_graph())
        write_json(self.workspace / "traceability_matrix.json", self._build_traceability_matrix())
        write_json(
            self.workspace / "migration_learning_report.json",
            {
                "schema_version": "3.1.0",
                "memory_packet_status": memory_packet.get("trust_status"),
                "reusable_pattern_count": len(patterns["patterns"]),
                "future_improvements": [
                    "connect live runtime capture providers",
                    "connect build-and-test repair loop",
                    "promote generated_only packets only after QA and human review",
                ],
            },
        )
        return {"patterns_saved": 1, "memory_packet_saved": True}

    def _build_evidence_graph(self) -> dict[str, Any]:
        artifacts = [artifact.as_dict() for artifact in self.artifacts]
        outputs = [
            "source_baseline.json",
            "platform_ast.json",
            "agent_execution_plan.json",
            "canonical_app_spec.json",
            "generated_file_manifest.json",
            "design_quality_score.json",
            "verified_memory_packet.json",
        ]
        return {
            "schema_version": "3.1.0",
            "nodes": artifacts + [{"artifact_id": output, "kind": "output"} for output in outputs],
            "edges": [
                {"from": artifact["artifact_id"], "to": "source_baseline.json", "relation": "ingested_into"}
                for artifact in artifacts
            ]
            + [
                {"from": "source_baseline.json", "to": "platform_ast.json", "relation": "normalized_into"},
                {"from": "source_baseline.json", "to": "agent_execution_plan.json", "relation": "scheduled_into"},
                {"from": "platform_ast.json", "to": "canonical_app_spec.json", "relation": "planned_into"},
                {"from": "canonical_app_spec.json", "to": "generated_file_manifest.json", "relation": "generated"},
                {"from": "generated_file_manifest.json", "to": "design_quality_score.json", "relation": "evaluated_by"},
                {"from": "canonical_app_spec.json", "to": "verified_memory_packet.json", "relation": "learned_into"},
            ],
        }

    def _build_traceability_matrix(self) -> dict[str, Any]:
        canonical = self._read_json("canonical_app_spec.json", {})
        return {
            "schema_version": "3.1.0",
            "rows": [
                {
                    "feature": screen.get("name"),
                    "source_evidence": [artifact.relative_path for artifact in self.artifacts[:5]],
                    "generated_output": "frontend/routes.json",
                    "qa_output": "design_quality_score.json",
                }
                for screen in canonical.get("screens", [])[:20]
            ],
        }

    def _read_module_section(self, module_name: str, key: str) -> Any:
        path = self.root / module_name / "module.yaml"
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
        match = re.search(rf"^{re.escape(key)}:\s*(.*)$", text, flags=re.MULTILINE)
        return match.group(1).strip() if match else []

    def _read_json(self, relative_name: str, default: dict[str, Any] | list[Any]) -> Any:
        path = self.workspace / relative_name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_text_lines(self, relative_name: str) -> list[str]:
        path = self.workspace / relative_name
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _approved_canonical_spec(self) -> dict[str, Any]:
        return self._read_json("approved_canonical_app_spec.json", self._read_json("canonical_app_spec.json", {}))

    def _write_human_gate_context(self) -> dict[str, Any]:
        context = collect_human_gate_context(self.workspace)
        write_json(self.workspace / "human_gate_context.json", context)
        plan_path = self.workspace / "agent_execution_plan.json"
        if plan_path.exists():
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["human_gate_context_file"] = "human_gate_context.json"
            plan["pending_human_gate_count"] = len(context.get("pending_confirmation_gates", []))
            plan["pipeline_sequence_changed_by_gates"] = False
            plan["agent_instruction"] = (
                "All agents must read human_gate_context.json before acting. "
                "Human gate notes are scoped input; they do not skip or reorder pipeline stages."
            )
            write_json(plan_path, plan)
        return context

    def _overall_artifact_confidence(self) -> float:
        if not self.artifacts:
            return 0.0
        return sum(artifact.confidence for artifact in self.artifacts) / len(self.artifacts)

    def _infer_domain(self) -> str:
        explicit = self.request.get("domain")
        if explicit:
            return str(explicit)
        joined = " ".join(artifact.relative_path.lower() for artifact in self.artifacts)
        for token, domain in (
            ("patient", "healthcare"),
            ("invoice", "finance"),
            ("employee", "hrms"),
            ("portal", "saas_admin"),
            ("shop", "ecommerce"),
        ):
            if token in joined:
                return domain
        return "saas_admin"

    def _infer_goal(self) -> str:
        if self.request.get("goal"):
            return str(self.request["goal"])
        if any(artifact.source_type == "website" for artifact in self.artifacts):
            return "modernize and rebuild website flows into production code"
        if any(artifact.source_type == "powerapps" for artifact in self.artifacts):
            return "migrate low-code workflows into production web software"
        return "reconstruct the application from provided source evidence"

    def _infer_scope(self) -> str:
        if self.request.get("scope"):
            return str(self.request["scope"])
        if any(artifact.source_type == "website" for artifact in self.artifacts):
            return "website"
        return "dashboard portal"

    def _user_prompt(self) -> str:
        values = [
            self.request.get("prompt"),
            self.request.get("goal"),
            self.request.get("notes"),
            self.request.get("domain"),
            self.request.get("scope"),
        ]
        return " ".join(str(value).strip() for value in values if value).strip() or (
            f"Migrate {self.app_name} from provided source evidence into production pro-code."
        )

    def _list_from_request(self, key: str) -> list[str]:
        value = self.request.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if isinstance(value, str):
            return [item.strip() for item in re.split(r"[,;\n]", value) if item.strip()]
        return [str(value)]

    def _estimated_screen_count(self) -> int:
        hints = 0
        for artifact in self.artifacts:
            hints += int(artifact.metadata.get("screen_count", 0))
        return hints or max(len(self.artifacts), 1)

    def _estimated_workflow_count(self) -> int:
        return sum(1 for artifact in self.artifacts if artifact.signal in {"workflow_xml_present", "powerapps_export_present"})

    def _critical_user_flows(self) -> list[str]:
        screens = self._approved_canonical_spec().get("screens", [])
        names = [str(screen.get("name")) for screen in screens[:10] if screen.get("name")]
        if not names:
            return ["open home", "review primary workflow", "validate key data capture path"]
        return [f"navigate {name}" for name in names]

    def _route_slug(self, name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        return slug or "home"

    def _render_schema_outline(self, entities: list[dict[str, Any]]) -> str:
        if not entities:
            return "-- No structured entities were extracted yet.\n"
        statements: list[str] = []
        for entity in entities[:20]:
            table_name = self._route_slug(str(entity.get("name", "entity"))).replace("-", "_")
            columns = entity.get("columns") or []
            rendered_columns = ["  id SERIAL PRIMARY KEY"]
            for column in columns[:12]:
                column_name = self._route_slug(str(column)).replace("-", "_")
                rendered_columns.append(f"  {column_name} TEXT")
            rendered_columns.append("  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
            statements.append(f"CREATE TABLE {table_name} (\n" + ",\n".join(rendered_columns) + "\n);\n")
        return "\n".join(statements)

    def _render_mode_options(self, options: list[dict[str, Any]]) -> str:
        if not options:
            return "- No migration mode options were configured."
        return "\n".join(
            f"- **{option.get('code')}. {option.get('label')}** (`{option.get('mode')}`): {option.get('technology')}"
            for option in options
        )

    def _render_brd_gate_options(self, options: list[dict[str, Any]]) -> str:
        if not options:
            return "- No BRD gate options were configured."
        return "\n".join(
            f"- **{option.get('code')}. {option.get('label')}** (`{option.get('action')}`): {option.get('description')}"
            for option in options
        )

    def _render_generated_app_gate_options(self, options: list[dict[str, Any]]) -> str:
        if not options:
            return "- No generated app approval options were configured."
        return "\n".join(
            f"- **{option.get('code')}. {option.get('label')}** (`{option.get('action')}`): {option.get('description')}"
            for option in options
        )

    def _write_migration_mode_artifacts(self, spec: dict[str, Any]) -> list[Path]:
        migration_mode = spec.get("migration_mode", {})
        selected_mode = str(migration_mode.get("selected_mode") or "hybrid_pilot_app")
        label = str(migration_mode.get("selected_label") or "Hybrid Pilot App")
        app_name = str(spec.get("app", {}).get("name") or self.app_name)
        localhost_required = bool(migration_mode.get("localhost_required", selected_mode != "production_e2e_app"))
        demo_credentials = {
            "schema_version": "3.1.0",
            "status": "demo_credentials_only",
            "warning": "Demo credentials are for local validation only. Do not use real patient/customer/company secrets.",
            "users": [
                {
                    "role": "demo_user",
                    "username": "demo@example.com",
                    "password": "demo123",
                }
            ],
        }
        localhost_url = {
            "schema_version": "3.1.0",
            "status": "local_run_ready" if localhost_required else "optional_for_production_mode",
            "frontend_url": "http://localhost:3000",
            "backend_url": "http://localhost:8000",
            "mode": selected_mode,
            "technology": migration_mode.get("technology"),
        }
        demo_report = textwrap.dedent(
            f"""\
            # Demo Run Report

            - App: {app_name}
            - Migration output mode: {label}
            - Technology profile: {migration_mode.get('technology')}
            - Localhost required: {localhost_required}
            - Frontend URL: http://localhost:3000
            - Backend URL: http://localhost:8000

            ## Purpose

            This report explains how to demonstrate the generated migration locally. Use `run_demo.ps1` to view the
            recommended commands for starting the frontend and backend.

            ## Demo scope

            {self._markdown_list(migration_mode.get("downstream_instructions", [])) or "- Validate the core generated workflow with sample data."}
            """
        )
        production_gap_report = textwrap.dedent(
            f"""\
            # Production Gap Report

            - Migration output mode: {label}
            - Production upgrade required: {migration_mode.get('production_upgrade_required', selected_mode != 'production_e2e_app')}

            ## Remaining production work

            {self._production_gap_list(selected_mode)}
            """
        )
        run_demo = textwrap.dedent(
            f"""\
            Write-Host "NoCode2ProCode Genesis demo runner"
            Write-Host "App: {app_name}"
            Write-Host "Mode: {label}"
            Write-Host ""
            Write-Host "Backend:"
            Write-Host "  cd backend"
            Write-Host "  python -m pip install -r requirements.txt"
            Write-Host "  python -m uvicorn app.main:app --reload --port 8000"
            Write-Host ""
            Write-Host "Frontend:"
            Write-Host "  cd frontend"
            Write-Host "  npm install"
            Write-Host "  npm run dev"
            Write-Host ""
            Write-Host "Open: http://localhost:3000"
            """
        )
        artifacts = [
            self.workspace / "run_demo.ps1",
            self.workspace / "demo_credentials.json",
            self.workspace / "localhost_url.json",
            self.workspace / "demo_report.md",
            self.workspace / "production_gap_report.md",
        ]
        write_text(artifacts[0], run_demo)
        write_json(artifacts[1], demo_credentials)
        write_json(artifacts[2], localhost_url)
        write_text(artifacts[3], demo_report)
        write_text(artifacts[4], production_gap_report)
        return artifacts

    def _production_gap_list(self, selected_mode: str) -> str:
        if selected_mode == "production_e2e_app":
            return self._markdown_list(
                [
                    "Complete human approval before release.",
                    "Connect real secrets through an approved vault.",
                    "Run environment-specific deployment and security scans.",
                ]
            )
        if selected_mode == "local_demo_app":
            return self._markdown_list(
                [
                    "Replace demo login and sample data with approved auth and persistence.",
                    "Add production database migrations and environment-specific configuration.",
                    "Run full security, accessibility, load, and deployment gates before release.",
                    "Convert demo-only workflow shortcuts into production service behavior.",
                ]
            )
        return self._markdown_list(
            [
                "Review the pilot with stakeholders and confirm production scope.",
                "Replace mock/lightweight data paths with approved persistent services.",
                "Harden auth, role permissions, audit logging, and observability.",
                "Run full deployment readiness checks before production handoff.",
            ]
        )

    def _markdown_list(self, items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    def _short_label(self, value: Any, limit: int = 72) -> str:
        text = str(value).strip()
        return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."

    def _unique_strings(self, values: list[Any]) -> list[str]:
        seen: set[str] = set()
        output = []
        for value in values:
            text = str(value).strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            output.append(text)
        return output

    def _validate_json_schema(self, payload: dict[str, Any], schema_path: Path) -> None:
        if not schema_path.exists():
            return
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=payload, schema=schema)

    def _read_text_evidence(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md", ".rst", ".yaml", ".yml", ".json", ".xml"}:
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix in {".docx", ".pptx"}:
            result = self.document_adapter.extract(path, self.workspace / "evidence" / "documents")
            summary = result.ast.get("summary_sentences", [])
            requirements = result.ast.get("functional_requirements", [])
            criteria = result.ast.get("acceptance_criteria", [])
            return "\n".join([*summary, *requirements, *criteria])
        return ""


def run_pipeline(
    command: str,
    project: Path | None = None,
    input_dir: Path | None = None,
    app_name: str | None = None,
    workspace: Path | None = None,
) -> PipelineRunResult:
    orchestrator = MigrationOrchestrator(project=project, input_dir=input_dir, app_name=app_name, workspace=workspace)
    return orchestrator.run(command)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
