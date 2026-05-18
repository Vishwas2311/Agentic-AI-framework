# Code Review Discipline

Use this reference during `generate_code`, `generated_app_approval_gate`, `run_agent_repair_loop`, and `pr_delivery_gate`.

OpenHands is strong at treating code review as a disciplined engineering pass. In Genesis, apply that discipline locally:

- Review generated code for correctness, maintainability, readability, security, accessibility, and testability.
- Tie review comments to specific files and evidence, not taste alone.
- Prefer small focused repairs over broad rewrites.
- Verify that generated app scripts, environment examples, seeds, and run instructions match the selected stack.
- Reject placeholder screens, unused generated files, unreachable routes, and dead scripts.
- Do not accept a review summary as proof. Link every critical claim to a file, command, screenshot, API result, or gate decision.

Generated-code approval should be blocked when code review finds:

- invalid packages or impossible imports;
- runtime-only UI library violations;
- schema/API/type/seed mismatches;
- auth-sensitive routes without protection;
- hidden dependency on external services when local demo mode is required;
- generated tests that are scaffolded but not executable.
