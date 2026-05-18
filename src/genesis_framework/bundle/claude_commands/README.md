# .claude/commands â€” Claude Code Slash Commands

Custom slash commands available in Claude Code when working inside this project. Each file defines one command that Claude Code registers as `/command-name`.

## Commands

### Migration Commands

| Command | File | Purpose |
|---------|------|---------|
| `/genesis-migrate` | `genesis-migrate.md` | Run full 46-stage Genesis migration pipeline |
| `/nocode2procode-migrate` | `nocode2procode-migrate.md` | Alias for genesis-migrate with NoCode2ProCode branding |
| `/nocode2procode-discover` | `nocode2procode-discover.md` | Discover and classify source platform inputs only (no generation) |

### Planning & Estimation

| Command | File | Purpose |
|---------|------|---------|
| `/genesis-estimate` | `genesis-estimate.md` | Estimate migration complexity, effort, and cost before committing |
| `/nocode2procode-estimate` | `nocode2procode-estimate.md` | Same as genesis-estimate with richer output format |
| `/nocode2procode-plan` | `nocode2procode-plan.md` | Generate a detailed migration plan document |

### Generation

| Command | File | Purpose |
|---------|------|---------|
| `/nocode2procode-generate` | `nocode2procode-generate.md` | Run code generation stages only (skips extraction if spec exists) |
| `/nocode2procode-figma` | `nocode2procode-figma.md` | Generate UI from a Figma URL input |
| `/nocode2procode-image` | `nocode2procode-image.md` | Generate UI from screenshot/image input |
| `/nocode2procode-website` | `nocode2procode-website.md` | Migrate a live website URL to Next.js |

### QA & Reporting

| Command | File | Purpose |
|---------|------|---------|
| `/genesis-qa` | `genesis-qa.md` | Run quality gates on an existing workspace output |
| `/nocode2procode-qa` | `nocode2procode-qa.md` | Run QA with full visual + accessibility + security checks |
| `/nocode2procode-report` | `nocode2procode-report.md` | Generate human-readable migration report from workspace |
| `/genesis-replay` | `genesis-replay.md` | Replay migration from a saved session (for debugging) |
| `/nocode2procode-replay` | `nocode2procode-replay.md` | Same as genesis-replay with richer UI |

### Deployment

| Command | File | Purpose |
|---------|------|---------|
| `/nocode2procode-deploy` | `nocode2procode-deploy.md` | Deploy generated app to staging (Vercel / Railway) |

### Setup

| Command | File | Purpose |
|---------|------|---------|
| `/install-genesis-e2e` | `install-genesis-e2e.md` | Full E2E framework install â€” equivalent to running `install-genesis.ps1` |
| `/nocode2procode-install` | `nocode2procode-install.md` | Install with NoCode2ProCode preset configuration |

## How Commands Work

Each `.md` file contains:
1. A short description line (shown in `/help`)
2. The exact instructions Claude Code follows when the command is invoked
3. References to the relevant Genesis config files and pipeline stages

Commands never bypass CLAUDE.md rules â€” they are shorthand for common workflows, not overrides.

## Adding a New Command

Create `commands/your-command.md` with:
```markdown
# /your-command

Short description shown in /help.

[Instructions for Claude Code...]
```

Claude Code picks it up automatically on next session start.

