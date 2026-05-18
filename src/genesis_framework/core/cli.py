from __future__ import annotations

import importlib.resources
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from genesis_framework.core.config import GenesisPaths, find_project_root, load_all, load_yaml
from genesis_framework.design.design_quality import evaluate_design_quality, write_design_quality_report
from genesis_framework.design.design_strategy import build_design_strategy, write_design_strategy, write_design_strategy_bundle
from genesis_framework.core.flow import stages_for_entrypoint, validate_flow
from genesis_framework.core.intake import DEFAULT_INPUT_DIR_NAME, default_input_dir, ensure_input_directory
from genesis_framework.core.orchestrator import run_pipeline
from genesis_framework.core.policy import is_tool_allowed
from genesis_framework.core.runtime_sessions import list_runtime_sessions, read_runtime_session
from genesis_framework.delivery.stack_resolver import resolve_stack_decision
from genesis_framework.design.visual_fidelity import write_visual_lock_spec
from genesis_framework.core.workspace import create_migration_workspace

app = typer.Typer(help="NoCode2ProCode by TrustEngines CLI. Internal engine codename: Genesis.")
console = Console()

_GENESIS_MARKER = Path.home() / ".genesis_pro_installed"


def _auto_install_if_first_run() -> None:
    """Silently run full install on first ever invocation."""
    if _GENESIS_MARKER.exists():
        return
    console.print("\n[bold cyan]Welcome to Genesis Pro! Running first-time setup...[/bold cyan]\n")
    _run_install(Path.cwd())
    _GENESIS_MARKER.touch()


