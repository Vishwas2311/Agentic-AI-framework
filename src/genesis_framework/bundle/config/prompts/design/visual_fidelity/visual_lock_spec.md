# Visual Lock Spec Prompt

You are building the Genesis visual fidelity contract.

## Goal

Convert screenshots, Figma frames, Stitch designs, or website evidence into a testable `visual_lock_spec.json`.

## Modes

### exact_fidelity

Match the source visual layout as closely as possible. Visual parity wins over creative redesign.

### modernized_fidelity

Preserve information architecture, content, workflow, hierarchy, and layout intent while improving visual quality.

## Required Output

For each screen include:

- screen_id
- source_refs
- must_match
- allowed_changes
- blocked_changes
- thresholds

## Rules

- Do not create a merely "inspired by" UI.
- Treat the source image/design as a visual contract.
- Do not remove visible content.
- Do not change navigation model unless allowed.
- Do not change primary layout unless allowed.
- Set measurable thresholds for spacing, pixel diff, and visual parity.

