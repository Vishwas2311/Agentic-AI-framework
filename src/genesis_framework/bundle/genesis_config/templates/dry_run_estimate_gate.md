<!-- GENESIS PIPELINE TEMPLATE — Dry Run Estimate Gate (Stage 9) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- dry_run_estimate_gate_data.json, then display verbatim. Never shorten. -->

## Dry Run Estimate Gate
**{{APP_NAME}}** · Stage 9 · Gate 4 of 14

Genesis is about to generate **{{TOTAL_FILES}} files** across the structure below. Review the scope and token estimate before approving generation.

---

**What Genesis will build:**

```
{{APP_NAME}}/
│
├── app/
{{SCREEN_FILE_TREE}}
│   └── api/
{{API_FILE_TREE}}
│
├── components/
{{COMPONENT_FILE_TREE}}
│
├── lib/
{{LIB_FILE_TREE}}
│
├── prisma/
│   ├── schema.prisma
│   └── migrations/
│
├── terraform/
{{TERRAFORM_FILE_TREE}}
│
├── .github/workflows/
{{CICD_FILE_TREE}}
│
├── tests/
{{TEST_FILE_TREE}}
│
└── docs/
{{DOCS_FILE_TREE}}
```

---

**Token Estimate:**

| Area | Estimated Tokens |
|------|-----------------|
| Design system + component generation | {{TOKENS_DESIGN}} |
| Frontend screens ({{SCREEN_COUNT}} screens) | {{TOKENS_SCREENS}} |
| API routes + auth + data layer | {{TOKENS_API}} |
| Terraform + CI/CD + DevOps configs | {{TOKENS_DEVOPS}} |
| Tests (E2E + unit + load + a11y) | {{TOKENS_TESTS}} |
| HIPAA docs + documentation | {{TOKENS_DOCS}} |
| Repair loop + QA buffer | {{TOKENS_BUFFER}} |
| **Total estimated** | **{{TOKENS_TOTAL}}** |

---

**A. Approve — begin generation**
`Start Build` · `{{TOTAL_FILES}} files` · `{{TOKENS_TOTAL}}` · `{{DELIVERY_MODE}}`
Scope and token estimate are correct. Genesis starts generating code now across all areas.

---

**B. Adjust scope before generation**
`Modify Scope` · `Add or Remove` · `Reduce tokens`
Something is missing or should not be built. Tell Genesis what to add or remove before files are written. Token estimate will update.

---

**C. Switch delivery mode**
`Change Mode` · `Smaller Scope` · `Fewer tokens`
Too large. Switch to Hybrid Pilot (~{{TOKENS_HYBRID}}, ~{{FILES_HYBRID}} files) or Local Demo (~{{TOKENS_DEMO}}, ~{{FILES_DEMO}} files).

---

Which decision? **(A / B / C)**
