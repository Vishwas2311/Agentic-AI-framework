# Accessibility And Design Quality Rules

Inspired by local UI/UX Pro Max, accessibility, screen-reader, and design-system skills.

## Design Director Rules

- Preserve source workflows and information architecture.
- Improve weak spacing, hierarchy, contrast, empty states, loading states, and responsive behavior.
- Match density to domain: dashboards and operational portals should be task-first, not marketing-style.
- Create measurable visual acceptance criteria before code generation.
- Do not approve attractive UI that breaks functional requirements.

## Accessibility Rules

- Forms need labels, errors, keyboard access, focus states, and useful validation messages.
- Dialogs, menus, selects, and tabs need keyboard behavior and accessible names.
- Tables and dashboards need scanable structure and meaningful headings.
- Reduced-motion mode must be honored.
- Axe/browser accessibility checks are required for production evidence.

## Required Outputs

- `design_decision_report.json`
- `design_tokens.json`
- `component_registry.json`
- `visual_acceptance_criteria.md`
- `design_quality_score.json`
- `visual_rejection_report.json`
