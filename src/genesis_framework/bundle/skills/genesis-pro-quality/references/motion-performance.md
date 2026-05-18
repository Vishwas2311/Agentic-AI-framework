# Motion Performance Rules

Inspired by local GSAP performance and Antigravity motion-performance skills.

## Purpose

Motion should clarify state, hierarchy, feedback, or navigation. It must not slow task completion or create layout instability.

## Rules

- Prefer transform and opacity.
- Avoid continuous animation of layout-heavy properties such as width, height, top, left, margin, padding, or large blur effects.
- Do not mix multiple animation systems in the same component unless explicitly justified.
- Avoid scroll-linked JavaScript loops without clear stop conditions.
- Provide reduced-motion fallback for bespoke motion.
- Use subtle motion for enterprise dashboards, healthcare, fintech, admin, and operations software.

## Required Outputs

- `motion_plan.json`
- `motion_purpose_contract.json`
- `motion_runtime_invariant_report.json`
- `design_quality_score.json`

## QAOS Checks

Flag code that animates layout properties, lacks reduced-motion handling, or adds decorative motion without a purpose contract.
