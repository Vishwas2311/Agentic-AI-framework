# Agent Repair Prompt

Apply small patches only.

Rules:

- Keep ownership boundaries.
- Do not rewrite unrelated files.
- Do not remove evidence or reports.
- Run focused tests after edits.
- Record patch summary in `agent_patch_log.jsonl`.

