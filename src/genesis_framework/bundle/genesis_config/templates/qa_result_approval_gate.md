<!-- GENESIS PIPELINE TEMPLATE — QA Result Approval Gate (Stage 36) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- qa_result_approval_gate data, then display verbatim. Never shorten.    -->

## QA Result Approval Gate
**{{APP_NAME}}** · Stage 36 · Gate 13 of 14

The full QA suite has completed. Review results before approving delivery.

---

**QA results:**

| Check | Result |
|-------|--------|
| Unit tests passed | {{UNIT_PASSED}} |
| Unit tests failed | {{UNIT_FAILED}} |
| E2E tests passed | {{E2E_PASSED}} |
| E2E tests failed | {{E2E_FAILED}} |
| Lighthouse score | {{LIGHTHOUSE_SCORE}} |
| Performance target URL | {{PERF_TARGET_URL}} |
| Runtime performance status | {{RUNTIME_PERF_STATUS}} |
| Runtime launch status | {{RUNTIME_LAUNCH_STATUS}} |
| QA evidence manifest | {{QA_EVIDENCE_STATUS}} |
| Console/page error status | {{CONSOLE_ERROR_STATUS}} |
| Accessibility violations | {{A11Y_VIOLATIONS}} |
| Security issues | {{SECURITY_ISSUES}} |
| Design quality score | {{DESIGN_SCORE}} |
| Overall QA status | **{{QA_GATE_STATUS}}** |

---

**A. Approve — proceed to delivery** `RECOMMENDED`
`Approve QA` · `Create PR + Deploy Staging`
All quality gates pass. Genesis creates the GitHub PR, generates the DevOps hand-off package, and deploys to staging.

---

**B. Approve with known issues**
`Approve with Waivers` · `Document Exceptions`
QA passes with minor known issues that are acceptable to ship. Describe the waived issues and Genesis will document them in the PR body and deployment notes.

---

**C. Trigger repair loop**
`Repair Loop` · `Fix Failures` · `Re-run QA`
One or more QA checks failed and must be fixed before delivery. Describe the priority fixes (or leave blank to auto-prioritize) and Genesis runs the full repair + re-QA cycle.

---

**D. Waive a specific failing check**
`Waive Check` · `Narrow Exception`
A specific check is failing for an acceptable reason. Tell Genesis which check to waive and why. The waiver is documented in the QA report.

---

Which decision? **(A / B / C / D)**
