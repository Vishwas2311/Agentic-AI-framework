# NoCode2ProCode by TrustEngines Prerequisites

This file lists what must be installed for a high-quality Genesis run. Claude Code can execute the framework, but it should not silently install tools that require credentials, licenses, global system changes, or cloud permissions.

## Required Runtime

- Python 3.11+
- Git
- Node.js 20+
- Claude Code
- Claude Code permission to read this project

## Required Python Setup

Use the one-command installer from the project root:

```powershell
cd "C:\Users\Vishwas\Desktop\AI\1.Python Work Space\NoCode2ProCode-Genesis"
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1
```

This creates `.venv`, installs Genesis with local E2E libraries, installs Node/Playwright/visual QA packages, installs Chromium, copies Claude command/skill assets, validates the framework, and writes `.genesis_runtime/install_report.json` plus `.genesis_runtime/install_report.md`.

If the machine is missing Python, Git, Node, or npm and company policy allows `winget`, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -AllowSystemInstall
```

For the Claude Code natural-language/bootstrap flow, type:

```text
install Genesis E2E
```

Claude Code should then run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-genesis.ps1 -Profile FullLocal -AllowSystemInstall -IncludeSecurityTools
```

Deployment tools are skipped by default for local product work. Add `-IncludeDeploy` only when you really need Docker/Kubernetes/Terraform delivery tooling.

The installer opens the project-local `Full User Manual - Genesis.html` after a successful install. Add `-NoLaunchManual` when installing on a headless or terminal-only machine.

DOCX BRD extraction support is included in the local E2E profile through `python-docx`, so Claude/Genesis can inspect BRD documents without falling into mismatched global `pip` installs.

## Recommended Claude Code Setup

Copy or symlink:

- `.claude/commands/*` into the project `.claude/commands/`
- `skills/nocode2procode-genesis` into the Claude Code skills directory when your Claude Code setup supports skills

Keep `CLAUDE.md` in the project root. It is the governance entrypoint for Claude Code.

## Core MCPs

Install/configure these first:

- GitHub MCP
- Playwright MCP
- Figma MCP
- Firecrawl MCP
- Context7 MCP
- E2B MCP
- PostgreSQL MCP in read-only mode
- Qdrant or pgvector memory access

## Optional/Gated MCPs

Configure only when needed:

- Docker MCP
- Kubernetes MCP
- Terraform MCP
- Jira MCP
- Linear MCP
- Slack MCP
- Datadog MCP
- Burp Suite MCP

## Required CLI Tools For Production Quality

- Playwright
- OpenAPI Generator
- AsyncAPI Generator
- Pact
- Schemathesis
- Testcontainers
- Semgrep
- CodeQL
- Gitleaks
- Syft
- Grype
- Trivy
- OSV Scanner
- OWASP ZAP
- axe-core
- k6 or Locust

## Platform-Specific Tools

- Mendix Model SDK for Mendix extraction
- Power Platform CLI for PowerApps `.pa.yaml` and Power Fx extraction
- Appian Deployment API credentials for Appian export packages
- OutSystems APIs and runtime access for OutSystems evidence-first migration

## Human Approval Required

Genesis must stop for approval before:

- Using production credentials
- Deploying infrastructure
- Running destructive tools
- Processing unmasked sensitive data
- Accepting low-confidence mappings
- Using protected/licensed media

## Genesis Install Plan

Tool installation behavior is controlled by:

```text
.genesis/genesis.install.yaml
```

Genesis classifies tools as:

- `auto_install_safe`
- `approval_required`
- `manual_setup_required`
- `enterprise_optional`

Claude Code should not silently install global tools, MCP servers, cloud tools, infrastructure tools, or anything needing credentials.
