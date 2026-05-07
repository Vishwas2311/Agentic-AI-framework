# Genesis Visual Fidelity Playbook

## Problem

Many app-generation systems recreate functionality but produce generic or visually poor UI because screenshots/Figma files are treated as inspiration instead of a contract.

## Genesis Fix

Use a closed-loop visual compiler:

```text
Screenshot / Figma / Website
→ Visual Evidence Extractor
→ Layout Geometry Tree
→ Design Token Extractor
→ Component Matcher
→ Visual Lock Spec
→ UI/UX Pro Max
→ 21st.dev Magic / shadcn
→ Claude Code implementation
→ Playwright screenshot
→ Pixel/geometry/a11y diff
→ UI Polish Agent loop
```

## Modes

### Exact Fidelity

Match source layout as closely as possible. Use for screenshot clone, Figma clone, or regulated app parity.

### Modernized Fidelity

Preserve information architecture, workflow, visible content, and layout intent while improving visual quality.

## Required Files

- `visual_layout_tree.json`
- `design_tokens.json`
- `component_mapping.json`
- `visual_lock_spec.json`
- `source_screenshots/`
- `generated_screenshots/`
- `geometry_diff.json`
- `pixel_diff_report.json`
- `ui_polish_report.md`

## Rule

Do not create a visually inspired UI. Create a UI that first satisfies the visual lock spec, then improves only within allowed modernization rules.

