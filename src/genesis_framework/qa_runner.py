from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator


CORE_REQUIRED_FILES = [
    "frontend/package.json",
    "frontend/app/page.tsx",
    "backend/app/main.py",
    "database/migration.sql",
    "tests/api/test_health.py",
    "tests/playwright/smoke.spec.ts",
    "docs/ARCHITECTURE_SUMMARY.md",
]

JSON_ARTIFACTS = [
    "canonical_app_spec.json",
    "generated_file_manifest.json",
    "frontend/package.json",
    "frontend/routes.json",
    "backend/service_blueprint.json",
]


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    details: str
    data: dict[str, Any]

    @property
    def gate_passed(self) -> bool:
        return self.status in {"passed", "warning", "skipped"}

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_quality_gates(
    workspace: Path,
    critical_flows: list[str],
    recommended_tools: list[str] | None = None,
) -> dict[str, Any]:
    recommended_tools = recommended_tools or []
    code_checks = [
        _check_required_files(workspace),
        _check_json_artifacts(workspace),
        _check_dependency_manifests(workspace),
        _check_frontend_routes(workspace),
        _check_python_syntax(workspace),
        _check_ruff(workspace),
    ]
    test_checks = [
        _check_backend_health(workspace),
    ]
    security_checks = [
        _check_secret_scan(workspace),
    ]

    code_quality_report = _build_gate_report(
        "code_quality",
        code_checks,
        extra={
            "recommended_tools": recommended_tools,
            "workspace": str(workspace),
        },
    )
    test_report = _build_gate_report(
        "tests",
        test_checks,
        extra={
            "critical_flows": critical_flows,
            "workspace": str(workspace),
        },
    )
    security_review = _build_gate_report(
        "security",
        security_checks,
        extra={"workspace": str(workspace)},
    )

    permission_parity = _permission_parity_report(critical_flows)
    compliance = _compliance_report(code_quality_report, test_report, security_review)
    eu_ai_act = _eu_ai_act_report(security_review)
    observability = _observability_report(workspace)

    return {
        "code_quality_report": code_quality_report,
        "test_report": test_report,
        "security_review": security_review,
        "permission_parity_report_md": permission_parity,
        "security_review_report_md": _render_markdown_report(
            "Security Review Report",
            security_checks,
            footer="This pass runs a local secret-pattern sweep. Static application security tools can plug into this gate later.",
        ),
        "compliance_report_md": compliance,
        "eu_ai_act_report_md": eu_ai_act,
        "observability_setup_report_md": observability,
    }


