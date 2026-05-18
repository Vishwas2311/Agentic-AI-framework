<!-- GENESIS PIPELINE TEMPLATE — Extraction Confidence Gate (Stage 14) -->
<!-- RENDER RULE: Load this file, populate all {{PLACEHOLDER}} tokens from  -->
<!-- extraction_confidence_gate data, then display verbatim. Never shorten. -->

## Extraction Confidence Gate
**{{APP_NAME}}** · Stage 14 · Gate 7 of 14

The semantic evidence graph has been built from all sources. Review the extraction confidence before the IR is validated.

---

**Confidence report:**

| Metric | Value |
|--------|-------|
| Overall gate decision | {{GATE_DECISION}} |
| Average confidence | {{AVG_CONFIDENCE}} |
| Evidence coverage | {{COVERAGE}} |
| Conflict count | {{CONFLICT_COUNT}} |

---

**A. Approve — confidence is acceptable** `RECOMMENDED`
`Approve Extraction` · `Proceed to IR Validation`
Extraction confidence meets the required threshold. Genesis proceeds to build the Universal Low-Code IR.

---

**B. Auto-close remaining gaps**
`Auto-Close Gaps` · `Improve Confidence` · `May add ~5–10%`
Genesis runs the BRD gap-closer to find and fill evidence gaps automatically. Uses BRD text and all input artifacts as search corpus.

---

**C. Force 100% coverage**
`Force Full Coverage` · `Maximum Depth` · `Slower`
Genesis attempts to reach 95%+ confidence by running deep iterative gap closure on every screen, workflow, entity, and acceptance criterion. Adds 1–3 extra closure passes.

---

Which decision? **(A / B / C)**
