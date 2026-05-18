<!-- GENESIS PIPELINE TEMPLATE — Generated App Approval Gate (Stage 31) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- generated_app_approval_gate data, then display verbatim. Never shorten. -->

## Generated App Approval Gate
**{{APP_NAME}}** · Stage 31 · Gate 12 of 14

Code generation is complete. Review the generated application before the QA and repair loop begins.

---

**Generation summary:**

| Metric | Value |
|--------|-------|
| Build status | {{BUILD_STATUS}} |
| Files generated | {{FILES_GENERATED}} |
| Tests passing | {{TESTS_PASSED}} |
| Tests failing | {{TESTS_FAILED}} |
| Tokens used | {{TOKENS_ACTUAL}} |
| Generation time | {{GENERATION_TIME}} |

---

**A. Approve — start QA loop** `RECOMMENDED`
`Approve Build` · `Begin QA + Repair Loop`
The generated app is structurally correct. Genesis starts the automated QA loop: unit tests, E2E tests, Lighthouse, accessibility, security scan, and visual QA. Any failures trigger the repair loop automatically.

---

**B. Reject — explain what is wrong**
`Reject Build` · `Describe Issues`
The generated app has fundamental problems that automated QA cannot fix. Describe what is wrong and Genesis will apply targeted patches before re-generation.

---

**C. Add extra input or missing requirement**
`Add Requirement` · `Expand Scope`
Something was not generated that should have been. Describe the missing screen, API, component, or behavior and Genesis will patch the generation before QA begins.

---

Which decision? **(A / B / C)**
