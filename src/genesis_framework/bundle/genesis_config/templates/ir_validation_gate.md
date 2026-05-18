<!-- GENESIS PIPELINE TEMPLATE — IR Validation Gate (Stage 22) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- ir_validation_gate data, then display verbatim. Never shorten.         -->

## IR Validation Gate
**{{APP_NAME}}** · Stage 22 · Gate 9 of 14

The Universal Low-Code Intermediate Representation (IR) has been built from all sources. Review the IR coverage and correctness before the canonical spec is generated.

---

**IR summary:**

| Area | Count |
|------|-------|
| Screens extracted | {{IR_SCREEN_COUNT}} |
| API endpoints | {{IR_API_COUNT}} |
| IR coverage | {{IR_COVERAGE}} |
| Validation errors | {{IR_ERROR_COUNT}} |

---

**A. Accept IR as valid** `RECOMMENDED`
`Approve IR` · `Build Canonical Spec`
Accept the validated ULC-IR and continue to canonical app spec building.

---

**B. Reject and rebuild IR**
`Reject IR` · `Rebuild Before Spec`
Reject the current IR with correction notes. Genesis will rebuild the IR applying your corrections before canonical spec continues.

---

**C. Accept with known issues**
`Accept with Caveats` · `Carry Known Issues`
Accept the IR while explicitly flagging known gaps or conflicts. Downstream agents will see these as structured caveats.

---

**D. Add IR corrections**
`Inject Corrections` · `Patch IR`
Provide specific field, entity, workflow, or role corrections to inject into the IR before canonical spec building.

---

Which decision? **(A / B / C / D)**
