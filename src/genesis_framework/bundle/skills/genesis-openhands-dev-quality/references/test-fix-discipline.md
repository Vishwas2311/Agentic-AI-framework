# Test-Fix Discipline

Use this reference during `run_agent_repair_loop`, `run_quality_gates`, and `qa_result_approval_gate`.

OpenHands' useful test-fix pattern is simple: failing observations drive repairs. Genesis should preserve that discipline:

- Start from the exact failing command, exit code, stdout/stderr excerpt, browser/server log, screenshot, or trace.
- Fix only the files implicated by the failure unless the evidence proves a wider cause.
- Do not delete, weaken, skip, or rewrite tests merely to make a gate pass.
- If a test expectation must change, require BRD/canonical-spec evidence or a recorded human gate decision.
- Rerun the failed check first, then rerun full QAOS.
- Store the repair handoff in `fix_task.json`.

`fix_task.json` must include:

- failing command and cwd;
- exit code;
- stdout/stderr excerpt;
- server/browser logs;
- suspected files;
- required fix;
- rerun command;
- evidence artifact paths.
