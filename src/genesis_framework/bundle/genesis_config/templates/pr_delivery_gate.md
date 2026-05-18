<!-- GENESIS PIPELINE TEMPLATE — PR Delivery Gate (Stage 41) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- pr_delivery_gate data, then display verbatim. Never shorten.           -->

## PR Delivery Gate
**{{APP_NAME}}** · Stage 41 · Gate 14 of 14

This is the final gate. Final approval is complete. Review the delivery target before Genesis creates a PR, exports an archive, or holds delivery.

---

**Delivery summary:**

| Item | Value |
|------|-------|
| PR title | {{PR_TITLE}} |
| Files in PR | {{TOTAL_FILES}} |
| Total tokens used this run | {{TOKENS_TOTAL_RUN}} |
| QA status | {{QA_STATUS}} |
| Staging URL | {{STAGING_URL}} |

---

**A. Approve PR delivery** `RECOMMENDED`
`Ship It` · `Create GitHub PR`
Create the GitHub PR with the Genesis-generated branch name, full description, CHANGELOG, test evidence, and DevOps hand-off package.

---

**B. Customize PR settings**
`Customize Target` · `Branch / Title / Reviewers`
Set a custom branch name, PR title, base branch, merge strategy, or reviewer list before the PR is created.

---

**C. Hold PR delivery**
`Hold PR` · `Do Not Deploy`
Keep the migration package local and block GitHub PR creation until a future explicit approval.

---

**D. Export archive only**
`Archive Only` · `No PR`
Export the generated output as a ZIP archive and skip GitHub PR creation entirely.

---

Which decision? **(A / B / C / D)**