def _build_gate_report(name: str, checks: list[CheckResult], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    summary = _summarize_checks(checks)
    return {
        "schema_version": "3.1.0",
        "gate": name,
        "status": summary["status"],
        "gate_passed": summary["gate_passed"],
        "summary": summary,
        "checks": [check.as_dict() for check in checks],
        **(extra or {}),
    }


def _summarize_checks(checks: list[CheckResult]) -> dict[str, Any]:
    counts = {"passed": 0, "failed": 0, "warning": 0, "skipped": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    if counts["failed"]:
        status = "failed"
    elif counts["warning"] or counts["skipped"]:
        status = "passed_with_warnings"
    else:
        status = "passed"
    return {
        "status": status,
        "gate_passed": counts["failed"] == 0,
        "counts": counts,
    }


def _check_required_files(workspace: Path) -> CheckResult:
    missing = [path for path in CORE_REQUIRED_FILES if not (workspace / path).exists()]
    if missing:
        return CheckResult(
            name="required_files",
            status="failed",
            details="Missing required scaffold outputs.",
            data={"missing": missing},
        )
    return CheckResult(
        name="required_files",
        status="passed",
        details="Core scaffold files are present.",
        data={"checked": CORE_REQUIRED_FILES},
    )


def _check_json_artifacts(workspace: Path) -> CheckResult:
    invalid: list[dict[str, str]] = []
    present = 0
    for relative_path in JSON_ARTIFACTS:
        path = workspace / relative_path
        if not path.exists():
            continue
        present += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            invalid.append({"path": relative_path, "error": str(exc)})
    if invalid:
        return CheckResult(
            name="json_artifacts",
            status="failed",
            details="One or more JSON artifacts are invalid.",
            data={"invalid": invalid},
        )
    if present == 0:
        return CheckResult(
            name="json_artifacts",
            status="warning",
            details="No JSON artifacts were available for validation.",
            data={"checked": JSON_ARTIFACTS},
        )
    return CheckResult(
        name="json_artifacts",
        status="passed",
        details="JSON artifacts parsed successfully.",
        data={"checked_count": present},
    )


def _check_dependency_manifests(workspace: Path) -> CheckResult:
    package_path = workspace / "frontend" / "package.json"
    requirements_path = workspace / "backend" / "requirements.txt"
    missing = []
    if not package_path.exists():
        missing.append("frontend/package.json")
    if not requirements_path.exists():
        missing.append("backend/requirements.txt")
    if missing:
        return CheckResult(
            name="dependency_manifests",
            status="failed",
            details="Expected dependency manifests are missing.",
            data={"missing": missing},
        )

    package = json.loads(package_path.read_text(encoding="utf-8"))
    dependencies = package.get("dependencies", {})
    scripts = package.get("scripts", {})
    requirements = requirements_path.read_text(encoding="utf-8")
    manifest_gaps = []
    for dep in ("next", "react", "react-dom"):
        if dep not in dependencies:
            manifest_gaps.append(f"frontend dependency missing: {dep}")
    for script in ("dev", "build", "start"):
        if script not in scripts:
            manifest_gaps.append(f"frontend script missing: {script}")
    for requirement in ("fastapi", "uvicorn"):
        if requirement not in requirements:
            manifest_gaps.append(f"backend requirement missing: {requirement}")
    if manifest_gaps:
        return CheckResult(
            name="dependency_manifests",
            status="warning",
            details="Dependency manifests exist but are missing some expected entries.",
            data={"issues": manifest_gaps},
        )
    return CheckResult(
        name="dependency_manifests",
        status="passed",
        details="Dependency manifests contain the expected baseline entries.",
        data={},
    )


def _check_frontend_routes(workspace: Path) -> CheckResult:
    routes_path = workspace / "frontend" / "routes.json"
    if not routes_path.exists():
        return CheckResult(
            name="frontend_routes",
            status="warning",
            details="Route manifest was not generated.",
            data={"path": "frontend/routes.json"},
        )
    routes = json.loads(routes_path.read_text(encoding="utf-8")).get("routes", [])
    missing_pages = []
    for route in routes:
        path_value = str(route.get("path", "/"))
        page = workspace / "frontend" / "app" / "page.tsx" if path_value == "/" else workspace / "frontend" / "app" / path_value.strip("/") / "page.tsx"
        if not page.exists():
            missing_pages.append({"route": path_value, "expected_file": str(page.relative_to(workspace))})
    if missing_pages:
        return CheckResult(
            name="frontend_routes",
            status="failed",
            details="Some route declarations do not have matching page files.",
            data={"missing_pages": missing_pages},
        )
    return CheckResult(
        name="frontend_routes",
        status="passed",
        details="Route manifest matches generated page files.",
        data={"route_count": len(routes)},
    )


def _check_python_syntax(workspace: Path) -> CheckResult:
    checked: list[str] = []
    errors: list[dict[str, str]] = []
    for path in list((workspace / "backend").rglob("*.py")) + list((workspace / "tests" / "api").rglob("*.py")):
        checked.append(str(path.relative_to(workspace)))
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            errors.append(
                {
                    "path": str(path.relative_to(workspace)),
                    "line": str(exc.lineno or 0),
                    "message": exc.msg,
                }
            )
    if errors:
        return CheckResult(
            name="python_syntax",
            status="failed",
            details="Generated Python files contain syntax errors.",
            data={"errors": errors},
        )
    return CheckResult(
        name="python_syntax",
        status="passed",
        details="Generated Python files compile successfully.",
        data={"checked": checked},
    )


def _check_ruff(workspace: Path) -> CheckResult:
    if importlib.util.find_spec("ruff") is None:
        return CheckResult(
            name="ruff_check",
            status="skipped",
            details="Ruff is not installed in the active environment.",
            data={},
        )
    targets = [str(workspace / "backend"), str(workspace / "tests" / "api")]
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "F,E9,I", *targets],
        capture_output=True,
        text=True,
        cwd=workspace,
        check=False,
    )
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return CheckResult(
            name="ruff_check",
            status="warning",
            details="Ruff found structural issues in generated Python files.",
            data={"output": output},
        )
    return CheckResult(
        name="ruff_check",
        status="passed",
        details="Ruff structural checks passed.",
        data={"output": output},
    )