def _run_install(target: Path) -> None:
    import shutil
    bundle_root = Path(__file__).parent.parent / "bundle"
    copies = [
        (bundle_root / "genesis_config",  target / ".genesis"),
        (bundle_root / "templates",       target / "templates"),
        (bundle_root / "skills",          target / "skills"),
        (bundle_root / "config",          target / "config"),
        (bundle_root / "claude_commands", target / ".claude" / "commands"),
    ]
    files = [
        (bundle_root / "package.json", target / "package.json"),
        (bundle_root / "CLAUDE.md",    target / "CLAUDE.md"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            console.print(f"  [green]✓[/green] {dst.relative_to(target)}")
    for src, dst in files:
        if src.exists():
            shutil.copy2(src, dst)
            console.print(f"  [green]✓[/green] {dst.name}")
    node_ok = shutil.which("node") is not None
    if node_ok and (target / "package.json").exists():
        console.print("  Running [cyan]npm install[/cyan]...")
        result = subprocess.run(["npm", "install"], cwd=target, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("  [green]✓[/green] npm packages installed")
    claude_ok = shutil.which("claude") is not None
    if not claude_ok:
        console.print("  [yellow]⚠[/yellow]  Claude Code not found — install from [link]https://claude.ai/code[/link]")
    console.print("\n[bold green]Setup complete![/bold green]")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    _auto_install_if_first_run()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def launch() -> None:
    """Open the Genesis dashboard in your browser."""
    with importlib.resources.path("genesis_framework.static", "dashboard.html") as html_path:
        url = html_path.as_uri()
    console.print(f"[green]Opening Genesis dashboard...[/green] {url}")
    webbrowser.open(url)


@app.command()
def install(
    target: Path = typer.Option(Path.cwd, "--target", "-t", help="Directory to install Genesis into"),
) -> None:
    """Full E2E installation: copy all configs, templates, skills, and Claude commands."""
    import shutil
    import sys

    target = Path(target).resolve()
    console.print(f"\n[bold cyan]Genesis E2E Installer[/bold cyan]")
    console.print(f"Installing into: [yellow]{target}[/yellow]\n")

    bundle_root = Path(__file__).parent.parent / "bundle"

    copies = [
        (bundle_root / "genesis_config", target / ".genesis"),
        (bundle_root / "templates",      target / "templates"),
        (bundle_root / "skills",         target / "skills"),
        (bundle_root / "config",         target / "config"),
        (bundle_root / "claude_commands", target / ".claude" / "commands"),
    ]
    files = [
        (bundle_root / "package.json", target / "package.json"),
        (bundle_root / "CLAUDE.md",    target / "CLAUDE.md"),
    ]

    for src, dst in copies:
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            console.print(f"  [green]✓[/green] {dst.relative_to(target)}")
        else:
            console.print(f"  [yellow]⚠[/yellow]  {src.name} not found in bundle, skipping")

    for src, dst in files:
        if src.exists():
            shutil.copy2(src, dst)
            console.print(f"  [green]✓[/green] {dst.relative_to(target)}")

    # Check Claude Code
    console.print("\n[bold]Checking dependencies...[/bold]")
    claude_ok = shutil.which("claude") is not None
    console.print(f"  {'[green]✓[/green]' if claude_ok else '[red]✗[/red]'} Claude Code CLI {'found' if claude_ok else 'NOT found — install from https://claude.ai/code'}")

    # Check Node.js and run npm install
    node_ok = shutil.which("node") is not None
    console.print(f"  {'[green]✓[/green]' if node_ok else '[red]✗[/red]'} Node.js {'found' if node_ok else 'NOT found — install from https://nodejs.org'}")

    if node_ok and (target / "package.json").exists():
        console.print("\n  Running [cyan]npm install[/cyan]...")
        import subprocess as _sp
        result = _sp.run(["npm", "install"], cwd=target, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("  [green]✓[/green] npm install complete")
        else:
            console.print(f"  [red]✗[/red] npm install failed: {result.stderr[:200]}")

    console.print("\n[bold green]Genesis installation complete![/bold green]")
    console.print("Run [cyan]genesis launch[/cyan] to open the dashboard.\n")


@app.command()
def validate(project: Optional[Path] = typer.Option(None, "--project", "-p")) -> None:
    """Validate Genesis framework configuration."""
    root = (project or find_project_root()).resolve()
    configs = load_all(root)
    errors = validate_flow(configs["flow"])
    if errors:
        for error in errors:
            console.print(f"[red]ERROR[/red] {error}")
        raise typer.Exit(code=1)
    console.print(f"[green]Genesis config valid[/green] at {root}")


@app.command()
def plan(
    entrypoint: str = typer.Option("genesis-migrate", "--entrypoint", "-e"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Show the ordered Genesis flow stages."""
    root = (project or find_project_root()).resolve()
    flow = load_yaml(GenesisPaths(root).flow_file)
    table = Table(title=f"NoCode2ProCode by TrustEngines flow: {entrypoint}")
    table.add_column("#", justify="right")
    table.add_column("Stage")
    table.add_column("Skill")
    table.add_column("Produces")
    for index, stage in enumerate(stages_for_entrypoint(flow, entrypoint), start=1):
        table.add_row(str(index), stage.name, stage.skill or "-", ", ".join(stage.produces))
    console.print(table)


@app.command()
def check_tool(
    stage: str = typer.Argument(...),
    tool: str = typer.Argument(...),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Check whether a tool is allowed during a stage."""
    root = (project or find_project_root()).resolve()
    tools = load_yaml(GenesisPaths(root).tools_file)
    decision = is_tool_allowed(tools, stage, tool)
    color = "green" if decision.allowed else "red"
    console.print(f"[{color}]{'ALLOW' if decision.allowed else 'DENY'}[/{color}] {decision.reason}")
    if not decision.allowed:
        raise typer.Exit(code=2)


@app.command()
def route(
    signal: str = typer.Argument(..., help="Routing signal, for example figma_url_present"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Show the configured Genesis tools/stages/prompt for an input signal."""
    root = (project or find_project_root()).resolve()
    routing = load_yaml(GenesisPaths(root).routing_file)
    source_routing = routing.get("source_routing", {})
    if signal not in source_routing:
        console.print(f"[red]Unknown route signal[/red] {signal}")
        raise typer.Exit(code=1)
    route_config = source_routing[signal]
    table = Table(title=f"Genesis route: {signal}")
    table.add_column("Field")
    table.add_column("Value")
    for key in ("tools", "stages", "prompt"):
        value = route_config.get(key, [])
        if isinstance(value, list):
            value = ", ".join(value)
        table.add_row(key, str(value))
    console.print(table)


@app.command("install-plan")
def install_plan(
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Show Genesis tool installation modes and commands."""
    root = (project or find_project_root()).resolve()
    install = load_yaml(GenesisPaths(root).install_file)
    table = Table(title="Genesis Installation Plan")
    table.add_column("Tool")
    table.add_column("Mode")
    table.add_column("Reason / Commands")
    for tool, spec in install.get("tools", {}).items():
        commands = spec.get("commands", [])
        reason = spec.get("reason", "")
        detail = reason or "; ".join(commands)
        table.add_row(tool, spec.get("install_mode", "unknown"), detail)
    console.print(table)


@app.command("install")
def install(
    profile: str = typer.Option("LocalE2E", "--profile", help="Core, LocalE2E, FullLocal, or AuditOnly."),
    allow_system_install: bool = typer.Option(False, "--allow-system-install", help="Allow winget installs for missing system tools."),
    include_deploy: bool = typer.Option(False, "--include-deploy", help="Include Docker/Kubernetes/Terraform checks and installs."),
    include_security_tools: bool = typer.Option(False, "--include-security-tools", help="Attempt optional local security scanner installs."),
    include_power_platform: bool = typer.Option(False, "--include-power-platform", help="Attempt Microsoft Power Platform CLI install."),
    no_claude_assets: bool = typer.Option(False, "--no-claude-assets", help="Skip copying Genesis Claude command/skill files."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print and report planned install work without installing packages."),
    print_only: bool = typer.Option(False, "--print-only", help="Only print the one-line installer command."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the one-command Genesis local installer from inside the CLI."""
    root = (project or find_project_root()).resolve()
    installer = root / "install-genesis.ps1"
    if not installer.exists():
        console.print(f"[red]Installer missing[/red] {installer}")
        raise typer.Exit(code=1)

    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(installer),
        "-Profile",
        profile,
    ]
    if allow_system_install:
        command.append("-AllowSystemInstall")
    if include_deploy:
        command.append("-IncludeDeploy")
    if include_security_tools:
        command.append("-IncludeSecurityTools")
    if include_power_platform:
        command.append("-IncludePowerPlatform")
    if no_claude_assets:
        command.append("-NoClaudeAssets")
    if dry_run:
        command.append("-DryRun")

    console.print("[cyan]Genesis one-command installer[/cyan]")
    console.print(" ".join(f'"{part}"' if " " in part else part for part in command))
    if print_only:
        return

    completed = subprocess.run(command, cwd=root)
    if completed.returncode != 0:
        raise typer.Exit(code=completed.returncode)


@app.command()
def init_workspace(
    app_name: str = typer.Argument(..., help="Source app name, for example Customer Portal"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Create a Genesis output workspace for a migration."""
    root = (project or find_project_root()).resolve()
    ensure_input_directory(root)
    workspace = create_migration_workspace(root, app_name)
    console.print(f"[green]Created migration workspace[/green] {workspace}")
    console.print(f"[green]Input folder ready[/green] {default_input_dir(root)}")


@app.command()
def estimate(
    app_name: str = typer.Argument("sample-app"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Create a placeholder dry-run estimate report for a migration."""
    root = (project or find_project_root()).resolve()
    workspace = create_migration_workspace(root, app_name)
    report = workspace / "estimation_report.md"
    report.write_text(
        "# Genesis Estimation Report\n\n"
        "Status: scaffold estimate only. Connect adapters and discovery evidence to compute real values.\n\n"
        "- Confidence: pending discovery\n"
        "- Unsupported items: pending discovery\n"
        "- LLM cost: pending telemetry\n",
        encoding="utf-8",
    )
    console.print(f"[green]Wrote[/green] {report}")


@app.command()
def visual_lock(
    screen_id: str = typer.Argument(..., help="Screen id, for example login"),
    mode: str = typer.Option("modernized_fidelity", "--mode", help="exact_fidelity or modernized_fidelity"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Create a starter visual_lock_spec.json for a screen."""
    root = (project or find_project_root()).resolve()
    target = output or (root / "visual_lock_spec.json")
    path = write_visual_lock_spec(target, screen_id, mode)
    console.print(f"[green]Wrote visual lock spec[/green] {path}")


@app.command("design-strategy")
def design_strategy(
    source_type: str = typer.Option("screenshot", "--source-type", help="screenshot, figma, website, component, lowcode"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Business domain, for example healthcare portal"),
    goal: Optional[str] = typer.Option(None, "--goal", help="Goal, for example lead generation, sales, dashboard"),
    scope: Optional[str] = typer.Option(None, "--scope", help="component or website"),
    reference_url: Optional[str] = typer.Option(None, "--reference-url", help="Reference website URL if using inspiration"),
    fidelity_mode: str = typer.Option("modernized_fidelity", "--fidelity-mode", help="exact_fidelity or modernized_fidelity"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Create a smart UI strategy for Magic, UI/UX Pro Max, and Motion."""
    root = (project or find_project_root()).resolve()
    strategy = build_design_strategy(
        source_type=source_type,
        domain=domain,
        goal=goal,
        scope=scope,
        reference_url=reference_url,
        fidelity_mode=fidelity_mode,
    )
    target = output or (root / "design_decision_report.json")
    path = write_design_strategy(target, strategy)
    bundle = write_design_strategy_bundle(target.parent, strategy)
    magic = strategy["magic_selection"]
    motion = strategy["motion_plan"]
    console.print(f"[green]Wrote design strategy[/green] {path}")
    console.print("[green]Wrote design bundle[/green] " + ", ".join(item.name for item in bundle.values()))
    console.print(
        "Magic: "
        f"{magic['project_type']} / {magic['creation_type']} / {magic['website_goal']} | "
        f"Motion: {motion['intensity']}"
    )


@app.command("design-quality")
def design_quality(
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Create a starter design quality rejection report."""
    root = (project or find_project_root()).resolve()
    target = output or (root / "design_quality_score.json")
    report = evaluate_design_quality()
    path = write_design_quality_report(target, report)
    console.print(f"[green]Wrote design quality report[/green] {path}")
    console.print(f"Approved: {report['approved']} | Next action: {report['next_action']}")


@app.command("stack-resolve")
def stack_resolve(
    prompt: str = typer.Argument(..., help="User migration intent or summary."),
    brd_stack: Optional[str] = typer.Option(None, "--brd-stack", help="Detected BRD stack, for example streamlit"),
    domain: Optional[str] = typer.Option(None, "--domain", help="Business domain, for example healthcare portal"),
    scope: Optional[str] = typer.Option(None, "--scope", help="UI scope, for example dashboard portal or public website"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Resolve delivery mode and target stack from user intent and BRD hints."""
    root = (project or find_project_root()).resolve()
    target = output or (root / "stack_decision_report.json")
    decision = resolve_stack_decision(prompt, brd_stack=brd_stack, domain=domain, scope=scope)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    console.print(f"[green]Wrote stack decision[/green] {target}")
    console.print(
        "Delivery: "
        f"{decision['selected_delivery_mode']} | Stack: {decision['selected_target_stack']} | "
        f"Approval required: {decision['human_approval_required']}"
    )


def _run_named_pipeline(
    command: str,
    app_name: Optional[str],
    input_dir: Optional[Path],
    workspace: Optional[Path],
    project: Optional[Path],
) -> None:
    root = (project or find_project_root()).resolve()
    result = run_pipeline(
        command,
        project=root,
        input_dir=(input_dir or default_input_dir(root)),
        app_name=app_name,
        workspace=workspace,
    )
    console.print(f"[green]Pipeline complete[/green] {command} -> {result.target_stage}")
    console.print(f"Workspace: {result.workspace}")
    console.print(f"Approval status: {result.approval_status} | Human approval required: {result.approval_required}")


@app.command("sessions")
def sessions(project: Optional[Path] = typer.Option(None, "--project", "-p")) -> None:
    """List known migration runtime sessions."""
    root = (project or find_project_root()).resolve()
    items = list_runtime_sessions(root)
    table = Table(title="NoCode2ProCode Runtime Sessions")
    table.add_column("Session")
    table.add_column("App")
    table.add_column("Status")
    table.add_column("Last Stage")
    table.add_column("Workspace")
    for item in items:
        table.add_row(
            str(item.get("session_id", "")),
            str(item.get("app_name", "")),
            str(item.get("status", "")),
            str(item.get("last_completed_stage", "")),
            str(item.get("workspace", "")),
        )
    console.print(table)


@app.command("status")
def status(
    workspace: Path = typer.Argument(..., help="Migration workspace path."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Show the current runtime session and approval status for a workspace."""
    _ = (project or find_project_root()).resolve()
    session = read_runtime_session(workspace.resolve())
    if not session:
        console.print(f"[red]No runtime session found[/red] for {workspace}")
        raise typer.Exit(code=1)
    approval_path = workspace.resolve() / "approval.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8")) if approval_path.exists() else {}
    console.print(f"[green]Session[/green] {session.get('session_id')}")
    console.print(f"App: {session.get('app_name')}")
    console.print(f"Status: {session.get('status')}")
    console.print(f"Last completed stage: {session.get('last_completed_stage')}")
    console.print(f"Approval: {approval.get('status', 'not_started')}")


@app.command("discover")
def discover(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run intake, discovery, extraction, and runtime-evidence scaffolding from migration inputs."""
    _run_named_pipeline("discover", app_name, input_dir, workspace, project)


@app.command("migrate")
@app.command("genesis-migrate")
def migrate(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the full NoCode2ProCode migration pipeline from intake through replay and pattern learning."""
    _run_named_pipeline("migrate", app_name, input_dir, workspace, project)


@app.command("plan-migration")
@app.command("plan-run")
def plan_run(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the planning path through source truth, IR, canonical spec, and visual-contract setup."""
    _run_named_pipeline("plan", app_name, input_dir, workspace, project)


@app.command("generate")
def generate_run(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the pipeline through deterministic scaffold generation."""
    _run_named_pipeline("generate", app_name, input_dir, workspace, project)


@app.command("qa")
def qa_run(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the pipeline through scaffold QA and design-quality reporting."""
    _run_named_pipeline("qa", app_name, input_dir, workspace, project)


@app.command("replay")
def replay_run(
    app_name: Optional[str] = typer.Option(None, "--app-name", help="Override app name inferred from inputs."),
    input_dir: Optional[Path] = typer.Option(None, "--input-dir", help=f"Input directory. Defaults to ./{DEFAULT_INPUT_DIR_NAME}"),
    workspace: Optional[Path] = typer.Option(None, "--workspace", help="Existing workspace to reuse."),
    project: Optional[Path] = typer.Option(None, "--project", "-p"),
) -> None:
    """Run the pipeline through replay-dashboard generation."""
    _run_named_pipeline("replay", app_name, input_dir, workspace, project)


if __name__ == "__main__":
    app()
