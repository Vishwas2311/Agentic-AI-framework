# Repair Loop And Package Hygiene Rules

Inspired by local repair-loop, validation manifest, package audit, and evidence-card patterns.

## Repair Discipline

Every failed check should produce a focused `fix_task.json` with:

- failed check name
- severity
- exact error/log excerpt
- artifact paths
- suspected files
- required fix
- rerun commands

Builder/repair agents must fix only the implicated files unless the evidence proves broader scope is required.

## Learning Discipline

Save a verified learning only when it includes:

- original failure
- applied fix
- rerun command
- passing evidence
- reusable condition

## Package Hygiene

Installer packages must exclude:

- `.git`, `.venv`, `node_modules`, `.genesis_runtime`
- `.env`, `.env.local`, keys, certs, traces, logs
- `workspace`, generated apps, screenshots, test-results, build outputs

Required package artifact:

- `package_cleanliness_report.json`
