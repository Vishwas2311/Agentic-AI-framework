# UI Polish Loop Prompt

Use this prompt after Playwright screenshots and visual diff reports exist.

## Inputs

- source screenshot
- generated screenshot
- visual_lock_spec.json
- geometry_diff.json
- pixel_diff_report.json
- accessibility_report.json

## Task

Patch only the UI differences that matter under the visual lock spec.

## Rules

- Fix layout before color.
- Fix typography before decoration.
- Fix missing/extra visible content before animation.
- Do not change app logic unless visual behavior depends on it.
- Re-run Playwright screenshot after every patch.

## Output

Append results to `ui_polish_report.md`.

