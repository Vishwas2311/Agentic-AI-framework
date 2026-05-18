# Action Observation Trajectory

Use this reference in every stage that runs commands, writes major artifacts, starts runtimes, tests the app, or repairs failures.

OpenHands' core development value is the Action -> Observation record. In Genesis, this becomes migration evidence:

```json
{
  "stage": "run_quality_gates",
  "action_type": "command",
  "action": "npx playwright test --workers=1",
  "cwd": "workspace/output/app",
  "started_at": "...",
  "completed_at": "...",
  "exit_code": 0,
  "observation_type": "test_result",
  "stdout_excerpt": "...",
  "stderr_excerpt": "...",
  "artifacts": ["functional_sanity_report.json"],
  "risk_level": "low",
  "skill_context": ["genesis-pro-quality", "genesis-openhands-dev-quality"]
}
```

Genesis must write:

- `migration_trajectory.jsonl`
- `migration_trajectory.zip`
- `action_observation_audit.json`
- `active_skill_context.json`

Approval should fail when a PASS claim lacks a matching action/observation record.
