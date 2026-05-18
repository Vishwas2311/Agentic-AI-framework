# skills/ — Claude Code Custom Skills

Claude Code skill definitions for Genesis. Skills are custom `/` commands that Claude Code IDE loads, allowing you to invoke Genesis pipeline operations directly from the IDE command palette.

```
skills/
└── nocode2procode-genesis/     Genesis skill set for Claude Code IDE
```

---

## What Skills Do

Skills extend Claude Code with Genesis-specific commands. When you type `/genesis-migrate` or a similar command in Claude Code, the IDE invokes the corresponding skill definition here.

These complement the `.claude/commands/` folder — commands are slash commands for Claude conversations, skills are the deeper IDE integration layer.

---

## Relationship to Other Configuration

| Folder | Purpose |
|---|---|
| `skills/` | Claude Code IDE skill definitions (this folder) |
| `.claude/commands/` | Claude slash commands for conversations |
| `.genesis/` | Pipeline governance YAML (read by Python orchestrator) |

---

## Note

This folder was part of the original project setup and is maintained by the Genesis install script (`install_genesis_all.ps1`). Do not delete it — the Claude Code IDE extension reads it at startup.
