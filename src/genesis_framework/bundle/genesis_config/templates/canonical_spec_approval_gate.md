<!-- GENESIS PIPELINE TEMPLATE — Canonical Spec Approval Gate (Stage 24) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- canonical_spec_approval_gate data, then display verbatim. Never shorten. -->

## Canonical Spec Approval Gate
**{{APP_NAME}}** · Stage 24 · Gate 10 of 14

This is the final human checkpoint before code generation begins. The canonical application spec locks every screen, API, entity, workflow, and acceptance criterion that Genesis will generate. Review it carefully — changes after this gate require a repair loop.

---

**Spec summary:**

| Area | Count |
|------|-------|
| Screens | {{SPEC_SCREEN_COUNT}} |
| API endpoints | {{SPEC_API_COUNT}} |
| Data fields | {{SPEC_FIELD_COUNT}} |
| Test cases | {{SPEC_TEST_COUNT}} |
| Estimated generation tokens | {{TOKENS_GENERATION}} |

---

**A. Approve — lock spec and begin code generation** `RECOMMENDED`
`Lock Spec` · `Start Generation` · `Point of No Easy Return`
The canonical spec is complete and correct. Genesis begins generating all application files: screens, APIs, components, data layer, DevOps, tests, and documentation.

---

**B. Add a missing requirement**
`Add Requirement` · `Expand Scope`
Something is missing from the spec. Describe the missing screen, API, entity, field, or rule and Genesis will add it before generation starts. Token estimate will update.

---

**C. Remove an out-of-scope item**
`Remove Item` · `Reduce Scope` · `Fewer tokens`
The spec includes something that should not be built. Tell Genesis what to remove and it will update the spec and token estimate before generation starts.

---

**D. Reject or edit spec**
`Edit Spec` · `Patch Before Generation`
Provide correction notes and Genesis will continue with a patched approved canonical spec.

---

Which decision? **(A / B / C / D)**