def _check_backend_health(workspace: Path) -> CheckResult:
    if importlib.util.find_spec("fastapi") is None:
        return CheckResult(
            name="backend_health",
            status="skipped",
            details="FastAPI is not installed in the active environment, so the backend smoke test was skipped.",
            data={},
        )
    try:
        from fastapi.testclient import TestClient  # type: ignore
    except Exception as exc:  # pragma: no cover - environment-specific
        return CheckResult(
            name="backend_health",
            status="skipped",
            details="FastAPI test client is unavailable in the active environment.",
            data={"error": str(exc)},
        )

    with _workspace_import_path(workspace):
        importlib.invalidate_caches()
        for module_name in [name for name in list(sys.modules) if name == "backend" or name.startswith("backend.")]:
            sys.modules.pop(module_name, None)
        try:
            module = importlib.import_module("backend.app.main")
            client = TestClient(module.app)
            response = client.get("/health")
        except Exception as exc:
            return CheckResult(
                name="backend_health",
                status="failed",
                details="Generated backend health endpoint could not be exercised.",
                data={"error": str(exc)},
            )
        finally:
            for module_name in [name for name in list(sys.modules) if name == "backend" or name.startswith("backend.")]:
                sys.modules.pop(module_name, None)

    if response.status_code != 200:
        return CheckResult(
            name="backend_health",
            status="failed",
            details="Generated backend responded with a non-200 health status.",
            data={"status_code": response.status_code, "body": response.text},
        )
    payload = response.json()
    if payload.get("status") != "ok":
        return CheckResult(
            name="backend_health",
            status="failed",
            details="Generated backend health payload does not match the expected contract.",
            data={"payload": payload},
        )
    return CheckResult(
        name="backend_health",
        status="passed",
        details="Generated backend health endpoint responded correctly.",
        data={"payload": payload},
    )


def _check_secret_scan(workspace: Path) -> CheckResult:
    pattern = re.compile(
        r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{6,}['\"]"
    )
    findings: list[dict[str, str]] = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".json", ".md", ".ts", ".tsx", ".js", ".sql", ".yml", ".yaml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                findings.append({"path": str(path.relative_to(workspace)), "line": str(line_number)})
                if len(findings) >= 20:
                    break
        if len(findings) >= 20:
            break
    if findings:
        return CheckResult(
            name="secret_scan",
            status="failed",
            details="Potential hard-coded secret patterns were found in generated files.",
            data={"findings": findings},
        )
    return CheckResult(
        name="secret_scan",
        status="passed",
        details="No obvious hard-coded secret patterns were found in generated files.",
        data={},
    )


def _permission_parity_report(critical_flows: list[str]) -> str:
    flows = "\n".join(f"- Review role coverage for: {flow}" for flow in critical_flows) or "- No critical flows were declared."
    return (
        "# Permission Parity Report\n\n"
        "This local pass checks that the migration declares critical flows and leaves role-parity review visible for humans.\n\n"
        "## Follow-up Areas\n"
        f"{flows}\n"
    )


def _compliance_report(
    code_quality_report: dict[str, Any],
    test_report: dict[str, Any],
    security_review: dict[str, Any],
) -> str:
    return (
        "# Compliance Report\n\n"
        f"- Code quality gate: {code_quality_report['status']}\n"
        f"- Test gate: {test_report['status']}\n"
        f"- Security gate: {security_review['status']}\n\n"
        "This local run confirms baseline engineering hygiene. Domain-specific compliance evidence still needs policy-specific controls and human review.\n"
    )


def _eu_ai_act_report(security_review: dict[str, Any]) -> str:
    return (
        "# EU AI Act Report\n\n"
        f"- Local security gate: {security_review['status']}\n"
        "- This migration pipeline is currently evaluated as a software-generation workflow that still requires human approval before production use.\n"
        "- Keep source-truth decisions, replay artifacts, and approval logs attached to regulated deliveries.\n"
    )


def _observability_report(workspace: Path) -> str:
    observability_doc = workspace / "observability" / "README.md"
    status = "present" if observability_doc.exists() else "missing"
    return (
        "# Observability Setup Report\n\n"
        f"- Observability plan document: {status}\n"
        "- Health endpoint validation is included in the local quality gate when FastAPI is available.\n"
        "- Add structured logs, tracing, and error monitoring providers before production release.\n"
    )


def _render_markdown_report(title: str, checks: list[CheckResult], footer: str = "") -> str:
    rows = "\n".join(f"- {check.name}: {check.status} - {check.details}" for check in checks)
    return f"# {title}\n\n{rows}\n\n{footer}\n".strip() + "\n"


@contextmanager
def _workspace_import_path(workspace: Path) -> Iterator[None]:
    workspace_str = str(workspace)
    sys.path.insert(0, workspace_str)
    try:
        yield
    finally:
        if workspace_str in sys.path:
            sys.path.remove(workspace_str)
